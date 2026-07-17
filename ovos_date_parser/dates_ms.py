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
"""Malay time formatting.

Malay names a clock time as "pukul <hour>" and adds minutes with
"lebih" (more/past): "pukul tiga lebih lima belas" = "quarter past
three". This mirrors Indonesian but uses the Malay connector "lebih"
rather than Indonesian "lewat". The half-to idiom ("pukul setengah
empat") shifts the named hour and is left out to keep the reading
unambiguous.
"""
from ovos_number_parser import pronounce_number


def _period_ms(hour):
    if hour < 12:
        return "pagi"
    if hour < 14:
        return "tengah hari"
    if hour < 19:
        return "petang"
    return "malam"


def nice_time_ms(dt, speech=True, use_24hour=False, use_ampm=False):
    """Format a time to a comfortable Malay human format.

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
        hour = dt.hour
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "tengah malam"
        if dt.hour == 12 and dt.minute == 0:
            return "tengah hari"
        hour = dt.hour % 12
        if hour == 0:
            hour = 12

    speak = "pukul " + pronounce_number(hour, lang="ms")
    if dt.minute:
        speak += " lebih " + pronounce_number(dt.minute, lang="ms")
    if use_ampm and not use_24hour:
        speak += " " + _period_ms(dt.hour)
    return speak
