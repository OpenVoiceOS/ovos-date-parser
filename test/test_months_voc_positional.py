"""months.voc is read by position, so every locale must ship exactly 12 lines.

``scoped_scan`` builds one named regex group per line of ``months.voc`` and
reads the month back as the index of the group that matched. That makes the
file positional: line 1 is January, line 12 is December. A spelling variant
given a line of its own shifts every month after it by one and pushes
December past the end of the table.

French shipped 15 lines and German 13. The result was silent for most of the
year and loud only in December: "la 1 semaine de mars" answered April, and
"la derniere semaine de decembre" raised ``StopIteration`` out of the parse.

Variants now live on the month's own line, separated by ``|``.
"""
import glob
import os
import unittest
from datetime import date

from ovos_date_parser.scoped_scan import (extract_scoped_date,
                                          load_scoped_vocabulary)

ANCHOR = date(2018, 1, 1)
LOCALE_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "ovos_date_parser", "locale")


class TestMonthsVocIsPositional(unittest.TestCase):
    """The structural contract, checked for every locale that ships one."""

    def test_every_months_voc_has_exactly_twelve_lines(self):
        found = sorted(glob.glob(os.path.join(LOCALE_ROOT, "*", "months.voc")))
        self.assertTrue(found, "no months.voc found; the glob is wrong")
        for path in found:
            with self.subTest(locale=os.path.basename(os.path.dirname(path))):
                with open(path, encoding="utf-8") as fh:
                    lines = [ln for ln in fh.read().splitlines() if ln.strip()]
                self.assertEqual(
                    len(lines), 12,
                    f"{path} has {len(lines)} lines; scoped_scan reads this "
                    f"file by position, so a variant belongs on its month's "
                    f"own line separated by '|', never on a line of its own")


class TestFrenchMonthsResolve(unittest.TestCase):
    """Both spellings of every French month, asserted by value."""

    CASES = (
        ("janvier", 1), ("février", 2), ("fevrier", 2), ("mars", 3),
        ("avril", 4), ("mai", 5), ("juin", 6), ("juillet", 7),
        ("août", 8), ("aout", 8), ("septembre", 9), ("octobre", 10),
        ("novembre", 11), ("décembre", 12), ("decembre", 12),
    )

    def test_each_month_answers_its_own_month(self):
        vocab = load_scoped_vocabulary("fr")
        for surface, expected in self.CASES:
            with self.subTest(month=surface):
                out = extract_scoped_date(
                    f"la 1 semaine de {surface}", vocab, ANCHOR)
                self.assertIsNotNone(out, f"{surface}: no scoped date")
                self.assertEqual(out[0].month, expected)

    def test_the_last_week_of_december_does_not_raise(self):
        """The reported phrase. It raised StopIteration at scoped_scan.py."""
        out = extract_scoped_date(
            "la derniere semaine de decembre",
            load_scoped_vocabulary("fr"), ANCHOR)
        self.assertIsNotNone(out)
        self.assertEqual(out[0].month, 12)


class TestGermanMonthsResolve(unittest.TestCase):
    """German shipped 13 lines: maerz beside märz."""

    CASES = (
        ("januar", 1), ("februar", 2), ("märz", 3), ("maerz", 3),
        ("april", 4), ("mai", 5), ("juni", 6), ("juli", 7),
        ("august", 8), ("september", 9), ("oktober", 10),
        ("november", 11), ("dezember", 12),
    )

    def test_each_month_answers_its_own_month(self):
        vocab = load_scoped_vocabulary("de")
        for surface, expected in self.CASES:
            with self.subTest(month=surface):
                out = extract_scoped_date(
                    f"die 1 woche des {surface}", vocab, ANCHOR)
                self.assertIsNotNone(out, f"{surface}: no scoped date")
                self.assertEqual(out[0].month, expected)


class TestAMissizedFileDoesNotRaise(unittest.TestCase):
    """The scan degrades to no-match rather than raising out of a parse.

    The data is fixed, so this drives the guard directly with a vocabulary
    built from a 13-line table. Without the guard this raises StopIteration,
    which is what reached callers before.
    """

    def test_a_group_past_the_twelfth_answers_none_instead_of_raising(self):
        vocab = load_scoped_vocabulary("fr")
        months = list(vocab.months) + ["(?:treizieme)"]   # a 13th line
        broken = vocab.__class__(**{**vocab.__dict__, "months": months})
        try:
            out = extract_scoped_date(
                "la 1 semaine de treizieme", broken, ANCHOR)
        except StopIteration:  # pragma: no cover - the defect being fixed
            self.fail("extract_scoped_date raised StopIteration")
        self.assertIsNone(out)

    def test_the_control_still_matches_on_the_same_broken_table(self):
        """The table above is only broken past the twelfth line, so a real
        month on it must still answer. Without this the test above would
        pass on a vocabulary that matches nothing at all."""
        vocab = load_scoped_vocabulary("fr")
        months = list(vocab.months) + ["(?:treizieme)"]
        broken = vocab.__class__(**{**vocab.__dict__, "months": months})
        out = extract_scoped_date("la 1 semaine de mars", broken, ANCHOR)
        self.assertIsNotNone(out)
        self.assertEqual(out[0].month, 3)


if __name__ == "__main__":
    unittest.main()
