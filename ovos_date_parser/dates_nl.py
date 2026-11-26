"""Date and time tools for Dutch.

Sources for the rules of the spoken date, time and year in this module:

Year. Taaladvies.net, "Uitspraak 2020: twintig twintig / tweeduizend twintig"
(https://taaladvies.net/uitspraak-2020-twintig-twintig-of-tweeduizend-twintig/):
"Jaartallen uit de twaalfde tot en met de twintigste eeuw worden vrijwel
altijd uitgesproken als een honderdtal: 1250 als 'twaalfhonderdvijftig', 1694
als 'zestienhonderdvierennegentig', 1914 als 'negentienhonderdveertien'";
"Jaartallen in de eenentwintigste eeuw worden door de meeste mensen met
'tweeduizend' uitgesproken: 2001 ('tweeduizend (en) een'), 2012 ('tweeduizend
(en) twaalf'), 2020 ('tweeduizend twintig')". Taaladvies.net, "Jaartallen
voluit" (https://taaladvies.net/jaartallen-voluit/): "Jaartallen volgen
dezelfde regels voor aaneenschrijven als gewone telwoorden", "negentienhonderd
drieënnegentig", and "Na het woord duizend komt er een spatie", with the
year "tweeduizend (en) vijf". Onze Taal, "Hoe
spreek je het jaartal 2026 uit?" (https://onzetaal.nl/taalloket/
hoe-spreek-je-jaartal-uit): "Het gebruikelijkst is om 2026 uit te spreken als
'tweeduizend zesentwintig'" and "tweeduizend één". The 1 inside a year takes no accent, as in
ovos-number-parser: Taaladvies.net, "Klemtoonteken (algemeen)"
(https://taaladvies.net/klemtoonteken-algemeen/) asks for an accent only where
a misreading threatens, and Taaladvies writes "tweeduizend (en) een". The
reading is the full
form, "negentienhonderdveertig", not the shortened "negentien-veertig". A year
below 1100 and from 2000 on reads as a cardinal of the number writer of
ovos-number-parser, with the space after "duizend": "duizend zesenzestig",
"tweeduizend drieëntwintig".

Date. Onze Taal, "Datumnotatie" (https://onzetaal.nl/taalloket/datumnotatie):
the date is written "1 mei 2025", "9 november 1989", "25 december 2023", with
the month name in full, which "sluit aan bij de manier waarop je de datum
meestal uitspreekt"; Taaladvies.net, "Datumnotatie"
(https://taaladvies.net/datumnotatie/): "de naam van de maand wordt met kleine
letters voluit geschreven". So the order is day, month, year, with no word
between them ("vijfentwintig december tweeduizend drieëntwintig"). The day
words are those of res/nl/date_time.json, the table that nice_date reads,
which spells every day as a cardinal and day 1 as "één". No fetched source
states how a date is spoken; the cardinal day follows that table.

Clock. Taaladvies.net, "Kloktijden: acht uur zeventien / zeventien over acht /
dertien voor halfnegen"
(https://taaladvies.net/kloktijden-acht-uur-zeventien-of-zeventien-over-acht-of-dertien-voor-halfnegen/):
"Het is ook mogelijk om de tijd te lezen zoals die op een digitale klok wordt
weergegeven: 8.17 uur wordt dan gelezen als 'acht uur zeventien' en 16.50 uur
als 'zestien uur vijftig'. Dit is gebruikelijk bij het aflezen van een
dienstregeling." So the "digits" style is the 24-hour reading "hour uur
minute". Onze Taal, "Tijden noteren" (https://onzetaal.nl/taalloket/
tijden-noteren): "12 uur, 14 uur, 18 uur" for whole hours.
The same page for the conversational reading: "Als het uur in vieren gedeeld
wordt, lezen we bijvoorbeeld alles tussen 8 uur en 8.15 uur met over acht,
alles tussen 8.15 uur en 8.30 uur met voor halfnegen, alles tussen 8.30 uur en
8.45 uur met over halfnegen en alles tussen 8.45 uur en 9 uur met voor negen",
with the examples "zeven over acht" (8.07), "dertien voor halfnegen" (8.17),
"tien voor halfnegen" (8.20), "acht over halfnegen" (8.38), "tien over
halfnegen" (8.40), "elf voor negen" (8.49), "acht voor negen" (8.52). These
readings count the hour from 1 to 12, so the "phrase" style needs the 12-hour
clock. "Halfnegen" is one word, as in "halfacht" of the Woordenlijst
Nederlandse Taal (Dutch Wiktionary, "halfacht": "staat in de Woordenlijst
Nederlandse Taal"). Taaladvies.net, "Half zes / halfzes"
(https://taaladvies.net/half-zes-of-halfzes/): "Beide spellingen zijn
correct", so "half acht" is as valid; this module writes the one-word form.
"Kwart over" (:15): Taaladvies.net, "Na / over (tien - drie)"
(https://taaladvies.net/tien-na-of-over-drie/): "Het voorzetsel over wordt in
de standaardtaal gebruikt om een precieze kloktijd aan te geven: tien over
drie, kwart over vier, twee minuten over halfzes"; the page says "over" is
standard in the whole language area, so nl-BE shares the reading. "Kwart
voor" (:45): no fetched source writes it. It follows from the division
above ("alles tussen 8.45 uur en 9 uur met voor negen") and from nice_time_nl
of this package, which gives it for the quarter point.
No unit-word clock and no seconds: no source gives a reading with the nouns
"minuten" and "seconden" for a clock time, so those styles raise
UnsupportedForm.

Day periods in 12-hour speech. Unicode CLDR 49, supplemental dayPeriods.xml,
the rules for "nl": midnight at 00:00, night1 from 00:00 before 06:00,
morning1 from 06:00 before 12:00, afternoon1 from 12:00 before 18:00,
evening1 from 18:00 before 24:00. The format names in nl.xml, as Babel 2.18
resolves them: "middernacht", "’s nachts", "’s ochtends", "’s middags",
"’s avonds" (CLDR writes the apostrophe as U+2019; this module writes the
ASCII apostrophe, like nice_part_of_day_nl). Noon has no name in nl.xml, so
12:00 reads "twaalf uur 's middags".
"""
import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from ovos_number_parser.numbers_nl import pronounce_number_nl


@lru_cache(maxsize=None)
def _date_names_nl():
    """The day, month and weekday names of res/nl/date_time.json, the table
    that nice_date reads: (days, months, weekdays by number, 0 = Monday)."""
    path = Path(__file__).parent / "res" / "nl" / "date_time.json"
    config = json.loads(path.read_text(encoding="utf8"))
    return tuple({int(number): name for number, name in config[key].items()}
                 for key in ("date", "month", "weekday"))


def spoken_year_nl(year: int) -> str:
    """A year as a cardinal, with the hundreds before 2000 and a space after
    "duizend": "negentienhonderdveertig", "tweeduizend zes"."""
    if 1100 <= year < 2000:
        rest = year % 100
        tail = "" if not rest else "een" if rest == 1 \
            else pronounce_number_nl(rest)
        return pronounce_number_nl(year // 100) + "honderd" + tail
    if year < 1000:
        return pronounce_number_nl(year)
    thousands, rest = year - year % 1000, year % 1000
    head = pronounce_number_nl(thousands)
    if not rest:
        return head
    return f"{head} {'een' if rest == 1 else pronounce_number_nl(rest)}"


def spoken_date_nl(day: Optional[int], month: Optional[int],
                   year: Optional[int], weekday: Optional[int] = None) -> str:
    """The fields of a date that are given, with no word between them:
    "vijfentwintig december tweeduizend drieëntwintig"."""
    days, months, weekdays = _date_names_nl()
    words = []
    if weekday is not None:
        words.append(weekdays[weekday])
    if day is not None:
        words.append(days[day])
    if month is not None:
        words.append(months[month])
    if year is not None:
        words.append(spoken_year_nl(year))
    return " ".join(words)


def _day_period_nl(hour: int) -> str:
    """The CLDR day period of an hour (see the module docstring)."""
    if hour < 6:
        return "'s nachts"
    if hour < 12:
        return "'s ochtends"
    if hour < 18:
        return "'s middags"
    return "'s avonds"


def spoken_time_nl(hour: int, minute: int, second: Optional[int] = None,
                   clock: str = "24h", style: str = "digits",
                   period: bool = False) -> Optional[str]:
    """A clock time in one style, or None for a style with no reading.

    digits: the digital clock, "zestien uur vijftig", and "veertien uur" on
        the hour.
    units: no reading.
    phrase: the 12-hour conversational reading, "tien voor halfacht".
    """
    if style == "units" or second is not None:
        return None
    if period and clock == "12h" and hour == 0 and minute == 0:
        return "middernacht"
    shown = hour if clock == "24h" else hour % 12 or 12
    if style == "phrase":
        if clock != "12h":
            return None
        now = pronounce_number_nl(shown)
        following = pronounce_number_nl(shown % 12 + 1)
        # inside the compound "halfeen" the "een" has no accent
        half = "half" + ("een" if following == "één" else following)
        if minute == 0:
            speak = f"{now} uur"
        elif minute < 15:
            speak = f"{pronounce_number_nl(minute)} over {now}"
        elif minute == 15:
            speak = f"kwart over {now}"
        elif minute < 30:
            speak = f"{pronounce_number_nl(30 - minute)} voor {half}"
        elif minute == 30:
            speak = half
        elif minute < 45:
            speak = f"{pronounce_number_nl(minute - 30)} over {half}"
        elif minute == 45:
            speak = f"kwart voor {following}"
        else:
            speak = f"{pronounce_number_nl(60 - minute)} voor {following}"
    else:
        speak = f"{pronounce_number_nl(shown)} uur"
        if minute:
            speak += " " + pronounce_number_nl(minute)
    if clock == "12h" and period:
        speak += " " + _day_period_nl(hour)
    return speak


def nice_time_nl(dt, speech=True, use_24hour=False, use_ampm=False):
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

    # Generate a speakable version of the time
    speak = ""
    if use_24hour:
        speak += pronounce_number_nl(dt.hour)
        speak += " uur"
        if not dt.minute == 0:  # zero minutes are not pronounced, 13:00 is
            # "13 uur" not "13 hundred hours"
            speak += " " + pronounce_number_nl(dt.minute)
        return speak  # ampm is ignored when use_24hour is true
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "Middernacht"
        hour = dt.hour % 12
        if dt.minute == 0:
            hour = _fix_hour_nl(hour)
            speak += pronounce_number_nl(hour)
            speak += " uur"
        elif dt.minute == 30:
            speak += "half "
            hour += 1
            hour = _fix_hour_nl(hour)
            speak += pronounce_number_nl(hour)
        elif dt.minute == 15:
            speak += "kwart over "
            hour = _fix_hour_nl(hour)
            speak += pronounce_number_nl(hour)
        elif dt.minute == 45:
            speak += "kwart voor "
            hour += 1
            hour = _fix_hour_nl(hour)
            speak += pronounce_number_nl(hour)
        elif dt.minute > 30:
            speak += pronounce_number_nl(60 - dt.minute)
            speak += " voor "
            hour += 1
            hour = _fix_hour_nl(hour)
            speak += pronounce_number_nl(hour)
        else:
            speak += pronounce_number_nl(dt.minute)
            speak += " over "
            hour = _fix_hour_nl(hour)
            speak += pronounce_number_nl(hour)

        if use_ampm:
            speak += nice_part_of_day_nl(dt)

        return speak


def _fix_hour_nl(hour):
    hour = hour % 12
    if hour == 0:
        hour = 12
    return hour


def nice_part_of_day_nl(dt, speech=True):
    if dt.hour < 6:
        return " 's nachts"
    if dt.hour < 12:
        return " 's ochtends"
    if dt.hour < 18:
        return " 's middags"
    if dt.hour < 24:
        return " 's avonds"
    raise ValueError('dt.hour is bigger than 24')
