"""Regression tests: "N units ago" past-marker offsets for az.

Markers: suffix "əvvəl" / "qabaq" (Wiktionary, papers/linguistics/az/
wiktionary_evvel.html and wiktionary_qabaq.html — the entry glosses "əvvəl" as
postposition "before, ago" with numeric examples such as "üç dəqiqə bundan
əvvəl — three minutes ago", synonym "qabaq", antonym "sonra"). These phrases
must resolve BACKWARD from the anchor. Azerbaijani is unsupported by the
dateparser library, so expected datetimes are hand-derived from the fixed
anchor, never pinned from engine output.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # fixed, deliberately non-midnight


def _dt(text):
    res = extract_datetime(text, lang="az", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestPastMarkerOffsets(unittest.TestCase):
    def test_weeks_evvel(self):
        self.assertEqual(_dt('2 həftə əvvəl'), datetime(2017, 6, 13))

    def test_days_evvel(self):
        self.assertEqual(_dt('2 gün əvvəl'), datetime(2017, 6, 25))

    def test_days_qabaq(self):
        self.assertEqual(_dt('2 gün qabaq'), datetime(2017, 6, 25))

    def test_months_evvel(self):
        self.assertEqual(_dt('3 ay əvvəl'), datetime(2017, 3, 27))

    def test_years_evvel(self):
        self.assertEqual(_dt('2 il əvvəl'), datetime(2015, 6, 27))

    def test_sentence_context(self):
        self.assertEqual(_dt('bu 2 həftə əvvəl oldu'), datetime(2017, 6, 13))

    def test_symmetry_future_minus_past(self):
        # "sonra" is the future antonym of "əvvəl"
        fut = _dt('2 həftə sonra')
        past = _dt('2 həftə əvvəl')
        self.assertEqual((fut - past).days, 28)

    def test_adversarial_non_offset(self):
        # marker word without a numeric offset must not produce a date
        self.assertIsNone(extract_datetime('çoxdan əvvəl', lang='az',
                                           anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
