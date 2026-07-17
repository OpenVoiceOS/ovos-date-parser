"""Finnish date/time tests: behaviour, adversarial input, round-trip sweep."""
import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (extract_datetime, extract_duration, nice_time,
                              nice_duration, nice_weekday, nice_month,
                              nice_year, nice_date)
from ovos_date_parser.dates_fi import extract_duration_fi

# Wednesday 10 January 2024, 12:00
ANCHOR = datetime(2024, 1, 10, 12, 0)


class TestNiceTimeFi(unittest.TestCase):
    def test_24hour(self):
        self.assertEqual(nice_time(datetime(2024, 1, 1, 15, 30), "fi",
                                   use_24hour=True),
                         "kello viisitoista kolmekymmentä")
        self.assertEqual(nice_time(datetime(2024, 1, 1, 9, 5), "fi",
                                   use_24hour=True),
                         "kello yhdeksän nolla viisi")
        self.assertEqual(nice_time(datetime(2024, 1, 1, 14, 0), "fi",
                                   use_24hour=True),
                         "kello neljätoista")

    def test_12hour(self):
        self.assertEqual(nice_time(datetime(2024, 1, 1, 15, 30), "fi"),
                         "kello kolme kolmekymmentä")

    def test_special(self):
        self.assertEqual(nice_time(datetime(2024, 1, 1, 0, 0), "fi"),
                         "keskiyö")
        self.assertEqual(nice_time(datetime(2024, 1, 1, 12, 0), "fi"),
                         "keskipäivä")

    def test_ampm_part_of_day(self):
        self.assertTrue(nice_time(datetime(2024, 1, 1, 20, 0), "fi",
                                  use_ampm=True).endswith("illalla"))
        self.assertTrue(nice_time(datetime(2024, 1, 1, 8, 0), "fi",
                                  use_ampm=True).endswith("aamulla"))

    def test_display(self):
        self.assertEqual(nice_time(datetime(2024, 1, 1, 13, 4), "fi",
                                   speech=False, use_24hour=True), "13:04")


class TestNiceDateFamilyFi(unittest.TestCase):
    def test_weekday(self):
        self.assertEqual(nice_weekday(ANCHOR, "fi"), "Keskiviikko")

    def test_month(self):
        self.assertEqual(nice_month(ANCHOR, "fi"), "Tammikuu")

    def test_year_is_cardinal(self):
        self.assertEqual(nice_year(datetime(1984, 1, 1), "fi"),
                         "tuhatyhdeksänsataakahdeksankymmentäneljä")

    def test_year_bc(self):
        self.assertTrue(nice_year(datetime(44, 1, 1), "fi", bc=True)
                        .endswith("ennen Kristusta"))

    def test_nice_date_non_empty(self):
        self.assertTrue(nice_date(ANCHOR, "fi").strip())


class TestExtractDatetimeFi(unittest.TestCase):
    def test_relative_days(self):
        self.assertEqual(extract_datetime("huomenna", "fi", ANCHOR)[0].date(),
                         datetime(2024, 1, 11).date())
        self.assertEqual(extract_datetime("eilen", "fi", ANCHOR)[0].date(),
                         datetime(2024, 1, 9).date())
        self.assertEqual(extract_datetime("ylihuomenna", "fi", ANCHOR)[0].date(),
                         datetime(2024, 1, 12).date())

    def test_weekday_essive_and_next(self):
        self.assertEqual(
            extract_datetime("maanantaina", "fi", ANCHOR)[0].date(),
            datetime(2024, 1, 15).date())
        self.assertEqual(
            extract_datetime("ensi maanantaina", "fi", ANCHOR)[0].date(),
            datetime(2024, 1, 15).date())
        self.assertEqual(
            extract_datetime("viime perjantaina", "fi", ANCHOR)[0].date(),
            datetime(2024, 1, 5).date())

    def test_clock(self):
        dt, _ = extract_datetime("kello 15:30", "fi", ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (15, 30))
        dt, _ = extract_datetime("kello 9", "fi", ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (9, 0))
        dt, _ = extract_datetime("15.30", "fi", ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (15, 30))

    def test_month_date(self):
        self.assertEqual(
            extract_datetime("15. tammikuuta", "fi", ANCHOR)[0].date(),
            datetime(2024, 1, 15).date())
        self.assertEqual(
            extract_datetime("tammikuun 20", "fi", ANCHOR)[0].date(),
            datetime(2024, 1, 20).date())

    def test_relative_offset(self):
        self.assertEqual(
            extract_datetime("kolme päivää kuluttua", "fi", ANCHOR)[0].date(),
            datetime(2024, 1, 13).date())

    def test_leftover(self):
        dt, leftover = extract_datetime("tapaaminen kello 9", "fi", ANCHOR)
        self.assertEqual(leftover, "tapaaminen")


class TestExtractDatetimeAdversarialFi(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(extract_datetime("", "fi", ANCHOR))

    def test_none(self):
        self.assertIsNone(extract_datetime(None, "fi", ANCHOR))

    def test_no_date(self):
        self.assertIsNone(extract_datetime("hei mitä kuuluu", "fi", ANCHOR))

    def test_punctuation_only(self):
        self.assertIsNone(extract_datetime("?!.,", "fi", ANCHOR))

    def test_invalid_clock_not_time(self):
        # 25:99 is not a valid clock; must not be read as a time
        res = extract_datetime("kello 25:99", "fi", ANCHOR)
        self.assertIsNone(res)

    def test_out_of_range_ordinal_day_ignored(self):
        # "45. tammikuuta" -> impossible day, falls back to day 1 of month
        res = extract_datetime("45. tammikuuta", "fi", ANCHOR)
        self.assertIsNotNone(res)
        self.assertEqual(res[0].month, 1)

    def test_garbage_tokens(self):
        self.assertIsNone(extract_datetime("xyzzy qwerty 12345abc", "fi",
                                           ANCHOR))


class TestExtractDurationAdversarialFi(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(extract_duration("", "fi"))

    def test_no_duration(self):
        dur, rem = extract_duration("ei mitään tässä", "fi")
        self.assertIsNone(dur)

    def test_unit_without_number(self):
        dur, _ = extract_duration("tuntia", "fi")
        self.assertIsNone(dur)

    def test_number_without_unit(self):
        dur, _ = extract_duration("viisi", "fi")
        self.assertIsNone(dur)

    def test_direct_function_matches_dispatch(self):
        self.assertEqual(extract_duration_fi("kaksi tuntia")[0],
                         timedelta(hours=2))


class TestDurationRoundTripFi(unittest.TestCase):
    """Sweep: nice_duration(seconds) -> extract_duration -> identity."""

    def _values(self):
        vals = set()
        # every second 1..90 (covers seconds+minute boundary)
        vals.update(range(1, 141))
        # minute multiples
        vals.update(m * 60 for m in range(1, 61))
        # hour multiples and combinations
        for h in range(1, 13):
            vals.add(h * 3600)
            vals.add(h * 3600 + 30 * 60)
            vals.add(h * 3600 + 90)
        # day-scale combinations
        for d in range(1, 15):
            vals.add(d * 86400 + 3600 + 60 + 1)
        return sorted(vals)

    def test_round_trip(self):
        values = self._values()
        self.assertGreaterEqual(len(values), 200)
        for secs in values:
            spoken = nice_duration(secs, "fi")
            dur, _ = extract_duration(spoken, "fi")
            self.assertIsNotNone(dur, f"{secs}: {spoken!r}")
            self.assertEqual(int(dur.total_seconds()), secs,
                             f"{secs}: {spoken!r} -> {dur}")


if __name__ == "__main__":
    unittest.main()
