"""Regression tests for nl: "gisteren", "eergisteren" and "om N uur".

"om N uur" is a clock time; "over N uur" is a duration. Expected values are
hand-derived from the anchors, never pinned from engine output.
"""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 10, 17, 12, 0, tzinfo=ZoneInfo("Europe/Lisbon"))
MORNING = datetime(2026, 10, 17, 9, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


def _res(text, anchor=ANCHOR):
    return extract_datetime(text, lang="nl-NL", anchorDate=anchor)


def _dt(text, anchor=ANCHOR):
    res = _res(text, anchor)
    assert res is not None, "no datetime extracted from %r" % text
    return res[0].replace(tzinfo=None)


class TestYesterday(unittest.TestCase):
    def test_gisteren(self):
        self.assertEqual(_dt("gisteren"), datetime(2026, 10, 16))

    def test_eergisteren(self):
        self.assertEqual(_dt("eergisteren"), datetime(2026, 10, 15))

    def test_capitalised(self):
        self.assertEqual(_dt("Gisteren"), datetime(2026, 10, 16))

    def test_in_sentence(self):
        self.assertEqual(_dt("wat was het weer gisteren"),
                         datetime(2026, 10, 16))

    def test_with_clock_time(self):
        self.assertEqual(_dt("gisteren om 8:00"),
                         datetime(2026, 10, 16, 8))

    def test_remainder(self):
        self.assertEqual(_res("het weer van eergisteren")[1], "het weer")


class TestJoinedDayParts(unittest.TestCase):
    def test_yesterday_evening(self):
        self.assertEqual(_dt("gisteravond"), datetime(2026, 10, 16, 19))

    def test_yesterday_afternoon(self):
        self.assertEqual(_dt("gistermiddag"), datetime(2026, 10, 16, 15))

    def test_yesterday_morning(self):
        self.assertEqual(_dt("gisterochtend"), datetime(2026, 10, 16, 8))

    def test_day_before_yesterday_evening(self):
        self.assertEqual(_dt("eergisteravond"), datetime(2026, 10, 15, 19))

    def test_day_before_yesterday_afternoon(self):
        self.assertEqual(_dt("eergistermiddag"), datetime(2026, 10, 15, 15))

    def test_day_after_tomorrow_evening(self):
        self.assertEqual(_dt("overmorgenavond"), datetime(2026, 10, 19, 19))

    def test_day_after_tomorrow_morning(self):
        self.assertEqual(_dt("overmorgenochtend"), datetime(2026, 10, 19, 8))

    def test_in_sentence(self):
        self.assertEqual(_res("wat deed ik gisteravond")[0].replace(tzinfo=None),
                         datetime(2026, 10, 16, 19))


EVENING = datetime(2026, 10, 17, 21, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


class TestThisDayPart(unittest.TestCase):
    def test_this_morning(self):
        self.assertEqual(_dt("vanochtend"), datetime(2026, 10, 17, 8))

    def test_this_morning_alternative_word(self):
        self.assertEqual(_dt("vanmorgen"), datetime(2026, 10, 17, 8))

    def test_this_morning_in_sentence(self):
        self.assertEqual(_dt("wat was het weer vanmorgen"),
                         datetime(2026, 10, 17, 8))

    def test_this_morning_remainder(self):
        self.assertEqual(_res("weer vanmorgen")[1], "weer")

    def test_this_morning_from_evening(self):
        self.assertEqual(_dt("vanochtend", EVENING), datetime(2026, 10, 17, 8))

    def test_this_morning_alternative_word_from_evening(self):
        self.assertEqual(_dt("vanmorgen", EVENING), datetime(2026, 10, 17, 8))

    def test_this_afternoon_from_evening(self):
        self.assertEqual(_dt("vanmiddag", EVENING), datetime(2026, 10, 17, 15))

    def test_this_evening_from_evening(self):
        self.assertEqual(_dt("vanavond", EVENING), datetime(2026, 10, 17, 19))

    def test_this_afternoon(self):
        self.assertEqual(_dt("vanmiddag"), datetime(2026, 10, 17, 15))

    def test_tonight_is_midnight_of_today(self):
        self.assertEqual(_dt("vannacht"), datetime(2026, 10, 17, 0))


LATE = datetime(2026, 10, 17, 22, 0, tzinfo=ZoneInfo("Europe/Lisbon"))


class TestNamedPartDecidesAmPm(unittest.TestCase):
    def test_this_morning_colon(self):
        self.assertEqual(_dt("vanochtend om 9:00"), datetime(2026, 10, 17, 9))

    def test_this_morning_uur(self):
        self.assertEqual(_dt("vanochtend om 9 uur"), datetime(2026, 10, 17, 9))

    def test_this_morning_bare_hour(self):
        self.assertEqual(_dt("vanochtend om 9"), datetime(2026, 10, 17, 9))

    def test_this_morning_part_after_hour(self):
        self.assertEqual(_dt("om 9 uur vanochtend"), datetime(2026, 10, 17, 9))

    def test_this_morning_alternative_word(self):
        self.assertEqual(_dt("vanmorgen om 9:00"), datetime(2026, 10, 17, 9))

    def test_tomorrow_morning_bare_hour(self):
        self.assertEqual(_dt("morgenochtend om 9"), datetime(2026, 10, 18, 9))

    def test_tomorrow_morning_uur(self):
        self.assertEqual(_dt("morgenochtend om 9 uur"),
                         datetime(2026, 10, 18, 9))

    def test_yesterday_morning_spaced(self):
        self.assertEqual(_dt("gisteren ochtend om 9 uur"),
                         datetime(2026, 10, 16, 9))

    def test_saturday_morning(self):
        self.assertEqual(_dt("zaterdagochtend om 9"), datetime(2026, 10, 17, 9))

    def test_this_evening_after_the_hour(self):
        self.assertEqual(_dt("vanavond om 9:00", LATE),
                         datetime(2026, 10, 17, 21))

    def test_this_evening_uur_after_the_hour(self):
        self.assertEqual(_dt("vanavond om 9 uur", LATE),
                         datetime(2026, 10, 17, 21))

    def test_saturday_evening_bare_hour(self):
        self.assertEqual(_dt("zaterdagavond om 8", LATE),
                         datetime(2026, 10, 17, 20))

    def test_saturday_evening_uur(self):
        self.assertEqual(_dt("zaterdagavond om 8 uur", LATE),
                         datetime(2026, 10, 17, 20))

    def test_yesterday_evening_colon(self):
        self.assertEqual(_dt("gisteravond om 8:00", LATE),
                         datetime(2026, 10, 16, 20))

    def test_yesterday_evening_bare_hour(self):
        self.assertEqual(_dt("gisteravond om 8"), datetime(2026, 10, 16, 20))

    def test_tomorrow_evening_uur(self):
        self.assertEqual(_dt("morgenavond om 9 uur"), datetime(2026, 10, 18, 21))

    def test_this_afternoon_hour(self):
        self.assertEqual(_dt("vanmiddag om 3 uur", LATE),
                         datetime(2026, 10, 17, 15))

    def test_bare_nine_keeps_next_occurrence_rule(self):
        self.assertEqual(_dt("om 9 uur"), datetime(2026, 10, 17, 21))

    def test_bare_nine_after_the_hour_is_next_morning(self):
        self.assertEqual(_dt("om 9 uur", LATE), datetime(2026, 10, 18, 9))

    def test_bare_nine_colon_keeps_rule(self):
        self.assertEqual(_dt("om 9:00"), datetime(2026, 10, 17, 21))

    def test_twenty_one_hundred(self):
        self.assertEqual(_dt("om 21 uur"), datetime(2026, 10, 17, 21))

    def test_nine_in_the_evening_genitive(self):
        self.assertEqual(_dt("om 9 uur 's avonds"), datetime(2026, 10, 17, 21))

    def test_tomorrow_spaced_morning_unchanged(self):
        self.assertEqual(_dt("morgen ochtend om 9"), datetime(2026, 10, 18, 9))

    def test_today_nine_uur(self):
        self.assertEqual(_dt("vandaag om 9 uur"), datetime(2026, 10, 17, 21))


def _at(h, m=0):
    return datetime(2026, 10, 17, h, m, tzinfo=ZoneInfo("Europe/Lisbon"))


class TestTwentyFourHourValues(unittest.TestCase):
    def test_equal_to_anchor_colon(self):
        for h in range(13, 24):
            with self.subTest(hour=h):
                self.assertEqual(_dt("om %d:00" % h, _at(h)),
                                 datetime(2026, 10, 17, h))

    def test_equal_to_anchor_uur(self):
        for h in range(13, 24):
            with self.subTest(hour=h):
                self.assertEqual(_dt("om %d uur" % h, _at(h)),
                                 datetime(2026, 10, 17, h))

    def test_twelve_at_noon(self):
        self.assertEqual(_dt("om 12:00", _at(12)), datetime(2026, 10, 17, 12))
        self.assertEqual(_dt("om 12 uur", _at(12)), datetime(2026, 10, 17, 12))

    def test_passed_moves_to_next_day(self):
        self.assertEqual(_dt("om 21:00", _at(21, 30)),
                         datetime(2026, 10, 18, 21))
        self.assertEqual(_dt("om 21 uur", _at(21, 30)),
                         datetime(2026, 10, 18, 21))

    def test_minutes_equal_to_anchor(self):
        self.assertEqual(_dt("om 14:30", _at(14, 30)),
                         datetime(2026, 10, 17, 14, 30))

    def test_not_yet_reached_stays_today(self):
        self.assertEqual(_dt("om 14:30", _at(14)),
                         datetime(2026, 10, 17, 14, 30))

    def test_midnight_colon_is_next_midnight(self):
        self.assertEqual(_dt("om 0:00", _at(5)), datetime(2026, 10, 18))

    def test_midnight_uur_is_next_midnight(self):
        self.assertEqual(_dt("om 0 uur", _at(12)), datetime(2026, 10, 18))
        self.assertEqual(_dt("om 0 uur", _at(5)), datetime(2026, 10, 18))

    def test_midnight_at_midnight(self):
        self.assertEqual(_dt("om 0 uur", _at(0)), datetime(2026, 10, 17))

    def test_named_day_is_not_moved(self):
        self.assertEqual(_dt("vandaag om 14:00", _at(15)),
                         datetime(2026, 10, 17, 14))

    def test_twelve_hour_values_keep_their_rule(self):
        self.assertEqual(_dt("om 9:00", _at(9)), datetime(2026, 10, 17, 21))
        self.assertEqual(_dt("om 9:00", _at(21)), datetime(2026, 10, 18, 9))
        self.assertEqual(_dt("om 9 uur", _at(9)), datetime(2026, 10, 17, 21))


class TestPartOfDayStaysInItsClause(unittest.TestCase):
    def test_morning_in_earlier_clause_does_not_make_the_hour_am(self):
        self.assertEqual(
            _dt("ik ben vanochtend gaan lopen, zet een wekker om 8", _at(15)),
            datetime(2026, 10, 17, 20))

    def test_evening_in_earlier_clause_does_not_make_the_hour_pm(self):
        self.assertEqual(_dt("vanavond kan ik niet, morgen om 10"),
                         datetime(2026, 10, 18, 10))

    def test_day_in_front_of_the_hour_decides_the_date(self):
        self.assertEqual(
            _dt("ik was gisteravond moe, herinner me morgen om 7 aan de afspraak"),
            datetime(2026, 10, 18, 7))

    def test_day_in_front_of_the_hour_decides_the_date_end_of_text(self):
        self.assertEqual(_dt("ik heb gisteravond gegeten, kom morgen om 9"),
                         datetime(2026, 10, 18, 9))

    def test_hour_followed_by_words(self):
        self.assertEqual(_dt("herinner me morgen om 7 aan de afspraak"),
                         datetime(2026, 10, 18, 7))

    def test_hour_with_particle_after(self):
        self.assertEqual(_dt("ik sta om 6 op"), datetime(2026, 10, 17, 18))

    def test_greeting_is_not_a_part_of_day(self):
        self.assertEqual(_dt("goedemorgen, herinner me om 8"),
                         datetime(2026, 10, 17, 20))

    def test_evening_greeting_is_not_a_part_of_day(self):
        self.assertEqual(_dt("goedenavond, zet een wekker om 7"),
                         datetime(2026, 10, 17, 19))

    def test_afternoon_greeting_is_not_a_part_of_day(self):
        self.assertEqual(_dt("goedemiddag, zet een wekker om 3"),
                         datetime(2026, 10, 17, 15))

    def test_part_of_day_after_the_hour(self):
        self.assertEqual(_dt("zet een wekker om 8 uur vanochtend"),
                         datetime(2026, 10, 17, 8))

    def test_two_clauses_each_with_own_part(self):
        self.assertEqual(_dt("maandagochtend om 10"), datetime(2026, 10, 19, 10))


class TestOmIsNotAlwaysATime(unittest.TestCase):
    def test_reasons(self):
        self.assertIsNone(_res("om 3 redenen"))

    def test_rooms(self):
        self.assertIsNone(_res("om 2 kamers te huren"))

    def test_euro(self):
        self.assertIsNone(_res("om 5 euro"))

    def test_people(self):
        self.assertIsNone(_res("om 10 man"))

    def test_persons(self):
        self.assertIsNone(_res("om 4 personen"))

    def test_every_three_days_keeps_its_value(self):
        self.assertEqual(_dt("om de 3 dagen"), datetime(2026, 10, 20))


class TestSpokenClockForms(unittest.TestCase):
    def test_half_nine(self):
        self.assertEqual(_dt("om half 9"), datetime(2026, 10, 17, 20, 30))

    def test_half_nine_spelled(self):
        self.assertEqual(_dt("om half negen"), datetime(2026, 10, 17, 20, 30))

    def test_half_nine_tomorrow(self):
        self.assertEqual(_dt("morgen om half 9"), datetime(2026, 10, 18, 8, 30))

    def test_half_nine_this_evening(self):
        self.assertEqual(_dt("vanavond om half 9"),
                         datetime(2026, 10, 17, 20, 30))

    def test_half_three(self):
        self.assertEqual(_dt("om half 3"), datetime(2026, 10, 17, 14, 30))

    def test_half_one(self):
        self.assertEqual(_dt("om half 1"), datetime(2026, 10, 17, 12, 30))

    def test_quarter_past_eight(self):
        self.assertEqual(_dt("om kwart over 8"), datetime(2026, 10, 17, 20, 15))

    def test_quarter_to_nine(self):
        self.assertEqual(_dt("om kwart voor 9"), datetime(2026, 10, 17, 20, 45))

    def test_quarter_to_one(self):
        self.assertEqual(_dt("om kwart voor 1"), datetime(2026, 10, 17, 12, 45))

    def test_quarter_past_three_without_om(self):
        self.assertEqual(_dt("kwart over 3"), datetime(2026, 10, 17, 15, 15))

    def test_ten_past_three(self):
        self.assertEqual(_dt("om 10 over 3"), datetime(2026, 10, 17, 15, 10))

    def test_five_to_twelve(self):
        self.assertEqual(_dt("om 5 voor 12"), datetime(2026, 10, 17, 23, 55))

    def test_ten_minutes_ahead_is_a_duration(self):
        self.assertEqual(_dt("over 10 minuten"), datetime(2026, 10, 17, 12, 10))

    def test_remainder_is_empty(self):
        self.assertEqual(_res("wekker om kwart voor 9")[1], "wekker")

    def test_ten_past_half_three_spelled(self):
        self.assertEqual(_dt("om tien over half drie"),
                         datetime(2026, 10, 17, 14, 40))

    def test_ten_past_half_three_digits(self):
        self.assertEqual(_dt("om 10 over half 3"),
                         datetime(2026, 10, 17, 14, 40))

    def test_five_to_half_three_spelled(self):
        self.assertEqual(_dt("om vijf voor half drie"),
                         datetime(2026, 10, 17, 14, 25))

    def test_five_to_half_three_digits(self):
        self.assertEqual(_dt("om 5 voor half 3"),
                         datetime(2026, 10, 17, 14, 25))

    def test_ten_past_half_without_om(self):
        self.assertEqual(_dt("tien over half drie"),
                         datetime(2026, 10, 17, 14, 40))

    def test_five_to_half_four(self):
        self.assertEqual(_dt("vijf voor half vier"),
                         datetime(2026, 10, 17, 15, 25))

    def test_ten_past_three_spelled(self):
        self.assertEqual(_dt("om tien over drie"),
                         datetime(2026, 10, 17, 15, 10))

    def test_half_ten_past_remainder_is_empty(self):
        self.assertEqual(_res("wekker om tien over half drie")[1], "wekker")


class TestHoursThatDoNotExist(unittest.TestCase):
    def test_twenty_five(self):
        self.assertIsNone(_res("om 25 uur"))

    def test_twenty_four(self):
        self.assertIsNone(_res("om 24 uur"))

    def test_ninety_nine(self):
        self.assertIsNone(_res("om 99 uur"))

    def test_negative(self):
        self.assertIsNone(_res("om -3 uur"))

    def test_colon_twenty_five(self):
        self.assertIsNone(_res("om 25:00"))

    def test_colon_twenty_four(self):
        self.assertIsNone(_res("om 24:00"))

    def test_colon_thirty(self):
        self.assertIsNone(_res("om 30:00"))

    def test_minutes_over_fifty_nine(self):
        self.assertIsNone(_res("om 9:75"))

    def test_named_day_keeps_the_date_only(self):
        self.assertEqual(_dt("morgen om 25 uur"), datetime(2026, 10, 18))

    def test_named_day_with_bad_minutes_keeps_the_date_only(self):
        self.assertEqual(_dt("morgen om 9:75"), datetime(2026, 10, 18))

    def test_last_minute_of_the_day(self):
        self.assertEqual(_dt("om 23:59"), datetime(2026, 10, 17, 23, 59))

    def test_midnight_is_hour_zero(self):
        self.assertEqual(_dt("om 0:00"), datetime(2026, 10, 18))

    def test_a_duration_may_exceed_a_day(self):
        self.assertEqual(_dt("over 25 uur"), datetime(2026, 10, 18, 13))

    def test_a_duration_ago_may_exceed_a_day(self):
        self.assertEqual(_dt("25 uur geleden"), datetime(2026, 10, 16, 11))


class TestQuarterAroundHalf(unittest.TestCase):
    def test_quarter_past_half_nine(self):
        self.assertEqual(_dt("om kwart over half 9"),
                         datetime(2026, 10, 17, 20, 45))

    def test_quarter_to_half_nine(self):
        self.assertEqual(_dt("om kwart voor half 9"),
                         datetime(2026, 10, 17, 20, 15))

    def test_quarter_past_half_nine_spelled(self):
        self.assertEqual(_dt("om kwart over half negen"),
                         datetime(2026, 10, 17, 20, 45))

    def test_quarter_to_half_nine_spelled(self):
        self.assertEqual(_dt("om kwart voor half negen"),
                         datetime(2026, 10, 17, 20, 15))

    def test_quarter_past_half_without_om(self):
        self.assertEqual(_dt("kwart over half negen"),
                         datetime(2026, 10, 17, 20, 45))

    def test_quarter_to_half_without_om(self):
        self.assertEqual(_dt("kwart voor half negen"),
                         datetime(2026, 10, 17, 20, 15))

    def test_quarter_past_half_three(self):
        self.assertEqual(_dt("om kwart over half drie"),
                         datetime(2026, 10, 17, 14, 45))

    def test_remainder_is_empty(self):
        self.assertEqual(_res("wekker om kwart over half 9")[1], "wekker")

    def test_plain_quarter_past_nine(self):
        self.assertEqual(_dt("om kwart over 9"), datetime(2026, 10, 17, 21, 15))

    def test_plain_quarter_to_nine(self):
        self.assertEqual(_dt("om kwart voor 9"), datetime(2026, 10, 17, 20, 45))


class TestNumbersJoinedByOrAnd(unittest.TestCase):
    def test_eight_or_nine_people(self):
        self.assertIsNone(_res("het gaat om 8 of 9 mensen"))

    def test_eight_and_nine_children(self):
        self.assertIsNone(_res("om 8 en 9 kinderen"))

    def test_spelled_numbers_joined_by_or(self):
        self.assertIsNone(_res("om acht of negen mensen"))

    def test_eight_and_spelled_nine(self):
        self.assertIsNone(_res("om 8 en negen"))

    def test_eight_or_nine_with_a_day_gives_the_date_only(self):
        res = _res("morgen om 8 of 9 mensen")
        self.assertEqual(res[0].replace(tzinfo=None), datetime(2026, 10, 18))

    def test_three_or_four_hours_at_noon(self):
        self.assertEqual(_dt("om 3 of 4 uur"), datetime(2026, 10, 17, 16))

    def test_three_or_four_hours_in_the_morning(self):
        self.assertEqual(_dt("om 3 of 4 uur", _at(7)),
                         datetime(2026, 10, 17, 16))

    def test_three_or_four_hours_in_the_evening(self):
        self.assertEqual(_dt("om 3 of 4 uur", _at(21)),
                         datetime(2026, 10, 18, 4))

    def test_three_or_four_hours_is_the_same_as_four_hours(self):
        for hour in (7, 12, 21):
            with self.subTest(hour=hour):
                self.assertEqual(_dt("om 3 of 4 uur", _at(hour)),
                                 _dt("om 4 uur", _at(hour)))

    def test_three_or_four_hours_remainder(self):
        self.assertEqual(_res("wekker om 3 of 4 uur")[1], "wekker")

    def test_a_stray_number_does_not_move_the_day(self):
        self.assertEqual(_dt("3 mensen 4 uur"), datetime(2026, 10, 17, 16))

    def test_a_stray_number_before_minutes_does_not_move_the_day(self):
        self.assertEqual(_dt("3 of 4 minuten"), datetime(2026, 10, 17, 12, 4))

    def test_eight_or_later_keeps_the_hour(self):
        self.assertEqual(_dt("vanavond om 8 of later"),
                         datetime(2026, 10, 17, 20))

    def test_eight_or_later_with_a_day(self):
        self.assertEqual(_dt("morgen om 10 of later"),
                         datetime(2026, 10, 18, 10))

    def test_eight_and_then_home_again(self):
        self.assertEqual(_dt("om 8 en dan weer thuis"),
                         datetime(2026, 10, 17, 20))


class TestClausesAroundAnHour(unittest.TestCase):
    def test_hour_then_reason_about_the_evening(self):
        self.assertEqual(_dt("morgen om 10, want vanavond kan ik niet"),
                         datetime(2026, 10, 18, 10))

    def test_hour_then_reason_without_comma(self):
        self.assertEqual(_dt("morgen om 10 want vanavond kan ik niet"),
                         datetime(2026, 10, 18, 10))

    def test_reason_about_the_evening_then_hour(self):
        self.assertEqual(_dt("vanavond kan ik niet, morgen om 10"),
                         datetime(2026, 10, 18, 10))

    def test_hour_then_but(self):
        self.assertEqual(_dt("morgen om 10 maar vanavond kan ik niet"),
                         datetime(2026, 10, 18, 10))

    def test_hour_then_reason_remainder(self):
        self.assertEqual(_res("morgen om 10, want vanavond kan ik niet")[1],
                         "want kan ik niet")

    def test_people_after_the_hour_are_still_no_time(self):
        res = _res("morgen om 3 mensen")
        self.assertEqual(res[0].replace(tzinfo=None), datetime(2026, 10, 18))


class TestOmWithANamedDay(unittest.TestCase):
    def test_people_are_not_a_time(self):
        res = _res("het gaat morgen om 3 mensen")
        self.assertEqual(res[0].replace(tzinfo=None), datetime(2026, 10, 18))

    def test_people_without_a_day_are_not_a_time(self):
        self.assertIsNone(_res("het gaat om 3 mensen"))

    def test_particle_afterwards(self):
        self.assertEqual(_dt("ik kom morgen om 8 thuis"),
                         datetime(2026, 10, 18, 8))

    def test_back_afterwards(self):
        self.assertEqual(_dt("bel me morgen om 5 terug"),
                         datetime(2026, 10, 18, 5))

    def test_to_the_appointment(self):
        self.assertEqual(_dt("herinner me morgen om 7 aan de afspraak"),
                         datetime(2026, 10, 18, 7))

    def test_end_of_clause(self):
        self.assertEqual(_dt("herinner me morgen om 7"),
                         datetime(2026, 10, 18, 7))

    def test_time_word_afterwards(self):
        self.assertEqual(_dt("morgen om 3 uur"), datetime(2026, 10, 18, 3))

    def test_particle_without_a_day(self):
        self.assertEqual(_dt("ik kom om 8 thuis"), datetime(2026, 10, 17, 20))

    def test_back_without_a_day(self):
        self.assertEqual(_dt("bel me om 5 terug"), datetime(2026, 10, 17, 17))

    def test_weekday_afterwards(self):
        self.assertEqual(_dt("om 3 op zondag"), datetime(2026, 10, 18, 3))


class TestAgo(unittest.TestCase):
    def test_hours_ago(self):
        self.assertEqual(_dt("3 uur geleden"), datetime(2026, 10, 17, 9))

    def test_minutes_ago(self):
        self.assertEqual(_dt("10 minuten geleden"),
                         datetime(2026, 10, 17, 11, 50))

    def test_spelled_hours_ago(self):
        self.assertEqual(_dt("drie uur geleden"), datetime(2026, 10, 17, 9))

    def test_spelled_one_hour_ago(self):
        self.assertEqual(_dt("een uur geleden"), datetime(2026, 10, 17, 11))

    def test_spelled_minutes_ago(self):
        self.assertEqual(_dt("tien minuten geleden"),
                         datetime(2026, 10, 17, 11, 50))

    def test_hours_ago_remainder(self):
        self.assertEqual(_res("het begon 3 uur geleden")[1], "het begon")

    def test_days_ago(self):
        self.assertEqual(_dt("2 dagen geleden"), datetime(2026, 10, 15))

    def test_spelled_days_ago(self):
        self.assertEqual(_dt("twee dagen geleden"), datetime(2026, 10, 15))

    def test_spelled_week_ago(self):
        self.assertEqual(_dt("een week geleden"), datetime(2026, 10, 10))

    def test_digit_week_ago(self):
        self.assertEqual(_dt("1 week geleden"), datetime(2026, 10, 10))

    def test_in_hours_is_ahead(self):
        self.assertEqual(_dt("over 3 uur"), datetime(2026, 10, 17, 15))


class TestSpelledNumbers(unittest.TestCase):
    def test_ten_in_the_evening(self):
        self.assertEqual(_dt("om tien uur 's avonds"), datetime(2026, 10, 17, 22))

    def test_this_evening_ten(self):
        self.assertEqual(_dt("vanavond om tien uur"), datetime(2026, 10, 17, 22))

    def test_three_o_clock(self):
        self.assertEqual(_dt("om drie uur"), datetime(2026, 10, 17, 15))

    def test_in_three_hours(self):
        self.assertEqual(_dt("over drie uur"), datetime(2026, 10, 17, 15))

    def test_in_two_days(self):
        self.assertEqual(_dt("over twee dagen"), datetime(2026, 10, 19))

    def test_article_is_not_a_number(self):
        self.assertEqual(_res("zet een wekker morgen")[1], "zet een wekker")

    def test_digit_ten_in_the_evening(self):
        self.assertEqual(_dt("om 10 uur 's avonds"), datetime(2026, 10, 17, 22))


class TestClockHour(unittest.TestCase):
    def test_tomorrow_eight(self):
        self.assertEqual(_dt("morgen om 8 uur"), datetime(2026, 10, 18, 8))

    def test_tomorrow_eight_from_morning(self):
        self.assertEqual(_dt("morgen om 8 uur", MORNING),
                         datetime(2026, 10, 18, 8))

    def test_twenty_hundred(self):
        self.assertEqual(_dt("om 20 uur"), datetime(2026, 10, 17, 20))

    def test_fourteen_hundred(self):
        self.assertEqual(_dt("om 14 uur"), datetime(2026, 10, 17, 14))

    def test_eight_before_it_has_passed(self):
        self.assertEqual(_dt("om 8 uur", MORNING), datetime(2026, 10, 17, 20))

    def test_three_before_it_has_passed(self):
        self.assertEqual(_dt("om 3 uur", MORNING), datetime(2026, 10, 17, 15))

    def test_weekday(self):
        self.assertEqual(_dt("maandag om 8 uur"), datetime(2026, 10, 19, 8))

    def test_day_after_tomorrow(self):
        self.assertEqual(_dt("overmorgen om 8 uur"), datetime(2026, 10, 19, 8))

    def test_remainder(self):
        self.assertEqual(_res("wekker morgen om 8 uur")[1], "wekker")


class TestNeighbouringFormsUnchanged(unittest.TestCase):
    def test_overmorgen(self):
        self.assertEqual(_dt("overmorgen"), datetime(2026, 10, 19))

    def test_morgen(self):
        self.assertEqual(_dt("morgen"), datetime(2026, 10, 18))

    def test_vandaag(self):
        self.assertEqual(_dt("vandaag"), datetime(2026, 10, 17))

    def test_eight_at_noon_is_this_evening(self):
        self.assertEqual(_dt("om 8 uur"), datetime(2026, 10, 17, 20))

    def test_eight_with_colon(self):
        self.assertEqual(_dt("om 8:00"), datetime(2026, 10, 17, 20))

    def test_eight_in_the_evening(self):
        self.assertEqual(_dt("om 8 uur 's avonds"), datetime(2026, 10, 17, 20))

    def test_eight_in_the_morning(self):
        self.assertEqual(_dt("om 8 uur 's ochtends"),
                         datetime(2026, 10, 18, 8))

    def test_twenty_with_colon(self):
        self.assertEqual(_dt("om 20:00"), datetime(2026, 10, 17, 20))

    def test_in_eight_hours_is_a_duration(self):
        self.assertEqual(_dt("over 8 uur"), datetime(2026, 10, 17, 20))

    def test_in_eight_hours_from_morning(self):
        self.assertEqual(_dt("over 8 uur", MORNING), datetime(2026, 10, 17, 17))

    def test_in_two_hours(self):
        self.assertEqual(_dt("over 2 uur"), datetime(2026, 10, 17, 14))

    def test_binnen_three_hours(self):
        self.assertEqual(_dt("binnen 3 uur"), datetime(2026, 10, 17, 15))

    def test_tomorrow_evening(self):
        self.assertEqual(_dt("morgenavond"), datetime(2026, 10, 18, 19))

    def test_tomorrow_morning(self):
        self.assertEqual(_dt("morgenochtend"), datetime(2026, 10, 18, 8))

    def test_this_evening(self):
        self.assertEqual(_dt("vanavond"), datetime(2026, 10, 17, 19))

    def test_spaced_yesterday_evening(self):
        self.assertEqual(_dt("gisteren avond"), datetime(2026, 10, 16, 19))

    def test_yesterday_night(self):
        self.assertEqual(_dt("gisternacht"), datetime(2026, 10, 16, 0))

    def test_saturday_evening(self):
        self.assertEqual(_dt("zaterdagavond"), datetime(2026, 10, 17, 19))


if __name__ == "__main__":
    unittest.main()
