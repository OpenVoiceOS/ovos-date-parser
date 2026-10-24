"""Regression tests: "siguiente" before a weekday name in es.

"el siguiente viernes" is the coming Friday, the same day as "el próximo
viernes" and "el viernes que viene". Expected datetimes are hand-derived from
the fixed anchor, Saturday 17 October 2026, never pinned from engine output.
"""
import unicodedata
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=ZoneInfo("Europe/Lisbon"))

# the first occurrence after Saturday 17 October 2026
COMING = {
    "lunes": datetime(2026, 10, 19),
    "martes": datetime(2026, 10, 20),
    "miércoles": datetime(2026, 10, 21),
    "jueves": datetime(2026, 10, 22),
    "viernes": datetime(2026, 10, 23),
    "domingo": datetime(2026, 10, 18),
}


def _fold(text):
    """Text without accents, so remainders compare the same with or
    without accent restoration."""
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if not unicodedata.combining(c))


def _dt(text):
    res = extract_datetime(text, lang="es-ES", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    return res[0].replace(tzinfo=None)


class TestSiguienteWeekday(unittest.TestCase):
    def test_issue_phrase(self):
        self.assertEqual(_dt("el siguiente viernes"), datetime(2026, 10, 23))

    def test_all_weekdays_with_article(self):
        for day, expected in COMING.items():
            with self.subTest(day=day):
                self.assertEqual(_dt("el siguiente " + day), expected)

    def test_all_weekdays_without_article(self):
        for day, expected in COMING.items():
            with self.subTest(day=day):
                self.assertEqual(_dt("siguiente " + day), expected)

    def test_saturday_from_a_weekday_anchor(self):
        anchor = datetime(2026, 10, 19, 12, 0)  # Monday
        for text in ("el siguiente sábado", "siguiente sábado", "el sábado"):
            with self.subTest(text=text):
                res = extract_datetime(text, lang="es-ES", anchorDate=anchor)
                self.assertEqual(res[0], datetime(2026, 10, 24))

    def test_inside_question(self):
        self.assertEqual(_dt("cuándo es el siguiente viernes"),
                         datetime(2026, 10, 23))

    def test_inside_sentence(self):
        self.assertEqual(_dt("la reunión es el siguiente jueves"),
                         datetime(2026, 10, 22))


class TestSiguienteWeekdayConfusables(unittest.TestCase):
    def test_other_forms_of_the_coming_friday(self):
        for text in ("el viernes", "viernes", "el próximo viernes",
                     "el viernes siguiente", "el viernes próximo",
                     "el viernes que viene"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), datetime(2026, 10, 23))

    def test_siguiente_alone_has_no_date(self):
        self.assertIsNone(extract_datetime("el siguiente", lang="es-ES",
                                           anchorDate=ANCHOR))

    def test_relative_days_unchanged(self):
        self.assertEqual(_dt("pasado mañana"), datetime(2026, 10, 19))
        self.assertEqual(_dt("ayer"), datetime(2026, 10, 16))

    def test_past_weekday_unchanged(self):
        self.assertEqual(_dt("el pasado viernes"), datetime(2026, 10, 16))


class TestWeekdayPasado(unittest.TestCase):
    def test_weekday_pasado_is_the_previous_occurrence(self):
        expected = {
            "lunes": datetime(2026, 10, 12),
            "martes": datetime(2026, 10, 13),
            "miércoles": datetime(2026, 10, 14),
            "jueves": datetime(2026, 10, 15),
            "viernes": datetime(2026, 10, 16),
            "domingo": datetime(2026, 10, 11),
        }
        for day, dt in expected.items():
            for text in ("el %s pasado" % day, "%s pasado" % day,
                         "el pasado %s" % day):
                with self.subTest(text=text):
                    self.assertEqual(_dt(text), dt)

    def test_inside_question(self):
        self.assertEqual(_dt("qué hice el viernes pasado"),
                         datetime(2026, 10, 16))


class TestNextWeek(unittest.TestCase):
    def test_week_from_today(self):
        for text in ("la semana que viene", "la semana siguiente",
                     "semana que viene", "nos vemos la semana que viene"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), datetime(2026, 10, 24))

    def test_last_week_unchanged(self):
        self.assertEqual(_dt("la semana pasada"), datetime(2026, 10, 10))

    def test_weekday_que_viene_unchanged(self):
        self.assertEqual(_dt("el lunes que viene"), datetime(2026, 10, 19))
        self.assertEqual(_dt("el viernes que viene"), datetime(2026, 10, 23))


class TestWeekdayOfAnotherWeek(unittest.TestCase):
    """The week starts on Monday, so from Saturday 17 October the next week
    runs from Monday 19 to Sunday 25 and the last week from 5 to 11."""

    def test_weekday_of_next_week(self):
        expected = {
            "lunes": datetime(2026, 10, 19),
            "jueves": datetime(2026, 10, 22),
            "viernes": datetime(2026, 10, 23),
            "domingo": datetime(2026, 10, 25),
        }
        for day, dt in expected.items():
            for tail in ("que viene", "siguiente"):
                text = "el %s de la semana %s" % (day, tail)
                with self.subTest(text=text):
                    self.assertEqual(_dt(text), dt)

    def test_weekday_of_last_week(self):
        expected = {
            "lunes": datetime(2026, 10, 5),
            "viernes": datetime(2026, 10, 9),
            "domingo": datetime(2026, 10, 11),
        }
        for day, dt in expected.items():
            with self.subTest(day=day):
                self.assertEqual(_dt("el %s de la semana pasada" % day), dt)

    def test_inside_question(self):
        self.assertEqual(_dt("qué hago el viernes de la semana que viene"),
                         datetime(2026, 10, 23))


FRIDAY = datetime(2026, 10, 16, 10, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


def _on(text, anchor):
    res = extract_datetime(text, lang="es-ES", anchorDate=anchor)
    assert res is not None, "no datetime extracted from %r" % text
    return res[0].replace(tzinfo=None), res[1]


class TestNextOnTheSameWeekday(unittest.TestCase):
    """Said on a Friday, "next Friday" is not today."""

    def test_friday_from_a_friday(self):
        for text in ("el siguiente viernes", "el viernes siguiente",
                     "el viernes que viene"):
            with self.subTest(text=text):
                self.assertEqual(_on(text, FRIDAY)[0], datetime(2026, 10, 23))

    def test_saturday_from_a_saturday(self):
        for text in ("el siguiente sábado", "el sábado siguiente",
                     "el sábado que viene"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), datetime(2026, 10, 24))

    def test_plain_and_past_weekday_unchanged(self):
        self.assertEqual(_on("el viernes", FRIDAY)[0], datetime(2026, 10, 16))
        self.assertEqual(_dt("el sábado"), datetime(2026, 10, 17))
        self.assertEqual(_on("el viernes pasado", FRIDAY)[0],
                         datetime(2026, 10, 9))


class TestQueVieneRemainder(unittest.TestCase):
    """Only the words that were understood leave the sentence."""

    def test_week_that_comes(self):
        self.assertEqual(_on("la semana que viene", ANCHOR),
                         (datetime(2026, 10, 24), ""))

    def test_words_around_the_phrase_are_kept(self):
        date, rest = _on("recuérdame la semana que viene comprar pan", ANCHOR)
        self.assertEqual(date, datetime(2026, 10, 24))
        self.assertEqual(_fold(rest), "recuerdame comprar pan")

    def test_weekday_that_comes(self):
        self.assertEqual(_on("el viernes que viene", ANCHOR),
                         (datetime(2026, 10, 23), "el"))

    def test_no_word_is_invented(self):
        res = extract_datetime("el tren que viene a las cinco", lang="es-ES",
                               anchorDate=ANCHOR)
        self.assertNotIn("siguiente", res[1])
        self.assertEqual(res[1], "el tren que viene")

    def test_other_uses_of_que_viene_have_no_date(self):
        for text in ("el autobús que viene", "lo que viene después",
                     "el que viene detrás", "el siguiente paso"):
            with self.subTest(text=text):
                self.assertIsNone(extract_datetime(
                    text, lang="es-ES", anchorDate=ANCHOR))


class TestClockTimeAfterADayQualifier(unittest.TestCase):
    """A day or part-of-day word before a colon time must not raise."""

    def test_tomorrow_at_a_clock_time(self):
        for text in ("mañana a las 10:30", "mañana a las 10:30 café"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), datetime(2026, 10, 18, 10, 30))

    def test_afternoon_phrases_before_a_clock_time(self):
        cases = {
            "esta tarde a las 3:15": datetime(2026, 10, 17, 15, 15),
            "por la tarde a las 4:30": datetime(2026, 10, 17, 16, 30),
            "mañana por la tarde a las 4:30": datetime(2026, 10, 18, 16, 30),
            "hoy por la tarde a las 5:00": datetime(2026, 10, 17, 17, 0),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_afternoon_and_night_at_a_clock_time(self):
        self.assertEqual(_dt("tarde a las 4:30"),
                         datetime(2026, 10, 17, 16, 30))
        self.assertEqual(_dt("esta noche a las 10:30"),
                         datetime(2026, 10, 17, 22, 30))


class TestMananaIsTomorrowOrTheMorning(unittest.TestCase):
    """"mañana" is the morning only in "de la mañana", "por la mañana",
    "en la mañana" and "esta mañana"; anywhere else it is tomorrow."""

    def test_tomorrow_at_a_clock_time(self):
        for text, expected in (
                ("mañana a las 22:30", datetime(2026, 10, 18, 22, 30)),
                ("mañana a las 10", datetime(2026, 10, 18, 10)),
                ("mañana a las 10:30", datetime(2026, 10, 18, 10, 30)),
                ("quedamos mañana a las 9", datetime(2026, 10, 18, 9))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_tomorrow_alone(self):
        self.assertEqual(_dt("mañana"), datetime(2026, 10, 18))
        self.assertEqual(_dt("hasta mañana"), datetime(2026, 10, 18))

    def test_the_morning_forms(self):
        for text, expected in (
                ("a las 8 de la mañana", datetime(2026, 10, 18, 8)),
                ("hoy a las 8 de la mañana", datetime(2026, 10, 17, 8)),
                ("a las 8 en la mañana", datetime(2026, 10, 18, 8)),
                ("esta mañana", datetime(2026, 10, 17, 8)),
                ("mañana por la mañana", datetime(2026, 10, 18, 8)),
                ("ayer por la mañana", datetime(2026, 10, 16, 8))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_other_parts_of_tomorrow_are_unchanged(self):
        self.assertEqual(_dt("pasado mañana"), datetime(2026, 10, 19))
        self.assertEqual(_dt("mañana por la tarde"),
                         datetime(2026, 10, 18, 15))


class TestMorningAfterAnArticleOrAQuantifier(unittest.TestCase):
    """"mañana" is the morning directly after "la", "de la", "por la", "en la",
    "esta", "cada" or "media"; "temprano" after a day word is the morning."""

    def test_the_morning_of_a_day(self):
        for text, expected in (
                ("la mañana del lunes", datetime(2026, 10, 19, 8)),
                ("a media mañana", datetime(2026, 10, 18, 10)),
                ("la mañana de mañana", datetime(2026, 10, 18, 8)),
                ("cada mañana", datetime(2026, 10, 18, 8))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_temprano_after_a_day_word(self):
        for text, expected in (
                ("mañana temprano", datetime(2026, 10, 18, 8)),
                ("el lunes temprano", datetime(2026, 10, 19, 8))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_temprano_leaves_no_remainder(self):
        self.assertEqual(
            extract_datetime("mañana temprano", lang="es-ES",
                             anchorDate=ANCHOR)[1], "")

    def test_the_earlier_cases_keep_their_values(self):
        for text, expected in (
                ("mañana a las 22:30", datetime(2026, 10, 18, 22, 30)),
                ("a las 8 de la mañana", datetime(2026, 10, 18, 8)),
                ("esta mañana", datetime(2026, 10, 17, 8)),
                ("mañana por la mañana", datetime(2026, 10, 18, 8)),
                ("mañana", datetime(2026, 10, 18)),
                ("pasado mañana", datetime(2026, 10, 19))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)


class TestTempranoNeedsADayWord(unittest.TestCase):
    """"temprano" is the morning only beside a day word."""

    def test_temprano_without_a_day_word_is_no_date(self):
        for text in ("llegué temprano", "temprano", "me levanto temprano",
                     "salgo muy temprano"):
            with self.subTest(text=text):
                self.assertIsNone(extract_datetime(
                    text, lang="es-ES", anchorDate=ANCHOR))

    def test_temprano_beside_a_day_word_is_the_morning(self):
        for text, expected in (
                ("mañana temprano", datetime(2026, 10, 18, 8)),
                ("mañana muy temprano", datetime(2026, 10, 18, 8)),
                ("el lunes temprano", datetime(2026, 10, 19, 8)),
                ("hoy temprano", datetime(2026, 10, 17, 8)),
                ("pasado mañana temprano", datetime(2026, 10, 19, 8)),
                ("temprano el lunes", datetime(2026, 10, 19, 8))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)


class TestIntensifierBeforeTemprano(unittest.TestCase):
    def test_an_intensifier_keeps_the_morning(self):
        for text, expected in (
                ("mañana bien temprano", datetime(2026, 10, 18, 8)),
                ("mañana muy temprano", datetime(2026, 10, 18, 8)),
                ("mañana tan temprano", datetime(2026, 10, 18, 8)),
                ("mañana más temprano", datetime(2026, 10, 18, 8)),
                ("el lunes bien temprano", datetime(2026, 10, 19, 8)),
                ("hoy muy temprano", datetime(2026, 10, 17, 8))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text), expected)

    def test_an_intensifier_without_a_day_word_is_no_date(self):
        for text in ("llegué bien temprano", "salgo más temprano"):
            with self.subTest(text=text):
                self.assertIsNone(extract_datetime(
                    text, lang="es-ES", anchorDate=ANCHOR))
