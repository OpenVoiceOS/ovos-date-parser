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


class TestClockIdiomsFi(unittest.TestCase):
    def _hm(self, text):
        res = extract_datetime(text, "fi", ANCHOR)
        self.assertIsNotNone(res, text)
        return res[0].hour, res[0].minute

    def test_half_hour_is_before_named_hour(self):
        # the classic trap: "puoli kaksi" is 1:30, NOT 2:30
        self.assertEqual(self._hm("puoli kaksi"), (1, 30))
        self.assertEqual(self._hm("puoli kolme"), (2, 30))

    def test_half_hour_wraps_at_one(self):
        # "puoli yksi" is half an hour before one o'clock -> 12:30
        self.assertEqual(self._hm("puoli yksi"), (12, 30))

    def test_half_hour_with_kello(self):
        self.assertEqual(self._hm("kello puoli kaksi"), (1, 30))

    def test_quarter_past(self):
        self.assertEqual(self._hm("varttia yli kaksi"), (2, 15))

    def test_quarter_to(self):
        self.assertEqual(self._hm("varttia vaille kaksi"), (1, 45))

    def test_minutes_past(self):
        self.assertEqual(self._hm("kymmenen yli kaksi"), (2, 10))
        self.assertEqual(self._hm("viisitoista yli kolme"), (3, 15))

    def test_minutes_to(self):
        self.assertEqual(self._hm("kymmentä vaille kaksi"), (1, 50))

    def test_duration_puoli_not_read_as_clock(self):
        # "puoli tuntia" is a duration, not a half-clock -> no datetime
        self.assertIsNone(extract_datetime("puoli tuntia", "fi", ANCHOR))


class TestFractionalDurationFi(unittest.TestCase):
    def test_half_hour(self):
        self.assertEqual(extract_duration("puoli tuntia", "fi")[0],
                         timedelta(minutes=30))

    def test_one_and_a_half_hours(self):
        self.assertEqual(extract_duration("puolitoista tuntia", "fi")[0],
                         timedelta(hours=1, minutes=30))

    def test_n_and_a_half_hours(self):
        self.assertEqual(extract_duration("kolme ja puoli tuntia", "fi")[0],
                         timedelta(hours=3, minutes=30))

    def test_half_minute(self):
        self.assertEqual(extract_duration("puoli minuuttia", "fi")[0],
                         timedelta(seconds=30))


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


class TestRealSentencesFi(unittest.TestCase):
    """Full natural sentences, not word<->value anchors.

    Every expected value is derived by hand from the anchor (Wednesday
    10 January 2024, 12:00) and Finnish reference usage, never copied from
    parser output. Each case also checks the surrounding words survive as
    leftover text.
    """

    # (sentence, expected (Y, M, D, h, m), expected leftover)
    CASES = [
        # idiomatic clock embedded in a request
        ("Herätä minut varttia yli seitsemän",
         (2024, 1, 10, 7, 15), "herätä minut"),
        ("tavataan puoli kolme", (2024, 1, 10, 2, 30), "tavataan"),
        ("nähdään huomenna puoli kaksi", (2024, 1, 11, 1, 30), "nähdään"),
        ("herätys varttia vaille kahdeksan",
         (2024, 1, 10, 7, 45), "herätys"),
        ("soita kymmentä vaille viisi", (2024, 1, 10, 4, 50), "soita"),
        # relative time offsets with the genitive numeral, as really spoken
        ("muistuta minua puolentoista tunnin päästä",
         (2024, 1, 10, 13, 30), "muistuta minua"),
        ("palaveri kolmen tunnin päästä", (2024, 1, 10, 15, 0), "palaveri"),
        ("muistutus viiden minuutin päästä",
         (2024, 1, 10, 12, 5), "muistutus"),
        ("herää puolen tunnin päästä", (2024, 1, 10, 12, 30), "herää"),
        # relative day/week offsets, genitive numeral + genitive unit
        ("soita minulle kolmen päivän kuluttua",
         (2024, 1, 13, 0, 0), "soita minulle"),
        ("kokous kahden viikon kuluttua", (2024, 1, 24, 0, 0), "kokous"),
        # weekdays, essive, with ensi/viime
        ("tapaaminen on ensi maanantaina kello 15:30",
         (2024, 1, 15, 15, 30), "tapaaminen on"),
        ("varaa aika perjantaina", (2024, 1, 12, 0, 0), "varaa aika"),
        ("kävin viime perjantaina", (2024, 1, 5, 0, 0), "kävin"),
        # relative days
        ("nähdään huomenna", (2024, 1, 11, 0, 0), "nähdään"),
        ("tulin eilen kotiin", (2024, 1, 9, 0, 0), "tulin kotiin"),
        # calendar dates with the month in the partitive
        ("lähden 15. tammikuuta", (2024, 1, 15, 0, 0), "lähden"),
        ("juhla on tammikuun 20", (2024, 1, 20, 0, 0), "juhla on"),
        # plain clock in a sentence, with trailing punctuation
        ("herätys kello 7.", (2024, 1, 10, 7, 0), "herätys"),
        ("juna lähtee 15:30", (2024, 1, 10, 15, 30), "juna lähtee"),
    ]

    def test_sentences(self):
        for text, exp, leftover in self.CASES:
            res = extract_datetime(text, "fi", ANCHOR)
            self.assertIsNotNone(res, text)
            got = (res[0].year, res[0].month, res[0].day,
                   res[0].hour, res[0].minute)
            self.assertEqual(got, exp, text)
            self.assertEqual(res[1], leftover, text)


class TestRealSentenceDurationsFi(unittest.TestCase):
    """Durations inside natural sentences, expectations derived by hand."""

    CASES = [
        ("ajasta kaksi tuntia", 2 * 3600, "ajasta"),
        ("aseta ajastin kolmekymmentä minuuttia", 30 * 60, "aseta ajastin"),
        ("lepää puoli tuntia", 30 * 60, "lepää"),
        ("kesto on puolitoista tuntia", 90 * 60, "kesto on"),
        ("juokse kolme ja puoli tuntia", int(3.5 * 3600), "juokse"),
        ("odota viisitoista minuuttia", 15 * 60, "odota"),
        ("nuku kahdeksan tuntia", 8 * 3600, "nuku"),
    ]

    def test_sentences(self):
        for text, secs, _leftover in self.CASES:
            dur, rem = extract_duration(text, "fi")
            self.assertIsNotNone(dur, text)
            self.assertEqual(int(dur.total_seconds()), secs, text)


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
