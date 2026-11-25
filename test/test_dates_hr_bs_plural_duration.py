"""hr and bs duration and relative-time nouns follow the CLDR 49 plural
categories one, few and other, and a feminine unit takes jedna and dvije.

Noun forms: cldr-units-full/main/{hr,bs}/units.json, long duration-day,
-hour, -minute, -second. Plural rules: cldr-core supplemental/plurals.json
(one: i % 10 = 1 and i % 100 != 11; few: i % 10 = 2..4 and
i % 100 != 12..14; other: the rest). Minute and second are feminine in CLDR
hr duration units; bs is standard Bosnian, which agrees.
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
COUNTS = (1, 2, 4, 5, 11, 12, 14, 21, 22, 25, 101)
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


if __name__ == "__main__":
    unittest.main()
