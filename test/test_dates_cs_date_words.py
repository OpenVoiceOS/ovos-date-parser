"""The cs date puts the day before the month, as Czech does.

CLDR cs gives the full date "EEEE d. MMMM y", the month in a date in the
genitive (monthContext "format": "ledna", "února", ...) and the era
abbreviation "př. n. l.". CLDR RBNF cs %spellout-ordinal-masculine-genitive
has "20: dvacátého[ >>];": the parts of an ordinal are apart, with no hyphen.
ovos-number-parser spells the same ordinals in the nominative, with a space."""
import json
import os
import unittest
from datetime import datetime

from ovos_number_parser import pronounce_ordinal

import ovos_date_parser
from ovos_date_parser import nice_date, nice_date_time, nice_month, nice_year

RESOURCE = os.path.join(os.path.dirname(ovos_date_parser.__file__),
                        "res", "cs", "date_time.json")


class TestCzechDateWords(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(RESOURCE, encoding="utf8") as f:
            cls.resource = json.load(f)

    def test_day_names_are_split_like_the_ordinals(self):
        for day in range(1, 32):
            with self.subTest(day=day):
                self.assertEqual(
                    len(self.resource["date"][str(day)].split()),
                    len(pronounce_ordinal(day, lang="cs").split()))

    def test_nice_date(self):
        self.assertEqual(
            nice_date(datetime(2024, 1, 21), "cs", now=datetime(2024, 6, 1)),
            "neděle, dvacátého prvního ledna")

    def test_nice_date_time(self):
        self.assertEqual(
            nice_date_time(datetime(2024, 3, 21, 13, 22), "cs",
                           now=datetime(2024, 6, 1), use_24hour=True),
            "čtvrtek, dvacátého prvního března v třináct dvacet dva")

    def test_era(self):
        self.assertEqual(nice_year(datetime(44, 1, 1), "cs", bc=True),
                         "čtyřicet čtyři př. n. l.")

    def test_month_stands_alone_in_the_nominative(self):
        self.assertEqual(nice_month(datetime(2024, 1, 21), "cs"), "Leden")


if __name__ == "__main__":
    unittest.main()
