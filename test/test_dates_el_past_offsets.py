"""Regression tests: "N units ago" past-marker offsets for el.

Marker: prefix "πριν", optionally "πριν από" (Λεξικό της κοινής νεοελληνικής /
Triantafyllidis, papers/linguistics/el/triantafyllides_prin.html). These phrases
must resolve BACKWARD from the anchor. Expected datetimes are hand-derived from
the fixed anchor, never pinned from engine output.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # fixed, deliberately non-midnight


def _dt(text):
    res = extract_datetime(text, lang="el", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestPastMarkerOffsets(unittest.TestCase):
    def test_weeks(self):
        self.assertEqual(_dt('πριν 2 εβδομάδες'), datetime(2017, 6, 13))

    def test_days_with_apo(self):
        self.assertEqual(_dt('πριν από 2 μέρες'), datetime(2017, 6, 25))

    def test_days_bare(self):
        self.assertEqual(_dt('πριν 3 μέρες'), datetime(2017, 6, 24))

    def test_months(self):
        self.assertEqual(_dt('πριν 2 μήνες'), datetime(2017, 4, 27))

    def test_years(self):
        self.assertEqual(_dt('πριν 2 χρόνια'), datetime(2015, 6, 27))

    def test_sentence_context(self):
        self.assertEqual(_dt('έγινε πριν 2 εβδομάδες'), datetime(2017, 6, 13))

    def test_symmetry_future_minus_past(self):
        fut = _dt('σε 2 εβδομάδες')
        past = _dt('πριν 2 εβδομάδες')
        self.assertEqual((fut - past).days, 28)

    def test_adversarial_non_offset(self):
        # marker word without a numeric offset must not produce a date
        self.assertIsNone(extract_datetime('πριν λίγο', lang='el',
                                           anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
