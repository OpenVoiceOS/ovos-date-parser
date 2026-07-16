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

LANG = "ast"


def extract_datetime(text, anchorDate=None, lang=LANG, default_time=None):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchorDate,
                                default_time=default_time)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=default_timezone()), res[1]]
    return res


def extract_duration(text, lang=LANG):
    return _odp.extract_duration(text, lang=lang)


class TestDatetimeAst(unittest.TestCase):
    # anchor: 1998-01-01 was a thursday
    ANCHOR = datetime(1998, 1, 1)
    ANCHOR_NOON = datetime(1998, 1, 1, 12, 0)

    def test_weekday(self):
        # next friday after thursday jan 1st is jan 2nd
        self.assertEqual(
            extract_datetime("vienres", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 2, tzinfo=default_timezone()))
        # next monday after thursday jan 1st is jan 5th
        self.assertEqual(
            extract_datetime("llunes", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 5, tzinfo=default_timezone()))
        # "que vien" == next occurrence
        self.assertEqual(
            extract_datetime("llunes que vien", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 5, tzinfo=default_timezone()))

    def test_tomorrow(self):
        # "mañana" defaults to morning (8:00) of the next day when the
        # anchor is past 8:00
        self.assertEqual(
            extract_datetime("mañana", anchorDate=self.ANCHOR_NOON)[0],
            datetime(1998, 1, 2, 8, 0, tzinfo=default_timezone()))

    def test_today(self):
        self.assertEqual(
            extract_datetime("güei", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, tzinfo=default_timezone()))

    def test_yesterday(self):
        self.assertEqual(
            extract_datetime("ayeri", anchorDate=self.ANCHOR)[0],
            datetime(1997, 12, 31, tzinfo=default_timezone()))

    def test_day_after_tomorrow(self):
        self.assertEqual(
            extract_datetime("pasáu mañana", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 3, tzinfo=default_timezone()))

    def test_in_n_days(self):
        self.assertEqual(
            extract_datetime("en 5 díes", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 6, tzinfo=default_timezone()))

    def test_explicit_date(self):
        # june 3rd comes after january 1st, so same year
        self.assertEqual(
            extract_datetime("3 de xunu", anchorDate=self.ANCHOR)[0],
            datetime(1998, 6, 3, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("11 de xineru",
                             anchorDate=datetime(1998, 1, 1))[0],
            datetime(1998, 1, 11, tzinfo=default_timezone()))

    def test_time_half_past(self):
        # 8 de la tarde == 20:00, y media -> 20:30
        self.assertEqual(
            extract_datetime("a les 8 y media de la tarde",
                             anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 20, 30, tzinfo=default_timezone()))

    def test_time_quarter_past(self):
        self.assertEqual(
            extract_datetime("a les 8 y cuartu de la mañana",
                             anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 8, 15, tzinfo=default_timezone()))

    def test_time_quarter_to(self):
        # 8 menos cuartu de la mañana == 7:45
        self.assertEqual(
            extract_datetime("a les 8 menos cuartu de la mañana",
                             anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 7, 45, tzinfo=default_timezone()))

    def test_spoken_hour(self):
        # "a les dos de la tarde" == 14:00
        self.assertEqual(
            extract_datetime("a les dos de la tarde",
                             anchorDate=self.ANCHOR_NOON)[0],
            datetime(1998, 1, 1, 14, 0, tzinfo=default_timezone()))

    def test_noon(self):
        self.assertEqual(
            extract_datetime("mediudía", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 12, 0, tzinfo=default_timezone()))

    def test_midnight(self):
        self.assertEqual(
            extract_datetime("medianueche", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 0, 0, tzinfo=default_timezone()))

    def test_digit_time(self):
        self.assertEqual(
            extract_datetime("a les 17:30", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 17, 30, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("15:30", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 15, 30, tzinfo=default_timezone()))

    def test_next_week(self):
        self.assertEqual(
            extract_datetime("la selmana que vien", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 8, tzinfo=default_timezone()))

    def test_last_week(self):
        self.assertEqual(
            extract_datetime("la selmana pasada", anchorDate=self.ANCHOR)[0],
            datetime(1997, 12, 25, tzinfo=default_timezone()))

    def test_no_date(self):
        self.assertIsNone(extract_datetime("hola mundu",
                                           anchorDate=self.ANCHOR))
        self.assertIsNone(extract_datetime("nun hai tiempu",
                                           anchorDate=self.ANCHOR))
        self.assertIsNone(extract_datetime("", anchorDate=self.ANCHOR))

    def test_default_time(self):
        # no time in the sentence -> default_time is applied
        self.assertEqual(
            extract_datetime("en 5 díes", anchorDate=self.ANCHOR,
                             default_time=time(9, 30))[0],
            datetime(1998, 1, 6, 9, 30, tzinfo=default_timezone()))


class TestExtractDurationAst(unittest.TestCase):
    def test_extract_duration(self):
        self.assertEqual(extract_duration("10 segundos"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minutos"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 hores"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 díes"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 selmanes"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("1 hora"),
                         (timedelta(hours=1), ""))
        self.assertEqual(extract_duration("1 día"),
                         (timedelta(days=1), ""))
        self.assertEqual(extract_duration("1 selmana"),
                         (timedelta(weeks=1), ""))


if __name__ == "__main__":
    unittest.main()
