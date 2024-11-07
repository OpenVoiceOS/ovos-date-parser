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

from dateutil import tz


class TestTimezones(unittest.TestCase):
    def test_default_tz(self):
        default = default_timezone()

        naive = datetime.now()

        # convert to default tz
        set_default_tz("Europe/London")
        dt = extract_datetime("tomorrow", anchorDate=naive)[0]
        self.assertEqual(dt.tzinfo, tz.gettz("Europe/London"))

        set_default_tz("America/Chicago")
        dt = extract_datetime("tomorrow", anchorDate=naive)[0]
        self.assertEqual(dt.tzinfo, tz.gettz("America/Chicago"))

        set_default_tz(default)  # undo changes to default tz after test

    def test_convert_to_anchorTZ(self):
        default = default_timezone()
        naive = datetime.now()
        local = now_local()
        london_time = datetime.now(tz=tz.gettz("Europe/London"))
        us_time = datetime.now(tz=tz.gettz("America/Chicago"))

        # convert to anchor date
        dt = extract_datetime("tomorrow", anchorDate=naive)[0]
        self.assertEqual(dt.tzinfo, default_timezone())
        dt = extract_datetime("tomorrow", anchorDate=local)[0]
        self.assertEqual(dt.tzinfo, local.tzinfo)
        dt = extract_datetime("tomorrow", anchorDate=london_time)[0]
        self.assertEqual(dt.tzinfo, london_time.tzinfo)
        dt = extract_datetime("tomorrow", anchorDate=us_time)[0]
        self.assertEqual(dt.tzinfo, us_time.tzinfo)

        # test naive == default tz
        set_default_tz("America/Chicago")
        dt = extract_datetime("tomorrow", anchorDate=naive)[0]
        self.assertEqual(dt.tzinfo, default_timezone())
        set_default_tz("Europe/London")
        dt = extract_datetime("tomorrow", anchorDate=naive)[0]
        self.assertEqual(dt.tzinfo, default_timezone())

        set_default_tz(default)  # undo changes to default tz after test


class TestTokenize(unittest.TestCase):
    def test_tokenize(self):
        self.assertEqual(tokenize('One small step for man'),
                         [Token('One', 0), Token('small', 1), Token('step', 2),
                          Token('for', 3), Token('man', 4)])

        self.assertEqual(tokenize('15%'),
                         [Token('15', 0), Token('%', 1)])

        self.assertEqual(tokenize('I am #1'),
                         [Token('I', 0), Token('am', 1), Token('#', 2),
                          Token('1', 3)])

        self.assertEqual(tokenize('hashtag #1world'),
                         [Token('hashtag', 0), Token('#', 1), Token('1world', 2)])

        self.assertEqual(tokenize(",;_!?<>|()=[]{}»«*~^`."),
                         [Token(",", 0), Token(";", 1), Token("_", 2), Token("!", 3),
                          Token("?", 4), Token("<", 5), Token(">", 6), Token("|", 7),
                          Token("(", 8), Token(")", 9), Token("=", 10), Token("[", 11),
                          Token("]", 12), Token("{", 13), Token("}", 14), Token("»", 15),
                          Token("«", 16), Token("*", 17), Token("~", 18), Token("^", 19),
                          Token("`", 20), Token(".", 21)])


if __name__ == "__main__":
    unittest.main()
