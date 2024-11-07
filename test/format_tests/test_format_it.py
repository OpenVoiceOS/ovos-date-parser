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


class Testtimes(unittest.TestCase):

    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31, 13, 22, 3, tzinfo=default_timezone())

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt, lang="it-it"),
                         nice_time(dt, "it-it", True, False, False))

        self.assertEqual(nice_time(dt, lang="it"),
                         "una e ventidue")
        self.assertEqual(nice_time(dt, lang="it", use_ampm=True),
                         "una e ventidue del pomeriggio")
        self.assertEqual(nice_time(dt, lang="it", speech=False), "1:22")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_ampm=True), "1:22 PM")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_24hour=True), "13:22")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_24hour=True, use_ampm=True), "13:22")
        self.assertEqual(nice_time(dt, lang="it", use_24hour=True,
                                   use_ampm=True), "tredici e ventidue")
        self.assertEqual(nice_time(dt, lang="it", use_24hour=True,
                                   use_ampm=False), "tredici e ventidue")
        # Verifica fasce orarie use_ampm = True
        d_time = datetime.datetime(2017, 1, 31, 8, 22, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(d_time, lang="it", use_ampm=True),
                         "otto e ventidue della mattina")
        d_time = datetime.datetime(2017, 1, 31, 20, 22, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(d_time, lang="it", use_ampm=True),
                         "otto e ventidue della sera")
        d_time = datetime.datetime(2017, 1, 31, 23, 22, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(d_time, lang="it", use_ampm=True),
                         "undici e ventidue della notte")
        d_time = datetime.datetime(2017, 1, 31, 00, 00, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(d_time, lang="it", use_ampm=True),
                         "mezzanotte")
        d_time = datetime.datetime(2017, 1, 31, 12, 00, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(d_time, lang="it", use_ampm=True),
                         "mezzogiorno")
        dt = datetime.datetime(2017, 1, 31, 13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="it"),
                         "una in punto")
        self.assertEqual(nice_time(dt, lang="it", use_ampm=True),
                         "una del pomeriggio")
        self.assertEqual(nice_time(dt, lang="it", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_ampm=True), "1:00 PM")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_24hour=True), "13:00")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_24hour=True, use_ampm=True), "13:00")
        self.assertEqual(nice_time(dt, lang="it", use_24hour=True,
                                   use_ampm=True), "tredici e zerozero")
        self.assertEqual(nice_time(dt, lang="it", use_24hour=True,
                                   use_ampm=False), "tredici e zerozero")

        dt = datetime.datetime(2017, 1, 31, 13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="it", use_24hour=True),
                         "tredici e zero due")
        self.assertEqual(nice_time(dt, lang="it", use_ampm=True),
                         "una e zero due del pomeriggio")
        self.assertEqual(nice_time(dt, lang="it", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_ampm=True), "1:02 PM")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_24hour=True), "13:02")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_24hour=True, use_ampm=True), "13:02")
        self.assertEqual(nice_time(dt, lang="it", use_24hour=True,
                                   use_ampm=True), "tredici e zero due")
        self.assertEqual(nice_time(dt, lang="it", use_24hour=True,
                                   use_ampm=False), "tredici e zero due")

        dt = datetime.datetime(2017, 1, 31, 0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="it"),
                         "mezzanotte e zero due")
        self.assertEqual(nice_time(dt, lang="it", use_ampm=True),
                         "mezzanotte e zero due")
        self.assertEqual(nice_time(dt, lang="it", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_ampm=True), "12:02 AM")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_24hour=True), "00:02")
        self.assertEqual(nice_time(dt, lang="it", speech=False,
                                   use_24hour=True,
                                   use_ampm=True), "00:02")
        self.assertEqual(nice_time(dt, lang="it", use_24hour=True,
                                   use_ampm=True), "zerozero e zero due")
        self.assertEqual(nice_time(dt, lang="it", use_24hour=True,
                                   use_ampm=False), "zerozero e zero due")
        # casi particolari
        d_time = datetime.datetime(2017, 1, 31, 1, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(d_time, lang="it", use_24hour=True,
                                   use_ampm=True), "una e zero due")
        d_time = datetime.datetime(2017, 1, 31, 2, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(d_time, lang="it", use_24hour=True,
                                   use_ampm=False), "zero due e zero due")
        d_time = datetime.datetime(2017, 1, 31, 10, 15, 0, tzinfo=default_timezone())
        self.assertEqual(nice_time(d_time, lang="it", use_24hour=False,
                                   use_ampm=False), "dieci e un quarto")
        d_time = datetime.datetime(2017, 1, 31, 22, 45, 0, tzinfo=default_timezone())
        self.assertEqual(nice_time(d_time, lang="it", use_24hour=False,
                                   use_ampm=False), "dieci e tre quarti")


if __name__ == "__main__":
    unittest.main()
