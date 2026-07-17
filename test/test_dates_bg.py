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

    def test_spoken_clock(self):
        cases = {
            "в осем": (8, 0),
            "осем и половина": (8, 30),
            "осем и четвърт": (8, 15),
            "девет без четвърт": (8, 45),
        }
        for phrase, (h, m) in cases.items():
            result = extract_datetime_bg(phrase, anchorDate=ANCHOR)
            self.assertIsNotNone(result, phrase)
            self.assertEqual((result[0].hour, result[0].minute), (h, m),
                             phrase)

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


class TestNaturalSentences(unittest.TestCase):
    """Full sentences a user would actually speak.

    Every expected value is derived from Bulgarian usage, then checked
    against the parser; both the resolved datetime and the leftover text
    are asserted.
    """
    CASES = [
        ("събуди ме утре в седем сутринта",
         "2017-06-29 07:00", "събуди ме"),
        ("напомни ми за срещата в петък в осем и половина вечерта",
         "2017-06-30 20:30", "напомни ми за срещата"),
        ("ще се видим след три часа",
         "2017-06-28 16:04", "ще се видим"),
        ("имам среща на 15 август в 14:30",
         "2017-08-15 14:30", "имам среща"),
        ("след десет минути",
         "2017-06-28 13:14", ""),
        ("следващата сряда по обед",
         "2017-07-05 12:00", ""),
        ("в осем и четвърт вечерта",
         "2017-06-28 20:15", ""),
        ("будилник в 6:45",
         "2017-06-29 06:45", "будилник"),
    ]

    def test_sentences(self):
        for text, expected_dt, expected_rem in self.CASES:
            result = extract_datetime_bg(text, anchorDate=ANCHOR)
            self.assertIsNotNone(result, text)
            self.assertEqual(result[0].strftime("%Y-%m-%d %H:%M"),
                             expected_dt, text)
            self.assertEqual(result[1], expected_rem, text)


class TestSpelledOffsets(unittest.TestCase):
    def test_spelled_in_minutes_hours_seconds(self):
        cases = {
            "след пет минути": timedelta(minutes=5),
            "след десет минути": timedelta(minutes=10),
            "след три часа": timedelta(hours=3),
            "след двадесет минути": timedelta(minutes=20),
            "след тридесет секунди": timedelta(seconds=30),
        }
        for phrase, delta in cases.items():
            result = extract_datetime_bg(phrase, anchorDate=ANCHOR)
            self.assertIsNotNone(result, phrase)
            self.assertEqual(result[0], ANCHOR + delta, phrase)


class TestDurationSentences(unittest.TestCase):
    def test_declined_numbers_in_context(self):
        self.assertEqual(
            extract_duration_bg("сложи таймер за два часа "
                                "и тридесет минути")[0],
            timedelta(hours=2, minutes=30))
        self.assertEqual(extract_duration_bg("изчакай пет минути")[0],
                         timedelta(minutes=5))
        self.assertEqual(extract_duration_bg("брой деветнадесет "
                                             "секунди")[0],
                         timedelta(seconds=19))


class TestBoundaryEdges(unittest.TestCase):
    def test_leap_day(self):
        result = extract_datetime_bg("29 февруари 2020", anchorDate=ANCHOR)
        self.assertEqual(result[0].strftime("%Y-%m-%d"), "2020-02-29")

    def test_mixed_case(self):
        result = extract_datetime_bg("УТРЕ В СЕДЕМ СУТРИНТА",
                                     anchorDate=ANCHOR)
        self.assertEqual(result[0].strftime("%Y-%m-%d %H:%M"),
                         "2017-06-29 07:00")

    def test_none_input(self):
        self.assertIsNone(extract_datetime_bg(None, anchorDate=ANCHOR))

    def test_language_code_variant_dispatch(self):
        result = extract_datetime("утре", "bg-BG", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(),
                         (ANCHOR + timedelta(days=1)).date())
        self.assertTrue(nice_time(ANCHOR, "bg-BG", use_24hour=True).strip())

    def test_wrap_around_clock(self):
        result = extract_datetime_bg("в 23:30", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (23, 30))

    def test_remainder_retained(self):
        result = extract_datetime_bg("колко струва билет за утре",
                                     anchorDate=ANCHOR)
        self.assertNotIn("утре", result[1])
        self.assertIn("билет", result[1])


class TestNumbersInContext(unittest.TestCase):
    def test_trailing_punctuation_and_digits(self):
        result = extract_datetime_bg("среща на 15 август?",
                                     anchorDate=ANCHOR)
        self.assertEqual((result[0].month, result[0].day), (8, 15))

    def test_digit_time_inside_sentence(self):
        result = extract_datetime_bg("влакът тръгва в 9:05",
                                     anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (9, 5))


class TestCrossLanguageContamination(unittest.TestCase):
    """Slovak/Croatian date phrases must not parse as Bulgarian dates."""
    FOREIGN = [
        "zajtra", "budúcu stredu", "o siedmej ráno", "15. augusta",
        "o desať minút", "stretneme sa o tri hodiny",
        "sutra", "sljedeću srijedu", "u sedam ujutro", "15. kolovoza",
        "za deset minuta", "vidimo se za tri sata",
    ]

    def test_foreign_phrases_do_not_match(self):
        for phrase in self.FOREIGN:
            self.assertIsNone(extract_datetime_bg(phrase, anchorDate=ANCHOR),
                              phrase)


if __name__ == "__main__":
    unittest.main()
