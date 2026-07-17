"""Occitan datetime extraction: natural phrasing, relative offsets and edge cases."""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

# whole-second anchor with a non-trivial time of day, so a midnight-based
# offset is visibly different from an anchor-based one
ANCHOR = datetime(2117, 9, 3, 13, 30, 0)
TZ = default_timezone()


def extract(text, lang="oc", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestRelativeOffsetKeepsAnchorTime(unittest.TestCase):
    """Purely relative future offsets are added on the anchor time of day."""

    def test_seconds_offset(self):
        self.assertEqual(extract("d'aquí 15 segondas")[0], dt(2117, 9, 3, 13, 30, 15))

    def test_single_second_singular(self):
        self.assertEqual(extract("d'aquí 1 segonda")[0], dt(2117, 9, 3, 13, 30, 1))

    def test_minutes_offset(self):
        self.assertEqual(extract("d'aquí 15 minutas")[0], dt(2117, 9, 3, 13, 45))

    def test_single_minute_singular(self):
        self.assertEqual(extract("d'aquí 1 minuta")[0], dt(2117, 9, 3, 13, 31))

    def test_hours_offset(self):
        self.assertEqual(extract("d'aquí 3 oras")[0], dt(2117, 9, 3, 16, 30))

    def test_single_hour_digit(self):
        self.assertEqual(extract("d'aquí 1 ora")[0], dt(2117, 9, 3, 14, 30))

    def test_single_hour_spoken(self):
        self.assertEqual(extract("d'aquí una ora")[0], dt(2117, 9, 3, 14, 30))

    def test_half_hour(self):
        self.assertEqual(extract("d'aquí mièja ora")[0], dt(2117, 9, 3, 14, 0))

    def test_minutes_roll_into_next_hour(self):
        # 13:30 + 90 min -> 15:00
        self.assertEqual(extract("d'aquí 90 minutas")[0], dt(2117, 9, 3, 15, 0))

    def test_seconds_roll_into_next_minute(self):
        # 13:30:00 + 120 s -> 13:32:00
        self.assertEqual(extract("d'aquí 120 segondas")[0], dt(2117, 9, 3, 13, 32, 0))

    def test_hours_wrap_past_midnight(self):
        # 13:30 + 12 h -> 01:30 next day
        self.assertEqual(extract("d'aquí 12 oras")[0], dt(2117, 9, 4, 1, 30))


class TestRelativeOffsetConsumesMarker(unittest.TestCase):
    """The future marker "d'aquí" is consumed and does not leak into remainder."""

    def test_clean_remainder_hours(self):
        self.assertEqual(extract("d'aquí 3 oras")[1], "")

    def test_clean_remainder_minutes(self):
        self.assertEqual(extract("d'aquí 15 minutas")[1], "")

    def test_reminder_keeps_verb(self):
        res = extract("revèlha-me d'aquí 3 oras")
        self.assertEqual(res[0], dt(2117, 9, 3, 16, 30))
        self.assertNotIn("aqui", res[1])


class TestAbsoluteClock(unittest.TestCase):

    def test_iso_clock(self):
        self.assertEqual(extract("17:30")[0], dt(2117, 9, 3, 17, 30))

    def test_quarter_past_seven(self):
        self.assertEqual(extract("a las 8 e quart")[0], dt(2117, 9, 4, 8, 15))

    def test_half_past_seven(self):
        self.assertEqual(extract("a las 8 e mièja")[0], dt(2117, 9, 4, 8, 30))

    def test_half_past_afternoon(self):
        self.assertEqual(extract("a las 8 e mièja del vespre")[0], dt(2117, 9, 3, 20, 30))

    def test_manca_un_quart(self):
        self.assertEqual(extract("a las 8 manca un quart")[0], dt(2117, 9, 4, 7, 45))

    def test_morning_qualifier(self):
        self.assertEqual(extract("a las 8 del matin")[0], dt(2117, 9, 4, 8, 0))

    def test_tomorrow_with_clock(self):
        self.assertEqual(extract("deman a las 9 del matin")[0], dt(2117, 9, 4, 9, 0))


class TestDayOffsets(unittest.TestCase):

    def test_in_n_days(self):
        self.assertEqual(extract("en 5 jorns")[0], dt(2117, 9, 8, 0, 0))

    def test_in_n_weeks(self):
        self.assertEqual(extract("en 5 setmanas")[0], dt(2117, 10, 8, 0, 0))

    def test_days_plus_clock(self):
        self.assertEqual(extract("en 2 jorns a las 15")[0], dt(2117, 9, 5, 15, 0))

    def test_tomorrow(self):
        self.assertEqual(extract("deman")[0], dt(2117, 9, 4, 0, 0))


class TestImpossibleAndAbsentDates(unittest.TestCase):
    """Impossible or absent dates return None instead of raising."""

    def test_february_30_returns_none(self):
        self.assertIsNone(extract("30 de febrier"))

    def test_april_31_returns_none(self):
        self.assertIsNone(extract("31 de abril"))

    def test_no_date_returns_none(self):
        self.assertIsNone(extract("banana"))

    def test_empty_string_returns_none(self):
        self.assertIsNone(extract(""))

    def test_impossible_clock_returns_none(self):
        # 25 is not a valid hour
        self.assertIsNone(extract("a las 25"))

    def test_valid_future_date(self):
        self.assertEqual(extract("15 de julhet")[0], dt(2118, 7, 15, 0, 0))

    def test_valid_date_with_year(self):
        self.assertEqual(extract("1 de genier de 2119")[0], dt(2119, 1, 1, 0, 0))


class TestNumericTimeTokensWithLetterSuffix(unittest.TestCase):
    """Glued time tokens like '20h' must parse without raising ValueError."""

    def test_bare_hour_suffix(self):
        self.assertEqual(extract("20h")[0], dt(2117, 9, 3, 20, 0))

    def test_preposition_hour_suffix(self):
        self.assertEqual(extract("a 20h")[0], dt(2117, 9, 3, 20, 0))

    def test_hour_minute_suffix(self):
        self.assertEqual(extract("21h30")[0], dt(2117, 9, 3, 21, 30))

    def test_impossible_glued_hour_does_not_raise(self):
        # 99h is not a valid clock reading; must not crash on the letter suffix
        try:
            extract("99h")
        except ValueError:
            self.fail("extract('99h') raised ValueError")

    def test_letter_only_token_does_not_raise(self):
        try:
            self.assertIsNone(extract("hhh"))
        except ValueError:
            self.fail("extract('hhh') raised ValueError")


if __name__ == "__main__":
    unittest.main()
