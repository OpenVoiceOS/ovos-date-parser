"""Estonian datetime extraction: natural phrasing, clock words and edge cases."""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

# a leap-free anchor with a non-zero time of day, so second-level offsets are
# visible and impossible-date handling is exercised (2117 is not a leap year)
ANCHOR = datetime(2117, 9, 3, 13, 30, 0)
TZ = default_timezone()


def extract(text, lang="et", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestRelativeSecondOffset(unittest.TestCase):
    """"N sekundi pärast" adds a seconds offset onto the anchor time of day."""

    def test_fifteen_seconds(self):
        self.assertEqual(extract("15 sekundi pärast")[0], dt(2117, 9, 3, 13, 30, 15))

    def test_spelled_seconds(self):
        self.assertEqual(extract("kolmkümmend sekundit pärast")[0],
                         dt(2117, 9, 3, 13, 30, 30))

    def test_genitive_one_second(self):
        self.assertEqual(extract("ühe sekundi pärast")[0], dt(2117, 9, 3, 13, 30, 1))

    def test_genitive_two_seconds(self):
        self.assertEqual(extract("kahe sekundi pärast")[0], dt(2117, 9, 3, 13, 30, 2))

    def test_seconds_preserve_anchor_time_of_day(self):
        # unlike minute/hour offsets, seconds must keep the anchor's minutes
        self.assertEqual(extract("45 sekundi pärast")[0], dt(2117, 9, 3, 13, 30, 45))

    def test_seconds_leftover_returned(self):
        res = extract("5 sekundi pärast koosolek")
        self.assertEqual(res[0], dt(2117, 9, 3, 13, 30, 5))
        self.assertEqual(res[1], "koosolek")

    def test_bare_second_unit_without_number(self):
        # mirrors minutes/hours: a bare unit with no numeral is not an offset
        self.assertIsNone(extract("sekundi pärast"))


class TestRelativeMinuteHourOffsetStillWorks(unittest.TestCase):
    """The pre-existing minute/hour offsets must be untouched by seconds."""

    def test_minutes(self):
        self.assertEqual(extract("15 minuti pärast")[0], dt(2117, 9, 3, 13, 45))

    def test_hours(self):
        self.assertEqual(extract("3 tunni pärast")[0], dt(2117, 9, 3, 16, 30))

    def test_half_minute(self):
        self.assertEqual(extract("poole minuti pärast")[0], dt(2117, 9, 3, 13, 30, 30))


class TestSpokenClockWords(unittest.TestCase):
    """Estonian fraction-of-hour clock words name the coming hour."""

    def test_quarter_of_eight_is_seven_fifteen(self):
        # "veerand kaheksa" = a quarter into the eighth hour = 07:15
        self.assertEqual(extract("veerand kaheksa")[0], dt(2117, 9, 3, 7, 15))

    def test_half_of_eight_is_seven_thirty(self):
        # "pool kaheksa" = half into the eighth hour = 07:30
        self.assertEqual(extract("pool kaheksa")[0], dt(2117, 9, 3, 7, 30))

    def test_quarter_of_nine(self):
        self.assertEqual(extract("kell veerand üheksa")[0], dt(2117, 9, 3, 8, 15))

    def test_bare_hour_word(self):
        self.assertEqual(extract("kell kaheksa")[0], dt(2117, 9, 3, 8, 0))


class TestRelativeDayOffsets(unittest.TestCase):
    """Day-level relative phrasing keeps working alongside sub-minute offsets."""

    def test_day_after_tomorrow(self):
        self.assertEqual(extract("ülehomme")[0], dt(2117, 9, 5))

    def test_three_days(self):
        self.assertEqual(extract("kolme päeva pärast")[0], dt(2117, 9, 6))

    def test_tomorrow_at_eight(self):
        self.assertEqual(extract("homme kell 8")[0], dt(2117, 9, 4, 8, 0))


class TestImpossibleDatesReturnNone(unittest.TestCase):
    """Malformed or impossible dates must return None, never crash."""

    def test_february_30(self):
        self.assertIsNone(extract("30. veebruaril"))

    def test_april_31(self):
        self.assertIsNone(extract("31. aprillil"))

    def test_february_29_non_leap_year(self):
        # 2117 is not a leap year, so 29 February does not exist
        self.assertIsNone(extract("29. veebruaril"))

    def test_gibberish_returns_none(self):
        self.assertIsNone(extract("xyzzy plurgh"))


if __name__ == "__main__":
    unittest.main()
