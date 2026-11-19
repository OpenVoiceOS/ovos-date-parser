import re
from datetime import datetime
from datetime import timedelta

from ovos_number_parser.numbers_ast import AST
from ovos_utils.time import now_local

WEEKDAYS_AST = {
    0: "llunes",
    1: "martes",
    2: "miércoles",
    3: "xueves",
    4: "vienres",
    5: "sábadu",
    6: "domingu"
}
MONTHS_AST = {
    1: "xineru",
    2: "febreru",
    3: "marzu",
    4: "abril",
    5: "mayu",
    6: "xunu",
    7: "xunetu",
    8: "agostu",
    9: "setiembre",
    10: "ochobre",
    11: "payares",
    12: "avientu"
}


def pronounce_number_ast(number, **kwargs):
    return AST.pronounce_number(number, **kwargs)


def nice_year_ast(dt, bc=False):
    """
        Formatea un añu nuna forma pronunciable.

        Args:
            dt (datetime): data a formatear (asúmese que yá ta na zona horaria llocal)
            bc (bool): amiesta a.C. dempués del añu
        Returns:
            (str): L'añu formateáu como cadena
    """
    year = pronounce_number_ast(dt.year)
    if bc:
        return f"{year} a.C."
    return year


def nice_weekday_ast(dt):
    weekday = WEEKDAYS_AST[dt.weekday()]
    return weekday.capitalize()


def nice_month_ast(dt):
    month = MONTHS_AST[dt.month]
    return month.capitalize()


def nice_day_ast(dt, date_format='DMY', include_month=True):
    if include_month:
        month = nice_month_ast(dt)
        if date_format == 'MDY':
            return "{} {}".format(month, dt.strftime("%d").lstrip("0"))
        else:
            return "{} {}".format(dt.strftime("%d").lstrip("0"), month)
    return dt.strftime("%d").lstrip("0")


def nice_date_time_ast(dt, now=None, use_24hour=False, use_ampm=False):
    """
        Formatea una data y hora de manera pronunciable.

        Por exemplu, xenera 'martes, cinco de xunu de 2018 a les cinco y media'.

        Args:
            dt (datetime): data a formatear (asúmese que yá ta na zona horaria llocal)
            now (datetime): Data actual. Si se proporciona, la data devuelta acurtiaráse.
            use_24hour (bool): salida en formatu de 24 hores o 12 hores
            use_ampm (bool): incluyir el am/pm en formatu de 12 hores
        Returns:
            (str): La cadena de data y hora formateada
    """
    now = now or now_local()
    # nice_time_ast yá inclúi l'artículu ("la una", "les cinco")
    return f"{nice_date_ast(dt, now)} a {nice_time_ast(dt, use_24hour=use_24hour, use_ampm=use_ampm)}"


def _de_month_ast(dt):
    """The month after "de", elided to "d'" before a vowel, as the CLDR ast
    format months write it: "de xineru", "d’abril", "d’agostu"."""
    month = nice_month_ast(dt)
    if month[0].lower() in "aeiou":
        return f"d'{month}"
    return f"de {month}"


def nice_date_ast(dt: datetime, now: datetime = None, include_weekday=True):
    """
    Formatea una data nuna forma pronunciable.

    Por exemplu, xenera 'martes, cinco de xunu de 2018'.

    Args:
        dt (datetime): data a formatear (asúmese que yá ta na zona horaria llocal)
        now (datetime): Data actual. Si se proporciona, la data devuelta acurtiaráse:
            Nun se devuelve l'añu si now ta nel mesmu añu que `dt`, nun se devuelve'l mes
            si now ta nel mesmu mes que `dt`. Si `now` y `dt` son el mesmu día,
            devuélvese 'güei'.
        include_weekday (bool, optional): Whether to prepend the weekday name to the formatted date. Defaults to True.

    Returns:
        (str): La cadena de data formateada
    """
    day = pronounce_number_ast(dt.day)
    if now is not None:
        nice = day
        if dt.date() == now.date():
            return "güei"
        if dt.date() == now.date() + timedelta(days=1):
            return "mañana"
        if dt.date() == now.date() - timedelta(days=1):
            return "ayeri"
        if dt.month != now.month or dt.year != now.year:
            nice = nice + " " + _de_month_ast(dt)
        if dt.year != now.year:
            nice = nice + " de " + nice_year_ast(dt)
    else:
        nice = f"{day} {_de_month_ast(dt)} de {nice_year_ast(dt)}"

    if include_weekday:
        weekday = nice_weekday_ast(dt)
        nice = f"{weekday}, {nice}"
    return nice


def nice_time_ast(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Formatea una hora nun formatu humanu comprensible

    Por exemplu, xenera 'les cinco y media' pa la fala o '5:30' pa testu.

    Args:
        dt (datetime): data a formatear (asúmese que yá ta na zona horaria llocal)
        speech (bool): formatu pa la fala (True, por defeutu) o pa testu (False)
        use_24hour (bool): salida en formatu de 24 hores o de 12 hores
        use_ampm (bool): incluyir am/pm pal formatu de 12 hores
    Returns:
        (str): La cadena de testu cola hora formateada
    """
    if use_24hour:
        # ex.: "03:01" o "14:22"
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            # ex.: "3:01 AM" o "2:22 PM"
            string = dt.strftime("%I:%M %p")
        else:
            # ex.: "3:01" o "2:22"
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # desaniciar ceros a la izquierda

    if not speech:
        return string

    # Xenerar una versión falada de la hora
    speak = ""
    if use_24hour:
        if dt.hour == 1:
            speak += "la una"
        else:
            speak += "les " + pronounce_number_ast(dt.hour)

        if dt.minute < 10:
            speak += " cero " + pronounce_number_ast(dt.minute)
        else:
            speak += " " + pronounce_number_ast(dt.minute)

    else:
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
            speak += "les doce"
        elif hour == 1 or hour == 13:
            speak += "la una"
        elif hour < 13:
            speak = "les " + pronounce_number_ast(hour)
        else:
            speak = "les " + pronounce_number_ast(hour - 12)

        if minute != 0:
            if minute == 15:
                speak += " y cuartu"
            elif minute == 30:
                speak += " y media"
            elif minute == -15:
                speak += " menos cuartu"
            else:
                if minute > 0:
                    speak += " y " + pronounce_number_ast(minute)
                else:
                    speak += " " + pronounce_number_ast(minute)

        if minute == 0 and not use_ampm:
            speak += " en puntu"

        if use_ampm:
            if hour >= 0 and hour < 6:
                speak += " de la madrugada"
            elif hour >= 6 and hour < 13:
                speak += " de la mañana"
            elif hour >= 13 and hour < 21:
                speak += " de la tarde"
            else:
                speak += " de la nueche"
    return speak


def extract_duration_ast(text):
    """
    Convierte una frase n'asturianu nun númberu de segundos.
    Convierte coses como:
        "10 minutos"
        "3 díes 8 hores 10 minutos y 49 segundos"
    nun númberu enteru que representa'l total de segundos.
    Les pallabres emplegaes na duración serán consumíes,
    devolviéndose'l testu restante.
    Por exemplu, "pon un temporizador de 5 minutos" devolvería
    (300, "pon un temporizador de").

    Args:
        text (str): cadena de testu que contién una duración

    Returns:
        (timedelta, str):
            Una tupla col tiempu total y el testu restante
            non consumíu nel análisis. El primer valor sedrá
            None si nun s'atopa nenguna duración.
    """
    if not text:
        return None, text

    text = text.lower().replace("í", "i").replace("é", "e")

    time_units = {
        'microseconds': 0,
        'milliseconds': 0,
        'seconds': 0,
        'minutes': 0,
        'hours': 0,
        'days': 0,
        'weeks': 0
    }

    # n'asturianu el plural femenín ye -es (hora > hores, selmana > selmanes)
    # y díes ye'l plural de día, polo que cada unidá lleva'l so propiu patrón
    unit_patterns = {
        'microseconds': r"microsegundos?",
        'milliseconds': r"milisegundos?",
        'seconds': r"segundos?|segundu",
        'minutes': r"minutos?|minutu",
        'hours': r"hores|hora",
        'days': r"dies|dias?",
        'weeks': r"selmanes|selmana"
    }

    non_std_patterns = {
        "months": r"meses|mes",
        "years": r"años?|añu",
        "decades": r"decades|decada",
        "centuries": r"sieglos?|sieglu",
        "millenniums": r"milenios?|mileniu"
    }

    pattern = r"(?P<value>\d+(?:\.?\d+)?)(?:\s+|\-)(?:{unit})\b"

    for unit_en, unit_ast in unit_patterns.items():
        unit_pattern = pattern.format(unit=unit_ast)

        def repl(match):
            time_units[unit_en] += float(match.group("value"))
            return ''

        text = re.sub(unit_pattern, repl, text)

    for unit_en, unit_ast in non_std_patterns.items():
        unit_pattern = pattern.format(unit=unit_ast)

        def repl_non_std(match):
            val = float(match.group("value"))
            if unit_en == "months":
                val = 30 * val  # aproximación d'un mes en díes
            elif unit_en == "years":
                val = 365 * val  # aproximación d'un añu en díes
            elif unit_en == "decades":
                val = 10 * 365 * val
            elif unit_en == "centuries":
                val = 100 * 365 * val
            elif unit_en == "millenniums":
                val = 1000 * 365 * val
            time_units["days"] += val
            return ''

        text = re.sub(unit_pattern, repl_non_std, text)

    text = text.strip()
    duration = timedelta(**time_units) if any(time_units.values()) else None

    return duration, text
