"""Behaviour tests for extract_date_en / extract_time_en.

These exercise the date-only / time-only public wrappers around the shared
English datetime scanner.  The anchor is a fixed Tuesday, ``2017-06-27 13:04``,
so every expected ``date(...)`` / ``time(...)`` value below is deterministic and
was worked out by hand from that anchor (weekday offsets, the "next X is at
least 48h away" rule, month-name resolution, relative offsets and the handful
of inherited scanner quirks that are called out in comments).

Both wrappers must never raise on garbage input -- they return ``None`` instead.
"""
import unittest
from datetime import datetime, date, time

from ovos_date_parser import extract_date_en, extract_time_en

# a plain Tuesday afternoon
ANCHOR = datetime(2017, 6, 27, 13, 4)


class TestExtractDateWeekdays(unittest.TestCase):
    """`on/next/last/this X` weekday phrases resolve against the Tuesday anchor."""

    def test_on_each_weekday(self):
        # "on X" is the coming X, today counts as itself (tuesday -> today)
        self.assertEqual(extract_date_en("on monday", ANCHOR),
                         (date(2017, 7, 3), ""))
        self.assertEqual(extract_date_en("on tuesday", ANCHOR),
                         (date(2017, 6, 27), ""))
        self.assertEqual(extract_date_en("on wednesday", ANCHOR),
                         (date(2017, 6, 28), ""))
        self.assertEqual(extract_date_en("on thursday", ANCHOR),
                         (date(2017, 6, 29), ""))
        self.assertEqual(extract_date_en("on friday", ANCHOR),
                         (date(2017, 6, 30), ""))
        self.assertEqual(extract_date_en("on saturday", ANCHOR),
                         (date(2017, 7, 1), ""))
        self.assertEqual(extract_date_en("on sunday", ANCHOR),
                         (date(2017, 7, 2), ""))

    def test_next_weekday_is_at_least_48h_out(self):
        # the inherited "next" rule: on Tuesday, "next monday" is <=2 days so
        # it rolls a week, but "next friday" (3 days) does not
        self.assertEqual(extract_date_en("next monday", ANCHOR),
                         (date(2017, 7, 3), ""))
        self.assertEqual(extract_date_en("next tuesday", ANCHOR),
                         (date(2017, 7, 4), ""))
        self.assertEqual(extract_date_en("next friday", ANCHOR),
                         (date(2017, 6, 30), ""))
        self.assertEqual(extract_date_en("next sunday", ANCHOR),
                         (date(2017, 7, 2), ""))

    def test_last_weekday(self):
        self.assertEqual(extract_date_en("last monday", ANCHOR),
                         (date(2017, 6, 26), ""))
        self.assertEqual(extract_date_en("last friday", ANCHOR),
                         (date(2017, 6, 23), ""))
        self.assertEqual(extract_date_en("last tuesday", ANCHOR),
                         (date(2017, 6, 20), ""))

    def test_this_weekday(self):
        self.assertEqual(extract_date_en("this wednesday", ANCHOR),
                         (date(2017, 6, 28), ""))
        self.assertEqual(extract_date_en("this friday", ANCHOR),
                         (date(2017, 6, 30), ""))


class TestExtractDateMonthNames(unittest.TestCase):
    """Month-name dates, ordinals and explicit years."""

    def test_bare_month_day(self):
        # no year given and the date has already passed this year -> next year
        self.assertEqual(extract_date_en("march 5th", ANCHOR),
                         (date(2018, 3, 5), ""))
        # still ahead this year -> this year
        self.assertEqual(extract_date_en("december 25th", ANCHOR),
                         (date(2017, 12, 25), ""))

    def test_ordinal_of_month(self):
        # "the" survives in the remainder (only "of july" is consumed)
        self.assertEqual(extract_date_en("the 3rd of july", ANCHOR),
                         (date(2017, 7, 3), "the"))
        self.assertEqual(extract_date_en("the 1st of january", ANCHOR),
                         (date(2018, 1, 1), "the"))

    def test_explicit_year(self):
        self.assertEqual(extract_date_en("5 december 2030", ANCHOR),
                         (date(2030, 12, 5), ""))
        self.assertEqual(extract_date_en("5 june 2030", ANCHOR),
                         (date(2030, 6, 5), ""))
        self.assertEqual(extract_date_en("february 29 2024", ANCHOR),
                         (date(2024, 2, 29), ""))

    def test_month_and_year(self):
        # "june 2027" -> month + bare 4-digit year, day 1 of that month
        self.assertEqual(extract_date_en("june 2027", ANCHOR),
                         (date(2027, 6, 1), ""))

    def test_worded_ordinal_with_year(self):
        # "the fifth of november 1955" -> "november 1955" parses (month + bare
        # year, day 1); the spelled ordinal is left in the remainder
        self.assertEqual(extract_date_en("the fifth of november 1955", ANCHOR),
                         (date(1955, 11, 1), "the fifth"))


class TestExtractDateRelative(unittest.TestCase):
    """Relative day/week/month/year offsets."""

    def test_relative_today_tomorrow_yesterday(self):
        self.assertEqual(extract_date_en("today", ANCHOR),
                         (date(2017, 6, 27), ""))
        self.assertEqual(extract_date_en("tomorrow", ANCHOR),
                         (date(2017, 6, 28), ""))
        self.assertEqual(extract_date_en("yesterday", ANCHOR),
                         (date(2017, 6, 26), ""))
        self.assertEqual(extract_date_en("day after tomorrow", ANCHOR),
                         (date(2017, 6, 29), ""))
        self.assertEqual(extract_date_en("day before yesterday", ANCHOR),
                         (date(2017, 6, 25), ""))

    def test_relative_days(self):
        self.assertEqual(extract_date_en("in 1 day", ANCHOR),
                         (date(2017, 6, 28), ""))
        self.assertEqual(extract_date_en("in 3 days", ANCHOR),
                         (date(2017, 6, 30), ""))
        self.assertEqual(extract_date_en("in 100 days", ANCHOR),
                         (date(2017, 10, 5), ""))

    def test_relative_weeks(self):
        self.assertEqual(extract_date_en("in 2 weeks", ANCHOR),
                         (date(2017, 7, 11), ""))
        self.assertEqual(extract_date_en("2 weeks ago", ANCHOR),
                         (date(2017, 6, 13), ""))
        # "next week" -> next monday
        self.assertEqual(extract_date_en("next week", ANCHOR),
                         (date(2017, 7, 3), ""))
        self.assertEqual(extract_date_en("last week", ANCHOR),
                         (date(2017, 6, 20), ""))

    def test_relative_months(self):
        # "next month" -> day 1 of next month
        self.assertEqual(extract_date_en("next month", ANCHOR),
                         (date(2017, 7, 1), ""))
        # "last month" keeps the day-of-month
        self.assertEqual(extract_date_en("last month", ANCHOR),
                         (date(2017, 5, 27), ""))
        self.assertEqual(extract_date_en("in 5 months", ANCHOR),
                         (date(2017, 11, 27), ""))

    def test_relative_years(self):
        # "next year" -> jan 1
        self.assertEqual(extract_date_en("next year", ANCHOR),
                         (date(2018, 1, 1), ""))
        self.assertEqual(extract_date_en("last year", ANCHOR),
                         (date(2016, 6, 27), ""))
        self.assertEqual(extract_date_en("3 years ago", ANCHOR),
                         (date(2014, 6, 27), ""))


class TestExtractDateWithTimeConsumed(unittest.TestCase):
    """A time in the phrase is still consumed, but only the date is returned."""

    def test_date_plus_time(self):
        self.assertEqual(extract_date_en("tomorrow at 5pm", ANCHOR),
                         (date(2017, 6, 28), ""))
        self.assertEqual(extract_date_en("next friday at 8 am", ANCHOR),
                         (date(2017, 6, 30), ""))
        self.assertEqual(
            extract_date_en("december 25th at 9 in the morning", ANCHOR),
            (date(2017, 12, 25), ""))


class TestExtractDateNone(unittest.TestCase):
    """Time-only, empty and nonsensical inputs yield no date."""

    def test_bare_time_is_not_a_date(self):
        self.assertIsNone(extract_date_en("at 5 pm", ANCHOR))
        self.assertIsNone(extract_date_en("at noon", ANCHOR))
        self.assertIsNone(extract_date_en("at midnight", ANCHOR))
        self.assertIsNone(extract_date_en("in 5 minutes", ANCHOR))
        self.assertIsNone(extract_date_en("half past 8", ANCHOR))

    def test_non_dates(self):
        self.assertIsNone(extract_date_en("no date here", ANCHOR))
        self.assertIsNone(extract_date_en("", ANCHOR))
        self.assertIsNone(extract_date_en("the the the", ANCHOR))
        self.assertIsNone(extract_date_en("12345", ANCHOR))

    def test_impossible_calendar_date(self):
        # "february 30" does not exist -> None rather than a wrong guess
        self.assertIsNone(extract_date_en("february 30", ANCHOR))
        self.assertIsNone(extract_date_en("february 29 2019", ANCHOR))


class TestExtractTimeClockForms(unittest.TestCase):
    """Absolute clock forms and am/pm."""

    def test_colon_and_ampm(self):
        # "at 7:30" with no am/pm and afternoon anchor -> 19:30 (assumed pm)
        self.assertEqual(extract_time_en("at 7:30", ANCHOR),
                         (time(19, 30), ""))
        self.assertEqual(extract_time_en("at 7 am", ANCHOR), (time(7, 0), ""))
        self.assertEqual(extract_time_en("at 7 pm", ANCHOR), (time(19, 0), ""))
        self.assertEqual(extract_time_en("at 5 pm", ANCHOR), (time(17, 0), ""))
        self.assertEqual(extract_time_en("at 23:00", ANCHOR), (time(23, 0), ""))
        self.assertEqual(extract_time_en("at 9 in the morning", ANCHOR),
                         (time(9, 0), ""))

    def test_noon_and_midnight(self):
        self.assertEqual(extract_time_en("at noon", ANCHOR), (time(12, 0), ""))
        self.assertEqual(extract_time_en("at midnight", ANCHOR),
                         (time(0, 0), ""))

    def test_remainder_preserved(self):
        self.assertEqual(extract_time_en("wake me at 8:15 pm", ANCHOR),
                         (time(20, 15), "wake me"))

    def test_twelve_oclock_colon_quirk(self):
        # QUIRK: "at 12:00" (no am/pm) rolls to hour 24, an invalid clock value,
        # so the whole extraction bails out -> None
        self.assertIsNone(extract_time_en("at 12:00", ANCHOR))


class TestExtractTimePastToForms(unittest.TestCase):
    """`half/quarter past`, `X to`, `X past` phrasings (with their quirks)."""

    def test_half_and_quarter_past_quirks(self):
        # QUIRK: the scanner does not truly compute "half/quarter past N"; it
        # reads N as the hour and assumes pm.  Values asserted as produced.
        self.assertEqual(extract_time_en("half past 8", ANCHOR),
                         (time(20, 0), "half past"))
        self.assertEqual(extract_time_en("quarter past 10", ANCHOR),
                         (time(22, 0), "quarter past"))
        self.assertEqual(extract_time_en("quarter to 9", ANCHOR),
                         (time(21, 0), "quarter to"))
        self.assertEqual(extract_time_en("20 to 5 pm", ANCHOR),
                         (time(17, 0), "20 to"))
        self.assertEqual(extract_time_en("10 past 4", ANCHOR),
                         (time(16, 0), "10 past"))


class TestExtractTimeRelative(unittest.TestCase):
    """Relative hour/minute/second offsets applied to 13:04."""

    def test_couple_of_hours(self):
        # "couple" normalises to 2 -> 13:04 + 2h = 15:04
        self.assertEqual(extract_time_en("in a couple of hours", ANCHOR),
                         (time(15, 4), ""))

    def test_minute_and_hour_and_second_offsets(self):
        self.assertEqual(extract_time_en("in 5 minutes", ANCHOR),
                         (time(13, 9), ""))
        self.assertEqual(extract_time_en("in 3 hours", ANCHOR),
                         (time(16, 4), ""))
        self.assertEqual(extract_time_en("in 30 seconds", ANCHOR),
                         (time(13, 4, 30), ""))

    def test_hours_ago(self):
        # "N hours ago" is a past offset -> 13:04 - 2h = 11:04
        self.assertEqual(extract_time_en("2 hours ago", ANCHOR),
                         (time(11, 4), ""))


class TestExtractTimeFromCombined(unittest.TestCase):
    """A date+time phrase yields the time half from extract_time_en."""

    def test_combined(self):
        self.assertEqual(extract_time_en("tomorrow at 5pm", ANCHOR),
                         (time(17, 0), ""))
        self.assertEqual(extract_time_en("next friday at 8 am", ANCHOR),
                         (time(8, 0), ""))


class TestExtractTimeNone(unittest.TestCase):
    """Date-only, empty and nonsensical inputs yield no time."""

    def test_bare_date_is_not_a_time(self):
        self.assertIsNone(extract_time_en("tomorrow", ANCHOR))
        self.assertIsNone(extract_time_en("next friday", ANCHOR))
        self.assertIsNone(extract_time_en("march 5th", ANCHOR))
        self.assertIsNone(extract_time_en("in 3 days", ANCHOR))
        self.assertIsNone(extract_time_en("yesterday", ANCHOR))

    def test_non_times(self):
        self.assertIsNone(extract_time_en("no date here", ANCHOR))
        self.assertIsNone(extract_time_en("", ANCHOR))
        self.assertIsNone(extract_time_en("february 30", ANCHOR))


class TestCombinedContract(unittest.TestCase):
    """The classic "next friday at 8 am" split: date AND time each returned."""

    def test_split(self):
        d = extract_date_en("next friday at 8 am", ANCHOR)
        t = extract_time_en("next friday at 8 am", ANCHOR)
        self.assertEqual(d, (date(2017, 6, 30), ""))
        self.assertEqual(t, (time(8, 0), ""))


class TestReferenceCoercion(unittest.TestCase):
    """ref_date/ref_time accept datetime or bare date; None uses now_local."""

    def test_bare_date_coerced_to_midnight(self):
        self.assertEqual(extract_date_en("tomorrow", date(2017, 6, 27)),
                         (date(2017, 6, 28), ""))

    def test_datetime_passthrough(self):
        self.assertEqual(extract_date_en("tomorrow", ANCHOR),
                         (date(2017, 6, 28), ""))

    def test_time_ref_as_bare_date(self):
        # midnight anchor: "in 3 hours" -> 03:00
        self.assertEqual(extract_time_en("in 3 hours", date(2017, 6, 27)),
                         (time(3, 0), ""))

    def test_none_ref_does_not_raise(self):
        # falls back to now_local(); we only assert it runs and stays typed
        r = extract_date_en("tomorrow")
        self.assertIsInstance(r, tuple)
        self.assertIsInstance(r[0], date)


class TestNeverRaises(unittest.TestCase):
    """Garbage input must return None (or a valid tuple), never raise."""

    GARBAGE = [
        "", " ", "?", "!!!", "the the the", "12345", "0", "-1",
        "at 25 o'clock", "february 30", "february 29 2019", "99:99",
        "2400", "24:00", "999999999999 hours", "in -5 minutes",
        "june 31st", "the 3rd of blursday", "at o'clock", ":::",
        "aaaa bbbb cccc", "5 5 5 5 5", "next next next", "of of of",
    ]

    def test_extract_date_never_raises(self):
        for text in self.GARBAGE:
            try:
                res = extract_date_en(text, ANCHOR)
            except Exception as exc:  # pragma: no cover - failure path
                self.fail(f"extract_date_en raised on {text!r}: {exc!r}")
            self.assertTrue(res is None or isinstance(res, tuple))

    def test_extract_time_never_raises(self):
        for text in self.GARBAGE:
            try:
                res = extract_time_en(text, ANCHOR)
            except Exception as exc:  # pragma: no cover - failure path
                self.fail(f"extract_time_en raised on {text!r}: {exc!r}")
            self.assertTrue(res is None or isinstance(res, tuple))

    def test_adversarial_out_of_range_clock_none(self):
        self.assertIsNone(extract_time_en("at 25 o'clock", ANCHOR))
        self.assertIsNone(extract_time_en("2400", ANCHOR))
        self.assertIsNone(extract_time_en("24:00", ANCHOR))

    def test_bare_numbers_are_neither_here(self):
        # a lone small number is read as a bare clock hour, not a date; the
        # afternoon anchor pushes the ambiguous "7" to 19:00
        self.assertIsNone(extract_date_en("7", ANCHOR))
        self.assertEqual(extract_time_en("7", ANCHOR), (time(19, 0), ""))
        # oversized offset cannot be represented -> both None
        self.assertIsNone(extract_date_en("999999999999 hours", ANCHOR))
        self.assertIsNone(extract_time_en("999999999999 hours", ANCHOR))


if __name__ == "__main__":
    unittest.main()
