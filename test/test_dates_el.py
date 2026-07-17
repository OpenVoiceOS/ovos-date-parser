"""Tests for Modern Greek (el) date/time formatting and extraction.

The verified forms asserted below are drawn from standard Modern Greek
usage: weekday and month names (nominative and genitive), the idiomatic
clock-time constructions "και μισή" / "και τέταρτο" / "παρά τέταρτο", and
the feminine clock-hour numerals that agree with "ώρα". No expected string
is pinned from engine output.
"""
import unittest
from datetime import datetime, time, timedelta

from ovos_date_parser.dates_el import (
    nice_year_el, nice_weekday_el, nice_month_el, nice_day_el,
    nice_date_time_el, nice_date_el, nice_time_el,
    extract_datetime_el, extract_duration_el,
    WEEKDAYS_EL, MONTHS_EL, MONTHS_GEN_EL,
)
from ovos_date_parser.duration import DurationResolution


class TestNiceYearEl(unittest.TestCase):
    def test_current_era(self):
        result = nice_year_el(datetime(1984, 1, 1))
        # χίλια εννιακόσια ογδόντα τέσσερα
        self.assertEqual(result, "χίλια εννιακόσια ογδόντα τέσσερα")
        self.assertNotIn("π.Χ.", result)

    def test_bc_marker(self):
        result = nice_year_el(datetime(44, 1, 1), bc=True)
        self.assertIn("π.Χ.", result)

    def test_sweep_non_empty(self):
        for y in range(1, 2100, 7):
            result = nice_year_el(datetime(y, 1, 1))
            self.assertIsInstance(result, str)
            self.assertTrue(result.strip())


class TestNiceWeekdayEl(unittest.TestCase):
    def test_all_weekdays(self):
        expected = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη",
                    "Παρασκευή", "Σάββατο", "Κυριακή"]
        # 2018-06-04 is a Monday
        for i in range(7):
            dt = datetime(2018, 6, 4 + i)
            self.assertEqual(nice_weekday_el(dt), expected[i])

    def test_matches_map(self):
        for i in range(7):
            dt = datetime(2018, 6, 4 + i)
            self.assertEqual(nice_weekday_el(dt), WEEKDAYS_EL[i])


class TestNiceMonthEl(unittest.TestCase):
    def test_all_months_nominative(self):
        expected = ["Ιανουάριος", "Φεβρουάριος", "Μάρτιος", "Απρίλιος",
                    "Μάιος", "Ιούνιος", "Ιούλιος", "Αύγουστος",
                    "Σεπτέμβριος", "Οκτώβριος", "Νοέμβριος", "Δεκέμβριος"]
        for i in range(12):
            dt = datetime(2018, i + 1, 1)
            self.assertEqual(nice_month_el(dt), expected[i])
            self.assertEqual(nice_month_el(dt), MONTHS_EL[i + 1])


class TestNiceDayEl(unittest.TestCase):
    def test_dmy_genitive(self):
        # 5 Ιουνίου
        self.assertEqual(nice_day_el(datetime(2018, 6, 5)), "5 Ιουνίου")

    def test_mdy(self):
        self.assertEqual(nice_day_el(datetime(2018, 6, 5),
                                     date_format='MDY'), "Ιουνίου 5")

    def test_no_month(self):
        self.assertEqual(nice_day_el(datetime(2018, 6, 5),
                                     include_month=False), "5")

    def test_sweep(self):
        for d in range(1, 29):
            result = nice_day_el(datetime(2018, 2, d))
            self.assertTrue(result.startswith(str(d)))
            self.assertIn("Φεβρουαρίου", result)


class TestNiceDateEl(unittest.TestCase):
    def test_full_date(self):
        dt = datetime(2018, 6, 5)
        result = nice_date_el(dt)
        self.assertTrue(result.startswith("Τρίτη,"))
        self.assertIn("Ιουνίου", result)

    def test_today(self):
        now = datetime(2018, 6, 5)
        self.assertEqual(nice_date_el(datetime(2018, 6, 5), now=now,
                                      include_weekday=False), "σήμερα")

    def test_tomorrow(self):
        now = datetime(2018, 6, 5)
        self.assertEqual(nice_date_el(datetime(2018, 6, 6), now=now,
                                      include_weekday=False), "αύριο")

    def test_yesterday(self):
        now = datetime(2018, 6, 5)
        self.assertEqual(nice_date_el(datetime(2018, 6, 4), now=now,
                                      include_weekday=False), "χθες")

    def test_no_weekday(self):
        result = nice_date_el(datetime(2018, 6, 5), include_weekday=False)
        self.assertFalse(result.startswith("Τρίτη"))

    def test_sweep_month(self):
        for d in range(1, 29):
            result = nice_date_el(datetime(2020, 2, d))
            self.assertIsInstance(result, str)
            self.assertTrue(result.strip())


class TestNiceTimeEl(unittest.TestCase):
    def test_display_non_speech(self):
        self.assertEqual(nice_time_el(datetime(2018, 6, 5, 5, 30),
                                      speech=False), "5:30")

    def test_display_strips_leading_zero(self):
        self.assertEqual(nice_time_el(datetime(2018, 6, 5, 3, 1),
                                      speech=False), "3:01")

    def test_24hour_display(self):
        self.assertEqual(nice_time_el(datetime(2018, 6, 5, 14, 22),
                                      speech=False, use_24hour=True),
                         "14:22")

    def test_half_past(self):
        # τρεις και μισή
        self.assertEqual(nice_time_el(datetime(2018, 6, 5, 3, 30)),
                         "τρεις και μισή")

    def test_quarter_past(self):
        # τρεις και τέταρτο
        self.assertEqual(nice_time_el(datetime(2018, 6, 5, 3, 15)),
                         "τρεις και τέταρτο")

    def test_quarter_to(self):
        # 2:45 -> τρεις παρά τέταρτο
        self.assertEqual(nice_time_el(datetime(2018, 6, 5, 2, 45)),
                         "τρεις παρά τέταρτο")

    def test_feminine_one(self):
        # 1:00 -> μία (feminine), not neuter ένα
        self.assertEqual(nice_time_el(datetime(2018, 6, 5, 1, 0)),
                         "μία ακριβώς")

    def test_feminine_three_four(self):
        self.assertTrue(nice_time_el(
            datetime(2018, 6, 5, 3, 0)).startswith("τρεις"))
        self.assertTrue(nice_time_el(
            datetime(2018, 6, 5, 4, 0)).startswith("τέσσερις"))

    def test_noon_and_midnight(self):
        self.assertEqual(nice_time_el(datetime(2018, 6, 5, 12, 0)),
                         "δώδεκα ακριβώς")
        self.assertEqual(nice_time_el(datetime(2018, 6, 5, 0, 0)),
                         "δώδεκα ακριβώς")

    def test_and_minutes(self):
        # 3:20 -> τρεις και είκοσι
        self.assertEqual(nice_time_el(datetime(2018, 6, 5, 3, 20)),
                         "τρεις και είκοσι")

    def test_para_minutes(self):
        # 2:40 -> τρεις παρά είκοσι
        self.assertEqual(nice_time_el(datetime(2018, 6, 5, 2, 40)),
                         "τρεις παρά είκοσι")

    def test_ampm_marker(self):
        result = nice_time_el(datetime(2018, 6, 5, 17, 0), use_ampm=True)
        self.assertIn("το απόγευμα", result)
        result = nice_time_el(datetime(2018, 6, 5, 9, 0), use_ampm=True)
        self.assertIn("το πρωί", result)

    def test_24hour_feminine_teens(self):
        # 13:00 -> δεκατρείς (feminine teen)
        self.assertTrue(nice_time_el(datetime(2018, 6, 5, 13, 0),
                                     use_24hour=True).startswith("δεκατρείς"))

    def test_sweep_all_times(self):
        for h in range(24):
            for mi in range(0, 60, 5):
                dt = datetime(2018, 6, 5, h, mi)
                for u24 in (False, True):
                    for ampm in (False, True):
                        result = nice_time_el(dt, use_24hour=u24,
                                              use_ampm=ampm)
                        self.assertIsInstance(result, str)
                        self.assertTrue(result.strip())


class TestNiceDateTimeEl(unittest.TestCase):
    def test_combined(self):
        dt = datetime(2018, 6, 5, 17, 30)
        now = datetime(2018, 6, 1)
        result = nice_date_time_el(dt, now=now)
        self.assertIn("στις", result)
        self.assertIn("μισή", result)


class TestExtractDatetimeEl(unittest.TestCase):
    def setUp(self):
        self.anchor = datetime(2018, 6, 1, 0, 0, 0)  # a Friday

    def _dt(self, text):
        res = extract_datetime_el(text, anchorDate=self.anchor)
        self.assertIsNotNone(res)
        return res[0]

    # --- adversarial / contract ---
    def test_empty_returns_none(self):
        self.assertIsNone(extract_datetime_el(""))

    def test_whitespace_returns_none(self):
        self.assertIsNone(extract_datetime_el("   ",
                                              anchorDate=self.anchor))

    def test_no_date_returns_none(self):
        self.assertIsNone(extract_datetime_el("χωρίς ημερομηνία εδώ",
                                              anchorDate=self.anchor))

    def test_garbage_returns_none(self):
        self.assertIsNone(extract_datetime_el("qwerty 12345 zzz",
                                              anchorDate=self.anchor))

    def test_malformed_time_returns_none(self):
        # 25:99 is not a valid time and there is nothing else to anchor
        self.assertIsNone(extract_datetime_el("25:99",
                                              anchorDate=self.anchor))

    def test_returns_pair(self):
        res = extract_datetime_el("σήμερα", anchorDate=self.anchor)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], datetime)
        self.assertIsInstance(res[1], str)

    # --- relative days ---
    def test_today(self):
        self.assertEqual(self._dt("σήμερα").date(), self.anchor.date())

    def test_tomorrow(self):
        self.assertEqual(self._dt("αύριο").date(),
                         (self.anchor + timedelta(days=1)).date())

    def test_yesterday(self):
        self.assertEqual(self._dt("χθες").date(),
                         (self.anchor - timedelta(days=1)).date())

    def test_day_after_tomorrow(self):
        self.assertEqual(self._dt("μεθαύριο").date(),
                         (self.anchor + timedelta(days=2)).date())

    def test_day_before_yesterday(self):
        self.assertEqual(self._dt("προχθές").date(),
                         (self.anchor - timedelta(days=2)).date())

    # --- offsets ---
    def test_in_minutes(self):
        self.assertEqual(self._dt("σε 5 λεπτά"),
                         self.anchor + timedelta(minutes=5))

    def test_in_hours(self):
        self.assertEqual(self._dt("σε 3 ώρες"),
                         self.anchor + timedelta(hours=3))

    def test_in_seconds(self):
        self.assertEqual(self._dt("σε 10 δευτερόλεπτα"),
                         self.anchor + timedelta(seconds=10))

    def test_in_days(self):
        self.assertEqual(self._dt("σε 2 μέρες").date(),
                         (self.anchor + timedelta(days=2)).date())

    def test_next_week(self):
        self.assertEqual(self._dt("την επόμενη εβδομάδα").date(),
                         (self.anchor + timedelta(days=7)).date())

    def test_next_month(self):
        self.assertEqual(self._dt("τον επόμενο μήνα").month, 7)

    # --- explicit clock times ---
    def test_time_24hour(self):
        dt = self._dt("στις 15:30")
        self.assertEqual((dt.hour, dt.minute), (15, 30))

    def test_time_colon(self):
        dt = self._dt("3:30")
        self.assertEqual((dt.hour, dt.minute), (3, 30))

    def test_time_bare_hour(self):
        dt = self._dt("στις 3")
        self.assertEqual(dt.hour, 3)

    def test_time_half_past(self):
        dt = self._dt("στις 8 και μισή")
        self.assertEqual((dt.hour, dt.minute), (8, 30))

    def test_time_quarter_to(self):
        dt = self._dt("στις 8 παρά τέταρτο")
        self.assertEqual((dt.hour, dt.minute), (7, 45))

    def test_time_afternoon(self):
        dt = self._dt("στις 3 το απόγευμα")
        self.assertEqual(dt.hour, 15)

    # --- boundaries ---
    def test_midnight_boundary(self):
        dt = self._dt("στις 00:00")
        self.assertEqual((dt.hour, dt.minute), (0, 0))

    def test_noon_boundary(self):
        dt = self._dt("στις 12:00")
        self.assertEqual((dt.hour, dt.minute), (12, 0))

    # --- absolute dates ---
    def test_day_month(self):
        dt = self._dt("5 Ιουνίου")
        self.assertEqual((dt.month, dt.day), (6, 5))

    def test_day_month_year(self):
        dt = self._dt("5 Ιουνίου 2020")
        self.assertEqual((dt.year, dt.month, dt.day), (2020, 6, 5))

    def test_feb_29_leap(self):
        dt = self._dt("29 Φεβρουαρίου 2020")
        self.assertEqual((dt.year, dt.month, dt.day), (2020, 2, 29))

    def test_weekday(self):
        # anchor is Friday; "την Παρασκευή" resolves to the same day
        dt = self._dt("την Παρασκευή")
        self.assertEqual(dt.weekday(), 4)

    def test_ascii_digits_in_input(self):
        # ASCII digits must be handled the same as any digit token
        dt = self._dt("σε 15 λεπτά")
        self.assertEqual(dt, self.anchor + timedelta(minutes=15))

    def test_default_time_applied(self):
        res = extract_datetime_el("αύριο", anchorDate=self.anchor,
                                  default_time=time(9, 30))
        self.assertEqual((res[0].hour, res[0].minute), (9, 30))


class TestExtractDatetimeSpokenEl(unittest.TestCase):
    """Spelled-out Greek numerals and clock idioms.

    Anchor is a non-midnight, non-zero-minute time so that relative
    offsets are exercised against a real time of day.
    """
    def setUp(self):
        self.anchor = datetime(2017, 6, 27, 13, 4, 0)  # a Tuesday

    def _dt(self, text):
        res = extract_datetime_el(text, anchorDate=self.anchor)
        self.assertIsNotNone(res)
        return res[0]

    # --- spoken-numeral offsets ---
    def test_spoken_minutes_offset(self):
        self.assertEqual(self._dt("σε τρία λεπτά"),
                         self.anchor + timedelta(minutes=3))

    def test_spoken_days_offset(self):
        self.assertEqual(self._dt("σε δύο μέρες").date(),
                         (self.anchor + timedelta(days=2)).date())

    def test_spoken_hours_offset_from_anchor(self):
        # "σε τρεις ώρες" must be anchor + 3h (16:04), not an absolute 03:00
        self.assertEqual(self._dt("σε τρεις ώρες"),
                         self.anchor + timedelta(hours=3))

    def test_spoken_one_hour_offset(self):
        self.assertEqual(self._dt("σε μία ώρα"),
                         self.anchor + timedelta(hours=1))

    def test_spoken_fifteen_minutes(self):
        self.assertEqual(self._dt("σε δεκαπέντε λεπτά"),
                         self.anchor + timedelta(minutes=15))

    def test_digit_hours_offset_from_anchor(self):
        # same OFFSET semantics for digit input
        self.assertEqual(self._dt("σε 3 ώρες"),
                         self.anchor + timedelta(hours=3))

    # --- clock idioms with spoken (gendered) hour ---
    def test_spoken_half_past(self):
        dt = self._dt("στις τρεις και μισή")
        self.assertEqual((dt.hour, dt.minute), (3, 30))

    def test_spoken_quarter_past(self):
        dt = self._dt("στις τρεις και τέταρτο")
        self.assertEqual((dt.hour, dt.minute), (3, 15))

    def test_spoken_quarter_to(self):
        # τέσσερις παρά τέταρτο -> 03:45 (feminine hour on input)
        dt = self._dt("στις τέσσερις παρά τέταρτο")
        self.assertEqual((dt.hour, dt.minute), (3, 45))

    def test_spoken_feminine_one(self):
        dt = self._dt("στις μία")
        self.assertEqual(dt.hour, 1)

    def test_spoken_day_month(self):
        # spelled-out day-of-month
        dt = self._dt("πέντε Ιουνίου")
        self.assertEqual((dt.month, dt.day), (6, 5))

    def test_spoken_next_weekday(self):
        # anchor is Tuesday; "την επόμενη Τρίτη" -> next Tuesday
        dt = self._dt("την επόμενη Τρίτη")
        self.assertEqual(dt.weekday(), 1)
        self.assertGreater(dt.date(), self.anchor.date())


class TestExtractDurationEl(unittest.TestCase):
    def test_empty_returns_none(self):
        self.assertIsNone(extract_duration_el(""))

    def test_no_duration(self):
        dur, rem = extract_duration_el("χωρίς διάρκεια εδώ")
        self.assertIsNone(dur)

    def test_minutes(self):
        dur, rem = extract_duration_el("5 λεπτά")
        self.assertEqual(dur, timedelta(minutes=5))

    def test_hours(self):
        dur, rem = extract_duration_el("2 ώρες")
        self.assertEqual(dur, timedelta(hours=2))

    def test_seconds(self):
        dur, rem = extract_duration_el("10 δευτερόλεπτα")
        self.assertEqual(dur, timedelta(seconds=10))

    def test_days(self):
        dur, rem = extract_duration_el("3 μέρες")
        self.assertEqual(dur, timedelta(days=3))

    def test_weeks(self):
        dur, rem = extract_duration_el("2 εβδομάδες")
        self.assertEqual(dur, timedelta(weeks=2))

    def test_spoken_number(self):
        dur, rem = extract_duration_el("πέντε λεπτά")
        self.assertEqual(dur, timedelta(minutes=5))

    def test_combined(self):
        dur, rem = extract_duration_el("2 ώρες και 30 λεπτά")
        self.assertEqual(dur, timedelta(hours=2, minutes=30))

    def test_total_seconds_resolution(self):
        dur, rem = extract_duration_el(
            "2 ώρες", resolution=DurationResolution.TOTAL_SECONDS)
        self.assertEqual(dur, 7200.0)

    def test_remainder_returned(self):
        dur, rem = extract_duration_el("βάλε 5 λεπτά χρονόμετρο")
        self.assertEqual(dur, timedelta(minutes=5))
        self.assertNotIn("5", rem)

    def test_replace_token(self):
        dur, rem = extract_duration_el("5 λεπτά", replace_token="X")
        self.assertEqual(dur, timedelta(minutes=5))
        self.assertIn("X", rem)


class _RealSentenceBase(unittest.TestCase):
    """Shared anchor and helpers for full-sentence extraction tests.

    All expected values are reference-verified against how a Modern Greek
    speaker reads the sentence, not pinned from engine output. The anchor
    is Tuesday 2017-06-27 13:04, a non-midnight time so that relative
    offsets and the "earlier clock time rolls to tomorrow" inference are
    both exercised. Remainder strings are asserted in the parser's
    normalized form (lowercased, diacritics dropped, final sigma folded).
    """
    def setUp(self):
        self.anchor = datetime(2017, 6, 27, 13, 4, 0)

    def _check(self, text, expected_dt, expected_remainder):
        res = extract_datetime_el(text, anchorDate=self.anchor)
        self.assertIsNotNone(res, f"expected a datetime for {text!r}")
        dt, remainder = res
        self.assertEqual(dt, expected_dt, f"datetime for {text!r}")
        self.assertEqual(remainder, expected_remainder,
                         f"remainder for {text!r}")

    def _none(self, text):
        self.assertIsNone(extract_datetime_el(text, anchorDate=self.anchor),
                          f"expected None for {text!r}")


class TestRealSentenceAlarmsReminders(_RealSentenceBase):
    """Alarms, reminders and timers phrased as complete utterances."""

    def test_wake_me_tomorrow_half_past_seven_morning(self):
        # "wake me tomorrow at half past seven in the morning"
        self._check("ξύπνα με αύριο στις εφτά και μισή το πρωί",
                    datetime(2017, 6, 28, 7, 30), "ξυπνα με")

    def test_wake_me_tomorrow_formal_seven(self):
        # formal επτά instead of colloquial εφτά
        self._check("ξύπνα με αύριο στις επτά και μισή το πρωί",
                    datetime(2017, 6, 28, 7, 30), "ξυπνα με")

    def test_remind_me_in_three_hours(self):
        # "remind me in three hours" -> anchor + 3h
        self._check("θύμισέ μου σε τρεις ώρες",
                    datetime(2017, 6, 27, 16, 4), "θυμισε μου")

    def test_remind_me_in_ten_minutes_with_tail(self):
        self._check("θύμισέ μου σε δέκα λεπτά να πάρω τηλέφωνο",
                    datetime(2017, 6, 27, 13, 14),
                    "θυμισε μου να παρω τηλεφωνο")

    def test_remind_me_in_two_days_with_tail(self):
        self._check("θύμισέ μου σε δύο μέρες να πληρώσω",
                    datetime(2017, 6, 29, 0, 0), "θυμισε μου να πληρωσω")

    def test_alarm_eight_oclock_colloquial(self):
        # οχτώ ακριβώς -> 08:00, rolls to tomorrow (earlier than anchor)
        self._check("βάλε ξυπνητήρι στις οχτώ ακριβώς",
                    datetime(2017, 6, 28, 8, 0), "βαλε ξυπνητηρι")

    def test_alarm_eight_oclock_formal(self):
        self._check("βάλε ξυπνητήρι στις οκτώ ακριβώς",
                    datetime(2017, 6, 28, 8, 0), "βαλε ξυπνητηρι")

    def test_timer_five_minutes_digit(self):
        self._check("βάλε χρονόμετρο για 5 λεπτά",
                    datetime(2017, 6, 27, 13, 9), "βαλε χρονομετρο για")

    def test_turn_off_light_in_five_minutes_spoken(self):
        self._check("κλείσε το φως σε πέντε λεπτά",
                    datetime(2017, 6, 27, 13, 9), "κλεισε φωσ")

    def test_leave_in_two_days_digit(self):
        self._check("θα φύγω σε 2 μέρες",
                    datetime(2017, 6, 29, 0, 0), "θα φυγω")


class TestRealSentenceAppointments(_RealSentenceBase):
    """Appointments and events carrying an absolute calendar date."""

    def test_doctor_on_fifth_of_june(self):
        # 5 Ιουνίου is already past this year's anchor -> next year
        self._check("ραντεβού στον γιατρό στις 5 Ιουνίου",
                    datetime(2018, 6, 5, 0, 0), "ραντεβου γιατρο")

    def test_train_leaves_fifteenth_of_march(self):
        self._check("το τρένο φεύγει στις 15 Μαρτίου",
                    datetime(2018, 3, 15, 0, 0), "το τρενο φευγει")

    def test_nominative_month_input(self):
        # nominative "Ιούνιος" accepted the same as the genitive
        self._check("ραντεβού στις 5 Ιούνιος",
                    datetime(2018, 6, 5, 0, 0), "ραντεβου")

    def test_spoken_day_of_month(self):
        # spelled-out day-of-month with genitive month
        self._check("κράτηση στις δεκαπέντε Ιουνίου",
                    datetime(2018, 6, 15, 0, 0), "κρατηση")

    def test_next_tuesday_question(self):
        # anchor is Tuesday -> next Tuesday is a week later
        self._check("τι γίνεται την επόμενη Τρίτη",
                    datetime(2017, 7, 4, 0, 0), "τι γινεται")

    def test_appointment_on_friday_ten_morning(self):
        # Friday after the anchor at 10:00
        self._check("ραντεβού την Παρασκευή στις δέκα το πρωί",
                    datetime(2017, 6, 30, 10, 0), "ραντεβου")

    def test_talk_tomorrow(self):
        self._check("μιλάμε αύριο", datetime(2017, 6, 28, 0, 0), "μιλαμε")


class TestRealSentenceClockIdioms(_RealSentenceBase):
    """και μισή / και τέταρτο / παρά τέταρτο / ακριβώς and parts of day."""

    def test_quarter_to_four_spoken(self):
        # τέσσερις παρά τέταρτο -> 03:45
        self._check("συνάντηση στις τέσσερις παρά τέταρτο",
                    datetime(2017, 6, 28, 3, 45), "συναντηση")

    def test_quarter_past_three_predawn(self):
        # τρεις και τέταρτο τα ξημερώματα -> 03:15
        self._check("ξύπνα με στις τρεις και τέταρτο τα ξημερώματα",
                    datetime(2017, 6, 28, 3, 15), "ξυπνα με")

    def test_three_in_the_afternoon(self):
        # τρεις το απόγευμα -> 15:00 same day
        self._check("κλείσε ραντεβού στις τρεις το απόγευμα",
                    datetime(2017, 6, 27, 15, 0), "κλεισε ραντεβου")

    def test_nine_thirty_at_night(self):
        # εννέα και μισή το βράδυ -> 21:30 same day
        self._check("η ταινία παίζει στις εννέα και μισή το βράδυ",
                    datetime(2017, 6, 27, 21, 30), "η ταινια παιζει")

    def test_nine_at_night(self):
        self._check("δείπνο απόψε στις εννέα το βράδυ",
                    datetime(2017, 6, 27, 21, 0), "δειπνο αποψε")

    def test_eleven_at_night(self):
        # έντεκα το βράδυ -> 23:00
        self._check("το πάρτι είναι στις έντεκα το βράδυ",
                    datetime(2017, 6, 27, 23, 0), "το παρτι ειναι")


class TestRealSentenceGenderInContext(_RealSentenceBase):
    """Gendered numerals embedded in sentences.

    Clock hours take the feminine μία/τρεις/τέσσερις; counted nouns take
    the neuter τρία/τέσσερα. Both must be understood on input.
    """

    def test_feminine_one_oclock(self):
        # στη μία -> 01:00 (rolls to tomorrow); feminine "μία"
        self._check("ξύπνα με στη μία",
                    datetime(2017, 6, 28, 1, 0), "ξυπνα με")

    def test_feminine_three_afternoon(self):
        self._check("τα λέμε στις τρεις το απόγευμα",
                    datetime(2017, 6, 27, 15, 0), "τα λεμε")

    def test_feminine_four_quarter_to(self):
        self._check("συνάντηση στις τέσσερις παρά τέταρτο",
                    datetime(2017, 6, 28, 3, 45), "συναντηση")

    def test_neuter_three_minutes(self):
        # counted noun "λεπτά" takes neuter "τρία"
        self._check("θύμισέ μου σε τρία λεπτά",
                    datetime(2017, 6, 27, 13, 7), "θυμισε μου")

    def test_neuter_four_days(self):
        self._check("έλα σε τέσσερα μέρες",
                    datetime(2017, 7, 1, 0, 0), "ελα")


class TestRealSentenceMixedDigits(_RealSentenceBase):
    """Sentences mixing spelled-out numerals with ASCII digits."""

    def test_digit_hour_spoken_half(self):
        # digit "7" + spoken idiom "και μισή"
        self._check("ξύπνα με στις 7 και μισή",
                    datetime(2017, 6, 28, 7, 30), "ξυπνα με")

    def test_digit_hour_spoken_quarter_morning(self):
        self._check("βάλε ξυπνητήρι στις 6 και τέταρτο το πρωί",
                    datetime(2017, 6, 28, 6, 15), "βαλε ξυπνητηρι")

    def test_digit_hours_spoken_minutes_offset(self):
        # "in 3 hours and twenty minutes" -> anchor + 3h20m
        self._check("θύμισέ μου σε 3 ώρες και είκοσι λεπτά",
                    datetime(2017, 6, 27, 16, 24), "θυμισε μου")

    def test_spoken_day_digit_absent(self):
        # spelled-out day, genitive month, no year -> next occurrence
        self._check("κράτηση στις δεκαπέντε Ιουνίου",
                    datetime(2018, 6, 15, 0, 0), "κρατηση")


class TestRealSentenceAdversarial(_RealSentenceBase):
    """Sentence-shaped inputs that must NOT yield a datetime."""

    def test_greeting_no_date(self):
        self._none("γεια σου τι κάνεις")

    def test_vague_sometime(self):
        self._none("πάμε σινεμά κάποια στιγμή")

    def test_plain_statement(self):
        self._none("αυτό είναι ένα κανονικό μήνυμα χωρίς ημερομηνία")

    def test_malformed_clock_in_sentence(self):
        # 25:99 is not a valid time and nothing else anchors the sentence
        self._none("ραντεβού στις 25:99 δεν υπάρχει")

    def test_empty(self):
        self.assertIsNone(extract_datetime_el(""))

    def test_whitespace_only(self):
        self._none("       ")


if __name__ == "__main__":
    unittest.main()
