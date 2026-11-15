"""Portuguese month and weekday labels, and "às" before the time.

The Acordo Ortográfico de 1990, Base XIX 1.º b), uses the lowercase initial
"Nos nomes dos dias, meses, estações do ano: segunda-feira; outubro;
primavera". The rule has no exception for a name that stands alone.

Base XII 1.º a) writes the grave accent "Na contração da preposição a com
as formas femininas do artigo": "à (de a+a), às (de a+as)". An hour takes
the article of "hora": "a uma", "as duas", so the time reads "à uma" and
"às duas". "Meia-noite" is feminine (à) and "meio-dia" is masculine, where
a + o is "ao" with no accent."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date_time, nice_day, nice_month, nice_weekday

NOW = datetime(2020, 1, 1)
DATE = "terça-feira, doze de março de dois mil e vinte e quatro"


class TestPortugueseLabels(unittest.TestCase):

    def test_nice_month(self):
        self.assertEqual(nice_month(datetime(2024, 3, 12), "pt-PT"), "março")

    def test_nice_weekday(self):
        self.assertEqual(nice_weekday(datetime(2024, 3, 12), "pt-PT"),
                         "terça-feira")

    def test_nice_day(self):
        self.assertEqual(nice_day(datetime(2024, 3, 12), "pt-PT"), "12 de março")


class TestPortugueseCrase(unittest.TestCase):

    def check(self, hour, minute, spoken):
        self.assertEqual(
            nice_date_time(datetime(2024, 3, 12, hour, minute), "pt-PT",
                           now=NOW),
            f"{DATE} {spoken}")

    def test_plural_hours(self):
        self.check(14, 30, "às duas e meia")

    def test_one_o_clock(self):
        self.check(13, 5, "à uma e cinco")

    def test_midnight_and_noon(self):
        self.check(0, 30, "à meia-noite e meia")
        self.check(12, 30, "ao meio-dia e meia")


if __name__ == "__main__":
    unittest.main()
