"""Bosnian (bs) date writing uses the CLDR 49 bs names, not the Croatian ones.

The expected words are the ``bs`` wide month and weekday names of
cldr-json 49.0.0, ``cldr-dates-full/main/bs/ca-gregorian.json``. The
``hr`` rows pin the Croatian output, which the ``bs`` resource must not
change."""
import unittest
from datetime import datetime

from ovos_date_parser import (
    nice_date, nice_date_time, nice_day, nice_month, nice_weekday, nice_year,
    nice_time)
from ovos_date_parser.common import writer_lang

CLDR_BS_MONTHS = [
    "januar", "februar", "mart", "april", "maj", "juni", "juli", "august",
    "septembar", "oktobar", "novembar", "decembar"]
CLDR_BS_WEEKDAYS = [
    "ponedjeljak", "utorak", "srijeda", "četvrtak", "petak", "subota",
    "nedjelja"]
CROATIAN_MONTHS = [
    "siječanj", "veljača", "ožujak", "travanj", "svibanj", "lipanj",
    "srpanj", "kolovoz", "rujan", "listopad", "studeni", "prosinac"]

# Thursday 2026-03-05
THURSDAY = datetime(2026, 3, 5)


class TestBosnianLookup(unittest.TestCase):

    def test_bs_tags_have_their_own_writer(self):
        for tag in ("bs", "bs-BA", "bs_ba", "BS"):
            with self.subTest(tag=tag):
                self.assertEqual(writer_lang(tag), "bs")

    def test_croatian_keeps_its_writer(self):
        for tag in ("hr", "hr-HR"):
            with self.subTest(tag=tag):
                self.assertEqual(writer_lang(tag), "hr")


class TestBosnianNames(unittest.TestCase):

    def test_nice_date_march(self):
        self.assertEqual(nice_date(THURSDAY, "bs"),
                         "četvrtak, peti mart 2026")

    def test_nice_date_regional_tag(self):
        self.assertEqual(nice_date(THURSDAY, "bs-BA"),
                         "četvrtak, peti mart 2026")

    def test_nice_date_without_weekday(self):
        self.assertEqual(nice_date(THURSDAY, "bs", include_weekday=False),
                         "peti mart 2026")

    def test_nice_date_every_month(self):
        for month, name in enumerate(CLDR_BS_MONTHS, start=1):
            with self.subTest(month=month):
                self.assertEqual(
                    nice_date(datetime(2026, month, 1), "bs",
                              include_weekday=False),
                    f"prvi {name} 2026")

    def test_nice_month_every_month(self):
        for month, name in enumerate(CLDR_BS_MONTHS, start=1):
            with self.subTest(month=month):
                self.assertEqual(nice_month(datetime(2026, month, 1), "bs"),
                                 name.capitalize())

    def test_january_february_march(self):
        self.assertEqual(nice_month(datetime(2026, 1, 15), "bs"), "Januar")
        self.assertEqual(nice_month(datetime(2026, 2, 15), "bs"), "Februar")
        self.assertEqual(nice_month(datetime(2026, 3, 15), "bs"), "Mart")

    def test_nice_weekday_every_day(self):
        for offset, name in enumerate(CLDR_BS_WEEKDAYS):
            with self.subTest(weekday=name):
                self.assertEqual(
                    nice_weekday(datetime(2026, 3, 2 + offset), "bs"),
                    name.capitalize())

    def test_nice_day_takes_the_month_name(self):
        self.assertEqual(nice_day(THURSDAY, "bs"), "05 Mart")
        self.assertEqual(nice_day(THURSDAY, "bs", date_format="MDY"),
                         "Mart 05")

    def test_nice_date_time_joins_with_u(self):
        spoken = nice_date_time(datetime(2026, 3, 5, 12, 0), "bs")
        self.assertEqual(spoken, "četvrtak, peti mart 2026 u podne")

    def test_bc_year_marker(self):
        self.assertEqual(nice_year(datetime(44, 3, 15), "bs", bc=True),
                         "44 prije nove ere")

    def test_no_croatian_month_name_leaks(self):
        for month in range(1, 13):
            spoken = nice_date(datetime(2026, month, 1), "bs")
            for name in CROATIAN_MONTHS:
                with self.subTest(month=month, croatian=name):
                    self.assertNotIn(name, spoken)

    def test_time_reads_as_before(self):
        self.assertEqual(nice_time(datetime(2026, 3, 5, 14, 30), "bs"),
                         nice_time(datetime(2026, 3, 5, 14, 30), "hr"))


class TestCroatianUnchanged(unittest.TestCase):

    def test_nice_date(self):
        self.assertEqual(nice_date(THURSDAY, "hr"),
                         "četvrtak, peti ožujak 2026")

    def test_nice_month_every_month(self):
        for month, name in enumerate(CROATIAN_MONTHS, start=1):
            with self.subTest(month=month):
                self.assertEqual(nice_month(datetime(2026, month, 1), "hr"),
                                 name.capitalize())

    def test_nice_date_time(self):
        self.assertEqual(
            nice_date_time(datetime(2026, 3, 5, 12, 0), "hr"),
            "četvrtak, peti ožujak 2026 u podne")

    def test_bc_year_marker(self):
        self.assertEqual(nice_year(datetime(44, 3, 15), "hr", bc=True),
                         "44 pr. Kr.")


if __name__ == "__main__":
    unittest.main()
