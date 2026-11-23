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

import pytest

from ovos_date_parser import (
    extract_duration, extract_datetime
)


class TestExtractDatetime(unittest.TestCase):

    def test_extractdatetime_de(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 0, 0)
            [extractedDate, leftover] = extract_datetime(text, lang="de-de", anchorDate=date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        # the remainder keeps the words that are not part of the date: an
        # article, and the preposition the verb takes ("setze ... auf")
        testExtract("mache den frisörtermin in einer halben stunde",
                    "2017-06-27 00:30:00", "mache den frisörtermin")

        testExtract("mache den frisörtermin in drei stunden",
                    "2017-06-27 03:00:00", "mache den frisörtermin")

        testExtract("setze den frisörtermin auf halb neun abends",
                    "2017-06-27 20:30:00", "setze den frisörtermin auf")

        # midnight equal to the anchor is the anchor (routing ruling, class 3)
        testExtract("setze den timer auf zwölf uhr nachts",
                    "2017-06-27 00:00:00", "setze den timer")

        testExtract("setze den frisörtermin auf halb neun",
                    "2017-06-27 08:30:00", "setze den frisörtermin auf")

        testExtract("setze den frisörtermin in 5 tagen",
                    "2017-07-02 00:00:00", "setze den frisörtermin")

        testExtract("wie ist das wetter übermorgen?",
                    "2017-06-29 00:00:00", "wie ist das wetter")

        testExtract("wie ist das wetter morgen",
                    "2017-06-28 00:00:00", "wie ist das wetter")

        testExtract(
            "erinnere mich meine mutter anzurufen in 8 Wochen und 2 Tagen",
            "2017-08-24 00:00:00", "erinnere mich meine mutter anzurufen")

        testExtract("spiele rick astley musik 2 tage von freitag",
                    "2017-07-02 00:00:00", "spiele rick astley musik")

        # the next Thursday after the anchor (routing ruling, class 3)
        testExtract("wie ist das wetter nächsten donnerstag?",
                    "2017-06-29 00:00:00", "wie ist das wetter")

        # the next Friday, at the middle of the de evening band (ruling 10)
        testExtract("wie ist das wetter nächsten freitag abend",
                    "2017-06-30 21:00:00", "wie ist das wetter")

        # the middle of the de afternoon band, 13:00 to 18:00 (ruling 10)
        testExtract("wie ist das wetter nächsten freitag nachmittag",
                    "2017-06-30 15:30:00", "wie ist das wetter")

        testExtract("wie ist das wetter am mittwoch um 07:00",
                    "2017-06-28 07:00:00", "wie ist das wetter")

        # TTS failure 
        # TTS failure
        testExtract("wie ist das wetter am mittwoch um 7 uhr",
                    "2017-06-28 07:00:00", "wie ist das wetter")

        testExtract("wie ist das wetter am mittwoch um 7 uhr 30",
                    "2017-06-28 07:30:00", "wie ist das wetter")

        # TTS failure
        testExtract("wie ist das wetter am mittwoch um 7 uhr 30 uhr",
                    "2017-06-28 07:30:00", "wie ist das wetter")

        testExtract("wie ist das wetter am mittwoch um 5 uhr nachmittags",
                    "2017-06-28 17:00:00", "wie ist das wetter")

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

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""

        self.assertEqual(extract_datetime('kein zeit', lang='de-de'), None)

    def test_extractdatetime_default_de(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime("lass uns treffen am freitag", lang='de-de', anchorDate=anchor, default_time=default)

        self.assertEqual(default, res[0].time())


class TestExtractDatetimeGerman(unittest.TestCase):
    """Natural and adversarial German date/time utterances."""

    anchor = datetime(2017, 6, 27, 0, 0)

    def _extract(self, text):
        res = extract_datetime(text, lang="de-de", anchorDate=self.anchor)
        if res is None:
            return None
        return [res[0].strftime("%Y-%m-%d %H:%M:%S"), res[1]]

    def test_part_of_day_makes_hour_pm(self):
        # explicit hour + part-of-day must convert to the evening hour
        self.assertEqual(self._extract("sieben uhr abends"),
                         ["2017-06-27 19:00:00", ""])
        self.assertEqual(self._extract("acht uhr abends"),
                         ["2017-06-27 20:00:00", ""])
        self.assertEqual(self._extract("elf uhr abends"),
                         ["2017-06-27 23:00:00", ""])
        self.assertEqual(self._extract("drei uhr nachmittags"),
                         ["2017-06-27 15:00:00", ""])
        self.assertEqual(self._extract("neun uhr morgens"),
                         ["2017-06-27 09:00:00", ""])

    def test_halb_is_half_to_next_hour(self):
        # "halb vier" is 03:30 (half to four), not 04:30
        self.assertEqual(self._extract("weck mich um halb vier")[0],
                         "2017-06-27 03:30:00")

    def test_trailing_clock_number_is_not_a_year(self):
        # a single clock digit after "15. Juni" must not be grabbed as the
        # year; the remainder keeps the case of the text
        self.assertEqual(self._extract("Treffen am 15. Juni um drei uhr"),
                         ["2018-06-15 03:00:00", "Treffen"])
        self.assertEqual(self._extract("15. Juni um sieben uhr"),
                         ["2018-06-15 07:00:00", ""])

    def test_explicit_four_digit_year_still_parses(self):
        self.assertEqual(self._extract("Treffen am 15. Juni 2019"),
                         ["2019-06-15 00:00:00", "Treffen"])
        self.assertEqual(self._extract("kaufe feuerwerk am 21. juli 2020"),
                         ["2020-07-21 00:00:00", "kaufe feuerwerk"])

    def test_leap_day_without_year_rolls_to_next_leap_year(self):
        # 2017 is not a leap year, the next 29 Feb is in 2020
        self.assertEqual(self._extract("am 29. februar"),
                         ["2020-02-29 00:00:00", ""])
        self.assertEqual(self._extract("am 29. februar 2020"),
                         ["2020-02-29 00:00:00", ""])

    def test_impossible_calendar_dates_return_none(self):
        # invalid days must not raise, they yield no datetime
        for text in ["am 31. juni", "am 31. april",
                     "am 32. märz", "am 29. februar 2021"]:
            with self.subTest(text=text):
                self.assertEqual(
                    extract_datetime(text, lang="de-de", anchorDate=self.anchor),
                    None)

    @pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1035")
    def test_day_zero_returns_none(self):
        self.assertIsNone(extract_datetime("am 0. januar", lang="de-de",
                                           anchorDate=self.anchor))

    def test_wraparound_midnight(self):
        # midnight equal to the anchor is the anchor (routing ruling, class 3);
        # the remainder keeps the article and the verb's preposition
        self.assertEqual(self._extract("setze den timer auf zwölf uhr nachts"),
                         ["2017-06-27 00:00:00", "setze den timer"])

    def test_empty_and_junk_return_none(self):
        for text in ["", "   ", "?", "kein zeit", "hallo wie geht es dir"]:
            with self.subTest(text=text):
                self.assertEqual(
                    extract_datetime(text, lang="de-de", anchorDate=self.anchor),
                    None)

    def test_lang_code_variants(self):
        for lang in ("de", "de-de", "de-DE"):
            with self.subTest(lang=lang):
                res = extract_datetime("sieben uhr abends", lang=lang,
                                       anchorDate=self.anchor)
                self.assertEqual(res[0].strftime("%H:%M"), "19:00")


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

        self.assertEqual(extract_duration("sieben stunden", lang="de-de"),
                         (timedelta(hours=7), ""))

        self.assertEqual(extract_duration("7,5 sekunden", lang="de-de"),
                         (timedelta(seconds=7.5), ""))

        self.assertEqual(extract_duration(("neun einhalb tage und "
                                           "10 minuten"), lang="de-de"),
                         (timedelta(days=9.5, minutes=10), ""))

        self.assertEqual(extract_duration("starte timer für 30 minuten", lang="de-de"),
                         (timedelta(minutes=30), "starte timer"))

        self.assertEqual(extract_duration(("viereinhalb minuten bis"
                                           " sonnenuntergang"), lang="de-de"),
                         (timedelta(minutes=4.5), "bis sonnenuntergang"))

        self.assertEqual(extract_duration("neunzehn minuten nach acht", lang="de-de"),
                         (timedelta(minutes=19), "nach acht"))

        duration, remainder = extract_duration(("weck mich in 3 wochen,"
                                                " 497 tagen und"
                                                " 391,6 sekunden"),
                                               lang="de-de")
        self.assertEqual(duration, timedelta(weeks=3, days=497,
                                             seconds=391.6))
        self.assertEqual(" ".join(remainder.replace(",", " ").split()),
                         "weck mich in")

        self.assertEqual(extract_duration("weck mich in einer viertel stunde", lang="de-de"),
                         (timedelta(hours=0.25), "weck mich in"))

        duration, remainder = extract_duration(
            ("der film ist eine stunde, fünfzehn"
             " einhalb minuten lang"), lang="de-de")
        self.assertEqual(duration, timedelta(hours=1, minutes=15.5))
        self.assertEqual(" ".join(remainder.replace(",", " ").split()),
                         "der film ist lang")

        # wenn überhaupt wäre anstatt -sekunde -sekündig[e][ns] notwendig
        self.assertEqual(extract_duration("10-sekunden", lang="de-de"),
                         (timedelta(seconds=10.0), ""))

        self.assertEqual(extract_duration("5-minuten", lang="de-de"),
                         (timedelta(minutes=5), ""))


@pytest.mark.parametrize("text,expected_date,expected_leftover", [
    pytest.param(
        "setze den frisörtermin auf halb neun am abend",
        "2017-06-27 20:30:00", "setze den frisörtermin auf",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1002")),
    pytest.param(
        "setze den frisörtermin in 5 tagen um halb 10",
        "2017-07-02 09:30:00", "setze den frisörtermin",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1034")),
    pytest.param(
        "setze den frisörtermin auf 5 tage von heute",
        "2017-07-02 00:00:00", "setze den frisörtermin auf",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1034")),
    pytest.param(
        "wir bekommen das ergebnis innerhalb eines tages",
        "2017-06-28 00:00:00", "wir bekommen das ergebnis",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1034")),
    pytest.param(
        "erinnere mich um 10:45 abends",
        "2017-06-27 22:45:00", "erinnere mich"),
    pytest.param(
        "was ist das Wetter am freitag morgen",
        "2017-06-30 07:30:00", "was ist das Wetter",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1033")),
    pytest.param(
        "starte die invasion um 3:45 pm am Donnerstag",
        "2017-06-29 15:45:00", "starte die invasion",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/992")),
    pytest.param(
        "am montag bestelle kuchen von der bäckerei",
        "2017-07-03 00:00:00", "bestelle kuchen von der bäckerei"),
    pytest.param(
        "spiele happy birthday musik 5 jahre von heute",
        "2022-06-27 00:00:00", "spiele happy birthday musik",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1034")),
    pytest.param(
        "skype mama um 12:45 pm nächsten Donnerstag",
        "2017-06-29 12:45:00", "skype mama",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/992")),
    pytest.param(
        "wie ist das Wetter nächsten Freitag morgen",
        "2017-06-30 07:30:00", "wie ist das Wetter",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1033")),
    pytest.param(
        "erinnere mich mama anzurufen am dritten august",
        "2017-08-03 00:00:00", "erinnere mich mama anzurufen"),
    pytest.param(
        "kaufe feuerwerk am einundzwanzigsten juli",
        "2017-07-21 00:00:00", "kaufe feuerwerk"),
    pytest.param(
        "wie ist das wetter 2 wochen ab nächsten freitag",
        "2017-07-14 00:00:00", "wie ist das wetter",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1034")),
    pytest.param(
        "wie ist das wetter am mittwoch um 07:00 Uhr",
        "2017-06-28 07:00:00", "wie ist das wetter",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1032")),
    pytest.param(
        "wie ist das wetter am mittwoch um 07.00 Uhr",
        "2017-06-28 07:00:00", "wie ist das wetter",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1032")),
    pytest.param(
        "wie ist das wetter am mittwoch um 07.30 Uhr",
        "2017-06-28 07:30:00", "wie ist das wetter",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1032")),
    pytest.param(
        "wie ist das wetter am mittwoch um 7:30 Uhr abends",
        "2017-06-28 19:30:00", "wie ist das wetter"),
    pytest.param(
        "wie ist das wetter am mittwoch um 7 uhr 30 am abend",
        "2017-06-28 19:30:00", "wie ist das wetter",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1002")),
    pytest.param(
        "wie ist das wetter am mittwoch um 11 uhr mittags",
        "2017-06-28 11:00:00", "wie ist das wetter",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1002")),
    pytest.param(
        "Mache einen Termin um 12:45 pm nächsten donnerstag",
        "2017-06-29 12:45:00", "Mache einen Termin",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/992")),
    pytest.param(
        "wie ist das wetter an diesem donnerstag?",
        "2017-06-29 00:00:00", "wie ist das wetter"),
    pytest.param(
        "vereinbare den besuch für 2 wochen und 6 tage ab samstag",
        "2017-07-21 00:00:00", "vereinbare den besuch für",
        marks=pytest.mark.xfail(
            strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1034")),
    pytest.param(
        "beginne die invasion um 03:45 am donnerstag",
        "2017-06-29 03:45:00", "beginne die invasion"),
    pytest.param(
        "lass uns treffen um 8:00 abends",
        "2017-06-27 20:00:00", "lass uns treffen"),
])
def test_extractdatetime_de_gaps(text, expected_date, expected_leftover):
    extracted, leftover = extract_datetime(text, lang='de-de',
                                           anchorDate=datetime(2017, 6, 27, 0, 0))
    assert (extracted.strftime("%Y-%m-%d %H:%M:%S"), leftover) == \
        (expected_date, expected_leftover)


if __name__ == "__main__":
    unittest.main()
