"""Regression tests: Italian sentences with "presto" and "tardi".

Without an hour in the sentence the two words set nothing, so "è tardi" has
no date. After an hour they move it by one. Expected datetimes are
hand-derived from the fixed anchor, Saturday 17 October 2026 12:00. A lone
spoken hour takes the next twelve-hour reading after the anchor (ruling 17),
so "alle tre" is 15:00 that day.
"""
import inspect
import json
import re
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

import ovos_date_parser
from ovos_date_parser import dates_it, extract_datetime

ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


def _extract(text):
    return extract_datetime(text, lang="it-IT", anchorDate=ANCHOR)


def _dt(text):
    res = _extract(text)
    assert res is not None, "no datetime extracted from %r" % text
    return res[0].replace(tzinfo=None)


def _defect(issue):
    return pytest.mark.xfail(strict=True, reason=issue)


# A range of lone hours takes the next twelve-hour reading of its start
# (ruling 17): at noon, "dalle 9 alle 11" starts at 21:00 that day.
HOUR_RANGE = _defect("https://github.com/TigreGotico/chronologia/issues/1032")
# A part of the day said before the clock ("stasera alle otto") names the
# half of the day the hour is in.
DAYPART_THEN_CLOCK = _defect("https://github.com/TigreGotico/chronologia/issues/1002")
# "stasera dieci meno un quarto" gives no reading.
DAYPART_THEN_MENO = _defect("https://github.com/TigreGotico/chronologia/issues/1234")
# "le", "dalle" and "delle" carry the clock as "alle" does.
ARTICLE_CLOCK = _defect("https://github.com/TigreGotico/chronologia/issues/1032")
# "presto" and "tardi" beside an hour.
EARLY_LATE = _defect("https://github.com/TigreGotico/chronologia/issues/1033")
# Minutes written as a second number after the hour ("alle 3 30").
HOUR_SPACE_MINUTES = _defect("https://github.com/TigreGotico/chronologia/issues/1032")
# Arithmetic and amounts are no time.
FALSE_POSITIVE = _defect("https://github.com/TigreGotico/chronologia/issues/1035")


def _row(*values, marks=()):
    return pytest.param(*values, marks=marks) if marks else values


@pytest.mark.parametrize("text", [
    "è tardi", "si è fatto tardi", "è troppo presto", "è ancora presto",
    "presto", "tardi", "più tardi", "a più tardi", "ci vediamo più tardi",
    "arrivo tardi", "perché è tardi"])
def test_sentences_without_a_date_are_none(text):
    assert _extract(text) is None


def test_a_date_beside_presto_or_tardi_is_still_read():
    assert _dt("domani è tardi") == datetime(2026, 10, 18)
    assert _dt("domani presto") == datetime(2026, 10, 18)


# After an hour the two words move it by one hour.
@pytest.mark.parametrize("text,expected", [
    ("alle 8 di sera", datetime(2026, 10, 17, 20)),
    _row("alle 8 di sera tardi", datetime(2026, 10, 17, 21), marks=EARLY_LATE),
    ("domani alle 7", datetime(2026, 10, 18, 7)),
    _row("domani alle 7 presto", datetime(2026, 10, 18, 6), marks=EARLY_LATE),
    # either word before the hour changes nothing
    _row("domani presto alle 7", datetime(2026, 10, 18, 7), marks=EARLY_LATE),
    _row("domani tardi alle 7", datetime(2026, 10, 18, 7), marks=EARLY_LATE),
])
def test_presto_and_tardi_beside_an_hour(text, expected):
    assert _dt(text) == expected


def _vocabulary():
    words = set()
    res = Path(ovos_date_parser.__file__).parent / "res" / "it"
    for path in res.glob("*.json"):
        text = path.read_text(encoding="utf8")
        words.update(re.findall(r"[^\W\d_]+", text.lower()))
    source = inspect.getsource(dates_it)
    words.update(re.findall(r"['\"]([^\W\d_]+)['\"]", source.lower()))
    return sorted(words)


class TestNoWordRaises(unittest.TestCase):
    def test_every_vocabulary_word_alone_does_not_raise(self):
        words = _vocabulary()
        self.assertGreater(len(words), 100)
        for word in words:
            with self.subTest(word=word):
                _extract(word)


# A number word is a clock hour only where a time can follow it.

@pytest.mark.parametrize("text,date,rest", [
    ("compra tre pani domani", datetime(2026, 10, 18), "compra tre pani"),
    ("domani ho dieci amici", datetime(2026, 10, 18), "ho dieci amici"),
    # words outside the date stay in the remainder as written
    ("lunedi compra due kili di pane", datetime(2026, 10, 19),
     "compra due kili di pane"),
    ("compra tre pani", None, None),
])
def test_a_count_of_things_is_not_an_hour(text, date, rest):
    res = _extract(text)
    if date is None:
        assert res is None
    else:
        assert res[0].replace(tzinfo=None) == date
        assert res[1] == rest


@pytest.mark.parametrize("text,expected", [
    ("alle tre", datetime(2026, 10, 17, 15)),
    _row("le tre", datetime(2026, 10, 17, 15), marks=ARTICLE_CLOCK),
    ("domani alle otto", datetime(2026, 10, 18, 8)),
    ("stasera alle otto", datetime(2026, 10, 17, 20)),
    ("alle tre del pomeriggio", datetime(2026, 10, 17, 15)),
    ("alle tre e mezza", datetime(2026, 10, 17, 15, 30)),
    ("tra tre ore", datetime(2026, 10, 17, 15)),
])
def test_spoken_clock_hours_are_still_read(text, expected):
    assert _dt(text) == expected


# "e" and "meno" join minutes to an hour.

@pytest.mark.parametrize("text,expected", [
    ("alle tre e un quarto", datetime(2026, 10, 17, 15, 15)),
    ("alle 3 e un quarto", datetime(2026, 10, 17, 15, 15)),
    _row("alle tre e tre quarti", datetime(2026, 10, 17, 15, 45),
         marks=_defect("https://github.com/TigreGotico/chronologia/issues/1032")),
    ("alle tre e venti", datetime(2026, 10, 17, 15, 20)),
    ("alle 3 e venti", datetime(2026, 10, 17, 15, 20)),
    ("alle tre e quindici", datetime(2026, 10, 17, 15, 15)),
    ("alle tre e mezza", datetime(2026, 10, 17, 15, 30)),
    ("domani alle otto e un quarto", datetime(2026, 10, 18, 8, 15)),
    ("stasera alle otto e un quarto", datetime(2026, 10, 17, 20, 15)),
])
def test_minutes_after_the_hour(text, expected):
    assert _dt(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("alle nove e cinque", datetime(2026, 10, 17, 21, 5)),
    ("alle tre e cinque", datetime(2026, 10, 17, 15, 5)),
    ("alle tre e due", datetime(2026, 10, 17, 15, 2)),
    ("alle 9 e 5", datetime(2026, 10, 17, 21, 5)),
    ("stasera alle nove e cinque", datetime(2026, 10, 17, 21, 5)),
    ("le sei e cinque di sera", datetime(2026, 10, 17, 18, 5)),
])
def test_single_digit_minutes_after_the_hour(text, expected):
    assert _dt(text) == expected
    assert _extract(text)[1].strip() in ("", "stasera")


@pytest.mark.parametrize("text,expected", [
    ("alle tre", datetime(2026, 10, 17, 15, 0)),
    ("alle nove", datetime(2026, 10, 17, 21, 0)),
    # a range answers its start
    _row("dalle 9 alle 11", datetime(2026, 10, 17, 21, 0), marks=HOUR_RANGE),
    ("alle sei meno cinque", datetime(2026, 10, 17, 17, 55)),
    ("alle 10 e 30", datetime(2026, 10, 17, 22, 30)),
    ("alle tre e mezza", datetime(2026, 10, 17, 15, 30)),
])
def test_single_digit_minutes_neighbours_unchanged(text, expected):
    assert _dt(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("domani mattina alle nove e cinque", datetime(2026, 10, 18, 9, 5)),
    ("domani mattina alle 9 e 5", datetime(2026, 10, 18, 9, 5)),
    ("domani mattina alle 9 e un quarto", datetime(2026, 10, 18, 9, 15)),
    ("lunedì mattina alle 8 e 15", datetime(2026, 10, 19, 8, 15)),
    ("oggi pomeriggio alle 3 e 20", datetime(2026, 10, 17, 15, 20)),
    ("domani pomeriggio alle 3 e 20", datetime(2026, 10, 18, 15, 20)),
    ("domani mattina alle 9:30", datetime(2026, 10, 18, 9, 30)),
])
def test_minutes_after_the_hour_with_a_part_of_the_day(text, expected):
    assert _dt(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("alle tre meno un quarto", datetime(2026, 10, 17, 14, 45)),
    ("alle tre meno dieci", datetime(2026, 10, 17, 14, 50)),
    ("alle tre meno venti", datetime(2026, 10, 17, 14, 40)),
    ("domani alle otto meno un quarto", datetime(2026, 10, 18, 7, 45)),
])
def test_minutes_before_the_hour(text, expected):
    assert _dt(text) == expected


@pytest.mark.parametrize("text", [
    "alle tre e un quarto", "alle tre e venti", "alle tre meno dieci"])
def test_minutes_leave_nothing_in_the_remainder(text):
    assert _extract(text)[1] == ""


@pytest.mark.parametrize("text,expected", [
    ("tra tre ore", datetime(2026, 10, 17, 15)),
    ("tra tre quarti ora", datetime(2026, 10, 17, 12, 45)),
    ("tra venti minuti", datetime(2026, 10, 17, 12, 20)),
    ("alle tre", datetime(2026, 10, 17, 15)),
])
def test_durations_are_unchanged(text, expected):
    assert _dt(text) == expected


@pytest.mark.parametrize("text", ["tre quarti", "un quarto"])
def test_a_fraction_without_an_hour_has_no_date(text):
    assert _extract(text) is None


def test_a_fraction_of_an_hour_with_d_ora():
    assert _dt("tra un quarto d'ora") == datetime(2026, 10, 17, 12, 15)
    assert _dt("tra tre quarti d'ora") == datetime(2026, 10, 17, 12, 45)


@pytest.mark.parametrize("text", [
    "meno dieci",
    _row("quanto fa 5 meno 2", marks=FALSE_POSITIVE),
    _row("quanto fa cinque meno due", marks=FALSE_POSITIVE),
    _row("dieci meno due", marks=FALSE_POSITIVE),
    "quanto fa",
])
def test_meno_without_a_clock_hour_has_no_time(text):
    assert _extract(text) is None


@pytest.mark.parametrize("text,expected", [
    ("alle dieci meno cinque", datetime(2026, 10, 17, 21, 55)),
    ("le tre meno un quarto", datetime(2026, 10, 17, 14, 45)),
    pytest.param("stasera dieci meno un quarto",
                 datetime(2026, 10, 17, 21, 45),
                 marks=DAYPART_THEN_MENO),
    ("ore 3 meno 10", datetime(2026, 10, 17, 14, 50)),
])
def test_meno_after_a_clock_hour(text, expected):
    assert _dt(text) == expected


def test_midnight_less_minutes_is_ten_to_midnight():
    assert _dt("alle 0 meno 10") == datetime(2026, 10, 17, 23, 50)


@pytest.mark.parametrize("text,expected", [
    ("un quarto d'ora fa", datetime(2026, 10, 17, 11, 45)),
    _row("tre quarti d'ora fa", datetime(2026, 10, 17, 11, 15),
         marks=_defect("https://github.com/TigreGotico/chronologia/issues/1032")),
    ("tre ore fa", datetime(2026, 10, 17, 9)),
    ("venti minuti fa", datetime(2026, 10, 17, 11, 40)),
    _row("mezzora fa", datetime(2026, 10, 17, 11, 30),
         marks=_defect("https://github.com/TigreGotico/chronologia/issues/1032")),
    # a counted offset keeps the anchor clock (class 1)
    ("due giorni fa", datetime(2026, 10, 15, 12)),
    ("dieci giorni fa", datetime(2026, 10, 7, 12)),
    ("una settimana fa", datetime(2026, 10, 10, 12)),
])
def test_hours_minutes_and_fractions_ago(text, expected):
    assert _dt(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("tra un quarto d'ora", datetime(2026, 10, 17, 12, 15)),
    ("tra tre ore", datetime(2026, 10, 17, 15)),
    ("tra venti minuti", datetime(2026, 10, 17, 12, 20)),
    # a counted offset keeps the anchor clock (class 1)
    ("tra due giorni", datetime(2026, 10, 19, 12)),
    ("tra tre giorni", datetime(2026, 10, 20, 12)),
])
def test_the_same_durations_ahead_are_unchanged(text, expected):
    assert _dt(text) == expected


@pytest.mark.parametrize("text", [
    "dal 10 al 15 marzo", "il 12 15 marzo", "ho speso 20 e 30 euro",
    "1, 1, 31, 13, 22, 3", "10 20 30 40", "3 3 3"])
def test_sentences_with_two_numbers_do_not_raise(text):
    _extract(text)


@pytest.mark.parametrize("text,expected", [
    ("alle 3 30", datetime(2026, 10, 17, 15, 30)),
    ("domani alle 8 15", datetime(2026, 10, 18, 8, 15)),
])
@HOUR_SPACE_MINUTES
def test_two_digit_groups_join_after_a_clock_marker(text, expected):
    assert _dt(text) == expected


def test_two_digit_groups_do_not_join_after_a_date():
    res = _extract("dal 10 al 15 marzo")
    assert (res[0].hour, res[0].minute) != (22, 15)


def test_a_range_reads_as_its_start():
    # a stretch of time answers when it starts
    assert _dt("dal 10 al 15 marzo") == datetime(2027, 3, 10)
    assert _extract("dal 10 al 15 marzo")[1] == ""


@FALSE_POSITIVE
def test_a_malformed_date_has_no_date():
    assert _extract("il 12 15 marzo") is None


@FALSE_POSITIVE
def test_two_amounts_are_no_time():
    assert _extract("ho speso 20 e 30 euro") is None


def test_a_single_date_is_unchanged():
    assert _dt("il 15 marzo") == datetime(2027, 3, 15)


# "il" before a number names that day of the month. A named day keeps the
# spoken hour (ruling 17), so "il 3 alle 5" is 05:00 on 3 November.
@pytest.mark.parametrize("text,expected", [
    ("il 3 alle 5", datetime(2026, 11, 3, 5)),
    ("il 20 alle 8", datetime(2026, 10, 20, 8)),
    ("il 3", datetime(2026, 11, 3)),
])
@_defect("https://github.com/TigreGotico/chronologia/issues/1035")
def test_il_followed_by_a_number_is_that_day_of_the_month(text, expected):
    assert _dt(text) == expected


@pytest.mark.parametrize("text,expected", [
    _row("il 3 novembre alle 5", datetime(2026, 11, 3, 5),
         marks=_defect("https://github.com/TigreGotico/chronologia/issues/1034")),
    ("il 15 marzo", datetime(2027, 3, 15)),
])
def test_dates_with_a_month(text, expected):
    assert _dt(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("ci sono 10 persone domani", datetime(2026, 10, 18)),
    ("domani ho 10 amici", datetime(2026, 10, 18)),
])
def test_a_count_before_a_plain_word_is_no_hour(text, expected):
    assert _dt(text) == expected


def test_a_count_with_no_date_is_no_date():
    assert _extract("ci sono 10 persone") is None


@pytest.mark.parametrize("text,expected", [
    ("alle 10", datetime(2026, 10, 17, 22)),
    ("domani 10 di mattina", datetime(2026, 10, 18, 10)),
    _row("stasera 10", datetime(2026, 10, 17, 22), marks=DAYPART_THEN_CLOCK),
    ("domani alle 10 di sera", datetime(2026, 10, 18, 22)),
    ("alle 10 e mezza", datetime(2026, 10, 17, 22, 30)),
])
def test_clock_hours_are_still_read(text, expected):
    assert _dt(text) == expected


# A bare number is an hour only after alle, le, alla or ore, or in a sentence
# with a part of the day, and only one number is the hour.

@pytest.mark.parametrize("text", [
    "siamo in 10", "ne voglio 3", "siamo in dieci", "10"])
def test_a_bare_number_is_no_hour(text):
    assert _extract(text) is None


# A bare hour inside a sentence with no clock marker is no clock (ruling 2):
# the day word alone is the date and the number is left over.
@pytest.mark.parametrize("text,expected", [
    ("domani 10", [datetime(2026, 10, 18), "10"]),
    ("lunedì 8", [datetime(2026, 10, 19), "8"]),
])
def test_a_bare_number_after_a_day_word_is_no_hour(text, expected):
    res = _extract(text)
    assert [res[0].replace(tzinfo=None), res[1]] == expected


@pytest.mark.parametrize("text,expected", [
    ("stasera alle 9 in 4", datetime(2026, 10, 17, 21)),
    ("alle 9 siamo in 4", datetime(2026, 10, 17, 21)),
])
def test_a_second_number_does_not_replace_the_hour(text, expected):
    assert _dt(text) == expected


@pytest.mark.parametrize("text,expected", [
    _row("stasera 10", datetime(2026, 10, 17, 22), marks=DAYPART_THEN_CLOCK),
    ("stasera alle 9", datetime(2026, 10, 17, 21)),
])
def test_a_part_of_the_day_still_names_the_hour(text, expected):
    assert _dt(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("il treno delle 8", datetime(2026, 10, 17, 20)),
    ("dalle 9", datetime(2026, 10, 17, 21)),
])
@ARTICLE_CLOCK
def test_delle_and_dalle_name_a_clock_hour(text, expected):
    assert _dt(text) == expected


@HOUR_RANGE
def test_a_range_of_hours_reads_as_its_start():
    assert _dt("dalle 9 alle 11") == datetime(2026, 10, 17, 21)


def test_a_count_before_alle_does_not_suppress_the_hour():
    assert _dt("ne prendo 2 alle 5") == datetime(2026, 10, 17, 17)


def test_a_count_after_a_day_word_stays_a_count():
    assert _dt("domani 10 persone") == datetime(2026, 10, 18)


@pytest.mark.parametrize("text", ["siamo in 10", "ne voglio 3"])
def test_a_count_alone_is_no_date(text):
    assert _extract(text) is None
