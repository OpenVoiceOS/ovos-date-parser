"""Punctuation written against the last word of a date or time expression.

The per-language engines split on whitespace, so "8," reached them as a word
that is not a clock. Each row names the date and leftover text the sentence
reads to once the punctuation is a word of its own.
"""
import itertools
import unittest
from datetime import date, datetime, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

import ovos_date_parser as _odp

# 2026-01-05 is a Monday
ANCHOR = datetime(2026, 1, 5, 6, 0)


def read(lang, text):
    return _odp.extract_datetime(text, lang, anchorDate=ANCHOR)


class TestPunctuationAfterExpression(unittest.TestCase):
    # (lang, text, datetime, leftover)
    ROWS = [
        ("en-us", "wake me at eight thirty, please",
         datetime(2026, 1, 5, 8, 30), "wake me please"),
        ("en-us", "remind me at 8 pm; thanks",
         datetime(2026, 1, 5, 20, 0), "remind me thanks"),
        ("en-us", "remind me at 8 pm! ok",
         datetime(2026, 1, 5, 20, 0), "remind me ok"),
        ("en-us", '"remind me at 8 pm" thanks',
         datetime(2026, 1, 5, 20, 0), "remind me thanks"),
        ("en-us", "remind me on friday; thanks",
         datetime(2026, 1, 9), "remind me thanks"),
        ("en-us", "remind me on december 25th! ok",
         datetime(2026, 12, 25), "remind me ok"),
        ("en-us", "remind me at eight thirty. thanks",
         datetime(2026, 1, 5, 8, 30), "remind me thanks"),
        ("pt-pt", "lembra-me às 8 horas: por favor",
         datetime(2026, 1, 5, 8, 0), "lembra-me por favor"),
        ("pt-pt", "lembra-me (às 8 horas) por favor",
         datetime(2026, 1, 5, 8, 0), "lembra-me por favor"),
        ("pt-pt", "lembra-me (dia 25 de dezembro) por favor",
         datetime(2026, 12, 25), "lembra-me por favor"),
        ("es-es", "despiértame a las 8, por favor",
         datetime(2026, 1, 5, 8, 0), "despiértame por favor"),
        ("es-es", "despiértame a las ocho, por favor",
         datetime(2026, 1, 5, 8, 0), "despiértame por favor"),
        ("es-es", "despiértame mañana a las 8, por favor",
         datetime(2026, 1, 6, 8, 0), None),
        ("es-es", "recuérdame a las ocho; gracias",
         datetime(2026, 1, 5, 8, 0), "recuérdame gracias"),
        ("gl-es", "espértame ás 8, por favor",
         datetime(2026, 1, 5, 8, 0), "espértame por favor"),
        ("gl-es", "espértame ás oito, por favor",
         datetime(2026, 1, 5, 8, 0), "espértame por favor"),
        ("gl-es", "espértame mañá ás 8, por favor",
         datetime(2026, 1, 6, 8, 0), None),
        ("fr-fr", "rappelle-moi à 8 heures; merci",
         datetime(2026, 1, 5, 8, 0), "rappelle-moi merci"),
        ("fr-fr", "rappelle-moi demain à 8 heures! ok",
         datetime(2026, 1, 6, 8, 0), None),
        ("fr-fr", "rappelle-moi lundi! ok",
         datetime(2026, 1, 5), "rappelle-moi ok"),
        ("fr-fr", "rappelle-moi le 25 décembre; merci",
         datetime(2026, 12, 25), "rappelle-moi merci"),
        ("de-de", "weck mich um 8 uhr, bitte",
         datetime(2026, 1, 5, 8, 0), "weck mich bitte"),
        ("de-de", "weck mich um acht uhr, bitte",
         datetime(2026, 1, 5, 8, 0), "weck mich bitte"),
        ("de-de", "weck mich morgen um 8 uhr, bitte",
         datetime(2026, 1, 6, 8, 0), None),
        ("de-de", "erinnere mich am montag, danke",
         datetime(2026, 1, 5), "erinnere mich danke"),
        ("it-it", "ricordamelo venerdì: grazie",
         datetime(2026, 1, 9), "ricordamelo grazie"),
        ("it-it", "ricordamelo domani: grazie",
         datetime(2026, 1, 6), "ricordamelo grazie"),
        ("it-it", "ricordamelo (il 25 dicembre) grazie",
         datetime(2026, 12, 25), "ricordamelo grazie"),
    ]

    def test_punctuation_does_not_hide_the_expression(self):
        for lang, text, moment, leftover in self.ROWS:
            with self.subTest(lang=lang, text=text):
                found = read(lang, text)
                self.assertIsNotNone(found)
                self.assertEqual(found[0], moment)
                if leftover is not None:
                    self.assertEqual(found[1], leftover)


class TestCommaBeforePartOfDay(unittest.TestCase):
    """A comma before the part of the day keeps the evening hour."""

    EXACT = [
        ("es-es", "despiértame a las 9, de la noche, por favor",
         datetime(2026, 1, 5, 21, 0)),
        ("es-es", "recuérdame llamar a las nueve, de la noche",
         datetime(2026, 1, 5, 21, 0)),
        ("es-es", "mañana a las 9, de la noche", datetime(2026, 1, 6, 21, 0)),
        ("es-es", "el martes a las 9, de la noche",
         datetime(2026, 1, 6, 21, 0)),
        ("es-es", "a las 9, esta noche", datetime(2026, 1, 5, 21, 0)),
        ("es-es", "a las 9, por la noche", datetime(2026, 1, 5, 21, 0)),
    ]
    # the engine reads these as 21:00 and 22:00, not 22:00 and 21:00
    EVENING = [
        ("es-es", "pon una alarma a las 10, de la noche"),
        ("ca-es", "a les 9, del vespre"),
    ]

    def test_exact_evening_hour(self):
        for lang, text, moment in self.EXACT:
            with self.subTest(lang=lang, text=text):
                self.assertEqual(read(lang, text)[0], moment)

    def test_evening_not_morning(self):
        for lang, text in self.EVENING:
            with self.subTest(lang=lang, text=text):
                moment = read(lang, text)[0]
                self.assertEqual(moment.date(), date(2026, 1, 5))
                self.assertGreaterEqual(moment.hour, 21)


class TestSeparatedReadingIsChosenWithCare(unittest.TestCase):
    def test_a_lone_comma_does_not_move_the_weekday(self):
        # gl reads "o mercores, pasado mañá" as Wednesday only while the
        # comma stays glued; apart, the engine moves it two days on
        self.assertEqual(read("gl-es", "o mercores, pasado mañá")[0],
                         datetime(2026, 1, 7))

    def test_a_clause_that_disagrees_keeps_the_text_as_written(self):
        # "klokken tre" alone is 03:00; with a word after it the engine
        # drops the time, so the separated reading is not taken
        self.assertIsNone(read("da", "klokken tre, tak"))

    def test_an_abbreviation_dot_is_not_a_sentence_end(self):
        # "dec ." is read as December 1st and loses the "3"
        found = read("en-us", "remind me on dec. 3 thanks")
        self.assertTrue(found is None or found[0].date() != date(2026, 12, 1))


class TestCountBeforeComma(unittest.TestCase):
    """A count before a comma is not an hour."""

    ROWS = [
        ("es-es", "mañana necesito 5, gracias", datetime(2026, 1, 6)),
        ("es-es", "recuérdame mañana comprar 2, gracias",
         datetime(2026, 1, 6)),
        ("es-es", "el martes somos 4, vale", datetime(2026, 1, 6)),
        ("es-es", "mañana en la sala 4, por favor", datetime(2026, 1, 6)),
        ("es-es", "el viernes es el número 7, gracias",
         datetime(2026, 1, 9)),
        ("es-es", "mañana compra 3, por favor", datetime(2026, 1, 6)),
        ("gl-es", "mañá compra 3, por favor", datetime(2026, 1, 6)),
        ("ca-es", "demà compra 3, si us plau", datetime(2026, 1, 6)),
    ]

    def test_the_count_stays_a_count(self):
        for lang, text, moment in self.ROWS:
            with self.subTest(lang=lang, text=text):
                self.assertEqual(read(lang, text)[0], moment)

    def test_a_clock_phrase_still_gives_the_hour(self):
        for lang, text, moment in (
                ("es-es", "despiértame mañana a las 8h, por favor",
                 datetime(2026, 1, 6, 8)),
                ("gl-es", "espértame mañá ás oito, por favor",
                 datetime(2026, 1, 6, 8)),
                ("ca-es", "desperta'm demà a les 9, si us plau",
                 datetime(2026, 1, 6, 9)),
                ("es-es", "mañana quedamos 8h, gracias",
                 datetime(2026, 1, 6, 8))):
            with self.subTest(lang=lang, text=text):
                self.assertEqual(read(lang, text)[0], moment)


class TestWithoutAnchor(unittest.TestCase):
    """eu and kab compare the anchor with naive dates."""

    ROWS = [("eu", "ekainaren 5ean", 6, 5),
            ("eu", "11 urt", 1, 11),
            ("eu", "ekainaren 5ean, mila esker", 6, 5),
            ("kab", "3 yennayer", 1, 3),
            ("kab", "3 yennayer, tanemmirt", 1, 3)]

    def test_no_anchor(self):
        for lang, text, month, day in self.ROWS:
            with self.subTest(lang=lang, text=text):
                found = _odp.extract_datetime(text, lang)
                self.assertEqual((found[0].month, found[0].day), (month, day))

    def test_text_without_punctuation_keeps_naive_output(self):
        for lang, text in (("eu", "ekainaren 5ean"), ("kab", "3 yennayer")):
            with self.subTest(lang=lang):
                self.assertIsNone(_odp.extract_datetime(text, lang)[0].tzinfo)

    def test_aware_anchor(self):
        aware = datetime(2026, 1, 5, 6, tzinfo=ZoneInfo("Europe/Lisbon"))
        for lang, text, month, day in self.ROWS:
            with self.subTest(lang=lang, text=text):
                found = _odp.extract_datetime(text, lang, anchorDate=aware)
                self.assertEqual((found[0].month, found[0].day), (month, day))


class TestChoiceBetweenReadings(unittest.TestCase):
    """The engine is scripted, so each case isolates one rule."""

    def choose(self, written, separated, clause=None):
        readings = {"a, b": written, "a , b": separated, "a": clause}
        with mock.patch.object(_odp, "_extract_datetime_legacy",
                               lambda text, *args: readings[text]):
            return _odp._extract_datetime_engine("a, b", "en-us", ANCHOR)

    def test_separated_reading_adds_the_clock_to_the_same_date(self):
        found = self.choose([datetime(2026, 1, 6), "b"],
                            [datetime(2026, 1, 6, 8), ""])
        self.assertEqual(found, [datetime(2026, 1, 6, 8), ""])

    def test_separated_reading_on_another_date_is_refused(self):
        written = [datetime(2026, 1, 6), "b"]
        found = self.choose(written, [datetime(2026, 1, 7, 8), ""])
        self.assertEqual(found, written)

    def test_separated_reading_that_leaves_more_words_is_refused(self):
        # "d ttnac, n yiḍ" is read as a whole as written; apart, the part of
        # the day stays unread
        written = [datetime(2026, 1, 6), "b"]
        found = self.choose(written, [datetime(2026, 1, 6, 12), "n yiḍ"])
        self.assertEqual(found, written)

    def test_a_reading_that_gains_nothing_keeps_the_written_text(self):
        written = [datetime(2026, 1, 6), "w; x"]
        found = self.choose(written, [datetime(2026, 1, 6), "w x"])
        self.assertEqual(found, written)

    def test_separated_reading_is_taken_where_nothing_was_read(self):
        found = self.choose(None, [datetime(2026, 1, 6, 8), "w , x"])
        self.assertEqual(found, [datetime(2026, 1, 6, 8), "w x"])

    def test_clause_that_disagrees_refuses_the_separated_reading(self):
        self.assertIsNone(self.choose(None, [datetime(2026, 1, 6), "x"],
                                      clause=[datetime(2026, 1, 7, 3), ""]))


class TestOneNowForBothReadings(unittest.TestCase):
    def test_relative_time_without_anchor(self):
        clock = (datetime(2026, 1, 5, 6, minute) for minute in itertools.count())
        with mock.patch.object(_odp, "now_local", lambda: next(clock)), \
                mock.patch("ovos_date_parser.dates_en.now_local",
                           lambda: next(clock)):
            found = _odp.extract_datetime("(in 5 minutes), please", "en-us")
        self.assertEqual(found[0], datetime(2026, 1, 5, 6, 0)
                         + timedelta(minutes=5))


class TestPunctuationInsideExpression(unittest.TestCase):
    """Punctuation that is part of a time or date keeps its reading."""

    ROWS = [
        ("en-us", "remind me at 8:30 p.m. thanks",
         datetime(2026, 1, 5, 20, 30), "remind me thanks"),
        ("en-us", "remind me at 8 a.m. thanks",
         datetime(2026, 1, 5, 8, 0), "remind me thanks"),
        ("en-us", "at 8 p.m., please",
         datetime(2026, 1, 5, 20, 0), "please"),
        ("en-us", "at 8!", datetime(2026, 1, 5, 8, 0), ""),
        ("pt-pt", "lembra-me no dia 3 dez. obrigado",
         datetime(2026, 12, 3), "lembra-me obrigado"),
        ("pt-pt", "lembra-me às 15h30 obrigado",
         datetime(2026, 1, 5, 15, 30), "lembra-me obrigado"),
        ("pt-pt", "lembra-me no dia 25/12 obrigado",
         datetime(2026, 12, 25), "lembra-me obrigado"),
        ("es-es", "recuérdame a las 8:30 gracias",
         datetime(2026, 1, 5, 8, 30), "recuérdame gracias"),
        ("es-es", "recuérdame el 3 dic. gracias",
         datetime(2026, 12, 3), "recuérdame gracias"),
        ("gl-es", "lémbrame o 3 dec. grazas",
         datetime(2026, 12, 3), "lémbrame grazas"),
        ("fr-fr", "rappelle-moi à 15h30 merci",
         datetime(2026, 1, 5, 15, 30), "rappelle-moi merci"),
        ("fr-fr", "rappelle-moi à 8h30 merci",
         datetime(2026, 1, 5, 8, 30), "rappelle-moi merci"),
        ("de-de", "erinnere mich am 3.5.2025 danke",
         datetime(2025, 5, 3), "erinnere mich danke"),
        ("de-de", "erinnere mich am 3. Dezember danke",
         datetime(2026, 12, 3), "erinnere mich danke"),
        ("de-de", "erinnere mich um 8.30 uhr danke",
         datetime(2026, 1, 5, 8, 30), "erinnere mich danke"),
        ("it-it", "ricordamelo alle 8:30 grazie",
         datetime(2026, 1, 5, 8, 30), "ricordamelo grazie"),
    ]

    def test_inner_punctuation_is_kept(self):
        for lang, text, moment, leftover in self.ROWS:
            with self.subTest(lang=lang, text=text):
                found = read(lang, text)
                self.assertIsNotNone(found)
                self.assertEqual(found[0], moment)
                self.assertEqual(found[1], leftover)


if __name__ == "__main__":
    unittest.main()
