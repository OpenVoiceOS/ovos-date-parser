"""Asturian datetime extraction: natural phrasing, clock words and edge cases."""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

# whole-second anchor with a non-trivial time of day, so a relative offset
# that ignored the anchor clock would be obvious
ANCHOR = datetime(2117, 9, 3, 13, 30, 0)
TZ = default_timezone()


def extract(text, anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang="ast", anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestRelativeOffsetKeepsAnchorClock(unittest.TestCase):
    """A bare hr/min/sec offset must be added to the anchor time of day,
    not to midnight."""

    def test_seconds(self):
        self.assertEqual(extract("en 15 segundos")[0], dt(2117, 9, 3, 13, 30, 15))

    def test_minutes(self):
        self.assertEqual(extract("en 15 minutos")[0], dt(2117, 9, 3, 13, 45))

    def test_hours(self):
        self.assertEqual(extract("en 3 hores")[0], dt(2117, 9, 3, 16, 30))

    def test_singular_units(self):
        self.assertEqual(extract("en 1 segundu")[0], dt(2117, 9, 3, 13, 30, 1))
        self.assertEqual(extract("en 1 minutu")[0], dt(2117, 9, 3, 13, 31))
        self.assertEqual(extract("en 1 hora")[0], dt(2117, 9, 3, 14, 30))

    def test_half_hour(self):
        self.assertEqual(extract("en media hora")[0], dt(2117, 9, 3, 14, 0))

    def test_minute_offset_carries_into_next_hour(self):
        self.assertEqual(extract("en 90 minutos")[0], dt(2117, 9, 3, 15, 0))

    def test_hour_offset_crosses_midnight(self):
        self.assertEqual(extract("en 25 hores")[0], dt(2117, 9, 4, 14, 30))

    def test_alarm_phrasing(self):
        self.assertEqual(extract("pon una alarma en 10 minutos")[0],
                         dt(2117, 9, 3, 13, 40))

    def test_reminder_phrasing(self):
        self.assertEqual(extract("recuérdame en 2 hores")[0],
                         dt(2117, 9, 3, 15, 30))

    def test_offset_seconds_are_exact(self):
        # a whole-second offset must not leak fractional seconds
        self.assertEqual(extract("en 30 segundos")[0].second, 30)
        self.assertEqual(extract("en 30 segundos")[0].microsecond, 0)


class TestAbsoluteClock(unittest.TestCase):
    """Absolute spoken clock times ignore the anchor time of day."""

    def test_bare_hour_word(self):
        # 3:00 is earlier than the 13:30 anchor -> next day
        self.assertEqual(extract("a les tres")[0], dt(2117, 9, 4, 3))

    def test_one_oclock_feminine(self):
        self.assertEqual(extract("a la una")[0], dt(2117, 9, 4, 1))

    def test_afternoon_adds_twelve(self):
        self.assertEqual(extract("a les 8 de la tarde")[0], dt(2117, 9, 3, 20))
        self.assertEqual(extract("a les cinco de la tarde")[0],
                         dt(2117, 9, 3, 17))

    def test_morning_stays_am(self):
        self.assertEqual(extract("a les ocho de la mañana")[0],
                         dt(2117, 9, 4, 8))

    def test_night(self):
        self.assertEqual(extract("a les nueve de la nueche")[0],
                         dt(2117, 9, 3, 21))

    def test_bare_24h(self):
        self.assertEqual(extract("a les 15")[0], dt(2117, 9, 3, 15))

    def test_half_past(self):
        # spoken hour is in the future -> rolls to the next day
        self.assertEqual(extract("a les 8 y media")[0], dt(2117, 9, 4, 8, 30))

    def test_quarter_past(self):
        self.assertEqual(extract("a les 8 y cuartu")[0], dt(2117, 9, 4, 8, 15))

    def test_quarter_to(self):
        self.assertEqual(extract("a les 8 menos cuartu")[0],
                         dt(2117, 9, 4, 7, 45))

    def test_on_the_dot(self):
        self.assertEqual(extract("a les 8 en puntu")[0], dt(2117, 9, 4, 8))


class TestDayAndCalendar(unittest.TestCase):
    """Day offsets and calendar dates."""

    def test_day_word_offset(self):
        self.assertEqual(extract("pa mañana")[0], dt(2117, 9, 4))

    def test_today(self):
        self.assertEqual(extract("güei")[0], dt(2117, 9, 3))

    def test_yesterday(self):
        self.assertEqual(extract("ayeri")[0], dt(2117, 9, 2))

    def test_next_week(self):
        self.assertEqual(extract("la selmana que vien")[0], dt(2117, 9, 10))

    def test_in_n_days(self):
        self.assertEqual(extract("en 3 díes")[0], dt(2117, 9, 6))

    def test_day_of_month_digits(self):
        # the day exists this year but is in the past -> next occurrence
        self.assertEqual(extract("11 de xineru")[0], dt(2118, 1, 11))

    def test_explicit_year(self):
        self.assertEqual(extract("15 de xineru de 2020")[0], dt(2020, 1, 15))


class TestImpossibleAndBoundaryDates(unittest.TestCase):
    """Impossible or out-of-range inputs must resolve safely, never crash."""

    def test_leap_day_resolves_to_next_leap_year(self):
        self.assertEqual(extract("el 29 de febreru")[0], dt(2120, 2, 29))

    def test_leap_day_non_leap_explicit_year(self):
        self.assertIsNone(extract("el 29 de febreru de 2021"))

    def test_february_thirty_first_is_none(self):
        # february never has 31 days in any year -> no date, no crash
        self.assertIsNone(extract("el 31 de febreru"))

    def test_february_thirtieth_is_none(self):
        self.assertIsNone(extract("el 30 de febreru"))

    def test_april_thirty_first_is_none(self):
        self.assertIsNone(extract("el 31 d'abril"))

    def test_day_thirty_two_is_none(self):
        self.assertIsNone(extract("el 32 de xineru"))

    def test_hour_out_of_range_is_none(self):
        self.assertIsNone(extract("a les 25"))

    def test_empty_and_garbage(self):
        self.assertIsNone(extract(""))
        self.assertIsNone(extract("una frase ensin data"))


if __name__ == "__main__":
    unittest.main()
