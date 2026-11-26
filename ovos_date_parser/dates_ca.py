from enum import IntEnum

from ovos_number_parser.numbers_ca import pronounce_number_ca


class TimeVariantCA(IntEnum):
    DEFAULT = 0
    BELL = 1
    FULL_BELL = 2
    SPANISH_LIKE = 3


# Human-friendly aliases so callers can pick a time-telling register by name
# instead of importing the enum. Catalan has two well-known ways to tell time:
#   - the "standard"/central register: "les quatre i quart", "les quatre i
#     mitja", "les cinc menys quart" (mapped to SPANISH_LIKE)
#   - the traditional "quarts" register: quarters counted toward the *next*
#     hour, "un quart de cinc" (4:15), "dos quarts de cinc" (4:30), "tres
#     quarts de cinc" (4:45), with the finer "mig quart" / "un quart i mig"
#     refinements (mapped to BELL, or FULL_BELL for the exhaustive gradation)
_TIME_VARIANT_ALIASES_CA = {
    "default": TimeVariantCA.DEFAULT,
    "watch": TimeVariantCA.DEFAULT,
    "standard": TimeVariantCA.SPANISH_LIKE,
    "central": TimeVariantCA.SPANISH_LIKE,
    "spanish_like": TimeVariantCA.SPANISH_LIKE,
    "quarts": TimeVariantCA.BELL,
    "bell": TimeVariantCA.BELL,
    "quarts_full": TimeVariantCA.FULL_BELL,
    "full_bell": TimeVariantCA.FULL_BELL,
}


def _resolve_time_variant_ca(variant):
    """Resolve a variant given as an enum member, an enum name, or a
    human-friendly alias string into a ``TimeVariantCA``.

    Anything unrecognised (including ``None``) falls back to
    ``TimeVariantCA.DEFAULT`` so existing callers keep the current behaviour.
    """
    if isinstance(variant, TimeVariantCA):
        return variant
    if isinstance(variant, str):
        key = variant.strip().lower()
        if key in _TIME_VARIANT_ALIASES_CA:
            return _TIME_VARIANT_ALIASES_CA[key]
        # also accept the exact enum member name, e.g. "FULL_BELL"
        try:
            return TimeVariantCA[variant.strip().upper()]
        except KeyError:
            return TimeVariantCA.DEFAULT
    if isinstance(variant, int):
        try:
            return TimeVariantCA(variant)
        except ValueError:
            return TimeVariantCA.DEFAULT
    return TimeVariantCA.DEFAULT


def nice_time_ca(dt, speech=True, use_24hour=False, use_ampm=False,
                 variant=TimeVariantCA.DEFAULT):
    """
    Format a time to a comfortable human format
     For example, generate 'cinc trenta' for speech or '5:30' for
    text display.
     Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)=Fal
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
        variant (TimeVariantCA|str): time-telling register. Accepts a
            TimeVariantCA member or a friendly alias string. Notable aliases:
            "standard"/"central" (i quart / i mitja / menys quart),
            "quarts" (traditional quarters-toward-next-hour: "un quart de
            cinc"), "quarts_full" (fine-grained quarts gradation) and
            "default" (plain watch time). Unknown values fall back to the
            default watch-time register, preserving existing behaviour.
    Returns:
        (str): The formatted time string
    """
    variant = _resolve_time_variant_ca(variant)

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
    if variant == TimeVariantCA.BELL:
        # Bell Catalan Time System
        # https://en.wikipedia.org/wiki/Catalan_time_system

        if dt.minute < 7:
            next_hour = False
        elif dt.minute == 7 or dt.minute == 8:
            speak += "mig quart"
            next_hour = True
        elif dt.minute < 15:
            next_hour = False
        elif dt.minute == 15:
            speak += "un quart"
            next_hour = True
        elif dt.minute == 16:
            speak += "un quart i un minut"
            next_hour = True
        elif dt.minute < 21:
            speak += "un quart i " + pronounce_number_ca(
                dt.minute - 15) + " minuts"
            next_hour = True
        elif dt.minute == 22 or dt.minute == 23:
            speak += "un quart i mig"
            next_hour = True
        elif dt.minute < 30:
            speak += "un quart i " + pronounce_number_ca(
                dt.minute - 15) + " minuts"
            next_hour = True
        elif dt.minute == 30:
            speak += "dos quarts"
            next_hour = True
        elif dt.minute == 31:
            speak += "dos quarts i un minut"
            next_hour = True
        elif dt.minute < 37:
            speak += "dos quarts i " + pronounce_number_ca(
                dt.minute - 30) + " minuts"
            next_hour = True
        elif dt.minute == 37 or dt.minute == 38:
            speak += "dos quarts i mig"
            next_hour = True
        elif dt.minute < 45:
            speak += "dos quarts i " + pronounce_number_ca(
                dt.minute - 30) + " minuts"
            next_hour = True
        elif dt.minute == 45:
            speak += "tres quarts"
            next_hour = True
        elif dt.minute == 46:
            speak += "tres quarts i un minut"
            next_hour = True
        elif dt.minute < 52:
            speak += "tres quarts i " + pronounce_number_ca(
                dt.minute - 45) + " minuts"
            next_hour = True
        elif dt.minute == 52 or dt.minute == 53:
            speak += "tres quarts i mig"
            next_hour = True
        elif dt.minute > 53:
            speak += "tres quarts i " + pronounce_number_ca(
                dt.minute - 45) + " minuts"
            next_hour = True

        if next_hour == True:
            next_hour = (dt.hour + 1) % 12
            if next_hour == 0:
                speak += " de dotze"
                if dt.hour == 11:
                    speak += " del migdia"
                else:
                    speak += " de la nit"

            elif next_hour == 1:
                speak += " d'una"
                if dt.hour == 12:
                    speak += " de la tarda"
                else:
                    speak += " de la matinada"
            elif next_hour == 2:
                speak += " de dues"
                if dt.hour == 13:
                    speak += " de la tarda"
                else:
                    speak += " de la nit"

            elif next_hour == 11:
                speak += " d'onze"
                if dt.hour == 22:
                    speak += " de la nit"
                else:
                    speak += " del matí"
            else:
                speak += " de " + pronounce_number_ca(next_hour)
                if dt.hour == 0 and dt.hour < 5:
                    speak += " de la matinada"
                elif dt.hour >= 5 and dt.hour < 11:
                    speak += " del matí"
                elif dt.hour == 11:
                    speak += " del migdia"
                elif dt.hour >= 12 and dt.hour <= 17:
                    speak += " de la tarda"
                elif dt.hour >= 18 and dt.hour < 20:
                    speak += " del vespre"
                elif dt.hour >= 21 and dt.hour <= 23:
                    speak += " de la nit"


        else:
            hour = dt.hour % 12
            if hour == 0:
                speak += "les dotze"
            elif hour == 1:
                speak += "la una"
            elif hour == 2:
                speak += "les dues"
            else:
                speak += "les " + pronounce_number_ca(hour)

            if dt.minute == 0:
                speak += " en punt"
            elif dt.minute == 1:
                speak += " i un minut"
            else:
                speak += " i " + pronounce_number_ca(dt.minute) + " minuts"

            if dt.hour == 0:
                speak += " de la nit"
            elif dt.hour >= 1 and dt.hour < 6:
                speak += " de la matinada"
            elif dt.hour >= 6 and dt.hour < 11:
                speak += " del matí"
            elif dt.hour == 12:
                speak += " del migdia"
            elif dt.hour >= 13 and dt.hour < 19:
                speak += " de la tarda"
            elif dt.hour >= 19 and dt.hour < 21:
                speak += " del vespre"
            elif dt.hour >= 21 and dt.hour <= 23:
                speak += " de la nit"

    elif variant == TimeVariantCA.FULL_BELL:
        # Full Bell Catalan Time System
        # https://en.wikipedia.org/wiki/Catalan_time_system

        if dt.minute < 2:
            # en punt
            next_hour = False
        if dt.minute < 5:
            # tocades
            next_hour = False
        elif dt.minute < 7:
            # ben tocades
            next_hour = False
        elif dt.minute < 9:
            # mig quart
            speak += "mig quart"
            next_hour = True
        elif dt.minute < 12:
            # mig quart passat
            speak += "mig quart passat"
            next_hour = True
        elif dt.minute < 14:
            # mig quart passat
            speak += "mig quart ben passat"
            next_hour = True
        elif dt.minute < 17:
            speak += "un quart"
            next_hour = True
        elif dt.minute < 20:
            speak += "un quart tocat"
            next_hour = True
        elif dt.minute < 22:
            speak += "un quart ben tocat"
            next_hour = True
        elif dt.minute < 24:
            speak += "un quart i mig"
            next_hour = True
        elif dt.minute < 27:
            speak += "un quart i mig passat"
            next_hour = True
        elif dt.minute < 29:
            speak += "un quart i mig ben passat"
            next_hour = True
        elif dt.minute < 32:
            speak += "dos quarts"
            next_hour = True
        elif dt.minute < 35:
            speak += "dos quarts tocats"
            next_hour = True
        elif dt.minute < 37:
            speak += "dos quarts ben tocats"
            next_hour = True
        elif dt.minute < 39:
            speak += "dos quarts i mig"
            next_hour = True
        elif dt.minute < 42:
            speak += "dos quarts i mig passats"
            next_hour = True
        elif dt.minute < 44:
            speak += "dos quarts i mig ben passats"
            next_hour = True
        elif dt.minute < 47:
            speak += "tres quarts"
            next_hour = True
        elif dt.minute < 50:
            speak += "tres quarts tocats"
            next_hour = True
        elif dt.minute < 52:
            speak += "tres quarts ben tocats"
            next_hour = True
        elif dt.minute < 54:
            speak += "tres quarts i mig"
            next_hour = True
        elif dt.minute < 57:
            speak += "tres quarts i mig passats"
            next_hour = True
        elif dt.minute < 59:
            speak += "tres quarts i mig ben passats"
            next_hour = True
        elif dt.minute == 59:
            next_hour = False

        if next_hour == True:
            next_hour = (dt.hour + 1) % 12
            if next_hour == 0:
                speak += " de dotze"
                if dt.hour == 11:
                    speak += " del migdia"
                else:
                    speak += " de la nit"

            elif next_hour == 1:
                speak += " d'una"
                if dt.hour == 12:
                    speak += " de la tarda"
                else:
                    speak += " de la matinada"
            elif next_hour == 2:
                speak += " de dues"
                if dt.hour == 13:
                    speak += " de la tarda"
                else:
                    speak += " de la nit"

            elif next_hour == 11:
                speak += " d'onze"
                if dt.hour == 22:
                    speak += " de la nit"
                else:
                    speak += " del matí"
            else:
                speak += " de " + pronounce_number_ca(next_hour)
                if dt.hour == 0 and dt.hour < 5:
                    speak += " de la matinada"
                elif dt.hour >= 5 and dt.hour < 11:
                    speak += " del matí"
                elif dt.hour == 11:
                    speak += " del migdia"
                elif dt.hour >= 12 and dt.hour <= 17:
                    speak += " de la tarda"
                elif dt.hour >= 18 and dt.hour < 20:
                    speak += " del vespre"
                elif dt.hour >= 21 and dt.hour <= 23:
                    speak += " de la nit"

        else:
            hour = dt.hour % 12
            if dt.minute == 59:
                hour = (hour + 1) % 12
            if hour == 0:
                speak += "les dotze"
            elif hour == 1:
                speak += "la una"
            elif hour == 2:
                speak += "les dues"
            else:
                speak += "les " + pronounce_number_ca(hour)

            if dt.minute == 0:
                speak += " en punt"
            elif dt.minute > 1 and dt.minute < 5:
                if hour == 1:
                    speak += " tocada"
                else:
                    speak += " tocades"
            elif dt.minute < 7:
                if hour == 1:
                    speak += " ben tocada"
                else:
                    speak += " ben tocades"

            if dt.hour == 0:
                if hour == 1:
                    speak += " de la matinada"
                else:
                    speak += " de la nit"
            elif dt.hour < 6:
                if hour == 6:
                    speak += " del matí"
                else:
                    speak += " de la matinada"
            elif dt.hour < 12:
                if hour == 12:
                    speak += " del migdia"
                else:
                    speak += " del matí"
            elif dt.hour == 12:
                if hour == 1:
                    speak += " de la tarda"
                else:
                    speak += " del migdia"
            elif dt.hour < 19:
                if hour == 7:
                    speak += " del vespre"
                else:
                    speak += " de la tarda"
            elif dt.hour < 21:
                if hour == 9:
                    speak += " de la nit"
                else:
                    speak += " del vespre"
            elif dt.hour <= 23:
                speak += " de la nit"

    elif variant == TimeVariantCA.SPANISH_LIKE:
        # Prepare for "tres menys quart" ??
        if dt.minute == 35:
            minute = -25
            hour = dt.hour + 1
        elif dt.minute == 40:
            minute = -20
            hour = dt.hour + 1
        elif dt.minute == 45:
            minute = -15
            hour = dt.hour + 1
        elif dt.minute == 50:
            minute = -10
            hour = dt.hour + 1
        elif dt.minute == 55:
            minute = -5
            hour = dt.hour + 1
        else:
            minute = dt.minute
            hour = dt.hour

        if hour == 0 or hour == 12:
            speak += "les dotze"
        elif hour == 1 or hour == 13:
            speak += "la una"
        elif hour < 13:
            speak = "les " + pronounce_number_ca(hour)
        else:
            speak = "les " + pronounce_number_ca(hour - 12)

        if minute != 0:
            # les hores especials
            if minute == 15:
                speak += " i quart"
            elif minute == 30:
                speak += " i mitja"
            elif minute == -15:
                speak += " menys quart"
            else:  # sis i nou. set i veint-i-cinc
                if minute > 0:
                    speak += " i " + pronounce_number_ca(minute)
                else:  # si son las set menys vint, no posem la "i"
                    speak += " " + pronounce_number_ca(minute)

    # Default Watch Time Sytem
    else:
        if use_24hour:
            # simply speak the number
            if dt.hour == 1:
                speak += "la una"
            elif dt.hour == 2:
                speak += "les dues"
            elif dt.hour == 21:
                speak += "les vint-i-una"
            elif dt.hour == 22:
                speak += "les vint-i-dues"
            else:
                speak += "les " + pronounce_number_ca(dt.hour)

            if dt.minute > 0:
                speak += " i " + pronounce_number_ca(dt.minute)

        else:
            # speak number and add daytime identifier
            # (equivalent to "in the morning")
            if dt.hour == 0:
                speak += "les dotze"
            # 1 and 2 are pronounced in female form when talking about hours
            elif dt.hour == 1 or dt.hour == 13:
                speak += "la una"
            elif dt.hour == 2 or dt.hour == 14:
                speak += "les dues"
            elif dt.hour < 13:
                speak = "les " + pronounce_number_ca(dt.hour)
            else:
                speak = "les " + pronounce_number_ca(dt.hour - 12)

            # exact time
            if dt.minute == 0:
                # 3:00
                speak += " en punt"
            # else
            else:
                speak += " i " + pronounce_number_ca(dt.minute)

            # TODO: review day-periods
            if use_ampm:
                if dt.hour == 0:
                    speak += " de la nit"
                elif dt.hour >= 1 and dt.hour < 6:
                    speak += " de la matinada"
                elif dt.hour >= 6 and dt.hour < 12:
                    speak += " del matí"
                elif dt.hour == 12:
                    speak += " del migdia"
                elif dt.hour >= 13 and dt.hour <= 18:
                    speak += " de la tarda"
                elif dt.hour >= 19 and dt.hour < 21:
                    speak += " del vespre"
                elif dt.hour != 0 and dt.hour != 12:
                    speak += " de la nit"
    return speak
