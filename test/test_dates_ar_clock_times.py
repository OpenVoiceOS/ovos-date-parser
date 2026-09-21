"""Clock times written in digits inside Arabic text, spoken as a speaker says
them: the hour as a feminine ordinal, fractions of the hour, and the period
words صباحًا, مساءً and ظهرًا. The sources are cited beside the tables in
``ovos_date_parser.dates_ar``."""
import unittest


def expand(text, lang="ar"):
    from ovos_date_parser import expand_times
    return expand_times(text, lang)


class TestArabicClockTimes(unittest.TestCase):

    def check(self, cases):
        for written, spoken in cases.items():
            with self.subTest(written=written):
                self.assertEqual(expand(written), spoken)

    def test_pm(self):
        self.check({
            "7 pm": "السابعة مساءً",
            "7pm": "السابعة مساءً",
            "7 PM": "السابعة مساءً",
            "7PM": "السابعة مساءً",
            "7:30 pm": "السابعة والنصف مساءً",
            "7:30pm": "السابعة والنصف مساءً",
        })

    def test_am(self):
        self.check({
            "7 am": "السابعة صباحًا",
            "7am": "السابعة صباحًا",
            "7 AM": "السابعة صباحًا",
            "7AM": "السابعة صباحًا",
            "9:15 am": "التاسعة والربع صباحًا",
        })

    def test_fractions_of_the_hour(self):
        self.check({
            "7:15": "السابعة والربع",
            "7:20": "السابعة والثلث",
            "7:30": "السابعة والنصف",
            "7:40": "الثامنة إلا ثلثًا",
            "7:45": "الثامنة إلا ربعًا",
            "12:45": "الواحدة إلا ربعًا",
        })

    def test_minutes_agree_with_their_count(self):
        self.check({
            "10:01": "العاشرة ودقيقة",
            "10:02": "العاشرة ودقيقتان",
            "10:05": "العاشرة وخمس دقائق",
            "10:10": "العاشرة وعشر دقائق",
            "10:11": "العاشرة وإحدى عشرة دقيقة",
            "10:25": "العاشرة وخمس وعشرون دقيقة",
        })

    def test_every_hour_of_the_12_hour_clock(self):
        names = {1: "الواحدة", 2: "الثانية", 3: "الثالثة", 4: "الرابعة",
                 5: "الخامسة", 6: "السادسة", 7: "السابعة", 8: "الثامنة",
                 9: "التاسعة", 10: "العاشرة", 11: "الحادية عشرة",
                 12: "الثانية عشرة"}
        for hour, name in names.items():
            with self.subTest(hour=hour):
                self.assertEqual(expand(f"{hour}:00"), name)
                self.assertEqual(expand(f"الساعة {hour}"), f"الساعة {name}")
                self.assertEqual(expand(f"{hour} am"),
                                 "منتصف الليل" if hour == 12
                                 else f"{name} صباحًا")
                self.assertEqual(expand(f"{hour} pm"),
                                 f"{name} ظهرًا" if hour == 12
                                 else f"{name} مساءً")

    def test_noon_and_midnight(self):
        self.check({
            "12 am": "منتصف الليل",
            "12 pm": "الثانية عشرة ظهرًا",
            "12:30 pm": "الثانية عشرة والنصف ظهرًا",
            "11:45 pm": "الثانية عشرة إلا ربعًا مساءً",
            "12:45 pm": "الواحدة إلا ربعًا مساءً",
            "0:00": "منتصف الليل",
        })

    def test_24_hour_clock_is_read_on_the_12_hour_clock(self):
        self.check({
            "19:30": "السابعة والنصف مساءً",
            "19:00": "السابعة مساءً",
            "13:05": "الواحدة وخمس دقائق مساءً",
            "00:30": "الثانية عشرة والنصف صباحًا",
            "07:15": "السابعة والربع",
        })

    def test_written_saa_is_kept(self):
        self.check({
            "الساعة 3": "الساعة الثالثة",
            "الساعة ٣": "الساعة الثالثة",
            "الساعة 19:30": "الساعة السابعة والنصف مساءً",
            "في الساعة 11 pm": "في الساعة الحادية عشرة مساءً",
        })

    def test_in_a_sentence(self):
        self.check({
            "الموعد 7:30 pm": "الموعد السابعة والنصف مساءً",
            "يبدأ الاجتماع 10:05 وينتهي 11:45":
                "يبدأ الاجتماع العاشرة وخمس دقائق وينتهي الثانية عشرة إلا ربعًا",
            "من ٧:٣٠ إلى 9 pm": "من السابعة والنصف إلى التاسعة مساءً",
        })

    def test_numbers_that_are_not_times_are_untouched(self):
        for text in ("7 km", "الطول 300 pm", "13 pm", "0 pm", "5 سيارات",
                     "الساعة 25", "24:00", "7:75", "7.5 pm", "12:30:45",
                     "العدد 7", "7 pmx"):
            with self.subTest(text=text):
                self.assertEqual(expand(text), text)

    def test_regional_tag_and_unsupported_language(self):
        self.assertEqual(expand("7 pm", "ar-SA"), "السابعة مساءً")
        with self.assertRaises(NotImplementedError):
            expand("7 pm", "en-us")


if __name__ == "__main__":
    unittest.main()
