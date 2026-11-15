"""The it compounds of "tre" carry the accent: "ventitré", "trentatré".

Treccani, Enciclopedia dell'Italiano, "Numerali", section "Pronuncia e
grafia": "I composti di tre vanno accentati". CLDR RBNF it writes the unit
3 after a ten as "3: i­tré;". The bare numeral "tre" has no accent.
ovos-number-parser spells the same compounds, so it is the second engine for
the years 1 to 99."""
import unittest
from datetime import datetime

from ovos_number_parser import pronounce_number

from ovos_date_parser import nice_date, nice_year


class TestItalianTreAccent(unittest.TestCase):

    def test_years_below_one_hundred(self):
        wrong = [year for year in range(1, 100)
                 if nice_year(datetime(year, 1, 1), "it")
                 != pronounce_number(year, lang="it")]
        self.assertEqual(wrong, [])

    def test_compounds(self):
        for year, spoken in ((3, "tre"),
                             (23, "ventitré"),
                             (93, "novantatré"),
                             (1983, "mille novecento ottantatré"),
                             (2023, "duemila ventitré")):
            with self.subTest(year=year):
                self.assertEqual(nice_year(datetime(year, 1, 1), "it"), spoken)

    def test_day_twenty_three(self):
        self.assertEqual(
            nice_date(datetime(2024, 1, 23), "it", now=datetime(2024, 6, 1)),
            "martedì, ventitré gennaio")


if __name__ == "__main__":
    unittest.main()
