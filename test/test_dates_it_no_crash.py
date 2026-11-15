"""Regression tests: Italian sentences with "presto" and "tardi".

Without an hour in the sentence the two words set nothing, so "è tardi" has
no date. After an hour they move it by one. Expected datetimes are
hand-derived from the fixed anchor, Saturday 17 October 2026 12:00.
"""
import inspect
import json
import re
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import ovos_date_parser
from ovos_date_parser import dates_it, extract_datetime

ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


def _extract(text):
    return extract_datetime(text, lang="it-IT", anchorDate=ANCHOR)


def _dt(text):
    res = _extract(text)
    assert res is not None, "no datetime extracted from %r" % text
    return res[0].replace(tzinfo=None)


class TestPrestoTardiWithoutAnHour(unittest.TestCase):
    def test_sentences_without_a_date_are_none(self):
        for text in ("è tardi", "si è fatto tardi", "è troppo presto",
                     "è ancora presto", "presto", "tardi", "più tardi",
                     "a più tardi", "ci vediamo più tardi", "arrivo tardi",
                     "perché è tardi"):
            with self.subTest(text=text):
                self.assertIsNone(_extract(text))

    def test_a_date_beside_them_is_still_read(self):
        self.assertEqual(_dt("domani è tardi"), datetime(2026, 10, 18))
        self.assertEqual(_dt("domani presto"), datetime(2026, 10, 18))


class TestPrestoTardiAfterAnHour(unittest.TestCase):
    def test_tardi_moves_the_hour_on(self):
        self.assertEqual(_dt("alle 8 di sera"), datetime(2026, 10, 17, 20))
        self.assertEqual(_dt("alle 8 di sera tardi"),
                         datetime(2026, 10, 17, 21))

    def test_presto_moves_the_hour_back(self):
        self.assertEqual(_dt("domani alle 7"), datetime(2026, 10, 18, 7))
        self.assertEqual(_dt("domani alle 7 presto"),
                         datetime(2026, 10, 18, 6))

    def test_either_word_before_the_hour_changes_nothing(self):
        self.assertEqual(_dt("domani presto alle 7"),
                         datetime(2026, 10, 18, 7))
        self.assertEqual(_dt("domani tardi alle 7"),
                         datetime(2026, 10, 18, 7))


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


class TestNumberWordThatIsNotAnHour(unittest.TestCase):
    """A number word is a clock hour only where a time can follow it."""

    def test_a_count_of_things_is_not_an_hour(self):
        for text, date, rest in (
                ("compra tre pani domani", datetime(2026, 10, 18),
                 "compra tre pani"),
                ("domani ho dieci amici", datetime(2026, 10, 18),
                 "ho dieci amici"),
                ("lunedi compra due kili di pane", datetime(2026, 10, 19),
                 "compra due kili pane"),
                ("compra tre pani", None, None)):
            with self.subTest(text=text):
                res = _extract(text)
                if date is None:
                    self.assertIsNone(res)
                else:
                    self.assertEqual(res[0].replace(tzinfo=None), date)
                    self.assertEqual(res[1], rest)

    def test_spoken_clock_hours_are_still_read(self):
        for text, expected in (
                ("alle tre", datetime(2026, 10, 17, 15)),
                ("le tre", datetime(2026, 10, 17, 15)),
                ("domani alle otto", datetime(2026, 10, 18, 8)),
                ("stasera alle otto", datetime(2026, 10, 17, 20)),
                ("alle tre del pomeriggio", datetime(2026, 10, 17, 15)),
                ("alle tre e mezza", datetime(2026, 10, 17, 15, 30)),
                ("tra tre ore", datetime(2026, 10, 17, 15))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)


class TestMinutesAroundTheHour(unittest.TestCase):
    """"e" and "meno" join minutes to an hour."""

    def test_minutes_after_the_hour(self):
        for text, expected in (
                ("alle tre e un quarto", datetime(2026, 10, 17, 15, 15)),
                ("alle 3 e un quarto", datetime(2026, 10, 17, 15, 15)),
                ("alle tre e tre quarti", datetime(2026, 10, 17, 15, 45)),
                ("alle tre e venti", datetime(2026, 10, 17, 15, 20)),
                ("alle 3 e venti", datetime(2026, 10, 17, 15, 20)),
                ("alle tre e quindici", datetime(2026, 10, 17, 15, 15)),
                ("alle tre e mezza", datetime(2026, 10, 17, 15, 30)),
                ("domani alle otto e un quarto", datetime(2026, 10, 18, 8, 15)),
                ("stasera alle otto e un quarto",
                 datetime(2026, 10, 17, 20, 15))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_single_digit_minutes_after_the_hour(self):
        for text, expected in (
                ("alle nove e cinque", datetime(2026, 10, 17, 21, 5)),
                ("alle tre e cinque", datetime(2026, 10, 17, 15, 5)),
                ("alle tre e due", datetime(2026, 10, 17, 15, 2)),
                ("alle 9 e 5", datetime(2026, 10, 17, 21, 5)),
                ("stasera alle nove e cinque", datetime(2026, 10, 17, 21, 5)),
                ("le sei e cinque di sera", datetime(2026, 10, 17, 18, 5))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)
                self.assertEqual(_extract(text)[1].strip() in ("", "stasera"),
                                 True)

    def test_single_digit_minutes_neighbours_unchanged(self):
        for text, expected in (
                ("alle tre", datetime(2026, 10, 17, 15, 0)),
                ("alle nove", datetime(2026, 10, 17, 21, 0)),
                ("dalle 9 alle 11", datetime(2026, 10, 17, 23, 0)),
                ("alle sei meno cinque", datetime(2026, 10, 17, 17, 55)),
                ("alle 10 e 30", datetime(2026, 10, 17, 22, 30)),
                ("alle tre e mezza", datetime(2026, 10, 17, 15, 30))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_minutes_after_the_hour_with_a_part_of_the_day(self):
        for text, expected in (
                ("domani mattina alle nove e cinque",
                 datetime(2026, 10, 18, 9, 5)),
                ("domani mattina alle 9 e 5", datetime(2026, 10, 18, 9, 5)),
                ("domani mattina alle 9 e un quarto",
                 datetime(2026, 10, 18, 9, 15)),
                ("lunedì mattina alle 8 e 15", datetime(2026, 10, 19, 8, 15)),
                ("oggi pomeriggio alle 3 e 20", datetime(2026, 10, 17, 15, 20)),
                ("domani pomeriggio alle 3 e 20",
                 datetime(2026, 10, 18, 15, 20)),
                ("domani mattina alle 9:30", datetime(2026, 10, 18, 9, 30))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_minutes_before_the_hour(self):
        for text, expected in (
                ("alle tre meno un quarto", datetime(2026, 10, 17, 14, 45)),
                ("alle tre meno dieci", datetime(2026, 10, 17, 14, 50)),
                ("alle tre meno venti", datetime(2026, 10, 17, 14, 40)),
                ("domani alle otto meno un quarto",
                 datetime(2026, 10, 18, 7, 45))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_minutes_leave_nothing_in_the_remainder(self):
        for text in ("alle tre e un quarto", "alle tre e venti",
                     "alle tre meno dieci"):
            with self.subTest(text=text):
                self.assertEqual(_extract(text)[1], "")

    def test_durations_are_unchanged(self):
        self.assertEqual(_dt("tra tre ore"), datetime(2026, 10, 17, 15))
        self.assertEqual(_dt("tra tre quarti ora"),
                         datetime(2026, 10, 17, 12, 45))
        self.assertEqual(_dt("tra venti minuti"),
                         datetime(2026, 10, 17, 12, 20))
        self.assertEqual(_dt("alle tre"), datetime(2026, 10, 17, 15))

    def test_a_fraction_without_an_hour_has_no_date(self):
        for text in ("tre quarti", "un quarto"):
            with self.subTest(text=text):
                self.assertIsNone(_extract(text))

    def test_a_fraction_of_an_hour_with_d_ora(self):
        self.assertEqual(_dt("tra un quarto d'ora"),
                         datetime(2026, 10, 17, 12, 15))
        self.assertEqual(_dt("tra tre quarti d'ora"),
                         datetime(2026, 10, 17, 12, 45))


class TestArithmeticIsNotATime(unittest.TestCase):
    def test_meno_without_a_clock_hour_has_no_time(self):
        for text in ("meno dieci", "quanto fa 5 meno 2",
                     "quanto fa cinque meno due", "dieci meno due",
                     "quanto fa"):
            with self.subTest(text=text):
                self.assertIsNone(_extract(text))

    def test_meno_after_a_clock_hour(self):
        self.assertEqual(_dt("alle dieci meno cinque"),
                         datetime(2026, 10, 17, 21, 55))
        self.assertEqual(_dt("le tre meno un quarto"),
                         datetime(2026, 10, 17, 14, 45))
        self.assertEqual(_dt("stasera dieci meno un quarto"),
                         datetime(2026, 10, 17, 21, 45))
        self.assertEqual(_dt("ore 3 meno 10"), datetime(2026, 10, 17, 14, 50))

    def test_midnight_less_minutes_is_ten_to_midnight(self):
        self.assertEqual(_dt("alle 0 meno 10"), datetime(2026, 10, 17, 23, 50))



class TestAgoAfterADuration(unittest.TestCase):
    def test_hours_minutes_and_fractions_ago(self):
        for text, expected in (
                ("un quarto d'ora fa", datetime(2026, 10, 17, 11, 45)),
                ("tre quarti d'ora fa", datetime(2026, 10, 17, 11, 15)),
                ("tre ore fa", datetime(2026, 10, 17, 9)),
                ("venti minuti fa", datetime(2026, 10, 17, 11, 40)),
                ("mezzora fa", datetime(2026, 10, 17, 11, 30)),
                ("due giorni fa", datetime(2026, 10, 15)),
                ("dieci giorni fa", datetime(2026, 10, 7)),
                ("una settimana fa", datetime(2026, 10, 10))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_the_same_durations_ahead_are_unchanged(self):
        for text, expected in (
                ("tra un quarto d'ora", datetime(2026, 10, 17, 12, 15)),
                ("tra tre ore", datetime(2026, 10, 17, 15)),
                ("tra venti minuti", datetime(2026, 10, 17, 12, 20)),
                ("tra due giorni", datetime(2026, 10, 19)),
                ("tra tre giorni", datetime(2026, 10, 20))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)


class TestTwoNumbersInARowDoNotRaise(unittest.TestCase):
    def test_sentences_with_two_numbers_do_not_raise(self):
        for text in ("dal 10 al 15 marzo", "il 12 15 marzo",
                     "ho speso 20 e 30 euro", "1, 1, 31, 13, 22, 3",
                     "10 20 30 40", "3 3 3"):
            with self.subTest(text=text):
                _extract(text)

    def test_two_digit_groups_join_only_after_a_clock_marker(self):
        self.assertEqual(_dt("alle 3 30"), datetime(2026, 10, 17, 15, 30))
        self.assertEqual(_dt("domani alle 8 15"), datetime(2026, 10, 18, 8, 15))
        res = _extract("dal 10 al 15 marzo")
        self.assertNotEqual((res[0].hour, res[0].minute), (22, 15))


class TestTwoNumbersInARow(unittest.TestCase):
    def test_a_range_reads_as_its_last_date(self):
        self.assertEqual(_dt("dal 10 al 15 marzo"), datetime(2027, 3, 15))
        self.assertEqual(_extract("dal 10 al 15 marzo")[1], "")

    def test_a_malformed_date_has_no_date(self):
        self.assertIsNone(_extract("il 12 15 marzo"))

    def test_two_amounts_are_no_time(self):
        self.assertIsNone(_extract("ho speso 20 e 30 euro"))

    def test_single_dates_and_clock_times_are_unchanged(self):
        self.assertEqual(_dt("il 15 marzo"), datetime(2027, 3, 15))
        self.assertEqual(_dt("alle 3 30"), datetime(2026, 10, 17, 15, 30))


class TestDayOfTheMonthAndCounts(unittest.TestCase):
    def test_il_followed_by_a_number_is_that_day_of_the_month(self):
        self.assertEqual(_dt("il 3 alle 5"), datetime(2026, 11, 3, 17))
        self.assertEqual(_dt("il 20 alle 8"), datetime(2026, 10, 20, 20))
        self.assertEqual(_dt("il 3"), datetime(2026, 11, 3))

    def test_dates_with_a_month_are_unchanged(self):
        self.assertEqual(_dt("il 3 novembre alle 5"),
                         datetime(2026, 11, 3, 17))
        self.assertEqual(_dt("il 15 marzo"), datetime(2027, 3, 15))

    def test_a_count_before_a_plain_word_is_no_hour(self):
        for text, expected in (
                ("ci sono 10 persone domani", datetime(2026, 10, 18)),
                ("domani ho 10 amici", datetime(2026, 10, 18))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)
        self.assertIsNone(_extract("ci sono 10 persone"))

    def test_clock_hours_are_still_read(self):
        for text, expected in (
                ("alle 10", datetime(2026, 10, 17, 22)),
                ("domani 10 di mattina", datetime(2026, 10, 18, 10)),
                ("stasera 10", datetime(2026, 10, 17, 22)),
                ("domani alle 10 di sera", datetime(2026, 10, 18, 22)),
                ("alle 10 e mezza", datetime(2026, 10, 17, 22, 30))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)


class TestBareNumberAtTheEnd(unittest.TestCase):
    """A bare number is an hour only after alle, le, alla or ore, or in a
    sentence with a part of the day, and only one number is the hour."""

    def test_a_bare_number_is_no_hour(self):
        for text in ("siamo in 10", "ne voglio 3", "siamo in dieci", "10"):
            with self.subTest(text=text):
                self.assertIsNone(_extract(text))
        self.assertEqual(_dt("domani 10"), datetime(2026, 10, 18, 10))

    def test_a_second_number_does_not_replace_the_hour(self):
        self.assertEqual(_dt("stasera alle 9 in 4"),
                         datetime(2026, 10, 17, 21))
        self.assertEqual(_dt("alle 9 siamo in 4"), datetime(2026, 10, 17, 21))

    def test_a_part_of_the_day_still_names_the_hour(self):
        self.assertEqual(_dt("stasera 10"), datetime(2026, 10, 17, 22))
        self.assertEqual(_dt("stasera alle 9"), datetime(2026, 10, 17, 21))


class TestClockPrepositionsAndDayHours(unittest.TestCase):
    def test_delle_and_dalle_name_a_clock_hour(self):
        self.assertEqual(_dt("il treno delle 8"), datetime(2026, 10, 17, 20))
        self.assertEqual(_dt("dalle 9"), datetime(2026, 10, 17, 21))

    def test_a_range_reads_as_its_last_time(self):
        # as "from 3pm to 5pm" in English; the last hour reads as it does alone
        self.assertEqual(_dt("dalle 9 alle 11"), _dt("alle 11"))
        self.assertEqual(_dt("dalle 9 alle 11"), datetime(2026, 10, 17, 23))

    def test_a_count_before_alle_does_not_suppress_the_hour(self):
        self.assertEqual(_dt("ne prendo 2 alle 5"), datetime(2026, 10, 17, 17))

    def test_a_bare_number_after_a_day_word_is_an_hour(self):
        res = _extract("lunedì 8")
        self.assertEqual((res[0].replace(tzinfo=None), res[1]),
                         (datetime(2026, 10, 19, 8), ""))
        self.assertEqual(_dt("domani 10"), datetime(2026, 10, 18, 10))

    def test_a_count_after_a_day_word_stays_a_count(self):
        self.assertEqual(_dt("domani 10 persone"), datetime(2026, 10, 18))
        for text in ("siamo in 10", "ne voglio 3"):
            with self.subTest(text=text):
                self.assertIsNone(_extract(text))
