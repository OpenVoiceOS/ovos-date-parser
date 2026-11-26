from ovos_number_parser.numbers_de import pronounce_number_de


def nice_time_de(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format
    For example, generate 'ein uhr eins' for speech or '01:01 Uhr' for
    text display.
    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)=Fal
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
    Returns:
        (str): The formatted time string
    """
    string = ""
    if not speech:
        if use_24hour:
            string = f"{dt.strftime('%H:%M')} uhr"
        else:
            string = f"{dt.strftime('%I:%M')} uhr"

    # Generate a speakable version of the time"
    elif use_24hour:
        if dt.hour == 1:
            string += "ein"  # 01:00 is "ein Uhr" not "eins Uhr"
        else:
            string += pronounce_number_de(dt.hour)
        string += " uhr"
        if not dt.minute == 0:  # zero minutes are not pronounced
            string += " " + pronounce_number_de(dt.minute)
    else:
        next_hour = (dt.hour + 1) % 12 or 12
        if dt.hour == 0 and dt.minute == 0:
            return "mitternacht"
        elif dt.hour == 12 and dt.minute == 0:
            return "mittag"
        elif dt.minute == 15:
            string = "viertel " + pronounce_number_de(next_hour)
        elif dt.minute == 30:
            string = "halb " + pronounce_number_de(next_hour)
        elif dt.minute == 45:
            string = "dreiviertel " + pronounce_number_de(next_hour)
        else:
            hour = dt.hour % 12
            if hour == 1:  # 01:00 and 13:00 is "ein Uhr" not "eins Uhr"
                string += 'ein'
            else:
                string += pronounce_number_de(hour)
            string += " uhr"

            if not dt.minute == 0:
                string += " " + pronounce_number_de(dt.minute)

    if use_ampm:
        if 3 <= dt.hour < 12:
            string += " morgens"  # 03:00 - 11:59 morgens/in the morning
        elif 12 <= dt.hour < 18:
            string += " nachmittags"  # 12:01 - 17:59 nachmittags/afternoon
        elif 18 <= dt.hour < 22:
            string += " abends"  # 18:00 - 21:59 abends/evening
        else:
            string += " nachts"  # 22:00 - 02:59 nachts/at night

    return string
