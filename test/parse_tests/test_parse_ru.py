import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime


class TestExtractDateTimeRU(unittest.TestCase):
    # Thursday, 6 June 2024, 06:00
    ANCHOR = datetime(2024, 6, 6, 6, 0)

    def extract(self, text, expected_dt, expected_leftover=""):
        result = extract_datetime(text, "ru", anchorDate=self.ANCHOR)
        self.assertIsNotNone(result, text)
        self.assertEqual(result[0], expected_dt, text)
        self.assertEqual(result[1], expected_leftover, text)

    def test_today(self):
        self.extract("сегодня", datetime(2024, 6, 6, 0, 0))

    def test_tomorrow(self):
        self.extract("завтра", datetime(2024, 6, 7, 0, 0))

    def test_day_after_tomorrow(self):
        self.extract("послезавтра", datetime(2024, 6, 8, 0, 0))

    def test_yesterday(self):
        self.extract("вчера", datetime(2024, 6, 5, 0, 0))

    def test_day_before_yesterday(self):
        self.extract("позавчера", datetime(2024, 6, 4, 0, 0))

    def test_weekday_accusative(self):
        # anchor is Thursday; accusative weekday forms in "в <day>"
        self.extract("в среду", datetime(2024, 6, 12, 0, 0))
        self.extract("в пятницу", datetime(2024, 6, 7, 0, 0))

    def test_month_genitive(self):
        # June 5 already passed relative to the anchor -> next year
        self.extract("5 июня", datetime(2025, 6, 5, 0, 0))

    def test_part_of_day_morning(self):
        self.extract("в 7 утра", datetime(2024, 6, 6, 7, 0))

    def test_part_of_day_evening(self):
        self.extract("в 9 вечера", datetime(2024, 6, 6, 21, 0))

    def test_part_of_day_afternoon(self):
        self.extract("в 5 дня", datetime(2024, 6, 6, 17, 0))

    def test_part_of_day_night_wraps(self):
        # 3am already passed at the 06:00 anchor -> next morning
        self.extract("в 3 часа ночи", datetime(2024, 6, 7, 3, 0))

    def test_relative_hours(self):
        self.extract("через 3 часа", datetime(2024, 6, 6, 9, 0))

    def test_relative_minutes(self):
        self.extract("через 10 минут", datetime(2024, 6, 6, 6, 10))

    def test_relative_seconds(self):
        self.extract("через 5 секунд", datetime(2024, 6, 6, 6, 0, 5))

    def test_explicit_clock(self):
        self.extract("в 14:30", datetime(2024, 6, 6, 14, 30))

    def test_leap_day_rolls_to_next_leap_year(self):
        # 29 february does not exist in 2025/2026/2027 -> next is 2028
        self.extract("29 февраля", datetime(2028, 2, 29, 0, 0))

    def test_leap_day_from_non_leap_anchor(self):
        result = extract_datetime("29 февраля", "ru",
                                  anchorDate=datetime(2023, 1, 1, 0, 0))
        self.assertIsNotNone(result)
        self.assertEqual(result[0], datetime(2024, 2, 29, 0, 0))

    def test_leap_day_in_sentence(self):
        result = extract_datetime("встреча 29 февраля в 15:00", "ru",
                                  anchorDate=self.ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], datetime(2028, 2, 29, 15, 0))
        self.assertEqual(result[1], "встреча")


class TestExtractDateTimeRUAdversarial(unittest.TestCase):
    ANCHOR = datetime(2024, 6, 6, 6, 0)

    def test_empty_string(self):
        self.assertIsNone(extract_datetime("", "ru", anchorDate=self.ANCHOR))

    def test_no_date(self):
        self.assertIsNone(
            extract_datetime("привет как дела", "ru", anchorDate=self.ANCHOR))

    def test_impossible_day_does_not_crash(self):
        # "45 march" is not a real day: must return None, never raise/hang
        self.assertIsNone(
            extract_datetime("45 марта", "ru", anchorDate=self.ANCHOR))

    def test_lang_code_variant(self):
        result = extract_datetime("завтра", "ru-RU", anchorDate=self.ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], datetime(2024, 6, 7, 0, 0))


if __name__ == "__main__":
    unittest.main()
