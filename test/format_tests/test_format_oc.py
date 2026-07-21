import unittest
from datetime import datetime
from ovos_date_parser.dates_oc import (nice_year_oc, nice_weekday_oc, nice_month_oc,
                                       nice_day_oc, nice_date_oc, nice_time_oc)


class TestNiceDateTimeOC(unittest.TestCase):
    def setUp(self):
        self.test_date = datetime(2023, 6, 5, 17, 30)  # Monday, June 5, 2023, 17:30
        self.test_now = datetime(2023, 6, 5)  # Same day as test_date

    def test_nice_year_oc(self):
        self.assertEqual(nice_year_oc(self.test_date), "dos mila e vint e tres")
        self.assertEqual(nice_year_oc(self.test_date, bc=True), "dos mila e vint e tres a.C.")

    def test_nice_weekday_oc(self):
        self.assertEqual(nice_weekday_oc(self.test_date), "Diluns")

    def test_nice_month_oc(self):
        self.assertEqual(nice_month_oc(self.test_date), "Junh")

    def test_nice_day_oc(self):
        self.assertEqual(nice_day_oc(self.test_date, date_format='DMY'), "5 Junh")
        self.assertEqual(nice_day_oc(self.test_date, date_format='MDY'), "Junh 5")
        self.assertEqual(nice_day_oc(self.test_date, include_month=False), "5")

    def test_nice_date_oc(self):
        self.assertEqual(nice_date_oc(self.test_date, self.test_now), "uèi")
        future_date = datetime(2023, 6, 6)
        self.assertEqual(nice_date_oc(future_date, self.test_now), "deman")
        past_date = datetime(2023, 6, 4)
        self.assertEqual(nice_date_oc(past_date, self.test_now), "ièr")

    def test_nice_time_oc(self):
        self.assertEqual(nice_time_oc(self.test_date, speech=True, use_24hour=True),
                         "dètz-e-sèt oras trenta")
        self.assertEqual(nice_time_oc(self.test_date, speech=True, use_24hour=False),
                         "cinc oras e mièja")
        self.assertEqual(nice_time_oc(self.test_date, speech=False, use_24hour=True), "17:30")
        self.assertEqual(nice_time_oc(self.test_date, speech=False, use_24hour=False), "5:30")

    def test_nice_time_idioms(self):
        # quarter past: "una ora e quart"
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 13, 15)), "una ora e quart")
        # quarter to names the next hour: 1:45 -> "doas oras manca un quart"
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 1, 45)),
                         "doas oras manca un quart")
        # noon and midnight
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 12, 0)), "miègjorn")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 0, 0)), "mièjanuèch")

    def test_nice_time_ampm(self):
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 9, 5), use_ampm=True),
                         "nòu oras e cinc del matin")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 15, 0), use_ampm=True),
                         "tres oras de l'aprèp-miègjorn")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 20, 0), use_ampm=True),
                         "uèch oras del ser")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 23, 0), use_ampm=True),
                         "onze oras de la nuèch")


if __name__ == '__main__':
    unittest.main()
