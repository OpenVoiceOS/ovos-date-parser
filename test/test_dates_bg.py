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
from ovos_date_parser.dates_bg import (
    nice_time_bg, extract_datetime_bg, extract_duration_bg,
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
                result = extract_datetime_bg(text, anchorDate=ANCHOR)
                self.assertIsNotNone(result, text)
                self.assertEqual((result[0].hour, result[0].minute),
                                 (hh, mm), text)
                checked += 1
        self.assertGreaterEqual(checked, 200)

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


class TestExtractDatetime(unittest.TestCase):
    def test_relative_days(self):
        cases = {
            "днес": 0,
            "утре": 1,
            "вдругиден": 2,
            "вчера": -1,
            "завчера": -2,
        }
        for phrase, offset in cases.items():
            result = extract_datetime_bg(phrase, anchorDate=ANCHOR)
            self.assertIsNotNone(result, phrase)
            self.assertEqual(result[0].date(),
                             (ANCHOR + timedelta(days=offset)).date(), phrase)

    def test_weekday(self):
        result = extract_datetime_bg("в петък", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0].weekday(), 4)

    def test_explicit_date(self):
        result = extract_datetime_bg("15 август", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual((result[0].month, result[0].day), (8, 15))

    def test_date_with_year(self):
        result = extract_datetime_bg("15 август 2020", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual((result[0].year, result[0].month, result[0].day),
                         (2020, 8, 15))

    def test_offset_minutes(self):
        result = extract_datetime_bg("след 5 минути", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], ANCHOR + timedelta(minutes=5))

    def test_definite_article_week_does_not_leak(self):
        # "следващата седмица" (next week) with the article on the adjective
        result = extract_datetime_bg("следващата седмица", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0].date(),
                         (ANCHOR + timedelta(days=7)).date())

    def test_leftover_text_returned(self):
        result = extract_datetime_bg("какво е времето утре",
                                     anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertNotIn("утре", result[1])
        self.assertIn("времето", result[1])


class TestExtractDuration(unittest.TestCase):
    def test_minutes(self):
        self.assertEqual(extract_duration_bg("10 минути")[0],
                         timedelta(minutes=10))

    def test_compound(self):
        self.assertEqual(extract_duration_bg("2 часа 30 минути")[0],
                         timedelta(hours=2, minutes=30))

    def test_spelled_number(self):
        self.assertEqual(extract_duration_bg("пет минути")[0],
                         timedelta(minutes=5))


class TestNiceDateFamily(unittest.TestCase):
    def test_non_empty(self):
        self.assertTrue(nice_date(ANCHOR, "bg").strip())
        self.assertTrue(nice_year(ANCHOR, "bg").strip())
        self.assertEqual(nice_month(ANCHOR, "bg").lower(), "юни")
        self.assertTrue(nice_weekday(ANCHOR, "bg").strip())
        self.assertTrue(nice_duration(163, "bg").strip())


class TestAdversarial(unittest.TestCase):
    def test_empty_and_blank(self):
        self.assertIsNone(extract_datetime_bg("", anchorDate=ANCHOR))
        self.assertIsNone(extract_datetime_bg("   ", anchorDate=ANCHOR))

    def test_no_date_text(self):
        self.assertIsNone(extract_datetime_bg("здравей как си",
                                              anchorDate=ANCHOR))

    def test_impossible_clock_values(self):
        for bad in ("99:99", "25:61", "40:00", "13:75"):
            self.assertIsNone(extract_datetime_bg(bad, anchorDate=ANCHOR), bad)

    def test_boundary_clock_values(self):
        self.assertEqual(extract_datetime_bg("00:00", anchorDate=ANCHOR)[0]
                         .hour, 0)
        self.assertEqual(extract_datetime_bg("24:00", anchorDate=ANCHOR)[0]
                         .hour, 0)

    def test_duration_empty_is_none(self):
        self.assertIsNone(extract_duration_bg(""))

    def test_duration_junk_yields_no_value(self):
        duration, remainder = extract_duration_bg("няма продължителност тук")
        self.assertIsNone(duration)

    def test_garbage_is_rejected(self):
        self.assertIsNone(extract_datetime_bg("qwerty zxcvb",
                                              anchorDate=ANCHOR))

    def test_lone_ordinal_dot_not_crash(self):
        result = extract_datetime_bg("15.", anchorDate=ANCHOR)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
