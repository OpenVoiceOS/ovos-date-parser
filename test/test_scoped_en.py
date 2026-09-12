"""Natural-language tests for English calendar-scoped ordinals and seasons.

Expected values follow ranges.py conventions: periods are floor-division
buckets (the 21st century starts 2000), weeks resolve to their Monday,
ordinal -1 ("the last ...") selects the final unit in the scope, and
seasons are meteorological (northern summer starts June 1st), with the
southern tables offset half a year.
"""
import unittest
from datetime import date, datetime

from ovos_date_parser import extract_date_en
from ovos_date_parser.ranges import DateTimeResolution, Hemisphere
from ovos_date_parser.scoped_en import extract_scoped_date_en

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a Tuesday


def d(text, hemisphere=None):
    out = extract_date_en(text, ANCHOR, hemisphere=hemisphere)
    return out and out[0]


def remainder(text):
    out = extract_date_en(text, ANCHOR)
    return out and out[1]


class TestAbsolutePeriods(unittest.TestCase):
    def test_centuries(self):
        self.assertEqual(d("the 21st century"), date(2000, 1, 1))
        self.assertEqual(d("the 1st century"), date(1, 1, 1))
        self.assertEqual(d("the 5th century"), date(400, 1, 1))
        self.assertEqual(d("the twentieth century"), date(1900, 1, 1))

    def test_millennia_and_decades(self):
        self.assertEqual(d("the 3rd millennium"), date(2000, 1, 1))
        self.assertEqual(d("the 1st millennium"), date(1, 1, 1))
        self.assertEqual(d("the 200th decade"), date(1990, 1, 1))

    def test_in_sentences(self):
        self.assertEqual(d("what happened in the 19th century"),
                         date(1800, 1, 1))
        self.assertEqual(remainder("what happened in the 19th century"),
                         "what happened in")


class TestScopedIntoMonth(unittest.TestCase):
    def test_weeks_of_month(self):
        # weeks resolve to their Monday
        self.assertEqual(d("the 3rd week of june"), date(2017, 6, 19))
        self.assertEqual(d("the first week of january"), date(2017, 1, 2))
        self.assertEqual(d("the 2nd week of december"), date(2017, 12, 11))

    def test_days_of_month(self):
        self.assertEqual(d("the 15th day of march"), date(2017, 3, 15))
        self.assertEqual(d("the last day of february 2024"),
                         date(2024, 2, 29))
        self.assertEqual(d("the last day of february 2023"),
                         date(2023, 2, 28))

    def test_with_year(self):
        self.assertEqual(d("the 3rd week of june 1969"), date(1969, 6, 16))

    def test_remainder(self):
        self.assertEqual(remainder("meet me in the 2nd week of december"),
                         "meet me in")


class TestScopedIntoYear(unittest.TestCase):
    def test_day_of_year(self):
        self.assertEqual(d("the 100th day of the year"), date(2017, 4, 10))
        self.assertEqual(d("the 1st day of the year"), date(2017, 1, 1))
        self.assertEqual(d("the 60th day of the year 2024"),
                         date(2024, 2, 29))  # leap year day 60

    def test_week_and_month_of_year(self):
        self.assertEqual(d("the 5th month of the year"), date(2017, 5, 1))
        self.assertEqual(d("the last month of the year"), date(2017, 12, 1))
        wk = d("the 10th week of the year")
        self.assertEqual(wk.weekday(), 0)


class TestNestedScopes(unittest.TestCase):
    def test_decade_of_century(self):
        self.assertEqual(d("the first decade of the 21st century"),
                         date(2000, 1, 1))
        self.assertEqual(d("the last decade of the 20th century"),
                         date(1990, 1, 1))
        self.assertEqual(d("the 5th decade of the 20th century"),
                         date(1940, 1, 1))

    def test_year_of_century(self):
        self.assertEqual(d("the 69th year of the 20th century"),
                         date(1968, 1, 1))

    def test_century_of_millennium(self):
        self.assertEqual(d("the 5th century of the 2nd millennium"),
                         date(1400, 1, 1))


class TestSeasons(unittest.TestCase):
    def test_season_of_year(self):
        self.assertEqual(d("summer of 1969"), date(1969, 6, 1))
        self.assertEqual(d("winter of 1963"), date(1963, 12, 1))
        self.assertEqual(d("the spring of 1945"), date(1945, 3, 1))

    def test_relative_seasons(self):
        # anchor 2017-06-27: next winter is Dec 2017, last spring Mar 2017
        self.assertEqual(d("next winter"), date(2017, 12, 1))
        self.assertEqual(d("last spring"), date(2017, 3, 1))
        self.assertEqual(d("this autumn"), date(2017, 9, 1))
        self.assertEqual(d("this fall"), date(2017, 9, 1))

    def test_southern_hemisphere(self):
        # southern summer starts December 1st
        self.assertEqual(d("summer of 1969", hemisphere=Hemisphere.SOUTH),
                         date(1969, 12, 1))
        self.assertEqual(d("winter of 1969", hemisphere=Hemisphere.SOUTH),
                         date(1969, 6, 1))

    def test_resolution_tag(self):
        out = extract_scoped_date_en("summer of 1969", ANCHOR)
        self.assertEqual(out[2], DateTimeResolution.MONTH)


class TestPrecedenceAndFallthrough(unittest.TestCase):
    def test_era_wins_over_scoped(self):
        # "the 3rd century BC" must resolve on the BC axis, not as the
        # AD-axis "3rd century"
        self.assertEqual(d("the 3rd century bc").year, -299)

    def test_legacy_scanner_untouched(self):
        self.assertEqual(d("tomorrow"), date(2017, 6, 28))
        self.assertEqual(d("next friday"), date(2017, 6, 30))
        self.assertEqual(d("march 5th"), date(2018, 3, 5))

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
