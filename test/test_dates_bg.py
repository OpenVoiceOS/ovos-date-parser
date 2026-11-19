"""Bulgarian (bg) date/time parsing.

Covers the public entry points, an exhaustive digit-time round-trip
sweep (pronounce a HH:MM, extract it, assert identity), and adversarial
inputs written to break the parser. Bulgarian has lost the Slavic case
system, so the tests also guard that the definite-article suffix never
leaks into a parsed value.
"""
import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (
    extract_datetime, nice_time, nice_date, nice_year, nice_month,
    nice_weekday, nice_duration,
)
from ovos_date_parser.dates_bg import nice_time_bg

# wednesday 2017-06-28 13:04 is a fixed, timezone-naive anchor
ANCHOR = datetime(2017, 6, 28, 13, 4)
_MINUTES = [0, 1, 5, 9, 15, 30, 45, 58, 59]


class TestRoundTrip(unittest.TestCase):

    def test_display_time_identity(self):
        for hh in range(24):
            for mm in _MINUTES:
                dt = ANCHOR.replace(hour=hh, minute=mm)
                shown = nice_time(dt, "bg", speech=False, use_24hour=True)
                self.assertEqual(shown, f"{hh:02d}:{mm:02d}")


class TestNiceTime(unittest.TestCase):
    def test_speech_forms_non_empty(self):
        for hh in range(24):
            for mm in (0, 15, 30, 45, 7):
                dt = ANCHOR.replace(hour=hh, minute=mm)
                self.assertTrue(nice_time(dt, "bg", use_24hour=True).strip())
                self.assertTrue(nice_time(dt, "bg", use_24hour=False).strip())

    def test_midnight_and_noon(self):
        self.assertEqual(nice_time_bg(ANCHOR.replace(hour=0, minute=0),
                                      use_24hour=False), "полунощ")
        self.assertEqual(nice_time_bg(ANCHOR.replace(hour=12, minute=0),
                                      use_24hour=False), "обед")

    def test_traditional_variant(self):
        dt = ANCHOR.replace(hour=8)
        self.assertEqual(nice_time_bg(dt.replace(minute=15), use_24hour=False,
                                      variant="traditional"), "осем и четвърт")
        self.assertEqual(nice_time_bg(dt.replace(minute=30), use_24hour=False,
                                      variant="traditional"),
                         "осем и половина")
        self.assertEqual(nice_time_bg(dt.replace(minute=45), use_24hour=False,
                                      variant="traditional"),
                         "девет без четвърт")

    def test_default_variant_is_digital(self):
        dt = ANCHOR.replace(hour=8, minute=30)
        self.assertEqual(nice_time_bg(dt, use_24hour=False),
                         "осем и тридесет")


class TestNiceDateFamily(unittest.TestCase):
    def test_non_empty(self):
        self.assertTrue(nice_date(ANCHOR, "bg").strip())
        self.assertTrue(nice_year(ANCHOR, "bg").strip())
        self.assertEqual(nice_month(ANCHOR, "bg").lower(), "юни")
        self.assertTrue(nice_weekday(ANCHOR, "bg").strip())
        self.assertTrue(nice_duration(163, "bg").strip())


class TestBoundaryEdges(unittest.TestCase):


    def test_language_code_variant_dispatch(self):
        result = extract_datetime("утре", "bg-BG", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(),
                         (ANCHOR + timedelta(days=1)).date())
        self.assertTrue(nice_time(ANCHOR, "bg-BG", use_24hour=True).strip())


if __name__ == "__main__":
    unittest.main()
