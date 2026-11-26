import unittest
from datetime import datetime, timedelta

import pytest

from ovos_date_parser import (extract_datetime, extract_duration, nice_date,
                              nice_month, nice_time, nice_weekday)

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a Tuesday


class TestNiceTimeKab(unittest.TestCase):
    def test_24hour(self):
        # 13:04 -> 1:04. Native spoken Kabyle uses 12-hour cycle + explicit minutes
        self.assertEqual(nice_time(ANCHOR, "kab", use_24hour=True),
                         "d lweḥda u ṛebɛa n ddqayeq")
        # 8:00 -> d ttmanya
        self.assertEqual(
            nice_time(datetime(2017, 6, 27, 8, 0), "kab", use_24hour=True),
            "d ttmanya")

    def test_12hour(self):
        # 13:04 -> 1:04 PM
        self.assertEqual(nice_time(ANCHOR, "kab"), "d lweḥda u ṛebɛa n ddqayeq")
        
        # With AM/PM marker (tmeddit = afternoon/evening)
        self.assertEqual(nice_time(ANCHOR, "kab", use_ampm=True),
                         "d lweḥda u ṛebɛa n ddqayeq n uzal")
        
        # 9:30 AM -> d tesɛa u neṣṣ n ssbeḥ
        self.assertEqual(
            nice_time(datetime(2017, 6, 27, 9, 30), "kab", use_ampm=True),
            "d tesɛa u neṣṣ n ssbeḥ")

    def test_display(self):
        # Digital display remains unchanged
        self.assertEqual(nice_time(ANCHOR, "kab", speech=False,
                                   use_24hour=True), "13:04")


class TestNiceDateKab(unittest.TestCase):
    def test_weekday_month(self):
        self.assertEqual(nice_weekday(ANCHOR, "kab").lower(), "ttlata")
        self.assertEqual(nice_month(ANCHOR, "kab").lower(), "yunyu")

    def test_relative_words(self):
        self.assertEqual(nice_date(ANCHOR + timedelta(days=1), "kab",
                                   now=ANCHOR), "azekka")
        self.assertEqual(nice_date(ANCHOR, "kab", now=ANCHOR), "ass-a")
        self.assertEqual(nice_date(ANCHOR - timedelta(days=1), "kab",
                                   now=ANCHOR), "iḍelli")


class TestExtractDurationKab(unittest.TestCase):
    def test_digit_quantities(self):
        self.assertEqual(extract_duration("10 n tesdidin", "kab")[0],
                         timedelta(minutes=10))
        self.assertEqual(extract_duration("5 n ddqiqa", "kab")[0],
                         timedelta(minutes=5))

    def test_spoken_quantities(self):
        self.assertEqual(extract_duration("sin wussan", "kab")[0],
                         timedelta(days=2))
        self.assertEqual(extract_duration("snat n tsaɛtin", "kab")[0],
                         timedelta(hours=2))
        self.assertEqual(extract_duration("yiwen amalas", "kab")[0],
                         timedelta(weeks=1))

    def test_remainder(self):
        duration, remainder = extract_duration(
            "sekker tanafa n 10 n tesdidin", "kab")
        self.assertEqual(duration, timedelta(minutes=10))
        self.assertNotIn("tesdidin", remainder)

    def test_no_duration(self):
        self.assertEqual(extract_duration("azul fell-awen", "kab"),
                         (None, "azul fell-awen"))


class TestExtractDatetimeKab(unittest.TestCase):
    def test_relative_days(self):
        result = extract_datetime("azekka", "kab", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(),
                         (ANCHOR + timedelta(days=1)).date())
        result = extract_datetime("iḍelli", "kab", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(),
                         (ANCHOR - timedelta(days=1)).date())
        result = extract_datetime("ass-a", "kab", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(), ANCHOR.date())

    def test_weekday(self):
        # anchor is a Tuesday; lexmis = Thursday
        result = extract_datetime("ass n lexmis", "kab", anchorDate=ANCHOR)
        self.assertEqual(result[0].weekday(), 3)
        self.assertGreater(result[0].date(), ANCHOR.date())

    def test_month_day(self):
        result = extract_datetime("3 yennayer", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].month, result[0].day), (1, 3))
        self.assertEqual(result[0].year, 2018)

    def test_time(self):
        result = extract_datetime("azekka 15:30", "kab", anchorDate=ANCHOR)
        self.assertEqual(result[0].date(),
                         (ANCHOR + timedelta(days=1)).date())
        self.assertEqual((result[0].hour, result[0].minute), (15, 30))

    def test_no_date(self):
        self.assertIsNone(
            extract_datetime("azul fell-awen amek tellam", "kab",
                             anchorDate=ANCHOR))

class TestExtractDatetimeSpokenTimeKab(unittest.TestCase):
    """A lone spoken hour takes the next twelve-hour reading after the
    13:04 anchor (ruling 17): ten o'clock is 22:00 the same day."""

    @pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1032")
    def test_bare_hour(self):
        # a lone hour takes the next twelve-hour reading (ruling 17): one
        # o'clock said at 13:04 is 01:00 the next day
        result = extract_datetime("d lweḥda", "kab", anchorDate=ANCHOR)
        self.assertEqual(result[0], datetime(2017, 6, 28, 1, 0))

    def test_exact_hour(self):
        result = extract_datetime("d lɛecṛa swaswa", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (22, 0))

    def test_quarter_past(self):
        result = extract_datetime("d lɛecṛa u ṛbeɛ", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (22, 15))


    def test_minus_minutes(self):
        result = extract_datetime("d lɛecṛa ɣiṛ xemsa", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (21, 55))

    def test_quarter_to(self):
        result = extract_datetime("d lɛecṛa ɣiṛ ṛbeɛ", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (21, 45))

    @pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1032")
    def test_day_period_disambiguation(self):
        # "d juǧ" alone stays 12h (2:00); a period word resolves to 24h
        result = extract_datetime("d juǧ n uzal", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (14, 0))

    def test_a_period_word_without_its_epenthetic_vowel(self):
        # "tmeddit" (no epenthetic vowel) must resolve the same as
        # "tameddit"
        result = extract_datetime("d lxemsa n tmeddit", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (17, 0))

    def test_regional_two_oclock(self):
        # Soummam valley "ssaɛtin" as an alternative to "juǧ" for "two"
        result = extract_datetime("d ssaɛtin ɣiṛ xemsa", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (13, 55))


    def test_sun_letter_article(self):
        # the fused article assimilates to "tt" before "t" (ttnac =
        # article + tnac "12"), as opposed to the plain "l-" in
        # test_day_period_disambiguation's "lxemsa"/"lɛecṛa"
        result = extract_datetime("d ttnac n uzal", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (12, 0))


OFFSET_ANCHOR = datetime(2026, 9, 23, 8, 5)


class TestKabRelativeOffsets(unittest.TestCase):
    """T-4196: a duration alone is an offset from the anchor.

    ``extract_duration`` read these phrases correctly and
    ``extract_datetime`` threw the answer away and returned ``None``, so
    every Kabyle relative-offset phrase read as no date at all. English,
    German and Portuguese all answer the anchor plus the duration, for
    the marked form and for the bare one.
    """

    @pytest.mark.xfail(strict=True,
                       reason="https://github.com/TigreGotico/chronologia/issues/992")
    def test_a_marked_offset_answers_the_anchor_plus_the_duration(self):
        result = extract_datetime("mbaed 10 n wesrag", "kab",
                                  anchorDate=OFFSET_ANCHOR)
        self.assertIsNotNone(result, "read as no date")
        self.assertEqual(result[0], OFFSET_ANCHOR + timedelta(hours=10))
        # The direction word belongs to the date, as fr "dans" does in
        # "dans 3 heures", so nothing is left over.
        self.assertEqual(result[1], "")

    def test_a_bare_duration_is_not_a_date(self):
        # ruling 3: a bare length with no direction word is not a date
        self.assertIsNone(extract_datetime(
            "melmi ara tili ma rgig 10 n tesdidin", "kab",
            anchorDate=OFFSET_ANCHOR))
        self.assertIsNone(extract_datetime("10 n tesdidin", "kab",
                                           anchorDate=OFFSET_ANCHOR))

    @pytest.mark.xfail(strict=True,
                       reason="https://github.com/TigreGotico/chronologia/issues/992")
    def test_a_compound_cardinal_is_not_split_by_a_clock_hour(self):
        """"mraw d yiwen" is eleven, and extract_duration reads "mraw d
        yiwen n tesdidin" as 660 seconds. Reading "d yiwen" as the
        presentative "it is one o'clock" splits the compound. The phrase
        is a bare length, so it names no date (ruling 3).
        """
        self.assertIsNone(extract_datetime("mraw d yiwen n tesdidin", "kab",
                                           anchorDate=OFFSET_ANCHOR))

    def test_the_duration_layer_already_read_these(self):
        """The measurement that located the defect: the duration was
        always available, so the gap was the datetime branch alone."""
        for phrase, seconds in (("mbaed 10 n wesrag", 36000),
                                ("10 n tesdidin", 600)):
            with self.subTest(phrase=phrase):
                self.assertEqual(extract_duration(phrase, "kab")[0],
                                 timedelta(seconds=seconds))

    def test_a_clock_time_still_wins_over_an_offset(self):
        """The control. The offset branch runs only where the function
        answered ``None``, so a phrase that names a clock time keeps the
        clock time and is not shifted from the anchor."""
        result = extract_datetime("d ttnac n uzal", "kab",
                                  anchorDate=OFFSET_ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (12, 0))

    def test_a_relative_day_still_wins_over_an_offset(self):
        result = extract_datetime("azekka", "kab", anchorDate=OFFSET_ANCHOR)
        self.assertEqual(result[0].date(),
                         (OFFSET_ANCHOR + timedelta(days=1)).date())


class TestKabBareUnitIsNotOne(unittest.TestCase):
    """T-4196: a unit noun with no quantity is not a duration.

    The loop defaulted a missing quantity to 1, so the question "acdal
    ara tili ssaɛa" ("what time will it be") read as one hour, and a
    phrase that also carried a real quantity got the spurious hour added
    to it. A wrong duration is worse than none: the skill read that
    phrasing as a place.
    """

    def test_a_bare_unit_is_not_a_duration(self):
        for phrase in ("ssaɛa", "asrag", "acdal ara tili ssaɛa"):
            with self.subTest(phrase=phrase):
                self.assertIsNone(extract_duration(phrase, "kab")[0],
                                  msg=f"{phrase!r} read as a duration")

    def test_the_bare_unit_does_not_inflate_a_real_quantity(self):
        """The case from the skill: ten minutes, not ten minutes plus an
        hour."""
        value, remainder = extract_duration(
            "deg 10 n tesdidin acdal ara tili ssaɛa", "kab")
        self.assertEqual(value, timedelta(minutes=10))
        self.assertIn("ssaɛa", remainder,
                      "the unread unit belongs in the remainder")

    def test_a_quantity_before_the_unit_still_reads(self):
        """The control that the fix did not simply stop reading hours."""
        for phrase in ("1 ssaɛa", "yiwet n ssaɛa"):
            with self.subTest(phrase=phrase):
                self.assertEqual(extract_duration(phrase, "kab")[0],
                                 timedelta(hours=1))
        self.assertEqual(extract_duration("sin wussan", "kab")[0],
                         timedelta(days=2))
        self.assertEqual(extract_duration("10 n tesdidin", "kab")[0],
                         timedelta(minutes=10))


if __name__ == "__main__":
    unittest.main()


class TestKabWordsBeforeTheQuantity(unittest.TestCase):
    """The words before the quantity stay in the remainder."""

    def test_the_words_before_the_quantity_survive(self):
        for phrase, seconds, rest in (
                ("mbaed 10 n wesrag", 36000, "mbaed"),
                ("melmi ara tili ma rgig 10 n tesdidin", 600,
                 "melmi ara tili ma rgig"),
                ("sekker tanafa n 10 n tesdidin", 600, "sekker tanafa n")):
            with self.subTest(phrase=phrase):
                duration, remainder = extract_duration(phrase, "kab")
                self.assertEqual(duration, timedelta(seconds=seconds))
                self.assertEqual(remainder, rest)


KAB_SPOKEN_CLOCK = pytest.mark.xfail(
    strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1032")


# A lone hour takes the next twelve-hour reading after the anchor (ruling
# 17): half past ten said at 13:04 is 22:30 on the anchor day. The four
# spellings are amazigh, old borrowing, assimil and contemporary.
@pytest.mark.parametrize("word", [
    pytest.param("neṣṣ", marks=KAB_SPOKEN_CLOCK),
    "azgen",
    pytest.param("nofc", marks=KAB_SPOKEN_CLOCK),
    pytest.param("nefs", marks=KAB_SPOKEN_CLOCK),
])
def test_half_past_spellings(word):
    result = extract_datetime(f"d lɛecṛa u {word}", "kab", anchorDate=ANCHOR)
    assert result[0] == datetime(2017, 6, 27, 22, 30)


# "u wac" and bare "ɣiṛ" are indeterminate in the source grammar; the
# reading takes ten minutes either side of the hour, and the lone hour
# takes the next twelve-hour reading (ruling 17).
@pytest.mark.parametrize("phrase,expected", [
    ("d lɛecṛa u wac", datetime(2017, 6, 27, 22, 10)),
    ("d lɛecṛa ɣiṛ", datetime(2017, 6, 27, 21, 50)),
])
@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1032")
def test_vague_approximations(phrase, expected):
    assert extract_datetime(phrase, "kab", anchorDate=ANCHOR)[0] == expected


# Midnight said at 13:04 is the coming midnight.
@pytest.mark.parametrize("phrase", [
    pytest.param("nṣaf n yiḍ", marks=pytest.mark.xfail(
        strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1032")),
    pytest.param("ttnaṣfa n yiḍ", marks=pytest.mark.xfail(
        strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1032")),
    "d ttnac n yiḍ",
])
def test_midnight_phrases(phrase):
    result = extract_datetime(phrase, "kab", anchorDate=ANCHOR)
    assert result[0] == datetime(2017, 6, 28, 0, 0)
