"""The pl date, year and date-time words are Polish.

A year said alone is a nominative ordinal: CLDR RBNF pl
%spellout-ordinal-masculine reads "1: pierwszy; 2: drugi;", and
ovos-number-parser gives "dwa tysiące dwudziesty czwarty" for 2024. Inside
a date the year takes the genitive: CLDR reads a year with
%spellout-numbering-year, which is "0: =%spellout-ordinal-masculine-genitive=;",
so 1905 in a date is "tysiąc dziewięćset piątego". Słownik języka polskiego
PWN spells the tens "pięćdziesiąty", "sześćdziesiąty" and
"dziewięćdziesiąty"; CLDR builds those three from the teen stems
("piętdziesiątego"), and the dictionary wins.

CLDR pl gives the full date "EEEE, d MMMM y", the month in a date in the
genitive (monthContext "format": "stycznia", "lutego", ...) and the era
"p.n.e.". The CLDR pl date-time pattern is "{1} {0}" for the full and long
styles and "{1}, {0}" for the medium and short styles; the spoken date-time
takes the comma of the medium style as a pause before the time.

ovos-number-parser spells the nominative ordinals, and the genitive of each
ordinal word ends in -ego, so it is the second engine for every year."""
import json
import os
import unittest
from datetime import datetime

from ovos_number_parser import pronounce_ordinal

import ovos_date_parser
from ovos_date_parser import nice_date, nice_date_time, nice_month, nice_year

RESOURCE = os.path.join(os.path.dirname(ovos_date_parser.__file__),
                        "res", "pl", "date_time.json")
CARDINAL_WORDS = {"trzy", "cztery", "tysięcy"}


def genitive_year(year):
    def genitive(word):
        if word in CARDINAL_WORDS:
            return word
        if word.endswith("y"):
            return word[:-1] + "ego"
        if word.endswith("i"):
            return word + "ego"
        return word

    return " ".join(genitive(word)
                    for word in pronounce_ordinal(year, lang="pl").split())


class TestPolishDateWords(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(RESOURCE, encoding="utf8") as f:
            cls.resource = json.load(f)

    def test_day_names(self):
        for day in range(1, 32):
            with self.subTest(day=day):
                self.assertEqual(self.resource["date"][str(day)],
                                 pronounce_ordinal(day, lang="pl"))

    def test_every_year(self):
        wrong = [year for year in range(1, 10000)
                 if nice_year(datetime(year, 1, 1), "pl")
                 != pronounce_ordinal(year, lang="pl")]
        self.assertEqual(wrong, [])

    def test_every_year_in_a_date(self):
        wrong = [year for year in range(1, 10000)
                 if not nice_date(datetime(year, 1, 1), "pl").endswith(
                     " stycznia " + genitive_year(year))]
        self.assertEqual(wrong, [])

    def test_years(self):
        for year, spoken in ((105, "sto piąty"),
                             (1100, "tysiąc setny"),
                             (1905, "tysiąc dziewięćset piąty"),
                             (1950, "tysiąc dziewięćset pięćdziesiąty"),
                             (2000, "dwutysięczny"),
                             (2024, "dwa tysiące dwudziesty czwarty")):
            with self.subTest(year=year):
                self.assertEqual(nice_year(datetime(year, 1, 1), "pl"), spoken)

    def test_years_in_a_date(self):
        for year, spoken in ((105, "sto piątego"),
                             (1100, "tysiąc setnego"),
                             (1905, "tysiąc dziewięćset piątego"),
                             (1950, "tysiąc dziewięćset pięćdziesiątego"),
                             (2000, "dwutysięcznego"),
                             (2024, "dwa tysiące dwudziestego czwartego")):
            with self.subTest(year=year):
                self.assertTrue(nice_date(datetime(year, 3, 1), "pl")
                                .endswith(" marca " + spoken))

    def test_era(self):
        self.assertEqual(nice_year(datetime(44, 1, 1), "pl", bc=True),
                         "czterdziesty czwarty p.n.e.")

    def test_nice_date(self):
        self.assertEqual(nice_date(datetime(2024, 1, 11), "pl"),
                         "czwartek, jedenasty stycznia dwa tysiące "
                         "dwudziestego czwartego")

    def test_nice_date_time(self):
        self.assertEqual(nice_date_time(datetime(2024, 1, 1, 9, 5), "pl"),
                         "poniedziałek, pierwszy stycznia dwa tysiące "
                         "dwudziestego czwartego, dziewiąta pięć")

    def test_month_stands_alone_in_the_nominative(self):
        self.assertEqual(nice_month(datetime(2024, 1, 11), "pl"), "Styczeń")


if __name__ == "__main__":
    unittest.main()
