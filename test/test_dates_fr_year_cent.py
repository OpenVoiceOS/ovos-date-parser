"""A fr year keeps "cent" and "vingt" invariable, as an ordinal does.

Office québécois de la langue française, Vitrine linguistique, "Pluriel de
vingt, de cent et de mille", section "Vingt et cent lorsqu'ils ont une
valeur ordinale": "Il y a un cas où vingt et cent sont invariables, même
s'ils sont multipliés et qu'ils ne sont pas suivis d'un nombre : c'est
lorsqu'ils ont une valeur ordinale, au sens de « vingtième » et de
« centième »." Examples: "L'année mille neuf cent (la 1900e année)", "La
page trois cent quatre-vingt (la 380e page)"."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_year


class TestFrenchYearCent(unittest.TestCase):

    def test_years(self):
        for year, spoken in ((100, "cent"),
                             (300, "trois-cent"),
                             (1900, "mille-neuf-cent"),
                             (1980, "mille-neuf-cent-quatre-vingt"),
                             (5200, "cinq-mille-deux-cent")):
            with self.subTest(year=year):
                self.assertEqual(nice_year(datetime(year, 1, 1), "fr"), spoken)

    def test_no_year_ends_in_a_plural(self):
        wrong = [year for year in range(1, 10000)
                 if nice_year(datetime(year, 1, 1), "fr").endswith(
                     ("cents", "vingts"))]
        self.assertEqual(wrong, [])


if __name__ == "__main__":
    unittest.main()
