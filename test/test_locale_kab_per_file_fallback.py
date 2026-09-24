"""Kabyle phrase sets resolve file by file, not language by language.

`ovos_date_parser/locale/kab/` ships 11 `.voc` files; chronologia's packaged
locale ships 75 for the same language, including the native forms a Kabyle
speaker supplied. Resolving a whole language to one root meant the 11 local
files hid all 75, so `marker_last`, `marker_of` and the season sets fell back
to their ENGLISH defaults and only a sentence mixing English markers with
Kabyle words could parse.
"""
from datetime import date

import pytest

from ovos_date_parser import extract_scoped_date, load_scoped_vocabulary
from ovos_date_parser.ranges import DateTimeResolution

REF = date(2026, 9, 23)


@pytest.fixture(scope="module")
def vocab_kab():
    return load_scoped_vocabulary("kab")


def test_markers_come_from_chronologia_when_the_local_folder_lacks_them(vocab_kab):
    """`marker_last` and `marker_of` are not in the parser's own kab folder.

    Before the per-file fallback these read 'last' and 'of'.
    """
    assert "aneggaru" in vocab_kab.last_word
    assert "iɛeddan" in vocab_kab.last_word
    assert "yezrin" in vocab_kab.last_word
    assert vocab_kab.of == "n"


def test_units_and_months_still_come_from_the_local_folder(vocab_kab):
    """The local folder still wins for every file it does ship."""
    assert vocab_kab.months[:3] == ["yennayer", "fuṛar", "meɣres"]
    assert "ass" in vocab_kab.units["day"]
    assert "aseggas" in vocab_kab.units["year"]


def test_a_kabyle_last_day_phrase_resolves(vocab_kab):
    """Fail-before by value: None on dev, a date here.

    The phrase carries only Kabyle words. `aneggaru` reaches the scan through
    chronologia's `marker_last.voc` and `n` through its `marker_of.voc`.
    """
    result = extract_scoped_date("aneggaru ass n meɣres", vocab_kab, REF)
    assert result is not None, "the Kabyle phrase did not resolve"
    assert result[0] == date(2026, 3, 31)
    assert result[2] == DateTimeResolution.DAY_OF_MONTH


def test_an_english_marker_no_longer_parses_as_kabyle(vocab_kab):
    """The other half of the fix, and the reason it is not cosmetic.

    `the last ass of meɣres` resolved before, because the English defaults
    were standing in for the missing files. A sentence that is half English
    must not parse as Kabyle.
    """
    assert extract_scoped_date("the last ass of meɣres", vocab_kab, REF) is None


def test_the_english_control_is_unchanged():
    """`en` has no local folder and resolved to chronologia before and after."""
    vocab_en = load_scoped_vocabulary("en")
    result = extract_scoped_date("the last day of march", vocab_en, REF)
    assert result is not None
    assert result[0] == date(2026, 3, 31)


@pytest.mark.parametrize("lang,phrase,expected", [
    ("fr", "le dernier jour de mars", date(2026, 4, 30)),
    ("de", "der letzte tag des märz", date(2026, 3, 31)),
    ("es", "el ultimo dia de marzo", date(2026, 3, 31)),
    ("it", "l'ultimo giorno di marzo", date(2026, 3, 31)),
    ("pt", "o ultimo dia de março", date(2026, 3, 31)),
])
def test_the_five_local_languages_are_unchanged(lang, phrase, expected):
    """Every language with its own folder keeps the same answer.

    These five have partial local folders too, so they are the regression
    surface of a per-file fallback.
    """
    result = extract_scoped_date(phrase, load_scoped_vocabulary(lang), REF)
    assert result is not None, f"{phrase!r} stopped resolving"
    assert result[0] == expected
