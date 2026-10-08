# Copyright 2026 OpenVoiceOS
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""One ``.voc`` per month, because a ``.voc`` is an unordered set.

OVOS-INTENT-2 §4.3, on the slot-free roles:

    `.entity`, `.voc`, and `.blacklist` share the **slot-free** format: a list
    of templates using expansion `(a|b)` / `[x]` only, **no named slots**. They
    are syntactically and semantically identical, and a loader parses all three
    the same way -- each **loads as** the union of the sample sets of all its
    lines (OVOS-INTENT-1 §4).

A union has no order and no fixed length. So a month table cannot be a file
whose Nth line is the Nth month: that reading makes a spelling on its own line
shift every month after it, and it makes a missing month answer as its
neighbour. Per-month granularity needs a file per month.

``month_1.voc`` .. ``month_12.voc`` hold every spelling of one
month each. The order lives in ``_MONTH_VOC``, in code, where the file NAME
maps to the month number. Nothing reads a line number.
"""
import os
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from ovos_date_parser.scoped_scan import (_MONTH_VOC, extract_scoped_date,
                                          load_scoped_vocabulary)

ANCHOR = date(2018, 1, 1)
LOCALE_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "ovos_date_parser", "locale")


class TestEveryShippedLocaleHasTwelveMonthFiles(unittest.TestCase):
    """The parser's own locales are migrated; nothing is left on the old path."""

    def test_twelve_files_per_locale(self):
        for lang in sorted(os.listdir(LOCALE_ROOT)):
            with self.subTest(locale=lang):
                for name in _MONTH_VOC:
                    path = os.path.join(LOCALE_ROOT, lang, f"{name}.voc")
                    self.assertTrue(os.path.exists(path),
                                    f"{lang} is missing {name}.voc")

    def test_no_month_file_is_empty(self):
        for lang in sorted(os.listdir(LOCALE_ROOT)):
            for name in _MONTH_VOC:
                with self.subTest(locale=lang, voc=name):
                    text = Path(LOCALE_ROOT, lang, f"{name}.voc").read_text(
                        encoding="utf-8")
                    self.assertTrue([ln for ln in text.splitlines() if ln.strip()],
                                    f"{lang}/{name}.voc has no spelling")


class TestSpellingsOfOneMonthAgree(unittest.TestCase):
    """A month spelled two ways is one month, and neither spelling depends on
    which line it sits on."""

    CASES = (
        # locale, (spelling, spelling, ...), month
        ("fr", ("février", "fevrier"), 2),
        ("fr", ("août", "aout"), 8),
        ("fr", ("décembre", "decembre"), 12),
        ("de", ("märz", "maerz"), 3),
    )

    def test_two_spellings_resolve_to_the_same_month(self):
        for lang, spellings, month in self.CASES:
            vocab = load_scoped_vocabulary(lang)
            for spelling in spellings:
                with self.subTest(locale=lang, spelling=spelling):
                    phrase = (f"la 1 semaine de {spelling}" if lang == "fr"
                              else f"die 1 woche des {spelling}")
                    out = extract_scoped_date(phrase, vocab, ANCHOR)
                    self.assertIsNotNone(out, f"{spelling!r} did not match")
                    self.assertEqual(out[0].month, month)


class TestAMonthFileTakesAnyNumberOfSpellings(unittest.TestCase):
    """Three spellings on three lines, in any order, all answer.

    This is what the old single-file table could not express: a third spelling
    had nowhere to go that did not move another month.
    """

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="month-voc-")
        self.addCleanup(tmp.cleanup)
        self.root = tmp.name
        os.mkdir(os.path.join(self.root, "fr"))
        for name in os.listdir(os.path.join(LOCALE_ROOT, "fr")):
            if name.endswith(".voc"):
                shutil.copy(os.path.join(LOCALE_ROOT, "fr", name),
                            os.path.join(self.root, "fr", name))
        self.march = Path(self.root, "fr", "month_3.voc")

    def test_three_spellings_all_resolve(self):
        self.march.write_text("mars\nmarss\nmarz\n", encoding="utf-8")
        vocab = load_scoped_vocabulary("fr", self.root)
        for spelling in ("mars", "marss", "marz"):
            with self.subTest(spelling=spelling):
                out = extract_scoped_date(
                    f"la 1 semaine de {spelling}", vocab, ANCHOR)
                self.assertIsNotNone(out, f"{spelling!r} did not match")
                self.assertEqual(out[0].month, 3)

    def test_the_line_order_does_not_matter(self):
        """The control for the case above: the same three lines reversed give
        the same answers, which a positional reader could not promise."""
        self.march.write_text("marz\nmarss\nmars\n", encoding="utf-8")
        vocab = load_scoped_vocabulary("fr", self.root)
        for spelling in ("mars", "marss", "marz"):
            with self.subTest(spelling=spelling):
                out = extract_scoped_date(
                    f"la 1 semaine de {spelling}", vocab, ANCHOR)
                self.assertIsNotNone(out)
                self.assertEqual(out[0].month, 3)

    def test_a_missing_month_file_is_filled_from_the_fallback_root(self):
        """Deleting a month from THIS root does not lose the month.

        The reader falls back per file to chronologia's packaged root, which
        ships the same ``month_<n>.voc`` names for every locale it carries.
        That fallback is the documented behaviour this loader inherits, and
        sharing the names is what lets it work per month rather than per
        locale. So a tree part-way through a migration is completed by the
        other root rather than left short.
        """
        self.march.unlink()
        vocab = load_scoped_vocabulary("fr", self.root)
        self.assertEqual(len(vocab.months), 12)
        out = extract_scoped_date("la 1 semaine de mars", vocab, ANCHOR)
        self.assertIsNotNone(out, "March came from neither root")
        self.assertEqual(out[0].month, 3)

    def test_a_missing_month_fails_loud_when_no_root_has_it(self):
        """The loud path: a locale no fallback root carries.

        ``zz`` exists only in the tree this test builds, so nothing can fill
        a gap in it. The message names the locale and the month file.
        """
        zz = os.path.join(self.root, "zz")
        os.mkdir(zz)
        for name in os.listdir(os.path.join(LOCALE_ROOT, "fr")):
            if name.endswith(".voc"):
                shutil.copy(os.path.join(LOCALE_ROOT, "fr", name),
                            os.path.join(zz, name))
        os.unlink(os.path.join(zz, "month_3.voc"))
        with self.assertRaises(FileNotFoundError) as caught:
            load_scoped_vocabulary("zz", self.root)
        message = str(caught.exception)
        self.assertIn("zz", message, "the locale is not named")
        self.assertIn("month_3.voc", message, "the month is not named")

    def test_the_control_zz_loads_twelve_when_complete(self):
        """So the raise above is the missing file and not the invented
        locale."""
        zz = os.path.join(self.root, "zz")
        os.mkdir(zz)
        for name in os.listdir(os.path.join(LOCALE_ROOT, "fr")):
            if name.endswith(".voc"):
                shutil.copy(os.path.join(LOCALE_ROOT, "fr", name),
                            os.path.join(zz, name))
        vocab = load_scoped_vocabulary("zz", self.root)
        self.assertEqual(len(vocab.months), 12)

    def test_the_control_the_untouched_copy_still_loads(self):
        """So the raise above is the missing file and not the copy itself."""
        vocab = load_scoped_vocabulary("fr", self.root)
        self.assertEqual(len(vocab.months), 12)


if __name__ == "__main__":
    unittest.main()
