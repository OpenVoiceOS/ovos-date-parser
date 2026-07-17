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


class TestExtractDatetimeArabicHardening(unittest.TestCase):
    # a Friday, so weekday math is unambiguous
    A = datetime(2026, 7, 17, 10, 0)

    def _dt(self, text):
        return extract_datetime(text, lang="ar", anchorDate=self.A)

    def test_minutes_to_the_hour(self):
        # "إلا خمس" = five minutes to the hour -> :55 of the previous hour
        cases = {
            "الساعة الخامسة إلا خمس": (4, 55),
            "الساعة التاسعة إلا عشر دقائق": (8, 50),
            "الساعة الواحدة إلا عشرين": (12, 40),
        }
        for phrase, (h, m) in cases.items():
            with self.subTest(phrase=phrase):
                r = self._dt(phrase)
                self.assertIsNotNone(r, phrase)
                self.assertEqual((r[0].hour, r[0].minute), (h, m), phrase)

    def test_quarter_and_third_to_the_hour(self):
        self.assertEqual(self._dt("الساعة التاسعة إلا ربعاً")[0].hour, 8)
        self.assertEqual(self._dt("الساعة التاسعة إلا ربعاً")[0].minute, 45)
        self.assertEqual(self._dt("الساعة التاسعة إلا ثلثاً")[0].minute, 40)

    def test_fractional_relative_offset(self):
        # "بعد ساعة ونصف" = in an hour and a half -> +90 min
        self.assertEqual(self._dt("بعد ساعة ونصف")[0],
                         self.A + timedelta(minutes=90))
        self.assertEqual(self._dt("بعد ساعتين ونصف")[0],
                         self.A + timedelta(minutes=150))
        self.assertEqual(self._dt("بعد ساعة وربع")[0],
                         self.A + timedelta(minutes=75))

    def test_invalid_calendar_date_does_not_crash(self):
        # an impossible date must not raise, just yield no such date
        self.assertIsNone(self._dt("موعد يوم ٣١ فبراير"))
        self.assertIsNone(self._dt("يوم 29 فبراير 2027"))  # not a leap year
        # a real leap day resolves
        r = self._dt("يوم 29 فبراير 2028")
        self.assertEqual((r[0].year, r[0].month, r[0].day), (2028, 2, 29))

    def test_appointment_with_day_month_and_clock(self):
        # known cross-lang trap: the clock hour must not be read as a year
        r = self._dt("موعد يوم ١٥ يونيو الساعة الثالثة")
        self.assertEqual((r[0].month, r[0].day, r[0].hour, r[0].minute),
                         (6, 15, 3, 0))

    def test_part_of_day_drives_pm(self):
        self.assertEqual(self._dt("الساعة الثالثة والنصف مساءً")[0].hour, 15)
        self.assertEqual(self._dt("الساعة الرابعة عصراً")[0].hour, 16)
        self.assertEqual(self._dt("الساعة السابعة صباحاً")[0].hour, 7)

    def test_twelve_with_part_of_day(self):
        # twelve in the morning is midnight; at noon it is 12:00
        self.assertEqual(self._dt("الساعة الثانية عشرة صباحاً")[0].hour, 0)
        self.assertEqual(self._dt("الساعة الثانية عشرة ظهراً")[0].hour, 12)

    def test_eastern_and_western_digit_clocks(self):
        self.assertEqual((self._dt("الساعة ١٧:٣٠")[0].hour,
                          self._dt("الساعة ١٧:٣٠")[0].minute), (17, 30))
        self.assertEqual((self._dt("5:30 مساءً")[0].hour,
                          self._dt("5:30 مساءً")[0].minute), (17, 30))

    def test_dual_relative_days(self):
        self.assertEqual(self._dt("بعد يومين")[0].day, 19)
        self.assertEqual(self._dt("بعد أسبوعين")[0],
                         self.A.replace(hour=0, minute=0) + timedelta(weeks=2))
        self.assertEqual(self._dt("قبل ساعتين")[0], self.A - timedelta(hours=2))

    def test_relative_day_words(self):
        base = self.A.replace(hour=0, minute=0)
        self.assertEqual(self._dt("بعد غد")[0], base + timedelta(days=2))
        self.assertEqual(self._dt("أول أمس")[0], base - timedelta(days=2))
        self.assertEqual(self._dt("أمس الأول")[0], base - timedelta(days=2))

    def test_diacritized_input(self):
        # voweled spelling must parse identically to the bare form
        self.assertEqual(self._dt("الساعة الثَّالِثة صباحاً")[0].hour, 3)


class TestExtractDurationArabicHardening(unittest.TestCase):
    def _d(self, text):
        return extract_duration(text, lang="ar")[0]

    def test_fractional_units(self):
        self.assertEqual(self._d("ساعة ونصف"), timedelta(hours=1, minutes=30))
        self.assertEqual(self._d("ساعة وربع"), timedelta(hours=1, minutes=15))
        self.assertEqual(self._d("نصف ساعة"), timedelta(minutes=30))

    def test_mixed_digits(self):
        self.assertEqual(self._d("٣٠ دقيقة"), timedelta(minutes=30))
        self.assertEqual(self._d("15 دقيقة"), timedelta(minutes=15))

    def test_no_duration(self):
        self.assertIsNone(extract_duration("مرحبا", lang="ar")[0])


if __name__ == "__main__":
    unittest.main()
