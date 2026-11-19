from datetime import timedelta

from ovos_number_parser.numbers_uk import pronounce_number_uk, _NUM_STRING_UK

# hours
HOURS_UK = {
    1: 'перша',
    2: 'друга',
    3: 'третя',
    4: 'четверта',
    5: "п'ята",
    6: 'шоста',
    7: 'сьома',
    8: 'восьма',
    9: "дев'ята",
    10: 'десята',
    11: 'одинадцята',
    12: 'дванадцята'
}
# Months


def nice_time_uk(dt, speech=True, use_24hour=True, use_ampm=False):
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
                string += " ночі"
            elif dt.hour < 12:
                string += " ранку"
            elif dt.hour < 18:
                string += " дня"
            else:
                string += " вечора"
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
            speak = pronounce_hour_uk(int(string[0]))
            if not speak:
                speak = pronounce_number_uk(int(string[0])) + ' '
            speak += pronounce_number_uk(int(string[1]))
        else:
            speak = pronounce_hour_uk(int(string[0:2]))
            if speak is None:
                speak = pronounce_number_uk(int(string[0:2]))

        speak += " "
        if string[3:5] == '00':
            speak += "рівно"
        else:
            if string[3] == '0':
                speak += pronounce_number_uk(0) + " "
                speak += pronounce_number_uk(int(string[4]))
            else:
                speak += pronounce_number_uk(int(string[3:5]))
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "опівночі"
        elif dt.hour == 12 and dt.minute == 0:
            return "опівдні"

        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        if dt.minute == 15:
            speak = "чверть після " + pronounce_hour_genitive_uk(hour)
        elif dt.minute == 30:
            speak = "половина після " + pronounce_hour_genitive_uk(hour)
        elif dt.minute == 45:
            next_hour = (dt.hour + 1) % 12 or 12
            speak = "без четверті " + pronounce_hour_uk(next_hour)
        else:
            speak = pronounce_hour_uk(hour)

            if use_ampm:
                if dt.hour < 4:
                    speak += " ночі"
                elif dt.hour < 12:
                    speak += " ранку"
                elif dt.hour < 18:
                    speak += " дня"
                else:
                    speak += " вечора"

            if dt.minute == 0:
                if not use_ampm:
                    if dt.hour % 12 == 1:
                        return speak
                    # TODO: the `one`/`few`/`many` structure doesn't cover
                    #   all cases in Ukrainian
                    return speak + " " + plural_uk(dt.hour % 12, one="година",
                                                   few="години", many="годин")
            else:
                if dt.minute < 10:
                    speak += " нуль"
                speak += " " + pronounce_number_uk(dt.minute)

        return speak


def nice_duration_uk(duration, speech=True):
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
        out += pronounce_number_uk(days)
        out += " " + plural_uk(days, "день", "дня", "днів")
    if hours > 0:
        if out:
            out += " "
        out += pronounce_number_feminine_uk(hours)
        if out == 'один':
            out = 'одна'
        out += " " + plural_uk(hours, "година", "години", "годин")
    if minutes > 0:
        if out:
            out += " "
        out += pronounce_number_feminine_uk(minutes)
        out += " " + plural_uk(minutes, "хвилина", "хвилини", "хвилин")
    if seconds > 0:
        if out:
            out += " "
        out += pronounce_number_feminine_uk(seconds)
        out += " " + plural_uk(seconds, "секунда", "секунди", "секунд")

    return out


def pronounce_hour_uk(num):
    if num in HOURS_UK.keys():
        return HOURS_UK[num] + ' година'


def pronounce_mins_uk(num):
    if num in _NUM_STRING_UK.keys():
        if num == 1:
            return 'одна хвилина'
        if num == 2:
            return 'дві хвилини'
        if num in [10, 20, 30, 40, 50, 60]:
            _NUM_STRING_UK[num] + 'хвилин'
        else:
            return


def pronounce_hour_genitive_uk(num):
    if num in HOURS_UK.keys():
        if num == 3:
            gen_hour = HOURS_UK[num][:-1] + 'ьої'
        else:
            gen_hour = HOURS_UK[num][:-1] + 'ої'
        return gen_hour + ' години'


def pronounce_number_feminine_uk(num):
    pronounced = pronounce_number_uk(num)

    num %= 100
    if num % 10 == 1 and num // 10 != 1:
        return pronounced[:-2] + "на"
    elif num % 10 == 2 and num // 10 != 1:
        return pronounced[:-1] + "і"

    return pronounced


def plural_uk(num: int, one: str, few: str, many: str):
    num %= 100
    if num // 10 == 1:
        return many
    if num % 10 == 1:
        return one
    if 2 <= num % 10 <= 4:
        return few
    return many
