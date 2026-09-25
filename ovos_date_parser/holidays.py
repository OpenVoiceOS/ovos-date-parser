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

Reading that trace costs a full chronologia parse — a second and a half for
a long sentence — and :func:`ovos_date_parser.extract_datetime_spans` asks
this layer about every window of every utterance, so the trace sits behind a
cheap door: a text written with no holiday phrase of its language never
reaches it. The door is chronologia's table too, widened only by the leading
clippings speech uses, and it decides nothing on its own.
"""
from __future__ import annotations

import re
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
        surfaces: Set[str] = set(holiday_surfaces(base))
        try:
            from chronologia.extract.loader import load_lang_spec
            surfaces.update(load_lang_spec(base).holidays)
        except Exception:
            pass
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
    language. It is a door, not a decision — the trace behind it still reads
    the real words.
    """
    words = re.findall(r"\w+(?:'\w+)?", text.lower())
    return " ".join(re.sub(r"(?:'s|s)$", "", w) or w for w in words)


def _names_a_holiday(text: str, lang: str) -> bool:
    """Whether ``text`` is written with any holiday phrase of ``lang``."""
    loose = _loosen(text)
    return any(re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", loose)
               for phrase in _holiday_phrases(lang))


def _holiday_won(text: str, lang: str, anchor: datetime) -> bool:
    """Whether a holiday construction is what chronologia matched in ``text``."""
    try:
        from chronologia import explain
        from chronologia.extract.loader import load_lang_spec
        trace = explain(text, load_lang_spec(_base_lang(lang)), anchor)
    except Exception:
        return False
    for won in trace.winners:
        match = won.match
        if match.construction in _HOLIDAY_CONSTRUCTIONS:
            return True
        if "HOLIDAY" in (match.slots or {}):
            return True
    return False


def extract_holiday_span(text: str, lang: str,
                         anchorDate: Optional[datetime] = None
                         ) -> Optional[Tuple[datetime, str]]:
    """Resolve a named holiday in ``text`` to ``(datetime, remainder)``.

    The date is the occurrence the utterance asks for — the next one by
    default, and the one its tense names when it carries one ("next easter",
    "last christmas") — as chronologia reckons it from ``anchorDate``.

    Returns None when the utterance names no holiday in its own language,
    when chronologia declines the phrase, or when chronologia answered from
    something other than a holiday.
    """
    if not text:
        return None
    if not _names_a_holiday(text, lang):
        return None
    anchor = anchorDate or datetime.now()
    if not _holiday_won(text, lang, anchor):
        return None
    try:
        from chronologia import extract_timespan
        result = extract_timespan(text, lang=_base_lang(lang), anchor=anchor,
                                  jurisdiction=_jurisdiction(lang))
    except Exception:
        return None
    if result is None:
        return None
    start = result.span.start_datetime
    if start is None:  # a span outside the datetime range
        return None
    remainder = re.sub(r"\s{2,}", " ", (result.remainder or "")).strip()
    return start, remainder


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
