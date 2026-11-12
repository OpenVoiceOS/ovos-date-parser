"""Czech reads a year as a cardinal number.

CLDR RBNF cs: "%spellout-numbering-year: 0: =%spellout-numbering=;", with
"1000: tisíc[ >>];" and "2000: <%spellout-cardinal-masculine<
$(cardinal,one{tisíc}few{tisíce}other{tisíc})$[ >>];".
ÚJČ Internetová jazyková příručka, heslo "sto": "ve spojení s výrazem dvě
mají tvary 1., 4. a 5. p. mn. č. podobu stě (dvě stě)"; nominative plural
"sta", genitive plural "set" ("pět set"). Heslo "tisíc": rod m. neživ.,
1. p. mn. č. "tisíce", 2. p. mn. č. "tisíc".
"""
import datetime
import unittest

from ovos_date_parser import nice_date, nice_date_time, nice_year

GOLD = {
    454: "čtyři sta padesát čtyři",
    803: "osm set tři",
    1000: "tisíc",
    1012: "tisíc dvanáct",
    1100: "tisíc sto",
    1807: "tisíc osm set sedm",
    1988: "tisíc devět set osmdesát osm",
    2000: "dva tisíce",
    2018: "dva tisíce osmnáct",
    2200: "dva tisíce dvě stě",
    3120: "tři tisíce sto dvacet",
    4300: "čtyři tisíce tři sta",
    5200: "pět tisíc dvě stě",
    9999: "devět tisíc devět set devadesát devět",
}


class TestCzechYear(unittest.TestCase):
    def test_gold_years(self):
        for year, words in GOLD.items():
            with self.subTest(year=year):
                self.assertEqual(nice_year(datetime.datetime(year, 1, 1), "cs"), words)

    def test_bc(self):
        self.assertEqual(nice_year(datetime.datetime(1988, 1, 1), "cs-CZ", bc=True),
                         "tisíc devět set osmdesát osm př. n. l.")

    def test_hundred_and_thousand_forms_agree_with_the_count(self):
        hundreds = {1: "sto", 2: "dvě stě", 3: "tři sta", 4: "čtyři sta",
                    5: "pět set", 6: "šest set", 7: "sedm set", 8: "osm set",
                    9: "devět set"}
        thousands = {2: "dva tisíce", 3: "tři tisíce", 4: "čtyři tisíce",
                     5: "pět tisíc", 9: "devět tisíc"}
        for h, words in hundreds.items():
            self.assertEqual(nice_year(datetime.datetime(h * 100, 1, 1), "cs"), words)
        for t, words in thousands.items():
            self.assertEqual(nice_year(datetime.datetime(t * 1000, 1, 1), "cs"), words)

    def test_date_carries_the_same_year(self):
        dt = datetime.datetime(2017, 1, 31, 13, 22, 3)
        self.assertEqual(nice_date(dt, "cs"),
                         "úterý, třicátého prvního ledna dva tisíce sedmnáct")
        self.assertEqual(nice_date_time(dt, "cs", use_24hour=True),
                         "úterý, třicátého prvního ledna dva tisíce sedmnáct "
                         "v třináct dvacet dva")


if __name__ == "__main__":
    unittest.main()
