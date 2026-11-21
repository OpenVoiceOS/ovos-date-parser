import re
from datetime import timedelta

from ovos_number_parser.numbers_pl import pronounce_number_pl
from ovos_number_parser.util import GrammaticalGender


def nice_time_pl(dt, speech=True, use_24hour=True, use_ampm=False):
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
    string = dt.strftime("%H:%M")
    if not speech:
        return string

    # Generate a speakable version of the time
    speak = ""

    # Either "0 8 hundred" or "13 hundred"
    if string[0:2] == '00':
        speak = ""
    else:
        speak = pronounce_number_pl(int(string[0:2]), ordinals=True,
                                    gender=GrammaticalGender.FEMININE)

    speak += ' ' if string[0:2] != '00' else ''
    if string[3:5] == '00':
        speak += 'zero zero'
    else:
        if string[3] == '0':
            speak += pronounce_number_pl(int(string[4]))
        else:
            speak += pronounce_number_pl(int(string[3:5]))

    if string[0:2] == '00':
        speak += " po północy"
    return speak


def nice_duration_pl(duration, speech=True):
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
    sec_main, sec_div = divmod(seconds, 10)
    min_main, min_div = divmod(minutes, 10)
    hour_main, hour_div = divmod(hours, 10)

    if days > 0:
        out += pronounce_number_pl(days) + " "
        if days == 1:
            out += 'dzień'
        else:
            out += 'dni'
    if hours > 0:
        if out:
            out += " "
        out += get_pronounce_number_for_duration(hours) + " "
        if hours == 1:
            out += 'godzina'
        elif hour_main == 1 or hour_div > 4:
            out += 'godzin'
        else:
            out += 'godziny'
    if minutes > 0:
        if out:
            out += " "
        out += get_pronounce_number_for_duration(minutes) + " "
        if minutes == 1:
            out += 'minuta'
        elif min_main == 1 or min_div > 4:
            out += 'minut'
        else:
            out += 'minuty'
    if seconds > 0:
        if out:
            out += " "
        out += get_pronounce_number_for_duration(seconds) + " "
        if sec_div == 0:
            out += 'sekund'
        elif seconds == 1:
            out += 'sekunda'
        elif sec_main == 1 or sec_div > 4:
            out += 'sekund'
        else:
            out += 'sekundy'

    return out


def get_pronounce_number_for_duration(num):
    pronounced = pronounce_number_pl(num)

    return 'jedna' if pronounced == 'jeden' else pronounced


# Ordinal day-of-month words in the genitive case Polish uses for dates,
# e.g. "piętnastego stycznia" -> 15 January. Mapped to the day number so the
# date parser can treat them like a numeric day.
_ORDINAL_DAY_UNITS_PL = {
    1: 'pierwszego', 2: 'drugiego', 3: 'trzeciego', 4: 'czwartego',
    5: 'piątego', 6: 'szóstego', 7: 'siódmego', 8: 'ósmego',
    9: 'dziewiątego', 10: 'dziesiątego', 11: 'jedenastego', 12: 'dwunastego',
    13: 'trzynastego', 14: 'czternastego', 15: 'piętnastego',
    16: 'szesnastego', 17: 'siedemnastego', 18: 'osiemnastego',
    19: 'dziewiętnastego', 20: 'dwudziestego', 30: 'trzydziestego',
}


_ORDINAL_TENS_PL = {
    2: 'dwudziestego', 3: 'trzydziestego', 4: 'czterdziestego',
    5: 'pięćdziesiątego', 6: 'sześćdziesiątego', 7: 'siedemdziesiątego',
    8: 'osiemdziesiątego', 9: 'dziewięćdziesiątego',
}
_HUNDREDS_PL = {
    1: 'sto', 2: 'dwieście', 3: 'trzysta', 4: 'czterysta', 5: 'pięćset',
    6: 'sześćset', 7: 'siedemset', 8: 'osiemset', 9: 'dziewięćset',
}
_ORDINAL_HUNDREDS_PL = {
    1: 'setnego', 2: 'dwusetnego', 3: 'trzechsetnego', 4: 'czterechsetnego',
    5: 'pięćsetnego', 6: 'sześćsetnego', 7: 'siedemsetnego',
    8: 'osiemsetnego', 9: 'dziewięćsetnego',
}
_ORDINAL_THOUSANDS_PL = {
    1: 'tysięcznego', 2: 'dwutysięcznego', 3: 'trzytysięcznego',
    4: 'czterotysięcznego', 5: 'pięciotysięcznego', 6: 'sześciotysięcznego',
    7: 'siedmiotysięcznego', 8: 'ośmiotysięcznego',
    9: 'dziewięciotysięcznego',
}


def nice_year_pl(dt, bc=False, genitive=False):
    """Format a year as Polish reads it: an ordinal.

    A year said alone is a nominative ordinal (CLDR RBNF pl
    ``%spellout-ordinal-masculine``): 2024 is "dwa tysiące dwudziesty
    czwarty". Inside a date the year is a genitive ordinal (CLDR
    ``%spellout-numbering-year``): 1905 is "tysiąc dziewięćset piątego".
    The thousands stay cardinal before a remainder; a round number takes
    the isolated ordinal ("dwutysięczny", "tysiąc dziewięćsetny").

    Args:
        dt (datetime): date whose year to format
        bc (bool): append "p.n.e." after the year
        genitive (bool): the genitive form a date takes
    Returns:
        (str): the year in words
    """
    thousands, rest = divmod(dt.year, 1000)
    hundreds, below = divmod(rest, 100)
    if not rest:
        words = [_ORDINAL_THOUSANDS_PL[thousands]]
    else:
        words = [pronounce_number_pl(thousands * 1000)] if thousands else []
        if not below:
            words.append(_ORDINAL_HUNDREDS_PL[hundreds])
        else:
            if hundreds:
                words.append(_HUNDREDS_PL[hundreds])
            tens, units = divmod(below, 10)
            if below < 20 or not units:
                words.append(_ORDINAL_DAY_UNITS_PL.get(below)
                             or _ORDINAL_TENS_PL[tens])
            else:
                words += [_ORDINAL_TENS_PL[tens], _ORDINAL_DAY_UNITS_PL[units]]
    year = " ".join(words)
    if not genitive:
        # the nominative ending replaces the genitive -ego:
        # "drugiego" -> "drugi", "piątego" -> "piąty"
        year = re.sub(r"ego\b", "y", re.sub(r"iego\b", "i", year))
    if bc:
        return f"{year} p.n.e."
    return year
