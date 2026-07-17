"""Relative future-offset regression tests for the Romance family.

A phrase like "in two hours" must be computed from the anchor time of day,
not from midnight: "dentro de dos horas" at 13:04 resolves to 15:04, never
to 02:00. These tests pin the expected datetimes by hand against a fixed
non-midnight anchor so engine output can never be used to justify the result.
"""
from datetime import datetime

import pytest

from ovos_date_parser import extract_datetime

# Fixed, deliberately non-midnight anchor: 2017-06-27 13:04:00.
ANCHOR = datetime(2017, 6, 27, 13, 4, 0)


def _extract(text, lang):
    res = extract_datetime(text, anchorDate=ANCHOR, lang=lang)
    assert res is not None, f"no datetime extracted from {text!r} ({lang})"
    return res[0]


# Each case: (lang, phrase, expected datetime) — hand-derived from the anchor.
HOUR_OFFSET_CASES = [
    # Spanish
    ("es", "en 2 horas", datetime(2017, 6, 27, 15, 4)),
    ("es", "dentro de 2 horas", datetime(2017, 6, 27, 15, 4)),
    ("es", "en 3 horas", datetime(2017, 6, 27, 16, 4)),
    ("es", "en 5 horas", datetime(2017, 6, 27, 18, 4)),
    # French
    ("fr", "dans 2 heures", datetime(2017, 6, 27, 15, 4)),
    ("fr", "dans deux heures", datetime(2017, 6, 27, 15, 4)),
    ("fr", "dans 5 heures", datetime(2017, 6, 27, 18, 4)),
    # Galician
    ("gl", "dentro de 2 horas", datetime(2017, 6, 27, 15, 4)),
    ("gl", "dentro de 5 horas", datetime(2017, 6, 27, 18, 4)),
    # Portuguese
    ("pt", "em 3 horas", datetime(2017, 6, 27, 16, 4)),
    ("pt", "daqui a 2 horas", datetime(2017, 6, 27, 15, 4)),
    # Italian
    ("it", "tra 2 ore", datetime(2017, 6, 27, 15, 4)),
    ("it", "tra 3 ore", datetime(2017, 6, 27, 16, 4)),
]

MINUTE_OFFSET_CASES = [
    ("es", "en 30 minutos", datetime(2017, 6, 27, 13, 34)),
    ("es", "en 45 minutos", datetime(2017, 6, 27, 13, 49)),
    ("fr", "dans 30 minutes", datetime(2017, 6, 27, 13, 34)),
    ("fr", "dans 45 minutes", datetime(2017, 6, 27, 13, 49)),
    ("gl", "dentro de 30 minutos", datetime(2017, 6, 27, 13, 34)),
    ("gl", "dentro de 45 minutos", datetime(2017, 6, 27, 13, 49)),
    ("pt", "em 45 minutos", datetime(2017, 6, 27, 13, 49)),
    ("it", "tra 45 minuti", datetime(2017, 6, 27, 13, 49)),
]

SECOND_OFFSET_CASES = [
    ("es", "en 10 segundos", datetime(2017, 6, 27, 13, 4, 10)),
    ("fr", "dans 20 secondes", datetime(2017, 6, 27, 13, 4, 20)),
    ("it", "tra 15 secondi", datetime(2017, 6, 27, 13, 4, 15)),
]


@pytest.mark.parametrize("lang, phrase, expected", HOUR_OFFSET_CASES)
def test_relative_hour_offset_from_anchor(lang, phrase, expected):
    assert _extract(phrase, lang).replace(tzinfo=None) == expected


@pytest.mark.parametrize("lang, phrase, expected", MINUTE_OFFSET_CASES)
def test_relative_minute_offset_from_anchor(lang, phrase, expected):
    assert _extract(phrase, lang).replace(tzinfo=None) == expected


@pytest.mark.parametrize("lang, phrase, expected", SECOND_OFFSET_CASES)
def test_relative_second_offset_from_anchor(lang, phrase, expected):
    assert _extract(phrase, lang).replace(tzinfo=None) == expected


# The offset must never collapse to a midnight base (the original bug):
# a correct anchor-relative result stays on the same afternoon.
@pytest.mark.parametrize("lang, phrase, expected", HOUR_OFFSET_CASES)
def test_relative_hour_offset_is_not_from_midnight(lang, phrase, expected):
    result = _extract(phrase, lang).replace(tzinfo=None)
    assert result.hour >= ANCHOR.hour, \
        f"{phrase!r} ({lang}) resolved to {result}, likely computed from midnight"
    assert result.minute == ANCHOR.minute, \
        f"{phrase!r} ({lang}) dropped the anchor minutes"


# Absolute clock parsing must remain unaffected by the fix.
ABSOLUTE_CASES = [
    ("es", "a las 5 de la tarde", (17, 0)),
    ("fr", "à 17h30", (17, 30)),
    ("gl", "ás 5 da tarde", (17, 0)),
]


@pytest.mark.parametrize("lang, phrase, hm", ABSOLUTE_CASES)
def test_absolute_clock_still_parses(lang, phrase, hm):
    result = _extract(phrase, lang)
    assert (result.hour, result.minute) == hm
