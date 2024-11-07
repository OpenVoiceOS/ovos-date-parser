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
from datetime import datetime, timedelta

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    extract_duration, extract_datetime
)


class TestNormalize(unittest.TestCase):

    def test_extract_duration_fa(self):
        self.assertEqual(extract_duration("10 ثانیه"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 دقیقه"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 ساعت"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 روز"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 هفته"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("هفت ساعت"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 ثانیه"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("هشت و نیم روز و "
                                          "سی و نه ثانیه"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("یک تایمر برای نیم ساعت دیگه بزار"),
                         (timedelta(minutes=30), "یک تایمر برای دیگه بزار"))
        self.assertEqual(extract_duration("چهار و نیم دقیقه تا "
                                          "طلوع آفتاب"),
                         (timedelta(minutes=4.5), "تا طلوع آفتاب"))
        self.assertEqual(extract_duration("این فیلم یک ساعت و پنجاه و هفت و نیم دقیقه "
                                          "طول می کشد"),
                         (timedelta(hours=1, minutes=57.5),
                          "این فیلم طول می کشد"))

    def test_extractdatetime_fa(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())  # Tue June 27, 2017 @ 1:04pm
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("الان ساعت اینه",
                    "2017-06-27 13:04:00", "ساعت اینه")
        testExtract("یک ثانیه دیگه",
                    "2017-06-27 13:04:01", "")
        testExtract("یک دقیقه دیگه",
                    "2017-06-27 13:05:00", "")
        testExtract("دو دقیقه دیگه",
                    "2017-06-27 13:06:00", "")
        testExtract("دو ساعت دیگه",
                    "2017-06-27 15:04:00", "")
        testExtract("من یک ساعت دیگه می خوامش",
                    "2017-06-27 14:04:00", "من می خوامش")
        testExtract("1 ثانیه دیگه",
                    "2017-06-27 13:04:01", "")
        testExtract("2 ثانیه دیگه",
                    "2017-06-27 13:04:02", "")
        testExtract("یک آلارم برای یک دقیقه بعد بزار",
                    "2017-06-27 13:05:00", "یک آلارم برای بزار")
        testExtract("یک آلارم برای نیم ساعت دیگه بزار",
                    "2017-06-27 13:34:00", "یک آلارم برای بزار")
        testExtract("یه آلارم برای پنج روز بعد بزار",
                    "2017-07-02 00:00:00", "یه آلارم برای بزار")
        testExtract("پس فردا",
                    "2017-06-29 00:00:00", "")
        testExtract("آب و هوا پس فردا چطوره؟",
                    "2017-06-29 00:00:00", "آب و هوا چطوره؟")
        # testExtract("ساعت بیست و دو و چهل و پنج دقیقه بهم یادآوری کن",
        #            "2017-06-27 22:45:00", "بهم یادآوری کن")
        testExtract("هوای جمعه صبح چطوره؟",
                    "2017-06-30 08:00:00", "هوای چطوره؟")
        testExtract("هوای فردا چطوره؟",
                    "2017-06-28 00:00:00", "هوای چطوره؟")
        testExtract("هوای امروز بعد از ظهر چطوره؟",
                    "2017-06-27 15:00:00", "هوای چطوره؟")
        testExtract("یادم بنداز که هشت هفته و دو روز دیگه به مادرم زنگ بزنم",
                    "2017-08-24 00:00:00", "یادم بنداز که به مادرم زنگ بزنم")
        # testExtract("یادم بنداز که دوازده مرداد به مادرم زنگ بزنم",
        #            "2017-08-03 00:00:00", "یادم بنداز که به مادرم زنگ بزنم")
        # testExtract("یادم بنداز که ساعت هفت به مادرم زنگ بزنم",
        #            "2017-06-28 07:00:00", "یادم بنداز که به مادرم زنگ بزنم")
        # testExtract("یادم بنداز که فردا ساعت بیست و دو به مادرم زنگ بزنم",
        #            "2017-06-28 22:00:00", "یادم بنداز که به مادرم زنگ بزنم")
        # TODO: This test is imperfect due to the "at 7:00" still in the
        #       remainder.  But let it pass for now since time is correct


if __name__ == "__main__":
    unittest.main()
