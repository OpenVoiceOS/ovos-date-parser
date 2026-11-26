from datetime import timedelta

from ovos_number_parser.numbers_ru import pronounce_number_ru


def nice_time_ru(dt, speech=True, use_24hour=True, use_ampm=False):
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
            string = dt.strftime("%I:%M")
            if dt.hour < 4:
                string += " ночи"
            elif dt.hour < 12:
                string += " утра"
            elif dt.hour < 18:
                string += " дня"
            else:
                string += " вечера"
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

        # Either "0 8 hundred" or "13 hundred"
        if string[0] == '0':
            speak += pronounce_hour_ru(int(string[0])) + " "
            speak += pronounce_number_ru(int(string[1]))
        else:
            speak = pronounce_hour_ru(int(string[0:2]))

        speak += " "
        if string[3:5] == '00':
            speak += "ровно"
        else:
            if string[3] == '0':
                speak += pronounce_number_ru(0) + " "
                speak += pronounce_number_ru(int(string[4]))
            else:
                speak += pronounce_number_ru(int(string[3:5]))
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "полночь"
        elif dt.hour == 12 and dt.minute == 0:
            return "полдень"

        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        if dt.minute == 15:
            speak = pronounce_hour_ru(hour) + " с четвертью"
        elif dt.minute == 30:
            speak = pronounce_hour_ru(hour) + " с половиной"
        elif dt.minute == 45:
            next_hour = (dt.hour + 1) % 12 or 12
            speak = "без четверти " + pronounce_hour_ru(next_hour)
        else:
            speak = pronounce_hour_ru(hour)

            if dt.minute == 0:
                if not use_ampm:
                    if dt.hour % 12 == 1:
                        return speak
                    return speak + " " + plural_ru(dt.hour % 12, "час", "часа", "часов")
            else:
                if dt.minute < 10:
                    speak += " ноль"
                speak += " " + pronounce_number_ru(dt.minute)

        if use_ampm:
            if dt.hour < 4:
                speak += " ночи"
            elif dt.hour < 12:
                speak += " утра"
            elif dt.hour < 18:
                speak += " дня"
            else:
                speak += " вечера"

        return speak


def nice_duration_ru(duration, speech=True):
    """ Convert duration to a nice spoken timespan

    Args:
        seconds: number of seconds
        minutes: number of minutes
        hours: number of hours
        days: number of days
    Returns:
        str: timespan as a string
    """

    if isinstance(duration, timedelta):
        duration = duration.total_seconds()

    if not speech:
        # M:SS, MM:SS, H:MM:SS, Dd H:MM:SS format
        _days = int(duration // 86400)
        _hours = int(duration // 3600 % 24)
        _minutes = int(duration // 60 % 60)
        _seconds = int(duration % 60)
        out = ""
        if _days > 0:
            out = str(_days) + "d "
        if _hours > 0 or _days > 0:
            out += str(_hours) + ":"
        if _minutes < 10 and (_hours > 0 or _days > 0):
            out += "0"
        out += str(_minutes) + ":"
        if _seconds < 10:
            out += "0"
        out += str(_seconds)
        return out

    days = int(duration // 86400)
    hours = int(duration // 3600 % 24)
    minutes = int(duration // 60 % 60)
    seconds = int(duration % 60)

    out = ''

    if days > 0:
        out += pronounce_number_ru(days)
        out += " " + plural_ru(days, "день", "дня", "дней")
    if hours > 0:
        if out:
            out += " "
        out += pronounce_number_ru(hours)
        out += " " + plural_ru(hours, "час", "часа", "часов")
    if minutes > 0:
        if out:
            out += " "
        out += pronounce_number_feminine_ru(minutes)
        out += " " + plural_ru(minutes, "минута", "минуты", "минут")
    if seconds > 0:
        if out:
            out += " "
        out += pronounce_number_feminine_ru(seconds)
        out += " " + plural_ru(seconds, "секунда", "секунды", "секунд")

    return out


def pronounce_hour_ru(num):
    if num == 1:
        return "час"
    return pronounce_number_ru(num)


def pronounce_number_feminine_ru(num):
    pronounced = pronounce_number_ru(num)

    num %= 100
    if num % 10 == 1 and num // 10 != 1:
        return pronounced[:-2] + "на"
    elif num % 10 == 2 and num // 10 != 1:
        return pronounced[:-1] + "е"

    return pronounced


def plural_ru(num: int, one: str, few: str, many: str):
    num %= 100
    if num // 10 == 1:
        return many
    if num % 10 == 1:
        return one
    if 2 <= num % 10 <= 4:
        return few
    return many
