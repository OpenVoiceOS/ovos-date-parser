"""Natural-language tests for Portuguese era/epoch extraction.

Same epoch definitions as test_eras_en.py (cited in
ovos_date_parser/eras.py); the phrasing under test is Portuguese:
"a.C."/"d.C." (antes/depois de Cristo), "a.e.C./e.C." (era comum),
"AP" (antes do presente — the radiocarbon abbreviation).
"""
import unittest
from datetime import date, datetime, timezone

from ovos_date_parser import AstroDate, DateTimeResolution
from ovos_date_parser.eras_pt import extract_era_date_pt


def d(text):
    out = extract_era_date_pt(text)
    return out and out[0]


def remainder(text):
    out = extract_era_date_pt(text)
    return out and out[1]


class TestAntesDeCristo(unittest.TestCase):
    def test_abbreviations(self):
        self.assertEqual(d("44 a.C."), AstroDate(-43))
        self.assertEqual(d("44 aC"), AstroDate(-43))
        self.assertEqual(d("44 a.e.c."), AstroDate(-43))
        self.assertEqual(d("1 a.C."), AstroDate(0))

    def test_spelled_out(self):
        self.assertEqual(d("44 antes de Cristo"), AstroDate(-43))
        self.assertEqual(d("500 antes da era comum"), AstroDate(-499))
        self.assertEqual(d("quarenta e quatro a.C."), AstroDate(-43))
        self.assertEqual(d("dois mil a.C."), AstroDate(-1999))

    def test_sentences(self):
        self.assertEqual(d("césar foi assassinado em 44 a.C."),
                         AstroDate(-43))
        self.assertEqual(remainder("césar foi assassinado em 44 a.C."),
                         "césar foi assassinado em")
        self.assertEqual(d("roma foi fundada em 753 a.C."), AstroDate(-752))
        self.assertEqual(d("no ano 3000 a.C."), AstroDate(-2999))
        self.assertEqual(d("no ano de 44 antes de Cristo"), AstroDate(-43))


class TestDepoisDeCristo(unittest.TestCase):
    def test_abbreviations(self):
        self.assertEqual(d("500 d.C."), date(500, 1, 1))
        self.assertEqual(d("500 dC"), date(500, 1, 1))
        self.assertEqual(d("500 e.c."), date(500, 1, 1))

    def test_spelled_out(self):
        self.assertEqual(d("79 depois de Cristo"), date(79, 1, 1))
        self.assertEqual(d("500 da era comum"), date(500, 1, 1))

    def test_sentences(self):
        self.assertEqual(d("pompeia foi destruída em 79 d.C."),
                         date(79, 1, 1))
        self.assertEqual(remainder("pompeia foi destruída em 79 d.C."),
                         "pompeia foi destruída em")


class TestAnoProfundo(unittest.TestCase):
    def test_bare_year_out_of_range(self):
        self.assertEqual(d("no ano 12000"), AstroDate(12000))
        self.assertEqual(d("o ano 100000"), AstroDate(100000))

    def test_representable_year_falls_through(self):
        self.assertIsNone(extract_era_date_pt("no ano 1996"))
        self.assertIsNone(extract_era_date_pt("o ano de 2525"))


class TestAntesDoPresente(unittest.TestCase):
    def test_ap(self):
        self.assertEqual(d("100 anos antes do presente"), date(1850, 1, 1))
        self.assertEqual(d("2000 anos antes do presente"), AstroDate(-50))
        self.assertEqual(d("10000 AP"), AstroDate(-8050))
        self.assertEqual(d("14000 a.p."), AstroDate(-12050))

    def test_sentences(self):
        self.assertEqual(
            d("a amostra foi datada em 12000 anos antes do presente"),
            AstroDate(-10050))


class TestEpocasFixas(unittest.TestCase):
    def test_unix(self):
        # second-counted eras keep their precision: aware UTC datetimes
        self.assertEqual(d("tempo unix 0"),
                         datetime(1970, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(d("timestamp unix 1000000000").date(),
                         date(2001, 9, 9))

    def test_dia_juliano(self):
        self.assertEqual(d("dia juliano 2451545"), date(2000, 1, 1))
        self.assertEqual(d("dia juliano número 2440588"), date(1970, 1, 1))
        jd0 = d("dia juliano 0")
        self.assertEqual((jd0.year, jd0.month, jd0.day), (-4713, 11, 24))

    def test_era_holocena(self):
        self.assertEqual(d("era holocena 12025"), date(2025, 1, 1))
        self.assertEqual(d("era humana 12017"), date(2017, 1, 1))

    def test_anno_mundi(self):
        self.assertEqual(d("anno mundi 5786"), date(2025, 1, 1))


class TestSeculosMilenios(unittest.TestCase):
    def test_seculo(self):
        self.assertEqual(d("o 3º século a.C.").year, -299)
        self.assertEqual(d("o 1º século a.C."),
                         AstroDate(-99, 1, 1,
                                   resolution=DateTimeResolution.CENTURY))
        self.assertEqual(d("século 5 a.C.").year, -499)
        self.assertEqual(d("roma expandiu no 3º século a.C.").year, -299)

    def test_milenio(self):
        self.assertEqual(d("o 2º milénio a.C.").year, -1999)
        self.assertEqual(d("o 2º milênio a.C.").year, -1999)  # pt-BR
        self.assertEqual(d("a escrita surgiu no 4º milénio a.C.").year,
                         -3999)


class TestGuardasDeAmbiguidade(unittest.TestCase):
    def test_plain_dates_do_not_trigger(self):
        for text in ("amanhã", "sexta-feira", "5 de março", "daqui a 3 dias",
                     "não há data aqui", ""):
            self.assertIsNone(extract_era_date_pt(text))

    def test_garbage_never_raises(self):
        for text in ("a.C.", "d.C.", "ap", "no ano", "século a.C.",
                     "999999999999999999 a.C."):
            extract_era_date_pt(text)  # must not raise

    def test_extremes(self):
        self.assertEqual(extract_era_date_pt("0 a.C.")[0], date(1, 1, 1))
        self.assertEqual(d("999999999 a.C."), AstroDate(-999999998))


if __name__ == "__main__":
    unittest.main()
