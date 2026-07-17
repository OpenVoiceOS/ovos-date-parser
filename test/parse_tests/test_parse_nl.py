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



# --- test harness compatibility shims (adapt legacy call convention to dev API) ---
import ovos_date_parser as _odp
from ovos_utils.time import now_local, to_local, DAYS_IN_1_YEAR, DAYS_IN_1_MONTH
from ovos_config.locale import get_default_tz as default_timezone
LANG = "nl"


def extract_datetime(text, anchorDate=None, lang=LANG, default_time=None):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchorDate,
                                default_time=default_time)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=default_timezone()), res[1]]
    return res


def extract_duration(text, lang=LANG):
    return _odp.extract_duration(text, lang=lang)


def normalize(text, lang=LANG, remove_articles=True):
    # the dev extractors normalize internally; passthrough preserves assertions
    return text
# --- end shims ---

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
        duration, remainder = extract_duration(
            "een treinrit van 2 uur, 17 minuten en zestien seconden", LANG)
        self.assertEqual(duration, timedelta(seconds=8236))
        self.assertEqual(" ".join(remainder.replace(",", " ").split()),
                         "1 treinrit van en")
        self.assertEqual(extract_duration("een uurtje", LANG),
                         (timedelta(seconds=3600), ""))


class TestParsingNatural(unittest.TestCase):
    """Natural spoken Dutch and adversarial inputs for extract_datetime."""

    def setUp(self):
        self.anchor = datetime(2017, 6, 27, 0, 0,
                               tzinfo=default_timezone())

    def _extract(self, text):
        return extract_datetime(text, anchorDate=self.anchor, lang=LANG)

    def _fmt(self, text):
        res = self._extract(text)
        self.assertIsNotNone(res, text)
        return res[0].strftime("%Y-%m-%d %H:%M:%S"), res[1]

    def test_dutch_month_names(self):
        # months whose Dutch spelling differs from the English one must not
        # crash the parser (strptime "%B" only knows C-locale month names)
        self.assertEqual(self._fmt("afspraak op 3 mei")[0],
                         "2018-05-03 00:00:00")
        self.assertEqual(self._fmt("afspraak op 5 juli")[0],
                         "2017-07-05 00:00:00")
        self.assertEqual(self._fmt("afspraak op 20 oktober")[0],
                         "2017-10-20 00:00:00")
        self.assertEqual(self._fmt("afspraak op 10 augustus")[0],
                         "2017-08-10 00:00:00")
        self.assertEqual(self._fmt("15 maart 2019")[0],
                         "2019-03-15 00:00:00")
        self.assertEqual(self._fmt("29 februari 2020")[0],
                         "2020-02-29 00:00:00")

    def test_all_month_names_do_not_crash(self):
        for m in ['januari', 'februari', 'maart', 'april', 'mei', 'juni',
                  'juli', 'augustus', 'september', 'oktober', 'november',
                  'december']:
            with self.subTest(month=m):
                res = self._extract("afspraak op 12 " + m)
                self.assertIsNotNone(res)
                self.assertEqual(res[0].day, 12)

    def test_part_of_day_makes_hour_pm(self):
        # a genitive part-of-day after an explicit hour marks it as pm
        self.assertEqual(self._fmt("3 uur 's middags")[0],
                         "2017-06-27 15:00:00")
        self.assertEqual(self._fmt("8 uur 's avonds")[0],
                         "2017-06-27 20:00:00")
        self.assertEqual(self._fmt("om 2 uur 's middags")[0],
                         "2017-06-27 14:00:00")
        date, leftover = self._fmt("plan een afspraak om 2 uur 's middags")
        self.assertEqual(date, "2017-06-27 14:00:00")
        self.assertEqual(leftover, "plan een afspraak")

    def test_part_of_day_morning_stays_am(self):
        self.assertEqual(self._fmt("3 uur 's ochtends")[0],
                         "2017-06-27 03:00:00")

    def test_hour_after_date_not_swallowed_as_year(self):
        # "3 uur" following a date must be a clock time, not a bogus year
        self.assertEqual(self._fmt("15 december 3 uur")[0],
                         "2017-12-15 03:00:00")
        self.assertEqual(self._fmt("afspraak op 15 juni om 3 uur")[0],
                         "2018-06-15 03:00:00")

    def test_relative_hour_offset_preserved(self):
        # "over 3 uur" stays a duration offset from the anchor
        self.assertEqual(self._fmt("over 3 uur")[0],
                         "2017-06-27 03:00:00")

    def test_mixed_case(self):
        self.assertEqual(self._fmt("AFSPRAAK OP 3 MEI")[0],
                         "2018-05-03 00:00:00")

    def test_no_date_returns_none(self):
        for junk in ["", "   ", "geen tijd hier", "hallo wereld", "!!!"]:
            with self.subTest(junk=junk):
                self.assertIsNone(self._extract(junk))


if __name__ == "__main__":
    unittest.main()
