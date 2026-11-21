# -*- coding: utf-8 -*-
"""Routing ``extract_duration`` through chronologia for every locale it reads.

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

#: five minutes, the same length in every other locale chronologia reads
MINUTES = {
    "ar": "5 دقائق", "az": "5 dəqiqə", "be": "5 хвілін", "cy": "5 munud",
    "da": "5 minutter", "de": "5 Minuten", "eo": "5 minutoj",
    "es": "5 minutos", "et": "5 minutit", "eu": "5 minutu",
    "fa": "5 دقیقه", "fil": "5 minuto", "ga": "5 nóiméad",
    "gl": "5 minutos", "ha": "minti 5", "he": "5 דקות", "hi": "5 मिनट",
    "hu": "5 perc", "hy": "5 րոպե", "is": "5 mínútur", "ka": "5 წუთი",
    "kab": "5 n tesdidin", "ko": "5분", "lt": "5 minutės", "lv": "5 minūtes",
    "mk": "5 минути", "mt": "5 minuti", "mwl": "5 minutos",
    "nl": "5 minuten", "pt": "5 minutos", "sq": "5 minuta",
    "sr": "5 минута", "sv": "5 minuter", "sw": "dakika 5",
    "ta": "5 நிமிடங்கள்", "th": "5 นาที", "vi": "5 phút",
}
ROWS += [(lang, text, 300, "") for lang, text in MINUTES.items()]


@pytest.fixture(autouse=True)
def now(monkeypatch):
    monkeypatch.setattr(ovos_date_parser, "now_local", lambda: NOW)


LOCALES = sorted({row[0] for row in ROWS})


@pytest.mark.parametrize("lang,text,seconds,remainder", ROWS)
def test_a_routed_locale_reads_the_length(lang, text, seconds, remainder):
    assert extract_duration(text, lang) == (timedelta(seconds=seconds),
                                            remainder)


def test_every_routed_locale_has_a_row():
    assert set(LOCALES) == ovos_date_parser.CHRONOLOGIA_LOCALES


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
        assert extract_duration(empty, lang) == (None, empty)


def test_the_options_convert_the_answer():
    assert extract_duration("2 months", "en") == (timedelta(days=61), "")
    assert extract_duration(
        "2 months", "en", resolution=DurationResolution.RELATIVEDELTA
    ) == (relativedelta(days=61), "")
    assert extract_duration(
        "2 months", "en", resolution=DurationResolution.TOTAL_DAYS
    ) == (61.0, "")
    assert extract_duration("set a timer for 5 minutes", "en",
                            replace_token="<d>") == (
        timedelta(minutes=5), "set a timer <d>")


@pytest.mark.parametrize("lang,text", [("ja", "2時間"), ("zh", "两小时")])
def test_a_locale_chronologia_does_not_read_answers_no_duration(lang, text):
    assert lang not in ovos_date_parser.CHRONOLOGIA_LOCALES
    assert extract_duration(text, lang) == (None, text)


PUNCTUATED = [
    # (lang, text, length, remainder with the token)
    ("en", "remind me in two hours to call mom.", 7200,
     "remind me in <d> to call mom."),
    ("en", "start the timer, 3 minutes", 180, "start the timer, <d>"),
    ("pt", "lembra-me daqui a duas horas de ligar à mãe.", 7200,
     "lembra-me daqui <d> de ligar à mãe."),
    ("es", "recuérdame en dos horas llamar a mamá.", 7200,
     "recuérdame en <d> llamar a mamá."),
    ("de", "erinnere mich in zwei Stunden an meine Mutter.", 7200,
     "erinnere mich in <d> an meine Mutter."),
    ("fr", "rappelle-moi dans deux heures d'appeler maman.", 7200,
     "rappelle-moi dans <d> d'appeler maman."),
    ("it", "ricordami tra due ore di chiamare la mamma.", 7200,
     "ricordami tra <d> di chiamare la mamma."),
    ("nl", "herinner me over twee uur om mama te bellen.", 7200,
     "herinner me over <d> om mama te bellen."),
    ("ca", "recorda'm d'aquí a dues hores de trucar a la mare.", 7200,
     "recorda'm d'aquí a <d> de trucar a la mare."),
    ("gl", "lémbrame dentro de dúas horas de chamar á nai.", 7200,
     "lémbrame dentro de <d> de chamar á nai."),
    ("fr", "Salut ! Rappelle-moi dans 5 minutes d'appeler maman.", 300,
     "Salut ! Rappelle-moi dans <d> d'appeler maman."),
    ("en", "remind me in two hours to call mom ? merci", 7200,
     "remind me in <d> to call mom ? merci"),
    ("de", "„Erinnere mich in 5 Minuten an Mama“", 300,
     "„Erinnere mich in <d> an Mama“"),
]


@pytest.mark.parametrize("lang,text,seconds,marked", PUNCTUATED)
def test_the_token_stands_where_the_length_was_beside_punctuation(
        lang, text, seconds, marked):
    assert extract_duration(text, lang, replace_token="<d>") == (
        timedelta(seconds=seconds), marked)
