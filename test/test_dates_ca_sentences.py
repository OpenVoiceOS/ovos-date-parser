"""Catalan datetime extraction: natural phrasing, relative offsets and edge cases."""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

# anchor carries a non-trivial time of day so relative offsets are exercised
ANCHOR = datetime(2117, 9, 3, 13, 30, 0)
TZ = default_timezone()


def extract(text, anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang="ca", anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestRelativeOffsetKeepsAnchorTime(unittest.TestCase):
    """Purely relative offsets must add onto the anchor time of day, not midnight."""

    def test_seconds(self):
        date, leftover = extract("d'aquí a 15 segons")
        self.assertEqual(date, dt(2117, 9, 3, 13, 30, 15))
        self.assertEqual(leftover, "")

    def test_one_second_singular(self):
        self.assertEqual(extract("d'aquí a 1 segon")[0], dt(2117, 9, 3, 13, 30, 1))

    def test_minutes(self):
        date, leftover = extract("d'aquí a 15 minuts")
        self.assertEqual(date, dt(2117, 9, 3, 13, 45))
        self.assertEqual(leftover, "")

    def test_one_minute_singular(self):
        self.assertEqual(extract("d'aquí a 1 minut")[0], dt(2117, 9, 3, 13, 31))

    def test_ninety_minutes_rolls_hour(self):
        self.assertEqual(extract("d'aquí a 90 minuts")[0], dt(2117, 9, 3, 15, 0))

    def test_hours(self):
        date, leftover = extract("d'aquí a 3 hores")
        self.assertEqual(date, dt(2117, 9, 3, 16, 30))
        self.assertEqual(leftover, "")

    def test_one_hour_singular(self):
        self.assertEqual(extract("d'aquí a 1 hora")[0], dt(2117, 9, 3, 14, 30))

    def test_two_hours(self):
        self.assertEqual(extract("d'aquí a 2 hores")[0], dt(2117, 9, 3, 15, 30))

    def test_twenty_four_hours_rolls_day(self):
        self.assertEqual(extract("d'aquí a 24 hores")[0], dt(2117, 9, 4, 13, 30))

    def test_future_marker_fully_consumed(self):
        # the "d'aquí a" future marker must not leak into the remainder
        for phrase in ("d'aquí a 15 segons", "d'aquí a 15 minuts",
                       "d'aquí a 3 hores"):
            with self.subTest(phrase=phrase):
                self.assertEqual(extract(phrase)[1], "")


class TestRelativeDayOffset(unittest.TestCase):
    """Day-level relative offsets resolve to midnight of the target day."""

    def test_five_days(self):
        self.assertEqual(extract("d'aquí a 5 dies")[0], dt(2117, 9, 8))

    def test_tomorrow(self):
        self.assertEqual(extract("demà")[0], dt(2117, 9, 4))

    def test_yesterday(self):
        self.assertEqual(extract("ahir")[0], dt(2117, 9, 2))

    def test_today(self):
        self.assertEqual(extract("avui")[0], dt(2117, 9, 3))


class TestAbsoluteClockTimes(unittest.TestCase):
    """Explicit clock times and parts of day."""

    def test_afternoon(self):
        self.assertEqual(extract("a les 3 de la tarda")[0], dt(2117, 9, 3, 15))

    def test_colon_evening(self):
        self.assertEqual(extract("a les 23:30")[0], dt(2117, 9, 3, 23, 30))

    def test_colon_midnight(self):
        self.assertEqual(extract("a les 00:00")[0], dt(2117, 9, 3, 0, 0))

    def test_morning_rolls_to_next_day(self):
        # 08:00 already passed relative to the 13:30 anchor -> next day
        self.assertEqual(extract("a les 8 del matí")[0], dt(2117, 9, 4, 8))


class TestCalendarDates(unittest.TestCase):
    """Explicit calendar dates with an explicit year."""

    def test_day_month_year(self):
        self.assertEqual(extract("el 15 de març de 2030")[0], dt(2030, 3, 15))

    def test_valid_leap_day(self):
        self.assertEqual(extract("el 29 de febrer de 2020")[0], dt(2020, 2, 29))


class TestImpossibleDatesReturnNone(unittest.TestCase):
    """Out-of-range calendar dates must return None, never raise."""

    def test_february_31(self):
        self.assertIsNone(extract("el 31 de febrer"))

    def test_february_30(self):
        self.assertIsNone(extract("el 30 de febrer de 2020"))

    def test_non_leap_february_29(self):
        self.assertIsNone(extract("reunió el 29 de febrer de 2021"))

    def test_impossible_hour(self):
        self.assertIsNone(extract("a les 25:00"))

    def test_impossible_minute(self):
        self.assertIsNone(extract("a les 15:70"))


class TestNoDateReturnsNone(unittest.TestCase):
    """Text with no temporal content yields None rather than a spurious date."""

    def test_empty(self):
        self.assertIsNone(extract(""))

    def test_plain_sentence(self):
        self.assertIsNone(extract("posa una cançó"))

    def test_non_latin_junk(self):
        self.assertIsNone(extract("посылка"))


class TestNumericTimeWithLetterSuffix(unittest.TestCase):
    """Glued time tokens like "20h" must parse, never raise on int() of the raw token."""

    def test_bare_hour_suffix(self):
        self.assertEqual(extract("20h")[0], dt(2117, 9, 3, 20, 0))

    def test_a_les_hour_suffix(self):
        self.assertEqual(extract("a les 20h")[0], dt(2117, 9, 3, 20, 0))

    def test_hour_minute_suffix(self):
        self.assertEqual(extract("21h30")[0], dt(2117, 9, 3, 21, 30))

    def test_a_les_hour_minute_suffix(self):
        self.assertEqual(extract("a les 21h30")[0], dt(2117, 9, 3, 21, 30))

    def test_impossible_hour_suffix_no_crash(self):
        # out-of-range hour must resolve to None, not raise
        self.assertIsNone(extract("a les 99h"))

    def test_non_numeric_suffix_no_crash(self):
        # gibberish glued token must not reach int() and blow up
        self.assertIsNone(extract("a les xxh"))


if __name__ == "__main__":
    unittest.main()
