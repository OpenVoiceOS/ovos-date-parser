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



# --- test harness compatibility shims (adapt legacy call convention to dev API) ---
import ovos_date_parser as _odp
from ovos_utils.time import now_local, to_local, DAYS_IN_1_YEAR, DAYS_IN_1_MONTH
from ovos_config.locale import get_default_tz as default_timezone
LANG = "sv"


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

class TestNormalize(unittest.TestCase):

    def test_extractdatetime_sv(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 0, 0)
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang='sv-se')
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        testExtract("Planera bakhållet 5 dagar från nu",
                    "2017-07-02 00:00:00", "planera bakhållet")
        testExtract("Vad blir vädret i övermorgon?",
                    "2017-06-29 00:00:00", "vad blir vädret")
        testExtract("Påminn mig klockan 10:45",
                    "2017-06-27 10:45:00", "påminn mig klockan")
        testExtract("vad blir vädret på fredag morgon",
                    "2017-06-30 08:00:00", "vad blir vädret")
        testExtract("vad blir morgondagens väder",
                    "2017-06-28 00:00:00", "vad blir väder")
        testExtract("påminn mig att ringa mamma om 8 veckor och 2 dagar",
                    "2017-08-24 00:00:00", "påminn mig att ringa mamma om och")
        testExtract("Spela Kurt Olssons musik 2 dagar från Fredag",
                    "2017-07-02 00:00:00", "spela kurt olssons musik")
        testExtract("vi möts 20:00",
                    "2017-06-27 20:00:00", "vi möts")

    def test_extractdatetime_default_sv(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime('påminn mig att klippa mig på fredag',
                               anchor, lang='sv-se', default_time=default)
        self.assertEqual(default, res[0].time())

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""
        self.assertEqual(extract_datetime('Ingen tid', lang='sv-se'), None)


class TestExtractDuration(unittest.TestCase):
    def test_valid_extract_duration(self):
        """Duration in sentence."""
        td, remains = extract_duration("5 minuter", lang='sv-se')
        self.assertEqual(td, timedelta(seconds=300))
        self.assertEqual(remains, '')

        td, remains = extract_duration("om 2 och en halv timme", lang='sv-se')
        self.assertEqual(td, timedelta(hours=2, minutes=30))
        self.assertEqual(remains, "om och")

        td, remains = extract_duration("starta en 9 minuters timer",
                                       lang='sv-se')
        self.assertEqual(td, timedelta(minutes=9))
        self.assertEqual(remains, "starta timer")

        # Extraction of things like "kvart" and "halvtimme"
        td, remains = extract_duration("i en kvart", lang='sv-se')
        self.assertEqual(td, timedelta(minutes=15))
        self.assertEqual(remains, "i")

        td, remains = extract_duration("hämta mig om två timmar och en kvart",
                                       lang='sv-se')
        self.assertEqual(td, timedelta(hours=2, minutes=15))
        self.assertEqual(remains, "hämta mig om och")

        td, remains = extract_duration("om en halvtimme", lang='sv-se')
        self.assertEqual(td, timedelta(minutes=30))
        self.assertEqual(remains, "om")

    def test_invalid_extract_duration(self):
        """No duration in sentence."""
        res = extract_duration("vad är en myrslok", lang='sv-se')
        self.assertEqual(res, None)

        res = extract_duration("svaret är 42", lang='sv-se')
        self.assertEqual(res, None)


if __name__ == "__main__":
    unittest.main()
