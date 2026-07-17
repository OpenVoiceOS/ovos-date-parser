from datetime import datetime

from ovos_number_parser.numbers_an import AN

# Standard written Aragonese weekday names.
# Sources: Biquipedia "Nombre d'os días d'a semana" and "Semana"
# (https://an.wikipedia.org/wiki/Nombre_d'os_d%C3%ADas_d'a_semana),
# Aragonese Wiktionary entry "luns".
WEEKDAYS_AN = {
    0: "luns",
    1: "martes",
    2: "miercres",
    3: "chueves",
    4: "viernes",
    5: "sabado",
    6: "dominche"
}
# Aragonese month names.
# Source: Biquipedia "Mes" (https://an.wikipedia.org/wiki/Mes).
MONTHS_AN = {
    1: "chinero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "chunyo",
    7: "chuliol",
    8: "agosto",
    9: "setiembre",
    10: "octubre",
    11: "noviembre",
    12: "deciembre"
}

# Feminine cardinal hour words for the spoken clock (1-12).
# The number engine emits a few masculine or variant forms (un, cuatre,
# siet), so the clock forms are pinned here.
HOURS_AN = {
    1: "una",
    2: "dos",
    3: "tres",
    4: "cuatro",
    5: "cinco",
    6: "seis",
    7: "siete",
    8: "ueito",
    9: "nueu",
    10: "diez",
    11: "once",
    12: "doce"
}

_VOWELS_AN = "aeiou"


def pronounce_number_an(number, **kwargs):
    return AN.pronounce_number(number, **kwargs)


def _starts_with_vowel_an(word):
    """Whether an Aragonese word starts with a vowel sound (accents ignored)."""
    first = word[:1].lower()
    first = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}.get(first, first)
    return first in _VOWELS_AN


def _de_connector_an(word):
    """The 'de' connector, elided to "d'" before a vowel-initial word."""
    if _starts_with_vowel_an(word):
        return f"d'{word}"
    return f"de {word}"


def nice_year_an(dt, bc=False):
    """Format a year in a pronounceable Aragonese form.

    Args:
        dt (datetime): date to format (assumed already in the local timezone)
        bc (bool): append "a.C." after the year
    Returns:
        (str): the year formatted as a string
    """
    year = pronounce_number_an(dt.year)
    if bc:
        return f"{year} a.C."
    return year


def nice_weekday_an(dt):
    weekday = WEEKDAYS_AN[dt.weekday()]
    return weekday.capitalize()


def nice_month_an(dt):
    month = MONTHS_AN[dt.month]
    return month.capitalize()


def nice_day_an(dt, date_format='DMY', include_month=True):
    if include_month:
        month = nice_month_an(dt)
        if date_format == 'MDY':
            return "{} {}".format(month, dt.strftime("%d").lstrip("0"))
        else:
            return "{} {}".format(dt.strftime("%d").lstrip("0"), month)
    return dt.strftime("%d").lstrip("0")


def nice_date_an(dt: datetime, now: datetime = None, include_weekday=True):
    """Format a date in a pronounceable Aragonese form.

    For example, generates 'luns, cinco de chunyo de 2018'.

    Args:
        dt (datetime): date to format (assumed already in the local timezone)
        now (datetime): reference date. When provided the returned date is
            shortened: the year is dropped when ``now`` is in the same year as
            ``dt`` and the month is dropped when ``now`` is in the same month.
        include_weekday (bool): whether to prepend the weekday name.
    Returns:
        (str): the formatted date string
    """
    day = pronounce_number_an(dt.day)
    month = _de_connector_an(nice_month_an(dt))
    year = _de_connector_an(nice_year_an(dt))
    nice = f"{day} {month} {year}"
    if now is not None:
        nice = day
        if dt.month != now.month:
            nice = nice + " " + _de_connector_an(nice_month_an(dt))
        if dt.year != now.year:
            nice = nice + " " + _de_connector_an(nice_year_an(dt))

    if include_weekday:
        weekday = nice_weekday_an(dt)
        nice = f"{weekday}, {nice}"
    return nice


def nice_time_an(dt, speech=True, use_24hour=False, use_ampm=False):
    """Format a time in a pronounceable Aragonese form.

    For example, generates 'Ye la meya pa las cinco' for speech, or '4:30'
    for display.

    Args:
        dt (datetime): time to format (assumed already in the local timezone)
        speech (bool): format for speech (True) or display (False)
        use_24hour (bool): output in 24-hour rather than 12-hour format
        use_ampm (bool): include am/pm in the 12-hour display format
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
        if string[0] == "0":
            string = string[1:]

    if not speech:
        return string

    if use_24hour:
        # Aragonese only fixes the 12-hour spoken idiom, so a 24-hour clock
        # is read out digit by digit rather than invented.
        hour = HOURS_AN[dt.hour] if dt.hour in HOURS_AN else pronounce_number_an(dt.hour)
        if dt.minute == 0:
            return f"{hour} en punto"
        if dt.minute < 10:
            return f"{hour} zero {pronounce_number_an(dt.minute)}"
        return f"{hour} {pronounce_number_an(dt.minute)}"

    minute = dt.minute
    # 12-hour clock: 0 -> 12, 13 -> 1, ...
    hour12 = dt.hour % 12
    if hour12 == 0:
        hour12 = 12
    next_hour = hour12 % 12 + 1

    def _on_hour(h):
        if h == 1:
            return "Ye la una"
        return f"Son las {HOURS_AN[h]}"

    if minute == 0:
        return _on_hour(hour12)
    if minute == 15:
        return f"Ye lo cuarto pa las {HOURS_AN[next_hour]}"
    if minute == 30:
        return f"Ye la meya pa las {HOURS_AN[next_hour]}"
    if minute == 45:
        return f"Son los tres cuartos pa las {HOURS_AN[next_hour]}"

    if minute < 30:
        mins = pronounce_number_an(minute)
        if hour12 == 1:
            return f"Ye la una y {mins}"
        return f"Son las {HOURS_AN[hour12]} y {mins}"
    # minute > 30 (and not 45): count toward the next hour
    mins = pronounce_number_an(60 - minute)
    if next_hour == 1:
        return f"Ye la una menos {mins}"
    return f"Son las {HOURS_AN[next_hour]} menos {mins}"


def nice_date_time_an(dt, now=None, use_24hour=False, use_ampm=False):
    """Format a date and time in a pronounceable Aragonese form.

    Args:
        dt (datetime): date and time to format (assumed already local)
        now (datetime): reference date; when provided the date is shortened
        use_24hour (bool): output the time in 24-hour rather than 12-hour form
        use_ampm (bool): include am/pm in the 12-hour time
    Returns:
        (str): the formatted date and time string
    """
    date_str = nice_date_an(dt, now)
    time_str = nice_time_an(dt, use_24hour=use_24hour, use_ampm=use_ampm)
    return f"{date_str} a las {time_str}"
