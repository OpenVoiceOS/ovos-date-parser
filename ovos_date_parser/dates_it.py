"""Date and time tools for Italian.

Sources for the rules of the spoken date, time and year in this module:

Cardinals for the days, an ordinal for the first. Accademia della Crusca,
consulenza 86 ("L'articolo con le date e le cifre"), quoting Serianni,
Grammatica italiana: "Per i giorni del mese si usa l'ordinale per il giorno
iniziale [...], ma il cardinale per i giorni successivi"; its example "il
1/2/2003 (cioè il primo febbraio duemilatré)". Treccani, Vocabolario,
"primo": "il p. di marzo o il p. marzo, sottint. giorno". So day 1 is
"primo" and every other day a cardinal: "ventuno" (Treccani, Enciclopedia
dell'Italiano, "Numerali": "il ventuno è il mio compleanno").

No "di" between the fields. Crusca 86, quoting Serianni: Manzoni wrote "ai 22
di settembre dell'anno 1612" in 1827 and "optò nel 1840 per il tipo «il 22
settembre» (da notare anche la soppressione della preposizione di tra mese e
anno)". The date reads "primo maggio", "dodici marzo duemilaventiquattro".

The article and the preposition belong to the text around the date. Crusca 86,
quoting Serianni: "L'anno è sempre preceduto dall'articolo: «il 1720», «nel
1988»", and a date with day and month is introduced by "un articolo maschile
singolare: «il 20 settembre 1870»". The article joins the preposition ("nel",
"dal", "del"), so the spoken forms here give the fields without them, and the
caller adds "il", "nel" or "del".

The year is one cardinal word. Crusca, consulenza 20176 ("In che anno siamo?
Nel venti ventidue o nel duemilaventidue?"): "non si direbbe diciannove
novantanove per millenovecentonovantanove, per es., ma neppure venti zerosette
per duemilasette"; Crusca 86 writes "millenovecentoottantanove" and
"duemilatré". The number words are those of pronounce_number_it.

The clock. Treccani, Vocabolario, "ora": "Nel linguaggio comune, le ore si
contano da 1 a 24 a partire dalla mezzanotte; è frequente l'uso di contare
separatamente le ore che vanno dalla mezzanotte al mezzogiorno e quelle che
vanno dal mezzogiorno alla mezzanotte, precisando talvolta se si tratta di ore
della mattina o della sera (le otto antimeridiane o di mattina; le quattro
pomeridiane o del pomeriggio; alle nove di sera)". Treccani, "zero": "l'aereo
parte alle ore zero precise, a mezzanotte in punto"; Treccani, "mezza": "le
ore zero e trenta minuti". So the 24-hour clock reads the hour as a cardinal,
0 as "zero", and the minutes after "e": "diciotto e trenta", "zero e trenta".
A whole hour has no noun: Crusca 86, quoting Della Valle and Patota,
"L'orologio segnava le cinque". Treccani, "ventuno": "al femm., le ventuno,
le ore 9 di sera", so 21 stays "ventuno". Hour 1 is "una": Crusca,
consulenza 236 ("Alle una o all'una?"): "l'una rimanga da preferirsi".

No unit-word clock. The "units" style raises UnsupportedForm. Treccani,
"ora", keeps the two senses apart: the clock reads "le otto antimeridiane o di
mattina; le quattro pomeridiane o del pomeriggio; alle nove di sera", with no
noun after the number, and the span of time reads "ho dormito solo sei ore;
[...] il viaggio dura circa tre ore". "Tredici ore e trenta minuti" is the
span. Crusca, consulenza 2777 ("Come si abbrevia, come si scrive e come si
legge 24 ore su 24"), gives one spoken sequence of hour, minute and second,
with the nouns first: "18:30:15 vale ore 18, minuti 30, secondi 15". No source
attests a full reading with "e" in that order, so the module gives none.

Half and quarter. Crusca, consulenza 48 ("Mezzo / mezza"), quoting Della
Valle and Patota: "Come preferite. Potete usare la forma le tre e mezzo [...]
oppure le tre e mezza, sottintendendo ora". This module says "mezza". Treccani, "quarto":
"manca un q. alle dieci o sono le dieci meno un q."; so the quarter before the
hour is "meno un quarto" and the quarter after is "e un quarto".

Midnight and noon. Treccani, "mezzogiorno": "è m. in punto; [...] è m. e un
quarto"; Treccani, "mezzanotte": "è m., m. in punto; m. e mezzo"; Crusca, consulenza
2968 ("Ci vediamo alla mezza"): "mezzanotte e mezza (0.30)". In a
12-hour reading with the day period, 00:00 reads "mezzanotte", 12:00
"mezzogiorno", and the hours after them keep the word: "mezzogiorno e un
quarto", "mezzanotte e mezza". The 24-hour reading keeps the numbers.

Day periods in 12-hour speech. Unicode CLDR 49, supplemental
dayPeriods.xml, the rules for "it": midnight at 00:00, noon at 12:00, night1
from 00:00 before 06:00, morning1 from 06:00 before 12:00, afternoon1 from
12:00 before 18:00, evening1 from 18:00 before 24:00. The format names in
it.xml, as Babel 2.18 resolves them: "di notte", "di mattina", "del
pomeriggio", "di sera", "mezzanotte", "mezzogiorno". Treccani, "ora": "di
mattina", "del pomeriggio", "di sera". The period is the one of the moment
itself, also when the phrase names the next hour ("sei meno un quarto del
pomeriggio" at 17:45).

Names of days and months. Treccani, Vocabolario, "lunedì", "venerdì",
"gennaio": the headwords are lowercase and the days carry the grave accent.
The names come from res/it/date_time.json, the table nice_date reads.
"""
import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from ovos_number_parser.numbers_it import pronounce_number_it

@lru_cache(maxsize=None)
def _date_names_it():
    """The month and weekday names of res/it/date_time.json, the table that
    nice_date reads: (months by number, weekdays by number, 0 = Monday)."""
    path = Path(__file__).parent / "res" / "it" / "date_time.json"
    config = json.loads(path.read_text(encoding="utf8"))
    months = config.get("month_format", config["month"])
    return (
        {int(number): name for number, name in months.items()},
        {int(number): name for number, name in config["weekday"].items()})


def spoken_year_it(year: int) -> str:
    """A year read as one cardinal word: "duemilaventiquattro"."""
    return pronounce_number_it(year)


def spoken_day_it(day: int) -> str:
    """The day of the month: an ordinal for the first day, else a cardinal."""
    return "primo" if day == 1 else pronounce_number_it(day)


def spoken_date_it(day: Optional[int], month: Optional[int],
                   year: Optional[int], weekday: Optional[int] = None) -> str:
    """The fields of a date that are given, with no "di" and no comma:
    "primo maggio duemilaventiquattro", "marzo duemilaventiquattro"."""
    months, weekdays = _date_names_it()
    words = []
    if weekday is not None:
        words.append(weekdays[weekday])
    if day is not None:
        words.append(spoken_day_it(day))
    if month is not None:
        words.append(months[month])
    if year is not None:
        words.append(spoken_year_it(year))
    return " ".join(words)


def _hour_it(hour: int) -> str:
    """An hour on its own: "una" for 1, else the cardinal ("zero", "ventuno")."""
    return "una" if hour == 1 else pronounce_number_it(hour)


def _day_period_it(hour: int) -> str:
    """The CLDR day period of an hour (see the module docstring)."""
    if hour < 6:
        return "di notte"
    if hour < 12:
        return "di mattina"
    if hour < 18:
        return "del pomeriggio"
    return "di sera"


def spoken_time_it(hour: int, minute: int, second: Optional[int] = None,
                   clock: str = "24h", style: str = "digits",
                   period: bool = False) -> Optional[str]:
    """A clock time in one style, or None for a style with no reading.

    digits: "quattordici e trenta", and "ventuno" on the hour.
    units: no reading.
    phrase: the 12-hour conversational reading, "due e mezza del pomeriggio".
    """
    if style == "units":
        return None
    named = period and clock == "12h" and minute == 0 and second is None \
        and hour in (0, 12)
    if named:
        return "mezzanotte" if hour == 0 else "mezzogiorno"
    shown = hour if clock == "24h" else hour % 12 or 12
    if style == "phrase":
        if clock != "12h" or second is not None:
            return None
        # a quarter before the hour names the next hour
        base = shown if minute != 45 else (hour + 1) % 12 or 12
        base_hour = hour if minute != 45 else (hour + 1) % 24
        if period and base_hour in (0, 12):
            word = "mezzanotte" if base_hour == 0 else "mezzogiorno"
            period = False
        else:
            word = _hour_it(base)
        if minute == 0:
            speak = word
        elif minute == 15:
            speak = f"{word} e un quarto"
        elif minute == 30:
            speak = f"{word} e mezza"
        elif minute == 45:
            speak = f"{word} meno un quarto"
        else:
            speak = f"{word} e {pronounce_number_it(minute)}"
    else:
        if second is not None:
            return None
        speak = _hour_it(shown)
        if minute:
            speak += " e " + pronounce_number_it(minute)
    if clock == "12h" and period:
        speak += " " + _day_period_it(hour)
    return speak


def nice_time_it(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format
    adapted to italian fron en version

    For example, generate 'cinque e trenta' for speech or '5:30' for
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
        # Either "zero 8 zerozero" o "13 zerozero"
        if string[0:2] == '00':
            speak += "zerozero"
        elif string[0] == '0':
            speak += pronounce_number_it(int(string[0])) + " "
            if int(string[1]) == 1:
                speak = "una"
            else:
                speak += pronounce_number_it(int(string[1]))
        else:
            speak = pronounce_number_it(int(string[0:2]))

        # in italian  "13 e 25"
        speak += " e "

        if string[3:5] == '00':
            speak += "zerozero"
        else:
            if string[3] == '0':
                speak += pronounce_number_it(0) + " "
                speak += pronounce_number_it(int(string[4]))
            else:
                speak += pronounce_number_it(int(string[3:5]))
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "mezzanotte"
        if dt.hour == 12 and dt.minute == 0:
            return "mezzogiorno"
        # TODO: "10 e un quarto", "4 e tre quarti" and ot her idiomatic times

        if dt.hour == 0:
            speak = "mezzanotte"
        elif dt.hour == 1 or dt.hour == 13:
            speak = "una"
        elif dt.hour > 13:  # era minore
            speak = pronounce_number_it(dt.hour - 12)
        else:
            speak = pronounce_number_it(dt.hour)

        speak += " e"
        if dt.minute == 0:
            speak = speak[:-2]
            if not use_ampm:
                speak += " in punto"
        elif dt.minute == 15:
            speak += " un quarto"
        elif dt.minute == 45:
            speak += " tre quarti"
        else:
            if dt.minute < 10:
                speak += " zero"
            speak += " " + pronounce_number_it(dt.minute)

        if use_ampm:

            if dt.hour < 4:
                speak.strip()
            elif dt.hour > 20:
                speak += " della notte"
            elif dt.hour > 17:
                speak += " della sera"
            elif dt.hour > 12:
                speak += " del pomeriggio"
            else:
                speak += " della mattina"

        return speak
