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


class TestNiceDateFormat(unittest.TestCase):
    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt, lang="es-es"),
                         nice_time(dt, "es-es", True, False, False))

        self.assertEqual(nice_time(dt, lang="es"),
                         "la una y veintidós")
        self.assertEqual(nice_time(dt, lang="es", use_ampm=True),
                         "la una y veintidós de la tarde")
        self.assertEqual(nice_time(dt, lang="es", speech=False), "1:22")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_ampm=True), "1:22 PM")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_24hour=True), "13:22")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_24hour=True, use_ampm=True), "13:22")
        self.assertEqual(nice_time(dt, lang="es", use_24hour=True,
                                   use_ampm=True), "las trece veintidós")
        self.assertEqual(nice_time(dt, lang="es", use_24hour=True,
                                   use_ampm=False), "las trece veintidós")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es"),
                         "la una en punto")
        self.assertEqual(nice_time(dt, lang="es", use_ampm=True),
                         "la una de la tarde")
        self.assertEqual(nice_time(dt, lang="es", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_ampm=True), "1:00 PM")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_24hour=True), "13:00")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_24hour=True, use_ampm=True), "13:00")
        self.assertEqual(nice_time(dt, lang="es", use_24hour=True,
                                   use_ampm=True), "las trece cero cero")
        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es", use_24hour=True),
                         "las trece cero dos")
        self.assertEqual(nice_time(dt, lang="es", use_ampm=True),
                         "la una y dos de la tarde")
        self.assertEqual(nice_time(dt, lang="es", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_ampm=True), "1:02 PM")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_24hour=True), "13:02")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_24hour=True, use_ampm=True), "13:02")
        self.assertEqual(nice_time(dt, lang="es", use_24hour=True,
                                   use_ampm=True), "las trece cero dos")
        self.assertEqual(nice_time(dt, lang="es", use_24hour=True,
                                   use_ampm=False), "las trece cero dos")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es"),
                         "las doce y dos")
        self.assertEqual(nice_time(dt, lang="es", use_ampm=True),
                         "las doce y dos de la madrugada")
        self.assertEqual(nice_time(dt, lang="es", use_24hour=True),
                         "las cero cero dos")
        self.assertEqual(nice_time(dt, lang="es", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_ampm=True), "12:02 AM")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_24hour=True), "00:02")
        self.assertEqual(nice_time(dt, lang="es", speech=False,
                                   use_24hour=True,
                                   use_ampm=True), "00:02")
        self.assertEqual(nice_time(dt, lang="es", use_24hour=True,
                                   use_ampm=True), "las cero cero dos")
        self.assertEqual(nice_time(dt, lang="es", use_24hour=True,
                                   use_ampm=False), "las cero cero dos")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es-es"),
                         "las doce y cuarto")
        self.assertEqual(nice_time(dt, lang="es-es", use_ampm=True),
                         "las doce y cuarto de la mañana")
        self.assertEqual(nice_time(dt, lang="es-es", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="es-es", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="es-es", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="es-es", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="es-es", use_24hour=True,
                                   use_ampm=True),
                         "las doce quince")
        self.assertEqual(nice_time(dt, lang="es-es", use_24hour=True,
                                   use_ampm=False),
                         "las doce quince")

        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es-es"),
                         "las ocho menos veinte")
        self.assertEqual(nice_time(dt, lang="es-es", use_ampm=True),
                         "las ocho menos veinte de la tarde")
        self.assertEqual(nice_time(dt, lang="es-es", speech=False),
                         "7:40")
        self.assertEqual(nice_time(dt, lang="es-es", speech=False,
                                   use_ampm=True),
                         "7:40 PM")
        self.assertEqual(nice_time(dt, lang="es-es", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="es-es", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="es-es", use_24hour=True,
                                   use_ampm=True),
                         "las diecinueve cuarenta")
        self.assertEqual(nice_time(dt, lang="es-es", use_24hour=True,
                                   use_ampm=False),
                         "las diecinueve cuarenta")

        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es-es", use_24hour=True),
                         "la una quince")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es-es"),
                         "las dos menos veinticinco")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es-es"),
                         "las dos menos cuarto")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es-es"),
                         "las cinco menos diez")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es-es"),
                         "las seis menos cinco")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es-es", use_ampm=True),
                         "las cinco y media de la madrugada")

        dt = datetime.datetime(2017, 1, 31,
                               23, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="es-es", use_24hour=True,
                                   use_ampm=True),
                         "las veintitrés quince")
        self.assertEqual(nice_time(dt, lang="es-es", use_24hour=False,
                                   use_ampm=True),
                         "las once y cuarto de la noche")


if __name__ == "__main__":
    unittest.main()
