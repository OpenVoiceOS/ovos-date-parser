#
# Copyright 2021 Mycroft AI Inc.
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


class TestNormalize(unittest.TestCase):

    def test_extract_duration_az(self):
        self.assertEqual(extract_duration("10 saniyə"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 dəqiqə"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 saat"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 gün"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 həftə"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("yeddi saat"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 saniyə"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("səkkiz yarım gün otuz"
                                          " doqquz saniyə"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("üç həftə, dörd yüz doxsan yeddi gün, "
                                          "üç yüz 91.6 saniyə sonra məni oyandır"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "sonra məni oyandır"))
        self.assertEqual(extract_duration("10-saniyə"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-dəqiqə"),
                         (timedelta(minutes=5), ""))

    def test_extract_duration_case_az(self):
        self.assertEqual(extract_duration("taymeri 30 dəqiqəyə qur"),
                         (timedelta(minutes=30), "taymeri qur"))
        self.assertEqual(extract_duration("Film bir saat, əlli yeddi"
                                          " yarım dəqiqə davam edir"),
                         (timedelta(hours=1, minutes=57.5),
                          "Film davam edir"))
        self.assertEqual(extract_duration("Gün batana dörd dəqiqə yarım qaldı"),
                         (timedelta(minutes=4.5), "Gün batana  qaldı"))
        self.assertEqual(extract_duration("Saatı on doqquz dəqiqə keçir"),
                         (timedelta(minutes=19), "Saatı keçir"))

    def test_extractdatetime_fractions_az(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())  # Tue June 27, 2017 @ 1:04pm
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("yarım saat sonra pusu qur",
                    "2017-06-27 13:34:00", "pusu qur")
        testExtract("yarım saat sora anama zəng etməyi xatırlat",
                    "2017-06-27 13:34:00", "anama zəng etməyi xatırlat")

    def test_extractdatetime_az(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())  # Tue June 27, 2017 @ 1:04pm
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            print(res)
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("indi vaxtıdır",
                    "2017-06-27 13:04:00", "vaxtıdır")
        testExtract("bir saniyəyə",
                    "2017-06-27 13:04:01", "")
        testExtract("bir dəqiqəyə",
                    "2017-06-27 13:05:00", "")
        testExtract("gələn onillikə",
                    "2027-06-27 00:00:00", "")
        testExtract("gələn yüzillikə",
                    "2117-06-27 00:00:00", "")
        testExtract("gələn minillikə",
                    "3017-06-27 00:00:00", "")
        testExtract("5 onillikə",
                    "2067-06-27 00:00:00", "")
        testExtract("2 yüzillikə",
                    "2217-06-27 00:00:00", "")
        testExtract("bir saata",
                    "2017-06-27 14:04:00", "")
        testExtract("bir saat ərzində istəyirəm",
                    "2017-06-27 14:04:00", "istəyirəm")
        testExtract("1 saniyəyə",
                    "2017-06-27 13:04:01", "")
        testExtract("2 saniyəyə",
                    "2017-06-27 13:04:02", "")
        testExtract("Pusunu 1 dəqiqə sonraya qur",
                    "2017-06-27 13:05:00", "pusunu qur")
        testExtract("5 gün sonraya pusu qur",
                    "2017-07-02 00:00:00", "pusu qur")
        testExtract("birigün",
                    "2017-06-29 00:00:00", "")
        testExtract("birigün hava necə olacaq?",
                    "2017-06-29 00:00:00", "hava necə olacaq")
        testExtract("Axşam 10:45 də yadıma sal",
                    "2017-06-27 22:45:00", "yadıma sal")
        testExtract("cümə səhər hava necədir",
                    "2017-06-30 08:00:00", "hava necədir")
        testExtract("sabah hava necedir",
                    "2017-06-28 00:00:00", "hava necedir")
        testExtract("bu günortadan sonra hava necədir",
                    "2017-06-27 15:00:00", "hava necədir")
        testExtract("bu axşam hava necədir",
                    "2017-06-27 19:00:00", "hava necədir")
        testExtract("bu səhər hava neceydi",
                    "2017-06-27 08:00:00", "hava neceydi")
        testExtract("8 həftə 2 gün sonra anama zəng etməyi xatırlat",
                    "2017-08-24 00:00:00", "anama zəng etməyi xatırlat")
        testExtract("3 avqustda anama zəng etməyi xatırlat",
                    "2017-08-03 00:00:00", "anama zəng etməyi xatırlat")
        testExtract("sabah 7 də anama zəng etməyi xatırlat",
                    "2017-06-28 07:00:00", "anama zəng etməyi xatırlat")
        testExtract("sabah axşam saat 10 da anama zəng etməyi xatırlat",
                    "2017-06-28 22:00:00", "anama zəng etməyi xatırlat")
        testExtract("səhər 7 də anama zəng etməyi xatırlat ",
                    "2017-06-28 07:00:00", "anama zəng etməyi xatırlat")
        testExtract("bir saatdan sonra anama zəng etməyi xatırlat",
                    "2017-06-27 14:04:00", "anama zəng etməyi xatırlat")
        testExtract("anama 17 30 da zəng etməyi xatırlat",
                    "2017-06-27 17:30:00", "anama zəng etməyi xatırlat")
        testExtract("anama 06 30 da zəng etməyi xatırlat",
                    "2017-06-28 06:30:00", "anama zəng etməyi xatırlat")
        testExtract("06 30 da anama zəng etməyi xatırlat",
                    "2017-06-28 06:30:00", "anama zəng etməyi xatırlat")
        testExtract("Cümə axşamı səhər 7:00 də anama zəng etməyi xatırlat",
                    "2017-06-29 07:00:00", "anama zəng etməyi xatırlat")
        testExtract("çərşənbə axşam 8 də anama zəng etməyi xatırlat",
                    "2017-06-28 20:00:00", "anama zəng etməyi xatırlat")
        testExtract("iki saatdan sonra anama zəng etməyi xatırlat",
                    "2017-06-27 15:04:00", "anama zəng etməyi xatırlat")
        testExtract("2 saatdan sonra anama zəng etməyi xatırlat",
                    "2017-06-27 15:04:00", "anama zəng etməyi xatırlat")
        testExtract("15 dəqiqə sonra anama zəng etməyi xatırlat",
                    "2017-06-27 13:19:00", "anama zəng etməyi xatırlat")
        testExtract("on beş dəqiqədən sonra anama zəng etməyi xatırlat",
                    "2017-06-27 13:19:00", "anama zəng etməyi xatırlat")
        testExtract("bu şənbə günündən 2 gün sonra səhər 10 da anama zəng etməyi xatırlat",
                    "2017-07-03 10:00:00", "anama zəng etməyi xatırlat")
        testExtract("Cümə günündən 2 gün sonra Rick Astley musiqisini çal",
                    "2017-07-02 00:00:00", "rick astley musiqisini çal")
        testExtract("Cümə axşamı günü saat 15:45 də hücuma başlayın",
                    "2017-06-29 15:45:00", "hücuma başlayın")
        testExtract("Bazar ertəsi günü çörəkxanadan çörək sifariş vər",
                    "2017-07-03 00:00:00", "çörəkxanadan çörək sifariş vər")
        testExtract("Bu gündən 5 il sonra Happy Birthday musiqisini çal",
                    "2022-06-27 00:00:00", "happy birthday musiqisini çal")
        testExtract("gələn cümə səhər hava necədir",
                    "2017-06-30 08:00:00", "hava necədir")
        testExtract("gələn cümə axşam hava necədir",
                    "2017-06-30 19:00:00", "hava necədir")
        testExtract("gələn cümə günortadan sonra hava necədir ",
                    "2017-06-30 15:00:00", "hava necədir")
        testExtract("iyulun 4 də atəşfəşanlıq al",
                    "2017-07-04 00:00:00", "atəşfəşanlıq al")
        testExtract("gələn cümə günündən 2 həftə sonra hava necədir",
                    "2017-07-14 00:00:00", "hava necədir")
        testExtract("çərşənbə günü saat 07 00 də hava necədir",
                    "2017-06-28 07:00:00", "hava necədir")
        testExtract("Gələn cümə axşamı saat 12:45 də görüş təyin ed",
                    "2017-07-06 12:45:00", "görüş təyin ed")
        testExtract("Bu cümə axşamı hava necədir?",
                    "2017-06-29 00:00:00", "hava necədir")
        testExtract("Cümə axşamı 03 45 də hücuma başlayın",
                    "2017-06-29 03:45:00", "hücuma başlayın")
        testExtract("Cümə axşamı axşam 8 də hücuma başlayın",
                    "2017-06-29 20:00:00", "hücuma başlayın")
        testExtract("Cümə axşamı günortada hücuma başlayın",
                    "2017-06-29 12:00:00", "hücuma başlayın")
        testExtract("Cümə axşamı gecə yarısında hücuma başlayın",
                    "2017-06-29 00:00:00", "hücuma başlayın")
        testExtract("Cümə axşamı saat 05:00 da hücuma başlayın",
                    "2017-06-29 05:00:00", "hücuma başlayın")
        testExtract("4 il sonra oyanmağı xatırlat",
                    "2021-06-27 00:00:00", "oyanmağı xatırlat")
        testExtract("4 il 4 gündə oyanmağı xatırlat",
                    "2021-07-01 00:00:00", "oyanmağı xatırlat")
        testExtract("dekabr 3",
                    "2017-12-03 00:00:00", "")
        testExtract("bu axşam saat 8:00 da görüşək",
                    "2017-06-27 20:00:00", "görüşək")
        testExtract("axşam 5 də görüşək ",
                    "2017-06-27 17:00:00", "görüşək")
        testExtract("səhər 8 də görüşək",
                    "2017-06-28 08:00:00", "görüşək")
        testExtract("mənə səhər 8 də oyanmağı xatırlat",
                    "2017-06-28 08:00:00", "mənə oyanmağı xatırlat")
        testExtract("çərşənbə axşamı hava necədir",
                    "2017-06-27 00:00:00", "hava necədir")
        testExtract("bazar ertəsi hava necədir",
                    "2017-07-03 00:00:00", "hava necədir")
        testExtract("bu çərşənbə günü hava necədir",
                    "2017-06-28 00:00:00", "hava necədir")
        testExtract("keçən bazar ertəsi hava necə idi",
                    "2017-06-26 00:00:00", "hava necə idi")
        testExtract("5 iyun 2017 ci il axşamı anama zəng etməyi xatırlat",
                    "2017-06-05 19:00:00", "anama zəng etməyi xatırlat")
        testExtract("dünən hansı gün idi",
                    "2017-06-26 00:00:00", "hansı gün idi")
        testExtract("dünən 6 da şam yedim",
                    "2017-06-26 06:00:00", "şam yedim")
        testExtract("dünən səhər 6 da şam yedim",
                    "2017-06-26 06:00:00", "şam yedim")
        testExtract("dünən axşam 6 da şam yedim",
                    "2017-06-26 18:00:00", "şam yedim")

    def test_extract_relativedatetime_az(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("5 dəqiqəyə görüşək",
                    "2017-06-27 10:06:02", "görüşək")
        testExtract("5 saniyədə görüşək",
                    "2017-06-27 10:01:07", "görüşək")
        testExtract("1 saatda görüşək",
                    "2017-06-27 11:01:02", "görüşək")
        testExtract("2 saata görüşək",
                    "2017-06-27 12:01:02", "görüşək")


if __name__ == "__main__":
    unittest.main()
