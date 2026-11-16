"""The spoken form of an Italian date, clock time and year.

Expected values follow the rules quoted in the dates_it module docstring:
day 1 is "primo" and the other days are cardinals, with no "di" between the
fields (Crusca 86, quoting Serianni: "il primo febbraio duemilatré"); the
year is one cardinal word (Crusca 20176); the 24-hour clock reads "le diciotto
e trenta" and 0 as "zero" (Treccani "ora", "zero", "mezza"); the half is "e
mezza" (Crusca 48); the quarter before the hour is "meno un quarto" (Treccani
"quarto"); midnight and noon keep their words (Treccani "mezzanotte",
"mezzogiorno"); the day periods follow CLDR 49. The number words are those of
pronounce_number_it; the years 1108 and 1908 need its "centootto".
"""
import re
import unittest

from ovos_date_parser.spoken import (
    UnsupportedForm, spoken_date, spoken_time, spoken_year
)

WORDS = re.compile(r"^[a-zà-ú]+(?:['\- ][a-zà-ú]+)*$")


class TestSpokenDateIt(unittest.TestCase):
    ROWS = [(dict(day=1, month=5), "primo maggio"),
            (dict(day=1, month=2, year=2003), "primo febbraio duemilatré"),
            (dict(day=12, month=3, year=2024),
             "dodici marzo duemilaventiquattro"),
            (dict(day=17, month=3, year=1861),
             "diciassette marzo milleottocentosessantuno"),
            (dict(day=25, month=4, year=1945),
             "venticinque aprile millenovecentoquarantacinque"),
            (dict(day=2, month=6, year=1946, weekday=6),
             "domenica due giugno millenovecentoquarantasei"),
            (dict(day=21, month=1, year=2003, weekday=1),
             "martedì ventuno gennaio duemilatré"),
            (dict(day=8, month=9, year=1908),
             "otto settembre millenovecentootto"),
            (dict(day=29, month=2), "ventinove febbraio"),
            (dict(day=1), "primo"),
            (dict(day=3), "tre"),
            (dict(month=3), "marzo"),
            (dict(month=3, year=2024), "marzo duemilaventiquattro"),
            (dict(year=1999), "millenovecentonovantanove")]

    def test_dates(self):
        for fields, expected in self.ROWS:
            with self.subTest(fields=fields):
                self.assertEqual(spoken_date("it", **fields), expected)

    def test_words_only(self):
        for fields, _ in self.ROWS:
            out = spoken_date("it", **fields)
            with self.subTest(out=out):
                self.assertRegex(out, WORDS)

    def test_sentences(self):
        self.assertEqual(
            f"Il {spoken_date('it', day=1, month=5)} è festa.",
            "Il primo maggio è festa.")
        self.assertEqual(
            f"L'Italia fu proclamata il "
            f"{spoken_date('it', day=17, month=3, year=1861)}.",
            "L'Italia fu proclamata il diciassette marzo "
            "milleottocentosessantuno.")

    def test_months_and_weekdays(self):
        months = [spoken_date("it", month=m) for m in range(1, 13)]
        self.assertEqual(months, [
            "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
            "luglio", "agosto", "settembre", "ottobre", "novembre",
            "dicembre"])
        # 4 January 2021 is a Monday
        days = [spoken_date("it", day=4 + d, month=1, year=2021, weekday=d)
                for d in range(7)]
        self.assertEqual([d.split()[0] for d in days], [
            "lunedì", "martedì", "mercoledì", "giovedì", "venerdì",
            "sabato", "domenica"])

    def test_region_tags(self):
        for lang in ("it", "it-IT", "it-CH", "it_IT", "IT"):
            with self.subTest(lang=lang):
                self.assertEqual(spoken_date(lang, day=1, month=5),
                                 "primo maggio")

    def test_impossible_dates(self):
        for fields in [dict(day=31, month=2), dict(day=29, month=2, year=2023),
                       dict(day=32), dict(month=13), dict(day=12, year=2024),
                       dict(day=12, month=3, year=2024, weekday=0), {}]:
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):
                    spoken_date("it", **fields)

    def test_no_case_in_italian(self):
        with self.assertRaises(UnsupportedForm):
            spoken_date("it", day=1, month=5, case="genitive")
        with self.assertRaises(UnsupportedForm):
            spoken_date("it", day=1, month=5, declension="weak")


class TestSpokenTimeIt(unittest.TestCase):
    P12 = dict(clock="12h", period=True)
    PHRASE = dict(style="phrase", clock="12h", period=True)
    ROWS = [((14, 30), {}, "quattordici e trenta"),
            ((18, 0), {}, "diciotto"),
            ((1, 0), {}, "una"),
            ((21, 0), {}, "ventuno"),
            ((0, 0), {}, "zero"),
            ((0, 30), {}, "zero e trenta"),
            ((9, 5), {}, "nove e cinque"),
            ((23, 59), {}, "ventitré e cinquantanove"),
            ((14, 30), dict(style="units"), "quattordici ore e trenta minuti"),
            ((1, 0), dict(style="units"), "un'ora"),
            ((1, 1), dict(style="units"), "un'ora e un minuto"),
            ((21, 0), dict(style="units"), "ventuno ore"),
            ((0, 0), dict(style="units"), "zero ore"),
            ((20, 30, 24), dict(style="units"),
             "venti ore trenta minuti e ventiquattro secondi"),
            ((20, 0, 1), dict(style="units"), "venti ore e un secondo"),
            ((14, 30), dict(clock="12h"), "due e trenta"),
            ((14, 0), P12, "due del pomeriggio"),
            ((0, 30), dict(clock="12h"), "dodici e trenta"),
            ((0, 30), P12, "dodici e trenta di notte"),
            ((0, 0), P12, "mezzanotte"),
            ((12, 0), P12, "mezzogiorno"),
            ((12, 0), dict(clock="12h"), "dodici"),
            ((8, 15), P12, "otto e quindici di mattina"),
            ((5, 59), P12, "cinque e cinquantanove di notte"),
            ((6, 0), P12, "sei di mattina"),
            ((17, 59), P12, "cinque e cinquantanove del pomeriggio"),
            ((18, 0), P12, "sei di sera"),
            ((19, 5), P12, "sette e cinque di sera"),
            ((14, 30), PHRASE, "due e mezza del pomeriggio"),
            ((8, 15), PHRASE, "otto e un quarto di mattina"),
            ((8, 30), PHRASE, "otto e mezza di mattina"),
            ((17, 45), PHRASE, "sei meno un quarto del pomeriggio"),
            ((9, 40), PHRASE, "nove e quaranta di mattina"),
            ((13, 0), PHRASE, "una del pomeriggio"),
            ((1, 30), PHRASE, "una e mezza di notte"),
            ((12, 15), PHRASE, "mezzogiorno e un quarto"),
            ((0, 30), PHRASE, "mezzanotte e mezza"),
            ((11, 45), PHRASE, "mezzogiorno meno un quarto"),
            ((23, 45), PHRASE, "mezzanotte meno un quarto"),
            ((14, 30), dict(style="phrase", clock="12h"), "due e mezza"),
            ((12, 30), dict(style="phrase", clock="12h"), "dodici e mezza")]

    def test_times(self):
        for clock, options, expected in self.ROWS:
            with self.subTest(clock=clock, options=options):
                self.assertEqual(spoken_time("it", *clock, **options),
                                 expected)

    def test_words_only(self):
        for clock, options, _ in self.ROWS:
            out = spoken_time("it", *clock, **options)
            with self.subTest(out=out):
                self.assertRegex(out, WORDS)

    def test_sentences(self):
        self.assertEqual(
            f"Sono le {spoken_time('it', 20, 30)} e il treno è in ritardo.",
            "Sono le venti e trenta e il treno è in ritardo.")
        self.assertEqual(
            f"Ci vediamo alle {spoken_time('it', 8, 30, **dict(style='phrase', clock='12h'))}.",
            "Ci vediamo alle otto e mezza.")

    def test_unsupported_styles(self):
        for clock, options in [((14, 30, 5), {}),
                               ((14, 30), dict(style="phrase")),
                               ((14, 30, 5), dict(style="phrase", clock="12h")),
                               ((14, 30), dict(case="genitive"))]:
            with self.subTest(clock=clock, options=options):
                with self.assertRaises(UnsupportedForm):
                    spoken_time("it", *clock, **options)

    def test_bad_values(self):
        for clock, options in [((24, 0), {}), ((12, 60), {}),
                               ((12, 0, 60), dict(style="units")),
                               ((12, 0), dict(style="spoken")),
                               ((12, 0), dict(clock="13h")),
                               ((14, 0), dict(period=True))]:
            with self.subTest(clock=clock, options=options):
                with self.assertRaises(ValueError):
                    spoken_time("it", *clock, **options)

    def test_every_minute_is_words(self):
        for hour in range(24):
            for minute in range(60):
                for style, clock in (("digits", "24h"), ("units", "24h"),
                                     ("digits", "12h"), ("phrase", "12h")):
                    out = spoken_time("it", hour, minute, style=style,
                                      clock=clock, period=clock == "12h")
                    self.assertRegex(out, WORDS)


class TestSpokenYearIt(unittest.TestCase):
    def test_years(self):
        for year, expected in [
                (1, "uno"), (1008, "milleotto"), (1108, "millecentootto"),
                (1861, "milleottocentosessantuno"),
                (1908, "millenovecentootto"),
                (1999, "millenovecentonovantanove"),
                (2003, "duemilatré"), (2008, "duemilaotto"),
                (2024, "duemilaventiquattro"),
                (9999, "novemilanovecentonovantanove")]:
            with self.subTest(year=year):
                self.assertEqual(spoken_year("it", year), expected)

    def test_range(self):
        for year in (0, -5, 10000):
            with self.subTest(year=year):
                with self.assertRaises(ValueError):
                    spoken_year("it", year)

    def test_no_ordinal_case_or_declension(self):
        for options in (dict(ordinal=True), dict(case="genitive"),
                        dict(declension="weak")):
            with self.subTest(options=options):
                with self.assertRaises(UnsupportedForm):
                    spoken_year("it", 2024, **options)

    def test_every_year_is_one_word(self):
        for year in range(1, 10000):
            self.assertRegex(spoken_year("it", year), r"^[a-zà-ú]+$")


if __name__ == "__main__":
    unittest.main()
