#
# Copyright 2017 Mycroft AI Inc.
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


class TestNiceDateFormat_hu(unittest.TestCase):
    def test_convert_times_hu(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, lang="hu-hu"),
                         "egy óra huszonkettő")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_ampm=True),
                         "délután egy óra huszonkettő")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False),
                         "1:22")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_ampm=True),
                         "1:22 PM")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=True),
                         "tizenhárom óra huszonkettő")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=False),
                         "tizenhárom óra huszonkettő")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="hu-hu"),
                         "egy óra")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_ampm=True),
                         "délután egy óra")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_ampm=True),
                         "1:00 PM")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=True),
                         "tizenhárom óra")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=False),
                         "tizenhárom óra")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="hu-hu"),
                         "egy óra kettő")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_ampm=True),
                         "délután egy óra kettő")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_ampm=True),
                         "1:02 PM")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=True),
                         "tizenhárom óra kettő")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=False),
                         "tizenhárom óra kettő")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="hu-hu"),
                         "tizenkét óra kettő")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_ampm=True),
                         "éjjel tizenkét óra kettő")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=True),
                         "nulla óra kettő")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=False),
                         "nulla óra kettő")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="hu-hu"),
                         "tizenkét óra tizenöt")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_ampm=True),
                         "délután tizenkét óra tizenöt")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=True),
                         "tizenkét óra tizenöt")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=False),
                         "tizenkét óra tizenöt")

        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="hu-hu"),
                         "hét óra negyven")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_ampm=True),
                         "este hét óra negyven")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False),
                         "7:40")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_ampm=True),
                         "7:40 PM")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="hu-hu", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=True),
                         "tizenkilenc óra negyven")
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True,
                                   use_ampm=False),
                         "tizenkilenc óra negyven")

        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="hu-hu", use_24hour=True),
                         "egy óra tizenöt")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="hu-hu"),
                         "egy óra harmincöt")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="hu-hu"),
                         "egy óra negyvenöt")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="hu-hu"),
                         "négy óra ötven")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="hu-hu"),
                         "öt óra ötvenöt")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="hu-hu", use_ampm=True),
                         "reggel öt óra harminc")


if __name__ == "__main__":
    unittest.main()
