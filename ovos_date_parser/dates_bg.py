from ovos_number_parser.numbers_bg import pronounce_number_bg


def nice_time_bg(dt, speech=True, use_24hour=True, use_ampm=False,
                 variant=None):
    """
    Format a time to a comfortable human format

    For example, generate 'осем и тридесет' (default) or 'осем и
    половина' (traditional) for speech, or '8:30' for text display.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
        variant (str): spoken register for the 12-hour clock. The default
            (None / "default") reads "<hour> и <minutes>". "traditional"
            uses the analog idiom ("осем и четвърт" = 8:15, "осем и
            половина" = 8:30, "девет без четвърт" = 8:45).
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
        # "тринадесет двадесет и две"
        speak = pronounce_number_bg(int(string[0:2]))
        speak += " "
        if string[3:5] == '00':
            speak += "нула нула"
        else:
            if string[3] == '0':
                speak += pronounce_number_bg(0) + " "
                speak += pronounce_number_bg(int(string[4]))
            else:
                speak += pronounce_number_bg(int(string[3:5]))
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "полунощ"
        elif dt.hour == 12 and dt.minute == 0:
            return "обед"

        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        next_hour = (dt.hour + 1) % 12 or 12
        if dt.minute == 0:
            unit = "час" if hour == 1 else "часа"
            speak = pronounce_number_bg(hour) + " " + unit
        elif traditional and dt.minute == 15:
            speak = pronounce_number_bg(hour) + " и четвърт"
        elif traditional and dt.minute == 30:
            speak = pronounce_number_bg(hour) + " и половина"
        elif traditional and dt.minute == 45:
            speak = pronounce_number_bg(next_hour) + " без четвърт"
        else:
            speak = pronounce_number_bg(hour) + " и " + \
                pronounce_number_bg(dt.minute)

        if use_ampm:
            if dt.hour > 11:
                speak += " p.m."
            else:
                speak += " a.m."

        return speak
