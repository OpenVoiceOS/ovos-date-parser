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
    nice_time,
    nice_duration
)


class TestNiceDateFormat(unittest.TestCase):
    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, "pl"),
                         "trzynasta dwadzieścia dwa")
        self.assertEqual(nice_time(dt, "pl", speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, "pl", use_24hour=True),
                         "trzynasta dwadzieścia dwa")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "pl"),
                         "trzynasta zero zero")
        self.assertEqual(nice_time(dt, "pl", speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, "pl", use_24hour=True),
                         "trzynasta zero zero")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "pl"),
                         "trzynasta dwa")
        self.assertEqual(nice_time(dt, "pl", speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, "pl", use_24hour=True, use_ampm=False),
                         "trzynasta dwa")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "pl"),
                         "dwa po północy")
        self.assertEqual(nice_time(dt, "pl", speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, "pl", use_24hour=True, use_ampm=False),
                         "dwa po północy")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "pl"),
                         "pierwsza dwa")
        self.assertEqual(nice_time(dt, "pl", speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, "pl", use_24hour=True, use_ampm=False),
                         "pierwsza dwa")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "pl"),
                         "dwunasta piętnaście")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "pl"),
                         "pierwsza czterdzieści pięć")

    def test_nice_duration(self):
        self.assertEqual(nice_duration(1, "pl"), "jedna sekunda")
        self.assertEqual(nice_duration(3, "pl"), "trzy sekundy")
        #self.assertEqual(nice_duration(1, "pl", speech=False), "0:01")
        self.assertEqual(nice_duration(61, "pl"), "jedna minuta jedna sekunda")
        #self.assertEqual(nice_duration(61, "pl", speech=False), "1:01")
        self.assertEqual(nice_duration(5000, "pl"),
                         "jedna godzina dwadzieścia trzy minuty dwadzieścia sekund")
        #self.assertEqual(nice_duration(5000, "pl", speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000, "pl"),
                         "trzynaście godzin pięćdziesiąt trzy minuty dwadzieścia sekund")
        #self.assertEqual(nice_duration(50000, "pl", speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000, "pl"),
                         "pięć dni osiemnaście godzin pięćdziesiąt trzy minuty dwadzieścia sekund")  # nopep8
        #self.assertEqual(nice_duration(500000, "pl", speech=False), "5d 18:53:20")
        #self.assertEqual(nice_duration(datetime.timedelta(seconds=500000), "pl",
        #                               speech=False),
        #                 "5d 18:53:20")


if __name__ == "__main__":
    unittest.main()
