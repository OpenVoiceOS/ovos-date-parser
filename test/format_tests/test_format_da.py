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
import datetime
import unittest

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    nice_time, nice_date, nice_year
)

class TestNiceDateFormat_da(unittest.TestCase):
    def test_nice_time_da_comprehensive(self):
        # issue #7: morning (AM) period, 24-hour format, midnight/noon
        # edge cases, and common minute intervals (00/15/30/45)

        # midnight / noon are special-cased words in speech mode
        midnight = datetime.datetime(2017, 1, 31, 0, 0, 0)
        noon = datetime.datetime(2017, 1, 31, 12, 0, 0)
        self.assertEqual(nice_time(midnight, lang="da"), "midnat")
        self.assertEqual(nice_time(midnight, lang="da", use_ampm=True),
                         "midnat")
        self.assertEqual(nice_time(noon, lang="da"), "middag")
        self.assertEqual(nice_time(noon, lang="da", use_ampm=True),
                         "middag")
        # the midnat/middag special case only applies to 12-hour speech;
        # 24-hour mode and display mode just show the raw hour/clock
        self.assertEqual(nice_time(midnight, lang="da", use_24hour=True),
                         "nul")
        self.assertEqual(nice_time(noon, lang="da", use_24hour=True),
                         "tolv")
        self.assertEqual(nice_time(midnight, lang="da", speech=False),
                         "12:00")
        self.assertEqual(nice_time(midnight, lang="da", speech=False,
                                   use_24hour=True), "00:00")
        self.assertEqual(nice_time(noon, lang="da", speech=False,
                                   use_24hour=True), "12:00")

        # morning (AM) period, quarter-hour intervals, use_ampm=True
        for minute, spoken_minute in ((0, ""), (15, "femten"),
                                      (30, "tredive"),
                                      (45, "femogfyrre")):
            dt = datetime.datetime(2017, 1, 31, 8, minute, 0)
            expected = "otte" + (f" {spoken_minute}" if spoken_minute else "")
            expected += " om morgenen"
            self.assertEqual(nice_time(dt, lang="da", use_ampm=True),
                             expected)

        # 24-hour format, quarter-hour intervals, both morning and evening
        for hour, hour_word in ((8, "otte"), (20, "tyve")):
            for minute, spoken_minute in ((0, ""), (15, "femten"),
                                          (30, "tredive"),
                                          (45, "femogfyrre")):
                dt = datetime.datetime(2017, 1, 31, hour, minute, 0)
                expected = hour_word + (
                    f" {spoken_minute}" if spoken_minute else "")
                self.assertEqual(
                    nice_time(dt, lang="da", use_24hour=True), expected)

        # night period (00:xx-02:59 and 22:00-23:59) for completeness
        self.assertEqual(
            nice_time(datetime.datetime(2017, 1, 31, 2, 30), lang="da",
                      use_ampm=True),
            "to tredive om natten")
        self.assertEqual(
            nice_time(datetime.datetime(2017, 1, 31, 23, 45), lang="da",
                      use_ampm=True),
            # Danish 11 is "elleve"; "elve" is not a standard spelling and
            # was corrected in the number parser
            "elleve femogfyrre om natten")
    def test_nice_date_ordinal_days_da(self):
        # issue #4/#9 follow-up (flagged by review on #257): the
        # day-of-month ordinal table is separate from the year/hundreds
        # table fixed there, and had its own spelling bugs
        self.assertEqual(
            nice_date(datetime.datetime(2017, 1, 3), "da"),
            "tirsdag, den tredje januar, to tusind og sytten")
        self.assertEqual(
            nice_date(datetime.datetime(2017, 1, 9), "da"),
            "mandag, den niende januar, to tusind og sytten")
        self.assertEqual(
            nice_date(datetime.datetime(2017, 1, 11), "da"),
            "onsdag, den ellevte januar, to tusind og sytten")

    def test_nice_year_da(self):
        # ported from the previously-unused res/da/date_time_test.json
        # fixtures (issue #7: missing Danish nice_year test coverage)
        self.assertEqual(nice_year(datetime.datetime(2017, 1, 31), "da"),
                         "to tusind og sytten")
        self.assertEqual(nice_year(datetime.datetime(1984, 1, 31), "da"),
                         "nitten hundrede og fire og firs")
        self.assertEqual(nice_year(datetime.datetime(1906, 1, 31), "da"),
                         "nitten hundrede og seks")
        self.assertEqual(nice_year(datetime.datetime(1802, 1, 31), "da"),
                         "atten hundrede og to")
        self.assertEqual(nice_year(datetime.datetime(806, 1, 31), "da"),
                         "otte hundrede og seks")
        self.assertEqual(nice_year(datetime.datetime(1800, 1, 31), "da"),
                         "atten hundrede")
        self.assertEqual(nice_year(datetime.datetime(103, 1, 31), "da"),
                         "et hundrede og tre")
        self.assertEqual(nice_year(datetime.datetime(1000, 1, 31), "da"),
                         "et tusind")
        self.assertEqual(nice_year(datetime.datetime(2000, 1, 31), "da"),
                         "to tusind")
        self.assertEqual(
            nice_year(datetime.datetime(99, 1, 31), "da", bc=True),
            "ni og halvfems f.kr.")
        self.assertEqual(
            nice_year(datetime.datetime(5, 1, 31), "da", bc=True),
            "fem f.kr.")
        self.assertEqual(
            nice_year(datetime.datetime(3120, 1, 31), "da", bc=True),
            "tre tusind et hundrede og tyve f.kr.")

    def test_nice_year_da_ad(self):
        # issue #11: explicit AD/CE year notation for Danish
        self.assertEqual(
            nice_year(datetime.datetime(103, 1, 31), "da", ad=True),
            "et hundrede og tre e.kr.")
        self.assertEqual(
            nice_year(datetime.datetime(806, 1, 31), "da", ad=True),
            "otte hundrede og seks e.kr.")
        # bc takes precedence if both are somehow passed together
        self.assertEqual(
            nice_year(datetime.datetime(103, 1, 31), "da", bc=True, ad=True),
            "et hundrede og tre f.kr.")
        # no explicit marker by default (implicit AD, as before)
        self.assertEqual(
            nice_year(datetime.datetime(1984, 1, 31), "da"),
            "nitten hundrede og fire og firs")
        # ad has no effect on locales without an "ad" resource key
        self.assertEqual(
            nice_year(datetime.datetime(103, 1, 31), "en", ad=True),
            "one hundred three")

    def test_convert_times_da(self):
        dt = datetime.datetime(2017, 1, 31, 13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, lang="da-dk"),
                         "et toogtyve")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "et toogtyve om eftermiddagen")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "01:22")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "01:22 PM")
        self.assertEqual(nice_time(dt, lang="da-dk",
                                   speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "tretten toogtyve")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "tretten toogtyve")

        dt = datetime.datetime(2017, 1, 31, 13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "et")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "et om eftermiddagen")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "01:00")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "01:00 PM")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "tretten")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "tretten")

        dt = datetime.datetime(2017, 1, 31, 13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "et nul to")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "et nul to om eftermiddagen")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "01:02")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "01:02 PM")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "tretten nul to")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "tretten nul to")

        dt = datetime.datetime(2017, 1, 31, 0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "tolv nul to")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "tolv nul to om natten")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "nul nul to")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "nul nul to")

        dt = datetime.datetime(2017, 1, 31, 12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "tolv femten")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "tolv femten om eftermiddagen")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "tolv femten")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "tolv femten")

        dt = datetime.datetime(2017, 1, 31, 19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "syv fyrre")
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "syv fyrre om aftenen")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False),
                         "07:40")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_ampm=True),
                         "07:40 PM")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="da-dk", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=True),
                         "nitten fyrre")
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True,
                                   use_ampm=False),
                         "nitten fyrre")

        dt = datetime.datetime(2017, 1, 31, 1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk", use_24hour=True),
                         "et femten")

        dt = datetime.datetime(2017, 1, 31, 1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"),
                         "et femogtredive")

        dt = datetime.datetime(2017, 1, 31, 1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "et femogfyrre")

        dt = datetime.datetime(2017, 1, 31, 4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "fire halvtreds")

        dt = datetime.datetime(2017, 1, 31, 5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk"), "fem femoghalvtreds")

        dt = datetime.datetime(2017, 1, 31, 5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="da-dk", use_ampm=True),
                         "fem tredive om morgenen")


if __name__ == "__main__":
    unittest.main()
