import unittest
from datetime import datetime, time

from ovos_date_parser import extract_datetime


class TestExtractDatetimeHu(unittest.TestCase):
    # anchor is a Tuesday
    ANCHOR = datetime(2017, 6, 27, 0, 0)

    def extract(self, text, **kwargs):
        return extract_datetime(text, lang="hu-hu", anchorDate=self.ANCHOR,
                                **kwargs)

    def assertDate(self, text, expected):
        result = self.extract(text)
        self.assertIsNotNone(result, text)
        self.assertEqual(result[0].strftime("%Y-%m-%d %H:%M:%S"), expected,
                         text)

    def test_today(self):
        self.assertDate("ma", "2017-06-27 00:00:00")

    def test_tomorrow(self):
        self.assertDate("holnap", "2017-06-28 00:00:00")

    def test_yesterday(self):
        self.assertDate("tegnap", "2017-06-26 00:00:00")

    def test_day_after_tomorrow(self):
        self.assertDate("holnapután", "2017-06-29 00:00:00")

    def test_day_before_yesterday(self):
        self.assertDate("tegnapelőtt", "2017-06-25 00:00:00")

    def test_weekday(self):
        # anchor is Tuesday, so "hétfőn" (on Monday) is next Monday
        self.assertDate("hétfőn", "2017-07-03 00:00:00")
        self.assertDate("pénteken", "2017-06-30 00:00:00")

    def test_next_weekday(self):
        self.assertDate("jövő hétfőn", "2017-07-03 00:00:00")

    def test_in_five_days(self):
        self.assertDate("5 nap múlva", "2017-07-02 00:00:00")

    def test_explicit_date(self):
        # June 3rd is in the past relative to the anchor -> next year
        self.assertDate("június 3", "2018-06-03 00:00:00")
        self.assertDate("augusztus 3-án", "2017-08-03 00:00:00")

    def test_at_8_oclock(self):
        self.assertDate("8 órakor", "2017-06-27 08:00:00")

    def test_half_nine_is_eight_thirty(self):
        # "fél kilenc" counts towards nine: 8:30, NOT 9:30
        self.assertDate("fél kilenc", "2017-06-27 08:30:00")

    def test_quarter_ten_is_nine_fifteen(self):
        self.assertDate("negyed tíz", "2017-06-27 09:15:00")

    def test_three_quarter_eight_is_seven_fortyfive(self):
        self.assertDate("háromnegyed nyolc", "2017-06-27 07:45:00")

    def test_half_nine_evening(self):
        self.assertDate("este fél kilenc", "2017-06-27 20:30:00")

    def test_noon(self):
        self.assertDate("délben", "2017-06-27 12:00:00")

    def test_midnight(self):
        self.assertDate("éjfélkor", "2017-06-27 00:00:00")

    def test_digit_time(self):
        self.assertDate("17:30-kor", "2017-06-27 17:30:00")
        self.assertDate("17:30", "2017-06-27 17:30:00")

    def test_afternoon_three(self):
        self.assertDate("délután 3 órakor", "2017-06-27 15:00:00")

    def test_next_week(self):
        self.assertDate("jövő héten", "2017-07-04 00:00:00")

    def test_last_week(self):
        self.assertDate("múlt héten", "2017-06-20 00:00:00")

    def test_tomorrow_morning(self):
        self.assertDate("holnap reggel", "2017-06-28 08:00:00")

    def test_leftover(self):
        result = self.extract("állíts be egy emlékeztetőt holnap")
        self.assertEqual(result[0].strftime("%Y-%m-%d %H:%M:%S"),
                         "2017-06-28 00:00:00")
        self.assertEqual(result[1], "állíts be egy emlékeztetőt")

    def test_no_date(self):
        self.assertIsNone(self.extract("helló világ"))
        self.assertIsNone(self.extract(""))

    def test_leap_day_explicit_year(self):
        # the explicit year must be honoured when building the date; the
        # anchor year (2017, a common year) must not reject Feb 29 first
        self.assertDate("február 29 2020", "2020-02-29 00:00:00")
        self.assertDate("február 29-én 2024", "2024-02-29 00:00:00")

    def test_leap_day_without_year_finds_next_leap_year(self):
        # anchor is 2017; the next February 29 is in 2020
        self.assertDate("február 29", "2020-02-29 00:00:00")

    def test_leap_day_with_time(self):
        self.assertDate("február 29-én 8 órakor", "2020-02-29 08:00:00")

    def test_invalid_calendar_date_is_not_a_date(self):
        # dates that never exist must fail cleanly, not raise
        self.assertIsNone(self.extract("április 31"))
        self.assertIsNone(self.extract("február 30"))
        self.assertIsNone(self.extract("november 31-én"))
        # Feb 29 of a common year is likewise impossible
        self.assertIsNone(self.extract("február 29 2019"))

    def test_invalid_date_keeps_a_valid_time(self):
        # an impossible day drops the date but a stated time still stands
        self.assertDate("április 31 8 órakor", "2017-06-27 08:00:00")

    def test_default_time(self):
        result = self.extract("holnap", default_time=time(9, 30))
        self.assertEqual(result[0].strftime("%Y-%m-%d %H:%M:%S"),
                         "2017-06-28 09:30:00")


if __name__ == "__main__":
    unittest.main()
