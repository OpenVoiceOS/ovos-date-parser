"""Regression tests: "de dag na/voor <vandaag|gisteren|morgen|...>" for nl.

Anchor: Saturday 2026-10-17 12:00 Europe/Lisbon. Expected dates are
hand-derived from the anchor, never pinned from engine output.
"""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


def _dt(text):
    res = extract_datetime(text, lang="nl-NL", anchorDate=ANCHOR)
    assert res is not None, "no datetime extracted from %r" % text
    d = res[0]
    return d.replace(tzinfo=None) if d.tzinfo else d


class TestDayAfterBefore(unittest.TestCase):
    def test_day_after_today(self):
        self.assertEqual(_dt("de dag na vandaag"), datetime(2026, 10, 18))

    def test_without_article(self):
        self.assertEqual(_dt("dag na vandaag"), datetime(2026, 10, 18))

    def test_with_preposition(self):
        self.assertEqual(_dt("op de dag na vandaag"), datetime(2026, 10, 18))

    def test_in_question(self):
        self.assertEqual(_dt("is de dag na vandaag een zondag"),
                         datetime(2026, 10, 18))

    def test_with_time(self):
        self.assertEqual(_dt("weer op de dag na morgen om 8:00"),
                         datetime(2026, 10, 19, 8))

    def test_day_after_tomorrow(self):
        self.assertEqual(_dt("de dag na morgen"), datetime(2026, 10, 19))

    def test_day_after_yesterday(self):
        self.assertEqual(_dt("de dag na gisteren"), datetime(2026, 10, 17))

    def test_day_after_day_after_tomorrow(self):
        self.assertEqual(_dt("de dag na overmorgen"), datetime(2026, 10, 20))

    def test_day_after_day_before_yesterday(self):
        self.assertEqual(_dt("de dag na eergisteren"), datetime(2026, 10, 16))

    def test_day_before_yesterday(self):
        self.assertEqual(_dt("de dag voor gisteren"), datetime(2026, 10, 15))

    def test_day_before_today(self):
        self.assertEqual(_dt("de dag voor vandaag"), datetime(2026, 10, 16))

    def test_day_before_tomorrow(self):
        self.assertEqual(_dt("de dag voor morgen"), datetime(2026, 10, 17))

    def test_day_before_day_before_yesterday(self):
        self.assertEqual(_dt("de dag voor eergisteren"), datetime(2026, 10, 14))

    def test_removes_phrase_from_remainder(self):
        res = extract_datetime("weer op de dag na vandaag",
                               lang="nl-NL", anchorDate=ANCHOR)
        self.assertEqual(res[1], "weer")


class TestNeighbouringFormsUnchanged(unittest.TestCase):
    def test_overmorgen(self):
        self.assertEqual(_dt("overmorgen"), datetime(2026, 10, 19))

    def test_morgen(self):
        self.assertEqual(_dt("morgen"), datetime(2026, 10, 18))

    def test_vandaag(self):
        self.assertEqual(_dt("vandaag"), datetime(2026, 10, 17))

    def test_na_vandaag_is_a_from_anchor(self):
        self.assertEqual(_dt("3 dagen na morgen"), datetime(2026, 10, 21))

    def test_every_day_is_not_a_day_count(self):
        d, rest = extract_datetime("elke dag na vandaag", lang="nl-NL",
                                   anchorDate=ANCHOR)
        self.assertEqual(d.replace(tzinfo=None), datetime(2026, 10, 17))
        self.assertEqual(rest, "elke dag")

    def test_one_day_after_today(self):
        self.assertEqual(_dt("1 dag na vandaag"), datetime(2026, 10, 18))

    def test_n_days_ago(self):
        self.assertEqual(_dt("3 dagen geleden"), datetime(2026, 10, 14))

    def test_in_n_days(self):
        self.assertEqual(_dt("over 3 dagen"), datetime(2026, 10, 20))

    def test_day_after_christmas_stays_holiday_relative(self):
        self.assertEqual(_dt("de dag na kerst"), datetime(2026, 12, 25))

    def test_after_noon(self):
        self.assertEqual(_dt("na de middag"), datetime(2026, 10, 17, 15))


if __name__ == "__main__":
    unittest.main()
