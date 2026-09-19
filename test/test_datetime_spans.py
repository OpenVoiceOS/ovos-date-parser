"""Code-point spans for date, time and duration expressions.

Phrases are reused from the per-language suites (test_dates_pt.py,
test_dates_de_sentences.py, test_multilang_invariants.py) so no new
linguistic claims are made here. Expected values are worked out from the
anchor by hand: 2026-03-11 is a Wednesday, so "friday" is 2026-03-13,
"monday" is the following 2026-03-16 and "next friday" is 2026-03-20.
"""
import unittest
from datetime import datetime, time, timedelta, timezone

from ovos_date_parser import (DateTimeSpan, DurationSpan, extract_datetime,
                              extract_datetime_spans, extract_duration,
                              extract_duration_spans)
from test.test_extract_datetime_return_shape import PHRASE_PER_LANG

UTC = timezone.utc
ANCHOR = datetime(2026, 3, 11, 10, 0, tzinfo=UTC)  # a Wednesday, mid morning


def dt(*args):
    return datetime(*args, tzinfo=UTC)


class SpanAssertions(unittest.TestCase):
    def assertDates(self, text, lang, expected, **kwargs):
        kwargs.setdefault("anchor_date", ANCHOR)
        return self._check(extract_datetime_spans(text, lang, **kwargs),
                           text, expected)

    def assertDurations(self, text, lang, expected):
        return self._check(extract_duration_spans(text, lang), text, expected)

    def _check(self, spans, text, expected):
        """Compare (surface, value) pairs and check the offset invariant."""
        self.assertEqual([(s.surface, s.value) for s in spans], expected)
        for span in spans:
            self.assertEqual(text[span.start:span.end], span.surface)
            self.assertLess(span.start, span.end)
        self.assertEqual([s.start for s in spans],
                         sorted(s.start for s in spans))
        return spans


class TestDateTimeSpansEN(SpanAssertions):
    def test_relative_date(self):
        self.assertDates("tomorrow", "en", [("tomorrow", dt(2026, 3, 12))])

    def test_date_with_time_is_one_span(self):
        self.assertDates("next friday at 5 pm", "en",
                         [("next friday at 5 pm", dt(2026, 3, 20, 17, 0))])

    def test_absolute_date_with_time(self):
        self.assertDates("meeting on march 5th 2027 at 10:30", "en",
                         [("on march 5th 2027 at 10:30", dt(2027, 3, 5, 10, 30)),
                          ("march 5th 2027 at 10:30", dt(2027, 3, 5, 10, 30))])

    def test_two_dates_in_one_utterance(self):
        self.assertDates("from monday to friday", "en",
                         [("from monday", dt(2026, 3, 16)),
                          ("monday", dt(2026, 3, 16)),
                          ("friday", dt(2026, 3, 13))])

    def test_two_times_in_one_utterance(self):
        self.assertDates("wake me at 7 and again at 9", "en",
                         [("at 7", dt(2026, 3, 11, 19, 0)),
                          ("7", dt(2026, 3, 11, 19, 0)),
                          ("at 9", dt(2026, 3, 11, 21, 0)),
                          ("9", dt(2026, 3, 11, 21, 0))])

    def test_punctuation_is_not_part_of_the_surface(self):
        self.assertDates("at 7, please", "en",
                         [("at 7", dt(2026, 3, 11, 19, 0)),
                          ("7", dt(2026, 3, 11, 19, 0))])

    def test_date_at_start_and_at_end(self):
        self.assertDates("tomorrow it rains", "en",
                         [("tomorrow", dt(2026, 3, 12))])
        self.assertDates("it rains tomorrow", "en",
                         [("tomorrow", dt(2026, 3, 12))])

    def test_offsets_are_code_points(self):
        # a byte oriented implementation reads 11 here instead of 7
        spans = self.assertDates("café ☕ tomorrow", "en",
                                 [("tomorrow", dt(2026, 3, 12))])
        self.assertEqual((spans[0].start, spans[0].end), (7, 15))

    def test_text_without_a_date(self):
        self.assertDates("hello how are you", "en", [])

    def test_candidates_do_not_overlap(self):
        # "next month" sits inside "the third of next month", and only the
        # widest coherent reading is reported. The English extractor drops
        # the day of month here and answers with the first of april, so the
        # span is the part it read - there is no second, partial span.
        self.assertDates("the third of next month", "en",
                         [("of next month", dt(2026, 4, 1)),
                          ("next month", dt(2026, 4, 1))])

    def test_surface_keeps_the_words_the_extractor_read(self):
        # the surface is the lookup key for a captured slot, so a modifier or
        # a preposition the extractor consumed belongs to it
        self.assertDates("at 5 pm", "en",
                         [("at 5 pm", dt(2026, 3, 11, 17, 0)),
                          ("5 pm", dt(2026, 3, 11, 17, 0))])
        self.assertDates("this monday", "en",
                         [("this monday", dt(2026, 3, 16)),
                          ("monday", dt(2026, 3, 16))])
        sunday = datetime(2026, 3, 8, 10, 0, tzinfo=UTC)
        self.assertDates("next friday", "en",
                         [("next friday", dt(2026, 3, 13)),
                          ("friday", dt(2026, 3, 13))],
                         anchor_date=sunday)

    def test_part_of_day_joins_the_date(self):
        self.assertDates("set an alarm for tomorrow morning", "en",
                         [("for tomorrow morning", dt(2026, 3, 12, 8, 0)),
                          ("morning", dt(2026, 3, 12, 8, 0))])

    def test_expression_longer_than_eight_words(self):
        text = "in two weeks and three days and four hours"
        spans = self.assertDates(
            text, "en", [(text, dt(2026, 3, 28, 14, 0)),
                         (text[3:], dt(2026, 3, 28, 14, 0))])
        self.assertGreater(len(spans[0].surface.split()), 8)

    def test_punctuation_inside_an_expression_is_not_a_boundary(self):
        # the extractor reads these whole, so a comma or an apostrophe
        # between two words does not end the expression
        text = "It will take about 2 hours, 30 minutes, and 10 seconds"
        self.assertDates(text, "en",
                         [("2 hours, 30 minutes, and 10 seconds",
                           dt(2026, 3, 11, 12, 30, 10))])
        self.assertDates("3 uur 's middags", "nl",
                         [("3 uur 's middags", dt(2026, 3, 11, 15, 0))])

    def test_punctuation_still_separates_two_expressions(self):
        self.assertDates("meeting tomorrow, party on saturday", "en",
                         [("tomorrow", dt(2026, 3, 12)),
                          ("on saturday", dt(2026, 3, 14)),
                          ("saturday", dt(2026, 3, 14))])

    def test_a_bridging_word_keeps_an_offset_whole(self):
        # swedish reads "8 veckor och 2 dagar" as one offset and leaves only
        # "och" behind, where "to" in "from monday to friday" ends the span
        self.assertDates("om 8 veckor och 2 dagar", "sv",
                         [("om 8 veckor och 2 dagar", dt(2026, 5, 8))])

    def test_anchor_date_is_respected(self):
        july = datetime(2026, 7, 1, 10, 0, tzinfo=UTC)  # a Wednesday
        self.assertDates("tomorrow", "en", [("tomorrow", dt(2026, 7, 2))],
                         anchor_date=july)

    def test_default_time_is_respected(self):
        self.assertDates("tomorrow", "en", [("tomorrow", dt(2026, 3, 12, 9, 30))],
                         default_time=time(9, 30))

    def test_naive_anchor_gets_the_local_zone(self):
        naive = datetime(2026, 3, 11, 10, 0)
        span = extract_datetime_spans("tomorrow", "en", anchor_date=naive)[0]
        self.assertIsNotNone(span.value.tzinfo)
        self.assertEqual(span.value.utcoffset(),
                         naive.astimezone().utcoffset())

    def test_naive_anchor_reaches_the_extractor_unchanged(self):
        # the basque extractor compares against the anchor it is given, so
        # zoning a naive anchor on the way in makes it raise
        naive = datetime(2018, 6, 1, 0, 0)
        self.assertEqual([s.value.date() for s in
                          extract_datetime_spans("11 eka", "eu", anchor_date=naive)],
                         [datetime(2018, 6, 11).date()])

    def test_a_framing_word_makes_a_second_entry(self):
        # which text the consumer holds is decided by the template that
        # captured it, so both readings are on offer
        # anchored on a sunday "next friday" and "friday" are the same day
        sunday = datetime(2026, 3, 8, 10, 0, tzinfo=UTC)
        for text, core, anchor in (("next friday", "friday", sunday),
                                   ("from monday", "monday", ANCHOR),
                                   ("at 5 pm", "5 pm", ANCHOR)):
            with self.subTest(text=text):
                spans = extract_datetime_spans(text, "en", anchor_date=anchor)
                self.assertEqual([s.surface for s in spans], [text, core])
                self.assertEqual(spans[0].value, spans[1].value)

    def test_an_expression_without_framing_is_one_entry(self):
        self.assertDates("tomorrow", "en", [("tomorrow", dt(2026, 3, 12))])

    def test_spans_are_frozen(self):
        span = extract_datetime_spans("tomorrow", "en", anchor_date=ANCHOR)[0]
        self.assertIsInstance(span, DateTimeSpan)
        with self.assertRaises(Exception):
            span.value = ANCHOR


class TestDurationSpansEN(SpanAssertions):
    def test_single_duration(self):
        self.assertDurations("set a timer for 5 minutes", "en",
                             [("5 minutes", timedelta(minutes=5))])

    def test_compound_duration_is_one_span(self):
        self.assertDurations("in two hours and thirty minutes", "en",
                             [("two hours and thirty minutes",
                               timedelta(hours=2, minutes=30))])

    def test_two_durations_do_not_add_up(self):
        # read as one expression this is ten and a half hours, a length
        # nobody said
        self.assertDurations("remind me in ten minutes and again in half an hour",
                             "en", [("ten minutes", timedelta(minutes=10)),
                                    ("half an hour", timedelta(minutes=30))])

    def test_text_without_a_duration(self):
        self.assertDurations("hello how are you", "en", [])

    def test_zero_is_a_length(self):
        # several languages report "no duration here" as a zero length, so
        # what tells a spoken zero from silence is the leftover: a spoken one
        # leaves nothing behind
        self.assertDurations("0 seconds", "en", [("0 seconds", timedelta(0))])
        self.assertDurations("set a timer for 0 minutes", "en",
                             [("0 minutes", timedelta(0))])
        self.assertDurations("0 minuten", "de", [("0 minuten", timedelta(0))])

    def test_a_unit_without_a_number_is_no_duration(self):
        self.assertDurations("ساعت", "fa", [])
        self.assertDurations("و", "fa", [])

    def test_no_duration_is_reported_as_a_pair(self):
        # every language answers with (value, remainder); a bare None cannot
        # be unpacked by a caller
        for text, lang in (("hej hur mår du", "sv"), ("سلام دنیا", "fa"),
                           ("hello how are you", "en")):
            with self.subTest(lang=lang):
                value, remainder = extract_duration(text, lang)
                self.assertIsNone(value)
                self.assertEqual(remainder, text)
        self.assertDurations("hej hur mår du", "sv", [])

    def test_duration_and_date_are_separate_span_lists(self):
        # a length of time is also a point in time relative to the anchor, so
        # "20 minutes" is reported by both scans, with its own value in each
        text = "wake me tomorrow, the nap is 20 minutes"
        self.assertDurations(text, "en", [("20 minutes", timedelta(minutes=20))])
        self.assertDates(text, "en", [("tomorrow", dt(2026, 3, 12)),
                                      ("20 minutes", dt(2026, 3, 11, 10, 20))])

    def test_spans_are_frozen(self):
        span = extract_duration_spans("5 minutes", "en")[0]
        self.assertIsInstance(span, DurationSpan)
        with self.assertRaises(Exception):
            span.value = timedelta(0)


class TestSpansPT(SpanAssertions):
    def test_relative_date(self):
        self.assertDates("amanhã", "pt", [("amanhã", dt(2026, 3, 12))])

    def test_date_with_time_is_one_span(self):
        self.assertDates("amanhã às 14:30", "pt",
                         [("amanhã às 14:30", dt(2026, 3, 12, 14, 30))])

    def test_two_dates_in_one_utterance(self):
        self.assertDates("de segunda a sexta", "pt",
                         [("de segunda", dt(2026, 3, 16)),
                          ("segunda", dt(2026, 3, 16)),
                          ("sexta", dt(2026, 3, 13))])

    def test_text_without_a_date(self):
        self.assertDates("olá como estás", "pt", [])

    def test_compound_duration_is_one_span(self):
        self.assertDurations("daqui a duas horas e trinta minutos", "pt",
                             [("duas horas e trinta minutos",
                               timedelta(hours=2, minutes=30))])

    def test_offsets_are_code_points(self):
        text = "está frio, amanhã chove"
        spans = self.assertDates(text, "pt", [("amanhã", dt(2026, 3, 12))])
        self.assertEqual((spans[0].start, spans[0].end), (11, 17))


class TestSpansDE(SpanAssertions):
    def test_relative_date(self):
        self.assertDates("morgen", "de", [("morgen", dt(2026, 3, 12))])

    def test_date_with_time_is_one_span(self):
        self.assertDates("morgen um 17 uhr", "de",
                         [("morgen um 17 uhr", dt(2026, 3, 12, 17, 0))])

    def test_two_dates_in_one_utterance(self):
        self.assertDates("von montag bis freitag", "de",
                         [("von montag", dt(2026, 3, 16)),
                          ("montag", dt(2026, 3, 16)),
                          ("bis freitag", dt(2026, 3, 13)),
                          ("freitag", dt(2026, 3, 13))])

    def test_text_without_a_date(self):
        self.assertDates("hallo wie geht es dir", "de", [])

    def test_compound_duration_is_one_span(self):
        self.assertDurations("in zwei stunden und dreißig minuten", "de",
                             [("zwei stunden und dreißig minuten",
                               timedelta(hours=2, minutes=30))])


class TestSpansFA(SpanAssertions):
    """A phrase whose words read as one value for a long stretch.

    The persian film length is one hour and fifty seven and a half minutes
    (test_parse_fa.py), and every window from "one hour" to the last word but
    one reads as one hour: only the final "minutes" moves the value. A scan
    that gives up on a run of words that do not change the value reports the
    hour and loses the minutes.
    """

    FILM = "این فیلم یک ساعت و پنجاه و هفت و نیم دقیقه طول می کشد"
    LENGTH = timedelta(hours=1, minutes=57.5)

    def test_long_unchanging_run_is_one_span(self):
        self.assertDates(self.FILM, "fa",
                         [("یک ساعت و پنجاه و هفت و نیم دقیقه",
                           ANCHOR + self.LENGTH),
                          ("ساعت و پنجاه و هفت و نیم دقیقه",
                           ANCHOR + self.LENGTH)])

    def test_duration_of_the_same_phrase(self):
        self.assertDurations(self.FILM, "fa",
                             [("یک ساعت و پنجاه و هفت و نیم دقیقه",
                               self.LENGTH)])


class TestFragments(unittest.TestCase):
    """Fragments a whole utterance never produces must not raise.

    Scanning windows hands the extractors partial phrases such as "in two
    hours and", where the conjunction is the last word, or "of april", where
    the word before the preposition is missing.
    """

    def test_month_without_a_day(self):
        self.assertIsNotNone(extract_datetime("of april", "en",
                                              anchorDate=ANCHOR))

    def test_trailing_conjunction_english(self):
        self.assertIsNotNone(extract_datetime("in two hours and", "en",
                                              anchorDate=ANCHOR))

    def test_trailing_conjunction_german(self):
        self.assertIsNotNone(extract_datetime("in zwei stunden und", "de",
                                              anchorDate=ANCHOR))

    def test_swedish_month_without_a_day_is_its_first(self):
        """A month named with no day of month means the first of it."""
        for text in ("i juni", "juni klockan 3"):
            with self.subTest(text=text):
                found = extract_datetime(text, "sv", anchorDate=ANCHOR)
                self.assertIsNotNone(found)
                self.assertEqual(found[0].date(), datetime(2026, 6, 1).date())

    def test_swedish_four_digit_number_after_a_month_is_its_year(self):
        """"juni 2027" names a year, not a day of month."""
        for text in ("juni 2027", "i juni 2027"):
            with self.subTest(text=text):
                found = extract_datetime(text, "sv", anchorDate=ANCHOR)
                self.assertIsNotNone(found)
                self.assertEqual(found[0].date(), datetime(2027, 6, 1).date())
        # a day of month still reads as one
        found = extract_datetime("15 juni 2027", "sv", anchorDate=ANCHOR)
        self.assertEqual(found[0].date(), datetime(2027, 6, 15).date())

    def test_unit_without_a_number_persian(self):
        self.assertIsNotNone(extract_datetime("ساعت", "fa", anchorDate=ANCHOR))

    def test_hyphenated_word_starting_with_a_digit(self):
        self.assertIsNone(extract_datetime("4-digit year", "en",
                                           anchorDate=ANCHOR))

    def test_impossible_leap_day_azerbaijani(self):
        """A day that does not exist in the year reports no date."""
        self.assertIsNone(extract_datetime("29 fevral", "az",
                                           anchorDate=ANCHOR))
        # the leap day itself still parses where the year has one
        found = extract_datetime("29 fevral", "az",
                                 anchorDate=datetime(2028, 1, 1, tzinfo=UTC))
        self.assertEqual(found[0].date(), datetime(2028, 2, 29).date())

    def test_clock_time_where_minutes_are_expected_azerbaijani(self):
        self.assertIsNotNone(extract_datetime("5g 18:53:20", "az",
                                              anchorDate=ANCHOR))

    def test_clock_time_where_minutes_are_expected_basque(self):
        self.assertIsNotNone(extract_datetime("25 15:00", "eu",
                                              anchorDate=ANCHOR))

    def test_trailing_ordinal_ukrainian(self):
        self.assertIsNotNone(extract_datetime("двадцятого", "uk",
                                              anchorDate=ANCHOR))

    def test_every_language_survives_its_own_windows(self):
        """Every window of a phrase must parse as safely as the whole."""
        for lang, phrase in PHRASE_PER_LANG.items():
            words = ("please remind me " + phrase + " and again later").split()
            for first in range(len(words)):
                for last in range(first, len(words)):
                    window = " ".join(words[first:last + 1])
                    with self.subTest(lang=lang, window=window):
                        extract_datetime(window, lang, anchorDate=ANCHOR)
