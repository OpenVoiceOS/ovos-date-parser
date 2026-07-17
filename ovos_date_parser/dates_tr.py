# Copyright OpenVoiceOS
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
"""Turkish time formatting.

Turkish reads clock times as "saat <hour> <minute>" (literally "hour
<h> <m>"), the form used in broadcast and announcement speech. The
idiomatic case-marked forms ("üçü on geçiyor" = "ten past three")
require the accusative/ablative declension of the numeral and are left
out rather than approximated.
"""
from ovos_number_parser import pronounce_number


def _period_tr(hour):
    if hour < 6:
        return "gece"
    if hour < 12:
        return "sabah"
    if hour < 18:
        return "öğleden sonra"
    if hour < 22:
        return "akşam"
    return "gece"


def nice_time_tr(dt, speech=True, use_24hour=False, use_ampm=False):
    """Format a time to a comfortable Turkish human format.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (True) or display (False)
        use_24hour (bool): output in 24-hour or 12-hour format
        use_ampm (bool): append the part of day for 12-hour format
    Returns:
        (str): The formatted time string
    """
    if use_24hour:
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            string = dt.strftime("%I:%M %p")
        else:
            string = dt.strftime("%I:%M")

    if not speech:
        return string

    if use_24hour:
        speak = "saat " + pronounce_number(dt.hour, lang="tr")
        if dt.minute:
            if dt.minute < 10:
                speak += " sıfır"
            speak += " " + pronounce_number(dt.minute, lang="tr")
        return speak

    if dt.hour == 0 and dt.minute == 0:
        return "gece yarısı"
    if dt.hour == 12 and dt.minute == 0:
        return "öğle"

    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    speak = "saat " + pronounce_number(hour, lang="tr")
    if dt.minute:
        if dt.minute < 10:
            speak += " sıfır"
        speak += " " + pronounce_number(dt.minute, lang="tr")
    if use_ampm:
        speak += " " + _period_tr(dt.hour)
    return speak
