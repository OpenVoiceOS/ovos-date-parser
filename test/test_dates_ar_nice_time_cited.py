"""nice_time for Arabic against the telling-time conventions cited in
``ovos_date_parser.dates_ar``: the hour as a feminine ordinal, والربع,
والنصف, إلا ربعاً and إلا ثلثاً, minute agreement, the period words, and
twelve o'clock as الثانية عشرة ظهراً or منتصف الليل."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_time


def at(hour, minute):
    return datetime(2017, 6, 27, hour, minute)


class TestNiceTimeArabicCited(unittest.TestCase):

    def check(self, cases, use_ampm):
        for (hour, minute), spoken in cases.items():
            with self.subTest(time=f"{hour:02d}:{minute:02d}"):
                self.assertEqual(nice_time(at(hour, minute), lang="ar",
                                           use_ampm=use_ampm), spoken)

    def test_with_period_words(self):
        self.check({
            (7, 0): "الساعة السابعة صباحاً",
            (7, 15): "الساعة السابعة والربع صباحاً",
            (7, 30): "الساعة السابعة والنصف صباحاً",
            (7, 40): "الساعة الثامنة إلا ثلثاً صباحاً",
            (7, 45): "الساعة الثامنة إلا ربعاً صباحاً",
            (10, 5): "الساعة العاشرة وخمس دقائق صباحاً",
            (12, 0): "الساعة الثانية عشرة ظهراً",
            (0, 0): "منتصف الليل",
            (19, 30): "الساعة السابعة والنصف مساءً",
            (19, 40): "الساعة الثامنة إلا ثلثاً مساءً",
            (1, 0): "الساعة الواحدة صباحاً",
            (23, 40): "الساعة الثانية عشرة إلا ثلثاً مساءً",
        }, use_ampm=True)

    def test_without_period_words(self):
        self.check({
            (7, 0): "الساعة السابعة",
            (7, 15): "الساعة السابعة والربع",
            (7, 30): "الساعة السابعة والنصف",
            (7, 40): "الساعة الثامنة إلا ثلثاً",
            (7, 45): "الساعة الثامنة إلا ربعاً",
            (10, 5): "الساعة العاشرة وخمس دقائق",
            (12, 0): "الظهر",
            (0, 0): "منتصف الليل",
            (19, 30): "الساعة السابعة والنصف",
            (1, 0): "الساعة الواحدة",
            (11, 40): "الساعة الثانية عشرة إلا ثلثاً",
            (12, 40): "الساعة الواحدة إلا ثلثاً",
        }, use_ampm=False)

    def test_minutes_agree_with_their_count(self):
        self.check({
            (10, 1): "الساعة العاشرة ودقيقة",
            (10, 2): "الساعة العاشرة ودقيقتان",
            (10, 10): "الساعة العاشرة وعشر دقائق",
            (10, 11): "الساعة العاشرة وإحدى عشرة دقيقة",
        }, use_ampm=False)

    def test_every_hour_is_a_feminine_ordinal(self):
        names = {1: "الواحدة", 2: "الثانية", 3: "الثالثة", 4: "الرابعة",
                 5: "الخامسة", 6: "السادسة", 7: "السابعة", 8: "الثامنة",
                 9: "التاسعة", 10: "العاشرة", 11: "الحادية عشرة"}
        for hour, name in names.items():
            with self.subTest(hour=hour):
                self.assertEqual(nice_time(at(hour + 12, 0), lang="ar",
                                           use_ampm=True),
                                 f"الساعة {name} مساءً")


if __name__ == "__main__":
    unittest.main()
