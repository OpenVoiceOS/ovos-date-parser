"""API-shape parity: extract_datetime must always return a list.

Regression coverage for extract_datetime_tr, extract_datetime_ar,
extract_datetime_fa, extract_datetime_id, extract_datetime_ms and
extract_datetime_kab, which used to return a bare tuple ``(dt, leftover)``
instead of the ``[dt, leftover]`` list every other supported language
returns. Callers that rely on the documented list shape (mutation,
``+`` concatenation with lists, ``isinstance(x, list)`` checks) broke for
these languages.

Phrases below are reused verbatim from the existing per-language test
suites (test_multilang_invariants.py, test_lang_parity.py, and the
individual test_dates_*.py files) so no new linguistic claims are made
here - this is an API-shape check, not a behavioural one.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2018, 6, 1, 0, 0, 0)  # a Friday, midnight

# One trivially-parseable phrase per supported language, reused from the
# existing test suite (test_multilang_invariants.TOMORROW,
# test_lang_parity._TOMORROW, and per-language test_dates_*.py files).
PHRASE_PER_LANG = {
    "ar": "غداً",
    "ast": "mañana",
    "az": "sabah",
    "bg": "в петък",
    "ca": "demà",
    "cs": "zítra",
    "da": "i morgen",
    "de": "morgen",
    "el": "σήμερα",
    "en": "tomorrow",
    "es": "mañana",
    "et": "homme",
    "eu": "bihar",
    "fa": "فردا",
    "fi": "huomenna",
    "fr": "demain",
    "gl": "mañá",
    "he": "מחר",
    "hr": "u petak",
    "hu": "holnap",
    "id": "besok",
    "it": "domani",
    "kab": "azekka",
    "ms": "esok",
    "nb": "i morgen",
    "nl": "morgen",
    "nn": "i morgon",
    "oc": "deman",
    "pl": "jutro",
    "pt": "amanhã",
    "ro": "mâine",
    "ru": "завтра",
    "sk": "zajtra",
    "sl": "jutri",
    "sv": "imorgon",
    "tr": "yarın",
    "uk": "завтра",
}

# Languages fixed by this change - must return None (not a tuple/falsy
# object other than None) when no date/time is found.
FIXED_LANGS_NO_MATCH = {
    "tr": "merhaba dünya",
    "ar": "مرحبا كيف حالك",
    "fa": "سلام چطوری",
    "id": "halo dunia",
    "ms": "helo dunia",
    "kab": "azul fell-awen amek tellam",
}


class TestExtractDatetimeReturnsListForEveryLanguage(unittest.TestCase):
    def test_every_supported_language_returns_a_list(self):
        for lang, phrase in PHRASE_PER_LANG.items():
            with self.subTest(lang=lang):
                result = extract_datetime(phrase, lang, anchorDate=ANCHOR)
                self.assertIsNotNone(result, f"{lang}: {phrase!r} did not parse")
                self.assertIsInstance(result, list, f"{lang} returned {type(result)}")
                self.assertEqual(len(result), 2, f"{lang} returned {result!r}")
                self.assertIsInstance(result[0], datetime, f"{lang} result[0] wrong type")


class TestFixedLanguagesReturnNoneOnNoMatch(unittest.TestCase):
    def test_no_match_returns_none(self):
        for lang, phrase in FIXED_LANGS_NO_MATCH.items():
            with self.subTest(lang=lang):
                result = extract_datetime(phrase, lang, anchorDate=ANCHOR)
                self.assertIsNone(result, f"{lang}: {phrase!r} should not parse")


if __name__ == "__main__":
    unittest.main()
