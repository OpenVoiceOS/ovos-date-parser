"""A BCP-47 tag means the same in any letter case.

RFC 5646, section 2.1.1: "At all times, language tags and their subtags,
including private use and extensions, are to be treated as case
insensitive: there exist conventions for the capitalization of some of the
subtags, but these MUST NOT be taken to carry meaning." The example given:
"the tag "mn-Cyrl-MN" is not distinct from "MN-cYRL-mn"". So each nice_*
function gives the same words for "PT-PT", "pt-PT" and "pt-pt"."""
import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (nice_date, nice_date_time, nice_day,
                              nice_duration, nice_relative_time, nice_time,
                              nice_year)

DT = datetime(2024, 3, 5, 13, 22)
CALLS = {
    "nice_time": lambda tag: nice_time(DT, tag),
    "nice_day": lambda tag: nice_day(DT, tag),
    "nice_duration": lambda tag: nice_duration(3661, tag),
    "nice_relative_time": lambda tag: nice_relative_time(
        DT + timedelta(minutes=5), DT, tag),
    "nice_date": lambda tag: nice_date(DT, tag),
    "nice_date_time": lambda tag: nice_date_time(DT, tag),
    "nice_year": lambda tag: nice_year(DT, tag),
}
TAGS = ("pt-PT", "pt-BR", "es-ES", "pl-PL", "eu-ES", "en-US", "ca-ES")


class TestTagCase(unittest.TestCase):

    def test_every_case_gives_the_same_words(self):
        for name, call in CALLS.items():
            for tag in TAGS:
                with self.subTest(function=name, tag=tag):
                    self.assertEqual(call(tag.upper()), call(tag.lower()))
                    self.assertEqual(call(tag.swapcase()), call(tag.lower()))

    def test_examples(self):
        self.assertEqual(nice_time(DT, "PT-PT"), "uma e vinte e dois")
        self.assertEqual(nice_time(DT, "ES-ES"), "la una y veintidós")
        self.assertEqual(nice_day(DT, "ES-ES"), "5 de marzo")
        self.assertEqual(nice_relative_time(DT + timedelta(minutes=5), DT,
                                            "PL-PL"), "pięć minut")


if __name__ == "__main__":
    unittest.main()
