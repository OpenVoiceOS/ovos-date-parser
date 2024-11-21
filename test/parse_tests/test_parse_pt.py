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

from ovos_date_parser import (
    extract_duration, extract_datetime
)


class TestNormalize(unittest.TestCase):
    """
        Test cases for Portuguese parsing
    """

    def test_extractdatetime_pt(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 0, 0, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang="pt")
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        testExtract("que dia é hoje",
                    "2017-06-27 00:00:00", "dia")
        testExtract("que dia é amanha",
                    "2017-06-28 00:00:00", "dia")
        testExtract("que dia foi ontem",
                    "2017-06-26 00:00:00", "dia")
        testExtract("que dia foi antes de ontem",
                    "2017-06-25 00:00:00", "dia")
        testExtract("que dia foi ante ontem",
                    "2017-06-25 00:00:00", "dia")
        testExtract("que dia foi ante ante ontem",
                    "2017-06-24 00:00:00", "dia")
        testExtract("marca o jantar em 5 dias",
                    "2017-07-02 00:00:00", "marca jantar")
        testExtract("como esta o tempo para o dia depois de amanha?",
                    "2017-06-29 00:00:00", "como tempo")
        testExtract("lembra me ás 10:45 pm",
                    "2017-06-27 22:45:00", "lembra")
        testExtract("como esta o tempo na sexta de manha",
                    "2017-06-30 08:00:00", "como tempo")
        testExtract("lembra me para ligar a mãe daqui "
                    "a 8 semanas e 2 dias",
                    "2017-08-24 00:00:00", "lembra ligar mae")
        testExtract("Toca black metal 2 dias a seguir a sexta",
                    "2017-07-02 00:00:00", "toca black metal")
        testExtract("Toca satanic black metal 2 dias para esta sexta",
                    "2017-07-02 00:00:00", "toca satanic black metal")
        testExtract("Toca super black metal 2 dias a partir desta sexta",
                    "2017-07-02 00:00:00", "toca super black metal")
        testExtract("Começa a invasão ás 3:45 pm de quinta feira",
                    "2017-06-29 15:45:00", "comeca invasao")
        testExtract("na segunda, compra queijo",
                    "2017-07-03 00:00:00", "compra queijo")
        testExtract("Toca os parabéns daqui a 5 anos",
                    "2022-06-27 00:00:00", "toca parabens")
        testExtract("manda Skype a Mãe ás 12:45 pm próxima quinta",
                    "2017-06-29 12:45:00", "manda skype mae")
        testExtract("como está o tempo esta sexta?",
                    "2017-06-30 00:00:00", "como tempo")
        testExtract("como está o tempo esta sexta de tarde?",
                    "2017-06-30 15:00:00", "como tempo")
        testExtract("como está o tempo esta sexta as tantas da manha?",
                    "2017-06-30 04:00:00", "como tempo")
        testExtract("como está o tempo esta sexta a meia noite?",
                    "2017-06-30 00:00:00", "como tempo")
        testExtract("como está o tempo esta sexta ao meio dia?",
                    "2017-06-30 12:00:00", "como tempo")
        testExtract("como está o tempo esta sexta ao fim da tarde?",
                    "2017-06-30 19:00:00", "como tempo")
        testExtract("como está o tempo esta sexta ao meio da manha?",
                    "2017-06-30 10:00:00", "como tempo")
        testExtract("lembra me para ligar a mae no dia 3 de agosto",
                    "2017-08-03 00:00:00", "lembra ligar mae")

        testExtract("compra facas no 13º dia de maio",
                    "2018-05-13 00:00:00", "compra facas")
        testExtract("gasta dinheiro no maio dia 13",
                    "2018-05-13 00:00:00", "gasta dinheiro")
        testExtract("compra velas a maio 13",
                    "2018-05-13 00:00:00", "compra velas")
        testExtract("bebe cerveja a 13 maio",
                    "2018-05-13 00:00:00", "bebe cerveja")
        testExtract("como esta o tempo 1 dia a seguir a amanha",
                    "2017-06-29 00:00:00", "como tempo")
        testExtract("como esta o tempo ás 0700 horas",
                    "2017-06-27 07:00:00", "como tempo")
        testExtract("como esta o tempo amanha ás 7 em ponto",
                    "2017-06-28 07:00:00", "como tempo")
        testExtract("como esta o tempo amanha pelas 2 da tarde",
                    "2017-06-28 14:00:00", "como tempo")
        testExtract("como esta o tempo amanha pelas 2",
                    "2017-06-28 02:00:00", "como tempo")
        testExtract("como esta o tempo pelas 2 da tarde da proxima sexta",
                    "2017-06-30 14:00:00", "como tempo")
        testExtract("lembra-me de acordar em 4 anos",
                    "2021-06-27 00:00:00", "lembra acordar")
        testExtract("lembra-me de acordar em 4 anos e 4 dias",
                    "2021-07-01 00:00:00", "lembra acordar")
        testExtract("dorme 3 dias depois de amanha",
                    "2017-07-02 00:00:00", "dorme")
        testExtract("marca consulta para 2 semanas e 6 dias depois de Sabado",
                    "2017-07-21 00:00:00", "marca consulta")
        testExtract("começa a festa ás 8 em ponto da noite de quinta",
                    "2017-06-29 20:00:00", "comeca festa")

    def test_extractdatetime_default_pt(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime(
            'marca consulta para 2 semanas e 6 dias depois de Sabado',
            anchor, lang='pt', default_time=default)
        self.assertEqual(default, res[0].time())


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
        self.assertEqual(extract_duration("sete horas"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 segundos"),
                         (timedelta(seconds=7.5), ""))
        # TODO - imperfect remainder
        self.assertEqual(extract_duration("oito dias e 39 segundos"),
                         (timedelta(days=8, seconds=39), "e"))
        # TODO - imperfect remainder
        self.assertEqual(extract_duration("acorda-me daqui a três semanas, quatro dias e noventa segundos"),
                         (timedelta(weeks=3, days=4, seconds=90),
                          "acorda - me daqui a ,  e"))
        self.assertEqual(extract_duration("10-segundos"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-minutos"),
                         (timedelta(minutes=5), ""))

    def test_non_std_units(self):
        self.assertEqual(extract_duration("1 mês"),
                         (timedelta(days=DAYS_IN_1_MONTH), ""))
        self.assertEqual(
            extract_duration("1 mês"),
            (timedelta(days=DAYS_IN_1_MONTH), ""))

        self.assertEqual(extract_duration("3 meses"),
                         (timedelta(days=DAYS_IN_1_MONTH * 3), ""))
        self.assertEqual(extract_duration("um ano"),
                         (timedelta(days=DAYS_IN_1_YEAR), ""))
        self.assertEqual(extract_duration("1 ano"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1), ""))
        self.assertEqual(extract_duration("5 anos"),
                         (timedelta(days=DAYS_IN_1_YEAR * 5), ""))
        self.assertEqual(extract_duration("uma década"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_duration("1 decada"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_duration("5 decadas"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10 * 5), ""))
        self.assertEqual(extract_duration("1 século"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_duration("um seculo"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_duration("5 séculos"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100 * 5), ""))
        self.assertEqual(extract_duration("1 milénio"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000), ""))
        self.assertEqual(extract_duration("5 milenios"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000 * 5), ""))


if __name__ == "__main__":
    unittest.main()
