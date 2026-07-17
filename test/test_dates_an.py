import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (
    nice_year, nice_weekday, nice_month, nice_day, nice_date,
)
from ovos_date_parser.dates_an import (
    nice_date_an, WEEKDAYS_AN, MONTHS_AN,
)

# A Tuesday
REF = datetime(2018, 6, 5)


class TestAragoneseAnchors(unittest.TestCase):
    """Verified anchors: Biquipedia "Nombre d'os días d'a semana", "Semana",
    "Mes"; Aragonese Wiktionary."""

    def test_weekdays(self):
        expected = ["Luns", "Martes", "Miercres", "Chueves",
                    "Viernes", "Sabado", "Dominche"]
        for i, name in enumerate(expected):
            # 2018-06-04 is a Monday
            self.assertEqual(nice_weekday(datetime(2018, 6, 4 + i), "an"), name)

    def test_months(self):
        expected = {
            1: "Chinero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Chunio", 7: "Chulio", 8: "Agosto",
            9: "Setiembre", 10: "Octubre", 11: "Noviembre", 12: "Aviento",
        }
        for m, name in expected.items():
            self.assertEqual(nice_month(datetime(2018, m, 1), "an"), name)

    def test_full_date(self):
        # weekday, day "de" month "de" year
        out = nice_date(datetime(2018, 6, 5), "an")
        self.assertTrue(out.startswith("Martes,"))
        self.assertIn("de Chunio de", out)

    def test_date_relative_now_drops_same_year(self):
        now = datetime(2018, 6, 1)
        out = nice_date_an(datetime(2018, 6, 5), now=now)
        # same month and year -> just weekday + day
        self.assertNotIn("Chunio", out)
        self.assertNotIn("mil", out)


class TestAragoneseAdversarial(unittest.TestCase):

    def test_bad_input_raises(self):
        for bad in (None, "not a date", 12345, [], {}):
            with self.assertRaises((AttributeError, TypeError, KeyError)):
                nice_weekday(bad, "an")

    def test_lang_code_variants_route(self):
        for code in ("an", "an-ES", "AN"):
            self.assertEqual(nice_weekday(REF, code), "Martes")

    def test_leap_day(self):
        self.assertEqual(nice_month(datetime(2020, 2, 29), "an"), "Febrero")
        self.assertEqual(nice_day(datetime(2020, 2, 29), "an"), "29 Febrero")

    def test_bc_year(self):
        self.assertTrue(nice_year(datetime(44, 3, 15), "an", bc=True).endswith("a.C."))

    def test_full_year_date_sweep_never_crashes(self):
        dt = datetime(2019, 1, 1)
        seen = 0
        while dt.year == 2019:
            out = nice_date(dt, "an")
            self.assertTrue(out)
            self.assertRegex(out, r",")  # weekday prefix + comma
            seen += 1
            dt = dt + timedelta(days=1)
        self.assertEqual(seen, 365)

    def test_tables_complete(self):
        self.assertEqual(set(WEEKDAYS_AN), set(range(7)))
        self.assertEqual(set(MONTHS_AN), set(range(1, 13)))


if __name__ == "__main__":
    unittest.main()
