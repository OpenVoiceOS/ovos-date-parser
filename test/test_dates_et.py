"""Estonian date/time tests: behaviour, adversarial input, round-trip sweep."""
import unittest
from datetime import datetime, timedelta

import pytest

from ovos_date_parser import (extract_datetime, extract_duration, nice_time,
                              nice_duration, nice_weekday, nice_month,
                              nice_year, nice_date)

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
        # a lone hour takes its next reading after the 12:00 anchor (ruling 17)
        dt, _ = extract_datetime("kell 9", "et", ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (21, 0))

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
    """A lone spoken hour takes the next twelve-hour reading after the 12:00
    anchor (ruling 17), so half past one is 13:30."""

    def _hm(self, text):
        res = extract_datetime(text, "et", ANCHOR)
        self.assertIsNotNone(res, text)
        return res[0].hour, res[0].minute

    def test_half_hour_is_before_named_hour(self):
        # the classic trap: "pool kaks" is half past one, NOT half past two
        self.assertEqual(self._hm("pool kaks"), (13, 30))
        self.assertEqual(self._hm("pool kolm"), (14, 30))

    def test_half_hour_wraps_at_one(self):
        self.assertEqual(self._hm("pool üks"), (12, 30))

    def test_quarter_into_hour(self):
        # traditional Estonian counting toward the coming hour
        self.assertEqual(self._hm("veerand kaks"), (13, 15))

    def test_three_quarters_into_hour(self):
        self.assertEqual(self._hm("kolmveerand kaks"), (13, 45))

    def test_with_kell(self):
        self.assertEqual(self._hm("kell pool kaks"), (13, 30))

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

    def test_out_of_range_ordinal_day_is_no_date(self):
        # January has 31 days, so "45. jaanuar" names no day
        self.assertIsNone(extract_datetime("45. jaanuar", "et", ANCHOR))

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


class TestRealSentencesEt(unittest.TestCase):
    """Full natural sentences, not word<->value anchors.

    Every expected value is derived by hand from the anchor (Wednesday
    10 January 2024, 12:00) and Estonian reference usage, never copied from
    parser output. Each case also checks the surrounding words survive as
    leftover text.
    """

    # (sentence, expected (Y, M, D, h, m), expected leftover)
    CASES = [
        # idiomatic clock (traditional counting toward the coming hour)
        # with a day word the spoken hour stays (ruling 17)
        ("näeme homme pool kaks", (2024, 1, 11, 1, 30), "näeme"),
        # relative time offsets with the genitive numeral
        ("tuleta mulle meelde kolme tunni pärast",
         (2024, 1, 10, 15, 0), "tuleta mulle meelde"),
        ("meeldetuletus viie minuti pärast",
         (2024, 1, 10, 12, 5), "meeldetuletus"),
        ("ärka poole tunni pärast", (2024, 1, 10, 12, 30), "ärka"),
        # genitive of "poolteist" is "poolteise" or "pooleteise" (ÕS 2018)
        ("helista pooleteise tunni pärast",
         (2024, 1, 10, 13, 30), "helista"),
        # relative day/week offsets
        # a counted offset keeps the anchor clock (class 1)
        ("helista mulle kolme päeva pärast",
         (2024, 1, 13, 12, 0), "helista mulle"),
        ("kohtumine kahe nädala pärast", (2024, 1, 24, 12, 0), "kohtumine"),
        # weekdays, nominative and adessive, with järgmine/eelmine
        ("kohtumine on järgmisel esmaspäeval kell 15:30",
         (2024, 1, 15, 15, 30), "kohtumine on"),
        ("broneeri aeg reedel", (2024, 1, 12, 0, 0), "broneeri aeg"),
        ("käisin eelmisel reedel", (2024, 1, 5, 0, 0), "käisin"),
        # relative days
        ("näeme homme", (2024, 1, 11, 0, 0), "näeme"),
        ("tulin eile koju", (2024, 1, 9, 0, 0), "tulin koju"),
        # calendar date with month name
        ("lähen 15. jaanuaril", (2024, 1, 15, 0, 0), "lähen"),
        # plain clock in a sentence, with trailing punctuation
        ("rong väljub 15:30", (2024, 1, 10, 15, 30), "rong väljub"),
    ]

    def test_sentences(self):
        for text, exp, leftover in self.CASES:
            res = extract_datetime(text, "et", ANCHOR)
            self.assertIsNotNone(res, text)
            got = (res[0].year, res[0].month, res[0].day,
                   res[0].hour, res[0].minute)
            self.assertEqual(got, exp, text)
            self.assertEqual(res[1], leftover, text)


class TestRealSentenceDurationsEt(unittest.TestCase):
    """Durations inside natural sentences, expectations derived by hand."""

    CASES = [
        ("sea taimer kaks tundi", 2 * 3600),
        ("puhka pool tundi", 30 * 60),
        ("kestus on poolteist tundi", 90 * 60),
        ("jookse kolm ja pool tundi", int(3.5 * 3600)),
        ("oota viisteist minutit", 15 * 60),
        ("maga kaheksa tundi", 8 * 3600),
        ("kolmkümmend minutit", 30 * 60),
    ]

    def test_sentences(self):
        for text, secs in self.CASES:
            dur, rem = extract_duration(text, "et")
            self.assertIsNotNone(dur, text)
            self.assertEqual(int(dur.total_seconds()), secs, text)


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


# A lone spoken hour takes the next twelve-hour reading after the anchor
# (ruling 17): at noon on 10 January 2024, "veerand kaheksa" (07:15) is 19:15.
@pytest.mark.parametrize("text,expected,leftover", [
    ("Ärata mind veerand kaheksa", (2024, 1, 10, 19, 15), "Ärata mind"),
    ("kohtume pool kolm", (2024, 1, 10, 14, 30), "kohtume"),
    ("äratus kolmveerand kaheksa", (2024, 1, 10, 19, 45), "äratus"),
    ("äratus kell 7.", (2024, 1, 10, 19, 0), "äratus"),
])
def test_lone_hour_in_a_sentence(text, expected, leftover):
    res = extract_datetime(text, "et", ANCHOR)
    got = (res[0].year, res[0].month, res[0].day, res[0].hour, res[0].minute)
    assert (got, res[1]) == (expected, leftover)
