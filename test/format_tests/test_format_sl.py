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

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    date_time_format,
    nice_time,
    nice_duration
)


class TestNiceDateFormat(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Read date_time_test.json files for test data
        language = "sl"
        config = date_time_format.config_path + "/" + language + "/date_time_test.json"

        cls.test_config = {}
        with open(config, encoding="utf8") as file:
            cls.test_config[language] = json.loads(file.read())

    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, "sl"),
                         "dvaindvajset čez ena")
        self.assertEqual(nice_time(dt, "sl", use_ampm=True),
                         "dvaindvajset čez ena p.m.")
        self.assertEqual(nice_time(dt, "sl", speech=False),
                         "1:22")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_ampm=True),
                         "1:22 PM")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, "sl", use_24hour=True, use_ampm=True),
                         "trinajst dvaindvajset")
        self.assertEqual(nice_time(dt, "sl", use_24hour=True, use_ampm=False),
                         "trinajst dvaindvajset")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "sl"),
                         "ena")
        self.assertEqual(nice_time(dt, "sl", use_ampm=True),
                         "ena p.m.")
        self.assertEqual(nice_time(dt, "sl", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_ampm=True),
                         "1:00 PM")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, "sl", use_24hour=True, use_ampm=True),
                         "trinajst nič nič")
        self.assertEqual(nice_time(dt, "sl", use_24hour=True, use_ampm=False),
                         "trinajst nič nič")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "sl"),
                         "dve čez ena")
        self.assertEqual(nice_time(dt, "sl", use_ampm=True),
                         "dve čez ena p.m.")
        self.assertEqual(nice_time(dt, "sl", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_ampm=True),
                         "1:02 PM")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, "sl", use_24hour=True, use_ampm=True),
                         "trinajst nič dve")
        self.assertEqual(nice_time(dt, "sl", use_24hour=True, use_ampm=False),
                         "trinajst nič dve")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "sl"),
                         "dve čez dvanajst")
        self.assertEqual(nice_time(dt, "sl", use_ampm=True),
                         "dve čez dvanajst a.m.")
        self.assertEqual(nice_time(dt, "sl", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, "sl", use_24hour=True, use_ampm=True),
                         "nič nič dve")
        self.assertEqual(nice_time(dt, "sl", use_24hour=True, use_ampm=False),
                         "nič nič dve")

        dt = datetime.datetime(2017, 1, 31,
                               20, 40, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "sl"),
                         "dvajset do devetih")
        self.assertEqual(nice_time(dt, "sl", use_ampm=True),
                         "dvajset do devetih p.m.")

        dt = datetime.datetime(2017, 1, 31,
                               0, 58, 40, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "sl"),
                         "dve do enih")
        self.assertEqual(nice_time(dt, "sl", use_ampm=True),
                         "dve do enih a.m.")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "sl"),
                         "dve čez ena")
        self.assertEqual(nice_time(dt, "sl", use_ampm=True),
                         "dve čez ena a.m.")
        self.assertEqual(nice_time(dt, "sl", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_ampm=True),
                         "1:02 AM")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, "sl", speech=False, use_24hour=True,
                                   use_ampm=True),
                         "01:02")
        self.assertEqual(nice_time(dt, "sl", use_24hour=True, use_ampm=True),
                         "ena nič dve")
        self.assertEqual(nice_time(dt, "sl", use_24hour=True, use_ampm=False),
                         "ena nič dve")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "sl"),
                         "petnajst čez dvanajst")
        self.assertEqual(nice_time(dt, "sl", use_ampm=True),
                         "petnajst čez dvanajst p.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "sl", use_ampm=True),
                         "petnajst čez ena a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "sl", use_ampm=True),
                         "petnajst do dveh a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "sl", use_ampm=True),
                         "pol šestih a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, "sl"),
                         "petnajst do dveh")

    @unittest.skip("missing code")
    def test_nice_duration(self):
        # TODO implement better plural support for nice_duration
        # Correct results are in comments

        self.assertEqual(nice_duration(1, "sl"), "ena sekunda")
        self.assertEqual(nice_duration(2, "sl"), "dve sekund")  # dve sekundi
        self.assertEqual(nice_duration(3, "sl"), "tri sekund")  # tri sekunde
        self.assertEqual(nice_duration(4, "sl"), "štiri sekund")  # štiri sekunde
        self.assertEqual(nice_duration(5, "sl"), "pet sekund")
        self.assertEqual(nice_duration(6, "sl"), "šest sekund")

        self.assertEqual(nice_duration(1, "sl", speech=False), "0:01")
        self.assertEqual(nice_duration(61, "sl"), "ena minuta ena sekunda")
        self.assertEqual(nice_duration(61, "sl", speech=False), "1:01")
        self.assertEqual(nice_duration(5000, "sl"),
                         "ena ura triindvajset minut dvajset sekund")
        self.assertEqual(nice_duration(5000, "sl", speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000, "sl"),
                         "trinajst ur triinpetdeset minut dvajset sekund")
        self.assertEqual(nice_duration(50000, "sl", speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000, "sl"),
                         "pet dni  osemnajst ur triinpetdeset minut dvajset sekund")  # nopep8
        self.assertEqual(nice_duration(500000, "sl", speech=False), "5d 18:53:20")
        self.assertEqual(nice_duration(datetime.timedelta(seconds=500000), "sl", "sl",
                                       speech=False),
                         "5d 18:53:20")


if __name__ == "__main__":
    unittest.main()
