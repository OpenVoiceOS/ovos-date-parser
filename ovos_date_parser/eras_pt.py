"""Portuguese era/epoch vocabulary: "44 a.C.", "2000 anos antes do presente".

Vocabulary-only module over the shared scanner
(:mod:`ovos_date_parser.eras_scan`), mirroring
:mod:`ovos_date_parser.eras_en`.

Recognised Portuguese phrasing (case-insensitive; spelled-out numbers are
normalised to digits first):

* ``44 a.C.`` / ``44 aC`` / ``44 antes de Cristo`` — antes da era comum
* ``44 a.e.c.`` / ``antes da era comum`` — the secular equivalent
* ``500 d.C.`` / ``500 depois de Cristo`` / ``500 e.c.`` /
  ``500 da era comum`` — era comum
* ``no ano 12000`` / ``o ano 12000`` — era comum, unbounded
* ``2000 AP`` / ``2000 anos antes do presente`` — radiocarbon BP
  (presente = AD 1950; Stuiver & Polach 1977; "AP" is the Portuguese
  radiocarbon abbreviation, *antes do presente*)
* ``tempo unix 1000000000`` / ``timestamp unix ...``
* ``dia juliano [número] 2451545``
* ``era holocena 12025`` / ``era humana 12025``
* ``anno mundi 5786``
* ``o 3º século a.C.`` / ``o 2º milénio a.C.`` (also ``milênio``, the
  Brazilian orthography) — scoped ordinals on the BC axis

"aC"/"dC"/"AP" only match immediately adjacent to a number, mirroring the
permissive-parse-then-validate stance used across the parser libs.
"""
import re

from ovos_number_parser.numbers_pt import PT_PT

from ovos_date_parser.eras_scan import EraPatterns, extract_era_date

#: ordinal marker on digits ("3º"/"3ª"/"3o"/"3a" -> 3)
_ORD = r"(\d+)\s*(?:[ºªoa]|\.[ºª])?"
#: a.C. / aC / a.e.c. / antes de Cristo / antes da era comum
_AC = r"(?:a\.?\s?c\.?|a\.?e\.?c\.?|antes\s+de\s+cristo|antes\s+da\s+era\s+comum)"
#: d.C. / dC / e.c. / depois de Cristo / da era comum
_DC = r"(?:d\.?\s?c\.?|e\.?c\.?|depois\s+de\s+cristo|d[ae]\s+era\s+comum)"

ERA_PATTERNS_PT: EraPatterns = [
    ("__century_bc__",
     re.compile(rf"\b(?:o\s+)?{_ORD}\s+s[ée]culo\s+{_AC}(?=\W|$)"
                rf"|\bs[ée]culo\s+{_ORD}\s+{_AC}(?=\W|$)", re.IGNORECASE)),
    ("__millennium_bc__",
     re.compile(rf"\b(?:o\s+)?{_ORD}\s+mil[éê]nio\s+{_AC}(?=\W|$)"
                rf"|\bmil[éê]nio\s+{_ORD}\s+{_AC}(?=\W|$)", re.IGNORECASE)),
    ("before_present",
     re.compile(r"\b(\d+)\s+anos\s+antes\s+do\s+presente(?=\W|$)",
                re.IGNORECASE)),
    ("before_present",
     re.compile(r"\b(\d+)\s*(?:ap|a\.p\.)(?=\W|$)", re.IGNORECASE)),
    ("unix",
     re.compile(r"\b(?:tempo|timestamp)\s+unix\s+(-?\d+)(?=\W|$)",
                re.IGNORECASE)),
    ("julian_day",
     re.compile(r"\bdia\s+juliano\s+(?:n[úu]mero\s+)?(-?\d+)(?=\W|$)",
                re.IGNORECASE)),
    ("holocene",
     re.compile(r"\bera\s+(?:holocena|humana)\s+(\d+)(?=\W|$)",
                re.IGNORECASE)),
    ("anno_mundi",
     re.compile(r"\banno\s+mundi\s+(\d+)(?=\W|$)", re.IGNORECASE)),
    ("before_christ",
     re.compile(rf"\b(?:(?:no|do|o)\s+)?ano\s+(?:de\s+)?(\d+)\s*{_AC}"
                r"(?=\W|$)", re.IGNORECASE)),
    ("before_christ",
     re.compile(rf"\b(\d+)\s*{_AC}(?=\W|$)", re.IGNORECASE)),
    ("common_era",
     re.compile(rf"\b(\d+)\s*{_DC}(?=\W|$)", re.IGNORECASE)),
    ("__bare_year__",
     re.compile(r"\b(?:n?o\s+)?ano\s+(?:de\s+)?(\d+)(?=\W|$)",
                re.IGNORECASE)),
]


def extract_era_date_pt(text: str):
    """Extract an era-qualified date from Portuguese text.

    Thin wrapper binding :data:`ERA_PATTERNS_PT` and the Portuguese
    spelled-number normaliser to the shared scanner — see
    :func:`ovos_date_parser.eras_scan.extract_era_date` for the contract.
    """
    return extract_era_date(text, ERA_PATTERNS_PT,
                            normalize=PT_PT.numbers_to_digits)
