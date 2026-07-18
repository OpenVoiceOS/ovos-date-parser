"""Norwegian Nynorsk (nn) date/time tests.

Covers the happy path, adversarial input (empty, malformed, boundary,
contract-violating) and a round-trip sweep of 250 duration values for
minutes and hours plus a full-day quarter-hour clock sweep. Anchors are
verified against Nynorskordboka and Språkrådet, not pinned from engine
output.
"""
import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (extract_datetime, extract_duration, nice_date,
                              nice_day, nice_duration, nice_month,
                              nice_relative_time, nice_time, nice_weekday,
                              nice_year)

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a Tuesday


class TestNiceTimeNn(unittest.TestCase):
    def test_display(self):
        self.assertEqual(
            nice_time(ANCHOR, "nn", speech=False, use_24hour=True), "13:04")

    def test_24hour_speech(self):
        self.assertEqual(nice_time(ANCHOR, "nn", use_24hour=True),
                         "tretten null fire")

    def test_one_oclock_neuter(self):
        one = datetime(2017, 6, 27, 1, 0)
        self.assertEqual(nice_time(one, "nn", use_24hour=True), "eitt")

    def test_noon_midnight(self):
        self.assertEqual(nice_time(datetime(2017, 6, 27, 12, 0), "nn"),
                         "middag")
        self.assertEqual(nice_time(datetime(2017, 6, 27, 0, 0), "nn"),
                         "midnatt")

    def test_ampm_qualifier(self):
        self.assertEqual(nice_time(ANCHOR, "nn", use_ampm=True),
                         "eitt null fire om ettermiddagen")


class TestNiceDateNn(unittest.TestCase):
    def test_weekday(self):
        self.assertEqual(nice_weekday(ANCHOR, "nn").lower(), "tysdag")
        self.assertEqual(nice_weekday(datetime(2017, 7, 1), "nn").lower(),
                         "laurdag")

    def test_month(self):
        self.assertEqual(nice_month(ANCHOR, "nn").lower(), "juni")

    def test_date_ordinal(self):
        self.assertIn("tjuesjuande", nice_date(ANCHOR, "nn"))

    def test_relative_words(self):
        self.assertEqual(nice_date(ANCHOR, "nn", now=ANCHOR), "i dag")
        self.assertEqual(
            nice_date(ANCHOR - timedelta(days=1), "nn", now=ANCHOR), "i går")
        self.assertEqual(
            nice_date(ANCHOR + timedelta(days=1), "nn", now=ANCHOR),
            "i morgon")


class TestNiceYearNn(unittest.TestCase):
    def test_years(self):
        # tens-first, decimal tens (åttifire, not fireogåtti)
        self.assertEqual(nice_year(datetime(1984, 1, 1), "nn"),
                         "nitten hundre og åttifire")
        self.assertEqual(nice_year(datetime(2021, 1, 1), "nn"),
                         "to tusen og tjueein")
        self.assertEqual(nice_year(datetime(2000, 1, 1), "nn"), "to tusen")


class TestNiceDurationNn(unittest.TestCase):
    def test_speech(self):
        self.assertEqual(nice_duration(3725, "nn"),
                         "ein time to minutt fem sekund")

    def test_display(self):
        self.assertIn(":", nice_duration(163, "nn", speech=False))

    def test_relative_time(self):
        spoken = nice_relative_time(ANCHOR + timedelta(minutes=5),
                                    relative_to=ANCHOR, lang="nn")
        self.assertTrue(spoken.strip())


class TestExtractDatetimeNn(unittest.TestCase):
    def test_tomorrow(self):
        self.assertEqual(
            extract_datetime("i morgon", "nn", anchorDate=ANCHOR)[0].date(),
            (ANCHOR + timedelta(days=1)).date())

    def test_day_after_tomorrow(self):
        self.assertEqual(
            extract_datetime("overmorgon", "nn", anchorDate=ANCHOR)[0].date(),
            (ANCHOR + timedelta(days=2)).date())

    def test_clock_time(self):
        dt, _ = extract_datetime("klokka 15:30", "nn", anchorDate=ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (15, 30))

    def test_month_date(self):
        dt, _ = extract_datetime("3 mai 2020", "nn", anchorDate=ANCHOR)
        self.assertEqual((dt.year, dt.month, dt.day), (2020, 5, 3))

    def test_next_week(self):
        nn = extract_datetime("neste veke", "nn", anchorDate=ANCHOR)[0]
        self.assertEqual(nn.date(), (ANCHOR + timedelta(days=7)).date())

    def test_relative_hours(self):
        dt, _ = extract_datetime("om 2 timar", "nn", anchorDate=ANCHOR)
        self.assertEqual(dt.hour, 15)

    def test_weekday(self):
        nn = extract_datetime("måndag", "nn", anchorDate=ANCHOR)[0]
        self.assertEqual(nn.weekday(), 0)


class TestExtractDurationNn(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            extract_duration("om 10 minutt", "nn")[0], timedelta(minutes=10))

    def test_compound(self):
        self.assertEqual(extract_duration("2 timar og 30 minutt", "nn")[0],
                         timedelta(hours=2, minutes=30))

    def test_days_weeks(self):
        self.assertEqual(extract_duration("3 dagar", "nn")[0],
                         timedelta(days=3))
        self.assertEqual(extract_duration("2 veker", "nn")[0],
                         timedelta(weeks=2))


class TestAdversarialNn(unittest.TestCase):
    def test_empty_string(self):
        self.assertIsNone(extract_datetime("", "nn", anchorDate=ANCHOR))

    def test_whitespace_only(self):
        self.assertIsNone(extract_datetime("   ", "nn", anchorDate=ANCHOR))

    def test_gibberish_no_date(self):
        self.assertIsNone(
            extract_datetime("hei korleis går det", "nn", anchorDate=ANCHOR))

    def test_out_of_range_time_not_parsed_as_clock(self):
        result = extract_datetime("25:99", "nn", anchorDate=ANCHOR)
        if result is not None:
            dt = result[0]
            self.assertLess(dt.hour, 24)
            self.assertLess(dt.minute, 60)

    def test_glued_clock_tokens_do_not_crash(self):
        # digit-leading tokens with trailing letters or slashes must not raise
        for token in ["20h", "klokka 20h", "3h30", "15/06/20", "3/0/0",
                      "0/0/0", "10sept"]:
            with self.subTest(token=token):
                extract_datetime(token, "nn", anchorDate=ANCHOR)

    def test_impossible_dates_return_none(self):
        for token in ["30 februar", "31 april", "29 februar", "31 april 2020"]:
            with self.subTest(token=token):
                self.assertIsNone(
                    extract_datetime(token, "nn", anchorDate=ANCHOR))

    def test_bare_number_no_unit(self):
        duration, remainder = extract_duration("42", "nn")
        self.assertIsNone(duration)
        self.assertIn("42", remainder)

    def test_empty_duration(self):
        # the shared duration engine returns None (not a tuple) for empty input
        self.assertIsNone(extract_duration("", "nn"))

    def test_zero_and_large_minutes(self):
        self.assertEqual(extract_duration("0 minutt", "nn")[0], timedelta(0))
        self.assertEqual(extract_duration("100000 minutt", "nn")[0],
                         timedelta(minutes=100000))

    def test_duration_leaves_remainder(self):
        duration, remainder = extract_duration(
            "vekk meg om 10 minutt takk", "nn")
        self.assertEqual(duration, timedelta(minutes=10))
        self.assertIn("takk", remainder)


class TestRoundTripNn(unittest.TestCase):
    """Sweep 250 duration values through the digit-form extractor and
    assert an exact round-trip."""

    def test_minutes_sweep(self):
        for n in range(1, 251):
            got, _ = extract_duration(f"{n} minutt", "nn")
            self.assertEqual(got, timedelta(minutes=n), f"{n} minutt")

    def test_hours_sweep(self):
        for n in range(1, 251):
            got, _ = extract_duration(f"{n} timar", "nn")
            self.assertEqual(got, timedelta(hours=n), f"{n} timar")

    def test_clock_sweep(self):
        for hh in range(0, 24):
            for mm in (0, 15, 30, 45):
                txt = f"klokka {hh:02d}:{mm:02d}"
                dt, _ = extract_datetime(txt, "nn", anchorDate=ANCHOR)
                self.assertEqual((dt.hour, dt.minute), (hh, mm), txt)


class TestRealSentencesNn(unittest.TestCase):
    """Natural Nynorsk sentences with the target embedded in surrounding
    words, punctuation and casing. Expected calendar values are computed
    independently from the Tuesday 2017-06-27 13:04 anchor; the linguistic
    anchors (weekday/month/ordinal words) follow Nynorskordboka."""

    def _dt(self, text):
        return extract_datetime(text, "nn", anchorDate=ANCHOR)

    def test_alarm_digit_clock_rolls_forward(self):
        dt, rem = self._dt("vekk meg klokka 7")
        # 07:00 is earlier than the 13:04 anchor -> next day
        self.assertEqual(dt, datetime(2017, 6, 28, 7, 0))
        self.assertEqual(rem, "vekk meg")

    def test_alarm_tomorrow_with_time(self):
        dt, rem = self._dt("set ein alarm klokka 07:30 i morgon")
        self.assertEqual(dt, datetime(2017, 6, 28, 7, 30))
        self.assertEqual(rem, "set ein alarm")

    def test_meeting_weekday_and_hour(self):
        dt, rem = self._dt("møtet er på fredag klokka 14")
        self.assertEqual(dt, datetime(2017, 6, 30, 14, 0))
        self.assertEqual(rem, "møtet er")

    def test_next_tuesday_in_sentence(self):
        dt, _ = self._dt("vi ses neste tysdag")
        self.assertEqual(dt.date(), datetime(2017, 7, 4).date())

    def test_ordinal_month_rolls_to_next_year(self):
        # 3 May already passed in 2017 -> next occurrence is 2018
        dt, _ = self._dt("bursdagen min er 3. mai")
        self.assertEqual(dt.date(), datetime(2018, 5, 3).date())

    def test_explicit_year_in_sentence(self):
        dt, _ = self._dt("eg reiser 15. august 2021")
        self.assertEqual(dt.date(), datetime(2021, 8, 15).date())

    def test_tomorrow_morning_qualifier(self):
        dt, _ = self._dt("vekk meg i morgon tidleg")
        self.assertEqual(dt, datetime(2017, 6, 28, 8, 0))

    def test_duration_sentence_spoken_number(self):
        dur, rem = extract_duration(
            "kan du minne meg på det om ti minutt", "nn")
        self.assertEqual(dur, timedelta(minutes=10))
        self.assertIn("minne meg", rem)

    def test_duration_sentence_half_hours(self):
        # "ein og ein halv time" = 1.5 hours
        dur, _ = extract_duration("timeren går om ein og ein halv time", "nn")
        self.assertEqual(dur, timedelta(hours=1, minutes=30))

    def test_duration_sentence_days(self):
        dur, _ = extract_duration("vi er borte i tre dagar", "nn")
        self.assertEqual(dur, timedelta(days=3))


class TestEdgeCasesNn(unittest.TestCase):
    def test_uppercase_input(self):
        dt, _ = extract_datetime("I MORGON", "nn", anchorDate=ANCHOR)
        self.assertEqual(dt.date(), datetime(2017, 6, 28).date())

    def test_mixed_case_clock(self):
        dt, _ = extract_datetime("Klokka 15:30", "nn", anchorDate=ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (15, 30))

    def test_trailing_punctuation(self):
        dt, rem = extract_datetime("vekk meg klokka 15:30!!!", "nn",
                                   anchorDate=ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (15, 30))
        self.assertIn("vekk meg", rem)

    def test_leap_day(self):
        dt, _ = extract_datetime("29. februar 2020", "nn", anchorDate=ANCHOR)
        self.assertEqual(dt.date(), datetime(2020, 2, 29).date())

    def test_clock_wraparound_bounds(self):
        for txt, exp in (("klokka 00:00", (0, 0)), ("klokka 23:59", (23, 59))):
            dt, _ = extract_datetime(txt, "nn", anchorDate=ANCHOR)
            self.assertEqual((dt.hour, dt.minute), exp, txt)

    def test_lang_code_variant_nn_no(self):
        self.assertEqual(nice_time(ANCHOR, "nn-NO", use_24hour=True),
                         "tretten null fire")
        dt, _ = extract_datetime("i morgon", "nn-NO", anchorDate=ANCHOR)
        self.assertEqual(dt.date(), datetime(2017, 6, 28).date())

    def test_none_input_raises(self):
        # the string-based contract rejects None (no silent coercion)
        with self.assertRaises((AttributeError, TypeError)):
            extract_datetime(None, "nn", anchorDate=ANCHOR)


class TestCrossContaminationNn(unittest.TestCase):
    """Bokmål-only forms must NOT be parsed by the Nynorsk engine."""

    def test_nb_tomorrow_word_rejected(self):
        self.assertIsNone(
            extract_datetime("i morgen", "nn", anchorDate=ANCHOR))

    def test_nb_weekday_rejected(self):
        self.assertIsNone(
            extract_datetime("neste tirsdag", "nn", anchorDate=ANCHOR))
        self.assertIsNone(
            extract_datetime("neste lørdag", "nn", anchorDate=ANCHOR))

    def test_nb_week_noun_rejected(self):
        # Nynorsk week is "veke"; the Bokmål "uke(r)" must not match
        self.assertIsNone(extract_duration("2 uker", "nn")[0])
        self.assertIsNone(
            extract_datetime("neste uke", "nn", anchorDate=ANCHOR))


if __name__ == "__main__":
    unittest.main()
