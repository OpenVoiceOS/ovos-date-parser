"""Named holidays ("christmas", "noël", "próxima páscoa") as dates.

A holiday name is a date reference like any other, but it is not a calendar
construction: no amount of month and weekday vocabulary turns "easter" into
28 March 2027. The rule behind the name, and the surfaces each language
speaks it by, live in :mod:`chronologia` — the ``civil_holidays`` package
holds the rules, and the extraction grammar of each locale holds the
phrasings. This module is the wiring only. No holiday table, no date rule
and no per-language holiday vocabulary is copied into this library;
chronologia is the source, and a language chronologia carries no holiday
data for simply extracts no holiday.

Why this layer reads chronologia's trace instead of calling it through
--------------------------------------------------------------------
chronologia's extractor reads far more than holidays. Handing it every
utterance this library's own engines made nothing of would quietly replace
those engines for a whole class of inputs, and would answer "the fourteenth"
or "in five minutes" from another library's grammar. So the answer is kept
only when chronologia says a *holiday construction* is what won the match:
:func:`chronologia.explain` names the construction behind every winning
match, and the three holiday constructions are enumerated in
:data:`_HOLIDAY_CONSTRUCTIONS`. Everything else is declined and the caller's
"no date found" stands.

Reading that trace needs chronologia's language spec, and
:func:`ovos_date_parser.extract_datetime_spans` asks this layer about every
window of every utterance. The spec is loaded once per language and kept
(``load_lang_spec`` compiles a locale on every call and caches nothing,
about a second each), and the trace itself sits behind a cheap door: a text
written with no holiday phrase of its language never reaches it. The door is
chronologia's table too, widened only by the leading clippings speech uses
and by the accents a transcript drops, and it decides nothing on its own.

What the answer covers is the matched construction's own extent, and nothing
around it. chronologia states a tense inside the construction it belongs to —
"next easter", "christmas eve", "veille de noël" each come back as one match
over all their words — but applies a modifier written outside the
construction to the result, taking those words out of its remainder with it.
Reading the extent keeps the tense the phrase states and leaves the question
its own words, so "how many days until christmas" and "combien de jours
avant noël" answer alike.
"""
from __future__ import annotations

import re
import threading
import unicodedata
from collections import Counter
from datetime import date, datetime
from typing import Dict, FrozenSet, Optional, Set, Tuple

#: The constructions chronologia resolves a named holiday with, enumerated
#: from the ``constructions`` tables of every packaged ``locale/*/lang.json``
#: (three of the 54 construction names across all locales name a holiday;
#: ``year_ref`` is a bare year and is not one of them). A match whose slots
#: carry ``HOLIDAY`` counts too, so a locale that adds a fourth holiday
#: construction is read without a change here.
_HOLIDAY_CONSTRUCTIONS = frozenset({"holiday_ref", "holiday_eve",
                                    "new_year_ref"})

#: language code -> {spoken surface: chronologia well-known key}. Cached only
#: to avoid rebuilding chronologia's table on every utterance.
_SURFACES: Dict[str, Dict[str, str]] = {}

#: language code -> chronologia's loaded language spec. ``load_lang_spec``
#: reads a locale directory and compiles its constructions on every call and
#: caches nothing, which costs about a second. The trace this layer reads
#: needs the spec, and :func:`ovos_date_parser.extract_datetime_spans` asks
#: this layer about every window of every utterance, so an uncached spec cost
#: one second per window: 15 to 30 seconds for one sentence carrying a
#: holiday word. The spec is a value, not a session, so one per language is
#: kept here and the second call costs nothing.
_SPECS: Dict[str, object] = {}
_SPEC_LOCK = threading.Lock()

#: language code -> {accent-folded surface: the surface as the language
#: writes it}. Speech to text drops accents, and chronologia's surface table
#: holds only the written form, so "noel" matched nothing while "noël" read
#: 25 December. Only a folded form of the SAME length is kept, so a
#: substitution never moves a character offset.
_FOLDED: Dict[str, Dict[str, str]] = {}

#: language code -> the holiday phrases that language speaks, each also
#: kept as its multi-word leading clippings. The cheap door in front of the
#: trace: reading the trace costs a full chronologia parse, and
#: :func:`extract_datetime_spans` asks this layer about every window of every
#: utterance, so a text with no holiday phrase in it is turned away before
#: that parse happens.
_HOLIDAY_PHRASES: Dict[str, FrozenSet[str]] = {}


def _base_lang(lang: str) -> str:
    """The language subtag of a BCP-47 code, lowercased ("pt-PT" -> "pt")."""
    return re.split(r"[-_]", lang)[0].lower()


def _jurisdiction(lang: str) -> Optional[str]:
    """The ISO country of a BCP-47 code, uppercased ("pt-PT" -> "PT").

    chronologia scopes a construction that depends on a country by
    jurisdiction, so the locale's own country is passed on when the code
    carries one. A bare language code names no country and scopes nothing.
    """
    for part in re.split(r"[-_]", lang)[1:]:
        if len(part) == 2 and part.isalpha():
            return part.upper()
    return None


def holiday_surfaces(lang: str) -> Dict[str, str]:
    """Every well-known holiday surface ``lang`` speaks, to chronologia's key.

    chronologia's own table, exposed here so a caller can ask which holidays
    a language names without importing the reckoning core. It is a reference,
    not the extraction gate: the extraction grammar of a locale reads
    phrasings this table does not list, such as the bare English "new year".
    """
    base = _base_lang(lang)
    if base not in _SURFACES:
        try:
            from chronologia.civil_holidays import well_known_surfaces
            _SURFACES[base] = dict(well_known_surfaces(base))
        except Exception:
            _SURFACES[base] = {}
    return _SURFACES[base]


def _holiday_surface_forms(lang: str) -> Set[str]:
    """Every holiday surface ``lang`` speaks, as chronologia holds it.

    Read from chronologia twice over: the extraction spec's own holiday
    table, which is what its grammar matches, and the well-known surfaces,
    which carry the spoken aliases. A language chronologia has no data for
    contributes nothing.
    """
    surfaces: Set[str] = set(holiday_surfaces(lang))
    try:
        surfaces.update(_spec(lang).holidays)
    except Exception:
        pass
    return surfaces


def _holiday_phrases(lang: str) -> FrozenSet[str]:
    """Every holiday phrase ``lang`` speaks, with its leading clippings.

    Read from chronologia twice over: the extraction spec's own holiday
    table, which is what its grammar matches, and the well-known surfaces,
    which carry the spoken aliases. Each phrase also contributes its
    multi-word leading clippings, because speech clips a holiday's name from
    the end — English says "new year" for the day the table calls "new
    year's day" — and the clipping is what the grammar then reads. A single
    word is never a clipping: "new" alone names no holiday, and admitting it
    would open this door to every utterance that happens to use the word.

    Phrases are held in the loose form :func:`_loosen` gives them, because
    the clipped name is not only shorter than the table's: it also drops the
    possessive and the plural the full name carries. The looseness costs
    nothing in precision here, because the trace behind this door decides.
    """
    base = _base_lang(lang)
    if base not in _HOLIDAY_PHRASES:
        surfaces: Set[str] = set(_holiday_surface_forms(base))
        phrases: Set[str] = set()
        for surface in surfaces:
            words = _loosen(surface).split()
            phrases.add(" ".join(words))
            for cut in range(2, len(words)):
                phrases.add(" ".join(words[:cut]))
        _HOLIDAY_PHRASES[base] = frozenset(p for p in phrases if p)
    return _HOLIDAY_PHRASES[base]


def _loosen(text: str) -> str:
    """``text`` lowercased, with the possessive and the plural taken off.

    A clipped holiday name differs from the table's full name by more than
    its missing words: English clips "new year's day" to "new year", losing
    the apostrophe and the s as well. Comparing both sides in this loose form
    lets the door recognise the clipping without a rule written for one
    language. The accents go the same way, because a transcript drops them
    and the door must not turn away a holiday the speaker named. It is a
    door, not a decision — the trace behind it still reads the real words,
    which :func:`_as_written` restores first.
    """
    words = re.findall(r"\w+(?:'\w+)?", _fold(text))
    return " ".join(re.sub(r"(?:'s|s)$", "", w) or w for w in words)


def _names_a_holiday(text: str, lang: str) -> bool:
    """Whether ``text`` is written with any holiday phrase of ``lang``."""
    loose = _loosen(text)
    return any(re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", loose)
               for phrase in _holiday_phrases(lang))


def _spec(lang: str):
    """chronologia's language spec for ``lang``, loaded once per language."""
    base = _base_lang(lang)
    spec = _SPECS.get(base)
    if spec is None:
        with _SPEC_LOCK:
            spec = _SPECS.get(base)
            if spec is None:
                from chronologia.extract.loader import load_lang_spec
                spec = _SPECS[base] = load_lang_spec(base)
    return spec


def _fold(text: str) -> str:
    """``text`` lowercased with its diacritics removed ("noël" -> "noel")."""
    stripped = "".join(c for c in unicodedata.normalize("NFD", text.lower())
                       if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", stripped)


def _folded_surfaces(lang: str) -> Dict[str, str]:
    """Accent-folded surface -> the surface as ``lang`` writes it.

    Built from chronologia's own tables, never hand-listed. A surface whose
    folded form is a different length is left out: the folded text is handed
    to chronologia in place of the written one, and an offset that moved
    would make the extent point at the wrong characters.
    """
    base = _base_lang(lang)
    if base not in _FOLDED:
        out: Dict[str, str] = {}
        for surface in _holiday_surface_forms(base):
            folded = _fold(surface)
            if folded != surface and len(folded) == len(surface):
                out.setdefault(folded, surface)
        _FOLDED[base] = out
    return _FOLDED[base]


def _as_written(text: str, lang: str) -> str:
    """``text`` with an unaccented holiday surface put back as written.

    A transcript that lost its accents names the holiday no less than one
    that kept them, but chronologia matches the written form. Each
    substitution replaces the same number of characters, so every offset in
    the answer still points into the caller's own text.
    """
    folded = _folded_surfaces(lang)
    if not folded:
        return text
    out = text
    for form, written in folded.items():
        if form in _fold(out):
            out = re.sub(rf"(?<!\w){re.escape(form)}(?!\w)", written, out,
                         flags=re.IGNORECASE)
    return out


def _holiday_extent(text: str, lang: str, anchor: datetime
                    ) -> Optional[Tuple[int, int]]:
    """The characters of ``text`` a holiday construction matched, or None.

    The gate and the extent are one question, asked once: a holiday reading
    is kept only when a winning match is a holiday construction, and what it
    matched is exactly the characters that construction covers.

    The extent is the whole answer to what the holiday phrase is. chronologia
    reports the tense a construction carries inside it -- "next easter",
    "last christmas", "christmas eve" and "veille de noël" each come back as
    one match over all their words -- while a modifier outside the
    construction, as in "combien de jours avant noël", is applied to the
    result without being part of the match. Reading the extent therefore
    keeps the tense the phrase states and leaves a word the question owns in
    the remainder, where "how many days until christmas" already left it.
    """
    try:
        from chronologia import explain
        trace = explain(text, _spec(lang), anchor)
    except Exception:
        return None
    for won in trace.winners:
        match = won.match
        if (match.construction not in _HOLIDAY_CONSTRUCTIONS
                and "HOLIDAY" not in (match.slots or {})):
            continue
        try:
            tokens = trace.tokens[match.span[0]:match.span[1]]
            return (min(t.char_start for t in tokens),
                    max(t.char_end for t in tokens))
        except Exception:
            return None
    return None


def _caller_spelling(text: str, written: str, remainder: str) -> Optional[str]:
    """``remainder``, which is cut from ``written``, re-spelled from ``text``.

    :func:`_as_written` may have put an accent back that the caller never
    typed, and the remainder is handed to the caller, so it must come back in
    the caller's own characters. Every substitution there replaces the same
    number of characters, so the two strings are the same length and a
    position in one is the same position in the other; that equality is
    checked rather than assumed, and a mismatch returns None so the caller can
    fall back.

    Each word of the remainder is found in ``written`` left to right, never
    searched for in the whole string, so a word that occurs twice takes its
    own occurrence. A word that is not found returns None: chronologia owns
    the remainder's spelling and may normalise a word one day, and a wrong
    offset must not be guessed at.
    """
    if len(written) != len(text):
        return None
    out = []
    at = 0
    for word in remainder.split():
        found = written.find(word, at)
        if found < 0:
            return None
        out.append(text[found:found + len(word)])
        at = found + len(word)
    return " ".join(out)


def _clock_extent(text: str, lang: str, anchor: datetime,
                  holiday: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    """The characters of the one clock time that stands beside the holiday.

    "good friday at 9am" holds two constructions, the holiday and a clock
    time. None is returned unless exactly one clock time sits outside the
    holiday's characters, so a text with two clock times keeps the holiday
    alone rather than guess which time belongs to it.
    """
    try:
        from chronologia import explain
        trace = explain(text, _spec(lang), anchor)
        extents = []
        for won in trace.winners:
            if won.match.construction != "clock_time":
                continue
            tokens = trace.tokens[won.match.span[0]:won.match.span[1]]
            extents.append((min(t.char_start for t in tokens),
                            max(t.char_end for t in tokens)))
    except Exception:
        return None
    outside = [e for e in extents if e[1] <= holiday[0] or e[0] >= holiday[1]]
    return outside[0] if len(extents) == 1 and outside else None


def extract_holiday_span(text: str, lang: str,
                         anchorDate: Optional[datetime] = None
                         ) -> Optional[Tuple[datetime, str]]:
    """Resolve a named holiday in ``text`` to ``(datetime, remainder)``.

    The date is the occurrence the phrase asks for: the next one by default,
    the one a determiner inside the phrase names when it carries one ("next
    easter", "last christmas", "christmas eve"), and the one an offset
    outside the phrase names ("the day after christmas", "two days after
    christmas", "le jour après noël"), as chronologia reckons it from
    ``anchorDate``. A verb tense is not read — "when was easter" answers with
    the next Easter, because chronologia reads no verb — so this claims the
    determiner and the offset, never the verb.

    The whole text is parsed, not the holiday construction's own characters.
    Parsing the substring was what lost the offset: a modifier outside the
    construction was never applied, so "the day after christmas" answered
    25 December and handed "the day after" back as though it were question
    words. :func:`_holiday_extent` stays, as the gate alone: a holiday
    reading is kept only when a winning match is a holiday construction. What
    the answer covers is then chronologia's to say, and it says it through
    ``DateSpanResult.remainder``.

    The remainder is therefore chronologia's, re-spelled with the caller's own
    characters by :func:`_caller_spelling`, and it keeps every word the parse
    did not consume: "how many days until christmas" and "quantos dias faltam
    para o natal" both answer with Christmas and both keep their question.

    **One known wrong answer, and it is chronologia's.** The French "combien
    de jours avant noël" asks how many days remain before Christmas, so the
    date is Christmas, and this answers 24 December with the remainder
    "combien": chronologia reads "avant" after an interrogative quantity as an
    offset. The English "how many days until christmas" and the French
    "combien de jours jusqu'a noël" are both read correctly. Telling the two
    French shapes apart needs a table of interrogatives per language, which
    belongs to chronologia and is not copied here.
    ``test_holidays_chronologia.py`` carries a cell holding that answer, so
    the day chronologia fixes it the cell says so.

    **A part-of-day offset is read as a time of day on the holiday, and the
    direction is dropped.** "the night before christmas" answers 21:00 on
    25 December, not the night of the 24th, and "the morning after christmas"
    answers 06:00 on the 25th, not the morning of the 26th. The before and the
    after make no difference to the answer, and every row of this family comes
    back with an EMPTY remainder, so a caller cannot see that the modifier was
    read at all. Eight rows are measured, in English, French and Portuguese.

    This is the same defect as the French row above and is chronologia's in the
    same way: the day offset is read correctly, so "the day after christmas"
    gives 26 December, and only the part-of-day word is misread. Task T-7350
    carries it. ``test_holidays_chronologia.py`` holds all eight answers in one
    parametrised cell, so the day chronologia fixes any of them the cell says
    which.

    Returns None when the utterance names no holiday in its own language, or
    when chronologia answered from something other than a holiday.
    """
    answer = _holiday_answer(text, lang, anchorDate)
    return answer[:2] if answer is not None else None


def _holiday_answer(text: str, lang: str, anchorDate: Optional[datetime]
                    ) -> Optional[Tuple[datetime, str, bool]]:
    """:func:`extract_holiday_span` plus whether a clock time was read.

    The flag tells a caller that a midnight in the answer was said ("good
    friday at midnight") and is not the absence of a time of day.
    """
    if not text:
        return None
    if not _names_a_holiday(text, lang):
        return None
    anchor = anchorDate or datetime.now()
    written = _as_written(text, lang)
    extent = _holiday_extent(written, lang, anchor)
    if extent is None:
        return None
    try:
        from chronologia import extract_timespan
        result = extract_timespan(written, lang=_base_lang(lang),
                                  anchor=anchor,
                                  jurisdiction=_jurisdiction(lang))
    except Exception:
        return None
    if result is None:
        return None
    start = result.span.start_datetime
    if start is None:  # a span outside the datetime range
        return None
    first, last = extent
    clock_read = False
    cut = [(first, last)]
    clock = _clock_extent(written, lang, anchor, (first, last))
    if clock is not None and not (_words(written[clock[0]:clock[1]])
                                  <= _words(result.remainder)):
        # chronologia can win a clock_time match and still leave its words
        # in the remainder ("easter at 25:00"); only a clock it consumed
        # counts as read.
        clock_read = True
        cut.append(clock)
    remainder = _caller_spelling(text, written, result.remainder)
    if remainder is None:
        # the offsets do not line up, so the holiday phrase and a clock read
        # beside it are cut out by their extents instead; the date stands,
        # only the remainder falls back
        remainder = text
        for begin, end in sorted(cut, reverse=True):
            remainder = remainder[:begin] + " " + remainder[end:]
    remainder = re.sub(r"\s{2,}", " ", remainder)
    return start.replace(tzinfo=anchor.tzinfo), remainder.strip(), clock_read


def _engine_read_only_a_clock(written: str, lang: str, anchor: datetime,
                              holiday: Tuple[int, int],
                              consumed: FrozenSet[str]) -> bool:
    """Whether the words the engine consumed are a clock time and nothing
    that places a date.

    A word the engine consumed beside the clock counts as a filler ("um" in
    "weihnachten um 18:30") unless chronologia reads it as part of another
    match ("friday", "tomorrow"). The date of such an answer is only the day
    the clock next comes round.
    """
    clock = _clock_extent(written, lang, anchor, holiday)
    if clock is None or not consumed:
        return False
    try:
        from chronologia import explain
        trace = explain(written, _spec(lang), anchor)
        placed = []
        for won in trace.winners:
            tokens = trace.tokens[won.match.span[0]:won.match.span[1]]
            placed.append((min(t.char_start for t in tokens),
                           max(t.char_end for t in tokens)))
    except Exception:
        return False
    for word in re.finditer(r"\w+", written):
        if _fold(word.group()) not in consumed:
            continue
        if clock[0] <= word.start() < clock[1]:
            continue
        if any(begin <= word.start() < end for begin, end in placed):
            return False
    if not _word_set(written[clock[0]:clock[1]]) & consumed:
        return False
    return _clock_is_the_holidays(written, lang, holiday, clock)


def _clock_is_the_holidays(written: str, lang: str, holiday: Tuple[int, int],
                           clock: Tuple[int, int]) -> bool:
    """Whether the clock time is said of the holiday, not of the sentence.

    "christmas at 9am" and "at 9am on christmas" say when the holiday is.
    "play christmas music at 9pm" and "musique de noël à 21 heures" use the
    holiday as an adjective of something else, so the clock is the date.
    The holiday and the clock must touch, with only the locale's own
    connectors (at, on, the) between them. When the holiday comes first, the
    word before it must be one of those connectors or nothing. A genitive
    connector (de, of, van) is not one: it makes the holiday a modifier.
    """
    connectors = _spec(lang).connectors
    linking = set()
    for name in ("at", "on", "in", "until", "article"):
        for surface in connectors.get(name, ()):
            linking.update(_fold(word) for word in re.findall(r"\w+", surface))
    for surface in connectors.get("of", ()):
        linking.difference_update(_fold(word)
                                  for word in re.findall(r"\w+", surface))
    between = written[min(holiday[1], clock[1]):max(holiday[0], clock[0])]
    if any(_fold(word) not in linking for word in re.findall(r"\w+", between)):
        return False
    if clock[0] < holiday[0]:
        return True
    before = re.findall(r"\w+", written[:holiday[0]])
    return not before or _fold(before[-1]) in linking


def holiday_overrides_engine(text: str, lang: str, engine_date: datetime,
                            engine_remainder: str = "",
                            anchorDate: Optional[datetime] = None) -> bool:
    """Whether a language engine read its date out of the holiday phrase.

    A holiday name may be written with calendar vocabulary of its own
    language: "good friday", "palm sunday", "may day". A per-language engine
    reads the weekday inside such a name and answers with the coming Friday,
    and the holiday layer, asked only when the engine found nothing, is never
    reached. The engine order is right everywhere else, so the question asked
    here is narrow: did the engine take its date from the holiday phrase
    itself?

    Args:
        text: the text the engine was given.
        lang: the BCP-47 code the engine was given.
        engine_date: the datetime the engine answered with. Its date is the
            value compared; its time is not read.
        engine_remainder: what the engine left over. Read only by the cheap
            guard below, which declines without a second engine call when the
            engine consumed no word of the holiday phrase.
        anchorDate: the date relative dating is reckoned from.

    The question is answered by asking the engine the holiday phrase on its
    own. The override fires when that answer's date equals ``engine_date``,
    the date the engine gave the whole text. For "good friday" the slice
    "good friday" gives the coming Friday and so does the whole text, so the
    engine read its date out of the phrase. For "play christmas music on
    friday" the slice is "christmas", which the engine cannot read at all, so
    the Friday came from elsewhere and stays the engine's. For "good friday
    and next friday" the slice gives the coming Friday and the whole text
    gives the one after, so the dates differ and the engine keeps its answer.

    When the engine consumed no word of the holiday phrase, the override
    fires only if what it consumed is one clock time and nothing that places
    a date, as in "christmas at 9am": the engine's date is then the day the
    clock next comes round, and the holiday date is the one asked for.

    Only the date is compared, never the time. A time of day beside the
    holiday name does not move the date, so "good friday at 9am" and
    "remind me on good friday at 9am" override exactly as the bare name does.

    The holiday layer answers with a date, so the engine's time of day is not
    carried onto it. "good friday at 9am" gives Good Friday at midnight and
    leaves "at 9am" in the remainder.

    A date word that moves the date keeps the engine's answer, as in "good
    friday and next friday". A word of the holiday phrase that the engine
    consumed and that also stands outside the phrase is a date the speaker
    gave separately, so the engine's answer stands: "remind me friday about
    good friday" is the coming Friday. "the friday before good friday" and
    "monday after easter monday" keep the engine's answer for the same
    reason, which is not the date they name.

    A holiday name takes no indefinite article, so "have a good friday" is a
    weekday and keeps the engine's answer. chronologia matches no holiday
    after an indefinite article, so no extent is found and this declines.

    The engine is asked twice for a text that names a holiday of its
    language, once by the caller and once here, so such a text costs more
    than one that names none. A text that names no holiday pays nothing: the
    table lookup below answers first.
    """
    if not text:
        return False
    if not _names_a_holiday(text, lang):
        return False
    anchor = anchorDate or datetime.now()
    written = _as_written(text, lang)
    extent = _holiday_extent(written, lang, anchor)
    if extent is None:
        return False
    first, last = extent
    phrase_words = _word_set(written[first:last])
    consumed = _word_set(text) - _word_set(engine_remainder)
    outside_words = _word_set(written[:first] + " " + written[last:])
    if consumed & phrase_words & outside_words:
        return False
    if not (consumed & phrase_words):
        # The engine read its date from words the phrase does not cover, so
        # the slice below cannot give the same date except by coincidence.
        # Declining here is what keeps a text that merely names a holiday
        # ("play christmas music on friday") to one engine call. The one
        # exception is a clock time beside the name: "christmas at 9am" has
        # no date word outside the holiday, and the engine's date is only
        # the day its clock next comes round.
        if not _engine_read_only_a_clock(written, lang, anchor, (first, last),
                                         consumed):
            return False
        answer = _holiday_answer(text, lang, anchor)
        return answer is not None and answer[2]
    # imported here, not at module scope: ovos_date_parser/__init__.py imports
    # this module, so a top-level import would be a cycle.
    from ovos_date_parser import _extract_datetime_engine
    inner = _extract_datetime_engine(written[first:last], lang,
                                     anchorDate=anchor)
    return inner is not None and inner[0].date() == engine_date.date()


def _words(text: str) -> Counter:
    """The folded words of ``text`` with their counts, so a word the clock
    shares with the rest of the sentence ("at") is counted once per use."""
    return Counter(_fold(word) for word in re.findall(r"\w+", text or ""))


def _word_set(text: str) -> FrozenSet[str]:
    """The folded words of ``text``, for comparing one extent with another."""
    return frozenset(_fold(word) for word in re.findall(r"\w+", text or ""))


def extract_holiday_date(text: str, lang: str,
                         ref_date: Optional[date] = None
                         ) -> Optional[Tuple[date, str]]:
    """The :func:`extract_holiday_span` answer as ``(date, remainder)``."""
    anchor = None
    if ref_date is not None:
        anchor = (ref_date if isinstance(ref_date, datetime)
                  else datetime(ref_date.year, ref_date.month, ref_date.day))
    got = extract_holiday_span(text, lang, anchorDate=anchor)
    if got is None:
        return None
    moment, remainder = got
    return moment.date(), remainder
