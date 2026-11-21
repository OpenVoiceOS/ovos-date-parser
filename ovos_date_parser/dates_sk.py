from ovos_number_parser.numbers_sk import pronounce_number_sk


# feminine genitive ordinals, used by the traditional "pol" idiom
# ("pol deviatej" = 8:30, literally "half of the ninth")
_ORDINAL_FEM_GEN_SK = {
    1: "jednej", 2: "druhej", 3: "tretej", 4: "štvrtej", 5: "piatej",
    6: "šiestej", 7: "siedmej", 8: "ôsmej", 9: "deviatej", 10: "desiatej",
    11: "jedenástej", 12: "dvanástej",
}


def nice_time_sk(dt, speech=True, use_24hour=True, use_ampm=False,
                 variant=None):
    """
    Format a time to a comfortable human format

    For example, generate 'osem pätnásť' (default) or 'štvrť na deväť'
    (traditional) for speech, or '8:15' for text display.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
        variant (str): spoken register for the 12-hour clock. The default
            (None / "default") reads the digits plainly. "traditional"
            uses the analog counting-to-the-next-hour idiom
            ("štvrť na deväť" = 8:15, "pol deviatej" = 8:30,
            "trištvrte na deväť" = 8:45), the register still common in
            everyday Slovak speech.
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
        speak = ""
        # Either "0 8 sto" or "13 sto"
        if string[0] == '0':
            speak += pronounce_number_sk(int(string[0])) + " "
            speak += pronounce_number_sk(int(string[1]))
        else:
            speak = pronounce_number_sk(int(string[0:2]))

        speak += " "
        if string[3:5] == '00':
            speak += "sto"
        else:
            if string[3] == '0':
                speak += pronounce_number_sk(0) + " "
                speak += pronounce_number_sk(int(string[4]))
            else:
                speak += pronounce_number_sk(int(string[3:5]))
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "polnoc"
        elif dt.hour == 12 and dt.minute == 0:
            return "poludnie"

        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        next_hour = (dt.hour + 1) % 12 or 12
        if traditional and dt.minute == 15:
            speak = "štvrť na " + pronounce_number_sk(next_hour)
        elif traditional and dt.minute == 30:
            speak = "pol " + _ORDINAL_FEM_GEN_SK[next_hour]
        elif traditional and dt.minute == 45:
            speak = "trištvrte na " + pronounce_number_sk(next_hour)
        else:
            speak = pronounce_number_sk(hour)

            if dt.minute == 0:
                if not use_ampm:
                    return speak + " hodín"
            else:
                if dt.minute < 10:
                    speak += " nula"
                speak += " " + pronounce_number_sk(dt.minute)

        if use_ampm:
            if dt.hour > 11:
                speak += " p.m."
            else:
                speak += " a.m."

        return speak
