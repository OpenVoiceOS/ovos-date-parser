"""A month-wide span reads as the CLDR yMMMM pattern of its language.

CLDR availableFormats yMMMM (cldr-dates-full, ca-gregorian.json):

    pt  "MMMM 'de' y"      es  "MMMM 'de' y"      gl  "MMMM 'de' y"
    ast "LLLL 'de' y"
    it, de, fr, nl, sv, da: "MMMM y"

The expected label substitutes nice_month and nice_year into the quoted
pattern, so the oracle is the CLDR string and not the code under test.
"""
import re

import pytest
from chronologia import AstroDate, DateSpan

from ovos_date_parser import nice_month, nice_span, nice_year

CLDR_YMMMM = {
    "pt-pt": "MMMM 'de' y",
    "pt-br": "MMMM 'de' y",
    "es-es": "MMMM 'de' y",
    "gl-es": "MMMM 'de' y",
    "ast-es": "LLLL 'de' y",
    "it-it": "MMMM y",
    "de-de": "MMMM y",
    "fr-fr": "MMMM y",
    "nl-nl": "MMMM y",
    "sv-se": "MMMM y",
    "da-dk": "MMMM y",
}


def _render(pattern, month, year):
    fields = {"MMMM": month, "LLLL": month, "y": year}
    return re.sub(r"'([^']*)'|MMMM|LLLL|y",
                  lambda m: m.group(1) if m.group(1) is not None
                  else fields[m.group(0)], pattern)


def _month_span(year, month):
    end = AstroDate(year + 1, 1, 1) if month == 12 else AstroDate(year, month + 1, 1)
    return DateSpan(AstroDate(year, month, 1), end)


@pytest.mark.parametrize("lang", sorted(CLDR_YMMMM))
def test_month_span_follows_cldr_pattern(lang):
    for month in range(1, 13):
        span = _month_span(2016, month)
        expected = _render(CLDR_YMMMM[lang], nice_month(span.start, lang),
                           nice_year(span.start, lang))
        assert nice_span(span, lang) == expected


def test_month_span_literals():
    march = _month_span(2016, 3)
    assert nice_span(march, "pt-pt") == "março de dois mil e dezasseis"
    assert nice_span(march, "es-es") == "marzo de dos mil dieciséis"
    assert nice_span(march, "PT-PT") == "março de dois mil e dezasseis"


def test_bc_month_span_keeps_the_join():
    span = DateSpan(AstroDate(-299, 1, 1), AstroDate(-299, 2, 1))
    assert nice_span(span, "pt-pt") == "janeiro de trezentos a.C."
