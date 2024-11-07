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
import json
import unittest
from pathlib import Path

from ovos_date_parser import (
    date_time_format,
    nice_time
)


class TestNiceDateFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read date_time_test.json files for test data
        cls.test_config = {}
        p = Path(date_time_format.config_path)
        for sub_dir in [x for x in p.iterdir() if x.is_dir()]:
            if (sub_dir / 'date_time_test.json').exists():
                print("Getting test for " +
                      str(sub_dir / 'date_time_test.json'))
                with (sub_dir / 'date_time_test.json').open() as f:
                    cls.test_config[sub_dir.parts[-1]] = json.loads(f.read())

    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3)

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt),
                         nice_time(dt, "fa-ir", True, False, False))

        self.assertEqual(nice_time(dt),
                         "یک و بیست و دو دقیقه")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "یک و بیست و دو دقیقه بعد از ظهر")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:22")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:22 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "سیزده و بیست و دو دقیقه")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "سیزده و بیست و دو دقیقه")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3)
        self.assertEqual(nice_time(dt),
                         "یک")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "یک بعد از ظهر")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:00 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "سیزده")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "سیزده")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3)
        self.assertEqual(nice_time(dt),
                         "یک و دو دقیقه")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "یک و دو دقیقه بعد از ظهر")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:02 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "سیزده و دو دقیقه")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "سیزده و دو دقیقه")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3)
        self.assertEqual(nice_time(dt),
                         "دوازده و دو دقیقه")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "دوازده و دو دقیقه قبل از ظهر")
        self.assertEqual(nice_time(dt, speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "صفر و دو دقیقه")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "صفر و دو دقیقه")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33)
        self.assertEqual(nice_time(dt),
                         "یک و دو دقیقه")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "یک و دو دقیقه قبل از ظهر")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:02 AM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "01:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "یک و دو دقیقه")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "یک و دو دقیقه")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9)
        self.assertEqual(nice_time(dt),
                         "دوازده و ربع")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "دوازده و ربع بعد از ظهر")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00)
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "پنج و نیم قبل از ظهر")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00)
        self.assertEqual(nice_time(dt),
                         "یه ربع به دو")

    # TODO: failed because of و
    # def test_nice_duration(self):
    #    self.assertEqual(nice_duration(1), "یک ثانیه")
    #    self.assertEqual(nice_duration(3), "سه ثانیه")
    #    self.assertEqual(nice_duration(1, speech=False), "0:01")
    #    self.assertEqual(nice_duration(61), "یک دقیقه و یک ثانیه")
    #    self.assertEqual(nice_duration(61, speech=False), "1:01")
    #    self.assertEqual(nice_duration(5000),
    #                     "یک ساعت و بیست و سه دقیقه و بیست ثانیه")
    #    self.assertEqual(nice_duration(5000, speech=False), "1:23:20")
    #    self.assertEqual(nice_duration(50000),
    #                     "سیزده ساعت و پنجاه و سه دقیقه و بیست ثانیه")
    #    self.assertEqual(nice_duration(50000, speech=False), "13:53:20")
    #    self.assertEqual(nice_duration(500000),
    #                     "پنج روز و هیجده ساعت و پنجاه و سه دقیقه و بیست ثانیه")  # nopep8
    #    self.assertEqual(nice_duration(500000, speech=False), "5d 18:53:20")
    #    self.assertEqual(nice_duration(datetime.timedelta(seconds=500000),
    #                                   speech=False),
    #                     "5d 18:53:20")

    def test_join(self):
        self.assertEqual(join_list(None, "and"), "")
        self.assertEqual(join_list([], "and"), "")

        self.assertEqual(join_list(["الف"], "و"), "الف")
        self.assertEqual(join_list(["الف", "ب"], "و"), "الف و ب")
        self.assertEqual(join_list(["الف", "ب"], "یا"), "الف یا ب")

        self.assertEqual(join_list(["الف", "ب", "ج"], "و"), "الف, ب و ج")
        self.assertEqual(join_list(["الف", "ب", "ج"], "یا"), "الف, ب یا ج")
        self.assertEqual(join_list(["الف", "ب", "ج"], "یا", ";"), "الف; ب یا ج")
        self.assertEqual(join_list(["الف", "ب", "ج", "دال"], "یا"), "الف, ب, ج یا دال")

        self.assertEqual(join_list([1, "ب", 3, "دال"], "یا"), "1, ب, 3 یا دال")


if __name__ == "__main__":
    unittest.main()
