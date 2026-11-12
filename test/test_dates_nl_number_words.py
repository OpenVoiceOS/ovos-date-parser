"""The nl year and date words follow the Dutch spelling rules.

Team Taaladvies, Aaneenschrijven 07 (Getallen, telwoorden en breuken),
Regel 1: "Schrijf getallen in woorden aaneen tot aan het woord duizend."
"Schrijf achter het woord duizend een spatie." "Schrijf een trema bij
klinkerbotsing in getallen zoals tweeëndertig en drieënhalf." Examples:
"32: tweeëndertig", "3254: drieduizend tweehonderdvierenvijftig".
CLDR nl gives the era abbreviation "v.Chr.". A year said by its century
(1988, 3241) splits the century from the rest, as CLDR RBNF nl
%spellout-numbering-year does with "1100/100: <<>%%2d-year>".
ovos-number-parser spells each part, so it is the second engine."""
import json
import os
import unittest
from datetime import datetime

from ovos_number_parser import pronounce_number

import ovos_date_parser
from ovos_date_parser import nice_date, nice_date_time, nice_year

FIXTURE = os.path.join(os.path.dirname(ovos_date_parser.__file__),
                       "res", "nl", "date_time_test.json")


def spoken_year(year):
    def words(number):
        return pronounce_number(number, lang="nl").replace("één", "een")

    if year < 1000:
        return words(year)
    if year % 1000 < 100:
        head = words(year - year % 100)
    else:
        head = words(year // 100) + ("honderd" if year % 100 == 0 else "")
    return head if year % 100 == 0 else f"{head} {words(year % 100)}"


def _args(text):
    return datetime(*(int(part) for part in text.split(",")))


class TestDutchNumberWords(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(FIXTURE, encoding="utf8") as f:
            cls.fixture = json.load(f)

    def test_every_year(self):
        wrong = [year for year in range(1, 10000)
                 if nice_year(datetime(year, 1, 1), "nl").replace("één", "een")
                 != spoken_year(year)]
        self.assertEqual(wrong, [])

    def test_compound_numbers(self):
        for year, spoken in ((15, "vijftien"),
                             (21, "eenentwintig"),
                             (22, "tweeëntwintig"),
                             (33, "drieëndertig"),
                             (88, "achtentachtig"),
                             (454, "vierhonderdvierenvijftig"),
                             (1988, "negentien achtentachtig"),
                             (2015, "tweeduizend vijftien")):
            with self.subTest(year=year):
                self.assertEqual(nice_year(datetime(year, 1, 1), "nl"), spoken)

    def test_era(self):
        self.assertEqual(nice_year(datetime(92, 1, 1), "nl", bc=True),
                         "tweeënnegentig v.Chr.")

    def test_fixture_nice_year(self):
        for key, case in self.fixture["test_nice_year"].items():
            with self.subTest(case=key):
                self.assertEqual(
                    nice_year(_args(case["datetime_param"]), "nl",
                              bc=case["bc"] == "True"),
                    case["assertEqual"])

    def test_fixture_nice_date(self):
        for key, case in self.fixture["test_nice_date"].items():
            now = None if case["now"] == "None" else _args(case["now"])
            with self.subTest(case=key):
                self.assertEqual(
                    nice_date(_args(case["datetime_param"]), "nl", now=now),
                    case["assertEqual"])

    def test_fixture_nice_date_time(self):
        for key, case in self.fixture["test_nice_date_time"].items():
            with self.subTest(case=key):
                self.assertEqual(
                    nice_date_time(_args(case["datetime_param"]), "nl",
                                   use_24hour=case["use_24hour"] == "True",
                                   use_ampm=case["use_ampm"] == "True"),
                    case["assertEqual"])


if __name__ == "__main__":
    unittest.main()
