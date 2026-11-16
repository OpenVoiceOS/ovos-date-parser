"""Punctuation written against the last word of a date or time expression.

The per-language engines split on whitespace, so "8," reached them as a word
that is not a clock. Each row names the date and leftover text the sentence
reads to once the punctuation is a word of its own.
"""
import unittest
from datetime import datetime

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
