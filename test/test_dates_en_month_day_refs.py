"""English day-of-month references: spelled ordinals before "of <month>",
"the first of the month" and "the last day of the month".

Anchor: Saturday 2026-10-17 12:00 Europe/Lisbon.  Every expected date is
worked out by hand from that anchor: a month-name date that has passed rolls
to next year, a day-of-month that has passed rolls to next month, and "last
day of <month>" is the calendar's final day.
"""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from ovos_date_parser import extract_datetime

TZ = ZoneInfo("Europe/Lisbon")
ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=TZ)


def parse(text, anchor=ANCHOR):
    return extract_datetime(text, anchorDate=anchor, lang="en-US")


def at(y, m, d, hour=0):
    return datetime(y, m, d, hour, 0, tzinfo=TZ)


class TestSpelledOrdinalOfMonth(unittest.TestCase):
    def test_the_fourth_of_july(self):
        self.assertEqual(parse("the fourth of july")[0], at(2027, 7, 4))

    def test_on_the_fourth_of_july(self):
        self.assertEqual(parse("on the fourth of july")[0], at(2027, 7, 4))

    def test_without_article(self):
        self.assertEqual(parse("fourth of july")[0], at(2027, 7, 4))

    def test_compound_ordinal(self):
        self.assertEqual(parse("the twenty-first of march")[0], at(2027, 3, 21))
        self.assertEqual(parse("the twenty first of march")[0], at(2027, 3, 21))

    def test_first_to_thirty_first(self):
        self.assertEqual(parse("the thirty-first of october")[0], at(2026, 10, 31))
        self.assertEqual(parse("the first of november")[0], at(2026, 11, 1))
        self.assertEqual(parse("the second of may")[0], at(2027, 5, 2))
        self.assertEqual(parse("the twentieth of december")[0], at(2026, 12, 20))

    def test_inside_a_sentence(self):
        d, rest = parse("what is the date on the fourth of july")
        self.assertEqual(d, at(2027, 7, 4))
        self.assertEqual(rest, "what is date")

    def test_with_time(self):
        self.assertEqual(parse("the third of june at noon")[0], at(2027, 6, 3, 12))

    def test_capitalised(self):
        self.assertEqual(parse("The Fourth of July")[0], at(2027, 7, 4))

    def test_remainder_is_empty(self):
        self.assertEqual(parse("the fourth of july")[1], "")


class TestFirstOfTheMonth(unittest.TestCase):
    def test_first_of_the_month(self):
        d, rest = parse("the first of the month")
        self.assertEqual(d, at(2026, 11, 1))
        self.assertEqual(rest, "")

    def test_digit_form(self):
        self.assertEqual(parse("the 1st of the month")[0], at(2026, 11, 1))

    def test_without_article(self):
        self.assertEqual(parse("first of the month")[0], at(2026, 11, 1))

    def test_first_of_next_month(self):
        d, rest = parse("the first of next month")
        self.assertEqual(d, at(2026, 11, 1))
        self.assertEqual(rest, "")

    def test_first_of_this_month_is_in_the_past(self):
        self.assertEqual(parse("the first of this month")[0], at(2026, 10, 1))

    def test_inside_a_sentence(self):
        d, rest = parse("pay the rent on the first of the month")
        self.assertEqual(d, at(2026, 11, 1))
        self.assertEqual(rest, "pay rent")

    def test_day_still_ahead_stays_in_this_month(self):
        self.assertEqual(parse("the twentieth of the month")[0], at(2026, 10, 20))

    def test_day_already_passed_rolls_to_next_month(self):
        self.assertEqual(parse("the 5th of the month")[0], at(2026, 11, 5))

    def test_rolls_over_the_year_end(self):
        anchor = datetime(2026, 12, 15, 9, 0, tzinfo=TZ)
        self.assertEqual(parse("the first of the month", anchor)[0], at(2027, 1, 1))

    def test_skips_a_month_that_lacks_the_day(self):
        anchor = datetime(2026, 11, 5, 9, 0, tzinfo=TZ)
        self.assertEqual(parse("the thirty-first of the month", anchor)[0],
                         at(2026, 12, 31))


class TestLastDayOfMonth(unittest.TestCase):
    def test_last_day_of_the_month(self):
        d, rest = parse("the last day of the month")
        self.assertEqual(d, at(2026, 10, 31))
        self.assertEqual(rest, "")

    def test_without_article(self):
        self.assertEqual(parse("last day of the month")[0], at(2026, 10, 31))

    def test_this_month(self):
        self.assertEqual(parse("the last day of this month")[0], at(2026, 10, 31))

    def test_of_february(self):
        self.assertEqual(parse("the last day of february")[0], at(2027, 2, 28))

    def test_of_a_leap_february(self):
        anchor = datetime(2027, 10, 17, 12, 0, tzinfo=TZ)
        self.assertEqual(parse("the last day of february", anchor)[0],
                         at(2028, 2, 29))

    def test_of_the_current_month_name(self):
        self.assertEqual(parse("the last day of october")[0], at(2026, 10, 31))

    def test_of_next_month(self):
        self.assertEqual(parse("the last day of next month")[0], at(2026, 11, 30))

    def test_of_next_month_from_january(self):
        anchor = datetime(2026, 1, 31, 12, 0, tzinfo=TZ)
        self.assertEqual(parse("the last day of next month", anchor)[0],
                         at(2026, 2, 28))

    def test_inside_a_sentence(self):
        d, rest = parse("the report is due on the last day of the month")
        self.assertEqual(d, at(2026, 10, 31))
        self.assertEqual(rest, "the report is due")


class TestMonthThenSpelledOrdinal(unittest.TestCase):
    def test_july_fourth(self):
        d, rest = parse("july fourth")
        self.assertEqual(d, at(2027, 7, 4))
        self.assertEqual(rest, "")

    def test_on_july_fourth(self):
        self.assertEqual(parse("on july fourth")[0], at(2027, 7, 4))

    def test_compound_ordinal(self):
        self.assertEqual(parse("march twenty-first")[0], at(2027, 3, 21))

    def test_with_article(self):
        self.assertEqual(parse("july the fourth")[0], at(2027, 7, 4))

    def test_with_year(self):
        self.assertEqual(parse("november fifth 1955")[0], at(1955, 11, 5))

    def test_inside_a_sentence(self):
        d, rest = parse("the party is on july second")
        self.assertEqual(d, at(2027, 7, 2))
        self.assertEqual(rest, "the party is")

    def test_month_alone_keeps_its_first_day(self):
        self.assertEqual(parse("july")[0], at(2027, 7, 1))

    def test_modal_may_is_not_read_as_a_day(self):
        self.assertEqual(parse("it may be late")[0], at(2026, 10, 17))


class TestLastDayOfMonthWithYear(unittest.TestCase):
    def test_leap_february(self):
        d, rest = parse("the last day of february 2028")
        self.assertEqual(d, at(2028, 2, 29))
        self.assertEqual(rest, "")

    def test_common_february(self):
        self.assertEqual(parse("the last day of february 2027")[0], at(2027, 2, 28))

    def test_year_in_the_past(self):
        self.assertEqual(parse("the last day of february 2026")[0], at(2026, 2, 28))


class TestOrdinarySpeechIsNotADate(unittest.TestCase):
    """Sentences with "of the month" that are not dates stay unparsed."""

    def test_fractions_of_the_month(self):
        for text in ("a third of the month is gone",
                     "i spent a third of the month in paris",
                     "a tenth of the month",
                     "we lost a fourth of this month to rain"):
            with self.subTest(text=text):
                self.assertIsNone(parse(text))

    def test_counts_of_the_month(self):
        for text in ("one of the month's best days",
                     "i read 3 of this month's books",
                     "i read 12 of the month's articles",
                     "we won 0 of this month's matches"):
            with self.subTest(text=text):
                self.assertIsNone(parse(text))

    def test_day_zero_does_not_raise(self):
        self.assertIsNone(parse("the 0th of the month"))
        self.assertIsNone(parse("the last day of february 0000"))

    def test_adjectives_between_count_article_and_fraction(self):
        for text in ("a full third of the month",
                     "a whole fifth of the month",
                     "nearly a third of the month",
                     "about a tenth of the month",
                     "an entire fifth of the month",
                     "a solid third of the month",
                     "a fair third of the month",
                     "a clear third of the month",
                     "a complete third of the month",
                     "a large third of the month",
                     "a mere fifth of the month",
                     "an extra fifth of the month",
                     "a total third of the month",
                     "another third of the month",
                     "some third of the month",
                     "any third of the month",
                     "no third of the month",
                     "several thirds of the month",
                     "half a third of the month"):
            with self.subTest(text=text):
                self.assertIsNone(parse(text))

    def test_ordinal_or_last_before_the_fraction(self):
        for text in ("the first third of the month",
                     "the last third of the month",
                     "the final third of the month"):
            with self.subTest(text=text):
                self.assertIsNone(parse(text))

    def test_other_determiners_leave_the_date(self):
        self.assertEqual(parse("every third of the month")[0], at(2026, 11, 3))
        self.assertEqual(parse("pay a bill on the third of the month")[0],
                         at(2026, 11, 3))
        for text in ("the next third of the month", "this third of the month",
                     "that third of the month", "next third of the month",
                     "my third of the month"):
            with self.subTest(text=text):
                self.assertEqual(parse(text)[0], at(2026, 11, 3))
        self.assertEqual(parse("a big fourth of july party")[0], at(2027, 7, 4))

    def test_modal_may_is_left_as_before(self):
        # "may" after a subject is the verb; the day is not taken from it
        for text in ("it may second guess", "i may third that"):
            with self.subTest(text=text):
                self.assertEqual(parse(text)[0], at(2027, 5, 1))

    def test_may_after_a_preposition_is_the_month(self):
        self.assertEqual(parse("my birthday is on may third")[0], at(2027, 5, 3))

    def test_unfitting_day_keeps_the_original_words(self):
        # no 30th in february: the phrase is left as it was said
        anchor = datetime(2026, 1, 31, 12, 0, tzinfo=TZ)
        d, rest = parse("the thirtieth of next month", anchor)
        self.assertEqual(d, at(2026, 2, 1))
        self.assertEqual(rest, "the thirtieth")


class TestAfterAMonthDay(unittest.TestCase):
    def test_after_month_then_spelled_day(self):
        d, rest = parse("after july fourth")
        self.assertEqual(d, at(2027, 7, 4))
        self.assertEqual(rest, "after")

    def test_after_month_then_digit_day(self):
        d, rest = parse("after july 4th")
        self.assertEqual(d, at(2027, 7, 4))
        self.assertEqual(rest, "after")

    def test_after_day_then_month(self):
        d, rest = parse("after the fourth of july")
        self.assertEqual(d, at(2027, 7, 4))
        self.assertEqual(rest, "after")

    def test_from_month_then_day(self):
        d, rest = parse("from july fourth")
        self.assertEqual(d, at(2027, 7, 4))
        self.assertEqual(rest, "from")

    def test_after_a_weekday_is_untouched(self):
        self.assertEqual(parse("after monday")[0], at(2026, 10, 19))
        self.assertEqual(parse("after tomorrow")[0], at(2026, 10, 18))


class TestNeighboursKeepTheirMeaning(unittest.TestCase):
    def test_digit_ordinal_of_month(self):
        self.assertEqual(parse("4th of july")[0], at(2027, 7, 4))
        self.assertEqual(parse("the 4th of july")[0], at(2027, 7, 4))

    def test_month_then_digit_ordinal(self):
        self.assertEqual(parse("july 4th")[0], at(2027, 7, 4))

    def test_ordinal_without_month_is_not_a_date(self):
        self.assertIsNone(parse("the fourth"))
        self.assertIsNone(parse("the first"))

    def test_first_time_is_not_a_date(self):
        self.assertIsNone(parse("the first time"))

    def test_second_is_still_a_duration_word(self):
        self.assertEqual(parse("in a second")[0], datetime(2026, 10, 17, 12, 0, 1, tzinfo=TZ))

    def test_last_day_alone_is_yesterday(self):
        self.assertEqual(parse("last day")[0], at(2026, 10, 16))

    def test_last_week_of_the_month_is_untouched(self):
        self.assertEqual(parse("the last week of the month")[0], at(2026, 10, 10))

    def test_first_monday_of_the_month_is_untouched(self):
        self.assertEqual(parse("the first monday of the month")[0], at(2026, 10, 19))

    def test_relative_words(self):
        self.assertEqual(parse("tomorrow")[0], at(2026, 10, 18))
        self.assertEqual(parse("next month")[0], at(2026, 11, 1))
        self.assertEqual(parse("day after tomorrow")[0], at(2026, 10, 19))

    def test_month_name_dates(self):
        self.assertEqual(parse("the first of november")[0], at(2026, 11, 1))
        self.assertEqual(parse("november 1st")[0], at(2026, 11, 1))


if __name__ == "__main__":
    unittest.main()
