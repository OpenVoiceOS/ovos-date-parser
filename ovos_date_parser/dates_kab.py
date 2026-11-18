"""Kabyle (Taqbaylit, ``kab``) date and time tools.

Weekday names are the Arabic-derived forms in everyday use (letnayen,
ttlata, ...); month names follow the Kabyle calendar spellings (yennayer,
fuṛar, ... dujembeṛ). Time units mix the attested Amazigh neologisms
(tasint "second", asrag "hour", amalas "week") with the Arabic-derived
words that carry daily usage (ddqiqa "minute", ssaɛa "hour").

Spoken clock phrases (e.g. "d lɛecṛa u ṛbeɛ", "d juǧ n uzal") are built
around the presentative particle "d" ("it is"), the additive/subtractive
conjunctions "u"/"ɣiṛ", and a closed set of fraction and day-period
words - see `_extract_spoken_time_kab` below.

Sources:
- https://kab.wikipedia.org/wiki/Yennayer (month names)
- https://apprendrelekabyle.com/les-jours-de-la-semaine-en-kabyle/
- https://glosbe.com/fr/kab (heure, minute, seconde, matin, soir, semaine)
- https://en.wikipedia.org/wiki/Kabyle_language (grammar)
- Boulifa, *Une première année de langue kabyle*, 1910 (roba', nofc,
  r'ir, eddeq'iq'a)
- Dallet, *Dictionnaire kabyle-français*, 1982 (azgen, swaswa/gedged)
- Amazit-Hamidchi & Lounaci, *Le Kabyle de poche*, Assimil, 2005
  (nefs, ɣir, u, ddqayeq, wac)
"""
from datetime import timedelta
from typing import Optional, Tuple

from ovos_number_parser.numbers_kab import extract_number_kab, _normalize


# duration units, singular and plural spellings (Amazigh neologisms and
# the Arabic-derived words both extract)
_SECONDS_UNITS = {"tasint", "tisinin"}
_MINUTES_UNITS = {"ddqiqa", "tesdidin", "tisdidin", "dqiqa"}
_HOURS_UNITS = {"ssaɛa", "saɛa", "tsaɛtin", "tisaɛtin", "asrag", "isragen",
                "wesrag", "usrag"}
_DAYS_UNITS = {"ass", "ussan", "wass", "wussan"}
_WEEKS_UNITS = {"amalas", "imalasen", "yimalasen", "ddurt", "dduṛt",
                "umalas"}


# ---------------------------------------------------------------------------
# Spoken clock-time grammar
# ---------------------------------------------------------------------------


def nice_time_kab(dt, speech=True, use_24hour=False, use_ampm=False):
    """Format a time to a human-readable string in Kabyle.
    Conforms to native speaker specifications (Mokraoui 2026).
    """
    if not speech:
        return dt.strftime("%H:%M")

    # Spoken Kabyle naturally uses a 12-hour cycle
    hour_12 = dt.hour % 12
    if hour_12 == 0:
        hour_12 = 12

    # Canonical hour words with article assimilation (sun/moon letters)
    hour_words = {
        1: "lweḥda",
        2: "ssaɛtin",    # Regional/Preferred form for 2 o'clock
        3: "ttlata",
        4: "ṛabɛa",
        5: "lxemsa",
        6: "setta",
        7: "ssebɛa",
        8: "ttmanya",
        9: "tesɛa",
        10: "lɛecṛa",
        11: "leḥdac",
        12: "ttnac"
    }

    # Section 3.1: Mandatory presentative "d"
    time_str = f"d {hour_words.get(hour_12, str(hour_12))}"
    minute = dt.minute

    # Section 4.1, 4.5: Handle minutes and fractions
    if minute == 0:
        pass  # Exact hour, no suffix needed (e.g., "d ttmanya")
    elif minute == 15:
        time_str += " u ṛbeɛ"
    elif minute == 30:
        time_str += " u neṣṣ"          # Canonical "neṣṣ"
    elif minute == 45:
        time_str += " ɣiṛ ṛbeɛ"
    else:
        # Section 4.5: Explicit minutes require "u [minute] n ddqayeq"
        # Note: Uses FEMININE numeral forms to agree with "ddqiqa" (minute)
        min_words = {
            1: "yiwet", 2: "snat", 3: "tlata", 4: "ṛebɛa", 5: "xemsa",
            6: "setta", 7: "sebɛa", 8: "tmanya", 9: "tesɛa", 10: "ɛecṛa",
            11: "hḍac", 12: "tnac",
            13: "tleṭṭac", 14: "ṛebɛaṭac", 15: "xemseṭṭac",
            16: "seṭṭac", 17: "sbeɛṭac", 18: "tmenṭac", 19: "tseɛṭac",
            20: "ɛecrin",
            21: "waḥed u ɛecrin", 22: "tnayn u ɛecrin", 23: "tlata u ɛecrin",
            24: "ṛebɛa u ɛecrin", 25: "xemsa u ɛecrin", 26: "setta u ɛecrin",
            27: "sebɛa u ɛecrin", 28: "tmanya u ɛecrin", 29: "tesɛa u ɛecrin",
            30: "tlatin",
            31: "waḥed u tlatin", 32: "tnayn u tlatin", 33: "tlata u tlatin",
            34: "ṛebɛa u tlatin", 35: "xemsa u tlatin", 36: "setta u tlatin",
            37: "sebɛa u tlatin", 38: "tmanya u tlatin", 39: "tesɛa u tlatin",
            40: "rebɛin",
            41: "waḥed u rebɛin", 42: "tnayn u rebɛin", 43: "tlata u rebɛin",
            44: "ṛebɛa u rebɛin", 45: "xemsa u rebɛin", 46: "setta u rebɛin",
            47: "sebɛa u rebɛin", 48: "tmanya u rebɛin", 49: "tesɛa u rebɛin",
            50: "xemsin",
            51: "waḥed u xemsin", 52: "tnayn u xemsin", 53: "tlata u xemsin",
            54: "ṛebɛa u xemsin", 55: "xemsa u xemsin", 56: "setta u xemsin",
            57: "sebɛa u xemsin", 58: "tmanya u xemsin", 59: "tesɛa u xemsin"
        }
        min_word = min_words.get(minute, str(minute))
        time_str += f" u {min_word} n ddqayeq"

    # Section 5: Handle AM/PM or day period context
    if use_ampm:
        if 4 <= dt.hour < 8:
            time_str += " n ṣṣbeḥ"
        elif 8 <= dt.hour < 12:
            time_str += " n ssbeḥ"
        elif 12 <= dt.hour < 15:
            time_str += " n uzal"
        elif 15 <= dt.hour < 20:
            time_str += " n tmeddit"
        else:
            time_str += " n yiḍ"

    return time_str


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
            first = None
            connector_used = False
            while start >= 0:
                if start in consumed:
                    break
                candidate = " ".join(tokens[start:j + 1])
                val = extract_number_kab(candidate)
                if val is False:
                    break
                if value is None or val != value:
                    value = val
                    first = start
                    connector_used = False
                    start -= 1
                    continue
                # The longer candidate reads the same value, so this token
                # adds nothing of its own. extract_number_kab tolerates any
                # prefix and answers the number it finds inside, so without
                # a stop here the scan walks to the start of the line and
                # the remainder comes back with every leading word removed.
                # One such token may still be the connector of a spoken
                # number ("mraw d yiwen" is 11), so one is allowed through,
                # and only when it does not spell a number by itself. This
                # is the rule ovos_number_parser.extract_number_spans uses
                # for the same problem.
                word = extract_number_kab(tokens[start].strip(".,!?;:"))
                if connector_used or word is not False:
                    break
                connector_used = True
                start -= 1
            if value is None:
                # a unit noun with no quantity before it is not a
                # duration. Reading it as one turns the question "acdal
                # ara tili ssaɛa" into an hour, and adds a spurious hour
                # to any phrase that also carries a real quantity.
                i += 1
                continue
            total += value * unit_seconds[tok]
            found = True
            consumed.update(range(first, i + 1))
        i += 1

    if not found:
        return None, text

    remainder = " ".join(t for idx, t in enumerate(tokens)
                         if idx not in consumed)
    return timedelta(seconds=total), remainder.strip()
