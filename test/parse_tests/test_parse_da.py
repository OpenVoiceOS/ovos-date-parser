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

    def test_extractdatetime_da(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 0, 0, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang="da-dk", )
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        testExtract("sæt frisøraftale på fredag",
                    "2017-06-30 00:00:00", "sæt frisøraftale")
        testExtract("hvordan er vejret i overmorgen?",
                    "2017-06-29 00:00:00", "hvordan er vejret")
        testExtract("mind mig om det 10:45 i aften",
                    "2017-06-27 22:45:00", "mind mig")
        testExtract("hvordan er vejret fredag om morgenen",
                    "2017-06-30 08:00:00", "hvordan er vejret")
        #        testExtract("hvordan er vejret i morgen",
        #                    "2017-06-28 00:00:00", "hvordan er vejret")
        testExtract(
            "påmind mig at ringe min mor om 8 uger og 2 dage",
            "2017-08-24 00:00:00", "påmind mig at ringe min mor")
        testExtract("afspil rick astley musik 2 dage fra fredag",
                    "2017-07-02 00:00:00", "afspil rick astley musik")
        testExtract("start inversionen 3:45 pm på torsdag",
                    "2017-06-29 15:45:00", "start inversionen")
        testExtract("på mandag bestil kager fra bageren",
                    "2017-07-03 00:00:00", "bestil kager fra bageren")
        testExtract("spil happy birthday musik om 5 år fra nu",
                    "2022-06-27 00:00:00", "spil happy birthday musik")
        testExtract("skype mor klokken 12:45 pm næste torsdag",
                    "2017-07-06 12:45:00", "skype mor")
        testExtract("hvordan er vejret på næste torsdag",
                    "2017-07-06 00:00:00", "hvordan er vejret")
        testExtract("hvordan er vejret næste fredag morgen",
                    "2017-07-07 08:00:00", "hvordan er vejret")
        testExtract("hvordan er vejret næste fredag aften",
                    "2017-07-07 19:00:00", "hvordan er vejret")
        testExtract("hvordan er vejret næste fredag eftermiddag",
                    "2017-07-07 15:00:00", "hvordan er vejret")
        testExtract("påmind mig at ringe min mor den tredie august",
                    "2017-08-03 00:00:00", "påmind mig at ringe min mor")
        testExtract("køb fyrværkeri den enogtyvende juli",
                    "2017-07-21 00:00:00", "køb fyrværkeri")
        testExtract("hvordan er vejret 2 uger fra næste fredag",
                    "2017-07-21 00:00:00", "hvordan er vejret")
        testExtract("hvordan er vejret på onsdag klokken 07:00",
                    "2017-06-28 07:00:00", "hvordan er vejret")
        testExtract("hvordan er vejret på onsdag klokken 7",
                    "2017-06-28 07:00:00", "hvordan er vejret")
        testExtract("marker en termin klokken 12:45 på næste torsdag",
                    "2017-07-06 12:45:00", "marker en termin")
        testExtract("hvordan er vejret på torsdag",
                    "2017-06-29 00:00:00", "hvordan er vejret")
        testExtract("forbered et besøg på 2 uger og 6 dage fra på lørdag",
                    "2017-07-21 00:00:00", "forbered et besøg")
        testExtract("begynd invasionen klokken 03:45 på torsdag",
                    "2017-06-29 03:45:00", "begynd invasionen")
        testExtract("begynd invasionen klokken 3 om natten på torsdag",
                    "2017-06-29 03:00:00", "begynd invasionen")
        testExtract("begynd invasionen klokken 8 am på torsdag",
                    "2017-06-29 08:00:00", "begynd invasionen")
        testExtract("start festen klokken 8 om aftenen på torsdag",
                    "2017-06-29 20:00:00", "start festen")
        testExtract("start invasionen klokken 8 om aftenen på torsdag",
                    "2017-06-29 20:00:00", "start invasionen")
        testExtract("start invasionen på torsdag ved middag",
                    "2017-06-29 12:00:00", "start invasionen")
        #        testExtract("start invasionen på torsdag om eftermiddagen",
        #                    "2017-06-29 00:00:00", "start invasionen")
        testExtract("start invasionen på torsdag klokken 5",
                    "2017-06-29 05:00:00", "start invasionen")
        testExtract("husk at vågne op om 4 år",
                    "2021-06-27 00:00:00", "husk at vågne op")
        testExtract("husk at vågne op om 4 år og 4 dage",
                    "2021-07-01 00:00:00", "husk at vågne op")

    #        testExtract("hvordan er vejret om 3 dage fra i morgen",
    #                    "2017-07-01 00:00:00", "hvordan er vejret")
    #        testExtract("tredie december",
    #                    "2017-12-03 00:00:00", "")
    #        testExtract("lad os mødes klokken 8:00 om aftenen",
    #                    "2017-06-27 20:00:00", "lad os mødes")

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""
        with self.assertWarns(UserWarning):
            self.assertEqual(extract_datetime('ingen tid', lang='da-da'), None)

    def test_extractdatetime_default_da(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime("lad os mødes på fredag klokken 9 om morgenen",
                               anchor, lang='da-dk', default_time=default)
        self.assertEqual(default, res[0].time())


if __name__ == "__main__":
    unittest.main()
