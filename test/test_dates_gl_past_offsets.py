"""Regression tests: "N units ago" past-marker offsets for gl.

Markers: prefix "hai" (Wiktionary, papers/linguistics/gl/wiktionary_haber.html; RAG's dicionario page is client-rendered and yielded no static definition text). These phrases must resolve BACKWARD from the anchor.
Expected datetimes are hand-derived from the fixed anchor, never pinned from
engine output. See the three-way differential harness (ours vs dateparser vs
dateutil).
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # fixed, deliberately non-midnight


def _dt(text):
    res = extract_datetime(text, lang="gl", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestPastMarkerOffsets(unittest.TestCase):
    def test_past_0(self):
        self.assertEqual(_dt('hai 2 semanas'), datetime(2017, 6, 13))

    def test_past_1(self):
        self.assertEqual(_dt('hai 3 dias'), datetime(2017, 6, 24))

    def test_past_2(self):
        self.assertEqual(_dt('hai 2 meses'), datetime(2017, 4, 27))

    def test_past_3(self):
        self.assertEqual(_dt('hai 4 anos'), datetime(2013, 6, 27))

    def test_sentence_context(self):
        self.assertEqual(_dt('pasou hai 2 semanas'), datetime(2017, 6, 13))

    def test_symmetry_future_minus_past(self):
        # future offset minus past offset == 2x the offset
        fut = _dt('dentro de 2 semanas')
        past = _dt('hai 2 semanas')
        self.assertEqual((fut - past).days, 28)

    def test_adversarial_non_offset(self):
        # marker word without a numeric offset must not produce a date
        self.assertIsNone(extract_datetime('hai moito tempo', lang='gl', anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
