"""Regression tests: "N units ago" past-marker offsets for sk.

Marker: prefix "pred" governing the instrumental case (Slovenské slovníky /
JÚĽŠ SAV, papers/linguistics/sk/juls_pred.html — "pred ... predl. ... p. rokom,
p. chvíľou"). The sign logic already existed, but the instrumental-plural noun
forms after "pred" (dňami, týždňami, mesiacmi, rokmi) were absent from the
unit-normalisation map, so the phrases parsed to None. These phrases must
resolve BACKWARD from the anchor. Expected datetimes are hand-derived from the
fixed anchor and cross-checked against the dateparser library, never pinned
from engine output.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # fixed, deliberately non-midnight


def _dt(text):
    res = extract_datetime(text, lang="sk", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestPastMarkerOffsets(unittest.TestCase):
    def test_weeks(self):
        self.assertEqual(_dt('pred 2 týždňami'), datetime(2017, 6, 13))

    def test_days(self):
        self.assertEqual(_dt('pred 3 dňami'), datetime(2017, 6, 24))

    def test_months(self):
        self.assertEqual(_dt('pred 3 mesiacmi'), datetime(2017, 3, 27))

    def test_years(self):
        self.assertEqual(_dt('pred 2 rokmi'), datetime(2015, 6, 27))

    def test_sentence_context(self):
        self.assertEqual(_dt('stalo sa to pred 2 týždňami'),
                         datetime(2017, 6, 13))

    def test_symmetry_future_minus_past(self):
        fut = _dt('cez 2 týždne')
        past = _dt('pred 2 týždňami')
        self.assertEqual((fut - past).days, 28)

    def test_adversarial_non_offset(self):
        # marker word without a numeric offset must not produce a date
        self.assertIsNone(extract_datetime('pred domom', lang='sk',
                                           anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
