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


def extract_holiday_span(text: str, lang: str,
                         anchorDate: Optional[datetime] = None
                         ) -> Optional[Tuple[datetime, str]]:
    """Resolve a named holiday in ``text`` to ``(datetime, remainder)``.

    The date is the occurrence the holiday phrase asks for: the next one by
    default, and the one a determiner inside the phrase names when it
    carries one ("next easter", "last christmas", "christmas eve"), as
    chronologia reckons it from ``anchorDate``. A verb tense is not read —
    "when was easter" answers with the next Easter, because chronologia
    reads no verb — so this claims the determiner only. A word outside the holiday phrase is not read: it
    stays in the remainder, so "how many days until christmas" and the
    French "combien de jours avant noël" both answer with Christmas and both
    keep their question.

    The remainder is the caller's own text with the holiday phrase cut out of
    it, and nothing else removed.

    Returns None when the utterance names no holiday in its own language, or
    when chronologia answered from something other than a holiday.
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
    first, last = extent
    try:
        from chronologia import extract_timespan
        result = extract_timespan(written[first:last], lang=_base_lang(lang),
                                  anchor=anchor,
                                  jurisdiction=_jurisdiction(lang))
    except Exception:
        return None
    if result is None:
        return None
    start = result.span.start_datetime
    if start is None:  # a span outside the datetime range
        return None
    remainder = re.sub(r"\s{2,}", " ", text[:first] + " " + text[last:])
    return start, remainder.strip()


def holiday_overrides_engine(text: str, lang: str, engine_remainder: str,
                            anchorDate: Optional[datetime] = None) -> bool:
    """Whether a language engine read its date out of the holiday phrase.

    A holiday name may be written with calendar vocabulary of its own
    language: "good friday", "palm sunday", "may day". A per-language engine
    reads the weekday inside such a name and answers with the coming Friday,
    and the holiday layer, asked only when the engine found nothing, is never
    reached. The engine order is right everywhere else, so the question asked
    here is narrow: did the engine take its date from words the holiday phrase
    itself covers?

    The words the engine consumed are ``text`` less its remainder. They lie
    inside the holiday phrase for "good friday", where the engine consumed
    "friday" and left "good", and outside it for "play christmas music on
    friday", where the engine consumed a Friday the phrase "christmas" does
    not cover. The first is the holiday layer's to answer; the second is the
    engine's, and stays so.

    A text that names no holiday of its language never reaches chronologia:
    :func:`_names_a_holiday` is a table lookup and answers first.
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
    return bool(consumed) and consumed <= phrase_words


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
