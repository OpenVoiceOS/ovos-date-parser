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

        self.assertEqual(nice_time(dt, "en"),
                         "one twenty two")

        self.assertEqual(nice_time(dt, "en", use_ampm=True),
                         "one twenty two p.m.")
        self.assertEqual(nice_time(dt, "en", speech=False),
                         "1:22")
        self.assertEqual(nice_time(dt, "en", speech=False, use_ampm=True),
                         "1:22 PM")
        self.assertEqual(nice_time(dt, "en", speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, "en", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, "en", use_24hour=True, use_ampm=True),
                         "thirteen twenty two")
        self.assertEqual(nice_time(dt, "en", use_24hour=True, use_ampm=False),
                         "thirteen twenty two")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "en"),
                         "one o'clock")
        self.assertEqual(nice_time(dt, "en", use_ampm=True),
                         "one p.m.")
        self.assertEqual(nice_time(dt, "en", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, "en", speech=False, use_ampm=True),
                         "1:00 PM")
        self.assertEqual(nice_time(dt, "en", speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, "en", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, "en", use_24hour=True, use_ampm=True),
                         "thirteen hundred")
        self.assertEqual(nice_time(dt, "en", use_24hour=True, use_ampm=False),
                         "thirteen hundred")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "en"),
                         "one oh two")
        self.assertEqual(nice_time(dt, "en", use_ampm=True),
                         "one oh two p.m.")
        self.assertEqual(nice_time(dt, "en", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, "en", speech=False, use_ampm=True),
                         "1:02 PM")
        self.assertEqual(nice_time(dt, "en", speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, "en", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, "en", use_24hour=True, use_ampm=True),
                         "thirteen zero two")
        self.assertEqual(nice_time(dt, "en", use_24hour=True, use_ampm=False),
                         "thirteen zero two")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "en"),
                         "twelve oh two")
        self.assertEqual(nice_time(dt, "en", use_ampm=True),
                         "twelve oh two a.m.")
        self.assertEqual(nice_time(dt, "en", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, "en", speech=False, use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, "en", speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, "en", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, "en", use_24hour=True, use_ampm=True),
                         "zero zero zero two")
        self.assertEqual(nice_time(dt, "en", use_24hour=True, use_ampm=False),
                         "zero zero zero two")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "en"),
                         "one oh two")
        self.assertEqual(nice_time(dt, "en", use_ampm=True),
                         "one oh two a.m.")
        self.assertEqual(nice_time(dt, "en", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, "en", speech=False, use_ampm=True),
                         "1:02 AM")
        self.assertEqual(nice_time(dt, "en", speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, "en", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "01:02")
        self.assertEqual(nice_time(dt, "en", use_24hour=True, use_ampm=True),
                         "zero one zero two")
        self.assertEqual(nice_time(dt, "en", use_24hour=True, use_ampm=False),
                         "zero one zero two")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "en"),
                         "quarter past twelve")
        self.assertEqual(nice_time(dt, "en", use_ampm=True),
                         "quarter past twelve p.m.")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "en", use_ampm=True),
                         "half past five a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "en"),
                         "quarter to two")

    @unittest.skip("missing code")
    def test_nice_duration(self):
        self.assertEqual(nice_duration(1, "en"), "one second")
        self.assertEqual(nice_duration(3, "en"), "three seconds")
        self.assertEqual(nice_duration(1, "en", speech=False), "0:01")
        self.assertEqual(nice_duration(61, "en"), "one minute one second")
        self.assertEqual(nice_duration(61, "en", speech=False), "1:01")
        self.assertEqual(nice_duration(5000, "en"),
                         "one hour twenty three minutes twenty seconds")
        self.assertEqual(nice_duration(5000, "en", speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000, "en"),
                         "thirteen hours fifty three minutes twenty seconds")
        self.assertEqual(nice_duration(50000, "en", speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000, "en"),
                         "five days  eighteen hours fifty three minutes twenty seconds")  # nopep8
        self.assertEqual(nice_duration(500000, "en", speech=False), "5d 18:53:20")
        self.assertEqual(nice_duration(datetime.timedelta(seconds=500000), "en",
                                       speech=False),
                         "5d 18:53:20")


if __name__ == "__main__":
    unittest.main()
