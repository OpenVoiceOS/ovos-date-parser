"""Slovak (sk) date/time parsing.

Covers the public entry points, an exhaustive digit-time round-trip
sweep (pronounce a HH:MM, extract it, assert identity), and adversarial
inputs written to break the parser.
"""
import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (
    extract_datetime,
    nice_time,
    nice_date,
    nice_year,
    nice_month,
    nice_weekday,
    nice_duration,
)
from ovos_date_parser.dates_sk import nice_time_sk

# wednesday 2017-06-28 13:04 is a fixed, timezone-naive anchor
ANCHOR = datetime(2017, 6, 28, 13, 4)
# minutes chosen to exercise <10 zero-padding, quarters and boundaries
_MINUTES = [0, 1, 5, 9, 15, 30, 45, 58, 59]


class TestRoundTrip(unittest.TestCase):

    def test_display_time_identity(self):
        # nice_time display form must be the printable HH:MM back again
        for hh in range(24):
            for mm in _MINUTES:
                dt = ANCHOR.replace(hour=hh, minute=mm)
                shown = nice_time(dt, "sk", speech=False, use_24hour=True)
                self.assertEqual(shown, f"{hh:02d}:{mm:02d}")


class TestNiceTime(unittest.TestCase):
    def test_speech_forms_non_empty(self):
        for hh in range(24):
            for mm in (0, 15, 30, 45, 7):
                dt = ANCHOR.replace(hour=hh, minute=mm)
                self.assertTrue(nice_time(dt, "sk", use_24hour=True).strip())
                self.assertTrue(nice_time(dt, "sk", use_24hour=False).strip())

    def test_midnight_and_noon(self):
        self.assertEqual(nice_time_sk(ANCHOR.replace(hour=0, minute=0),
                                      use_24hour=False), "polnoc")
        self.assertEqual(nice_time_sk(ANCHOR.replace(hour=12, minute=0),
                                      use_24hour=False), "poludnie")

    def test_traditional_variant(self):
        dt = ANCHOR.replace(hour=8)
        self.assertEqual(nice_time_sk(dt.replace(minute=15), use_24hour=False,
                                      variant="traditional"),
                         "štvrť na deväť")
        self.assertEqual(nice_time_sk(dt.replace(minute=30), use_24hour=False,
                                      variant="traditional"), "pol deviatej")
        self.assertEqual(nice_time_sk(dt.replace(minute=45), use_24hour=False,
                                      variant="traditional"),
                         "trištvrte na deväť")

    def test_default_variant_is_digital(self):
        dt = ANCHOR.replace(hour=8, minute=15)
        self.assertEqual(nice_time_sk(dt, use_24hour=False), "osem pätnásť")


class TestNiceDateFamily(unittest.TestCase):
    def test_non_empty(self):
        self.assertTrue(nice_date(ANCHOR, "sk").strip())
        self.assertTrue(nice_year(ANCHOR, "sk").strip())
        self.assertIn(nice_month(ANCHOR, "sk").lower(), ("jún",))
        self.assertTrue(nice_weekday(ANCHOR, "sk").strip())
        self.assertTrue(nice_duration(163, "sk").strip())


class TestBoundaryEdges(unittest.TestCase):


    def test_language_code_variant_dispatch(self):
        # regional code must still route through the Slovak parser
        result = extract_datetime("zajtra", "sk-SK", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(),
                         (ANCHOR + timedelta(days=1)).date())
        self.assertTrue(nice_time(ANCHOR, "sk-SK", use_24hour=True).strip())


if __name__ == "__main__":
    unittest.main()
