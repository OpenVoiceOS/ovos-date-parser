#
# Copyright 2019 Mycroft AI Inc.
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
from ovos_date_parser.dates_ca import TimeVariantCA


class TestNiceDateFormat(unittest.TestCase):
    def test_pm(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, lang="ca"), "la una i vint-i-dos")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "la una i vint-i-dos de la tarda")
        self.assertEqual(nice_time(dt, lang="ca", speech=False), "1:22")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "1:22 PM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "13:22")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True, use_ampm=True), "13:22")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les tretze i vint-i-dos")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les tretze i vint-i-dos")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca"), "la una en punt")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "la una en punt de la tarda")
        self.assertEqual(nice_time(dt, lang="ca", speech=False), "1:00")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "1:00 PM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "13:00")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True, use_ampm=True), "13:00")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les tretze")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True),
                         "les tretze i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "la una i dos de la tarda")
        self.assertEqual(nice_time(dt, lang="ca", speech=False), "1:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "1:02 PM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "13:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True, use_ampm=True), "13:02")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les tretze i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les tretze i dos")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 0, tzinfo=default_timezone())
        # Default Watch system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les dotze i quinze")
        # Spanish-like time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.SPANISH_LIKE),
                         "les dotze i quart")
        # Catalan Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant=TimeVariantCA.BELL),
                         "un quart d'una de la tarda")
        # Catalan Full Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant=TimeVariantCA.BELL),
                         "un quart d'una de la tarda")

        dt = datetime.datetime(2017, 1, 31,
                               00, 14, 0, tzinfo=default_timezone())
        # Default Watch system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les zero i catorze")
        # Spanish-like time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.SPANISH_LIKE),
                         "les dotze i catorze")
        # Catalan Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant=TimeVariantCA.BELL),
                         "les dotze i catorze minuts de la nit")
        # Catalan Full Bell time system: 00:31
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.FULL_BELL),
                         "un quart d'una de la matinada")
        # Catalan Full Bell time system: 16:31                 
        dt = datetime.datetime(2017, 1, 31,
                               16, 31, 0, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.FULL_BELL),
                         "dos quarts de cinc de la tarda")
        # Catalan Full Bell time system: 5:32                 
        dt = datetime.datetime(2017, 1, 31,
                               5, 32, 0, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.FULL_BELL),
                         "dos quarts tocats de sis del matí")
        # Catalan Full Bell time system: 19:19                 
        dt = datetime.datetime(2017, 1, 31,
                               19, 19, 0, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.FULL_BELL),
                         "un quart tocat de vuit del vespre")

    def test_midnight(self):
        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca"),
                         "les dotze i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "les dotze i dos de la nit")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True),
                         "les zero i dos")
        self.assertEqual(nice_time(dt, lang="ca", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "12:02 AM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "00:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True,
                                   use_ampm=True), "00:02")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les zero i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les zero i dos")

    def test_midday(self):
        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les dotze i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es", use_ampm=True),
                         "les dotze i quinze del migdia")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=True),
                         "les dotze i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=False),
                         "les dotze i quinze")

    def test_minutes_to_hour(self):
        # "twenty minutes to midnight"
        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les set i quaranta")
        self.assertEqual(nice_time(dt, lang="ca-es", use_ampm=True),
                         "les set i quaranta del vespre")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False),
                         "7:40")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_ampm=True),
                         "7:40 PM")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=True),
                         "les dinou i quaranta")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=False),
                         "les dinou i quaranta")

    def test_minutes_past_hour(self):
        # "quarter past ten"
        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True),
                         "la una i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "la una i quinze")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "la una i trenta-cinc")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "la una i quaranta-cinc")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les quatre i cinquanta")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les cinc i cinquanta-cinc")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es", use_ampm=True),
                         "les cinc i trenta de la matinada")

        dt = datetime.datetime(2017, 1, 31,
                               23, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=True),
                         "les vint-i-tres i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=False,
                                   use_ampm=True),
                         "les onze i quinze de la nit")

    def test_variant_strings(self):
        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 0, tzinfo=default_timezone())
        # Default variant
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant="default"),
                         "les dotze i quinze")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False),
                         "les dotze i quinze")

        dt = datetime.datetime(2017, 1, 31,
                               00, 14, 0, tzinfo=default_timezone())
        # Spanish-like time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.SPANISH_LIKE),
                         "les dotze i catorze")
        # Catalan Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant=TimeVariantCA.BELL),
                         "les dotze i catorze minuts de la nit")

        # Catalan Full Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.FULL_BELL),
                         "un quart d'una de la matinada")

        # error
        # with self.assertRaises(ValueError):
        #    nice_time(dt, lang="ca", variant="invalid")
        #    nice_time(dt, lang="ca", variant="bad_VARIANT")


if __name__ == "__main__":
    unittest.main()
