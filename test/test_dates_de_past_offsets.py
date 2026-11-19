"""Regression tests: "N units ago" past-marker offsets for de.

Markers: prefix "vor" + Dativ (DWDS, papers/linguistics/de/dwds_vor.html; Duden had no static entry for bare "vor"). These phrases must resolve BACKWARD from the anchor.
Expected datetimes are hand-derived from the fixed anchor, never pinned from
engine output. See the three-way differential harness (ours vs dateparser vs
dateutil).
"""
import unittest
from datetime import datetime


from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # fixed, deliberately non-midnight


def _dt(text):
    res = extract_datetime(text, lang="de", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestPastMarkerOffsets(unittest.TestCase):
    # a counted offset keeps the anchor's clock (routing ruling, class 1)
    def test_past_0(self):
        self.assertEqual(_dt('vor 2 wochen'), datetime(2017, 6, 13, 13, 4))

    def test_past_1(self):
        self.assertEqual(_dt('vor 3 tagen'), datetime(2017, 6, 24, 13, 4))

    def test_past_2(self):
        self.assertEqual(_dt('vor 2 monaten'), datetime(2017, 4, 27, 13, 4))

    def test_past_3(self):
        self.assertEqual(_dt('vor 4 jahren'), datetime(2013, 6, 27, 13, 4))

    def test_sentence_context(self):
        self.assertEqual(_dt('das war vor 2 wochen'), datetime(2017, 6, 13, 13, 4))

    def test_symmetry_future_minus_past(self):
        # future offset minus past offset == 2x the offset
        fut = _dt('in 2 wochen')
        past = _dt('vor 2 wochen')
        self.assertEqual((fut - past).days, 28)

    def test_quarter_to_is_a_clock_not_an_offset(self):
        # "Viertel vor fünf" is 4:45 (Duden, "Viertel": "[ein] Viertel vor
        # drei"), and a lone spoken hour takes the next twelve-hour reading
        # (ruling 17): 16:45 at a 13:04 anchor
        self.assertEqual(_dt('viertel vor 5'), datetime(2017, 6, 27, 16, 45))


if __name__ == "__main__":
    unittest.main()
