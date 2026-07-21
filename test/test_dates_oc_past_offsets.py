"""Regression tests: "N units ago" past-marker offsets for oc.

Marker: prefix "fa" (Lo Congrès's Dicodoc is a client-rendered SPA, so
Wiktionary is cited instead: papers/linguistics/oc/wiktionary_far.html and
wiktionary_oc_fa.html — "fa" is the impersonal of "far", analogue of
Catalan/French "fa/il y a"). These phrases must resolve BACKWARD from the
anchor. Occitan is unsupported by the dateparser library, so expected
datetimes are hand-derived from the fixed anchor, never pinned from engine
output.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # fixed, deliberately non-midnight


def _dt(text):
    res = extract_datetime(text, lang="oc", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestPastMarkerOffsets(unittest.TestCase):
    def test_weeks(self):
        self.assertEqual(_dt('fa 2 setmanas'), datetime(2017, 6, 13))

    def test_days(self):
        self.assertEqual(_dt('fa 3 jorns'), datetime(2017, 6, 24))

    def test_months(self):
        self.assertEqual(_dt('fa 3 meses'), datetime(2017, 3, 27))

    def test_years(self):
        self.assertEqual(_dt('fa 2 ans'), datetime(2015, 6, 27))

    def test_sentence_context(self):
        self.assertEqual(_dt('aquò arribèt fa 2 setmanas'),
                         datetime(2017, 6, 13))

    def test_symmetry_future_minus_past(self):
        fut = _dt('dins 2 setmanas')
        past = _dt('fa 2 setmanas')
        self.assertEqual((fut - past).days, 28)

    def test_adversarial_non_offset(self):
        # marker word without a numeric offset must not produce a date
        self.assertIsNone(extract_datetime('fa pauc', lang='oc',
                                           anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
