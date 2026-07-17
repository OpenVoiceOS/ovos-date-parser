import unittest
from datetime import datetime

from ovos_date_parser.dates_uk import extract_datetime_uk

# A fixed Tuesday afternoon anchor keeps every assertion deterministic.
ANCHOR = datetime(2017, 6, 27, 13, 0, 0)


def _dt(text):
    return extract_datetime_uk(text, anchor_date=ANCHOR)


class TestUkrainianRelativeDays(unittest.TestCase):
    def test_relative_days(self):
        cases = {
            "сьогодні": datetime(2017, 6, 27, 0, 0, 0),
            "завтра": datetime(2017, 6, 28, 0, 0, 0),
            "післязавтра": datetime(2017, 6, 29, 0, 0, 0),
            "вчора": datetime(2017, 6, 26, 0, 0, 0),
            "позавчора": datetime(2017, 6, 25, 0, 0, 0),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(_dt(text)[0], expected)

    def test_relative_offsets(self):
        # "in 2 hours" from 13:00 -> 15:00
        self.assertEqual(_dt("через 2 години")[0], datetime(2017, 6, 27, 15, 0, 0))
        # "in 30 minutes" from 13:00 -> 13:30
        self.assertEqual(_dt("через 30 хвилин")[0], datetime(2017, 6, 27, 13, 30, 0))


class TestUkrainianWeekdaysAndMonths(unittest.TestCase):
    def test_next_weekday(self):
        # next Monday after a Tuesday anchor
        self.assertEqual(_dt("наступного понеділка")[0].date(),
                         datetime(2017, 7, 3).date())

    def test_genitive_month(self):
        # "1st of September" -> forthcoming 1 September, midnight
        self.assertEqual(_dt("першого вересня")[0], datetime(2017, 9, 1, 0, 0, 0))

    def test_ordinal_day_and_month_with_time(self):
        dt, remainder = _dt("нагадай третього січня о 15:30")
        self.assertEqual(dt, datetime(2018, 1, 3, 15, 30, 0))
        self.assertEqual(remainder, "нагадай")

    def test_explicit_four_digit_year(self):
        self.assertEqual(_dt("двадцятого травня 2020")[0],
                         datetime(2020, 5, 20, 0, 0, 0))


class TestUkrainianClockTimes(unittest.TestCase):
    def test_colon_time(self):
        self.assertEqual(_dt("о 22:00")[0], datetime(2017, 6, 27, 22, 0, 0))

    def test_part_of_day_evening(self):
        # "at 8 in the evening" -> 20:00 same day
        self.assertEqual(_dt("о 8 вечора")[0], datetime(2017, 6, 27, 20, 0, 0))

    def test_part_of_day_day(self):
        self.assertEqual(_dt("о 3 дня")[0], datetime(2017, 6, 27, 15, 0, 0))

    def test_part_of_day_morning_consumes_digit(self):
        # "at 11 in the morning": the hour must come from the digit (11:00),
        # not the morning default of 08:00, and the digit must be consumed.
        dt, remainder = _dt("о 11 ранку")
        self.assertEqual(dt.hour, 11)
        self.assertEqual(dt.minute, 0)
        self.assertNotIn("11", remainder)

    def test_morning_hours_track_the_digit(self):
        for digit, hour in [("7", 7), ("9", 9), ("11", 11)]:
            with self.subTest(digit=digit):
                self.assertEqual(_dt(f"о {digit} ранку")[0].hour, hour)


class TestUkrainianAdversarial(unittest.TestCase):
    def test_empty_returns_none(self):
        self.assertIsNone(extract_datetime_uk("", anchor_date=ANCHOR))

    def test_no_date_returns_none(self):
        self.assertIsNone(_dt("юнк текст без дати"))

    def test_trailing_number_is_not_a_year(self):
        # A bare 1-2 digit number after a month/day must not be read as a
        # year (which previously crashed strptime). It is parsed as an hour.
        for text in ["третього січня 8", "1 січня 10"]:
            with self.subTest(text=text):
                dt = _dt(text)[0]
                self.assertEqual((dt.year, dt.month), (2018, 1))


if __name__ == "__main__":
    unittest.main()
