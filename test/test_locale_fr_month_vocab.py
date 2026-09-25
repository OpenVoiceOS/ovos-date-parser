"""French locale phrase sets, and a cross-language tripwire.

Regression guard for the four ``locale/fr/`` files that the localize app
overwrote with Kabyle (``months.voc``, ``unit_day.voc``, ``unit_year.voc``,
``season_winter.voc``; merged as 33bdabad, 7ae9743e, 2114ef47, b9254f08 and
shipped in 0.31.3a4 to 0.31.3a7).  With Kabyle in those files every scoped
French phrase below returns ``None``.

Two tripwires follow.  ``months.voc`` must still carry the month names the
language's own extractor module hard-codes -- that source is not writable by
the translation app, so it is the reference for what language a folder is
in, and it is the check that a whole foreign month table fails.  A ``.voc``
file may carry another language's month name only when that name is also a
month of its own language (``marzo`` is both Spanish and Italian).
"""
import ast
import os
import shutil
from datetime import date

import pytest

from ovos_date_parser import load_scoped_vocabulary, extract_scoped_date
from ovos_date_parser.ranges import DateTimeResolution

PACKAGE_DIR = os.path.dirname(
    os.path.abspath(__import__("ovos_date_parser").__file__))
LOCALE_DIR = os.path.join(PACKAGE_DIR, "locale")
LANGS = sorted(d for d in os.listdir(LOCALE_DIR)
               if os.path.isdir(os.path.join(LOCALE_DIR, d)))

REF = date(2026, 9, 19)


@pytest.fixture(scope="module")
def vocab_fr():
    return load_scoped_vocabulary("fr")


@pytest.mark.parametrize("text,expected,resolution", [
    ("le 3eme jour de janvier", date(2026, 1, 3),
     DateTimeResolution.DAY_OF_MONTH),
    ("le dernier jour de mars", date(2026, 4, 30),
     DateTimeResolution.DAY_OF_MONTH),
    ("en hiver", date(2026, 12, 1), DateTimeResolution.MONTH),
    ("le 2eme jour de l'annee", date(2026, 1, 2),
     DateTimeResolution.DAY_OF_YEAR),
])
def test_scoped_french_phrases_resolve(vocab_fr, text, expected, resolution):
    """French month, day, year and winter forms drive the scoped scan."""
    result = extract_scoped_date(text, vocab_fr, REF)
    assert result is not None, f"{text!r} did not resolve"
    assert result[0] == expected
    assert result[2] == resolution


def test_french_vocab_is_french(vocab_fr):
    """The phrase sets the four overwritten files feed are French."""
    assert vocab_fr.months[:3] == ["janvier", "février", "fevrier"]
    assert "hiver" in vocab_fr.seasons[list(vocab_fr.seasons)[-1]]
    assert "jour" in vocab_fr.units["day"]
    assert "ans" in vocab_fr.units["year"]


def _names_a_month_table(target, lang):
    """True for the name a module gives its own month table.

    ``dates_fr.py`` and its siblings write ``months``. ``dates_kab.py``
    writes ``MONTHS_KAB``. Reading only the lower-case bare name skipped
    Kabyle entirely, so the tripwire never ran for the one locale whose
    folder was the reason the tripwire exists.
    """
    name = getattr(target, "id", "").lower()
    return name in ("months", f"months_{lang.lower()}")


def _twelve_month_values(value):
    """The 12 month names out of a list or a dict, in month order.

    Two shapes are in the tree. A 12-element list is January first. A dict
    is keyed by month number, so it is read by its keys and not by the
    order the source happens to write them in: ``{1: ..., 12: ...}`` and
    the same entries shuffled are the same table.
    """
    if (isinstance(value, ast.List) and len(value.elts) == 12
            and all(isinstance(e, ast.Constant) for e in value.elts)):
        return [e.value.lower() for e in value.elts]
    if isinstance(value, ast.Dict) and len(value.keys) == 12:
        pairs = {}
        for key, item in zip(value.keys, value.values):
            if not isinstance(key, ast.Constant) or not isinstance(key.value, int):
                return None
            if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
                return None
            pairs[key.value] = item.value.lower()
        if sorted(pairs) != list(range(1, 13)):
            return None
        return [pairs[n] for n in range(1, 13)]
    return None


def _module_months(lang):
    """The 12 month names hard-coded in ``dates_<lang>.py``.

    These live in the extractor source, which the translation app never
    writes, so they are the reference for what language a locale folder
    is supposed to be in.
    """
    path = os.path.join(PACKAGE_DIR, f"dates_{lang}.py")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(_names_a_month_table(t, lang) for t in node.targets):
            continue
        table = _twelve_month_values(node.value)
        if table is not None and table not in found:
            found.append(table)
    if not found:
        return None
    # A module may write its months more than once and the two spellings
    # need not agree. dates_es.py has MONTHS_ES as a dict AND a local
    # ``months`` list, identical. dates_pt.py has MONTHS_PT with "março"
    # and a local list with the ASCII "marco", which is the licence to
    # differ this file's own docstring describes. Both are the language's
    # own, so each slot keeps every spelling declared for it rather than
    # one table winning.
    return [tuple(dict.fromkeys(table[n] for table in found))
            for n in range(12)]


def _voc_lines(path):
    """Every surface a ``.voc`` file offers, one per entry.

    A line may carry several spellings of one month separated by ``|``:
    ``months.voc`` is read BY POSITION by ``scoped_scan``, so a variant
    cannot have a line of its own without shifting every later month. Each
    variant is a surface the tripwire may match, so the line is split
    rather than compared whole.
    """
    surfaces = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip().lower()
            if not line:
                continue
            surfaces.extend(part.strip() for part in line.split("|")
                            if part.strip())
    return surfaces


@pytest.mark.parametrize("lang", LANGS)
def test_months_voc_matches_the_extractor(lang):
    """``months.voc`` is still in its own language.

    A folder keeps a small licence to differ from the extractor source:
    ``locale/pt/months.voc`` writes ``março`` where ``dates_pt.py`` writes
    the ASCII ``marco``.  A whole month table from another language keeps
    none of the 12 names, so the majority rule still catches it.
    """
    expected = _module_months(lang)
    if expected is None:
        pytest.skip(f"dates_{lang}.py declares no month table")
    lines = _voc_lines(os.path.join(LOCALE_DIR, lang, "months.voc"))
    kept = [slot for slot in expected if any(name in lines for name in slot)]
    missing = sorted("/".join(slot) for slot in expected if slot not in kept)
    assert len(kept) >= 9, (
        f"locale/{lang}/months.voc keeps only {len(kept)} of the 12 month "
        f"names in dates_{lang}.py: {missing}")


def test_the_kabyle_dict_table_is_read():
    """dates_kab.py writes MONTHS_KAB as a dict keyed by month number.

    The extractor used to look only for a 12-element LIST assigned to the
    bare name ``months``, so Kabyle declared "no month table", the
    tripwire skipped it, and the one locale whose folder was overwritten
    with another language was the one locale the guard never checked.
    """
    table = _module_months("kab")
    assert table is not None, "dates_kab.py still reads as no month table"
    assert len(table) == 12
    assert table[0] == ("yennayer",), "January is not first"
    assert table[11] == ("dujember",) or "dujembe\u1e5b" in table[11]


def test_a_swapped_kabyle_table_is_caught(tmp_path):
    """Fail-before for the widened tripwire, with the real numbers.

    The majority rule allows three of twelve to differ, so swapping THREE
    French names in leaves nine kept and passes by design. Four trips it.
    Three are still caught, by the foreign-month guard below rather than
    by this one, which is why the pair exists.
    """
    expected = _module_months("kab")
    swapped = tmp_path / "kab"
    shutil.copytree(os.path.join(LOCALE_DIR, "kab"), swapped)
    lines = _voc_lines(str(swapped / "months.voc"))

    for count, still_passes in ((3, True), (4, False)):
        french = ["janvier", "f\u00e9vrier", "mars", "avril"][:count]
        mixed = french + lines[count:]
        kept = [slot for slot in expected
                if any(name in mixed for name in slot)]
        assert (len(kept) >= 9) is still_passes, (
            f"{count} French names swapped in left {len(kept)} of 12 kept; "
            f"expected the 9-of-12 rule to "
            f"{'pass' if still_passes else 'fail'}")


def _foreign_offenders(lang, lang_dir):
    """Lines in ``lang_dir`` that are another shipped language's month name.

    "Own" comes from the extractor source alone. Reading ``months.voc``
    here would make the file vouch for itself: a whole-file swap of
    another language into ``locale/<lang>/months.voc`` would put that
    language's names into "own", and every one of its month names would
    then pass this check. reviewer-b proved that live with es into fr on
    #341, and ``test_a_whole_file_language_swap_is_caught`` below is the
    failing-first case for it.
    """
    own = {name for slot in (_module_months(lang) or []) for name in slot}
    foreign = {}
    for other in LANGS:
        if other == lang:
            continue
        for slot in _module_months(other) or []:
            for name in slot:
                foreign.setdefault(name, []).append(other)
    offenders = []
    for name in sorted(os.listdir(lang_dir)):
        if not name.endswith(".voc"):
            continue
        for line in _voc_lines(os.path.join(lang_dir, name)):
            if line in foreign and line not in own:
                offenders.append(f"{name}: {line!r} "
                                 f"(a month of {'/'.join(foreign[line])})")
    return offenders


@pytest.mark.parametrize("lang", LANGS)
def test_no_foreign_month_names_in_locale(lang):
    """No phrase set carries another shipped language's month name."""
    offenders = _foreign_offenders(lang, os.path.join(LOCALE_DIR, lang))
    assert not offenders, f"locale/{lang} carries " + "; ".join(offenders)


def test_a_whole_file_language_swap_is_caught(tmp_path):
    """Spanish months written over ``locale/fr/months.voc`` must be caught.

    This is the case the old exemption missed. It built "own" from the
    on-disk ``months.voc``, so the swapped-in Spanish names vouched for
    themselves and the check passed on a corrupted locale.
    """
    swapped = tmp_path / "fr"
    shutil.copytree(os.path.join(LOCALE_DIR, "fr"), swapped)
    shutil.copy(os.path.join(LOCALE_DIR, "es", "months.voc"),
                swapped / "months.voc")

    offenders = _foreign_offenders("fr", str(swapped))

    spanish = {name for slot in _module_months("es") for name in slot}
    caught = {line.split("'")[1] for line in offenders if "'" in line}
    assert caught & spanish, (
        "a whole-file es swap into fr/months.voc went unreported; "
        f"offenders were {offenders}")
