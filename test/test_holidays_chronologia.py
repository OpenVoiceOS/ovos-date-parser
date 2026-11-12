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
    ("pt-PT", "quantos dias faltam para o natal", "quantos dias faltam para o"),
    ("en-US", "play some christmas music", "play some music"),
])
def test_the_remainder_keeps_every_word_the_parse_did_not_consume(
        lang, utterance, kept):
    """A question word the parse did not read stays in the remainder.

    The remainder is chronologia's, re-spelled with the caller's own
    characters, so it holds exactly what the parse left. The French sibling
    of the first row is not here: it is a known wrong answer and has its own
    cell below.
    """
    got = extract_datetime(utterance, lang, REF)
    assert got is not None
    assert got[1] == kept


def test_the_english_question_keeps_its_words_and_answers_christmas():
    """The shape the French row below should have, and does not."""
    english = extract_datetime("how many days until christmas", "en-US", REF)
    assert english[0] == CHRISTMAS
    assert english[1] == "how many days until"


# --- known answers, not correct answers -------------------------------------

def test_a_french_interrogative_quantity_before_a_holiday_is_read_as_an_offset():
    """Known answer, and the defect is chronologia's: task T-6896.

    "combien de jours avant noël" asks how many days remain before Christmas,
    so the date is Christmas, 25 December. chronologia reads "avant" after an
    interrogative quantity as an offset and answers the day before, taking
    "de jours avant" into the match and leaving "combien" behind.

    The two controls are the shapes that ARE read correctly, so the cell
    blames the interrogative and not the language or the preposition: the
    English "how many days until christmas" above, and the French
    "combien de jours jusqu'a noël" here.

    Parsing the holiday construction's own substring hid this row, at the
    price of four silently wrong offset dates ("the day after christmas" and
    its siblings). The whole text is right on those four and wrong on this
    one. The day chronologia fixes it, this cell fails and says so.
    """
    got = extract_datetime("combien de jours avant noël", "fr-FR", REF)
    assert got is not None
    assert got[0] == datetime(2026, 12, 24, 0, 0)
    assert got[0] != CHRISTMAS
    assert got[1] == "combien"

    control = extract_datetime("combien de jours jusqu'à noël", "fr-FR", REF)
    assert control[0] == CHRISTMAS


#: The C1 rows: an offset written OUTSIDE the holiday construction. Each date
#: is counted by hand from Christmas, 25 December 2026.
#: The C1 rows: an offset written OUTSIDE the holiday construction. Each date
#: is counted by hand from Christmas, 25 December 2026.
OFFSET_UTTERANCES = [
    ("en-US", "the day after christmas", datetime(2026, 12, 26, 0, 0)),
    ("en-US", "the day before christmas", datetime(2026, 12, 24, 0, 0)),
    ("en-US", "two days after christmas", datetime(2026, 12, 27, 0, 0)),
    ("fr-FR", "le jour après noël", datetime(2026, 12, 26, 0, 0)),
    ("fr-FR", "le jour apres noel", datetime(2026, 12, 26, 0, 0)),
]

#: The rows above that reach the holiday layer through `extract_datetime`.
#: "two days after christmas" is not one of them and has its own cell below.
OFFSET_THROUGH_EXTRACT_DATETIME = [
    row for row in OFFSET_UTTERANCES if not row[1].startswith("two days")
]


@pytest.mark.parametrize("lang,utterance,expected", OFFSET_UTTERANCES)
def test_an_offset_outside_the_holiday_phrase_moves_the_date(
        lang, utterance, expected):
    """The C1 regression, one cell per row, on the layer that owns it.

    Each of these answered 25 December, the holiday itself, and handed the
    offset back in the remainder as though it were question words. The parse
    read the holiday construction's own characters, so a modifier outside the
    construction was never applied.

    The last row is the same French sentence without its accents, which is
    what speech to text produces; it must read the same.
    """
    got = extract_holiday_span(utterance, lang, REF)
    assert got is not None
    assert got[0] == expected
    assert got[0] != CHRISTMAS


@pytest.mark.parametrize("lang,utterance,expected", OFFSET_UTTERANCES)
def test_an_offset_phrase_leaves_no_remainder(lang, utterance, expected):
    """The other half: the offset words are consumed, not handed back.

    A caller that reads the remainder as the rest of the command would have
    been given "the day after" to act on.
    """
    got = extract_holiday_span(utterance, lang, REF)
    assert got is not None
    assert got[1] == ""


@pytest.mark.parametrize("lang,utterance,expected",
                         OFFSET_THROUGH_EXTRACT_DATETIME)
def test_an_offset_phrase_reads_the_same_through_extract_datetime(
        lang, utterance, expected):
    """The whole call, not the layer alone, for the rows that reach it.

    Without this the module could pass on a library whose entry point never
    consults the holiday layer at all.
    """
    got = extract_datetime(utterance, lang, REF)
    assert got is not None
    assert got[0] == expected


def test_two_days_after_christmas_is_answered_by_the_engine_not_the_holiday():
    """Known answer, and a different defect from the one above.

    The holiday layer reads this row correctly, and the cells above assert
    that. `extract_datetime` never asks it: the per-language engine reads
    "two days" as an offset from the anchor, answers 27 September 2026 and
    hands back "after christmas", so the engine-first order ends the walk
    before the holiday layer is reached.

    That is the shadowing family of finding 5 of the #369 review, but not the
    case `holiday_overrides_engine` covers: its rule asks whether the words
    the engine consumed all lie inside the holiday phrase, and "two days"
    does not lie inside "christmas". The rule is right to decline here; the
    engine's partial read is the defect, and it is filed on its own.

    The cell holds the answer this library gives today so the day that is
    fixed it fails and says so.
    """
    got = extract_datetime("two days after christmas", "en-US", REF)
    assert got is not None
    assert got[0] == datetime(2026, 9, 27, 0, 0)
    assert got[1] == "after christmas"

    # the control: the layer the walk skipped has the right answer
    layer = extract_holiday_span("two days after christmas", "en-US", REF)
    assert layer[0] == datetime(2026, 12, 27, 0, 0)


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


# --- the part-of-day offset family, T-7244 from reviewer-d's review of #381 -

# A part-of-day word written as the offset is read as a time of day ON the
# holiday, and the before/after is dropped: "before" and "after" give the same
# answer. Every row comes back with an EMPTY remainder, so a caller cannot see
# that the modifier was read at all. That is what makes the family worth a cell
# rather than a note: dev at least handed the offset back in the remainder.
#
# The defect is chronologia's, like the French interrogative above, and task
# T-7350 carries it. The day offset is read correctly on the same anchor
# ("the day after christmas" gives 26 December), so the part-of-day word is the
# whole of it.
#
# These call extract_holiday_span rather than extract_datetime, because it is
# that function's contract this family bounds. Through extract_datetime the
# per-language engine answers these utterances first and the holiday layer is
# never reached, so extract_datetime would assert the engine's answer, which is
# a different wrong answer and not this one.

PART_OF_DAY_OFFSETS = [
    # lang, utterance, the answer given today, what the utterance names
    ("en-US", "the night before christmas",
     datetime(2026, 12, 25, 21, 0), "the night of 24 December"),
    ("en-US", "the morning after christmas",
     datetime(2026, 12, 25, 6, 0), "the morning of 26 December"),
    ("en-US", "the evening after christmas",
     datetime(2026, 12, 25, 18, 0), "the evening of 26 December"),
    ("en-US", "the night after christmas",
     datetime(2026, 12, 25, 21, 0), "the night of 26 December"),
    ("en-US", "the morning before christmas",
     datetime(2026, 12, 25, 6, 0), "the morning of 24 December"),
    ("fr-FR", "le soir avant noël",
     datetime(2026, 12, 25, 18, 0), "le soir du 24 décembre"),
    ("fr-FR", "le matin après noël",
     datetime(2026, 12, 25, 4, 0), "le matin du 26 décembre"),
    ("pt-PT", "a noite antes do natal",
     datetime(2026, 12, 25, 19, 0), "a noite de 24 de dezembro"),
]


@pytest.mark.parametrize("lang,utterance,given,asked", PART_OF_DAY_OFFSETS)
def test_a_part_of_day_offset_is_read_as_a_time_on_the_holiday(
        lang, utterance, given, asked):
    """Known answer, not a correct answer: the defect is chronologia's, T-7350.

    Each expected value is the answer this library gives today. What the
    utterance actually names is written beside it. The day chronologia fixes
    any of these the cell fails and says which.
    """
    got = extract_holiday_span(utterance, lang, REF)
    assert got is not None, f"{utterance!r} no longer reaches the holiday layer"
    assert got[0] == given, f"{utterance!r} asks for {asked}"
    assert got[1] == "", (
        f"{utterance!r} left {got[1]!r} over; an empty remainder is what makes "
        "this family invisible to a caller, and the cell holds that too")


def test_the_direction_makes_no_difference_to_a_part_of_day_offset():
    """The sharpest statement of the defect: before and after agree.

    A cell per row could pass while the two directions still collapsed onto
    one answer, so the collapse is asserted on its own.
    """
    before = extract_holiday_span("the night before christmas", "en-US", REF)
    after = extract_holiday_span("the night after christmas", "en-US", REF)
    assert before[0] == after[0] == datetime(2026, 12, 25, 21, 0)


def test_a_day_offset_is_still_read_correctly():
    """Control: the direction IS honoured for a day offset, so the family
    above blames the part-of-day word and not the offset machinery."""
    got = extract_holiday_span("the day after christmas", "en-US", REF)
    assert got is not None
    assert got[0] == datetime(2026, 12, 26, 0, 0)



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


@pytest.mark.parametrize("lang,utterance,expected,remainder",
                         HOLIDAYS_WITH_A_CLOCK_TIME)
def test_extract_datetime_keeps_the_time_of_a_holiday(
        lang, utterance, expected, remainder):
    assert extract_datetime(utterance, lang, REF) == (expected, remainder)


#: Holidays whose name is no calendar word, so the engine reads only the clock
#: and answers with the day that clock next comes round (26 September 2026).
#: 25 December is Christmas by decree; Christmas Eve is the day before.
HOLIDAYS_THE_ENGINE_READS_ONLY_A_CLOCK_BESIDE = [
    ("en-US", "christmas at 9am", datetime(2026, 12, 25, 9, 0), ""),
    ("en-US", "christmas at 9 am", datetime(2026, 12, 25, 9, 0), ""),
    ("en-US", "christmas 9am", datetime(2026, 12, 25, 9, 0), ""),
    ("en-US", "christmas eve at noon", datetime(2026, 12, 24, 12, 0), ""),
    ("de-DE", "weihnachten um 18:30", datetime(2026, 12, 25, 18, 30), "um"),
    ("de-DE", "ostern um 9 uhr", datetime(2027, 3, 28, 9, 0), ""),
    ("fr-FR", "pâques à 9 heures", datetime(2027, 3, 28, 9, 0), ""),
    ("es-ES", "navidad a las 9", datetime(2026, 12, 25, 9, 0), ""),
]


@pytest.mark.parametrize("lang,utterance,expected,remainder",
                         HOLIDAYS_THE_ENGINE_READS_ONLY_A_CLOCK_BESIDE)
def test_a_clock_beside_a_holiday_name_is_not_the_engines_next_day(
        lang, utterance, expected, remainder):
    assert extract_datetime(utterance, lang, REF) == (expected, remainder)


#: A holiday word that modifies something else, or a clock that belongs to
#: another part of the sentence, leaves the engine's day: the next time the
#: clock comes round after 25 September 2026 12:00. 9am has passed today, so
#: it is the 26th; 5pm, 9pm and 21 hours are still to come on the 25th.
CLOCK_NOT_BESIDE_THE_HOLIDAY = [
    ("en-US", "buy christmas presents at 5pm", datetime(2026, 9, 25, 17, 0)),
    ("en-US", "play christmas music at 9pm", datetime(2026, 9, 25, 21, 0)),
    ("en-US", "remind me at 5pm to buy christmas cards",
     datetime(2026, 9, 25, 17, 0)),
    ("en-US", "christmas island at 9am", datetime(2026, 9, 26, 9, 0)),
    ("en-US", "call mom at 9am about easter", datetime(2026, 9, 26, 9, 0)),
    ("fr-FR", "musique de noël à 21 heures", datetime(2026, 9, 25, 21, 0)),
    ("de-DE", "geschenke für weihnachten um 17 uhr kaufen",
     datetime(2026, 9, 25, 17, 0)),
]


@pytest.mark.parametrize("lang,utterance,expected",
                         CLOCK_NOT_BESIDE_THE_HOLIDAY)
def test_a_clock_that_is_not_the_holidays_keeps_the_engines_day(
        lang, utterance, expected):
    got = extract_datetime(utterance, lang, REF)
    assert got is not None
    assert got[0] == expected


@pytest.mark.parametrize("utterance", [
    "play christmas music on friday",
    "play christmas music on friday at 9am",
    "remind me on friday at 9am about christmas",
    "christmas tomorrow at 9am",
])
def test_a_date_word_beside_the_clock_keeps_the_engines_date(utterance):
    """The engine read a date word as well as the clock, so the holiday does
    not replace its answer."""
    got = extract_datetime(utterance, "en-US", REF)
    assert got is not None
    assert got[0].date() != date(2026, 12, 25)
    assert got[0].date() <= date(2026, 10, 2)


@pytest.mark.parametrize("utterance", [
    "remind me at 9am on christmas",
    "remind me on christmas at 9am",
])
def test_a_clock_before_or_after_the_holiday_is_the_holidays(utterance):
    got = extract_datetime(utterance, "en-US", REF)
    assert got is not None
    assert got[0] == datetime(2026, 12, 25, 9, 0)


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
