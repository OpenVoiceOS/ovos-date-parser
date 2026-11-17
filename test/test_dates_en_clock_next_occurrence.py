"""English clock times name the next occurrence after the anchor.

"at 18:00" said at 20:46 is tomorrow's 18:00. Said at exactly 18:00 it is
18:00 that day: an instant equal to the anchor is the anchor (class 3 of the
routing rulings). The gold value is plain datetime arithmetic: today at the
spoken time, plus a day when that moment is before the anchor.
"""
import unittest
from datetime import datetime, timedelta, timezone

import pytest

from ovos_date_parser import extract_datetime

MARKER_STRAND = "https://github.com/TigreGotico/chronologia/issues/996"
TWELVE_AT_NIGHT = "https://github.com/TigreGotico/chronologia/issues/1002"
HOUR_WITH_DAYPART = "https://github.com/TigreGotico/chronologia/issues/1002"

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
    return moment if moment >= anchor else moment + timedelta(days=1)


class TestClockNextOccurrence(unittest.TestCase):
    def check(self, text, hour, minute, remainder=""):
        for anchor in ANCHORS:
            with self.subTest(text=text, anchor=anchor.isoformat()):
                got = extract_datetime(text, lang="en-US", anchorDate=anchor)
                self.assertIsNotNone(got)
                self.assertEqual(got[0], next_after(anchor, hour, minute))
                self.assertEqual(got[1], remainder)

    def test_bare_24_hour_clock(self):
        self.check("18:00", 18, 0)

    def test_alarm_request(self):
        # "an" and "for" are not part of the date, so they stay in the
        # remainder (the routing remainder rule)
        self.check("set an alarm for 18:00", 18, 0, "set an alarm for")

    def test_pm_hour_agrees_with_24_hour_clock(self):
        self.check("at 6 pm", 18, 0)

    def test_a_named_day_is_not_moved(self):
        for anchor in ANCHORS:
            with self.subTest(anchor=anchor.isoformat()):
                got = extract_datetime("tomorrow at 18:00", lang="en-US",
                                       anchorDate=anchor)
                self.assertEqual(got[0], (anchor + timedelta(days=1)).replace(
                    hour=18, minute=0, second=0, microsecond=0))


def anchored(text, rows):
    """One pytest param per anchor: (text, anchor, expected value)."""
    return [pytest.param(text, anchor, value, id=f"{text}@{anchor.isoformat()}")
            for anchor, value in rows]


@pytest.mark.xfail(strict=True, reason=MARKER_STRAND)
@pytest.mark.parametrize("text,anchor,expected", [
    *anchored("at 18:00", [(a, next_after(a, 18, 0)) for a in ANCHORS]),
    *anchored("at 13:00", [(a, next_after(a, 13, 0)) for a in ANCHORS]),
])
def test_at_before_a_clock_leaves_no_remainder(text, anchor, expected):
    got = extract_datetime(text, lang="en-US", anchorDate=anchor)
    assert got is not None
    assert got[0] == expected
    assert got[1] == ""


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


BARE_MINUTES_ANCHORS = [
    datetime(2026, 10, 23, 0, 0, 30), datetime(2026, 10, 23, 9, 0),
    datetime(2026, 10, 23, 11, 59), datetime(2026, 10, 23, 13, 10),
    datetime(2026, 10, 23, 15, 0), datetime(2026, 10, 23, 23, 59)]


# A digit clock "H:MM" keeps its 24-hour reading: ruling 17 (the next
# twelve-hour reading) covers a spoken hour only. So "at 3:30" is the next
# 03:30, by class 3.
@pytest.mark.xfail(strict=True, reason=MARKER_STRAND)
@pytest.mark.parametrize("text,anchor,expected", [
    *(row for hour in range(1, 12) for minute in (15, 30, 45)
      for row in anchored(f"at {hour}:{minute}",
                          [(a, next_after(a, hour, minute))
                           for a in BARE_MINUTES_ANCHORS])),
])
def test_a_digit_clock_reads_as_written(text, anchor, expected):
    got = extract_datetime(text, lang="en-US", anchorDate=anchor)
    assert got is not None
    assert got[0] == expected
    assert got[1] == ""


class TestDigitClockHours(unittest.TestCase):
    def test_after_the_afternoon_hour_in_the_same_hour(self):
        # ruling 17 leaves a digit clock alone: 01:45 is the next 1:45
        anchor = datetime(2026, 10, 23, 13, 10)
        got = extract_datetime("at 1:45", lang="en-US", anchorDate=anchor)
        self.assertEqual(got[0], datetime(2026, 10, 24, 1, 45))

    def test_a_named_today_keeps_the_written_hour(self):
        # ruling 17 leaves a digit clock alone, and a named day is not moved
        # by a clock that has passed (ruling 16)
        anchor = datetime(2026, 10, 23, 15, 0)
        got = extract_datetime("at 3:30 today", lang="en-US", anchorDate=anchor)
        self.assertEqual(got[0], datetime(2026, 10, 23, 3, 30))


TONIGHT_ANCHORS = [datetime(2026, 10, 23, 0, 0, 30),
                   datetime(2026, 10, 23, 15, 0),
                   datetime(2026, 10, 23, 23, 59)]


def end_of_day(anchor, days=1, minute=0):
    """00:MM at the end of the anchor's day, or of a day ``days - 1`` on."""
    midnight = anchor.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight + timedelta(days=days, minutes=minute)


# "12 tonight" is 00:MM at the end of the anchor's day: "tonight" is the
# night of the anchor's own day (ruling 10), even when said at 00:00:30.
@pytest.mark.xfail(strict=True, reason=TWELVE_AT_NIGHT)
@pytest.mark.parametrize("text,anchor,expected", [
    *(row for text, minute in (("at 12 tonight", 0),
                               ("at 12:30 tonight", 30),
                               ("tonight at 12", 0),
                               ("at twelve thirty tonight", 30),
                               ("tonight at twelve thirty", 30),
                               ("at 12 30 tonight", 30))
      for row in anchored(text, [(a, end_of_day(a, minute=minute))
                                 for a in TONIGHT_ANCHORS])),
])
def test_twelve_tonight_is_the_midnight_that_ends_the_day(text, anchor,
                                                           expected):
    got = extract_datetime(text, lang="en-US", anchorDate=anchor)
    assert got is not None
    assert got[0] == expected
    assert got[1] == ""


@pytest.mark.xfail(strict=True, reason=HOUR_WITH_DAYPART)
def test_tonight_at_eleven_is_unchanged():
    got = extract_datetime("at 11 tonight", lang="en-US",
                           anchorDate=datetime(2026, 10, 23, 15, 0))
    assert got[0] == datetime(2026, 10, 23, 23, 0)


NAMED_DAY_ANCHORS = [datetime(2026, 10, 23, 0, 0, 30),
                     datetime(2026, 10, 23, 15, 0),
                     datetime(2026, 10, 23, 15, 30),
                     datetime(2026, 10, 23, 23, 59),
                     datetime(2026, 10, 23, 15, 0,
                              tzinfo=timezone(timedelta(hours=-5)))]


# With a named day, "12 tonight" is the midnight that ends that day.
@pytest.mark.xfail(strict=True, reason=TWELVE_AT_NIGHT)
@pytest.mark.parametrize("text,anchor,expected", [
    *(row for text, days in (("at 12 tonight today", 1),
                             # 2026-10-23 is a Friday
                             ("at 12 tonight on friday", 1),
                             ("at 12 tonight tomorrow", 2),
                             ("at 12 tonight in 2 days", 3))
      for row in anchored(text, [(a, end_of_day(a, days))
                                 for a in NAMED_DAY_ANCHORS])),
])
def test_twelve_tonight_on_a_named_day(text, anchor, expected):
    got = extract_datetime(text, lang="en-US", anchorDate=anchor)
    assert got is not None
    assert got[0] == expected
    assert got[1] == ""


def test_a_duration_is_not_a_clock_time():
    # a bare length is no date (ruling 3), so only "tonight" is read: the
    # middle of the 21:00-24:00 night (ruling 10)
    anchor = datetime(2026, 10, 23, 15, 0)
    got = extract_datetime("set a timer for 12 minutes tonight",
                           lang="en-US", anchorDate=anchor)
    assert got[0] == datetime(2026, 10, 23, 22, 30)


if __name__ == "__main__":
    unittest.main()
