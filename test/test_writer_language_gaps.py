"""Strict xfails for the writers that raise NotImplementedError in an, fy, id and ms.

The forms of these writers are not cited yet, so each row asks for the number
words that ovos-number-parser writes for the same language.
"""
import datetime as dt

import pytest
from ovos_number_parser import pronounce_number

from ovos_date_parser import nice_date, nice_date_time, nice_duration, nice_relative_time, nice_year

ISSUE = "https://github.com/OpenVoiceOS/ovos-date-parser/issues/702"
WHEN = dt.datetime(2026, 11, 25, 15, 10)
FIVE_MINUTES = dt.timedelta(minutes=5)


def xfail_rows(entries):
    return [pytest.param(*entry, marks=pytest.mark.xfail(strict=True, raises=NotImplementedError, reason=ISSUE))
            for entry in entries]


@pytest.mark.parametrize("lang,write,number", xfail_rows([
    ("an", lambda lang: nice_duration(FIVE_MINUTES, lang), 5),
    ("an", lambda lang: nice_relative_time(WHEN + FIVE_MINUTES, WHEN, lang), 5),
    ("fy", lambda lang: nice_duration(FIVE_MINUTES, lang), 5),
    ("fy", lambda lang: nice_relative_time(WHEN + FIVE_MINUTES, WHEN, lang), 5),
    ("id", lambda lang: nice_date(WHEN, lang), 25),
    ("id", lambda lang: nice_date_time(WHEN, lang), 25),
    ("id", lambda lang: nice_year(WHEN, lang), 2026),
    ("ms", lambda lang: nice_date(WHEN, lang), 25),
    ("ms", lambda lang: nice_date_time(WHEN, lang), 25),
    ("ms", lambda lang: nice_year(WHEN, lang), 2026),
]))
def test_the_writer_speaks_its_number(lang, write, number):
    assert pronounce_number(number, lang) in write(lang)


@pytest.mark.parametrize("lang,write,number", [
    ("an", lambda lang: nice_year(WHEN, lang), 2026),
    ("fy", lambda lang: nice_year(WHEN, lang), 2026),
    ("id", lambda lang: nice_duration(FIVE_MINUTES, lang), 5),
    ("ms", lambda lang: nice_duration(FIVE_MINUTES, lang), 5),
])
def test_control_writer_keeps_its_number(lang, write, number):
    assert pronounce_number(number, lang) in write(lang)
