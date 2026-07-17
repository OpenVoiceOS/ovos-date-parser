"""Slovak (sk) date/time parsing.

Covers the public entry points, an exhaustive digit-time round-trip
sweep (pronounce a HH:MM, extract it, assert identity), and adversarial
inputs written to break the parser.
"""
import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (
    extract_datetime, extract_duration, nice_time, nice_date, nice_year,
    nice_month, nice_weekday, nice_duration,
)
from ovos_date_parser.dates_sk import (
    nice_time_sk, extract_datetime_sk, extract_duration_sk,
)

# wednesday 2017-06-28 13:04 is a fixed, timezone-naive anchor
ANCHOR = datetime(2017, 6, 28, 13, 4)
# minutes chosen to exercise <10 zero-padding, quarters and boundaries
_MINUTES = [0, 1, 5, 9, 15, 30, 45, 58, 59]


class TestRoundTrip(unittest.TestCase):
    def test_digit_time_identity(self):
        checked = 0
        for hh in range(24):
            for mm in _MINUTES:
                text = f"{hh}:{mm:02d}"
                result = extract_datetime_sk(text, anchorDate=ANCHOR)
                self.assertIsNotNone(result, text)
                self.assertEqual((result[0].hour, result[0].minute),
                                 (hh, mm), text)
                checked += 1
        self.assertGreaterEqual(checked, 200)

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


class TestExtractDatetime(unittest.TestCase):
    def test_relative_days(self):
        cases = {
            "dnes": 0,
            "zajtra": 1,
            "pozajtra": 2,
            "včera": -1,
            "predvčerom": -2,
        }
        for phrase, offset in cases.items():
            result = extract_datetime_sk(phrase, anchorDate=ANCHOR)
            self.assertIsNotNone(result, phrase)
            self.assertEqual(result[0].date(),
                             (ANCHOR + timedelta(days=offset)).date(), phrase)

    def test_weekday(self):
        # anchor is a wednesday; "v piatok" is two days later
        result = extract_datetime_sk("v piatok", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0].weekday(), 4)

    def test_weekday_accusative(self):
        result = extract_datetime_sk("v stredu", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0].weekday(), 2)

    def test_explicit_date(self):
        result = extract_datetime_sk("15. augusta", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual((result[0].month, result[0].day), (8, 15))

    def test_date_with_year(self):
        result = extract_datetime_sk("15. augusta 2020", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual((result[0].year, result[0].month, result[0].day),
                         (2020, 8, 15))

    def test_offset_minutes(self):
        result = extract_datetime_sk("o 5 minút", anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], ANCHOR + timedelta(minutes=5))

    def test_spoken_clock(self):
        cases = {
            "o ôsmej": (8, 0),
            "o pol deviatej": (8, 30),
            "o štvrť na deväť": (8, 15),
            "o trištvrte na deväť": (8, 45),
        }
        for phrase, (h, m) in cases.items():
            result = extract_datetime_sk(phrase, anchorDate=ANCHOR)
            self.assertIsNotNone(result, phrase)
            self.assertEqual((result[0].hour, result[0].minute), (h, m),
                             phrase)

    def test_leftover_text_returned(self):
        result = extract_datetime_sk("aké je počasie zajtra",
                                     anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertNotIn("zajtra", result[1])
        self.assertIn("počasie", result[1])


class TestExtractDuration(unittest.TestCase):
    def test_minutes(self):
        self.assertEqual(extract_duration_sk("10 minút")[0],
                         timedelta(minutes=10))

    def test_compound(self):
        self.assertEqual(extract_duration_sk("2 hodiny 30 minút")[0],
                         timedelta(hours=2, minutes=30))

    def test_spelled_number(self):
        self.assertEqual(extract_duration_sk("päť minút")[0],
                         timedelta(minutes=5))


class TestNiceDateFamily(unittest.TestCase):
    def test_non_empty(self):
        self.assertTrue(nice_date(ANCHOR, "sk").strip())
        self.assertTrue(nice_year(ANCHOR, "sk").strip())
        self.assertIn(nice_month(ANCHOR, "sk").lower(), ("jún",))
        self.assertTrue(nice_weekday(ANCHOR, "sk").strip())
        self.assertTrue(nice_duration(163, "sk").strip())


class TestAdversarial(unittest.TestCase):
    def test_empty_and_blank(self):
        self.assertIsNone(extract_datetime_sk("", anchorDate=ANCHOR))
        self.assertIsNone(extract_datetime_sk("   ", anchorDate=ANCHOR))

    def test_no_date_text(self):
        self.assertIsNone(extract_datetime_sk("ahoj ako sa máš",
                                              anchorDate=ANCHOR))

    def test_impossible_clock_values(self):
        for bad in ("99:99", "25:61", "40:00", "13:75"):
            self.assertIsNone(extract_datetime_sk(bad, anchorDate=ANCHOR), bad)

    def test_boundary_clock_values(self):
        # 24:00 folds to midnight, 00:00 stays midnight
        self.assertEqual(extract_datetime_sk("00:00", anchorDate=ANCHOR)[0]
                         .hour, 0)
        self.assertEqual(extract_datetime_sk("24:00", anchorDate=ANCHOR)[0]
                         .hour, 0)

    def test_duration_empty_is_none(self):
        self.assertIsNone(extract_duration_sk(""))

    def test_duration_junk_yields_no_value(self):
        duration, remainder = extract_duration_sk("žiadne trvanie tu")
        self.assertIsNone(duration)

    def test_garbage_is_rejected(self):
        self.assertIsNone(extract_datetime_sk("qwerty zxcvb",
                                              anchorDate=ANCHOR))

    def test_lone_ordinal_dot_not_crash(self):
        # a bare number with a trailing dot must not raise
        result = extract_datetime_sk("15.", anchorDate=ANCHOR)
        # no month -> not a date
        self.assertIsNone(result)


class TestNaturalSentences(unittest.TestCase):
    """Full sentences a user would actually speak.

    Every expected value is derived from Slovak usage, then checked
    against the parser; both the resolved datetime and the leftover text
    are asserted so number/date words are consumed but the surrounding
    request survives.
    """
    CASES = [
        ("nastav budík na zajtra o siedmej ráno",
         "2017-06-29 07:00", "nastav budík"),
        ("pripomeň mi stretnutie v piatok o pol tretej poobede",
         "2017-06-30 14:30", "pripomeň mi stretnutie"),
        ("zobuď ma o štvrť na osem",
         "2017-06-29 07:15", "zobuď ma"),
        ("mám schôdzku 15. augusta o 14:30",
         "2017-08-15 14:30", "mám schôdzku"),
        ("stretneme sa o tri hodiny",
         "2017-06-28 16:04", "stretneme sa"),
        ("pripomeň mi to o desať minút",
         "2017-06-28 13:14", "pripomeň mi to"),
        ("rezervácia je na 3. januára 2020",
         "2020-01-03 00:00", "rezervácia je"),
        ("budúcu stredu o dvanástej",
         "2017-07-05 12:00", ""),
        ("o dvadsaťpäť minút",
         "2017-06-28 13:29", ""),
        ("budík na 6:45 ráno",
         "2017-06-29 06:45", "budík"),
    ]

    def test_sentences(self):
        for text, expected_dt, expected_rem in self.CASES:
            result = extract_datetime_sk(text, anchorDate=ANCHOR)
            self.assertIsNotNone(result, text)
            self.assertEqual(result[0].strftime("%Y-%m-%d %H:%M"),
                             expected_dt, text)
            self.assertEqual(result[1], expected_rem, text)


class TestSpelledOffsets(unittest.TestCase):
    def test_spelled_in_minutes_hours_seconds(self):
        cases = {
            "o päť minút": timedelta(minutes=5),
            "o desať minút": timedelta(minutes=10),
            "cez tri hodiny": timedelta(hours=3),
            "za dvadsaťpäť minút": timedelta(minutes=25),
            "o štyridsaťpäť sekúnd": timedelta(seconds=45),
        }
        for phrase, delta in cases.items():
            result = extract_datetime_sk(phrase, anchorDate=ANCHOR)
            self.assertIsNotNone(result, phrase)
            self.assertEqual(result[0], ANCHOR + delta, phrase)


class TestDurationSentences(unittest.TestCase):
    def test_declined_numbers_in_context(self):
        self.assertEqual(
            extract_duration_sk("nastav časovač na dve hodiny "
                                 "a tridsať minút")[0],
            timedelta(hours=2, minutes=30))
        self.assertEqual(extract_duration_sk("počkaj päť minút")[0],
                         timedelta(minutes=5))
        self.assertEqual(extract_duration_sk("odpočítavaj devätnásť "
                                             "sekúnd")[0],
                         timedelta(seconds=19))


class TestBoundaryEdges(unittest.TestCase):
    def test_leap_day(self):
        result = extract_datetime_sk("29. februára 2020", anchorDate=ANCHOR)
        self.assertEqual(result[0].strftime("%Y-%m-%d"), "2020-02-29")

    def test_mixed_case(self):
        result = extract_datetime_sk("ZAJTRA O SIEDMEJ RÁNO",
                                     anchorDate=ANCHOR)
        self.assertEqual(result[0].strftime("%Y-%m-%d %H:%M"),
                         "2017-06-29 07:00")

    def test_none_input(self):
        self.assertIsNone(extract_datetime_sk(None, anchorDate=ANCHOR))

    def test_language_code_variant_dispatch(self):
        # regional code must still route through the Slovak parser
        result = extract_datetime("zajtra", "sk-SK", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(),
                         (ANCHOR + timedelta(days=1)).date())
        self.assertTrue(nice_time(ANCHOR, "sk-SK", use_24hour=True).strip())

    def test_wrap_around_clock(self):
        result = extract_datetime_sk("o 23:30", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (23, 30))

    def test_remainder_retained(self):
        result = extract_datetime_sk("koľko stojí lístok na zajtra",
                                     anchorDate=ANCHOR)
        self.assertNotIn("zajtra", result[1])
        self.assertIn("lístok", result[1])


class TestNumbersInContext(unittest.TestCase):
    def test_trailing_punctuation_and_digits(self):
        result = extract_datetime_sk("stretnutie 15. augusta?",
                                     anchorDate=ANCHOR)
        self.assertEqual((result[0].month, result[0].day), (8, 15))

    def test_digit_time_inside_sentence(self):
        result = extract_datetime_sk("vlak odchádza o 9:05",
                                     anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (9, 5))


class TestCrossLanguageContamination(unittest.TestCase):
    """Croatian/Bulgarian date phrases must not parse as Slovak dates."""
    FOREIGN = [
        "sutra", "sljedeću srijedu", "u sedam ujutro", "15. kolovoza",
        "za deset minuta", "vidimo se za tri sata",
        "утре", "следващата сряда", "в седем сутринта", "15 август",
        "след десет минути", "след три часа",
    ]

    def test_foreign_phrases_do_not_match(self):
        for phrase in self.FOREIGN:
            self.assertIsNone(extract_datetime_sk(phrase, anchorDate=ANCHOR),
                              phrase)


if __name__ == "__main__":
    unittest.main()
