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


class TestExtractDatetime(unittest.TestCase):

    def test_extractdatetime_de(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 0, 0)
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang="de-de", )
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        testExtract("mache den frisörtermin in einer halben stunde",
                    "2017-06-27 00:30:00", "mache frisörtermin")

        testExtract("mache den frisörtermin in drei stunden",
                    "2017-06-27 03:00:00", "mache frisörtermin")

        testExtract("setze den frisörtermin auf halb neun abends",
                    "2017-06-27 20:30:00", "setze frisörtermin")

        testExtract("setze den frisörtermin auf halb neun am abend",
                    "2017-06-27 20:30:00", "setze frisörtermin")

        testExtract("setze den timer auf zwölf uhr nachts",
                    "2017-06-28 00:00:00", "setze timer")

        testExtract("setze den frisörtermin auf halb neun",
                    "2017-06-27 08:30:00", "setze frisörtermin")

        testExtract("setze den frisörtermin in 5 tagen",
                    "2017-07-02 00:00:00", "setze frisörtermin")

        testExtract("setze den frisörtermin in 5 tagen um halb 10",
                    "2017-07-02 09:30:00", "setze frisörtermin")

        testExtract("setze den frisörtermin auf 5 tage von heute",
                    "2017-07-02 00:00:00", "setze frisörtermin")

        testExtract("wir bekommen das ergebnis innerhalb eines tages",
                    "2017-06-28 00:00:00", "wir bekommen das ergebnis innerhalb")

        testExtract("wie ist das wetter übermorgen?",
                    "2017-06-29 00:00:00", "wie ist das wetter")

        testExtract("erinnere mich um 10:45 abends",
                    "2017-06-27 22:45:00", "erinnere mich")

        testExtract("was ist das Wetter am freitag morgen",
                    "2017-06-30 08:00:00", "was ist das wetter")

        testExtract("wie ist das wetter morgen",
                    "2017-06-28 00:00:00", "wie ist das wetter")

        testExtract(
            "erinnere mich meine mutter anzurufen in 8 Wochen und 2 Tagen",
            "2017-08-24 00:00:00", "erinnere mich meine mutter anzurufen")

        testExtract("spiele rick astley musik 2 tage von freitag",
                    "2017-07-02 00:00:00", "spiele rick astley musik")

        testExtract("starte die invasion um 3:45 pm am Donnerstag",
                    "2017-06-29 15:45:00", "starte die invasion")

        testExtract("am montag bestelle kuchen von der bäckerei",
                    "2017-07-03 00:00:00", "bestelle kuchen von bäckerei")

        testExtract("spiele happy birthday musik 5 jahre von heute",
                    "2022-06-27 00:00:00", "spiele happy birthday musik")

        testExtract("skype mama um 12:45 pm nächsten Donnerstag",
                    "2017-07-06 12:45:00", "skype mama")

        testExtract("wie ist das wetter nächsten donnerstag?",
                    "2017-07-06 00:00:00", "wie ist das wetter")

        testExtract("wie ist das Wetter nächsten Freitag morgen",
                    "2017-07-07 08:00:00", "wie ist das wetter")

        testExtract("wie ist das wetter nächsten freitag abend",
                    "2017-07-07 19:00:00", "wie ist das wetter")

        testExtract("wie ist das wetter nächsten freitag nachmittag",
                    "2017-07-07 15:00:00", "wie ist das wetter")

        testExtract("erinnere mich mama anzurufen am dritten august",
                    "2017-08-03 00:00:00", "erinnere mich mama anzurufen")

        testExtract("kaufe feuerwerk am einundzwanzigsten juli",
                    "2017-07-21 00:00:00", "kaufe feuerwerk")

        testExtract("wie ist das wetter 2 wochen ab nächsten freitag",
                    "2017-07-21 00:00:00", "wie ist das wetter")

        testExtract("wie ist das wetter am mittwoch um 07:00",
                    "2017-06-28 07:00:00", "wie ist das wetter")

        testExtract("wie ist das wetter am mittwoch um 07:00 Uhr",
                    "2017-06-28 07:00:00", "wie ist das wetter")

        # TTS failure 
        testExtract("wie ist das wetter am mittwoch um 07.00 Uhr",
                    "2017-06-28 07:00:00", "wie ist das wetter")

        # TTS failure
        testExtract("wie ist das wetter am mittwoch um 07.30 Uhr",
                    "2017-06-28 07:30:00", "wie ist das wetter")

        testExtract("wie ist das wetter am mittwoch um 7 uhr",
                    "2017-06-28 07:00:00", "wie ist das wetter")

        testExtract("wie ist das wetter am mittwoch um 7 uhr 30",
                    "2017-06-28 07:30:00", "wie ist das wetter")

        # TTS failure
        testExtract("wie ist das wetter am mittwoch um 7 uhr 30 uhr",
                    "2017-06-28 07:30:00", "wie ist das wetter")

        testExtract("wie ist das wetter am mittwoch um 7:30 Uhr abends",
                    "2017-06-28 19:30:00", "wie ist das wetter")

        testExtract("wie ist das wetter am mittwoch um 7 uhr 30 am abend",
                    "2017-06-28 19:30:00", "wie ist das wetter")

        testExtract("wie ist das wetter am mittwoch um 5 uhr nachmittags",
                    "2017-06-28 17:00:00", "wie ist das wetter")

        testExtract("wie ist das wetter am mittwoch um 11 uhr mittags",
                    "2017-06-28 11:00:00", "wie ist das wetter")

        testExtract("Mache einen Termin um 12:45 pm nächsten donnerstag",
                    "2017-07-06 12:45:00", "mache 1 termin")

        testExtract("wie ist das wetter an diesem donnerstag?",
                    "2017-06-29 00:00:00", "wie ist das wetter")

        testExtract("vereinbare den besuch für 2 wochen und 6 tage ab samstag",
                    "2017-07-21 00:00:00", "vereinbare besuch")

        testExtract("beginne die invasion um 03:45 am donnerstag",
                    "2017-06-29 03:45:00", "beginne die invasion")

        testExtract("beginne die invasion um 3 uhr nachts am donnerstag",
                    "2017-06-29 03:00:00", "beginne die invasion")

        testExtract("beginne die invasion um 8 Uhr am donnerstag",
                    "2017-06-29 08:00:00", "beginne die invasion")

        testExtract("starte die party um 8 uhr abends am donnerstag",
                    "2017-06-29 20:00:00", "starte die party")

        testExtract("starte die invasion um 8 abends am donnerstag",
                    "2017-06-29 20:00:00", "starte die invasion")

        testExtract("starte die invasion am donnerstag um mittag",
                    "2017-06-29 12:00:00", "starte die invasion")

        testExtract("starte die invasion am donnerstag um mitternacht",
                    "2017-06-29 00:00:00", "starte die invasion")

        testExtract("starte die invasion am donnerstag um 5 uhr",
                    "2017-06-29 05:00:00", "starte die invasion")

        testExtract("erinnere mich aufzuwachen in 4 jahren",
                    "2021-06-27 00:00:00", "erinnere mich aufzuwachen")

        testExtract("erinnere mich aufzuwachen in 4 jahren und 4 tagen",
                    "2021-07-01 00:00:00", "erinnere mich aufzuwachen")

        testExtract("wie ist das wetter 3 Tage nach morgen?",
                    "2017-07-01 00:00:00", "wie ist das wetter")

        testExtract("dritter dezember",
                    "2017-12-03 00:00:00", "")

        testExtract("lass uns treffen um 8:00 abends",
                    "2017-06-27 20:00:00", "lass uns treffen")

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""

        self.assertEqual(extract_datetime('kein zeit', lang='de-de'), None)

    def test_extractdatetime_default_de(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime("lass uns treffen am freitag",
                               anchor, lang='de-de', default_time=default)

        self.assertEqual(default, res[0].time())


class TestExtractDuration(unittest.TestCase):
    def test_extract_duration_de(self):
        self.assertEqual(extract_duration("10 sekunden", lang="de-de"),
                         (timedelta(seconds=10.0), ""))

        self.assertEqual(extract_duration("5 minuten", lang="de-de"),
                         (timedelta(minutes=5), ""))

        self.assertEqual(extract_duration("2 stunden", lang="de-de"),
                         (timedelta(hours=2), ""))

        self.assertEqual(extract_duration("3 tage", lang="de-de"),
                         (timedelta(days=3), ""))

        self.assertEqual(extract_duration("25 wochen", lang="de-de"),
                         (timedelta(weeks=25), ""))

        self.assertEqual(extract_duration("sieben stunden"),
                         (timedelta(hours=7), ""))

        self.assertEqual(extract_duration("7,5 sekunden", lang="de-de"),
                         (timedelta(seconds=7.5), ""))

        self.assertEqual(extract_duration(("neun einhalb tage und "
                                           "10 minuten")),
                         (timedelta(days=9.5, minutes=10), "und"))

        self.assertEqual(extract_duration("starte timer für 30 minuten", lang="de-de"),
                         (timedelta(minutes=30), "starte timer für"))

        self.assertEqual(extract_duration(("viereinhalb minuten bis"
                                           " sonnenuntergang")),
                         (timedelta(minutes=4.5), "bis sonnenuntergang"))

        self.assertEqual(extract_duration("neunzehn minuten nach acht"),
                         (timedelta(minutes=19), "nach 8"))

        self.assertEqual(extract_duration(("weck mich in 3 wochen,"
                                           " 497 tagen und"
                                           " 391.6 sekunden"), lang="de-de"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "weck mich in , und"))

        self.assertEqual(extract_duration("weck mich in einer viertel stunde"),
                         (timedelta(hours=0.25), "weck mich in"))

        self.assertEqual(extract_duration(("der film ist eine stunde, fünfzehn"
                                           " einhalb minuten lang")),
                         (timedelta(hours=1, minutes=15.5),
                          "der film ist , lang"))

        # wenn überhaupt wäre anstatt -sekunde -sekündig[e][ns] notwendig
        self.assertEqual(extract_duration("10-sekunden", lang="de-de"),
                         (timedelta(seconds=10.0), ""))

        self.assertEqual(extract_duration("5-minuten", lang="de-de"),
                         (timedelta(minutes=5), ""))


if __name__ == "__main__":
    unittest.main()
