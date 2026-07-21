"""English era/epoch vocabulary: "44 BC", "2000 years before present".

This module is *vocabulary only* — the scanning, epoch resolution and
in-range/AstroDate return rule live in the language-agnostic
:mod:`ovos_date_parser.eras_scan`; the epochs themselves (with their
canonical citations) in :mod:`ovos_date_parser.eras`.  A new language is
added by writing the equivalent pattern table for that language's era
phrasing, nothing more.

Recognised English phrasing (case-insensitive; spelled-out numbers are
normalised to digits first, so "forty four BC" works):

* ``44 BC`` / ``44 B.C.`` / ``44 BCE`` — before the common era
* ``500 AD`` / ``AD 500`` / ``500 CE`` / ``anno domini 500`` — common era
* ``[in] the year 12000`` — common era, unbounded
* ``2000 BP`` / ``2000 [years] before [the] present`` — radiocarbon BP
  (present = AD 1950; Stuiver & Polach 1977)
* ``unix time 1000000000`` / ``unix timestamp ...`` / ``epoch time ...``
* ``julian day [number] 2451545``
* ``holocene era 12025`` / ``human era 12025`` / ``12025 HE``
  (bare ``HE`` only with a 5+ digit year — "he" is an English pronoun,
  and every Holocene year for a CE date is >= 10001)
* ``anno mundi 5786`` / ``5786 anno mundi`` (never bare "AM": that is a
  clock-time meridiem)
* ``the 3rd century BC`` / ``the 2nd millennium BCE`` — scoped ordinals on
  the BC axis (the AD-axis forms already resolve via ``get_date_ordinal``)

Era words that double as ordinary English ("ad", "ce", "he", "am") only
match immediately adjacent to a number, mirroring the permissive-parse-
then-validate stance used across the parser libs.
"""
import re
from typing import Optional

from ovos_number_parser.numbers_en import numbers_to_digits_en

from ovos_date_parser.eras_scan import EraPatterns, extract_era_date

#: ordinal suffix on digits ("3rd" -> 3)
_ORD = r"(\d+)\s*(?:st|nd|rd|th)?"
#: BCE / BC / B.C. / B.C.E.
_BC = r"(?:bce?|b\.c\.e?\.?)"

#: Ordered vocabulary; longer, more specific phrasing first so "2000
#: years before present" is not half-consumed by a shorter pattern.
ERA_PATTERNS_EN: EraPatterns = [
    ("__century_bc__",
     re.compile(rf"\b(?:the\s+)?{_ORD}\s+century\s+{_BC}(?=\W|$)",
                re.IGNORECASE)),
    ("__millennium_bc__",
     re.compile(rf"\b(?:the\s+)?{_ORD}\s+millennium\s+{_BC}(?=\W|$)",
                re.IGNORECASE)),
    ("before_present",
     re.compile(r"\b(\d+)\s+years?\s+before\s+(?:the\s+)?present(?=\W|$)",
                re.IGNORECASE)),
    ("before_present",
     re.compile(r"\b(\d+)\s*(?:bp|b\.p\.)(?=\W|$)", re.IGNORECASE)),
    ("unix",
     re.compile(r"\b(?:unix|epoch)\s+time(?:stamp)?\s+(-?\d+)(?=\W|$)",
                re.IGNORECASE)),
    ("julian_day",
     re.compile(r"\bjulian\s+day\s+(?:number\s+)?(-?\d+)(?=\W|$)",
                re.IGNORECASE)),
    ("holocene",
     re.compile(r"\b(?:holocene|human)\s+era\s+(\d+)(?=\W|$)",
                re.IGNORECASE)),
    # bare "HE" collides with the English pronoun, so it only counts with a
    # 5+ digit year; smaller counts need the era spelled out
    ("holocene",
     re.compile(r"\b(?:(\d{5,})\s+he|(\d+)\s+(?:holocene|human)\s+era)"
                r"(?=\W|$)", re.IGNORECASE)),
    ("anno_mundi",
     re.compile(r"\banno\s+mundi\s+(\d+)(?=\W|$)", re.IGNORECASE)),
    ("anno_mundi",
     re.compile(r"\b(\d+)\s+anno\s+mundi(?=\W|$)", re.IGNORECASE)),
    ("before_christ",
     re.compile(rf"\b(?:(?:in|of)\s+)?(?:the\s+)?year\s+(\d+)\s*{_BC}"
                r"(?=\W|$)", re.IGNORECASE)),
    ("before_christ",
     re.compile(rf"\b(\d+)\s*{_BC}(?=\W|$)", re.IGNORECASE)),
    ("common_era",
     re.compile(r"\b(?:anno\s+domini|ad|a\.d\.)\s+(\d+)(?=\W|$)",
                re.IGNORECASE)),
    ("common_era",
     re.compile(r"\b(\d+)\s*(?:ad|a\.d\.|ce|c\.e\.|"
                r"anno\s+domini|common\s+era)(?=\W|$)", re.IGNORECASE)),
    ("__bare_year__",
     re.compile(r"\b(?:in\s+)?the\s+year\s+(\d+)(?=\W|$)", re.IGNORECASE)),
]


def extract_era_date_en(text: str):
    """Extract an era-qualified date from English text.

    Thin wrapper binding :data:`ERA_PATTERNS_EN` and the English
    spelled-number normaliser to the shared scanner — see
    :func:`ovos_date_parser.eras_scan.extract_era_date` for the contract.
    """
    return extract_era_date(
        text, ERA_PATTERNS_EN,
        normalize=lambda s: numbers_to_digits_en(s, ordinals=True))
