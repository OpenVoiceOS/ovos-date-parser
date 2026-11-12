"""Regression tests: next and last week, month and year in es.

Expected datetimes are hand-derived from the fixed anchor, Saturday
17 October 2026, never pinned from engine output. A month or a year away
keeps the day of the month, as "en 1 mes" does.
"""
import unicodedata
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


def _fold(text):
    """Text without accents, so remainders compare the same with or
    without accent restoration."""
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if not unicodedata.combining(c))


def _dt(text):
    res = extract_datetime(text, lang="es-ES", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    return res[0].replace(tzinfo=None)


class TestNextAndLastPeriod(unittest.TestCase):
    def _all(self, texts, expected):
        for text in texts:
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_next_week(self):
        self._all(["la próxima semana", "próxima semana", "la semana próxima",
                   "la semana que viene", "la semana siguiente"],
                  datetime(2026, 10, 24))

    def test_next_month(self):
        self._all(["el próximo mes", "próximo mes", "el mes próximo",
                   "el mes que viene", "el mes siguiente"],
                  datetime(2026, 11, 17))

    def test_next_year(self):
        self._all(["el próximo año", "próximo año", "el año próximo",
                   "el año que viene", "el año siguiente"],
                  datetime(2027, 10, 17))

    def test_last_month(self):
        self._all(["el mes pasado", "el último mes", "el mes anterior"],
                  datetime(2026, 9, 17))

    def test_last_year(self):
        self._all(["el año pasado", "el último año", "el año anterior"],
                  datetime(2025, 10, 17))

    def test_inside_sentence(self):
        self.assertEqual(_dt("qué haremos el mes que viene"),
                         datetime(2026, 11, 17))
        self.assertEqual(_dt("cuándo es la próxima semana"),
                         datetime(2026, 10, 24))
        self.assertEqual(_dt("viajamos el año que viene"),
                         datetime(2027, 10, 17))


class TestNextAndLastPeriodConfusables(unittest.TestCase):
    def test_counted_periods_unchanged(self):
        self.assertEqual(_dt("en 1 mes"), datetime(2026, 11, 17))
        self.assertEqual(_dt("hace 1 mes"), datetime(2026, 9, 17))
        self.assertEqual(_dt("hace 1 año"), datetime(2025, 10, 17))
        self.assertEqual(_dt("hace 2 semanas"), datetime(2026, 10, 3))

    def test_weeks_and_weekdays_unchanged(self):
        self.assertEqual(_dt("la semana pasada"), datetime(2026, 10, 10))
        self.assertEqual(_dt("el próximo viernes"), datetime(2026, 10, 23))
        self.assertEqual(_dt("el viernes que viene"), datetime(2026, 10, 23))
        self.assertEqual(_dt("el siguiente viernes"), datetime(2026, 10, 23))
        self.assertEqual(_dt("el viernes de la semana que viene"),
                         datetime(2026, 10, 23))

    def test_marker_alone_has_no_date(self):
        for text in ("el próximo", "el mes", "el año"):
            with self.subTest(text=text):
                self.assertIsNone(extract_datetime(
                    text, lang="es-ES", anchorDate=ANCHOR))


FRIDAY = datetime(2026, 10, 16, 10, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


class TestNextOnTheSameWeekday(unittest.TestCase):
    def test_next_saturday_from_a_saturday(self):
        for text in ("el próximo sábado", "el sábado próximo",
                     "el siguiente sábado", "el sábado que viene"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), datetime(2026, 10, 24))

    def test_next_friday_from_a_friday(self):
        for text in ("el próximo viernes", "el viernes próximo",
                     "el siguiente viernes", "el viernes que viene"):
            with self.subTest(text=text):
                res = extract_datetime(text, lang="es-ES", anchorDate=FRIDAY)
                self.assertEqual(res[0].replace(tzinfo=None),
                                 datetime(2026, 10, 23))
                self.assertEqual(res[1], "el")


class TestRemainder(unittest.TestCase):
    def test_words_around_the_phrase_are_kept(self):
        for text, rest in (
                ("recuérdame el mes que viene comprar pan",
                 "recuerdame comprar pan"),
                ("recuérdame el año que viene comprar pan",
                 "recuerdame comprar pan"),
                ("recuérdame la próxima semana comprar pan",
                 "recuerdame comprar pan"),
                ("recuérdame el mes pasado comprar pan",
                 "recuerdame comprar pan")):
            with self.subTest(text=text):
                res = extract_datetime(text, lang="es-ES", anchorDate=ANCHOR)
                self.assertEqual(_fold(res[1]), rest)

    def test_nothing_is_left_of_a_bare_phrase(self):
        for text in ("el mes que viene", "el año siguiente",
                     "el mes pasado", "la semana próxima"):
            with self.subTest(text=text):
                res = extract_datetime(text, lang="es-ES", anchorDate=ANCHOR)
                self.assertNotIn("siguiente", res[1])
                self.assertNotIn("viene", res[1])
                self.assertNotIn("pasado", res[1])


class TestMonthNamedAfterMes(unittest.TestCase):
    def test_first_day_of_the_named_month(self):
        for text, expected in (
                ("el próximo mes de diciembre", datetime(2026, 12, 1)),
                ("el mes de diciembre", datetime(2026, 12, 1)),
                ("el mes de enero", datetime(2027, 1, 1)),
                ("el último mes del año", datetime(2026, 12, 1))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_months_without_a_name_are_unchanged(self):
        self.assertEqual(_dt("el próximo mes"), datetime(2026, 11, 17))
        self.assertEqual(_dt("el mes pasado"), datetime(2026, 9, 17))
        self.assertEqual(_dt("en 2 meses"), datetime(2026, 12, 17))


class TestWeekdayOfNextWeek(unittest.TestCase):
    """The Monday-based week after the anchor's week, anchored on every day
    of the week of Monday 19 October 2026."""

    def _on_each_day(self, text, expected):
        for offset in range(7):
            anchor = datetime(2026, 10, 19, 12, 0,
                              tzinfo=ZoneInfo("Europe/Lisbon")) + \
                timedelta(days=offset)
            with self.subTest(text=text, anchor=anchor.strftime("%a %d")):
                res = extract_datetime(text, lang="es-ES", anchorDate=anchor)
                self.assertEqual(res[0].replace(tzinfo=None), expected)
                self.assertNotIn("semana", res[1])
                self.assertNotIn("proxima", _fold(res[1]))

    def test_friday_of_the_next_week(self):
        for text in ("el viernes de la próxima semana",
                     "el viernes de la semana próxima",
                     "el viernes de la semana que viene"):
            self._on_each_day(text, datetime(2026, 10, 30))

    def test_monday_of_the_next_week(self):
        self._on_each_day("el lunes de la próxima semana",
                          datetime(2026, 10, 26))

    def test_a_weekday_with_a_trailing_next_is_unchanged(self):
        wednesday = datetime(2026, 10, 21, 12, 0,
                             tzinfo=ZoneInfo("Europe/Lisbon"))
        res = extract_datetime("el viernes próximo", lang="es-ES",
                               anchorDate=wednesday)
        self.assertEqual(res[0].replace(tzinfo=None), datetime(2026, 10, 23))


class TestNextMonthNamedAsTheCurrentMonth(unittest.TestCase):
    def test_october_said_in_october_is_next_year(self):
        self.assertEqual(_dt("el próximo mes de octubre"),
                         datetime(2027, 10, 1))

    def test_december_said_in_december_is_next_year(self):
        december = datetime(2026, 12, 15, 12, 0,
                            tzinfo=ZoneInfo("Europe/Lisbon"))
        res = extract_datetime("el próximo mes de diciembre", lang="es-ES",
                               anchorDate=december)
        self.assertEqual(res[0].replace(tzinfo=None), datetime(2027, 12, 1))

    def test_a_later_month_stays_in_this_year(self):
        self.assertEqual(_dt("el próximo mes de diciembre"),
                         datetime(2026, 12, 1))

    def test_an_earlier_month_is_next_year(self):
        self.assertEqual(_dt("el próximo mes de marzo"),
                         datetime(2027, 3, 1))

    def test_the_month_without_a_next_marker_is_unchanged(self):
        self.assertEqual(_dt("el mes de octubre"), datetime(2026, 10, 1))
