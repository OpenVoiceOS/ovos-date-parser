"""Norwegian Nynorsk (nn) date and time parsing.

Ported from the Danish (da) module — the nearest Scandinavian relative —
and adapted to Nynorsk orthography and the modern tens-first counting
reform ("tjueein" = 21). Number and ordinal words come from
:mod:`ovos_number_parser.numbers_nn`; month, weekday, article and
time-of-day vocabulary follow Nynorskordboka / Språkrådet. Nynorsk
differs from Bokmål in weekday names (tysdag, laurdag), "i morgon"
vs "i morgen", veke/månad noun forms, and neuter "eitt".
"""

from ovos_number_parser.numbers_nn import pronounce_number_nn


def nice_time_nn(dt, speech=True, use_24hour=False, use_ampm=False):
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
            speak += "eitt"  # klokka 01:00 is "eitt"
        else:
            speak += pronounce_number_nn(dt.hour)
        if not dt.minute == 0:
            if dt.minute < 10:
                speak += ' null'
            speak += " " + pronounce_number_nn(dt.minute)

        return speak  # ampm is ignored when use_24hour is true
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "midnatt"
        if dt.hour == 12 and dt.minute == 0:
            return "middag"

        if dt.hour == 0:
            speak += pronounce_number_nn(12)
        elif dt.hour <= 13:
            if dt.hour == 1 or dt.hour == 13:  # 01:00 and 13:00 is "eitt"
                speak += 'eitt'
            else:
                speak += pronounce_number_nn(dt.hour)
        else:
            speak += pronounce_number_nn(dt.hour - 12)

        if not dt.minute == 0:
            if dt.minute < 10:
                speak += ' null'
            speak += " " + pronounce_number_nn(dt.minute)

        if use_ampm:
            if dt.hour > 11:
                if dt.hour < 18:
                    speak += " om ettermiddagen"
                elif dt.hour < 22:
                    speak += " om kvelden"
                else:
                    speak += " om natta"
            elif dt.hour < 3:
                speak += " om natta"
            else:
                speak += " om morgonen"

        return speak
