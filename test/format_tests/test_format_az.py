#
# Copyright 2021 Mycroft AI Inc.
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
# See the License for the specific language governing permissions və
# limitations under the License.
#

import ast
import datetime
import json
import unittest
from pathlib import Path

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    date_time_format,
    nice_date,
    nice_date_time,
    nice_time,
    nice_duration,
    nice_year
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
                               13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, "az-az"),
                         "ikiyə iyirmi iki dəqiqə işləyib")

        self.assertEqual(nice_time(dt, "az-az", use_ampm=True),
                         "gündüz ikiyə iyirmi iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, "az-az", speech=False),
                         "1:22")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_ampm=True),
                         "gündüz 1:22")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, "az-az", use_24hour=True, use_ampm=True),
                         "on üç iyirmi iki")
        self.assertEqual(nice_time(dt, "az-az", use_24hour=True, use_ampm=False),
                         "on üç iyirmi iki")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "az-az"),
                         "bir tamamdır")
        self.assertEqual(nice_time(dt, "az-az", use_ampm=True),
                         "gündüz bir tamamdır")
        self.assertEqual(nice_time(dt, "az-az", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_ampm=True),
                         "gündüz 1:00")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, "az-az", use_24hour=True, use_ampm=True),
                         "on üç sıfır sıfır")
        self.assertEqual(nice_time(dt, "az-az", use_24hour=True, use_ampm=False),
                         "on üç sıfır sıfır")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "az-az"),
                         "ikiyə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, "az-az", use_ampm=True),
                         "gündüz ikiyə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, "az-az", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_ampm=True),
                         "gündüz 1:02")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, "az-az", use_24hour=True, use_ampm=True),
                         "on üç sıfır iki")
        self.assertEqual(nice_time(dt, "az-az", use_24hour=True, use_ampm=False),
                         "on üç sıfır iki")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "az-az"),
                         "birə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, "az-az", use_ampm=True),
                         "gecə birə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, "az-az", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_ampm=True),
                         "gecə 12:02")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, "az-az", use_24hour=True, use_ampm=True),
                         "sıfır sıfır sıfır iki")
        self.assertEqual(nice_time(dt, "az-az", use_24hour=True, use_ampm=False),
                         "sıfır sıfır sıfır iki")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "az-az"),
                         "ikiyə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, "az-az", use_ampm=True),
                         "gecə ikiyə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, "az-az", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_ampm=True),
                         "gecə 1:02")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, "az-az", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "01:02")
        self.assertEqual(nice_time(dt, "az-az", use_24hour=True, use_ampm=True),
                         "sıfır bir sıfır iki")
        self.assertEqual(nice_time(dt, "az-az", use_24hour=True, use_ampm=False),
                         "sıfır bir sıfır iki")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "az-az"),
                         "birə on beş dəqiqə işləyib")
        self.assertEqual(nice_time(dt, "az-az", use_ampm=True),
                         "gündüz birə on beş dəqiqə işləyib")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "az-az", use_ampm=True),
                         "gecə altının yarısı")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "az-az"),
                         "ikiyə on beş dəqiqə qalıb")

    def test_nice_date(self):
        lang = "az"
        i = 1
        while (self.test_config[lang].get('test_nice_date') and
               self.test_config[lang]['test_nice_date'].get(str(i))):
            p = self.test_config[lang]['test_nice_date'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            np = ast.literal_eval(p['now'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5])
            now = None if not np else datetime.datetime(
                np[0], np[1], np[2], np[3], np[4], np[5])
            print('Testing for ' + lang + ' that ' + str(dt) +
                  ' is date ' + p['assertEqual'])
            self.assertEqual(p['assertEqual'],
                             nice_date(dt, lang=lang, now=now))
            i = i + 1

        for dt in (datetime.datetime(2017, 12, 30, 0, 2, 3) +
                   datetime.timedelta(n) for n in range(368)):
            self.assertTrue(len(nice_date(dt, lang=lang)) > 0)

    def test_nice_date_time(self):
        # TODO: migrate these tests (in res files) to respect the new
        # language loading features. Right now, some of them break if
        # their languages are not default.
        lang = "az"

        i = 1
        while (self.test_config[lang].get('test_nice_date_time') and
               self.test_config[lang]['test_nice_date_time'].get(str(i))):
            p = self.test_config[lang]['test_nice_date_time'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            np = ast.literal_eval(p['now'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                tzinfo=default_timezone())
            now = None if not np else datetime.datetime(
                np[0], np[1], np[2], np[3], np[4], np[5],
                tzinfo=default_timezone())
            print('Testing for ' + lang + ' that ' + str(dt) +
                  ' is date time ' + p['assertEqual'])
            self.assertEqual(
                p['assertEqual'],
                nice_date_time(
                    dt, lang=lang, now=now,
                    use_24hour=ast.literal_eval(p['use_24hour']),
                    use_ampm=ast.literal_eval(p['use_ampm'])))
            i = i + 1

    def test_nice_year(self):
        lang = "az"
        i = 1
        while (self.test_config[lang].get('test_nice_year') and
               self.test_config[lang]['test_nice_year'].get(str(i))):
            p = self.test_config[lang]['test_nice_year'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5])
            print('Testing for ' + lang + ' that ' + str(dt) +
                  ' is year ' + p['assertEqual'])
            self.assertEqual(p['assertEqual'], nice_year(
                dt, lang=lang, bc=ast.literal_eval(p['bc'])))
            i = i + 1

        # Test all years from 0 to 9999 for az,
        # that some output is produced
        print("Test all years in " + lang)
        for i in range(1, 9999):
            dt = datetime.datetime(i, 1, 31, 13, 2, 3, tzinfo=default_timezone())
            self.assertTrue(len(nice_year(dt, lang=lang)) > 0)

    def test_nice_duration(self):
        self.assertEqual(nice_duration(1, "az-az"), "bir saniyə")
        self.assertEqual(nice_duration(3, "az-az"), "üç saniyə")
        self.assertEqual(nice_duration(1, "az-az", speech=False), "0:01")
        self.assertEqual(nice_duration(61, "az-az"), "bir dəqiqə bir saniyə")
        self.assertEqual(nice_duration(61, "az-az", speech=False), "1:01")
        self.assertEqual(nice_duration(5000, "az-az"),
                         "bir saat iyirmi üç dəqiqə iyirmi saniyə")
        self.assertEqual(nice_duration(5000, "az-az", speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000, "az-az"),
                         "on üç saat əlli üç dəqiqə iyirmi saniyə")
        self.assertEqual(nice_duration(50000, "az-az", speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000, "az-az"),
                         "beş gün on səkkiz saat əlli üç dəqiqə iyirmi saniyə")  # nopep8
        self.assertEqual(nice_duration(500000, "az-az", speech=False), "5g 18:53:20")
        self.assertEqual(nice_duration(datetime.timedelta(seconds=500000), "az-az",
                                       speech=False),
                         "5g 18:53:20")

if __name__ == "__main__":
    unittest.main()
