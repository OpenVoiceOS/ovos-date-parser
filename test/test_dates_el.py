"""Tests for Modern Greek (el) date/time formatting and extraction.

The verified forms asserted below are drawn from standard Modern Greek
usage: weekday and month names (nominative and genitive), the idiomatic
clock-time constructions "και μισή" / "και τέταρτο" / "παρά τέταρτο", and
the feminine clock-hour numerals that agree with "ώρα". No expected string
is pinned from engine output.
"""
import unittest
from datetime import datetime

from ovos_date_parser.dates_el import (
    nice_year_el,
    nice_weekday_el,
    nice_month_el,
    nice_day_el,
    nice_date_time_el,
    nice_date_el,
    nice_time_el,
    WEEKDAYS_EL,
    MONTHS_EL,
)


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


if __name__ == "__main__":
    unittest.main()
