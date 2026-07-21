"""Natural-language tests for French era/epoch extraction.

Same epoch definitions as test_eras_en.py (cited in
ovos_date_parser/eras.py); the phrasing under test is French:
"av./ap. J.-C." (avant/après Jésus-Christ), "ère/notre ère" (the
secular before/after our era phrasing), "B.P." (avant le présent — the
radiocarbon abbreviation).

Spelled-out multi-word numbers are tested with a space between the
tens and units word ("quarante quatre") rather than the hyphenated
written form ("quarante-quatre"): :func:`FR.numbers_to_digits
<ovos_number_parser.numbers_fr.FR.numbers_to_digits>` mis-tokenises the
hyphenated compound (turning "quarante-quatre" into "40 - 4" instead of
"44"), a pre-existing library quirk unrelated to era phrasing.
"""
import unittest
from datetime import date, datetime, timezone

from ovos_date_parser import AstroDate, DateTimeResolution
from ovos_date_parser.eras_fr import extract_era_date_fr


def d(text):
    out = extract_era_date_fr(text)
    return out and out[0]


def remainder(text):
    out = extract_era_date_fr(text)
    return out and out[1]


class TestAvantJesusChrist(unittest.TestCase):
    def test_abbreviations(self):
        self.assertEqual(d("44 av. J.-C."), AstroDate(-43))
        self.assertEqual(d("44 av. JC"), AstroDate(-43))
        self.assertEqual(d("1 av. J.-C."), AstroDate(0))

    def test_spelled_out(self):
        self.assertEqual(d("44 avant Jésus-Christ"), AstroDate(-43))
        self.assertEqual(d("500 avant notre ère"), AstroDate(-499))
        self.assertEqual(d("quarante quatre av. J.-C."), AstroDate(-43))
        self.assertEqual(d("deux mille av. J.-C."), AstroDate(-1999))

    def test_sentences(self):
        self.assertEqual(d("jules césar fut assassiné en 44 av. J.-C."),
                         AstroDate(-43))
        self.assertEqual(
            remainder("jules césar fut assassiné en 44 av. J.-C."),
            "jules césar fut assassiné en")
        self.assertEqual(d("rome fut fondée en 753 av. J.-C."),
                         AstroDate(-752))
        self.assertEqual(d("44 avant jésus-christ"), AstroDate(-43))


class TestApresJesusChrist(unittest.TestCase):
    def test_abbreviations(self):
        self.assertEqual(d("500 ap. J.-C."), date(500, 1, 1))
        self.assertEqual(d("500 ap. JC"), date(500, 1, 1))

    def test_spelled_out(self):
        self.assertEqual(d("79 après Jésus-Christ"), date(79, 1, 1))
        self.assertEqual(d("500 de notre ère"), date(500, 1, 1))

    def test_sentences(self):
        self.assertEqual(d("pompéi fut détruite en 79 ap. J.-C."),
                         date(79, 1, 1))
        self.assertEqual(remainder("pompéi fut détruite en 79 ap. J.-C."),
                         "pompéi fut détruite en")


class TestAnneeProfonde(unittest.TestCase):
    def test_bare_year_out_of_range(self):
        self.assertEqual(d("en l'an 12000"), AstroDate(12000))
        self.assertEqual(d("l'an 100000"), AstroDate(100000))

    def test_representable_year_falls_through(self):
        self.assertIsNone(extract_era_date_fr("en l'an 1996"))
        self.assertIsNone(extract_era_date_fr("l'année 2525"))


class TestAvantLePresent(unittest.TestCase):
    def test_bp(self):
        self.assertEqual(d("100 ans avant le présent"), date(1850, 1, 1))
        self.assertEqual(d("2000 ans avant le présent"), AstroDate(-50))
        self.assertEqual(d("10000 BP"), AstroDate(-8050))
        self.assertEqual(d("14000 b.p."), AstroDate(-12050))

    def test_sentences(self):
        self.assertEqual(
            d("l'échantillon fut daté à 12000 ans avant le présent"),
            AstroDate(-10050))


class TestEpoquesFixes(unittest.TestCase):
    def test_unix(self):
        self.assertEqual(d("temps unix 0"),
                         datetime(1970, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(d("temps unix 1000000000").date(),
                         date(2001, 9, 9))

    def test_jour_julien(self):
        self.assertEqual(d("jour julien 2451545"), date(2000, 1, 1))
        self.assertEqual(d("jour julien numéro 2440588"), date(1970, 1, 1))
        jd0 = d("jour julien 0")
        self.assertEqual((jd0.year, jd0.month, jd0.day), (-4713, 11, 24))

    def test_ere_holocene(self):
        self.assertEqual(d("ère holocène 12025"), date(2025, 1, 1))
        self.assertEqual(d("ère humaine 12017"), date(2017, 1, 1))

    def test_anno_mundi(self):
        self.assertEqual(d("anno mundi 5786"), date(2025, 1, 1))


class TestSieclesMillenaires(unittest.TestCase):
    def test_siecle(self):
        self.assertEqual(d("le 3e siècle av. J.-C.").year, -299)
        self.assertEqual(d("le 1er siècle av. J.-C."),
                         AstroDate(-99, 1, 1,
                                   resolution=DateTimeResolution.CENTURY))
        self.assertEqual(d("siècle 5 av. J.-C.").year, -499)
        self.assertEqual(d("rome s'étendit au 3e siècle av. J.-C.").year,
                         -299)

    def test_millenaire(self):
        self.assertEqual(d("le 2e millénaire av. J.-C.").year, -1999)
        self.assertEqual(
            d("l'écriture apparut au 4e millénaire av. J.-C.").year,
            -3999)


class TestGardesFousAmbiguite(unittest.TestCase):
    def test_plain_dates_do_not_trigger(self):
        for text in ("demain matin", "vendredi", "5 mars",
                     "dans 3 jours", "il n'y a pas de date ici", ""):
            self.assertIsNone(extract_era_date_fr(text))

    def test_garbage_never_raises(self):
        for text in ("av. J.-C.", "ap. J.-C.", "bp", "l'an", "siècle av. J.-C.",
                     "999999999999999999 av. J.-C."):
            extract_era_date_fr(text)  # must not raise

    def test_extremes(self):
        self.assertEqual(extract_era_date_fr("0 av. J.-C.")[0],
                         date(1, 1, 1))
        self.assertEqual(d("999999999 av. J.-C."), AstroDate(-999999998))


if __name__ == "__main__":
    unittest.main()
