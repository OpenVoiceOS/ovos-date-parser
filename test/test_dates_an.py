import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (
    nice_year, nice_weekday, nice_month, nice_day, nice_date,
    nice_time, nice_date_time,
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
            5: "Mayo", 6: "Chunyo", 7: "Chuliol", 8: "Agosto",
            9: "Setiembre", 10: "Octubre", 11: "Noviembre", 12: "Deciembre",
        }
        for m, name in expected.items():
            self.assertEqual(nice_month(datetime(2018, m, 1), "an"), name)

    def test_full_date(self):
        # weekday, day "de" month "de" year
        out = nice_date(datetime(2018, 6, 5), "an")
        self.assertTrue(out.startswith("Martes,"))
        self.assertIn("de Chunyo de", out)

    def test_date_connector_elision(self):
        # "de" elides to "d'" before a vowel-initial month, else stays "de"
        self.assertIn("d'Abril", nice_date(datetime(2018, 4, 2), "an"))
        self.assertIn("d'Agosto", nice_date(datetime(2018, 8, 2), "an"))
        self.assertIn("d'Octubre", nice_date(datetime(2018, 10, 2), "an"))
        self.assertIn("de Chinero", nice_date(datetime(2018, 1, 2), "an"))
        self.assertIn("de Deciembre", nice_date(datetime(2018, 12, 2), "an"))
        # the connector before the year is always "de"
        self.assertNotIn("d'2018", nice_date(datetime(2018, 4, 2), "an"))

    def test_date_relative_now_drops_same_year(self):
        now = datetime(2018, 6, 1)
        out = nice_date_an(datetime(2018, 6, 5), now=now)
        # same month and year -> just weekday + day
        self.assertNotIn("Chunyo", out)
        self.assertNotIn("mil", out)


class TestAragoneseClock(unittest.TestCase):
    """Spoken-clock idiom per the Aragonese review."""

    def _t(self, h, m):
        return nice_time(datetime(2018, 1, 1, h, m), "an")

    def test_on_the_hour(self):
        self.assertEqual(self._t(1, 0), "Ye la una")
        self.assertEqual(self._t(2, 0), "Son las dos")
        self.assertEqual(self._t(3, 0), "Son las tres")

    def test_half_past_counts_to_next(self):
        self.assertEqual(self._t(4, 30), "Ye la meya pa las cinco")
        self.assertEqual(self._t(7, 30), "Ye la meya pa las ueito")

    def test_quarters(self):
        self.assertEqual(self._t(4, 15), "Ye lo cuarto pa las cinco")
        self.assertEqual(self._t(4, 45), "Son los tres cuartos pa las cinco")

    def test_loose_minutes(self):
        self.assertEqual(self._t(4, 10), "Son las cuatro y diez")
        self.assertEqual(self._t(4, 50), "Son las cinco menos diez")

    def test_wraparound_to_one_and_twelve(self):
        self.assertEqual(self._t(11, 15), "Ye lo cuarto pa las doce")
        self.assertEqual(self._t(12, 15), "Ye lo cuarto pa las una")

    def test_display_form(self):
        self.assertEqual(
            nice_time(datetime(2018, 1, 1, 4, 30), "an", speech=False), "4:30")

    def test_date_time_combines(self):
        out = nice_date_time(datetime(2018, 6, 5, 4, 30), "an")
        self.assertIn("Ye la meya pa las cinco", out)
        self.assertIn("de Chunyo", out)

    def test_bad_time_input_raises(self):
        for bad in (None, "nope", 123):
            with self.assertRaises((AttributeError, TypeError)):
                nice_time(bad, "an")


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
