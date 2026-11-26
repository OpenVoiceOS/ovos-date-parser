"""The uk date resource spells its cardinal numbers in Ukrainian.

СУМ-11 has the headword "ШІСТНА́ДЦЯТЬ" ("Назва числа 16"). CLDR RBNF uk,
%spellout-cardinal-masculine, has "16: шістнадцять;" and "500: пʼятсот",
"600: шістсот", "900: девʼятсот", with no soft sign before "сот".
ovos-number-parser spells the same cardinals, so it is the second engine
for every entry of the number table and for every year nice_year reads."""
import json
import os
import unittest
from datetime import datetime

from ovos_number_parser import pronounce_number

import ovos_date_parser
from ovos_date_parser import nice_date, nice_year

RESOURCE = os.path.join(os.path.dirname(ovos_date_parser.__file__),
                        "res", "uk", "date_time.json")


class TestUkrainianResourceSpelling(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(RESOURCE, encoding="utf8") as f:
            cls.resource = json.load(f)

    def test_number_table(self):
        for number, word in self.resource["number"].items():
            with self.subTest(number=number):
                self.assertEqual(word, pronounce_number(int(number), lang="uk"))

    def test_nice_year_2016(self):
        self.assertEqual(nice_year(datetime(2016, 1, 1), "uk"),
                         "дві тисячі шістнадцять")

    def test_nice_year_every_year(self):
        wrong = [year for year in range(1, 10000)
                 if nice_year(datetime(year, 1, 1), "uk")
                 != pronounce_number(year, lang="uk")]
        self.assertEqual(wrong, [])

    def test_nice_year_hundreds(self):
        for year, spoken in ((500, "п'ятсот"),
                             (1600, "тисяча шістсот"),
                             (3950, "три тисячі дев'ятсот п'ятдесят")):
            with self.subTest(year=year):
                self.assertEqual(nice_year(datetime(year, 1, 1), "uk"), spoken)

    def test_nice_date_1916(self):
        self.assertEqual(nice_date(datetime(1916, 3, 16), "uk"),
                         "четвер, шістнадцяте березня, тисяча дев'ятсот шістнадцять")


if __name__ == "__main__":
    unittest.main()
