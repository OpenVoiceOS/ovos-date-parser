"""nice_duration accepts a timedelta and returns the same text as the equal
number of whole seconds."""
from datetime import timedelta

import pytest

from ovos_date_parser import nice_duration

DELTA = timedelta(days=2, hours=1, minutes=5, seconds=3)
SECONDS = 2 * 86400 + 3903
LANGS = ["ar", "az", "pl", "ru", "uk", "en", "pt", "de", "es", "fr", "it", "nl"]


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("speech", [True, False])
@pytest.mark.parametrize("delta,seconds", [
    (timedelta(hours=1, minutes=5, seconds=3), 3903),
    (DELTA, SECONDS),
])
def test_timedelta_equals_seconds(lang, speech, delta, seconds):
    expected = nice_duration(seconds, lang, speech=speech)
    assert expected
    assert nice_duration(delta, lang, speech=speech) == expected


def test_pl_exact_strings():
    delta = timedelta(hours=1, minutes=5, seconds=3)
    assert nice_duration(delta, "pl") == "jedna godzina pięć minut trzy sekundy"
    assert nice_duration(delta, "pl", speech=False) == "1:05:03"
