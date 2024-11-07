#
# Copyright 2019 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
import unittest

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    nice_time
)


class TestNiceDateFormat(unittest.TestCase):
    def test_pm(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt, lang="pt"),
                         nice_time(dt, "pt", True, False, False))

        self.assertEqual(nice_time(dt, lang="pt"),
                         "uma e vinte e dois")
        self.assertEqual(nice_time(dt, lang="pt", use_ampm=True),
                         "uma e vinte e dois da tarde")
        self.assertEqual(nice_time(dt, lang="pt", speech=False), "1:22")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_ampm=True), "1:22 PM")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True), "13:22")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True, use_ampm=True), "13:22")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=True), "treze e vinte e dois")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=False), "treze e vinte e dois")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt"),
                         "uma em ponto")
        self.assertEqual(nice_time(dt, lang="pt", use_ampm=True),
                         "uma da tarde")
        self.assertEqual(nice_time(dt, lang="pt", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_ampm=True), "1:00 PM")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True), "13:00")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True, use_ampm=True), "13:00")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=True), "treze")
        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True),
                         "treze e dois")
        self.assertEqual(nice_time(dt, lang="pt", use_ampm=True),
                         "uma e dois da tarde")
        self.assertEqual(nice_time(dt, lang="pt", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_ampm=True), "1:02 PM")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True), "13:02")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True, use_ampm=True), "13:02")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=True), "treze e dois")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=False), "treze e dois")

    def test_midnight(self):
        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt"),
                         "meia noite e dois")
        self.assertEqual(nice_time(dt, lang="pt", use_ampm=True),
                         "meia noite e dois")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True),
                         "zero e dois")
        self.assertEqual(nice_time(dt, lang="pt", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_ampm=True), "12:02 AM")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True), "00:02")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True,
                                   use_ampm=True), "00:02")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=True), "zero e dois")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=False), "zero e dois")

    def test_midday(self):
        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt"),
                         "meio dia e um quarto")
        self.assertEqual(nice_time(dt, lang="pt", use_ampm=True),
                         "meio dia e um quarto")
        self.assertEqual(nice_time(dt, lang="pt", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=True),
                         "doze e quinze")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=False),
                         "doze e quinze")

    def test_minutes_to_hour(self):
        # "twenty minutes to midnight"
        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt"),
                         "oito menos vinte")
        self.assertEqual(nice_time(dt, lang="pt", use_ampm=True),
                         "oito menos vinte da tarde")
        self.assertEqual(nice_time(dt, lang="pt", speech=False),
                         "7:40")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_ampm=True),
                         "7:40 PM")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="pt", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=True),
                         "dezanove e quarenta")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=False),
                         "dezanove e quarenta")

    def test_minutes_past_hour(self):
        # "quarter past ten"
        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True),
                         "uma e quinze")
        self.assertEqual(nice_time(dt, lang="pt"),
                         "uma e um quarto")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt"),
                         "duas menos vinte e cinco")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt"),
                         "duas menos um quarto")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt"),
                         "cinco menos dez")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt"),
                         "seis menos cinco")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt", use_ampm=True),
                         "cinco e meia da madrugada")

        dt = datetime.datetime(2017, 1, 31,
                               23, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=True,
                                   use_ampm=True),
                         "vinte e três e quinze")
        self.assertEqual(nice_time(dt, lang="pt", use_24hour=False,
                                   use_ampm=True),
                         "onze e um quarto da noite")


if __name__ == "__main__":
    unittest.main()
