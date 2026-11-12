"""German counts one of a unit with the article form: "eine Minute".

CLDR RBNF de has "1: ein;" in %spellout-cardinal-masculine and "1: eine;" in
%spellout-cardinal-feminine; "eins" is %spellout-numbering, the numeral said
alone (Duden "eins": "eins und zwei macht drei", "es ist eins"). Tag is
masculine; Stunde, Minute and Sekunde are feminine (Duden: "eine Stunde Zeit
haben")."""
import unittest

from ovos_date_parser import nice_duration


class TestGermanDurationOne(unittest.TestCase):

    def test_one_of_each_unit(self):
        for seconds, spoken in ((1, "eine Sekunde"),
                                (60, "eine Minute"),
                                (3600, "eine Stunde")):
            with self.subTest(seconds=seconds):
                self.assertEqual(nice_duration(seconds, "de"), spoken)

    def test_one_day(self):
        self.assertEqual(nice_duration(86400, "de").split(), ["ein", "Tag"])

    def test_one_beside_other_counts(self):
        self.assertEqual(nice_duration(2 * 3600 + 60 + 21, "de-DE"),
                         "zwei Stunden eine Minute einundzwanzig Sekunden")

    def test_other_languages_keep_their_numeral(self):
        self.assertEqual(nice_duration(61, "en"), "one minute one second")


if __name__ == "__main__":
    unittest.main()
