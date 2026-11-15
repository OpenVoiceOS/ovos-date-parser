import unittest
from datetime import datetime

from ovos_date_parser import (nice_date, nice_date_time, nice_day, nice_month,
                              nice_time, nice_weekday, nice_year)

# Saturday
SATURDAY = datetime(2026, 10, 17, 12, 0)


class TestNiceDateTr(unittest.TestCase):
    def test_full_date(self):
        self.assertEqual(nice_date(SATURDAY, "tr-TR"),
                         "on yedi ekim iki bin yirmi altı cumartesi")
        self.assertEqual(nice_date(SATURDAY, "tr"),
                         "on yedi ekim iki bin yirmi altı cumartesi")

    def test_without_weekday(self):
        self.assertEqual(nice_date(SATURDAY, "tr-TR", include_weekday=False),
                         "on yedi ekim iki bin yirmi altı")

    def test_other_dates(self):
        cases = {
            datetime(2024, 1, 5): "beş ocak iki bin yirmi dört cuma",
            datetime(1999, 12, 31): "otuz bir aralık bin dokuz yüz doksan dokuz cuma",
            datetime(2000, 2, 29): "yirmi dokuz şubat iki bin salı",
            datetime(2026, 7, 15): "on beş temmuz iki bin yirmi altı çarşamba",
            datetime(2026, 8, 20): "yirmi ağustos iki bin yirmi altı perşembe",
            datetime(2026, 11, 1): "bir kasım iki bin yirmi altı pazar",
        }
        for dt, expected in cases.items():
            self.assertEqual(nice_date(dt, "tr-TR"), expected)

    def test_relative_to_now(self):
        self.assertEqual(nice_date(SATURDAY, "tr-TR", now=SATURDAY), "bugün")
        self.assertEqual(
            nice_date(SATURDAY, "tr-TR", now=datetime(2026, 10, 16, 8, 0)),
            "yarın")
        self.assertEqual(
            nice_date(SATURDAY, "tr-TR", now=datetime(2026, 10, 18, 8, 0)),
            "dün")

    def test_same_year_drops_year(self):
        self.assertEqual(
            nice_date(SATURDAY, "tr-TR", now=datetime(2026, 3, 1)),
            "on yedi ekim cumartesi")
        self.assertEqual(
            nice_date(SATURDAY, "tr-TR", now=datetime(2026, 10, 5)),
            "on yedi ekim cumartesi")
        self.assertEqual(
            nice_date(SATURDAY, "tr-TR", now=datetime(2026, 3, 1),
                      include_weekday=False),
            "on yedi ekim")

    def test_other_year_keeps_year(self):
        self.assertEqual(
            nice_date(SATURDAY, "tr-TR", now=datetime(2025, 10, 17)),
            "on yedi ekim iki bin yirmi altı cumartesi")

    def test_date_time(self):
        self.assertEqual(
            nice_date_time(datetime(2026, 10, 17, 14, 0), "tr-TR",
                           use_24hour=True),
            "on yedi ekim iki bin yirmi altı cumartesi saat on dört")
        self.assertEqual(
            nice_date_time(datetime(2026, 10, 17, 14, 5), "tr-TR",
                           now=datetime(2026, 10, 17, 9, 0),
                           use_24hour=True),
            "bugün saat on dört sıfır beş")


class TestNiceWeekdayMonthDayTr(unittest.TestCase):
    def test_weekday(self):
        names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma",
                 "Cumartesi", "Pazar"]
        for offset, name in enumerate(names):
            self.assertEqual(
                nice_weekday(datetime(2026, 10, 19 + offset), "tr-TR"), name)

    def test_month(self):
        names = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                 "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        for month, name in enumerate(names, 1):
            self.assertEqual(nice_month(datetime(2026, month, 1), "tr-TR"),
                             name)

    def test_day(self):
        self.assertEqual(nice_day(SATURDAY, "tr-TR"), "17 Ekim")
        self.assertEqual(nice_day(SATURDAY, "tr-TR", date_format="MDY"),
                         "Ekim 17")
        self.assertEqual(nice_day(SATURDAY, "tr-TR", include_month=False),
                         "17")

    def test_year(self):
        self.assertEqual(nice_year(SATURDAY, "tr-TR"),
                         "iki bin yirmi altı")
        self.assertEqual(nice_year(datetime(1984, 1, 1), "tr-TR"),
                         "bin dokuz yüz seksen dört")
        self.assertEqual(nice_year(datetime(300, 1, 1), "tr-TR", bc=True),
                         "milattan önce üç yüz")


class TestLanguagesWithoutDateResources(unittest.TestCase):
    """A language without a date_time.json is reported as unsupported, the
    way nice_time reports it, instead of failing with a KeyError."""

    def test_unsupported_raises_clear_error(self):
        for lang in ("id", "ms", "xx"):
            with self.subTest(lang=lang):
                with self.assertRaises(NotImplementedError):
                    nice_date(SATURDAY, lang)
                with self.assertRaises(NotImplementedError):
                    nice_date_time(SATURDAY, lang)
                with self.assertRaises(NotImplementedError):
                    nice_year(SATURDAY, lang)

    def test_weekday_and_month_keep_english_fallback(self):
        self.assertEqual(nice_weekday(SATURDAY, "xx"), "Saturday")
        self.assertEqual(nice_month(SATURDAY, "xx"), "October")

    def test_neighbouring_languages_unchanged(self):
        self.assertEqual(nice_date(SATURDAY, "az", now=SATURDAY), "bu gün")
        self.assertEqual(nice_date(SATURDAY, "en", now=SATURDAY), "today")
        self.assertEqual(nice_date(SATURDAY, "pt", now=SATURDAY), "hoje")


if __name__ == "__main__":
    unittest.main()
