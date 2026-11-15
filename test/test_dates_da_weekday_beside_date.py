"""A Danish weekday beside a calendar date is part of the question, not an
offset from the anchor.

"4. juli på en søndag" asks whether 4 July is a Sunday; the date is 4 July and
the weekday word stays in the remainder for the caller to check.  The anchor is
a Friday, so the old reading added the two days to Sunday onto 4 July.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 10, 23, 12, 0)


class TestWeekdayBesideDate(unittest.TestCase):
    def test_question_about_the_weekday_of_a_date(self):
        got = extract_datetime("4. juli på en søndag", lang="da-DK",
                               anchorDate=ANCHOR)
        # next 4 July after 2026-10-23 is in 2027
        self.assertEqual(got[0], datetime(2027, 7, 4))
        self.assertIn("søndag", got[1])

    def test_is_the_date_a_weekday(self):
        got = extract_datetime("er den 4. juli en søndag", lang="da-DK",
                               anchorDate=ANCHOR)
        self.assertEqual(got[0], datetime(2027, 7, 4))
        self.assertIn("søndag", got[1])

    def test_weekday_before_the_date(self):
        got = extract_datetime("søndag 4. juli", lang="da-DK", anchorDate=ANCHOR)
        self.assertEqual(got[0], datetime(2027, 7, 4))

    def test_bare_weekday_is_unchanged(self):
        got = extract_datetime("på søndag", lang="da-DK", anchorDate=ANCHOR)
        self.assertEqual(got[0], datetime(2026, 10, 25))

    def test_date_alone_is_unchanged(self):
        got = extract_datetime("4. juli", lang="da-DK", anchorDate=ANCHOR)
        self.assertEqual(got[0], datetime(2027, 7, 4))


if __name__ == "__main__":
    unittest.main()
