"""The eu date resource spells its month and day names as Euskaltzaindia does.

Araua 196 (EBO I, "Laburtzapenak"), in its abbreviation list, gives the
month names, September as "iraila" ("ira. -> iraila"). Araua 7
("Zenbakien idazkeraz") gives 28 as "hogeita zortzi"; ovos-number-parser
follows that table, so it is the second engine for the 31 day names."""
import json
import os
import unittest
from datetime import datetime

from ovos_number_parser.numbers_eu import pronounce_number_eu

import ovos_date_parser
from ovos_date_parser import nice_date

RESOURCE = os.path.join(os.path.dirname(ovos_date_parser.__file__),
                        "res", "eu", "date_time.json")
ARAUA_196_MONTHS = ["urtarrila", "otsaila", "martxoa", "apirila", "maiatza",
                    "ekaina", "uztaila", "abuztua", "iraila", "urria",
                    "azaroa", "abendua"]


class TestBasqueResourceSpelling(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(RESOURCE, encoding="utf8") as f:
            cls.resource = json.load(f)

    def test_month_names(self):
        self.assertEqual([self.resource["month"][str(m)] for m in range(1, 13)],
                         ARAUA_196_MONTHS)

    def test_day_names(self):
        for day in range(1, 32):
            with self.subTest(day=day):
                self.assertEqual(self.resource["date"][str(day)],
                                 pronounce_number_eu(day))

    def test_nice_date_september(self):
        spoken = nice_date(datetime(2024, 9, 28), "eu", include_weekday=False)
        self.assertIn("irailaren hogeita zortzi", spoken)


if __name__ == "__main__":
    unittest.main()
