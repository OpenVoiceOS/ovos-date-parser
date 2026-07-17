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
from datetime import datetime



# --- test harness compatibility shims (adapt legacy call convention to dev API) ---
import ovos_date_parser as _odp
from ovos_utils.time import now_local, to_local, DAYS_IN_1_YEAR, DAYS_IN_1_MONTH
from ovos_config.locale import get_default_tz as default_timezone
from ovos_date_parser import extract_datetime_eu
LANG = "eu"


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

class TestDatetime_eu(unittest.TestCase):

    def test_datetime_by_date_eu(self):
        # test currentDate==None
        _now = now_local()
        relative_year = _now.year if (_now.month == 1 and _now.day < 11) else \
            (_now.year + 1)
        self.assertEqual(extract_datetime_eu("11 urt")[0],
                         datetime(relative_year, 1, 11))

        # test months
        self.assertEqual(extract_datetime(
            "11 urt", lang='eu', anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 ots", lang='eu', anchorDate=datetime(1998, 2, 1))[0],
                         datetime(1998, 2, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 mar", lang='eu', anchorDate=datetime(1998, 3, 1))[0],
                         datetime(1998, 3, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 api", lang='eu', anchorDate=datetime(1998, 4, 1))[0],
                         datetime(1998, 4, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 mai", lang='eu', anchorDate=datetime(1998, 5, 1))[0],
                         datetime(1998, 5, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 eka", lang='eu', anchorDate=datetime(1998, 6, 1))[0],
                         datetime(1998, 6, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 ekaina", lang='eu', anchorDate=datetime(1998, 6, 1))[0],
                         datetime(1998, 6, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 uztaila", lang='eu', anchorDate=datetime(1998, 7, 1))[0],
                         datetime(1998, 7, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 abu", lang='eu', anchorDate=datetime(1998, 8, 1))[0],
                         datetime(1998, 8, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 ira", lang='eu', anchorDate=datetime(1998, 9, 1))[0],
                         datetime(1998, 9, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 urr", lang='eu', anchorDate=datetime(1998, 10, 1))[0],
                         datetime(1998, 10, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 aza", lang='eu', anchorDate=datetime(1998, 11, 1))[0],
                         datetime(1998, 11, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 abe", lang='eu', anchorDate=datetime(1998, 12, 1))[0],
                         datetime(1998, 12, 11, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("", lang='eu'), None)

    # TODO fix bug causing these tests to fail (MycroftAI/mycroft-core#2348)
    #         reparar error de traducción preveniendo las funciones abajo de
    #         retornar correctamente
    #         (escrito con disculpas por un Inglés hablante)
    #      further broken tests are below their respective working tests.
    def test_bugged_output_wastebasket(self):
        # It's failing on years
        self.assertEqual(extract_datetime("11 abu 1998", lang='eu')[0],
                         datetime(1998, 8, 11, tzinfo=default_timezone()))

    def test_extract_datetime_relative(self):
        self.assertEqual(extract_datetime("gaurko gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu'), [datetime(1998, 1, 1, 21, 0, 0, tzinfo=default_timezone()), ''])
        self.assertEqual(extract_datetime("gau honetan", anchorDate=datetime(1998, 1, 1),
                                          lang='eu'),
                         [datetime(1998, 1, 1, 21, 0, 0, tzinfo=default_timezone()), 'honetan'])
        self.assertEqual(extract_datetime("atzoko gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 31, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("herenegungo gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 30, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("duela 3 eguneko gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 29, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("biharko goiza", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1998, 1, 2, 8, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("atzoko arratsaldea", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 31, 15, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("duela 2 egun", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 30, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("gaurko goizeko 2", lang='eu', anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 2, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("gaurko arratsaldeko 2", lang='eu', anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 14, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("datorren urtea", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1999, 1, 1, tzinfo=default_timezone()))

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""
        self.assertEqual(extract_datetime('ez dago denborarik', lang='eu-eu'), None)

    @unittest.skip("These phrases are not parsing correctly.")
    def test_extract_datetime_relative_failing(self):
        self.assertEqual(extract_datetime("bart", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 31, 21, tzinfo=default_timezone()))

    def test_part_of_day_applies_pm(self):
        anchor = datetime(1998, 1, 1)
        # arratsaldeko = "in the afternoon" -> the hour is PM
        self.assertEqual(extract_datetime_eu("arratsaldeko 3etan", anchorDate=anchor)[0],
                         datetime(1998, 1, 1, 15, 0))
        self.assertEqual(extract_datetime_eu("arratsaldea 5:00", anchorDate=anchor)[0],
                         datetime(1998, 1, 1, 17, 0))
        # goizeko = "in the morning" -> the hour stays AM
        self.assertEqual(extract_datetime_eu("goizeko 8etan", anchorDate=anchor)[0],
                         datetime(1998, 1, 1, 8, 0))
        self.assertEqual(extract_datetime_eu("goiza 11:00", anchorDate=anchor)[0],
                         datetime(1998, 1, 1, 11, 0))

    def test_night_clock_does_not_wrap_to_am(self):
        anchor = datetime(1998, 1, 1)
        # "23:00 at night" must stay 23:00, not fold to 11:00
        self.assertEqual(extract_datetime_eu("23:00 gauean", anchorDate=anchor)[0],
                         datetime(1998, 1, 1, 23, 0))
        # an early hour "at night" reads as AM
        self.assertEqual(extract_datetime_eu("3:00 gauean", anchorDate=anchor)[0],
                         datetime(1998, 1, 1, 3, 0))

    def test_inflected_bare_hour_does_not_crash(self):
        anchor = datetime(1998, 1, 1)
        # "3etan" = "at 3 o'clock" (locative), a case-inflected number
        self.assertEqual(extract_datetime_eu("3etan", anchorDate=anchor)[0],
                         datetime(1998, 1, 1, 3, 0))

    def test_trailing_clock_not_taken_as_year(self):
        anchor = datetime(2020, 1, 1)
        # the clock time after the date must not be swallowed as a year
        self.assertEqual(extract_datetime_eu("abendua 25 15:00", anchorDate=anchor)[0],
                         datetime(2020, 12, 25, 15, 0))
        # explicit four digit year still works
        self.assertEqual(extract_datetime_eu("maiatza 13 1998",
                                             anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 5, 13, 0, 0))

    def test_leap_day(self):
        # Feb 29 resolves in a leap year
        self.assertEqual(extract_datetime_eu("otsaila 29", anchorDate=datetime(2020, 1, 1))[0],
                         datetime(2020, 2, 29, 0, 0))
        self.assertEqual(extract_datetime_eu("otsaila 29 2020",
                                             anchorDate=datetime(2020, 1, 1))[0],
                         datetime(2020, 2, 29, 0, 0))
        # Feb 29 is impossible in a non-leap year -> no date, not a crash
        self.assertEqual(extract_datetime_eu("otsaila 29", anchorDate=datetime(2021, 1, 1)),
                         None)

    def test_out_of_range_day_is_no_date(self):
        # day 32 does not exist -> no date, not a crash
        self.assertEqual(extract_datetime_eu("maiatza 32", anchorDate=datetime(2020, 1, 1)),
                         None)

    def test_remainder_text_is_returned(self):
        anchor = datetime(1998, 1, 1)
        res = extract_datetime_eu("bihar 15:00 mesedez", anchorDate=anchor)
        self.assertEqual(res[0], datetime(1998, 1, 2, 15, 0))
        self.assertEqual(res[1], "mesedez")

    def test_mixed_case_and_lang_variants(self):
        anchor = datetime(1998, 1, 1)
        self.assertEqual(extract_datetime_eu("BIHAR 15:00", anchorDate=anchor)[0],
                         datetime(1998, 1, 2, 15, 0))
        # eu and eu-es route to the same extractor
        self.assertEqual(extract_datetime("bihar 15:00", lang="eu-es", anchorDate=anchor)[0],
                         datetime(1998, 1, 2, 15, 0, tzinfo=default_timezone()))

    def test_empty_input_is_none(self):
        self.assertEqual(extract_datetime_eu(""), None)


if __name__ == "__main__":
    unittest.main()
