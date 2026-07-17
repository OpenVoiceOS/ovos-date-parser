"""Natural-sentence tests for Aragonese (an) date formatting.

These exercise the formatters the way a skill actually uses them: composed
into full Aragonese sentences with surrounding words, punctuation and casing,
rather than isolated word<->value anchors.

Every expected string is built only from reference-verified Aragonese forms:
- weekdays: Biquipedia "Nombre d'os días d'a semana"/"Semana"; Wiktionary "luns"
    Luns, Martes, Miercres, Chueves, Viernes, Sabado, Dominche
- months: Biquipedia "Mes"
    Chinero, Febrero, Marzo, Abril, Mayo, Chunio, Chulio, Agosto,
    Setiembre, Octubre, Noviembre, Aviento
- carrier words: "Hue" (today), "ye" (is, 3rd person singular) — attested
    Aragonese, used only to place the verified date inside a real sentence.

Aragonese is date-only for now: the spoken clock idiom is pending expert
review, so no time sentences are asserted here.
"""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date, nice_weekday, nice_month, nice_year, nice_day

# 2018-06-04 is a Monday, so the whole week is 2018-06-04 .. 2018-06-10
WEEK = {
    "Luns": datetime(2018, 6, 4),
    "Martes": datetime(2018, 6, 5),
    "Miercres": datetime(2018, 6, 6),
    "Chueves": datetime(2018, 6, 7),
    "Viernes": datetime(2018, 6, 8),
    "Sabado": datetime(2018, 6, 9),
    "Dominche": datetime(2018, 6, 10),
}
# first of each month in 2019
MONTH_FIRST = {
    "Chinero": datetime(2019, 1, 1),
    "Febrero": datetime(2019, 2, 1),
    "Marzo": datetime(2019, 3, 1),
    "Abril": datetime(2019, 4, 1),
    "Mayo": datetime(2019, 5, 1),
    "Chunio": datetime(2019, 6, 1),
    "Chulio": datetime(2019, 7, 1),
    "Agosto": datetime(2019, 8, 1),
    "Setiembre": datetime(2019, 9, 1),
    "Octubre": datetime(2019, 10, 1),
    "Noviembre": datetime(2019, 11, 1),
    "Aviento": datetime(2019, 12, 1),
}


class TestAragoneseWeekdaySentences(unittest.TestCase):
    """Every weekday spoken inside 'Hue ye ...' (Today is ...)."""

    def test_each_weekday_in_sentence(self):
        for name, dt in WEEK.items():
            sentence = f"Hue ye {nice_weekday(dt, 'an')}."
            self.assertEqual(sentence, f"Hue ye {name}.")

    def test_weekday_lowercased_mid_sentence(self):
        # a skill may lowercase the weekday when it is not sentence-initial
        dt = WEEK["Miercres"]
        sentence = f"Nos veyemos o {nice_weekday(dt, 'an').lower()} que viene."
        self.assertEqual(sentence, "Nos veyemos o miercres que viene.")


class TestAragoneseFullDateSentences(unittest.TestCase):
    """The complete date spoken as a natural clause."""

    def test_full_date_with_weekday(self):
        sentence = f"L'acto ye o {nice_date(WEEK['Martes'], 'an')}."
        self.assertEqual(
            sentence,
            "L'acto ye o Martes, cinco de Chunio de dos mil y deciueito.")

    def test_full_date_without_weekday(self):
        dt = MONTH_FIRST["Chinero"]
        sentence = f"Naixió o {nice_date(dt, 'an', include_weekday=False)}."
        self.assertEqual(sentence, "Naixió o un de Chinero de dos mil y decinueu.")

    def test_relative_same_month_shortens(self):
        now = datetime(2018, 6, 1)
        dt = datetime(2018, 6, 5)
        sentence = f"Ye ta {nice_date(dt, 'an', now=now)}."
        self.assertEqual(sentence, "Ye ta Martes, cinco.")

    def test_every_month_first_in_sentence(self):
        for month, dt in MONTH_FIRST.items():
            clause = nice_date(dt, "an", include_weekday=False)
            sentence = f"O mes prencipia o {clause}."
            self.assertIn(f"de {month} de", sentence)
            self.assertTrue(sentence.endswith("."))


class TestAragoneseDayAndYearSentences(unittest.TestCase):

    def test_nice_day_in_sentence(self):
        dt = datetime(2019, 8, 15)
        sentence = f"A fiesta ye o {nice_day(dt, 'an')}."
        self.assertEqual(sentence, "A fiesta ye o 15 Agosto.")

    def test_year_in_sentence(self):
        dt = datetime(2020, 1, 1)
        sentence = f"Estamos en l'anyo {nice_year(dt, 'an')}."
        self.assertEqual(sentence, "Estamos en l'anyo dos mil y vinte.")

    def test_bc_year_in_sentence(self):
        dt = datetime(44, 3, 15)
        sentence = f"Chulio Zesar morió en {nice_year(dt, 'an', bc=True)}."
        self.assertEqual(sentence, "Chulio Zesar morió en cuaranta y cuatre a.C..")
        self.assertIn(" a.C.", sentence)


class TestAragoneseEdgeCasesInContext(unittest.TestCase):

    def test_leap_day_sentence(self):
        dt = datetime(2020, 2, 29)
        sentence = f"O {nice_date(dt, 'an', include_weekday=False)} ye bisiesto."
        # nice_date pronounces the day number ("vintinueu" = 29)
        self.assertEqual(
            sentence, "O vintinueu de Febrero de dos mil y vinte ye bisiesto.")

    def test_lang_code_variants_route(self):
        for code in ("an", "an-ES", "AN", "an-es"):
            self.assertEqual(nice_weekday(datetime(2018, 6, 5), code), "Martes")

    def test_casing_upper_and_strip(self):
        dt = datetime(2018, 6, 5)
        loud = f"  hue ye {nice_weekday(dt, 'an')}!  ".strip().upper()
        self.assertEqual(loud, "HUE YE MARTES!")

    def test_malformed_input_raises(self):
        for bad in (None, "cinco de chunio", 20180605, [], {}, 3.14):
            with self.assertRaises((AttributeError, TypeError, KeyError)):
                nice_date(bad, "an")

    def test_cross_language_uses_aragonese_not_neighbours(self):
        # Aragonese-specific spellings, never the Castilian or Frisian ones
        self.assertEqual(nice_weekday(WEEK["Miercres"], "an"), "Miercres")
        self.assertNotEqual(nice_weekday(WEEK["Miercres"], "an"), "Miércoles")  # es
        self.assertNotEqual(nice_weekday(WEEK["Miercres"], "an"), "Woansdei")   # fy
        self.assertEqual(nice_month(MONTH_FIRST["Aviento"], "an"), "Aviento")
        self.assertNotEqual(nice_month(MONTH_FIRST["Aviento"], "an"), "Diciembre")  # es
        self.assertNotEqual(nice_month(MONTH_FIRST["Aviento"], "an"), "Desimber")   # fy
        self.assertEqual(nice_month(MONTH_FIRST["Chinero"], "an"), "Chinero")
        self.assertNotEqual(nice_month(MONTH_FIRST["Chinero"], "an"), "Enero")      # es


if __name__ == "__main__":
    unittest.main()
