"""Cross-language behavioural invariants.

Every supported language must resolve its "tomorrow" word, parse digit
times, parse simple durations, shorten nice_date to its "today" word, and
return None for date-less text.
"""
import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (extract_datetime, extract_duration, nice_date,
                              nice_time)

ANCHOR = datetime(2023, 6, 5, 12, 0)  # monday, noon

TOMORROW = {
    "ar": "غداً", "en": "tomorrow", "de": "morgen", "nl": "morgen", "da": "i morgen",
    "sv": "imorgon", "es": "mañana", "pt": "amanhã", "ca": "demà",
    "it": "domani", "fr": "demain", "cs": "zítra", "pl": "jutro",
    "ru": "завтра", "uk": "завтра", "fa": "فردا", "eu": "bihar",
    "az": "sabah",
    "oc": "deman",
    "sk": "zajtra",
}

FIVE_MINUTES = {
    "ar": "5 دقائق", "en": "5 minutes", "de": "5 minuten", "nl": "5 minuten",
    "da": "5 minutter", "sv": "5 minuter", "es": "5 minutos",
    "pt": "5 minutos", "ca": "5 minuts", "cs": "5 minut", "pl": "5 minut",
    "ru": "5 минут", "uk": "5 хвилин", "fa": "پنج دقیقه", "az": "5 dəqiqə",
    "gl": "5 minutos",
    "oc": "5 minutas",
    "sk": "5 minút",
}

NO_DATE = {
    "ar": "مرحبا بالعالم", "en": "hello world", "de": "hallo welt", "nl": "hallo wereld",
    "da": "hej verden", "sv": "hej världen", "es": "hola mundo",
    "pt": "olá mundo", "ca": "hola món", "it": "ciao mondo",
    "fr": "bonjour le monde", "cs": "ahoj světe", "pl": "witaj świecie",
    "ru": "привет мир", "uk": "привіт світ", "fa": "سلام دنیا",
    "eu": "kaixo mundua", "az": "salam dünya",
    "oc": "adiu amics",
    "sk": "ahoj svet",
}

TODAY_WORD = {
    "ar": "اليوم", "en": "today", "de": "heute", "nl": "vandaag", "da": "i dag",
    "sv": "idag", "es": "hoy", "pt": "hoje", "ca": "avui", "it": "oggi",
    "fr": "aujourd'hui", "cs": "dnes", "pl": "dziś", "ru": "сегодня",
    "uk": "сьогодні", "fa": "امروز", "eu": "gaur", "az": "bu gün",
    "gl": "hoxe", "hu": "ma",
    "oc": "uèi",
    "sk": "dnes",
}

DIGIT_TIME_LANGS = ["ar", "en", "de", "nl", "da", "sv", "es", "pt", "ca", "it",
                    "fr", "cs", "oc", "pl", "ru", "uk", "fa", "eu", "az", "sk"]


class TestTomorrow(unittest.TestCase):
    def test_tomorrow_resolves_to_next_day(self):
        for lang, word in TOMORROW.items():
            with self.subTest(lang=lang):
                result = extract_datetime(word, lang, anchorDate=ANCHOR)
                self.assertIsNotNone(result, lang)
                self.assertEqual(result[0].date(),
                                 (ANCHOR + timedelta(days=1)).date())


class TestDigitTime(unittest.TestCase):
    def test_hh_mm_parses(self):
        for lang in DIGIT_TIME_LANGS:
            with self.subTest(lang=lang):
                result = extract_datetime("15:30", lang, anchorDate=ANCHOR)
                self.assertIsNotNone(result, lang)
                self.assertEqual((result[0].hour, result[0].minute), (15, 30))


class TestDuration(unittest.TestCase):
    def test_five_minutes(self):
        for lang, phrase in FIVE_MINUTES.items():
            with self.subTest(lang=lang):
                duration, _ = extract_duration(phrase, lang)
                self.assertEqual(duration, timedelta(minutes=5))


class TestNoDate(unittest.TestCase):
    def test_dateless_text_returns_none(self):
        for lang, phrase in NO_DATE.items():
            with self.subTest(lang=lang):
                self.assertIsNone(
                    extract_datetime(phrase, lang, anchorDate=ANCHOR))


class TestNiceDateToday(unittest.TestCase):
    def test_same_day_shortens_to_today(self):
        now = datetime(2023, 6, 5, 9, 0)
        for lang, word in TODAY_WORD.items():
            with self.subTest(lang=lang):
                self.assertEqual(
                    nice_date(datetime(2023, 6, 5), lang, now=now), word)


class TestNiceTimeDisplay(unittest.TestCase):
    def test_display_form_contains_minutes(self):
        dt = datetime(2023, 6, 5, 15, 30)
        for lang in TODAY_WORD:
            with self.subTest(lang=lang):
                out = nice_time(dt, lang, speech=False)
                self.assertIn("30", out)

    def test_24h_display(self):
        dt = datetime(2023, 6, 5, 15, 30)
        for lang in TODAY_WORD:
            with self.subTest(lang=lang):
                out = nice_time(dt, lang, speech=False, use_24hour=True)
                self.assertIn("15", out)
                self.assertIn("30", out)


if __name__ == "__main__":
    unittest.main()
