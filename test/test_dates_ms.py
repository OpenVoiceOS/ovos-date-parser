import unittest
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from ovos_date_parser import (nice_time, nice_duration, extract_duration,
                              nice_relative_time)
from ovos_date_parser.duration import DurationResolution


class TestNiceTimeMs(unittest.TestCase):
    def test_display(self):
        dt = datetime(2026, 7, 17, 13, 4)
        self.assertEqual(nice_time(dt, "ms", speech=False, use_24hour=True),
                         "13:04")

    def test_24hour(self):
        self.assertEqual(
            nice_time(datetime(2026, 7, 17, 14, 0), "ms", use_24hour=True),
            "pukul empat belas")
        self.assertEqual(
            nice_time(datetime(2026, 7, 17, 14, 5), "ms", use_24hour=True),
            "pukul empat belas lebih lima")

    def test_12hour(self):
        self.assertEqual(nice_time(datetime(2026, 7, 17, 15, 0), "ms"),
                         "pukul tiga")
        self.assertEqual(nice_time(datetime(2026, 7, 17, 15, 15), "ms"),
                         "pukul tiga lebih lima belas")

    def test_midnight_noon(self):
        self.assertEqual(nice_time(datetime(2026, 7, 17, 0, 0), "ms"),
                         "tengah malam")
        self.assertEqual(nice_time(datetime(2026, 7, 17, 12, 0), "ms"),
                         "tengah hari")

    def test_ampm_period(self):
        self.assertTrue(
            nice_time(datetime(2026, 7, 17, 8, 0), "ms",
                      use_ampm=True).endswith("pagi"))
        self.assertTrue(
            nice_time(datetime(2026, 7, 17, 16, 0), "ms",
                      use_ampm=True).endswith("petang"))


class TestDurationMs(unittest.TestCase):
    def test_nice_duration(self):
        # Malay "second" is saat, distinct from Indonesian "detik"
        self.assertEqual(nice_duration(3720, "ms"), "satu jam dua minit")
        self.assertEqual(nice_duration(1, "ms"), "satu saat")

    def test_extract_units(self):
        self.assertEqual(
            extract_duration("tiga jam lima belas minit lagi", "ms"),
            (timedelta(hours=3, minutes=15), "lagi"))
        self.assertEqual(
            extract_duration("dua puluh saat", "ms"),
            (timedelta(seconds=20), ""))
        self.assertEqual(
            extract_duration("tiga tahun dua bulan", "ms",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=3, months=2), ""))

    def test_relative_time(self):
        anchor = datetime(2026, 7, 17, 14, 0, 0)
        self.assertEqual(
            nice_relative_time(anchor + timedelta(seconds=45), anchor, "ms"),
            "empat puluh lima saat")

    def test_roundtrip_sweep(self):
        vals = list(range(1, 240)) + [3599, 3600, 3661, 86399, 86400, 90061]
        for s in vals:
            spoken = nice_duration(s, "ms")
            dur, _ = extract_duration(spoken, "ms")
            self.assertEqual(int(dur.total_seconds()), s,
                             f"roundtrip {s} via {spoken!r}")


class TestAdversarialMs(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(extract_duration("", "ms"))

    def test_no_duration(self):
        self.assertEqual(extract_duration("helo dunia", "ms"),
                         (None, "helo dunia"))

    def test_bare_unit_without_number(self):
        self.assertEqual(extract_duration("jam", "ms"), (None, "jam"))

    def test_number_without_unit(self):
        self.assertEqual(extract_duration("lima", "ms"), (None, "5"))

    def test_uses_malay_not_indonesian_minute(self):
        # Indonesian "menit" must NOT match Malay (which uses "minit")
        self.assertEqual(extract_duration("lima menit", "ms")[0], None)

    def test_zero(self):
        dur, _ = extract_duration("sifar minit", "ms")
        self.assertEqual(dur, timedelta(0))


if __name__ == "__main__":
    unittest.main()
