"""Occitan date and time formatting.

Classical orthography (norma classica), Lengadocian referential variety.

Sources:
- Lo Congrès permanent de la lenga occitana (dicod'Òc, dicodoc.eu)
- the Occitan date-fns locale authored by a native speaker
  (github.com/date-fns/date-fns, src/locale/oc)
- attested time expressions: "una ora un quart", "una ora e mièja",
  "doas oras manca un quart" (histo.cat, "Català i occità, diferents en
  13 punts"); day words uèi/deman/ièr, miègjorn/mièjanuèch
  (occitan-foss.blogspot.com, wordsrus.info/oci)
"""
from datetime import datetime

from ovos_number_parser.numbers_oc import OC
from ovos_number_parser.util import GrammaticalGender

WEEKDAYS_OC = {
    0: "diluns",
    1: "dimars",
    2: "dimècres",
    3: "dijòus",
    4: "divendres",
    5: "dissabte",
    6: "dimenge"
}
MONTHS_OC = {
    1: "genièr",
    2: "febrièr",
    3: "març",
    4: "abril",
    5: "mai",
    6: "junh",
    7: "julhet",
    8: "agost",
    9: "setembre",
    10: "octòbre",
    11: "novembre",
    12: "decembre"
}


def _pronounce_oc(number, feminine=False):
    gender = GrammaticalGender.FEMININE if feminine \
        else GrammaticalGender.MASCULINE
    return OC.pronounce_number(number, gender=gender)


def nice_year_oc(dt, bc=False):
    """Format a year into a pronounceable form, e.g. 'dos mila vint e tres'."""
    # no "e" directly after "mila": "dos mila vint e tres", but
    # "mila cent e cinc" keeps its "e" (only hundreds join it)
    year = _pronounce_oc(dt.year).replace("mila e ", "mila ", 1)
    if bc:
        return f"{year} a.C."
    return year


def nice_weekday_oc(dt):
    weekday = WEEKDAYS_OC[dt.weekday()]
    return weekday.capitalize()


def nice_month_oc(dt):
    month = MONTHS_OC[dt.month]
    return month.capitalize()


def nice_day_oc(dt, date_format='DMY', include_month=True):
    if include_month:
        month = nice_month_oc(dt)
        if date_format == 'MDY':
            return "{} {}".format(month, dt.strftime("%d").lstrip("0"))
        else:
            return "{} {}".format(dt.strftime("%d").lstrip("0"), month)
    return dt.strftime("%d").lstrip("0")


def nice_date_time_oc(dt, now=None, use_24hour=False, use_ampm=False):
    """Format a date and time in a pronounceable way,
    e.g. 'dimars, cinc de junh de 2018 a las cinc e mièja'."""
    now = now or None
    return f"{nice_date_oc(dt, now)} a las {nice_time_oc(dt, use_24hour=use_24hour, use_ampm=use_ampm)}"


def nice_date_oc(dt: datetime, now: datetime = None, include_weekday=True):
    """Format a date in a pronounceable way,
    e.g. 'dimars, cinc de junh de dos mila dètz-e-uèch'."""
    day = _pronounce_oc(dt.day)
    # months are lowercase in running text; vowel-initial months take "d'"
    # (abril, agost, octòbre), as in Catalan
    month = MONTHS_OC[dt.month]
    month_part = "d'" + month if month[0] in "aeiou" else "de " + month
    if now is not None:
        nice = day
        if dt.day == now.day:
            return "uèi"
        if dt.day == now.day + 1:
            return "deman"
        if dt.day == now.day - 1:
            return "ièr"
        if dt.month != now.month or dt.year != now.year:
            nice = nice + " " + month_part
        if dt.year != now.year:
            nice = nice + " de " + nice_year_oc(dt)
    else:
        nice = f"{day} {month_part} de {nice_year_oc(dt)}"

    if include_weekday:
        weekday = nice_weekday_oc(dt)
        nice = f"{weekday}, {nice}"
    return nice


def nice_time_oc(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time into a human-comprehensible form.

    For example, generates 'cinc oras e mièja' for speech or '5:30' for
    text display. The quarter-to reading names the next hour:
    'doas oras manca un quart' for 1:45.
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
            string = string[1:]  # strip leading zero

    if not speech:
        return string

    def spoken_hour(hour):
        if hour == 1:
            return "una ora"
        return _pronounce_oc(hour, feminine=True) + " oras"

    speak = ""
    if use_24hour:
        if dt.hour == 0:
            speak += "mièjanuèch"
        elif dt.hour == 12:
            speak += "miègjorn"
        else:
            speak += spoken_hour(dt.hour)
        if dt.hour in (0, 12):
            # noon and midnight take the half-hour idiom, not digit minutes
            if dt.minute == 30:
                speak += " e mièg"
            elif dt.minute != 0:
                speak += " e " + _pronounce_oc(dt.minute)
        elif dt.minute < 10:
            speak += " zèro " + _pronounce_oc(dt.minute)
        else:
            speak += " " + _pronounce_oc(dt.minute)

    else:
        if dt.minute == 45:
            minute = -15
            hour = dt.hour + 1
        else:
            minute = dt.minute
            hour = dt.hour

        if hour == 0 or hour == 24:
            speak += "mièjanuèch"
        elif hour == 12:
            speak += "miègjorn"
        elif hour < 13:
            speak += spoken_hour(hour)
        else:
            speak += spoken_hour(hour - 12)

        if minute != 0:
            if minute == 15:
                speak += " e quart"
            elif minute == 30:
                # "mièjanuèch/miègjorn e mièg", but "cinc oras e mièja"
                speak += " e mièg" if hour in (0, 12) else " e mièja"
            elif minute == -15:
                speak += " manca un quart"
            else:
                speak += " e " + _pronounce_oc(minute)

        if use_ampm:
            if dt.hour == 0 or dt.hour == 12:
                pass  # mièjanuèch / miègjorn need no qualifier
            elif dt.hour < 13:
                speak += " del matin"
            elif dt.hour < 19:
                speak += " de l'aprèp-miègjorn"
            elif dt.hour < 22:
                speak += " del ser"
            else:
                speak += " de la nuèch"
    return speak
