"""Regression tests: "N units ago" past-marker offsets for cs.

Markers: prefix "před" (Internetová jazyková příručka, papers/linguistics/cs/ujc_pred.html). These phrases must resolve BACKWARD from the anchor.
Expected datetimes are hand-derived from the fixed anchor, never pinned from
engine output. See the three-way differential harness (ours vs dateparser vs
dateutil).
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # fixed, deliberately non-midnight


def _dt(text):
    res = extract_datetime(text, lang="cs", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestPastMarkerOffsets(unittest.TestCase):
    def test_past_0(self):
        self.assertEqual(_dt('před 2 týdny'), datetime(2017, 6, 13))

    def test_past_1(self):
        self.assertEqual(_dt('před 3 dny'), datetime(2017, 6, 24))

    def test_past_2(self):
        self.assertEqual(_dt('před 2 měsíci'), datetime(2017, 4, 27))

    def test_sentence_context(self):
        self.assertEqual(_dt('stalo se to před 2 týdny'), datetime(2017, 6, 13))

    def test_symmetry_future_minus_past(self):
        # future offset minus past offset == 2x the offset
        fut = _dt('za 2 týdny')
        past = _dt('před 2 týdny')
        self.assertEqual((fut - past).days, 28)

    def test_adversarial_non_offset(self):
        # marker word without a numeric offset must not produce a date
        self.assertIsNone(extract_datetime('před domem', lang='cs', anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
