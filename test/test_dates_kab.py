import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (extract_datetime, extract_duration, nice_date,
                              nice_month, nice_time, nice_weekday)

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a Tuesday


class TestNiceTimeKab(unittest.TestCase):
    def test_24hour(self):
        self.assertEqual(nice_time(ANCHOR, "kab", use_24hour=True),
                         "tleṭṭac d kuẓ")
        self.assertEqual(
            nice_time(datetime(2017, 6, 27, 8, 0), "kab", use_24hour=True),
            "tam")

    def test_12hour(self):
        self.assertEqual(nice_time(ANCHOR, "kab"), "yiwen d kuẓ")
        self.assertEqual(nice_time(ANCHOR, "kab", use_ampm=True),
                         "yiwen d kuẓ tameddit")
        self.assertEqual(
            nice_time(datetime(2017, 6, 27, 9, 30), "kab", use_ampm=True),
            "tẓa d tlatin ssbeḥ")

    def test_display(self):
        self.assertEqual(nice_time(ANCHOR, "kab", speech=False,
                                   use_24hour=True), "13:04")


class TestNiceDateKab(unittest.TestCase):
    def test_weekday_month(self):
        self.assertEqual(nice_weekday(ANCHOR, "kab").lower(), "ttlata")
        self.assertEqual(nice_month(ANCHOR, "kab").lower(), "yunyu")

    def test_relative_words(self):
        self.assertEqual(nice_date(ANCHOR + timedelta(days=1), "kab",
                                   now=ANCHOR), "azekka")
        self.assertEqual(nice_date(ANCHOR, "kab", now=ANCHOR), "ass-a")
        self.assertEqual(nice_date(ANCHOR - timedelta(days=1), "kab",
                                   now=ANCHOR), "iḍelli")


class TestExtractDurationKab(unittest.TestCase):
    def test_digit_quantities(self):
        self.assertEqual(extract_duration("10 n tesdidin", "kab")[0],
                         timedelta(minutes=10))
        self.assertEqual(extract_duration("5 n ddqiqa", "kab")[0],
                         timedelta(minutes=5))

    def test_spoken_quantities(self):
        self.assertEqual(extract_duration("sin wussan", "kab")[0],
                         timedelta(days=2))
        self.assertEqual(extract_duration("snat n tsaɛtin", "kab")[0],
                         timedelta(hours=2))
        self.assertEqual(extract_duration("yiwen amalas", "kab")[0],
                         timedelta(weeks=1))
        self.assertEqual(extract_duration("tlatin tasint", "kab")[0],
                         timedelta(seconds=30))

    def test_remainder(self):
        duration, remainder = extract_duration(
            "sekker tanafa n 10 n tesdidin", "kab")
        self.assertEqual(duration, timedelta(minutes=10))
        self.assertNotIn("tesdidin", remainder)

    def test_no_duration(self):
        self.assertEqual(extract_duration("azul fell-awen", "kab"),
                         (None, "azul fell-awen"))


class TestExtractDatetimeKab(unittest.TestCase):
    def test_relative_days(self):
        result = extract_datetime("azekka", "kab", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(),
                         (ANCHOR + timedelta(days=1)).date())
        result = extract_datetime("iḍelli", "kab", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(),
                         (ANCHOR - timedelta(days=1)).date())
        result = extract_datetime("ass-a", "kab", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(), ANCHOR.date())

    def test_weekday(self):
        # anchor is a Tuesday; lexmis = Thursday
        result = extract_datetime("ass n lexmis", "kab", anchorDate=ANCHOR)
        self.assertEqual(result[0].weekday(), 3)
        self.assertGreater(result[0].date(), ANCHOR.date())

    def test_month_day(self):
        result = extract_datetime("3 yennayer", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].month, result[0].day), (1, 3))
        self.assertEqual(result[0].year, 2018)

    def test_time(self):
        result = extract_datetime("azekka 15:30", "kab", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(),
                         (ANCHOR + timedelta(days=1)).date())
        self.assertEqual((result[0].hour, result[0].minute), (15, 30))

    def test_no_date(self):
        self.assertIsNone(
            extract_datetime("azul fell-awen amek tellam", "kab",
                             anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
