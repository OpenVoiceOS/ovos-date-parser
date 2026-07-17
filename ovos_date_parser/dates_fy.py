from datetime import datetime

from ovos_number_parser.numbers_fy import pronounce_number_fy

# West Frisian (Frysk) weekday names.
# Sources: West Frisian phrasebook (Wikivoyage) and West Frisian language
# (Wikipedia). "Sneon" is the standard form for Saturday; "Saterdei" also
# occurs regionally.
WEEKDAYS_FY = {
    0: "moandei",
    1: "tiisdei",
    2: "woansdei",
    3: "tongersdei",
    4: "freed",
    5: "sneon",
    6: "snein"
}
# West Frisian month names.
# Source: West Frisian phrasebook (Wikivoyage).
MONTHS_FY = {
    1: "jannewaris",
    2: "febrewaris",
    3: "maart",
    4: "april",
    5: "maaie",
    6: "juny",
    7: "july",
    8: "augustus",
    9: "septimber",
    10: "oktober",
    11: "novimber",
    12: "desimber"
}
# Inflected hour forms used after "healwei", "kertier oer/foar" and the
# "minutes oer/foar" constructions when telling the time.
# Source: "Telling Time in West Frisian"
# (funwithfrisian.blogspot.com/2016/04/telling-time-in-west-frisian.html).
HOURS_FY = {
    1: "ienen",
    2: "twaen",
    3: "trijen",
    4: "fjouweren",
    5: "fiven",
    6: "seizen",
    7: "sânen",
    8: "achten",
    9: "njoggenen",
    10: "tsienen",
    11: "alven",
    12: "tolven"
}


def _fix_hour_fy(hour):
    hour = hour % 12
    if hour == 0:
        hour = 12
    return hour


def nice_year_fy(dt, bc=False):
    """Format a year in a pronounceable West Frisian form.

    Args:
        dt (datetime): date to format (assumed already in the local timezone)
        bc (bool): append "f.Kr." after the year
    Returns:
        (str): the year formatted as a string
    """
    year = pronounce_number_fy(dt.year)
    if bc:
        return f"{year} f.Kr."
    return year


def nice_weekday_fy(dt):
    weekday = WEEKDAYS_FY[dt.weekday()]
    return weekday.capitalize()


def nice_month_fy(dt):
    month = MONTHS_FY[dt.month]
    return month.capitalize()


def nice_day_fy(dt, date_format='DMY', include_month=True):
    if include_month:
        month = nice_month_fy(dt)
        if date_format == 'MDY':
            return "{} {}".format(month, dt.strftime("%d").lstrip("0"))
        else:
            return "{} {}".format(dt.strftime("%d").lstrip("0"), month)
    return dt.strftime("%d").lstrip("0")


def nice_date_fy(dt: datetime, now: datetime = None, include_weekday=True):
    """Format a date in a pronounceable West Frisian form.

    For example, generates 'moandei 5 maaie 2018'. West Frisian keeps the
    Germanic day-month-year order.

    Args:
        dt (datetime): date to format (assumed already in the local timezone)
        now (datetime): reference date. When provided the returned date is
            shortened: the year is dropped when ``now`` is in the same year as
            ``dt`` and the month is dropped when ``now`` is in the same month.
        include_weekday (bool): whether to prepend the weekday name.
    Returns:
        (str): the formatted date string
    """
    day = pronounce_number_fy(dt.day)
    nice = f"{day} {nice_month_fy(dt)} {nice_year_fy(dt)}"
    if now is not None:
        nice = day
        if dt.month != now.month:
            nice = nice + " " + nice_month_fy(dt)
        if dt.year != now.year:
            nice = nice + " " + nice_year_fy(dt)

    if include_weekday:
        weekday = nice_weekday_fy(dt)
        nice = f"{weekday} {nice}"
    return nice


def nice_date_time_fy(dt, now=None, use_24hour=False, use_ampm=False):
    """Format a date and time in a pronounceable West Frisian form.

    For example, generates 'moandei 5 maaie 2018 om fjouwer oere'.
    """
    return f"{nice_date_fy(dt, now)} om " \
           f"{nice_time_fy(dt, use_24hour=use_24hour, use_ampm=use_ampm)}"


def nice_part_of_day_fy(dt, speech=True):
    """Return the West Frisian adverbial name for the part of the day.

    Source: Taalportaal / West Frisian phrasebook — the genitive "-s" adverbs
    moarns, middeis, jûns, nachts.
    """
    if dt.hour < 6:
        return " nachts"
    if dt.hour < 12:
        return " moarns"
    if dt.hour < 18:
        return " middeis"
    return " jûns"


def nice_time_fy(dt, speech=True, use_24hour=False, use_ampm=False):
    """Format a time in a comfortable West Frisian human format.

    For example, generates 'healwei fiven' for speech or '4:30' for text.

    West Frisian, like Dutch, looks ahead to the coming hour for the half and
    the quarter-to: 'healwei fiven' is 4:30 (literally "halfway to five") and
    'kertier foar fiven' is 4:45. The hour word is "oere".

    Args:
        dt (datetime): date to format (assumed already in the local timezone)
        speech (bool): format for speech (default/True) or display (False)
        use_24hour (bool): output in 24-hour format
        use_ampm (bool): include the part of day for 12-hour format
    Returns:
        (str): the formatted time string
    """
    if use_24hour:
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            string = dt.strftime("%I:%M %p")
        else:
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # strip leading zeros

    if not speech:
        return string

    speak = ""
    if use_24hour:
        speak += pronounce_number_fy(dt.hour)
        speak += " oere"
        if dt.minute != 0:
            speak += " " + pronounce_number_fy(dt.minute)
        return speak  # ampm is ignored when use_24hour is true

    hour = dt.hour % 12
    if dt.minute == 0:
        hour = _fix_hour_fy(hour)
        speak += pronounce_number_fy(hour)
        speak += " oere"
    elif dt.minute == 15:
        hour = _fix_hour_fy(hour)
        speak += "kertier oer " + HOURS_FY[hour]
    elif dt.minute == 30:
        hour = _fix_hour_fy(hour + 1)
        speak += "healwei " + HOURS_FY[hour]
    elif dt.minute == 45:
        hour = _fix_hour_fy(hour + 1)
        speak += "kertier foar " + HOURS_FY[hour]
    elif dt.minute < 30:
        hour = _fix_hour_fy(hour)
        speak += pronounce_number_fy(dt.minute) + " oer " + HOURS_FY[hour]
    else:
        hour = _fix_hour_fy(hour + 1)
        speak += pronounce_number_fy(60 - dt.minute) + " foar " + HOURS_FY[hour]

    if use_ampm:
        speak += nice_part_of_day_fy(dt)

    return speak
