"""Numeric day/week/month/year period-offset tests for Finnish.

Both directions must resolve: the future postpositions "kuluttua" / "päästä"
and the past postposition "sitten". Expected datetimes are hand-derived from a
fixed anchor (2017-06-27 13:04) so engine output can never justify the result.

Past-marker "sitten" (postposition "ago", "expressing time before now", with a
partitive-case complement "kaksi viikkoa sitten") is documented in the
deposited dictionary source, cited so the past direction rests on an external
authority:
    ~/AgentWorkspaces/papers/linguistics/fi/wiktionary_sitten.html
"""
from datetime import datetime

import pytest

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4, 0)


def _date(text):
    res = extract_datetime(text, anchorDate=ANCHOR, lang="fi")
    assert res is not None, f"no datetime extracted from {text!r}"
    return res[0].replace(tzinfo=None).date()


FUTURE_CASES = [
    ("3 päivän kuluttua", datetime(2017, 6, 30).date()),
    ("3 päivän päästä", datetime(2017, 6, 30).date()),
    ("2 viikon kuluttua", datetime(2017, 7, 11).date()),
    ("2 kuukauden kuluttua", datetime(2017, 8, 27).date()),
    ("5 vuoden kuluttua", datetime(2022, 6, 27).date()),
]

PAST_CASES = [
    ("3 päivää sitten", datetime(2017, 6, 24).date()),
    ("2 viikkoa sitten", datetime(2017, 6, 13).date()),
    ("2 kuukautta sitten", datetime(2017, 4, 27).date()),
    ("5 vuotta sitten", datetime(2012, 6, 27).date()),
]

# Postposition without a preceding numeral must not fabricate an offset.
NON_MATCHES = ["viikon kuluttua", "viikkoa sitten", "2 sitten"]


@pytest.mark.parametrize("phrase, expected", FUTURE_CASES)
def test_future_period_offset(phrase, expected):
    assert _date(phrase) == expected


@pytest.mark.parametrize("phrase, expected", PAST_CASES)
def test_past_period_offset(phrase, expected):
    assert _date(phrase) == expected


@pytest.mark.parametrize("phrase", NON_MATCHES)
def test_incomplete_offset_is_not_matched(phrase):
    res = extract_datetime(phrase, anchorDate=ANCHOR, lang="fi")
    assert res is None or res[0].replace(tzinfo=None).date() == ANCHOR.date()
