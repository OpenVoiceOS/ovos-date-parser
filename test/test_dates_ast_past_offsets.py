"""Regression tests: "N units ago" past-marker offsets for ast.

Markers: prefix "hai"/"fai" and suffix "atras" (DALLA is a client-rendered
SPA, so Wiktionary is cited instead: papers/linguistics/ast/wiktionary_haber.html,
papers/linguistics/ast/wiktionary_facer.html,
papers/linguistics/ast/wiktionary_atras.html). These phrases must resolve
BACKWARD from the anchor. Asturian is unsupported by the dateparser library,
so the expected datetimes are hand-derived from the fixed anchor, never pinned
from engine output.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # fixed, deliberately non-midnight


def _dt(text):
    res = extract_datetime(text, lang="ast", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestPastMarkerOffsets(unittest.TestCase):
    def test_prefix_hai_weeks(self):
        self.assertEqual(_dt('hai 2 selmanes'), datetime(2017, 6, 13))

    def test_prefix_fai_days(self):
        self.assertEqual(_dt('fai 3 dies'), datetime(2017, 6, 24))

    def test_suffix_atras_months(self):
        self.assertEqual(_dt('2 meses atras'), datetime(2017, 4, 27))

    def test_prefix_fai_years(self):
        self.assertEqual(_dt('fai 2 años'), datetime(2015, 6, 27))

    def test_sentence_context(self):
        self.assertEqual(_dt('foi hai 2 selmanes'), datetime(2017, 6, 13))

    def test_symmetry_future_minus_past(self):
        fut = _dt('en 2 selmanes')
        past = _dt('hai 2 selmanes')
        self.assertEqual((fut - past).days, 28)

    def test_adversarial_non_offset(self):
        # marker word without a numeric offset must not produce a date
        self.assertIsNone(extract_datetime('hai muncho tiempu', lang='ast',
                                           anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
