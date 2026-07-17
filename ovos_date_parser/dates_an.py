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
    6: "chunio",
    7: "chulio",
    8: "agosto",
    9: "setiembre",
    10: "octubre",
    11: "noviembre",
    12: "aviento"
}


def pronounce_number_an(number, **kwargs):
    return AN.pronounce_number(number, **kwargs)


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

    For example, generates 'luns, cinco de chunio de 2018'.

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
    nice = f"{day} de {nice_month_an(dt)} de {nice_year_an(dt)}"
    if now is not None:
        nice = day
        if dt.month != now.month:
            nice = nice + " de " + nice_month_an(dt)
        if dt.year != now.year:
            nice = nice + " de " + nice_year_an(dt)

    if include_weekday:
        weekday = nice_weekday_an(dt)
        nice = f"{weekday}, {nice}"
    return nice
