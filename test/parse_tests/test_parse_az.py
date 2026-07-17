import unittest
from datetime import datetime, timedelta

from ovos_date_parser.dates_az import (
    extract_datetime_az,
    extract_duration_az,
    nice_time_az,
    nice_duration_az,
)

# A fixed weekday reference: 2017-06-27 is a Tuesday, 13:04 local
ANCHOR = datetime(2017, 6, 27, 13, 4)


def extract_dt(text, anchor=ANCHOR):
    return extract_datetime_az(text, anchor)


class TestExtractDatetimeAz(unittest.TestCase):
    def test_relative_days(self):
        self.assertEqual(extract_dt("bu gün")[0], datetime(2017, 6, 27, 0, 0))
        self.assertEqual(extract_dt("sabah")[0], datetime(2017, 6, 28, 0, 0))
        self.assertEqual(extract_dt("dünən")[0], datetime(2017, 6, 26, 0, 0))
        self.assertEqual(extract_dt("srağagün")[0], datetime(2017, 6, 25, 0, 0))
        self.assertEqual(extract_dt("birigün")[0], datetime(2017, 6, 29, 0, 0))

    def test_relative_units(self):
        self.assertEqual(extract_dt("gələn il")[0], datetime(2018, 6, 27, 0, 0))
        self.assertEqual(extract_dt("keçən il")[0], datetime(2016, 6, 27, 0, 0))
        self.assertEqual(extract_dt("keçən ay")[0], datetime(2017, 5, 27, 0, 0))
        self.assertEqual(extract_dt("gələn həftə")[0], datetime(2017, 7, 4, 0, 0))
        self.assertEqual(extract_dt("keçən həftə")[0], datetime(2017, 6, 20, 0, 0))
        self.assertEqual(extract_dt("5 gün sonra")[0], datetime(2017, 7, 2, 0, 0))

    def test_explicit_dates(self):
        # day + month, spoken naturally
        self.assertEqual(extract_dt("3 avqust")[0], datetime(2017, 8, 3, 0, 0))
        # 5 iyun has already passed this year -> rolls to next year
        self.assertEqual(extract_dt("5 iyun")[0], datetime(2018, 6, 5, 0, 0))
        # explicit 4-digit year is honoured
        self.assertEqual(extract_dt("3 avqust 2020")[0], datetime(2020, 8, 3, 0, 0))
        self.assertEqual(extract_dt("5 iyun 2019")[0], datetime(2019, 6, 5, 0, 0))

    def test_leap_day_does_not_crash(self):
        # regression: "29 fevral" used to raise ValueError because the
        # date was parsed against a non-leap default year
        res = extract_dt("29 fevral", datetime(2020, 1, 1))
        self.assertEqual(res[0], datetime(2020, 2, 29, 0, 0))

    def test_clock_after_saat(self):
        # regression: "saat N" (o'clock) dropped the hour entirely
        self.assertEqual(extract_dt("səhər saat 8")[0], datetime(2017, 6, 28, 8, 0))
        self.assertEqual(extract_dt("saat 8:30")[0], datetime(2017, 6, 28, 8, 30))

    def test_part_of_day_applies_pm(self):
        # regression: evening/afternoon qualifier was not shifting the
        # explicit clock hour into the afternoon
        self.assertEqual(extract_dt("axşam saat 8")[0], datetime(2017, 6, 27, 20, 0))
        self.assertEqual(extract_dt("günorta saat 4")[0], datetime(2017, 6, 27, 16, 0))
        self.assertEqual(extract_dt("günorta 4 də")[0], datetime(2017, 6, 27, 16, 0))

    def test_dated_clock_no_year_crash(self):
        # regression: a trailing clock digit after a date was taken as a
        # year and fed to strptime, raising ValueError
        res = extract_dt("3 avqust saat 8")
        self.assertEqual(res[0], datetime(2017, 8, 3, 8, 0))
        # a bare trailing single digit must not crash either
        self.assertIsNotNone(extract_dt("3 avqust 8"))

    def test_remainder_is_retained(self):
        dt, remainder = extract_dt("axşam saat 8 də hava necədir")
        self.assertEqual(dt, datetime(2017, 6, 27, 20, 0))
        self.assertEqual(remainder, "hava necədir")

    def test_indi_returns_anchor(self):
        dt, remainder = extract_dt("indi hava necədir")
        self.assertEqual(dt, ANCHOR.replace(microsecond=0))
        self.assertEqual(remainder, "hava necədir")

    def test_no_date_returns_none(self):
        self.assertIsNone(extract_dt("qwerty"))
        self.assertIsNone(extract_dt("hava necədir"))

    def test_empty_returns_none(self):
        self.assertIsNone(extract_datetime_az("", ANCHOR))

    def test_lang_code_variants_via_facade(self):
        from ovos_date_parser import extract_datetime
        for lang in ("az", "az-az", "az-AZ"):
            res = extract_datetime("sabah", anchorDate=ANCHOR, lang=lang)
            self.assertEqual(res[0], datetime(2017, 6, 28, 0, 0))

    def test_mixed_case(self):
        self.assertEqual(extract_dt("SABAH")[0], datetime(2017, 6, 28, 0, 0))
        self.assertEqual(extract_dt("Axşam Saat 8")[0],
                         datetime(2017, 6, 27, 20, 0))


class TestExtractDurationAz(unittest.TestCase):
    def test_basic_units(self):
        self.assertEqual(extract_duration_az("10 dəqiqə")[0], timedelta(minutes=10))
        self.assertEqual(extract_duration_az("30 saniyə")[0], timedelta(seconds=30))
        self.assertEqual(extract_duration_az("2 gün")[0], timedelta(days=2))
        self.assertEqual(extract_duration_az("2 saat 30 dəqiqə")[0],
                         timedelta(hours=2, minutes=30))

    def test_half_hour(self):
        self.assertEqual(extract_duration_az("yarım saat")[0], timedelta(minutes=30))

    def test_decimal_duration(self):
        self.assertEqual(extract_duration_az("1.5 saat")[0], timedelta(hours=1, minutes=30))

    def test_remainder_retained(self):
        dur, remainder = extract_duration_az("10 dəqiqə sonra film")
        self.assertEqual(dur, timedelta(minutes=10))
        self.assertIn("film", remainder)

    def test_empty_and_none(self):
        self.assertIsNone(extract_duration_az(""))
        self.assertIsNone(extract_duration_az(None))

    def test_no_duration(self):
        dur, remainder = extract_duration_az("salam dünya")
        self.assertIsNone(dur)


class TestNiceTimeAz(unittest.TestCase):
    def test_display(self):
        self.assertEqual(nice_time_az(datetime(2017, 1, 31, 13, 22), speech=False),
                         "1:22")
        self.assertEqual(nice_time_az(datetime(2017, 1, 31, 13, 22),
                                      speech=False, use_24hour=True), "13:22")

    def test_speech_forms(self):
        self.assertEqual(nice_time_az(datetime(2017, 1, 31, 13, 22)),
                         "ikiyə iyirmi iki dəqiqə işləyib")
        self.assertEqual(nice_time_az(datetime(2017, 1, 31, 1, 45)),
                         "ikiyə on beş dəqiqə qalıb")
        self.assertEqual(nice_time_az(datetime(2017, 1, 31, 13, 0)),
                         "bir tamamdır")

    def test_half_hour(self):
        self.assertEqual(nice_time_az(datetime(2017, 1, 31, 5, 30), use_ampm=True),
                         "gecə altının yarısı")

    def test_wraparound_midnight(self):
        # 23:59 and 00:00 must both produce non-empty speech without error
        self.assertTrue(nice_time_az(datetime(2017, 1, 31, 23, 59)))
        self.assertTrue(nice_time_az(datetime(2017, 1, 31, 0, 0)))


class TestNiceDurationAz(unittest.TestCase):
    def test_speech(self):
        self.assertEqual(nice_duration_az(1), "bir saniyə")
        self.assertEqual(nice_duration_az(61), "bir dəqiqə bir saniyə")

    def test_display(self):
        self.assertEqual(nice_duration_az(1, speech=False), "0:01")
        self.assertEqual(nice_duration_az(500000, speech=False), "5g 18:53:20")

    def test_timedelta_input(self):
        self.assertEqual(nice_duration_az(timedelta(seconds=61)),
                         "bir dəqiqə bir saniyə")


class TestRoundTripAz(unittest.TestCase):
    def test_duration_display_roundtrip(self):
        # nice_duration display then a manual re-read of the components
        for secs in (61, 5000, 50000):
            out = nice_duration_az(secs, speech=False)
            self.assertTrue(out)

    def test_clock_extract_matches_named_hours(self):
        # a spoken absolute hour should extract back to that hour
        for hh in (8, 9, 11):
            dt = extract_dt("səhər saat {}".format(hh))[0]
            self.assertEqual(dt.hour, hh)


if __name__ == "__main__":
    unittest.main()
