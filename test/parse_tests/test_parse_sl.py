import unittest
from datetime import datetime, time

from ovos_date_parser import extract_datetime


class TestExtractDateTimeSL(unittest.TestCase):
    # Tuesday, 6 June 2023, 06:00
    ANCHOR = datetime(2023, 6, 6, 6, 0)

    def extract(self, text, expected_dt, expected_leftover=""):
        result = extract_datetime(text, "sl", anchorDate=self.ANCHOR)
        self.assertIsNotNone(result, text)
        self.assertEqual(result[0], expected_dt, text)
        self.assertEqual(result[1], expected_leftover, text)

    def test_today(self):
        self.extract("danes", datetime(2023, 6, 6, 0, 0))

    def test_tomorrow(self):
        self.extract("jutri", datetime(2023, 6, 7, 0, 0))

    def test_yesterday(self):
        self.extract("včeraj", datetime(2023, 6, 5, 0, 0))

    def test_day_after_tomorrow(self):
        self.extract("pojutrišnjem", datetime(2023, 6, 8, 0, 0))

    def test_day_before_yesterday(self):
        self.extract("predvčerajšnjim", datetime(2023, 6, 4, 0, 0))

    def test_weekday(self):
        # anchor is Tuesday -> following Monday is June 12
        self.extract("v ponedeljek", datetime(2023, 6, 12, 0, 0))
        # accusative form: "v sredo" -> Wednesday June 7
        self.extract("v sredo", datetime(2023, 6, 7, 0, 0))
        self.extract("v soboto", datetime(2023, 6, 10, 0, 0))

    def test_in_5_days(self):
        self.extract("čez 5 dni", datetime(2023, 6, 11, 0, 0))

    def test_ordinal_date(self):
        # June 3 already passed relative to the anchor -> next year
        self.extract("3. junija", datetime(2024, 6, 3, 0, 0))

    def test_ordinal_date_future(self):
        self.extract("15. avgusta", datetime(2023, 8, 15, 0, 0))

    def test_spoken_hour(self):
        # "ob osmih" = at eight o'clock
        self.extract("ob osmih", datetime(2023, 6, 6, 8, 0))

    def test_half_hour_counts_towards_next_hour(self):
        # "ob pol devetih" = 8:30, NOT 9:30 ("pol" towards the next hour)
        self.extract("ob pol devetih", datetime(2023, 6, 6, 8, 30))

    def test_spoken_hour_evening(self):
        self.extract("ob osmih zvečer", datetime(2023, 6, 6, 20, 0))

    def test_noon(self):
        self.extract("opoldne", datetime(2023, 6, 6, 12, 0))

    def test_midnight(self):
        self.extract("opolnoči", datetime(2023, 6, 6, 0, 0))

    def test_digit_time(self):
        self.extract("ob 17:30", datetime(2023, 6, 6, 17, 30))

    def test_next_week(self):
        self.extract("naslednji teden", datetime(2023, 6, 13, 0, 0))

    def test_last_week(self):
        self.extract("prejšnji teden", datetime(2023, 5, 30, 0, 0))

    def test_in_10_minutes(self):
        self.extract("čez 10 minut", datetime(2023, 6, 6, 6, 10))

    def test_combined_date_and_time(self):
        self.extract("jutri ob pol devetih zvečer",
                     datetime(2023, 6, 7, 20, 30))

    def test_leftover_text(self):
        self.extract("nastavi opomnik za jutri", datetime(2023, 6, 7, 0, 0),
                     "nastavi opomnik")

    def test_no_date_returns_none(self):
        self.assertIsNone(
            extract_datetime("zdravo svet", "sl", anchorDate=self.ANCHOR))
        self.assertIsNone(
            extract_datetime("", "sl", anchorDate=self.ANCHOR))

    def test_default_time(self):
        result = extract_datetime("jutri", "sl", anchorDate=self.ANCHOR,
                                  default_time=time(9, 30))
        self.assertEqual(result[0], datetime(2023, 6, 7, 9, 30))


if __name__ == "__main__":
    unittest.main()
