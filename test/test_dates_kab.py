import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (extract_datetime, extract_duration, nice_date,
                              nice_month, nice_time, nice_weekday)

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a Tuesday


class TestNiceTimeKab(unittest.TestCase):
    def test_24hour(self):
        # 13:04 -> 1:04. Native spoken Kabyle uses 12-hour cycle + explicit minutes
        self.assertEqual(nice_time(ANCHOR, "kab", use_24hour=True),
                         "d lweḥda u ṛebɛa n ddqayeq")
        # 8:00 -> d ttmanya
        self.assertEqual(
            nice_time(datetime(2017, 6, 27, 8, 0), "kab", use_24hour=True),
            "d ttmanya")

    def test_12hour(self):
        # 13:04 -> 1:04 PM
        self.assertEqual(nice_time(ANCHOR, "kab"), "d lweḥda u ṛebɛa n ddqayeq")
        
        # With AM/PM marker (tmeddit = afternoon/evening)
        self.assertEqual(nice_time(ANCHOR, "kab", use_ampm=True),
                         "d lweḥda u ṛebɛa n ddqayeq n uzal")
        
        # 9:30 AM -> d tesɛa u neṣṣ n ssbeḥ
        self.assertEqual(
            nice_time(datetime(2017, 6, 27, 9, 30), "kab", use_ampm=True),
            "d tesɛa u neṣṣ n ssbeḥ")

    def test_display(self):
        # Digital display remains unchanged
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

class TestExtractDatetimeSpokenTimeKab(unittest.TestCase):
    def test_bare_hour(self):
        result = extract_datetime("d lweḥda", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (1, 0))

    def test_exact_hour(self):
        result = extract_datetime("d lɛecṛa swaswa", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (10, 0))

    def test_quarter_past(self):
        result = extract_datetime("d lɛecṛa u ṛbeɛ", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (10, 15))

    def test_half_past_spellings(self):
        # amazigh, old borrowing, assimil, contemporary - all four accepted
        for word in ("neṣṣ", "azgen", "nofc", "nefs"):
            result = extract_datetime(f"d lɛecṛa u {word}", "kab",
                                      anchorDate=ANCHOR)
            self.assertEqual((result[0].hour, result[0].minute), (10, 30),
                             msg=f"failed for {word!r}")

    def test_minus_minutes(self):
        result = extract_datetime("d lɛecṛa ɣiṛ xemsa", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (9, 55))

    def test_quarter_to(self):
        result = extract_datetime("d lɛecṛa ɣiṛ ṛbeɛ", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (9, 45))

    def test_vague_approximations(self):
        # "u wac"/"u ci" and bare "ɣiṛ" are indeterminate in the source
        # grammar; coded as a fixed +/-10 minute offset rather than a
        # specific count
        result = extract_datetime("d lɛecṛa u wac", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (10, 10))
        result = extract_datetime("d lɛecṛa ɣiṛ", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (9, 50))

    def test_day_period_disambiguation(self):
        # "d juǧ" alone stays 12h (2:00); a period word resolves to 24h
        result = extract_datetime("d juǧ n uzal", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (14, 0))
        # "tmeddit" (no epenthetic vowel) must resolve the same as
        # "tameddit"
        result = extract_datetime("d lxemsa n tmeddit", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (17, 0))

    def test_regional_two_oclock(self):
        # Soummam valley "ssaɛtin" as an alternative to "juǧ" for "two"
        result = extract_datetime("d ssaɛtin ɣiṛ xemsa", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (1, 55))

    def test_midnight_phrases(self):
        for phrase in ("nṣaf n yiḍ", "ttnaṣfa n yiḍ", "d ttnac n yiḍ"):
            result = extract_datetime(phrase, "kab", anchorDate=ANCHOR)
            self.assertEqual((result[0].hour, result[0].minute), (0, 0),
                             msg=f"failed for {phrase!r}")

    def test_sun_letter_article(self):
        # the fused article assimilates to "tt" before "t" (ttnac =
        # article + tnac "12"), as opposed to the plain "l-" in
        # test_day_period_disambiguation's "lxemsa"/"lɛecṛa"
        result = extract_datetime("d ttnac n uzal", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (12, 0))


if __name__ == "__main__":
    unittest.main()
