"""Modern Greek (el) date and time formatting and extraction.

Gender and case scope
----------------------
Greek inflects a handful of low numerals for grammatical gender and marks
month names for case. This module commits to the following consistent
conventions and stays inside them:

* Spoken **clock hours** agree with the feminine noun ``ώρα`` ("hour"), so
  the hours 1/3/4 use their feminine forms ``μία``/``τρεις``/``τέσσερις``
  (and the feminine teens/twenties in 24-hour mode). The leading article
  (``η``/``οι``) is intentionally omitted — "τρεις και μισή" rather than
  "οι τρεις και μισή" — which is idiomatic and sidesteps article agreement.
* Spoken **minutes**, **day-of-month** and **years** use the neuter cardinal
  emitted by ``pronounce_number_el`` (``ένα``/``τρία``/``τέσσερα``), the
  citation counting form.
* Month names are rendered in the **genitive** inside date phrases ("5
  Ιουνίου"), the case Greek uses when a day precedes the month, and in the
  **nominative** by :func:`nice_month_el`.

Modern Greek clock-telling has a single colloquial standard (the hour
followed by ``και``/``παρά`` with ``μισή``/``τέταρτο`` or a minute count);
there is no second legitimate register comparable to the Catalan "quarts"
system, so :func:`nice_time_el` exposes no register parameter. The
extraction side accepts every verifiable spoken variant: numerals spelled
out in words (routed through the number parser), the gendered hour forms
μία/τρεις/τέσσερις, and the ``και``/``παρά`` + ``μισή``/``τέταρτο`` idioms.

Copyright: OpenVoiceOS
"""
import unicodedata

from ovos_number_parser import numbers_to_digits
from ovos_number_parser.numbers_el import pronounce_number_el
from ovos_utils.time import now_local

from ovos_date_parser.duration import (
    register_duration_lexicon,
    DurationLexicon,
)

# 0=Monday .. 6=Sunday, matching datetime.weekday()
WEEKDAYS_EL = {
    0: "Δευτέρα",
    1: "Τρίτη",
    2: "Τετάρτη",
    3: "Πέμπτη",
    4: "Παρασκευή",
    5: "Σάββατο",
    6: "Κυριακή",
}

# nominative month names
MONTHS_EL = {
    1: "Ιανουάριος",
    2: "Φεβρουάριος",
    3: "Μάρτιος",
    4: "Απρίλιος",
    5: "Μάιος",
    6: "Ιούνιος",
    7: "Ιούλιος",
    8: "Αύγουστος",
    9: "Σεπτέμβριος",
    10: "Οκτώβριος",
    11: "Νοέμβριος",
    12: "Δεκέμβριος",
}

# genitive month names, used inside "<day> <month> <year>" phrases
MONTHS_GEN_EL = {
    1: "Ιανουαρίου",
    2: "Φεβρουαρίου",
    3: "Μαρτίου",
    4: "Απριλίου",
    5: "Μαΐου",
    6: "Ιουνίου",
    7: "Ιουλίου",
    8: "Αυγούστου",
    9: "Σεπτεμβρίου",
    10: "Οκτωβρίου",
    11: "Νοεμβρίου",
    12: "Δεκεμβρίου",
}

# feminine clock-hour forms (agree with "ώρα"); differ from the neuter
# cardinals only for 1, 3 and 4
_FEM_HOURS = {
    0: "δώδεκα", 1: "μία", 2: "δύο", 3: "τρεις", 4: "τέσσερις",
    5: "πέντε", 6: "έξι", 7: "επτά", 8: "οκτώ", 9: "εννέα",
    10: "δέκα", 11: "έντεκα", 12: "δώδεκα",
    13: "δεκατρείς", 14: "δεκατέσσερις", 15: "δεκαπέντε",
    16: "δεκαέξι", 17: "δεκαεπτά", 18: "δεκαοκτώ", 19: "δεκαεννέα",
    20: "είκοσι", 21: "είκοσι μία", 22: "είκοσι δύο", 23: "είκοσι τρεις",
}


def _fem_hour(hour):
    """Feminine spoken form of an hour value (0-23)."""
    return _FEM_HOURS.get(hour, pronounce_number_el(hour))


def _fold_el(text):
    """Lowercase Greek text, drop diacritics and normalize final sigma."""
    text = text.lower().replace("ς", "σ")
    decomposed = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in decomposed
                       if unicodedata.combining(c) == 0)
    return unicodedata.normalize("NFC", stripped)


def nice_year_el(dt, bc=False):
    """Format a year as a pronounceable string.

    For example, generates 'χίλια εννιακόσια ογδόντα τέσσερα' for 1984.

    Args:
        dt (datetime): date to format (assumed already in local timezone)
        bc (bool): append the "before Christ" marker
    Returns:
        (str): the formatted year
    """
    year = pronounce_number_el(dt.year)
    if bc:
        return f"{year} π.Χ."
    return year


def nice_weekday_el(dt):
    return WEEKDAYS_EL[dt.weekday()]


def nice_month_el(dt):
    return MONTHS_EL[dt.month]


def nice_day_el(dt, date_format='DMY', include_month=True):
    day = dt.strftime("%d").lstrip("0")
    if include_month:
        month = MONTHS_GEN_EL[dt.month]
        if date_format == 'MDY':
            return "{} {}".format(month, day)
        return "{} {}".format(day, month)
    return day


def nice_date_time_el(dt, now=None, use_24hour=False, use_ampm=False):
    """Format a date and time in a pronounceable way.

    For example, generates 'Τρίτη, πέντε Ιουνίου δύο χιλιάδες δεκαοκτώ στις
    πέντε και μισή'.

    Args:
        dt (datetime): date to format (assumed already in local timezone)
        now (datetime): reference date; when supplied the returned date is
            shortened (the year is dropped when it matches ``now``'s year,
            the month when it matches ``now``'s month, and same-day dates
            collapse to 'σήμερα').
        use_24hour (bool): output 24-hour format
        use_ampm (bool): include the part-of-day marker in 12-hour format
    Returns:
        (str): the formatted date and time
    """
    now = now or now_local()
    return (f"{nice_date_el(dt, now)} στις "
            f"{nice_time_el(dt, use_24hour=use_24hour, use_ampm=use_ampm)}")


def nice_date_el(dt, now=None, include_weekday=True):
    """Format a date in a pronounceable way.

    For example, generates 'Τρίτη, πέντε Ιουνίου δύο χιλιάδες δεκαοκτώ'.

    Args:
        dt (datetime): date to format (assumed already in local timezone)
        now (datetime): reference date; when supplied the returned date is
            shortened (the year is dropped when it matches ``now``'s year,
            the month when it matches ``now``'s month, and same-day dates
            collapse to 'σήμερα').
        include_weekday (bool): prepend the weekday name. Defaults to True.
    Returns:
        (str): the formatted date
    """
    day = pronounce_number_el(dt.day)
    if now is not None:
        nice = day
        if dt.day == now.day:
            return "σήμερα"
        if dt.day == now.day + 1:
            return "αύριο"
        if dt.day == now.day - 1:
            return "χθες"
        if dt.month != now.month:
            nice = nice + " " + MONTHS_GEN_EL[dt.month]
        if dt.year != now.year:
            nice = nice + " " + nice_year_el(dt)
    else:
        nice = f"{day} {MONTHS_GEN_EL[dt.month]} {nice_year_el(dt)}"

    if include_weekday:
        nice = f"{nice_weekday_el(dt)}, {nice}"
    return nice


def nice_time_el(dt, speech=True, use_24hour=False, use_ampm=False):
    """Format a time in a human understandable way.

    For example, generates 'πέντε και μισή' for speech or '5:30' for a
    text display.

    Args:
        dt (datetime): date to format (assumed already in local timezone)
        speech (bool): format for speech (True) or display (False)
        use_24hour (bool): output 24-hour format
        use_ampm (bool): include the part-of-day marker in 12-hour format
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
            string = string[1:]  # strip leading zero

    if not speech:
        return string

    speak = ""
    if use_24hour:
        speak += "μηδέν" if dt.hour == 0 else _fem_hour(dt.hour)
        if dt.minute < 10:
            speak += " και μηδέν " + pronounce_number_el(dt.minute)
        else:
            speak += " και " + pronounce_number_el(dt.minute)
        return speak

    # 12-hour spoken form
    if dt.minute >= 35:
        minute = dt.minute - 60
        hour = dt.hour + 1
    else:
        minute = dt.minute
        hour = dt.hour

    if hour == 0 or hour == 12 or hour == 24:
        speak += "δώδεκα"
    elif hour < 13:
        speak += _fem_hour(hour)
    else:
        speak += _fem_hour(hour - 12)

    if minute != 0:
        if minute == 15:
            speak += " και τέταρτο"
        elif minute == 30:
            speak += " και μισή"
        elif minute == -15:
            speak += " παρά τέταρτο"
        elif minute > 0:
            speak += " και " + pronounce_number_el(minute)
        else:
            speak += " παρά " + pronounce_number_el(-minute)
    elif not use_ampm:
        speak += " ακριβώς"

    if use_ampm:
        if 0 <= hour < 6:
            speak += " τα ξημερώματα"
        elif 6 <= hour < 12:
            speak += " το πρωί"
        elif 12 <= hour < 18:
            speak += " το απόγευμα"
        else:
            speak += " το βράδυ"
    return speak


# Greek number words are normalized to digits with accents folded, so the
# unit fragments below are written accent-free. Nouns take their plural
# nominative/accusative forms after a numeral.
register_duration_lexicon(DurationLexicon(
    lang="el",
    normalize=lambda text: numbers_to_digits(_fold_el(text), "el"),
    units={
        "microseconds": r"μικροδευτερολεπτ[οα]",
        "milliseconds": r"μιλιδευτερολεπτ[οα]|χιλιοστοδευτερολεπτ[οα]",
        "seconds": r"δευτερολεπτ[οα]",
        "minutes": r"λεπτ[οα]",
        "hours": r"ωρ[αεσ]+",
        "days": r"(?:η?μερ[αεσ]+)",
        "weeks": r"εβδομαδ[αεσ]+",
        "months": r"μην[αεσ]+|μηνασ",
        "years": r"χρον(?:ια|οσ|ο)|ετ(?:οσ|η)",
        "decades": r"δεκαετι[αεσ]+",
        "centuries": r"αιων[αεσ]+",
        "millenniums": r"χιλιετι[αεσ]+",
    }))
