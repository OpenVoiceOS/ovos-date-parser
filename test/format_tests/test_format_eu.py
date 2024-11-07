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

from ovos_date_parser import (
    nice_time
)


class TestNiceDateFormat(unittest.TestCase):
    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3)

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         nice_time(dt, "eu-eu", True, False, False))

        self.assertEqual(nice_time(dt, lang="eu"),
                         "ordubata eta hogeita bi")
        self.assertEqual(nice_time(dt, lang="eu", use_ampm=True),
                         "arratsaldeko ordubata eta hogeita bi")
        self.assertEqual(nice_time(dt, lang="eu", speech=False), "1:22")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_ampm=True), "1:22 PM")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True), "13:22")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True, use_ampm=True), "13:22")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=True), "hamahiruak hogeita bi")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=False), "hamahiruak hogeita bi")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3)
        self.assertEqual(nice_time(dt, lang="eu"),
                         "ordubata puntuan")
        self.assertEqual(nice_time(dt, lang="eu", use_ampm=True),
                         "arratsaldeko ordubata")
        self.assertEqual(nice_time(dt, lang="eu", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_ampm=True), "1:00 PM")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True), "13:00")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True, use_ampm=True), "13:00")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=True), "hamahiruak zero zero")
        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3)
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True),
                         "hamahiruak zero bi")
        self.assertEqual(nice_time(dt, lang="eu", use_ampm=True),
                         "arratsaldeko ordubata eta bi")
        self.assertEqual(nice_time(dt, lang="eu", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_ampm=True), "1:02 PM")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True), "13:02")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True, use_ampm=True), "13:02")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=True), "hamahiruak zero bi")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=False), "hamahiruak zero bi")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3)
        self.assertEqual(nice_time(dt, lang="eu"),
                         "hamabiak eta bi")
        self.assertEqual(nice_time(dt, lang="eu", use_ampm=True),
                         "gaueko hamabiak eta bi")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True),
                         "zeroak zero bi")
        self.assertEqual(nice_time(dt, lang="eu", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_ampm=True), "12:02 AM")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True), "00:02")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True,
                                   use_ampm=True), "00:02")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=True), "zeroak zero bi")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=False), "zeroak zero bi")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "hamabiak eta laurden")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_ampm=True),
                         "goizeko hamabiak eta laurden")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True,
                                   use_ampm=True),
                         "hamabiak hamabost")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True,
                                   use_ampm=False),
                         "hamabiak hamabost")

        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "zortzirak hogei gutxi")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_ampm=True),
                         "arratsaldeko zortzirak hogei gutxi")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False),
                         "7:40")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_ampm=True),
                         "7:40 PM")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True,
                                   use_ampm=True),
                         "hemeretziak berrogei")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True,
                                   use_ampm=False),
                         "hemeretziak berrogei")

        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True),
                         "batak hamabost")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "ordubiak hogeita bost gutxi")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "ordubiak laurden gutxi")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "bostak hamar gutxi")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "seirak bost gutxi")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu", use_ampm=True),
                         "gaueko bostak eta erdi")

        dt = datetime.datetime(2017, 1, 31,
                               23, 15, 9)
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True,
                                   use_ampm=True),
                         "hogeita hiruak hamabost")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=False,
                                   use_ampm=True),
                         "gaueko hamaikak eta laurden")


if __name__ == "__main__":
    unittest.main()
