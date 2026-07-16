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


class TestNiceDateFormat_nl(unittest.TestCase):
    def test_convert_times_nl(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, lang="nl-nl"),
                         "tweeentwintig over één")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_ampm=True),
                         "tweeentwintig over één 's middags")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False),
                         "1:22")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_ampm=True),
                         "1:22 PM")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=True),
                         "dertien uur tweeentwintig")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=False),
                         "dertien uur tweeentwintig")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="nl-nl"),
                         "één uur")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_ampm=True),
                         "één uur 's middags")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_ampm=True),
                         "1:00 PM")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=True),
                         "dertien uur")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=False),
                         "dertien uur")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="nl-nl"),
                         "twee over één")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_ampm=True),
                         "twee over één 's middags")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_ampm=True),
                         "1:02 PM")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=True),
                         "dertien uur twee")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=False),
                         "dertien uur twee")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="nl-nl"),
                         "twee over twaalf")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_ampm=True),
                         "twee over twaalf 's nachts")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=True),
                         "nul uur twee")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=False),
                         "nul uur twee")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="nl-nl"),
                         "kwart over twaalf")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_ampm=True),
                         "kwart over twaalf 's middags")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=True),
                         "twaalf uur vijftien")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=False),
                         "twaalf uur vijftien")

        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="nl-nl"),
                         "twintig voor acht")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_ampm=True),
                         "twintig voor acht 's avonds")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False),
                         "7:40")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_ampm=True),
                         "7:40 PM")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="nl-nl", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=True),
                         "negentien uur veertig")
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True,
                                   use_ampm=False),
                         "negentien uur veertig")

        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="nl-nl", use_24hour=True),
                         "één uur vijftien")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="nl-nl"),
                         "vijfentwintig voor twee")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="nl-nl"),
                         "kwart voor twee")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="nl-nl"),
                         "tien voor vijf")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="nl-nl"),
                         "vijf voor zes")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="nl-nl", use_ampm=True),
                         "half zes 's nachts")


if __name__ == "__main__":
    unittest.main()
