"""nice_date for Portuguese writes month and weekday names in lowercase.

The Acordo Ortográfico de 1990, Base XIX 1.º b), uses the lowercase initial
"Nos nomes dos dias, meses, estações do ano: segunda-feira; outubro;
primavera". Both pt-PT and pt-BR follow the agreement."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date, nice_date_time

TUESDAY = datetime(2024, 3, 12, 14, 30)


class TestPortugueseLowercaseNames(unittest.TestCase):

    def test_month(self):
        for lang in ("pt-PT", "pt-BR"):
            with self.subTest(lang=lang):
                self.assertEqual(
                    nice_date(TUESDAY, lang, include_weekday=False),
                    "doze de março, dois mil e vinte e quatro")

    def test_weekday(self):
        self.assertEqual(nice_date(TUESDAY, "pt-PT"),
                         "terça-feira, doze de março, dois mil e vinte e quatro")

    def test_relative_to_now(self):
        self.assertEqual(nice_date(TUESDAY, "pt-PT", now=datetime(2024, 1, 5),
                                   include_weekday=False),
                         "doze de março")

    def test_nice_date_time(self):
        date_part = "terça-feira, doze de março, dois mil e vinte e quatro "
        spoken = nice_date_time(TUESDAY, "pt-PT", now=datetime(2020, 1, 1))
        self.assertEqual(spoken[:len(date_part)], date_part)


if __name__ == "__main__":
    unittest.main()
