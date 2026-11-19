"""Natural-language tests for English era/epoch extraction.

Every expected value is derived from the cited epoch definitions (see
ovos_date_parser/eras.py and papers/calendars/): X BC = astronomical
1 - X (ISO 8601 expanded numbering), Before Present counts from AD 1950
(Stuiver & Polach 1977), Julian day 0 begins 24 November 4714 BC
proleptic Gregorian (USNO), the Unix Epoch is 1970-01-01T00:00:00Z
(POSIX.1-2017), HE = CE + 10000, AM 1 = 3761 BC, BE(Thai) = CE + 543.
"""
import unittest
from datetime import datetime

from ovos_date_parser.eras_en import extract_era_date_en

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a Tuesday


class TestADPhrases(unittest.TestCase):


    def test_ad_never_matches_the_word_ads(self):
        # "ads" must not be read as "500 AD s"
        self.assertIsNone(extract_era_date_en("i watched 500 ads"))


class TestDeepFutureYears(unittest.TestCase):

    def test_representable_years_fall_through(self):
        # "the year 1996" belongs to the ordinary scanner, not the era
        # layer -- the era pre-pass must not claim it
        self.assertIsNone(extract_era_date_en("the year 1996"))
        self.assertIsNone(extract_era_date_en("in the year 2525"))


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


    def test_garbage_never_raises(self):
        for text in ("bc", "ad", "bp", "the year", "century bc",
                     "0 bc bc bc", "999999999999999999 bc",
                     "julian day", "unix time"):
            extract_era_date_en(text)  # must not raise


if __name__ == "__main__":
    unittest.main()
