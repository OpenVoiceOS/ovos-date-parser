"""Date and time tools for Portuguese, European (pt-PT) and Brazilian (pt-BR).

Sources for the rules of the spoken date and time in this module:

The first day of the month. Ciberdúvidas, answer 32700 ("Numerais em
datas"), citing Cunha & Cintra, "Nova Gramática do Português
Contemporâneo", p. 374: "nas referências aos dias do mês usam-se os
cardinais, salvo na designação do primeiro dia, em que é de regra o uso do
numeral ordinal". Its examples: "Chegaremos às seis horas do dia primeiro de
maio", "São duas horas da tarde [...]". So day 1 is "primeiro", every other day a
cardinal, and a whole hour takes the noun: "às seis horas".

The clock with unit words. Ciberdúvidas, answer 14586 ("Minuto"): "20 h 30 m
24 s [...] vinte horas, trinta minutos e vinte e quatro segundos".
Ciberdúvidas, answer 14648 ("A grafia das horas"): "a representação
correcta de dezassete horas e trinta minutos, com algarismos, é: 17h30 min".
The spoken form here has no comma: "vinte horas trinta minutos e vinte e
quatro segundos".

Zero hours. Dicio, "Zero grau ou zero graus" (Flávia Neves): "No Brasil, o
zero é encarado como singular: zero grau; zero real; zero hora. Em Portugal,
o zero é encarado como plural: zero graus; zero reais; zero horas."

Day periods in 12-hour speech. Unicode CLDR 49, supplemental dayPeriods.xml,
rules for "pt" (pt_PT has no rules of its own and inherits them): night1
from 00:00 before 06:00, morning1 from 06:00 before 12:00, afternoon1 from
12:00 before 19:00, evening1 from 19:00 before 24:00, and midnight at 00:00
and noon at 12:00. CLDR 49 pt.xml, format names: "da madrugada", "da manhã",
"da tarde", "da noite", "meia-noite", "meio-dia". The rules divide
the time of day, so the period is the one of the moment itself, also when the
phrase names the next hour ("sete menos um quarto da tarde" at 18:45). This
module follows CLDR in pt-PT and pt-BR: "da noite" starts at 19:00. Senado
Federal, "Manual de Comunicação", entry "Hora", starts the night earlier, "A
noite, das 18h às 24h (ou à meia-noite)", and accepts both forms for the 18h
hour: "tanto fica correto usar «às seis da tarde» quanto «às seis da noite»".
Priberam gives no clock hour: "tarde" is the "Espaço do dia compreendido entre
o meio-dia e o anoitecer", and "madrugada" (sense 3) the "Período de tempo
entre a meia-noite e o amanhecer".

Minutes before the hour. Ciberdúvidas, answer 38623: "Depois da meia hora,
no registo corrente em Portugal, existem duas maneiras de indicar os minutos
que faltam para a hora", "são três menos um quarto" and "é um quarto para as
três". Priberam, "quarto", sense 3: "falta um quarto para as nove"; "para",
sense 5: "faltam cinco para a uma". Both forms are standard; this module
says "dez menos um quarto". For pt-BR, only teaching sites say that
"quinze para as dez" is the usual Brazilian form; no dictionary or grammar
was found, so pt-BR keeps the same form.
"""
from datetime import datetime, timedelta
from typing import Optional

from ovos_number_parser.numbers_pt import (
    PortugueseVariant,
    pronounce_number_pt,
)
from ovos_number_parser.util import GrammaticalGender
from ovos_utils.time import now_local

# Lowercase, as the Acordo Ortográfico de 1990, Base XIX 1.º b), writes the
# names of days and months.
WEEKDAYS_PT = {
    0: "segunda-feira",
    1: "terça-feira",
    2: "quarta-feira",
    3: "quinta-feira",
    4: "sexta-feira",
    5: "sábado",
    6: "domingo"
}
MONTHS_PT = {
    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro"
}


def portuguese_variant(lang: str) -> PortugueseVariant:
    """The spelling of the numbers for a Portuguese BCP-47 tag.

    Priberam, "dezesseis": "Grafia no Brasil: dezesseis. Grafia em Portugal:
    dezasseis." Brazil (BR) takes the Brazilian forms; every other region,
    and a tag with no region, takes the European ones.
    """
    regions = lang.lower().replace("_", "-").split("-")[1:]
    return PortugueseVariant.BR if "br" in regions else PortugueseVariant.PT


def nice_year_pt(dt, bc=False, variant=PortugueseVariant.PT):
    """
        Format a datetime to a pronounceable year

        For example, generate 'nineteen-hundred and eighty-four' for year 1984

        Args:
            dt (datetime): date to format (assumes already in local timezone)
            bc (bool) pust B.C. after the year (python does not support dates
                B.C. in datetime)
            variant (PortugueseVariant): the spelling of the numbers
        Returns:
            (str): The formatted year string
    """
    year = spoken_year_pt(dt.year, variant=variant)
    if bc:
        return f"{year} a.C."
    return year


def spoken_year_pt(year: int, variant=PortugueseVariant.PT) -> str:
    """A year read as a masculine cardinal: "dois mil e vinte e quatro"."""
    return pronounce_number_pt(year, variant=variant,
                               gender=GrammaticalGender.MASCULINE)


def spoken_day_pt(day: int, variant=PortugueseVariant.PT) -> str:
    """The day of the month: an ordinal for the first day, else a cardinal."""
    if day == 1:
        return "primeiro"
    return pronounce_number_pt(day, variant=variant,
                               gender=GrammaticalGender.MASCULINE)


def spoken_date_pt(day: Optional[int], month: Optional[int],
                   year: Optional[int], weekday: Optional[int] = None,
                   variant=PortugueseVariant.PT) -> str:
    """The fields of a date that are given, joined by "de", with no comma:
    "primeiro de maio de dois mil e vinte e quatro", "março de dois mil"."""
    words = []
    if day is not None:
        words.append(spoken_day_pt(day, variant))
    if month is not None:
        words.append(MONTHS_PT[month])
    if year is not None:
        words.append(spoken_year_pt(year, variant))
    date = " de ".join(words)
    if weekday is not None:
        date = f"{WEEKDAYS_PT[weekday]} {date}"
    return date


def _hours_pt(hour: int, variant) -> str:
    """A count of hours with the noun: "uma hora", "vinte e uma horas";
    zero takes the singular in pt-BR and the plural in pt-PT."""
    count = pronounce_number_pt(hour, variant=variant,
                                gender=GrammaticalGender.FEMININE)
    if hour == 1 or (hour == 0 and variant == PortugueseVariant.BR):
        return f"{count} hora"
    return f"{count} horas"


def _count_pt(value: int, noun: str, variant) -> str:
    """A masculine count with its noun: "um minuto", "trinta segundos"."""
    count = pronounce_number_pt(value, variant=variant,
                                gender=GrammaticalGender.MASCULINE)
    return f"{count} {noun}" if value == 1 else f"{count} {noun}s"


def spoken_time_pt(hour: int, minute: int, second: Optional[int] = None,
                   clock: str = "24h", style: str = "digits",
                   period: bool = False,
                   variant=PortugueseVariant.PT) -> Optional[str]:
    """A clock time in one style, or None for a style with no reading.

    digits: "catorze e trinta", and "vinte e uma horas" on the hour.
    units: "catorze horas e trinta minutos", with the seconds if given.
    phrase: the 12-hour conversational reading of nice_time_pt, "duas e
    meia da tarde".
    """
    if style == "phrase":
        if clock != "12h" or second is not None:
            return None
        return nice_time_pt(datetime(2000, 1, 1, hour, minute),
                            use_24hour=False, use_ampm=period,
                            variant=variant)
    shown = hour if clock == "24h" else hour % 12 or 12
    if style == "units":
        parts = [_hours_pt(shown, variant)]
        if minute:
            parts.append(_count_pt(minute, "minuto", variant))
        if second is not None:
            parts.append(_count_pt(second, "segundo", variant))
        speak = " e ".join(parts) if len(parts) < 3 \
            else f"{parts[0]} {parts[1]} e {parts[2]}"
    else:
        if second is not None:
            return None
        if minute:
            speak = pronounce_number_pt(
                shown, variant=variant, gender=GrammaticalGender.FEMININE
            ) + " e " + pronounce_number_pt(
                minute, variant=variant, gender=GrammaticalGender.MASCULINE)
        else:
            speak = _hours_pt(shown, variant)
    if clock == "12h" and period:
        if minute == 0 and second is None and hour in (0, 12):
            # CLDR pt: midnight at 00:00, noon at 12:00
            return "meia-noite" if hour == 0 else "meio-dia"
        speak += " " + _day_period_pt(hour)
    return speak


def _day_period_pt(hour: int) -> str:
    """The CLDR day period of an hour (see the module docstring)."""
    if hour < 6:
        return "da madrugada"
    if hour < 12:
        return "da manhã"
    if hour < 19:
        return "da tarde"
    return "da noite"


def nice_weekday_pt(dt):
    return WEEKDAYS_PT[dt.weekday()]


def nice_month_pt(dt):
    return MONTHS_PT[dt.month]


def nice_day_pt(dt, date_format='DMY', include_month=True):
    if include_month:
        month = nice_month_pt(dt)
        # Unicode CLDR pt, availableFormats MMMMd: "d 'de' MMMM", with the
        # day unpadded
        if date_format == 'MDY':
            return f"{month} {dt.day}"
        else:
            return f"{dt.day} de {month}"
    return dt.strftime("%d")


def nice_date_time_pt(dt, now=None, use_24hour=False,
                      use_ampm=False, variant=PortugueseVariant.PT):
    """
        Format a datetime to a pronounceable date and time

        For example, generate 'tuesday, june the fifth, 2018 at five thirty'

        Args:
            dt (datetime): date to format (assumes already in local timezone)
            now (datetime): Current date. If provided, the returned date for
                speech will be shortened accordingly: No year is returned if
                now is in the same year as td, no month is returned if now is
                in the same month as td. If now and td is the same day, 'today'
                is returned.
            use_24hour (bool): output in 24-hour/military or 12-hour format
            use_ampm (bool): include the am/pm for 12-hour format
            variant (PortugueseVariant): the spelling of the numbers
        Returns:
            (str): The formatted date time string
    """
    now = now or now_local()
    time = nice_time_pt(dt, use_24hour=use_24hour, use_ampm=use_ampm,
                        variant=variant)
    # a + the article of the hour: à uma, às duas, à meia-noite, ao meio-dia
    if time.startswith("meio-dia"):
        at = "ao"
    elif time.startswith(("uma", "meia-noite")):
        at = "à"
    else:
        at = "às"
    return f"{nice_date_pt(dt, now, variant=variant)} {at} {time}"


def nice_date_pt(dt: datetime, now: datetime = None, include_weekday=True,
                 variant=PortugueseVariant.PT):
    """
    Format a datetime to a pronounceable date

    For example, generates 'tuesday, june the fifth, 2018'

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        now (datetime): Current date. If provided, the returned date for speech
            will be shortened accordingly: No year is returned if now is in the
            same year as td, no month is returned if now is in the same month
            as td. If now and td is the same day, 'today' is returned.
        include_weekday (bool, optional): Whether to include the weekday name in the output. Defaults to True.
        variant (PortugueseVariant): the spelling of the numbers

    Returns:
        (str): The formatted date string
    """
    day = spoken_day_pt(dt.day, variant)
    if now is not None:
        nice = day
        if dt.date() == now.date():
            return "hoje"
        if dt.date() == now.date() + timedelta(days=1):
            return "amanhã"
        if dt.date() == now.date() - timedelta(days=1):
            return "ontem"
        if dt.month != now.month or dt.year != now.year:
            nice = nice + " de " + MONTHS_PT[dt.month]
        if dt.year != now.year:
            nice = nice + " de " + nice_year_pt(dt, variant=variant)
    else:
        nice = f"{day} de {MONTHS_PT[dt.month]} de {nice_year_pt(dt, variant=variant)}"

    if include_weekday:
        nice = f"{WEEKDAYS_PT[dt.weekday()]}, {nice}"
    return nice


def nice_time_pt(dt, speech=True, use_24hour=False, use_ampm=False,
                 variant=PortugueseVariant.PT):
    """
    Format a time to a comfortable human format
     For example, generate 'cinco treinta' for speech or '5:30' for
    text display.
     Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)=Fal
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
        variant (PortugueseVariant): the spelling of the numbers
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
        # simply speak the number
        speak += pronounce_number_pt(dt.hour, variant=variant,
                                     gender=GrammaticalGender.FEMININE)

        # equivalent to "quarter past ten"
        if dt.minute > 0:
            speak += " e " + pronounce_number_pt(
                dt.minute, variant=variant,
                gender=GrammaticalGender.MASCULINE)

    else:
        # speak number and add daytime identifier
        # (equivalent to "in the morning")
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
        hour %= 24

        if hour == 0:
            speak += "meia-noite"
        elif hour == 12:
            speak += "meio-dia"
        elif hour < 13:
            speak = pronounce_number_pt(hour, variant=variant,
                                        gender=GrammaticalGender.FEMININE)
        else:
            speak = pronounce_number_pt(hour - 12, variant=variant,
                                        gender=GrammaticalGender.FEMININE)

        if minute != 0:
            if minute == 15:
                speak += " e um quarto"
            elif minute == 30:
                speak += " e meia"
            elif minute == -15:
                speak += " menos um quarto"
            else:
                if minute > 0:
                    speak += " e " + pronounce_number_pt(
                        minute, variant=variant,
                        gender=GrammaticalGender.MASCULINE)
                else:
                    speak += " " + pronounce_number_pt(
                        minute, variant=variant,
                        gender=GrammaticalGender.MASCULINE)

        # exact time
        if minute == 0 and not use_ampm:
            # 3:00
            speak += " em ponto"

        if use_ampm and hour not in (0, 12):
            # the period of the moment itself, also when the phrase names
            # the next hour: 18:45 is "sete menos um quarto da tarde"
            speak += " " + _day_period_pt(dt.hour)
    return speak
