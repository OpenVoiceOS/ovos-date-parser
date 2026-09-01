"""Span-native formatting: ``nice_span`` and AstroDate-transparent formatters.

The width of a :class:`~chronologia.DateSpan` *is* its precision, so
``nice_span`` labels a span at the granularity it carries. The contract is
two-sided:

* a hand-written gold corpus fixes the exact English strings, and
* a round-trip gate proves ``extract_timespan(nice_span(span)) == span`` for
  every width chronologia can re-parse.

Every English width from a day up round-trips: weeks through the "week of
<date>" construct, BC days through the era-marked calendar date, BC decades,
centuries and millennia through the scoped-era constructions. Sub-day widths
read as a spoken date and time, which extraction cannot take back, and are
strict xfails.
"""
from datetime import datetime

import pytest

import chronologia as c
from ovos_date_parser import (
    nice_span, nice_time, nice_date, nice_date_time, nice_year,
)
from ovos_date_parser.astrodate import AstroDate, DateSpan


def _span(start, end):
    return DateSpan(start, end)


# --------------------------------------------------------------------------
# Gold corpus -- the exact English label is the contract.
# --------------------------------------------------------------------------

GOLD_EN = [
    (_span(AstroDate(2026, 7, 21), AstroDate(2026, 7, 22)), "July 21st, 2026"),
    (_span(AstroDate(2026, 7, 1), AstroDate(2026, 8, 1)), "July 2026"),
    (_span(AstroDate(2026, 1, 1), AstroDate(2027, 1, 1)), "2026"),
    (_span(AstroDate(1066, 1, 1), AstroDate(1067, 1, 1)), "1066"),
    (_span(AstroDate(1980, 1, 1), AstroDate(1990, 1, 1)), "the 1980s"),
    (_span(AstroDate(2020, 1, 1), AstroDate(2030, 1, 1)), "the 2020s"),
    (_span(AstroDate(1800, 1, 1), AstroDate(1900, 1, 1)), "the 19th century"),
    (_span(AstroDate(1, 1, 1), AstroDate(101, 1, 1)), "the 1st century"),
    (_span(AstroDate(2000, 1, 1), AstroDate(2100, 1, 1)), "the 21st century"),
    (_span(AstroDate(2000, 1, 1), AstroDate(3000, 1, 1)), "the 3rd millennium"),
    # BC eras, formatted symmetrically with extraction phrasing
    (_span(AstroDate(-299, 1, 1), AstroDate(-299, 1, 2)), "January 1st, 300 BC"),
    (_span(AstroDate(-299, 1, 1), AstroDate(-299, 2, 1)), "January 300 BC"),
    (_span(AstroDate(-299, 1, 1), AstroDate(-299, 1, 8)),
     "the week of January 1st, 300 BC"),
    (_span(AstroDate(-299, 1, 1), AstroDate(-298, 1, 1)), "300 BC"),
    (_span(AstroDate(-299, 1, 1), AstroDate(-199, 1, 1)), "the 3rd century BC"),
    (_span(AstroDate(-308, 1, 1), AstroDate(-298, 1, 1)), "the 300s BC"),
    (_span(AstroDate(-1999, 1, 1), AstroDate(-999, 1, 1)), "the 2nd millennium BC"),
]


@pytest.mark.parametrize("span,expected", GOLD_EN,
                         ids=[e for _, e in GOLD_EN])
def test_nice_span_en_gold(span, expected):
    assert nice_span(span, "en") == expected
    # locale suffix must not change the label
    assert nice_span(span, "en-us") == expected


# --------------------------------------------------------------------------
# Round-trip gate: extract_timespan(nice_span(span)) recovers span (English).
# --------------------------------------------------------------------------

ROUNDTRIP_EN = [
    ("day-future", _span(AstroDate(2026, 7, 21), AstroDate(2026, 7, 22))),
    ("day-past", _span(AstroDate(1900, 1, 3), AstroDate(1900, 1, 4))),
    ("month-future", _span(AstroDate(2026, 7, 1), AstroDate(2026, 8, 1))),
    ("month-past", _span(AstroDate(1850, 3, 1), AstroDate(1850, 4, 1))),
    ("year-future", _span(AstroDate(2050, 1, 1), AstroDate(2051, 1, 1))),
    ("year-past", _span(AstroDate(1066, 1, 1), AstroDate(1067, 1, 1))),
    ("decade-past", _span(AstroDate(1980, 1, 1), AstroDate(1990, 1, 1))),
    ("decade-future", _span(AstroDate(2020, 1, 1), AstroDate(2030, 1, 1))),
    ("century-past", _span(AstroDate(1800, 1, 1), AstroDate(1900, 1, 1))),
    ("century-future", _span(AstroDate(2000, 1, 1), AstroDate(2100, 1, 1))),
    ("millennium", _span(AstroDate(2000, 1, 1), AstroDate(3000, 1, 1))),
    ("day-bc", _span(AstroDate(-299, 1, 1), AstroDate(-299, 1, 2))),
    ("month-bc", _span(AstroDate(-299, 1, 1), AstroDate(-299, 2, 1))),
    ("year-bc", _span(AstroDate(-299, 1, 1), AstroDate(-298, 1, 1))),
    ("century-bc", _span(AstroDate(-299, 1, 1), AstroDate(-199, 1, 1))),
    ("millennium-bc", _span(AstroDate(-1999, 1, 1), AstroDate(-999, 1, 1))),
    ("week", _span(AstroDate(2026, 7, 20), AstroDate(2026, 7, 27))),
    # The low end of the gated year range (see NO_ROUNDTRIP_EN for the
    # years just outside it).
    ("day-ad-1000", _span(AstroDate(1000, 1, 1), AstroDate(1000, 1, 2))),
    ("year-ad-1000", _span(AstroDate(1000, 1, 1), AstroDate(1001, 1, 1))),
    ("decade-ad-1000", _span(AstroDate(1000, 1, 1), AstroDate(1010, 1, 1))),
    ("day-bc-32", _span(AstroDate(-31, 3, 15), AstroDate(-31, 3, 16))),
    ("month-bc-32", _span(AstroDate(-31, 3, 1), AstroDate(-31, 4, 1))),
    ("year-bc-1", _span(AstroDate(0, 1, 1), AstroDate(1, 1, 1))),
    ("decade-bc", _span(AstroDate(-308, 1, 1), AstroDate(-298, 1, 1))),
]


@pytest.mark.parametrize("name,span", ROUNDTRIP_EN,
                         ids=[n for n, _ in ROUNDTRIP_EN])
def test_nice_span_en_roundtrip(name, span):
    label = nice_span(span, "en")
    result = c.extract_timespan(label, "en-us")
    assert result is not None, f"{label!r} did not extract"
    got, remainder = result
    assert remainder.strip() == "", f"{label!r} left remainder {remainder!r}"
    assert got.start == span.start and got.end == span.end, (
        f"{label!r} -> {got.start}..{got.end}, wanted {span.start}..{span.end}")




# --------------------------------------------------------------------------
# Cases nice_span labels correctly but extraction cannot read back: sub-day
# widths, BC weeks, and years whose numeral is ambiguous with a day-of-month
# or an anchor-relative decade. Each is a tripwire -- if the round-trip ever
# starts working the case fails loudly and has to be promoted to the gate.
# --------------------------------------------------------------------------

#: A single-digit or two-digit year reads as a day-of-month or an ordinal, and
#: a bare three-digit year does not read as a year at all, so the gate starts
#: at 1000 AD going forward and at 32 BC going back. These cells pin the years
#: just outside that range.
NO_ROUNDTRIP_EN = [
    ("hour", "nice_date_time drops the meridiem, and chronologia reads no "
             "clock reading inside a spoken date",
     _span(AstroDate(2026, 9, 2, 15, 0), AstroDate(2026, 9, 2, 15, 1))),
    ("minute", "nice_date_time drops the meridiem, and chronologia reads no "
               "clock reading inside a spoken date",
     _span(AstroDate(2026, 9, 2, 15, 47), AstroDate(2026, 9, 2, 15, 48))),
    ("week-bc", "chronologia's week resolver projects to a datetime, which "
                "cannot hold a BC year",
     _span(AstroDate(-299, 1, 1), AstroDate(-299, 1, 8))),
    ("day-ad-1", "a bare 1 reads as a day-of-month, not a year",
     _span(AstroDate(1, 1, 1), AstroDate(1, 1, 2))),
    ("year-ad-1", "a bare 1 does not read as a year",
     _span(AstroDate(1, 1, 1), AstroDate(2, 1, 1))),
    ("year-ad-999", "a bare three-digit numeral does not read as a year",
     _span(AstroDate(999, 1, 1), AstroDate(1000, 1, 1))),
    ("decade-ad-990", "a bare decade below 1000 resolves against the anchor's "
                      "century",
     _span(AstroDate(990, 1, 1), AstroDate(1000, 1, 1))),
    ("day-bc-1", "a bare 1 before the era marker reads as a day-of-month",
     _span(AstroDate(0, 3, 15), AstroDate(0, 3, 16))),
    ("day-bc-31", "a BC year up to 31 reads as a day-of-month",
     _span(AstroDate(-30, 3, 15), AstroDate(-30, 3, 16))),
    ("decade-straddling-the-era", "a decade spanning 1 BC to 1 AD labels as "
                                  "'the 0s BC', which has no reading",
     _span(AstroDate(-8, 1, 1), AstroDate(2, 1, 1))),
]


@pytest.mark.parametrize("name,missing,span", NO_ROUNDTRIP_EN,
                         ids=[n for n, _, _ in NO_ROUNDTRIP_EN])
def test_nice_span_en_no_roundtrip(name, missing, span):
    label = nice_span(span, "en")
    try:
        result = c.extract_timespan(label, "en-us")
    except Exception:
        result = None
    recovered = (result is not None
                 and result[1].strip() == ""
                 and result[0].start == span.start
                 and result[0].end == span.end)
    if recovered:
        pytest.fail(f"en {name}: round-trip now works -- promote to the gate")
    pytest.xfail(f"en {name}: {missing}")


# --------------------------------------------------------------------------
# Other languages: labels are written in the language, and the widths with no
# localised construction are refused rather than answered in English.
# --------------------------------------------------------------------------

#: Labels the locale's own word tables produce, at every width nice_span
#: answers for a BC point. The era year is spoken, never the astronomical one.
GOLD_BC_BY_LANG = {
    "en": ["January 1st, 300 BC", "January 300 BC", "300 BC"],
    "pt-pt": ["Sábado, um de Janeiro, trezentos a.C.",
              "Janeiro trezentos a.C.",
              "trezentos a.C."],
    "de-de": ["Samstag, erster Januar, drei hundert v.d.Z.",
              "Januar drei hundert v.d.Z.",
              "drei hundert v.d.Z."],
}

BC_WIDTHS = [
    _span(AstroDate(-299, 1, 1), AstroDate(-299, 1, 2)),
    _span(AstroDate(-299, 1, 1), AstroDate(-299, 2, 1)),
    _span(AstroDate(-299, 1, 1), AstroDate(-298, 1, 1)),
]


@pytest.mark.parametrize("lang", sorted(GOLD_BC_BY_LANG))
def test_nice_span_bc_speaks_the_era_year(lang):
    labels = [nice_span(span, lang) for span in BC_WIDTHS]
    assert labels == GOLD_BC_BY_LANG[lang]
    assert not any("-299" in label for label in labels)


COARSE_WIDTHS = [
    ("decade", _span(AstroDate(1980, 1, 1), AstroDate(1990, 1, 1))),
    ("century", _span(AstroDate(1800, 1, 1), AstroDate(1900, 1, 1))),
    ("millennium", _span(AstroDate(2000, 1, 1), AstroDate(3000, 1, 1))),
]


@pytest.mark.parametrize("lang", ["pt-pt", "de-de", "es-es", "ru-ru", "xx"])
@pytest.mark.parametrize("name,span", COARSE_WIDTHS,
                         ids=[n for n, _ in COARSE_WIDTHS])
def test_nice_span_refuses_unlocalised_coarse_widths(lang, name, span):
    with pytest.raises(NotImplementedError):
        nice_span(span, lang)


# --------------------------------------------------------------------------
# Native-script span labels for the other extractor languages (he, ar).
#
# nice_span now emits the exact native calendar phrasing chronologia's ar/he
# extractors re-parse, so those widths round-trip in native script. Decade
# words in these locales are century-relative (the extractor resolves a bare
# "eighties"/"twenties" against an anchor's century), so the round-trip battery
# pins a fixed anchor to keep the decade case timeless.
# --------------------------------------------------------------------------

#: Fixed anchor so anchor-relative widths (decade words) resolve
#: deterministically -- the same anchor the ar/he extraction corpora use.
_SEMITIC_ANCHOR = datetime(2017, 6, 27, 13, 4)


# Gold corpus -- the exact native string is the contract. Grammar notes cite
# the phrasing chronologia's ar/he extraction corpora assert
# (test/nl_corpus_{ar,he}/): Arabic day/month use bare Gregorian-Arabic month
# names in "DAY MONTH YEAR"/"MONTH YEAR"; Hebrew prefixes the month with ב
# ("in") in a full date but leaves it bare in a month-year; BC uses each
# locale's era marker ("ق.م", the gershayim form "לפנה״ס").
GOLD_AR = [
    (_span(AstroDate(2026, 7, 21), AstroDate(2026, 7, 22)), "21 يوليو 2026"),
    (_span(AstroDate(2026, 7, 1), AstroDate(2026, 8, 1)), "يوليو 2026"),
    (_span(AstroDate(2026, 1, 1), AstroDate(2027, 1, 1)), "2026"),
    (_span(AstroDate(1066, 1, 1), AstroDate(1067, 1, 1)), "1066"),
    (_span(AstroDate(-299, 1, 1), AstroDate(-298, 1, 1)), "300 ق.م"),
    (_span(AstroDate(1980, 1, 1), AstroDate(1990, 1, 1)), "الثمانينات"),
]

GOLD_HE = [
    (_span(AstroDate(2026, 7, 21), AstroDate(2026, 7, 22)), "21 ביולי 2026"),
    (_span(AstroDate(2026, 7, 1), AstroDate(2026, 8, 1)), "יולי 2026"),
    (_span(AstroDate(2026, 1, 1), AstroDate(2027, 1, 1)), "2026"),
    (_span(AstroDate(1066, 1, 1), AstroDate(1067, 1, 1)), "1066"),
    (_span(AstroDate(-299, 1, 1), AstroDate(-298, 1, 1)), "300 לפנה״ס"),
    (_span(AstroDate(1980, 1, 1), AstroDate(1990, 1, 1)), "שנות השמונים"),
]


@pytest.mark.parametrize("span,expected", GOLD_AR,
                         ids=[e for _, e in GOLD_AR])
def test_nice_span_ar_gold(span, expected):
    assert nice_span(span, "ar") == expected


@pytest.mark.parametrize("span,expected", GOLD_HE,
                         ids=[e for _, e in GOLD_HE])
def test_nice_span_he_gold(span, expected):
    assert nice_span(span, "he") == expected


# Widths whose native construction the ar/he extractors accept: these round-trip.
ROUNDTRIP_SEMITIC = [
    ("day", _span(AstroDate(2026, 7, 21), AstroDate(2026, 7, 22))),
    ("day-past", _span(AstroDate(1969, 7, 20), AstroDate(1969, 7, 21))),
    ("month", _span(AstroDate(2026, 7, 1), AstroDate(2026, 8, 1))),
    ("month-past", _span(AstroDate(1929, 10, 1), AstroDate(1929, 11, 1))),
    ("year-future", _span(AstroDate(2050, 1, 1), AstroDate(2051, 1, 1))),
    ("year-past", _span(AstroDate(1066, 1, 1), AstroDate(1067, 1, 1))),
    ("year-bc", _span(AstroDate(-299, 1, 1), AstroDate(-298, 1, 1))),
    ("decade-1980s", _span(AstroDate(1980, 1, 1), AstroDate(1990, 1, 1))),
]


@pytest.mark.parametrize("lang", ["ar", "he"])
@pytest.mark.parametrize("name,span", ROUNDTRIP_SEMITIC,
                         ids=[n for n, _ in ROUNDTRIP_SEMITIC])
def test_nice_span_semitic_roundtrip(lang, name, span):
    label = nice_span(span, lang)
    result = c.extract_timespan(label, lang, _SEMITIC_ANCHOR)
    assert result is not None, f"{lang}: {label!r} did not extract"
    got, remainder = result
    assert remainder.strip() == "", f"{lang}: {label!r} left remainder {remainder!r}"
    assert got.start == span.start and got.end == span.end, (
        f"{lang}: {label!r} -> {got.start}..{got.end}, "
        f"wanted {span.start}..{span.end}")


# Widths ar/he label but the extractors cannot read back. Strict xfails, so the
# day a native construction lands the flip-to-fail forces promotion to the gate
# above. Each case names the missing construction.
NO_CONSTRUCTION_SEMITIC = [
    ("week", "no 'week of <date>' construction",
     _span(AstroDate(2026, 7, 20), AstroDate(2026, 7, 27))),
    ("day-bc", "no calendar_date with an era marker",
     _span(AstroDate(-299, 1, 1), AstroDate(-299, 1, 2))),
    ("month-bc", "no month-year with an era marker",
     _span(AstroDate(-299, 1, 1), AstroDate(-299, 2, 1))),
]

# Coarse widths with no ar/he label at all: refused rather than answered in
# English numerals.
REFUSED_SEMITIC = [
    ("century", _span(AstroDate(1800, 1, 1), AstroDate(1900, 1, 1))),
    ("millennium", _span(AstroDate(2000, 1, 1), AstroDate(3000, 1, 1))),
    ("decade-bc", _span(AstroDate(-308, 1, 1), AstroDate(-298, 1, 1))),
    ("century-bc", _span(AstroDate(-299, 1, 1), AstroDate(-199, 1, 1))),
    ("millennium-bc", _span(AstroDate(-1999, 1, 1), AstroDate(-999, 1, 1))),
]


@pytest.mark.parametrize("lang", ["ar", "he"])
@pytest.mark.parametrize("name,span", REFUSED_SEMITIC,
                         ids=[n for n, _ in REFUSED_SEMITIC])
def test_nice_span_semitic_refuses_unlocalised_widths(lang, name, span):
    with pytest.raises(NotImplementedError):
        nice_span(span, lang)


# The bare ar/he decade word is century-relative: the extractors resolve it
# into the 20th century, so the same word names the 1890s, the 1990s and the
# 2090s. Only the century it can express is answered.
OTHER_CENTURY_DECADES = [
    ("1890s", _span(AstroDate(1890, 1, 1), AstroDate(1900, 1, 1))),
    ("2090s", _span(AstroDate(2090, 1, 1), AstroDate(2100, 1, 1))),
]


@pytest.mark.parametrize("lang", ["ar", "he"])
@pytest.mark.parametrize("name,span", OTHER_CENTURY_DECADES,
                         ids=[n for n, _ in OTHER_CENTURY_DECADES])
def test_nice_span_semitic_refuses_decades_outside_the_named_century(
        lang, name, span):
    with pytest.raises(NotImplementedError):
        nice_span(span, lang)


@pytest.mark.parametrize("lang", ["ar", "he"])
@pytest.mark.parametrize("name,missing,span", NO_CONSTRUCTION_SEMITIC,
                         ids=[n for n, _, _ in NO_CONSTRUCTION_SEMITIC])
def test_nice_span_semitic_no_construction(lang, name, missing, span):
    label = nice_span(span, lang)
    result = c.extract_timespan(label, lang, _SEMITIC_ANCHOR)
    recovered = (result is not None
                 and result[1].strip() == ""
                 and result[0].start == span.start
                 and result[0].end == span.end)
    if recovered:
        pytest.fail(f"{lang} {name}: round-trip now works -- promote to the gate")
    pytest.xfail(f"{lang} {name}: {missing} in chronologia's {lang} locale")


def test_nice_span_type_guard():
    with pytest.raises(TypeError):
        nice_span("July 2026", "en")


# --------------------------------------------------------------------------
# AstroDate transparent formatting: the datetime-shaped formatters accept an
# AstroDate directly, projecting it to a datetime when it fits one.
# --------------------------------------------------------------------------

def test_nice_time_accepts_astrodate():
    ad = AstroDate(2026, 7, 21, 15, 30)
    assert nice_time(ad, "en") == nice_time(ad.datetime(), "en") == "half past three"


def test_nice_date_accepts_astrodate():
    ad = AstroDate(2026, 7, 21, 15, 30)
    assert nice_date(ad, "en") == nice_date(ad.datetime(), "en")
    assert nice_date(ad, "en") == "tuesday, july twenty-first, twenty twenty six"


def test_nice_date_time_accepts_astrodate():
    ad = AstroDate(2026, 7, 21, 15, 30)
    assert nice_date_time(ad, "en") == nice_date_time(ad.datetime(), "en")


def test_nice_year_unbounded_year():
    # A year no datetime can hold still formats -- the year-only path needs
    # nothing a datetime provides.
    assert nice_year(AstroDate(50000, 1, 1), "en") == "50000"


def test_nice_time_out_of_range_astrodate_fails_loudly():
    # A clock reading on a BC point cannot be projected to a datetime; the
    # formatter must raise rather than silently invent a value.
    with pytest.raises((ValueError, OverflowError, AttributeError)):
        nice_time(AstroDate(-200, 1, 1, 3, 0), "en")
