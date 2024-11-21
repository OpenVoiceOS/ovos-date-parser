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
                print("Načítám test pro " +
                      str(sub_dir / 'date_time_test.json'))
                with (sub_dir / 'date_time_test.json').open() as f:
                    cls.test_config[sub_dir.parts[-1]] = json.loads(f.read())

    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, "cs",  use_24hour=False),
                         "jedna dvacet dva")
        self.assertEqual(nice_time(dt, "cs",  use_24hour=False, use_ampm=True),
                         "jedna dvacet dva p.m.")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=False),
                         "1:22")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=False, use_ampm=True),
                         "1:22 PM")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, "cs", use_24hour=True, use_ampm=True),
                         "třináct dvacet dva")
        self.assertEqual(nice_time(dt, "cs", use_24hour=True, use_ampm=False),
                         "třináct dvacet dva")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "cs", use_24hour=False),
                         "jedna hodin")
        self.assertEqual(nice_time(dt, "cs", use_24hour=False, use_ampm=True),
                         "jedna p.m.")
        self.assertEqual(nice_time(dt, "cs", use_24hour=False, speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=False, use_ampm=True),
                         "1:00 PM")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, "cs", use_24hour=True, use_ampm=True),
                         "třináct sto")
        self.assertEqual(nice_time(dt, "cs", use_24hour=True, use_ampm=False),
                         "třináct sto")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "cs", use_24hour=False),
                         "jedna oh dva")
        self.assertEqual(nice_time(dt, "cs", use_24hour=False, use_ampm=True),
                         "jedna oh dva p.m.")
        self.assertEqual(nice_time(dt, "cs", use_24hour=False, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, "cs", use_24hour=False, speech=False, use_ampm=True),
                         "1:02 PM")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, "cs", use_24hour=True, use_ampm=True),
                         "třináct nula dva")
        self.assertEqual(nice_time(dt, "cs", use_24hour=True, use_ampm=False),
                         "třináct nula dva")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "cs", use_24hour=False),
                         "dvanáct oh dva")
        self.assertEqual(nice_time(dt, "cs", use_24hour=False, use_ampm=True),
                         "dvanáct oh dva a.m.")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=False),
                         "12:02")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=False, use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, "cs", use_24hour=True, use_ampm=True),
                         "nula nula nula dva")
        self.assertEqual(nice_time(dt, "cs", use_24hour=True, use_ampm=False),
                         "nula nula nula dva")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "cs", use_24hour=False),
                         "jedna oh dva")
        self.assertEqual(nice_time(dt, "cs", use_24hour=False, use_ampm=True),
                         "jedna oh dva a.m.")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=False),
                         "1:02")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=False, use_ampm=True),
                         "1:02 AM")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, "cs", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "01:02")
        self.assertEqual(nice_time(dt, "cs", use_24hour=True, use_ampm=True),
                         "nula jedna nula dva")
        self.assertEqual(nice_time(dt, "cs", use_24hour=True, use_ampm=False),
                         "nula jedna nula dva")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "cs", use_24hour=False),
                         "čtvrt po dvanáct")
        self.assertEqual(nice_time(dt, "cs", use_24hour=False, use_ampm=True),
                         "čtvrt po dvanáct p.m.")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "cs", use_24hour=False, use_ampm=True),
                         "půl po pět a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "cs", use_24hour=False),
                         "třičtvrtě na dva")

    def test_nice_date(self):
        lang = "cs"
        i = 1
        while (self.test_config[lang].get('test_nice_date') and
               self.test_config[lang]['test_nice_date'].get(str(i).encode('utf8'))):
            p = self.test_config[lang]['test_nice_date'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            np = ast.literal_eval(p['now'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                tzinfo=default_timezone())
            now = None if not np else datetime.datetime(
                np[0], np[1], np[2], np[3], np[4], np[5],
                tzinfo=default_timezone())
            print('Testing for ' + lang + ' that ' + str(dt) +
                  ' is date ' + p['assertEqual'])
            self.assertEqual(p['assertEqual'],
                             nice_date(dt, lang=lang, now=now))
            i = i + 1

        # test fall back to english !!!Skiped
        # dt = datetime.datetime(2018, 2, 4, 0, 2, 3, tzinfo=default_timezone())
        # self.assertEqual(nice_date(
        #    dt, lang='invalid', now=datetime.datetime(2018, 2, 4, 0, 2, 3)),
        #    'today')

        # test all days in a year for all languages,
        # that some output is produced
        # for lang in self.test_config:
        for dt in (datetime.datetime(2017, 12, 30, 0, 2, 3,
                                     tzinfo=default_timezone()) +
                   datetime.timedelta(n) for n in range(368)):
            self.assertTrue(len(nice_date(dt, lang=lang)) > 0)

    def test_nice_date_time(self):
        lang = "cs"
        i = 1
        while (self.test_config[lang].get('test_nice_date_time') and
               self.test_config[lang]['test_nice_date_time'].get(str(i).encode('utf8'))):
            p = self.test_config[lang]['test_nice_date_time'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            np = ast.literal_eval(p['now'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                tzinfo=default_timezone())
            now = None if not np else datetime.datetime(
                np[0], np[1], np[2], np[3], np[4], np[5])
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
        lang = "cs"
        i = 1
        while (self.test_config[lang].get('test_nice_year') and
               self.test_config[lang]['test_nice_year'].get(str(i).encode('utf8'))):
            p = self.test_config[lang]['test_nice_year'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                tzinfo=default_timezone())
            print('Testing for ' + lang + ' that ' + str(dt) +
                  ' is year ' + p['assertEqual'])
            self.assertEqual(p['assertEqual'], nice_year(
                dt, lang=lang, bc=ast.literal_eval(p['bc'])))
            i = i + 1

        # Test all years from 0 to 9999 for all languages,
        # that some output is produced
        print("Test all years in " + lang)
        for i in range(1, 9999):
            dt = datetime.datetime(i, 1, 31, 13, 2, 3,
                                   tzinfo=default_timezone())
            self.assertTrue(len(nice_year(dt, lang=lang)) > 0)
            # Looking through the date sequence can be helpful

    #                print(nice_year(dt, lang=lang))


if __name__ == "__main__":
    unittest.main()