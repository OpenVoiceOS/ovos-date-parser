import unittest
from datetime import datetime, time, timedelta

from dateutil.relativedelta import relativedelta

from ovos_date_parser import (nice_time, nice_duration, extract_duration,
                              nice_relative_time, extract_datetime)
from ovos_date_parser.duration import DurationResolution

# a fixed Wednesday noon anchor
ANCHOR = datetime(2026, 7, 15, 12, 0)


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


class TestExtractDatetimeTr(unittest.TestCase):
    def _dt(self, text, **kw):
        return extract_datetime(text, "tr", anchorDate=ANCHOR, **kw)

    def test_relative_days(self):
        self.assertEqual(self._dt("yarın")[0], datetime(2026, 7, 16, 0, 0))
        self.assertEqual(self._dt("dün")[0], datetime(2026, 7, 14, 0, 0))
        self.assertEqual(self._dt("bugün")[0], datetime(2026, 7, 15, 0, 0))
        self.assertEqual(self._dt("öbür gün")[0], datetime(2026, 7, 17, 0, 0))

    def test_weekday_next_last(self):
        self.assertEqual(self._dt("gelecek salı")[0],
                         datetime(2026, 7, 21, 0, 0))
        self.assertEqual(self._dt("geçen cuma")[0],
                         datetime(2026, 7, 10, 0, 0))
        # bare weekday resolves to the next occurrence
        self.assertEqual(self._dt("pazartesi")[0],
                         datetime(2026, 7, 20, 0, 0))

    def test_offsets(self):
        self.assertEqual(self._dt("üç gün önce")[0],
                         datetime(2026, 7, 12, 0, 0))
        self.assertEqual(self._dt("iki saat sonra")[0],
                         datetime(2026, 7, 15, 14, 0))
        self.assertEqual(self._dt("gelecek hafta")[0],
                         datetime(2026, 7, 22, 0, 0))

    def test_clock(self):
        self.assertEqual(self._dt("saat 3")[0], datetime(2026, 7, 15, 3, 0))
        self.assertEqual(self._dt("saat üç")[0], datetime(2026, 7, 15, 3, 0))
        self.assertEqual(self._dt("15:30")[0], datetime(2026, 7, 15, 15, 30))

    def test_month_date(self):
        self.assertEqual(self._dt("26 temmuz 2026")[0],
                         datetime(2026, 7, 26, 0, 0))

    def test_combined_and_remainder(self):
        dt, rem = self._dt("bana üç saat sonra hatırlat")
        self.assertEqual(dt, datetime(2026, 7, 15, 15, 0))
        self.assertEqual(rem, "bana hatırlat")
        self.assertEqual(self._dt("yarın saat 3")[0],
                         datetime(2026, 7, 16, 3, 0))

    def test_default_time(self):
        self.assertEqual(self._dt("yarın", default_time=time(8, 30))[0],
                         datetime(2026, 7, 16, 8, 30))


class TestExtractDatetimeAdversarialTr(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(extract_datetime("", "tr", anchorDate=ANCHOR))

    def test_no_datetime(self):
        self.assertIsNone(
            extract_datetime("merhaba dünya", "tr", anchorDate=ANCHOR))

    def test_number_without_unit(self):
        self.assertIsNone(extract_datetime("beş", "tr", anchorDate=ANCHOR))

    def test_offset_without_direction(self):
        # "üç gün" alone is a bare span, not a datetime; needs önce/sonra
        self.assertIsNone(extract_datetime("üç gün", "tr", anchorDate=ANCHOR))

    def test_impossible_clock(self):
        # 25:00 is not a valid clock time and must be ignored
        self.assertIsNone(extract_datetime("25:00", "tr", anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()


class TestRealSentencesTr(unittest.TestCase):
    """Natural Turkish sentences a user actually speaks/writes."""

    def _dt(self, text, **kw):
        return extract_datetime(text, "tr", anchorDate=ANCHOR, **kw)

    def test_relative_day_sentences(self):
        self.assertEqual(self._dt("Toplantı yarın."),
                         [datetime(2026, 7, 16, 0, 0), "toplantı"])
        self.assertEqual(self._dt("Dün akşam geldim.")[0],
                         datetime(2026, 7, 14, 0, 0))
        self.assertEqual(self._dt("Öbür gün tatil.")[0],
                         datetime(2026, 7, 17, 0, 0))
        self.assertEqual(self._dt("Önceki gün aramıştı.")[0],
                         datetime(2026, 7, 13, 0, 0))
        self.assertEqual(self._dt("Bugün işe gitmedim.")[0],
                         datetime(2026, 7, 15, 0, 0))

    def test_offset_sentences(self):
        self.assertEqual(self._dt("Beni iki saat sonra uyandır."),
                         [datetime(2026, 7, 15, 14, 0), "beni uyandır"])
        self.assertEqual(self._dt("Üç gün önce geldi."),
                         [datetime(2026, 7, 12, 0, 0), "geldi"])
        self.assertEqual(self._dt("On beş dakika sonra çıkıyoruz.")[0],
                         datetime(2026, 7, 15, 12, 15))
        # a whole-day-or-larger offset resolves to midnight of that day
        self.assertEqual(self._dt("Bir hafta sonra sınav var.")[0],
                         datetime(2026, 7, 22, 0, 0))

    def test_weekday_sentences(self):
        self.assertEqual(self._dt("Gelecek salı görüşürüz."),
                         [datetime(2026, 7, 21, 0, 0), "görüşürüz"])
        self.assertEqual(self._dt("Geçen cuma oradaydım."),
                         [datetime(2026, 7, 10, 0, 0), "oradaydım"])
        self.assertEqual(self._dt("Geçen pazartesi başladı.")[0],
                         datetime(2026, 7, 13, 0, 0))
        self.assertEqual(self._dt("Pazartesi spora gidiyorum."),
                         [datetime(2026, 7, 20, 0, 0), "spora gidiyorum"])

    def test_period_sentences(self):
        self.assertEqual(self._dt("Gelecek hafta tatildeyim."),
                         [datetime(2026, 7, 22, 0, 0), "tatildeyim"])
        self.assertEqual(self._dt("Geçen ay taşındık.")[0],
                         datetime(2026, 6, 15, 0, 0))
        self.assertEqual(self._dt("Gelecek yıl mezun oluyorum.")[0],
                         datetime(2027, 7, 15, 0, 0))

    def test_clock_sentences(self):
        # Turkish written locative suffix on the hour
        self.assertEqual(self._dt("Alarmı saat 7'ye kur."),
                         [datetime(2026, 7, 15, 7, 0), "alarmı kur"])
        self.assertEqual(self._dt("Randevu 15:30'da."),
                         [datetime(2026, 7, 15, 15, 30), "randevu"])
        self.assertEqual(self._dt("Bugün saat 23:59")[0],
                         datetime(2026, 7, 15, 23, 59))
        # spelled-out clock hour
        self.assertEqual(self._dt("Saat üç buluşalım.")[0],
                         datetime(2026, 7, 15, 3, 0))

    def test_month_date_sentences(self):
        self.assertEqual(self._dt("Doğum günüm 26 Temmuz 2026."),
                         [datetime(2026, 7, 26, 0, 0), "doğum günüm"])
        # a past month rolls to next year
        self.assertEqual(self._dt("5 Nisan")[0], datetime(2027, 4, 5, 0, 0))

    def test_combined_date_and_time(self):
        self.assertEqual(self._dt("Yarın saat 9'da toplantı var.")[0],
                         datetime(2026, 7, 16, 9, 0))


class TestRealSentenceEdgesTr(unittest.TestCase):
    def test_none_input(self):
        self.assertIsNone(extract_datetime(None, "tr", anchorDate=ANCHOR))

    def test_whitespace_only(self):
        self.assertIsNone(extract_datetime("   ", "tr", anchorDate=ANCHOR))

    def test_leading_trailing_junk(self):
        self.assertEqual(
            extract_datetime("!!! yarın !!!", "tr", anchorDate=ANCHOR)[0],
            datetime(2026, 7, 16, 0, 0))

    def test_mixed_case_with_dotless_i(self):
        # "YARIN" must lowercase to "yarın" (dotless), not "yarin"
        self.assertEqual(
            extract_datetime("YARIN Saat 3", "tr", anchorDate=ANCHOR)[0],
            datetime(2026, 7, 16, 3, 0))

    def test_language_code_variant(self):
        self.assertEqual(
            extract_datetime("yarın", "tr-TR", anchorDate=ANCHOR)[0],
            datetime(2026, 7, 16, 0, 0))

    def test_leap_day(self):
        self.assertEqual(
            extract_datetime("29 Şubat 2028", "tr", anchorDate=ANCHOR)[0],
            datetime(2028, 2, 29, 0, 0))

    def test_impossible_clock_hour(self):
        self.assertIsNone(
            extract_datetime("saat 25", "tr", anchorDate=ANCHOR))

    def test_cross_language_contamination(self):
        # Indonesian "besok"/"lusa" must not parse as Turkish
        self.assertIsNone(extract_datetime("besok", "tr", anchorDate=ANCHOR))
        self.assertIsNone(extract_datetime("lusa", "tr", anchorDate=ANCHOR))

    def test_omitted_half_idiom(self):
        # the "buçuk" (half past) idiom is deliberately not supported: the
        # number parser reads "dokuz buçuk" as 9.5, which is not a valid
        # clock token, so nothing date/time related is extracted
        self.assertIsNone(
            extract_datetime("saat dokuz buçuk", "tr", anchorDate=ANCHOR))
