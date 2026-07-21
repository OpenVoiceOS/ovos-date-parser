import unittest
from datetime import date, datetime

from ovos_date_parser import (
    Hemisphere, Season, DateTimeResolution,
    get_week_range, get_weekend_range, get_month_range, get_year_range,
    get_decade_range, get_century_range, get_millennium_range,
    get_season_range, get_week_number, get_date_ordinal,
    date_to_season, season_to_date, next_season_date, last_season_date,
)


class TestRanges(unittest.TestCase):
    def test_week_range(self):
        # 1994-02-27 was a sunday
        self.assertEqual(get_week_range(date(1994, 2, 27)),
                         (date(1994, 2, 21), date(1994, 2, 27)))
        # 2026-07-16 is a thursday
        self.assertEqual(get_week_range(date(2026, 7, 16)),
                         (date(2026, 7, 13), date(2026, 7, 19)))
        # monday maps onto itself
        self.assertEqual(get_week_range(date(2026, 7, 13)),
                         (date(2026, 7, 13), date(2026, 7, 19)))

    def test_weekend_range(self):
        # from a weekday: the upcoming weekend
        self.assertEqual(get_weekend_range(date(2026, 7, 16)),
                         (date(2026, 7, 18), date(2026, 7, 19)))
        # from a saturday or sunday: the current weekend
        self.assertEqual(get_weekend_range(date(2026, 7, 18)),
                         (date(2026, 7, 18), date(2026, 7, 19)))
        self.assertEqual(get_weekend_range(date(2026, 7, 19)),
                         (date(2026, 7, 18), date(2026, 7, 19)))

    def test_month_range(self):
        self.assertEqual(get_month_range(date(1994, 2, 27)),
                         (date(1994, 2, 1), date(1994, 2, 28)))
        # leap year february
        self.assertEqual(get_month_range(date(2024, 2, 10)),
                         (date(2024, 2, 1), date(2024, 2, 29)))
        # december does not overflow into the next year
        self.assertEqual(get_month_range(date(2026, 12, 5)),
                         (date(2026, 12, 1), date(2026, 12, 31)))

    def test_year_range(self):
        self.assertEqual(get_year_range(date(1994, 2, 27)),
                         (date(1994, 1, 1), date(1994, 12, 31)))

    def test_decade_century_millennium_ranges(self):
        ref = date(1994, 2, 27)
        self.assertEqual(get_decade_range(ref),
                         (date(1990, 1, 1), date(1999, 12, 31)))
        self.assertEqual(get_century_range(ref),
                         (date(1900, 1, 1), date(1999, 12, 31)))
        self.assertEqual(get_millennium_range(ref),
                         (date(1000, 1, 1), date(1999, 12, 31)))
        ref = date(2112, 2, 27)
        self.assertEqual(get_decade_range(ref),
                         (date(2110, 1, 1), date(2119, 12, 31)))
        self.assertEqual(get_century_range(ref),
                         (date(2100, 1, 1), date(2199, 12, 31)))
        self.assertEqual(get_millennium_range(ref),
                         (date(2000, 1, 1), date(2999, 12, 31)))

    def test_week_number(self):
        # ISO-8601: 2026-01-01 is a thursday, week 1
        self.assertEqual(get_week_number(date(2026, 1, 1)), 1)
        # 2021-01-01 is a friday, ISO week 53 of 2020
        self.assertEqual(get_week_number(date(2021, 1, 1)), 53)
        self.assertEqual(get_week_number(date(1994, 2, 27)), 8)


class TestSeasons(unittest.TestCase):
    def test_date_to_season_north(self):
        self.assertEqual(date_to_season(date(2026, 4, 10)), Season.SPRING)
        self.assertEqual(date_to_season(date(2026, 7, 16)), Season.SUMMER)
        self.assertEqual(date_to_season(date(2026, 10, 1)), Season.FALL)
        self.assertEqual(date_to_season(date(2026, 1, 15)), Season.WINTER)
        # season boundaries: last days belong to the season
        self.assertEqual(date_to_season(date(2026, 5, 31)), Season.SPRING)
        self.assertEqual(date_to_season(date(2026, 8, 31)), Season.SUMMER)
        self.assertEqual(date_to_season(date(2026, 11, 30)), Season.FALL)
        self.assertEqual(date_to_season(date(2026, 12, 1)), Season.WINTER)
        self.assertEqual(date_to_season(date(2024, 2, 29)), Season.WINTER)

    def test_date_to_season_south(self):
        south = Hemisphere.SOUTH
        self.assertEqual(date_to_season(date(2026, 4, 10), south),
                         Season.FALL)
        self.assertEqual(date_to_season(date(2026, 7, 16), south),
                         Season.WINTER)
        self.assertEqual(date_to_season(date(2026, 10, 1), south),
                         Season.SPRING)
        self.assertEqual(date_to_season(date(2026, 1, 15), south),
                         Season.SUMMER)

    def test_autumn_is_fall(self):
        self.assertEqual(Season.AUTUMN, Season.FALL)
        self.assertEqual(date_to_season(date(2026, 10, 1)), Season.AUTUMN)

    def test_season_to_date(self):
        self.assertEqual(season_to_date(Season.SPRING, 2026),
                         date(2026, 3, 1))
        self.assertEqual(season_to_date(Season.SUMMER, 2026),
                         date(2026, 6, 1))
        self.assertEqual(season_to_date(Season.FALL, 2026),
                         date(2026, 9, 1))
        self.assertEqual(season_to_date(Season.WINTER, 2026),
                         date(2026, 12, 1))
        # southern hemisphere is shifted by two seasons
        south = Hemisphere.SOUTH
        self.assertEqual(season_to_date(Season.SPRING, 2026, south),
                         date(2026, 9, 1))
        self.assertEqual(season_to_date(Season.SUMMER, 2026, south),
                         date(2026, 12, 1))
        self.assertEqual(season_to_date(Season.FALL, 2026, south),
                         date(2026, 3, 1))
        self.assertEqual(season_to_date(Season.WINTER, 2026, south),
                         date(2026, 6, 1))
        # a date can stand in for the year
        self.assertEqual(season_to_date(Season.SPRING, date(2026, 7, 16)),
                         date(2026, 3, 1))

    def test_next_and_last_season_date(self):
        ref = date(2026, 7, 16)  # northern summer
        self.assertEqual(next_season_date(Season.FALL, ref),
                         date(2026, 9, 1))
        self.assertEqual(next_season_date(Season.SPRING, ref),
                         date(2027, 3, 1))
        self.assertEqual(last_season_date(Season.SPRING, ref),
                         date(2026, 3, 1))
        self.assertEqual(last_season_date(Season.FALL, ref),
                         date(2025, 9, 1))
        # on the start day itself, "next" is today
        self.assertEqual(next_season_date(Season.SUMMER, date(2026, 6, 1)),
                         date(2026, 6, 1))

    def test_season_range(self):
        self.assertEqual(get_season_range(date(2026, 7, 16)),
                         (date(2026, 6, 1), date(2026, 8, 31)))
        self.assertEqual(get_season_range(date(2026, 4, 10)),
                         (date(2026, 3, 1), date(2026, 5, 31)))
        self.assertEqual(get_season_range(date(2026, 10, 1)),
                         (date(2026, 9, 1), date(2026, 11, 30)))
        # winter wraps the new year
        self.assertEqual(get_season_range(date(2026, 12, 15)),
                         (date(2026, 12, 1), date(2027, 2, 28)))
        self.assertEqual(get_season_range(date(2027, 1, 15)),
                         (date(2026, 12, 1), date(2027, 2, 28)))
        # leap year february
        self.assertEqual(get_season_range(date(2024, 2, 10)),
                         (date(2023, 12, 1), date(2024, 2, 29)))
        # southern hemisphere: july is winter, december starts summer
        south = Hemisphere.SOUTH
        self.assertEqual(get_season_range(date(2026, 7, 16), south),
                         (date(2026, 6, 1), date(2026, 8, 31)))
        self.assertEqual(get_season_range(date(2026, 12, 15), south),
                         (date(2026, 12, 1), date(2027, 2, 28)))


class TestDateOrdinals(unittest.TestCase):
    def test_day_ordinals(self):
        ref = date(2026, 7, 16)
        self.assertEqual(
            get_date_ordinal(1, ref, DateTimeResolution.DAY_OF_MONTH),
            date(2026, 7, 1))
        self.assertEqual(
            get_date_ordinal(-1, ref, DateTimeResolution.DAY_OF_MONTH),
            date(2026, 7, 31))
        self.assertEqual(
            get_date_ordinal(-1, date(2026, 2, 5),
                             DateTimeResolution.DAY_OF_MONTH),
            date(2026, 2, 28))
        self.assertEqual(
            get_date_ordinal(1, ref, DateTimeResolution.DAY_OF_YEAR),
            date(2026, 1, 1))
        # 2026 is not a leap year: day 100 is april 10
        self.assertEqual(
            get_date_ordinal(100, ref, DateTimeResolution.DAY_OF_YEAR),
            date(2026, 4, 10))
        self.assertEqual(
            get_date_ordinal(-1, ref, DateTimeResolution.DAY_OF_YEAR),
            date(2026, 12, 31))
        self.assertEqual(
            get_date_ordinal(1, ref, DateTimeResolution.DAY_OF_DECADE),
            date(2020, 1, 1))
        self.assertEqual(
            get_date_ordinal(-1, ref, DateTimeResolution.DAY_OF_DECADE),
            date(2029, 12, 31))
        self.assertEqual(
            get_date_ordinal(1, ref, DateTimeResolution.DAY_OF_CENTURY),
            date(2000, 1, 1))
        self.assertEqual(
            get_date_ordinal(-1, ref, DateTimeResolution.DAY_OF_CENTURY),
            date(2099, 12, 31))
        self.assertEqual(
            get_date_ordinal(-1, ref, DateTimeResolution.DAY_OF_MILLENNIUM),
            date(2999, 12, 31))
        # the very first day
        self.assertEqual(get_date_ordinal(1, ref, DateTimeResolution.DAY),
                         date(1, 1, 1))

    def test_week_ordinals(self):
        ref = date(2026, 7, 16)
        # weeks resolve to their monday; the first week of july 2026
        # is the week containing july 7 (monday july 6)
        self.assertEqual(
            get_date_ordinal(1, ref, DateTimeResolution.WEEK_OF_MONTH),
            date(2026, 7, 6))
        self.assertEqual(
            get_date_ordinal(-1, ref, DateTimeResolution.WEEK_OF_MONTH),
            date(2026, 7, 27))
        self.assertEqual(
            get_date_ordinal(1, ref, DateTimeResolution.WEEK_OF_YEAR),
            date(2026, 1, 5))
        self.assertEqual(
            get_date_ordinal(-1, ref, DateTimeResolution.WEEK_OF_YEAR),
            date(2026, 12, 28))
        with self.assertRaises(ValueError):
            get_date_ordinal(5, ref, DateTimeResolution.WEEK_OF_MONTH)

    def test_month_ordinals(self):
        ref = date(2026, 7, 16)
        self.assertEqual(
            get_date_ordinal(1, ref, DateTimeResolution.MONTH_OF_YEAR),
            date(2026, 1, 1))
        self.assertEqual(
            get_date_ordinal(7, ref, DateTimeResolution.MONTH_OF_YEAR),
            date(2026, 7, 1))
        self.assertEqual(
            get_date_ordinal(-1, ref, DateTimeResolution.MONTH_OF_YEAR),
            date(2026, 12, 1))
        self.assertEqual(
            get_date_ordinal(15, ref, DateTimeResolution.MONTH_OF_DECADE),
            date(2021, 3, 1))
        self.assertEqual(
            get_date_ordinal(-1, ref, DateTimeResolution.MONTH_OF_CENTURY),
            date(2099, 12, 1))

    def test_year_ordinals(self):
        ref = date(2026, 7, 16)
        self.assertEqual(get_date_ordinal(2026, ref, DateTimeResolution.YEAR),
                         date(2026, 1, 1))
        self.assertEqual(
            get_date_ordinal(1, ref, DateTimeResolution.YEAR_OF_DECADE),
            date(2020, 1, 1))
        self.assertEqual(
            get_date_ordinal(-1, ref, DateTimeResolution.YEAR_OF_DECADE),
            date(2029, 1, 1))
        self.assertEqual(
            get_date_ordinal(50, ref, DateTimeResolution.YEAR_OF_CENTURY),
            date(2049, 1, 1))
        self.assertEqual(
            get_date_ordinal(500, ref,
                             DateTimeResolution.YEAR_OF_MILLENNIUM),
            date(2499, 1, 1))

    def test_decade_century_millennium_ordinals(self):
        ref = date(2026, 7, 16)
        # the 1st decade is years 1-10, the 203rd started in 2020
        self.assertEqual(get_date_ordinal(1, ref, DateTimeResolution.DECADE),
                         date(1, 1, 1))
        self.assertEqual(
            get_date_ordinal(203, ref, DateTimeResolution.DECADE),
            date(2020, 1, 1))
        self.assertEqual(
            get_date_ordinal(3, ref, DateTimeResolution.DECADE_OF_CENTURY),
            date(2020, 1, 1))
        self.assertEqual(get_date_ordinal(21, ref,
                                          DateTimeResolution.CENTURY),
                         date(2000, 1, 1))
        self.assertEqual(
            get_date_ordinal(1, ref,
                             DateTimeResolution.CENTURY_OF_MILLENNIUM),
            date(2000, 1, 1))
        self.assertEqual(get_date_ordinal(3, ref,
                                          DateTimeResolution.MILLENNIUM),
                         date(2000, 1, 1))

    def test_before_present(self):
        ref = date(2026, 7, 16)
        self.assertEqual(
            get_date_ordinal(0, ref, DateTimeResolution.BEFORE_PRESENT_YEAR),
            date(1950, 1, 1))
        self.assertEqual(
            get_date_ordinal(100, ref,
                             DateTimeResolution.BEFORE_PRESENT_YEAR),
            date(1850, 1, 1))
        self.assertEqual(
            get_date_ordinal(2, ref,
                             DateTimeResolution.BEFORE_PRESENT_DECADE),
            date(1930, 1, 1))
        self.assertEqual(
            get_date_ordinal(1, ref, DateTimeResolution.BEFORE_PRESENT_DAY),
            date(1949, 12, 31))
        with self.assertRaises(OverflowError):
            get_date_ordinal(-1, ref,
                             DateTimeResolution.BEFORE_PRESENT_YEAR)

    def test_datetime_ref_is_accepted(self):
        ref = datetime(2026, 7, 16, 12, 30)
        self.assertEqual(
            get_date_ordinal(-1, ref, DateTimeResolution.DAY_OF_MONTH),
            date(2026, 7, 31))


if __name__ == "__main__":
    unittest.main()
