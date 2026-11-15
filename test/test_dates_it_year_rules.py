"""Every it year from 1 to 9999 is said in words.

The year rules read a year with no hundreds after the thousands as the
thousands and then the last two digits: 2015 is "duemila quindici". The rule
for that reading matched only 20xx, so 3001 to 9099 fell through to a rule
that also read the hundreds and printed them as a digit: 3001 was
"tremila 1 uno". ovos-number-parser spells the thousands, so it is the
second engine for the first word."""
import re
import unittest
from datetime import datetime

from ovos_number_parser import pronounce_number

from ovos_date_parser import nice_year


class TestItalianYearRules(unittest.TestCase):

    def test_no_year_has_digits(self):
        years = {year: nice_year(datetime(year, 1, 1), "it")
                 for year in range(1, 10000)}
        self.assertEqual(len(years), 9999)
        self.assertEqual([year for year, words in years.items()
                          if re.search(r"\d", words)], [])

    def test_thousands_then_the_last_two_digits(self):
        wrong = []
        for thousands in range(2, 10):
            for rest in range(1, 100):
                year = thousands * 1000 + rest
                expected = (pronounce_number(thousands * 1000, lang="it")
                            + " " + nice_year(datetime(rest, 1, 1), "it"))
                if nice_year(datetime(year, 1, 1), "it") != expected:
                    wrong.append(year)
        self.assertEqual(wrong, [])

    def test_years(self):
        for year, spoken in ((2015, "duemila quindici"),
                             (3001, "tremila uno"),
                             (5050, "cinquemila cinquanta"),
                             (9099, "novemila novantanove"),
                             (1999, "mille novecento novantanove"),
                             (3100, "tremila cento")):
            with self.subTest(year=year):
                self.assertEqual(nice_year(datetime(year, 1, 1), "it"), spoken)


if __name__ == "__main__":
    unittest.main()
