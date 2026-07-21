"""English datetime extraction: month+year and ISO 8601 calendar dates.

Two behaviours are pinned here:

1. A month followed by a bare 4-digit year and no day
   ("june 2027", "the meeting is in june 2027") resolves to the 1st of that
   month in that year, keeping past years in the past ("january 1990").

2. ISO 8601 calendar dates. The extended form YYYY-MM-DD (and the slash
   variant YYYY/MM/DD) are parsed largest-component-first; impossible dates
   and non-date digit runs (phone numbers) are left unparsed.
   Reference: ISO, "ISO 8601 Date and time format" (ISO 8601-1:2019),
   ~/AgentWorkspaces/papers/standards/iso_8601_date_and_time_format.html
   ("YYYY-MM-DD", e.g. 2019-04-25).

Expected values cross-checked against both dateparser and dateutil, which
agree on the year and on rejecting the impossible dates.
"""
import unittest
from datetime import datetime

from ovos_date_parser.dates_en import extract_datetime_en

ANCHOR = datetime(2017, 6, 27, 13, 4)


def extract(text, anchor=ANCHOR):
    return extract_datetime_en(text, anchorDate=anchor)


class TestMonthPlusBareYear(unittest.TestCase):
    """Month + bare 4-digit year -> 1st of that month in that year."""

    def test_month_future_year(self):
        d, rem = extract("june 2027")
        self.assertEqual(d, datetime(2027, 6, 1))
        self.assertEqual(rem, "")

    def test_december_2030(self):
        d, _ = extract("december 2030")
        self.assertEqual(d, datetime(2030, 12, 1))

    def test_past_year_stays_in_past(self):
        # 1990 is before the 2017 anchor and must NOT roll forward
        d, _ = extract("january 1990")
        self.assertEqual(d, datetime(1990, 1, 1))

    def test_in_month_year_marker_consumed(self):
        d, rem = extract("in june 2027")
        self.assertEqual(d, datetime(2027, 6, 1))
        self.assertEqual(rem, "")

    def test_natural_sentence_remainder(self):
        d, rem = extract("the meeting is in june 2027")
        self.assertEqual(d, datetime(2027, 6, 1))
        self.assertEqual(rem, "the meeting is")

    def test_month_day_year_still_works(self):
        # regression guard: an explicit day is unaffected
        d, _ = extract("june 5 2027")
        self.assertEqual(d, datetime(2027, 6, 5))


class TestISO8601CalendarDate(unittest.TestCase):
    """YYYY-MM-DD / YYYY-MM-DD, validated against the calendar."""

    def test_iso_extended(self):
        d, rem = extract("2017-06-30")
        self.assertEqual(d, datetime(2017, 6, 30))
        self.assertEqual(rem, "")

    def test_iso_slash_variant(self):
        d, _ = extract("2017/06/30")
        self.assertEqual(d, datetime(2017, 6, 30))

    def test_natural_sentence_remainder(self):
        d, rem = extract("the deadline is 2017-06-30")
        self.assertEqual(d, datetime(2017, 6, 30))
        self.assertEqual(rem, "the deadline is")

    def test_iso_then_time(self):
        d, rem = extract("call me on 2017-06-30 at 5pm")
        self.assertEqual(d, datetime(2017, 6, 30, 17, 0))
        self.assertEqual(rem, "call me")

    def test_leap_day_valid(self):
        d, _ = extract("2024-02-29")
        self.assertEqual(d, datetime(2024, 2, 29))


class TestISO8601Rejections(unittest.TestCase):
    """Impossible dates and non-dates must not parse as a date."""

    def test_non_leap_feb_29_rejected(self):
        # 2023 is not a leap year; both dateparser and dateutil reject it
        self.assertIsNone(extract("2023-02-29"))

    def test_impossible_month_and_day(self):
        self.assertIsNone(extract("2017-13-45"))

    def test_phone_number_not_a_date(self):
        # adversarial: a 3-2-4 digit run is not YYYY-MM-DD
        self.assertIsNone(extract("123-45-6789"))


if __name__ == "__main__":
    unittest.main()
