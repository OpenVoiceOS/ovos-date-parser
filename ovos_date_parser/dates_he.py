# Copyright OpenVoiceOS
"""Hebrew date and time formatting and extraction.

Grammatical gender scope
------------------------
Hebrew cardinal numerals are gendered. This module fixes one consistent
convention per grammatical context:

* Years and day-of-month counts are rendered with masculine cardinals,
  the form produced by ``pronounce_number_he``. This matches how a
  numeric year or calendar day is read aloud.
* Clock hours and whole-minute counts are rendered with feminine
  cardinals, because the counted noun "שעה" (hour) is feminine and
  Hebrew tells the time in the feminine. A small feminine numeral table
  (0-59) is built from the standard cardinal paradigm for this purpose.

Time-telling register
---------------------
Modern Hebrew tells the clock one way: feminine hour cardinals with the
half/quarter idioms (שלוש וחצי, רבע לארבע). There is no second colloquial
register comparable to Catalan "quarts", so no register parameter is
offered; ``nice_time_he`` keeps this single sensible default.

Extraction scope
----------------
``extract_datetime_he`` recognises relative day words, weekday names
(with or without a ב/ל proclitic), "in N <unit>" / "N <unit> ago"
offsets in both masculine and feminine spoken forms (routed through the
number normaliser), the dual nouns יומיים/שבועיים/חודשיים/שנתיים/שעתיים,
relative hour/minute/second offsets (בעוד N שעות/דקות) including "וחצי"
/"ורבע" fractions of an hour, explicit "N of <month> [year]" dates (a
month with a year but no day resolves to the first of the month), and
clock times given as ``HH:MM``, "בשעה N", or "רבע ל<hour>". A part-of-day
word (בבוקר/אחר הצהריים/בערב/בלילה) shifts a spoken or absolute hour into
the right half of the day. Spoken minute compounds beyond half and
quarter are out of scope: an unrecognised time is left in the returned
remainder rather than guessed at.
"""
from datetime import datetime

from ovos_number_parser import numbers_to_digits
from ovos_number_parser.numbers_he import pronounce_number_he
from ovos_utils.time import now_local

from ovos_date_parser.duration import (
    register_duration_lexicon,
    DurationLexicon,
)

# Python weekday(): 0=Monday .. 6=Sunday
WEEKDAYS_HE = {
    0: "יום שני",
    1: "יום שלישי",
    2: "יום רביעי",
    3: "יום חמישי",
    4: "יום שישי",
    5: "שבת",
    6: "יום ראשון",
}
MONTHS_HE = {
    1: "ינואר",
    2: "פברואר",
    3: "מרץ",
    4: "אפריל",
    5: "מאי",
    6: "יוני",
    7: "יולי",
    8: "אוגוסט",
    9: "ספטמבר",
    10: "אוקטובר",
    11: "נובמבר",
    12: "דצמבר",
}

# feminine cardinal paradigm, used for clock counting
_FEM_ONES = {
    0: "אפס",
    1: "אחת",
    2: "שתיים",
    3: "שלוש",
    4: "ארבע",
    5: "חמש",
    6: "שש",
    7: "שבע",
    8: "שמונה",
    9: "תשע",
    10: "עשר",
}
_FEM_TEEN = {
    11: "אחת עשרה",
    12: "שתים עשרה",
    13: "שלוש עשרה",
    14: "ארבע עשרה",
    15: "חמש עשרה",
    16: "שש עשרה",
    17: "שבע עשרה",
    18: "שמונה עשרה",
    19: "תשע עשרה",
}
# tens are gender neutral in Hebrew
_TENS = {
    20: "עשרים",
    30: "שלושים",
    40: "ארבעים",
    50: "חמישים",
}


def _feminine_number_he(n):
    """Feminine cardinal for 0-59, used to count hours and minutes."""
    if n < 0 or n > 59:
        raise ValueError("feminine clock numeral out of range")
    if n <= 10:
        return _FEM_ONES[n]
    if n < 20:
        return _FEM_TEEN[n]
    tens = (n // 10) * 10
    unit = n % 10
    if unit == 0:
        return _TENS[tens]
    return _TENS[tens] + " ו" + _FEM_ONES[unit]


def nice_year_he(dt, bc=False):
    """Format a year as spoken Hebrew (masculine cardinals).

    Produces e.g. 'אלף תשע מאות שמונים וארבעה' for 1984.

    Args:
        dt (datetime): date to format (assumed already in local time)
        bc (bool): append the "before common era" marker
    Returns:
        (str): the formatted year
    """
    # Hebrew date fields keep the masculine forms this formatter has always
    # produced; the number parser now defaults to the feminine abstract
    # counting form, so the gender is requested explicitly here. Whether a
    # year (שנה, feminine) or day-of-month should instead be feminine is a
    # separate Hebrew-dates question, deliberately not changed here.
    year = pronounce_number_he(dt.year, feminine=False)
    if bc:
        return f"{year} לפני הספירה"
    return year


def nice_weekday_he(dt):
    return WEEKDAYS_HE[dt.weekday()]


def nice_month_he(dt):
    return MONTHS_HE[dt.month]


def nice_day_he(dt, date_format='DMY', include_month=True):
    if include_month:
        month = nice_month_he(dt)
        if date_format == 'MDY':
            return "{} {}".format(month, dt.strftime("%d").lstrip("0"))
        else:
            return "{} {}".format(dt.strftime("%d").lstrip("0"), month)
    return dt.strftime("%d").lstrip("0")


def nice_date_he(dt: datetime, now: datetime = None, include_weekday=True):
    """Format a date as spoken Hebrew.

    Produces e.g. 'יום שלישי, חמישה ביוני 2018'.

    Args:
        dt (datetime): date to format (assumed already in local time)
        now (datetime): reference date. When given, the result is
            shortened: the year is dropped when it matches ``now``, the
            month is dropped when it matches ``now``, and same-day dates
            return 'היום' / 'מחר' / 'אתמול'.
        include_weekday (bool): prepend the weekday name.
    Returns:
        (str): the formatted date
    """
    day = pronounce_number_he(dt.day, feminine=False)
    if now is not None:
        if dt.year == now.year and dt.month == now.month:
            if dt.day == now.day:
                return "היום"
            if dt.day == now.day + 1:
                return "מחר"
            if dt.day == now.day - 1:
                return "אתמול"
        nice = day
        if dt.month != now.month or dt.year != now.year:
            nice = nice + " ב" + nice_month_he(dt)
        if dt.year != now.year:
            nice = nice + " " + nice_year_he(dt)
    else:
        nice = f"{day} ב{nice_month_he(dt)} {nice_year_he(dt)}"

    if include_weekday:
        nice = f"{nice_weekday_he(dt)}, {nice}"
    return nice


def nice_date_time_he(dt, now=None, use_24hour=False, use_ampm=False):
    """Format a date and time as spoken Hebrew.

    Produces e.g. 'יום שלישי, חמישה ביוני 2018 בשעה חמש וחצי'.
    """
    now = now or now_local()
    date_str = nice_date_he(dt, now)
    time_str = nice_time_he(dt, use_24hour=use_24hour, use_ampm=use_ampm)
    return f"{date_str} בשעה {time_str}"


def nice_time_he(dt, speech=True, use_24hour=False, use_ampm=False):
    """Format a time in a human friendly way.

    Produces e.g. 'שלוש וחצי' for speech or '3:30' for display.

    Args:
        dt (datetime): date to format (assumed already in local time)
        speech (bool): spoken form (True) or display form (False)
        use_24hour (bool): 24 hour output instead of 12 hour
        use_ampm (bool): add a part-of-day marker in 12 hour output
    Returns:
        (str): the formatted time
    """
    if use_24hour:
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            string = dt.strftime("%I:%M %p")
        else:
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]

    if not speech:
        return string

    if use_24hour:
        speak = _feminine_number_he(dt.hour)
        if dt.minute > 0:
            if dt.minute < 10:
                speak += " אפס " + _feminine_number_he(dt.minute)
            else:
                speak += " " + _feminine_number_he(dt.minute)
        return speak

    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    speak = _feminine_number_he(hour)

    minute = dt.minute
    if minute == 15:
        speak += " ורבע"
    elif minute == 30:
        speak += " וחצי"
    elif minute == 45:
        nxt = (hour % 12) + 1
        speak = "רבע ל" + _feminine_number_he(nxt)
    elif minute != 0:
        speak += " ו" + _feminine_number_he(minute)

    if use_ampm:
        if dt.hour < 5:
            speak += " בלילה"
        elif dt.hour < 12:
            speak += " בבוקר"
        elif dt.hour < 18:
            speak += " אחר הצהריים"
        else:
            speak += " בערב"
    return speak


register_duration_lexicon(DurationLexicon(
    lang="he",
    normalize=lambda text: numbers_to_digits(text, "he"),
    joiner=r"(?:\s+|-)",
    units={
        "microseconds": r"מיקרו[ ]?שני[ה]?|מיקרו[ ]?שניות",
        "milliseconds": r"מילי[ ]?שני[ה]?|מילי[ ]?שניות|אלפית[ ]?השנייה",
        "seconds": r"שנייה|שני[ה]?|שניות",
        "minutes": r"דקה|דקות",
        "hours": r"שעה|שעות|שעתיים",
        "days": r"יום|ימים|יומיים",
        "weeks": r"שבוע|שבועות|שבועיים",
        "months": r"חודש|חודשים|חודשיים",
        "years": r"שנה|שנים|שנתיים",
        "decades": r"עשור|עשורים",
        "centuries": r"מאה|מאות",
        "millenniums": r"אלף שנה|אלפי שנים|מילניום",
    }))
