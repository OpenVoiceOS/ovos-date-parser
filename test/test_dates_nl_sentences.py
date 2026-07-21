"""Dutch datetime extraction: natural phrasing and malformed-input hardening.

The adversarial cases guard against a regression where out-of-range clock
values, impossible calendar dates and absurd offsets raised exceptions
instead of reporting nothing.
"""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(1998, 1, 1)
TZ = default_timezone()


def extract(text, lang="nl", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestNaturalPhrasing(unittest.TestCase):
    """Ordinary Dutch date/time sentences must keep parsing correctly."""

    def test_bare_hour(self):
        self.assertEqual(extract("om 7 uur")[0], dt(1998, 1, 1, 7))

    def test_24h_hour(self):
        self.assertEqual(extract("om 19 uur")[0], dt(1998, 1, 1, 19))

    def test_relative_minutes(self):
        self.assertEqual(extract("over 15 minuten")[0], dt(1998, 1, 1, 0, 15))

    def test_relative_hours(self):
        self.assertEqual(extract("over 3 uur")[0], dt(1998, 1, 1, 3))

    def test_relative_seconds(self):
        self.assertEqual(extract("over 5 seconden")[0], dt(1998, 1, 1, 0, 0, 5))

    def test_relative_days(self):
        self.assertEqual(extract("over 2 dagen")[0], dt(1998, 1, 3))

    def test_tomorrow(self):
        self.assertEqual(extract("morgen")[0], dt(1998, 1, 2))

    def test_tomorrow_at_time(self):
        self.assertEqual(extract("morgen om 10 uur")[0], dt(1998, 1, 2, 10))

    def test_next_week(self):
        self.assertEqual(extract("volgende week")[0], dt(1998, 1, 8))

    def test_next_year(self):
        self.assertEqual(extract("volgend jaar")[0], dt(1999, 1, 1))

    def test_clock_time(self):
        self.assertEqual(extract("23:30")[0], dt(1998, 1, 1, 23, 30))

    def test_explicit_date(self):
        self.assertEqual(extract("5 januari 2020")[0], dt(2020, 1, 5))


class TestMalformedInputReturnsNone(unittest.TestCase):
    """Impossible input must report nothing, never raise."""

    def test_hour_24_clock(self):
        self.assertIsNone(extract("2400"))

    def test_hour_24_colon(self):
        self.assertIsNone(extract("24:00"))

    def test_hour_25(self):
        self.assertIsNone(extract("25:30"))

    def test_minute_out_of_range(self):
        self.assertIsNone(extract("12:99"))

    def test_impossible_day_in_month(self):
        self.assertIsNone(extract("30 februari"))

    def test_non_leap_29_february(self):
        self.assertIsNone(extract("29 februari 2019"))

    def test_impossible_day_number(self):
        self.assertIsNone(extract("99 januari"))

    def test_absurd_hour_offset(self):
        self.assertIsNone(extract("999999999999 uur"))

    def test_absurd_minute_offset(self):
        self.assertIsNone(extract("over 999999999999 minuten"))

    def test_absurd_day_offset(self):
        self.assertIsNone(extract("over 999999999999 dagen"))


class TestAdversarialDoesNotCrash(unittest.TestCase):
    """A broad fuzz of ill-formed strings must never raise."""

    CASES = [
        "", " ", "2400", "24:00", "25:99", "99:99", "0000",
        "30 februari", "29 februari 2019", "31 april", "32 januari",
        "999999999999 uur", "over 999999999999 seconden",
        "uur uur uur", "half", "kwart", "over", "om om om",
        "-1 uur", "over -5 minuten", "13de maand", "0 februari",
    ]

    def test_no_crash(self):
        for text in self.CASES:
            with self.subTest(text=text):
                try:
                    extract(text)
                except Exception as exc:  # noqa: BLE001
                    self.fail(f"extract({text!r}) raised {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    unittest.main()
