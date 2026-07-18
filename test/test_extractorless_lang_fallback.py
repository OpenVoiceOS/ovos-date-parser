import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime, extract_duration

# Languages that ship formatting (nice_*) helpers but no native
# extract_datetime/extract_duration implementation. Asking to EXTRACT
# from these must degrade gracefully instead of raising.
EXTRACTORLESS_LANGS = ("fy", "an")

ANCHOR = datetime(2020, 1, 1)

ADVERSARIAL_INPUTS = ("", "   ", "asdf gibberish qwerty", "25:99",
                      "february 30 2020", "!!!", "0")


class TestExtractorlessDatetime(unittest.TestCase):

    def test_never_raises_not_implemented(self):
        for lang in EXTRACTORLESS_LANGS:
            for txt in ("in 3 hours",) + ADVERSARIAL_INPUTS:
                try:
                    result = extract_datetime(txt, lang=lang, anchorDate=ANCHOR)
                except NotImplementedError as e:
                    self.fail(f"extract_datetime raised for {lang!r} {txt!r}: {e}")
                # either no extraction (None) or a sensible fallback tuple
                if result is not None:
                    self.assertIsInstance(result, tuple)
                    self.assertEqual(len(result), 2)
                    self.assertIsInstance(result[0], datetime)

    def test_gibberish_returns_none(self):
        for lang in EXTRACTORLESS_LANGS:
            self.assertIsNone(
                extract_datetime("asdf gibberish qwerty", lang=lang,
                                 anchorDate=ANCHOR))

    def test_lang_code_variants_do_not_raise(self):
        for code in ("fy-NL", "FY", "an-ES"):
            self.assertIsNone(
                extract_datetime("qwerty nonsense", lang=code, anchorDate=ANCHOR))


class TestExtractorlessDuration(unittest.TestCase):

    def test_never_raises_and_reports_no_duration(self):
        for lang in EXTRACTORLESS_LANGS:
            for txt in ("3 hours",) + ADVERSARIAL_INPUTS:
                try:
                    duration, remainder = extract_duration(txt, lang=lang)
                except NotImplementedError as e:
                    self.fail(f"extract_duration raised for {lang!r} {txt!r}: {e}")
                self.assertIsNone(duration)
                self.assertEqual(remainder, txt)


class TestImplementedLangsUnchanged(unittest.TestCase):
    """A language with a native extractor still extracts, and still
    returns None (never a spurious fallback) when nothing matches."""

    def test_english_still_extracts(self):
        result = extract_datetime("in 3 hours", lang="en",
                                  anchorDate=ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], datetime(2020, 1, 1, 3, 0))

    def test_english_no_match_returns_none(self):
        self.assertIsNone(
            extract_datetime("asdf gibberish qwerty", lang="en",
                             anchorDate=ANCHOR))

    def test_english_duration_still_extracts(self):
        duration, _ = extract_duration("3 hours", lang="en")
        self.assertIsNotNone(duration)


if __name__ == "__main__":
    unittest.main()
