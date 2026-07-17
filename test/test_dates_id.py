import unittest
from datetime import datetime, time, timedelta

from dateutil.relativedelta import relativedelta

from ovos_date_parser import (nice_time, nice_duration, extract_duration,
                              nice_relative_time, extract_datetime)
from ovos_date_parser.duration import DurationResolution

# a fixed Wednesday noon anchor
ANCHOR = datetime(2026, 7, 15, 12, 0)


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


class TestExtractDatetimeId(unittest.TestCase):
    def _dt(self, text, **kw):
        return extract_datetime(text, "id", anchorDate=ANCHOR, **kw)

    def test_relative_days(self):
        self.assertEqual(self._dt("besok")[0], datetime(2026, 7, 16, 0, 0))
        self.assertEqual(self._dt("kemarin")[0], datetime(2026, 7, 14, 0, 0))
        self.assertEqual(self._dt("hari ini")[0], datetime(2026, 7, 15, 0, 0))
        self.assertEqual(self._dt("lusa")[0], datetime(2026, 7, 17, 0, 0))

    def test_weekday_next_last(self):
        self.assertEqual(self._dt("selasa depan")[0],
                         datetime(2026, 7, 21, 0, 0))
        self.assertEqual(self._dt("jumat lalu")[0],
                         datetime(2026, 7, 10, 0, 0))

    def test_offsets(self):
        self.assertEqual(self._dt("tiga hari lalu")[0],
                         datetime(2026, 7, 12, 0, 0))
        self.assertEqual(self._dt("dua jam lagi")[0],
                         datetime(2026, 7, 15, 14, 0))
        self.assertEqual(self._dt("minggu depan")[0],
                         datetime(2026, 7, 22, 0, 0))
        self.assertEqual(self._dt("minggu lalu")[0],
                         datetime(2026, 7, 8, 0, 0))

    def test_clock(self):
        self.assertEqual(self._dt("pukul 3")[0], datetime(2026, 7, 15, 3, 0))
        self.assertEqual(self._dt("jam 9")[0], datetime(2026, 7, 15, 9, 0))
        self.assertEqual(self._dt("15:30")[0], datetime(2026, 7, 15, 15, 30))

    def test_month_date(self):
        self.assertEqual(self._dt("17 juli 2026")[0],
                         datetime(2026, 7, 17, 0, 0))

    def test_combined_and_remainder(self):
        dt, rem = self._dt("ada rapat besok jam 10")
        self.assertEqual(dt, datetime(2026, 7, 16, 10, 0))
        self.assertEqual(rem, "ada rapat")

    def test_default_time(self):
        self.assertEqual(self._dt("besok", default_time=time(8, 30))[0],
                         datetime(2026, 7, 16, 8, 30))


class TestExtractDatetimeAdversarialId(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(extract_datetime("", "id", anchorDate=ANCHOR))

    def test_no_datetime(self):
        self.assertIsNone(
            extract_datetime("halo dunia", "id", anchorDate=ANCHOR))

    def test_offset_without_direction(self):
        self.assertIsNone(extract_datetime("tiga hari", "id",
                                           anchorDate=ANCHOR))

    def test_impossible_clock(self):
        self.assertIsNone(extract_datetime("pukul 30", "id",
                                           anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()


class TestRealSentencesId(unittest.TestCase):
    """Natural Indonesian sentences a user actually speaks/writes."""

    def _dt(self, text, **kw):
        return extract_datetime(text, "id", anchorDate=ANCHOR, **kw)

    def test_relative_day_sentences(self):
        self.assertEqual(self._dt("Meeting besok jam 10 pagi."),
                         (datetime(2026, 7, 16, 10, 0), "meeting pagi"))
        self.assertEqual(self._dt("Hari ini saya libur.")[0],
                         datetime(2026, 7, 15, 0, 0))
        self.assertEqual(self._dt("Kemarin hujan.")[0],
                         datetime(2026, 7, 14, 0, 0))
        self.assertEqual(self._dt("Lusa ada ujian.")[0],
                         datetime(2026, 7, 17, 0, 0))
        self.assertEqual(self._dt("Kemarin lusa dia datang.")[0],
                         datetime(2026, 7, 13, 0, 0))

    def test_offset_sentences(self):
        self.assertEqual(self._dt("Ingatkan saya dua jam lagi."),
                         (datetime(2026, 7, 15, 14, 0), "ingatkan saya"))
        self.assertEqual(self._dt("Tiga hari yang lalu dia pergi.")[0],
                         datetime(2026, 7, 12, 0, 0))
        self.assertEqual(
            self._dt("Tolong ingatkan lima belas menit lagi.")[0],
            datetime(2026, 7, 15, 12, 15))

    def test_weekday_sentences(self):
        self.assertEqual(self._dt("Ada acara Selasa depan."),
                         (datetime(2026, 7, 21, 0, 0), "ada acara"))
        self.assertEqual(self._dt("Jumat lalu kami bertemu.")[0],
                         datetime(2026, 7, 10, 0, 0))

    def test_period_sentences(self):
        self.assertEqual(self._dt("Minggu depan libur."),
                         (datetime(2026, 7, 22, 0, 0), "libur"))
        self.assertEqual(self._dt("Bulan depan gajian.")[0],
                         datetime(2026, 8, 15, 0, 0))
        self.assertEqual(self._dt("Tahun lalu kami menikah.")[0],
                         datetime(2025, 7, 15, 0, 0))

    def test_clock_sentences(self):
        self.assertEqual(self._dt("Sampai jumpa pukul 9.")[0],
                         datetime(2026, 7, 15, 9, 0))
        self.assertEqual(self._dt("Rapat pukul tiga sore.")[0],
                         datetime(2026, 7, 15, 3, 0))
        self.assertEqual(self._dt("Kereta berangkat 15:30.")[0],
                         datetime(2026, 7, 15, 15, 30))

    def test_month_date_sentences(self):
        self.assertEqual(self._dt("Ulang tahun 17 Agustus 2026!"),
                         (datetime(2026, 8, 17, 0, 0), "ulang tahun"))

    def test_combined_date_and_time(self):
        self.assertEqual(self._dt("Besok pukul 8 ada kelas.")[0],
                         datetime(2026, 7, 16, 8, 0))


class TestRealSentenceEdgesId(unittest.TestCase):
    def test_none_input(self):
        self.assertIsNone(extract_datetime(None, "id", anchorDate=ANCHOR))

    def test_whitespace_only(self):
        self.assertIsNone(extract_datetime("   ", "id", anchorDate=ANCHOR))

    def test_leading_trailing_junk(self):
        self.assertEqual(
            extract_datetime("... besok ...", "id", anchorDate=ANCHOR)[0],
            datetime(2026, 7, 16, 0, 0))

    def test_mixed_case(self):
        self.assertEqual(
            extract_datetime("ESOK jam 8", "id", anchorDate=ANCHOR)[0],
            datetime(2026, 7, 16, 8, 0))

    def test_language_code_variant(self):
        self.assertEqual(
            extract_datetime("besok", "id-ID", anchorDate=ANCHOR)[0],
            datetime(2026, 7, 16, 0, 0))

    def test_new_year_eve(self):
        self.assertEqual(
            extract_datetime("31 Desember 2026", "id", anchorDate=ANCHOR)[0],
            datetime(2026, 12, 31, 0, 0))

    def test_impossible_clock_hour(self):
        self.assertIsNone(
            extract_datetime("pukul 30", "id", anchorDate=ANCHOR))

    def test_cross_language_contamination(self):
        # Malay "semalam" (yesterday) / "minit" must not parse as Indonesian
        self.assertIsNone(extract_datetime("semalam", "id", anchorDate=ANCHOR))
        self.assertIsNone(
            extract_datetime("lima minit lagi", "id", anchorDate=ANCHOR))

    def test_omitted_half_idiom(self):
        # "setengah empat" (half to four) is deliberately not supported
        self.assertIsNone(
            extract_datetime("pukul setengah empat", "id", anchorDate=ANCHOR))
