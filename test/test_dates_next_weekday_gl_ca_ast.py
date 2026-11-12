"""Regression tests: a next/last marker around a weekday name in gl, ca, ast.

"o seguinte venres" is the coming Friday, the same day as "o venres seguinte"
and "o venres que vén"; "o venres pasado" is the Friday before today.
Expected datetimes are hand-derived from the fixed anchor, Saturday
17 October 2026, never pinned from engine output.
"""
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=ZoneInfo("Europe/Lisbon"))

# weekday name: (first occurrence after the anchor, last occurrence before it)
GL = {
    "luns": (19, 12), "martes": (20, 13), "mercores": (21, 14),
    "xoves": (22, 15), "venres": (23, 16), "domingo": (18, 11),
}
CA = {
    "dilluns": (19, 12), "dimarts": (20, 13), "dimecres": (21, 14),
    "dijous": (22, 15), "divendres": (23, 16), "diumenge": (18, 11),
}
AST = {
    "llunes": (19, 12), "martes": (20, 13), "miércoles": (21, 14),
    "xueves": (22, 15), "vienres": (23, 16), "domingu": (18, 11),
}


def _dt(text, lang):
    res = extract_datetime(text, lang=lang, anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    return res[0].replace(tzinfo=None)


def _oct(day):
    return datetime(2026, 10, day)


class TestGalician(unittest.TestCase):
    def test_seguinte_before_weekday(self):
        for day, (coming, _) in GL.items():
            for text in ("o seguinte %s" % day, "seguinte %s" % day):
                with self.subTest(text=text):
                    self.assertEqual(_dt(text, "gl-ES"), _oct(coming))

    def test_seguinte_inside_question(self):
        self.assertEqual(_dt("cando é o seguinte venres", "gl-ES"), _oct(23))

    def test_pasado_after_weekday(self):
        for day, (_, last) in GL.items():
            for text in ("o %s pasado" % day, "%s pasado" % day):
                with self.subTest(text=text):
                    self.assertEqual(_dt(text, "gl-ES"), _oct(last))

    def test_confusables(self):
        for text in ("o venres", "venres", "o venres seguinte",
                     "o venres que vén", "o proximo venres"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text, "gl-ES"), _oct(23))
        self.assertEqual(_dt("o pasado venres", "gl-ES"), _oct(16))
        self.assertEqual(_dt("a semana que vén", "gl-ES"), _oct(24))


class TestCatalan(unittest.TestCase):
    def test_vinent_before_weekday(self):
        for day, (coming, _) in CA.items():
            for text in ("el vinent %s" % day, "vinent %s" % day):
                with self.subTest(text=text):
                    self.assertEqual(_dt(text, "ca-ES"), _oct(coming))

    def test_vinent_inside_question(self):
        self.assertEqual(_dt("quan és el vinent divendres", "ca-ES"), _oct(23))

    def test_confusables(self):
        for text in ("el divendres", "divendres", "el divendres vinent",
                     "el divendres que ve", "el pròxim divendres",
                     "el següent divendres"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text, "ca-ES"), _oct(23))
        for text in ("el passat divendres", "el divendres passat"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text, "ca-ES"), _oct(16))
        self.assertEqual(_dt("la setmana següent", "ca-ES"), _oct(24))


class TestAsturian(unittest.TestCase):
    def test_siguiente_before_weekday(self):
        for day, (coming, _) in AST.items():
            for text in ("el siguiente %s" % day, "siguiente %s" % day):
                with self.subTest(text=text):
                    self.assertEqual(_dt(text, "ast-ES"), _oct(coming))

    def test_siguiente_inside_question(self):
        self.assertEqual(_dt("cuándo ye el siguiente vienres", "ast-ES"),
                         _oct(23))

    def test_pasau_after_weekday(self):
        for day, (_, last) in AST.items():
            for text in ("el %s pasáu" % day, "%s pasáu" % day):
                with self.subTest(text=text):
                    self.assertEqual(_dt(text, "ast-ES"), _oct(last))

    def test_confusables(self):
        for text in ("el vienres", "vienres", "el vienres siguiente",
                     "el vienres que vien"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text, "ast-ES"), _oct(23))
        self.assertEqual(_dt("el pasáu vienres", "ast-ES"), _oct(16))
        self.assertEqual(_dt("la selmana siguiente", "ast-ES"), _oct(24))


class TestWeekdayOfAnotherWeek(unittest.TestCase):
    """The week starts on Monday, so from Saturday 17 October the next week
    runs from Monday 19 to Sunday 25 and the last week from 5 to 11."""

    CASES = {
        "gl-ES": ("o %s da semana que vén", "o %s da semana seguinte",
                  "o %s da semana pasada", {"luns": 0, "venres": 4,
                                            "domingo": 6}),
        "ast-ES": ("el %s de la selmana que vien",
                   "el %s de la selmana siguiente",
                   "el %s de la selmana pasada", {"llunes": 0, "vienres": 4,
                                                  "domingu": 6}),
    }

    def test_weekday_of_next_and_last_week(self):
        for lang, (que_ven, seguinte, pasada, names) in self.CASES.items():
            for name, idx in names.items():
                for tmpl in (que_ven, seguinte):
                    text = tmpl % name
                    with self.subTest(lang=lang, text=text):
                        self.assertEqual(_dt(text, lang), _oct(19 + idx))
                text = pasada % name
                with self.subTest(lang=lang, text=text):
                    self.assertEqual(_dt(text, lang), _oct(5 + idx))

    def test_catalan_unchanged(self):
        self.assertEqual(_dt("el divendres de la setmana que ve", "ca-ES"),
                         _oct(23))


FRIDAY = datetime(2026, 10, 16, 10, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


def _on(text, lang, anchor):
    res = extract_datetime(text, lang=lang, anchorDate=anchor)
    assert res is not None, "no datetime extracted from %r" % text
    return res[0].replace(tzinfo=None), res[1]


class TestNextOnTheSameWeekday(unittest.TestCase):
    """Said on the weekday itself, "next <weekday>" is a week away."""

    def test_friday_from_a_friday(self):
        for lang, texts in (
                ("gl-ES", ("o seguinte venres", "o venres seguinte")),
                ("ca-ES", ("el vinent divendres", "el divendres vinent",
                           "el divendres següent", "el proper divendres")),
                ("ast-ES", ("el siguiente vienres", "el vienres siguiente"))):
            for text in texts:
                with self.subTest(text=text):
                    self.assertEqual(_on(text, lang, FRIDAY)[0], _oct(23))

    def test_saturday_from_a_saturday(self):
        for lang, texts in (
                ("gl-ES", ("o seguinte sábado", "o sábado seguinte")),
                ("ca-ES", ("el vinent dissabte", "el dissabte següent")),
                ("ast-ES", ("el siguiente sábadu", "el sábadu siguiente"))):
            for text in texts:
                with self.subTest(text=text):
                    self.assertEqual(_dt(text, lang), _oct(24))

    def test_plain_weekday_is_still_today(self):
        self.assertEqual(_on("o venres", "gl-ES", FRIDAY)[0], _oct(16))
        self.assertEqual(_on("el divendres", "ca-ES", FRIDAY)[0], _oct(16))
        self.assertEqual(_on("el vienres", "ast-ES", FRIDAY)[0], _oct(16))


class TestCatalanNext(unittest.TestCase):
    def test_every_next_form_of_the_coming_friday(self):
        for text in ("el vinent divendres", "el divendres vinent",
                     "el divendres següent", "el proper divendres",
                     "el pròxim divendres", "el divendres que ve"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text, "ca-ES"), _oct(23))

    def test_next_week(self):
        for text in ("la setmana que ve", "la setmana vinent",
                     "la setmana següent", "la propera setmana"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text, "ca-ES"), _oct(24))

    def test_proper_leaves_no_word_behind(self):
        self.assertEqual(_on("el proper divendres", "ca-ES", ANCHOR),
                         (_oct(23), ""))
        self.assertEqual(_on("la setmana que ve", "ca-ES", ANCHOR),
                         (_oct(24), ""))

    def test_weekday_of_next_week_unchanged(self):
        self.assertEqual(_dt("el divendres de la setmana que ve", "ca-ES"),
                         _oct(23))
        self.assertEqual(_dt("el divendres de la setmana vinent", "ca-ES"),
                         _oct(23))


class TestQueVenRemainder(unittest.TestCase):
    """"que vén" / "que vien" is read in place; no word is added."""

    CASES = (
        ("gl-ES", "a semana que vén", _oct(24)),
        ("gl-ES", "o venres que vén", _oct(23)),
        ("gl-ES", "o venres da semana que vén", _oct(23)),
        ("gl-ES", "o mes que vén", datetime(2026, 11, 17)),
        ("gl-ES", "o ano que vén", datetime(2027, 10, 17)),
        ("ast-ES", "la selmana que vien", _oct(24)),
        ("ast-ES", "el vienres que vien", _oct(23)),
        ("ast-ES", "el vienres de la selmana que vien", _oct(23)),
        ("ast-ES", "el mes que vien", datetime(2026, 11, 17)),
        ("ast-ES", "el añu que vien", datetime(2027, 10, 17)),
    )

    def test_phrase_leaves_no_remainder(self):
        for lang, text, expected in self.CASES:
            with self.subTest(text=text):
                date, rest = _on(text, lang, ANCHOR)
                self.assertEqual(date, expected)
                self.assertNotIn("seguinte", rest)
                self.assertNotIn("siguiente", rest)
                self.assertNotIn("ven", rest.split())
                self.assertNotIn("vien", rest.split())

    def test_bare_phrase_remainder_is_empty(self):
        self.assertEqual(_on("a semana que vén", "gl-ES", ANCHOR)[1], "")
        self.assertEqual(_on("la selmana que vien", "ast-ES", ANCHOR)[1], "")

    def test_words_around_the_phrase_are_kept(self):
        self.assertEqual(
            _on("recorda a semana que vén mercar pan", "gl-ES", ANCHOR),
            (_oct(24), "recorda mercar pan"))
        self.assertEqual(
            _on("recuerda la selmana que vien mercar pan", "ast-ES", ANCHOR),
            (_oct(24), "recuerda mercar pan"))


class TestProximoOnTheSameWeekday(unittest.TestCase):
    """Said on a Friday, "next Friday" with "próximo" is a week away."""

    def test_friday_from_a_friday(self):
        for lang, text in (("gl-ES", "o próximo venres"),
                           ("gl-ES", "o proximo venres"),
                           ("ca-ES", "el pròxim divendres"),
                           ("ca-ES", "el proper divendres"),
                           ("ast-ES", "el próximu vienres"),
                           ("ast-ES", "el proximu vienres")):
            with self.subTest(text=text):
                self.assertEqual(_on(text, lang, FRIDAY)[0], _oct(23))

    def test_other_weekdays_are_unchanged(self):
        for lang, text in (("gl-ES", "o próximo luns"),
                           ("ca-ES", "el pròxim dilluns"),
                           ("ast-ES", "el próximu llunes")):
            with self.subTest(text=text):
                self.assertEqual(_on(text, lang, FRIDAY)[0], _oct(19))


class TestPartOfTheDayAloneDoesNotRaise(unittest.TestCase):
    def test_vespre_alone(self):
        res = extract_datetime("vespre", lang="ca-ES", anchorDate=ANCHOR)
        self.assertEqual(res[0].replace(tzinfo=None),
                         datetime(2026, 10, 17, 19))
        self.assertEqual(res[1], "")


class TestMananaIsTomorrowOrTheMorning(unittest.TestCase):
    """"mañá" and "mañana" are the morning only after a morning preposition
    or "esta"; anywhere else they are tomorrow."""

    CASES = (
        ("gl-ES", "mañá ás 22:30", datetime(2026, 10, 18, 22, 30)),
        ("gl-ES", "mañá ás 10", datetime(2026, 10, 18, 10)),
        ("gl-ES", "mañá", datetime(2026, 10, 18)),
        ("gl-ES", "ás 8 da mañá", datetime(2026, 10, 18, 8)),
        ("gl-ES", "hoxe ás 8 da mañá", datetime(2026, 10, 17, 8)),
        ("gl-ES", "esta mañá", datetime(2026, 10, 17, 8)),
        ("gl-ES", "mañá pola mañá", datetime(2026, 10, 18, 8)),
        ("ast-ES", "mañana a les 22:30", datetime(2026, 10, 18, 22, 30)),
        ("ast-ES", "mañana a les 10", datetime(2026, 10, 18, 10)),
        ("ast-ES", "mañana", datetime(2026, 10, 18)),
        ("ast-ES", "a les 8 de la mañana", datetime(2026, 10, 18, 8)),
        ("ast-ES", "güei a les 8 de la mañana", datetime(2026, 10, 17, 8)),
        ("ast-ES", "esta mañana", datetime(2026, 10, 17, 8)),
        ("ast-ES", "mañana pela mañana", datetime(2026, 10, 18, 8)),
    )

    def test_tomorrow_and_the_morning(self):
        for lang, text, expected in self.CASES:
            with self.subTest(text=text):
                self.assertEqual(_dt(text, lang), expected)


class TestMorningAfterAnArticleOrAQuantifier(unittest.TestCase):
    CASES = (
        ("gl-ES", "a mañá do luns", datetime(2026, 10, 19, 8)),
        ("gl-ES", "cada mañá", datetime(2026, 10, 18, 8)),
        ("gl-ES", "mañá cedo", datetime(2026, 10, 18, 8)),
        ("ast-ES", "la mañana del llunes", datetime(2026, 10, 19, 8)),
        ("ast-ES", "cada mañana", datetime(2026, 10, 18, 8)),
        ("ast-ES", "mañana ceo", datetime(2026, 10, 18, 8)),
    )

    def test_the_morning_of_a_day(self):
        for lang, text, expected in self.CASES:
            with self.subTest(text=text):
                self.assertEqual(_dt(text, lang), expected)

    def test_a_cedo_leaves_no_remainder(self):
        self.assertEqual(_on("mañá cedo", "gl-ES", ANCHOR)[1], "")
        self.assertEqual(_on("mañana ceo", "ast-ES", ANCHOR)[1], "")


class TestCedoNeedsADayWord(unittest.TestCase):
    """"cedo" and "ceo" are the morning only beside a day word."""

    def test_without_a_day_word_there_is_no_date(self):
        for lang, text in (("gl-ES", "chegou cedo"),
                           ("gl-ES", "érguome cedo"),
                           ("gl-ES", "cedo"),
                           ("gl-ES", "érguome moi cedo"),
                           ("ast-ES", "llegué ceo"),
                           ("ast-ES", "ceo")):
            with self.subTest(text=text):
                self.assertIsNone(extract_datetime(
                    text, lang=lang, anchorDate=ANCHOR))

    def test_beside_a_day_word_it_is_the_morning(self):
        for lang, text, expected in (
                ("gl-ES", "mañá cedo", datetime(2026, 10, 18, 8)),
                ("gl-ES", "mañá moi cedo", datetime(2026, 10, 18, 8)),
                ("gl-ES", "o luns cedo", datetime(2026, 10, 19, 8)),
                ("gl-ES", "hoxe cedo", datetime(2026, 10, 17, 8)),
                ("ast-ES", "mañana ceo", datetime(2026, 10, 18, 8)),
                ("ast-ES", "el llunes ceo", datetime(2026, 10, 19, 8)),
                ("ast-ES", "güei ceo", datetime(2026, 10, 17, 8))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text, lang), expected)


class TestIntensifierBeforeCedo(unittest.TestCase):
    def test_an_intensifier_keeps_the_morning(self):
        for lang, text, expected in (
                ("gl-ES", "mañá moi cedo", datetime(2026, 10, 18, 8)),
                ("gl-ES", "mañá ben cedo", datetime(2026, 10, 18, 8)),
                ("gl-ES", "mañá tan cedo", datetime(2026, 10, 18, 8)),
                ("gl-ES", "o luns máis cedo", datetime(2026, 10, 19, 8)),
                ("ast-ES", "mañana mui ceo", datetime(2026, 10, 18, 8)),
                ("ast-ES", "mañana bien ceo", datetime(2026, 10, 18, 8)),
                ("ast-ES", "mañana tan ceo", datetime(2026, 10, 18, 8)),
                ("ast-ES", "el llunes más ceo", datetime(2026, 10, 19, 8))):
            with self.subTest(text=text):
                self.assertEqual(_dt(text, lang), expected)

    def test_an_intensifier_without_a_day_word_is_no_date(self):
        for lang, text in (("gl-ES", "chegou moi cedo"),
                           ("gl-ES", "érguome ben cedo"),
                           ("ast-ES", "llegué mui ceo")):
            with self.subTest(text=text):
                self.assertIsNone(extract_datetime(
                    text, lang=lang, anchorDate=ANCHOR))


# Monday 19 October 2026 .. Sunday 25 October 2026
WEEK_ANCHORS = [datetime(2026, 10, 19 + k, 12, 0,
                         tzinfo=ZoneInfo("Europe/Lisbon"))
                for k in range(7)]
WEEKDAY_NAMES = {
    "gl-ES": ["luns", "martes", "mercores", "xoves", "venres", "sabado",
              "domingo"],
    "ca-ES": ["dilluns", "dimarts", "dimecres", "dijous", "divendres",
              "dissabte", "diumenge"],
    "ast-ES": ["llunes", "martes", "miércoles", "xueves", "vienres",
               "sábadu", "domingu"],
}
NEXT_WEEK_PHRASES = {
    "gl-ES": ("a semana que vén o {d}", "a semana seguinte o {d}"),
    "ca-ES": ("la setmana que ve {d}", "la setmana vinent el {d}"),
    "ast-ES": ("la selmana que vien el {d}", "la selmana siguiente el {d}"),
}
LAST_WORD = {"gl-ES": "pasado", "ca-ES": "passat", "ast-ES": "pasáu"}


def _at(text, lang, anchor):
    res = extract_datetime(text, lang=lang, anchorDate=anchor)
    assert res is not None, "no datetime extracted from %r" % text
    return res[0].replace(tzinfo=None)


class TestWeekdayAfterNextWeek(unittest.TestCase):
    def test_every_weekday_of_next_week_from_every_anchor(self):
        # the Monday after the anchor week is 26 October
        for lang, names in WEEKDAY_NAMES.items():
            for phrase in NEXT_WEEK_PHRASES[lang]:
                for idx, name in enumerate(names):
                    for anchor in WEEK_ANCHORS:
                        text = phrase.format(d=name)
                        with self.subTest(text=text, anchor=anchor.day):
                            self.assertEqual(_at(text, lang, anchor),
                                             datetime(2026, 10, 26)
                                             + timedelta(days=idx))

    def test_friday_of_last_week_from_every_anchor(self):
        for anchor in WEEK_ANCHORS:
            with self.subTest(anchor=anchor.day):
                self.assertEqual(_at("a semana pasada o venres", "gl-ES",
                                     anchor), _oct(16))


class TestLastWeekdayFromEveryAnchor(unittest.TestCase):
    def test_pasado_after_weekday_is_the_last_occurrence_before_today(self):
        for lang, names in WEEKDAY_NAMES.items():
            for idx, name in enumerate(names):
                for anchor in WEEK_ANCHORS:
                    # walk back one day at a time until the weekday matches
                    day = anchor.day - 1
                    while (day - 19) % 7 != idx:
                        day -= 1
                    text = "%s %s" % (name, LAST_WORD[lang])
                    with self.subTest(text=text, anchor=anchor.day):
                        self.assertEqual(_at(text, lang, anchor), _oct(day))

    def test_sunday_said_on_a_sunday(self):
        sunday = WEEK_ANCHORS[6]
        self.assertEqual(_at("o domingo pasado", "gl-ES", sunday), _oct(18))
        self.assertEqual(_at("el domingu pasáu", "ast-ES", sunday), _oct(18))
        self.assertEqual(_at("diumenge passat", "ca-ES", sunday), _oct(18))


class TestEstaMorningGalician(unittest.TestCase):
    def test_nesta_mana_is_today_morning(self):
        for text in ("nesta mañá", "esta mañá"):
            with self.subTest(text=text):
                self.assertEqual(_dt(text, "gl-ES"),
                                 datetime(2026, 10, 17, 8, 0))


class TestWeekdayBeforePasadoManana(unittest.TestCase):
    PHRASES = {
        "gl-ES": ("o {d} pasado mañá", "o {d}, pasado mañá"),
        "ast-ES": ("el {d} pasao mañana", "el {d} pasáu mañana"),
    }

    def test_weekday_two_days_ahead_is_that_day(self):
        # the weekday of anchor + 2 days is the day after tomorrow
        for lang, phrases in self.PHRASES.items():
            for k, anchor in enumerate(WEEK_ANCHORS):
                name = WEEKDAY_NAMES[lang][(k + 2) % 7]
                for phrase in phrases:
                    text = phrase.format(d=name)
                    with self.subTest(text=text, anchor=anchor.day):
                        self.assertEqual(_at(text, lang, anchor).date(),
                                         datetime(2026, 10, 21 + k).date())

    def test_pasado_manana_alone_is_unchanged(self):
        for text, lang in (("pasado mañá", "gl-ES"),
                           ("pasao mañana", "ast-ES")):
            for k, anchor in enumerate(WEEK_ANCHORS):
                with self.subTest(text=text, anchor=anchor.day):
                    self.assertEqual(_at(text, lang, anchor).date(),
                                     datetime(2026, 10, 21 + k).date())


class TestDeMananaIsTheMorning(unittest.TestCase):
    def test_after_a_weekday(self):
        for lang, phrase in (("gl-ES", "o {d} de mañá"),
                             ("ast-ES", "el {d} de mañana")):
            for k, anchor in enumerate(WEEK_ANCHORS):
                name = WEEKDAY_NAMES[lang][(k + 2) % 7]
                text = phrase.format(d=name)
                with self.subTest(text=text, anchor=anchor.day):
                    self.assertEqual(_at(text, lang, anchor),
                                     datetime(2026, 10, 21 + k, 8, 0))

    def test_after_manana(self):
        for lang, text in (("gl-ES", "mañá de mañá"),
                           ("ast-ES", "mañana de mañana")):
            for k, anchor in enumerate(WEEK_ANCHORS):
                with self.subTest(text=text, anchor=anchor.day):
                    self.assertEqual(_at(text, lang, anchor),
                                     datetime(2026, 10, 20 + k, 8, 0))


class TestEstaWithAnAccent(unittest.TestCase):
    def test_esta_with_an_accent_is_not_this_morning(self):
        for text, lang in (("a reunión está mañá", "gl-ES"),
                           ("la reunión está mañana", "ast-ES")):
            with self.subTest(text=text):
                self.assertEqual(_dt(text, lang).date(),
                                 datetime(2026, 10, 18).date())

    def test_esta_without_an_accent_is_this_morning(self):
        for text, lang in (("esta mañá", "gl-ES"), ("nesta mañá", "gl-ES"),
                           ("esta mañana", "ast-ES")):
            with self.subTest(text=text):
                self.assertEqual(_dt(text, lang),
                                 datetime(2026, 10, 17, 8, 0))


class TestWeekdayPasadoInTheMorning(unittest.TestCase):
    PHRASES = {
        "gl-ES": ("o {d} pasado pola mañá", "o {d} pasado á mañá"),
        "ast-ES": ("el {d} pasáu pela mañana", "el {d} pasao la mañana"),
    }

    def test_last_weekday_in_the_morning(self):
        for lang, phrases in self.PHRASES.items():
            for idx, name in enumerate(WEEKDAY_NAMES[lang]):
                for anchor in WEEK_ANCHORS:
                    # last occurrence strictly before the anchor day
                    day = anchor.day - 1
                    while (day - 19) % 7 != idx:
                        day -= 1
                    for phrase in phrases:
                        text = phrase.format(d=name)
                        with self.subTest(text=text, anchor=anchor.day):
                            self.assertEqual(_at(text, lang, anchor),
                                             datetime(2026, 10, day, 8, 0))
