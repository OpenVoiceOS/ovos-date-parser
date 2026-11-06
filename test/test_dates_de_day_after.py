"""Regression tests: "der Tag nach/vor <heute|gestern|morgen|...>" for de.

Anchor: Saturday 2026-10-17 12:00 Europe/Lisbon. Expected dates are
hand-derived from the anchor, never pinned from engine output.
"""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


def _dt(text):
    res = extract_datetime(text, lang="de-DE", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestDayAfterBefore(unittest.TestCase):
    def test_day_after_tomorrow(self):
        self.assertEqual(_dt("der tag nach morgen"), datetime(2026, 10, 19))

    def test_day_after_tomorrow_capitalised(self):
        self.assertEqual(_dt("Der Tag nach morgen"), datetime(2026, 10, 19))

    def test_without_article(self):
        self.assertEqual(_dt("tag nach morgen"), datetime(2026, 10, 19))

    def test_with_preposition(self):
        self.assertEqual(_dt("am Tag nach morgen"), datetime(2026, 10, 19))

    def test_in_question(self):
        self.assertEqual(_dt("ist der Tag nach morgen ein Montag"),
                         datetime(2026, 10, 19))

    def test_with_time(self):
        self.assertEqual(_dt("wetter am tag nach morgen um 8 uhr"),
                         datetime(2026, 10, 19, 8))

    def test_day_after_today(self):
        self.assertEqual(_dt("der Tag nach heute"), datetime(2026, 10, 18))

    def test_day_after_yesterday(self):
        self.assertEqual(_dt("der Tag nach gestern"), datetime(2026, 10, 17))

    def test_day_after_day_after_tomorrow(self):
        self.assertEqual(_dt("der Tag nach übermorgen"), datetime(2026, 10, 20))

    def test_day_before_yesterday(self):
        self.assertEqual(_dt("der Tag vor gestern"), datetime(2026, 10, 15))

    def test_day_before_today(self):
        self.assertEqual(_dt("der Tag vor heute"), datetime(2026, 10, 16))

    def test_day_before_tomorrow(self):
        self.assertEqual(_dt("der Tag vor morgen"), datetime(2026, 10, 17))

    def test_day_before_day_before_yesterday(self):
        self.assertEqual(_dt("der Tag vor vorgestern"), datetime(2026, 10, 14))

    def test_one_day_before_tomorrow(self):
        self.assertEqual(_dt("ein Tag vor morgen"), datetime(2026, 10, 17))

    def test_two_days_before_tomorrow(self):
        self.assertEqual(_dt("zwei Tage vor morgen"), datetime(2026, 10, 16))

    def test_digit_days_before_tomorrow(self):
        self.assertEqual(_dt("1 tag vor morgen"), datetime(2026, 10, 17))

    def test_one_day_before_today(self):
        self.assertEqual(_dt("ein Tag vor heute"), datetime(2026, 10, 16))

    def test_two_days_before_yesterday(self):
        self.assertEqual(_dt("zwei Tage vor gestern"), datetime(2026, 10, 14))

    def test_greeting_is_not_a_day_count(self):
        self.assertEqual(_dt("guten Tag nach morgen"), datetime(2026, 10, 18))

    def test_every_day_is_not_a_day_count(self):
        self.assertEqual(_dt("jeden Tag nach morgen"), datetime(2026, 10, 18))

    def test_one_day_after_tomorrow(self):
        self.assertEqual(_dt("ein Tag nach morgen"), datetime(2026, 10, 19))

    def test_accusative_one_day_after_tomorrow(self):
        self.assertEqual(_dt("einen Tag nach morgen"), datetime(2026, 10, 19))

    def test_three_days_after_tomorrow(self):
        self.assertEqual(_dt("drei Tage nach morgen"), datetime(2026, 10, 21))

    def test_numbered_remainder(self):
        res = extract_datetime("wetter zwei Tage vor morgen",
                               lang="de-DE", anchorDate=ANCHOR)
        self.assertEqual(res[1], "wetter")

    def test_removes_phrase_from_remainder(self):
        res = extract_datetime("wetter am tag nach morgen",
                               lang="de-DE", anchorDate=ANCHOR)
        self.assertEqual(res[1], "wetter")


class TestNeighbouringFormsUnchanged(unittest.TestCase):
    def test_uebermorgen(self):
        self.assertEqual(_dt("übermorgen"), datetime(2026, 10, 19))

    def test_vorgestern(self):
        self.assertEqual(_dt("vorgestern"), datetime(2026, 10, 15))

    def test_morgen(self):
        self.assertEqual(_dt("morgen"), datetime(2026, 10, 18))

    def test_gestern(self):
        self.assertEqual(_dt("gestern"), datetime(2026, 10, 16))

    def test_heute(self):
        self.assertEqual(_dt("heute"), datetime(2026, 10, 17))

    def test_nach_morgen_is_a_from_anchor(self):
        self.assertEqual(_dt("nach morgen"), datetime(2026, 10, 18))

    def test_n_days_after_tomorrow(self):
        self.assertEqual(_dt("3 tage nach morgen"), datetime(2026, 10, 21))

    def test_one_day_after_tomorrow(self):
        self.assertEqual(_dt("1 tag nach morgen"), datetime(2026, 10, 19))

    def test_n_days_ago(self):
        self.assertEqual(_dt("vor 3 tagen"), datetime(2026, 10, 14))

    def test_in_n_days(self):
        self.assertEqual(_dt("in 3 tagen"), datetime(2026, 10, 20))

    def test_day_after_christmas_stays_holiday_relative(self):
        self.assertEqual(_dt("der Tag nach Weihnachten"),
                         datetime(2026, 12, 25))

    def test_after_noon(self):
        self.assertEqual(_dt("nach dem Mittag"), datetime(2026, 10, 17, 12))

    def test_day_after_noon(self):
        self.assertEqual(_dt("der tag nach dem mittag"),
                         datetime(2026, 10, 17, 12))


if __name__ == "__main__":
    unittest.main()
