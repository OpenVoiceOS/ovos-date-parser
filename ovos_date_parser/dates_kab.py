"""Kabyle (Taqbaylit, ``kab``) date and time tools.

Weekday names are the Arabic-derived forms in everyday use (letnayen,
ttlata, ...); month names follow the Kabyle calendar spellings (yennayer,
fuṛar, ... dujembeṛ). Time units mix the attested Amazigh neologisms
(tasint "second", asrag "hour", amalas "week") with the Arabic-derived
words that carry daily usage (ddqiqa "minute", ssaɛa "hour").

Spoken clock phrases (e.g. "d lɛecṛa u ṛbeɛ", "d juǧ n uzal") are built
around the presentative particle "d" ("it is"), the additive/subtractive
conjunctions "u"/"ɣiṛ", and a closed set of fraction and day-period
words.

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


