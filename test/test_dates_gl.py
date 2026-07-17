import unittest
from datetime import datetime, timedelta

from ovos_date_parser.dates_gl import (
    nice_year_gl, nice_weekday_gl, nice_month_gl, nice_day_gl,
    nice_time_gl, extract_datetime_gl, extract_duration_gl,
    WEEKDAYS_GL, MONTHS_GL
)


class TestVocabularyGL(unittest.TestCase):
    """Galician weekday and month names must not leak Spanish/Portuguese forms."""

    def test_weekdays(self):
        expected = ["luns", "martes", "mércores", "xoves",
                    "venres", "sábado", "domingo"]
        self.assertEqual([WEEKDAYS_GL[i] for i in range(7)], expected)

    def test_months(self):
        expected = ["xaneiro", "febreiro", "marzo", "abril", "maio", "xuño",
                    "xullo", "agosto", "setembro", "outubro", "novembro",
                    "decembro"]
        self.assertEqual([MONTHS_GL[i] for i in range(1, 13)], expected)

    def test_nice_weekday(self):
        # 2026-07-13 is a Monday
        for i in range(7):
            self.assertEqual(nice_weekday_gl(datetime(2026, 7, 13 + i)),
                             ["Luns", "Martes", "Mércores", "Xoves",
                              "Venres", "Sábado", "Domingo"][i])

    def test_nice_month(self):
        self.assertEqual(nice_month_gl(datetime(2026, 6, 1)), "Xuño")
        self.assertEqual(nice_month_gl(datetime(2026, 12, 1)), "Decembro")


class TestNiceTimeGL(unittest.TestCase):

    def test_half_past(self):
        dt = datetime(2026, 7, 17, 15, 30)
        self.assertEqual(nice_time_gl(dt, use_24hour=False), "as tres e media")
        self.assertEqual(nice_time_gl(dt, use_24hour=False, use_ampm=True),
                         "as tres e media da tarde")

    def test_quarter_past(self):
        dt = datetime(2026, 7, 17, 7, 15)
        self.assertEqual(nice_time_gl(dt, use_24hour=False), "as sete e cuarto")

    def test_midnight_and_noon(self):
        self.assertEqual(nice_time_gl(datetime(2026, 7, 17, 0, 0)),
                         "as doce en punto")
        self.assertEqual(nice_time_gl(datetime(2026, 7, 17, 12, 0)),
                         "as doce en punto")


class TestExtractDatetimeGL(unittest.TestCase):

    def setUp(self):
        self.anchor = datetime(2026, 7, 17, 12, 0, 0)

    def _dt(self, text):
        return extract_datetime_gl(text, anchorDate=self.anchor)

    def test_alarm_quarter_past(self):
        dt, remainder = self._dt("pon unha alarma ás sete e cuarto")
        self.assertEqual(dt, datetime(2026, 7, 18, 7, 15))
        self.assertEqual(remainder, "pon alarma")

    def test_appointment_with_month_and_hour(self):
        # trailing clock number must not be swallowed as a year
        dt, _ = self._dt("cita o 15 de xuño ás tres")
        self.assertEqual(dt, datetime(2027, 6, 15, 3, 0))

    def test_part_of_day_pm(self):
        dt, _ = self._dt("ás tres da tarde")
        self.assertEqual(dt, datetime(2026, 7, 17, 15, 0))

    def test_part_of_day_am(self):
        dt, _ = self._dt("ás tres da mañá")
        self.assertEqual(dt, datetime(2026, 7, 18, 3, 0))

    def test_part_of_day_night(self):
        dt, _ = self._dt("ás oito da noite")
        self.assertEqual(dt, datetime(2026, 7, 17, 20, 0))

    def test_month_day_numeric(self):
        dt, _ = self._dt("o 3 de decembro")
        self.assertEqual(dt, datetime(2026, 12, 3, 0, 0))

    def test_month_day_first_numeric(self):
        dt, _ = self._dt("o 1 de xaneiro")
        self.assertEqual(dt, datetime(2027, 1, 1, 0, 0))

    def test_relative_days(self):
        self.assertEqual(self._dt("onte")[0], datetime(2026, 7, 16, 0, 0))
        self.assertEqual(self._dt("hoxe")[0], datetime(2026, 7, 17, 0, 0))
        self.assertEqual(self._dt("pasado mañá")[0], datetime(2026, 7, 19, 0, 0))

    def test_weekday(self):
        # next Monday after Friday 2026-07-17
        dt, _ = self._dt("reunión o luns")
        self.assertEqual(dt, datetime(2026, 7, 20, 0, 0))

    def test_full_sentence_half_past_morning(self):
        dt, remainder = self._dt("pon o espertador ás sete e media da mañá")
        self.assertEqual(dt, datetime(2026, 7, 18, 7, 30))
        self.assertEqual(remainder, "pon espertador")

    # --- adversarial ---
    def test_empty_and_none(self):
        self.assertIsNone(self._dt(""))
        self.assertIsNone(self._dt("   "))

    def test_no_date(self):
        self.assertIsNone(self._dt("pon a mesa e limpa o chan"))


class TestExtractDurationGL(unittest.TestCase):

    def test_spelled_numbers(self):
        # regression: spelled-out numbers were not converted before matching
        self.assertEqual(extract_duration_gl("dez minutos")[0],
                         timedelta(minutes=10))
        self.assertEqual(extract_duration_gl("dúas horas")[0],
                         timedelta(hours=2))
        self.assertEqual(extract_duration_gl("tres días")[0],
                         timedelta(days=3))
        self.assertEqual(extract_duration_gl("corenta e cinco segundos")[0],
                         timedelta(seconds=45))

    def test_digit_numbers(self):
        self.assertEqual(extract_duration_gl("10 minutos")[0],
                         timedelta(minutes=10))
        self.assertEqual(extract_duration_gl("1.5 horas")[0],
                         timedelta(hours=1, minutes=30))
        self.assertEqual(extract_duration_gl("2 semanas")[0],
                         timedelta(weeks=2))

    def test_remainder_retained(self):
        duration, remainder = extract_duration_gl("agarda dez minutos e vai")
        self.assertEqual(duration, timedelta(minutes=10))
        self.assertEqual(remainder, "agarda e vai")

    def test_empty_and_junk(self):
        self.assertIsNone(extract_duration_gl(""))
        self.assertEqual(extract_duration_gl("pon a mesa"), (None, "pon a mesa"))


if __name__ == '__main__':
    unittest.main()
