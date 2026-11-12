"""The year of a spoken date follows the preposition "de", not a comma.

CLDR 49 gives the full date pattern "EEEE, d 'de' MMMM 'de' y" for pt, pt-PT,
es and gl, and "EEEE, d MMMM 'de' y" for ast, whose month names carry "de"
("de marzu"). RAE and ASALE, Diccionario panhispánico de dudas, "fecha",
§ 3 c: "La preposición de se emplea entre la mención del día y el mes, y entre
la del mes y el año: Murió el 15 de julio de 1957." § 4 keeps the comma after
the weekday: "Hoy es sábado, 18 de agosto de 2001."
"""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date, nice_date_time

# 12 March 2024 is a Tuesday (calendar.weekday(2024, 3, 12) == 1).
DT = datetime(2024, 3, 12, 16, 5)
NEXT_YEAR = datetime(2025, 1, 1)


class TestYearPreposition(unittest.TestCase):

    def test_portuguese(self):
        self.assertEqual(
            nice_date(DT, "pt-PT"),
            "terça-feira, doze de março de dois mil e vinte e quatro")
        self.assertEqual(
            nice_date(DT, "pt-PT", include_weekday=False),
            "doze de março de dois mil e vinte e quatro")

    def test_spanish(self):
        self.assertEqual(
            nice_date(DT, "es-ES"),
            "martes, doce de marzo de dos mil veinticuatro")
        self.assertEqual(
            nice_date(DT, "es-ES", include_weekday=False),
            "doce de marzo de dos mil veinticuatro")

    def test_galician(self):
        self.assertTrue(
            nice_date(DT, "gl-ES").lower().endswith(
                ", doce de marzo de dous mil e vinte e catro"))

    def test_asturian(self):
        self.assertTrue(
            nice_date(DT, "ast-ES").lower().endswith(
                ", doce de marzu de dos mil y venticuatro"))

    def test_year_kept_against_a_reference_date(self):
        self.assertEqual(
            nice_date(DT, "pt-PT", now=NEXT_YEAR, include_weekday=False),
            "doze de março de dois mil e vinte e quatro")
        self.assertEqual(
            nice_date(DT, "es-ES", now=NEXT_YEAR, include_weekday=False),
            "doce de marzo de dos mil veinticuatro")

    def test_month_kept_when_only_the_year_differs(self):
        same_month_next_year = datetime(2025, 3, 1)
        self.assertEqual(
            nice_date(DT, "gl-ES", now=same_month_next_year,
                      include_weekday=False).lower(),
            "doce de marzo de dous mil e vinte e catro")
        self.assertEqual(
            nice_date(DT, "ast-ES", now=same_month_next_year,
                      include_weekday=False).lower(),
            "doce de marzu de dos mil y venticuatro")

    def test_date_time(self):
        self.assertEqual(
            nice_date_time(DT, "pt-PT", use_24hour=True),
            "terça-feira, doze de março de dois mil e vinte e quatro "
            "às dezasseis e cinco")
        self.assertTrue(
            nice_date_time(DT, "es-ES", use_24hour=True).startswith(
                "martes, doce de marzo de dos mil veinticuatro a las "))


if __name__ == "__main__":
    unittest.main()
