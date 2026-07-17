"""English datetime extraction: malformed input must never raise."""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2117, 9, 3, 13, 30, 0)
TZ = default_timezone()


def extract(text, lang="en", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0):
    return datetime(y, mo, d, h, mi, tzinfo=TZ)


class TestMalformedClockValues(unittest.TestCase):
    """Out-of-range clock values must return None, never raise."""

    def test_bare_2400_returns_none(self):
        # "2400" maps to hour 24, which is not a valid clock time
        self.assertIsNone(extract("2400"))

    def test_colon_2400_returns_none(self):
        # "24:00" likewise exceeds the 0..23 hour range
        self.assertIsNone(extract("24:00"))


class TestOversizedOffsets(unittest.TestCase):
    """Relative offsets too large to represent must return None, never raise."""

    def test_absurd_hour_offset_returns_none(self):
        self.assertIsNone(extract("999999999999 hours"))

    def test_absurd_year_offset_returns_none(self):
        self.assertIsNone(extract("in 999999999999 years"))


class TestValidSentencesUnaffected(unittest.TestCase):
    """Well-formed inputs must keep parsing correctly."""

    def test_tomorrow_at_five_pm(self):
        self.assertEqual(extract("tomorrow at 5pm")[0], dt(2117, 9, 4, 17, 0))

    def test_in_two_hours(self):
        self.assertEqual(extract("in 2 hours")[0], dt(2117, 9, 3, 15, 30))

    def test_explicit_calendar_date(self):
        self.assertEqual(extract("june 5")[0], dt(2118, 6, 5, 0, 0))


if __name__ == "__main__":
    unittest.main()
