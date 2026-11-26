from ovos_number_parser.numbers_hr import pronounce_number_hr


def _plural_sat_hr(hour):
    """Return the correct declension of 'sat' (hour) for a cardinal count."""
    if hour == 1:
        return "sat"
    if 2 <= hour <= 4:
        return "sata"
    return "sati"


def nice_time_hr(dt, speech=True, use_24hour=False, use_ampm=False,
                 variant=None):
    """
    Format a time to a comfortable human format

    For example, generate 'osam i trideset' (default) or 'pola devet'
    (traditional) for speech, or '8:30' for text display.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
        variant (str): spoken register for the 12-hour clock. The default
            (None / "default") reads "<hour> i <minutes>". "traditional"
            uses the analog idiom ("osam i petnaest" = 8:15,
            "pola devet" = 8:30, "petnaest do devet" = 8:45).
    Returns:
        (str): The formatted time string
    """
    traditional = variant in ("traditional", "analog")
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
    if use_24hour:
        # "trinaest dvadeset dva"
        speak = pronounce_number_hr(int(string[0:2]))
        speak += " "
        if string[3:5] == '00':
            speak += "nula nula"
        else:
            if string[3] == '0':
                speak += pronounce_number_hr(0) + " "
                speak += pronounce_number_hr(int(string[4]))
            else:
                speak += pronounce_number_hr(int(string[3:5]))
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "ponoć"
        elif dt.hour == 12 and dt.minute == 0:
            return "podne"

        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        next_hour = (dt.hour + 1) % 12 or 12
        if dt.minute == 0:
            speak = pronounce_number_hr(hour) + " " + _plural_sat_hr(hour)
        elif traditional and dt.minute == 30:
            speak = "pola " + pronounce_number_hr(next_hour)
        elif traditional and dt.minute == 45:
            speak = "petnaest do " + pronounce_number_hr(next_hour)
        else:
            speak = pronounce_number_hr(hour) + " i " + \
                pronounce_number_hr(dt.minute)

        if use_ampm:
            if dt.hour > 11:
                speak += " p.m."
            else:
                speak += " a.m."

        return speak
