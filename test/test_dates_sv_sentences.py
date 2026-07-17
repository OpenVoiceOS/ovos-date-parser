"""Swedish datetime extraction: natural phrasing, relative offsets and edge cases."""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

# Afternoon anchor so purely-relative offsets ("om 3 timmar") are observable:
# a midnight anchor would hide a time-of-day reset bug.
ANCHOR = datetime(2117, 9, 3, 13, 30, 0)
TZ = default_timezone()


def extract(text, lang="sv", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestRelativeFutureOffsets(unittest.TestCase):
    """Swedish uses "om" for relative future ("om 15 minuter" = in 15 minutes).

    A purely-relative offset keeps the anchor time of day; it must not reset to
    midnight.
    """

    def test_seconds(self):
        self.assertEqual(extract("om 15 sekunder")[0], dt(2117, 9, 3, 13, 30, 15))

    def test_minutes(self):
        self.assertEqual(extract("om 15 minuter")[0], dt(2117, 9, 3, 13, 45))

    def test_hours(self):
        self.assertEqual(extract("om 3 timmar")[0], dt(2117, 9, 3, 16, 30))

    def test_ninety_minutes_rolls_hour(self):
        self.assertEqual(extract("om 90 minuter")[0], dt(2117, 9, 3, 15, 0))

    def test_single_hour(self):
        self.assertEqual(extract("om en timme")[0], dt(2117, 9, 3, 14, 30))

    def test_single_minute(self):
        self.assertEqual(extract("om en minut")[0], dt(2117, 9, 3, 13, 31))

    def test_single_second(self):
        self.assertEqual(extract("om en sekund")[0], dt(2117, 9, 3, 13, 30, 1))

    def test_half_hour(self):
        # "en halvtimme" = half an hour = 30 minutes
        self.assertEqual(extract("om en halvtimme")[0], dt(2117, 9, 3, 14, 0))

    def test_quarter_hour(self):
        # "en kvart" = a quarter of an hour = 15 minutes
        self.assertEqual(extract("om en kvart")[0], dt(2117, 9, 3, 13, 45))

    def test_natural_sentence(self):
        res = extract("påminn mig om 10 minuter")
        self.assertEqual(res[0], dt(2117, 9, 3, 13, 40))
        self.assertEqual(res[1], "påminn mig")


class TestRelativeDayOffsets(unittest.TestCase):
    def test_today(self):
        self.assertEqual(extract("idag")[0], dt(2117, 9, 3))

    def test_tomorrow(self):
        self.assertEqual(extract("imorgon")[0], dt(2117, 9, 4))

    def test_day_after_tomorrow(self):
        self.assertEqual(extract("övermorgon")[0], dt(2117, 9, 5))

    def test_next_friday(self):
        self.assertEqual(extract("nästa fredag")[0], dt(2117, 9, 10))

    def test_eight_weeks(self):
        self.assertEqual(extract("om 8 veckor")[0], dt(2117, 10, 29))


class TestPartOfDay(unittest.TestCase):
    def test_tomorrow_morning(self):
        self.assertEqual(extract("imorgon morgon")[0], dt(2117, 9, 4, 8))

    def test_tomorrow_noon(self):
        self.assertEqual(extract("imorgon middag")[0], dt(2117, 9, 4, 12))

    def test_tomorrow_evening(self):
        self.assertEqual(extract("imorgon kväll")[0], dt(2117, 9, 4, 19))


class TestAbsoluteDates(unittest.TestCase):
    def test_this_year_christmas(self):
        # 25 december is still ahead of the September anchor -> same year
        self.assertEqual(extract("25 december")[0], dt(2117, 12, 25))

    def test_next_occurrence_rolls_year(self):
        # 15 juli already passed this year -> next occurrence
        self.assertEqual(extract("15 juli")[0], dt(2118, 7, 15))

    def test_leap_day_rolls_to_leap_year(self):
        # 29 februari only exists in a leap year; 2120 is the next one
        self.assertEqual(extract("29 februari")[0], dt(2120, 2, 29))


class TestClock(unittest.TestCase):
    def test_time_rolls_to_next_day(self):
        # 10:45 already passed today -> next day
        self.assertEqual(extract("klockan 10:45")[0], dt(2117, 9, 4, 10, 45))


class TestImpossibleAndEmpty(unittest.TestCase):
    """Impossible or empty input must return None, never crash or hang."""

    def test_empty(self):
        self.assertEqual(extract(""), None)

    def test_april_31(self):
        self.assertEqual(extract("31 april"), None)

    def test_april_31_with_year(self):
        self.assertEqual(extract("31 april 2020"), None)

    def test_february_30(self):
        self.assertEqual(extract("30 februari"), None)

    def test_june_31(self):
        self.assertEqual(extract("31 juni"), None)

    def test_impossible_clock(self):
        self.assertEqual(extract("klockan 25:70"), None)

    def test_no_date(self):
        self.assertEqual(extract("det finns ingen tid här"), None)


class TestDurationEdgeCases(unittest.TestCase):
    """extract_duration must signal 'no duration' with None, never crash."""

    def test_empty_string(self):
        self.assertIsNone(_odp.extract_duration("", lang="sv"))

    def test_whitespace_only(self):
        self.assertIsNone(_odp.extract_duration("   ", lang="sv"))

    def test_tabs_and_newlines(self):
        self.assertIsNone(_odp.extract_duration("\t\n  ", lang="sv"))

    def test_gibberish(self):
        self.assertIsNone(_odp.extract_duration("blahonga foo bar", lang="sv"))

    def test_words_without_numbers(self):
        self.assertIsNone(_odp.extract_duration("minuter och sekunder", lang="sv"))

    def test_normal_duration_still_parses(self):
        td, remainder = _odp.extract_duration("5 minuter", lang="sv")
        self.assertEqual(td.total_seconds(), 300)

    def test_compound_duration_still_parses(self):
        td, remainder = _odp.extract_duration(
            "2 timmar och 30 minuter", lang="sv")
        self.assertEqual(td.total_seconds(), 2 * 3600 + 30 * 60)


if __name__ == "__main__":
    unittest.main()
