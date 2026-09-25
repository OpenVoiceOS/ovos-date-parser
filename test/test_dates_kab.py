import unittest
from datetime import datetime, timedelta

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
        self.assertEqual(extract_duration("tlatin tasint", "kab")[0],
                         timedelta(seconds=30))

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
    def test_bare_hour(self):
        result = extract_datetime("d lweḥda", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (1, 0))

    def test_exact_hour(self):
        result = extract_datetime("d lɛecṛa swaswa", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (10, 0))

    def test_quarter_past(self):
        result = extract_datetime("d lɛecṛa u ṛbeɛ", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (10, 15))

    def test_half_past_spellings(self):
        # amazigh, old borrowing, assimil, contemporary - all four accepted
        for word in ("neṣṣ", "azgen", "nofc", "nefs"):
            result = extract_datetime(f"d lɛecṛa u {word}", "kab",
                                      anchorDate=ANCHOR)
            self.assertEqual((result[0].hour, result[0].minute), (10, 30),
                             msg=f"failed for {word!r}")

    def test_minus_minutes(self):
        result = extract_datetime("d lɛecṛa ɣiṛ xemsa", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (9, 55))

    def test_quarter_to(self):
        result = extract_datetime("d lɛecṛa ɣiṛ ṛbeɛ", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (9, 45))

    def test_vague_approximations(self):
        # "u wac"/"u ci" and bare "ɣiṛ" are indeterminate in the source
        # grammar; coded as a fixed +/-10 minute offset rather than a
        # specific count
        result = extract_datetime("d lɛecṛa u wac", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (10, 10))
        result = extract_datetime("d lɛecṛa ɣiṛ", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (9, 50))

    def test_day_period_disambiguation(self):
        # "d juǧ" alone stays 12h (2:00); a period word resolves to 24h
        result = extract_datetime("d juǧ n uzal", "kab", anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (14, 0))
        # "tmeddit" (no epenthetic vowel) must resolve the same as
        # "tameddit"
        result = extract_datetime("d lxemsa n tmeddit", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (17, 0))

    def test_regional_two_oclock(self):
        # Soummam valley "ssaɛtin" as an alternative to "juǧ" for "two"
        result = extract_datetime("d ssaɛtin ɣiṛ xemsa", "kab",
                                  anchorDate=ANCHOR)
        self.assertEqual((result[0].hour, result[0].minute), (1, 55))

    def test_midnight_phrases(self):
        for phrase in ("nṣaf n yiḍ", "ttnaṣfa n yiḍ", "d ttnac n yiḍ"):
            result = extract_datetime(phrase, "kab", anchorDate=ANCHOR)
            self.assertEqual((result[0].hour, result[0].minute), (0, 0),
                             msg=f"failed for {phrase!r}")

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

    def test_a_marked_offset_answers_the_anchor_plus_the_duration(self):
        result = extract_datetime("mbaed 10 n wesrag", "kab",
                                  anchorDate=OFFSET_ANCHOR)
        self.assertIsNotNone(result, "read as no date")
        self.assertEqual(result[0], OFFSET_ANCHOR + timedelta(hours=10))
        # The second element is the contract a skill reads the rest of
        # the utterance from, so it is asserted, not ignored. The marker
        # is not part of the quantity and must survive.
        self.assertEqual(result[1], "mbaed")

    def test_an_offset_inside_a_question_is_still_an_offset(self):
        result = extract_datetime("melmi ara tili ma rgig 10 n tesdidin",
                                  "kab", anchorDate=OFFSET_ANCHOR)
        self.assertIsNotNone(result, "read as no date")
        self.assertEqual(result[0], OFFSET_ANCHOR + timedelta(minutes=10))
        self.assertEqual(result[1], "melmi ara tili ma rgig")

    def test_a_bare_duration_is_an_offset(self):
        result = extract_datetime("10 n tesdidin", "kab",
                                  anchorDate=OFFSET_ANCHOR)
        self.assertIsNotNone(result, "read as no date")
        self.assertEqual(result[0], OFFSET_ANCHOR + timedelta(minutes=10))
        # The whole phrase is the quantity here, so nothing is left.
        self.assertEqual(result[1], "")

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


class TestKabBackwardScanIsBounded(unittest.TestCase):
    """The backward scan that finds the quantity before a unit noun.

    ``extract_number_kab`` answers the number it finds inside a phrase and
    tolerates any prefix, so an unbounded scan reads the same value from
    every longer candidate and walks to the start of the line. The
    remainder then comes back with every leading word removed. The scan
    stops when a token does not change the value, and lets one token
    through when it is the connector of a spoken number and does not spell
    a number by itself. This is the rule
    ``ovos_number_parser.extract_number_spans`` uses for the same problem.
    """

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

    def test_a_spoken_number_keeps_its_connector(self):
        """The control on the stop rule. "mraw d yiwen" is eleven, and its
        "d" reads the same value as "yiwen" alone, so a stop with no
        connector allowance would answer one minute instead of eleven."""
        for phrase, seconds in (("mraw d yiwen n tesdidin", 660),
                                ("mraw d sin n tesdidin", 720),
                                ("\u025becrin d yiwen n tesdidin", 1260)):
            with self.subTest(phrase=phrase):
                self.assertEqual(extract_duration(phrase, "kab")[0],
                                 timedelta(seconds=seconds))

    def test_a_two_word_number_is_read_whole(self):
        """"sin mraw" is twelve in Kabyle, not two beside ten, and the
        longer candidate changes the value, so the scan keeps growing
        without needing its connector allowance."""
        duration, remainder = extract_duration("sin mraw n tesdidin", "kab")
        self.assertEqual(duration, timedelta(minutes=12))
        self.assertEqual(remainder, "")
