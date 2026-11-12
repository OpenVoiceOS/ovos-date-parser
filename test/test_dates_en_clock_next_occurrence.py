"""English clock times name the next occurrence strictly after the anchor.

"at 18:00" said at 20:46 is tomorrow's 18:00, and said at exactly 18:00 it is
tomorrow's too, because the anchor itself is not after the anchor.  The gold
value is plain datetime arithmetic: today at the spoken time, plus a day when
that moment is not after the anchor.
"""
import unittest
from datetime import datetime, timedelta, timezone

from ovos_date_parser import extract_datetime

DAY = datetime(2026, 10, 23)
ANCHORS = [
    DAY.replace(hour=9, minute=0),
    DAY.replace(hour=17, minute=59, second=30),
    DAY.replace(hour=18, minute=0),
    DAY.replace(hour=18, minute=0, second=30),
    DAY.replace(hour=18, minute=1),
    DAY.replace(hour=20, minute=46),
    DAY.replace(hour=23, minute=59),
]


def next_after(anchor, hour, minute):
    moment = anchor.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return moment if moment > anchor else moment + timedelta(days=1)


class TestClockNextOccurrence(unittest.TestCase):
    def check(self, text, hour, minute, remainder=""):
        for anchor in ANCHORS:
            with self.subTest(text=text, anchor=anchor.isoformat()):
                got = extract_datetime(text, lang="en-US", anchorDate=anchor)
                self.assertIsNotNone(got)
                self.assertEqual(got[0], next_after(anchor, hour, minute))
                self.assertEqual(got[1], remainder)

    def test_at_24_hour_clock(self):
        self.check("at 18:00", 18, 0)

    def test_bare_24_hour_clock(self):
        self.check("18:00", 18, 0)

    def test_alarm_request(self):
        self.check("set an alarm for 18:00", 18, 0, "set alarm")

    def test_afternoon_hour_past_noon(self):
        self.check("at 13:00", 13, 0)

    def test_pm_hour_agrees_with_24_hour_clock(self):
        self.check("at 6 pm", 18, 0)

    def test_a_named_day_is_not_moved(self):
        for anchor in ANCHORS:
            with self.subTest(anchor=anchor.isoformat()):
                got = extract_datetime("tomorrow at 18:00", lang="en-US",
                                       anchorDate=anchor)
                self.assertEqual(got[0], (anchor + timedelta(days=1)).replace(
                    hour=18, minute=0, second=0, microsecond=0))


class TestSpokenMidnight(unittest.TestCase):
    """A spoken midnight is the next midnight strictly after the anchor."""

    ANCHORS = [datetime(2026, 10, 23, 15, 0), datetime(2026, 10, 23, 23, 59),
               datetime(2026, 10, 23, 0, 0, 30)]

    def check(self, text):
        for anchor in self.ANCHORS:
            with self.subTest(text=text, anchor=anchor.isoformat()):
                got = extract_datetime(text, lang="en-US", anchorDate=anchor)
                self.assertIsNotNone(got)
                self.assertEqual(got[0], next_after(anchor, 0, 0))

    def test_00_00(self):
        self.check("at 00:00")

    def test_0_00(self):
        self.check("at 0:00")

    def test_alarm_request(self):
        self.check("set an alarm for 00:00")

    def test_wake_me(self):
        self.check("wake me at 0:00")

    def test_12_am(self):
        self.check("at 12 am")

    def test_midnight(self):
        self.check("at midnight")


class TestSpokenNoon(unittest.TestCase):
    """A spoken twelve o'clock is the next such moment strictly after the anchor."""

    ANCHORS = [datetime(2026, 10, 23, 0, 0, 30), datetime(2026, 10, 23, 11, 59),
               datetime(2026, 10, 23, 12, 0), datetime(2026, 10, 23, 12, 30),
               datetime(2026, 10, 23, 15, 0), datetime(2026, 10, 23, 23, 59)]

    def check(self, text, hour, minute):
        for anchor in self.ANCHORS:
            with self.subTest(text=text, anchor=anchor.isoformat()):
                got = extract_datetime(text, lang="en-US", anchorDate=anchor)
                self.assertIsNotNone(got)
                self.assertEqual(got[0], next_after(anchor, hour, minute))

    def test_12_00(self):
        self.check("at 12:00", 12, 0)

    def test_12_30(self):
        self.check("at 12:30", 12, 30)

    def test_12_pm(self):
        self.check("at 12 pm", 12, 0)

    def test_noon(self):
        self.check("at noon", 12, 0)

    def test_12_00_pm(self):
        self.check("at 12:00 pm", 12, 0)

    def test_12_30_am(self):
        self.check("at 12:30 am", 0, 30)


class TestBareTwelveHourMinutes(unittest.TestCase):
    """A bare "H:MM" is the earlier of H:MM and H+12:MM strictly after the anchor."""

    ANCHORS = [datetime(2026, 10, 23, 0, 0, 30), datetime(2026, 10, 23, 9, 0),
               datetime(2026, 10, 23, 11, 59), datetime(2026, 10, 23, 13, 10),
               datetime(2026, 10, 23, 15, 0), datetime(2026, 10, 23, 23, 59)]

    @staticmethod
    def earliest_after(anchor, hour, minute):
        return min(next_after(anchor, h, minute) for h in (hour, hour + 12))

    def check(self, text, hour, minute):
        for anchor in self.ANCHORS:
            with self.subTest(text=text, anchor=anchor.isoformat()):
                got = extract_datetime(text, lang="en-US", anchorDate=anchor)
                self.assertIsNotNone(got)
                self.assertEqual(got[0],
                                 self.earliest_after(anchor, hour, minute))
                self.assertEqual(got[1], "")

    def test_half_past_the_hour(self):
        for hour in range(1, 12):
            self.check(f"at {hour}:30", hour, 30)

    def test_quarter_to_and_past_the_hour(self):
        for hour in range(1, 12):
            self.check(f"at {hour}:15", hour, 15)
            self.check(f"at {hour}:45", hour, 45)

    def test_after_the_afternoon_hour_in_the_same_hour(self):
        anchor = datetime(2026, 10, 23, 13, 10)
        got = extract_datetime("at 1:45", lang="en-US", anchorDate=anchor)
        self.assertEqual(got[0], datetime(2026, 10, 23, 13, 45))

    def test_a_named_today_keeps_the_afternoon_reading(self):
        anchor = datetime(2026, 10, 23, 15, 0)
        got = extract_datetime("at 3:30 today", lang="en-US", anchorDate=anchor)
        self.assertEqual(got[0], datetime(2026, 10, 23, 15, 30))


class TestSpokenMidnightTonight(unittest.TestCase):
    """"12 tonight" is the next 00:MM strictly after the anchor.

    With a named day it is the 00:MM that ends that day.
    """

    ANCHORS = [datetime(2026, 10, 23, 0, 0, 30), datetime(2026, 10, 23, 15, 0),
               datetime(2026, 10, 23, 23, 59)]

    def check(self, text, minute):
        for anchor in self.ANCHORS:
            with self.subTest(text=text, anchor=anchor.isoformat()):
                got = extract_datetime(text, lang="en-US", anchorDate=anchor)
                self.assertIsNotNone(got)
                self.assertEqual(got[0], next_after(anchor, 0, minute))
                self.assertEqual(got[1], "")

    def test_12_tonight(self):
        self.check("at 12 tonight", 0)

    def test_12_30_tonight(self):
        self.check("at 12:30 tonight", 30)

    def test_tonight_at_12(self):
        self.check("tonight at 12", 0)

    def test_tonight_at_eleven_is_unchanged(self):
        got = extract_datetime("at 11 tonight", lang="en-US",
                               anchorDate=datetime(2026, 10, 23, 15, 0))
        self.assertEqual(got[0], datetime(2026, 10, 23, 23, 0))

    def test_spoken_minutes(self):
        self.check("at twelve thirty tonight", 30)
        self.check("tonight at twelve thirty", 30)
        self.check("at 12 30 tonight", 30)


class TestSpokenMidnightTonightOnANamedDay(unittest.TestCase):
    """With a named day, "12 tonight" is the midnight that ends that day."""

    ANCHORS = [datetime(2026, 10, 23, 0, 0, 30), datetime(2026, 10, 23, 15, 0),
               datetime(2026, 10, 23, 15, 30), datetime(2026, 10, 23, 23, 59),
               datetime(2026, 10, 23, 15, 0,
                        tzinfo=timezone(timedelta(hours=-5)))]

    def check(self, text, days_until_end_of_day):
        for anchor in self.ANCHORS:
            with self.subTest(text=text, anchor=anchor.isoformat()):
                got = extract_datetime(text, lang="en-US", anchorDate=anchor)
                self.assertIsNotNone(got)
                midnight = anchor.replace(hour=0, minute=0, second=0,
                                          microsecond=0)
                self.assertEqual(got[0], midnight + timedelta(
                    days=days_until_end_of_day))
                self.assertEqual(got[1], "")

    def test_today(self):
        self.check("at 12 tonight today", 1)

    def test_on_the_anchor_weekday(self):
        # 2026-10-23 is a Friday
        self.check("at 12 tonight on friday", 1)

    def test_tomorrow(self):
        self.check("at 12 tonight tomorrow", 2)

    def test_in_two_days(self):
        self.check("at 12 tonight in 2 days", 3)

    def test_a_duration_is_not_a_clock_time(self):
        anchor = datetime(2026, 10, 23, 15, 0)
        got = extract_datetime("set a timer for 12 minutes tonight",
                               lang="en-US", anchorDate=anchor)
        self.assertEqual(got[0], datetime(2026, 10, 23, 15, 12))


if __name__ == "__main__":
    unittest.main()
