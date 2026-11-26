from ovos_number_parser.numbers_cs import pronounce_number_cs


#: The hundreds as ÚJČ declines "sto": "dvě stě", then "tři sta", then
#: "pět set" (Internetová jazyková příručka, heslo "sto").
_HUNDREDS_CS = {1: "sto", 2: "dvě stě", 3: "tři sta", 4: "čtyři sta",
                5: "pět set", 6: "šest set", 7: "sedm set", 8: "osm set",
                9: "devět set"}
#: The masculine count before "tisíc", a masculine noun (ÚJČ, heslo "tisíc").
_THOUSANDS_CS = {1: "tisíc", 2: "dva tisíce", 3: "tři tisíce",
                 4: "čtyři tisíce", 5: "pět tisíc", 6: "šest tisíc",
                 7: "sedm tisíc", 8: "osm tisíc", 9: "devět tisíc"}


def nice_year_cs(dt, bc=False):
    """Format a year as Czech reads it: a cardinal number.

    CLDR 49 RBNF cs reads a year with ``%spellout-numbering``: 1988 is
    "tisíc devět set osmdesát osm" and 2018 is "dva tisíce osmnáct".
    The tens and units below a hundred keep the counting form of
    pronounce_number_cs ("dvacet jedna"), the form ÚJČ writes for a number
    in words (Internetová jazyková příručka, id=791). An astronomical year
    below 1 is read by pronounce_number_cs as it stands.

    Args:
        dt (datetime): date whose year to format
        bc (bool): append "př. n. l." after the year
    Returns:
        (str): the year in words
    """
    if dt.year < 1:
        year = pronounce_number_cs(dt.year)
        return f"{year} př. n. l." if bc else year
    thousands, rest = divmod(dt.year, 1000)
    hundreds, below = divmod(rest, 100)
    words = []
    if thousands:
        words.append(_THOUSANDS_CS[thousands])
    if hundreds:
        words.append(_HUNDREDS_CS[hundreds])
    if below:
        words.append(pronounce_number_cs(below))
    year = " ".join(words)
    return f"{year} př. n. l." if bc else year


def nice_time_cs(dt, speech=True, use_24hour=True, use_ampm=False):
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
            speak += pronounce_number_cs(int(string[0])) + " "
            speak += pronounce_number_cs(int(string[1]))
        else:
            speak = pronounce_number_cs(int(string[0:2]))

        speak += " "
        if string[3:5] == '00':
            speak += "sto"
        else:
            if string[3] == '0':
                speak += pronounce_number_cs(0) + " "
                speak += pronounce_number_cs(int(string[4]))
            else:
                speak += pronounce_number_cs(int(string[3:5]))
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "půlnoc"
        elif dt.hour == 12 and dt.minute == 0:
            return "poledne"

        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        if dt.minute == 15:
            speak = "čtvrt po " + pronounce_number_cs(hour)
        elif dt.minute == 30:
            speak = "půl po " + pronounce_number_cs(hour)
        elif dt.minute == 45:
            next_hour = (dt.hour + 1) % 12 or 12
            speak = "třičtvrtě na " + pronounce_number_cs(next_hour)
        else:
            speak = pronounce_number_cs(hour)

            if dt.minute == 0:
                if not use_ampm:
                    return speak + " hodin"
            else:
                if dt.minute < 10:
                    speak += " oh"
                speak += " " + pronounce_number_cs(dt.minute)

        if use_ampm:
            if dt.hour > 11:
                speak += " p.m."
            else:
                speak += " a.m."

        return speak
