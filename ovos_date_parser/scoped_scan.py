"""Language-agnostic scanning of calendar-scoped ordinals and seasons.

The natural-language layer over ``ranges.py``'s scope arithmetic: "the
third week of june", "the 100th day of the year", "the first decade of
the 21st century", "summer of 1969", "next winter".  Like the era layer
(:mod:`ovos_date_parser.eras_scan`), the surface forms are translatable
resources in ``ovos_date_parser/locale/<lang>/*.voc`` loaded through
ovos-spec-tools; the grammar, the calls into
:func:`~ovos_date_parser.ranges.get_date_ordinal` and the season helpers
live here.

Grammar (all forms optional-article, case-insensitive):

* ``[the] Nth {century|millennium|decade}`` — absolute-axis periods:
  "the 21st century" is the century starting 2000 (the floor-division
  bucket convention of ``get_date_ordinal``, documented there).
* ``[the] {Nth|last} {day|week|month} of {month-name} [YYYY]`` — scoped
  into a month: "the 3rd week of june".
* ``[the] {Nth|last} {day|week|month} of the year [YYYY]`` — scoped into
  a year: "the 100th day of the year".
* ``[the] {Nth|last} {year|decade|century} of the Mth
  {century|millennium}`` — one nesting level: "the first decade of the
  21st century".
* ``[{next|last|this}] {season}`` and ``{season} of YYYY`` — resolved
  with the hemisphere-aware meteorological season tables of ``ranges.py``.

Word-form numbers must already be digits — callers pass the language's
normaliser output (the same convention as the era layer).
"""
import re
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Tuple

from ovos_spec_tools import LocaleResources

from ovos_date_parser.eras_scan import LOCALE_DIR, _alt, _voc_reader
from ovos_date_parser.ranges import (DateTimeResolution, Hemisphere, Season,
                                     get_date_ordinal, last_season_date,
                                     next_season_date, season_to_date)

#: unit name -> the {unit}_OF_{scope} resolutions it participates in
_UNIT_OF_MONTH = {"day": DateTimeResolution.DAY_OF_MONTH,
                  "week": DateTimeResolution.WEEK_OF_MONTH}
_UNIT_OF_YEAR = {"day": DateTimeResolution.DAY_OF_YEAR,
                 "week": DateTimeResolution.WEEK_OF_YEAR,
                 "month": DateTimeResolution.MONTH_OF_YEAR}
_UNIT_OF_CENTURY = {"year": DateTimeResolution.YEAR_OF_CENTURY,
                    "decade": DateTimeResolution.DECADE_OF_CENTURY}
_UNIT_OF_MILLENNIUM = {"year": DateTimeResolution.YEAR_OF_MILLENNIUM,
                       "decade": DateTimeResolution.DECADE_OF_MILLENNIUM,
                       "century": DateTimeResolution.CENTURY_OF_MILLENNIUM}
_ABSOLUTE = {"decade": DateTimeResolution.DECADE,
             "century": DateTimeResolution.CENTURY,
             "millennium": DateTimeResolution.MILLENNIUM}


@dataclass(frozen=True)
class ScopedVocabulary:
    """A language's surface forms, as regex alternations built from its
    ``.voc`` phrase sets by :func:`load_scoped_vocabulary`.

    Every fragment is used inside a larger, case-insensitively compiled
    pattern; fragments must not contain capturing groups (the builder
    escapes all phrases, so this holds by construction).
    """
    #: canonical unit -> alternation of surface forms
    units: Dict[str, str]
    #: month name alternations, January first
    months: List[str]
    #: Season -> alternation of names
    seasons: Dict[Season, str]
    #: ordinal number: exposes ONE capturing group with the digits
    ordinal: str
    #: "the Nth ... OF ..." connector
    of: str
    #: optional article before ordinals/periods
    article: str
    #: "the year" literal used for year-scoped ordinals
    year_word: str
    #: word selecting the final unit in a scope ("the last week of june")
    last_word: str
    #: season qualifiers
    next_word: str
    this_word: str


def _month_alt(line: str) -> str:
    """One month's line from ``months.voc`` as a regex fragment.

    The file is read BY POSITION: line 1 is January and line 12 is December.
    A spelling variant therefore cannot have a line of its own, because an
    extra line shifts every month after it by one and pushes December off
    the end. Variants go on the month's own line, separated by ``|``.

    Each variant is escaped, so nothing in a vocabulary file is ever read as
    a regex. The alternation is wrapped, so the caller can embed the result
    in a larger group without the ``|`` escaping its scope.
    """
    variants = [v.strip() for v in line.split("|") if v.strip()]
    return "(?:" + "|".join(re.escape(v) for v in variants) + ")"


def load_scoped_vocabulary(lang: str,
                           locale_dir: str = LOCALE_DIR
                           ) -> ScopedVocabulary:
    """Build a language's scoped vocabulary from its ``.voc`` phrase sets.

    Files consumed (under ``<locale_dir>/<lang>/``): ``unit_day.voc``,
    ``unit_week.voc``, ``unit_month.voc``, ``unit_year.voc``,
    ``unit_decade.voc``, ``unit_century.voc``, ``unit_millennium.voc``,
    ``months.voc`` (exactly 12 lines, January first, one line per month,
    spelling variants on that line separated by ``|``), ``season_spring.voc``,
    ``season_summer.voc``, ``season_fall.voc``, ``season_winter.voc``,
    ``ordinal_suffixes.voc``, ``marker_of.voc``, ``marker_article.voc``,
    ``marker_year_word.voc``, ``marker_last.voc``, ``marker_next.voc``,
    ``marker_this.voc``.
    """
    read = _voc_reader(lang, locale_dir)

    def voc(name):
        try:
            phrases = read(name)
        except FileNotFoundError:
            return None
        return _alt(phrases) if phrases else None

    months = read("months")
    ord_suf = voc("ordinal_suffixes")
    return ScopedVocabulary(
        units={u: voc(f"unit_{u}") for u in
               ("day", "week", "month", "year", "decade", "century",
                "millennium") if voc(f"unit_{u}")},
        months=[_month_alt(m) for m in months],
        seasons={s: voc(f"season_{n}") for s, n in
                 ((Season.SPRING, "spring"), (Season.SUMMER, "summer"),
                  (Season.FALL, "fall"), (Season.WINTER, "winter"))
                 if voc(f"season_{n}")},
        ordinal=rf"(\d+)\s*(?:{ord_suf})?" if ord_suf else r"(\d+)",
        of=voc("marker_of") or "of",
        article=voc("marker_article") or "the",
        year_word=voc("marker_year_word") or "year",
        last_word=voc("marker_last") or "last",
        next_word=voc("marker_next") or "next",
        this_word=voc("marker_this") or "this",
    )


def _art(vocab):
    # The alternation needs its own group: without it ``\s+`` binds to the
    # last alternative alone, so every other article matches with no space
    # after it and stays in the remainder. ``eras_scan._era_pattern`` writes
    # the same construct with the inner group.
    #
    # The space is required after every article except an elided one.
    # French and Italian write ``l'annee`` and ``l'anno`` with nothing
    # between the article and the noun, so an article that ends in an
    # apostrophe takes no whitespace. The lookbehind reads the character
    # the article ended on, so it costs nothing for the other forms.
    return rf"(?:(?:{vocab.article})(?:\s+|(?<=')))?"


def extract_scoped_date(text: str, vocab: ScopedVocabulary,
                        ref_date: Optional[date] = None,
                        hemisphere: Hemisphere = Hemisphere.NORTH,
                        lang: Optional[str] = None
                        ) -> Optional[Tuple[date, str,
                                            DateTimeResolution]]:
    """Extract a calendar-scoped ordinal, season or named-holiday reference.

    Args:
        text: normalised (digits, lowercase-insensitive) phrase.
        vocab: the language's surface forms.
        ref_date: anchor for relative scopes (default: today via the
            underlying range helpers).
        hemisphere: season table to use.
        lang: the BCP-47 code of ``text``. A named holiday is the one
            reference here whose surfaces are not in ``vocab``: the rule
            behind "easter" lives in :mod:`chronologia`, keyed by language,
            so the holiday reading is offered only when the caller names the
            language. Without it the function reads exactly what it always
            read.

    Returns:
        ``(date, remainder, resolution)`` or ``None`` when no scoped
        phrasing is present. A holiday comes back at
        :attr:`DateTimeResolution.DAY`, the width chronologia gives it.
    """
    if not text:
        return None

    def _finish(match, value, resolution):
        remainder = (text[:match.start()] + text[match.end():]).strip()
        return value, re.sub(r"\s{2,}", " ", remainder), resolution

    art, of = _art(vocab), vocab.of
    ordinal_or_last = rf"(?:{vocab.ordinal}|({vocab.last_word}))"

    # -- "the Nth unit of the Mth century/millennium" (one nesting level)
    for scope_name, unit_map in (("century", _UNIT_OF_CENTURY),
                                 ("millennium", _UNIT_OF_MILLENNIUM)):
        if scope_name not in vocab.units:
            continue
        units = {u: r for u, r in unit_map.items() if u in vocab.units}
        if not units:
            continue
        unit_alt = "|".join(f"(?P<u_{u}>{vocab.units[u]})" for u in units)
        pattern = re.compile(
            rf"\b{art}{ordinal_or_last}\s+(?:{unit_alt})\s+(?:{of})\s+"
            rf"{art}{vocab.ordinal}\s+(?:{vocab.units[scope_name]})(?=\W|$)",
            re.IGNORECASE)
        match = pattern.search(text)
        if match:
            groups = match.groups()
            n = -1 if groups[1] else int(groups[0])
            scope_n = int(groups[-1])
            scope_ref = get_date_ordinal(scope_n,
                                         resolution=_ABSOLUTE[scope_name])
            unit = next(u for u in units if match.group(f"u_{u}"))
            resolution = units[unit]
            return _finish(match, get_date_ordinal(n, scope_ref, resolution),
                           resolution)

    # -- "the Nth day/week of june [1969]" and "... of the year [1969]"
    month_units = {u: r for u, r in _UNIT_OF_MONTH.items()
                   if u in vocab.units}
    year_units = {u: r for u, r in _UNIT_OF_YEAR.items() if u in vocab.units}
    if month_units and vocab.months:
        unit_alt = "|".join(f"(?P<u_{u}>{vocab.units[u]})"
                            for u in month_units)
        month_alt = "|".join(f"(?P<m_{i}>{m})"
                             for i, m in enumerate(vocab.months))
        pattern = re.compile(
            rf"\b{art}{ordinal_or_last}\s+(?:{unit_alt})\s+(?:{of})\s+"
            rf"(?:{month_alt})(?:\s+(\d{{4}}))?(?=\W|$)", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            groups = match.groups()
            n = -1 if groups[1] else int(groups[0])
            index = next((i for i in range(len(vocab.months))
                          if match.group(f"m_{i}")), None)
            if index is None or index >= 12:
                # A months.voc with the wrong number of lines can match a
                # group this loop cannot name a month for. Report no scoped
                # date rather than raising out of a parse.
                return None
            month = index + 1
            year = int(groups[-1]) if groups[-1] else \
                (ref_date.year if ref_date else date.today().year)
            unit = next(u for u in month_units if match.group(f"u_{u}"))
            resolution = month_units[unit]
            scope_ref = date(year, month, 1)
            return _finish(match, get_date_ordinal(n, scope_ref, resolution),
                           resolution)
    if year_units:
        unit_alt = "|".join(f"(?P<u_{u}>{vocab.units[u]})" for u in year_units)
        pattern = re.compile(
            rf"\b{art}{ordinal_or_last}\s+(?:{unit_alt})\s+(?:{of})\s+"
            rf"{art}(?:{vocab.year_word})(?:\s+(\d{{4}}))?(?=\W|$)",
            re.IGNORECASE)
        match = pattern.search(text)
        if match:
            groups = match.groups()
            n = -1 if groups[1] else int(groups[0])
            year = int(groups[-1]) if groups[-1] else \
                (ref_date.year if ref_date else date.today().year)
            unit = next(u for u in year_units if match.group(f"u_{u}"))
            resolution = year_units[unit]
            return _finish(match, get_date_ordinal(n, date(year, 1, 1),
                                                   resolution), resolution)

    # -- absolute periods: "the 21st century", "the 3rd millennium"
    for unit, resolution in _ABSOLUTE.items():
        if unit not in vocab.units:
            continue
        pattern = re.compile(
            rf"\b{art}{vocab.ordinal}\s+(?:{vocab.units[unit]})(?=\W|$)",
            re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return _finish(match,
                           get_date_ordinal(int(match.group(1)),
                                            resolution=resolution),
                           resolution)

    # -- seasons: "summer of 1969", "next summer", "last winter", "summer"
    if vocab.seasons:
        season_alt = "|".join(f"(?P<s_{s.name}>{alt})"
                              for s, alt in vocab.seasons.items())
        pattern = re.compile(
            rf"\b(?:({vocab.next_word})|({vocab.last_word})|"
            rf"({vocab.this_word}))?\s*(?:{season_alt})"
            rf"(?:\s+(?:{of})\s+(\d{{4}}))?(?=\W|$)", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            season = next(s for s in vocab.seasons
                          if match.group(f"s_{s.name}"))
            year = match.groups()[-1]
            if year:
                value = season_to_date(season, int(year), hemisphere)
            elif match.group(2):  # last
                value = last_season_date(season, ref_date, hemisphere)
            elif match.group(1):  # next
                value = next_season_date(season, ref_date, hemisphere)
            else:  # this / bare: the season's start in the anchor year
                value = season_to_date(season, ref_date, hemisphere)
            return _finish(match, value, DateTimeResolution.MONTH)
    # -- a named holiday, the one reference whose surfaces are chronologia's
    if lang:
        from ovos_date_parser.holidays import extract_holiday_date
        got = extract_holiday_date(text, lang, ref_date)
        if got is not None:
            moment, remainder = got
            return moment, remainder, DateTimeResolution.DAY

    return None
