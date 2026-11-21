# -*- coding: utf-8 -*-
"""The per-language reader names answer through the routed readers.

``extract_datetime_<lang>`` and ``extract_duration_<lang>`` were readers of
their own. Each name still imports from ``ovos_date_parser``, warns that it
goes away in the next major release, and answers what
``extract_datetime(text, lang)`` or ``extract_duration(text, lang)`` answers.
"""
import re
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

import pytest

import ovos_date_parser as odp
from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)

DATETIME_LANGS = ("an ar ast az bg ca cs da de el en es et eu fa fi fr fy gl "
                  "he hr hu id it kab ms nb nl nn oc pl pt ro ru sk sl sv tr "
                  "uk").split()
DURATION_LANGS = ("an az bg ca cs da de el en es et eu fi fr fy gl he hr hu "
                  "it nb nl nn pl pt ro ru sk sl uk").split()


def next_major():
    """The next major version, read from version.py as text."""
    source = (Path(odp.__file__).parent / "version.py").read_text()
    major = int(re.search(r"^VERSION_MAJOR = (\d+)$", source, re.M)[1])
    return f"{major + 1}.0.0"


def deprecated(name):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        reader = getattr(odp, name)
    assert [w.category for w in caught] == [DeprecationWarning]
    message = str(caught[0].message)
    assert name in message and f"removed in {next_major()}" in message
    return reader


@pytest.mark.parametrize("lang", DATETIME_LANGS)
def test_a_datetime_reader_name_reads_through_extract_datetime(lang):
    reader = deprecated(f"extract_datetime_{lang}")
    assert reader.__name__ == f"extract_datetime_{lang}"
    with mock.patch.object(odp, "extract_datetime") as public:
        assert reader("23:30", ANCHOR, None) is public.return_value
    public.assert_called_once_with("23:30", lang, anchorDate=ANCHOR,
                                   default_time=None)
    assert (reader("23:30", ANCHOR)
            == extract_datetime("23:30", lang, anchorDate=ANCHOR)
            == [datetime(2017, 6, 27, 23, 30), ""])


def test_a_datetime_reader_name_keeps_its_keywords():
    reader = deprecated("extract_datetime_en")
    assert (reader("tomorrow", anchorDate=ANCHOR, default_time=None)
            == [datetime(2017, 6, 28), ""])


@pytest.mark.parametrize("lang", DURATION_LANGS)
def test_a_duration_reader_name_reads_through_extract_duration(lang):
    reader = deprecated(f"extract_duration_{lang}")
    assert reader.__name__ == f"extract_duration_{lang}"
    with mock.patch.object(odp, "extract_duration") as public:
        assert reader("ten", "units", "@") is public.return_value
    public.assert_called_once_with("ten", lang, resolution="units",
                                   replace_token="@")


def test_a_duration_reader_name_reads_a_duration():
    reader = deprecated("extract_duration_en")
    assert reader("ten minutes") == (timedelta(minutes=10), "")


@pytest.mark.parametrize("name", ["extract_duration_ar", "extract_duration_ast",
                                  "extract_duration_kab", "extract_duration_fa",
                                  "extract_duration_sv"])
def test_a_duration_reader_extract_duration_calls_is_no_shim(name):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        reader = getattr(odp, name)
    assert reader.__module__ == f"ovos_date_parser.dates_{name.split('_')[-1]}"


@pytest.mark.parametrize("name", ["extract_datetime_xx", "extract_duration_ar_x",
                                  "extract_date_en", "extract_time_en",
                                  "extract_duration_kab_extra"])
def test_any_other_name_is_missing(name):
    with pytest.raises(AttributeError):
        getattr(odp, name)
