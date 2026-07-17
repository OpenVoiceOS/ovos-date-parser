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

    # --- dual forms (single-word "two X") ---
    def test_dual_two_days(self):
        self.assertEqual(self._dt("בעוד יומיים"),
                         datetime(2018, 6, 7, 0, 0))

    def test_dual_two_weeks(self):
        self.assertEqual(self._dt("בעוד שבועיים"),
                         datetime(2018, 6, 19, 0, 0))

    def test_dual_two_months(self):
        self.assertEqual(self._dt("בעוד חודשיים"),
                         datetime(2018, 8, 5, 0, 0))

    def test_dual_two_years(self):
        self.assertEqual(self._dt("בעוד שנתיים"),
                         datetime(2020, 6, 5, 0, 0))

    def test_dual_two_hours(self):
        self.assertEqual(self._dt("בעוד שעתיים"),
                         datetime(2018, 6, 5, 11, 0))

    def test_dual_days_ago(self):
        self.assertEqual(self._dt("לפני יומיים"),
                         datetime(2018, 6, 3, 0, 0))

    def test_dual_weeks_ago(self):
        self.assertEqual(self._dt("לפני שבועיים"),
                         datetime(2018, 5, 22, 0, 0))

    # --- relative clock offsets count from the anchor time ---
    def test_offset_three_hours(self):
        self.assertEqual(self._dt("בעוד שלוש שעות"),
                         datetime(2018, 6, 5, 12, 0))

    def test_offset_ten_minutes(self):
        self.assertEqual(self._dt("בעוד 10 דקות"),
                         datetime(2018, 6, 5, 9, 10))

    def test_offset_an_hour(self):
        self.assertEqual(self._dt("בעוד שעה"),
                         datetime(2018, 6, 5, 10, 0))

    def test_hours_ago(self):
        self.assertEqual(self._dt("לפני שעתיים"),
                         datetime(2018, 6, 5, 7, 0))

    # --- both spoken numeral genders extract identically ---
    def test_gender_day_counts(self):
        self.assertEqual(self._dt("בעוד שלושה ימים"),
                         self._dt("בעוד שלוש ימים"))

    def test_gender_hour_offsets(self):
        self.assertEqual(self._dt("בעוד שלוש שעות"),
                         self._dt("בעוד שלושה שעות"))

    def test_gender_clock_hour(self):
        # feminine spoken "בשעה שלוש" and the digit form agree
        self.assertEqual(self._dt("מחר בשעה שלוש"),
                         self._dt("מחר בשעה 3"))


class TestRealSentencesHe(unittest.TestCase):
    """Full natural sentences a user actually speaks.

    Each case asserts both the parsed datetime and the remainder text
    (the spoken command left after the date/time words are consumed).
    Expected values are checked against Modern Hebrew usage, never
    pinned from engine output. Sentences that exercise idioms the parser
    does not yet cover (e.g. an explicit hour combined with a part-of-day
    word meaning PM, day-of-month or weekday carrying a ב/ל proclitic,
    or "half" attached to an hour offset) are intentionally left out.
    """

    def _parse(self, text):
        res = extract_datetime_he(text, ANCHOR)
        self.assertIsNotNone(res, f"expected a datetime for: {text}")
        return res[0], res[1]

    # --- reminders / relative day offsets ---
    def test_remind_in_two_days(self):
        dt, rem = self._parse("תזכיר לי בעוד יומיים")
        self.assertEqual(dt, datetime(2018, 6, 7, 0, 0))
        self.assertEqual(rem, "תזכיר לי")

    def test_remind_in_two_days_with_task(self):
        dt, rem = self._parse("תזכיר לי בעוד יומיים לקנות חלב")
        self.assertEqual(dt, datetime(2018, 6, 7, 0, 0))
        self.assertEqual(rem, "תזכיר לי לקנות חלב")

    def test_remind_in_three_days_call_mom(self):
        dt, rem = self._parse("תזכיר לי בעוד שלושה ימים להתקשר לאמא")
        self.assertEqual(dt, datetime(2018, 6, 8, 0, 0))
        self.assertEqual(rem, "תזכיר לי להתקשר לאמא")

    def test_remind_in_two_weeks(self):
        dt, rem = self._parse("תזכיר לי בעוד שבועיים")
        self.assertEqual(dt, datetime(2018, 6, 19, 0, 0))
        self.assertEqual(rem, "תזכיר לי")

    def test_meeting_in_two_months(self):
        dt, rem = self._parse("פגישה בעוד חודשיים")
        self.assertEqual(dt, datetime(2018, 8, 5, 0, 0))
        self.assertEqual(rem, "פגישה")

    def test_remind_in_two_years_renew_passport(self):
        dt, rem = self._parse("תזכיר לי בעוד שנתיים לחדש דרכון")
        self.assertEqual(dt, datetime(2020, 6, 5, 0, 0))
        self.assertEqual(rem, "תזכיר לי לחדש דרכון")

    def test_what_did_i_do_yesterday(self):
        dt, rem = self._parse("מה עשיתי אתמול")
        self.assertEqual(dt, datetime(2018, 6, 4, 0, 0))
        self.assertEqual(rem, "מה עשיתי")

    # --- relative clock offsets counted from the anchor time ---
    def test_alert_in_three_hours(self):
        dt, rem = self._parse("קבע התראה בעוד שלוש שעות")
        self.assertEqual(dt, datetime(2018, 6, 5, 12, 0))
        self.assertEqual(rem, "קבע התראה")

    def test_alert_in_45_minutes(self):
        dt, rem = self._parse("קבע התראה בעוד 45 דקות")
        self.assertEqual(dt, datetime(2018, 6, 5, 9, 45))
        self.assertEqual(rem, "קבע התראה")

    # --- explicit clock times ---
    def test_doctor_tomorrow_hhmm(self):
        dt, rem = self._parse("פגישה עם הרופא מחר בשעה 15:30")
        self.assertEqual(dt, datetime(2018, 6, 6, 15, 30))
        self.assertEqual(rem, "פגישה עם הרופא")

    def test_meeting_hhmm_then_tomorrow(self):
        dt, rem = self._parse("פגישה בשעה 14:00 מחר")
        self.assertEqual(dt, datetime(2018, 6, 6, 14, 0))
        self.assertEqual(rem, "פגישה")

    def test_wake_me_six_morning(self):
        dt, rem = self._parse("תעיר אותי בשעה 6 בבוקר")
        self.assertEqual(dt, datetime(2018, 6, 6, 6, 0))
        self.assertEqual(rem, "תעיר אותי")

    # --- spoken (feminine) clock hours and half/quarter idioms ---
    def test_alarm_half_past_seven_morning(self):
        dt, rem = self._parse("האזעקה בשעה שבע וחצי בבוקר")
        self.assertEqual(dt, datetime(2018, 6, 6, 7, 30))
        self.assertEqual(rem, "האזעקה")

    def test_talk_quarter_past_three(self):
        dt, rem = self._parse("נדבר בשעה שלוש ורבע")
        self.assertEqual(dt, datetime(2018, 6, 6, 3, 15))
        self.assertEqual(rem, "נדבר")

    def test_remind_tomorrow_eight_morning_take_pill(self):
        dt, rem = self._parse("תזכיר לי מחר בשעה שמונה בבוקר לקחת תרופה")
        self.assertEqual(dt, datetime(2018, 6, 6, 8, 0))
        self.assertEqual(rem, "תזכיר לי לקחת תרופה")

    def test_alert_half_past_eight_morning_tomorrow(self):
        dt, rem = self._parse("קבע התראה בשעה שמונה וחצי בבוקר מחר")
        self.assertEqual(dt, datetime(2018, 6, 6, 8, 30))
        self.assertEqual(rem, "קבע התראה")

    # --- part-of-day only (no explicit hour) ---
    def test_meeting_tomorrow_morning(self):
        dt, rem = self._parse("קבע פגישה מחר בבוקר")
        self.assertEqual(dt, datetime(2018, 6, 6, 8, 0))
        self.assertEqual(rem, "קבע פגישה")

    def test_event_day_after_tomorrow_evening(self):
        dt, rem = self._parse("האירוע מחרתיים בערב")
        self.assertEqual(dt, datetime(2018, 6, 7, 20, 0))
        self.assertEqual(rem, "האירוע")

    def test_remind_today_evening(self):
        dt, rem = self._parse("תזכיר לי היום בערב")
        self.assertEqual(dt, datetime(2018, 6, 5, 20, 0))
        self.assertEqual(rem, "תזכיר לי")

    # --- weekday in sentence ---
    def test_meet_friday_evening(self):
        dt, rem = self._parse("נפגשים ביום שישי בערב")
        self.assertEqual(dt, datetime(2018, 6, 8, 20, 0))
        self.assertEqual(rem, "נפגשים")

    def test_wake_seven_morning_next_sunday(self):
        dt, rem = self._parse("תעיר אותי בשעה שבע בבוקר ביום ראשון הבא")
        self.assertEqual(dt, datetime(2018, 6, 10, 7, 0))
        self.assertEqual(rem, "תעיר אותי")

    # --- mixed spoken numeral + ASCII digits in one sentence ---
    def test_mixed_spoken_days_and_digit_clock(self):
        dt, rem = self._parse("תזכיר לי בעוד שלושה ימים בשעה 15:30")
        self.assertEqual(dt, datetime(2018, 6, 8, 15, 30))
        self.assertEqual(rem, "תזכיר לי")

    # --- gendered numerals embedded in sentences ---
    def test_gender_days_in_sentence(self):
        masc, _ = self._parse("תזכיר לי בעוד שלושה ימים")
        fem, _ = self._parse("תזכיר לי בעוד שלוש ימים")
        self.assertEqual(masc, datetime(2018, 6, 8, 0, 0))
        self.assertEqual(fem, masc)

    def test_gender_hours_in_sentence(self):
        fem, _ = self._parse("קבע התראה בעוד שלוש שעות")
        masc, _ = self._parse("קבע התראה בעוד שלושה שעות")
        self.assertEqual(fem, datetime(2018, 6, 5, 12, 0))
        self.assertEqual(masc, fem)

    # --- adversarial: no date in an otherwise valid sentence ---
    def test_no_date_what_time(self):
        self.assertIsNone(extract_datetime_he("מה השעה", ANCHOR))

    def test_no_date_tell_joke(self):
        self.assertIsNone(extract_datetime_he("ספר לי בדיחה", ANCHOR))

    def test_no_date_thanks(self):
        self.assertIsNone(extract_datetime_he("תודה רבה", ANCHOR))

    # --- adversarial: malformed clock inside a valid sentence ---
    def test_malformed_time_in_sentence(self):
        # 25:99 is rejected but the day word "מחר" still resolves; the
        # bad token is left untouched in the remainder
        res = extract_datetime_he("קבע פגישה בשעה 25:99 מחר", ANCHOR)
        self.assertIsNotNone(res)
        self.assertEqual(res[0], datetime(2018, 6, 6, 0, 0))
        self.assertIn("25:99", res[1])


class TestDurationSentencesHe(unittest.TestCase):
    def test_timer_for_ten_minutes(self):
        dur, rem = extract_duration_he("קבע טיימר ל10 דקות")
        self.assertEqual(dur, timedelta(minutes=10))

    def test_countdown_three_hours_ten_minutes(self):
        dur, rem = extract_duration_he("ספירה לאחור של שלוש שעות ועשר דקות")
        self.assertEqual(dur, timedelta(hours=3, minutes=10))

    def test_boil_for_five_minutes(self):
        dur, rem = extract_duration_he("להרתיח במשך 5 דקות")
        self.assertEqual(dur, timedelta(minutes=5))


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
