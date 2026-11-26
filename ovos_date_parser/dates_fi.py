"""Finnish date and time formatting.

Finnish is agglutinative and heavily inflected: numerals concatenate
("kaksikymmentäyksi" = 21) and the noun that follows a numeral greater than
one stands in the partitive singular ("kaksi tuntia", "viisi minuuttia").
The spoken clock keeps the "kello" marker ("kello kaksitoista") and reads
the year as a plain cardinal number rather than in decade pairs.

References:
    * Kotimaisten kielten keskus (Kotus), Kielitoimiston ohjepankki,
      "Kellonajat" and "Päivämäärät"
    * https://fi.wikipedia.org/wiki/Kellonaika
"""

from ovos_number_parser.numbers_fi import pronounce_number_fi


# ---------------------------------------------------------------------------
# formatting
# ---------------------------------------------------------------------------

# part-of-day adverbs (adessive/essive) used with the 12h clock
_PART_OF_DAY_FI = (
    (5, 11, "aamulla"),      # morning
    (12, 17, "päivällä"),    # daytime
    (18, 22, "illalla"),     # evening
)


def _part_of_day_fi(hour):
    for start, end, word in _PART_OF_DAY_FI:
        if start <= hour <= end:
            return word
    return "yöllä"  # night, 23..4


def nice_year_fi(dt, bc=False):
    """Speak a year as a Finnish cardinal number.

    Finnish reads years as whole cardinals ("tuhat yhdeksänsataa-
    kahdeksankymmentäneljä" for 1984), not as decade pairs.
    """
    year = pronounce_number_fi(dt.year)
    if bc:
        return year + " ennen Kristusta"
    return year


def _speak_minutes_fi(minute):
    # single-digit minutes are read with a leading "nolla" (09:05)
    if minute < 10:
        return " nolla " + pronounce_number_fi(minute)
    return " " + pronounce_number_fi(minute)


def nice_time_fi(dt, speech=True, use_24hour=False, use_ampm=False):
    """Format a time in a natural Finnish way.

    For example, generate "kello viisitoista kolmekymmentä" for 15:30.

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
            string = string[1:]  # strip leading zero

    if not speech:
        return string

    if use_24hour:
        speak = "kello " + pronounce_number_fi(dt.hour)
        if dt.minute:
            speak += _speak_minutes_fi(dt.minute)
        return speak

    if dt.hour == 0 and dt.minute == 0:
        return "keskiyö"
    if dt.hour == 12 and dt.minute == 0:
        return "keskipäivä"

    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    speak = "kello " + pronounce_number_fi(hour)
    if dt.minute:
        speak += _speak_minutes_fi(dt.minute)
    if use_ampm:
        speak += " " + _part_of_day_fi(dt.hour)
    return speak


# ---------------------------------------------------------------------------
# duration
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# datetime extraction
# ---------------------------------------------------------------------------
