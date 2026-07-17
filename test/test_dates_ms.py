import unittest
from datetime import datetime, time, timedelta

from dateutil.relativedelta import relativedelta

from ovos_date_parser import (nice_time, nice_duration, extract_duration,
                              nice_relative_time, extract_datetime)
from ovos_date_parser.duration import DurationResolution

# a fixed Wednesday noon anchor
ANCHOR = datetime(2026, 7, 15, 12, 0)


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


class TestRealSentencesMs(unittest.TestCase):
    """Natural Malay sentences a user actually speaks/writes."""

    def _dt(self, text, **kw):
        return extract_datetime(text, "ms", anchorDate=ANCHOR, **kw)

    def test_relative_day_sentences(self):
        self.assertEqual(self._dt("Jumpa esok pukul 9 pagi."),
                         (datetime(2026, 7, 16, 9, 0), "jumpa pagi"))
        self.assertEqual(self._dt("Hari ini saya cuti.")[0],
                         datetime(2026, 7, 15, 0, 0))
        self.assertEqual(self._dt("Semalam hujan.")[0],
                         datetime(2026, 7, 14, 0, 0))
        self.assertEqual(self._dt("Lusa ada peperiksaan.")[0],
                         datetime(2026, 7, 17, 0, 0))

    def test_offset_sentences(self):
        self.assertEqual(self._dt("Ingatkan saya dua jam lagi."),
                         (datetime(2026, 7, 15, 14, 0), "ingatkan saya"))
        self.assertEqual(self._dt("Lima hari lepas dia pergi.")[0],
                         datetime(2026, 7, 10, 0, 0))
        self.assertEqual(
            self._dt("Tolong ingatkan lima belas minit lagi.")[0],
            datetime(2026, 7, 15, 12, 15))

    def test_weekday_sentences(self):
        self.assertEqual(self._dt("Mesyuarat Selasa depan."),
                         (datetime(2026, 7, 21, 0, 0), "mesyuarat"))
        self.assertEqual(self._dt("Jumaat lepas kami berjumpa.")[0],
                         datetime(2026, 7, 10, 0, 0))
        # "Ahad ini" resolves to the coming Sunday
        self.assertEqual(self._dt("Ahad ini ada kenduri.")[0],
                         datetime(2026, 7, 19, 0, 0))

    def test_period_sentences(self):
        self.assertEqual(self._dt("Minggu depan cuti."),
                         (datetime(2026, 7, 22, 0, 0), "cuti"))
        self.assertEqual(self._dt("Bulan lepas kami berpindah.")[0],
                         datetime(2026, 6, 15, 0, 0))
        self.assertEqual(self._dt("Tahun depan saya bergraduasi.")[0],
                         datetime(2027, 7, 15, 0, 0))

    def test_clock_sentences(self):
        self.assertEqual(self._dt("Jumpa pukul 3.")[0],
                         datetime(2026, 7, 15, 3, 0))
        self.assertEqual(self._dt("Kereta bertolak 15:30.")[0],
                         datetime(2026, 7, 15, 15, 30))

    def test_month_date_sentences(self):
        self.assertEqual(self._dt("Hari lahir 17 Julai 2026."),
                         (datetime(2026, 7, 17, 0, 0), "hari lahir"))
        # Malay month name "Mac" (March), distinct from Indonesian "Maret"
        self.assertEqual(self._dt("3 Mac 2027")[0],
                         datetime(2027, 3, 3, 0, 0))

    def test_combined_date_and_time(self):
        self.assertEqual(self._dt("Esok pukul 8 ada kelas.")[0],
                         datetime(2026, 7, 16, 8, 0))


class TestRealSentenceEdgesMs(unittest.TestCase):
    def test_none_input(self):
        self.assertIsNone(extract_datetime(None, "ms", anchorDate=ANCHOR))

    def test_whitespace_only(self):
        self.assertIsNone(extract_datetime("   ", "ms", anchorDate=ANCHOR))

    def test_leading_trailing_junk(self):
        self.assertEqual(
            extract_datetime("... esok ...", "ms", anchorDate=ANCHOR)[0],
            datetime(2026, 7, 16, 0, 0))

    def test_mixed_case(self):
        self.assertEqual(
            extract_datetime("ESOK Pukul 8", "ms", anchorDate=ANCHOR)[0],
            datetime(2026, 7, 16, 8, 0))

    def test_language_code_variant(self):
        self.assertEqual(
            extract_datetime("esok", "ms-MY", anchorDate=ANCHOR)[0],
            datetime(2026, 7, 16, 0, 0))

    def test_new_year_eve(self):
        self.assertEqual(
            extract_datetime("31 Disember 2026", "ms", anchorDate=ANCHOR)[0],
            datetime(2026, 12, 31, 0, 0))

    def test_impossible_clock_hour(self):
        self.assertIsNone(
            extract_datetime("pukul 30", "ms", anchorDate=ANCHOR))

    def test_cross_language_contamination(self):
        # Indonesian "kemarin" (yesterday) / "menit" must not parse as Malay
        self.assertIsNone(extract_datetime("kemarin", "ms", anchorDate=ANCHOR))
        self.assertIsNone(
            extract_datetime("lima menit lagi", "ms", anchorDate=ANCHOR))

    def test_omitted_half_idiom(self):
        # "pukul setengah empat" (half to four) is deliberately not supported
        self.assertIsNone(
            extract_datetime("pukul setengah empat", "ms", anchorDate=ANCHOR))


class TestExtractDatetimeMs(unittest.TestCase):
    def _dt(self, text, **kw):
        return extract_datetime(text, "ms", anchorDate=ANCHOR, **kw)

    def test_relative_days(self):
        self.assertEqual(self._dt("esok")[0], datetime(2026, 7, 16, 0, 0))
        self.assertEqual(self._dt("semalam")[0], datetime(2026, 7, 14, 0, 0))
        self.assertEqual(self._dt("hari ini")[0], datetime(2026, 7, 15, 0, 0))
        self.assertEqual(self._dt("lusa")[0], datetime(2026, 7, 17, 0, 0))

    def test_weekday_next_last(self):
        self.assertEqual(self._dt("selasa depan")[0],
                         datetime(2026, 7, 21, 0, 0))
        self.assertEqual(self._dt("jumaat lepas")[0],
                         datetime(2026, 7, 10, 0, 0))

    def test_offsets(self):
        self.assertEqual(self._dt("lima hari lepas")[0],
                         datetime(2026, 7, 10, 0, 0))
        self.assertEqual(self._dt("dua jam lagi")[0],
                         datetime(2026, 7, 15, 14, 0))
        self.assertEqual(self._dt("minggu depan")[0],
                         datetime(2026, 7, 22, 0, 0))
        self.assertEqual(self._dt("tahun lepas")[0],
                         datetime(2025, 7, 15, 0, 0))

    def test_clock(self):
        self.assertEqual(self._dt("pukul 3")[0], datetime(2026, 7, 15, 3, 0))
        self.assertEqual(self._dt("jam 9")[0], datetime(2026, 7, 15, 9, 0))
        self.assertEqual(self._dt("15:30")[0], datetime(2026, 7, 15, 15, 30))

    def test_month_date(self):
        self.assertEqual(self._dt("17 julai 2026")[0],
                         datetime(2026, 7, 17, 0, 0))

    def test_default_time(self):
        self.assertEqual(self._dt("esok", default_time=time(8, 30))[0],
                         datetime(2026, 7, 16, 8, 30))


class TestExtractDatetimeAdversarialMs(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(extract_datetime("", "ms", anchorDate=ANCHOR))

    def test_no_datetime(self):
        self.assertIsNone(
            extract_datetime("helo dunia", "ms", anchorDate=ANCHOR))

    def test_offset_without_direction(self):
        self.assertIsNone(extract_datetime("lima hari", "ms",
                                           anchorDate=ANCHOR))

    def test_impossible_clock(self):
        self.assertIsNone(extract_datetime("pukul 30", "ms",
                                           anchorDate=ANCHOR))
