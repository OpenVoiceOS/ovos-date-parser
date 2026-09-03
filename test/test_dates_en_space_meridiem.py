"""Space-separated ``H MM <meridiem>`` clock forms.

Regression coverage for the case where hour and minute are given as two
plain digit groups separated by whitespace ("11 55 pm") instead of a colon
("11:55 pm"), including the equivalent all-word phrasing ("eleven fifty
five pm"). Before the fix, this branch was misclassified as military time:
the hour was taken literally with no 12->24h conversion and the trailing
am/pm token was left unconsumed in the remainder.
"""
import unittest
from datetime import datetime, time

from ovos_date_parser import extract_time_en

ANCHOR = datetime(2017, 6, 27, 13, 4)

WORD_HOURS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve",
}
WORD_MINUTES = {
    0: "zero zero", 5: "five", 15: "fifteen", 30: "thirty", 45: "forty five",
    55: "fifty five",
}


class TestIssue310Table(unittest.TestCase):
    """The exact rows reported in issue #310."""

    def test_eleven_fifty_five_pm_digits(self):
        self.assertEqual(extract_time_en("at 11 55 pm", ANCHOR),
                         (time(23, 55), ""))

    def test_eleven_fifty_five_pm_words(self):
        self.assertEqual(extract_time_en("at eleven fifty five pm", ANCHOR),
                         (time(23, 55), ""))

    def test_twelve_oh_five_am(self):
        self.assertEqual(extract_time_en("at 12 05 am", ANCHOR),
                         (time(0, 5), ""))

    def test_one_fifteen_pm(self):
        self.assertEqual(extract_time_en("at 1 15 pm", ANCHOR),
                         (time(13, 15), ""))

    def test_colon_forms_unaffected(self):
        # already-correct colon forms must keep working identically
        self.assertEqual(extract_time_en("at 11:55 pm", ANCHOR),
                         (time(23, 55), ""))

    def test_bare_hour_forms_unaffected(self):
        # already-correct bare-hour forms must keep working identically
        self.assertEqual(extract_time_en("at 11 pm", ANCHOR),
                         (time(23, 0), ""))


class TestBoundaryNoonMidnight(unittest.TestCase):
    """12 is the boundary hour: 12h -> 0h for am, stays 12h for pm."""

    def test_twelve_zero_zero_am_is_midnight(self):
        self.assertEqual(extract_time_en("at 12 00 am", ANCHOR),
                         (time(0, 0), ""))

    def test_twelve_zero_zero_pm_is_noon(self):
        self.assertEqual(extract_time_en("at 12 00 pm", ANCHOR),
                         (time(12, 0), ""))

    def test_matches_colon_midnight_semantics(self):
        # space-separated form must mirror the colon form exactly
        self.assertEqual(extract_time_en("at 12 00 am", ANCHOR),
                         extract_time_en("at 12:00 am", ANCHOR))
        self.assertEqual(extract_time_en("at 12 00 pm", ANCHOR),
                         extract_time_en("at 12:00 pm", ANCHOR))


class TestShapeSweep(unittest.TestCase):
    """Hours 1-12, both meridiems, digit and word-number phrasing.

    Each case is cross-checked against the equivalent colon form, which was
    already correct before the fix.
    """

    def test_digit_hour_minute_sweep(self):
        for hour in range(1, 13):
            for meridiem, offset in (("am", 0), ("pm", 12)):
                expected_hour = hour % 12 + (offset if meridiem == "pm" else 0)
                phrase = f"at {hour} 30 {meridiem}"
                colon = f"at {hour}:30 {meridiem}"
                expected = (time(expected_hour, 30), "")
                self.assertEqual(extract_time_en(phrase, ANCHOR), expected,
                                 msg=phrase)
                self.assertEqual(extract_time_en(phrase, ANCHOR),
                                 extract_time_en(colon, ANCHOR), msg=phrase)

    def test_word_hour_minute_sweep(self):
        for hour in range(1, 13):
            for meridiem, offset in (("am", 0), ("pm", 12)):
                expected_hour = hour % 12 + (offset if meridiem == "pm" else 0)
                phrase = f"at {WORD_HOURS[hour]} thirty {meridiem}"
                expected = (time(expected_hour, 30), "")
                self.assertEqual(extract_time_en(phrase, ANCHOR), expected,
                                 msg=phrase)


class TestRemainderConsumed(unittest.TestCase):
    """The meridiem token must be consumed, never left dangling."""

    def test_no_dangling_meridiem_digit(self):
        result = extract_time_en("wake me at 11 55 pm", ANCHOR)
        self.assertEqual(result, (time(23, 55), "wake me"))
        self.assertNotIn("pm", result[1])

    def test_no_dangling_meridiem_words(self):
        result = extract_time_en("wake me at eleven fifty five pm", ANCHOR)
        self.assertEqual(result, (time(23, 55), "wake me"))
        self.assertNotIn("pm", result[1])

    def test_no_dangling_meridiem_am(self):
        result = extract_time_en("wake me at 12 05 am", ANCHOR)
        self.assertEqual(result, (time(0, 5), "wake me"))
        self.assertNotIn("am", result[1])


class TestMilitaryTimeStillWorks(unittest.TestCase):
    """The military-time branch this fix shares code with must be untouched."""

    def test_military_hours_still_parsed(self):
        self.assertEqual(extract_time_en("at 04 38 hours", ANCHOR),
                         (time(4, 38), ""))

    def test_bare_military_digits_still_parsed(self):
        self.assertEqual(extract_time_en("at 22 15 hours", ANCHOR),
                         (time(22, 15), ""))
