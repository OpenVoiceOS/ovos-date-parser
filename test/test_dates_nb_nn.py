"""Norwegian Bokmål (nb) and Nynorsk (nn) date/time tests.

Covers the happy path, adversarial input (empty, malformed, boundary,
contract-violating) and a round-trip sweep of 250 duration values per
written standard. Anchors are verified against Bokmålsordboka /
Nynorskordboka and Språkrådet, not pinned from engine output.
"""
import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (extract_datetime, extract_duration, nice_date,
                              nice_date_time, nice_day, nice_duration,
                              nice_month, nice_relative_time, nice_time,
                              nice_weekday, nice_year)

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a Tuesday


class TestNiceTimeNorwegian(unittest.TestCase):
    def test_display(self):
        for lang in ("nb", "nn"):
            self.assertEqual(
                nice_time(ANCHOR, lang, speech=False, use_24hour=True),
                "13:04", lang)

    def test_24hour_speech(self):
        self.assertEqual(nice_time(ANCHOR, "nb", use_24hour=True),
                         "tretten null fire")
        self.assertEqual(nice_time(ANCHOR, "nn", use_24hour=True),
                         "tretten null fire")

    def test_one_oclock_neuter(self):
        one = datetime(2017, 6, 27, 1, 0)
        self.assertEqual(nice_time(one, "nb", use_24hour=True), "ett")
        self.assertEqual(nice_time(one, "nn", use_24hour=True), "eitt")

    def test_noon_midnight(self):
        for lang in ("nb", "nn"):
            self.assertEqual(nice_time(datetime(2017, 6, 27, 12, 0), lang),
                             "middag", lang)
            self.assertEqual(nice_time(datetime(2017, 6, 27, 0, 0), lang),
                             "midnatt", lang)

    def test_ampm_qualifier(self):
        self.assertEqual(nice_time(ANCHOR, "nb", use_ampm=True),
                         "ett null fire om ettermiddagen")
        self.assertEqual(nice_time(ANCHOR, "nn", use_ampm=True),
                         "eitt null fire om ettermiddagen")


class TestNiceDateNorwegian(unittest.TestCase):
    def test_weekday(self):
        self.assertEqual(nice_weekday(ANCHOR, "nb").lower(), "tirsdag")
        self.assertEqual(nice_weekday(ANCHOR, "nn").lower(), "tysdag")

    def test_month(self):
        for lang in ("nb", "nn"):
            self.assertEqual(nice_month(ANCHOR, lang).lower(), "juni", lang)

    def test_saturday_form(self):
        sat = datetime(2017, 7, 1)
        self.assertEqual(nice_weekday(sat, "nb").lower(), "lørdag")
        self.assertEqual(nice_weekday(sat, "nn").lower(), "laurdag")

    def test_date_ordinal(self):
        # 27th: nb tjuesjuende, nn tjuesjuande
        self.assertIn("tjuesjuende", nice_date(ANCHOR, "nb"))
        self.assertIn("tjuesjuande", nice_date(ANCHOR, "nn"))

    def test_relative_words(self):
        for lang in ("nb", "nn"):
            self.assertEqual(nice_date(ANCHOR, lang, now=ANCHOR), "i dag", lang)
            self.assertEqual(
                nice_date(ANCHOR - timedelta(days=1), lang, now=ANCHOR),
                "i går", lang)
        self.assertEqual(
            nice_date(ANCHOR + timedelta(days=1), "nb", now=ANCHOR),
            "i morgen")
        self.assertEqual(
            nice_date(ANCHOR + timedelta(days=1), "nn", now=ANCHOR),
            "i morgon")


class TestNiceYearNorwegian(unittest.TestCase):
    def test_years(self):
        # tens-first, decimal tens (åttifire, not fireogåtti)
        self.assertEqual(nice_year(datetime(1984, 1, 1), "nb"),
                         "nitten hundre og åttifire")
        self.assertEqual(nice_year(datetime(2021, 1, 1), "nb"),
                         "to tusen og tjueen")
        self.assertEqual(nice_year(datetime(2021, 1, 1), "nn"),
                         "to tusen og tjueein")
        self.assertEqual(nice_year(datetime(2000, 1, 1), "nb"), "to tusen")


class TestNiceDurationNorwegian(unittest.TestCase):
    def test_speech(self):
        self.assertEqual(nice_duration(3725, "nb"),
                         "en time to minutter fem sekunder")
        self.assertEqual(nice_duration(3725, "nn"),
                         "ein time to minutt fem sekund")

    def test_display(self):
        for lang in ("nb", "nn"):
            self.assertIn(":", nice_duration(163, lang, speech=False), lang)

    def test_relative_time(self):
        for lang in ("nb", "nn"):
            spoken = nice_relative_time(ANCHOR + timedelta(minutes=5),
                                        relative_to=ANCHOR, lang=lang)
            self.assertTrue(spoken.strip(), lang)


class TestExtractDatetimeNorwegian(unittest.TestCase):
    def test_tomorrow(self):
        self.assertEqual(
            extract_datetime("i morgen", "nb", anchorDate=ANCHOR)[0].date(),
            (ANCHOR + timedelta(days=1)).date())
        self.assertEqual(
            extract_datetime("i morgon", "nn", anchorDate=ANCHOR)[0].date(),
            (ANCHOR + timedelta(days=1)).date())

    def test_day_after_tomorrow(self):
        self.assertEqual(
            extract_datetime("overmorgen", "nb", anchorDate=ANCHOR)[0].date(),
            (ANCHOR + timedelta(days=2)).date())
        self.assertEqual(
            extract_datetime("overmorgon", "nn", anchorDate=ANCHOR)[0].date(),
            (ANCHOR + timedelta(days=2)).date())

    def test_clock_time(self):
        for lang in ("nb", "nn"):
            dt, _ = extract_datetime("klokka 15:30", lang, anchorDate=ANCHOR)
            self.assertEqual((dt.hour, dt.minute), (15, 30), lang)

    def test_month_date(self):
        for lang in ("nb", "nn"):
            dt, _ = extract_datetime("3 mai 2020", lang, anchorDate=ANCHOR)
            self.assertEqual((dt.year, dt.month, dt.day), (2020, 5, 3), lang)

    def test_next_week(self):
        nb = extract_datetime("neste uke", "nb", anchorDate=ANCHOR)[0]
        self.assertEqual(nb.date(), (ANCHOR + timedelta(days=7)).date())
        nn = extract_datetime("neste veke", "nn", anchorDate=ANCHOR)[0]
        self.assertEqual(nn.date(), (ANCHOR + timedelta(days=7)).date())

    def test_relative_hours(self):
        for lang in ("nb", "nn"):
            dt, _ = extract_datetime("om 2 timer", lang, anchorDate=ANCHOR)
            self.assertEqual(dt.hour, 15, lang)

    def test_weekday(self):
        # next Monday after a Tuesday anchor -> 6 days ahead
        nb = extract_datetime("mandag", "nb", anchorDate=ANCHOR)[0]
        self.assertEqual(nb.weekday(), 0)
        nn = extract_datetime("måndag", "nn", anchorDate=ANCHOR)[0]
        self.assertEqual(nn.weekday(), 0)


class TestExtractDurationNorwegian(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            extract_duration("om 10 minutter", "nb")[0], timedelta(minutes=10))
        self.assertEqual(
            extract_duration("om 10 minutt", "nn")[0], timedelta(minutes=10))

    def test_compound(self):
        for lang, txt in (("nb", "2 timer og 30 minutter"),
                          ("nn", "2 timar og 30 minutt")):
            self.assertEqual(extract_duration(txt, lang)[0],
                             timedelta(hours=2, minutes=30), lang)

    def test_days_weeks(self):
        self.assertEqual(extract_duration("3 dager", "nb")[0],
                         timedelta(days=3))
        self.assertEqual(extract_duration("3 dagar", "nn")[0],
                         timedelta(days=3))
        self.assertEqual(extract_duration("2 uker", "nb")[0],
                         timedelta(weeks=2))
        self.assertEqual(extract_duration("2 veker", "nn")[0],
                         timedelta(weeks=2))


class TestAdversarialNorwegian(unittest.TestCase):
    def test_empty_string(self):
        for lang in ("nb", "nn"):
            self.assertIsNone(extract_datetime("", lang, anchorDate=ANCHOR),
                              lang)

    def test_whitespace_only(self):
        for lang in ("nb", "nn"):
            self.assertIsNone(
                extract_datetime("   ", lang, anchorDate=ANCHOR), lang)

    def test_gibberish_no_date(self):
        for lang, txt in (("nb", "hei hvordan går det"),
                          ("nn", "hei korleis går det")):
            self.assertIsNone(extract_datetime(txt, lang, anchorDate=ANCHOR),
                              lang)

    def test_out_of_range_time_not_parsed_as_clock(self):
        # 25:99 is not a valid wall-clock; must not yield hour=25/min=99
        for lang in ("nb", "nn"):
            result = extract_datetime("25:99", lang, anchorDate=ANCHOR)
            if result is not None:
                dt = result[0]
                self.assertLess(dt.hour, 24, lang)
                self.assertLess(dt.minute, 60, lang)

    def test_bare_number_no_unit(self):
        for lang in ("nb", "nn"):
            duration, remainder = extract_duration("42", lang)
            self.assertIsNone(duration, lang)
            self.assertIn("42", remainder, lang)

    def test_empty_duration(self):
        # the shared duration engine returns None (not a tuple) for empty input
        for lang in ("nb", "nn"):
            self.assertIsNone(extract_duration("", lang), lang)

    def test_zero_and_large_minutes(self):
        for lang, unit in (("nb", "minutter"), ("nn", "minutt")):
            self.assertEqual(
                extract_duration(f"0 {unit}", lang)[0], timedelta(0), lang)
            self.assertEqual(
                extract_duration(f"100000 {unit}", lang)[0],
                timedelta(minutes=100000), lang)

    def test_duration_leaves_remainder(self):
        for lang, txt in (("nb", "vekk meg om 10 minutter takk"),
                          ("nn", "vekk meg om 10 minutt takk")):
            duration, remainder = extract_duration(txt, lang)
            self.assertEqual(duration, timedelta(minutes=10), lang)
            self.assertIn("takk", remainder, lang)


class TestRoundTripNorwegian(unittest.TestCase):
    """Sweep 250 duration values per written standard through the
    digit-form extractor and assert an exact round-trip."""

    def test_minutes_sweep(self):
        for lang, unit in (("nb", "minutter"), ("nn", "minutt")):
            for n in range(1, 251):
                got, _ = extract_duration(f"{n} {unit}", lang)
                self.assertEqual(got, timedelta(minutes=n),
                                 f"{lang}: {n} {unit}")

    def test_hours_sweep(self):
        for lang, unit in (("nb", "timer"), ("nn", "timar")):
            for n in range(1, 251):
                got, _ = extract_duration(f"{n} {unit}", lang)
                self.assertEqual(got, timedelta(hours=n),
                                 f"{lang}: {n} {unit}")

    def test_clock_sweep(self):
        # every quarter hour of the day round-trips through the clock parser
        for lang in ("nb", "nn"):
            for hh in range(0, 24):
                for mm in (0, 15, 30, 45):
                    txt = f"klokka {hh:02d}:{mm:02d}"
                    dt, _ = extract_datetime(txt, lang, anchorDate=ANCHOR)
                    self.assertEqual((dt.hour, dt.minute), (hh, mm),
                                     f"{lang}: {txt}")


if __name__ == "__main__":
    unittest.main()
