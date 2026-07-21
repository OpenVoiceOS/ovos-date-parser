"""Numeric day/week/month/year period-offset tests for Russian.

Both directions must resolve: the future prefix marker "через" and the past
suffix marker "назад". Expected datetimes are hand-derived from a fixed anchor
(2017-06-27 13:04) so engine output can never justify the result.

Past-marker "назад" (adverb, temporal sense "раньше" / German "vor") is
documented in the deposited dictionary source, cited so the expected past
direction rests on an external authority:
    ~/AgentWorkspaces/papers/linguistics/ru/wiktionary_nazad.html
"""
from datetime import datetime

import pytest

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4, 0)


def _date(text):
    res = extract_datetime(text, anchorDate=ANCHOR, lang="ru")
    assert res is not None, f"no datetime extracted from {text!r}"
    return res[0].replace(tzinfo=None).date()


# (phrase, expected date) — natural sentences, singular/plural/case variants.
FUTURE_CASES = [
    ("встретимся через 3 дня", datetime(2017, 6, 30).date()),
    ("через 1 день", datetime(2017, 6, 28).date()),
    ("через 2 недели", datetime(2017, 7, 11).date()),
    ("напомни мне через 2 месяца", datetime(2017, 8, 27).date()),
    ("через 5 лет", datetime(2022, 6, 27).date()),
    ("через 2 года", datetime(2019, 6, 27).date()),
]

PAST_CASES = [
    ("это случилось 3 дня назад", datetime(2017, 6, 24).date()),
    ("1 день назад", datetime(2017, 6, 26).date()),
    ("2 недели назад", datetime(2017, 6, 13).date()),
    ("3 недель назад", datetime(2017, 6, 6).date()),
    ("2 месяца назад", datetime(2017, 4, 27).date()),
    ("5 месяцев назад", datetime(2017, 1, 27).date()),
    ("5 лет назад", datetime(2012, 6, 27).date()),
    ("2 года назад", datetime(2015, 6, 27).date()),
]

# Marker or number alone must not fabricate a period offset.
NON_MATCHES = ["через недели", "2 назад"]


@pytest.mark.parametrize("phrase, expected", FUTURE_CASES)
def test_future_period_offset(phrase, expected):
    assert _date(phrase) == expected


@pytest.mark.parametrize("phrase, expected", PAST_CASES)
def test_past_period_offset(phrase, expected):
    assert _date(phrase) == expected


@pytest.mark.parametrize("phrase", NON_MATCHES)
def test_incomplete_offset_is_not_matched(phrase):
    res = extract_datetime(phrase, anchorDate=ANCHOR, lang="ru")
    assert res is None or res[0].replace(tzinfo=None).date() == ANCHOR.date()
