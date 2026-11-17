# -*- coding: utf-8 -*-
"""Routing ``extract_duration`` through chronologia.

A month or a year has no fixed length, so the route counts it on the calendar
from now. "Now" is pinned to Tuesday 2017-06-27 13:04, and every expected
value below is calendar arithmetic from that day done by hand:

* 1 month  -> 27 July, 30 days; 2 months -> 27 August, 61 days;
  3 months -> 27 September, 92 days
* 1 year   -> 27 June 2018, 365 days; 2 years -> 730 days
* 5 years  -> 27 June 2022, 5 * 365 + 1 (29 February 2020) = 1826 days
* 10 years -> 27 June 2027, 10 * 365 + 2 (2020, 2024) = 3652 days
* 3 years 2 months -> 27 August 2020, 3 * 365 + 1 + 61 = 1157 days

The fixed-width readings follow from arithmetic on the units: 2 h 30 min is
9000 s, 3 d 8 h 10 min 49 s is 288649 s, 3 h 20 min is 12000 s.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from dateutil.relativedelta import relativedelta

import ovos_date_parser
from ovos_date_parser import DurationResolution, extract_duration

NOW = datetime(2017, 6, 27, 13, 4)
DAY = 86400

ROWS = [
    # (lang, text, seconds, remainder)
    ("an", "aguardar 3 horas y 20 minutos", 12000, "aguardar"),
    ("ast", "2 meses", 61 * DAY, ""),
    ("bg", "сложи таймер за два часа и тридесет минути", 9000,
     "сложи таймер за"),
    ("ca", "2 mesos", 61 * DAY, ""),
    ("ca", "1 any", 365 * DAY, ""),
    ("cs", "2 měsíce", 61 * DAY, ""),
    ("cs", "1 rok", 365 * DAY, ""),
    ("el", "2 ώρες και 30 λεπτά", 9000, ""),
    ("en", "2 months", 61 * DAY, ""),
    ("en", "1 year", 365 * DAY, ""),
    ("fi", "2 kuukautta", 61 * DAY, ""),
    ("fi", "1 vuosi", 365 * DAY, ""),
    ("fr", "un mois", 30 * DAY, ""),
    ("fr", "2 mois", 61 * DAY, ""),
    ("fr", "deux ans", 730 * DAY, ""),
    ("fr", "1 décennie", 3652 * DAY, ""),
    ("fr", "3 jours 8 heures 10 minutes et 49 secondes", 288649, ""),
    ("fy", "wachtsje 3 oeren en 20 minuten", 12000, "wachtsje"),
    ("hr", "postavi timer na dva sata i trideset minuta", 9000,
     "postavi timer na"),
    ("id", "tiga tahun dua bulan", 1157 * DAY, ""),
    ("it", "un anno", 365 * DAY, ""),
    ("it", "2 anni e 3 mesi", 822 * DAY, ""),
    ("it", "imposta un timer di dieci minuti", 600, "imposta un timer"),
    ("ms", "tiga tahun dua bulan", 1157 * DAY, ""),
    ("nb", "2 timer og 30 minutter", 9000, ""),
    ("nn", "2 timar og 30 minutt", 9000, ""),
    ("oc", "1 an", 365 * DAY, ""),
    ("oc", "2 mes", 61 * DAY, ""),
    ("pl", "2 miesiące", 61 * DAY, ""),
    ("pl", "1 rok", 365 * DAY, ""),
    ("ro", "3 luni", 92 * DAY, ""),
    ("ro", "un an", 365 * DAY, ""),
    ("ro", "2 ani", 730 * DAY, ""),
    ("ro", "un deceniu", 3652 * DAY, ""),
    ("ru", "2 месяца", 61 * DAY, ""),
    ("ru", "1 год", 365 * DAY, ""),
    ("sk", "nastav časovač na dve hodiny a tridsať minút", 9000,
     "nastav časovač na"),
    ("sl", "en mesec", 30 * DAY, ""),
    ("sl", "pet let", 1826 * DAY, ""),
    ("tr", "üç yıl iki ay", 1157 * DAY, ""),
    ("tr", "bir sene", 365 * DAY, ""),
    ("uk", "2 місяці", 61 * DAY, ""),
    ("uk", "1 рік", 365 * DAY, ""),
]


@pytest.fixture(autouse=True)
def now(monkeypatch):
    monkeypatch.setattr(ovos_date_parser, "now_local", lambda: NOW)


LOCALES = sorted({row[0] for row in ROWS})


@pytest.mark.parametrize("lang,text,seconds,remainder", ROWS)
def test_a_routed_locale_reads_the_length(lang, text, seconds, remainder):
    assert extract_duration(text, lang) == (timedelta(seconds=seconds),
                                            remainder)


def test_every_routed_locale_has_a_row():
    assert set(LOCALES) == set(ovos_date_parser.CHRONOLOGIA_DURATION_LOCALES)


@pytest.mark.parametrize("text,lang", [
    ("2 months", "en-US"), ("2 months", "en-gb"), ("2 mois", "fr-CA"),
    ("2 mesos", "ca-ES"), ("2 luni", "ro-RO"),
])
def test_a_regional_tag_routes_like_its_language(text, lang):
    assert extract_duration(text, lang) == (timedelta(days=61), "")


def test_a_month_is_counted_from_now(monkeypatch):
    """From 10 February 2020 a month ends on 10 March, 29 days on, because
    2020 is a leap year."""
    monkeypatch.setattr(ovos_date_parser, "now_local",
                        lambda: datetime(2020, 2, 10, 9, 0))
    assert extract_duration("1 month", "en") == (timedelta(days=29), "")


def test_a_zoned_now_gives_the_same_length(monkeypatch):
    zoned = NOW.replace(tzinfo=ZoneInfo("Europe/Lisbon"))
    monkeypatch.setattr(ovos_date_parser, "now_local", lambda: zoned)
    assert extract_duration("2 months", "en") == (timedelta(days=61), "")


@pytest.mark.parametrize("lang", LOCALES)
def test_a_text_with_no_duration_is_returned_whole(lang):
    assert extract_duration("xyzzy qq", lang) == (None, "xyzzy qq")


@pytest.mark.parametrize("lang", LOCALES)
def test_an_empty_text_is_no_duration(lang):
    for empty in ("", None):
        found = extract_duration(empty, lang)
        assert found is None or found[0] is None


def test_the_options_of_the_shared_engine_stay_with_it():
    """chronologia has no resolution or replace token, so a call that asks
    for one is answered by the shared engine, which has both."""
    assert extract_duration("2 months", "en") == (timedelta(days=61), "")
    assert extract_duration(
        "2 months", "en", resolution=DurationResolution.RELATIVEDELTA
    ) == (relativedelta(months=2), "")
    assert extract_duration("set a timer for 5 minutes", "en",
                            replace_token="<d>") == (
        timedelta(minutes=5), "set a timer for <d>")


def test_a_locale_outside_the_set_keeps_its_reader():
    assert "pt" not in ovos_date_parser.CHRONOLOGIA_DURATION_LOCALES
    got = extract_duration("2 meses", "pt")[0]
    assert got != timedelta(days=61)
    assert timedelta(days=60) < got < timedelta(days=61)


def test_the_set_does_not_follow_the_datetime_set(monkeypatch):
    monkeypatch.setattr(ovos_date_parser, "CHRONOLOGIA_LOCALES",
                        frozenset())
    assert extract_duration("2 months", "en") == (timedelta(days=61), "")
