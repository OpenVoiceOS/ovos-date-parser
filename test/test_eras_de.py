"""Natural-language tests for German era/epoch extraction.

Same epoch definitions as test_eras_en.py (cited in
ovos_date_parser/eras.py); the phrasing under test is German:
"v./n. Chr." (vor/nach Christus, the Duden convention), "unserer
Zeitrechnung" (the secular before/after our era phrasing), "B.P."
(Jahre vor heute — the radiocarbon abbreviation), and the German
punctuation-ordinal convention ("3. Jahrhundert").
"""
import unittest
from datetime import date, datetime, timezone

from ovos_date_parser import AstroDate, DateTimeResolution
from ovos_date_parser.eras_de import extract_era_date_de


def d(text):
    out = extract_era_date_de(text)
    return out and out[0]


def remainder(text):
    out = extract_era_date_de(text)
    return out and out[1]


class TestVorChristus(unittest.TestCase):
    def test_abbreviations(self):
        self.assertEqual(d("44 v. Chr."), AstroDate(-43))
        self.assertEqual(d("44 v.Chr."), AstroDate(-43))
        self.assertEqual(d("1 v. Chr."), AstroDate(0))

    def test_spelled_out(self):
        self.assertEqual(d("44 vor Christus"), AstroDate(-43))
        self.assertEqual(d("500 vor unserer Zeitrechnung"), AstroDate(-499))
        self.assertEqual(d("vierundvierzig v. Chr."), AstroDate(-43))
        self.assertEqual(d("zweitausend v. Chr."), AstroDate(-1999))

    def test_sentences(self):
        self.assertEqual(d("julius cäsar wurde 44 v. Chr. ermordet"),
                         AstroDate(-43))
        self.assertEqual(
            remainder("julius cäsar wurde 44 v. Chr. ermordet"),
            "julius cäsar wurde ermordet")
        self.assertEqual(d("rom wurde 753 v. Chr. gegründet"),
                         AstroDate(-752))


class TestNachChristus(unittest.TestCase):
    def test_abbreviations(self):
        self.assertEqual(d("500 n. Chr."), date(500, 1, 1))
        self.assertEqual(d("500 n.Chr."), date(500, 1, 1))

    def test_spelled_out(self):
        self.assertEqual(d("79 nach Christus"), date(79, 1, 1))
        self.assertEqual(d("500 unserer Zeitrechnung"), date(500, 1, 1))

    def test_sentences(self):
        self.assertEqual(d("pompeji wurde 79 n. Chr. zerstört"),
                         date(79, 1, 1))
        self.assertEqual(remainder("pompeji wurde 79 n. Chr. zerstört"),
                         "pompeji wurde zerstört")


class TestTiefesJahr(unittest.TestCase):
    def test_bare_year_out_of_range(self):
        self.assertEqual(d("im Jahr 12000"), AstroDate(12000))
        self.assertEqual(d("das Jahr 100000"), AstroDate(100000))

    def test_representable_year_falls_through(self):
        self.assertIsNone(extract_era_date_de("im Jahr 1996"))
        self.assertIsNone(extract_era_date_de("im Jahre 2525"))


class TestJahreVorHeute(unittest.TestCase):
    def test_bp(self):
        self.assertEqual(d("100 Jahre vor heute"), date(1850, 1, 1))
        self.assertEqual(d("2000 Jahre vor heute"), AstroDate(-50))
        self.assertEqual(d("10000 BP"), AstroDate(-8050))
        self.assertEqual(d("14000 b.p."), AstroDate(-12050))

    def test_sentences(self):
        self.assertEqual(
            d("die probe wurde auf 12000 Jahre vor heute datiert"),
            AstroDate(-10050))


class TestFesteEpochen(unittest.TestCase):
    def test_unix(self):
        self.assertEqual(d("Unixzeit 0"),
                         datetime(1970, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(d("Unixzeit 1000000000").date(),
                         date(2001, 9, 9))

    def test_julianischer_tag(self):
        self.assertEqual(d("julianischer Tag 2451545"), date(2000, 1, 1))
        self.assertEqual(d("julianisches Datum 2440588"), date(1970, 1, 1))
        jd0 = d("julianischer Tag 0")
        self.assertEqual((jd0.year, jd0.month, jd0.day), (-4713, 11, 24))

    def test_holozaen_aera(self):
        self.assertEqual(d("Holozän-Ära 12025"), date(2025, 1, 1))
        self.assertEqual(d("Menschheitsära 12017"), date(2017, 1, 1))

    def test_anno_mundi(self):
        self.assertEqual(d("anno mundi 5786"), date(2025, 1, 1))


class TestJahrhundertJahrtausend(unittest.TestCase):
    def test_jahrhundert(self):
        self.assertEqual(d("3. Jahrhundert v. Chr.").year, -299)
        self.assertEqual(d("1. Jahrhundert v. Chr."),
                         AstroDate(-99, 1, 1,
                                   resolution=DateTimeResolution.CENTURY))
        self.assertEqual(d("Rom expandierte im 3. Jahrhundert v. Chr.").year,
                         -299)

    def test_jahrtausend(self):
        self.assertEqual(d("2. Jahrtausend v. Chr.").year, -1999)
        self.assertEqual(
            d("die Schrift entstand im 4. Jahrtausend v. Chr.").year,
            -3999)


class TestMehrdeutigkeitsSchutz(unittest.TestCase):
    def test_plain_dates_do_not_trigger(self):
        for text in ("morgen früh um 8", "freitag", "5. März",
                     "in 3 Tagen", "hier ist kein Datum", ""):
            self.assertIsNone(extract_era_date_de(text))

    def test_garbage_never_raises(self):
        for text in ("v. Chr.", "n. Chr.", "bp", "im Jahr",
                     "Jahrhundert v. Chr.",
                     "999999999999999999 v. Chr."):
            extract_era_date_de(text)  # must not raise

    def test_extremes(self):
        self.assertEqual(extract_era_date_de("0 v. Chr.")[0],
                         date(1, 1, 1))
        self.assertEqual(d("999999999 v. Chr."), AstroDate(-999999998))


if __name__ == "__main__":
    unittest.main()
