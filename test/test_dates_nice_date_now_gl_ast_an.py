"""nice_date with `now` compares whole dates in gl, ast and an.

The docstrings of nice_date_gl and nice_date_ast state the rule: the year
is dropped when `now` is in the same year, the month when it is in the same
month, and "hoxe" / "güei" is said when `now` and `dt` are the same day.
nice_date_es applies it to the whole date (dt.date() == now.date(), and one
day before or after). The cases below are dates a calendar settles: 12 May
2023 is not 12 March 2024, and 1 April 2024 is the day after 31 March 2024."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date

WORDS = {"gl": ("hoxe", "mañá", "onte"),
         "ast": ("güei", "mañana", "ayeri")}


class TestNiceDateNow(unittest.TestCase):

    def test_same_day_of_month_in_another_year(self):
        for lang in ("gl", "ast", "an"):
            dt = datetime(2023, 5, 12)
            with self.subTest(lang=lang):
                self.assertEqual(nice_date(dt, lang, now=datetime(2024, 3, 12)),
                                 nice_date(dt, lang))

    def test_same_month_in_another_year(self):
        for lang in ("gl", "ast", "an"):
            dt = datetime(2023, 3, 5)
            with self.subTest(lang=lang):
                self.assertEqual(nice_date(dt, lang, now=datetime(2024, 3, 12)),
                                 nice_date(dt, lang))

    def test_same_day_of_month_in_another_month(self):
        for lang in ("gl", "ast"):
            today = WORDS[lang][0]
            with self.subTest(lang=lang):
                self.assertNotEqual(
                    nice_date(datetime(2024, 4, 12), lang,
                              now=datetime(2024, 3, 12)), today)

    def test_across_a_month_boundary(self):
        for lang, (_, tomorrow, yesterday) in WORDS.items():
            with self.subTest(lang=lang):
                self.assertEqual(nice_date(datetime(2024, 4, 1), lang,
                                           now=datetime(2024, 3, 31)), tomorrow)
                self.assertEqual(nice_date(datetime(2024, 3, 31), lang,
                                           now=datetime(2024, 4, 1)), yesterday)
                self.assertEqual(nice_date(datetime(2025, 1, 1), lang,
                                           now=datetime(2024, 12, 31)),
                                 tomorrow)

    def test_next_day_number_in_another_month(self):
        for lang, (_, tomorrow, _) in WORDS.items():
            with self.subTest(lang=lang):
                self.assertNotEqual(nice_date(datetime(2024, 4, 13), lang,
                                              now=datetime(2024, 3, 12)),
                                    tomorrow)

    def test_same_day(self):
        for lang, (today, _, _) in WORDS.items():
            with self.subTest(lang=lang):
                self.assertEqual(nice_date(datetime(2024, 3, 12, 20), lang,
                                           now=datetime(2024, 3, 12, 8)),
                                 today)


if __name__ == "__main__":
    unittest.main()
