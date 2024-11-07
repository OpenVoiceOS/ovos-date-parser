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
    nice_day, nice_month, nice_weekday, get_date_strings
)


class TestNiceTime_de(unittest.TestCase):

    def test_convert_times_de(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, "de", "de"),
                         "ein uhr zweiundzwanzig")
        self.assertEqual(nice_time(dt, "de", "de", use_ampm=True),
                         "ein uhr zweiundzwanzig nachmittags")
        self.assertEqual(nice_time(dt, "de", speech=False),
                         "01:22 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_ampm=True),
                         "01:22 uhr nachmittags")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True),
                         "13:22 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:22 uhr nachmittags")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=True),
                         "dreizehn uhr zweiundzwanzig nachmittags")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=False),
                         "dreizehn uhr zweiundzwanzig")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "de"),
                         "ein uhr")
        self.assertEqual(nice_time(dt, "de", use_ampm=True),
                         "ein uhr nachmittags")
        self.assertEqual(nice_time(dt, "de", speech=False),
                         "01:00 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_ampm=True),
                         "01:00 uhr nachmittags")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True),
                         "13:00 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:00 uhr nachmittags")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=True),
                         "dreizehn uhr nachmittags")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=False),
                         "dreizehn uhr")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "de"),
                         "ein uhr zwei")
        self.assertEqual(nice_time(dt, "de", use_ampm=True),
                         "ein uhr zwei nachmittags")
        self.assertEqual(nice_time(dt, "de", speech=False),
                         "01:02 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_ampm=True),
                         "01:02 uhr nachmittags")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True),
                         "13:02 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:02 uhr nachmittags")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=True),
                         "dreizehn uhr zwei nachmittags")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=False),
                         "dreizehn uhr zwei")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "de"),
                         "null uhr zwei")
        self.assertEqual(nice_time(dt, "de", use_ampm=True),
                         "null uhr zwei nachts")
        self.assertEqual(nice_time(dt, "de", speech=False),
                         "12:02 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_ampm=True),
                         "12:02 uhr nachts")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True),
                         "00:02 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "00:02 uhr nachts")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=True),
                         "null uhr zwei nachts")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=False),
                         "null uhr zwei")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "de"),
                         "viertel eins")
        self.assertEqual(nice_time(dt, "de", use_ampm=True),
                         "viertel eins nachmittags")
        self.assertEqual(nice_time(dt, "de", speech=False),
                         "12:15 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_ampm=True),
                         "12:15 uhr nachmittags")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True),
                         "12:15 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15 uhr nachmittags")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=True),
                         "zwölf uhr fünfzehn nachmittags")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=False),
                         "zwölf uhr fünfzehn")

        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "de"),
                         "sieben uhr vierzig")
        self.assertEqual(nice_time(dt, "de", use_ampm=True),
                         "sieben uhr vierzig abends")
        self.assertEqual(nice_time(dt, "de", speech=False),
                         "07:40 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_ampm=True),
                         "07:40 uhr abends")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True),
                         "19:40 uhr")
        self.assertEqual(nice_time(dt, "de", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40 uhr abends")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=True),
                         "neunzehn uhr vierzig abends")
        self.assertEqual(nice_time(dt, "de", use_24hour=True,
                                   use_ampm=False),
                         "neunzehn uhr vierzig")

        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "de", use_24hour=True),
                         "ein uhr fünfzehn")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "de"),
                         "ein uhr fünfunddreißig")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "de"),
                         "dreiviertel zwei")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "de"),
                         "vier uhr fünfzig")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "de"),
                         "fünf uhr fünfundfünfzig")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "de", use_ampm=True),
                         "halb sechs morgens")


class TestNiceDateUtils(unittest.TestCase):

    def test_nice_day(self):
        # Test with include_month=True
        dt = datetime.datetime(2022, 10, 31)
        self.assertEqual(nice_day(dt, "de", 'MDY', True), "Oktober 31")
        self.assertEqual(nice_day(dt, "de", 'DMY', True), "31 Oktober")

        # Test with include_month=False
        self.assertEqual(nice_day(dt, include_month=False, lang="de"), "31")

    def test_nice_month(self):
        dt = datetime.datetime(2022, 10, 31)
        self.assertEqual(nice_month(dt, lang="de"), "Oktober")

    def test_nice_weekday(self):
        dt = datetime.datetime(2022, 10, 31)
        self.assertEqual(nice_weekday(dt, lang="de"), "Montag")

    def test_get_date_strings(self):
        # Test with default arguments
        dt = datetime.datetime(2022, 10, 31, 13, 30, 0)
        expected_output = {
            "date_string": "10/31/2022",
            "time_string": "13:30 uhr",
            "month_string": "Oktober",
            "day_string": "31",
            "year_string": "2022",
            "weekday_string": "Montag"
        }
        self.assertEqual(get_date_strings(dt, lang="de"), expected_output)

        # Test with different date_format
        expected_output = {
            "date_string": "31/10/2022",
            "time_string": "13:30 uhr",
            "month_string": "Oktober",
            "day_string": "31",
            "year_string": "2022",
            "weekday_string": "Montag"
        }
        self.assertEqual(get_date_strings(dt,
                                          date_format='DMY',
                                          lang="de"), expected_output)

        # Test with different time_format
        expected_output = {
            "date_string": "10/31/2022",
            "time_string": "01:30 uhr",
            "month_string": "Oktober",
            "day_string": "31",
            "year_string": "2022",
            "weekday_string": "Montag"
        }
        self.assertEqual(get_date_strings(dt,
                                          time_format="half",
                                          lang="de"), expected_output)


if __name__ == "__main__":
    unittest.main()
