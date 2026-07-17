"""Natural-sentence tests for West Frisian (fy) date and time formatting.

These exercise the formatters the way a skill actually uses them: composed
into full Frisian sentences with surrounding words, punctuation and casing,
and across the whole wrap-around clock, rather than isolated anchors.

Every expected string is built only from reference-verified Frisian forms:
- weekdays/months: Wikivoyage West Frisian phrasebook; Wikipedia
    "West Frisian language".
- clock (look-ahead system, hour word "oere", inflected hours after
    healwei/kertier/oer/foar): "Telling Time in West Frisian"
    (funwithfrisian.blogspot.com), cross-checked with the phrasebook.
- parts of day: Taalportaal; phrasebook (moarns/middeis/jûns/nachts).
- carrier words: "It is" (it is), "hjoed" (today), "om" (at) — attested
    Frisian, used to place the verified date/time inside a real sentence.
"""
import unittest
from datetime import datetime

from ovos_date_parser import (
    nice_date, nice_weekday, nice_month, nice_year, nice_day,
    nice_time, nice_date_time,
)

# 2018-06-04 is a Monday -> whole week 2018-06-04 .. 2018-06-10
WEEK = {
    "Moandei": datetime(2018, 6, 4),
    "Tiisdei": datetime(2018, 6, 5),
    "Woansdei": datetime(2018, 6, 6),
    "Tongersdei": datetime(2018, 6, 7),
    "Freed": datetime(2018, 6, 8),
    "Sneon": datetime(2018, 6, 9),
    "Snein": datetime(2018, 6, 10),
}
MONTHS = {
    "Jannewaris": 1, "Febrewaris": 2, "Maart": 3, "April": 4,
    "Maaie": 5, "Juny": 6, "July": 7, "Augustus": 8,
    "Septimber": 9, "Oktober": 10, "Novimber": 11, "Desimber": 12,
}


class TestFrisianWeekdaySentences(unittest.TestCase):

    def test_each_weekday_in_sentence(self):
        for name, dt in WEEK.items():
            sentence = f"Hjoed is it {nice_weekday(dt, 'fy')}."
            self.assertEqual(sentence, f"Hjoed is it {name}.")

    def test_weekday_lowercased_mid_sentence(self):
        dt = WEEK["Woansdei"]
        sentence = f"Wy sjogge inoar oankommende {nice_weekday(dt, 'fy').lower()}."
        self.assertEqual(sentence, "Wy sjogge inoar oankommende woansdei.")


class TestFrisianDateSentences(unittest.TestCase):

    def test_full_date_germanic_order(self):
        sentence = f"De gearkomste is op {nice_date(WEEK['Tiisdei'], 'fy')}."
        self.assertEqual(
            sentence,
            "De gearkomste is op Tiisdei fiif Juny twatûzenachttjin.")

    def test_date_without_weekday(self):
        dt = datetime(2019, 1, 1)
        sentence = f"Hy is berne op {nice_date(dt, 'fy', include_weekday=False)}."
        # nice_date capitalizes the month name
        self.assertEqual(sentence, "Hy is berne op ien Jannewaris twatûzennjoggentjin.")

    def test_every_month_in_sentence(self):
        for name, m in MONTHS.items():
            dt = datetime(2019, m, 10)
            clause = nice_date(dt, "fy", include_weekday=False)
            sentence = f"It barde yn {clause}."
            self.assertIn(name, sentence)  # month capitalized by nice_date

    def test_relative_same_month_shortens(self):
        now = datetime(2018, 6, 1)
        dt = datetime(2018, 6, 5)
        sentence = f"It is op {nice_date(dt, 'fy', now=now)}."
        self.assertEqual(sentence, "It is op Tiisdei fiif.")


class TestFrisianClockSentences(unittest.TestCase):
    """Full spoken times inside sentences, across the wrap-around clock."""

    def test_oclock(self):
        sentence = f"De trein giet om {nice_time(datetime(2018, 6, 5, 4, 0), 'fy')}."
        self.assertEqual(sentence, "De trein giet om fjouwer oere.")

    def test_quarter_past(self):
        sentence = f"It is no {nice_time(datetime(2018, 6, 5, 4, 15), 'fy')}."
        self.assertEqual(sentence, "It is no kertier oer fjouweren.")

    def test_half_past_looks_ahead(self):
        # 4:30 == 'healwei fiven' (halfway to five)
        sentence = f"Wy ite om {nice_time(datetime(2018, 6, 5, 4, 30), 'fy')}."
        self.assertEqual(sentence, "Wy ite om healwei fiven.")

    def test_quarter_to(self):
        sentence = f"De winkel slút om {nice_time(datetime(2018, 6, 5, 4, 45), 'fy')}."
        self.assertEqual(sentence, "De winkel slút om kertier foar fiven.")

    def test_wrap_around_before_midnight(self):
        # 23:45 -> 'kertier foar tolven' (quarter to twelve)
        sentence = f"It fjoerwurk begjint om {nice_time(datetime(2018, 12, 31, 23, 45), 'fy')}."
        self.assertEqual(sentence, "It fjoerwurk begjint om kertier foar tolven.")

    def test_wrap_around_after_midnight(self):
        # 00:30 -> 'healwei ienen' (halfway to one)
        sentence = f"Ik gong om {nice_time(datetime(2018, 6, 6, 0, 30), 'fy')} nei bêd."
        self.assertEqual(sentence, "Ik gong om healwei ienen nei bêd.")

    def test_noon_and_midnight_both_tolve_oere(self):
        self.assertEqual(nice_time(datetime(2018, 6, 5, 12, 0), "fy"), "tolve oere")
        self.assertEqual(nice_time(datetime(2018, 6, 5, 0, 0), "fy"), "tolve oere")

    def test_minutes_past_and_to(self):
        self.assertEqual(
            f"om {nice_time(datetime(2018, 6, 5, 4, 20), 'fy')}",
            "om tweintich oer fjouweren")
        self.assertEqual(
            f"om {nice_time(datetime(2018, 6, 5, 13, 50), 'fy')}",
            "om tsien foar twaen")

    def test_24hour_in_sentence(self):
        sentence = f"Fertrek: {nice_time(datetime(2018, 6, 5, 16, 15), 'fy', use_24hour=True)} oere lokaal."
        self.assertEqual(sentence, "Fertrek: sechstjin oere fyftjin oere lokaal.")

    def test_part_of_day_ampm(self):
        # 9:30 in the morning -> healwei tsienen moarns
        sentence = f"Wy moetsje {nice_time(datetime(2018, 6, 5, 9, 30), 'fy', use_ampm=True)}."
        self.assertEqual(sentence, "Wy moetsje healwei tsienen moarns.")

    def test_evening_part_of_day(self):
        sentence = nice_time(datetime(2018, 6, 5, 20, 0), "fy", use_ampm=True)
        self.assertEqual(sentence, "acht oere jûns")


class TestFrisianDateTimeSentences(unittest.TestCase):

    def test_full_datetime_with_om(self):
        dt = datetime(2018, 6, 5, 16, 30)
        sentence = f"Set in wekker foar {nice_date_time(dt, 'fy')}."
        self.assertEqual(
            sentence,
            "Set in wekker foar Tiisdei fiif Juny twatûzenachttjin om healwei fiven.")


class TestFrisianEdgeCasesInContext(unittest.TestCase):

    def test_leap_day_sentence(self):
        dt = datetime(2020, 2, 29)
        sentence = f"De {nice_day(dt, 'fy')} komt ien kear yn 'e fjouwer jier."
        self.assertEqual(
            sentence, "De 29 Febrewaris komt ien kear yn 'e fjouwer jier.")

    def test_bc_year_in_sentence(self):
        dt = datetime(44, 3, 15)
        sentence = f"Dat wie yn {nice_year(dt, 'fy', bc=True)}."
        self.assertIn(" f.Kr.", sentence)

    def test_lang_code_variants_route(self):
        for code in ("fy", "fy-NL", "FY", "FY-nl", "fy-nl"):
            self.assertEqual(nice_weekday(datetime(2018, 6, 5), code), "Tiisdei")

    def test_casing_upper_and_strip(self):
        dt = datetime(2018, 6, 5, 4, 30)
        loud = f"  it is {nice_time(dt, 'fy')}!  ".strip().upper()
        self.assertEqual(loud, "IT IS HEALWEI FIVEN!")

    def test_malformed_input_raises(self):
        for bad in (None, "healwei fiven", 20180605, [], {}, 3.14):
            with self.assertRaises((AttributeError, TypeError, KeyError)):
                nice_time(bad, "fy")

    def test_speech_false_is_language_neutral(self):
        self.assertEqual(nice_time(datetime(2018, 6, 5, 16, 5), "fy",
                                   speech=False, use_24hour=True), "16:05")

    def test_cross_language_uses_frisian_not_dutch(self):
        # Frisian-specific spellings, never the Dutch or English neighbours
        self.assertEqual(nice_weekday(WEEK["Woansdei"], "fy"), "Woansdei")
        self.assertNotEqual(nice_weekday(WEEK["Woansdei"], "fy"), "Woensdag")   # nl
        self.assertNotEqual(nice_weekday(WEEK["Woansdei"], "fy"), "Wednesday")  # en
        self.assertEqual(nice_month(datetime(2019, 6, 1), "fy"), "Juny")
        self.assertNotEqual(nice_month(datetime(2019, 6, 1), "fy"), "Juni")     # nl
        # look-ahead half is Frisian 'healwei', not Dutch 'half'
        half = nice_time(datetime(2018, 6, 5, 4, 30), "fy")
        self.assertTrue(half.startswith("healwei"))
        self.assertNotIn("half", half)

    def test_full_wrap_around_clock_sweep(self):
        # every wall-clock minute yields a non-empty spoken form anchored on a
        # Frisian time particle; no crashes across the 24h wrap-around
        for hour in range(24):
            for minute in range(60):
                spoken = nice_time(datetime(2018, 6, 5, hour, minute), "fy")
                self.assertTrue(spoken)
                self.assertTrue(
                    "oere" in spoken or " oer " in spoken
                    or "foar" in spoken or "healwei" in spoken,
                    f"{hour}:{minute:02d} -> {spoken}")


if __name__ == "__main__":
    unittest.main()
