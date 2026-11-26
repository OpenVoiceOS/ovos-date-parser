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
from ovos_date_parser.holidays import (_holiday_answer, _spec,
                                      extract_holiday_date)
from ovos_date_parser.ranges import DateTimeResolution

REF = datetime(2026, 9, 25, 12, 0, 0)


def _known_defects(rows, defects):
    """``rows`` with each row that holds an utterance of ``defects`` marked
    as a known defect, tracked by the issue it maps to."""
    marked = []
    for row in rows:
        issue = next((defects[value] for value in row
                      if isinstance(value, str) and value in defects), None)
        marks = () if issue is None else pytest.mark.xfail(
            strict=True, reason=issue)
        marked.append(pytest.param(*row, marks=marks))
    return marked

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
    assert tuple(got) == (date(2026, 12, 25), "", DateTimeResolution.DAY)


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


@pytest.mark.parametrize("lang,utterance,kept", _known_defects([
    ("en-US", "how many days until christmas", "how many days until"),
    ("fr-FR", "combien de jours avant noël", "combien de jours avant"),
    ("pt-PT", "quantos dias faltam para o natal", "quantos dias faltam para"),
    ("en-US", "play some christmas music", "play some music"),
], {"combien de jours avant noël": "https://github.com/TigreGotico/chronologia/issues/1004"}))
def test_the_remainder_keeps_every_word_the_parse_did_not_consume(
        lang, utterance, kept):
    """A question word stays in the remainder: only the holiday phrase is
    cut out of the text."""
    got = extract_datetime(utterance, lang, REF)
    assert got is not None
    assert got[1] == kept


def test_the_english_question_keeps_its_words_and_answers_christmas():
    """The question keeps its words and asks about Christmas itself."""
    english = extract_datetime("how many days until christmas", "en-US", REF)
    assert english[0] == CHRISTMAS
    assert english[1] == "how many days until"


#: A preposition alone before a holiday is no offset: "until christmas" is a
#: range that ends on the holiday and "after christmas" one that starts on it.
#: The holiday answers, and the preposition is handed back.
PREPOSITION_ALONE = [
    ("en-US", "until easter", EASTER, "until"),
    ("en-US", "before christmas", CHRISTMAS, "before"),
    ("en-US", "after christmas", CHRISTMAS, "after"),
    ("fr-FR", "avant noël", CHRISTMAS, "avant"),
    ("fr-FR", "après noël", CHRISTMAS, "après"),
    ("es-ES", "hasta navidad", CHRISTMAS, "hasta"),
    ("es-ES", "después de navidad", CHRISTMAS, "después de"),
    ("de-DE", "bis Weihnachten", CHRISTMAS, "bis"),
    ("de-DE", "nach Weihnachten", CHRISTMAS, "nach"),
    ("nl-NL", "tot kerst", CHRISTMAS, "tot"),
    ("pt-PT", "até ao natal", CHRISTMAS, "até ao"),
    ("it-IT", "dopo natale", CHRISTMAS, "dopo"),
]


@pytest.mark.parametrize("lang,utterance,expected,kept", PREPOSITION_ALONE)
def test_a_preposition_alone_is_no_offset(lang, utterance, expected, kept):
    assert extract_holiday_span(utterance, lang, REF) == (expected, kept)
    assert tuple(extract_datetime(utterance, lang, REF)) == (expected, kept)


@pytest.mark.parametrize("lang,utterance,expected,kept", [
    ("en-US", "how many days between today and christmas", CHRISTMAS,
     "how many days between today and"),
    ("en-US", "how many days from now until christmas", CHRISTMAS,
     "how many days from now until"),
    ("en-US", "remind me on sunday to buy palms for palm sunday",
     datetime(2027, 3, 21, 0, 0), "remind me on sunday to buy palms for"),
    ("en-US", "remind me at 5pm to buy christmas cards", CHRISTMAS,
     "remind me at 5pm to buy cards"),
    ("en-US", "christmas and christmas eve", CHRISTMAS, "and christmas eve"),
    ("en-US", "remind me friday about good friday",
     datetime(2027, 3, 26, 0, 0), "remind me friday about"),
])
def test_the_holiday_layer_answers_the_holiday(lang, utterance, expected,
                                               kept):
    """A date word elsewhere in the sentence is no offset of the holiday.

    The whole-text parse answers from "today", "sunday", "5pm" or "friday"
    here; the holiday layer answers the holiday it names (Palm Sunday 2027 is
    21 March, Good Friday 26 March) and hands every other word back.
    """
    assert extract_holiday_span(utterance, lang, REF) == (expected, kept)


#: A question for the count with two clock times after it: chronologia splits
#: "9am" into "9" and "am", and normalises "10h" to a token with no position.
TWO_CLOCKS_AFTER_A_QUESTION = [
    ("en-US", "how many days before christmas at 9am and 10am",
     "how many days before at 9am and 10am"),
    ("en-US", "how many days before christmas at 9am or 10am",
     "how many days before at 9am or 10am"),
    ("fr-FR", "combien de jours avant noël à 9h et à 10h",
     "combien de jours avant à 9h et à 10h"),
    ("pt-PT", "quantos dias faltam para o natal às 9h e às 10h",
     "quantos dias faltam para às 9h e às 10h"),
    ("pt-PT", "quantos dias antes do natal às 9h e às 10h",
     "quantos dias antes do às 9h e às 10h"),
    ("es-ES", "cuántos días antes de navidad a las 9h y 10h",
     "cuántos días antes de a las 9h y 10h"),
]


@pytest.mark.parametrize("lang,utterance,kept", TWO_CLOCKS_AFTER_A_QUESTION)
def test_two_clock_times_after_a_question_for_the_count(lang, utterance,
                                                         kept):
    assert extract_holiday_span(utterance, lang, REF) == (CHRISTMAS, kept)
    assert extract_holiday_date(utterance, lang, REF.date()) == (
        CHRISTMAS.date(), kept)
    vocab = load_scoped_vocabulary(lang.split("-")[0])
    got = extract_scoped_date(utterance, vocab, REF.date(), lang=lang)
    assert got is not None and got[0] == CHRISTMAS.date()


@pytest.mark.parametrize("lang,utterance,quantifier", [
    ("en-US", "a few days after christmas", "few"),
    ("en-US", "several days after christmas", "several"),
    ("fr-FR", "quelques jours après noël", "quelques"),
    ("de-DE", "einige Tage nach Weihnachten", "einige"),
])
def test_a_quantifier_counts_a_plural_unit(lang, utterance, quantifier):
    """The quantifier is the count, as a number is ("two days after").

    The number of days is the value chronologia gives the quantifier.
    """
    days = _spec(lang).quantifiers[quantifier]
    expected = CHRISTMAS + timedelta(days=days)
    assert extract_holiday_span(utterance, lang, REF) == (expected, "")


@pytest.mark.parametrize("lang,utterance,kept", [
    ("en-US", "a couple of days after christmas", "a couple of days after"),
])
def test_an_offset_chronologia_reads_wrong_is_handed_back(lang, utterance,
                                                          kept):
    """chronologia leaves "a couple" over and reads one day. That is no
    counted offset of the holiday, so it stays in the remainder."""
    assert extract_holiday_span(utterance, lang, REF) == (CHRISTMAS, kept)


@pytest.mark.parametrize("utterance,expected", [
    # Easter 2027 is 28 March: Good Friday 26 March, Easter Monday 29 March
    ("the friday before good friday", datetime(2027, 3, 19, 0, 0)),
    ("monday after easter monday", datetime(2027, 4, 5, 0, 0)),
    ("the monday after easter", datetime(2027, 3, 29, 0, 0)),
])
def test_a_weekday_counts_as_one(utterance, expected):
    assert extract_holiday_span(utterance, "en-US", REF) == (expected, "")


def test_a_clock_after_a_counted_offset_is_read_on_the_moved_day():
    """25 December + 2 days, at 09:00."""
    got = _holiday_answer("two days after christmas at 9am", "en-US", REF)
    assert tuple(got) == (datetime(2026, 12, 27, 9, 0), "", True)


def test_words_consumed_after_the_holiday_are_no_offset_of_it():
    """chronologia consumes "a few days after" behind Christmas as well; the
    offset of Christmas cannot be told apart, so the holiday is read alone."""
    got = extract_holiday_span(
        "a day before christmas a few days after easter", "en-US", REF)
    assert tuple(got) == (CHRISTMAS, "a day before a few days after easter")


def test_a_holiday_word_left_over_is_no_offset_of_the_holiday():
    """chronologia reads "two days after friday" and leaves "good friday";
    the holiday layer answers Good Friday, 26 March 2027."""
    got = extract_holiday_span("two days after friday good friday", "en-US",
                               REF)
    assert tuple(got) == (datetime(2027, 3, 26, 0, 0), "two days after friday")


@pytest.mark.parametrize("lang,utterance,expected", [
    ("fr-FR", "noël 10h", datetime(2026, 12, 25, 10, 0)),
    ("fr-FR", "10h noël", datetime(2026, 12, 25, 10, 0)),
    ("fr-FR", "noël 9h30", datetime(2026, 12, 25, 9, 30)),
    ("pt-PT", "natal 10h", datetime(2026, 12, 25, 10, 0)),
])
def test_a_clock_beside_the_holiday_is_the_time_of_it(lang, utterance,
                                                      expected):
    """chronologia reads "10h" as the clock of the holiday and consumes it."""
    assert extract_holiday_span(utterance, lang, REF) == (expected, "")


@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1004")
def test_the_same_question_reads_the_same_in_english_and_french():
    """The French question asked about Christmas and was answered Christmas Eve."""
    english = extract_datetime("how many days until christmas", "en-US", REF)
    french = extract_datetime("combien de jours avant noël", "fr-FR", REF)
    assert english[0] == french[0] == CHRISTMAS


#: A question that asks for the count names the holiday itself. The plural
#: unit has no number, so it is no offset, and the question stays in the
#: remainder.
QUESTIONS_THAT_ASK_FOR_THE_COUNT = [
    ("fr-FR", "combien de jours avant noël", CHRISTMAS, "combien de jours avant"),
    ("fr-FR", "combien de jours après noël", CHRISTMAS, "combien de jours après"),
    ("fr-FR", "combien de semaines avant pâques", EASTER,
     "combien de semaines avant"),
    ("en-US", "how many days before christmas", CHRISTMAS,
     "how many days before"),
    ("en-US", "how many days after christmas", CHRISTMAS, "how many days after"),
    ("en-US", "how many days before christmas at 9am", CHRISTMAS,
     "how many days before at 9am"),
    ("es-ES", "cuántos días antes de navidad", CHRISTMAS,
     "cuántos días antes de"),
    ("es-ES", "cuántos días faltan para navidad", CHRISTMAS,
     "cuántos días faltan para"),
    ("de-DE", "wie viele Tage vor Weihnachten", CHRISTMAS, "wie viele Tage vor"),
    ("de-DE", "wie viele Tage bis Weihnachten", CHRISTMAS, "wie viele Tage bis"),
    ("nl-NL", "hoeveel dagen voor kerst", CHRISTMAS, "hoeveel dagen voor"),
    ("pt-PT", "quantos dias antes do natal", CHRISTMAS, "quantos dias antes do"),
    ("pt-PT", "quantos dias faltam para o natal", CHRISTMAS,
     "quantos dias faltam para"),
]


@pytest.mark.parametrize("lang,utterance,expected,kept",
                         QUESTIONS_THAT_ASK_FOR_THE_COUNT)
def test_a_question_for_the_count_is_no_offset(lang, utterance, expected,
                                               kept):
    assert extract_holiday_span(utterance, lang, REF) == (expected, kept)


@pytest.mark.parametrize("lang,utterance,expected", [
    # 25 December 2026 - 1 day; Easter 28 March 2027 - 7 days
    ("fr-FR", "un jour avant noël", datetime(2026, 12, 24, 0, 0)),
    ("en-US", "a week before easter", datetime(2027, 3, 21, 0, 0)),
])
def test_a_singular_unit_is_a_count_of_one(lang, utterance, expected):
    """The control for the cell above: a unit with an article is counted."""
    assert extract_holiday_span(utterance, lang, REF) == (expected, "")


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


def test_two_days_after_christmas_counts_from_christmas():
    """Christmas 2026 is 25 December, and two days after it is the 27th.

    chronologia reads the whole phrase, so the offset counts from the
    holiday and not from the anchor.
    """
    got = extract_datetime("two days after christmas", "en-US", REF)
    assert got is not None
    assert got[0] == datetime(2026, 12, 27, 0, 0)
    assert got[1] == ""

    # the control: the layer the walk skipped has the right answer
    layer = extract_holiday_span("two days after christmas", "en-US", REF)
    assert layer[0] == datetime(2026, 12, 27, 0, 0)


@pytest.mark.parametrize("lang,plain,written", _known_defects([
    ("fr-FR", "noel", "noël"),
    ("fr-FR", "paques", "pâques"),
    ("fr-FR", "combien de jours avant noel", "combien de jours avant noël"),
    ("pt-PT", "pascoa", "páscoa"),
], {"combien de jours avant noel": "https://github.com/TigreGotico/chronologia/issues/1004"}))
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


# --- the part-of-day offset family, T-7350 ---------------------------------

# A part-of-day word written as the offset ("the night before christmas") has
# no unit and no count, so it is no counted offset. chronologia reads it as a
# time of day ON the holiday and drops the direction, so the whole-text answer
# is not used. The holiday answers its own date and the offset words stay in
# the remainder, where a caller can see them. What each utterance names is
# written beside it; the day the library reads it, the cell fails.

PART_OF_DAY_OFFSETS = [
    # lang, utterance, the words handed back, what the utterance names
    ("en-US", "the night before christmas", "the night before",
     "the night of 24 December"),
    ("en-US", "the morning after christmas", "the morning after",
     "the morning of 26 December"),
    ("en-US", "the evening after christmas", "the evening after",
     "the evening of 26 December"),
    ("en-US", "the night after christmas", "the night after",
     "the night of 26 December"),
    ("en-US", "the morning before christmas", "the morning before",
     "the morning of 24 December"),
    ("fr-FR", "le soir avant noël", "le soir avant", "le soir du 24 décembre"),
    ("fr-FR", "le matin après noël", "le matin après", "le matin du 26 décembre"),
    ("pt-PT", "a noite antes do natal", "a noite antes do",
     "a noite de 24 de dezembro"),
]


@pytest.mark.parametrize("lang,utterance,kept,asked", PART_OF_DAY_OFFSETS)
def test_a_part_of_day_offset_is_handed_back_in_the_remainder(
        lang, utterance, kept, asked):
    got = extract_holiday_span(utterance, lang, REF)
    assert tuple(got) == (CHRISTMAS, kept), f"{utterance!r} asks for {asked}"


def test_a_day_offset_is_still_read_correctly():
    """Control: the direction IS honoured for a day offset, so the family
    above blames the part-of-day word and not the offset machinery."""
    got = extract_holiday_span("the day after christmas", "en-US", REF)
    assert got is not None
    assert got[0] == datetime(2026, 12, 26, 0, 0)


#: An offset that is not a whole number of days, counted from the start of
#: the holiday (00:00). Each answer is worked by hand from New Year's Day
#: 2027-01-01 00:00, Christmas 2026-12-25 00:00 and Easter 2027-03-28 00:00.
OFFSETS_NOT_IN_WHOLE_DAYS = [
    # lang, utterance, expected, remainder
    ("en-US", "remind me an hour before new year",      # 1 Jan 00:00 - 1 h
     datetime(2026, 12, 31, 23, 0), "remind me"),
    ("en-US", "remind me half an hour before new year",  # 1 Jan 00:00 - 30 min
     datetime(2026, 12, 31, 23, 30), "remind me"),
    ("en-US", "an hour after christmas",                 # 25 Dec 00:00 + 1 h
     datetime(2026, 12, 25, 1, 0), ""),
    ("en-US", "an hour and a half before christmas",     # 25 Dec - 1 h 30
     datetime(2026, 12, 24, 22, 30), ""),
    ("en-US", "the hour before christmas",               # 25 Dec - 1 h
     datetime(2026, 12, 24, 23, 0), ""),
    ("en-US", "an hour before easter",                   # 28 Mar - 1 h
     datetime(2027, 3, 27, 23, 0), ""),
    ("pt-PT", "lembra-me uma hora antes do natal",       # 25 Dec - 1 h
     datetime(2026, 12, 24, 23, 0), "lembra-me"),
    ("pt-PT", "lembra-me uma hora antes do ano novo",    # 1 Jan - 1 h
     datetime(2026, 12, 31, 23, 0), "lembra-me"),
    ("pt-PT", "meia hora antes do ano novo",             # 1 Jan - 30 min
     datetime(2026, 12, 31, 23, 30), ""),
    ("pt-PT", "uma hora depois do natal",                # 25 Dec + 1 h
     datetime(2026, 12, 25, 1, 0), ""),
    ("pt-PT", "duas horas antes do natal",               # 25 Dec - 2 h
     datetime(2026, 12, 24, 22, 0), ""),
    ("it-IT", "ricordami un'ora prima di capodanno",     # 1 Jan - 1 h
     datetime(2026, 12, 31, 23, 0), "ricordami"),
    ("it-IT", "un'ora dopo natale",                      # 25 Dec + 1 h
     datetime(2026, 12, 25, 1, 0), ""),
    # "few" is 3 in chronologia's English quantifiers, "a" is 1
    ("en-US", "a few hours before christmas",            # 25 Dec - 3 h
     datetime(2026, 12, 24, 21, 0), ""),
]

#: Rows the per-language engine answers first in `extract_datetime`; the
#: holiday layer reads them alone.
OFFSETS_NOT_IN_WHOLE_DAYS_IN_THE_LAYER = [
    ("en-US", "30 minutes before christmas",             # 25 Dec - 30 min
     datetime(2026, 12, 24, 23, 30), ""),
    ("en-US", "half a day after christmas",              # 25 Dec + 12 h
     datetime(2026, 12, 25, 12, 0), ""),
    ("en-US", "three days and a half before christmas",  # 25 Dec - 84 h
     datetime(2026, 12, 21, 12, 0), ""),
    ("en-US", "an hour before christmas at 9am",         # 25 Dec 09:00 - 1 h
     datetime(2026, 12, 25, 8, 0), ""),
    ("pt-PT", "30 minutos antes do natal",               # 25 Dec - 30 min
     datetime(2026, 12, 24, 23, 30), ""),
    ("it-IT", "due ore prima di natale",                 # 25 Dec - 2 h
     datetime(2026, 12, 24, 22, 0), ""),
]


@pytest.mark.parametrize(
    "lang,utterance,expected,kept",
    OFFSETS_NOT_IN_WHOLE_DAYS + OFFSETS_NOT_IN_WHOLE_DAYS_IN_THE_LAYER)
def test_an_offset_not_in_whole_days_is_counted_in_its_unit(
        lang, utterance, expected, kept):
    """chronologia moves a holiday by whole days only. The offset is counted
    here in its own unit, from the start of the holiday."""
    assert extract_holiday_span(utterance, lang, REF) == (expected, kept)


@pytest.mark.parametrize("lang,utterance,expected,kept",
                         OFFSETS_NOT_IN_WHOLE_DAYS)
@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/pull/977")
def test_extract_datetime_counts_an_offset_not_in_whole_days(
        lang, utterance, expected, kept):
    assert tuple(extract_datetime(utterance, lang, REF)) == (expected, kept)


@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/pull/977")
def test_a_default_time_does_not_replace_the_time_an_offset_gives():
    """The offset sets the time of day, so a default time is not applied."""
    got = extract_datetime("remind me an hour before new year", "en-US", REF,
                           default_time=time(9, 0))
    assert tuple(got) == (datetime(2026, 12, 31, 23, 0), "remind me")


def test_a_default_time_still_fills_a_whole_day_offset():
    """A whole-day offset names a day and no time, as the holiday does."""
    got = extract_datetime("the day before christmas", "en-US", REF,
                           default_time=time(9, 0))
    assert tuple(got) == (datetime(2026, 12, 24, 9, 0), "")


@pytest.mark.parametrize("lang,utterance", [
    ("en-US", "two hours and thirty minutes before christmas"),
    ("en-US", "two days and three hours before christmas"),
    ("en-US", "an hour before the day before christmas"),
    ("en-US", "the hour before the friday before christmas"),
])
def test_an_offset_read_only_in_part_is_handed_back(lang, utterance):
    """chronologia reads only "thirty minutes" or "three hours" and leaves
    the rest over, or chains two offsets and moves the hour by a whole day.
    The holiday is read alone, and the whole offset stays in the
    remainder."""
    got = extract_holiday_span(utterance, lang, REF)
    assert tuple(got) == (CHRISTMAS, utterance[:-len(" christmas")])


def test_a_unit_left_over_with_no_count_does_not_stop_the_offset():
    """The words "what day is" leave the unit "day" over, but no count, so
    the offset after them is read: 25 December - 1 day."""
    got = extract_holiday_span("what day is the day before christmas",
                               "en-US", REF)
    assert tuple(got) == (datetime(2026, 12, 24, 0, 0), "what day is")


#: A quarter of an hour, where chronologia reads only "de hora antes de"
#: and leaves the count "un cuarto" over. 25 Dec 00:00 - 15 min is
#: 24 Dec 23:45, - 45 min is 23:15, + 15 min is 25 Dec 00:15.
QUARTERS_OF_AN_HOUR = [
    ("es-ES", "un cuarto de hora antes de navidad",
     datetime(2026, 12, 24, 23, 45), ""),
    ("es-ES", "tres cuartos de hora antes de navidad",
     datetime(2026, 12, 24, 23, 15), ""),
    ("fr-FR", "un quart d'heure avant noël",
     datetime(2026, 12, 24, 23, 45), ""),
    ("fr-FR", "trois quarts d'heure avant noël",
     datetime(2026, 12, 24, 23, 15), ""),
    ("pt-PT", "um quarto de hora antes do natal",
     datetime(2026, 12, 24, 23, 45), ""),
    ("pt-PT", "três quartos de hora antes do natal",
     datetime(2026, 12, 24, 23, 15), ""),
    ("pt-PT", "lembra-me um quarto de hora depois do natal",
     datetime(2026, 12, 25, 0, 15), "lembra-me"),
    ("ca-ES", "un quart d'hora abans de nadal",
     datetime(2026, 12, 24, 23, 45), ""),
    ("gl-ES", "un cuarto de hora antes do nadal",
     datetime(2026, 12, 24, 23, 45), ""),
]

#: Rows the per-language engine answers first in `extract_datetime`.
QUARTERS_OF_AN_HOUR_IN_THE_LAYER = [
    ("it-IT", "un quarto d'ora prima di natale",
     datetime(2026, 12, 24, 23, 45), ""),
    ("it-IT", "tre quarti d'ora prima di natale",
     datetime(2026, 12, 24, 23, 15), ""),
    ("de-DE", "eine viertel Stunde vor Weihnachten",
     datetime(2026, 12, 24, 23, 45), ""),
    # chronologia counts its one hour from 09:00; the quarter is 08:45
    ("es-ES", "recuérdame un cuarto de hora antes de navidad a las 9",
     datetime(2026, 12, 25, 8, 45), "recuérdame"),
    # 0.5 x 0.25 hour = 7.5 min before 25 Dec 00:00
    ("en-US", "half a quarter of an hour before christmas",
     datetime(2026, 12, 24, 23, 52, 30), ""),
    # 0.5 x 2 weeks = 7 days; 0.25 x 4 days = 1 day
    ("en-US", "half of two weeks before christmas",
     datetime(2026, 12, 18, 0, 0), ""),
    ("es-ES", "un cuarto de cuatro días antes de navidad",
     datetime(2026, 12, 24, 0, 0), ""),
    # "ein" is one, "paar" is two: 25 Dec + 2 days
    ("de-DE", "ein paar Tage nach Weihnachten", datetime(2026, 12, 27, 0, 0),
     ""),
]


@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1034")
def test_a_default_time_fills_a_whole_day_offset_with_a_left_over_count():
    """Half of two weeks is 7 days, a day and no time: 18 Dec at 09:00."""
    got = extract_datetime("half of two weeks before christmas", "en-US", REF,
                           default_time=time(9, 0))
    assert tuple(got) == (datetime(2026, 12, 18, 9, 0), "")


@pytest.mark.parametrize(
    "lang,utterance,expected,kept",
    QUARTERS_OF_AN_HOUR + QUARTERS_OF_AN_HOUR_IN_THE_LAYER)
def test_a_count_left_over_before_the_unit_is_part_of_the_offset(
        lang, utterance, expected, kept):
    assert extract_holiday_span(utterance, lang, REF) == (expected, kept)


@pytest.mark.parametrize("lang,utterance,expected,kept", QUARTERS_OF_AN_HOUR)
@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/pull/977")
def test_extract_datetime_reads_a_quarter_of_an_hour(lang, utterance,
                                                     expected, kept):
    assert tuple(extract_datetime(utterance, lang, REF)) == (expected, kept)


@pytest.mark.parametrize("lang,utterance,kept", [
    # "kvart" is a quantifier of 0.25 with no unit: a quarter of what
    ("sv-SE", "en kvart före jul", "en kvart före"),
    # a whole number left over is no part of the count "an hour"
    ("en-US", "remind me 2 an hour before christmas",
     "remind me 2 an hour before"),
    # "en kvart" is one number of 0.25, and "kvart" is counted again
    ("sv-SE", "en kvart timme före jul", "en kvart timme före"),
    # chronologia reads "media hora" and leaves "un cuarto y"
    ("es-ES", "un cuarto y media hora antes de navidad",
     "un cuarto y media hora antes de"),
])
def test_a_count_with_no_unit_or_fraction_is_handed_back(lang, utterance,
                                                         kept):
    assert extract_holiday_span(utterance, lang, REF) == (CHRISTMAS, kept)


@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/pull/977")
def test_extract_datetime_reads_a_quarter_before_the_holiday():
    """Swedish "kvart" alone is "Fifteen minutes of time" (Wiktionary,
    "kvart", Swedish noun, sense 2), so "en kvart före jul" is 23:45 on
    24 December."""
    got = extract_datetime("en kvart före jul", "sv-SE", REF)
    assert tuple(got) == (datetime(2026, 12, 24, 23, 45), "")


#: Easter 2027 is 28 March, the day the EU clocks go forward at 01:00 UTC.
#: Lisbon: Easter starts 00:00 WET = 00:00 UTC; one hour later is 01:00 UTC,
#: which Lisbon writes 02:00 WEST. Berlin: Easter starts 00:00 CET =
#: 23:00 UTC on 27 March; one hour later is 01:00 CET, two hours later is
#: 01:00 UTC, which Berlin writes 03:00 CEST.
OFFSETS_ACROSS_THE_SPRING_FORWARD = [
    ("Europe/Lisbon", "en-US", "an hour after easter",
     "2027-03-28T02:00:00+01:00"),
    ("Europe/Lisbon", "en-US", "two hours after easter",
     "2027-03-28T03:00:00+01:00"),
    ("Europe/Lisbon", "en-US", "an hour before easter",
     "2027-03-27T23:00:00+00:00"),
    ("Europe/Berlin", "de-DE", "eine Stunde nach Ostern",
     "2027-03-28T01:00:00+01:00"),
    ("Europe/Berlin", "de-DE", "zwei Stunden nach Ostern",
     "2027-03-28T03:00:00+02:00"),
]


@pytest.mark.parametrize("zone,lang,utterance,expected",
                         OFFSETS_ACROSS_THE_SPRING_FORWARD)
def test_an_offset_is_elapsed_time_across_a_clock_change(zone, lang,
                                                          utterance, expected):
    anchor = REF.replace(tzinfo=ZoneInfo(zone))
    got = extract_holiday_span(utterance, lang, anchor)
    assert got[0].isoformat() == expected and got[1] == ""


@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/pull/977")
def test_extract_datetime_counts_elapsed_time_across_a_clock_change():
    anchor = REF.replace(tzinfo=ZoneInfo("Europe/Lisbon"))
    got = extract_datetime("uma hora depois da páscoa", "pt-PT", anchor)
    assert got[0].isoformat() == "2027-03-28T02:00:00+01:00"
    assert got[1] == ""


# Whole days move the date on the wall clock, and only the part shorter than
# a day is elapsed time. Each value is counted by hand. Easter 2027 is
# 28 March: Lisbon goes from +00:00 to +01:00 at 01:00 that day, Berlin from
# +01:00 to +02:00 at 02:00. On 31 October 2027 Lisbon goes back from +01:00
# to +00:00 at 02:00, Berlin from +02:00 to +01:00 at 03:00. Halloween is
# 31 October, All Saints 1 November, Remembrance Day 11 November and
# St Patrick's Day 17 March. "ein paar Tage" is two days and "half of two
# weeks" is seven days.
AUTUMN_REF = datetime(2027, 9, 25, 12, 0, 0)
DAYS_ACROSS_A_CLOCK_CHANGE = [
    # spring: the Sunday has 23 hours
    (REF, "Europe/Berlin", "de-DE", "ein paar Tage vor Ostermontag",
     "2027-03-27T00:00:00+01:00"),
    (REF, "Europe/Berlin", "de-DE", "ein paar Tage nach Ostern",
     "2027-03-30T00:00:00+02:00"),
    (REF, "Europe/Lisbon", "en-GB", "half of two weeks before easter monday",
     "2027-03-22T00:00:00+00:00"),
    (REF, "Europe/Lisbon", "en-GB", "half of two weeks after good friday",
     "2027-04-02T00:00:00+01:00"),
    # autumn: the Sunday has 25 hours
    (AUTUMN_REF, "Europe/Berlin", "de-DE", "ein paar Tage nach Halloween",
     "2027-11-02T00:00:00+01:00"),
    (AUTUMN_REF, "Europe/Berlin", "de-DE", "ein paar Tage vor Allerheiligen",
     "2027-10-30T00:00:00+02:00"),
    (AUTUMN_REF, "Europe/Lisbon", "en-GB", "half of two weeks after halloween",
     "2027-11-07T00:00:00+00:00"),
    # whole days on the wall clock, then 12 hours of elapsed time
    (REF, "Europe/Berlin", "en-GB", "a day and a half after easter",
     "2027-03-29T12:00:00+02:00"),
    (REF, "Europe/Berlin", "de-DE", "eineinhalb Tage nach Ostern",
     "2027-03-29T12:00:00+02:00"),
    (REF, "Europe/Lisbon", "en-GB", "a day and a half before easter monday",
     "2027-03-27T12:00:00+00:00"),
    (REF, "Europe/Lisbon", "en-GB", "two and a half days before easter monday",
     "2027-03-26T12:00:00+00:00"),
    (REF, "Europe/Lisbon", "en-GB", "1.5 days after easter",
     "2027-03-29T12:00:00+01:00"),
    (AUTUMN_REF, "Europe/Lisbon", "en-GB", "a day and a half after halloween",
     "2027-11-01T12:00:00+00:00"),
    (AUTUMN_REF, "Europe/Berlin", "de-DE", "eineinhalb Tage nach Halloween",
     "2027-11-01T12:00:00+01:00"),
    # a clock time: chronologia counts "two weeks" from the clock, and the
    # seven days back from that cross the clock change
    (REF, "Europe/Lisbon", "en-GB",
     "half of two weeks after st patrick's day at 9am",
     "2027-03-24T09:00:00+00:00"),
    (AUTUMN_REF, "Europe/Berlin", "en-GB",
     "half of two weeks before remembrance day at 9am",
     "2027-11-04T09:00:00+01:00"),
    # the 12 hours after the whole day cross the change: Holy Saturday is
    # 27 March, one day later is 28 March 00:00+01:00, and 12 hours of
    # elapsed time from there is 11:00 UTC
    (REF, "Europe/Berlin", "en-GB", "a day and a half after holy saturday",
     "2027-03-28T13:00:00+02:00"),
    # a wall-clock reading the clocks go back over is the earlier instant:
    # Havana goes from -04:00 to -05:00 at 01:00 on 7 November 2027, so
    # 00:00 happens twice; Madrid goes from +02:00 to +01:00 at 03:00 on
    # 31 October 2027, so 02:30 happens twice
    (AUTUMN_REF, "America/Havana", "en-US",
     "half of two weeks after halloween", "2027-11-07T00:00:00-04:00"),
    (AUTUMN_REF, "Europe/Madrid", "es-ES",
     "un cuarto de cuatro días antes de todos los santos a las 2:30",
     "2027-10-31T02:30:00+02:00"),
    # controls: hours, and half a day, are elapsed time
    (REF, "Europe/Lisbon", "en-GB", "36 hours after easter",
     "2027-03-29T13:00:00+01:00"),
    (REF, "Europe/Berlin", "en-GB", "half a day after easter",
     "2027-03-28T13:00:00+02:00"),
    (AUTUMN_REF, "Europe/Lisbon", "en-GB", "two hours after halloween",
     "2027-10-31T01:00:00+00:00"),
    (AUTUMN_REF, "Europe/Lisbon", "en-GB", "a day and a half before halloween",
     "2027-10-29T12:00:00+01:00"),
]


@pytest.mark.parametrize("ref,zone,lang,utterance,expected",
                         DAYS_ACROSS_A_CLOCK_CHANGE)
def test_whole_days_move_the_wall_clock_across_a_clock_change(
        ref, zone, lang, utterance, expected):
    anchor = ref.replace(tzinfo=ZoneInfo(zone))
    got = extract_holiday_span(utterance, lang, anchor)
    assert got[0].isoformat() == expected and got[1] == ""


def test_extract_datetime_moves_whole_days_on_the_wall_clock():
    anchor = REF.replace(tzinfo=ZoneInfo("Europe/Berlin"))
    got = extract_datetime("ein paar Tage vor Ostermontag", "de-DE", anchor)
    assert got[0].isoformat() == "2027-03-27T00:00:00+01:00"
    assert got[1] == ""
    got = extract_datetime("ein paar Tage vor Ostermontag", "de-DE", anchor,
                           default_time=time(9, 0))
    assert got[0].isoformat() == "2027-03-27T09:00:00+01:00"


# Beirut goes from +02:00 to +03:00 at 00:00 on the last Sunday of March,
# which in 2027 is Easter Day, so that day starts at 01:00. "zwei Tage nach
# Ostern", which chronologia moves itself, is 30 March 00:00.
DAYS_FROM_A_DAY_WITH_NO_MIDNIGHT = [
    ("de-DE", "ein paar Tage nach Ostern", "2027-03-30T00:00:00+03:00"),
    ("de-DE", "zwei Tage nach Ostern", "2027-03-30T00:00:00+03:00"),
    ("en-GB", "a day and a half after easter", "2027-03-29T12:00:00+03:00"),
    ("en-GB", "a day and a half before easter", "2027-03-26T12:00:00+02:00"),
    ("en-GB", "an hour after easter", "2027-03-28T02:00:00+03:00"),
]


@pytest.mark.parametrize("lang,utterance,expected",
                         DAYS_FROM_A_DAY_WITH_NO_MIDNIGHT)
def test_whole_days_count_from_the_holidays_wall_clock(lang, utterance,
                                                       expected):
    anchor = REF.replace(tzinfo=ZoneInfo("Asia/Beirut"))
    got = extract_holiday_span(utterance, lang, anchor)
    assert got[0].isoformat() == expected and got[1] == ""


# chronologia moves the clock by whole days only: "a day and a half before
# christmas at 9am" reads as two days before. Each value is the holiday at
# the clock less the offset, counted by hand: 25 December 09:00 less 36
# hours is 23 December 21:00, less 12 hours is 24 December 21:00, less half
# a week (84 hours) is 21 December 21:00, and less ten and a half days is
# 14 December 21:00.
FRACTIONAL_DAYS_WITH_A_CLOCK = [
    ("en-US", "a day and a half before christmas at 9am",
     datetime(2026, 12, 23, 21, 0)),
    ("en-US", "a day and a half after christmas at 9am",
     datetime(2026, 12, 26, 21, 0)),
    ("en-US", "half a day before christmas at 9am",
     datetime(2026, 12, 24, 21, 0)),
    ("en-US", "half a week before christmas at 9am",
     datetime(2026, 12, 21, 21, 0)),
    ("en-US", "a week and a half before christmas at 9am",
     datetime(2026, 12, 14, 21, 0)),
    ("en-US", "a day and a half before christmas at 11pm",
     datetime(2026, 12, 24, 11, 0)),
    ("de-DE", "eineinhalb Tage vor Weihnachten um 9 Uhr",
     datetime(2026, 12, 23, 21, 0)),
    ("nl-NL", "anderhalve dag voor kerst om 9 uur",
     datetime(2026, 12, 23, 21, 0)),
    ("es-ES", "medio día antes de navidad a las 9",
     datetime(2026, 12, 24, 21, 0)),
    # controls: a whole number of days, and hours, keep chronologia's answer
    ("en-US", "two days before christmas at 9am",
     datetime(2026, 12, 23, 9, 0)),
    ("en-US", "36 hours before christmas at 9am",
     datetime(2026, 12, 23, 21, 0)),
]


@pytest.mark.parametrize("lang,utterance,expected",
                         FRACTIONAL_DAYS_WITH_A_CLOCK)
def test_a_fraction_of_a_day_with_a_clock_is_counted_from_the_clock(
        lang, utterance, expected):
    assert extract_holiday_span(utterance, lang, REF) == (expected, "")


@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/pull/977")
def test_extract_datetime_counts_a_fraction_of_a_day_from_the_clock():
    """Easter Monday 2027 is 29 March; 09:00 less 36 hours is 27 March
    21:00."""
    got = extract_datetime("a day and a half before easter monday at 9am",
                           "en-US", REF)
    assert tuple(got) == (datetime(2027, 3, 27, 21, 0), "")


# The offset is counted from the holiday at the clock wherever the clock
# stands. chronologia reads "at 9am an hour before christmas" as a whole day
# before, at 09:00. 25 December 09:00 less an hour is 08:00, less 36 hours
# is 23 December 21:00. Easter Monday 2027 is 29 March: 06:00 less 12 hours
# is 28 March 18:00, and in Berlin 09:00+02:00 less an hour is 08:00+02:00.
CLOCK_BEFORE_THE_OFFSET = [
    ("en-US", "at 9am an hour before christmas",
     (datetime(2026, 12, 25, 8, 0), "")),
    ("pt-PT", "às 9 uma hora antes do natal",
     (datetime(2026, 12, 25, 8, 0), "")),
    ("es-ES", "a las 9 una hora antes de navidad",
     (datetime(2026, 12, 25, 8, 0), "")),
    ("en-US", "at 9am 36 hours before christmas",
     (datetime(2026, 12, 23, 21, 0), "")),
    ("en-US", "remind me at 9am an hour before christmas",
     (datetime(2026, 12, 25, 8, 0), "remind me")),
    ("en-US", "at 9am a day and a half before christmas",
     (datetime(2026, 12, 23, 21, 0), "")),
    # chronologia reads "um 9 Uhr eine" as 09:01 and leaves the hour with
    # no count, so the holiday is read alone
    ("de-DE", "um 9 Uhr eine Stunde vor Weihnachten",
     (datetime(2026, 12, 25, 0, 0), "um 9 Uhr eine Stunde vor")),
    # chronologia reads "half of two weeks" after a clock as two weeks, so
    # the holiday is read alone
    ("en-US", "at 9am half of two weeks before christmas",
     (datetime(2026, 12, 25, 0, 0), "at 9am half of two weeks before")),
    # an offset that does not move the date is no offset
    ("en-US", "0 days before christmas",
     (datetime(2026, 12, 25, 0, 0), "0 days before")),
    # chronologia reads "a couple" as "a 2": a whole number is no fraction
    ("en-US", "a couple hours before christmas",
     (datetime(2026, 12, 24, 22, 0), "")),
]


@pytest.mark.parametrize("lang,utterance,expected", CLOCK_BEFORE_THE_OFFSET)
def test_the_offset_counts_from_a_clock_before_it(lang, utterance, expected):
    assert extract_holiday_span(utterance, lang, REF) == expected


@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/pull/977")
def test_extract_datetime_counts_from_a_clock_before_the_offset():
    assert extract_datetime("at 6am 12 hours before easter monday", "en-US",
                            REF) == (datetime(2027, 3, 28, 18, 0), "")
    assert extract_datetime("às 9 uma hora antes do natal", "pt-PT",
                            REF) == (datetime(2026, 12, 25, 8, 0), "")


@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1034")
def test_a_default_time_does_not_replace_the_clock_of_an_offset():
    """Easter Monday 2027 is 29 March; seven days before at 09:00 is
    22 March 09:00."""
    got = extract_datetime("half of two weeks before easter monday at 9am",
                           "en-US", REF, default_time=time(18, 0))
    assert tuple(got) == (datetime(2027, 3, 22, 9, 0), "")


def test_a_clock_before_the_offset_in_a_zone():
    anchor = REF.replace(tzinfo=ZoneInfo("Europe/Berlin"))
    got = extract_holiday_span("at 9am an hour before easter monday", "en-US",
                               anchor)
    assert got[0].isoformat() == "2027-03-29T08:00:00+02:00"
    assert got[1] == ""


def test_whole_days_with_a_naive_anchor():
    assert extract_holiday_span("ein paar Tage vor Ostermontag", "de-DE",
                                REF) == (datetime(2027, 3, 27), "")
    assert extract_holiday_span("a day and a half after easter", "en-GB",
                                REF) == (datetime(2027, 3, 29, 12), "")


def test_another_date_word_does_not_replace_the_holiday():
    """A parse of the whole text reads "remind me friday about good friday"
    as Friday 2 October with "good friday" left over. That date is not the
    holiday's, so the layer answers Good Friday, 26 March 2027."""
    got = extract_holiday_span("remind me friday about good friday", "en-US",
                               REF)
    assert tuple(got) == (datetime(2027, 3, 26, 0, 0), "remind me friday about")


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


#: The routed reader takes the "on" that opens the date with the date, so it
#: does not stay in the remainder; the holiday layer leaves it there.
_ROUTED_REMAINDER = {
    "remind me on to call mum": "remind me to call mum",
    "remind me at home on": "remind me at home",
}


@pytest.mark.parametrize("lang,utterance,expected,remainder",
                         HOLIDAYS_WITH_A_CLOCK_TIME)
def test_extract_datetime_keeps_the_time_of_a_holiday(
        lang, utterance, expected, remainder):
    # a routed locale answers through chronologia as a list, the holiday
    # layer as a tuple; the values are what is asserted
    remainder = _ROUTED_REMAINDER.get(remainder, remainder)
    assert tuple(extract_datetime(utterance, lang, REF)) == (expected,
                                                             remainder)


#: Holidays whose name is no calendar word, so the engine reads only the clock
#: and answers with the day that clock next comes round (26 September 2026).
#: 25 December is Christmas by decree; Christmas Eve is the day before.
HOLIDAYS_THE_ENGINE_READS_ONLY_A_CLOCK_BESIDE = [
    ("en-US", "christmas at 9am", datetime(2026, 12, 25, 9, 0), ""),
    ("en-US", "christmas at 9 am", datetime(2026, 12, 25, 9, 0), ""),
    ("en-US", "christmas 9am", datetime(2026, 12, 25, 9, 0), ""),
    ("en-US", "christmas eve at noon", datetime(2026, 12, 24, 12, 0), ""),
    # "um" is the clock's own preposition, so it is not left over
    ("de-DE", "weihnachten um 18:30", datetime(2026, 12, 25, 18, 30), ""),
    ("de-DE", "ostern um 9 uhr", datetime(2027, 3, 28, 9, 0), ""),
    ("fr-FR", "pâques à 9 heures", datetime(2027, 3, 28, 9, 0), ""),
    ("es-ES", "navidad a las 9", datetime(2026, 12, 25, 9, 0), ""),
]


@pytest.mark.parametrize("lang,utterance,expected,remainder",
                         HOLIDAYS_THE_ENGINE_READS_ONLY_A_CLOCK_BESIDE)
def test_a_clock_beside_a_holiday_name_is_not_the_engines_next_day(
        lang, utterance, expected, remainder):
    remainder = _ROUTED_REMAINDER.get(remainder, remainder)
    assert tuple(extract_datetime(utterance, lang, REF)) == (expected,
                                                             remainder)


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


@pytest.mark.parametrize("lang,utterance,expected", _known_defects(
    CLOCK_NOT_BESIDE_THE_HOLIDAY, dict.fromkeys(
        ("buy christmas presents at 5pm", "play christmas music at 9pm",
         "christmas island at 9am", "musique de noël à 21 heures",
         "geschenke für weihnachten um 17 uhr kaufen"),
        "https://github.com/TigreGotico/chronologia/issues/1035")))
def test_a_clock_that_is_not_the_holidays_keeps_the_engines_day(
        lang, utterance, expected):
    got = extract_datetime(utterance, lang, REF)
    assert got is not None
    assert got[0] == expected


#: REF is Friday 25 September 2026 12:00. "friday" said on a Friday is that
#: day (ruling 6). A bare weekday with a clock that has passed is the next
#: one (ruling 16), so "friday at 9am" is 2 October 09:00. A named day keeps
#: the spoken hour (ruling 17), so "tomorrow at 9am" is the 26th at 09:00.
DATE_WORD_BESIDE_THE_CLOCK = [
    ("play christmas music on friday", datetime(2026, 9, 25, 0, 0)),
    ("play christmas music on friday at 9am", datetime(2026, 10, 2, 9, 0)),
    ("remind me on friday at 9am about christmas", datetime(2026, 10, 2, 9, 0)),
    ("remind me at 9am on friday about christmas", datetime(2026, 10, 2, 9, 0)),
    ("christmas tomorrow at 9am", datetime(2026, 9, 26, 9, 0)),
]


@pytest.mark.parametrize("utterance,expected", _known_defects(
    DATE_WORD_BESIDE_THE_CLOCK, dict.fromkeys(
        ("play christmas music on friday",
         "play christmas music on friday at 9am",
         "remind me on friday at 9am about christmas",
         "remind me at 9am on friday about christmas",
         "christmas tomorrow at 9am"),
        "https://github.com/TigreGotico/chronologia/issues/1035")))
def test_a_date_word_beside_the_clock_keeps_the_engines_date(utterance,
                                                             expected):
    """The engine read a date word as well as the clock, so the holiday does
    not replace its answer, and the answer keeps both the day and the clock."""
    got = extract_datetime(utterance, "en-US", REF)
    assert got is not None
    assert got[0] == expected


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
    assert tuple(got) == (expected, "")


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


@pytest.mark.xfail(strict=True,
                   reason="https://github.com/TigreGotico/chronologia/issues/1035")
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


@pytest.mark.parametrize("utterance,expected", _known_defects(
    WEEKDAY_OUTSIDE_THE_HOLIDAY_PHRASES,
    {"good friday plans, remind me friday": "https://github.com/TigreGotico/chronologia/issues/1035"}))
def test_a_weekday_outside_the_holiday_phrase_keeps_the_engine_answer(
        utterance, expected):
    got = extract_datetime(utterance, "en-US", REF)
    assert got is not None
    assert got[0].date() == expected


@pytest.mark.xfail(strict=True,
                   reason="https://github.com/TigreGotico/chronologia/issues/1035")
def test_a_relative_phrase_the_engine_keeps_is_not_taken():
    """Control, the opposite call on a phrase of the same shape.

    "good friday and next friday" carries a Friday outside the holiday phrase,
    so the engine keeps the utterance. 25 September 2026 is a Friday, so the
    next one is 2 October.
    """
    got = extract_datetime("good friday and next friday", "en-US", REF)
    assert got is not None
    assert got[0].date() == date(2026, 10, 2)


# A relative phrase on a holiday word counts from the holiday. The dates the
# phrases name: the Friday before Good Friday (26 March 2027) is 19 March, and
# the Monday after Easter Monday (29 March 2027) is 5 April.
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
@pytest.mark.xfail(strict=True,
                   reason="https://github.com/TigreGotico/chronologia/issues/1035")
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


class TestHolidayAnchorZone:
    """A holiday answer is in the anchor's zone, like every other answer."""

    def test_aware_anchor_gives_an_aware_holiday(self):
        import pytz
        from ovos_date_parser import extract_datetime
        tz = pytz.timezone("Europe/Copenhagen")
        anchor = tz.localize(datetime(2026, 10, 1, 9, 0))
        holiday, _ = extract_datetime("christmas", anchorDate=anchor, lang="en-US")
        assert holiday.tzinfo is not None
        assert (holiday.year, holiday.month, holiday.day, holiday.hour) == (2026, 12, 25, 0)
        assert holiday.utcoffset().total_seconds() == 3600  # CET in December
        assert holiday > anchor  # comparable with an aware now

    def test_zoneinfo_anchor(self):
        from zoneinfo import ZoneInfo
        from ovos_date_parser import extract_datetime
        anchor = datetime(2026, 10, 1, 9, 0, tzinfo=ZoneInfo("America/New_York"))
        holiday, _ = extract_datetime("christmas", anchorDate=anchor, lang="en-US")
        assert holiday == datetime(2026, 12, 25, tzinfo=ZoneInfo("America/New_York"))

    def test_naive_anchor_stays_naive(self):
        from ovos_date_parser import extract_datetime
        holiday, _ = extract_datetime("christmas", anchorDate=datetime(2026, 10, 1), lang="en-US")
        assert holiday.tzinfo is None


class TestHolidayDiscontinuity:
    """The wall-clock-to-instant seam at a DST discontinuity, through
    chronologia's resolve_wall_clock: no guess, a defined answer."""

    def test_midnight_gap_answers_the_start_of_the_day(self):
        # Santiago springs forward at midnight on 6 September 2026:
        # 00:00 -04 never happens, the day begins at 01:00 -03
        from zoneinfo import ZoneInfo
        from ovos_date_parser.holidays import _in_anchor_zone
        zone = ZoneInfo("America/Santiago")
        anchor = datetime(2026, 9, 1, 9, 0, tzinfo=zone)
        got = _in_anchor_zone(datetime(2026, 9, 6), anchor)
        assert (got.day, got.hour, got.minute) == (6, 1, 0)
        assert got.utcoffset().total_seconds() == -3 * 3600

    def test_midnight_fold_answers_the_earlier_instant(self):
        # Havana falls back at 01:00 to 00:00 on 1 November 2026:
        # midnight happens twice, the first one (-04) is the answer
        from zoneinfo import ZoneInfo
        from ovos_date_parser.holidays import _in_anchor_zone
        zone = ZoneInfo("America/Havana")
        anchor = datetime(2026, 10, 1, 9, 0, tzinfo=zone)
        got = _in_anchor_zone(datetime(2026, 11, 1), anchor)
        assert (got.day, got.hour) == (1, 0)
        assert got.utcoffset().total_seconds() == -4 * 3600

    def test_a_pytz_zone_does_not_read_local_mean_time(self):
        import pytz
        from ovos_date_parser.holidays import _in_anchor_zone
        anchor = pytz.timezone("Europe/Copenhagen").localize(datetime(2026, 10, 1, 9))
        got = _in_anchor_zone(datetime(2026, 12, 25), anchor)
        assert got.utcoffset().total_seconds() == 3600  # not LMT +00:53

    def test_a_fixed_offset_anchor(self):
        from datetime import timedelta, timezone
        from ovos_date_parser.holidays import _in_anchor_zone
        zone = timezone(timedelta(hours=5, minutes=30))
        got = _in_anchor_zone(datetime(2026, 12, 25),
                              datetime(2026, 10, 1, tzinfo=zone))
        assert got == datetime(2026, 12, 25, tzinfo=zone)


#: A range that opens at the anchor answers the date it reaches. The expected
#: value is date arithmetic on the anchor, Friday 2026-03-13 being two days
#: after the Wednesday 2026-03-11.
RANGE_FROM_NOW = [
    ("de", "bis freitag", datetime(2026, 3, 13), "bis"),
    ("en", "until friday", datetime(2026, 3, 13), "until"),
    ("en", "until 5pm", datetime(2026, 3, 11, 17), "until"),
    ("en", "until june", datetime(2026, 6, 1), "until"),
]


@pytest.mark.parametrize("lang,utterance,expected,remainder", RANGE_FROM_NOW)
def test_a_range_from_now_answers_the_date_it_reaches(
        lang, utterance, expected, remainder):
    anchor = datetime(2026, 3, 11, 10, 0)
    found = extract_datetime(utterance, lang, anchor)
    assert (found[0], found[1]) == (expected, remainder)
