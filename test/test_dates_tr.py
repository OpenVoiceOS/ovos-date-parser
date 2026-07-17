import unittest
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from ovos_date_parser import (nice_time, nice_duration, extract_duration,
                              nice_relative_time)
from ovos_date_parser.duration import DurationResolution


class TestNiceTimeTr(unittest.TestCase):
    def test_display(self):
        dt = datetime(2026, 7, 17, 13, 4)
        self.assertEqual(nice_time(dt, "tr", speech=False, use_24hour=True),
                         "13:04")
        self.assertEqual(nice_time(dt, "tr", speech=False), "01:04")

    def test_24hour(self):
        self.assertEqual(
            nice_time(datetime(2026, 7, 17, 14, 0), "tr", use_24hour=True),
            "saat on dört")
        # sub-ten minute gets the explicit zero to stay unambiguous
        self.assertEqual(
            nice_time(datetime(2026, 7, 17, 14, 5), "tr", use_24hour=True),
            "saat on dört sıfır beş")
        self.assertEqual(
            nice_time(datetime(2026, 7, 17, 9, 30), "tr", use_24hour=True),
            "saat dokuz otuz")

    def test_12hour(self):
        self.assertEqual(nice_time(datetime(2026, 7, 17, 15, 0), "tr"),
                         "saat üç")
        self.assertEqual(nice_time(datetime(2026, 7, 17, 15, 15), "tr"),
                         "saat üç on beş")

    def test_midnight_noon(self):
        self.assertEqual(nice_time(datetime(2026, 7, 17, 0, 0), "tr"),
                         "gece yarısı")
        self.assertEqual(nice_time(datetime(2026, 7, 17, 12, 0), "tr"),
                         "öğle")

    def test_ampm_period(self):
        self.assertTrue(
            nice_time(datetime(2026, 7, 17, 15, 0), "tr",
                      use_ampm=True).endswith("öğleden sonra"))
        self.assertTrue(
            nice_time(datetime(2026, 7, 17, 8, 0), "tr",
                      use_ampm=True).endswith("sabah"))


class TestDurationTr(unittest.TestCase):
    def test_nice_duration(self):
        self.assertEqual(nice_duration(3720, "tr"), "bir saat iki dakika")
        self.assertEqual(nice_duration(1, "tr"), "bir saniye")
        self.assertEqual(nice_duration(90061, "tr"),
                         "bir gün  bir saat bir dakika bir saniye")

    def test_extract_units(self):
        self.assertEqual(
            extract_duration("iki saat otuz dakika sonra", "tr"),
            (timedelta(hours=2, minutes=30), "sonra"))
        self.assertEqual(
            extract_duration("on beş dakika", "tr"),
            (timedelta(minutes=15), ""))
        self.assertEqual(
            extract_duration("üç yıl iki ay", "tr",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=3, months=2), ""))
        # "sene" is an accepted synonym for "yıl" (year)
        self.assertEqual(
            extract_duration("bir sene", "tr",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=1), ""))

    def test_relative_time(self):
        anchor = datetime(2026, 7, 17, 14, 0, 0)
        self.assertEqual(
            nice_relative_time(anchor + timedelta(seconds=45), anchor, "tr"),
            "kırk beş saniye")

    def test_roundtrip_sweep(self):
        vals = list(range(1, 240)) + [3599, 3600, 3661, 86399, 86400, 90061]
        for s in vals:
            spoken = nice_duration(s, "tr")
            dur, _ = extract_duration(spoken, "tr")
            self.assertEqual(int(dur.total_seconds()), s,
                             f"roundtrip {s} via {spoken!r}")


class TestAdversarialTr(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(extract_duration("", "tr"))

    def test_no_duration(self):
        self.assertEqual(extract_duration("merhaba dünya", "tr"),
                         (None, "merhaba dünya"))

    def test_bare_unit_without_number(self):
        # a unit word with no numeral must not be consumed
        self.assertEqual(extract_duration("saat", "tr"), (None, "saat"))

    def test_number_without_unit(self):
        self.assertEqual(extract_duration("beş", "tr"), (None, "5"))

    def test_weekday_not_month(self):
        # "ay" is month; without a preceding numeral nothing matches
        self.assertEqual(extract_duration("bu ay", "tr"), (None, "bu ay"))

    def test_zero(self):
        dur, _ = extract_duration("sıfır dakika", "tr")
        self.assertEqual(dur, timedelta(0))


if __name__ == "__main__":
    unittest.main()
