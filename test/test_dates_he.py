import unittest
from datetime import datetime, timedelta

from ovos_date_parser.dates_he import (
    nice_year_he, nice_weekday_he, nice_month_he, nice_day_he,
    nice_date_he, nice_date_time_he, nice_time_he,
    extract_datetime_he, extract_duration_he,
)
from ovos_date_parser.duration import DurationResolution

# 2018-06-05 is a Tuesday
ANCHOR = datetime(2018, 6, 5, 9, 0, 0)


class TestNiceYearHe(unittest.TestCase):
    def test_known_years(self):
        self.assertEqual(nice_year_he(datetime(1984, 1, 1)),
                         "אלף תשע מאות שמונים וארבעה")
        self.assertEqual(nice_year_he(datetime(2000, 1, 1)), "אלפיים")

    def test_bc_marker(self):
        self.assertTrue(nice_year_he(datetime(44, 1, 1), bc=True)
                        .endswith("לפני הספירה"))

    def test_sweep_non_empty(self):
        for y in range(1, 3000, 7):
            self.assertTrue(nice_year_he(datetime(y, 1, 1)).strip())


class TestNiceWeekdayHe(unittest.TestCase):
    def test_all_weekdays(self):
        # 2018-06-04 is a Monday
        expected = ["יום שני", "יום שלישי", "יום רביעי", "יום חמישי",
                    "יום שישי", "שבת", "יום ראשון"]
        for i, name in enumerate(expected):
            self.assertEqual(nice_weekday_he(datetime(2018, 6, 4) +
                                             timedelta(days=i)), name)


class TestNiceMonthHe(unittest.TestCase):
    def test_all_months(self):
        expected = ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני",
                    "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"]
        for m, name in enumerate(expected, start=1):
            self.assertEqual(nice_month_he(datetime(2018, m, 15)), name)


class TestNiceDayHe(unittest.TestCase):
    def test_dmy(self):
        self.assertEqual(nice_day_he(datetime(2018, 6, 5)), "5 יוני")

    def test_mdy(self):
        self.assertEqual(nice_day_he(datetime(2018, 6, 5), date_format='MDY'),
                         "יוני 5")

    def test_no_month(self):
        self.assertEqual(nice_day_he(datetime(2018, 6, 5), include_month=False),
                         "5")


class TestNiceDateHe(unittest.TestCase):
    def test_full(self):
        self.assertEqual(
            nice_date_he(datetime(2018, 6, 5)),
            "יום שלישי, חמישה ביוני אלפיים ושמונה עשר")

    def test_no_weekday(self):
        self.assertEqual(
            nice_date_he(datetime(2018, 6, 5), include_weekday=False),
            "חמישה ביוני אלפיים ושמונה עשר")

    def test_relative_today_tomorrow_yesterday(self):
        self.assertEqual(nice_date_he(ANCHOR, ANCHOR), "היום")
        self.assertEqual(
            nice_date_he(ANCHOR + timedelta(days=1), ANCHOR), "מחר")
        self.assertEqual(
            nice_date_he(ANCHOR - timedelta(days=1), ANCHOR), "אתמול")

    def test_sweep_over_month(self):
        for d in range(1, 29):
            self.assertTrue(nice_date_he(datetime(2020, 2, d)).strip())


class TestNiceTimeHe(unittest.TestCase):
    def test_display(self):
        self.assertEqual(
            nice_time_he(datetime(2018, 1, 1, 15, 30), speech=False), "3:30")
        self.assertEqual(
            nice_time_he(datetime(2018, 1, 1, 15, 30), speech=False,
                         use_24hour=True), "15:30")

    def test_half(self):
        self.assertEqual(nice_time_he(datetime(2018, 1, 1, 15, 30)),
                         "שלוש וחצי")

    def test_quarter_past(self):
        self.assertEqual(nice_time_he(datetime(2018, 1, 1, 3, 15)),
                         "שלוש ורבע")

    def test_quarter_to(self):
        self.assertEqual(nice_time_he(datetime(2018, 1, 1, 3, 45)),
                         "רבע לארבע")

    def test_midnight_noon(self):
        self.assertEqual(nice_time_he(datetime(2018, 1, 1, 0, 0)),
                         "שתים עשרה")
        self.assertEqual(nice_time_he(datetime(2018, 1, 1, 12, 0)),
                         "שתים עשרה")

    def test_arbitrary_minute(self):
        self.assertEqual(nice_time_he(datetime(2018, 1, 1, 5, 20)),
                         "חמש ועשרים")

    def test_24hour_spoken(self):
        self.assertEqual(
            nice_time_he(datetime(2018, 1, 1, 14, 5), use_24hour=True),
            "ארבע עשרה אפס חמש")

    def test_sweep_all_times(self):
        for h in range(24):
            for m in range(0, 60, 5):
                dt = datetime(2018, 1, 1, h, m)
                self.assertTrue(nice_time_he(dt).strip())
                self.assertTrue(nice_time_he(dt, use_24hour=True).strip())
                self.assertTrue(
                    nice_time_he(dt, use_24hour=False, use_ampm=True).strip())


class TestNiceDateTimeHe(unittest.TestCase):
    def test_combined(self):
        got = nice_date_time_he(ANCHOR, ANCHOR)
        self.assertEqual(got, "היום בשעה תשע")


class TestExtractDatetimeHe(unittest.TestCase):
    def _dt(self, text):
        res = extract_datetime_he(text, ANCHOR)
        return None if res is None else res[0]

    def test_empty_returns_none(self):
        self.assertIsNone(extract_datetime_he(""))

    def test_whitespace_returns_none(self):
        self.assertIsNone(extract_datetime_he("   "))

    def test_none_input(self):
        self.assertIsNone(extract_datetime_he(None))

    def test_no_date_returns_none(self):
        self.assertIsNone(extract_datetime_he("שלום עולם", ANCHOR))

    def test_today(self):
        self.assertEqual(self._dt("היום"), datetime(2018, 6, 5, 0, 0))

    def test_tomorrow(self):
        self.assertEqual(self._dt("מחר"), datetime(2018, 6, 6, 0, 0))

    def test_day_after_tomorrow(self):
        self.assertEqual(self._dt("מחרתיים"), datetime(2018, 6, 7, 0, 0))

    def test_yesterday(self):
        self.assertEqual(self._dt("אתמול"), datetime(2018, 6, 4, 0, 0))

    def test_day_before_yesterday(self):
        self.assertEqual(self._dt("שלשום"), datetime(2018, 6, 3, 0, 0))

    def test_in_three_days(self):
        self.assertEqual(self._dt("בעוד שלושה ימים"),
                         datetime(2018, 6, 8, 0, 0))

    def test_in_two_weeks_digits(self):
        self.assertEqual(self._dt("בעוד 2 שבועות"),
                         datetime(2018, 6, 19, 0, 0))

    def test_days_ago(self):
        self.assertEqual(self._dt("לפני 3 ימים"),
                         datetime(2018, 6, 2, 0, 0))

    def test_next_week(self):
        self.assertEqual(self._dt("שבוע הבא"), datetime(2018, 6, 12, 0, 0))

    def test_next_month(self):
        self.assertEqual(self._dt("חודש הבא"), datetime(2018, 7, 5, 0, 0))

    def test_next_year(self):
        self.assertEqual(self._dt("שנה הבאה"), datetime(2019, 6, 5, 0, 0))

    def test_explicit_date(self):
        self.assertEqual(self._dt("15 ביוני"), datetime(2018, 6, 15, 0, 0))

    def test_explicit_date_with_year(self):
        self.assertEqual(self._dt("15 ביוני 2020"),
                         datetime(2020, 6, 15, 0, 0))

    def test_weekday_saturday(self):
        # anchor is Tuesday 2018-06-05, next Saturday is 2018-06-09
        self.assertEqual(self._dt("שבת"), datetime(2018, 6, 9, 0, 0))

    def test_weekday_last(self):
        # last Sunday before Tuesday 2018-06-05 -> 2018-06-03
        self.assertEqual(self._dt("יום ראשון שעבר"),
                         datetime(2018, 6, 3, 0, 0))

    def test_time_hhmm(self):
        self.assertEqual(self._dt("מחר בשעה 15:30"),
                         datetime(2018, 6, 6, 15, 30))

    def test_time_spoken_half(self):
        self.assertEqual(self._dt("מחר בשעה שלוש וחצי"),
                         datetime(2018, 6, 6, 3, 30))

    def test_malformed_time_ignored(self):
        # 25:99 is not a valid clock; no date should be found
        self.assertIsNone(extract_datetime_he("בשעה 25:99", ANCHOR))

    def test_remainder_text(self):
        res = extract_datetime_he("פגישה מחר", ANCHOR)
        self.assertIsNotNone(res)
        self.assertEqual(res[1], "פגישה")

    def test_ascii_digits_and_words_equivalent(self):
        a = self._dt("בעוד 3 ימים")
        b = self._dt("בעוד שלושה ימים")
        self.assertEqual(a, b)


class TestExtractDurationHe(unittest.TestCase):
    def test_none_on_empty(self):
        self.assertIsNone(extract_duration_he(""))

    def test_hours_and_minutes(self):
        dur, rem = extract_duration_he("שלוש שעות ועשר דקות")
        self.assertEqual(dur, timedelta(hours=3, minutes=10))

    def test_days(self):
        dur, rem = extract_duration_he("5 ימים")
        self.assertEqual(dur, timedelta(days=5))

    def test_minutes_only(self):
        dur, rem = extract_duration_he("קבע טיימר ל10 דקות")
        self.assertEqual(dur, timedelta(minutes=10))

    def test_no_duration(self):
        dur, rem = extract_duration_he("שלום עולם")
        self.assertIsNone(dur)

    def test_total_seconds_resolution(self):
        dur, rem = extract_duration_he(
            "2 דקות", resolution=DurationResolution.TOTAL_SECONDS)
        self.assertEqual(dur, 120)


if __name__ == "__main__":
    unittest.main()
