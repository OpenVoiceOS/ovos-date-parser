# -*- coding: utf-8 -*-
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
import unittest
from datetime import datetime, time, timedelta

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    extract_duration, extract_datetime
)


class TestParsing(unittest.TestCase):

    def test_extractdatetime_nl(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 0, 0, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, anchorDate=date,
                                                         lang=LANG)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        testExtract("zet een alarm voor 1 dag na vandaag",
                    "2017-06-28 00:00:00", "zet een alarm")
        testExtract("laten we om 8:00 's avonds afspreken",
                    "2017-06-27 20:00:00", "laten we afspreken")
        testExtract("zet een alarm voor 5 dagen na vandaag",
                    "2017-07-02 00:00:00", "zet een alarm")
        testExtract("wat voor weer is het overmorgen?",
                    "2017-06-29 00:00:00", "wat voor weer is")
        testExtract("herinner me om 10:45 's avonds",
                    "2017-06-27 22:45:00", "herinner me")
        testExtract("Hoe is het weer morgen",
                    "2017-06-28 00:00:00", "hoe is weer")
        testExtract("3 december",
                    "2017-12-03 00:00:00", "")
        testExtract("hoe is het weer vandaag", "2017-06-27 00:00:00",
                    "hoe is weer")
        testExtract("herinner me over 5 jaar aan mijn contract",
                    "2022-06-27 00:00:00", "herinner me aan mijn contract")
        testExtract("hoe is het weer volgende week vrijdag",
                    "2017-06-30 00:00:00", "hoe is weer")
        testExtract("herinner me mijn moeder te bellen op 7 september",
                    "2017-09-07 00:00:00", "herinner me mijn moeder te bellen")
        testExtract("hoe is het weer 3 dagen na vandaag",
                    "2017-06-30 00:00:00", "hoe is weer")
        testExtract(
            "herinner me vanavond aan het ophalen van mijn kinderen",
            "2017-06-27 19:00:00",
            "herinner me aan ophalen van mijn kinderen")
        testExtract(
            "Herinner me mijn moeder te bellen over 8 weken en 2 dagen",
            "2017-08-24 00:00:00", "herinner me mijn moeder te bellen")

        testExtract("Speel rick astley 2 dagen na vrijdag",
                    "2017-07-02 00:00:00", "speel rick astley")
        testExtract("plan een afspraak in de nacht van 3 september",
                    "2017-09-03 00:00:00", "plan een afspraak")

        testExtract("hoe is het weer morgenavond", "2017-06-28 19:00:00",
                    "hoe is weer")
        testExtract("hoe is het weer woensdagavond", "2017-06-28 19:00:00",
                    "hoe is weer")
        testExtract("hoe is het weer dinsdagochtend", "2017-06-27 08:00:00",
                    "hoe is weer")
        testExtract("plan een afspraak in voor donderdagmiddag",
                    "2017-06-29 15:00:00", "plan een afspraak")
        testExtract("Wat voor weer wordt het vrijdagochtend",
                    "2017-06-30 08:00:00", "wat voor weer wordt")

        # TODO these fail altogether
        # testExtract("laten we vanavond om 8:00 uur afspreken",
        #             "2017-06-27 20:00:00", "laten we afspreken")
        # testExtract(
        #     "wordt er regen verwacht op maandag om 3 uur 's middags", "", "")
        # testExtract("plan een afspraak in voor maandagmiddag 4 uur",
        #             "2017-07-03 16:00:00", "plan een afspraak")
        # testExtract("plan een afspraak om 2 uur 's middags",
        #             "2017-06-27 14:00:00", "plan een afspraak")

    def test_extractdatetime_default_nl(self):
        default = time(9, 0, 0)
        anchor = datetime(2019, 11, 1, 0, 0)
        res = extract_datetime("laten we afspreken op donderdag",
                               anchor, lang=LANG, default_time=default)
        self.assertEqual(default, res[0].time())

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""
        self.assertEqual(extract_datetime('geen tijd', lang=LANG), None)

    def test_extract_duration_nl(self):
        self.assertEqual(extract_duration("een minuut", LANG),
                         (timedelta(seconds=60), ""))
        self.assertEqual(extract_duration("10 minuten", LANG),
                         (timedelta(seconds=600), ""))
        self.assertEqual(extract_duration("een uur en 2 minuten", LANG),
                         (timedelta(seconds=3720), "en"))
        self.assertEqual(extract_duration("een dag", LANG),
                         (timedelta(days=1), ""))
        self.assertEqual(extract_duration("twee dag", LANG),
                         (timedelta(days=2), ""))
        self.assertEqual(extract_duration("vijf minuten na het uur", LANG),
                         (timedelta(seconds=300), "na het uur"))
        self.assertEqual(extract_duration("zet een timer voor 1 uur", LANG),
                         (timedelta(seconds=3600), "zet 1 timer voor"))
        self.assertEqual(extract_duration("een treinrit van 2 uur, 17 minuten en zestien seconden", LANG),
                         (timedelta(seconds=8236), "1 treinrit van  ,  en"))
        self.assertEqual(extract_duration("een uurtje", LANG),
                         (timedelta(seconds=3600), ""))


if __name__ == "__main__":
    unittest.main()
