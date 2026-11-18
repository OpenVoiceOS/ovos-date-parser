"""Estonian date and time parsing and formatting.

Estonian, like Finnish, is agglutinative and case-rich: numerals below a
hundred that are not round agglutinate ("kaksteist" = 12, "kakskümmend" = 20)
and the noun after a numeral greater than one takes the partitive singular
("kaks tundi", "viis minutit"). The spoken clock keeps the "kell" marker
("kell kaksteist") and the year is read as a plain cardinal number.

References:
    * Eesti Keele Instituut (EKI), Eesti keele käsiraamat,
      "Arvsõnad" and kellaaja/kuupäeva usage
    * https://et.wikipedia.org/wiki/Kellaaeg
"""

from ovos_number_parser.numbers_et import pronounce_number_et


# ---------------------------------------------------------------------------
# formatting
# ---------------------------------------------------------------------------

_PART_OF_DAY_ET = (
    (5, 11, "hommikul"),   # morning
    (12, 17, "päeval"),    # daytime
    (18, 22, "õhtul"),     # evening
)


def _part_of_day_et(hour):
    for start, end, word in _PART_OF_DAY_ET:
        if start <= hour <= end:
            return word
    return "öösel"  # night, 23..4


def nice_year_et(dt, bc=False):
    """Speak a year as an Estonian cardinal number.

    Estonian reads years as whole cardinals ("tuhat üheksasada
    kaheksakümmend neli" for 1984), not as decade pairs.
    """
    year = pronounce_number_et(dt.year)
    if bc:
        return year + " enne Kristust"
    return year


def _speak_minutes_et(minute):
    if minute < 10:
        return " null " + pronounce_number_et(minute)
    return " " + pronounce_number_et(minute)


def nice_time_et(dt, speech=True, use_24hour=False, use_ampm=False):
    """Format a time in a natural Estonian way.

    For example, generate "kell viisteist kolmkümmend" for 15:30.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default) or display (False)
        use_24hour (bool): output in 24-hour format
        use_ampm (bool): include a part-of-day adverb for 12-hour format
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
        if string[0] == "0":
            string = string[1:]

    if not speech:
        return string

    if use_24hour:
        speak = "kell " + pronounce_number_et(dt.hour)
        if dt.minute:
            speak += _speak_minutes_et(dt.minute)
        return speak

    if dt.hour == 0 and dt.minute == 0:
        return "kesköö"
    if dt.hour == 12 and dt.minute == 0:
        return "keskpäev"

    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    speak = "kell " + pronounce_number_et(hour)
    if dt.minute:
        speak += _speak_minutes_et(dt.minute)
    if use_ampm:
        speak += " " + _part_of_day_et(dt.hour)
    return speak


# ---------------------------------------------------------------------------
# duration
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# datetime extraction
# ---------------------------------------------------------------------------
