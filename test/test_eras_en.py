"""Natural-language tests for English era/epoch extraction.

Every expected value is derived from the cited epoch definitions (see
ovos_date_parser/eras.py and papers/calendars/): X BC = astronomical
1 - X (ISO 8601 expanded numbering), Before Present counts from AD 1950
(Stuiver & Polach 1977), Julian day 0 begins 24 November 4714 BC
proleptic Gregorian (USNO), the Unix Epoch is 1970-01-01T00:00:00Z
(POSIX.1-2017), HE = CE + 10000, AM 1 = 3761 BC, BE(Thai) = CE + 543.
"""
import unittest
from datetime import date, datetime

from ovos_date_parser import AstroDate, DateTimeResolution, extract_date_en
from ovos_date_parser.eras_en import extract_era_date_en

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a Tuesday


def d(text):
    out = extract_date_en(text, ANCHOR)
    return out and out[0]


def remainder(text):
    out = extract_date_en(text, ANCHOR)
    return out and out[1]


class TestBCPhrases(unittest.TestCase):
    def test_plain_bc(self):
        self.assertEqual(d("44 BC"), AstroDate(-43))
        self.assertEqual(d("44 bc"), AstroDate(-43))
        self.assertEqual(d("44 B.C."), AstroDate(-43))
        self.assertEqual(d("44 BCE"), AstroDate(-43))
        self.assertEqual(d("1 BC"), AstroDate(0))
        self.assertEqual(d("3761 BCE"), AstroDate(-3760))

    def test_bc_in_sentences(self):
        self.assertEqual(d("caesar was assassinated in 44 BC"),
                         AstroDate(-43))
        self.assertEqual(remainder("caesar was assassinated in 44 BC"),
                         "caesar was assassinated in")
        self.assertEqual(d("rome was founded in 753 BC"), AstroDate(-752))
        self.assertEqual(d("the pyramids were built around 2560 BCE"),
                         AstroDate(-2559))
        self.assertEqual(d("what happened in the year 3000 BC"),
                         AstroDate(-2999))
        self.assertEqual(d("alexander died in 323 b.c. in babylon"),
                         AstroDate(-322))

    def test_spelled_out_numbers(self):
        self.assertEqual(d("forty four BC"), AstroDate(-43))
        self.assertEqual(d("two thousand BC"), AstroDate(-1999))
        self.assertEqual(d("five hundred BCE"), AstroDate(-499))

    def test_bc_value_is_bc(self):
        result = d("44 BC")
        self.assertTrue(result.is_bc)
        self.assertEqual(result.bc_year, 44)
        self.assertIsNone(result.date())


class TestADPhrases(unittest.TestCase):
    def test_suffix_and_prefix_ad(self):
        self.assertEqual(d("500 AD"), date(500, 1, 1))
        self.assertEqual(d("AD 500"), date(500, 1, 1))
        self.assertEqual(d("500 A.D."), date(500, 1, 1))
        self.assertEqual(d("500 CE"), date(500, 1, 1))
        self.assertEqual(d("anno domini 1066"), date(1066, 1, 1))
        self.assertEqual(d("79 AD"), date(79, 1, 1))

    def test_ad_in_sentences(self):
        self.assertEqual(d("pompeii was destroyed in 79 AD"),
                         date(79, 1, 1))
        self.assertEqual(remainder("pompeii was destroyed in 79 AD"),
                         "pompeii was destroyed in")
        self.assertEqual(d("the battle of hastings was in 1066 CE"),
                         date(1066, 1, 1))

    def test_in_range_returns_plain_date(self):
        self.assertNotIsInstance(d("500 AD"), AstroDate)

    def test_ad_never_matches_the_word_ads(self):
        # "ads" must not be read as "500 AD s"
        self.assertIsNone(extract_era_date_en("i watched 500 ads"))


class TestDeepFutureYears(unittest.TestCase):
    def test_in_the_year(self):
        self.assertEqual(d("in the year 12000"), AstroDate(12000))
        self.assertEqual(d("the year 10000"), AstroDate(10000))
        self.assertEqual(d("what will happen in the year 1000000"),
                         AstroDate(1000000))

    def test_representable_years_fall_through(self):
        # "the year 1996" belongs to the ordinary scanner, not the era
        # layer -- the era pre-pass must not claim it
        self.assertIsNone(extract_era_date_en("the year 1996"))
        self.assertIsNone(extract_era_date_en("in the year 2525"))

    def test_ordering(self):
        self.assertGreater(d("in the year 12000"), date(9999, 12, 31))
        self.assertLess(d("44 BC"), date(1, 1, 1))
        self.assertLess(d("3000 BC"), d("44 BC"))


class TestBeforePresent(unittest.TestCase):
    def test_years_before_present(self):
        self.assertEqual(d("100 years before present"), date(1850, 1, 1))
        self.assertEqual(d("2000 years before present"), AstroDate(-50))
        self.assertEqual(d("10000 years before present"), AstroDate(-8050))
        self.assertEqual(d("10000 BP"), AstroDate(-8050))
        self.assertEqual(d("14000 B.P."), AstroDate(-12050))

    def test_bp_in_sentences(self):
        self.assertEqual(
            d("the sample was dated to 12000 years before present"),
            AstroDate(-10050))
        self.assertEqual(
            remainder("the sample was dated to 12000 years before present"),
            "the sample was dated to")
        self.assertEqual(d("humans reached australia 50000 years "
                           "before the present"), AstroDate(-48050))

    def test_bc_bp_correspondence(self):
        # 2000 BP = AD -50 = 51 BC: both phrasings agree
        self.assertEqual(d("2000 years before present"), d("51 BC"))


class TestFixedEpochCounts(unittest.TestCase):
    def test_unix(self):
        self.assertEqual(d("unix time 0"), date(1970, 1, 1))
        self.assertEqual(d("unix timestamp 1000000000"), date(2001, 9, 9))
        self.assertEqual(d("epoch time 86400"), date(1970, 1, 2))

    def test_julian_day(self):
        self.assertEqual(d("julian day 2451545"), date(2000, 1, 1))
        self.assertEqual(d("julian day number 2440588"), date(1970, 1, 1))
        jd0 = d("julian day 0")
        self.assertEqual((jd0.year, jd0.month, jd0.day), (-4713, 11, 24))

    def test_holocene(self):
        self.assertEqual(d("holocene era 12025"), date(2025, 1, 1))
        self.assertEqual(d("human era 12017"), date(2017, 1, 1))
        self.assertEqual(d("12025 HE"), date(2025, 1, 1))
        self.assertEqual(d("holocene era 1"), AstroDate(-9999))

    def test_anno_mundi(self):
        self.assertEqual(d("anno mundi 5786"), date(2025, 9, 23))
        self.assertEqual(d("5786 anno mundi"), date(2025, 9, 23))
        self.assertEqual(d("anno mundi 1"), AstroDate(-3760, 9, 7))


class TestScopedOrdinalsBC(unittest.TestCase):
    def test_century_bc(self):
        # the Nth century BC starts at 100N BC = astronomical 1 - 100N
        self.assertEqual(d("the 1st century BC"),
                         AstroDate(-99, 1, 1))
        self.assertEqual(d("the 3rd century BC").year, -299)
        self.assertEqual(d("the 5th century BCE").year, -499)
        self.assertEqual(d("rome expanded in the 3rd century bc").year, -299)

    def test_millennium_bc(self):
        self.assertEqual(d("the 2nd millennium BCE").year, -1999)
        self.assertEqual(d("writing appeared in the 4th millennium BC").year,
                         -3999)
        # the legacy scanner returns a year-wide AstroDate value; referential
        # width (millennium) is surfaced via DateSpan at the engine level
        self.assertEqual(d("the 1st millennium bc").year, -999)

    def test_spelled_ordinals(self):
        self.assertEqual(d("the third century BC").year, -299)
        self.assertEqual(d("the second millennium BCE").year, -1999)


class TestAmbiguityGuards(unittest.TestCase):
    def test_pronoun_he_is_not_holocene(self):
        self.assertIsNone(extract_era_date_en("he said hello"))
        self.assertIsNone(extract_era_date_en("give him 5 he asked"))

    def test_meridiem_am_is_not_anno_mundi(self):
        self.assertIsNone(extract_era_date_en("wake me at 9 am"))
        self.assertIsNone(extract_era_date_en("the meeting is at 11 am"))

    def test_plain_dates_do_not_trigger(self):
        for text in ("tomorrow", "next friday", "march 5th", "in 3 days",
                     "june 2027", "no date here", ""):
            self.assertIsNone(extract_era_date_en(text))

    def test_legacy_scanner_still_works_through_extract_date(self):
        self.assertEqual(d("tomorrow"), date(2017, 6, 28))
        self.assertEqual(d("next friday"), date(2017, 6, 30))

    def test_garbage_never_raises(self):
        for text in ("bc", "ad", "bp", "the year", "century bc",
                     "0 bc bc bc", "999999999999999999 bc",
                     "julian day", "unix time"):
            extract_era_date_en(text)  # must not raise

    def test_zero_and_extreme_values(self):
        # "0 BC" is not a real year name but must resolve, not crash:
        # astronomical 1 - 0 = 1 = AD 1
        self.assertEqual(extract_era_date_en("0 bc")[0], date(1, 1, 1))
        self.assertEqual(d("999999999 BC"), AstroDate(-999999998))


if __name__ == "__main__":
    unittest.main()
