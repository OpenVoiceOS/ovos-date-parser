from datetime import datetime

from ovos_number_parser.numbers_ro import RO
from ovos_number_parser.util import GrammaticalGender
from ovos_utils.time import now_local


WEEKDAYS_RO = {
    0: "luni",
    1: "marți",
    2: "miercuri",
    3: "joi",
    4: "vineri",
    5: "sâmbătă",
    6: "duminică",
}
MONTHS_RO = {
    1: "ianuarie",
    2: "februarie",
    3: "martie",
    4: "aprilie",
    5: "mai",
    6: "iunie",
    7: "iulie",
    8: "august",
    9: "septembrie",
    10: "octombrie",
    11: "noiembrie",
    12: "decembrie",
}

# spoken number phrases -> digits, longest first so compounds win
# ("douăzeci și unu" before "douăzeci")
_NUM_WORDS = {}
for _n in range(1, 60):
    _NUM_WORDS[RO.pronounce_number(_n)] = _n
    _NUM_WORDS[RO.pronounce_number(_n, gender=GrammaticalGender.FEMININE)] = _n


def _spoken_hour_ro(hour: int) -> str:
    """Hours are counted with feminine numerals ("ora două",
    "ora douăsprezece") except for "unu" ("ora unu", "ora douăzeci și unu").
    """
    word = RO.pronounce_number(hour, gender=GrammaticalGender.FEMININE)
    if word == "una":
        return "unu"
    if word.endswith(" una"):
        return word[:-4] + " unu"
    return word


def nice_year_ro(dt, bc=False):
    """Format a year into a pronounceable Romanian form.

    Years are read as full numbers: 1984 is
    "o mie nouă sute optzeci și patru".
    """
    year = RO.pronounce_number(dt.year)
    if bc:
        return f"{year} î.Hr."
    return year


def nice_weekday_ro(dt):
    weekday = WEEKDAYS_RO[dt.weekday()]
    return weekday.capitalize()


def nice_month_ro(dt):
    month = MONTHS_RO[dt.month]
    return month.capitalize()


def _nice_day_of_month_ro(day: int) -> str:
    # the first of the month is "întâi" ("întâi mai"), other days
    # are read as cardinals
    if day == 1:
        return "întâi"
    return RO.pronounce_number(day)


def nice_day_ro(dt, date_format='DMY', include_month=True):
    if include_month:
        month = nice_month_ro(dt)
        if date_format == 'MDY':
            return "{} {}".format(month, dt.strftime("%d").lstrip("0"))
        else:
            return "{} {}".format(dt.strftime("%d").lstrip("0"), month)
    return dt.strftime("%d").lstrip("0")


def nice_date_time_ro(dt, now=None, use_24hour=False, use_ampm=False):
    """Format a date and time in a pronounceable way, for example
    "marți, cinci iunie, două mii optsprezece la ora cinci și jumătate".
    """
    now = now or now_local()
    return f"{nice_date_ro(dt, now)} la ora " \
           f"{nice_time_ro(dt, use_24hour=use_24hour, use_ampm=use_ampm)}"


def nice_date_ro(dt: datetime, now: datetime = None, include_weekday=True):
    """Format a date in a pronounceable way, for example
    "marți, cinci iunie, două mii optsprezece".
    """
    day = _nice_day_of_month_ro(dt.day)
    if now is not None:
        nice = day
        if dt.day == now.day and dt.month == now.month and dt.year == now.year:
            return "azi"
        if (dt.date() - now.date()).days == 1:
            return "mâine"
        if (dt.date() - now.date()).days == -1:
            return "ieri"
        if dt.month != now.month or dt.year != now.year:
            nice = nice + " " + nice_month_ro(dt).lower()
        if dt.year != now.year:
            nice = nice + ", " + nice_year_ro(dt)
    else:
        nice = f"{day} {nice_month_ro(dt).lower()}, {nice_year_ro(dt)}"

    if include_weekday:
        weekday = nice_weekday_ro(dt)
        nice = f"{weekday}, {nice}"
    return nice


def nice_time_ro(dt, speech=True, use_24hour=False, use_ampm=False):
    """Format a time in a human readable Romanian form.

    For example, "opt și jumătate" for 8:30, "nouă fără un sfert"
    for 8:45, "opt fix" for 8:00.
    """
    if use_24hour:
        # e.g. "03:01" or "14:22"
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            # e.g. "3:01 AM" or "2:22 PM"
            string = dt.strftime("%I:%M %p")
        else:
            # e.g. "3:01" or "2:22"
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # strip leading zeros

    if not speech:
        return string

    speak = ""
    if use_24hour:
        speak = _spoken_hour_ro(dt.hour) if dt.hour else "zero"
        if dt.minute == 0:
            speak += " fix"
        elif dt.minute < 10:
            speak += " zero " + RO.pronounce_number(
                dt.minute, gender=GrammaticalGender.FEMININE)
        else:
            speak += " " + RO.pronounce_number(
                dt.minute, gender=GrammaticalGender.FEMININE)
    else:
        # quarter-to and minutes-to forms use "fără" against the next hour
        if dt.minute in (35, 40, 45, 50, 55):
            minute = dt.minute - 60
            hour = dt.hour + 1
        else:
            minute = dt.minute
            hour = dt.hour

        hour12 = hour % 12 or 12
        speak = _spoken_hour_ro(hour12)

        if minute != 0:
            if minute == 15:
                speak += " și un sfert"
            elif minute == 30:
                speak += " și jumătate"
            elif minute == -15:
                speak += " fără un sfert"
            elif minute > 0:
                speak += " și " + RO.pronounce_number(
                    minute, gender=GrammaticalGender.FEMININE)
            else:
                speak += " fără " + RO.pronounce_number(
                    -minute, gender=GrammaticalGender.FEMININE)

        if minute == 0 and not use_ampm:
            speak += " fix"

        if use_ampm:
            if hour < 6 or hour >= 22:
                speak += " noaptea"
            elif hour < 12:
                speak += " dimineața"
            elif hour < 18:
                speak += " după-amiaza"
            else:
                speak += " seara"
    return speak
