"""Natural-language tests for Spanish era/epoch extraction.

Same epoch definitions as test_eras_en.py (cited in
ovos_date_parser/eras.py); the phrasing under test is Spanish:
"a.C."/"d.C." (antes/después de Cristo, the RAE/DPD "a. C."/"d. C."
convention), "a.e.c."/"e.c." (antes/después de nuestra era), "AP" (años
antes del presente — the radiocarbon abbreviation).
"""
import unittest
from datetime import date, datetime, timezone

from ovos_date_parser import AstroDate, DateTimeResolution
from ovos_date_parser.eras_es import extract_era_date_es


def d(text):
    out = extract_era_date_es(text)
    return out and out[0]


def remainder(text):
    out = extract_era_date_es(text)
    return out and out[1]


class TestAntesDeCristo(unittest.TestCase):
    def test_abbreviations(self):
        self.assertEqual(d("44 a.C."), AstroDate(-43))
        self.assertEqual(d("44 a. C."), AstroDate(-43))
        self.assertEqual(d("44 ac"), AstroDate(-43))
        self.assertEqual(d("44 a.e.c."), AstroDate(-43))
        self.assertEqual(d("1 a.C."), AstroDate(0))

    def test_spelled_out(self):
        self.assertEqual(d("44 antes de Cristo"), AstroDate(-43))
        self.assertEqual(d("500 antes de nuestra era"), AstroDate(-499))
        self.assertEqual(d("cuarenta y cuatro a.C."), AstroDate(-43))
        self.assertEqual(d("dos mil a.C."), AstroDate(-1999))

    def test_sentences(self):
        self.assertEqual(d("julio césar fue asesinado en 44 a.C."),
                         AstroDate(-43))
        self.assertEqual(remainder("julio césar fue asesinado en 44 a.C."),
                         "julio césar fue asesinado en")
        self.assertEqual(d("roma fue fundada en 753 a.C."), AstroDate(-752))
        self.assertEqual(d("en el año 3000 a.C."), AstroDate(-2999))
        self.assertEqual(d("en el año de 44 antes de Cristo"),
                         AstroDate(-43))


class TestDespuesDeCristo(unittest.TestCase):
    def test_abbreviations(self):
        self.assertEqual(d("500 d.C."), date(500, 1, 1))
        self.assertEqual(d("500 d. C."), date(500, 1, 1))
        self.assertEqual(d("500 dc"), date(500, 1, 1))
        self.assertEqual(d("500 e.c."), date(500, 1, 1))

    def test_spelled_out(self):
        self.assertEqual(d("79 después de Cristo"), date(79, 1, 1))
        self.assertEqual(d("500 de nuestra era"), date(500, 1, 1))

    def test_sentences(self):
        self.assertEqual(d("pompeya fue destruida en 79 d.C."),
                         date(79, 1, 1))
        self.assertEqual(remainder("pompeya fue destruida en 79 d.C."),
                         "pompeya fue destruida en")


class TestAnoProfundo(unittest.TestCase):
    def test_bare_year_out_of_range(self):
        self.assertEqual(d("en el año 12000"), AstroDate(12000))
        self.assertEqual(d("el año 100000"), AstroDate(100000))

    def test_representable_year_falls_through(self):
        self.assertIsNone(extract_era_date_es("en el año 1996"))
        self.assertIsNone(extract_era_date_es("el año de 2525"))


class TestAnosAntesDelPresente(unittest.TestCase):
    def test_ap(self):
        self.assertEqual(d("100 años antes del presente"),
                         date(1850, 1, 1))
        self.assertEqual(d("2000 años antes del presente"), AstroDate(-50))
        self.assertEqual(d("10000 AP"), AstroDate(-8050))
        self.assertEqual(d("14000 a.p."), AstroDate(-12050))

    def test_sentences(self):
        self.assertEqual(
            d("la muestra fue datada en 12000 años antes del presente"),
            AstroDate(-10050))


class TestEpocasFijas(unittest.TestCase):
    def test_unix(self):
        self.assertEqual(d("tiempo unix 0"),
                         datetime(1970, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(d("timestamp unix 1000000000").date(),
                         date(2001, 9, 9))

    def test_dia_juliano(self):
        self.assertEqual(d("día juliano 2451545"), date(2000, 1, 1))
        self.assertEqual(d("día juliano número 2440588"), date(1970, 1, 1))
        jd0 = d("día juliano 0")
        self.assertEqual((jd0.year, jd0.month, jd0.day), (-4713, 11, 24))

    def test_era_holocena(self):
        self.assertEqual(d("era holocena 12025"), date(2025, 1, 1))
        self.assertEqual(d("era humana 12017"), date(2017, 1, 1))

    def test_anno_mundi(self):
        self.assertEqual(d("anno mundi 5786"), date(2025, 9, 23))


class TestSiglosMilenios(unittest.TestCase):
    def test_siglo(self):
        self.assertEqual(d("el 3º siglo a.C.").year, -299)
        self.assertEqual(d("el 1º siglo a.C."),
                         AstroDate(-99, 1, 1))
        self.assertEqual(d("siglo 5 a.C.").year, -499)
        self.assertEqual(d("roma se expandió en el 3º siglo a.C.").year,
                         -299)

    def test_milenio(self):
        self.assertEqual(d("el 2º milenio a.C.").year, -1999)
        self.assertEqual(d("la escritura surgió en el 4º milenio a.C.").year,
                         -3999)


class TestGuardasDeAmbiguedad(unittest.TestCase):
    def test_plain_dates_do_not_trigger(self):
        for text in ("mañana a las 5", "viernes", "5 de marzo",
                     "dentro de 3 días", "no hay fecha aquí", ""):
            self.assertIsNone(extract_era_date_es(text))

    def test_garbage_never_raises(self):
        for text in ("a.C.", "d.C.", "ap", "el año", "siglo a.C.",
                     "999999999999999999 a.C."):
            extract_era_date_es(text)  # must not raise

    def test_extremes(self):
        self.assertEqual(extract_era_date_es("0 a.C.")[0], date(1, 1, 1))
        self.assertEqual(d("999999999 a.C."), AstroDate(-999999998))


if __name__ == "__main__":
    unittest.main()
