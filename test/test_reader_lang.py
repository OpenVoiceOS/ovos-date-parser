# -*- coding: utf-8 -*-
"""A language tag reads as its shortest standard code, and "no" as "nb".

"deu" is "de" and "iw" is "he". "no" names Norwegian in general and Bokmål is
its written standard, so every reader answers "no" the way it answers "nb".
The anchor is a Tuesday at 13:04; the hand-computed values are derived from
it.
"""
from datetime import datetime, timedelta

import pytest

from ovos_date_parser import extract_datetime, extract_duration

ANCHOR = datetime(2017, 6, 27, 13, 4)

TEXTS = ["om tre dager", "neste fredag", "i morgen klokka 8",
         "klokka 6 om kvelden", "5. juli", "på fredag klokka 15"]


@pytest.mark.parametrize("tag", ["no", "no-NO", "NO_no"])
@pytest.mark.parametrize("text", TEXTS)
def test_no_reads_a_date_as_nb(text, tag):
    assert (extract_datetime(text, tag, anchorDate=ANCHOR)
            == extract_datetime(text, "nb", anchorDate=ANCHOR))


def test_no_reads_a_counted_offset():
    found = extract_datetime("om tre dager", "no", anchorDate=ANCHOR)
    assert found[0] == datetime(2017, 6, 30, 13, 4)


@pytest.mark.parametrize("text,expected", [
    ("tre timer", timedelta(hours=3)),
    ("ti minutter", timedelta(minutes=10)),
])
def test_no_reads_a_duration_as_nb(text, expected):
    assert extract_duration(text, "no")[0] == expected
    assert extract_duration(text, "no") == extract_duration(text, "nb")


@pytest.mark.parametrize("tag,short,text", [
    ("deu", "de", "morgen um 8 uhr"),
    ("est", "et", "homme kell 8"),
    ("slk", "sk", "zajtra o 8"),
    ("nob", "nb", "i morgen klokka 8"),
    ("iw", "he", "מחר בשמונה"),
])
def test_a_long_or_old_code_reads_as_its_short_code(tag, short, text):
    """A three-letter code reads as its two-letter one, never as a language
    whose code it begins with ("est" is Estonian, not Spanish)."""
    expected = extract_datetime(text, short, anchorDate=ANCHOR)
    assert expected is not None
    assert extract_datetime(text, tag, anchorDate=ANCHOR) == expected


@pytest.mark.parametrize("tag,text,expected", [
    ("nl_NL", "acht uur", timedelta(hours=8)),
    ("pt_BR", "uma hora", timedelta(hours=1)),
    ("en_US", "ten minutes", timedelta(minutes=10)),
])
def test_a_duration_reads_a_tag_written_with_an_underscore(tag, text, expected):
    """"nl_NL" is "nl-NL", for a duration as for a date."""
    assert extract_duration(text, tag)[0] == expected
    assert extract_duration(text, tag) == extract_duration(
        text, tag.replace("_", "-"))
