"""nice_date for Basque writes the year in words with its -ko suffix.

Euskaltzaindia, Araua 37 ("Data nola adierazi"), recommends
"1995eko martxoaren 7a(n)": the year takes -ko after a vowel ("1983ko")
and -eko after a consonant ("1995eko", from "hamabost"). A final r doubles
before the vowel ("aurreko", "beharreko"). The year words follow the table
of Araua 7 ("Zenbakien idazkeraz"): 1984 is "mila bederatziehun eta
laurogeita lau" and 1200 is "mila eta berrehun".
"""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date, nice_date_time


def date(y, m, d):
    return nice_date(datetime(y, m, d), "eu", include_weekday=False)


class TestBasqueDateYear(unittest.TestCase):

    def test_araua_37_example(self):
        self.assertEqual(
            date(1995, 3, 7),
            "mila bederatziehun eta laurogeita hamabosteko martxoaren zazpi")

    def test_suffix_after_a_vowel(self):
        self.assertEqual(date(1983, 3, 7),
                         "mila bederatziehun eta laurogeita hiruko "
                         "martxoaren zazpi")
        self.assertEqual(date(2024, 3, 12),
                         "bi mila eta hogeita lauko martxoaren hamabi")
        self.assertEqual(date(2000, 3, 7), "bi milako martxoaren zazpi")

    def test_suffix_after_a_consonant(self):
        self.assertEqual(date(2001, 3, 7),
                         "bi mila eta bateko martxoaren zazpi")
        self.assertEqual(date(1900, 3, 7),
                         "mila eta bederatziehuneko martxoaren zazpi")
        self.assertEqual(date(1970, 3, 7),
                         "mila bederatziehun eta hirurogeita hamarreko "
                         "martxoaren zazpi")

    def test_with_weekday(self):
        self.assertEqual(nice_date(datetime(2024, 3, 12), "eu"),
                         "asteartea, bi mila eta hogeita lauko "
                         "martxoaren hamabi")

    def test_nice_date_time(self):
        date_part = "asteartea, bi mila eta hogeita lauko martxoaren hamabi "
        spoken = nice_date_time(datetime(2024, 3, 12, 14, 30), "eu",
                                now=datetime(2020, 1, 1))
        self.assertEqual(spoken[:len(date_part)], date_part)


if __name__ == "__main__":
    unittest.main()
