import unittest
from datetime import date, datetime

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
        found = extract_datetime(text, "zh-cn", anchorDate=ANCHOR)
        self.assertIsNotNone(found, text)
        self.assertEqual(found[0].date(), expected, text)
        return found[1]

    def test_tomorrow_weekday_question(self):
        self.assertEqual(self.assertDay("明天星期几", date(2026, 5, 25)), "几")
        self.assertEqual(self.assertDay("明天周几", date(2026, 5, 25)), "几")

    def test_today_weekday_question(self):
        self.assertEqual(self.assertDay("今天星期几", date(2026, 5, 24)), "几")

    def test_other_relative_days_weekday_question(self):
        self.assertDay("后天星期几", date(2026, 5, 26))
        self.assertDay("后天周几", date(2026, 5, 26))
        self.assertDay("昨天星期几", date(2026, 5, 23))
        self.assertDay("前天星期几", date(2026, 5, 22))

    def test_traditional_question_word(self):
        self.assertDay("明天星期幾", date(2026, 5, 25))
        self.assertDay("明天週幾", date(2026, 5, 25))

    def test_forms_that_already_worked_are_unchanged(self):
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
        self.assertIsNone(extract_datetime("你好", "zh-cn", anchorDate=ANCHOR))
        self.assertIsNone(extract_datetime("星期几", "zh-cn",
                                           anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
