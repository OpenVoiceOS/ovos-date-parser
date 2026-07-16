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
from datetime import datetime, time, timedelta

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

LANG = "gl"


def extract_datetime(text, anchorDate=None, lang=LANG, default_time=None):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchorDate,
                                default_time=default_time)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=default_timezone()), res[1]]
    return res


def extract_duration(text, lang=LANG):
    return _odp.extract_duration(text, lang=lang)


class TestDatetimeGl(unittest.TestCase):
    # anchor: 1998-01-01 was a thursday
    ANCHOR = datetime(1998, 1, 1)
    ANCHOR_NOON = datetime(1998, 1, 1, 12, 0)

    def test_weekday(self):
        # next friday after thursday jan 1st is jan 2nd
        self.assertEqual(
            extract_datetime("venres", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 2, tzinfo=default_timezone()))
        # next monday after thursday jan 1st is jan 5th
        self.assertEqual(
            extract_datetime("luns", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 5, tzinfo=default_timezone()))
        # "que vén" == next occurrence
        self.assertEqual(
            extract_datetime("luns que vén", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 5, tzinfo=default_timezone()))

    def test_tomorrow(self):
        # "mañá" defaults to morning (8:00) of the next day when the
        # anchor is past 8:00
        self.assertEqual(
            extract_datetime("mañá", anchorDate=self.ANCHOR_NOON)[0],
            datetime(1998, 1, 2, 8, 0, tzinfo=default_timezone()))

    def test_yesterday(self):
        self.assertEqual(
            extract_datetime("onte", anchorDate=self.ANCHOR)[0],
            datetime(1997, 12, 31, tzinfo=default_timezone()))

    def test_day_after_tomorrow(self):
        self.assertEqual(
            extract_datetime("pasadomañá", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 3, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("pasado mañá", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 3, tzinfo=default_timezone()))

    def test_in_n_days(self):
        self.assertEqual(
            extract_datetime("en 5 días", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 6, tzinfo=default_timezone()))

    def test_explicit_date(self):
        # june 3rd comes after january 1st, so same year
        self.assertEqual(
            extract_datetime("3 de xuño", anchorDate=self.ANCHOR)[0],
            datetime(1998, 6, 3, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("11 de xaneiro",
                             anchorDate=datetime(1998, 1, 1))[0],
            datetime(1998, 1, 11, tzinfo=default_timezone()))

    def test_time_half_past(self):
        # 8 da tarde == 20:00, e media -> 20:30
        self.assertEqual(
            extract_datetime("ás 8 e media da tarde",
                             anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 20, 30, tzinfo=default_timezone()))

    def test_time_quarter_past(self):
        self.assertEqual(
            extract_datetime("ás 8 e cuarto da mañá",
                             anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 8, 15, tzinfo=default_timezone()))

    def test_time_quarter_to(self):
        # 8 menos cuarto da mañá == 7:45
        self.assertEqual(
            extract_datetime("ás 8 menos cuarto da mañá",
                             anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 7, 45, tzinfo=default_timezone()))

    def test_spoken_hour(self):
        # "ás dúas da tarde" == 14:00
        self.assertEqual(
            extract_datetime("ás dúas da tarde",
                             anchorDate=self.ANCHOR_NOON)[0],
            datetime(1998, 1, 1, 14, 0, tzinfo=default_timezone()))

    def test_noon(self):
        self.assertEqual(
            extract_datetime("mediodía", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 12, 0, tzinfo=default_timezone()))

    def test_midnight(self):
        self.assertEqual(
            extract_datetime("medianoite", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 0, 0, tzinfo=default_timezone()))

    def test_digit_time(self):
        self.assertEqual(
            extract_datetime("ás 17:30", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 17, 30, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("15:30", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 15, 30, tzinfo=default_timezone()))

    def test_next_week(self):
        self.assertEqual(
            extract_datetime("a semana que vén", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 8, tzinfo=default_timezone()))

    def test_last_week(self):
        self.assertEqual(
            extract_datetime("a semana pasada", anchorDate=self.ANCHOR)[0],
            datetime(1997, 12, 25, tzinfo=default_timezone()))

    def test_no_date(self):
        self.assertIsNone(extract_datetime("ola mundo",
                                           anchorDate=self.ANCHOR))
        self.assertIsNone(extract_datetime("non hai tempo",
                                           anchorDate=self.ANCHOR))
        self.assertIsNone(extract_datetime("", anchorDate=self.ANCHOR))

    def test_default_time(self):
        # no time in the sentence -> default_time is applied
        self.assertEqual(
            extract_datetime("en 5 días", anchorDate=self.ANCHOR,
                             default_time=time(9, 30))[0],
            datetime(1998, 1, 6, 9, 30, tzinfo=default_timezone()))


class TestExtractDurationGl(unittest.TestCase):
    def test_extract_duration(self):
        self.assertEqual(extract_duration("10 segundos"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minutos"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 horas"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 días"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 semanas"),
                         (timedelta(weeks=25), ""))


if __name__ == "__main__":
    unittest.main()
