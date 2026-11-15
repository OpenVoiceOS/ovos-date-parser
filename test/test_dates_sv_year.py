"""Swedish reads a year in hundreds from 1100 to 9999, as one word.

CLDR RBNF sv: "%spellout-numbering-year: 0: =%spellout-numbering=;
1100/100: <<hundra[>>]; 10000: =%spellout-numbering=;".
Språkrådet (frageladan.isof.se/faqs/27138): "Övriga tal skrivs ihop:
tjugofem, femtusentrettio."
CLDR sv eraNames: "0": "före Kristus".

GOLD is ICU 78 RuleBasedNumberFormat("sv").format(year,
"%spellout-numbering-year") with the soft hyphens and the space after
"tusen" removed, so the oracle is a second engine and not this package.
"""
import datetime
import unittest

from ovos_date_parser import nice_date, nice_date_time, nice_year

GOLD = {
    1: "ett",
    21: "tjugoett",
    100: "etthundra",
    803: "åttahundratre",
    1000: "ettusen",
    1012: "ettusentolv",
    1099: "ettusennittionio",
    1100: "elvahundra",
    1807: "artonhundrasju",
    1988: "nittonhundraåttioåtta",
    2000: "tjugohundra",
    2009: "tjugohundranio",
    2018: "tjugohundraarton",
    2100: "tjugoetthundra",
    9999: "nittioniohundranittionio",
}


class TestSwedishYear(unittest.TestCase):
    def test_gold_years(self):
        for year, words in GOLD.items():
            with self.subTest(year=year):
                self.assertEqual(nice_year(datetime.datetime(year, 1, 1), "sv"), words)

    def test_a_year_is_one_word(self):
        for year in range(1, 10000):
            self.assertNotIn(" ", nice_year(datetime.datetime(year, 1, 1), "sv-SE"))

    def test_bc(self):
        self.assertEqual(nice_year(datetime.datetime(92, 1, 1), "sv", bc=True),
                         "nittiotvå före Kristus")

    def test_date_carries_the_same_year(self):
        dt = datetime.datetime(2018, 2, 4, 13, 22, 3)
        self.assertEqual(nice_date(dt, "sv"),
                         "söndag, den fjärde februari, tjugohundraarton")
        self.assertEqual(nice_date_time(dt, "sv", use_24hour=True),
                         "söndag, den fjärde februari, tjugohundraarton "
                         "klockan tretton tjugotvå")


if __name__ == "__main__":
    unittest.main()
