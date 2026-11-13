"""The sl date resource spells the ordinal day names as the dictionaries do.

SSKJ2 and Slovenski pravopis 2001 give the ordinal of 15 as "petnajsti"
("petnájsti -a -o, vrstil. štev."). CLDR RBNF sl, %spellout-ordinal-masculine,
has "15: petnajsti;". ovos-number-parser spells the same ordinals, so it is
the second engine for the 31 day names."""
import json
import os
import unittest
from datetime import datetime

from ovos_number_parser import pronounce_ordinal

import ovos_date_parser
from ovos_date_parser import nice_date

RESOURCE = os.path.join(os.path.dirname(ovos_date_parser.__file__),
                        "res", "sl", "date_time.json")


class TestSlovenianResourceSpelling(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(RESOURCE, encoding="utf8") as f:
            cls.resource = json.load(f)

    def test_day_names(self):
        for day in range(1, 32):
            with self.subTest(day=day):
                self.assertEqual(self.resource["date"][str(day)],
                                 pronounce_ordinal(day, lang="sl"))

    def test_nice_date_fifteenth(self):
        self.assertEqual(nice_date(datetime(2024, 1, 15), "sl"),
                         "ponedeljek, petnajsti januar dva tisoč štiriindvajset")


if __name__ == "__main__":
    unittest.main()
