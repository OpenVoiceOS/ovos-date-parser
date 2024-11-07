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

# fractions are not capitalized for now
NUMBERS_FIXTURE_da = {
    1.435634: '1,436',
    2: '2',
    5.0: '5',
    1234567890: '1234567890',
    12345.67890: '12345,679',
    0.027: '0,027',
    0.5: '1 halv',
    1.333: '1 og 1 trediedel',
    2.666: '2 og 2 trediedele',
    0.25: '1 fjerdedel',
    1.25: '1 og 1 fjerdedel',
    0.75: '3 fjerdedele',
    1.75: '1 og 3 fjerdedele',
    3.4: '3 og 2 femtedele',
    16.8333: '16 og 5 sjettedele',
    12.5714: '12 og 4 syvendedele',
    9.625: '9 og 5 ottendedele',
    6.777: '6 og 7 niendedele',
    3.1: '3 og 1 tiendedel',
    2.272: '2 og 3 elftedele',
    5.583: '5 og 7 tolvtedele',
    8.384: '8 og 5 trettendedele',
    0.071: '1 fjortendedel',
    6.466: '6 og 7 femtendedele',
    8.312: '8 og 5 sejstendedele',
    2.176: '2 og 3 syttendedele',
    200.722: '200 og 13 attendedele',
    7.421: '7 og 8 nittendedele',
    0.05: '1 tyvendedel'
}


class TestNiceDateFormat_da(unittest.TestCase):
    def test_convert_times_da(self):
        dt = datetime.datetime(2017, 1, 31, 13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, lang="da-dk"),
                         "et toogtyve")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "et toogtyve om eftermiddagen")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "01:22")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "01:22 PM")
        self.assertEqual(nice_time(dt, lang="da-dk",
                                   speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "tretten toogtyve")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "tretten toogtyve")

        dt = datetime.datetime(2017, 1, 31, 13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "et")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "et om eftermiddagen")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "01:00")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "01:00 PM")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "tretten")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "tretten")

        dt = datetime.datetime(2017, 1, 31, 13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "et nul to")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "et nul to om eftermiddagen")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "01:02")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "01:02 PM")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "tretten nul to")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "tretten nul to")

        dt = datetime.datetime(2017, 1, 31, 0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "tolv nul to")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "tolv nul to om natten")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "nul nul to")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "nul nul to")

        dt = datetime.datetime(2017, 1, 31, 12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "tolv femten")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "tolv femten om eftermiddagen")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "tolv femten")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "tolv femten")

        dt = datetime.datetime(2017, 1, 31, 19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "syv fyrre")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "syv fyrre om aftenen")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "07:40")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "07:40 PM")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "nitten fyrre")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "nitten fyrre")

        dt = datetime.datetime(2017, 1, 31, 1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True),
                         "et femten")

        dt = datetime.datetime(2017, 1, 31, 1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"),
                         "et femogtredive")

        dt = datetime.datetime(2017, 1, 31, 1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "et femogfyrre")

        dt = datetime.datetime(2017, 1, 31, 4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "fire halvtres")

        dt = datetime.datetime(2017, 1, 31, 5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "fem femoghalvtres")

        dt = datetime.datetime(2017, 1, 31, 5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "fem tredive om morgenen")


if __name__ == "__main__":
    unittest.main()
