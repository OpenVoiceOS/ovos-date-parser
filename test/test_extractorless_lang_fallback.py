import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime, extract_duration

# fy (West Frisian) and an (Aragonese) now ship native
# extract_datetime/extract_duration implementations. They must extract
# real references, degrade gracefully (None, never an exception) on
# gibberish, and never raise NotImplementedError.
NATIVE_LANGS = ("fy", "an")

ANCHOR = datetime(2020, 1, 1)

ADVERSARIAL_INPUTS = ("", "   ", "asdf gibberish qwerty", "25:99",
                      "february 30 2020", "!!!", "0")


class TestNativeDatetime(unittest.TestCase):

    def test_never_raises(self):
        for lang in NATIVE_LANGS:
            for txt in ("in 3 hours",) + ADVERSARIAL_INPUTS:
                try:
                    result = extract_datetime(txt, lang=lang, anchorDate=ANCHOR)
                except NotImplementedError as e:
                    self.fail(f"extract_datetime raised for {lang!r} {txt!r}: {e}")
                if result is not None:
                    # native extractors return [datetime, remainder]
                    self.assertEqual(len(result), 2)
                    self.assertIsInstance(result[0], datetime)

    def test_gibberish_returns_none(self):
        for lang in NATIVE_LANGS:
            self.assertIsNone(
                extract_datetime("asdf gibberish qwerty", lang=lang,
                                 anchorDate=ANCHOR))

    def test_lang_code_variants_do_not_raise(self):
        for code in ("fy-NL", "FY", "an-ES"):
            self.assertIsNone(
                extract_datetime("qwerty nonsense", lang=code, anchorDate=ANCHOR))

    def test_native_extracts_real_reference(self):
        # "tomorrow" in each language resolves one day past the anchor
        self.assertEqual(
            extract_datetime("moarn", lang="fy", anchorDate=ANCHOR)[0],
            datetime(2020, 1, 2))
        self.assertEqual(
            extract_datetime("demán", lang="an", anchorDate=ANCHOR)[0],
            datetime(2020, 1, 2))


class TestNativeDuration(unittest.TestCase):

    def test_no_match_reports_no_duration(self):
        # an/fy vocab does not match the English word "hours"
        for lang in NATIVE_LANGS:
            for txt in ("3 hours", "asdf gibberish qwerty", "0"):
                try:
                    duration, remainder = extract_duration(txt, lang=lang)
                except NotImplementedError as e:
                    self.fail(f"extract_duration raised for {lang!r} {txt!r}: {e}")
                self.assertIsNone(duration)
                self.assertIsInstance(remainder, str)

    def test_native_extracts_real_duration(self):
        duration, _ = extract_duration("2 semanas", lang="an")
        self.assertEqual(duration.days, 14)
        duration, _ = extract_duration("2 wiken", lang="fy")
        self.assertEqual(duration.days, 14)


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
