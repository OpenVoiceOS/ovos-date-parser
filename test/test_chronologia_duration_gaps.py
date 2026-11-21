# -*- coding: utf-8 -*-
"""Lengths chronologia does not read yet.

Each row is a phrase this package's own readers read before ``extract_duration``
moved to chronologia. A row is a strict xfail that names the chronologia issue
tracking it, so the row fails the run as soon as the issue is fixed and the
marker has to go. The calendar rows (#1238) and the token rows (#1242) also need
a change here: ``extract_duration`` reads only the timedelta and the remainder
of chronologia's answer, so a months field or a consumed span reaches the
caller only when the adapter uses it. Months and years are counted from a
pinned "now", and the expected value of a calendar row is dateutil's calendar
arithmetic from it.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

import ovos_date_parser
from ovos_date_parser import DurationResolution, extract_duration

NOW = datetime(2017, 6, 27, 13, 4)
ISSUES = "https://github.com/TigreGotico/chronologia/issues/"


def calendar(**units):
    return NOW + relativedelta(**units) - NOW


def gap(issue, lang, text, duration, remainder=""):
    return pytest.param(
        lang, text, duration, remainder, id=f"{issue}-{lang}-{text}",
        marks=pytest.mark.xfail(strict=True, reason=ISSUES + str(issue)))


ROWS = [
    # a decimal point in the count
    gap(1204, "es", "7.5 segundos", timedelta(seconds=7.5)),
    gap(1204, "fa", "7.5 ثانیه", timedelta(seconds=7.5)),
    gap(1204, "de", "weck mich in 3 wochen, 497 tagen und 391.6 sekunden",
        timedelta(weeks=3, days=497, seconds=391.6), "weck mich in"),
    # a century or a millennium
    gap(1203, "es", "1 siglo", calendar(years=100)),
    gap(1203, "es", "5 siglos", calendar(years=500)),
    gap(1203, "es", "1 milenio", calendar(years=1000)),
    gap(1203, "es", "5 milenios", calendar(years=5000)),
    # a suffix on the unit noun
    gap(1017, "eu", "hamar minutuko tenporizadorea", timedelta(minutes=10),
        "tenporizadorea"),
    gap(1020, "hu", "állíts be egy időzítőt tíz percre",
        timedelta(minutes=10), "állíts be egy időzítőt"),
    gap(1211, "sv", "starta en 9 minuters timer", timedelta(minutes=9),
        "starta en timer"),
    # a unit the locale does not know
    gap(1211, "kab", "tlatin tasint", timedelta(seconds=30)),
    # a compound number
    gap(1210, "kab", "mraw d yiwen n tesdidin", timedelta(minutes=11)),
    gap(1210, "kab", "mraw d sin n tesdidin", timedelta(minutes=12)),
    gap(1210, "kab", "ɛecrin d yiwen n tesdidin", timedelta(minutes=21)),
    gap(1239, "kab", "sin mraw n tesdidin", timedelta(minutes=12)),
    # the dual and the count written after the unit
    gap(1209, "ar", "ثانية واحدة", timedelta(seconds=1)),
    gap(1209, "ar", "أسبوع واحد", timedelta(weeks=1)),
    gap(1209, "ar", "سنة واحدة", calendar(years=1)),
    gap(1209, "ar", "شهرين", calendar(months=2)),
    gap(1209, "ar", "سنتين", calendar(years=2)),
    # a singular noun after a tens count and a fused conjunction
    gap(1236, "ar", "ثلاثون ثانية", timedelta(seconds=30)),
    gap(1236, "ar", "ثلاثة أيام وخمس ساعات", timedelta(days=3, hours=5)),
    # the unit word after a trailing fraction
    gap(1240, "sv", "hämta mig om två timmar och en kvart",
        timedelta(hours=2, minutes=15), "hämta mig om"),
    gap(1240, "sv", "två timmar och en halvtimme",
        timedelta(hours=2, minutes=30)),
    # "the hour" is no count
    gap(1206, "nl", "vijf minuten na het uur", timedelta(minutes=5),
        "na het uur"),
    gap(1237, "en", "five minutes past the hour", timedelta(minutes=5),
        "past the hour"),
]


@pytest.fixture(autouse=True)
def now(monkeypatch):
    monkeypatch.setattr(ovos_date_parser, "now_local", lambda: NOW)


@pytest.mark.parametrize("lang,text,duration,remainder", ROWS)
def test_a_length_chronologia_does_not_read_yet(lang, text, duration,
                                                remainder):
    assert extract_duration(text, lang) == (duration, remainder)


CALENDAR_ROWS = [
    # the calendar part of a length is lost in a day count
    gap(1238, "en", "2 months", relativedelta(months=2)),
    gap(1238, "fr", "2 mois", relativedelta(months=2)),
    gap(1238, "it", "2 anni e 3 mesi", relativedelta(years=2, months=3)),
    gap(1238, "id", "tiga tahun dua bulan", relativedelta(years=3, months=2)),
    gap(1238, "ms", "tiga tahun dua bulan", relativedelta(years=3, months=2)),
    gap(1238, "tr", "üç yıl iki ay", relativedelta(years=3, months=2)),
    gap(1238, "tr", "bir sene", relativedelta(years=1)),
]


@pytest.mark.parametrize("lang,text,duration,remainder", CALENDAR_ROWS)
def test_a_calendar_length_in_months_and_years(lang, text, duration,
                                               remainder):
    assert extract_duration(
        text, lang, resolution=DurationResolution.RELATIVEDELTA
    ) == (duration, remainder)


TOKEN_ROWS = [
    # the consumed span is unknown, so a word diff places the token
    gap(1242, "en", "boil it 5 minutes 5 times", "boil it <d> 5 times"),
    gap(1242, "pt", "mexe 5 minutos 5 vezes", "mexe <d> 5 vezes"),
    gap(1242, "fr", "minuteur d'une heure", "minuteur <d>"),
    gap(1242, "ca", "temporitzador d'una hora", "temporitzador <d>"),
]


@pytest.mark.parametrize("lang,text,marked,remainder", TOKEN_ROWS)
def test_the_token_marks_the_place_of_a_repeated_or_elided_length(
        lang, text, marked, remainder):
    assert extract_duration(text, lang, replace_token="<d>")[1] == marked
