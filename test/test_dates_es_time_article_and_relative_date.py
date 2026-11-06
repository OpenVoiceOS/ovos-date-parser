"""Spanish date and time: one article before the hour, relative days.

nice_time_es starts with the article of "hora": "la una", "las dos". The
date and the time join with the bare preposition: "a la una", "a las dos".

nice_date_es with ``now`` says "hoy", "mañana" or "ayer" only for the same
calendar date, the next one or the previous one. It names the month when
the month or the year differs."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date, nice_date_time

NOW = datetime(2020, 1, 1)
DATE = "martes, doce de marzo, dos mil veinticuatro"


class TestSpanishTimeArticle(unittest.TestCase):

    def test_one_article(self):
        for hour, minute, spoken in ((13, 5, "a la una y cinco"),
                                     (14, 30, "a las dos y media"),
                                     (12, 0, "a las doce en punto")):
            with self.subTest(hour=hour, minute=minute):
                self.assertEqual(
                    nice_date_time(datetime(2024, 3, 12, hour, minute),
                                   "es-ES", now=NOW),
                    f"{DATE} {spoken}")

    def test_24_hour(self):
        self.assertEqual(
            nice_date_time(datetime(2024, 3, 12, 1, 15), "es-ES", now=NOW,
                           use_24hour=True),
            f"{DATE} a la una quince")


class TestSpanishRelativeDate(unittest.TestCase):

    def check(self, dt, now, spoken):
        self.assertEqual(nice_date(dt, "es-ES", now=now), spoken)

    def test_same_day_number_other_month(self):
        self.check(datetime(2024, 3, 12), datetime(2024, 1, 12),
                   "martes, doce de marzo")

    def test_same_day_and_month_other_year(self):
        self.check(datetime(2025, 3, 12), datetime(2024, 3, 12),
                   "miércoles, doce de marzo, dos mil veinticinco")

    def test_tomorrow_across_a_month(self):
        self.check(datetime(2024, 2, 1), datetime(2024, 1, 31), "mañana")

    def test_yesterday_across_a_month(self):
        self.check(datetime(2024, 2, 29), datetime(2024, 3, 1), "ayer")

    def test_today(self):
        self.check(datetime(2024, 3, 12, 18), datetime(2024, 3, 12, 9), "hoy")


if __name__ == "__main__":
    unittest.main()
