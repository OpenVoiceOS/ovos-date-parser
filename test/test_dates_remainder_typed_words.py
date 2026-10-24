"""Regression tests: the remainder keeps the words the user typed.

The parsers of es, gl, ast, pt and it strip accents and turn hyphens into
spaces to match words, so "recuérdame mañana comprar pan" used to leave
"recuerdame comprar pan" and "check-in" came back as "check in". The
remainder holds the user's words, in lower case.
"""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


def _rest(text, lang):
    res = extract_datetime(text, lang=lang, anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    return res[1]


class TestRemainderKeepsAccents(unittest.TestCase):
    CASES = (
        ("es-ES", "recuérdame mañana comprar pan", "recuérdame comprar pan"),
        ("es-ES", "ver al médico mañana", "ver médico"),
        ("es-ES", "está lloviendo mañana", "está lloviendo"),
        ("es-ES", "recuérdame el lunes llamar al papá",
         "recuérdame llamar papá"),
        ("gl-ES", "recórdame mañá mercar pan", "recórdame mercar pan"),
        ("gl-ES", "ver o médico mañá", "ver médico"),
        ("gl-ES", "chámame mañá", "chámame"),
        ("ast-ES", "recuérdame mañana mercar pan", "recuérdame mercar pan"),
        ("ast-ES", "ver al médicu mañana", "ver médicu"),
        ("pt-PT", "compra pão amanhã", "compra pão"),
        ("pt-PT", "liga à avó amanhã", "liga à avó"),
        ("it-IT", "ricordami domani di comprare il pane perché",
         "ricordami comprare pane perché"),
        ("it-IT", "chiamami domani perché è importante",
         "chiamami perché importante"),
    )

    def test_remainder_holds_the_typed_accents(self):
        for lang, text, rest in self.CASES:
            with self.subTest(text=text):
                self.assertEqual(_rest(text, lang), rest)

    def test_words_without_accents_are_unchanged(self):
        for lang, text, rest in (
                ("es-ES", "recuerda mañana comprar pan", "recuerda comprar pan"),
                ("gl-ES", "recorda mañá mercar pan", "recorda mercar pan"),
                ("ast-ES", "recuerda mañana mercar pan", "recuerda mercar pan"),
                ("pt-PT", "compra pao amanhã", "compra pao"),
                ("it-IT", "chiamami domani perche", "chiamami perche")):
            with self.subTest(text=text):
                self.assertEqual(_rest(text, lang), rest)

    def test_two_spellings_keep_their_order(self):
        self.assertEqual(_rest("como lluvia cómo mañana", "es-ES"),
                         "como lluvia cómo")

    def test_a_sentence_without_a_date_stays_none(self):
        for lang, text in (("es-ES", "recuérdame comprar pan"),
                           ("gl-ES", "recórdame mercar pan"),
                           ("ast-ES", "recuérdame mercar pan"),
                           ("pt-PT", "compra pão"),
                           ("it-IT", "perché è importante")):
            with self.subTest(text=text):
                self.assertIsNone(extract_datetime(text, lang=lang,
                                                   anchorDate=ANCHOR))


class TestRemainderKeepsHyphens(unittest.TestCase):
    CASES = (
        ("es-ES", "reserva mañana el check-in", "reserva check-in"),
        ("es-ES", "recuérdame mañana el check-in", "recuérdame check-in"),
        ("gl-ES", "recórdame mañá o check-in", "recórdame check-in"),
        ("ast-ES", "recuérdame mañana el check-in", "recuérdame check-in"),
        ("pt-PT", "lembra-me amanhã de comprar pão", "lembra-me comprar pão"),
        ("pt-PT", "lembra-me amanhã do guarda-chuva",
         "lembra-me guarda-chuva"),
        ("it-IT", "ricordami domani il check-in", "ricordami check-in"),
    )

    def test_hyphenated_words_stay_whole(self):
        for lang, text, rest in self.CASES:
            with self.subTest(text=text):
                self.assertEqual(_rest(text, lang), rest)

    def test_a_hyphenated_date_word_does_not_leave_a_hyphen(self):
        self.assertEqual(_rest("lembra-me segunda-feira", "pt-PT"),
                         "lembra-me")

    def test_two_words_stay_two_words(self):
        # the user typed a space, so the remainder has no hyphen
        self.assertEqual(_rest("reserva mañana el check in", "es-ES"),
                         "reserva check in")
        self.assertEqual(_rest("lembra guarda chuva amanhã", "pt-PT"),
                         "lembra guarda chuva")

    def test_a_spaced_dash_is_not_a_word(self):
        self.assertEqual(_rest("reserva - mañana - el hotel", "es-ES"),
                         "reserva hotel")

    def test_punctuation_still_leaves_the_remainder(self):
        self.assertEqual(_rest("compra pão, amanhã.", "pt-PT"), "compra pão")
