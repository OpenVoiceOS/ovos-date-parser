from ovos_number_parser.numbers_en import pronounce_number_en


def nice_time_en(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format
    For example, generate 'five thirty' for speech or '5:30' for
    text display.
    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)=Fal
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
    Returns:
        (str): The formatted time string
    """
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

        # Either "0 8 hundred" or "13 hundred"
        if string[0] == '0':
            speak += pronounce_number_en(int(string[0])) + " "
            speak += pronounce_number_en(int(string[1]))
        else:
            speak = pronounce_number_en(int(string[0:2]))

        speak += " "
        if string[3:5] == '00':
            speak += "hundred"
        else:
            if string[3] == '0':
                speak += pronounce_number_en(0) + " "
                speak += pronounce_number_en(int(string[4]))
            else:
                speak += pronounce_number_en(int(string[3:5]))
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "midnight"
        elif dt.hour == 12 and dt.minute == 0:
            return "noon"

        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        if dt.minute == 15:
            speak = "quarter past " + pronounce_number_en(hour)
        elif dt.minute == 30:
            speak = "half past " + pronounce_number_en(hour)
        elif dt.minute == 45:
            next_hour = (dt.hour + 1) % 12 or 12
            speak = "quarter to " + pronounce_number_en(next_hour)
        else:
            speak = pronounce_number_en(hour)

            if dt.minute == 0:
                if not use_ampm:
                    return speak + " o'clock"
            else:
                if dt.minute < 10:
                    speak += " oh"
                speak += " " + pronounce_number_en(dt.minute)

        if use_ampm:
            if dt.hour > 11:
                speak += " p.m."
            else:
                speak += " a.m."

        return speak
