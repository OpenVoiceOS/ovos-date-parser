"""Regression tests: "último" before a weekday name in es.

On its own "el último viernes" is the most recent Friday, as "el viernes
pasado". Followed by a period ("del mes", "de octubre") it is the last Friday
of that period. Expected datetimes are hand-derived from the fixed anchor,
Saturday 17 October 2026, never pinned from engine output.
"""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


def _dt(text):
    res = extract_datetime(text, lang="es-ES", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    return res[0].replace(tzinfo=None)


# the most recent occurrence before Saturday 17 October 2026
RECENT = {
    "lunes": datetime(2026, 10, 12),
    "martes": datetime(2026, 10, 13),
    "miércoles": datetime(2026, 10, 14),
    "jueves": datetime(2026, 10, 15),
    "viernes": datetime(2026, 10, 16),
    "sábado": datetime(2026, 10, 10),
    "domingo": datetime(2026, 10, 11),
}


class TestUltimoWeekday(unittest.TestCase):
    def test_most_recent_weekday(self):
        for day, expected in RECENT.items():
            for text in ("el último %s" % day, "último %s" % day):
                with self.subTest(text=text):
                    self.assertEqual(_dt(text), expected)

    def test_inside_question(self):
        self.assertEqual(_dt("qué hice el último viernes"),
                         datetime(2026, 10, 16))

    def test_last_weekday_of_the_month(self):
        for text in ("el último viernes del mes",
                     "el último viernes de este mes",
                     "el último viernes de octubre"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), datetime(2026, 10, 30))
        self.assertEqual(_dt("el último lunes del mes"),
                         datetime(2026, 10, 26))
        self.assertEqual(_dt("el último sábado de octubre"),
                         datetime(2026, 10, 31))
        self.assertEqual(_dt("el último domingo de este mes"),
                         datetime(2026, 10, 25))

    def test_last_weekday_of_a_later_month(self):
        self.assertEqual(_dt("el último viernes de noviembre"),
                         datetime(2026, 11, 27))

    def test_last_weekday_of_a_month_already_past_is_next_year(self):
        self.assertEqual(_dt("el último viernes de enero"),
                         datetime(2027, 1, 29))


class TestUltimoWeekdayConfusables(unittest.TestCase):
    def test_other_forms_of_the_previous_friday(self):
        for text in ("el viernes pasado", "el pasado viernes"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), datetime(2026, 10, 16))

    def test_coming_friday_unchanged(self):
        for text in ("el viernes", "el siguiente viernes",
                     "el próximo viernes", "el viernes que viene"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), datetime(2026, 10, 23))

    def test_last_period_unchanged(self):
        self.assertEqual(_dt("el último mes"), datetime(2026, 9, 17))
        self.assertEqual(_dt("el último año"), datetime(2025, 10, 17))
        self.assertEqual(_dt("la última semana"), datetime(2026, 10, 10))


class TestLastWeekdayOfOtherPeriods(unittest.TestCase):
    def _all(self, texts, expected):
        for text in texts:
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_next_month(self):
        self._all(["el último viernes del mes que viene",
                   "el último viernes del próximo mes",
                   "el último viernes del mes siguiente"],
                  datetime(2026, 11, 27))

    def test_previous_month(self):
        self._all(["el último viernes del mes pasado"],
                  datetime(2026, 9, 25))

    def test_whole_year(self):
        self._all(["el último viernes del año", "el último viernes de 2026"],
                  datetime(2026, 12, 25))

    def test_month_and_year(self):
        self._all(["el último viernes de noviembre de 2027"],
                  datetime(2027, 11, 26))

    def test_without_the_accent(self):
        self._all(["el ultimo viernes"], datetime(2026, 10, 16))
        self._all(["el ultimo viernes del mes"], datetime(2026, 10, 30))

    def test_only_the_understood_words_leave_the_sentence(self):
        res = extract_datetime("el último viernes del mes que viene",
                               lang="es-ES", anchorDate=ANCHOR)
        self.assertEqual(res[1], "el")


class TestLastWeekdayOfAShiftedYear(unittest.TestCase):
    def test_last_weekday_of_next_and_last_year(self):
        for text, expected in (
                ("el último viernes del año que viene",
                 datetime(2027, 12, 31)),
                ("el último viernes del año siguiente",
                 datetime(2027, 12, 31)),
                ("el último viernes del año pasado", datetime(2025, 12, 26)),
                ("el último viernes del año", datetime(2026, 12, 25))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_a_month_of_a_shifted_year(self):
        for text, expected in (
                ("el último viernes de noviembre del año que viene",
                 datetime(2027, 11, 26)),
                ("el último viernes de octubre del año pasado",
                 datetime(2025, 10, 31))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_only_the_understood_words_leave_the_sentence_again(self):
        res = extract_datetime("el último viernes del año que viene",
                               lang="es-ES", anchorDate=ANCHOR)
        self.assertEqual(res[1], "el")


class TestLastWeekdayOfAGivenYear(unittest.TestCase):
    def test_last_friday_of_a_year_given_in_digits(self):
        res = extract_datetime("el último viernes del año 2027",
                               lang="es-ES", anchorDate=ANCHOR)
        self.assertEqual(res[0].replace(tzinfo=None), datetime(2027, 12, 31))
        self.assertEqual(res[1], "el")

    def test_a_month_of_a_year_given_with_the_word_year(self):
        self.assertEqual(_dt("el último viernes de octubre del año 2027"),
                         datetime(2027, 10, 29))


class TestLastWeekdayWithAPrefixedYearOrNamedMonth(unittest.TestCase):
    def _all(self, texts, expected):
        for text in texts:
            with self.subTest(text=text):
                res = extract_datetime(text, lang="es-ES", anchorDate=ANCHOR)
                self.assertEqual(res[0].replace(tzinfo=None), expected)
                self.assertEqual(res[1], "el")

    def test_prefixed_next_year(self):
        self._all(["el último viernes del próximo año",
                   "el último viernes del proximo año",
                   "el último viernes del siguiente año",
                   "el ultimo viernes del siguiente año"],
                  datetime(2027, 12, 31))

    def test_month_introduced_by_the_word_month(self):
        self._all(["el último viernes del mes de noviembre"],
                  datetime(2026, 11, 27))

    def test_month_of_a_year_after_the_word_month(self):
        self._all(["el último viernes del mes de octubre del año que viene"],
                  datetime(2027, 10, 29))
