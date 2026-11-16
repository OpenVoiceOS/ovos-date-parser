"""The spoken form of a Dutch date, clock time and year.

Expected values follow the rules quoted in the dates_nl module docstring:
the year reads as a honderdtal before 2000 and with "tweeduizend" after it,
with a space after "duizend" (Taaladvies.net, "Uitspraak 2020" and
"Jaartallen voluit": 1250 "twaalfhonderdvijftig", 1694
"zestienhonderdvierennegentig", 1914 "negentienhonderdveertien", 2020
"tweeduizend twintig", 3025 "drieduizend vijfentwintig"); the date is day,
month, year with cardinal days (Onze Taal, "Datumnotatie"); the digital clock
reads "acht uur zeventien" and "zestien uur vijftig" (Taaladvies.net,
"Kloktijden"); the 12-hour phrase divides the hour in four, with the examples
8.07 "zeven over acht", 8.17 "dertien voor halfnegen", 8.20 "tien voor
halfnegen", 8.38 "acht over halfnegen", 8.40 "tien over halfnegen", 8.49 "elf
voor negen" and 8.52 "acht voor negen"; the day periods follow CLDR 49. The
gold values are written by hand; the sweeps use the oracle in this file.
"""
import re
import unittest
from datetime import datetime

from ovos_date_parser import nice_date

from ovos_date_parser.spoken import (
    UnsupportedForm, spoken_date, spoken_time, spoken_year
)

WORDS = re.compile(r"^'?[a-zà-ú]+(?: '?[a-zà-ú]+)*$")
PHRASE = dict(style="phrase", clock="12h")
PHRASE_P = dict(style="phrase", clock="12h", period=True)
P12 = dict(clock="12h", period=True)


class TestSpokenYearNl(unittest.TestCase):
    ROWS = [(1, "één"), (66, "zesenzestig"), (537, "vijfhonderdzevenendertig"),
            (999, "negenhonderdnegenennegentig"),
            (1000, "duizend"), (1066, "duizend zesenzestig"),
            (1099, "duizend negenennegentig"),
            (1100, "elfhonderd"), (1204, "twaalfhonderdvier"),
            (1250, "twaalfhonderdvijftig"),
            (1492, "veertienhonderdtweeënnegentig"),
            (1694, "zestienhonderdvierennegentig"),
            (1900, "negentienhonderd"), (1901, "negentienhonderdeen"),
            (1914, "negentienhonderdveertien"),
            (1940, "negentienhonderdveertig"),
            (1993, "negentienhonderddrieënnegentig"),
            (1998, "negentienhonderdachtennegentig"),
            (1999, "negentienhonderdnegenennegentig"),
            (2000, "tweeduizend"), (2001, "tweeduizend één"),
            (2006, "tweeduizend zes"), (2012, "tweeduizend twaalf"),
            (2020, "tweeduizend twintig"),
            (2022, "tweeduizend tweeëntwintig"),
            (2023, "tweeduizend drieëntwintig"),
            (2026, "tweeduizend zesentwintig"),
            (3025, "drieduizend vijfentwintig"),
            (7002, "zevenduizend twee"),
            (9999, "negenduizend negenhonderdnegenennegentig")]

    def test_years(self):
        for year, expected in self.ROWS:
            with self.subTest(year=year):
                self.assertEqual(spoken_year("nl-NL", year), expected)

    def test_every_year_against_the_oracle(self):
        for year in range(1, 10000):
            with self.subTest(year=year):
                self.assertEqual(spoken_year("nl", year), year_oracle(year))

    def test_range(self):
        for year in (0, -5, 10000):
            with self.subTest(year=year):
                with self.assertRaises(ValueError):
                    spoken_year("nl", year)

    def test_no_ordinal_case_or_declension(self):
        for options in (dict(ordinal=True), dict(case="genitive"),
                        dict(declension="weak")):
            with self.subTest(options=options):
                with self.assertRaises(UnsupportedForm):
                    spoken_year("nl", 2024, **options)


class TestSpokenDateNl(unittest.TestCase):
    ROWS = [(dict(day=25, month=12, year=2023),
             "vijfentwintig december tweeduizend drieëntwintig"),
            (dict(day=1, month=5), "één mei"),
            (dict(day=1, month=5, year=2025), "één mei tweeduizend vijfentwintig"),
            (dict(day=9, month=11, year=1989),
             "negen november negentienhonderdnegenentachtig"),
            (dict(day=14, month=4, year=2011),
             "veertien april tweeduizend elf"),
            (dict(day=28, month=10, year=1975),
             "achtentwintig oktober negentienhonderdvijfenzeventig"),
            (dict(day=22, month=2, year=2022, weekday=1),
             "dinsdag tweeëntwintig februari tweeduizend tweeëntwintig"),
            (dict(day=31, month=1), "eenendertig januari"),
            (dict(day=29, month=2), "negenentwintig februari"),
            (dict(day=3), "drie"),
            (dict(month=3), "maart"),
            (dict(month=3, year=2024), "maart tweeduizend vierentwintig"),
            (dict(year=1999), "negentienhonderdnegenennegentig")]

    def test_dates(self):
        for fields, expected in self.ROWS:
            with self.subTest(fields=fields):
                self.assertEqual(spoken_date("nl", **fields), expected)

    def test_words_only(self):
        for fields, _ in self.ROWS:
            out = spoken_date("nl", **fields)
            with self.subTest(out=out):
                self.assertRegex(out, WORDS)

    def test_sentences(self):
        self.assertEqual(
            f"Het is {spoken_date('nl', day=25, month=12, year=2023)}.",
            "Het is vijfentwintig december tweeduizend drieëntwintig.")

    def test_names_are_the_nice_date_table(self):
        for month in range(1, 13):
            word = spoken_date("nl", month=month)
            self.assertIn(word, re.findall(r"[^\s,]+", nice_date(
                datetime(2024, month, 1), "nl", include_weekday=False)))
        for weekday in range(7):
            word = spoken_date("nl", day=1 + weekday, month=1, year=2024,
                               weekday=weekday).split()[0]
            self.assertIn(word, re.findall(r"[^\s,]+", nice_date(
                datetime(2024, 1, 1 + weekday), "nl")))

    def test_months_and_weekdays(self):
        months = [spoken_date("nl", month=m) for m in range(1, 13)]
        self.assertEqual(months, [
            "januari", "februari", "maart", "april", "mei", "juni", "juli",
            "augustus", "september", "oktober", "november", "december"])
        # 4 January 2021 is a Monday
        days = [spoken_date("nl", day=4 + d, month=1, year=2021, weekday=d)
                for d in range(7)]
        self.assertEqual([d.split()[0] for d in days], [
            "maandag", "dinsdag", "woensdag", "donderdag", "vrijdag",
            "zaterdag", "zondag"])

    def test_every_day_of_a_leap_year(self):
        for month, days in enumerate(
                (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31), 1):
            for day in range(1, days + 1):
                out = spoken_date("nl", day=day, month=month, year=2024)
                with self.subTest(day=day, month=month):
                    self.assertEqual(out, " ".join((
                        year_oracle(day) if day != 1 else "één",
                        MONTHS[month - 1], year_oracle(2024))))

    def test_region_tags(self):
        for lang in ("nl", "nl-NL", "nl-BE", "nl-SR", "nl_NL", "NL"):
            with self.subTest(lang=lang):
                self.assertEqual(spoken_date(lang, day=1, month=5),
                                 "één mei")

    def test_impossible_dates(self):
        for fields in [dict(day=31, month=2), dict(day=29, month=2, year=2023),
                       dict(day=32), dict(month=13), dict(day=12, year=2024),
                       dict(day=12, month=3, year=2024, weekday=0), {}]:
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):
                    spoken_date("nl", **fields)

    def test_no_case_in_dutch(self):
        with self.assertRaises(UnsupportedForm):
            spoken_date("nl", day=1, month=5, case="genitive")
        with self.assertRaises(UnsupportedForm):
            spoken_date("nl", day=1, month=5, declension="weak")


class TestSpokenTimeNl(unittest.TestCase):
    ROWS = [((8, 17), {}, "acht uur zeventien"),
            ((16, 50), {}, "zestien uur vijftig"),
            ((8, 37), {}, "acht uur zevenendertig"),
            ((8, 57), {}, "acht uur zevenenvijftig"),
            ((14, 0), {}, "veertien uur"),
            ((12, 0), {}, "twaalf uur"),
            ((18, 0), {}, "achttien uur"),
            ((1, 0), {}, "één uur"),
            ((0, 0), {}, "nul uur"),
            ((0, 30), {}, "nul uur dertig"),
            ((9, 5), {}, "negen uur vijf"),
            ((23, 59), {}, "drieëntwintig uur negenenvijftig"),
            ((14, 30), dict(clock="12h"), "twee uur dertig"),
            ((14, 0), P12, "twee uur 's middags"),
            ((12, 0), P12, "twaalf uur 's middags"),
            ((0, 0), P12, "middernacht"),
            ((0, 30), P12, "twaalf uur dertig 's nachts"),
            ((5, 59), P12, "vijf uur negenenvijftig 's nachts"),
            ((6, 0), P12, "zes uur 's ochtends"),
            ((17, 59), P12, "vijf uur negenenvijftig 's middags"),
            ((18, 0), P12, "zes uur 's avonds"),
            ((8, 7), PHRASE, "zeven over acht"),
            ((8, 13), PHRASE, "dertien over acht"),
            ((8, 15), PHRASE, "kwart over acht"),
            ((8, 17), PHRASE, "dertien voor halfnegen"),
            ((8, 20), PHRASE, "tien voor halfnegen"),
            ((8, 30), PHRASE, "halfnegen"),
            ((8, 38), PHRASE, "acht over halfnegen"),
            ((8, 40), PHRASE, "tien over halfnegen"),
            ((8, 45), PHRASE, "kwart voor negen"),
            ((8, 49), PHRASE, "elf voor negen"),
            ((8, 52), PHRASE, "acht voor negen"),
            ((8, 0), PHRASE, "acht uur"),
            ((19, 30), PHRASE, "halfacht"),
            ((19, 30), PHRASE_P, "halfacht 's avonds"),
            ((12, 30), PHRASE, "halfeen"),
            ((11, 45), PHRASE, "kwart voor twaalf"),
            ((12, 45), PHRASE, "kwart voor één"),
            ((13, 0), PHRASE, "één uur"),
            ((1, 7), PHRASE, "zeven over één"),
            ((0, 0), PHRASE_P, "middernacht"),
            ((12, 0), PHRASE_P, "twaalf uur 's middags"),
            ((23, 45), PHRASE_P, "kwart voor twaalf 's avonds"),
            ((14, 15), PHRASE_P, "kwart over twee 's middags")]

    def test_times(self):
        for clock, options, expected in self.ROWS:
            with self.subTest(clock=clock, options=options):
                self.assertEqual(spoken_time("nl", *clock, **options),
                                 expected)

    def test_words_only(self):
        for clock, options, _ in self.ROWS:
            out = spoken_time("nl", *clock, **options)
            with self.subTest(out=out):
                self.assertRegex(out, WORDS)

    def test_sentences(self):
        self.assertEqual(
            f"Er is een tram om {spoken_time('nl', 8, 17)}.",
            "Er is een tram om acht uur zeventien.")
        self.assertEqual(
            f"Ik kom om {spoken_time('nl', 19, 30, **PHRASE)}.",
            "Ik kom om halfacht.")

    def test_every_phrase_against_the_oracle(self):
        for hour in range(24):
            for minute in range(60):
                with self.subTest(hour=hour, minute=minute):
                    self.assertEqual(
                        spoken_time("nl", hour, minute, **PHRASE),
                        phrase_oracle(hour % 12 or 12, minute))

    def test_every_digital_reading_against_the_oracle(self):
        for hour in range(24):
            for minute in range(60):
                expected = f"{NUMBERS[hour]} uur" + (
                    f" {NUMBERS[minute]}" if minute else "")
                with self.subTest(hour=hour, minute=minute):
                    self.assertEqual(spoken_time("nl", hour, minute),
                                     expected)

    def test_every_minute_is_words(self):
        for hour in range(24):
            for minute in range(60):
                for style, clock in (("digits", "24h"), ("digits", "12h"),
                                     ("phrase", "12h")):
                    out = spoken_time("nl", hour, minute, style=style,
                                      clock=clock, period=clock == "12h")
                    self.assertRegex(out, WORDS)

    def test_unsupported_styles(self):
        for clock, options in [((14, 30, 5), {}),
                               ((14, 30), dict(style="phrase")),
                               ((14, 30, 5), dict(style="phrase", clock="12h")),
                               ((14, 30), dict(style="units")),
                               ((13, 0), dict(style="units", clock="12h",
                                              period=True)),
                               ((20, 30, 24), dict(style="units")),
                               ((14, 30), dict(case="genitive"))]:
            with self.subTest(clock=clock, options=options):
                with self.assertRaises(UnsupportedForm):
                    spoken_time("nl", *clock, **options)

    def test_bad_values(self):
        for clock, options in [((24, 0), {}), ((12, 60), {}),
                               ((12, 0), dict(style="spoken")),
                               ((12, 0), dict(clock="13h")),
                               ((14, 0), dict(period=True))]:
            with self.subTest(clock=clock, options=options):
                with self.assertRaises(ValueError):
                    spoken_time("nl", *clock, **options)


MONTHS = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
          "augustus", "september", "oktober", "november", "december"]
UNITS = ["nul", "één", "twee", "drie", "vier", "vijf", "zes", "zeven", "acht",
         "negen", "tien", "elf", "twaalf", "dertien", "veertien", "vijftien",
         "zestien", "zeventien", "achttien", "negentien"]
TENS = {2: "twintig", 3: "dertig", 4: "veertig", 5: "vijftig", 6: "zestig",
        7: "zeventig", 8: "tachtig", 9: "negentig"}


def number_below_100(n):
    if n < 20:
        return UNITS[n]
    if n % 10 == 0:
        return TENS[n // 10]
    unit = "een" if n % 10 == 1 else UNITS[n % 10]
    return unit + ("ën" if n % 10 in (2, 3) else "en") + TENS[n // 10]


NUMBERS = [number_below_100(n) for n in range(60)]


def below_1000(n):
    hundreds, rest = divmod(n, 100)
    words = ""
    if hundreds:
        words = ("" if hundreds == 1 else UNITS[hundreds]) + "honderd"
    if rest:
        words += "een" if words and rest == 1 else number_below_100(rest)
    return words


def year_oracle(year):
    if year < 1000:
        return below_1000(year) if year > 99 else number_below_100(year)
    if year < 1100:
        return "duizend" + (" " + number_below_100(year - 1000)
                            if year > 1000 else "")
    if year < 2000:
        return number_below_100(year // 100) + "honderd" + (
            "" if year % 100 == 0 else "een" if year % 100 == 1
            else number_below_100(year % 100))
    thousands = number_below_100(year // 1000) + "duizend"
    return thousands + (" " + below_1000(year % 1000) if year % 1000 else "")


def phrase_oracle(hour, minute):
    """The four-part division of the hour, with the 12-hour numbers."""
    this, following = NUMBERS[hour], NUMBERS[hour % 12 + 1]
    half = "half" + ("een" if following == "één" else following)
    if minute == 0:
        return this + " uur"
    if minute <= 14:
        return f"{NUMBERS[minute]} over {this}"
    if minute == 15:
        return f"kwart over {this}"
    if minute <= 29:
        return f"{NUMBERS[30 - minute]} voor {half}"
    if minute == 30:
        return half
    if minute <= 44:
        return f"{NUMBERS[minute - 30]} over {half}"
    if minute == 45:
        return f"kwart voor {following}"
    return f"{NUMBERS[60 - minute]} voor {following}"


if __name__ == "__main__":
    unittest.main()
