"""The spoken form of a Portuguese date, clock time and year.

Expected values follow the rules quoted in the dates_pt module docstring:
day 1 is "primeiro" (Cunha & Cintra p. 374), a whole hour takes "horas"
("às seis horas"), the clock with unit words reads "vinte horas, trinta
minutos e vinte e quatro segundos" (written here without the comma), and
zero hours is "zero hora" in pt-BR and "zero horas" in pt-PT (Dicio). The
number words are those of pronounce_number_pt.
"""
import unittest

from ovos_date_parser import nice_date
from ovos_date_parser.spoken import (
    UnsupportedForm, spoken_date, spoken_time, spoken_year
)
from datetime import datetime


class TestSpokenDatePt(unittest.TestCase):
    ROWS = [("pt-PT", dict(day=12, month=3, year=2024),
             "doze de março de dois mil e vinte e quatro"),
            ("pt-PT", dict(day=1, month=3, year=2024),
             "primeiro de março de dois mil e vinte e quatro"),
            ("pt-BR", dict(day=1, month=5, year=2024),
             "primeiro de maio de dois mil e vinte e quatro"),
            ("pt-BR", dict(day=19, month=12, year=2016),
             "dezenove de dezembro de dois mil e dezesseis"),
            ("pt-PT", dict(day=19, month=12, year=2016),
             "dezanove de dezembro de dois mil e dezasseis"),
            ("pt", dict(day=16, month=7), "dezasseis de julho"),
            ("pt-PT", dict(day=1), "primeiro"),
            ("pt-PT", dict(day=3), "três"),
            ("pt-PT", dict(month=3), "março"),
            ("pt-PT", dict(year=1999), "mil novecentos e noventa e nove"),
            ("pt-PT", dict(month=3, year=2024),
             "março de dois mil e vinte e quatro"),
            ("pt-PT", dict(day=29, month=2), "vinte e nove de fevereiro"),
            ("pt-PT", dict(day=12, month=3, year=2024, weekday=1),
             "terça-feira doze de março de dois mil e vinte e quatro")]

    def test_dates(self):
        for lang, fields, expected in self.ROWS:
            with self.subTest(lang=lang, fields=fields):
                self.assertEqual(spoken_date(lang, **fields), expected)

    def test_words_only(self):
        for lang, fields, _ in self.ROWS:
            out = spoken_date(lang, **fields)
            with self.subTest(out=out):
                self.assertRegex(out, r"^[a-zà-ú]+(?:[ -][a-zà-ú]+)*$")

    def test_nice_date_says_primeiro_too(self):
        self.assertEqual(
            nice_date(datetime(2024, 5, 1), "pt-PT", include_weekday=False),
            "primeiro de maio de dois mil e vinte e quatro")

    def test_impossible_dates(self):
        for fields in [dict(day=31, month=2), dict(day=29, month=2, year=2023),
                       dict(day=32), dict(month=13), dict(day=12, year=2024),
                       dict(day=12, month=3, year=2024, weekday=0),
                       dict(month=3, year=2024, weekday=4),
                       dict(day=12, weekday=7), dict(day=12, weekday=-1), {}]:
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):
                    spoken_date("pt-PT", **fields)

    def test_no_case_in_portuguese(self):
        with self.assertRaises(UnsupportedForm):
            spoken_date("pt-PT", day=1, month=5, case="genitive")
        with self.assertRaises(UnsupportedForm):
            spoken_date("pt-PT", day=1, month=5, declension="weak")

    def test_region_spellings(self):
        for lang in ("pt-BR", "pt-br", "pt_BR", "PT_br"):
            with self.subTest(lang=lang):
                self.assertEqual(spoken_date(lang, day=16), "dezesseis")
        for lang in ("pt", "pt-PT", "pt-AO"):
            with self.subTest(lang=lang):
                self.assertEqual(spoken_date(lang, day=16), "dezasseis")

    def test_other_languages_refuse(self):
        with self.assertRaises(UnsupportedForm) as raised:
            spoken_date("hi", day=1, month=5)
        self.assertIsInstance(raised.exception, NotImplementedError)


class TestSpokenTimePt(unittest.TestCase):
    ROWS = [("pt-PT", (14, 30), {}, "catorze e trinta"),
            ("pt-PT", (21, 0), {}, "vinte e uma horas"),
            ("pt-PT", (1, 0), {}, "uma hora"),
            ("pt-PT", (0, 0), {}, "zero horas"),
            ("pt-BR", (0, 0), {}, "zero hora"),
            ("pt-BR", (2, 0), {}, "duas horas"),
            ("pt-PT", (9, 5), {}, "nove e cinco"),
            ("pt-PT", (14, 30), dict(style="units"),
             "catorze horas e trinta minutos"),
            ("pt-PT", (19, 30), dict(style="units"),
             "dezanove horas e trinta minutos"),
            ("pt-BR", (19, 30), dict(style="units"),
             "dezenove horas e trinta minutos"),
            ("pt-PT", (1, 1), dict(style="units"), "uma hora e um minuto"),
            ("pt-PT", (21, 0), dict(style="units"), "vinte e uma horas"),
            ("pt-PT", (20, 30, 24), dict(style="units"),
             "vinte horas trinta minutos e vinte e quatro segundos"),
            ("pt-PT", (20, 0, 1), dict(style="units"),
             "vinte horas e um segundo"),
            ("pt-PT", (14, 30), dict(clock="12h"), "duas e trinta"),
            ("pt-PT", (14, 0), dict(clock="12h", period=True),
             "duas horas da tarde"),
            ("pt-PT", (0, 30), dict(clock="12h"), "doze e trinta"),
            ("pt-PT", (0, 30), dict(clock="12h", period=True),
             "doze e trinta da madrugada"),
            ("pt-PT", (0, 0), dict(clock="12h", period=True), "meia-noite"),
            ("pt-PT", (12, 0), dict(clock="12h", period=True), "meio-dia"),
            ("pt-PT", (12, 0), dict(clock="12h"), "doze horas"),
            ("pt-PT", (14, 30), dict(style="phrase", clock="12h", period=True),
             "duas e meia da tarde"),
            ("pt-PT", (18, 45), dict(style="phrase", clock="12h", period=True),
             "sete menos um quarto da tarde")]

    def test_times(self):
        for lang, clock, options, expected in self.ROWS:
            with self.subTest(lang=lang, clock=clock, options=options):
                self.assertEqual(spoken_time(lang, *clock, **options), expected)

    def test_unsupported_styles(self):
        for clock, options in [((14, 30, 5), {}),
                               ((14, 30), dict(style="phrase")),
                               ((14, 30, 5), dict(style="phrase", clock="12h")),
                               ((14, 30), dict(case="genitive"))]:
            with self.subTest(clock=clock, options=options):
                with self.assertRaises(UnsupportedForm):
                    spoken_time("pt-PT", *clock, **options)

    def test_bad_values(self):
        for clock, options in [((24, 0), {}), ((12, 60), {}),
                               ((12, 0, 60), dict(style="units")),
                               ((12, 0), dict(style="spoken")),
                               ((12, 0), dict(clock="13h")),
                               ((14, 0), dict(period=True))]:
            with self.subTest(clock=clock, options=options):
                with self.assertRaises(ValueError):
                    spoken_time("pt-PT", *clock, **options)


class TestSpokenYearPt(unittest.TestCase):
    def test_years(self):
        for year, expected in [(1, "um"), (2024, "dois mil e vinte e quatro"),
                               (9999, "nove mil novecentos e noventa e nove")]:
            with self.subTest(year=year):
                self.assertEqual(spoken_year("pt-PT", year), expected)

    def test_range(self):
        for year in (0, -5, 10000):
            with self.subTest(year=year):
                with self.assertRaises(ValueError):
                    spoken_year("pt-PT", year)

    def test_no_ordinal_case_or_declension(self):
        for options in (dict(ordinal=True), dict(case="genitive"),
                        dict(declension="weak")):
            with self.subTest(options=options):
                with self.assertRaises(UnsupportedForm):
                    spoken_year("pt-PT", 2024, **options)


if __name__ == "__main__":
    unittest.main()
