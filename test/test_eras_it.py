"""Natural-language tests for Italian era/epoch extraction.

Same epoch definitions as test_eras_en.py (cited in
ovos_date_parser/eras.py); the phrasing under test is Italian:
"a.C."/"d.C." (avanti/dopo Cristo, the Treccani convention), "era
volgare"/"a.e.v." (the secular before/after our era phrasing), "B.P."
(anni prima del presente — the radiocarbon abbreviation).
"""
import unittest
from datetime import date, datetime, timezone

from ovos_date_parser import AstroDate, DateTimeResolution
from ovos_date_parser.eras_it import extract_era_date_it


def d(text):
    out = extract_era_date_it(text)
    return out and out[0]


def remainder(text):
    out = extract_era_date_it(text)
    return out and out[1]


class TestAvantiCristo(unittest.TestCase):
    def test_abbreviations(self):
        self.assertEqual(d("44 a.C."), AstroDate(-43))
        self.assertEqual(d("44 a. C."), AstroDate(-43))
        self.assertEqual(d("44 ac"), AstroDate(-43))
        self.assertEqual(d("1 a.C."), AstroDate(0))

    def test_spelled_out(self):
        self.assertEqual(d("44 avanti Cristo"), AstroDate(-43))
        self.assertEqual(d("500 avanti l'era volgare"), AstroDate(-499))
        self.assertEqual(d("quarantaquattro a.C."), AstroDate(-43))
        self.assertEqual(d("duemila a.C."), AstroDate(-1999))

    def test_sentences(self):
        self.assertEqual(d("giulio cesare fu assassinato nel 44 a.C."),
                         AstroDate(-43))
        self.assertEqual(
            remainder("giulio cesare fu assassinato nel 44 a.C."),
            "giulio cesare fu assassinato nel")
        self.assertEqual(d("roma fu fondata nel 753 a.C."), AstroDate(-752))


class TestDopoCristo(unittest.TestCase):
    def test_abbreviations(self):
        self.assertEqual(d("500 d.C."), date(500, 1, 1))
        self.assertEqual(d("500 d. C."), date(500, 1, 1))
        self.assertEqual(d("500 dc"), date(500, 1, 1))

    def test_spelled_out(self):
        self.assertEqual(d("79 dopo Cristo"), date(79, 1, 1))
        self.assertEqual(d("500 era volgare"), date(500, 1, 1))

    def test_sentences(self):
        self.assertEqual(d("pompei fu distrutta nel 79 d.C."),
                         date(79, 1, 1))
        self.assertEqual(remainder("pompei fu distrutta nel 79 d.C."),
                         "pompei fu distrutta nel")


class TestAnnoProfondo(unittest.TestCase):
    def test_bare_year_out_of_range(self):
        self.assertEqual(d("nell'anno 12000"), AstroDate(12000))
        self.assertEqual(d("l'anno 100000"), AstroDate(100000))

    def test_representable_year_falls_through(self):
        self.assertIsNone(extract_era_date_it("nell'anno 1996"))
        self.assertIsNone(extract_era_date_it("l'anno 2525"))
        self.assertIsNone(extract_era_date_it("nel 1996"))


class TestAnniPrimaDelPresente(unittest.TestCase):
    def test_bp(self):
        self.assertEqual(d("100 anni prima del presente"),
                         date(1850, 1, 1))
        self.assertEqual(d("2000 anni prima del presente"), AstroDate(-50))
        self.assertEqual(d("10000 BP"), AstroDate(-8050))
        self.assertEqual(d("14000 b.p."), AstroDate(-12050))

    def test_sentences(self):
        self.assertEqual(
            d("il campione fu datato a 12000 anni prima del presente"),
            AstroDate(-10050))


class TestEpocheFisse(unittest.TestCase):
    def test_unix(self):
        self.assertEqual(d("tempo unix 0"),
                         datetime(1970, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(d("tempo unix 1000000000").date(),
                         date(2001, 9, 9))

    def test_giorno_giuliano(self):
        self.assertEqual(d("giorno giuliano 2451545"), date(2000, 1, 1))
        self.assertEqual(d("giorno giuliano numero 2440588"),
                         date(1970, 1, 1))
        jd0 = d("giorno giuliano 0")
        self.assertEqual((jd0.year, jd0.month, jd0.day), (-4713, 11, 24))

    def test_era_olocenica(self):
        self.assertEqual(d("era olocenica 12025"), date(2025, 1, 1))
        self.assertEqual(d("era umana 12017"), date(2017, 1, 1))

    def test_anno_mundi(self):
        self.assertEqual(d("anno mundi 5786"), date(2025, 9, 23))


class TestSecoliMillenni(unittest.TestCase):
    def test_secolo(self):
        self.assertEqual(d("il 3º secolo a.C.").year, -299)
        self.assertEqual(d("il 1º secolo a.C."),
                         AstroDate(-99, 1, 1))
        self.assertEqual(d("secolo 5 a.C.").year, -499)
        self.assertEqual(d("roma si espanse nel 3º secolo a.C.").year,
                         -299)

    def test_millennio(self):
        self.assertEqual(d("il 2º millennio a.C.").year, -1999)
        self.assertEqual(
            d("la scrittura apparve nel 4º millennio a.C.").year,
            -3999)


class TestGuardieDiAmbiguita(unittest.TestCase):
    def test_plain_dates_do_not_trigger(self):
        for text in ("domani mattina", "venerdì", "5 marzo",
                     "tra 3 giorni", "non c'è una data qui", ""):
            self.assertIsNone(extract_era_date_it(text))

    def test_garbage_never_raises(self):
        for text in ("a.C.", "d.C.", "bp", "l'anno", "secolo a.C.",
                     "999999999999999999 a.C."):
            extract_era_date_it(text)  # must not raise

    def test_extremes(self):
        self.assertEqual(extract_era_date_it("0 a.C.")[0], date(1, 1, 1))
        self.assertEqual(d("999999999 a.C."), AstroDate(-999999998))


if __name__ == "__main__":
    unittest.main()
