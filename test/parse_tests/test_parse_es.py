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
from datetime import datetime, timedelta

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    extract_duration, extract_datetime
)


class TestDatetime_es(unittest.TestCase):

    def test_datetime_by_date_es(self):
        # test currentDate==None
        _now = datetime.now()
        relative_year = _now.year if (_now.month == 1 and _now.day < 11) else \
            (_now.year + 1)
        self.assertEqual(extract_datetime_es("11 ene", anchorDate=_now)[0],
                         datetime(relative_year, 1, 11))

        # test months
        self.assertEqual(extract_datetime(
            "11 ene", lang='es', anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 feb", lang='es', anchorDate=datetime(1998, 2, 1))[0],
                         datetime(1998, 2, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 mar", lang='es', anchorDate=datetime(1998, 3, 1))[0],
                         datetime(1998, 3, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 abr", lang='es', anchorDate=datetime(1998, 4, 1))[0],
                         datetime(1998, 4, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 may", lang='es', anchorDate=datetime(1998, 5, 1))[0],
                         datetime(1998, 5, 11, tzinfo=default_timezone()))
        # there is an issue with the months of june through september (below)
        # hay un problema con las meses junio hasta septiembre (lea abajo)
        self.assertEqual(extract_datetime(
            "11 oct", lang='es', anchorDate=datetime(1998, 10, 1))[0],
                         datetime(1998, 10, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 nov", lang='es', anchorDate=datetime(1998, 11, 1))[0],
                         datetime(1998, 11, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 dic", lang='es', anchorDate=datetime(1998, 12, 1))[0],
                         datetime(1998, 12, 11, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("", lang='es'), None)

    # TODO fix bug causing these tests to fail (MycroftAI/mycroft-core#2348)
    #         reparar error de traducción preveniendo las funciones abajo de
    #         retornar correctamente
    #         (escrito con disculpas por un Inglés hablante)
    #      further broken tests are below their respective working tests.
    @unittest.skip("currently processing these months incorrectly")
    def test_bugged_output_wastebasket(self):
        self.assertEqual(extract_datetime(
            "11 jun", lang='es', anchorDate=datetime(1998, 6, 1))[0],
                         datetime(1998, 6, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 junio", lang='es', anchorDate=datetime(1998, 6, 1))[0],
                         datetime(1998, 6, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 jul", lang='es', anchorDate=datetime(1998, 7, 1))[0],
                         datetime(1998, 7, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 ago", lang='es', anchorDate=datetime(1998, 8, 1))[0],
                         datetime(1998, 8, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 sep", lang='es', anchorDate=datetime(1998, 9, 1))[0],
                         datetime(1998, 9, 11, tzinfo=default_timezone()))

        # It's also failing on years
        self.assertEqual(extract_datetime(
            "11 ago 1998", lang='es')[0],
                         datetime(1998, 8, 11, tzinfo=default_timezone()))

    def test_extract_datetime_relative(self):
        self.assertEqual(extract_datetime(
            "esta noche", anchorDate=datetime(1998, 1, 1),
            lang='es'), [datetime(1998, 1, 1, 21, 0, 0, tzinfo=default_timezone()), 'esta'])
        self.assertEqual(extract_datetime(
            "ayer noche", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 31, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "el noche anteayer", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 30, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "el noche ante ante ayer", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 29, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "mañana por la mañana", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1998, 1, 2, 8, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "ayer por la tarde", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 31, 15, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("hoy 2 de la mañana", lang='es',
                                          anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 2, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("hoy 2 de la tarde", lang='es',
                                          anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 14, tzinfo=default_timezone()))

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""
        self.assertEqual(extract_datetime('no hay tiempo', lang='es-es'), None)

    @unittest.skip("These phrases are not parsing correctly.")
    def test_extract_datetime_relative_failing(self):
        # parses as "morning" and returns 8:00 on anchorDate
        self.assertEqual(extract_datetime(
            "mañana", anchorDate=datetime(1998, 1, 1), lang='es')[0],
                         datetime(1998, 1, 2))

        # unimplemented logic
        self.assertEqual(extract_datetime(
            "anoche", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 31, 21))
        self.assertEqual(extract_datetime(
            "anteanoche", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 30, 21))
        self.assertEqual(extract_datetime(
            "hace tres noches", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 29, 21))


class TestExtractDuration(unittest.TestCase):
    def test_extract_duration(self):
        self.assertEqual(extract_duration("10 segundos"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minutos"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 horas"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 dias"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 semanas"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("7.5 segundos"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("10-segundos"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-minutos"),
                         (timedelta(minutes=5), ""))

    def test_non_std_units(self):
        self.assertEqual(
            extract_duration("1 mes"),
            (timedelta(days=DAYS_IN_1_MONTH), ""))

        self.assertEqual(extract_duration("3 meses"),
                         (timedelta(days=DAYS_IN_1_MONTH * 3), ""))
        self.assertEqual(extract_duration("1 año"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1), ""))
        self.assertEqual(extract_duration("5 años"),
                         (timedelta(days=DAYS_IN_1_YEAR * 5), ""))
        self.assertEqual(extract_duration("1 decada"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_duration("5 decadas"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10 * 5), ""))
        self.assertEqual(extract_duration("1 siglo"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_duration("5 siglos"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100 * 5), ""))
        self.assertEqual(extract_duration("1 milenio"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000), ""))
        self.assertEqual(extract_duration("5 milenios"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000 * 5), ""))


if __name__ == "__main__":
    unittest.main()
