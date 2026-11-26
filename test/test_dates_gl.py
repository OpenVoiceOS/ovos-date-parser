import unittest
from datetime import datetime

from ovos_date_parser.dates_gl import (
    nice_weekday_gl,
    nice_month_gl,
    nice_time_gl,
    WEEKDAYS_GL,
    MONTHS_GL,
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
                             ["luns", "martes", "mércores", "xoves",
                              "venres", "sábado", "domingo"][i])

    def test_nice_month(self):
        self.assertEqual(nice_month_gl(datetime(2026, 6, 1)), "xuño")
        self.assertEqual(nice_month_gl(datetime(2026, 12, 1)), "decembro")


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


if __name__ == '__main__':
    unittest.main()
