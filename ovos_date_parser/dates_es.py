from datetime import datetime, timedelta

from ovos_number_parser.numbers_es import pronounce_number_es
from ovos_utils.time import now_local

# Lowercase, as the Ortografía de la lengua española (RAE and ASALE, 2010)
# writes the names of days and months. The locator p. 502 comes from a
# classroom digest that cites the book; the book itself was not read.
WEEKDAYS_ES = {
    0: "lunes",
    1: "martes",
    2: "miércoles",
    3: "jueves",
    4: "viernes",
    5: "sábado",
    6: "domingo"
}
MONTHS_ES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre"
}


def nice_year_es(dt, bc=False):
    """
        Formatea un año en una forma pronunciable.

        Por ejemplo, genera 'mil novecientos ochenta y cuatro' para el año 1984.

        Args:
            dt (datetime): fecha a formatear (se supone que ya está en la zona horaria local)
            bc (bool): añade a.C. después del año (Python no soporta fechas a.C. en datetime)
        Returns:
            (str): El año formateado como cadena
    """
    year = pronounce_number_es(dt.year)
    if bc:
        return f"{year} a.C."
    return year


def nice_weekday_es(dt):
    return WEEKDAYS_ES[dt.weekday()]


def nice_month_es(dt):
    return MONTHS_ES[dt.month]


def nice_day_es(dt, date_format='DMY', include_month=True):
    if include_month:
        month = nice_month_es(dt)
        # Unicode CLDR es, availableFormats MMMMd: "d 'de' MMMM", with the
        # day unpadded
        if date_format == 'MDY':
            return f"{month} {dt.day}"
        else:
            return f"{dt.day} de {month}"
    return dt.strftime("%d")


def nice_date_time_es(dt, now=None, use_24hour=False,
                      use_ampm=False):
    """
        Formatea una fecha y hora de manera pronunciable.

        Por ejemplo, genera 'martes, cinco de junio de 2018 a las cinco y media'.

        Args:
            dt (datetime): fecha a formatear (se supone que ya está en la zona horaria local)
            now (datetime): Fecha actual. Si se proporciona, la fecha devuelta se acortará en consecuencia:
                No se devuelve el año si ahora está en el mismo año que `dt`, no se devuelve el mes
                si ahora está en el mismo mes que `dt`. Si `now` y `dt` son el mismo día, se devuelve 'hoy'.
            use_24hour (bool): salida en formato de 24 horas/militar o 12 horas
            use_ampm (bool): incluir el am/pm en formato de 12 horas
        Returns:
            (str): La cadena de fecha y hora formateada
    """
    now = now or now_local()
    # nice_time_es starts with the article: a la una, a las dos
    return f"{nice_date_es(dt, now)} a {nice_time_es(dt, use_24hour=use_24hour, use_ampm=use_ampm)}"


def nice_date_es(dt: datetime, now: datetime = None, include_weekday=True):
    """
    Formatea una fecha en una forma pronunciable.

    Por ejemplo, genera 'martes, cinco de junio de 2018'.

    Args:
        dt (datetime): fecha a formatear (se supone que ya está en la zona horaria local)
        now (datetime): Fecha actual. Si se proporciona, la fecha devuelta se acortará en consecuencia:
            No se devuelve el año si ahora está en el mismo año que `dt`, no se devuelve el mes
            si ahora está en el mismo mes que `dt`. Si `now` y `dt` son el mismo día, se devuelve 'hoy'.
        include_weekday (bool, optional): Whether to include the weekday name in the output. Defaults to True.

    Returns:
        (str): La cadena de fecha formateada
    """
    day = pronounce_number_es(dt.day)
    if now is not None:
        nice = day
        if dt.date() == now.date():
            return "hoy"
        if dt.date() == now.date() + timedelta(days=1):
            return "mañana"
        if dt.date() == now.date() - timedelta(days=1):
            return "ayer"
        if dt.month != now.month or dt.year != now.year:
            nice = nice + " de " + nice_month_es(dt)
        if dt.year != now.year:
            nice = nice + " de " + nice_year_es(dt)
    else:
        nice = f"{day} de {nice_month_es(dt)} de {nice_year_es(dt)}"

    if include_weekday:
        weekday = nice_weekday_es(dt)
        nice = f"{weekday}, {nice}"
    return nice


def nice_time_es(dt, speech=True, use_24hour=False, use_ampm=False):
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
        # Tenemos que tener en cuenta que cuando hablamos en formato
        # 24h, no hay que especificar ninguna precisión adicional
        # como "la noche", "la tarde" o "la mañana"
        # http://lema.rae.es/dpd/srv/search?id=YNoTWNJnAD6bhhVBf9
        if dt.hour == 1:
            speak += "la una"
        else:
            speak += "las " + pronounce_number_es(dt.hour)

        # las 14:04 son "las catorce cero cuatro"
        if dt.minute < 10:
            speak += " cero " + pronounce_number_es(dt.minute)
        else:
            speak += " " + pronounce_number_es(dt.minute)

    else:
        # Prepare for "tres menos cuarto" ??
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

        if hour == 0 or hour == 12:
            speak += "las doce"
        elif hour == 1 or hour == 13:
            speak += "la una"
        elif hour < 13:
            speak = "las " + pronounce_number_es(hour)
        else:
            speak = "las " + pronounce_number_es(hour - 12)

        if minute != 0:
            # las horas especiales
            if minute == 15:
                speak += " y cuarto"
            elif minute == 30:
                speak += " y media"
            elif minute == -15:
                speak += " menos cuarto"
            else:  # seis y nueve. siete y veinticinco
                if minute > 0:
                    speak += " y " + pronounce_number_es(minute)
                else:  # si son las siete menos veinte, no ponemos la "y"
                    speak += " " + pronounce_number_es(minute)

        # si no especificamos de la tarde, noche, mañana, etc
        if minute == 0 and not use_ampm:
            # 3:00
            speak += " en punto"

        if use_ampm:
            # "de la noche" es desde que anochece hasta medianoche
            # así que decir que es desde las 21h es algo subjetivo
            # en España a las 20h se dice "de la tarde"
            # en castellano, las 12h es de la mañana o mediodía
            # así que diremos "de la tarde" a partir de las 13h.
            # http://lema.rae.es/dpd/srv/search?id=YNoTWNJnAD6bhhVBf9
            if hour >= 0 and hour < 6:
                speak += " de la madrugada"
            elif hour >= 6 and hour < 13:
                speak += " de la mañana"
            elif hour >= 13 and hour < 21:
                speak += " de la tarde"
            else:
                speak += " de la noche"
    return speak
