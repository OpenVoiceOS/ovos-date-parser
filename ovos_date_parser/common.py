import datetime
import json
import os.path
import re
import unicodedata
from typing import Callable, Optional

from ovos_number_parser import pronounce_number


def _translate_word(keyword: str, lang: str) -> str:
    lang = lang.split("-")[0]
    p = f"{os.path.dirname(__file__)}/res/{lang}/date_words.json"
    if not os.path.isfile(p):
        raise NotImplementedError(f"Unsupported language: {lang} - please translate {p}")
    with open(p) as f:
        words = json.load(f)
    return words[keyword]


def nice_relative_time_generic(lang, when, relative_to):
    """Create a relative phrase to roughly describe a datetime

    Examples are "25 seconds", "tomorrow", "7 days".

    Args:
        lang (str): BCP-47 language code
        when (datetime): Local timezone
        relative_to (datetime): Baseline for relative time
    Returns:
        str: Relative description of the given time
    """
    delta = when - relative_to

    seconds = delta.total_seconds()
    if seconds < 1:
        try:
            return _translate_word("now", lang)
        except NotImplementedError:
            nice = pronounce_number(0, lang=lang)
            return f"{nice} " + _translate_word("seconds", lang)

    if seconds < 90:
        nice = pronounce_number(seconds, lang=lang)
        if seconds == 1:
            return f"{nice} " + _translate_word("second", lang)
        else:
            return f"{nice} " + _translate_word("seconds", lang)

    minutes = int((delta.total_seconds() + 30) // 60)  # +30 to round minutes
    if minutes < 90:
        nice = pronounce_number(minutes, lang=lang)
        if minutes == 1:
            return f"{nice} " + _translate_word("minute", lang)
        else:
            return f"{nice} " + _translate_word("minutes", lang)

    hours = int((minutes + 30) // 60)  # +30 to round hours
    if hours < 36:
        nice = pronounce_number(hours, lang=lang)
        if hours == 1:
            return f"{nice} " + _translate_word("hour", lang)
        else:
            return f"{nice} " + _translate_word("hours", lang)

    # TODO: "2 weeks", "3 months", "4 years", etc
    days = int((hours + 12) // 24)  # +12 to round days
    nice = pronounce_number(days, lang=lang)
    if days == 1:
        return f"{nice} " + _translate_word("day", lang)
    else:
        return f"{nice} " + _translate_word("days", lang)


#: One of a unit takes the form that agrees with the unit's gender, not the
#: numeral said alone ("eins", "uno", "ett"). The forms are the "1:" rules of
#: CLDR RBNF %spellout-cardinal-masculine, -feminine, -neuter, -common and
#: -reale. The genders are the CLDR units genders of duration-day, -hour,
#: -minute and -second, or a dictionary where CLDR names another noun or no
#: gender: SAOB "DAG ... r." (sv), Bokmålsordboka "minutt n3" and
#: "sekund m1" (nb), Real Academia Galega "hora: substantivo feminino" (gl),
#: Речник на българския език (bg). Italian elides "una" before a vowel,
#: "una ora -> un'ora" (Treccani, Enciclopedia dell'Italiano, "elisione").
_ONE_BEFORE_UNIT = {
    "bg": {"day": "един", "hour": "един", "minute": "една", "second": "една"},
    "ca": {"day": "un", "hour": "una", "minute": "un", "second": "un"},
    "cs": {"day": "jeden", "hour": "jedna", "minute": "jedna", "second": "jedna"},
    "da": {"day": "en", "hour": "en", "minute": "et", "second": "et"},
    "de": {"day": "ein", "hour": "eine", "minute": "eine", "second": "eine"},
    "el": {"day": "μία", "hour": "μία", "minute": "ένα", "second": "ένα"},
    "es": {"day": "un", "hour": "una", "minute": "un", "second": "un"},
    "fr": {"day": "un", "hour": "une", "minute": "une", "second": "une"},
    "gl": {"day": "un", "hour": "unha", "minute": "un", "second": "un"},
    "hr": {"day": "jedan", "hour": "jedan", "minute": "jedna", "second": "jedna"},
    "it": {"day": "un", "hour": "un'", "minute": "un", "second": "un"},
    "nb": {"minute": "ett"},
    "pt": {"day": "um", "hour": "uma", "minute": "um", "second": "um"},
    "sk": {"day": "jeden", "hour": "jedna", "minute": "jedna", "second": "jedna"},
    "sl": {"day": "en", "hour": "ena", "minute": "ena", "second": "ena"},
    "sv": {"day": "en", "hour": "en", "minute": "en", "second": "en"},
}


def _count(number, unit, lang):
    """Say ``number`` as it stands before ``unit`` in ``lang``."""
    one = _ONE_BEFORE_UNIT.get(lang.lower().split("-")[0], {}).get(unit)
    if number == 1 and one:
        return one
    return pronounce_number(number, lang)


def nice_duration_generic(lang, duration, speech=True):
    """ Convert duration in seconds to a nice spoken timespan

    Examples:
       duration = 60  ->  "1:00" or "one minute"
       duration = 163  ->  "2:43" or "two minutes forty three seconds"

    Args:
        lang (str): BCP-47 language code
        duration: time, in seconds
        speech (bool): format for speech (True) or display (False)

    Returns:
        str: timespan as a string
    """
    if isinstance(duration, datetime.timedelta):
        duration = duration.total_seconds()

    # Do traditional rounding: 2.5->3, 3.5->4, plus this
    # helps in a few cases of where calculations generate
    # times like 2:59:59.9 instead of 3:00.
    duration += 0.5

    days = int(duration // 86400)
    hours = int(duration // 3600 % 24)
    minutes = int(duration // 60 % 60)
    seconds = int(duration % 60)

    if speech:
        parts = []
        for count, unit in ((days, "day"), (hours, "hour"),
                            (minutes, "minute"), (seconds, "second")):
            if count > 0:
                number = _count(count, unit, lang)
                word = _translate_word(unit if count == 1 else unit + "s", lang)
                # an elided "un'" joins its noun with no space
                parts.append(number + word if number.endswith("'")
                             else f"{number} {word}")
        out = " ".join(parts)
    else:
        # M:SS, MM:SS, H:MM:SS, Dd H:MM:SS format
        out = ""
        if days > 0:
            out = str(days) + "d "
        if hours > 0 or days > 0:
            out += str(hours) + ":"
        if minutes < 10 and (hours > 0 or days > 0):
            out += "0"
        out += str(minutes) + ":"
        if seconds < 10:
            out += "0"
        out += str(seconds)

    return out


#: The most words a spelled number in a remainder is read back from:
#: "un millón doscientos mil trescientos cuarenta y cinco" is eight.
_LONGEST_SPELLED_NUMBER = 8


def restore_typed_words(remainder: str, text: str,
                        to_digits: Optional[Callable[[str], str]] = None
                        ) -> str:
    """Give the words of a remainder back the spelling the user typed.

    A parser lower-cases the sentence, strips its accents, turns hyphens into
    spaces and drops punctuation before it reads it, so the remainder holds
    words the user did not type. Each run of remainder words that matches one
    of the typed words, in order, is replaced by that word. Case stays lower.

    A parser that turns spelled numbers into digits before it reads passes its
    converter as ``to_digits``. A digit in the remainder then takes back the
    longest run of typed words that the converter turns into that digit, so
    "tres" stays "tres" and "veinte y tres" stays three words.
    """
    def bare(word):
        return "".join(c for c in unicodedata.normalize("NFD", word)
                       if not unicodedata.combining(c) and c not in "'_")

    typed = []
    for chunk in text.lower().split():
        chunk = "".join(c for c in chunk if c not in ".,;?!ºª")
        parts = [bare(part) for part in chunk.split("-") if bare(part)]
        if parts:
            typed.append((chunk, parts))

    words = remainder.split()
    out = []
    pos = 0
    i = 0
    while i < len(words):
        for j in range(pos, len(typed)):
            chunk, parts = typed[j]
            if [bare(w) for w in words[i:i + len(parts)]] == parts:
                out.append(chunk)
                i += len(parts)
                pos = j + 1
                break
            if to_digits is not None and words[i].isdigit():
                run = _spelled_run(words[i], typed, j, to_digits)
                if run:
                    out.append(" ".join(chunk for chunk, _ in typed[j:j + run]))
                    i += 1
                    pos = j + run
                    break
        else:
            out.append(words[i])
            i += 1
    return " ".join(out)


def _spelled_run(digits: str, typed: list, start: int,
                 to_digits: Callable[[str], str]) -> int:
    """How many typed words from ``start`` spell ``digits``, longest first.

    Zero when no run spells it.
    """
    for size in range(min(_LONGEST_SPELLED_NUMBER, len(typed) - start), 0, -1):
        phrase = " ".join(chunk for chunk, _ in typed[start:start + size])
        if to_digits(phrase) == digits:
            return size
    return 0
