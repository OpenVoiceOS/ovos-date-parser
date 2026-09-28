"""months.voc is read by position, so every locale must ship exactly 12 lines.

``scoped_scan`` builds one named regex group per line of ``months.voc`` and
reads the month back as the index of the group that matched. That makes the
file positional: line 1 is January, line 12 is December. A spelling variant
given a line of its own shifts every month after it by one and pushes
December past the end of the table.

French shipped 15 lines and German 13. The result was silent for most of the
year and loud only in December: "la 1 semaine de mars" answered April, and
"la derniere semaine de decembre" raised ``StopIteration`` out of the parse.

Variants live on the month's own line, as one group: ``(février|fevrier)``.
A bare ``février|fevrier`` is malformed (OVOS-INTENT-1 section 3.6, "a pipe
outside a group"), and ovos-spec-tools 1.14.0a1 skips such a line rather than
splitting it, which took French back to 11 months. The loader therefore reads
this file line by line and expands each line on its own, so line N's samples
stay line N's whatever a line contains.
"""
import glob
import os
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from ovos_spec_tools import expand, read_resource_file
from ovos_spec_tools.expansion import MalformedTemplate

from ovos_date_parser.eras_scan import _positional_voc_reader
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
                    f"file by position, so a second spelling belongs on its "
                    f"month's own line as one group, (a|b), never on a line "
                    f"of its own (OVOS-INTENT-1 §3.6)")


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


class TestAMalformedLineRaisesOutOfTheLoader(unittest.TestCase):
    """The loader's half of the posture, pinned so it cannot drift back.

    ``_positional_voc_reader`` expands each line with no guard, so a line
    ovos-spec-tools rejects raises ``MalformedTemplate`` out of the loader
    instead of being skipped. Skipping is the defect this module exists to
    close: a dropped line shifts every month after it, and the caller reads
    the shifted table as a month table.

    This is the LOADER. ``TestAMissizedFileDoesNotRaise`` below is the SCAN,
    on a table already in memory, and it still degrades to no-match. The two
    are different layers, not a contradiction: loading fails loud, scanning
    fails soft.
    """

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="months-voc-")
        self.addCleanup(tmp.cleanup)
        self.root = tmp.name
        os.mkdir(os.path.join(self.root, "fr"))
        self.voc = os.path.join(self.root, "fr", "months.voc")

    def _write(self, second_line):
        good = ["janvier", second_line, "mars", "avril", "mai", "juin",
                "juillet", "aout", "septembre", "octobre", "novembre",
                "decembre"]
        with open(self.voc, "w", encoding="utf-8") as fh:
            fh.write("\n".join(good) + "\n")

    def test_a_bare_pipe_raises(self):
        # the exact form OVOS-INTENT-1 3.6 forbids and this PR removed
        self._write("février|fevrier")
        read = _positional_voc_reader("fr", self.root)
        with self.assertRaises(MalformedTemplate):
            read("months")

    def test_the_control_a_well_formed_group_loads_twelve(self):
        """Without this the test above could pass on a tree that never loads."""
        self._write("(février|fevrier)")
        read = _positional_voc_reader("fr", self.root)
        lines = read("months")
        self.assertEqual(len(lines), 12)
        self.assertEqual(sorted(lines[1]), ["fevrier", "février"])


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


class TestAShortMonthsVocIsRefused(unittest.TestCase):
    """T-4767: the count guard was one-sided and a short file answered wrong.

    ``months.voc`` is read BY POSITION, so a file with a month missing shifts
    every month after the gap. Before this guard, an 11-line ``fr`` tree with
    ``mars`` deleted answered:

        le 31 jour de avril   ->  2018-03-31    (31 March, for April)
        la 1 semaine de avril ->  2018-03-05
        la derniere semaine de avril -> 2018-03-26

    silently, with no warning and no exception. The old guard only refused an
    index PAST the twelfth, which a short file never produces.

    The two halves of a wrong count are not symmetric and the fix is not
    either. MORE than twelve: only the entries past the twelfth cannot be
    named, so a real month still answers - pinned by
    ``TestAMissizedFileDoesNotRaise`` below. FEWER than twelve: every entry at
    or after the gap is the wrong month and nothing says where the gap is, so
    no index is trustworthy and the table is refused whole.
    """

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="months-voc-short-")
        self.addCleanup(tmp.cleanup)
        self.root = tmp.name
        src = os.path.join(LOCALE_ROOT, "fr")
        dst = os.path.join(self.root, "fr")
        os.mkdir(dst)
        for name in os.listdir(src):
            if name.endswith(".voc"):
                shutil.copy(os.path.join(src, name), os.path.join(dst, name))
        self.voc = os.path.join(dst, "months.voc")

    def _drop_month(self, index):
        """Delete one month line, leaving 11."""
        with open(self.voc, encoding="utf-8") as fh:
            lines = [ln for ln in fh.read().splitlines() if ln.strip()]
        self.assertEqual(len(lines), 12, "the fr fixture is not 12 lines")
        del lines[index]
        with open(self.voc, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

    def test_the_loader_refuses_an_eleven_line_file(self):
        """The loud half: the loader knows the locale and the count."""
        self._drop_month(2)                       # drop mars
        with self.assertRaises(ValueError) as caught:
            load_scoped_vocabulary("fr", self.root)
        message = str(caught.exception)
        self.assertIn("fr", message, "the locale is not named")
        self.assertIn("11", message, "the count is not named")

    def test_the_control_the_untouched_fixture_still_loads(self):
        """Without this the case above could pass on a tree that never loads
        for some unrelated reason."""
        vocab = load_scoped_vocabulary("fr", self.root)
        self.assertEqual(len(vocab.months), 12)

    def test_avril_is_not_march_on_a_short_table(self):
        """The reported symptom, driven through the scan.

        The loader now refuses the file, so the short table is built in
        memory to reach the scan's own backstop - the path a caller that did
        not come through the loader takes.
        """
        vocab = load_scoped_vocabulary("fr", self.root)
        months = list(vocab.months)
        del months[2]                             # mars, as on disk
        short = vocab.__class__(**{**vocab.__dict__, "months": months})
        for utterance in ("le 3 jour de avril",
                          "la 1 semaine de avril",
                          "la derniere semaine de avril"):
            with self.subTest(utterance=utterance):
                out = extract_scoped_date(utterance, short, ANCHOR)
                self.assertIsNone(
                    out, f"{utterance!r} answered {out[0] if out else None} "
                         f"on an 11-entry table")

    def test_the_control_the_same_utterances_answer_on_a_full_table(self):
        """So the Nones above are the guard and not phrases that never
        matched. April, not March, on the untouched fixture.

        ``le 31 jour de avril`` is not among the controls: on a CORRECT table
        it raises ``ValueError: day is out of range for month`` from
        ``ranges.get_date_ordinal``, because April has 30 days. That is a
        separate pre-existing defect, reproduced on dev and filed as T-6763;
        it is why the reported symptom could answer 31 March at all, since
        the shifted table landed it on a month that has a 31st.
        """
        vocab = load_scoped_vocabulary("fr", self.root)
        for utterance, day in (("la 1 semaine de avril", 2),
                               ("le 3 jour de avril", 4)):
            with self.subTest(utterance=utterance):
                out = extract_scoped_date(utterance, vocab, ANCHOR)
                self.assertIsNotNone(out, f"{utterance!r} did not match")
                self.assertEqual(out[0].month, 4,
                                 f"{utterance!r} answered month "
                                 f"{out[0].month}, expected April")


class TestTheLoadedTableIsTwelveLong(unittest.TestCase):
    """The invariant the file-line count alone does not carry.

    A 12-line file can still load as 11 or 13 months: the reader expands
    templates, so a line it rejects contributes nothing and a line carrying a
    group contributes one entry per branch. ovos-spec-tools 1.14.0a1 turned the
    first case real. Assert the LOADED table, not only the file.
    """

    def test_every_locale_loads_exactly_twelve_months(self):
        found = sorted(glob.glob(os.path.join(LOCALE_ROOT, "*", "months.voc")))
        self.assertTrue(found, "no months.voc found; the glob is wrong")
        for path in found:
            lang = os.path.basename(os.path.dirname(path))
            with self.subTest(locale=lang):
                vocab = load_scoped_vocabulary(lang)
                self.assertEqual(
                    len(vocab.months), 12,
                    f"{lang} loaded {len(vocab.months)} months from a "
                    f"12-line file; the loader must keep one entry per line")

    def test_both_french_spellings_are_on_one_month_fragment(self):
        """February's fragment carries both spellings, which is what keeps the
        variant off a line of its own."""
        vocab = load_scoped_vocabulary("fr")
        february = vocab.months[1]
        self.assertIn("f", february)
        self.assertIn("vrier", february)
        self.assertIn("fevrier", february)
        self.assertEqual(vocab.months[11].count("cembre"), 2,
                         f"December lost a spelling: {vocab.months[11]}")


class TestEveryShippedVocLineExpands(unittest.TestCase):
    """No shipped .voc line may be skipped or rejected by the reader.

    A skipped line is silent: the file keeps its line count and the surface
    form simply stops matching. This is the check that catches it, over every
    locale and every phrase set rather than months.voc alone.
    """

    def test_no_line_is_rejected_and_none_expands_to_nothing(self):
        found = sorted(glob.glob(os.path.join(LOCALE_ROOT, "*", "*.voc")))
        self.assertTrue(found, "no .voc found; the glob is wrong")
        for path in found:
            for number, line in enumerate(read_resource_file(Path(path)), 1):
                with self.subTest(file=os.path.relpath(path, LOCALE_ROOT),
                                  line=number):
                    try:
                        samples = expand(line)
                    except Exception as e:
                        self.fail(f"{line!r} is rejected: "
                                  f"{type(e).__name__}: {e}")
                    self.assertTrue(samples,
                                    f"{line!r} expands to no sample")


if __name__ == "__main__":
    unittest.main()
