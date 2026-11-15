"""nice_day puts a day and a month together, so the month takes the format
form: the genitive in Czech and Polish.

CLDR cs and pl give the month in a date in the monthContext "format": cs
"ledna, února, března, dubna, května, června, července, srpna, září, října,
listopadu, prosince"; pl "stycznia, lutego, marca, kwietnia, maja, czerwca,
lipca, sierpnia, września, października, listopada, grudnia". The CLDR cs
date pattern is "d. MMMM y", the pl pattern "d MMMM y", with the format
month. nice_month says the month alone, so it keeps the stand-alone form."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_day, nice_month

CS = ("ledna", "února", "března", "dubna", "května", "června", "července",
      "srpna", "září", "října", "listopadu", "prosince")
PL = ("stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca",
      "sierpnia", "września", "października", "listopada", "grudnia")


class TestNiceDayFormatMonth(unittest.TestCase):

    def test_every_month(self):
        for lang, months in (("cs", CS), ("pl", PL)):
            for month, name in enumerate(months, start=1):
                with self.subTest(lang=lang, month=month):
                    self.assertEqual(nice_day(datetime(2024, month, 21), lang),
                                     "21 " + name)

    def test_month_first(self):
        self.assertEqual(nice_day(datetime(2024, 1, 21), "cs-CZ", "MDY"),
                         "ledna 21")

    def test_month_alone_stays_nominative(self):
        self.assertEqual(nice_month(datetime(2024, 1, 21), "cs"), "Leden")
        self.assertEqual(nice_month(datetime(2024, 1, 21), "pl"), "Styczeń")

    def test_other_languages_unchanged(self):
        self.assertEqual(nice_day(datetime(2024, 1, 21), "en"), "21 January")
        self.assertEqual(nice_day(datetime(2024, 1, 21), "de"), "21 Januar")


if __name__ == "__main__":
    unittest.main()
