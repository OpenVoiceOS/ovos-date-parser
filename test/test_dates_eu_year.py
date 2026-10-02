"""Basque year pronunciation: ``nice_year`` must speak words, not digits."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_year


class TestNiceYearEu(unittest.TestCase):
    """One case per century shape, anchored on ``pronounce_number_eu``."""

    def test_single_digit(self):
        self.assertEqual(nice_year(datetime(1, 1, 1), "eu-ES"), "bat")

    def test_two_digit(self):
        self.assertEqual(nice_year(datetime(99, 1, 1), "eu-ES"),
                          "laurogeita hemeretzi")

    def test_three_digit_round_hundred(self):
        self.assertEqual(nice_year(datetime(500, 1, 1), "eu-ES"), "bostehun")

    def test_three_digit(self):
        self.assertEqual(nice_year(datetime(999, 1, 1), "eu-ES"),
                          "bederatziehun eta laurogeita hemeretzi")

    def test_four_digit_round_thousand(self):
        self.assertEqual(nice_year(datetime(1000, 1, 1), "eu-ES"), "mila")

    def test_four_digit_1500s(self):
        self.assertEqual(nice_year(datetime(1519, 1, 1), "eu-ES"),
                          "mila bostehun eta hemeretzi")

    def test_four_digit_1900s(self):
        self.assertEqual(nice_year(datetime(1983, 1, 1), "eu-ES"),
                          "mila bederatziehun eta laurogeita hiru")

    def test_four_digit_round_thousand_multiple(self):
        self.assertEqual(nice_year(datetime(2000, 1, 1), "eu-ES"), "bi mila")

    def test_four_digit_2000s(self):
        self.assertEqual(nice_year(datetime(2024, 1, 1), "eu-ES"),
                          "bi mila eta hogeita lau")

    def test_lang_code_variants_route(self):
        for code in ("eu", "eu-ES", "EU", "EU-es"):
            self.assertEqual(nice_year(datetime(1983, 1, 1), code),
                              "mila bederatziehun eta laurogeita hiru")

    def test_bc_year(self):
        self.assertTrue(
            nice_year(datetime(44, 3, 15), "eu-ES", bc=True).endswith("k.a."))

    def test_never_returns_bare_digits(self):
        for year in (1, 99, 500, 999, 1000, 1519, 1900, 1983, 2000, 2024):
            spoken = nice_year(datetime(year, 1, 1), "eu-ES")
            self.assertFalse(spoken.isdigit(), f"{year} -> {spoken!r}")


if __name__ == "__main__":
    unittest.main()
