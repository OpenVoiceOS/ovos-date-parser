# -*- coding: utf-8 -*-
"""Routing ``extract_datetime`` through chronologia.

chronologia answers a stretch of time; this signature answers an instant, so
the routing has to choose one. These pin the choice for each shape a span can
take, and the boundaries of which locales are routed at all.

The anchor is a Tuesday at 13:04. Expected values are derived from it by hand.
"""
from datetime import datetime, time

import pytest

from ovos_date_parser import (CHRONOLOGIA_LOCALES, extract_datetime,
                              extract_duration)

ANCHOR = datetime(2017, 6, 27, 13, 4)


def when(text, lang, **kw):
    got = extract_datetime(text, lang, anchorDate=ANCHOR, **kw)
    return None if got is None else got[0]


@pytest.mark.parametrize("lang", sorted(CHRONOLOGIA_LOCALES))
def test_a_routed_locale_reads_an_iso_clock(lang):
    assert when("23:30", lang) == datetime(2017, 6, 27, 23, 30)


@pytest.mark.parametrize("text,lang", [("u 23:30", "hr"), ("o 23:30", "sk")])
def test_the_at_preposition_is_consumed(text, lang):
    """The marker belongs to the reading, not to the leftover text."""
    got = extract_datetime(text, lang, anchorDate=ANCHOR)
    assert got[0] == datetime(2017, 6, 27, 23, 30)
    assert got[1] == ""


@pytest.mark.parametrize("lang", sorted(CHRONOLOGIA_LOCALES))
def test_midnight_rolls_forward(lang):
    """00:00 has already gone at 13:04, so it names tomorrow."""
    assert when("00:00", lang) == datetime(2017, 6, 28, 0, 0)


@pytest.mark.parametrize("text,lang", [("za 3 dana", "hr"), ("o 3 dni", "sk")])
def test_an_offset_in_days_names_the_date(text, lang):
    """"in three days" names a date; the time of day was not said."""
    assert when(text, lang) == datetime(2017, 6, 30, 0, 0)


@pytest.mark.parametrize("text,lang", [("za 2 sata", "hr"), ("o 2 hodiny", "sk")])
def test_an_offset_in_hours_names_the_moment(text, lang):
    """"in two hours" names an instant, so the time of day is the answer."""
    assert when(text, lang) == datetime(2017, 6, 27, 15, 4)


@pytest.mark.parametrize("text,lang", [
    ("sutra", "hr"), ("zajtra", "sk"),
])
def test_a_bare_day_starts_at_midnight(text, lang):
    assert when(text, lang) == datetime(2017, 6, 28, 0, 0)


@pytest.mark.parametrize("text,lang", [
    ("sutra", "hr"), ("zajtra", "sk"),
])
def test_default_time_fills_a_day_the_phrase_left_open(text, lang):
    assert when(text, lang, default_time=time(8, 0)) == datetime(2017, 6, 28, 8, 0)


@pytest.mark.parametrize("text,lang", [("za 2 sata", "hr"), ("o 2 hodiny", "sk")])
def test_default_time_does_not_overwrite_an_offset(text, lang):
    """"in two hours" has already fixed a moment; a default must not move it.

    ``default_time`` supplies the time of day a phrase left unsaid. An offset
    shorter than a day did not leave it unsaid.
    """
    assert when(text, lang, default_time=time(8, 0)) == datetime(2017, 6, 27, 15, 4)


@pytest.mark.parametrize("text,lang", [
    ("2 hodiny 30 minut", "cs"),
    ("2 sata 30 minuta", "hr"),
    ("2 hodiny 30 minút", "sk"),
])
def test_a_spoken_length_counts_forward_from_now(text, lang):
    """"two and a half hours" is when a skill should fire, not a time of day.

    chronologia declines these, and is right to: its contract is spans, and a
    length names no span. This signature's contract is the instant a skill
    schedules, and "remind me in two and a half hours" is an ordinary thing
    to say, so the length counts forward from the anchor.

    The expected value is derived from the duration reader rather than
    written down: it returns two and a half hours for the phrase, and the
    anchor plus that is 15:34. Nothing here asks the function under test what
    the answer should be.
    """
    expected = ANCHOR + extract_duration(text, lang)[0]
    assert expected == datetime(2017, 6, 27, 15, 34)
    got = extract_datetime(text, lang, anchorDate=ANCHOR)
    assert got is not None, text
    assert got[0] == expected
    assert got[1] == ""


@pytest.mark.parametrize("text,lang", [
    ("2 hodiny 30 minut", "cs"),
    ("2 sata 30 minuta", "hr"),
    ("2 hodiny 30 minút", "sk"),
])
def test_a_default_time_does_not_move_a_spoken_length(text, lang):
    """The length fixed a moment, so there is nothing for a default to fill."""
    assert when(text, lang, default_time=time(8, 0)) == datetime(2017, 6, 27, 15, 34)


@pytest.mark.parametrize("text,lang,expected", [
    ("za 2 hodiny", "cs", datetime(2017, 6, 27, 15, 4)),
    ("zítra", "cs", datetime(2017, 6, 28, 0, 0)),
    ("příští týden", "cs", datetime(2017, 7, 3, 0, 0)),
    ("o 23:30", "sk", datetime(2017, 6, 27, 23, 30)),
    ("u 23:30", "hr", datetime(2017, 6, 27, 23, 30)),
    ("sutra", "hr", datetime(2017, 6, 28, 0, 0)),
])
def test_the_readings_that_must_not_move(text, lang, expected):
    """The fence around the change: every one asserted by value.

    A differential can report these as unchanged while both sides are wrong
    together. These say what the answer is.
    """
    got = extract_datetime(text, lang, anchorDate=ANCHOR)
    assert got is not None, text
    assert got[0] == expected
    assert got[1] == ""


@pytest.mark.parametrize("lang", ["en", "de", "es", "pt", "fr", "pl", "bg"])
def test_an_unrouted_locale_keeps_its_own_extractor(lang):
    """Routing is per locale, so the rest are untouched."""
    assert lang not in CHRONOLOGIA_LOCALES
