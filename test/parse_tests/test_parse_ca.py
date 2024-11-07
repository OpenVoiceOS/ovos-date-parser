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
from datetime import datetime, time

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    extract_datetime
)


class TestNormalize(unittest.TestCase):
    """
        Test cases for Catalan parsing
    """

    def test_extractdatetime_ca(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 0, 0, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang="ca")
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        testExtract("quin dia és avui",
                    "2017-06-27 00:00:00", "dia")
        testExtract("quin dia som avui",
                    "2017-06-27 00:00:00", "dia")
        testExtract("quin dia és demà",
                    "2017-06-28 00:00:00", "dia")
        testExtract("quin dia va ser ahir",
                    "2017-06-26 00:00:00", "dia ser")
        testExtract("quin dia va ser abans ahir",
                    "2017-06-25 00:00:00", "dia ser")
        testExtract("quin dia va ser abans d'ahir",
                    "2017-06-25 00:00:00", "dia ser")
        testExtract("quin dia va ser abans-d'ahir",
                    "2017-06-25 00:00:00", "dia ser")
        testExtract("quin dia va ser abans d'abans d'ahir",
                    "2017-06-24 00:00:00", "dia ser")
        testExtract("fer el sopar d'aquí 5 dies",
                    "2017-07-02 00:00:00", "fer sopar aquí")
        testExtract("fer el sopar en 5 dies",
                    "2017-07-02 00:00:00", "fer sopar")
        testExtract("quin temps farà demà?",
                    "2017-06-28 00:00:00", "temps farà")
        testExtract("quin temps farà demà-passat?",
                    "2017-06-29 00:00:00", "temps farà")
        testExtract("quin temps farà despús-demà?",
                    "2017-06-29 00:00:00", "temps farà")
        testExtract("quin temps farà despús demà?",
                    "2017-06-29 00:00:00", "temps farà")
        testExtract("truca a la mare les 10:45 pm",
                    "2017-06-27 22:45:00", "truca mare")
        testExtract("quin temps fa el divendres de matí",
                    "2017-06-30 08:00:00", "temps fa")
        testExtract("truca'm per a quedar d'aquí a 8 setmanes i 2 dies",
                    "2017-08-24 00:00:00", "truca m quedar aquí i")
        testExtract("Toca black-metal 2 dies després de divendres",
                    "2017-07-02 00:00:00", "toca black-metal")
        testExtract("Toca satanic black metal 2 dies per a aquest divendres",
                    "2017-07-02 00:00:00", "toca satanic black metal")
        testExtract("Toca super black metal 2 dies a partir d'aquest divendres",
                    "2017-07-02 00:00:00", "toca super black metal")
        testExtract("Começa la invasió a les 3:45 pm de dijous",
                    "2017-06-29 15:45:00", "começa invasió")
        testExtract("dilluns, compra formatge",
                    "2017-07-03 00:00:00", "compra formatge")
        testExtract("Envia felicitacions d'aquí a 5 anys",
                    "2022-06-27 00:00:00", "envia felicitacions aquí")
        testExtract("Envia felicitacions en 5 anys",
                    "2022-06-27 00:00:00", "envia felicitacions")
        testExtract("Truca per Skype a la mare pròxim dijous a les 12:45 pm",
                    "2017-06-29 12:45:00", "truca skype mare")
        testExtract("quin temps fa aquest divendres?",
                    "2017-06-30 00:00:00", "temps fa")
        testExtract("quin temps fa aquest divendres per la tarda?",
                    "2017-06-30 15:00:00", "temps fa")
        testExtract("quin temps farà aquest divendres de matinada?",
                    "2017-06-30 04:00:00", "temps farà")
        testExtract("quin temps fa aquest divendres a mitja nit?",
                    "2017-06-30 00:00:00", "temps fa mitjanit")
        testExtract("quin temps fa aquest divendres al migdia?",
                    "2017-06-30 12:00:00", "temps fa")
        testExtract("quin temps fa aquest divendres al final de tarda?",
                    "2017-06-30 19:00:00", "temps fa")
        testExtract("quin temps fa aquest divendres a mig matí?",
                    "2017-06-30 10:00:00", "temps fa")
        testExtract("recorda de trucar a la mare el dia 3 d'agost",
                    "2017-08-03 00:00:00", "recorda trucar mare")

        testExtract("compra ganivets el 13 de maig",
                    "2018-05-13 00:00:00", "compra ganivets")
        testExtract("gasta diners el dia 13 de maig",
                    "2018-05-13 00:00:00", "gasta diners")
        testExtract("compra espelmes el 13 de maig",
                    "2018-05-13 00:00:00", "compra espelmes")
        testExtract("beure cervesa el 13 de maig",
                    "2018-05-13 00:00:00", "beure cervesa")
        testExtract("quin temps farà 1 dia després de demà",
                    "2017-06-29 00:00:00", "temps farà")
        testExtract("quin temps farà a les 0700 hores",
                    "2017-06-27 07:00:00", "temps farà")
        testExtract("quin temps farà demà a les 7 en punt",
                    "2017-06-28 07:00:00", "temps farà")
        testExtract("quin temps farà demà a les 2 de la tarda",
                    "2017-06-28 14:00:00", "temps farà")
        testExtract("quin temps farà demà a les 2",
                    "2017-06-28 02:00:00", "temps farà")
        testExtract("quin temps farà a les 2 de la tarda de divendres vinent",
                    "2017-06-30 14:00:00", "temps farà vinent")
        testExtract("recorda'm de despertar en 4 anys",
                    "2021-06-27 00:00:00", "recorda m despertar")
        testExtract("recorda'm de despertar en 4 anys i 4 dies",
                    "2021-07-01 00:00:00", "recorda m despertar i")
        # testExtract("dorm 3 dies després de demà",
        #            "2017-07-02 00:00:00", "dorm")
        testExtract("concerta cita d'aquí a 2 setmanes i 6 dies després de dissabte",
                    "2017-07-21 00:00:00", "concerta cita aquí i")
        testExtract("comença la festa a les 8 en punt de la nit de dijous",
                    "2017-06-29 20:00:00", "comença festa")

    def test_extractdatetime_default_ca(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime(
            'concerta cita per a 2 setmanes i 6 dies després de dissabte',
            anchor, lang='ca-es', default_time=default)
        self.assertEqual(default, res[0].time())


if __name__ == "__main__":
    unittest.main()
