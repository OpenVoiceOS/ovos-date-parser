from ovos_number_parser.numbers_da import pronounce_number_da


def nice_time_da(dt, speech=True, use_24hour=False, use_ampm=False):
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

    if not speech:
        return string

    # Generate a speakable version of the time
    speak = ""
    if use_24hour:
        if dt.hour == 1:
            speak += "et"  # 01:00 is "et" not "en"
        else:
            speak += pronounce_number_da(dt.hour)
        if not dt.minute == 0:
            if dt.minute < 10:
                speak += ' nul'
            speak += " " + pronounce_number_da(dt.minute)

        return speak  # ampm is ignored when use_24hour is true
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "midnat"
        if dt.hour == 12 and dt.minute == 0:
            return "middag"

        # idiomatic quarter/half hours: "kvart over tre" (3:15), "halv fire"
        # (3:30 - counts towards the NEXT hour, not "half past three"),
        # "kvart i fire" (3:45). This is how these times are normally
        # spoken in Danish, not as two separate digits.
        hour12 = dt.hour % 12 or 12
        nextHour12 = (hour12 % 12) + 1

        def _speakHour(h):
            return 'et' if h == 1 else pronounce_number_da(h)

        if dt.minute == 15:
            speak += "kvart over " + _speakHour(hour12)
        elif dt.minute == 30:
            speak += "halv " + _speakHour(nextHour12)
        elif dt.minute == 45:
            speak += "kvart i " + _speakHour(nextHour12)
        else:
            if dt.hour == 0:
                speak += pronounce_number_da(12)
            elif dt.hour <= 13:
                if dt.hour == 1 or dt.hour == 13:  # 01:00 and 13:00 is "et"
                    speak += 'et'
                else:
                    speak += pronounce_number_da(dt.hour)
            else:
                speak += pronounce_number_da(dt.hour - 12)

            if not dt.minute == 0:
                if dt.minute < 10:
                    speak += ' nul'
                speak += " " + pronounce_number_da(dt.minute)

        if use_ampm:
            if dt.hour > 11:
                if dt.hour < 18:
                    # 12:01 - 17:59 nachmittags/afternoon
                    speak += " om eftermiddagen"
                elif dt.hour < 22:
                    # 18:00 - 21:59 abends/evening
                    speak += " om aftenen"
                else:
                    # 22:00 - 23:59 nachts/at night
                    speak += " om natten"
            elif dt.hour < 3:
                # 00:01 - 02:59 nachts/at night
                speak += " om natten"
            else:
                # 03:00 - 11:59 morgens/in the morning
                speak += " om morgenen"

        return speak
