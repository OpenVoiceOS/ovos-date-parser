"""A clock hour followed by more words, with no comma to end it.

Speech-to-text output carries no punctuation, so "mañana a las 8 por favor"
reaches the engines as one run of words. A number right after a clock
preposition is the hour wherever it sits in the text; a count elsewhere is not.
"""
import unittest
from datetime import date, datetime

import ovos_date_parser as _odp

# 2026-01-05 is a Monday
ANCHOR = datetime(2026, 1, 5, 6, 0)


def read(lang, text):
    return _odp.extract_datetime(text, lang, anchorDate=ANCHOR)


def at(day, hour, minute=0):
    return datetime(2026, 1, day, hour, minute)


class TestHourBeforeMoreWords(unittest.TestCase):
    # (lang, text, expected datetime, leftover text or None to skip the check)
    ROWS = [
        ("es-es", "mañana a las 8 por favor", at(6, 8), "por favor"),
        ("es-es", "qué hora será mañana a las ocho por favor", at(6, 8), None),
        ("es-es", "a las 8 gracias", at(5, 8), None),
        ("es-es", "a las ocho por favor", at(5, 8), None),
        ("es-es", "a la una por favor", at(6, 1), None),
        ("es-es", "a las 8 y media por favor", at(5, 8, 30), None),
        ("es-es", "a las 9 de la noche por favor", at(5, 21), None),
        ("gl-es", "ás 8 por favor", at(5, 8), "por favor"),
        ("gl-es", "ás oito por favor", at(5, 8), "por favor"),
        ("gl-es", "mañá ás 8 por favor", at(6, 8), "por favor"),
        ("gl-es", "á unha por favor", at(6, 1), "por favor"),
        ("gl-es", "ás 8 e media por favor", at(5, 8, 30), None),
        ("gl-es", "ás 9 da noite por favor", at(5, 21), None),
        ("ca-es", "demà a les 8 si us plau", at(6, 8), "si us plau"),
        ("ca-es", "a les 8 gràcies", at(5, 8), "gràcies"),
        ("ca-es", "a les vuit gràcies", at(5, 8), "gràcies"),
        ("ca-es", "a les 8 i mitja gràcies", at(5, 8, 30), "gràcies"),
        ("ca-es", "a les 8 i quart gràcies", at(5, 8, 15), "gràcies"),
        ("ast-es", "mañana a les 8 por favor", at(6, 8), None),
        ("ast-es", "a les 8 gracies", at(5, 8), "gracies"),
        ("ast-es", "a les ocho gracies", at(5, 8), "gracies"),
        ("ast-es", "a les 8 y media gracies", at(5, 8, 30), "gracies"),
        ("ast-es", "a les 9 de la nueche gracies", at(5, 21), None),
        ("pt-pt", "acorda-me às 8 por favor", at(5, 8), None),
        ("pt-pt", "amanhã às 8 por favor", at(6, 8), "por favor"),
        ("pt-pt", "às oito por favor", at(5, 8), "por favor"),
        ("pt-pt", "às 8 e meia por favor", at(5, 8, 30), "por favor"),
        ("pt-pt", "às oito e meia por favor", at(5, 8, 30), "por favor"),
        ("pt-pt", "à uma por favor", at(6, 1), None),
        ("en-us", "wake me at 8 please", at(5, 8), "wake me please"),
        ("en-us", "tomorrow at 8 please", at(6, 8), "please"),
        ("en-us", "at eight please", at(5, 8), "please"),
        ("en-us", "at 8 and a half please", at(5, 8, 30), "please"),
        ("en-us", "at 9 in the evening please", at(5, 21), None),
        ("it-it", "alle otto per favore", at(5, 8), None),
        ("it-it", "domani alle otto per favore", at(6, 8), None),
        ("it-it", "domani alle otto e mezza per favore", at(6, 8, 30), None),
        ("it-it", "domani alle nove di sera per favore", at(6, 21), None),
        # engines that need the clock word keep reading it before more words
        ("fr-fr", "demain à 8 heures s'il vous plaît", at(6, 8), None),
        ("fr-fr", "réveille-moi à huit heures s'il te plaît", at(5, 8), None),
        ("de-de", "morgen um 8 Uhr bitte", at(6, 8), None),
        ("de-de", "um acht Uhr bitte", at(5, 8), None),
    ]

    def test_rows(self):
        for lang, text, expected, leftover in self.ROWS:
            with self.subTest(lang=lang, text=text):
                found = read(lang, text)
                self.assertIsNotNone(found)
                self.assertEqual(found[0], expected)
                if leftover is not None:
                    self.assertEqual(found[1], leftover)


class TestCountIsNotAnHour(unittest.TestCase):
    # (lang, text): the date is read, the count stays a count
    ROWS = [
        ("es-es", "mañana necesito 5 por favor"),
        ("es-es", "mañana compra las 5 cosas por favor"),
        ("es-es", "mañana cambia a la 2 por favor"),
        ("gl-es", "mañá necesito 5 por favor"),
        ("gl-es", "mañá compra as 5 cousas por favor"),
        ("gl-es", "mañá doulle 1 libro por favor"),
        ("es-es", "mañana dame 1 libro por favor"),
        ("ca-es", "demà necessito 5 si us plau"),
        ("ca-es", "demà compra les 5 coses si us plau"),
        ("ca-es", "demà dóna a 5 persones si us plau"),
        ("ast-es", "mañana necesito 5 por favor"),
        ("ast-es", "mañana compra les 5 coses por favor"),
        ("ast-es", "mañana dalo a 5 persones por favor"),
        ("pt-pt", "amanhã preciso de 5 por favor"),
        ("pt-pt", "amanhã compra as 5 coisas por favor"),
        ("pt-pt", "amanhã dou 1 livro por favor"),
        ("en-us", "tomorrow I need 5 please"),
        ("en-us", "tomorrow buy 5 apples please"),
        ("it-it", "domani ho bisogno di 5 per favore"),
        ("it-it", "domani compra tre pani per favore"),
        ("it-it", "domani compra le tre pizze per favore"),
        ("fr-fr", "demain j'ai besoin de 5 s'il vous plaît"),
        ("fr-fr", "demain à 8 euros s'il vous plaît"),
        ("fr-fr", "de 5 à 8 personnes demain"),
        ("de-de", "morgen brauche ich 5 bitte"),
        ("de-de", "von 5 bis 8 um 3 Euro morgen"),
    ]

    def test_rows(self):
        for lang, text in self.ROWS:
            with self.subTest(lang=lang, text=text):
                found = read(lang, text)
                self.assertIsNotNone(found)
                self.assertEqual(found[0], at(6, 0))


class TestMarkGluedToTheClock(unittest.TestCase):
    # A quoted phrase reads as the same phrase without the quotes.
    ROWS = [
        ("es-es", "a las tres y media"),
        ("es-es", "a las tres y cuarto"),
        ("es-es", "ponme una alarma a las siete y cuarto"),
        ("gl-es", "pon unha alarma ás sete e cuarto"),
        ("it-it", "metti una sveglia alle quattro e mezza"),
        ("it-it", "stasera alle nove e cinque"),
        ("en-us", "tomorrow at 5pm"),
        ("en-us", "christmas island at 9am"),
    ]

    def test_rows(self):
        for lang, text in self.ROWS:
            with self.subTest(lang=lang, text=text):
                self.assertEqual(read(lang, '"%s" ok' % text)[0],
                                 read(lang, text)[0])


class TestHourKeepsFollowingDate(unittest.TestCase):
    def test_hour_then_offset_from_holiday(self):
        found = read("pt-pt", "às 9 uma hora antes do natal")
        self.assertEqual(found[0].date(), date(2026, 12, 25))

    def test_hour_with_a_part_of_day_elsewhere_stays_a_night_hour(self):
        for text in ("at 3 at night", "at 3 at night."):
            with self.subTest(text=text):
                found = read("en", text)
                self.assertTrue(found is None or found[0].hour >= 18
                                or found[0].hour < 6)

    def test_hour_then_glued_mark_reads_the_marked_word(self):
        self.assertEqual(read("en-us", "remind me at 8 pm; thanks")[0],
                         at(5, 20))
        self.assertEqual(read("en-us", "wake me at eight thirty, please")[0],
                         at(5, 8, 30))


if __name__ == "__main__":
    unittest.main()
