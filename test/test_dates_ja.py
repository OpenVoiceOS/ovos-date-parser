import unittest
from datetime import date, datetime, time

from ovos_date_parser import extract_datetime

# ja has no extractor of its own: extract_datetime reads it through the
# dateparser fallback, which drops 次の and cannot read 来週の at all.
SUNDAY = datetime(2026, 5, 24, 12, 0)
WEDNESDAY = datetime(2026, 5, 20, 12, 0)
FRIDAY = datetime(2026, 5, 22, 12, 0)


class TestWeekdayWithAWeekWordJa(unittest.TestCase):
    """A weekday named with 次の, 今度の, 来週, 今週 or 先週."""

    def assertDay(self, text, anchor, expected):
        """Assert ``text`` reads as the day ``expected``; return the remainder."""
        found = extract_datetime(text, "ja-jp", anchorDate=anchor)
        self.assertIsNotNone(found, text)
        self.assertEqual(found[0].date(), expected, text)
        return found[1]

    def test_next_friday_question(self):
        """次の金曜日は何日 on a Sunday is the coming Friday, not the last one."""
        self.assertEqual(
            self.assertDay("次の金曜日は何日", SUNDAY, date(2026, 5, 29)),
            "は何日")

    def test_next_weekday(self):
        """次の and 今度の read the first such day after the anchor."""
        self.assertDay("次の金曜日", SUNDAY, date(2026, 5, 29))
        self.assertDay("次の月曜日", SUNDAY, date(2026, 5, 25))
        self.assertDay("今度の金曜日", SUNDAY, date(2026, 5, 29))
        self.assertDay("次の金曜日", WEDNESDAY, date(2026, 5, 22))
        self.assertDay("今度の金曜日", WEDNESDAY, date(2026, 5, 22))
        # on a Friday, the next Friday is a week away
        self.assertDay("次の金曜日", FRIDAY, date(2026, 5, 29))
        self.assertDay("次の金曜", SUNDAY, date(2026, 5, 29))

    def test_weekday_of_next_week(self):
        """来週 reads the day in the week after the anchor's (weeks start Monday)."""
        self.assertDay("来週の金曜日", WEDNESDAY, date(2026, 5, 29))
        self.assertDay("来週金曜日", WEDNESDAY, date(2026, 5, 29))
        self.assertDay("来週の月曜日", WEDNESDAY, date(2026, 5, 25))
        self.assertDay("来週の金曜日", SUNDAY, date(2026, 5, 29))

    def test_weekday_of_last_week(self):
        """先週 reads the day in the week before the anchor's."""
        self.assertDay("先週の金曜日", WEDNESDAY, date(2026, 5, 15))
        self.assertDay("先週の金曜日", SUNDAY, date(2026, 5, 15))
        self.assertDay("先週の月曜日", WEDNESDAY, date(2026, 5, 11))

    def test_weekday_of_this_week(self):
        """今週 reads the day in the anchor's own week."""
        self.assertDay("今週の金曜日", WEDNESDAY, date(2026, 5, 22))
        self.assertDay("今週の月曜日", WEDNESDAY, date(2026, 5, 18))

    def test_sunday(self):
        """日曜日 is a weekday name, not 日 for day."""
        self.assertDay("次の日曜日", WEDNESDAY, date(2026, 5, 24))
        self.assertDay("来週の日曜日", WEDNESDAY, date(2026, 5, 31))

    def test_default_time_is_given_to_the_date(self):
        """The day has no time of its own, so it takes ``default_time``."""
        found = extract_datetime("次の金曜日", "ja-jp", anchorDate=SUNDAY,
                                 default_time=time(8, 15))
        self.assertEqual(found[0], datetime(2026, 5, 29, 8, 15))

    def test_a_clock_is_not_answered_at_midnight(self):
        """The date is read without a clock, so a text with one is not taken."""
        for text in ("来週の金曜日の午後3時に会議", "次の金曜日の朝"):
            found = extract_datetime(text, "ja-jp", anchorDate=SUNDAY)
            if found is not None:
                self.assertNotEqual(found[0].replace(tzinfo=None),
                                    datetime(2026, 5, 29), text)

    def test_forms_without_a_week_word_are_unchanged(self):
        """Texts without the week word still go to dateparser as before."""
        self.assertDay("金曜日", SUNDAY, date(2026, 5, 22))
        self.assertDay("明日", SUNDAY, date(2026, 5, 25))
        self.assertIsNone(extract_datetime("こんにちは", "ja-jp",
                                           anchorDate=SUNDAY))


if __name__ == "__main__":
    unittest.main()
