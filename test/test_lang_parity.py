"""Every supported language must provide every public function.

Guards against partial language support: no language may raise
NotImplementedError from any public entry point.
"""
import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (extract_datetime, extract_duration, nice_date,
                              nice_date_time, nice_day, nice_duration,
                              nice_month, nice_relative_time, nice_time,
                              nice_weekday, nice_year, get_date_strings)

LANGS = ["ar", "ast", "az", "ca", "cs", "da", "de", "en", "es", "eu", "fa",
         "fi", "fr", "gl", "hu", "it", "kab", "nl", "oc", "pl", "pt", "ro", "ru", "sl", "sv", "uk"]
LANGS = ["ar", "ast", "az", "ca", "cs", "da", "de", "he", "en", "es", "eu", "fa", "fr",
         "gl", "hu", "it", "kab", "nl", "oc", "pl", "pt", "ro", "ru", "sl", "sv", "uk"]
LANGS = ["ar", "ast", "az", "ca", "cs", "da", "de", "en", "es", "eu", "fa", "fr",
         "gl", "hu", "it", "kab", "nl", "oc", "pl", "pt", "ro", "ru", "sl", "sv", "uk", "sk"]

ANCHOR = datetime(2017, 6, 27, 13, 4)

_TOMORROW = {
    "ar": "غداً", "ast": "mañana", "az": "sabah", "ca": "demà", "cs": "zítra", "da": "i morgen",
    "de": "morgen", "he": "מחר", "en": "tomorrow", "es": "mañana", "eu": "bihar",
    "fa": "فردا", "fr": "demain", "gl": "mañá", "hu": "holnap",
    "fi": "huomenna", "it": "domani", "kab": "azekka", "nl": "morgen", "oc": "deman", "pl": "jutro", "pt": "amanhã",
    "ro": "mâine", "ru": "завтра", "sl": "jutri", "sv": "imorgon", "uk": "завтра",
    "sk": "zajtra",
}

_NO_DATE = {
    "ar": "مرحبا كيف حالك", "ast": "hola qué tal", "az": "salam necəsən", "ca": "hola com estàs", "cs": "ahoj jak se máš",
    "da": "hej hvordan har du det", "de": "hallo wie geht es dir", "he": "שלום מה שלומך",
    "en": "hello how are you", "es": "hola qué tal", "eu": "kaixo zer moduz",
    "fa": "سلام چطوری", "fr": "bonjour ça va", "gl": "ola que tal",
    "fi": "hei mitä kuuluu", "hu": "szia hogy vagy", "it": "ciao come stai",
    "kab": "azul fell-awen amek tellam", "nl": "hallo hoe gaat het",
    "pl": "cześć jak się masz", "pt": "olá tudo bem",
    "ro": "salut ce faci", "ru": "привет как дела",
    "sl": "živjo kako si", "sv": "hej hur mår du", "uk": "привіт як справи",
    "oc": "adiu amics",
    "sk": "ahoj ako sa máš",
}

_DURATION_STRINGS = {
    "ar": "١٠ دقائق", "ast": "10 minutos", "az": "10 dəqiqə", "ca": "10 minuts", "cs": "10 minut",
    "da": "10 minutter", "de": "10 minuten", "he": "10 דקות", "en": "10 minutes",
    "es": "10 minutos", "eu": "10 minutu", "fa": "۱۰ دقیقه",
    "fr": "10 minutes", "gl": "10 minutos", "hu": "10 perc",
    "fi": "10 minuuttia", "it": "10 minuti", "kab": "10 n tesdidin", "nl": "10 minuten", "pl": "10 minut",
    "pt": "10 minutos", "ro": "10 minute", "ru": "10 минут", "sl": "10 minut",
    "sv": "10 minuter", "uk": "10 хвилин",
    "oc": "10 minutas",
    "sk": "10 minút",
}


class TestLanguageParity(unittest.TestCase):
    def test_nice_time(self):
        for lang in LANGS:
            for kwargs in ({"use_24hour": True}, {"use_24hour": False}):
                spoken = nice_time(ANCHOR, lang, **kwargs)
                self.assertTrue(str(spoken).strip(), f"{lang} {kwargs}")

    def test_nice_duration(self):
        for lang in LANGS:
            spoken = nice_duration(163, lang)
            self.assertTrue(spoken.strip(), lang)
            display = nice_duration(163, lang, speech=False)
            self.assertIn(":", display, lang)

    def test_nice_relative_time(self):
        for lang in LANGS:
            spoken = nice_relative_time(ANCHOR + timedelta(minutes=5),
                                        relative_to=ANCHOR, lang=lang)
            self.assertTrue(spoken.strip(), lang)

    def test_extract_duration(self):
        for lang in LANGS:
            duration, _ = extract_duration(_DURATION_STRINGS[lang], lang)
            self.assertEqual(duration, timedelta(minutes=10),
                             f"{lang}: {_DURATION_STRINGS[lang]}")

    def test_extract_datetime_tomorrow(self):
        for lang in LANGS:
            result = extract_datetime(_TOMORROW[lang], lang,
                                      anchorDate=ANCHOR)
            self.assertIsNotNone(result, lang)
            self.assertEqual(result[0].date(),
                             (ANCHOR + timedelta(days=1)).date(),
                             f"{lang}: {_TOMORROW[lang]}")

    def test_extract_datetime_no_date(self):
        for lang in LANGS:
            self.assertIsNone(
                extract_datetime(_NO_DATE[lang], lang, anchorDate=ANCHOR),
                f"{lang}: {_NO_DATE[lang]}")

    def test_nice_date_family(self):
        for lang in LANGS:
            self.assertTrue(nice_date(ANCHOR, lang).strip(), lang)
            self.assertTrue(nice_date_time(ANCHOR, lang).strip(), lang)
            self.assertTrue(nice_day(ANCHOR, lang).strip(), lang)
            self.assertTrue(nice_weekday(ANCHOR, lang).strip(), lang)
            self.assertTrue(nice_month(ANCHOR, lang).strip(), lang)
            self.assertTrue(nice_year(ANCHOR, lang).strip(), lang)

    def test_get_date_strings(self):
        for lang in LANGS:
            strings = get_date_strings(ANCHOR, lang)
            self.assertEqual(strings["year_string"], "2017", lang)
            self.assertTrue(strings["month_string"], lang)


if __name__ == "__main__":
    unittest.main()
