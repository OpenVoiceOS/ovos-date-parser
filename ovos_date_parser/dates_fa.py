from ovos_number_parser.numbers_fa import pronounce_number_fa


def nice_time_fa(dt, speech=True, use_24hour=False, use_ampm=False):
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
            speak += pronounce_number_fa(int(string[1]))
        else:
            speak = pronounce_number_fa(int(string[0:2]))
        if not string[3:5] == '00':
            speak += " و "
            if string[3] == '0':
                speak += pronounce_number_fa(int(string[4]))
            else:
                speak += pronounce_number_fa(int(string[3:5]))
            speak += ' دقیقه'
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "نیمه شب"
        elif dt.hour == 12 and dt.minute == 0:
            return "ظهر"

        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        if dt.minute == 15:
            speak = pronounce_number_fa(hour) + " و ربع"
        elif dt.minute == 30:
            speak = pronounce_number_fa(hour) + " و نیم"
        elif dt.minute == 45:
            next_hour = (dt.hour + 1) % 12 or 12
            speak = "یه ربع به " + pronounce_number_fa(next_hour)
        else:
            speak = pronounce_number_fa(hour)

            if dt.minute == 0:
                if not use_ampm:
                    return speak
            else:
                speak += " و " + pronounce_number_fa(dt.minute) + ' دقیقه'

        if use_ampm:
            if dt.hour > 11:
                speak += " بعد از ظهر"
            else:
                speak += " قبل از ظهر"

        return speak
