"""Italian datetime extraction: natural phrasing and malformed-input hardening.

Malformed clock values and impossible/garbage numeric tokens must never raise;
they resolve to ``None`` (no time found). A handful of valid natural sentences
guard against regressions in the good path.
"""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2117, 9, 3, 13, 30, 0)
TZ = default_timezone()


def extract(text, lang="it", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestMalformedInputDoesNotCrash(unittest.TestCase):
    """Garbage or out-of-range clock tokens must return None, never raise."""

    NON_TIMES = [
        "0",
        "99",
        "12345",
        "0000",
        "at 25",
        "25:99",
        "12:60",
        "24:00",
        "february 30",
        "999999999999 hours",
        "1234567890 seconds",
        "tomorrow at 99",
    ]

    def test_returns_none_without_crashing(self):
        for text in self.NON_TIMES:
            with self.subTest(text=text):
                self.assertIsNone(extract(text))

    def test_out_of_range_colon_time_is_none(self):
        # hour > 23 or minute > 59 are not valid clock values
        self.assertIsNone(extract("25:99"))
        self.assertIsNone(extract("12:60"))
        self.assertIsNone(extract("24:00"))

    def test_bare_out_of_range_hour_is_none(self):
        self.assertIsNone(extract("99"))
        self.assertIsNone(extract("12345"))


class TestValidSentencesStillWork(unittest.TestCase):
    """Regression guard: known-good Italian phrasings keep resolving."""

    def test_spoken_bare_hour(self):
        self.assertEqual(extract("alle tre")[0], dt(2117, 9, 3, 15, 0))

    def test_digit_clock(self):
        self.assertEqual(extract("alle 15:30")[0], dt(2117, 9, 3, 15, 30))

    def test_evening_qualifier(self):
        self.assertEqual(extract("alle 8 di sera")[0], dt(2117, 9, 3, 20, 0))

    def test_relative_seconds_offset(self):
        self.assertEqual(extract("tra 15 secondi")[0], dt(2117, 9, 3, 13, 30, 15))
        self.assertEqual(extract("tra 30 secondi")[0], dt(2117, 9, 3, 13, 30, 30))

    def test_noon(self):
        self.assertEqual(extract("a mezzogiorno")[0], dt(2117, 9, 4, 12, 0))


if __name__ == "__main__":
    unittest.main()
