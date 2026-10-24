import unittest
from datetime import date, datetime, time

from ovos_date_parser import extract_datetime

# zh has no extractor of its own: extract_datetime reads it through the
# dateparser fallback. Noon keeps the date the same in every timezone the
# fallback may convert the answer to.
ANCHOR = datetime(2026, 5, 24, 12, 0)  # a Sunday


class TestRelativeDayBeforeWeekdayQuestionZh(unittest.TestCase):
    """A relative day written straight against 星期几 or 周几.

    dateparser joins the English words it translates a zh chunk into
    without a space, so 明天星期几 became "in 1 dayweek" and nothing was
    read. With 是 in between, the chunk stops at 明天 and it always worked.
    """

    def assertDay(self, text, expected):
        """Assert ``text`` reads as the day ``expected``; return the remainder."""
        found = extract_datetime(text, "zh-cn", anchorDate=ANCHOR)
        self.assertIsNotNone(found, text)
        self.assertEqual(found[0].date(), expected, text)
        return found[1]

    def test_tomorrow_weekday_question(self):
        """明天星期几 and 明天周几 read tomorrow and leave 几."""
        self.assertEqual(self.assertDay("明天星期几", date(2026, 5, 25)), "几")
        self.assertEqual(self.assertDay("明天周几", date(2026, 5, 25)), "几")

    def test_today_weekday_question(self):
        """今天星期几 reads today."""
        self.assertEqual(self.assertDay("今天星期几", date(2026, 5, 24)), "几")

    def test_other_relative_days_weekday_question(self):
        """后天, 昨天 and 前天 read their own day."""
        self.assertDay("后天星期几", date(2026, 5, 26))
        self.assertDay("后天周几", date(2026, 5, 26))
        self.assertDay("昨天星期几", date(2026, 5, 23))
        self.assertDay("前天星期几", date(2026, 5, 22))

    def test_traditional_question_word(self):
        """The traditional 幾 and 週 read the same day."""
        self.assertDay("明天星期幾", date(2026, 5, 25))
        self.assertDay("明天週幾", date(2026, 5, 25))

    def test_forms_that_already_worked_are_unchanged(self):
        """The forms the fallback read before keep their date and remainder."""
        self.assertEqual(self.assertDay("明天是星期几", date(2026, 5, 25)),
                         "是星期几")
        self.assertEqual(self.assertDay("明天礼拜几", date(2026, 5, 25)),
                         "礼拜几")
        self.assertEqual(self.assertDay("明天 星期几", date(2026, 5, 25)),
                         "几")
        self.assertEqual(self.assertDay("后天是星期几", date(2026, 5, 26)),
                         "是星期几")
        self.assertEqual(self.assertDay("明天", date(2026, 5, 25)), "")

    def test_no_date_still_reads_nothing(self):
        """A text with no date in it still reads as None."""
        self.assertIsNone(extract_datetime("你好", "zh-cn", anchorDate=ANCHOR))
        self.assertIsNone(extract_datetime("星期几", "zh-cn",
                                           anchorDate=ANCHOR))

    def test_default_time_is_given_to_the_date(self):
        """The date has no time of its own, so it takes ``default_time``."""
        found = extract_datetime("明天星期几", "zh-cn", anchorDate=ANCHOR,
                                 default_time=time(8, 15))
        self.assertEqual(found[0].date(), date(2026, 5, 25))
        self.assertEqual((found[0].hour, found[0].minute), (8, 15))

    def test_only_the_date_read_leaves_the_remainder(self):
        """A second copy of the phrase stays in the remainder."""
        self.assertEqual(self.assertDay("明天星期几，明天星期几",
                                        date(2026, 5, 25)),
                         "几，明天星期几")

    def test_a_clock_it_cannot_read_stays_none(self):
        """A clock the retry would drop is not answered with the anchor's."""
        for text in ("明天下午三点", "今天下午3点"):
            self.assertIsNone(
                extract_datetime(text, "zh-cn", anchorDate=ANCHOR), text)


if __name__ == "__main__":
    unittest.main()
