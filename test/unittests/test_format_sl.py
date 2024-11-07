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
        language = "sl-si"
        config = date_time_format.config_path + "/" + language + "/date_time_test.json"

        cls.test_config = {}
        with open(config, encoding="utf8") as file:
            cls.test_config[language] = json.loads(file.read())

    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt),
                         nice_time(dt, "sl-si", True, False, False))

        self.assertEqual(nice_time(dt),
                         "dvaindvajset čez ena")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dvaindvajset čez ena p.m.")
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
                         "trinajst dvaindvajset")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "trinajst dvaindvajset")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "ena")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "ena p.m.")
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
                         "trinajst nič nič")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "trinajst nič nič")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dve čez ena")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dve čez ena p.m.")
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
                         "trinajst nič dve")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "trinajst nič dve")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dve čez dvanajst")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dve čez dvanajst a.m.")
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
                         "nič nič dve")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "nič nič dve")

        dt = datetime.datetime(2017, 1, 31,
                               20, 40, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dvajset do devetih")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dvajset do devetih p.m.")

        dt = datetime.datetime(2017, 1, 31,
                               0, 58, 40, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dve do enih")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dve do enih a.m.")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dve čez ena")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dve čez ena a.m.")
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
                         "ena nič dve")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "ena nič dve")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "petnajst čez dvanajst")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "petnajst čez dvanajst p.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "petnajst čez ena a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "petnajst do dveh a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "pol šestih a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "petnajst do dveh")

    def test_nice_date(self):
        for lang in self.test_config:
            i = 1
            while (self.test_config[lang].get('test_nice_date') and
                   self.test_config[lang]['test_nice_date'].get(str(i))):
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

    def test_nice_date_time(self):
        for lang in self.test_config:
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
        for lang in self.test_config:
            i = 1
            while (self.test_config[lang].get('test_nice_year') and
                   self.test_config[lang]['test_nice_year'].get(str(i))):
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
        for lang in self.test_config:
            print("Test all years in " + lang)
            for i in range(1, 9999):
                dt = datetime.datetime(i, 1, 31, 13, 2, 3,
                                       tzinfo=default_timezone())
                self.assertTrue(len(nice_year(dt, lang=lang)) > 0)
                # Looking through the date sequence can be helpful

    #                print(nice_year(dt, lang=lang))

    def test_nice_duration(self):
        # TODO implement better plural support for nice_duration
        # Correct results are in comments

        self.assertEqual(nice_duration(1), "ena sekunda")
        self.assertEqual(nice_duration(2), "dve sekund")  # dve sekundi
        self.assertEqual(nice_duration(3), "tri sekund")  # tri sekunde
        self.assertEqual(nice_duration(4), "štiri sekund")  # štiri sekunde
        self.assertEqual(nice_duration(5), "pet sekund")
        self.assertEqual(nice_duration(6), "šest sekund")

        self.assertEqual(nice_duration(1, speech=False), "0:01")
        self.assertEqual(nice_duration(61), "ena minuta ena sekunda")
        self.assertEqual(nice_duration(61, speech=False), "1:01")
        self.assertEqual(nice_duration(5000),
                         "ena ura triindvajset minut dvajset sekund")
        self.assertEqual(nice_duration(5000, speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000),
                         "trinajst ur triinpetdeset minut dvajset sekund")
        self.assertEqual(nice_duration(50000, speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000),
                         "pet dni  osemnajst ur triinpetdeset minut dvajset sekund")  # nopep8
        self.assertEqual(nice_duration(500000, speech=False), "5d 18:53:20")
        self.assertEqual(nice_duration(datetime.timedelta(seconds=500000),
                                       speech=False),
                         "5d 18:53:20")

    def test_join(self):
        self.assertEqual(join_list(None, "in"), "")
        self.assertEqual(join_list([], "in"), "")

        self.assertEqual(join_list(["a"], "in"), "a")
        self.assertEqual(join_list(["a", "b"], "in"), "a in b")
        self.assertEqual(join_list(["a", "b"], "ali"), "a ali b")

        self.assertEqual(join_list(["a", "b", "c"], "in"), "a, b in c")
        self.assertEqual(join_list(["a", "b", "c"], "ali"), "a, b ali c")
        self.assertEqual(join_list(["a", "b", "c"], "ali", ";"), "a; b ali c")
        self.assertEqual(
            join_list(["a", "b", "c", "d"], "ali"), "a, b, c ali d")

        self.assertEqual(join_list([1, "b", 3, "d"], "ali"), "1, b, 3 ali d")


if __name__ == "__main__":
    unittest.main()
