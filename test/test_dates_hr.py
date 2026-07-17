"""Croatian (hr) date/time parsing.

Covers the public entry points, an exhaustive digit-time round-trip
sweep (pronounce a HH:MM, extract it, assert identity), and adversarial
inputs written to break the parser.
"""
import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (
    extract_datetime, nice_time, nice_date, nice_year, nice_month,
    nice_weekday, nice_duration,
)
from ovos_date_parser.dates_hr import (
    nice_time_hr, extract_datetime_hr, extract_duration_hr,
)

# wednesday 2017-06-28 13:04 is a fixed, timezone-naive anchor
ANCHOR = datetime(2017, 6, 28, 13, 4)
_MINUTES = [0, 1, 5, 9, 15, 30, 45, 58, 59]


class TestRoundTrip(unittest.TestCase):
    def test_digit_time_identity(self):
        checked = 0
        for hh in range(24):
            for mm in _MINUTES:
                text = f"{hh}:{mm:02d}"
                result = extract_datetime_hr(text, anchorDate=ANCHOR)
                self.assertIsNotNone(result, text)
                self.assertEqual((result[0].hour, result[0].minute),
                                 (hh, mm), text)
                checked += 1
        self.assertGreaterEqual(checked, 200)

    def test_display_time_identity(self):
        for hh in range(24):
            for mm in _MINUTES:
                dt = ANCHOR.replace(hour=hh, minute=mm)
                shown = nice_time(dt, "hr", speech=False, use_24hour=True)
                self.assertEqual(shown, f"{hh:02d}:{mm:02d}")


class TestNiceTime(unittest.TestCase):
    def test_speech_forms_non_empty(self):
        for hh in range(24):
            for mm in (0, 15, 30, 45, 7):
                dt = ANCHOR.replace(hour=hh, minute=mm)
                self.assertTrue(nice_time(dt, "hr", use_24hour=True).strip())
                self.assertTrue(nice_time(dt, "hr", use_24hour=False).strip())

    def test_midnight_and_noon(self):
        self.assertEqual(nice_time_hr(ANCHOR.replace(hour=0, minute=0),
                                      use_24hour=False), "ponoć")
        self.assertEqual(nice_time_hr(ANCHOR.replace(hour=12, minute=0),
                                      use_24hour=False), "podne")


class TestExtractDatetime(unittest.TestCase):
    def test_relative_days(self):
        cases = {
            "danas": 0,
            "sutra": 1,
            "prekosutra": 2,
            "jučer": -1,
            "prekjučer": -2,
        }
        for phrase, offset in cases.items():
            result = extract_datetime_hr(phrase, anchorDate=ANCHOR)
            self.assertIsNotNone(result, phrase)
            self.assertEqual(result[0].date(),
                             (ANCHOR + timedelta(days=offset)).date(), phrase)

    def test_weekday(self):
        result = extract_datetime_hr("u petak", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0].weekday(), 4)

    def test_weekday_accusative(self):
        result = extract_datetime_hr("u srijedu", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0].weekday(), 2)

    def test_explicit_date(self):
        result = extract_datetime_hr("15. kolovoza", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual((result[0].month, result[0].day), (8, 15))

    def test_date_with_year(self):
        result = extract_datetime_hr("15. kolovoza 2020", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual((result[0].year, result[0].month, result[0].day),
                         (2020, 8, 15))

    def test_offset_minutes(self):
        result = extract_datetime_hr("za 5 minuta", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], ANCHOR + timedelta(minutes=5))

    def test_leftover_text_returned(self):
        result = extract_datetime_hr("kakvo je vrijeme sutra",
                                     anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertNotIn("sutra", result[1])
        self.assertIn("vrijeme", result[1])


class TestExtractDuration(unittest.TestCase):
    def test_minutes(self):
        self.assertEqual(extract_duration_hr("10 minuta")[0],
                         timedelta(minutes=10))

    def test_compound(self):
        self.assertEqual(extract_duration_hr("2 sata 30 minuta")[0],
                         timedelta(hours=2, minutes=30))

    def test_spelled_number(self):
        self.assertEqual(extract_duration_hr("pet minuta")[0],
                         timedelta(minutes=5))


class TestNiceDateFamily(unittest.TestCase):
    def test_non_empty(self):
        self.assertTrue(nice_date(ANCHOR, "hr").strip())
        self.assertTrue(nice_year(ANCHOR, "hr").strip())
        self.assertEqual(nice_month(ANCHOR, "hr").lower(), "lipanj")
        self.assertTrue(nice_weekday(ANCHOR, "hr").strip())
        self.assertTrue(nice_duration(163, "hr").strip())


class TestAdversarial(unittest.TestCase):
    def test_empty_and_blank(self):
        self.assertIsNone(extract_datetime_hr("", anchorDate=ANCHOR))
        self.assertIsNone(extract_datetime_hr("   ", anchorDate=ANCHOR))

    def test_no_date_text(self):
        self.assertIsNone(extract_datetime_hr("bok kako si",
                                              anchorDate=ANCHOR))

    def test_impossible_clock_values(self):
        for bad in ("99:99", "25:61", "40:00", "13:75"):
            self.assertIsNone(extract_datetime_hr(bad, anchorDate=ANCHOR), bad)

    def test_boundary_clock_values(self):
        self.assertEqual(extract_datetime_hr("00:00", anchorDate=ANCHOR)[0]
                         .hour, 0)
        self.assertEqual(extract_datetime_hr("24:00", anchorDate=ANCHOR)[0]
                         .hour, 0)

    def test_duration_empty_is_none(self):
        self.assertIsNone(extract_duration_hr(""))

    def test_duration_junk_yields_no_value(self):
        duration, remainder = extract_duration_hr("nema trajanja ovdje")
        self.assertIsNone(duration)

    def test_garbage_is_rejected(self):
        self.assertIsNone(extract_datetime_hr("qwerty zxcvb",
                                              anchorDate=ANCHOR))

    def test_lone_ordinal_dot_not_crash(self):
        result = extract_datetime_hr("15.", anchorDate=ANCHOR)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
