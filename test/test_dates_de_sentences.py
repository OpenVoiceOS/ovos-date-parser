"""German datetime extraction: natural phrasing, clock words and edge cases."""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

# whole-second anchor: anchor seconds are truncated to :00 before offsets,
# so a non-zero anchor second would make purely-relative expectations flaky.
ANCHOR = datetime(2117, 9, 3, 13, 30, 0)  # a Friday
TZ = default_timezone()


def extract(text, anchor=ANCHOR, lang="de"):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestRelativeOffsetKeepsAnchorTime(unittest.TestCase):
    """A purely-relative offset must build on the anchor time of day,
    never on midnight."""

    def test_seconds_offset(self):
        self.assertEqual(extract("in 15 sekunden")[0], dt(2117, 9, 3, 13, 30, 15))

    def test_minutes_offset(self):
        self.assertEqual(extract("in 15 minuten")[0], dt(2117, 9, 3, 13, 45))

    def test_hours_offset(self):
        self.assertEqual(extract("in 3 stunden")[0], dt(2117, 9, 3, 16, 30))

    def test_single_hour_word(self):
        self.assertEqual(extract("in einer stunde")[0], dt(2117, 9, 3, 14, 30))

    def test_single_minute_word(self):
        self.assertEqual(extract("in einer minute")[0], dt(2117, 9, 3, 13, 31))

    def test_single_second_word(self):
        self.assertEqual(extract("in 5 sekunden")[0], dt(2117, 9, 3, 13, 30, 5))

    def test_hour_wraps_into_next_day(self):
        self.assertEqual(extract("in 24 stunden")[0], dt(2117, 9, 4, 13, 30))

    def test_minutes_carry_the_hour(self):
        self.assertEqual(extract("in 90 minuten")[0], dt(2117, 9, 3, 15, 0))

    def test_compound_hour_and_minutes(self):
        self.assertEqual(extract("in einer stunde und 20 minuten")[0],
                         dt(2117, 9, 3, 14, 50))

    def test_reminder_sentence(self):
        res = extract("erinnere mich in 2 stunden")
        self.assertEqual(res[0], dt(2117, 9, 3, 15, 30))

    def test_offset_from_non_midnight_morning_anchor(self):
        anchor = datetime(2020, 1, 1, 9, 15, 0)
        res = extract("in 15 sekunden", anchor=anchor)
        self.assertEqual(res[0].replace(tzinfo=None),
                         datetime(2020, 1, 1, 9, 15, 15))

    def test_offset_hours_from_non_midnight_anchor(self):
        anchor = datetime(2020, 1, 1, 9, 15, 0)
        res = extract("erinnere mich in 2 stunden", anchor=anchor)
        self.assertEqual(res[0].replace(tzinfo=None),
                         datetime(2020, 1, 1, 11, 15, 0))


class TestSingularAndPluralUnits(unittest.TestCase):
    """Both singular and plural unit words must be understood."""

    def test_stunde_singular_and_plural(self):
        self.assertEqual(extract("in einer stunde")[0].hour, 14)
        self.assertEqual(extract("in zwei stunden")[0].hour, 15)

    def test_minute_singular_and_plural(self):
        self.assertEqual(extract("in einer minute")[0].minute, 31)
        self.assertEqual(extract("in zwei minuten")[0].minute, 32)

    def test_sekunde_singular_and_plural(self):
        self.assertEqual(extract("in einer sekunde")[0].second, 1)
        self.assertEqual(extract("in zwei sekunden")[0].second, 2)


class TestAbsoluteClockTimes(unittest.TestCase):
    """Absolute clock times are placed on the anchor (or next) day at
    midnight-based time, independent of the anchor time of day."""

    def test_bare_hour_uhr(self):
        # 19:00 today, still ahead of the 13:30 anchor
        self.assertEqual(extract("um 19 uhr")[0], dt(2117, 9, 3, 19))

    def test_evening_qualifier_makes_pm(self):
        self.assertEqual(extract("um 8 uhr abends")[0], dt(2117, 9, 3, 20))

    def test_half_past_word(self):
        # "halb neun" == 8:30; already past today, rolls to next day
        self.assertEqual(extract("um halb neun")[0], dt(2117, 9, 4, 8, 30))

    def test_part_of_day_evening(self):
        self.assertEqual(extract("heute abend")[0], dt(2117, 9, 3, 19))

    def test_part_of_day_night(self):
        self.assertEqual(extract("heute nacht")[0], dt(2117, 9, 3, 23))

    def test_morning_tomorrow_with_clock(self):
        self.assertEqual(extract("morgen früh um 6 uhr")[0], dt(2117, 9, 4, 6))


class TestRelativeDays(unittest.TestCase):
    """Day-level relative expressions reset to midnight of the target day."""

    def test_tomorrow(self):
        self.assertEqual(extract("morgen")[0], dt(2117, 9, 4))

    def test_day_after_tomorrow(self):
        self.assertEqual(extract("übermorgen")[0], dt(2117, 9, 5))

    def test_in_two_weeks(self):
        self.assertEqual(extract("in zwei wochen")[0], dt(2117, 9, 17))

    def test_next_year(self):
        self.assertEqual(extract("nächstes jahr")[0], dt(2118, 9, 3))

    def test_last_friday(self):
        res = extract("letzten freitag")[0]
        self.assertEqual(res.strftime("%A"), "Friday")
        self.assertLess(res.replace(tzinfo=None), ANCHOR)

    def test_days_offset_with_clock(self):
        self.assertEqual(extract("in 3 tagen um 15 uhr")[0], dt(2117, 9, 6, 15))

    def test_named_weekday_with_clock(self):
        res = extract("nächsten montag um 9 uhr")[0]
        self.assertEqual(res.strftime("%A"), "Monday")
        self.assertEqual(res.hour, 9)
        self.assertGreater(res.replace(tzinfo=None), ANCHOR)


class TestImpossibleAndUnparseable(unittest.TestCase):
    """Impossible calendar dates and junk must return None, never crash."""

    def test_thirtyfirst_of_june(self):
        self.assertIsNone(extract("am 31. juni"))

    def test_thirtieth_of_february(self):
        self.assertIsNone(extract("am 30. februar"))

    def test_zeroth_of_january(self):
        self.assertIsNone(extract("am 0. januar"))

    def test_twentyninth_february_non_leap(self):
        self.assertIsNone(extract("am 29. februar 2021"))

    def test_empty_string(self):
        self.assertIsNone(extract(""))

    def test_pure_noise(self):
        self.assertIsNone(extract("blablabla"))


class TestLeapDate(unittest.TestCase):
    """29 February is valid in a leap year and must be preserved."""

    def test_twentyninth_february_leap_year(self):
        self.assertEqual(extract("am 29. februar 2024")[0], dt(2024, 2, 29))


if __name__ == "__main__":
    unittest.main()
