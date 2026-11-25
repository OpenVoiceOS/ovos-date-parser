"""The writers pick their language from a tag through linguatag, so every
spelling and every code of a language reaches the writer of that language."""
from datetime import datetime

import pytest

from ovos_date_parser import (nice_date, nice_day, nice_duration, nice_month,
                              nice_relative_time, nice_time, nice_weekday,
                              nice_year)

DT = datetime(2026, 3, 14, 16, 16, 7)
NOW = datetime(2026, 3, 10, 9, 0)
TWO_DAYS_LATER = datetime(2026, 3, 12, 9, 0)


@pytest.mark.parametrize("tag", ["PT_BR", "pt_br", "pt-BR", "PT-br", "pt_PT", "pt"])
def test_duration_and_relative_time_read_any_spelling_of_portuguese(tag):
    assert nice_duration(3725, tag) == "uma hora dois minutos cinco segundos"
    assert nice_relative_time(TWO_DAYS_LATER, NOW, tag) == "dois dias"


@pytest.mark.parametrize("tag", ["no", "NO", "no-NO", "nb", "nb_NO"])
def test_norwegian_reads_as_bokmal(tag):
    assert nice_duration(3725, tag) == "en time to minutter fem sekunder"


@pytest.mark.parametrize("tag", ["fil", "FIL", "fil-PH"])
def test_filipino_is_not_finnish(tag):
    with pytest.raises(NotImplementedError):
        nice_time(DT, tag)
    with pytest.raises(NotImplementedError):
        nice_year(DT, tag)


def test_south_ndebele_is_not_bokmal():
    with pytest.raises(NotImplementedError):
        nice_time(DT, "nbl")


@pytest.mark.parametrize("tag,language", [
    ("deu", "de"), ("fra", "fr"), ("spa", "es"), ("por", "pt"), ("iw", "he"),
    ("nob", "nb"), ("nno", "nn"), ("arz", "ar"), ("arb", "ar"), ("azj", "az"),
    ("ekk", "et"), ("pes", "fa"), ("zsm", "ms")])
def test_a_code_of_a_language_reads_as_its_language(tag, language):
    assert nice_time(DT, tag) == nice_time(DT, language)


def test_a_padded_tag_reads_as_its_language():
    assert nice_time(DT, " en ") == nice_time(DT, "en")
    assert nice_date(DT, "pt-BR ") == nice_date(DT, "pt-BR")


@pytest.mark.parametrize("tag", ["de_DE", "DE-de", "de_ch", "deu"])
def test_the_resource_formatters_read_any_spelling_of_german(tag):
    assert nice_day(DT, tag) == "14 März"
    assert nice_month(DT, tag) == "März"
    assert nice_weekday(DT, tag) == "Samstag"


@pytest.mark.parametrize("tag", [" en", "en ", " en ", "\tde"])
def test_a_padded_tag_reaches_the_generic_writers(tag):
    language = tag.strip()
    assert nice_duration(3725, tag) == nice_duration(3725, language)
    assert nice_relative_time(TWO_DAYS_LATER, NOW, tag) == \
        nice_relative_time(TWO_DAYS_LATER, NOW, language)


def test_a_padded_brazilian_tag_reads_brazilian_in_every_writer():
    assert nice_time(DT, "pt-BR ") == nice_time(DT, "pt-BR")
    assert nice_duration(976, " pt-BR") == nice_duration(976, "pt-BR")
