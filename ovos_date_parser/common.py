import datetime
import json
import os.path
import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from pathlib import Path
from typing import Callable, Optional

from linguatag import closest_lang, standardize_lang

from ovos_number_parser import pronounce_number


#: the languages that have a writer: a ``dates_<code>`` module or a ``res`` folder
_PACKAGE = Path(__file__).parent
_WRITER_LANGS = frozenset(
    {path.stem.removeprefix("dates_") for path in _PACKAGE.glob("dates_*.py")}
    | {path.parent.name for path in (_PACKAGE / "res").glob("*/date_time.json")})


@lru_cache(maxsize=4096)
def primary_language(lang: str) -> str:
    """The language subtag of ``lang`` in canonical form: "PT_br" is "pt"
    and "iw" is "he"."""
    return standardize_lang(lang.strip()).partition("-")[0]


@lru_cache(maxsize=4096)
def writer_lang(lang: str) -> Optional[str]:
    """The language of ``_WRITER_LANGS`` that writes ``lang``, or None:
    "PT_BR" is "pt", "no" is "nb" and "fil" has none."""
    return closest_lang(primary_language(lang), sorted(_WRITER_LANGS))


@lru_cache(maxsize=None)
def _load_words(code: str) -> dict:
    p = f"{os.path.dirname(__file__)}/res/{code}/date_words.json"
    if not os.path.isfile(p):
        raise NotImplementedError(f"Unsupported language: {code} - please translate {p}")
    with open(p) as f:
        return json.load(f)


def _words(lang: str) -> dict:
    return _load_words(writer_lang(lang) or lang)


def _translate_word(keyword: str, lang: str) -> str:
    return _words(lang)[keyword]


def _operands(number) -> tuple:
    """The whole number and the visible fraction digits of ``number`` as
    ``pronounce_number`` speaks it, rounded half up to three places. The
    fraction is an int, the CLDR operand f, or None when nothing is spoken
    after the whole number: 2.2 is (2, 2), 1.05 is (1, 5) and 12.0 is (12, None)."""
    if isinstance(number, int):
        return abs(number), None
    spoken = Decimal(str(abs(number))).quantize(Decimal("0.001"), ROUND_HALF_UP)
    whole, _, fraction = f"{spoken:f}".partition(".")
    fraction = fraction.rstrip("0")
    return int(whole), int(fraction) if fraction else None


def _plural_category(number, rule: dict) -> str:
    """The plural category of ``number`` under ``rule``, else "other".

    ``rule`` maps a category to a condition on the whole number
    ("integer") and one on the visible fraction digits ("fraction"). A
    condition lists the last digits and the last two digits that put the
    operand in the category, as in the CLDR plural rules of hr and bs:
    ``{"one": {"integer": {"last_digit": [1], "not_last_two": [11]}}}``.
    A number with a spoken fraction takes the fraction condition."""
    whole, fraction = _operands(number)
    part, operand = ("integer", whole) if fraction is None else ("fraction", fraction)
    for category, conditions in rule.items():
        cond = conditions.get(part)
        if cond and operand % 10 in cond["last_digit"] \
                and operand % 100 not in cond["not_last_two"]:
            return category
    return "other"


def _unit_word(unit: str, count, lang: str) -> str:
    """The noun of ``unit`` for ``count``. A language whose date_words.json
    has a "plural_rule" and "plural_forms" takes the form of the count's
    plural category; the others take the singular for 1 and the plural
    otherwise."""
    words = _words(lang)
    if "plural_rule" in words:
        category = _plural_category(count, words["plural_rule"])
        return words["plural_forms"][unit][category]
    return words[unit if count == 1 else unit + "s"]


def _agree(number_words: str, unit: str, count, lang: str) -> str:
    """Give the last word of a spelled whole ``count`` the gender of ``unit``,
    from the "feminine_units" and "feminine_numerals" of date_words.json. A
    count with a fraction keeps the words ``pronounce_number`` gives."""
    words = _words(lang)
    if unit not in words.get("feminine_units", ()) or _operands(count)[1] is not None:
        return number_words
    head, _, last = number_words.rpartition(" ")
    last = words["feminine_numerals"].get(last, last)
    return f"{head} {last}" if head else last


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
    lang = lang.strip()
    delta = when - relative_to

    seconds = delta.total_seconds()
    if seconds < 1:
        try:
            return _translate_word("now", lang)
        except NotImplementedError:
            nice = pronounce_number(0, lang=lang)
            return f"{nice} " + _translate_word("seconds", lang)

    if seconds < 90:
        nice = _agree(pronounce_number(seconds, lang=lang), "second", seconds, lang)
        return f"{nice} " + _unit_word("second", seconds, lang)

    minutes = int((delta.total_seconds() + 30) // 60)  # +30 to round minutes
    if minutes < 90:
        nice = _agree(pronounce_number(minutes, lang=lang), "minute", minutes, lang)
        return f"{nice} " + _unit_word("minute", minutes, lang)

    hours = int((minutes + 30) // 60)  # +30 to round hours
    if hours < 36:
        nice = _agree(pronounce_number(hours, lang=lang), "hour", hours, lang)
        return f"{nice} " + _unit_word("hour", hours, lang)

    # TODO: "2 weeks", "3 months", "4 years", etc
    days = int((hours + 12) // 24)  # +12 to round days
    nice = _agree(pronounce_number(days, lang=lang), "day", days, lang)
    return f"{nice} " + _unit_word("day", days, lang)


#: One of a unit takes the form that agrees with the unit's gender, not the
#: numeral said alone ("eins", "uno", "ett"). The forms are the "1:" rules of
#: CLDR 49 RBNF %spellout-cardinal-masculine, -feminine, -neuter, -common and
#: -reale. The genders are the CLDR 49 units genders of duration-day, -hour,
#: -minute and -second, or a dictionary where CLDR names another noun or no
#: gender: SAOB "DAG ... r." (sv), Bokmålsordboka "minutt" n3 (article
#: 38590) and "sekund" n3, the unit of time (article 50558) (nb), Real
#: Academia Galega "hora: substantivo feminino" (gl), Речник на българския
#: език (bg). Italian elides "una" before a vowel,
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
    "it": {"day": "un", "hour": "un'", "minute": "un", "second": "un"},
    "nb": {"minute": "ett", "second": "ett"},
    "pt": {"day": "um", "hour": "uma", "minute": "um", "second": "um"},
    "sk": {"day": "jeden", "hour": "jedna", "minute": "jedna", "second": "jedna"},
    "sl": {"day": "en", "hour": "ena", "minute": "ena", "second": "ena"},
    "sv": {"day": "en", "hour": "en", "minute": "en", "second": "en"},
}


def _count(number, unit, lang):
    """Say ``number`` as it stands before ``unit`` in ``lang``."""
    one = _ONE_BEFORE_UNIT.get(writer_lang(lang), {}).get(unit)
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
    lang = lang.strip()
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
                number = _agree(_count(count, unit, lang), unit, count, lang)
                word = _unit_word(unit, count, lang)
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
