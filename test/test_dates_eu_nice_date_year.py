"""nice_date for Basque writes the year and the day in words.

Euskaltzaindia, Araua 37 ("Data nola adierazi"), p. 194, recommends
"Durango(n), 1995eko martxoaren 7a(n), aukeran utziz inesiboaren marka":
only the inessive -n is optional. The year takes -ko after a vowel
("1983ko") and -eko after a consonant ("1995eko", from "hamabost"); a
final r doubles before the vowel ("beharreko", behar + -eko). The day takes
the article -a ("7a", and "urtarrilaren 20a" on p. 193), so 7 reads
"zazpia". The year words follow the table of Araua 7 ("Zenbakien
idazkeraz"): 1984 is "mila bederatziehun eta laurogeita lau" and 1200 is
"mila eta berrehun".
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
            "mila bederatziehun eta laurogeita hamabosteko martxoaren zazpia")

    def test_suffix_after_a_vowel(self):
        self.assertEqual(date(1983, 3, 7),
                         "mila bederatziehun eta laurogeita hiruko "
                         "martxoaren zazpia")
        self.assertEqual(date(2024, 3, 12),
                         "bi mila eta hogeita lauko martxoaren hamabia")
        self.assertEqual(date(2000, 3, 7), "bi milako martxoaren zazpia")

    def test_suffix_after_a_consonant(self):
        self.assertEqual(date(2001, 3, 7),
                         "bi mila eta bateko martxoaren zazpia")
        self.assertEqual(date(1900, 3, 7),
                         "mila eta bederatziehuneko martxoaren zazpia")
        self.assertEqual(date(1970, 3, 7),
                         "mila bederatziehun eta hirurogeita hamarreko "
                         "martxoaren zazpia")

    def test_with_weekday(self):
        self.assertEqual(nice_date(datetime(2024, 3, 12), "eu"),
                         "asteartea, bi mila eta hogeita lauko "
                         "martxoaren hamabia")

    def test_nice_date_time(self):
        date_part = "asteartea, bi mila eta hogeita lauko martxoaren hamabia "
        spoken = nice_date_time(datetime(2024, 3, 12, 14, 30), "eu",
                                now=datetime(2020, 1, 1))
        self.assertEqual(spoken[:len(date_part)], date_part)


class TestBasqueDateDay(unittest.TestCase):

    def test_araua_37_days(self):
        self.assertEqual(date(2024, 3, 7),
                         "bi mila eta hogeita lauko martxoaren zazpia")
        self.assertEqual(date(2024, 1, 20),
                         "bi mila eta hogeita lauko urtarrilaren hogeia")

    def test_article_after_a_consonant_and_a_final_a(self):
        # Araua 37 writes only vowel-final days; these follow the general
        # Basque article: -a after t, -ra after a doubled r, none after -a
        for day, spoken in {1: "bata", 10: "hamarra", 11: "hamaika",
                            15: "hamabosta", 30: "hogeita hamarra",
                            31: "hogeita hamaika"}.items():
            with self.subTest(day=day):
                self.assertEqual(date(2024, 3, day),
                                 f"bi mila eta hogeita lauko martxoaren {spoken}")

    def test_same_month(self):
        self.assertEqual(nice_date(datetime(2024, 3, 12), "eu",
                                   now=datetime(2024, 3, 1)),
                         "asteartea, hamabia")


if __name__ == "__main__":
    unittest.main()
