from ovos_number_parser.numbers_fr import pronounce_number_fr


def nice_time_fr(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format

    For example, generate 'cinq heures trente' for speech or '5:30' for
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
    speak = ""
    if use_24hour:

        # "13 heures trente"
        if dt.hour == 0:
            speak += "minuit"
        elif dt.hour == 12:
            speak += "midi"
        elif dt.hour == 1:
            speak += "une heure"
        else:
            speak += pronounce_number_fr(dt.hour) + " heures"

        if dt.minute != 0:
            speak += " " + pronounce_number_fr(dt.minute)

    else:
        # Prepare for "trois heures moins le quart"
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

        if hour == 0:
            speak += "minuit"
        elif hour == 12:
            speak += "midi"
        elif hour == 1 or hour == 13:
            speak += "une heure"
        elif hour < 13:
            speak = pronounce_number_fr(hour) + " heures"
        else:
            speak = pronounce_number_fr(hour - 12) + " heures"

        if minute != 0:
            if minute == 15:
                speak += " et quart"
            elif minute == 30:
                speak += " et demi"
            elif minute == -15:
                speak += " moins le quart"
            else:
                speak += " " + pronounce_number_fr(minute)

        if use_ampm:
            if hour > 17:
                speak += " du soir"
            elif hour > 12:
                speak += " de l'après-midi"
            elif hour > 0 and hour < 12:
                speak += " du matin"

    return speak
