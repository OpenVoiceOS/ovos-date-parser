import re
from datetime import datetime, timedelta

from ovos_number_parser import numbers_to_digits
from ovos_number_parser.numbers_hu import pronounce_number_hu, _NUM_STRING_HU, extract_number_hu
from ovos_utils.time import DAYS_IN_1_MONTH, DAYS_IN_1_YEAR


def nice_time_hu(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format

    For example, generate 'five thirty' for speech or '5:30' for
    text display.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)=Fal
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
    Returns:
        (str): The formatted time string
    """
    if use_24hour:
        # e.g. "03:01" or "14:22"
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            # e.g. "3:01 AM" or "2:22 PM"
            string = dt.strftime("%I:%M %p")
        else:
            # e.g. "3:01" or "2:22"
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # strip leading zeros

    if not speech:
        return string

    # Generate a speakable version of the time
    speak = ""
    if use_24hour:
        speak += pronounce_number_hu(dt.hour)
        speak = speak.replace(_NUM_STRING_HU[2], 'két')
        speak += " óra"
        if not dt.minute == 0:  # zero minutes are not pronounced
            speak += " " + pronounce_number_hu(dt.minute)

        return speak  # ampm is ignored when use_24hour is true
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "éjfél"
        if dt.hour == 12 and dt.minute == 0:
            return "dél"
        # TODO: "half past 3", "a quarter of 4" and other idiomatic times

        if dt.hour == 0:
            speak += pronounce_number_hu(12)
        elif dt.hour < 13:
            speak = pronounce_number_hu(dt.hour)
        else:
            speak = pronounce_number_hu(dt.hour - 12)

        speak = speak.replace(_NUM_STRING_HU[2], 'két')
        speak += " óra"

        if not dt.minute == 0:
            speak += " " + pronounce_number_hu(dt.minute)

        if use_ampm:
            if dt.hour > 11:
                if dt.hour < 18:
                    speak = "délután " + speak  # 12:01 - 17:59
                elif dt.hour < 22:
                    speak = "este " + speak  # 18:00 - 21:59 este/evening
                else:
                    speak = "éjjel " + speak  # 22:00 - 23:59 éjjel/at night
            elif dt.hour < 3:
                speak = "éjjel " + speak  # 00:01 - 02:59 éjjel/at night
            else:
                speak = "reggel " + speak  # 03:00 - 11:59 reggel/in t. morning

        return speak


def extract_duration_hu(text):
    """
    Convert a Hungarian phrase into a number of seconds.

    Converts things like "tíz perc" or "3 nap 8 óra 10 perc" into a
    timedelta. "hét" is both "seven" and "week": it is read as the unit
    when a number precedes it and as the numeral otherwise. The words
    used in the duration are consumed, the remainder of the text is
    returned.

    Args:
        text (str): string containing a duration.
    Returns:
        (timedelta, str): the duration and the remaining unconsumed text,
                          or None if the input is empty. The duration is
                          None if no duration was found.
    """
    if not text:
        return None

    tokens = text.lower().split()
    protected = []
    for i, tok in enumerate(tokens):
        if tok == "hét" and i > 0 and \
                extract_number_hu(tokens[i - 1]) is not False:
            protected.append("\x00hét\x00")
        else:
            protected.append(tok)
    text = numbers_to_digits(" ".join(protected), "hu")
    text = text.replace("\x00hét\x00", "hét")

    units = [
        (r"mikroszekundum(?:ot)?", "microseconds", None),
        (r"(?:milliszekundum(?:ot)?|ezredmásodperc(?:et)?)", "milliseconds", None),
        (r"másodperc(?:et|re|ig)?", "seconds", None),
        (r"perc(?:et|re|ig)?", "minutes", None),
        (r"(?:óra|órát|órára|óráig)", "hours", None),
        (r"nap(?:ot|ra|ig)?", "days", None),
        (r"h[eé]t(?:et|re|ig)?", "weeks", None),
        (r"hónap(?:ot|ra|ig)?", "days", DAYS_IN_1_MONTH),
        (r"év(?:et|re|ig)?", "days", DAYS_IN_1_YEAR),
        (r"évtized(?:et)?", "days", 10 * DAYS_IN_1_YEAR),
        (r"évszázad(?:ot)?", "days", 100 * DAYS_IN_1_YEAR),
        (r"évezred(?:et)?", "days", 1000 * DAYS_IN_1_YEAR),
    ]
    values = {}
    for unit_re, unit, mult in units:
        pattern = r"(?P<value>\d+(?:[.,]\d+)?)(?:\s+|-)" + unit_re + r"\b"

        def repl(match):
            val = float(match.group("value").replace(",", "."))
            values[unit] = values.get(unit, 0) + (val * mult if mult else val)
            return ""

        text = re.sub(pattern, repl, text)

    text = re.sub(r"\s+", " ", text).strip(" ,;.!")
    duration = timedelta(**values) if values else None
    return duration, text
