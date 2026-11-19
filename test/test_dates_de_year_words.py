"""German years are written as one word.

The Amtliches Regelwerk der deutschen Rechtschreibung (2024), § 36 (1.6),
writes "mehrteilige Kardinalzahlen unter einer Million" together and gives
"siebenhundert" and "neunzehnhundertneunundachtzig" as examples. Years from
1100 to 1999 read as hundreds ("neunzehnhundert..."); from 2000 on they read
as the cardinal, so ovos-number-parser is the second engine for that range.
"""
import unittest
from datetime import datetime

from ovos_number_parser import pronounce_number

from ovos_date_parser import nice_date, nice_year


def year(y, **kwargs):
    return nice_year(datetime(y, 1, 1), "de", **kwargs)


class TestGermanYearWords(unittest.TestCase):

    def test_regelwerk_example(self):
        self.assertEqual(year(1989), "neunzehnhundertneunundachtzig")

    def test_hundreds_reading(self):
        for y, spoken in {
            1066: "tausendsechsundsechzig",
            1100: "elfhundert",
            1101: "elfhunderteins",
            1110: "elfhundertzehn",
            1995: "neunzehnhundertfünfundneunzig",
        }.items():
            with self.subTest(year=y):
                self.assertEqual(year(y), spoken)

    def test_cardinal_reading(self):
        for y, spoken in {
            2001: "zweitausendeins",
            2010: "zweitausendzehn",
            2024: "zweitausendvierundzwanzig",
            2101: "zweitausendeinhunderteins",
        }.items():
            with self.subTest(year=y):
                self.assertEqual(year(y), spoken)

    def test_cardinal_years_match_number_parser(self):
        for y in range(2000, 10000):
            with self.subTest(year=y):
                self.assertEqual(year(y), pronounce_number(y, "de"))

    def test_before_christ(self):
        self.assertEqual(year(300, bc=True), "dreihundert v.d.Z.")

    def test_nice_date(self):
        self.assertEqual(nice_date(datetime(2024, 3, 12), "de",
                                   include_weekday=False),
                         "zwölfter März, zweitausendvierundzwanzig")


if __name__ == "__main__":
    unittest.main()
