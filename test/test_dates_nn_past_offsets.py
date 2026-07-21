"""Regression tests: "N units ago" past-marker offsets for nn.

Markers: suffix "sidan" (Nynorskordboka via ord.uib.no JSON API, papers/linguistics/nn/ordbokene_nn_sidan_article65396.json; ordbokene.no itself is client-rendered). These phrases must resolve BACKWARD from the anchor.
Expected datetimes are hand-derived from the fixed anchor, never pinned from
engine output. See the three-way differential harness (ours vs dateparser vs
dateutil).
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # fixed, deliberately non-midnight


def _dt(text):
    res = extract_datetime(text, lang="nn", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestPastMarkerOffsets(unittest.TestCase):
    def test_past_0(self):
        self.assertEqual(_dt('2 veker sidan'), datetime(2017, 6, 13))

    def test_past_1(self):
        self.assertEqual(_dt('3 dagar sidan'), datetime(2017, 6, 24))

    def test_past_2(self):
        self.assertEqual(_dt('4 år sidan'), datetime(2013, 6, 27))

    def test_sentence_context(self):
        self.assertEqual(_dt('det hende 2 veker sidan'), datetime(2017, 6, 13))

    def test_symmetry_future_minus_past(self):
        # future offset minus past offset == 2x the offset
        fut = _dt('om 2 veker')
        past = _dt('2 veker sidan')
        self.assertEqual((fut - past).days, 28)

    def test_adversarial_non_offset(self):
        # marker word without a numeric offset must not produce a date
        self.assertIsNone(extract_datetime('lenge sidan', lang='nn', anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
