"""An ordinal word is a day of the month only before a month name.

Danish and Norwegian name several holidays with an ordinal: "første
juledag", "anden påskedag", "andre pinsedag". The da, nb and nn engines
turned every ordinal word into a digit and then read a lone digit as a clock
hour, so "første" alone answered 01:00 tomorrow and "første påskedag" answered
today. sproget.dk ("Den 101. dalmatiner", Politiken 23 January 2008): "Ordenstal
er talord, der angiver en plads i en rækkefølge ... De dertil svarende
mængdetal er talord, der angiver antallet af enheder i en mængde". A clock
hour is a quantity, not a place in a sequence.

Every expected date is counted by hand from the anchor, Sunday 27 September
2026: Easter 2027 falls on 28 March (Anonymous Gregorian computus) and
Pentecost 49 days later on 16 May.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 9, 27, 12, 0)


def _read(text, lang):
    return extract_datetime(text, lang=lang, anchorDate=ANCHOR)


class TestOrdinalHolidays(unittest.TestCase):
    def test_easter_and_pentecost_dates(self):
        for lang, text, day in (
                ("da-dk", "første påskedag", datetime(2027, 3, 28)),
                ("da-dk", "første pinsedag", datetime(2027, 5, 16)),
                ("nb-no", "første påskedag", datetime(2027, 3, 28)),
                ("nb-no", "første pinsedag", datetime(2027, 5, 16)),
                ("nn-no", "fyrste påskedag", datetime(2027, 3, 28)),
                ("nn-no", "fyrste pinsedag", datetime(2027, 5, 16))):
            with self.subTest(lang=lang, text=text):
                self.assertEqual(_read(text, lang)[0], day)

    def test_a_clock_beside_the_holiday(self):
        for lang, text in (("nb-no", "første påskedag klokken 10"),
                           ("nn-no", "fyrste påskedag klokka 10")):
            with self.subTest(lang=lang, text=text):
                self.assertEqual(tuple(_read(text, lang)),
                                 (datetime(2027, 3, 28, 10, 0), ""))

    def test_christmas_and_boxing_day_still_read(self):
        for lang, text, day in (
                ("da-dk", "første juledag", datetime(2026, 12, 25)),
                ("da-dk", "anden juledag", datetime(2026, 12, 26)),
                ("nb-no", "første juledag", datetime(2026, 12, 25)),
                ("nb-no", "andre juledag", datetime(2026, 12, 26))):
            with self.subTest(lang=lang, text=text):
                self.assertEqual(tuple(_read(text, lang)), (day, ""))


class TestLoneOrdinalIsNotADate(unittest.TestCase):
    def test_a_lone_ordinal(self):
        for lang, text in (("da-dk", "første"), ("da-dk", "anden"),
                           ("da-dk", "tredje"), ("nb-no", "første"),
                           ("nn-no", "fyrste")):
            with self.subTest(lang=lang, text=text):
                self.assertIsNone(_read(text, lang))

    def test_an_ordinal_before_a_noun(self):
        for lang, text in (("da-dk", "første gang"),
                           ("nb-no", "første gang")):
            with self.subTest(lang=lang, text=text):
                self.assertIsNone(_read(text, lang))


class TestOrdinalBeforeAMonth(unittest.TestCase):
    def test_the_day_of_the_month_still_reads(self):
        for lang, text, day in (
                ("da-dk", "første januar", datetime(2027, 1, 1)),
                ("da-dk", "første jan", datetime(2027, 1, 1)),
                ("da-dk", "tredje april klokken 10", datetime(2027, 4, 3, 10)),
                ("nb-no", "første januar", datetime(2027, 1, 1)),
                ("nn-no", "fyrste januar", datetime(2027, 1, 1))):
            with self.subTest(lang=lang, text=text):
                self.assertEqual(tuple(_read(text, lang)), (day, ""))
