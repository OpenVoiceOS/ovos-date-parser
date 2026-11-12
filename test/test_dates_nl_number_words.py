"""The nl year and date words follow the Dutch spelling rules.

Team Taaladvies, "Aaneenschrijven van telwoorden (algemeen)":
"Hoofdtelwoorden worden aaneengeschreven tot en met het woord duizend."
"Na het woord duizend (en samenstellingen hiermee, zoals vierduizend)
staat een spatie." Examples: "43 / drieënveertig", "101 / honderdeen of
honderdeneen", "6028 / zesduizend achtentwintig".

Team Taaladvies, "Jaartallen voluit": "Jaartallen volgen dezelfde regels
voor aaneenschrijven als gewone telwoorden." "Bij klinkerbotsing krijgen
getallen in letters, hoewel het samenstellingen zijn, een trema."
"Voorbeelden: tweeëndertig, drieënhalf, vijfhonderddrieëntwintigduizend."

Team Taaladvies, "Uitspraak 2020: twintig twintig / tweeduizend
twintig": "Vaak wordt het woorddeel honderd in de uitspraak weggelaten."
"1694 als 'zestien vierennegentig'". "Jaartallen in de eenentwintigste
eeuw worden door de meeste mensen met 'tweeduizend' uitgesproken."

CLDR nl gives the era abbreviation "v.Chr." and "1: een;" in
%spellout-numbering. ovos-number-parser spells each part of a year, so
it is the second engine. It writes the bare number 1 as "één", so the
expected words take the CLDR "een" for that one part."""
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
        return "een" if number == 1 else pronounce_number(number, lang="nl")

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
                 if nice_year(datetime(year, 1, 1), "nl") != spoken_year(year)]
        self.assertEqual(wrong, [])

    def test_compound_numbers(self):
        for year, spoken in ((15, "vijftien"),
                             (21, "eenentwintig"),
                             (22, "tweeëntwintig"),
                             (33, "drieëndertig"),
                             (88, "achtentachtig"),
                             (101, "honderdeen"),
                             (454, "vierhonderdvierenvijftig"),
                             (2001, "tweeduizend een"),
                             (1988, "negentien achtentachtig"),
                             (2015, "tweeduizend vijftien")):
            with self.subTest(year=year):
                self.assertEqual(nice_year(datetime(year, 1, 1), "nl"), spoken)

    def test_day_names(self):
        for day in range(1, 32):
            date = nice_date(datetime(2024, 1, day), "nl",
                             now=datetime(2024, 6, 1))
            with self.subTest(day=day):
                self.assertEqual(date.split(", ")[1],
                                 f"{pronounce_number(day, lang='nl')} januari")

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
