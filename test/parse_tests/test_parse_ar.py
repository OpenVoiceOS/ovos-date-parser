import unittest
from datetime import datetime, timedelta

from ovos_date_parser import extract_datetime, extract_duration, nice_time

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a tuesday


class TestExtractDurationArabic(unittest.TestCase):

    def test_units_and_plurals(self):
        expected = {
            "عشر دقائق": timedelta(minutes=10),
            "خمس دقائق": timedelta(minutes=5),
            "ثلاث ساعات": timedelta(hours=3),
            "ثانية واحدة": timedelta(seconds=1),
            "ثلاثون ثانية": timedelta(seconds=30),
            "ثلاثة أيام": timedelta(days=3),
            "أسبوع واحد": timedelta(weeks=1),
            "ثلاثة أسابيع": timedelta(weeks=3),
            "سنة واحدة": timedelta(days=365),
        }
        for phrase, duration in expected.items():
            with self.subTest(phrase=phrase):
                self.assertEqual(extract_duration(phrase, lang="ar")[0],
                                 duration)

    def test_dual_forms(self):
        # the dual encodes both the count and the unit: يومان = 2 days
        expected = {
            "يومان": timedelta(days=2), "يومين": timedelta(days=2),
            "ساعتان": timedelta(hours=2), "ساعتين": timedelta(hours=2),
            "دقيقتان": timedelta(minutes=2),
            "أسبوعان": timedelta(weeks=2),
            "شهرين": timedelta(days=60),
            "سنتين": timedelta(days=730),
        }
        for phrase, duration in expected.items():
            with self.subTest(phrase=phrase):
                self.assertEqual(extract_duration(phrase, lang="ar")[0],
                                 duration)

    def test_fractions_and_compounds(self):
        self.assertEqual(extract_duration("نصف ساعة", lang="ar")[0],
                         timedelta(minutes=30))
        self.assertEqual(extract_duration("ساعة ونصف", lang="ar")[0],
                         timedelta(minutes=90))
        self.assertEqual(
            extract_duration("ثلاثة أيام وخمس ساعات", lang="ar")[0],
            timedelta(days=3, hours=5))

    def test_eastern_digits(self):
        self.assertEqual(extract_duration("١٠ دقائق", lang="ar")[0],
                         timedelta(minutes=10))
        self.assertEqual(extract_duration("٣ ساعات", lang="ar")[0],
                         timedelta(hours=3))

    def test_remainder(self):
        duration, remainder = extract_duration(
            "اضبط مؤقتا لمدة خمس دقائق", lang="ar")
        self.assertEqual(duration, timedelta(minutes=5))
        self.assertNotIn("دقائق", remainder)
        self.assertNotIn("خمس", remainder)

    def test_no_duration(self):
        duration, remainder = extract_duration("مرحبا كيف حالك", lang="ar")
        self.assertIsNone(duration)


class TestExtractDatetimeArabic(unittest.TestCase):

    def test_relative_days(self):
        expected = {
            "اليوم": ANCHOR.date(),
            "غدا": (ANCHOR + timedelta(days=1)).date(),
            "غداً": (ANCHOR + timedelta(days=1)).date(),
            "أمس": (ANCHOR - timedelta(days=1)).date(),
            "بعد غد": (ANCHOR + timedelta(days=2)).date(),
        }
        for phrase, date in expected.items():
            with self.subTest(phrase=phrase):
                result = extract_datetime(phrase, lang="ar",
                                          anchorDate=ANCHOR)
                self.assertIsNotNone(result)
                self.assertEqual(result[0].date(), date)

    def test_weekdays(self):
        # anchor is a tuesday
        expected = {
            "الأربعاء": 1, "الخميس": 2, "الجمعة": 3, "السبت": 4,
            "الأحد": 5, "الاثنين": 6, "الثلاثاء": 0,
            "يوم الجمعة": 3,
        }
        for phrase, offset in expected.items():
            with self.subTest(phrase=phrase):
                result = extract_datetime(phrase, lang="ar",
                                          anchorDate=ANCHOR)
                self.assertIsNotNone(result)
                self.assertEqual(result[0].date(),
                                 (ANCHOR + timedelta(days=offset)).date())

    def test_relative_offsets(self):
        expected = {
            "بعد ثلاثة أيام": ANCHOR.date() + timedelta(days=3),
            "بعد يومين": ANCHOR.date() + timedelta(days=2),
            "قبل يومين": ANCHOR.date() - timedelta(days=2),
            "الأسبوع القادم": ANCHOR.date() + timedelta(weeks=1),
            "الأسبوع الماضي": ANCHOR.date() - timedelta(weeks=1),
        }
        for phrase, date in expected.items():
            with self.subTest(phrase=phrase):
                result = extract_datetime(phrase, lang="ar",
                                          anchorDate=ANCHOR)
                self.assertIsNotNone(result)
                self.assertEqual(result[0].date(), date)

    def test_relative_hours(self):
        result = extract_datetime("بعد ساعتين", lang="ar", anchorDate=ANCHOR)
        self.assertEqual(result[0], ANCHOR + timedelta(hours=2))

    def test_months(self):
        result = extract_datetime("الخامس من يناير", lang="ar",
                                  anchorDate=ANCHOR)
        self.assertEqual(result[0].date(), datetime(2017, 1, 5).date())
        result = extract_datetime("5 يناير", lang="ar", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(), datetime(2017, 1, 5).date())
        result = extract_datetime("يناير 2030", lang="ar", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(), datetime(2030, 1, 1).date())

    def test_clock_times(self):
        expected = {
            # half-past semantics: التاسعة والنصف = 9:30
            "الساعة التاسعة والنصف": (9, 30),
            "الساعة التاسعة والربع": (9, 15),
            # quarter to: التاسعة إلا ربعاً = 8:45
            "الساعة التاسعة إلا ربعاً": (8, 45),
            "الساعة الواحدة": (1, 0),
            "الساعة الثانية عشرة": (12, 0),
            "الساعة التاسعة والنصف مساءً": (21, 30),
            "الساعة السابعة صباحاً": (7, 0),
            "غدا الساعة الخامسة مساء": (17, 0),
            "5:30": (5, 30), "15:30": (15, 30),
        }
        for phrase, (hour, minute) in expected.items():
            with self.subTest(phrase=phrase):
                result = extract_datetime(phrase, lang="ar",
                                          anchorDate=ANCHOR)
                self.assertIsNotNone(result)
                self.assertEqual((result[0].hour, result[0].minute),
                                 (hour, minute))

    def test_remainder(self):
        result = extract_datetime("ما هو الطقس غدا", lang="ar",
                                  anchorDate=ANCHOR)
        self.assertEqual(result[0].date(),
                         (ANCHOR + timedelta(days=1)).date())
        self.assertNotIn("غدا", result[1])

    def test_no_date(self):
        self.assertIsNone(extract_datetime("مرحبا كيف حالك", lang="ar",
                                           anchorDate=ANCHOR))
        self.assertIsNone(extract_datetime("", lang="ar", anchorDate=ANCHOR))

    def test_nice_time_round_trip(self):
        for hour, minute in [(9, 30), (9, 15), (8, 45), (15, 25), (7, 0),
                             (23, 45), (12, 0), (1, 5)]:
            with self.subTest(hour=hour, minute=minute):
                dt = ANCHOR.replace(hour=hour, minute=minute)
                spoken = nice_time(dt, lang="ar", use_ampm=True)
                result = extract_datetime(spoken, lang="ar",
                                          anchorDate=ANCHOR)
                self.assertIsNotNone(result, spoken)
                self.assertEqual((result[0].hour, result[0].minute),
                                 (hour, minute), spoken)


if __name__ == "__main__":
    unittest.main()
