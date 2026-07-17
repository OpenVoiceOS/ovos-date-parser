"""Finnish date and time parsing and formatting.

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
from datetime import timedelta

from ovos_number_parser.numbers_fi import (
    pronounce_number_fi, extract_number_fi,
)
from ovos_utils.time import now_local

from ovos_date_parser.duration import (
    DurationResolution, DURATION_LEXICONS, extract_duration_generic,
)

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

def extract_duration_fi(text, resolution=DurationResolution.TIMEDELTA,
                        replace_token=""):
    """Convert a Finnish phrase into a duration.

    Handles "kaksi tuntia", "puoli tuntia" is not supported (fractional
    numerals are out of scope); numerals are read by the shared number
    parser and matched against the declined unit nouns.
    """
    return extract_duration_generic(text, DURATION_LEXICONS["fi"],
                                    resolution, replace_token)


# ---------------------------------------------------------------------------
# datetime extraction
# ---------------------------------------------------------------------------

_WEEKDAYS_FI = {
    "maanantai": 0, "tiistai": 1, "keskiviikko": 2, "torstai": 3,
    "perjantai": 4, "lauantai": 5, "sunnuntai": 6,
}
# the essive ("maanantaina") is the case used when naming the day of an event
_WEEKDAYS_ESSIVE_FI = {
    "maanantaina": 0, "tiistaina": 1, "keskiviikkona": 2, "torstaina": 3,
    "perjantaina": 4, "lauantaina": 5, "sunnuntaina": 6,
}
_MONTHS_FI = {
    "tammikuu": 1, "helmikuu": 2, "maaliskuu": 3, "huhtikuu": 4,
    "toukokuu": 5, "kesäkuu": 6, "heinäkuu": 7, "elokuu": 8,
    "syyskuu": 9, "lokakuu": 10, "marraskuu": 11, "joulukuu": 12,
}
# month stems accept the partitive/genitive endings that appear in dates
# ("tammikuuta", "tammikuun")
_MONTH_STEMS_FI = {name[:-2]: num for name, num in _MONTHS_FI.items()}

_DAY_UNITS_FI = ("päivä", "päivää", "päivän", "päivan")
_WEEK_UNITS_FI = ("viikko", "viikkoa", "viikon")
_MONTH_UNITS_FI = ("kuukausi", "kuukautta", "kuukauden")
_YEAR_UNITS_FI = ("vuosi", "vuotta", "vuoden")
# adpositions that mark "in X <unit>" / "after"
_AFTER_MARKERS_FI = ("kuluttua", "päästä", "päähän")
_NEXT_FI = ("ensi", "seuraava", "seuraavana", "tuleva", "tulevana")
_LAST_FI = ("viime", "edellinen", "edellisenä", "mennyt", "menneenä")


def _clean_tokens_fi(text):
    out = []
    for tok in text.lower().replace(",", " ").split():
        # keep internal separators (15.30, 15:30) but drop edge punctuation,
        # so an ordinal "15." becomes "15"
        tok = tok.strip("?!;:.")
        if tok:
            out.append(tok)
    return out


def _month_from_word_fi(word):
    if word in _MONTHS_FI:
        return _MONTHS_FI[word]
    for stem, num in _MONTH_STEMS_FI.items():
        if word.startswith(stem):
            return num
    return None


def extract_datetime_fi(text, anchorDate=None, default_time=None):
    """Extract date/time information from Finnish text.

    Supported constructs (each verified against everyday usage):
        * tänään / huomenna / ylihuomenna / eilen / toissapäivänä
        * weekday names, optionally with ensi/viime
        * "N päivän/viikon/kuukauden/vuoden kuluttua|päästä"
        * "ensi|viime viikolla|kuussa|vuonna"
        * clock times: "kello 15:30", "kello 15", "15:30", "15.30"
        * dates with a month name: "15. tammikuuta", "tammikuun 15."

    Returns a ``[datetime, leftover_text]`` pair, or ``None`` when nothing
    date related is found.
    """
    if not text:
        return None

    anchor = anchorDate or now_local()
    anchor = anchor.replace(microsecond=0)
    words = _clean_tokens_fi(text)
    if not words:
        return None

    day_offset = None
    week_offset = 0
    month_offset = 0
    year_offset = 0
    abs_month = None
    abs_day = None
    hr_abs = None
    min_abs = None
    consumed = [False] * len(words)
    found = False

    for idx, word in enumerate(words):
        if consumed[idx]:
            continue
        prev = words[idx - 1] if idx > 0 else ""
        nxt = words[idx + 1] if idx + 1 < len(words) else ""

        # relative day keywords
        if word in ("tänään", "nyt"):
            day_offset = 0
            consumed[idx] = True
            found = True
            continue
        if word == "huomenna":
            day_offset = 1
            consumed[idx] = True
            found = True
            continue
        if word == "ylihuomenna":
            day_offset = 2
            consumed[idx] = True
            found = True
            continue
        if word == "eilen":
            day_offset = -1
            consumed[idx] = True
            found = True
            continue
        if word in ("toissapäivänä", "toissa"):
            day_offset = -2
            consumed[idx] = True
            found = True
            continue

        # weekdays (nominative or essive)
        if word in _WEEKDAYS_FI or word in _WEEKDAYS_ESSIVE_FI:
            target = _WEEKDAYS_FI.get(word, _WEEKDAYS_ESSIVE_FI.get(word))
            diff = (target - anchor.weekday()) % 7
            if prev in _NEXT_FI:
                if diff == 0:
                    diff = 7
                consumed[idx - 1] = True
            elif prev in _LAST_FI:
                diff = diff - 7 if diff != 0 else -7
                consumed[idx - 1] = True
            day_offset = diff
            consumed[idx] = True
            found = True
            continue

        # "ensi/viime viikolla|kuussa|vuonna"
        if word in ("viikolla", "viikko", "viikon") and prev in _NEXT_FI + _LAST_FI:
            week_offset = 1 if prev in _NEXT_FI else -1
            consumed[idx] = consumed[idx - 1] = True
            found = True
            continue
        if word in ("kuussa", "kuukausi", "kuukautena") and prev in _NEXT_FI + _LAST_FI:
            month_offset = 1 if prev in _NEXT_FI else -1
            consumed[idx] = consumed[idx - 1] = True
            found = True
            continue
        if word in ("vuonna", "vuosi", "vuotena") and prev in _NEXT_FI + _LAST_FI:
            year_offset = 1 if prev in _NEXT_FI else -1
            consumed[idx] = consumed[idx - 1] = True
            found = True
            continue

        # "N <unit> kuluttua/päästä"
        if word in _AFTER_MARKERS_FI and idx >= 2:
            unit = words[idx - 1]
            num = extract_number_fi(words[idx - 2])
            if num is not False and num is not None:
                num = int(num)
                if unit in _DAY_UNITS_FI:
                    day_offset = (day_offset or 0) + num
                elif unit in _WEEK_UNITS_FI:
                    week_offset += num
                elif unit in _MONTH_UNITS_FI:
                    month_offset += num
                elif unit in _YEAR_UNITS_FI:
                    year_offset += num
                else:
                    continue
                consumed[idx] = consumed[idx - 1] = consumed[idx - 2] = True
                found = True
                continue

        # clock time with explicit "kello" marker or a HH:MM / HH.MM token
        if word == "kello":
            time_tok = nxt
            if _parse_clock_fi(time_tok) is not None:
                hr_abs, min_abs = _parse_clock_fi(time_tok)
                consumed[idx] = consumed[idx + 1] = True
                found = True
                continue
            num = extract_number_fi(nxt) if nxt else False
            if num is not False and num is not None and 0 <= num <= 23:
                hr_abs, min_abs = int(num), 0
                consumed[idx] = consumed[idx + 1] = True
                found = True
                continue

        clock = _parse_clock_fi(word)
        if clock is not None:
            hr_abs, min_abs = clock
            consumed[idx] = True
            found = True
            continue

        # month-name dates
        month = _month_from_word_fi(word)
        if month is not None:
            day = None
            if prev:
                d = _ordinal_day_fi(prev)
                if d is not None:
                    day = d
                    consumed[idx - 1] = True
            if day is None and nxt:
                d = _ordinal_day_fi(nxt)
                if d is not None:
                    day = d
                    consumed[idx + 1] = True
            abs_month = month
            abs_day = day if day is not None else 1
            consumed[idx] = True
            found = True
            continue

    if not found:
        return None

    extracted = anchor.replace(hour=0, minute=0, second=0)

    if abs_month is not None:
        year = anchor.year
        try:
            candidate = extracted.replace(month=abs_month, day=abs_day)
        except ValueError:
            return None
        if candidate.date() < anchor.date():
            candidate = candidate.replace(year=year + 1)
        extracted = candidate
    else:
        if day_offset is not None:
            extracted = extracted + timedelta(days=day_offset)
        if week_offset:
            extracted = extracted + timedelta(weeks=week_offset)
        if month_offset:
            extracted = _add_months(extracted, month_offset)
        if year_offset:
            try:
                extracted = extracted.replace(year=extracted.year + year_offset)
            except ValueError:  # Feb 29
                extracted = extracted.replace(
                    year=extracted.year + year_offset, day=28)

    if hr_abs is None and default_time is not None:
        hr_abs = default_time.hour
        min_abs = default_time.minute
    if hr_abs is not None:
        extracted = extracted.replace(hour=hr_abs, minute=min_abs or 0)

    leftover = " ".join(w for i, w in enumerate(words)
                        if not consumed[i] and w != ".")
    leftover = " ".join(leftover.split())
    return [extracted, leftover]


def _add_months(dt, months):
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, [31, 29 if year % 4 == 0 and
                       (year % 100 != 0 or year % 400 == 0) else 28,
                       31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return dt.replace(year=year, month=month, day=day)


def _parse_clock_fi(token):
    """Parse an HH:MM or HH.MM clock token into (hour, minute) or None."""
    if not token:
        return None
    for sep in (":", "."):
        if sep in token:
            parts = token.split(sep)
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                hour, minute = int(parts[0]), int(parts[1])
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return hour, minute
            return None
    return None


def _ordinal_day_fi(token):
    """Return a day-of-month 1..31 from a "15." or "15" or spelled ordinal."""
    stripped = token.rstrip(".")
    if stripped.isdigit():
        val = int(stripped)
        if 1 <= val <= 31:
            return val
    from ovos_number_parser.numbers_fi import is_ordinal_fi
    val = is_ordinal_fi(stripped)
    if val is not False and 1 <= val <= 31:
        return val
    return None
