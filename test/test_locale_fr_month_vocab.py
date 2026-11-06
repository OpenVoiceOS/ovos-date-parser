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
    # March, not April. This row read date(2026, 4, 30) while months.voc
    # carried fevrier on a line of its own: the file is positional, so the
    # extra line moved mars to April's slot and the gold was written from
    # the defect rather than from the phrase. Every other language in
    # test_locale_kab_per_file_fallback.py asserts the 31st of March for
    # the same sentence.
    ("le dernier jour de mars", date(2026, 3, 31),
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
    # One entry per month, variants inside the entry. The old shape put
    # "fevrier" on its own line, which shifted every later month by one.
    assert vocab_fr.months[:3] == ["(?:janvier)", "(?:février|fevrier)",
                                   "(?:mars)"]
    assert "hiver" in vocab_fr.seasons[list(vocab_fr.seasons)[-1]]
    assert "jour" in vocab_fr.units["day"]
    assert "ans" in vocab_fr.units["year"]


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
        if not any(getattr(t, "id", "") == "months" for t in node.targets):
            continue
        value = node.value
        if (isinstance(value, ast.List) and len(value.elts) == 12
                and all(isinstance(e, ast.Constant) for e in value.elts)):
            found.append([e.value.lower() for e in value.elts])
    if len(found) != 1:
        return None
    return found[0]


def _voc_lines(path):
    with open(path, encoding="utf-8") as handle:
        return [line.strip().lower() for line in handle if line.strip()]


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
        pytest.skip(f"dates_{lang}.py declares no single month table")
    lines = _voc_lines(os.path.join(LOCALE_DIR, lang, "months.voc"))
    kept = [m for m in expected if m in lines]
    assert len(kept) >= 9, (
        f"locale/{lang}/months.voc keeps only {len(kept)} of the 12 month "
        f"names in dates_{lang}.py: {sorted(set(expected) - set(kept))}")


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
    own = set(_module_months(lang) or [])
    foreign = {}
    for other in LANGS:
        if other == lang:
            continue
        for name in _module_months(other) or []:
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

    spanish = set(_module_months("es"))
    caught = {line.split("'")[1] for line in offenders if "'" in line}
    assert caught & spanish, (
        "a whole-file es swap into fr/months.voc went unreported; "
        f"offenders were {offenders}")
