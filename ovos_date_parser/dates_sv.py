from ovos_number_parser.numbers_sv import pronounce_number_sv


def nice_year_sv(dt, bc=False):
    """Format a year as Swedish reads it.

    CLDR RBNF sv ``%spellout-numbering-year`` reads 1100 to 9999 in
    hundreds, "1100/100: <<hundra[>>]": 1988 is "nittonhundraåttioåtta".
    Other years read as the cardinal number: 1012 is "ettusentolv".
    Språkrådet writes a number in words as one word: "Övriga tal skrivs
    ihop: tjugofem, femtusentrettio." The era is the CLDR sv eraName
    "före Kristus".

    Args:
        dt (datetime): date whose year to format
        bc (bool): append "före Kristus" after the year
    Returns:
        (str): the year in words
    """
    def words(number):
        return pronounce_number_sv(number).replace(" ", "")

    hundreds, below = divmod(dt.year, 100)
    if 11 <= hundreds <= 99:
        year = words(hundreds) + "hundra" + (words(below) if below else "")
    else:
        year = words(dt.year)
    return f"{year} före Kristus" if bc else year


def nice_time_sv(dt, speech=True, use_24hour=False, use_ampm=False):
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
            speak += "ett"  # 01:00 is "ett" not "en"
        else:
            speak += pronounce_number_sv(dt.hour)
        if not dt.minute == 0:
            if dt.minute < 10:
                speak += ' noll'

            if dt.minute == 1:
                speak += ' ett'
            else:
                speak += " " + pronounce_number_sv(dt.minute)

        return speak  # ampm is ignored when use_24hour is true
    else:
        hour = dt.hour

        if not dt.minute == 0:
            if dt.minute < 30:
                if dt.minute != 15:
                    speak += pronounce_number_sv(dt.minute)
                else:
                    speak += 'kvart'

                if dt.minute == 1:
                    speak += ' minut över '
                elif dt.minute != 10 and dt.minute != 5 and dt.minute != 15:
                    speak += ' minuter över '
                else:
                    speak += ' över '
            elif dt.minute > 30:
                if dt.minute != 45:
                    speak += pronounce_number_sv((60 - dt.minute))
                else:
                    speak += 'kvart'

                if dt.minute == 1:
                    speak += ' minut i '
                elif dt.minute != 50 and dt.minute != 55 and dt.minute != 45:
                    speak += ' minuter i '
                else:
                    speak += ' i '

                hour = (hour + 1) % 12
            elif dt.minute == 30:
                speak += 'halv '
                hour = (hour + 1) % 12

        if hour == 0 and dt.minute == 0:
            return "midnatt"
        if hour == 12 and dt.minute == 0:
            return "middag"
        # TODO: "half past 3", "a quarter of 4" and other idiomatic times

        if hour == 0:
            speak += pronounce_number_sv(12)
        elif hour <= 13:
            if hour == 1 or hour == 13:  # 01:00 and 13:00 is "ett"
                speak += 'ett'
            else:
                speak += pronounce_number_sv(hour)
        else:
            speak += pronounce_number_sv(hour - 12)

        if use_ampm:
            if dt.hour > 11:
                if dt.hour < 18:
                    # 12:01 - 17:59 nachmittags/afternoon
                    speak += " på eftermiddagen"
                elif dt.hour < 22:
                    # 18:00 - 21:59 abends/evening
                    speak += " på kvällen"
                else:
                    # 22:00 - 23:59 nachts/at night
                    speak += " på natten"
            elif dt.hour < 3:
                # 00:01 - 02:59 nachts/at night
                speak += " på natten"
            else:
                # 03:00 - 11:59 morgens/in the morning
                speak += " på morgonen"

        return speak


