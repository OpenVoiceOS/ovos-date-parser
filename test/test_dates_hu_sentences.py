"""Hungarian datetime extraction: natural phrasing, clock words and edge cases."""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

# a whole-second afternoon anchor, so a preserved time of day is observable and
# second-level offsets do not get truncated
ANCHOR = datetime(2117, 9, 3, 13, 30, 0)
TZ = default_timezone()


def extract(text, lang="hu", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestRelativeOffsetKeepsTimeOfDay(unittest.TestCase):
    """"X <unit> múlva" (in X units) must offset from the anchor time of day,
    not from midnight."""

    def test_seconds_offset(self):
        self.assertEqual(extract("15 másodperc múlva")[0], dt(2117, 9, 3, 13, 30, 15))

    def test_minutes_offset(self):
        self.assertEqual(extract("15 perc múlva")[0], dt(2117, 9, 3, 13, 45))

    def test_hours_offset(self):
        self.assertEqual(extract("3 óra múlva")[0], dt(2117, 9, 3, 16, 30))

    def test_seconds_offset_spelled(self):
        self.assertEqual(extract("tizenöt másodperc múlva")[0], dt(2117, 9, 3, 13, 30, 15))

    def test_minutes_offset_spelled(self):
        self.assertEqual(extract("tizenöt perc múlva")[0], dt(2117, 9, 3, 13, 45))

    def test_hours_offset_spelled(self):
        self.assertEqual(extract("három óra múlva")[0], dt(2117, 9, 3, 16, 30))

    def test_hour_offset_wraps_past_midnight(self):
        # 13:30 + 12h crosses into the next day
        self.assertEqual(extract("12 óra múlva")[0], dt(2117, 9, 4, 1, 30))

    def test_minutes_offset_wraps_the_hour(self):
        self.assertEqual(extract("45 perc múlva")[0], dt(2117, 9, 3, 14, 15))

    def test_implicit_one_hour(self):
        self.assertEqual(extract("óra múlva")[0], dt(2117, 9, 3, 14, 30))

    def test_day_offset_still_resets_to_midnight(self):
        # a day/week offset carries no time of day and must stay at midnight
        self.assertEqual(extract("3 nap múlva")[0], dt(2117, 9, 6))

    def test_week_offset_resets_to_midnight(self):
        self.assertEqual(extract("két hét múlva")[0], dt(2117, 9, 17))


class TestSpokenClockKor(unittest.TestCase):
    """The "-kor" (at) suffix, hyphenated on digits and attached on words."""

    def test_digit_kor(self):
        self.assertEqual(extract("8-kor")[0], dt(2117, 9, 4, 8))

    def test_bare_hour_word_kor(self):
        self.assertEqual(extract("nyolckor")[0], dt(2117, 9, 4, 8))

    def test_hour_word_kor_five(self):
        self.assertEqual(extract("ötkor")[0], dt(2117, 9, 4, 5))

    def test_hour_word_kor_twelve(self):
        self.assertEqual(extract("tizenkettőkor")[0], dt(2117, 9, 4, 12))

    def test_reminder_sentence_bare_hour(self):
        res = extract("ébressz fel nyolckor")
        self.assertEqual(res[0], dt(2117, 9, 4, 8))

    def test_orakor_suffix(self):
        self.assertEqual(extract("kilenc órakor")[0], dt(2117, 9, 4, 9))


class TestFractionalHours(unittest.TestCase):
    """Hungarian counts fractions towards the NEXT hour."""

    def test_fel(self):
        self.assertEqual(extract("fél kilenc")[0], dt(2117, 9, 4, 8, 30))

    def test_negyed(self):
        self.assertEqual(extract("negyed kilenc")[0], dt(2117, 9, 4, 8, 15))

    def test_haromnegyed(self):
        self.assertEqual(extract("háromnegyed kilenc")[0], dt(2117, 9, 4, 8, 45))

    def test_fel_with_kor(self):
        self.assertEqual(extract("fél nyolckor")[0], dt(2117, 9, 4, 7, 30))

    def test_negyed_with_kor(self):
        self.assertEqual(extract("negyed nyolckor")[0], dt(2117, 9, 4, 7, 15))

    def test_haromnegyed_with_kor(self):
        self.assertEqual(extract("háromnegyed nyolckor")[0], dt(2117, 9, 4, 7, 45))

    def test_reminder_fractional_kor(self):
        res = extract("ébressz fel negyed nyolckor")
        self.assertEqual(res[0], dt(2117, 9, 4, 7, 15))


class TestPartsOfDay(unittest.TestCase):
    def test_noon(self):
        self.assertEqual(extract("délben")[0], dt(2117, 9, 4, 12))

    def test_midnight(self):
        self.assertEqual(extract("éjfélkor")[0], dt(2117, 9, 3, 0))

    def test_morning_hour(self):
        self.assertEqual(extract("holnap reggel 8-kor")[0], dt(2117, 9, 4, 8))

    def test_evening_qualifier(self):
        # "ma este" resolves to an evening default hour on the anchor day
        res = extract("ma este")
        self.assertEqual(res[0].date(), datetime(2117, 9, 3).date())
        self.assertGreaterEqual(res[0].hour, 18)


class TestRelativeDays(unittest.TestCase):
    def test_today(self):
        self.assertEqual(extract("ma")[0].date(), datetime(2117, 9, 3).date())

    def test_tomorrow(self):
        self.assertEqual(extract("holnap")[0], dt(2117, 9, 4))

    def test_yesterday(self):
        self.assertEqual(extract("tegnap")[0], dt(2117, 9, 2))

    def test_day_after_tomorrow(self):
        self.assertEqual(extract("holnapután")[0], dt(2117, 9, 5))

    def test_next_monday(self):
        self.assertEqual(extract("jövő hétfőn")[0], dt(2117, 9, 6))


class TestExplicitDates(unittest.TestCase):
    def test_month_day_rolls_forward(self):
        # june 3 has already passed relative to the september anchor
        self.assertEqual(extract("június 3")[0], dt(2118, 6, 3))

    def test_leap_day_walks_to_next_leap_year(self):
        self.assertEqual(extract("február 29")[0], dt(2120, 2, 29))

    def test_explicit_year(self):
        res = extract("2117 december 25")
        self.assertEqual(res[0].date(), datetime(2117, 12, 25).date())


class TestAdversarialInputs(unittest.TestCase):
    """Malformed and impossible inputs must return None, never crash."""

    def test_empty(self):
        self.assertIsNone(extract(""))

    def test_impossible_date_returns_none(self):
        self.assertIsNone(extract("április 31"))

    def test_impossible_leap_with_year_returns_none(self):
        self.assertIsNone(extract("2020 február 30"))

    def test_kor_homograph_akkor_not_a_time(self):
        # "akkor" (then) ends in "kor" but is not a clock reference
        self.assertIsNone(extract("akkor"))

    def test_kor_homograph_amikor_not_a_time(self):
        self.assertIsNone(extract("amikor jössz"))

    def test_pure_noise_returns_none(self):
        self.assertIsNone(extract("valami értelmetlen szöveg"))

    def test_no_crash_on_trailing_number(self):
        # a bare trailing number must not raise
        try:
            extract("találkozzunk 42")
        except Exception as e:  # pragma: no cover
            self.fail(f"unexpected crash: {e!r}")


if __name__ == "__main__":
    unittest.main()
