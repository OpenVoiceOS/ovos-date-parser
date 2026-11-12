"""The fa year is a Persian cardinal joined with "و".

CLDR RBNF fa reads a year with %spellout-numbering-year, the cardinal:
"20: بیست[ و >>];", "100: صد[ و >>];", "1000: << هزار[ و >>];". CLDR fa
names the era before year 1 "قبل از میلاد"; the resource had "بعد از میلاد",
the era after it. ovos-number-parser spells the same cardinals, so it is
the second engine for every year. For 1000 to 1999 the two differ: the CLDR
rule "<< هزار" puts "یک" before "هزار", so CLDR gives 1345 as
"یک هزار و سیصد و چهل و پنج". The resource follows ovos-number-parser,
which gives "هزار و سیصد و چهل و پنج". The resource keeps the spoken teens پونزده, شونزده, هیفده and
هیجده where the number parser writes پانزده, شانزده, هفده and هجده."""
import json
import os
import unittest
from datetime import datetime

from ovos_number_parser import pronounce_number

import ovos_date_parser
from ovos_date_parser import nice_date, nice_date_time, nice_year

FIXTURE = os.path.join(os.path.dirname(ovos_date_parser.__file__),
                       "res", "fa", "date_time_test.json")
SPOKEN_TEENS = {"پانزده": "پونزده", "شانزده": "شونزده",
                "هفده": "هیفده", "هجده": "هیجده"}


def spoken_year(year):
    return " ".join(SPOKEN_TEENS.get(word, word)
                    for word in pronounce_number(year, lang="fa").split())


def _args(text):
    return datetime(*(int(part) for part in text.split(",")))


class TestPersianYearWords(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(FIXTURE, encoding="utf8") as f:
            cls.fixture = json.load(f)

    def test_every_year(self):
        wrong = [year for year in range(1, 10000)
                 if nice_year(datetime(year, 1, 1), "fa") != spoken_year(year)]
        self.assertEqual(wrong, [])

    def test_years(self):
        for year, spoken in ((45, "چهل و پنج"),
                             (1100, "هزار و صد"),
                             (1345, "هزار و سیصد و چهل و پنج"),
                             (2024, "دو هزار و بیست و چهار")):
            with self.subTest(year=year):
                self.assertEqual(nice_year(datetime(year, 1, 1), "fa"), spoken)

    def test_era(self):
        self.assertEqual(nice_year(datetime(44, 1, 1), "fa", bc=True),
                         "چهل و چهار قبل از میلاد")

    def test_fixture_nice_year(self):
        for key, case in self.fixture["test_nice_year"].items():
            with self.subTest(case=key):
                self.assertEqual(
                    nice_year(_args(case["datetime_param"]), "fa",
                              bc=case["bc"] == "True"),
                    case["assertEqual"])

    def test_fixture_nice_date(self):
        for key, case in self.fixture["test_nice_date"].items():
            now = None if case["now"] == "None" else _args(case["now"])
            with self.subTest(case=key):
                self.assertEqual(
                    nice_date(_args(case["datetime_param"]), "fa", now=now),
                    case["assertEqual"])

    def test_fixture_nice_date_time(self):
        for key, case in self.fixture["test_nice_date_time"].items():
            with self.subTest(case=key):
                self.assertEqual(
                    nice_date_time(_args(case["datetime_param"]), "fa",
                                   use_24hour=case["use_24hour"] == "True",
                                   use_ampm=case["use_ampm"] == "True"),
                    case["assertEqual"])


if __name__ == "__main__":
    unittest.main()
