"""Equal instants give the language's word for "now" through nice_relative_time.

Sources for the words: de.wiktionary.org/wiki/jetzt, es.wiktionary.org/wiki/ahora
and ca.wiktionary.org/wiki/ara (translation "en: now").
"""
from datetime import datetime

import pytest

from ovos_date_parser import nice_relative_time

ISSUE = "https://github.com/OpenVoiceOS/ovos-date-parser/issues/684"
INSTANT = datetime(2024, 1, 5, 15, 30)


@pytest.mark.parametrize("lang,now", [("en", "now"), ("pt", "agora")])
def test_equal_instants_are_now(lang, now):
    assert nice_relative_time(INSTANT, INSTANT, lang) == now


@pytest.mark.xfail(strict=True, raises=KeyError, reason=ISSUE)
@pytest.mark.parametrize("lang,now", [("de", "jetzt"), ("es", "ahora"), ("ca", "ara")])
def test_equal_instants_are_now_without_a_now_key(lang, now):
    assert nice_relative_time(INSTANT, INSTANT, lang) == now
