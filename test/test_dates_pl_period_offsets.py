"""Numeric day/week/month/year period-offset tests for Polish.

Both directions must resolve: the future prefix marker "za" and the past suffix
marker "temu". Expected datetimes are hand-derived from a fixed anchor
(2017-06-27 13:04) so engine output can never justify the result.

Past-marker "temu" (sense "przed tym odstępem czasu", example "dwiema godzinami
temu") is documented in the deposited dictionary source, cited so the expected
past direction rests on an external authority:
    ~/AgentWorkspaces/papers/linguistics/pl/wiktionary_temu.html
"""
from datetime import datetime

import pytest

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4, 0)


def _date(text):
    res = extract_datetime(text, anchorDate=ANCHOR, lang="pl")
    assert res is not None, f"no datetime extracted from {text!r}"
    return res[0].replace(tzinfo=None).date()


FUTURE_CASES = [
    ("spotkajmy się za 3 dni", datetime(2017, 6, 30).date()),
    ("za 2 tygodnie", datetime(2017, 7, 11).date()),
    ("za 5 tygodni", datetime(2017, 8, 1).date()),
    ("przypomnij mi za 2 miesiące", datetime(2017, 8, 27).date()),
    ("za 5 miesięcy", datetime(2017, 11, 27).date()),
    ("za 5 lat", datetime(2022, 6, 27).date()),
    ("za 2 lata", datetime(2019, 6, 27).date()),
]

PAST_CASES = [
    ("to było 3 dni temu", datetime(2017, 6, 24).date()),
    ("2 tygodnie temu", datetime(2017, 6, 13).date()),
    ("5 tygodni temu", datetime(2017, 5, 23).date()),
    ("2 miesiące temu", datetime(2017, 4, 27).date()),
    ("5 miesięcy temu", datetime(2017, 1, 27).date()),
    ("5 lat temu", datetime(2012, 6, 27).date()),
    ("2 lata temu", datetime(2015, 6, 27).date()),
]

NON_MATCHES = ["za tygodnie", "2 temu"]


@pytest.mark.parametrize("phrase, expected", FUTURE_CASES)
def test_future_period_offset(phrase, expected):
    assert _date(phrase) == expected


@pytest.mark.parametrize("phrase, expected", PAST_CASES)
def test_past_period_offset(phrase, expected):
    assert _date(phrase) == expected


@pytest.mark.parametrize("phrase", NON_MATCHES)
def test_incomplete_offset_is_not_matched(phrase):
    res = extract_datetime(phrase, anchorDate=ANCHOR, lang="pl")
    assert res is None or res[0].replace(tzinfo=None).date() == ANCHOR.date()
