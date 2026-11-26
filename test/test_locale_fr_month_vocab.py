"""French locale phrase sets, and a cross-language tripwire.

Regression guard for the four ``locale/fr/`` files that the localize app
overwrote with Kabyle (``months.voc``, ``unit_day.voc``, ``unit_year.voc``,
``season_winter.voc``; merged as 33bdabad, 7ae9743e, 2114ef47, b9254f08 and
shipped in 0.31.3a4 to 0.31.3a7).  With Kabyle in those files every scoped
French phrase below returns ``None``.

Two tripwires follow.  ``months.voc`` must still carry the month names that
the language's own date extractor hard-coded -- that source was not writable
by the translation app, so its table, kept below, is the reference for what
language a folder is in, and it is the check that a whole foreign month
table fails.  A ``.voc``
file may carry another language's month name only when that name is also a
month of its own language (``marzo`` is both Spanish and Italian).
"""
import os
import shutil
import unicodedata
from datetime import date

import pytest

from ovos_date_parser import load_scoped_vocabulary, extract_scoped_date
from ovos_date_parser.ranges import DateTimeResolution

PACKAGE_DIR = os.path.dirname(
    os.path.abspath(__import__("ovos_date_parser").__file__))
LOCALE_DIR = os.path.join(PACKAGE_DIR, "locale")
LANGS = sorted(d for d in os.listdir(LOCALE_DIR)
               if os.path.isdir(os.path.join(LOCALE_DIR, d)))

# The 12 month names each language's date extractor hard-coded in
# ``dates_<lang>.py``, lower-cased. chronologia reads dates now and the
# extractors are gone, so their tables are kept here as the reference.
_EXTRACTOR_MONTHS = {
    "an": ["chinero", "febrero", "marzo", "abril", "mayo", "chunyo",
        "chuliol", "agosto", "setiembre", "octubre", "noviembre",
        "deciembre"],
    "ast": ["xineru", "febreru", "marzu", "abril", "mayu", "xunu", "xunetu",
        "agostu", "setiembre", "ochobre", "payares", "avientu"],
    "az": ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul",
        "avqust", "sentyabr", "oktyabr", "moyabr", "dekabr"],
    "ca": ["gener", "febrer", "març", "abril", "maig", "juny", "juliol",
        "agost", "setembre", "octubre", "novembre", "desembre"],
    "da": ["januar", "februar", "marts", "april", "maj", "juni", "juli",
        "august", "september", "oktober", "november", "december"],
    "de": ["januar", "februar", "märz", "april", "mai", "juni", "juli",
        "august", "september", "oktober", "november", "dezember"],
    "el": ["ιανουαριου", "φεβρουαριου", "μαρτιου", "απριλιου", "μαιου",
        "ιουνιου", "ιουλιου", "αυγουστου", "σεπτεμβριου", "οκτωβριου",
        "νοεμβριου", "δεκεμβριου"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
        "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "eu": ["urtarrila", "otsaila", "martxoa", "apirila", "maiatza", "ekaina",
        "uztaila", "abuztua", "iraila", "urria", "azaroa", "abendua"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"],
    "fy": ["jannewaris", "febrewaris", "maart", "april", "maaie", "juny",
        "july", "augustus", "septimber", "oktober", "novimber", "desimber"],
    "gl": ["xaneiro", "febreiro", "marzo", "abril", "maio", "xuño", "xullo",
        "agosto", "setembro", "outubro", "novembro", "decembro"],
    "it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
    "nl": ["januari", "februari", "maart", "april", "mei", "juni", "juli",
        "augustus", "september", "oktober", "november", "december"],
    "oc": ["genier", "febrier", "març", "abril", "mai", "junh", "julhet",
        "agost", "setembre", "octobre", "novembre", "decembre"],
    "pt": ["janeiro", "fevereiro", "marco", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
    "ro": ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
        "iulie", "august", "septembrie", "octombrie", "noiembrie",
        "decembrie"],
    "sv": ["januari", "februari", "mars", "april", "maj", "juni", "juli",
        "augusti", "september", "oktober", "november", "december"],
}

# The languages whose month names the foreign check knows about. A locale
# folder is only one of the languages this package understands: the
# extractors carried a month table for languages that ship no folder, and a
# swap from one of those is the same defect. Built from the tables, not from
# LANGS, so the set does not shrink to the folders that exist.
MONTH_LANGS = sorted(_EXTRACTOR_MONTHS)

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
    """The 12 month names the ``dates_<lang>.py`` extractor hard-coded, or
    None for a language that had no single table."""
    return _EXTRACTOR_MONTHS.get(lang)


def _voc_lines(path):
    with open(path, encoding="utf-8") as handle:
        return [line.strip().lower() for line in handle if line.strip()]


@pytest.mark.parametrize("lang", LANGS)
def test_months_voc_matches_the_extractor(lang):
    """``months.voc`` is still in its own language.

    A folder keeps a small licence to differ from the extractor source:
    ``locale/pt/months.voc`` writes ``março`` where ``dates_pt.py`` wrote
    the ASCII ``marco``.  A whole month table from another language keeps
    none of the 12 names, so the majority rule still catches it.
    """
    expected = _module_months(lang)
    if expected is None:
        pytest.skip(f"dates_{lang}.py had no single month table")
    lines = _voc_lines(os.path.join(LOCALE_DIR, lang, "months.voc"))
    kept = [m for m in expected if m in lines]
    assert len(kept) >= 9, (
        f"locale/{lang}/months.voc keeps only {len(kept)} of the 12 month "
        f"names in dates_{lang}.py: {sorted(set(expected) - set(kept))}")


def _unaccented(word):
    return "".join(c for c in unicodedata.normalize("NFD", word)
                   if not unicodedata.combining(c))


def _foreign_offenders(lang, lang_dir):
    """Lines in ``lang_dir`` that are another shipped language's month name.

    "Another language" is every ``dates_<lang>.py`` extractor that had one
    12-name month table, not the locale folders alone. Of the 13 languages
    with a month table and no folder, a whole-table swap of 10 is caught by
    names they happen to share with the folders; az, el and eu share none,
    so reading LANGS alone passed them in silence.

    "Own" comes from the extractor table alone, each name with its accents
    and without them: ``locale/fr`` writes ``decembre`` beside ``décembre``
    for a transcript with no accents, and that spelling is French even
    though Occitan writes its own December the same way. Reading
    ``months.voc`` here would make the file vouch for itself: a whole-file
    swap of another language into ``locale/<lang>/months.voc`` would put
    that language's names into "own", and every one of its month names
    would then pass this check. reviewer-b proved that live with es into fr on
    #341, and ``test_a_whole_file_language_swap_is_caught`` below is the
    failing-first case for it.
    """
    own = {form for month in _module_months(lang) or []
           for form in (month, _unaccented(month))}
    foreign = {}
    for other in MONTH_LANGS:
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


@pytest.mark.parametrize("other", ["az", "el", "eu"])
def test_a_swap_from_a_language_with_no_locale_folder_is_caught(tmp_path,
                                                                other):
    """The three swaps the folder-only foreign set passed in silence.

    The ``dates_az.py``, ``dates_el.py`` and ``dates_eu.py`` extractors
    each had a month table, and the languages ship no ``locale/`` folder. Their names are shared with
    none of the folders that do ship, so a whole table written over
    ``locale/fr/months.voc`` kept no name the check knew, and the locale
    read as clean. The other ten languages in the same position were caught
    only by coincidental shared names, which is luck, not a check.
    """
    names = _module_months(other)
    assert names, f"dates_{other}.py had no single month table"

    swapped = tmp_path / "fr"
    shutil.copytree(os.path.join(LOCALE_DIR, "fr"), swapped)
    (swapped / "months.voc").write_text("\n".join(names) + "\n",
                                        encoding="utf-8")

    offenders = _foreign_offenders("fr", str(swapped))
    caught = {line.split("'")[1] for line in offenders if "'" in line}
    assert caught & set(names), (
        f"a whole-table {other} swap into fr/months.voc went unreported; "
        f"offenders were {offenders}")


def test_the_foreign_set_reads_the_modules_not_the_locale_folders():
    """The definition itself, so a narrowing of it fails here.

    Every language with a month table takes part, including those with no
    locale folder; LANGS stays the set of folders to scan. The 18 languages
    below each had a 12-name month table, so a set that drops any of
    them fails here.
    """
    with_tables = {lang for lang in MONTH_LANGS if _module_months(lang)}
    assert with_tables >= {
        "an", "ast", "az", "ca", "da", "de", "el", "es", "eu", "fr", "fy",
        "gl", "it", "nl", "oc", "pt", "ro", "sv"}
    assert {"az", "el", "eu"}.isdisjoint(LANGS)
