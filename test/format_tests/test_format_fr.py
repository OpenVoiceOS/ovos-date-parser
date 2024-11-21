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


class TestNiceDateFormat_fr(unittest.TestCase):
    def test_convert_times_fr(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, lang="fr-fr"),
                         "une heure vingt-deux")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_ampm=True),
                         "une heure vingt-deux de l'après-midi")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False),
                         "1:22")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_ampm=True),
                         "1:22 PM")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=True),
                         "treize heures vingt-deux")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=False),
                         "treize heures vingt-deux")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="fr-fr"),
                         "une heure")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_ampm=True),
                         "une heure de l'après-midi")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_ampm=True),
                         "1:00 PM")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=True),
                         "treize heures")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=False),
                         "treize heures")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="fr-fr"),
                         "une heure deux")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_ampm=True),
                         "une heure deux de l'après-midi")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_ampm=True),
                         "1:02 PM")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=True),
                         "treize heures deux")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=False),
                         "treize heures deux")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="fr-fr"),
                         "minuit deux")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_ampm=True),
                         "minuit deux")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=True),
                         "minuit deux")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=False),
                         "minuit deux")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="fr-fr"),
                         "midi et quart")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_ampm=True),
                         "midi et quart")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=True),
                         "midi quinze")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=False),
                         "midi quinze")

        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="fr-fr"),
                         "huit heures moins vingt")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_ampm=True),
                         "huit heures moins vingt du soir")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False),
                         "7:40")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_ampm=True),
                         "7:40 PM")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="fr-fr", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=True),
                         "dix-neuf heures quarante")
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True,
                                   use_ampm=False),
                         "dix-neuf heures quarante")

        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="fr-fr", use_24hour=True),
                         "une heure quinze")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="fr-fr"),
                         "deux heures moins vingt-cinq")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="fr-fr"),
                         "deux heures moins le quart")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="fr-fr"),
                         "cinq heures moins dix")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="fr-fr"),
                         "six heures moins cinq")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="fr-fr", use_ampm=True),
                         "cinq heures et demi du matin")


if __name__ == "__main__":
    unittest.main()