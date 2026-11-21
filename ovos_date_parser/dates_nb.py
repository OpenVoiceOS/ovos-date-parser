"""Norwegian Bokmål (nb) date and time formatting.

Ported from the Danish (da) module — the nearest Scandinavian relative —
and adapted to Bokmål orthography and the modern tens-first counting
reform ("den nye tellemåten", ``tjueen`` = 21). Number and ordinal words
come from :mod:`ovos_number_parser.numbers_nb`; month, weekday, article
and time-of-day vocabulary follow Bokmålsordboka / Språkrådet.
"""

from ovos_number_parser.numbers_nb import pronounce_number_nb


def nice_time_nb(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format

    For example, generate 'fem tretti' for speech or '5:30' for
    text display.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
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

    speak = ""
    if use_24hour:
        if dt.hour == 1:
            speak += "ett"  # klokka 01:00 is "ett"
        else:
            speak += pronounce_number_nb(dt.hour)
        if not dt.minute == 0:
            if dt.minute < 10:
                speak += ' null'
            speak += " " + pronounce_number_nb(dt.minute)

        return speak  # ampm is ignored when use_24hour is true
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "midnatt"
        if dt.hour == 12 and dt.minute == 0:
            return "middag"

        if dt.hour == 0:
            speak += pronounce_number_nb(12)
        elif dt.hour <= 13:
            if dt.hour == 1 or dt.hour == 13:  # 01:00 and 13:00 is "ett"
                speak += 'ett'
            else:
                speak += pronounce_number_nb(dt.hour)
        else:
            speak += pronounce_number_nb(dt.hour - 12)

        if not dt.minute == 0:
            if dt.minute < 10:
                speak += ' null'
            speak += " " + pronounce_number_nb(dt.minute)

        if use_ampm:
            if dt.hour > 11:
                if dt.hour < 18:
                    speak += " om ettermiddagen"
                elif dt.hour < 22:
                    speak += " om kvelden"
                else:
                    speak += " om natten"
            elif dt.hour < 3:
                speak += " om natten"
            else:
                speak += " om morgenen"

        return speak
