"""Kabyle (Taqbaylit, ``kab``) date and time tools.

Weekday names are the Arabic-derived forms in everyday use (letnayen,
ttlata, ...); month names follow the Kabyle calendar spellings (yennayer,
fuṛar, ... dujembeṛ). Time units mix the attested Amazigh neologisms
(tasint "second", asrag "hour", amalas "week") with the Arabic-derived
words that carry daily usage (ddqiqa "minute", ssaɛa "hour").

Sources:
- https://kab.wikipedia.org/wiki/Yennayer (month names)
- https://apprendrelekabyle.com/les-jours-de-la-semaine-en-kabyle/
- https://glosbe.com/fr/kab (heure, minute, seconde, matin, soir, semaine)
- https://en.wikipedia.org/wiki/Kabyle_language (grammar)
"""
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

from ovos_number_parser.numbers_kab import (pronounce_number_kab,
                                            extract_number_kab, _normalize)

WEEKDAYS_KAB = {0: "letnayen", 1: "ttlata", 2: "laṛebɛa", 3: "lexmis",
                4: "lǧemɛa", 5: "ssebt", 6: "lḥedd"}
MONTHS_KAB = {1: "yennayer", 2: "fuṛar", 3: "meɣres", 4: "yebrir",
              5: "mayyu", 6: "yunyu", 7: "yulyu", 8: "ɣuct",
              9: "ctembeṛ", 10: "tubeṛ", 11: "wambeṛ", 12: "dujembeṛ"}

# day-part words: ssbeḥ "morning", tameddit "evening", iḍ "night"
_MORNING = "ssbeḥ"
_EVENING = "tameddit"

# duration units, singular and plural spellings (Amazigh neologisms and
# the Arabic-derived words both extract)
_SECONDS_UNITS = {"tasint", "tisinin"}
_MINUTES_UNITS = {"ddqiqa", "tesdidin", "tisdidin", "dqiqa"}
_HOURS_UNITS = {"ssaɛa", "saɛa", "tsaɛtin", "tisaɛtin", "asrag", "isragen",
                "wesrag", "usrag"}
_DAYS_UNITS = {"ass", "ussan", "wass", "wussan"}
_WEEKS_UNITS = {"amalas", "imalasen", "yimalasen", "ddurt", "dduṛt",
                "wamalas"}

_RELATIVE_DAYS = {"azekka": 1, "iḍelli": -1, "idelli": -1,
                  "ass-a": 0, "assa": 0, "ass-agi": 0}


def nice_time_kab(dt, speech=True, use_24hour=False, use_ampm=False):
    """Format a time to a comfortable human format in Kabyle.

    Hours and minutes are joined with the conjunction "d"; exact hours
    are spoken alone.
    """
    if use_24hour:
        string = dt.strftime("%H:%M")
    else:
        string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]
        if use_ampm:
            string += " " + (_MORNING if dt.hour < 12 else _EVENING)
    if not speech:
        return string

    if use_24hour:
        speak = pronounce_number_kab(dt.hour)
        if dt.minute:
            speak += f" d {pronounce_number_kab(dt.minute)}"
        return speak

    hour = dt.hour % 12 or 12
    speak = pronounce_number_kab(hour)
    if dt.minute:
        speak += f" d {pronounce_number_kab(dt.minute)}"
    if use_ampm:
        speak += " " + (_MORNING if dt.hour < 12 else _EVENING)
    return speak


def extract_duration_kab(text: str) -> Tuple[Optional[timedelta], str]:
    """Extract a duration from Kabyle text.

    Understands digit and spoken quantities followed by an optional "n"
    genitive particle and a time unit ("10 n ddqayeq", "sin wussan").
    """
    if not text:
        return None, text

    unit_seconds = {}
    for w in _SECONDS_UNITS:
        unit_seconds[_normalize(w)] = 1
    for w in _MINUTES_UNITS:
        unit_seconds[_normalize(w)] = 60
    for w in _HOURS_UNITS:
        unit_seconds[_normalize(w)] = 3600
    for w in _DAYS_UNITS:
        unit_seconds[_normalize(w)] = 86400
    for w in _WEEKS_UNITS:
        unit_seconds[_normalize(w)] = 604800

    tokens = text.split()
    total = 0.0
    found = False
    consumed = set()
    i = 0
    while i < len(tokens):
        tok = _normalize(tokens[i].strip(".,!?;:"))
        if tok in unit_seconds:
            # find the quantity immediately before (skipping genitive "n")
            j = i - 1
            if j >= 0 and _normalize(tokens[j].strip(".,!?;:")) == "n":
                j -= 1
            # allow multiword spoken numbers before the unit
            start = j
            value = None
            while start >= 0:
                if start in consumed:
                    break
                candidate = " ".join(tokens[start:j + 1])
                val = extract_number_kab(candidate)
                if val is False:
                    break
                value = val
                start -= 1
            if value is None:
                value = 1
                start = j
            total += value * unit_seconds[tok]
            found = True
            consumed.update(range(start + 1, i + 1))
        i += 1

    if not found:
        return None, text

    remainder = " ".join(t for idx, t in enumerate(tokens)
                         if idx not in consumed)
    return timedelta(seconds=total), remainder.strip()


def extract_datetime_kab(text: str, anchorDate: Optional[datetime] = None,
                         default_time=None):
    """Extract a datetime from Kabyle text.

    Understands the relative day words (azekka "tomorrow", iḍelli
    "yesterday", ass-a "today"), weekday and month names, day-of-month
    numbers and clock times ("13:04").
    """
    if not text:
        return None
    anchor = anchorDate or datetime.now()
    tokens = [t.strip(".,!?;:") for t in text.lower().split()]
    norm = [_normalize(t) for t in tokens]

    date_found = False
    result = anchor
    consumed = set()

    rel_days = {_normalize(k): v for k, v in _RELATIVE_DAYS.items()}
    weekdays = {_normalize(v): k for k, v in WEEKDAYS_KAB.items()}
    months = {_normalize(v): k for k, v in MONTHS_KAB.items()}

    for i, tok in enumerate(norm):
        if tok in rel_days:
            result = anchor + timedelta(days=rel_days[tok])
            date_found = True
            consumed.add(i)
        elif tok in weekdays:
            target = weekdays[tok]
            diff = (target - anchor.weekday()) % 7 or 7
            result = anchor + timedelta(days=diff)
            date_found = True
            consumed.add(i)
        elif tok in months:
            month = months[tok]
            day = None
            for j in (i - 1, i + 1):
                if 0 <= j < len(tokens):
                    if j == i + 1 and norm[j] == "n" and j + 1 < len(tokens):
                        j += 1
                    val = extract_number_kab(tokens[j])
                    if val and float(val).is_integer() and 1 <= val <= 31:
                        day = int(val)
                        consumed.add(j)
                        break
            year = anchor.year
            if datetime(year, month, day or 1) < anchor.replace(
                    hour=0, minute=0, second=0, microsecond=0):
                year += 1
            result = result.replace(year=year, month=month, day=day or 1)
            date_found = True
            consumed.add(i)

    time_found = False
    for i, tok in enumerate(tokens):
        m = re.fullmatch(r"(\d{1,2}):(\d{2})", tok)
        if m:
            hour, minute = int(m.group(1)), int(m.group(2))
            if hour < 24 and minute < 60:
                result = result.replace(hour=hour, minute=minute, second=0,
                                        microsecond=0)
                time_found = True
                consumed.add(i)
                break

    if not date_found and not time_found:
        return None
    if not time_found:
        if default_time:
            result = result.replace(hour=default_time.hour,
                                    minute=default_time.minute,
                                    second=default_time.second,
                                    microsecond=0)
        else:
            result = result.replace(hour=0, minute=0, second=0,
                                    microsecond=0)
    remainder = " ".join(t for idx, t in enumerate(tokens)
                         if idx not in consumed)
    return [result, remainder.strip()]
