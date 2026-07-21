"""Numeric day/week/month/year period-offset tests for Ukrainian.

Both directions must resolve: the future prefix marker "через" and the past
suffix marker "тому". Expected datetimes are hand-derived from a fixed anchor
(2017-06-27 13:04) so engine output can never justify the result.

Past-marker "тому" (adverb / прислівник, sense "указує на час, що минув від
якоїсь дії, події") is documented in the deposited dictionary source, cited so
the expected past direction rests on an external authority:
    ~/AgentWorkspaces/papers/linguistics/uk/wiktionary_tomu.html
"""
from datetime import datetime

import pytest

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4, 0)


def _date(text):
    res = extract_datetime(text, anchorDate=ANCHOR, lang="uk")
    assert res is not None, f"no datetime extracted from {text!r}"
    return res[0].replace(tzinfo=None).date()


FUTURE_CASES = [
    ("зустрінемось через 3 дні", datetime(2017, 6, 30).date()),
    ("через 1 день", datetime(2017, 6, 28).date()),
    ("через 2 тижні", datetime(2017, 7, 11).date()),
    ("нагадай мені через 2 місяці", datetime(2017, 8, 27).date()),
    ("через 5 років", datetime(2022, 6, 27).date()),
    ("через 2 роки", datetime(2019, 6, 27).date()),
]

PAST_CASES = [
    ("це сталося 3 дні тому", datetime(2017, 6, 24).date()),
    ("1 день тому", datetime(2017, 6, 26).date()),
    ("2 тижні тому", datetime(2017, 6, 13).date()),
    ("3 тижнів тому", datetime(2017, 6, 6).date()),
    ("2 місяці тому", datetime(2017, 4, 27).date()),
    ("5 місяців тому", datetime(2017, 1, 27).date()),
    ("5 років тому", datetime(2012, 6, 27).date()),
    ("2 роки тому", datetime(2015, 6, 27).date()),
]

NON_MATCHES = ["2 тому", "через 2"]


@pytest.mark.parametrize("phrase, expected", FUTURE_CASES)
def test_future_period_offset(phrase, expected):
    assert _date(phrase) == expected


@pytest.mark.parametrize("phrase, expected", PAST_CASES)
def test_past_period_offset(phrase, expected):
    assert _date(phrase) == expected


@pytest.mark.parametrize("phrase", NON_MATCHES)
def test_incomplete_offset_is_not_matched(phrase):
    res = extract_datetime(phrase, anchorDate=ANCHOR, lang="uk")
    assert res is None or res[0].replace(tzinfo=None).date() == ANCHOR.date()
