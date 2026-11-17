"""A language tag reads the same in every spelling.

BCP-47 tags are case-insensitive (RFC 5646, section 2.1.1), and callers also
write the POSIX form with "_" ("en_US", "pt_br"). Each spelling must reach
the same reader as the canonical tag.
"""
from datetime import datetime

import pytest

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)  # Tuesday


# A counted offset keeps the anchor clock (class 1): three days after
# Tuesday 27 June 13:04 is Friday 30 June 13:04.
@pytest.mark.parametrize("tag,text", [
    ("en_US", "in 3 days"),
    ("EN-US", "in 3 days"),
    ("en_us", "in 3 days"),
    ("EN", "in 3 days"),
    ("pt_br", "daqui a 3 dias"),
    ("PT_BR", "daqui a 3 dias"),
])
def test_every_spelling_of_the_tag_reads_the_same(tag, text):
    assert tuple(extract_datetime(text, tag, ANCHOR)) == \
        (datetime(2017, 6, 30, 13, 4), "")


def test_an_underscore_tag_does_not_raise():
    text = "next tuesday at 5pm"
    assert extract_datetime(text, "pt_br", ANCHOR) == \
        extract_datetime(text, "pt-BR", ANCHOR)
