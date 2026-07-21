"""Regression tests: "N units ago" past-marker offsets for ro.

Marker: prefix "acum" (dexonline.ro, papers/linguistics/ro/dexonline_acum.html).
These phrases must resolve BACKWARD from the anchor. Expected datetimes are
hand-derived from the fixed anchor and cross-checked against the dateparser
library, never pinned from engine output.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # fixed, deliberately non-midnight


def _dt(text):
    res = extract_datetime(text, lang="ro", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestPastMarkerOffsets(unittest.TestCase):
    def test_weeks(self):
        self.assertEqual(_dt('acum 2 săptămâni'), datetime(2017, 6, 13))

    def test_days(self):
        self.assertEqual(_dt('acum 3 zile'), datetime(2017, 6, 24))

    def test_months(self):
        self.assertEqual(_dt('acum 2 luni'), datetime(2017, 4, 27))

    def test_years(self):
        self.assertEqual(_dt('acum 2 ani'), datetime(2015, 6, 27))

    def test_sentence_context(self):
        self.assertEqual(_dt('s-a întâmplat acum 2 săptămâni'),
                         datetime(2017, 6, 13))

    def test_symmetry_future_minus_past(self):
        fut = _dt('peste 2 săptămâni')
        past = _dt('acum 2 săptămâni')
        self.assertEqual((fut - past).days, 28)

    def test_adversarial_non_offset(self):
        # marker word without a numeric offset must not produce a date
        self.assertIsNone(extract_datetime('acum plouă', lang='ro',
                                           anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
