import unittest
from datetime import datetime

from ovos_date_parser.dates_ro import extract_datetime_ro


class TestExtractDatetimeRO(unittest.TestCase):
    """Romanian datetime extraction must survive numeric tokens carrying a
    letter suffix (e.g. "20h") without raising on int() of the raw token."""

    anchor = datetime(2117, 9, 3, 13, 30, 0)

    def _extract(self, text):
        return extract_datetime_ro(text, anchorDate=self.anchor)

    def test_glued_hour_suffix(self):
        # "20h" is a single token whose int() would fail on the trailing "h"
        result = self._extract("20h")
        self.assertIsNotNone(result)
        self.assertEqual(result[0].hour, 20)
        self.assertEqual(result[0].minute, 0)

    def test_la_glued_hour_suffix(self):
        result = self._extract("la 20h")
        self.assertIsNotNone(result)
        self.assertEqual(result[0].hour, 20)
        self.assertEqual(result[0].minute, 0)

    def test_glued_hour_minute_suffix(self):
        # "21h30" collapses to 21:30 without crashing
        result = self._extract("21h30")
        self.assertIsNotNone(result)
        self.assertEqual(result[0].hour, 21)
        self.assertEqual(result[0].minute, 30)

    def test_ora_glued_hour_suffix(self):
        result = self._extract("la ora 20h")
        self.assertIsNotNone(result)
        self.assertEqual(result[0].hour, 20)

    def test_gibberish_with_suffix_does_not_crash(self):
        # a non-time token containing digits+letters must not raise
        result = self._extract("fkjdslf20h ceva")
        # no meaningful time to extract, but the call must return, not raise
        self.assertIsNone(result)

    def test_impossible_hour_token_does_not_crash(self):
        # 99h is not a valid clock hour; extractor must reject it gracefully
        result = self._extract("la 99h")
        self.assertIsNone(result)

    def test_empty_and_pure_letter_tokens_do_not_crash(self):
        for text in ["", "h", "ora", "la ora"]:
            self.assertIsNone(self._extract(text))

    def test_impossible_dates_return_none(self):
        for text in ["30 februarie", "31 aprilie", "29 februarie",
                     "31 aprilie 2020"]:
            with self.subTest(text=text):
                self.assertIsNone(self._extract(text))

    def test_leap_day_in_leap_year_parses(self):
        result = self._extract("29 februarie 2020")
        self.assertEqual(result[0], datetime(2020, 2, 29, 0, 0))


if __name__ == "__main__":
    unittest.main()
