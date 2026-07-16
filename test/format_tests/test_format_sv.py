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


class TestNiceDateFormat_sv(unittest.TestCase):
    def test_convert_times_sv(self):
        dt = datetime.datetime(2017, 1, 31, 13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, lang="sv-se"),
                         "tjugotvå minuter över ett")
        self.assertEqual(nice_time(dt, lang="sv-se", use_ampm=True),
                         "tjugotvå minuter över ett på eftermiddagen")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False),
                         "01:22")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_ampm=True),
                         "01:22 PM")
        self.assertEqual(nice_time(dt, lang="sv-se",
                                   speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=True),
                         "tretton tjugotvå")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=False),
                         "tretton tjugotvå")

        dt = datetime.datetime(2017, 1, 31, 13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="sv-se"), "ett")
        self.assertEqual(nice_time(dt, lang="sv-se", use_ampm=True),
                         "ett på eftermiddagen")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False),
                         "01:00")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_ampm=True),
                         "01:00 PM")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=True),
                         "tretton")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=False),
                         "tretton")

        dt = datetime.datetime(2017, 1, 31, 13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="sv-se"), "två minuter över ett")
        self.assertEqual(nice_time(dt, lang="sv-se", use_ampm=True),
                         "två minuter över ett på eftermiddagen")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False),
                         "01:02")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_ampm=True),
                         "01:02 PM")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=True),
                         "tretton noll två")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=False),
                         "tretton noll två")

        dt = datetime.datetime(2017, 1, 31, 0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="sv-se"), "två minuter över tolv")
        self.assertEqual(nice_time(dt, lang="sv-se", use_ampm=True),
                         "två minuter över tolv på natten")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=True),
                         "noll noll två")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=False),
                         "noll noll två")

        dt = datetime.datetime(2017, 1, 31, 12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="sv-se"), "kvart över tolv")
        self.assertEqual(nice_time(dt, lang="sv-se", use_ampm=True),
                         "kvart över tolv på eftermiddagen")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=True),
                         "tolv femton")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=False),
                         "tolv femton")

        dt = datetime.datetime(2017, 1, 31, 19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="sv-se"), "tjugo minuter i åtta")
        self.assertEqual(nice_time(dt, lang="sv-se", use_ampm=True),
                         "tjugo minuter i åtta på kvällen")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False),
                         "07:40")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_ampm=True),
                         "07:40 PM")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="sv-se", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=True),
                         "nitton fyrtio")
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True,
                                   use_ampm=False),
                         "nitton fyrtio")

        dt = datetime.datetime(2017, 1, 31, 1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="sv-se", use_24hour=True),
                         "ett femton")

        dt = datetime.datetime(2017, 1, 31, 1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="sv-se"),
                         "tjugofem minuter i två")

        dt = datetime.datetime(2017, 1, 31, 1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="sv-se"), "kvart i två")

        dt = datetime.datetime(2017, 1, 31, 4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="sv-se"), "tio i fem")

        dt = datetime.datetime(2017, 1, 31, 5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="sv-se"), "fem i sex")

        dt = datetime.datetime(2017, 1, 31, 5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="sv-se", use_ampm=True),
                         "halv sex på morgonen")


if __name__ == "__main__":
    unittest.main()
