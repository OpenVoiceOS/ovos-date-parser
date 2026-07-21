"""Regression tests: "N units ago" past-marker offsets for en.

Markers: suffix "ago"/"earlier" on hour/minute offsets (Wiktionary, papers/linguistics/en/wiktionary_ago.html; Merriam-Webster blocked by a Cloudflare challenge). These phrases must resolve BACKWARD from the anchor.
Expected datetimes are hand-derived from the fixed anchor, never pinned from
engine output. See the three-way differential harness (ours vs dateparser vs
dateutil).
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # fixed, deliberately non-midnight


def _dt(text):
    res = extract_datetime(text, lang="en", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestPastMarkerOffsets(unittest.TestCase):
    def test_past_0(self):
        self.assertEqual(_dt('2 hours ago'), datetime(2017, 6, 27, 11, 4))

    def test_past_1(self):
        self.assertEqual(_dt('30 minutes ago'), datetime(2017, 6, 27, 12, 34))

    def test_past_2(self):
        self.assertEqual(_dt('45 seconds ago'), datetime(2017, 6, 27, 13, 3, 15))

    def test_past_3(self):
        self.assertEqual(_dt('5 minutes earlier'), datetime(2017, 6, 27, 12, 59))

    def test_sentence_context(self):
        self.assertEqual(_dt('it happened 2 hours ago'), datetime(2017, 6, 27, 11, 4))

    def test_symmetry_future_minus_past(self):
        # future offset minus past offset == 2x the offset
        fut = _dt('in 2 hours')
        past = _dt('2 hours ago')
        self.assertEqual((fut - past).total_seconds() / 3600, 4)

    def test_adversarial_non_offset(self):
        # no past marker -> must not flip to the past
        self.assertEqual(_dt('2 hours'), datetime(2017, 6, 27, 15, 4))


if __name__ == "__main__":
    unittest.main()
