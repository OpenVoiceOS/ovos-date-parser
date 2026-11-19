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
import unittest
from datetime import datetime


# --- test harness compatibility shims (adapt legacy call convention to dev API) ---
import ovos_date_parser as _odp
from ovos_config.locale import get_default_tz as default_timezone
LANG = "eu"


def extract_datetime(text, anchorDate=None, lang=LANG, default_time=None):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchorDate,
                                default_time=default_time)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=default_timezone()), res[1]]
    return res


def extract_duration(text, lang=LANG):
    return _odp.extract_duration(text, lang=lang)


# --- end shims ---

class TestDatetime_eu(unittest.TestCase):


    # TODO fix bug causing these tests to fail (MycroftAI/mycroft-core#2348)
    #         reparar error de traducción preveniendo las funciones abajo de
    #         retornar correctamente
    #         (escrito con disculpas por un Inglés hablante)
    #      further broken tests are below their respective working tests.
    def test_bugged_output_wastebasket(self):
        # It's failing on years
        self.assertEqual(extract_datetime("11 abu 1998", lang='eu')[0],
                         datetime(1998, 8, 11, tzinfo=default_timezone()))

    def test_extract_datetime_relative(self):
        # A part of the day answers the middle of its band: night
        # 21:00-24:00 is 22:30, morning 00:00-12:00 is 06:00 and afternoon
        # 12:00-19:00 is 15:30. "honetan" (in this) is part of the date.
        self.assertEqual(extract_datetime("gaurko gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu'), [datetime(1998, 1, 1, 22, 30, 0, tzinfo=default_timezone()), ''])
        self.assertEqual(extract_datetime("gau honetan", anchorDate=datetime(1998, 1, 1),
                                          lang='eu'),
                         [datetime(1998, 1, 1, 22, 30, 0, tzinfo=default_timezone()), ''])
        self.assertEqual(extract_datetime("atzoko gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 31, 22, 30, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("herenegungo gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 30, 22, 30, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("duela 3 eguneko gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 29, 22, 30, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("biharko goiza", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1998, 1, 2, 6, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("atzoko arratsaldea", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 31, 15, 30, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("duela 2 egun", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 30, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("gaurko goizeko 2", lang='eu', anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 2, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("gaurko arratsaldeko 2", lang='eu', anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 14, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("datorren urtea", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1999, 1, 1, tzinfo=default_timezone()))

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""
        self.assertEqual(extract_datetime('ez dago denborarik', lang='eu-eu'), None)

    @unittest.skip("These phrases are not parsing correctly.")
    def test_extract_datetime_relative_failing(self):
        self.assertEqual(extract_datetime("bart", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 31, 21, tzinfo=default_timezone()))


if __name__ == "__main__":
    unittest.main()
