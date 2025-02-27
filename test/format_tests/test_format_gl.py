import unittest
from datetime import datetime
from ovos_date_parser.dates_gl import nice_year_gl, nice_weekday_gl, nice_month_gl, nice_day_gl, nice_date_gl, nice_time_gl

class TestNiceDateTimeGL(unittest.TestCase):
    def setUp(self):
        self.test_date = datetime(2023, 6, 5, 17, 30)  # Monday, June 5, 2023, 17:30
        self.test_now = datetime(2023, 6, 5)  # Same day as test_date

    @unittest.skip("number parser for galician only goes up to 100, update ovos-number-parser")
    def test_nice_year_gl(self):
        self.assertEqual(nice_year_gl(self.test_date), "dous mil vinte e tres")
        self.assertEqual(nice_year_gl(self.test_date, bc=True), "dous mil vinte e tres a.C.")

    def test_nice_weekday_gl(self):
        self.assertEqual(nice_weekday_gl(self.test_date), "Luns")

    def test_nice_month_gl(self):
        self.assertEqual(nice_month_gl(self.test_date), "Xuño")

    def test_nice_day_gl(self):
        self.assertEqual(nice_day_gl(self.test_date, date_format='DMY'), "5 Xuño")
        self.assertEqual(nice_day_gl(self.test_date, date_format='MDY'), "Xuño 5")
        self.assertEqual(nice_day_gl(self.test_date, include_month=False), "5")

    def test_nice_date_gl(self):
        self.assertEqual(nice_date_gl(self.test_date, self.test_now), "hoxe")
        future_date = datetime(2023, 6, 6)
        self.assertEqual(nice_date_gl(future_date, self.test_now), "mañá")
        past_date = datetime(2023, 6, 4)
        self.assertEqual(nice_date_gl(past_date, self.test_now), "onte")

    def test_nice_time_gl(self):
        self.assertEqual(nice_time_gl(self.test_date, speech=True, use_24hour=True), "as dezasete trinta")
        self.assertEqual(nice_time_gl(self.test_date, speech=True, use_24hour=False), "as cinco e media")
        self.assertEqual(nice_time_gl(self.test_date, speech=False, use_24hour=True), "17:30")
        self.assertEqual(nice_time_gl(self.test_date, speech=False, use_24hour=False), "5:30")

if __name__ == '__main__':
    unittest.main()