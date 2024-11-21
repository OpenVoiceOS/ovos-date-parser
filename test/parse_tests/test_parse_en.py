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
from datetime import datetime, timedelta, time

from dateutil import tz
from dateutil.relativedelta import relativedelta
from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    extract_duration, extract_datetime
)


class TestExtractDuration(unittest.TestCase):
    def test_extract_duration_en(self):
        self.assertEqual(extract_duration("10 seconds"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minutes"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 hours"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 days"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 weeks"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("seven hours"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 seconds"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("eight and a half days thirty"
                                          " nine seconds"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("wake me up in three weeks, four"
                                          " hundred ninety seven days, and"
                                          " three hundred 91.6 seconds"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "wake me up in  ,  , and"))
        self.assertEqual(extract_duration("10-seconds"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-minutes"),
                         (timedelta(minutes=5), ""))

    def test_extract_duration_case_en(self):
        self.assertEqual(extract_duration("Set a timer for 30 minutes"),
                         (timedelta(minutes=30), "Set a timer for"))
        self.assertEqual(extract_duration("The movie is one hour, fifty seven"
                                          " and a half minutes long"),
                         (timedelta(hours=1, minutes=57.5),
                          "The movie is  ,  long"))
        self.assertEqual(extract_duration("Four and a Half minutes until"
                                          " sunset"),
                         (timedelta(minutes=4.5), "until sunset"))
        self.assertEqual(extract_duration("Nineteen minutes past THE hour"),
                         (timedelta(minutes=19), "past THE hour"))

    def test_non_std_units(self):
        self.assertEqual(extract_duration("1 month"),
                         (timedelta(days=DAYS_IN_1_MONTH), ""))
        self.assertEqual(
            extract_duration("1 month"),
            (timedelta(days=DAYS_IN_1_MONTH), ""))

        self.assertEqual(extract_duration("3 months"),
                         (timedelta(days=DAYS_IN_1_MONTH * 3), ""))
        self.assertEqual(extract_duration("a year"),
                         (timedelta(days=DAYS_IN_1_YEAR), ""))
        self.assertEqual(extract_duration("1 year"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1), ""))
        self.assertEqual(extract_duration("5 years"),
                         (timedelta(days=DAYS_IN_1_YEAR * 5), ""))
        self.assertEqual(extract_duration("a decade"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_duration("1 decade"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_duration("5 decades"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10 * 5), ""))
        self.assertEqual(extract_duration("1 century"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_duration("a century"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_duration("5 centuries"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100 * 5), ""))
        self.assertEqual(extract_duration("1 millennium"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000), ""))
        self.assertEqual(extract_duration("5 millenniums"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000 * 5), ""))


class TestExtractDateTime(unittest.TestCase):
    def test_extractdatetime_fractions_en(self):
        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("Set the ambush for half an hour",
                    "2017-06-27 13:34:00", "set ambush")
        testExtract("remind me to call mom in half an hour",
                    "2017-06-27 13:34:00", "remind me to call mom")
        testExtract("remind me to call mom in a half hour",
                    "2017-06-27 13:34:00", "remind me to call mom")
        testExtract("remind me to call mom in a quarter hour",
                    "2017-06-27 13:19:00", "remind me to call mom")
        testExtract("remind me to call mom in a quarter of an hour",
                    "2017-06-27 13:19:00", "remind me to call mom")

    def test_extractdatetime_year_multiples_en(self):
        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("in a decade",
                    "2027-06-27 00:00:00", "")
        testExtract("in a couple of decades",
                    "2037-06-27 00:00:00", "")
        testExtract("next decade",
                    "2027-06-27 00:00:00", "")
        testExtract("in a century",
                    "2117-06-27 00:00:00", "")
        testExtract("in a millennium",
                    "3017-06-27 00:00:00", "")
        testExtract("in a couple decades",
                    "2037-06-27 00:00:00", "")
        testExtract("in 5 decades",
                    "2067-06-27 00:00:00", "")
        testExtract("in a couple centuries",
                    "2217-06-27 00:00:00", "")
        testExtract("in a couple of centuries",
                    "2217-06-27 00:00:00", "")
        testExtract("in 2 centuries",
                    "2217-06-27 00:00:00", "")
        testExtract("in a couple millenniums",
                    "4017-06-27 00:00:00", "")
        testExtract("in a couple of millenniums",
                    "4017-06-27 00:00:00", "")

        # in {float} year multiple
        for i in range(1, 500):
            testExtract(f"in {i} decades",
                        f"{2017 + 10 * i}-06-27 00:00:00", "")
            for j in range(1, 9):  # TODO fix higher numbers
                testExtract(f"in {i}.{j} decades",
                            f"{2017 + j + 10 * i}-06-27 00:00:00", "")
        for i in range(1, 50):
            testExtract(f"in {i} centuries",
                        f"{2017 + 100 * i}-06-27 00:00:00", "")
            for j in range(1, 9):  # TODO fix higher numbers
                testExtract(f"in {i}.{j} centuries",
                            f"{2017 + j * 10 + 100 * i}-06-27 00:00:00", "")
        for i in range(1, 8):
            testExtract(f"in {i} millenniums",
                        f"{2017 + 1000 * i}-06-27 00:00:00", "")
            for j in range(1, 9):  # TODO fix higher numbers
                testExtract(f"in {i}.{j} millenniums",
                            f"{2017 + j * 100 + 1000 * i}-06-27 00:00:00", "")

    def test_extractdatetime_en(self):
        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("now is the time",
                    "2017-06-27 13:04:00", "is time")
        testExtract("in a second",
                    "2017-06-27 13:04:01", "")
        testExtract("in a minute",
                    "2017-06-27 13:05:00", "")
        testExtract("in a couple minutes",
                    "2017-06-27 13:06:00", "")
        testExtract("in a couple of minutes",
                    "2017-06-27 13:06:00", "")
        testExtract("in a couple hours",
                    "2017-06-27 15:04:00", "")
        testExtract("in a couple of hours",
                    "2017-06-27 15:04:00", "")
        testExtract("in a couple weeks",
                    "2017-07-11 00:00:00", "")
        testExtract("in a couple of weeks",
                    "2017-07-11 00:00:00", "")
        testExtract("in a couple months",
                    "2017-08-27 00:00:00", "")
        testExtract("in a couple years",
                    "2019-06-27 00:00:00", "")
        testExtract("in a couple of months",
                    "2017-08-27 00:00:00", "")
        testExtract("in a couple of years",
                    "2019-06-27 00:00:00", "")
        testExtract("in an hour",
                    "2017-06-27 14:04:00", "")
        testExtract("i want it within the hour",
                    "2017-06-27 14:04:00", "i want it")
        testExtract("in 1 second",
                    "2017-06-27 13:04:01", "")
        testExtract("in 2 seconds",
                    "2017-06-27 13:04:02", "")
        testExtract("Set the ambush in 1 minute",
                    "2017-06-27 13:05:00", "set ambush")
        testExtract("Set the ambush for 5 days from today",
                    "2017-07-02 00:00:00", "set ambush")
        testExtract("day after tomorrow",
                    "2017-06-29 00:00:00", "")
        testExtract("What is the day after tomorrow's weather?",
                    "2017-06-29 00:00:00", "what is weather")
        testExtract("Remind me at 10:45 pm",
                    "2017-06-27 22:45:00", "remind me")
        testExtract("what is the weather on friday morning",
                    "2017-06-30 08:00:00", "what is weather")
        testExtract("what is tomorrow's weather",
                    "2017-06-28 00:00:00", "what is weather")
        testExtract("what is this afternoon's weather",
                    "2017-06-27 15:00:00", "what is weather")
        testExtract("what is this evening's weather",
                    "2017-06-27 19:00:00", "what is weather")
        testExtract("what was this morning's weather",
                    "2017-06-27 08:00:00", "what was weather")
        testExtract("remind me to call mom in 8 weeks and 2 days",
                    "2017-08-24 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom on august 3rd",
                    "2017-08-03 00:00:00", "remind me to call mom")
        testExtract("remind me tomorrow to call mom at 7am",
                    "2017-06-28 07:00:00", "remind me to call mom")
        testExtract("remind me tomorrow to call mom at 10pm",
                    "2017-06-28 22:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7am",
                    "2017-06-28 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom in an hour",
                    "2017-06-27 14:04:00", "remind me to call mom")
        testExtract("remind me to call mom at 1730",
                    "2017-06-27 17:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 0630",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 06 30 hours",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 06 30",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 06 30 hours",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 7 o'clock",
                    "2017-06-27 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom this evening at 7 o'clock",
                    "2017-06-27 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom  at 7 o'clock tonight",
                    "2017-06-27 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7 o'clock in the morning",
                    "2017-06-28 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom Thursday evening at 7 o'clock",
                    "2017-06-29 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom Thursday morning at 7 o'clock",
                    "2017-06-29 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7 o'clock Thursday morning",
                    "2017-06-29 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7:00 Thursday morning",
                    "2017-06-29 07:00:00", "remind me to call mom")
        # TODO: This test is imperfect due to the "at 7:00" still in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("remind me to call mom at 7:00 Thursday evening",
                    "2017-06-29 19:00:00", "remind me to call mom at 7:00")
        testExtract("remind me to call mom at 8 Wednesday evening",
                    "2017-06-28 20:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 8 Wednesday in the evening",
                    "2017-06-28 20:00:00", "remind me to call mom")
        testExtract("remind me to call mom Wednesday evening at 8",
                    "2017-06-28 20:00:00", "remind me to call mom")
        testExtract("remind me to call mom in two hours",
                    "2017-06-27 15:04:00", "remind me to call mom")
        testExtract("remind me to call mom in 2 hours",
                    "2017-06-27 15:04:00", "remind me to call mom")
        testExtract("remind me to call mom in 15 minutes",
                    "2017-06-27 13:19:00", "remind me to call mom")
        testExtract("remind me to call mom in fifteen minutes",
                    "2017-06-27 13:19:00", "remind me to call mom")
        testExtract("remind me to call mom at 10am 2 days after this saturday",
                    "2017-07-03 10:00:00", "remind me to call mom")
        testExtract("Play Rick Astley music 2 days from Friday",
                    "2017-07-02 00:00:00", "play rick astley music")
        testExtract("Begin the invasion at 3:45 pm on Thursday",
                    "2017-06-29 15:45:00", "begin invasion")
        testExtract("On Monday, order pie from the bakery",
                    "2017-07-03 00:00:00", "order pie from bakery")
        testExtract("Play Happy Birthday music 5 years from today",
                    "2022-06-27 00:00:00", "play happy birthday music")
        testExtract("Skype Mom at 12:45 pm next Thursday",
                    "2017-07-06 12:45:00", "skype mom")
        testExtract("What's the weather next Friday?",
                    "2017-06-30 00:00:00", "what weather")
        testExtract("What's the weather next Wednesday?",
                    "2017-07-05 00:00:00", "what weather")
        testExtract("What's the weather next Thursday?",
                    "2017-07-06 00:00:00", "what weather")
        testExtract("what is the weather next friday morning",
                    "2017-06-30 08:00:00", "what is weather")
        testExtract("what is the weather next friday evening",
                    "2017-06-30 19:00:00", "what is weather")
        testExtract("what is the weather next friday afternoon",
                    "2017-06-30 15:00:00", "what is weather")
        testExtract("remind me to call mom on august 3rd",
                    "2017-08-03 00:00:00", "remind me to call mom")
        testExtract("Buy fireworks on the 4th of July",
                    "2017-07-04 00:00:00", "buy fireworks")
        testExtract("what is the weather 2 weeks from next friday",
                    "2017-07-14 00:00:00", "what is weather")
        testExtract("what is the weather wednesday at 0700 hours",
                    "2017-06-28 07:00:00", "what is weather")
        testExtract("set an alarm wednesday at 7 o'clock",
                    "2017-06-28 07:00:00", "set alarm")
        testExtract("Set up an appointment at 12:45 pm next Thursday",
                    "2017-07-06 12:45:00", "set up appointment")
        testExtract("What's the weather this Thursday?",
                    "2017-06-29 00:00:00", "what weather")
        testExtract("set up the visit for 2 weeks and 6 days from Saturday",
                    "2017-07-21 00:00:00", "set up visit")
        testExtract("Begin the invasion at 03 45 on Thursday",
                    "2017-06-29 03:45:00", "begin invasion")
        testExtract("Begin the invasion at o 800 hours on Thursday",
                    "2017-06-29 08:00:00", "begin invasion")
        testExtract("Begin the party at 8 o'clock in the evening on Thursday",
                    "2017-06-29 20:00:00", "begin party")
        testExtract("Begin the invasion at 8 in the evening on Thursday",
                    "2017-06-29 20:00:00", "begin invasion")
        testExtract("Begin the invasion on Thursday at noon",
                    "2017-06-29 12:00:00", "begin invasion")
        testExtract("Begin the invasion on Thursday at midnight",
                    "2017-06-29 00:00:00", "begin invasion")
        testExtract("Begin the invasion on Thursday at 0500",
                    "2017-06-29 05:00:00", "begin invasion")
        testExtract("remind me to wake up in 4 years",
                    "2021-06-27 00:00:00", "remind me to wake up")
        testExtract("remind me to wake up in 4 years and 4 days",
                    "2021-07-01 00:00:00", "remind me to wake up")
        testExtract("What is the weather 3 days after tomorrow?",
                    "2017-07-01 00:00:00", "what is weather")
        testExtract("december 3",
                    "2017-12-03 00:00:00", "")
        testExtract("lets meet at 8:00 tonight",
                    "2017-06-27 20:00:00", "lets meet")
        testExtract("lets meet at 5pm",
                    "2017-06-27 17:00:00", "lets meet")
        testExtract("lets meet at 8 a.m.",
                    "2017-06-28 08:00:00", "lets meet")
        testExtract("what is the weather on tuesday",
                    "2017-06-27 00:00:00", "what is weather")
        testExtract("what is the weather on monday",
                    "2017-07-03 00:00:00", "what is weather")
        testExtract("what is the weather this wednesday",
                    "2017-06-28 00:00:00", "what is weather")
        testExtract("on thursday what is the weather",
                    "2017-06-29 00:00:00", "what is weather")
        testExtract("on this thursday what is the weather",
                    "2017-06-29 00:00:00", "what is weather")
        testExtract("on last monday what was the weather",
                    "2017-06-26 00:00:00", "what was weather")
        testExtract("set an alarm for wednesday evening at 8",
                    "2017-06-28 20:00:00", "set alarm")
        testExtract("set an alarm for wednesday at 3 o'clock in the afternoon",
                    "2017-06-28 15:00:00", "set alarm")
        testExtract("set an alarm for wednesday at 3 o'clock in the morning",
                    "2017-06-28 03:00:00", "set alarm")
        testExtract("set an alarm for wednesday morning at 7 o'clock",
                    "2017-06-28 07:00:00", "set alarm")
        testExtract("set an alarm for today at 7 o'clock",
                    "2017-06-27 19:00:00", "set alarm")
        testExtract("set an alarm for this evening at 7 o'clock",
                    "2017-06-27 19:00:00", "set alarm")
        # TODO: This test is imperfect due to the "at 7:00" still in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("set an alarm for this evening at 7:00",
                    "2017-06-27 19:00:00", "set alarm at 7:00")
        testExtract("on the evening of june 5th 2017 remind me to" +
                    " call my mother",
                    "2017-06-05 19:00:00", "remind me to call my mother")
        # TODO: This test is imperfect due to the missing "for" in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("update my calendar for a morning meeting with julius" +
                    " on march 4th",
                    "2018-03-04 08:00:00",
                    "update my calendar meeting with julius")
        testExtract("remind me to call mom next tuesday",
                    "2017-07-04 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 3 weeks",
                    "2017-07-18 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 8 weeks",
                    "2017-08-22 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 8 weeks and 2 days",
                    "2017-08-24 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 4 days",
                    "2017-07-01 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 3 months",
                    "2017-09-27 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 2 years and 2 days",
                    "2019-06-29 00:00:00", "remind me to call mom")

        testExtract("remind me to call mom at 10am on saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 10am this saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 10 next saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 10am next saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        # test yesterday
        testExtract("what day was yesterday",
                    "2017-06-26 00:00:00", "what day was")
        testExtract("what day was the day before yesterday",
                    "2017-06-25 00:00:00", "what day was")
        testExtract("i had dinner yesterday at 6",
                    "2017-06-26 06:00:00", "i had dinner")
        testExtract("i had dinner yesterday at 6 am",
                    "2017-06-26 06:00:00", "i had dinner")
        testExtract("i had dinner yesterday at 6 pm",
                    "2017-06-26 18:00:00", "i had dinner")

        # Below two tests, ensure that time is picked
        # even if no am/pm is specified
        # in case of weekdays/tonight
        testExtract("set alarm for 9 on weekdays",
                    "2017-06-27 21:00:00", "set alarm weekdays")
        testExtract("for 8 tonight",
                    "2017-06-27 20:00:00", "")
        testExtract("for 8:30pm tonight",
                    "2017-06-27 20:30:00", "")
        # Tests a time with ':' & without am/pm
        testExtract("set an alarm for tonight 9:30",
                    "2017-06-27 21:30:00", "set alarm")
        testExtract("set an alarm at 9:00 for tonight",
                    "2017-06-27 21:00:00", "set alarm")
        # Check if it picks the intent irrespective of correctness
        testExtract("set an alarm at 9 o'clock for tonight",
                    "2017-06-27 21:00:00", "set alarm")
        testExtract("remind me about the game tonight at 11:30",
                    "2017-06-27 23:30:00", "remind me about game")
        testExtract("set alarm at 7:30 on weekdays",
                    "2017-06-27 19:30:00", "set alarm on weekdays")

        #  "# days <from X/after X>"
        testExtract("my birthday is 2 days from today",
                    "2017-06-29 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days after today",
                    "2017-06-29 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days from tomorrow",
                    "2017-06-30 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days after tomorrow",
                    "2017-06-30 00:00:00", "my birthday is")
        testExtract("remind me to call mom at 10am 2 days after next saturday",
                    "2017-07-10 10:00:00", "remind me to call mom")
        testExtract("my birthday is 2 days from yesterday",
                    "2017-06-28 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days after yesterday",
                    "2017-06-28 00:00:00", "my birthday is")

        #  "# days ago>"
        testExtract("my birthday was 1 day ago",
                    "2017-06-26 00:00:00", "my birthday was")
        testExtract("my birthday was 2 days ago",
                    "2017-06-25 00:00:00", "my birthday was")
        testExtract("my birthday was 3 days ago",
                    "2017-06-24 00:00:00", "my birthday was")
        testExtract("my birthday was 4 days ago",
                    "2017-06-23 00:00:00", "my birthday was")
        # TODO this test is imperfect due to "tonight" in the reminder, but let is pass since the date is correct
        testExtract("lets meet tonight",
                    "2017-06-27 22:00:00", "lets meet tonight")
        # TODO this test is imperfect due to "at night" in the reminder, but let is pass since the date is correct
        testExtract("lets meet later at night",
                    "2017-06-27 22:00:00", "lets meet later at night")
        # TODO this test is imperfect due to "night" in the reminder, but let is pass since the date is correct
        testExtract("what's the weather like tomorrow night",
                    "2017-06-28 22:00:00", "what is weather like night")
        # TODO this test is imperfect due to "night" in the reminder, but let is pass since the date is correct
        testExtract("what's the weather like next tuesday night",
                    "2017-07-04 22:00:00", "what is weather like night")

    def test_extractdatetime_with_default_time_en(self):
        def extractWithFormat(text):
            default_time = time(15, 4, tzinfo=default_timezone())
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())  # Tue June 27, 2017 @ 1:04pm
            [extractedDate, leftover] = extract_datetime(text, date, default_time=default_time)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        # ignore default time arg
        testExtract("in a second",
                    "2017-06-27 13:04:01", "")
        testExtract("in a minute",
                    "2017-06-27 13:05:00", "")
        testExtract("in an hour",
                    "2017-06-27 14:04:00", "")

        # use default time
        testExtract("in a couple weeks",
                    "2017-07-11 15:04:00", "")
        testExtract("in a couple of weeks",
                    "2017-07-11 15:04:00", "")
        testExtract("in a couple months",
                    "2017-08-27 15:04:00", "")
        testExtract("in a couple years",
                    "2019-06-27 15:04:00", "")
        testExtract("in a couple of months",
                    "2017-08-27 15:04:00", "")
        testExtract("in a couple of years",
                    "2019-06-27 15:04:00", "")
        testExtract("in a decade",
                    "2027-06-27 15:04:00", "")
        testExtract("in a couple of decades",
                    "2037-06-27 15:04:00", "")
        testExtract("next decade",
                    "2027-06-27 15:04:00", "")
        testExtract("in a century",
                    "2117-06-27 15:04:00", "")
        testExtract("in a millennium",
                    "3017-06-27 15:04:00", "")
        testExtract("in a couple decades",
                    "2037-06-27 15:04:00", "")
        testExtract("in 5 decades",
                    "2067-06-27 15:04:00", "")
        testExtract("in a couple centuries",
                    "2217-06-27 15:04:00", "")
        testExtract("in a couple of centuries",
                    "2217-06-27 15:04:00", "")
        testExtract("in 2 centuries",
                    "2217-06-27 15:04:00", "")
        testExtract("in a couple millenniums",
                    "4017-06-27 15:04:00", "")
        testExtract("in a couple of millenniums",
                    "4017-06-27 15:04:00", "")

    def test_extract_date_years(self):
        date = datetime(2017, 6, 27, tzinfo=default_timezone())  # Tue June 27, 2017
        self.assertEqual(extract_datetime('in 2007', date)[0],
                         datetime(2007, 6, 27, tzinfo=date.tzinfo))

    def test_extract_ambiguous_month_en(self):
        dec = datetime(2017, 12, 27, 8, 1, 2)
        jun = datetime(2017, 6, 27, 20, 1, 2)
        self.assertEqual(
            extract_datetime('when is september', jun)[0],
            datetime(2017, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('when was september', dec)[0],
            datetime(2017, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('when was september', jun)[0],
            datetime(2016, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('when is september', dec)[0],
            datetime(2018, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i did the thing last september', jun)[0],
            datetime(2016, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('past september the thing was done', dec)[0],
            datetime(2017, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i will do the thing in september', jun)[0],
            datetime(2017, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('next september the thing will be done', dec)[0],
            datetime(2018, 9, 1, tzinfo=default_timezone()))

    def test_extract_ambiguous_time_en(self):
        morning = datetime(2017, 6, 27, 8, 1, 2, tzinfo=default_timezone())
        evening = datetime(2017, 6, 27, 20, 1, 2, tzinfo=default_timezone())
        noonish = datetime(2017, 6, 27, 12, 1, 2, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('feed the fish'), None)
        self.assertEqual(
            extract_datetime('day'), None)
        self.assertEqual(
            extract_datetime('week'), None)
        self.assertEqual(
            extract_datetime('month'), None)
        self.assertEqual(
            extract_datetime('year'), None)
        self.assertEqual(
            extract_datetime(' '), None)
        self.assertEqual(
            extract_datetime('feed fish at 10 o\'clock', morning)[0],
            datetime(2017, 6, 27, 10, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('feed fish at 10 o\'clock', noonish)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('feed fish at 10 o\'clock', evening)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))

    def test_extract_later_en(self):
        dt = datetime(2017, 1, 1, 13, 12, 30)
        self.assertEqual(
            extract_datetime('10 seconds later', dt)[0],
            datetime(2017, 1, 1, 13, 12, 40, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('15 minutes later', dt)[0],
            datetime(2017, 1, 1, 13, 27, 30, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('12 hours later', dt)[0],
            datetime(2017, 1, 2, 1, 12, 30, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('28 days later', dt)[0],
            datetime(2017, 1, 29, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('2 weeks later', dt)[0],
            datetime(2017, 1, 15, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('6 months later', dt)[0],
            datetime(2017, 7, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('10 years later', dt)[0],
            datetime(2027, 1, 1, tzinfo=default_timezone()))

    def test_extract_date_with_may_I_en(self):
        now = datetime(2019, 7, 4, 8, 1, 2, tzinfo=default_timezone())
        may_date = datetime(2019, 5, 2, 10, 11, 20, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('May I know what time it is tomorrow', now)[0],
            datetime(2019, 7, 5, 0, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('May I when 10 o\'clock is', now)[0],
            datetime(2019, 7, 4, 10, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('On 24th of may I want a reminder', may_date)[0],
            datetime(2019, 5, 24, 0, 0, 0, tzinfo=default_timezone()))

    def test_extract_weekend_en(self):
        dt = datetime(2017, 6, 1)  # thursday <- reference date
        self.assertEqual(
            extract_datetime('i have things to do next weekend', dt)[0],
            datetime(2017, 6, 3, tzinfo=default_timezone()))
        # TODO next saturday extraction seems to be wrong
        # datetime(2017, 6, 1) -> thursday
        # datetime(2017, 6, 3) -> saturday <- this should be extracted
        # datetime(2017, 6, 10) -> saturday  <- this is being extracted
        # self.assertEqual(
        #    extract_datetime('i have things to do next weekend', dt)[0],
        #    extract_datetime('i have things to do next saturday', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in a weekend', dt)[0],
            datetime(2017, 6, 5, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a weekend', dt)[0],
            extract_datetime('i have things to do next monday', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in 1 weekend', dt)[0],
            extract_datetime('i have things to do next monday', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in 1 weekend', dt)[0],
            datetime(2017, 6, 5, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in 2 weekends', dt)[0],
            datetime(2017, 6, 12, tzinfo=default_timezone()))

        self.assertEqual(
            extract_datetime('i had things to do last weekend', dt)[0],
            extract_datetime('i had things to do last saturday', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last weekend', dt)[0],
            datetime(2017, 5, 27, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do past weekend', dt)[0],
            datetime(2017, 5, 27, tzinfo=default_timezone()))

        self.assertEqual(
            extract_datetime('i had things to do a weekend ago', dt)[0],
            extract_datetime('i had things to do last friday', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do a weekend ago', dt)[0],
            datetime(2017, 5, 26, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do 2 weekends ago', dt)[0],
            datetime(2017, 5, 19, tzinfo=default_timezone()))

    def test_extract_next_en(self):
        dt = datetime(2017, 6, 1, 0, 0, 0)
        # next {timedelta unit}
        self.assertEqual(
            extract_datetime('i have things to do next second', dt)[0],
            datetime(2017, 6, 1, 0, 0, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do next minute', dt)[0],
            datetime(2017, 6, 1, 0, 1, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do next hour', dt)[0],
            datetime(2017, 6, 1, 1, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do next day', dt)[0],
            datetime(2017, 6, 2, tzinfo=default_timezone()))

        # 1st day of {calendar unit}
        self.assertEqual(
            extract_datetime('i have things to do next week', dt)[0],
            extract_datetime('i have things to do next monday', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do next week', dt)[0],
            datetime(2017, 6, 5, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do next month', dt)[0],
            datetime(2017, 7, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do next year', dt)[0],
            datetime(2018, 1, 1, tzinfo=default_timezone()))

        # old test moved here due to new disambiguation between "next week" and "in a week"
        # testExtract("remind me to call mom next week",
        #            "2017-07-04 00:00:00", "remind me to call mom")

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("remind me to call mom in a week",  # + 7 days
                    "2017-07-04 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom next week",  # next monday
                    "2017-07-03 00:00:00", "remind me to call mom")

    def test_extract_in_en(self):
        dt = datetime(2017, 6, 1, 0, 0, 0)

        self.assertEqual(
            extract_datetime('i have things to do in a second', dt)[0],
            datetime(2017, 6, 1, 0, 0, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a minute', dt)[0],
            datetime(2017, 6, 1, 0, 1, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a minute', dt)[0],
            extract_datetime('i have things to do in 60 seconds', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in an hour', dt)[0],
            datetime(2017, 6, 1, 1, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a day', dt)[0],
            extract_datetime('i have things to do in 24 hours', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in a day', dt)[0],
            datetime(2017, 6, 2, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a week', dt)[0],
            datetime(2017, 6, 8, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a week', dt)[0],
            extract_datetime('i have things to do in 7 days', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in a month', dt)[0],
            datetime(2017, 7, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a year', dt)[0],
            datetime(2018, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a year', dt)[0],
            extract_datetime('i have things to do in 365 days', dt)[0])

        self.assertEqual(
            extract_datetime('i have things to do in 1 day', dt)[0],
            datetime(2017, 6, 2, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in 2 days', dt)[0],
            datetime(2017, 6, 3, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in 1 week', dt)[0],
            datetime(2017, 6, 8, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in 1 month', dt)[0],
            datetime(2017, 7, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in 1 year', dt)[0],
            datetime(2018, 6, 1, tzinfo=default_timezone()))

    def test_extract_within_a_en(self):
        dt = datetime(2017, 6, 1, 0, 0, 0, tzinfo=default_timezone())

        self.assertEqual(extract_datetime('i have things to do within a second', dt)[0],
                         dt + timedelta(seconds=1))
        self.assertEqual(extract_datetime('i have things to do within a minute', dt)[0],
                         dt + timedelta(minutes=1))
        self.assertEqual(extract_datetime('i have things to do within an hour', dt)[0],
                         dt + timedelta(hours=1))
        self.assertEqual(extract_datetime('i have things to do within a day', dt)[0],
                         dt + timedelta(days=1))
        self.assertEqual(extract_datetime('i have things to do within a week', dt)[0],
                         dt + timedelta(days=7))
        self.assertEqual(extract_datetime('i have things to do within a month', dt)[0],
                         dt + timedelta(days=30))
        self.assertEqual(extract_datetime('i have things to do within a year', dt)[0],
                         dt + timedelta(days=365))

    @unittest.skip("currently can not disambiguate a/the because of normalization")
    def test_extract_within_the_en(self):
        # TODO we can not disambiguate a/the because of normalization
        # this is not really a LF problem but a mycroft problem... will give it a think
        #  "within a month" -> month is a timedelta of 30 days
        #  "with the month" -> before 1st day of next month

        dt = datetime(2017, 6, 1, 12, 30, 30, tzinfo=default_timezone())  # thursday  - weekday 3

        self.assertEqual(extract_datetime('i have things to do within the second', dt)[0],
                         dt.replace(second=dt.second + 1))
        self.assertEqual(extract_datetime('i have things to do within the second', dt)[0],
                         extract_datetime('i have things to do before the next second', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the minute', dt)[0],
                         dt.replace(minute=dt.minute + 1, second=0))
        self.assertEqual(extract_datetime('i have things to do within the minute', dt)[0],
                         extract_datetime('i have things to do before the next minute', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the hour', dt)[0],
                         dt.replace(hour=dt.hour + 1, minute=0, second=0))
        self.assertEqual(extract_datetime('i have things to do within the hour', dt)[0],
                         extract_datetime('i have things to do before the next hour', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the day', dt)[0],
                         dt.replace(day=dt.day + 1, hour=0, minute=0, second=0))
        self.assertEqual(extract_datetime('i have things to do within the day', dt)[0],
                         extract_datetime('i have things to do before the next day', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the month', dt)[0],
                         dt.replace(day=1, month=dt.month + 1, hour=0, minute=0, second=0))
        self.assertEqual(extract_datetime('i have things to do within the month', dt)[0],
                         extract_datetime('i have things to do before the next month', dt)[0])

        self.assertEqual(extract_datetime('i have things to do within the week', dt)[0],
                         extract_datetime('i have things to do before next week', dt)[0])  # next monday
        self.assertEqual(extract_datetime('i have things to do within the week', dt)[0],
                         extract_datetime('i have things to do before next monday', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the week', dt)[0],
                         dt.replace(day=dt.day + 7 - dt.weekday(), hour=0, minute=0, second=0))
        self.assertEqual(extract_datetime('i have things to do within the year', dt)[0],
                         extract_datetime('i have things to do before next year', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the year', dt)[0],
                         dt.replace(day=1, month=1, year=dt.year + 1, hour=0, minute=0, second=0))

    def test_extract_last_int_timeunit_en(self):
        dt = datetime(2017, 6, 1)
        self.assertEqual(
            extract_datetime('i wrote a lot of unittests in the past second', dt)[0],
            datetime(2017, 5, 31, 23, 59, 59, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i wrote a lot of unittests in the past minute', dt)[0],
            datetime(2017, 5, 31, 23, 59, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i wrote a lot of unittests in the past hour', dt)[0],
            datetime(2017, 5, 31, 23, 0, 0, tzinfo=default_timezone()))

        for i in range(1, 1500):
            expected = to_local(dt - timedelta(seconds=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} seconds', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} seconds', dt)[0],
                expected)

        for i in range(1, 1500):
            expected = to_local(dt - timedelta(minutes=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} minutes', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} minutes', dt)[0],
                expected)

        # this is also testing conflicts with military time,
        # the parser ignores 100 <= N <= 2400 unless there is a past_marker word
        for i in range(1, 1500):
            expected = to_local(dt - timedelta(hours=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} hours', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} hours', dt)[0],
                expected)

    def test_extract_last_int_dateunit_en(self):
        dt = datetime(2017, 6, 1)

        for i in range(1, 1500):
            expected = to_local(dt - timedelta(days=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} days', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} days', dt)[0],
                expected)

        for i in range(1, 1500):
            expected = to_local(dt - timedelta(days=i * 7))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} weeks', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} weeks', dt)[0],
                expected)

        for i in range(1, 150):
            expected = to_local(dt - relativedelta(months=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} months', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} months', dt)[0],
                expected)

        for i in range(1, 150):
            expected = to_local(dt - relativedelta(years=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} years', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} years', dt)[0],
                expected)

        for i in range(1, 150):
            expected = to_local(dt - relativedelta(years=i * 10))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} decades', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} decades', dt)[0],
                expected)

        for i in range(1, 15):
            expected = to_local(dt - relativedelta(years=i * 100))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} centuries', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} centuries', dt)[0],
                expected)

        for i in range(1, 2):
            expected = to_local(dt - relativedelta(years=i * 1000))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} millenniums', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} millenniums', dt)[0],
                expected)

    def test_extract_last_X_en(self):
        dt = datetime(2017, 6, 1)
        self.assertEqual(
            extract_datetime('i had things to do last second', dt)[0],
            datetime(2017, 5, 31, 23, 59, 59, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past second', dt)[0],
            extract_datetime('i had things to do last second', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last minute', dt)[0],
            datetime(2017, 5, 31, 23, 59, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past minute', dt)[0],
            extract_datetime('i had things to do last minute', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last hour', dt)[0],
            datetime(2017, 5, 31, 23, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past hour', dt)[0],
            extract_datetime('i had things to do last hour', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last day', dt)[0],
            datetime(2017, 5, 31, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past day', dt)[0],
            extract_datetime('i had things to do last day', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last week', dt)[0],
            datetime(2017, 5, 25, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past week', dt)[0],
            extract_datetime('i had things to do last week', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last month', dt)[0],
            datetime(2017, 5, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past month', dt)[0],
            extract_datetime('i had things to do last month', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last year', dt)[0],
            datetime(2016, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past year', dt)[0],
            extract_datetime('i had things to do last year', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last decade', dt)[0],
            datetime(2007, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past decade', dt)[0],
            extract_datetime('i had things to do last decade', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last century', dt)[0],
            datetime(1917, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past century', dt)[0],
            extract_datetime('i had things to do last century', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last millennium', dt)[0],
            datetime(1017, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past millennium', dt)[0],
            extract_datetime('i had things to do last millennium', dt)[0])

    def test_extract_ago_en(self):
        dt = datetime(2017, 6, 1, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('i had things to do a day ago', dt)[0],
            datetime(2017, 5, 31, tzinfo=default_timezone()))
        for i in range(1, 1500):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} days ago', dt)[0],
                dt - timedelta(days=i))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} days earlier', dt)[0],
                dt - timedelta(days=i))

        self.assertEqual(
            extract_datetime('i had things to do a week ago', dt)[0],
            datetime(2017, 5, 25, tzinfo=default_timezone()))
        for i in range(1, 1500):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} weeks ago', dt)[0],
                dt - relativedelta(weeks=i))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} weeks earlier', dt)[0],
                dt - relativedelta(weeks=i))

        self.assertEqual(
            extract_datetime('i had things to do a month ago', dt)[0],
            datetime(2017, 5, 1, tzinfo=default_timezone()))
        for i in range(1, 1500):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} months ago', dt)[0],
                dt - relativedelta(months=i))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} months earlier', dt)[0],
                dt - relativedelta(months=i))

        self.assertEqual(
            extract_datetime('i had things to do a year ago', dt)[0],
            datetime(2016, 6, 1, tzinfo=default_timezone()))
        for i in range(1, 1500):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} years ago', dt)[0],
                dt - relativedelta(years=i))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} years earlier', dt)[0],
                dt - relativedelta(years=i))
        self.assertEqual(
            extract_datetime('i had things to do 2 years ago', dt)[0],
            datetime(2015, 6, 1, tzinfo=default_timezone()))

    def test_extract_centuries_ago_en(self):
        dt = datetime(2017, 6, 1, tzinfo=default_timezone())

        self.assertEqual(
            extract_datetime('i had things to do a decade ago', dt)[0],
            datetime(2007, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do 2 decades ago', dt)[0],
            datetime(1997, 6, 1, tzinfo=default_timezone()))

        for i in range(1, 9):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} decades ago', dt)[0],
                dt - relativedelta(years=i * 10))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} decades earlier', dt)[0],
                dt - relativedelta(years=i * 10))

        for i in range(1, 9):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} centuries ago', dt)[0],
                dt - relativedelta(years=i * 100))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} centuries earlier', dt)[0],
                dt - relativedelta(years=i * 100))

        for i in range(1, 2):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} millenniums ago', dt)[0],
                dt - relativedelta(years=i * 1000))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} millenniums earlier', dt)[0],
                dt - relativedelta(years=i * 1000))

    def test_extract_with_other_tzinfo(self):
        local_tz = default_timezone()
        local_dt = datetime(2019, 7, 4, 7, 1, 2, tzinfo=local_tz)
        local_tz_offset = local_tz.utcoffset(local_dt)
        not_local_offset = local_tz_offset + timedelta(hours=1)
        not_local_tz = tz.tzoffset('TST', not_local_offset.total_seconds())
        not_local_dt = datetime(2019, 7, 4, 8, 1, 2, tzinfo=not_local_tz)
        test_dt, remainder = extract_datetime("now is the time", not_local_dt)
        self.assertEqual((test_dt.year, test_dt.month, test_dt.day,
                          test_dt.hour, test_dt.minute, test_dt.second,
                          test_dt.tzinfo),
                         (not_local_dt.year, not_local_dt.month, not_local_dt.day,
                          not_local_dt.hour, not_local_dt.minute, not_local_dt.second,
                          not_local_dt.tzinfo))
        self.assertNotEqual((test_dt.year, test_dt.month, test_dt.day,
                             test_dt.hour, test_dt.minute, test_dt.second,
                             test_dt.tzinfo),
                            (local_dt.year, local_dt.month, local_dt.day,
                             local_dt.hour, local_dt.minute, local_dt.second,
                             local_dt.tzinfo))

    def test_extract_relativedatetime_en(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("lets meet in 5 minutes",
                    "2017-06-27 10:06:02", "lets meet")
        testExtract("lets meet in 5minutes",
                    "2017-06-27 10:06:02", "lets meet")
        testExtract("lets meet in 5 seconds",
                    "2017-06-27 10:01:07", "lets meet")
        testExtract("lets meet in 1 hour",
                    "2017-06-27 11:01:02", "lets meet")
        testExtract("lets meet in 2 hours",
                    "2017-06-27 12:01:02", "lets meet")
        testExtract("lets meet in 2hours",
                    "2017-06-27 12:01:02", "lets meet")
        testExtract("lets meet in 1 minute",
                    "2017-06-27 10:02:02", "lets meet")
        testExtract("lets meet in 1 second",
                    "2017-06-27 10:01:03", "lets meet")
        testExtract("lets meet in 5seconds",
                    "2017-06-27 10:01:07", "lets meet")

    def test_extract_date_with_number_words(self):
        now = datetime(2019, 7, 4, 8, 1, 2, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('What time will it be in 2 minutes', now)[0],
            datetime(2019, 7, 4, 8, 3, 2, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('What time will it be in two minutes', now)[0],
            datetime(2019, 7, 4, 8, 3, 2, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('What time will it be in two hundred minutes', now)[0],
            datetime(2019, 7, 4, 11, 21, 2, tzinfo=default_timezone()))


if __name__ == "__main__":
    unittest.main()