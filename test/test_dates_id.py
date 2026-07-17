import unittest
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from ovos_date_parser import (nice_time, nice_duration, extract_duration,
                              nice_relative_time)
from ovos_date_parser.duration import DurationResolution


class TestNiceTimeId(unittest.TestCase):
    def test_display(self):
        dt = datetime(2026, 7, 17, 13, 4)
        self.assertEqual(nice_time(dt, "id", speech=False, use_24hour=True),
                         "13:04")

    def test_24hour(self):
        self.assertEqual(
            nice_time(datetime(2026, 7, 17, 14, 0), "id", use_24hour=True),
            "pukul empat belas")
        self.assertEqual(
            nice_time(datetime(2026, 7, 17, 14, 5), "id", use_24hour=True),
            "pukul empat belas lewat lima")

    def test_12hour(self):
        self.assertEqual(nice_time(datetime(2026, 7, 17, 15, 0), "id"),
                         "pukul tiga")
        self.assertEqual(nice_time(datetime(2026, 7, 17, 15, 15), "id"),
                         "pukul tiga lewat lima belas")

    def test_midnight_noon(self):
        self.assertEqual(nice_time(datetime(2026, 7, 17, 0, 0), "id"),
                         "tengah malam")
        self.assertEqual(nice_time(datetime(2026, 7, 17, 12, 0), "id"),
                         "tengah hari")

    def test_ampm_period(self):
        self.assertTrue(
            nice_time(datetime(2026, 7, 17, 8, 0), "id",
                      use_ampm=True).endswith("pagi"))
        self.assertTrue(
            nice_time(datetime(2026, 7, 17, 20, 0), "id",
                      use_ampm=True).endswith("malam"))


class TestDurationId(unittest.TestCase):
    def test_nice_duration(self):
        self.assertEqual(nice_duration(3720, "id"), "satu jam dua menit")
        self.assertEqual(nice_duration(1, "id"), "satu detik")

    def test_extract_units(self):
        self.assertEqual(
            extract_duration("dua jam tiga puluh menit lagi", "id"),
            (timedelta(hours=2, minutes=30), "lagi"))
        self.assertEqual(
            extract_duration("lima belas menit", "id"),
            (timedelta(minutes=15), ""))
        self.assertEqual(
            extract_duration("tiga tahun dua bulan", "id",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=3, months=2), ""))
        # "pekan" is an accepted synonym for "minggu" (week)
        self.assertEqual(
            extract_duration("dua pekan", "id")[0], timedelta(weeks=2))

    def test_relative_time(self):
        anchor = datetime(2026, 7, 17, 14, 0, 0)
        self.assertEqual(
            nice_relative_time(anchor + timedelta(seconds=45), anchor, "id"),
            "empat puluh lima detik")

    def test_roundtrip_sweep(self):
        vals = list(range(1, 240)) + [3599, 3600, 3661, 86399, 86400, 90061]
        for s in vals:
            spoken = nice_duration(s, "id")
            dur, _ = extract_duration(spoken, "id")
            self.assertEqual(int(dur.total_seconds()), s,
                             f"roundtrip {s} via {spoken!r}")


class TestAdversarialId(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(extract_duration("", "id"))

    def test_no_duration(self):
        self.assertEqual(extract_duration("halo dunia", "id"),
                         (None, "halo dunia"))

    def test_bare_unit_without_number(self):
        self.assertEqual(extract_duration("jam", "id"), (None, "jam"))

    def test_number_without_unit(self):
        self.assertEqual(extract_duration("lima", "id"), (None, "5"))

    def test_uses_indonesian_not_malay_units(self):
        # "detik"/"menit" are Indonesian; Malay "minit" must NOT match here
        self.assertEqual(extract_duration("lima minit", "id")[0], None)

    def test_zero(self):
        dur, _ = extract_duration("nol menit", "id")
        self.assertEqual(dur, timedelta(0))


if __name__ == "__main__":
    unittest.main()
