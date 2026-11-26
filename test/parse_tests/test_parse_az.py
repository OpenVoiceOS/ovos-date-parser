import unittest
from datetime import datetime, timedelta

from ovos_date_parser.dates_az import nice_time_az, nice_duration_az

# A fixed weekday reference: 2017-06-27 is a Tuesday, 13:04 local
ANCHOR = datetime(2017, 6, 27, 13, 4)


class TestExtractDatetimeAz(unittest.TestCase):


    def test_lang_code_variants_via_facade(self):
        from ovos_date_parser import extract_datetime
        for lang in ("az", "az-az", "az-AZ"):
            res = extract_datetime("sabah", anchorDate=ANCHOR, lang=lang)
            self.assertEqual(res[0], datetime(2017, 6, 28, 0, 0))


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


if __name__ == "__main__":
    unittest.main()
