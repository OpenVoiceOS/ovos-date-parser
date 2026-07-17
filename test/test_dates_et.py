"""Estonian date/time tests: behaviour, adversarial input, round-trip sweep."""
import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (extract_datetime, extract_duration, nice_time,
                              nice_duration, nice_weekday, nice_month,
                              nice_year, nice_date)
from ovos_date_parser.dates_et import extract_duration_et

# Wednesday 10 January 2024, 12:00
ANCHOR = datetime(2024, 1, 10, 12, 0)


class TestNiceTimeEt(unittest.TestCase):
    def test_24hour(self):
        self.assertEqual(nice_time(datetime(2024, 1, 1, 15, 30), "et",
                                   use_24hour=True),
                         "kell viisteist kolmkümmend")
        self.assertEqual(nice_time(datetime(2024, 1, 1, 9, 5), "et",
                                   use_24hour=True),
                         "kell üheksa null viis")
        self.assertEqual(nice_time(datetime(2024, 1, 1, 14, 0), "et",
                                   use_24hour=True),
                         "kell neliteist")

    def test_12hour(self):
        self.assertEqual(nice_time(datetime(2024, 1, 1, 15, 30), "et"),
                         "kell kolm kolmkümmend")

    def test_special(self):
        self.assertEqual(nice_time(datetime(2024, 1, 1, 0, 0), "et"),
                         "kesköö")
        self.assertEqual(nice_time(datetime(2024, 1, 1, 12, 0), "et"),
                         "keskpäev")

    def test_ampm_part_of_day(self):
        self.assertTrue(nice_time(datetime(2024, 1, 1, 20, 0), "et",
                                  use_ampm=True).endswith("õhtul"))
        self.assertTrue(nice_time(datetime(2024, 1, 1, 8, 0), "et",
                                  use_ampm=True).endswith("hommikul"))

    def test_display(self):
        self.assertEqual(nice_time(datetime(2024, 1, 1, 13, 4), "et",
                                   speech=False, use_24hour=True), "13:04")


class TestNiceDateFamilyEt(unittest.TestCase):
    def test_weekday(self):
        self.assertEqual(nice_weekday(ANCHOR, "et"), "Kolmapäev")

    def test_month(self):
        self.assertEqual(nice_month(ANCHOR, "et"), "Jaanuar")

    def test_year_is_cardinal(self):
        self.assertEqual(nice_year(datetime(1984, 1, 1), "et"),
                         "tuhat üheksasada kaheksakümmend neli")

    def test_year_bc(self):
        self.assertTrue(nice_year(datetime(44, 1, 1), "et", bc=True)
                        .endswith("enne Kristust"))

    def test_nice_date_non_empty(self):
        self.assertTrue(nice_date(ANCHOR, "et").strip())


class TestExtractDatetimeEt(unittest.TestCase):
    def test_relative_days(self):
        self.assertEqual(extract_datetime("homme", "et", ANCHOR)[0].date(),
                         datetime(2024, 1, 11).date())
        self.assertEqual(extract_datetime("eile", "et", ANCHOR)[0].date(),
                         datetime(2024, 1, 9).date())
        self.assertEqual(extract_datetime("ülehomme", "et", ANCHOR)[0].date(),
                         datetime(2024, 1, 12).date())

    def test_weekday_adessive_and_next(self):
        self.assertEqual(
            extract_datetime("teisipäeval", "et", ANCHOR)[0].date(),
            datetime(2024, 1, 16).date())
        self.assertEqual(
            extract_datetime("järgmine esmaspäev", "et", ANCHOR)[0].date(),
            datetime(2024, 1, 15).date())
        self.assertEqual(
            extract_datetime("eelmine reede", "et", ANCHOR)[0].date(),
            datetime(2024, 1, 5).date())

    def test_clock(self):
        dt, _ = extract_datetime("kell 15:30", "et", ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (15, 30))
        dt, _ = extract_datetime("kell 9", "et", ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (9, 0))

    def test_month_date(self):
        self.assertEqual(
            extract_datetime("15. jaanuar", "et", ANCHOR)[0].date(),
            datetime(2024, 1, 15).date())

    def test_relative_offset(self):
        self.assertEqual(
            extract_datetime("kolm päeva pärast", "et", ANCHOR)[0].date(),
            datetime(2024, 1, 13).date())

    def test_leftover(self):
        dt, leftover = extract_datetime("kohtumine kell 9", "et", ANCHOR)
        self.assertEqual(leftover, "kohtumine")


class TestClockIdiomsEt(unittest.TestCase):
    def _hm(self, text):
        res = extract_datetime(text, "et", ANCHOR)
        self.assertIsNotNone(res, text)
        return res[0].hour, res[0].minute

    def test_half_hour_is_before_named_hour(self):
        # the classic trap: "pool kaks" is 1:30, NOT 2:30
        self.assertEqual(self._hm("pool kaks"), (1, 30))
        self.assertEqual(self._hm("pool kolm"), (2, 30))

    def test_half_hour_wraps_at_one(self):
        self.assertEqual(self._hm("pool üks"), (12, 30))

    def test_quarter_into_hour(self):
        # traditional Estonian counting toward the coming hour
        self.assertEqual(self._hm("veerand kaks"), (1, 15))

    def test_three_quarters_into_hour(self):
        self.assertEqual(self._hm("kolmveerand kaks"), (1, 45))

    def test_with_kell(self):
        self.assertEqual(self._hm("kell pool kaks"), (1, 30))

    def test_duration_pool_not_read_as_clock(self):
        # "pool tundi" is a duration, not a half-clock -> no datetime
        self.assertIsNone(extract_datetime("pool tundi", "et", ANCHOR))


class TestFractionalDurationEt(unittest.TestCase):
    def test_half_hour(self):
        self.assertEqual(extract_duration("pool tundi", "et")[0],
                         timedelta(minutes=30))

    def test_one_and_a_half_hours(self):
        self.assertEqual(extract_duration("poolteist tundi", "et")[0],
                         timedelta(hours=1, minutes=30))

    def test_n_and_a_half_hours(self):
        self.assertEqual(extract_duration("kolm ja pool tundi", "et")[0],
                         timedelta(hours=3, minutes=30))


class TestExtractDatetimeAdversarialEt(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(extract_datetime("", "et", ANCHOR))

    def test_none(self):
        self.assertIsNone(extract_datetime(None, "et", ANCHOR))

    def test_no_date(self):
        self.assertIsNone(extract_datetime("tere kuidas läheb", "et", ANCHOR))

    def test_punctuation_only(self):
        self.assertIsNone(extract_datetime("?!.,", "et", ANCHOR))

    def test_invalid_clock_not_time(self):
        self.assertIsNone(extract_datetime("kell 25:99", "et", ANCHOR))

    def test_out_of_range_ordinal_day_ignored(self):
        res = extract_datetime("45. jaanuar", "et", ANCHOR)
        self.assertIsNotNone(res)
        self.assertEqual(res[0].month, 1)

    def test_garbage_tokens(self):
        self.assertIsNone(extract_datetime("xyzzy qwerty 12345abc", "et",
                                           ANCHOR))


class TestExtractDurationAdversarialEt(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(extract_duration("", "et"))

    def test_no_duration(self):
        dur, _ = extract_duration("siin pole midagi", "et")
        self.assertIsNone(dur)

    def test_unit_without_number(self):
        dur, _ = extract_duration("tundi", "et")
        self.assertIsNone(dur)

    def test_number_without_unit(self):
        dur, _ = extract_duration("viis", "et")
        self.assertIsNone(dur)

    def test_direct_function_matches_dispatch(self):
        self.assertEqual(extract_duration_et("kaks tundi")[0],
                         timedelta(hours=2))


class TestDurationRoundTripEt(unittest.TestCase):
    """Sweep: nice_duration(seconds) -> extract_duration -> identity."""

    def _values(self):
        vals = set()
        vals.update(range(1, 141))
        vals.update(m * 60 for m in range(1, 61))
        for h in range(1, 13):
            vals.add(h * 3600)
            vals.add(h * 3600 + 30 * 60)
            vals.add(h * 3600 + 90)
        for d in range(1, 15):
            vals.add(d * 86400 + 3600 + 60 + 1)
        return sorted(vals)

    def test_round_trip(self):
        values = self._values()
        self.assertGreaterEqual(len(values), 200)
        for secs in values:
            spoken = nice_duration(secs, "et")
            dur, _ = extract_duration(spoken, "et")
            self.assertIsNotNone(dur, f"{secs}: {spoken!r}")
            self.assertEqual(int(dur.total_seconds()), secs,
                             f"{secs}: {spoken!r} -> {dur}")


if __name__ == "__main__":
    unittest.main()
