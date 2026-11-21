"""Natural-language tests for English calendar-scoped ordinals and seasons.

Expected values follow ranges.py conventions: periods are floor-division
buckets (the 21st century starts 2000), weeks resolve to their Monday,
ordinal -1 ("the last ...") selects the final unit in the scope, and
seasons are meteorological (northern summer starts June 1st), with the
southern tables offset half a year.
"""
import unittest
from datetime import datetime

from ovos_date_parser.ranges import DateTimeResolution
from ovos_date_parser.scoped_en import extract_scoped_date_en

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a Tuesday


class TestSeasons(unittest.TestCase):


    def test_resolution_tag(self):
        out = extract_scoped_date_en("summer of 1969", ANCHOR)
        self.assertEqual(out[2], DateTimeResolution.MONTH)


class TestPrecedenceAndFallthrough(unittest.TestCase):


    def test_no_match(self):
        for text in ("no scopes here", "", "hello world",
                     "the week", "century", "of june"):
            self.assertIsNone(extract_scoped_date_en(text, ANCHOR))

    def test_garbage_never_raises(self):
        for text in ("the 99th week of june", "the 0th day of march",
                     "the 999th day of the year", "week of of of"):
            try:
                extract_scoped_date_en(text, ANCHOR)
            except (ValueError, OverflowError):
                pass  # range validation errors are acceptable leads,
                # crashes on malformed grammar are not


if __name__ == "__main__":
    unittest.main()
