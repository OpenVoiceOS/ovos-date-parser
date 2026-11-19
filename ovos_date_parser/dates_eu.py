from ovos_number_parser.numbers_eu import pronounce_number_eu
from ovos_date_parser.common import _translate_word

# Euskaltzaindia Araua 35, "Orduak nola esan", decision 1: "ordu bata, ordu
# biak, hirurak, laurak, bostak, seiak, zazpiak"
HOUR_STRING_EU = {
    1: 'ordu bata',
    2: 'ordu biak',
    3: 'hirurak',
    4: 'laurak',
    5: 'bostak',
    6: 'seiak',
    7: 'zazpiak',
    8: 'zortziak',
    9: 'bederatziak',
    10: 'hamarrak',
    11: 'hamaikak',
    12: 'hamabiak'
}


def nice_time_eu(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format

    For example, generate 'cinco treinta' for speech or '5:30' for
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
        # Araua 35, section 5 c), the formal reading: "Hamabostak eta
        # bostean", "Zero ordua / orena eta hogeita hamarrean". Only hiru and
        # lau keep the old -r- (EBE, "lau (4) eta hiru (3) zenbakiak"), so 13
        # is "hamahiruak"
        if dt.hour == 0:
            speak = "zero ordua"
        elif dt.hour <= 12:
            speak = HOUR_STRING_EU[dt.hour]
        else:
            speak = pronounce_number_eu(dt.hour) + "ak"
        if dt.minute:
            speak += " eta " + pronounce_number_eu(dt.minute)

    else:
        minute = dt.minute
        hour = dt.hour

        _hour = hour
        if _hour == 0:
            _hour = 12
        if _hour > 12:
            _hour -= 12

        if (minute > 30):
            # counts down to the next hour, and 12 is followed by 1
            _hour = _hour % 12 + 1

        speak = HOUR_STRING_EU[_hour]

        if minute != 0:
            if minute <= 30:
                if minute == 15:
                    speak += " eta laurden"
                elif minute == 30:
                    # Araua 35, decision 2: the plural mark goes on erdi only,
                    # "ordu bat eta erdiak", "hiru eta erdiak"
                    hour_number = {1: "ordu bat", 2: "ordu bi"}.get(
                        _hour, pronounce_number_eu(_hour))
                    speak = f"{hour_number} eta erdiak"
                else:
                    speak += " eta " + pronounce_number_eu(minute)
            else:
                if minute == 45:
                    speak += " laurden gutxi"
                else:
                    speak += " " + pronounce_number_eu(60 - minute) + " gutxi"

        # si no especificamos de la tarde, noche, mañana, etc
        if minute == 0 and not use_ampm:
            # 3:00
            speak += " puntuan"

        if use_ampm:
            # The part of the day belongs to the hour that is said, which is
            # the next hour after half past. Araua 35 and the EBE entry
            # "orduak nola esan": "gaueko hamabiak" (00:00), "goiz(ald)eko
            # ordu bata" (01:00), "goizeko 11,30etan", "Eguardiko amabiak
            # laurden gutxitan", "arratsaldeko 5etan", "iluntzeko 8etatik 11k
            # arte"
            said_hour = (hour + 1 if minute > 30 else hour) % 24
            if said_hour == 0:
                speak = "gaueko " + speak
            elif said_hour < 12:
                speak = "goizeko " + speak
            elif said_hour == 12:
                speak = "eguerdiko " + speak
            elif said_hour < 20:
                speak = "arratsaldeko " + speak
            else:
                speak = "iluntzeko " + speak
    return speak
    # hemen dago tranpa
    # return str(dt.hour) + ":" + str(dt.minute)


def nice_time_inessive_eu(dt, use_24hour=False, use_ampm=False):
    """Format a time in the inessive case, the "at" form of a date and time.

    The forms follow Euskaltzaindia Araua 35, "Orduak nola esan": the hour
    takes the plural inessive ("ordu batean", "bietan", "hiruretan"), erdi
    and laurden take it after "eta" ("bost eta erdietan", "hirurak eta
    laurdenetan"), "gutxi" takes -tan ("bostak laurden gutxitan"), and a
    minute takes the singular inessive ("seiak eta bostean", "laurak eta
    hogeian"). "puntuan" follows the inflected hour ("zazpietan puntuan",
    Elhuyar, "en punto").

    Args:
        dt (datetime): time to format
        use_24hour (bool): output in 24-hour format
        use_ampm (bool): include the part of the day for 12-hour format
    Returns:
        (str): the time in the inessive case
    """
    time = nice_time_eu(dt, use_24hour=use_24hour, use_ampm=use_ampm)
    on_the_hour = time.endswith(" puntuan")
    if on_the_hour:
        time = time[:-len(" puntuan")]
    if time.endswith(" gutxi"):
        time += "tan"
    elif time.endswith(" erdiak"):
        time = time[:-len("ak")] + "etan"
    elif time.endswith(" laurden"):
        time += "etan"
    elif " eta " in time:
        if time.endswith("r"):
            time += "rean"
        elif time.endswith("a"):
            time += "n"
        elif time.endswith(("e", "i", "o", "u")):
            time += "an"
        else:
            time += "ean"
    elif time.endswith("ordu bata"):
        time = time[:-len("a")] + "ean"
    elif time == "zero ordua":
        time += "n"
    else:
        time = time[:-len("ak")] + "etan"
    if on_the_hour:
        time += " puntuan"
    return time


def nice_year_eu(dt, bc=False):
    """Format a year in a pronounceable Basque form.

    Args:
        dt (datetime): date to format (assumed already in the local timezone)
        bc (bool): append "k.a." after the year
    Returns:
        (str): the year formatted as a string
    """
    year = pronounce_number_eu(dt.year)
    if bc:
        return f"{year} k.a."
    return year


def nice_date_year_eu(dt):
    """Format the year of a date with the -ko suffix of Basque dates.

    Euskaltzaindia, Araua 37 ("Data nola adierazi") writes the year as
    "1983ko" and "1995eko": the suffix is -ko after a vowel and -eko after
    a consonant, where a final r doubles ("hamarreko").

    Args:
        dt (datetime): date whose year to format
    Returns:
        (str): the year in words with its suffix
    """
    year = pronounce_number_eu(dt.year)
    if year[-1] in "aeiou":
        return f"{year}ko"
    if year[-1] == "r":
        return f"{year}reko"
    return f"{year}eko"


def nice_date_day_eu(dt):
    """Format the day of a date with the article of Basque dates.

    Euskaltzaindia, Araua 37 ("Data nola adierazi"), writes the day with the
    article -a: "1995eko martxoaren 7a(n)", "urtarrilaren 20a". Only the
    inessive -n is optional. A word that ends in -a takes no second -a
    ("hamaika"), and a final r doubles ("hamarra").

    Args:
        dt (datetime): date whose day to format
    Returns:
        (str): the day in words with its article
    """
    day = pronounce_number_eu(dt.day)
    if day[-1] == "a":
        return day
    if day[-1] == "r":
        return f"{day}ra"
    return f"{day}a"


def nice_relative_time_eu(when, relative_to):
    """Create a relative phrase to roughly describe a datetime

    Examples are "25 seconds", "tomorrow", "7 days".

    Args:
        when (datetime): Local timezone
        relative_to (datetime): Baseline for relative time
    Returns:
        str: Relative description of the given time
    """
    delta = when - relative_to

    seconds = delta.total_seconds()
    if seconds < 1:
        try:
            return _translate_word("now", "eu")
        except NotImplementedError:
            nice = pronounce_number_eu(0)
            return f"{nice} " + _translate_word("seconds", "eu")

    if seconds < 90:
        nice = pronounce_number_eu(seconds)
        s = _translate_word("second", "eu")
        if seconds == 1:
            return f"{s} bat"
        else:
            return f"{nice} {s}"

    minutes = int((delta.total_seconds() + 30) // 60)  # +30 to round minutes
    if minutes < 90:
        nice = pronounce_number_eu(minutes)
        s = _translate_word("minute", "eu")
        if minutes == 1:
            return f"{s} bat"
        else:
            return f"{nice} {s}"

    hours = int((minutes + 30) // 60)  # +30 to round hours
    if hours < 36:
        nice = pronounce_number_eu(hours)
        s = _translate_word("hour", "eu")
        if hours == 1:
            return f"{s} bat"
        else:
            return f"{nice} {s}"

    # TODO: "2 weeks", "3 months", "4 years", etc
    days = int((hours + 12) // 24)  # +12 to round days
    nice = pronounce_number_eu(days)
    s = _translate_word("day", "eu")
    if days == 1:
        return f"{s} bat"
    else:
        return f"{nice} {s}"
