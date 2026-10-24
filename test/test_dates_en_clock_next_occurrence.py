"""English clock times name the next occurrence strictly after the anchor.

"at 18:00" said at 20:46 is tomorrow's 18:00, and said at exactly 18:00 it is
tomorrow's too, because the anchor itself is not after the anchor.  The gold
value is plain datetime arithmetic: today at the spoken time, plus a day when
that moment is not after the anchor.
"""
import unittest
from datetime import datetime, timedelta

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


if __name__ == "__main__":
    unittest.main()
