"""Named holidays resolve through chronologia, in the utterance's language.

Every expected date here is reckoned independently of the parser: Christmas
is 25 December by decree, New Year's Day 1 January, and Western Easter 2027
is 28 March by the Gregorian computus (Easter 2026 is 5 April, already past
the anchor, so the next one from September 2026 is 2027's).

The anchor is fixed at 25 September 2026, so "the next one" is a stated date
rather than whatever today makes it.
"""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from ovos_date_parser import (extract_datetime, extract_datetime_spans,
                              extract_scoped_date,
                              extract_holiday_span, holiday_surfaces,
                              load_scoped_vocabulary)
from ovos_date_parser.ranges import DateTimeResolution

REF = datetime(2026, 9, 25, 12, 0, 0)

CHRISTMAS = datetime(2026, 12, 25, 0, 0)
NEW_YEAR = datetime(2027, 1, 1, 0, 0)
EASTER = datetime(2027, 3, 28, 0, 0)

#: The five English utterances of ovos-skill-date-time#274, and the same
#: five in French and Portuguese. Each is (lang, utterance, expected date).
UTTERANCES = [
    ("en-US", "how many days until christmas", CHRISTMAS),
    ("en-US", "christmas", CHRISTMAS),
    ("en-US", "what day is christmas", CHRISTMAS),
    ("en-US", "how many days until new year", NEW_YEAR),
    ("en-US", "next easter", EASTER),
    ("fr-FR", "combien de jours jusqu'à noël", CHRISTMAS),
    ("fr-FR", "noël", CHRISTMAS),
    ("fr-FR", "quel jour est noël", CHRISTMAS),
    ("fr-FR", "combien de jours jusqu'au nouvel an", NEW_YEAR),
    ("fr-FR", "prochaine pâques", EASTER),
    ("pt-PT", "quantos dias faltam para o natal", CHRISTMAS),
    ("pt-PT", "natal", CHRISTMAS),
    ("pt-PT", "que dia é o natal", CHRISTMAS),
    ("pt-PT", "quantos dias faltam para o ano novo", NEW_YEAR),
    ("pt-PT", "próxima páscoa", EASTER),
]


@pytest.mark.parametrize("lang,utterance,expected", UTTERANCES)
def test_extract_datetime_reads_a_named_holiday(lang, utterance, expected):
    got = extract_datetime(utterance, lang, REF)
    assert got is not None, f"{lang} {utterance!r} extracted no date"
    moment, _ = got
    assert moment.replace(tzinfo=None) == expected


@pytest.mark.parametrize("lang,utterance,expected", UTTERANCES)
def test_the_holiday_name_is_consumed(lang, utterance, expected):
    """The remainder is what the skill matches its intent on, so the holiday
    itself must be gone from it — a leftover "christmas" means the date was
    read from some other word."""
    _, remainder = extract_datetime(utterance, lang, REF)
    for name in ("christmas", "noël", "natal", "easter", "pâques", "páscoa",
                 "new year", "nouvel an", "ano novo"):
        assert name not in remainder.lower(), remainder


@pytest.mark.parametrize("lang,utterance,expected", UTTERANCES)
def test_extract_holiday_span_alone(lang, utterance, expected):
    got = extract_holiday_span(utterance, lang, REF)
    assert got is not None
    assert got[0] == expected


def test_tense_selects_the_occurrence():
    """"last christmas" is the one behind the anchor, "next" the one ahead."""
    assert extract_datetime("next christmas", "en-US", REF)[0] == CHRISTMAS
    got = extract_datetime("last christmas", "en-US", REF)
    assert got is not None
    assert got[0] == datetime(2025, 12, 25, 0, 0)


NOT_HOLIDAYS = ["tomorrow", "next friday", "june 2027", "in 5 minutes",
                "eastern time", "the 3rd week of june", "next winter"]


@pytest.mark.parametrize("utterance", NOT_HOLIDAYS)
def test_a_non_holiday_is_declined_by_the_holiday_layer(utterance):
    """The layer answers for holidays only. Without this the fallback would
    hand every utterance the engines read nothing in to another library's
    grammar, which is a different change from the one made here."""
    assert extract_holiday_span(utterance, "en-US", REF) is None


@pytest.mark.parametrize("utterance", ["tomorrow", "next friday", "june 2027"])
def test_the_engine_still_answers_what_it_always_answered(utterance):
    """The holiday layer runs behind the language engine, never in front."""
    assert extract_datetime(utterance, "en-US", REF) is not None


def test_scoped_date_reads_a_holiday_when_told_the_language():
    got = extract_scoped_date("christmas", load_scoped_vocabulary("en"),
                              REF.date(), lang="en-US")
    assert got == (date(2026, 12, 25), "", DateTimeResolution.DAY)


def test_scoped_date_without_a_language_reads_what_it_always_read():
    """The holiday reading needs a language; the vocabulary carries none, so
    an existing caller that passes none keeps its old behaviour exactly."""
    assert extract_scoped_date("christmas",
                               load_scoped_vocabulary("en"), REF.date()) is None


def test_a_language_with_no_holiday_data_extracts_no_holiday():
    """Honestly scoped: no guess at English for a language chronologia has no
    holiday table for."""
    assert holiday_surfaces("zz") == {}
    assert extract_holiday_span("christmas", "zz-ZZ", REF) is None


def test_surfaces_come_from_chronologia():
    """No holiday vocabulary is copied into this library: the surfaces are
    chronologia's own table, read through, not restated."""
    from chronologia.civil_holidays import well_known_surfaces
    assert holiday_surfaces("pt") == dict(well_known_surfaces("pt"))
    assert "natal" in holiday_surfaces("pt")


# --------------------------------------------------------------------- #
# The fix round on #369: cost, remainder, accents
# --------------------------------------------------------------------- #

def test_the_language_spec_is_loaded_once_per_language():
    """The mechanism behind the cost.

    ``load_lang_spec`` compiles a locale on every call and caches nothing,
    about a second each time. ``extract_datetime_spans`` asks the holiday
    layer about every window of an utterance, so an uncached spec cost a
    second per window: 15 to 30 seconds for one sentence.
    """
    from ovos_date_parser import holidays

    assert holidays._spec("en-US") is holidays._spec("en")


def test_a_sentence_that_merely_names_a_holiday_costs_milliseconds():
    """The outcome, measured on the sentence the review blocked on.

    The bound is generous against a loaded box; what it rules out is the
    per-window reload, which took 15 seconds here and 29.9 on the reviewer's
    box against 0.00 on dev.
    """
    import time

    extract_datetime("christmas", "en-US", REF)  # warm the language spec
    started = time.monotonic()
    spans = extract_datetime_spans("play some christmas music", "en-US")
    elapsed = time.monotonic() - started
    assert elapsed < 3.0, f"the span scan took {elapsed:.1f}s"
    assert [s.surface for s in spans] == ["christmas"]


@pytest.mark.parametrize("lang,utterance,kept", [
    ("en-US", "how many days until christmas", "how many days until"),
    ("fr-FR", "combien de jours avant noël", "combien de jours avant"),
    ("pt-PT", "quantos dias faltam para o natal", "quantos dias faltam para o"),
    ("en-US", "play some christmas music", "play some music"),
])
def test_the_remainder_keeps_every_word_outside_the_holiday_phrase(
        lang, utterance, kept):
    """Only the holiday phrase leaves the remainder.

    "combien de jours avant noël" came back as 'combien': chronologia
    applied "avant" as an offset from outside the match and took "de jours"
    with it, so a French question lost words its English sibling kept.
    """
    got = extract_datetime(utterance, lang, REF)
    assert got is not None
    assert got[1] == kept


def test_the_same_question_reads_the_same_in_english_and_french():
    """The French question asked about Christmas and was answered Christmas Eve."""
    english = extract_datetime("how many days until christmas", "en-US", REF)
    french = extract_datetime("combien de jours avant noël", "fr-FR", REF)
    assert english[0] == french[0] == CHRISTMAS


@pytest.mark.parametrize("lang,plain,written", [
    ("fr-FR", "noel", "noël"),
    ("fr-FR", "paques", "pâques"),
    ("fr-FR", "combien de jours avant noel", "combien de jours avant noël"),
    ("pt-PT", "pascoa", "páscoa"),
])
def test_a_transcript_without_accents_reads_the_same_date(lang, plain, written):
    """Speech to text drops accents; the holiday is named either way.

    French resolved only the written form, while Portuguese already resolved
    both, so the same feature answered one language and refused the other.
    """
    assert extract_datetime(plain, lang, REF) is not None
    assert extract_datetime(plain, lang, REF)[0] == \
        extract_datetime(written, lang, REF)[0]


def test_the_documented_french_example_is_true():
    """docs/api.md says the unaccented "noel" resolves. It must."""
    from pathlib import Path

    import ovos_date_parser

    doc = (Path(ovos_date_parser.__file__).parent.parent / "docs" / "api.md")
    if doc.exists():
        assert "noel" in doc.read_text(encoding="utf-8")
    assert extract_datetime("noel", "fr-FR", REF)[0] == CHRISTMAS


@pytest.mark.parametrize("utterance,expected", [
    ("next easter", EASTER),
    ("last christmas", datetime(2025, 12, 25, 0, 0)),
    ("christmas eve", datetime(2026, 12, 24, 0, 0)),
])
def test_a_tense_inside_the_holiday_phrase_still_reads(utterance, expected):
    """The control on reading the construction's own extent.

    Reading only the matched extent must not cost the tense a phrase states
    inside it: chronologia reports "next easter", "last christmas" and
    "christmas eve" each as one match over all their words.
    """
    assert extract_datetime(utterance, "en-US", REF)[0] == expected


# --- finding 5 of the #369 review: a holiday named after a weekday ----------

# `extract_datetime` runs the per-language engine first. A holiday whose own
# name carries weekday vocabulary — "good friday", "palm sunday" — therefore
# answered with the coming weekday and never reached the holiday layer, which
# knew the right date all along. Eight of the twelve weekday- and month-named
# English holidays answered that way.
#
# Every date below is reckoned independently of the parser. Western Easter 2027
# is 28 March by the Gregorian computus, and the movable feasts are counted from
# it: Palm Sunday is Easter minus 7 (21 March), Maundy Thursday minus 3
# (25 March), Good Friday minus 2 (26 March), Holy Saturday minus 1 (27 March),
# Easter Monday plus 1 (29 March), Whit Monday plus 50 (17 May). Shrove Tuesday
# is Easter minus 47 (9 February) and Ash Wednesday minus 46 (10 February).

WEEKDAY_NAMED_HOLIDAYS = [
    ("palm sunday", date(2027, 3, 21)),
    ("maundy thursday", date(2027, 3, 25)),
    ("good friday", date(2027, 3, 26)),
    ("holy saturday", date(2027, 3, 27)),
    ("easter monday", date(2027, 3, 29)),
    ("whit monday", date(2027, 5, 17)),
    ("shrove tuesday", date(2027, 2, 9)),
    ("ash wednesday", date(2027, 2, 10)),
]


@pytest.mark.parametrize("utterance,expected", WEEKDAY_NAMED_HOLIDAYS)
def test_a_weekday_named_holiday_answers_with_the_holiday(utterance, expected):
    """The holiday layer's date wins when the engine read the holiday's own
    words as a weekday."""
    got = extract_datetime(utterance, "en-US", REF)
    assert got is not None
    assert got[0].date() == expected


@pytest.mark.parametrize("utterance,expected", WEEKDAY_NAMED_HOLIDAYS)
def test_a_weekday_named_holiday_keeps_no_half_of_its_name(utterance, expected):
    """The remainder holds no word of the holiday's own name."""
    got = extract_datetime(utterance, "en-US", REF)
    assert got is not None
    for word in utterance.split():
        assert word not in got[1].lower()


# --- a word of time beside the holiday name, from the #374 review ----------

# The first cut compared the words the engine consumed against the words of the
# holiday phrase, and declined whenever the engine consumed anything else. A
# time of day is something else, so "good friday at 9am" kept the engine's
# coming Friday and left `'good'` in the remainder: half the holiday's own name,
# on the commonest spoken form of all eight. The test asks the engine the
# holiday phrase on its own instead, and the override fires when that answer's
# date equals the date the whole text produced, which a time of day does not
# move.
#
# Each expected date is reckoned independently from the computus, as above.

WEEKDAY_NAMED_HOLIDAYS_WITH_A_TIME = [
    ("good friday at 9am", date(2027, 3, 26)),
    ("remind me on good friday at 9am", date(2027, 3, 26)),
    ("palm sunday at noon", date(2027, 3, 21)),
    ("easter monday morning", date(2027, 3, 29)),
    ("shrove tuesday at 6pm", date(2027, 2, 9)),
    ("set an alarm for good friday at 7", date(2027, 3, 26)),
]

WEEKDAY_NAMED_HOLIDAY_WORDS = frozenset(
    word for utterance, _ in WEEKDAY_NAMED_HOLIDAYS for word in utterance.split()
)


@pytest.mark.parametrize("utterance,expected",
                         WEEKDAY_NAMED_HOLIDAYS_WITH_A_TIME)
def test_a_time_beside_a_holiday_name_still_answers_with_the_holiday(
        utterance, expected):
    """A time of day beside the holiday name does not send the answer back to
    the engine's weekday."""
    got = extract_datetime(utterance, "en-US", REF)
    assert got is not None
    assert got[0].date() == expected


@pytest.mark.parametrize("utterance,expected",
                         WEEKDAY_NAMED_HOLIDAYS_WITH_A_TIME)
def test_a_time_beside_a_holiday_name_keeps_no_half_of_the_name(
        utterance, expected):
    """The remainder holds no word of any weekday-named holiday.

    The whole set is checked, not only the words of this utterance, because the
    failure this cell exists for left `'good'`, `'palm'`, `'easter'` and
    `'shrove'` behind.
    """
    got = extract_datetime(utterance, "en-US", REF)
    assert got is not None
    remainder_words = set(got[1].lower().split())
    assert not (remainder_words & WEEKDAY_NAMED_HOLIDAY_WORDS)


#: (lang, utterance, expected datetime, expected remainder). Easter 2027 is
#: 28 March, so Good Friday is 26 March, Palm Sunday 21 March and Easter
#: Monday 29 March. Pentecost 2027 is 16 May, so Whit Monday is 17 May.
HOLIDAYS_WITH_A_CLOCK_TIME = [
    ("en-US", "good friday at 9am", datetime(2027, 3, 26, 9, 0), ""),
    ("en-US", "good friday at 5pm", datetime(2027, 3, 26, 17, 0), ""),
    ("en-US", "palm sunday at noon", datetime(2027, 3, 21, 12, 0), ""),
    ("en-US", "remind me on good friday at 9am to call mum",
     datetime(2027, 3, 26, 9, 0), "remind me on to call mum"),
    ("en-US", "easter monday at 9am", datetime(2027, 3, 29, 9, 0), ""),
    ("pt-PT", "sexta-feira santa às 9", datetime(2027, 3, 26, 9, 0), ""),
    ("pt-PT", "domingo de ramos às 10 horas",
     datetime(2027, 3, 21, 10, 0), ""),
    ("pt-PT", "sexta-feira santa às 9 da manhã",
     datetime(2027, 3, 26, 9, 0), ""),
    ("en-US", "remind me at home on good friday at 9am",
     datetime(2027, 3, 26, 9, 0), "remind me at home on"),
    ("en-US", "good friday at 9am at the office",
     datetime(2027, 3, 26, 9, 0), "at the office"),
    ("de-DE", "karfreitag um 9 uhr", datetime(2027, 3, 26, 9, 0), ""),
    ("de-DE", "ostermontag um 9 uhr", datetime(2027, 3, 29, 9, 0), ""),
    ("de-DE", "pfingstmontag um 10 uhr", datetime(2027, 5, 17, 10, 0), ""),
]


@pytest.mark.parametrize("lang,utterance,expected,remainder",
                         HOLIDAYS_WITH_A_CLOCK_TIME)
def test_the_holiday_layer_keeps_the_time_of_day(lang, utterance, expected,
                                                 remainder):
    """The clock time beside a holiday name is part of the answer and leaves
    the remainder."""
    assert extract_holiday_span(utterance, lang, REF) == (expected, remainder)


@pytest.mark.parametrize("lang,utterance,expected,remainder", [
    case for case in HOLIDAYS_WITH_A_CLOCK_TIME
    if case[0] in ("en-US", "pt-PT")])
def test_extract_datetime_keeps_the_time_of_a_weekday_named_holiday(
        lang, utterance, expected, remainder):
    """German is not listed: the German engine answers "karfreitag um 9 uhr"
    with tomorrow at nine before the holiday layer is asked."""
    assert extract_datetime(utterance, lang, REF) == (expected, remainder)


def test_a_default_time_does_not_replace_a_time_that_was_read():
    got = extract_datetime("good friday at 9am", "en-US", REF,
                           default_time=time(18, 30))
    assert got[0] == datetime(2027, 3, 26, 9, 0)


@pytest.mark.parametrize("utterance,expected", [
    ("good friday at midnight", datetime(2027, 3, 26, 0, 0)),
    ("easter monday at midnight", datetime(2027, 3, 29, 0, 0)),
    ("palm sunday at 12am", datetime(2027, 3, 21, 0, 0)),
])
def test_a_default_time_does_not_replace_a_midnight_that_was_said(
        utterance, expected):
    got = extract_datetime(utterance, "en-US", REF,
                           default_time=time(18, 30))
    assert got == (expected, "")


@pytest.mark.parametrize("utterance,expected,remainder", [
    ("easter at 25:00", datetime(2027, 3, 28, 0, 0), "at 25:00"),
    ("good friday at 9am tomorrow", datetime(2027, 3, 26, 0, 0),
     "at 9am tomorrow"),
])
def test_a_clock_chronologia_did_not_apply_stays_in_the_remainder(
        utterance, expected, remainder):
    """chronologia names a clock_time match in both phrases and leaves its
    words in its own remainder; the words are not cut from ours either."""
    assert extract_holiday_span(utterance, "en-US", REF) == (expected,
                                                             remainder)


def test_a_default_time_still_fills_a_holiday_with_no_time():
    got = extract_datetime("good friday", "en-US", REF,
                           default_time=time(18, 30))
    assert got[0] == datetime(2027, 3, 26, 18, 30)


def test_two_clock_times_leave_the_holiday_without_one():
    """Which of two times belongs to the holiday is a guess; none is taken."""
    got = extract_holiday_span("good friday at 9am and then at 5pm", "en-US",
                               REF)
    assert got is not None
    assert got[0] == datetime(2027, 3, 26, 0, 0)


def test_a_plain_weekday_still_answers_with_the_weekday(utterance=None):
    """Control: a weekday that names no holiday is untouched.

    25 September 2026 is a Friday, so the coming Sunday is the 27th.
    """
    got = extract_datetime("sunday", "en-US", REF)
    assert got is not None
    assert got[0].date() == date(2026, 9, 27)


def test_a_weekday_beside_a_holiday_keeps_the_weekday():
    """Control: the engine's answer stands when it read words the holiday
    phrase does not cover.

    "play christmas music on friday" asks about Friday. The holiday phrase is
    "christmas" alone, so the engine's Friday is not inside it and the holiday
    date must not replace it.
    """
    got = extract_datetime("play christmas music on friday", "en-US", REF)
    assert got is not None
    assert got[0].date() == date(2026, 9, 25) or got[0].date() == date(2026, 10, 2)
    assert got[0].date() != date(2026, 12, 25)


def test_a_holiday_the_engine_cannot_read_is_unchanged():
    """Control: the None path of the engine still answers from the layer."""
    got = extract_datetime("boxing day", "en-US", REF)
    assert got is not None
    assert got[0].date() == date(2026, 12, 26)


# --- a weekday given outside the holiday phrase --------------------------

# `holiday_overrides_engine` declines when a word of the holiday name that the
# engine consumed also stands outside the name: the speaker gave that weekday
# separately and the engine's answer is the one asked for. Anchor Friday
# 2026-09-25, so the coming Friday is that day, the coming Sunday is 27
# September and the coming Monday is 28 September.

WEEKDAY_OUTSIDE_THE_HOLIDAY_PHRASES = [
    ("remind me friday about good friday", date(2026, 9, 25)),
    ("remind me on sunday to buy palms for palm sunday", date(2026, 9, 27)),
    ("call mom on monday about easter monday plans", date(2026, 9, 28)),
    ("this friday let us plan good friday", date(2026, 9, 25)),
    ("good friday plans, remind me friday", date(2026, 9, 25)),
]


@pytest.mark.parametrize("utterance,expected",
                         WEEKDAY_OUTSIDE_THE_HOLIDAY_PHRASES)
def test_a_weekday_outside_the_holiday_phrase_keeps_the_engine_answer(
        utterance, expected):
    got = extract_datetime(utterance, "en-US", REF)
    assert got is not None
    assert got[0].date() == expected


def test_a_relative_phrase_the_engine_keeps_is_not_taken():
    """Control, the opposite call on a phrase of the same shape.

    "good friday and next friday" carries a Friday outside the holiday phrase,
    so the engine keeps the utterance. 25 September 2026 is a Friday, so the
    next one is 2 October.
    """
    got = extract_datetime("good friday and next friday", "en-US", REF)
    assert got is not None
    assert got[0].date() == date(2026, 10, 2)


# The engine reads a weekday named twice as the coming weekday. The dates the
# phrases name: the Friday before Good Friday (26 March 2027) is 19 March, and
# the Monday after Easter Monday (29 March 2027) is 5 April.
@pytest.mark.xfail(strict=True, reason="a relative phrase on a holiday word "
                   "answers with the engine's coming weekday")
@pytest.mark.parametrize("utterance,expected", [
    ("the friday before good friday", date(2027, 3, 19)),
    ("monday after easter monday", date(2027, 4, 5)),
])
def test_a_relative_phrase_on_a_holiday_word_names_its_own_date(
        utterance, expected):
    got = extract_datetime(utterance, "en-US", REF)
    assert got is not None
    assert got[0].date() == expected


# Anchor Friday 2026-09-25: the weekday is the engine's answer, not the holiday.
A_GOOD_WEEKDAY_IS_NOT_A_HOLIDAY = [
    ("en-US", "have a good friday", date(2026, 9, 25)),
    ("en-US", "hope you have a good friday", date(2026, 9, 25)),
    ("en-US", "remind me to wish bob a good friday", date(2026, 9, 25)),
    ("en-US", "a good friday for a walk", date(2026, 9, 25)),
    ("nl-NL", "een goede vrijdag", date(2026, 9, 25)),
    ("nl-NL", "ik wens je een goede vrijdag", date(2026, 9, 25)),
]


@pytest.mark.parametrize("lang,utterance,expected",
                         A_GOOD_WEEKDAY_IS_NOT_A_HOLIDAY)
def test_an_indefinite_article_before_the_name_is_a_weekday(
        lang, utterance, expected):
    got = extract_datetime(utterance, lang, REF)
    assert got is not None
    assert got[0].date() == expected


# Anchor Friday 2026-09-25. Western Easter 2027 is 28 March, so Good Friday is
# 26 March. chronologia refuses a holiday after an indefinite article only
# in English and Dutch; in Portuguese "a" is "the", so the holiday still wins. German names the weekday
# outside the holiday phrase and keeps the engine's coming Friday.
HOLIDAYS_IN_OTHER_LANGUAGES = [
    ("pt-PT", "sexta-feira santa", date(2027, 3, 26)),
    ("pt-BR", "sexta-feira santa", date(2027, 3, 26)),
    ("pt-PT", "a sexta-feira santa", date(2027, 3, 26)),
    ("pt-PT", "domingo de páscoa", date(2027, 3, 28)),
    ("es-ES", "viernes santo", date(2027, 3, 26)),
    ("fr-FR", "vendredi saint", date(2027, 3, 26)),
    ("it-IT", "venerdì santo", date(2027, 3, 26)),
    ("de-DE", "am freitag ist karfreitag", date(2026, 9, 25)),
]


@pytest.mark.parametrize("lang,utterance,expected",
                         HOLIDAYS_IN_OTHER_LANGUAGES)
def test_holiday_phrases_in_languages_without_an_article_rule(
        lang, utterance, expected):
    got = extract_datetime(utterance, lang, REF)
    assert got is not None
    assert got[0].date() == expected


# --- the anchor's time zone --------------------------------------------------

NEW_YORK = ZoneInfo("America/New_York")
AWARE_REF = datetime(2026, 10, 17, 12, 0, tzinfo=NEW_YORK)


@pytest.mark.parametrize("utterance", ["christmas", "how many days until christmas"])
def test_a_holiday_answer_keeps_the_anchors_time_zone(utterance):
    """The engine answers in the anchor's zone, so a caller that subtracts the
    anchor from the answer must not meet a naive datetime."""
    got = extract_datetime(utterance, "en-US", AWARE_REF)
    assert got is not None
    assert got[0].tzinfo is NEW_YORK
    assert got[0] - AWARE_REF == timedelta(days=68, hours=12)


def test_a_holiday_in_winter_has_the_winter_offset():
    """25 December 2026 is New York standard time, five hours behind UTC."""
    got = extract_datetime("christmas", "en-US", AWARE_REF)
    assert got[0].utcoffset() == timedelta(hours=-5)


def test_the_holiday_span_keeps_the_anchors_time_zone():
    got = extract_holiday_span("christmas at 9am", "en-US", AWARE_REF)
    assert got[0] == datetime(2026, 12, 25, 9, 0, tzinfo=NEW_YORK)


def test_a_naive_anchor_still_gets_a_naive_answer():
    got = extract_datetime("christmas", "en-US", REF)
    assert got[0].tzinfo is None
