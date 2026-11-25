"""hr and bs duration and relative-time nouns follow the CLDR 49 plural
categories one, few and other, and a feminine unit takes jedna and dvije.

Noun forms: cldr-units-full/main/{hr,bs}/units.json, long duration-day,
-hour, -minute, -second. Plural rules: cldr-core supplemental/plurals.json
(one: i % 10 = 1 and i % 100 != 11; few: i % 10 = 2..4 and
i % 100 != 12..14; other: the rest). The rule for a number with visible
fraction digits is the same test on f, the fraction digits as an integer: one
is f % 10 = 1 and f % 100 != 11, few is f % 10 = 2..4 and f % 100 != 12..14.
Minute and second are feminine in CLDR hr duration units; bs is standard
Bosnian, which agrees.
"""
import datetime
import unittest

from ovos_number_parser import pronounce_number

from ovos_date_parser import nice_duration, nice_relative_time

FORMS = {
    "day": ("dan", "dana", "dana"),
    "hour": ("sat", "sata", "sati"),
    "minute": ("minuta", "minute", "minuta"),
    "second": ("sekunda", "sekunde", "sekundi"),
}
SECONDS = {"day": 86400, "hour": 3600, "minute": 60, "second": 1}
FEMININE = {"minute": {"jedan": "jedna", "dva": "dvije"},
            "second": {"jedan": "jedna", "dva": "dvije"}}
COUNTS = (1, 2, 4, 5, 11, 12, 13, 14, 21, 22, 25, 101, 113)
NOW = datetime.datetime(2025, 1, 1, 12, 0, 0)


def category(n):
    if n % 10 == 1 and n % 100 != 11:
        return 0
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return 1
    return 2


def phrase(n, unit, lang):
    words = pronounce_number(n, lang).split(" ")
    words[-1] = FEMININE.get(unit, {}).get(words[-1], words[-1])
    return " ".join(words) + " " + FORMS[unit][category(n)]

#: seconds, then the noun by the CLDR fraction rule worked by hand: the
#: fraction digits of 2.2 are f = 2 (few), of 1.5 f = 5 (other), of 11.1 f = 1
#: (one), and a whole number 12.0 is read as 12 (other)
FRACTIONS = ((2.2, "sekunde"), (3.3, "sekunde"), (21.4, "sekunde"),
             (1.5, "sekundi"), (1.1, "sekunda"), (11.1, "sekunda"),
             (12.0, "sekundi"), (1.12, "sekundi"), (2.11, "sekundi"),
             (1.25, "sekundi"), (4.14, "sekundi"), (1.11, "sekundi"), (1.31, "sekunda"),
             (5.011, "sekundi"), (1.001, "sekunda"))


class TestCroatianBosnianPlurals(unittest.TestCase):
    def test_issue_examples(self):
        for lang in ("hr", "bs"):
            self.assertEqual(nice_duration(18000, lang=lang), "pet sati")
            self.assertEqual(nice_duration(300, lang=lang), "pet minuta")
            self.assertEqual(nice_duration(120, lang=lang), "dvije minute")
            self.assertEqual(nice_duration(1260, lang=lang),
                             "dvadeset jedna minuta")
            self.assertEqual(nice_duration(1320, lang=lang),
                             "dvadeset dvije minute")
            self.assertEqual(nice_duration(7200, lang=lang), "dva sata")
            self.assertEqual(nice_duration(1, lang=lang), "jedna sekunda")
            self.assertEqual(nice_duration(86400, lang=lang), "jedan dan")

    def test_duration_every_unit(self):
        for lang in ("hr", "bs"):
            for unit, size in SECONDS.items():
                for n in COUNTS:
                    if (unit in ("minute", "second") and n >= 60) or \
                            (unit == "hour" and n >= 24):
                        continue
                    with self.subTest(lang=lang, unit=unit, n=n):
                        self.assertEqual(nice_duration(n * size, lang=lang),
                                         phrase(n, unit, lang))

    def test_relative_time_every_unit(self):
        for lang in ("hr", "bs"):
            for unit, size in SECONDS.items():
                for n in COUNTS:
                    # a count reads as the unit only below 90 s, 90 min and 36 h
                    if (unit in ("minute", "second") and n >= 90) or \
                            (unit == "hour" and n >= 36):
                        continue
                    # one minute reads as 60 seconds and one hour as 60 minutes
                    if n == 1 and unit != "second" and unit != "day":
                        continue
                    if unit == "day" and n * 24 < 36:
                        continue
                    when = NOW + datetime.timedelta(seconds=n * size)
                    with self.subTest(lang=lang, unit=unit, n=n):
                        self.assertEqual(nice_relative_time(when, NOW, lang=lang),
                                         phrase(n, unit, lang))

    def test_fractional_seconds_take_the_fraction_noun(self):
        for lang in ("hr", "bs"):
            for seconds, noun in FRACTIONS:
                when = NOW + datetime.timedelta(seconds=seconds)
                with self.subTest(lang=lang, seconds=seconds):
                    self.assertEqual(nice_relative_time(when, NOW, lang=lang),
                                     f"{pronounce_number(seconds, lang)} {noun}")

    def test_fractional_count_keeps_the_numerals_of_pronounce_number(self):
        when = NOW + datetime.timedelta(seconds=1.1)
        self.assertEqual(nice_relative_time(when, NOW, lang="hr"),
                         "jedan zarez jedan sekunda")
        when = NOW + datetime.timedelta(seconds=2.2)
        self.assertEqual(nice_relative_time(when, NOW, lang="hr"),
                         "dva zarez dva sekunde")
        # the whole number 12.0 and 1.0 are spoken as integers and agree
        for seconds, spoken in ((12.0, "dvanaest sekundi"),
                                (1.0, "jedna sekunda"),
                                (2.0, "dvije sekunde")):
            when = NOW + datetime.timedelta(seconds=seconds)
            for lang in ("hr", "bs"):
                with self.subTest(lang=lang, seconds=seconds):
                    self.assertEqual(nice_relative_time(when, NOW, lang=lang),
                                     spoken)


if __name__ == "__main__":
    unittest.main()
