"""The cs date puts the day before the month, as Czech does.

CLDR cs gives the full date "EEEE d. MMMM y", the month in a date in the
genitive (monthContext "format": "ledna", "února", ...) and the era
abbreviation "př. n. l.". The CLDR cs format-wide months are "ledna, února,
března, dubna, května, června, července, srpna, září, října, listopadu,
prosince".

CLDR RBNF cs %spellout-ordinal-masculine-genitive reads "1: prvního;
2: druhého; 3: třetího;" and "20: dvacátého[ >>];": the parts of an ordinal
are apart, with no hyphen. ovos-number-parser spells the same ordinals in
the nominative ("první", "dvacátý druhý"). The genitive of a hard adjective
ends in -ého for the nominative -ý, and of a soft adjective in -ího for -í,
so the nominative gives the expected genitive day name."""
import unittest
from datetime import datetime

from ovos_number_parser import pronounce_ordinal

from ovos_date_parser import nice_date, nice_date_time, nice_month, nice_year

CLDR_FORMAT_MONTHS = ("ledna", "února", "března", "dubna", "května", "června",
                      "července", "srpna", "září", "října", "listopadu",
                      "prosince")
NOW = datetime(2024, 6, 15)


def genitive(ordinal):
    return " ".join(word[:-1] + ("ého" if word.endswith("ý") else "ího")
                    for word in ordinal.split())


class TestCzechDateWords(unittest.TestCase):

    def test_day_names(self):
        for day in range(1, 32):
            with self.subTest(day=day):
                self.assertEqual(
                    nice_date(datetime(2024, 1, day), "cs", now=NOW,
                              include_weekday=False),
                    genitive(pronounce_ordinal(day, lang="cs")) + " ledna")

    def test_month_names(self):
        for month, name in enumerate(CLDR_FORMAT_MONTHS, start=1):
            with self.subTest(month=month):
                self.assertEqual(
                    nice_date(datetime(2024, month, 1), "cs", now=NOW,
                              include_weekday=False),
                    "prvního " + name)

    def test_nice_date_with_the_year(self):
        date = datetime(2023, 1, 21)
        self.assertEqual(nice_date(date, "cs"),
                         "sobota, dvacátého prvního ledna "
                         + nice_year(date, "cs"))

    def test_nice_date(self):
        self.assertEqual(
            nice_date(datetime(2024, 1, 21), "cs", now=datetime(2024, 6, 1)),
            "neděle, dvacátého prvního ledna")

    def test_nice_date_time(self):
        self.assertEqual(
            nice_date_time(datetime(2024, 3, 21, 13, 22), "cs",
                           now=datetime(2024, 6, 1), use_24hour=True),
            "čtvrtek, dvacátého prvního března v třináct dvacet dva")

    def test_era(self):
        self.assertEqual(nice_year(datetime(44, 1, 1), "cs", bc=True),
                         "čtyřicet čtyři př. n. l.")

    def test_month_stands_alone_in_the_nominative(self):
        self.assertEqual(nice_month(datetime(2024, 1, 21), "cs"), "Leden")


if __name__ == "__main__":
    unittest.main()
