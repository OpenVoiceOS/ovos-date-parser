from datetime import timedelta

from ovos_number_parser.numbers_az import pronounce_number_az


def _get_full_time_ak(hour):
    if hour in [1, 3, 4, 5, 8, 11]:
        return "ə"
    if hour in [2, 7, 12]:
        return "yə"
    if hour in [9, 10]:
        return "a"
    return "ya"


def _get_half_time_ak(hour):
    if hour in [1, 5, 8, 11]:
        return "in"
    if hour in [2, 7, 12]:
        return "nin"
    if hour in [3, 4]:
        return "ün"
    if hour in [9, 10]:
        return "un"
    return "nın"


def _get_daytime(hour):
    if hour < 6:
        return "gecə"
    if hour < 12:
        return "səhər"
    if hour < 18:
        return "gündüz"
    return "axşam"


def nice_time_az(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format
    For example, generate 'altının yarısı' for speech or '5:30' for
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
            string = dt.strftime("%I:%M")
            if string[0] == '0':
                string = string[1:]  # strip leading zeros
            string = _get_daytime(dt.hour) + " " + string
        else:
            # e.g. "3:01" or "2:22"
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # strip leading zeros

    if not speech:
        return string

    # Generate a speakable version of the time
    if use_24hour:
        speak = ""

        # Either "0 8" or "13"
        if string[0] == '0':
            speak += pronounce_number_az(int(string[0])) + " "
            speak += pronounce_number_az(int(string[1]))
        else:
            speak = pronounce_number_az(int(string[0:2]))

        speak += " "
        if string[3] == '0':
            speak += pronounce_number_az(0) + " "
            speak += pronounce_number_az(int(string[4]))
        else:
            speak += pronounce_number_az(int(string[3:5]))
        return speak
    else:

        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        next_hour = (dt.hour + 1) % 12 or 12
        speak = ""
        if use_ampm:
            speak += _get_daytime(dt.hour) + " "

        if dt.minute == 0:
            speak += "{} tamamdır".format(pronounce_number_az(hour))
        elif dt.minute < 30:
            speak += "{}{} {} dəqiqə işləyib".format(pronounce_number_az(next_hour), _get_full_time_ak(next_hour),
                                                     pronounce_number_az(dt.minute))
        elif dt.minute == 30:
            speak += "{}{} yarısı".format(pronounce_number_az(next_hour), _get_half_time_ak(next_hour))
        else:
            speak += "{}{} {} dəqiqə qalıb".format(pronounce_number_az(next_hour), _get_full_time_ak(next_hour),
                                                   pronounce_number_az(dt.minute - 30))

        return speak


def nice_duration_az(duration, speech=True):
    """ Convert duration in seconds to a nice spoken timespan

    Examples:
       duration = 60  ->  "1:00" or "bir dəqiqə"
       duration = 163  ->  "2:43" or "iki deqiqe qırx üç saniyə"

    Args:
        duration: time, in seconds
        speech (bool): format for speech (True) or display (False)

    Returns:
        str: timespan as a string
    """

    if isinstance(duration, timedelta):
        duration = duration.total_seconds()

    # Do traditional rounding: 2.5->3, 3.5->4, plus this
    # helps in a few cases of where calculations generate
    # times like 2:59:59.9 instead of 3:00.
    duration += 0.5

    days = int(duration // 86400)
    hours = int(duration // 3600 % 24)
    minutes = int(duration // 60 % 60)
    seconds = int(duration % 60)

    if speech:
        out = ""
        if days > 0:
            out += pronounce_number_az(days) + " "
            out += "gün"
        if hours > 0:
            if out:
                out += " "
            out += pronounce_number_az(hours) + " "
            out += "saat"
        if minutes > 0:
            if out:
                out += " "
            out += pronounce_number_az(minutes) + " "
            out += "dəqiqə"
        if seconds > 0:
            if out:
                out += " "
            out += pronounce_number_az(seconds) + " "
            out += "saniyə"
    else:
        # M:SS, MM:SS, H:MM:SS, Dd H:MM:SS format
        out = ""
        if days > 0:
            out = str(days) + "g "
        if hours > 0 or days > 0:
            out += str(hours) + ":"
        if minutes < 10 and (hours > 0 or days > 0):
            out += "0"
        out += str(minutes) + ":"
        if seconds < 10:
            out += "0"
        out += str(seconds)

    return out
