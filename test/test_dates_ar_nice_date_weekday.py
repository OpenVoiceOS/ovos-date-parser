"""nice_date for Arabic without the weekday.

The ``ar`` templates write the weekday with the Arabic comma (U+060C):
``{weekday}، {day} من {month} {formatted_year}``. Leaving the weekday out
must drop the comma with it, so the date starts on the day."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date

TUESDAY = datetime(2024, 3, 12)


class TestNiceDateArabicNoWeekday(unittest.TestCase):

    def test_full_date(self):
        self.assertEqual(nice_date(TUESDAY, "ar", include_weekday=False),
                         "الثاني عشر من مارس ألفان وأربعة وعشرون")

    def test_same_year(self):
        now = datetime(2024, 1, 5)
        self.assertEqual(nice_date(TUESDAY, "ar", now=now,
                                   include_weekday=False),
                         "الثاني عشر من مارس")

    def test_same_month(self):
        now = datetime(2024, 3, 1)
        self.assertEqual(nice_date(TUESDAY, "ar", now=now,
                                   include_weekday=False),
                         "الثاني عشر")

    def test_matches_the_date_with_weekday(self):
        with_weekday = nice_date(TUESDAY, "ar")
        self.assertTrue(with_weekday.startswith("الثلاثاء، "), with_weekday)
        self.assertEqual(nice_date(TUESDAY, "ar", include_weekday=False),
                         with_weekday[len("الثلاثاء، "):])


if __name__ == "__main__":
    unittest.main()
