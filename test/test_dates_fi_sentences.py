"""Finnish datetime extraction: natural phrasing, relative offsets and edge cases."""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2117, 9, 3, 13, 30, 0)
TZ = default_timezone()


def extract(text, lang="fi", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestRelativeSecondsOffset(unittest.TestCase):
    """"N sekunnin päästä/kuluttua" adds a seconds offset to the anchor time."""

    def test_fifteen_seconds_digits(self):
        self.assertEqual(extract("15 sekunnin päästä")[0],
                         dt(2117, 9, 3, 13, 30, 15))

    def test_fifteen_seconds_spelled(self):
        self.assertEqual(extract("viidentoista sekunnin päästä")[0],
                         dt(2117, 9, 3, 13, 30, 15))

    def test_thirty_seconds_kuluttua(self):
        self.assertEqual(extract("30 sekunnin kuluttua")[0],
                         dt(2117, 9, 3, 13, 30, 30))

    def test_five_seconds_paahan(self):
        self.assertEqual(extract("5 sekunnin päähän")[0],
                         dt(2117, 9, 3, 13, 30, 5))

    def test_seconds_preserve_anchor_seconds(self):
        anchor = datetime(2117, 9, 3, 13, 30, 42)
        self.assertEqual(extract("20 sekunnin päästä", anchor=anchor)[0],
                         dt(2117, 9, 3, 13, 31, 2))

    def test_seconds_rollover_minute(self):
        self.assertEqual(extract("45 sekunnin päästä")[0],
                         dt(2117, 9, 3, 13, 30, 45))


class TestRelativeOffsetsStillWork(unittest.TestCase):
    """Adding seconds must not disturb the existing minute/hour offsets."""

    def test_minutes_offset(self):
        self.assertEqual(extract("15 minuutin päästä")[0],
                         dt(2117, 9, 3, 13, 45))

    def test_hours_offset(self):
        self.assertEqual(extract("3 tunnin päästä")[0],
                         dt(2117, 9, 3, 16, 30))

    def test_minutes_zero_the_seconds(self):
        anchor = datetime(2117, 9, 3, 13, 30, 42)
        self.assertEqual(extract("15 minuutin päästä", anchor=anchor)[0],
                         dt(2117, 9, 3, 13, 45, 0))


class TestClockAndEdgeCases(unittest.TestCase):
    """Clock idioms parse; impossible dates return None rather than crashing."""

    def test_quarter_past_seven(self):
        self.assertEqual(extract("varttia yli seitsemän")[0].hour, 7)
        self.assertEqual(extract("varttia yli seitsemän")[0].minute, 15)

    def test_impossible_february_day(self):
        self.assertIsNone(extract("30 helmikuuta"))

    def test_leap_day_non_leap_year(self):
        self.assertIsNone(extract("29 helmikuuta", anchor=datetime(2119, 1, 1)))

    def test_leap_day_leap_year(self):
        self.assertEqual(extract("29 helmikuuta", anchor=datetime(2120, 1, 1))[0],
                         dt(2120, 2, 29))

    def test_gibberish_returns_none(self):
        self.assertIsNone(extract("xyzzy plugh"))


if __name__ == "__main__":
    unittest.main()
