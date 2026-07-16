import unittest
from datetime import datetime

from ovos_date_parser.dates_ro import (nice_year_ro, nice_weekday_ro,
                                       nice_month_ro, nice_day_ro,
                                       nice_date_ro, nice_date_time_ro,
                                       nice_time_ro)


class TestNiceDateTimeRO(unittest.TestCase):
    def setUp(self):
        # Monday, June 5, 2023, 17:30
        self.test_date = datetime(2023, 6, 5, 17, 30)
        self.test_now = datetime(2023, 6, 5)

    def test_nice_year_ro(self):
        self.assertEqual(nice_year_ro(self.test_date),
                         "două mii douăzeci și trei")
        self.assertEqual(nice_year_ro(datetime(1984, 1, 1)),
                         "o mie nouă sute optzeci și patru")
        self.assertEqual(nice_year_ro(datetime(2000, 1, 1)), "două mii")
        self.assertEqual(nice_year_ro(self.test_date, bc=True),
                         "două mii douăzeci și trei î.Hr.")

    def test_nice_weekday_ro(self):
        self.assertEqual(nice_weekday_ro(self.test_date), "Luni")
        self.assertEqual(nice_weekday_ro(datetime(2023, 6, 6)), "Marți")
        self.assertEqual(nice_weekday_ro(datetime(2023, 6, 10)), "Sâmbătă")
        self.assertEqual(nice_weekday_ro(datetime(2023, 6, 11)), "Duminică")

    def test_nice_month_ro(self):
        self.assertEqual(nice_month_ro(self.test_date), "Iunie")
        self.assertEqual(nice_month_ro(datetime(2023, 1, 1)), "Ianuarie")
        self.assertEqual(nice_month_ro(datetime(2023, 11, 1)), "Noiembrie")

    def test_nice_day_ro(self):
        self.assertEqual(nice_day_ro(self.test_date, date_format='DMY'),
                         "5 Iunie")
        self.assertEqual(nice_day_ro(self.test_date, date_format='MDY'),
                         "Iunie 5")
        self.assertEqual(nice_day_ro(self.test_date, include_month=False),
                         "5")

    def test_nice_date_ro(self):
        self.assertEqual(nice_date_ro(self.test_date, self.test_now), "azi")
        self.assertEqual(nice_date_ro(datetime(2023, 6, 6), self.test_now),
                         "mâine")
        self.assertEqual(nice_date_ro(datetime(2023, 6, 4), self.test_now),
                         "ieri")
        self.assertEqual(nice_date_ro(datetime(2018, 6, 5)),
                         "Marți, cinci iunie, două mii optsprezece")
        # the first of the month is "întâi"
        self.assertEqual(nice_date_ro(datetime(2018, 5, 1)),
                         "Marți, întâi mai, două mii optsprezece")

    def test_nice_date_time_ro(self):
        self.assertEqual(
            nice_date_time_ro(datetime(2018, 6, 5, 17, 30), now=self.test_now),
            "Marți, cinci iunie, două mii optsprezece la ora "
            "cinci și jumătate")


class TestNiceTimeRO(unittest.TestCase):
    def test_exact_hours(self):
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 8, 0)), "opt fix")
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 1, 0)), "unu fix")
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 12, 0)),
                         "douăsprezece fix")
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 14, 0)),
                         "două fix")

    def test_quarter_and_half(self):
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 8, 15)),
                         "opt și un sfert")
        # half past semantics: 8:30 belongs to eight
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 8, 30)),
                         "opt și jumătate")
        # "fără" = minus: 8:45 is quarter to nine
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 8, 45)),
                         "nouă fără un sfert")
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 9, 40)),
                         "zece fără douăzeci")

    def test_minutes(self):
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 8, 10)),
                         "opt și zece")
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 8, 22)),
                         "opt și douăzeci și două")

    def test_ampm(self):
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 8, 0),
                                      use_ampm=True), "opt dimineața")
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 15, 0),
                                      use_ampm=True), "trei după-amiaza")
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 19, 30),
                                      use_ampm=True),
                         "șapte și jumătate seara")
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 1, 0),
                                      use_ampm=True), "unu noaptea")

    def test_24hour(self):
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 13, 30),
                                      use_24hour=True),
                         "treisprezece treizeci")
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 8, 5),
                                      use_24hour=True), "opt zero cinci")
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 22, 0),
                                      use_24hour=True),
                         "douăzeci și două fix")

    def test_display(self):
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 17, 30),
                                      speech=False), "5:30")
        self.assertEqual(nice_time_ro(datetime(2023, 6, 5, 17, 30),
                                      speech=False, use_24hour=True),
                         "17:30")


if __name__ == "__main__":
    unittest.main()
