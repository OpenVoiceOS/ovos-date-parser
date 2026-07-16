import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (nice_time, nice_duration, nice_date,
                              nice_date_time, nice_year, nice_weekday,
                              nice_month, nice_day, nice_relative_time)

ANCHOR = datetime(2017, 6, 27, 13, 4)


class TestNiceTimeArabic(unittest.TestCase):
    """Arabic tells time with feminine hour names and half-past semantics."""

    def test_full_hours(self):
        expected = {1: "الساعة الواحدة", 2: "الساعة الثانية",
                    3: "الساعة الثالثة", 4: "الساعة الرابعة",
                    5: "الساعة الخامسة", 6: "الساعة السادسة",
                    7: "الساعة السابعة", 8: "الساعة الثامنة",
                    9: "الساعة التاسعة", 10: "الساعة العاشرة",
                    11: "الساعة الحادية عشرة"}
        for hour, spoken in expected.items():
            with self.subTest(hour=hour):
                dt = ANCHOR.replace(hour=hour, minute=0)
                self.assertEqual(nice_time(dt, lang="ar"), spoken)

    def test_half_past_quarter_past_quarter_to(self):
        # Arabic uses HALF-PAST semantics: 9:30 = "التاسعة والنصف"
        self.assertEqual(nice_time(ANCHOR.replace(hour=9, minute=30),
                                   lang="ar"),
                         "الساعة التاسعة والنصف")
        self.assertEqual(nice_time(ANCHOR.replace(hour=9, minute=15),
                                   lang="ar"),
                         "الساعة التاسعة والربع")
        self.assertEqual(nice_time(ANCHOR.replace(hour=9, minute=20),
                                   lang="ar"),
                         "الساعة التاسعة والثلث")
        # quarter to: 8:45 is told against the NEXT hour
        self.assertEqual(nice_time(ANCHOR.replace(hour=8, minute=45),
                                   lang="ar"),
                         "الساعة التاسعة إلا ربعاً")

    def test_minutes_gender_agreement(self):
        # دقيقة is feminine: dual and polarity-opposed numerals
        self.assertEqual(nice_time(ANCHOR.replace(hour=1, minute=4),
                                   lang="ar"),
                         "الساعة الواحدة وأربع دقائق")
        self.assertEqual(nice_time(ANCHOR.replace(hour=15, minute=25),
                                   lang="ar"),
                         "الساعة الثالثة وخمس وعشرون دقيقة")
        self.assertEqual(nice_time(ANCHOR.replace(hour=6, minute=2),
                                   lang="ar"),
                         "الساعة السادسة ودقيقتان")

    def test_am_pm(self):
        self.assertEqual(nice_time(ANCHOR.replace(hour=7, minute=0),
                                   lang="ar", use_ampm=True),
                         "الساعة السابعة صباحاً")
        self.assertEqual(nice_time(ANCHOR.replace(hour=19, minute=0),
                                   lang="ar", use_ampm=True),
                         "الساعة السابعة مساءً")

    def test_special_hours(self):
        self.assertEqual(nice_time(ANCHOR.replace(hour=0, minute=0),
                                   lang="ar"), "منتصف الليل")
        self.assertEqual(nice_time(ANCHOR.replace(hour=12, minute=0),
                                   lang="ar"), "الظهر")

    def test_display(self):
        dt = ANCHOR.replace(hour=15, minute=30)
        self.assertEqual(nice_time(dt, lang="ar", speech=False), "3:30")
        self.assertEqual(nice_time(dt, lang="ar", speech=False,
                                   use_24hour=True), "15:30")

    def test_24hour_speech(self):
        dt = ANCHOR.replace(hour=13, minute=4)
        self.assertEqual(nice_time(dt, lang="ar", use_24hour=True),
                         "ثلاثة عشر وأربع دقائق")


class TestNiceDurationArabic(unittest.TestCase):
    """Arabic counted nouns: singular for 1, dual for 2, plural for 3-10."""

    def test_durations(self):
        expected = {
            1: "ثانية", 2: "ثانيتان", 3: "ثلاث ثوان", 45: "خمس وأربعون ثانية",
            60: "دقيقة", 120: "دقيقتان", 300: "خمس دقائق",
            163: "دقيقتان وثلاث وأربعون ثانية",
            3600: "ساعة", 7200: "ساعتان", 3 * 3600: "ثلاث ساعات",
            86400: "يوم", 2 * 86400: "يومان", 3 * 86400: "ثلاثة أيام",
            90061: "يوم وساعة ودقيقة وثانية",
        }
        for seconds, spoken in expected.items():
            with self.subTest(seconds=seconds):
                self.assertEqual(nice_duration(seconds, lang="ar"), spoken)

    def test_display(self):
        self.assertEqual(nice_duration(163, lang="ar", speech=False), "2:43")


class TestNiceDateArabic(unittest.TestCase):

    def test_nice_date(self):
        self.assertEqual(
            nice_date(ANCHOR, lang="ar"),
            "الثلاثاء، السابع والعشرون من يونيو ألفان وسبعة عشر")

    def test_nice_date_relative(self):
        now = ANCHOR
        self.assertEqual(nice_date(ANCHOR, lang="ar", now=now), "اليوم")
        self.assertEqual(nice_date(ANCHOR + timedelta(days=1), lang="ar",
                                   now=now), "غداً")
        self.assertEqual(nice_date(ANCHOR - timedelta(days=1), lang="ar",
                                   now=now), "أمس")

    def test_nice_year(self):
        expected = {1985: "ألف وتسعمئة وخمسة وثمانون",
                    1900: "ألف وتسعمئة",
                    2005: "ألفان وخمسة",
                    2017: "ألفان وسبعة عشر",
                    2000: "ألفان"}
        for year, spoken in expected.items():
            with self.subTest(year=year):
                self.assertEqual(
                    nice_year(datetime(year, 1, 1), lang="ar"), spoken)

    def test_nice_weekday_month_day(self):
        self.assertEqual(nice_weekday(ANCHOR, lang="ar"), "الثلاثاء")
        self.assertEqual(nice_month(ANCHOR, lang="ar"), "يونيو")
        self.assertEqual(nice_day(ANCHOR, lang="ar"), "27 يونيو")

    def test_nice_date_time(self):
        self.assertEqual(
            nice_date_time(ANCHOR, lang="ar"),
            "الثلاثاء، السابع والعشرون من يونيو ألفان وسبعة عشر "
            "الساعة الواحدة وأربع دقائق")

    def test_nice_relative_time(self):
        self.assertEqual(
            nice_relative_time(ANCHOR + timedelta(minutes=5),
                               relative_to=ANCHOR, lang="ar"),
            "خمسة دقائق")


if __name__ == "__main__":
    unittest.main()
