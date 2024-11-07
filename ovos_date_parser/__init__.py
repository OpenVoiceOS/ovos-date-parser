from datetime import datetime, timedelta, time
from typing import Optional, Tuple, Union

from ovos_date_parser.dates_az import (
    extract_datetime_az,
    extract_duration_az,
    nice_duration_az,
    nice_time_az,
)
from ovos_date_parser.dates_ca import (
    TimeVariantCA,
    extract_datetime_ca,
    nice_time_ca,
)
from ovos_date_parser.dates_cs import (
    extract_duration_cs,
    extract_datetime_cs,
    nice_time_cs,
)
from ovos_date_parser.dates_da import (
    extract_datetime_da,
    nice_time_da,
)
from ovos_date_parser.dates_de import (
    extract_datetime_de,
    extract_duration_de,
    nice_time_de,
)
from ovos_date_parser.dates_en import (
    extract_datetime_en,
    extract_duration_en,
    nice_time_en,
)
from ovos_date_parser.dates_es import (
    extract_datetime_es,
    extract_duration_es,
    nice_time_es,
)
from ovos_date_parser.dates_eu import (
    extract_datetime_eu,
    nice_time_eu,
    nice_relative_time_eu,
)
from ovos_date_parser.dates_fa import (
    extract_datetime_fa,
    nice_time_fa,
    extract_duration_fa,
)
from ovos_date_parser.dates_fr import (
    extract_datetime_fr,
    nice_time_fr
)
from ovos_date_parser.dates_hu import nice_time_hu
from ovos_date_parser.dates_it import (
    extract_datetime_it,
    nice_time_it
)
from ovos_date_parser.dates_nl import (
    extract_datetime_nl,
    nice_part_of_day_nl,
    extract_duration_nl,
    nice_time_nl
)
from ovos_date_parser.dates_pl import (
    extract_datetime_pl,
    extract_duration_pl,
    nice_time_pl,
    nice_duration_pl
)
from ovos_date_parser.dates_pt import (
    extract_datetime_pt,
    extract_duration_pt,
    nice_time_pt
)
from ovos_date_parser.dates_ru import (
    extract_datetime_ru,
    extract_duration_ru,
    nice_time_ru,
    nice_duration_ru
)
from ovos_date_parser.dates_sv import (
    extract_datetime_sv,
    extract_duration_sv,
    nice_time_sv
)
from ovos_date_parser.dates_uk import (
    extract_datetime_uk,
    extract_duration_uk,
    nice_time_uk,
nice_duration_uk
)


def nice_time(
        dt: datetime,
        lang: str,
        speech: bool = True,
        use_24hour: bool = False,
        use_ampm: bool = False,
        variant: Optional[TimeVariantCA] = None,
) -> str:
    """
    Format a time to a comfortable human format.

    Args:
        dt: date to format (assumes already in local timezone).
        lang: A BCP-47 language code.
        speech: Format for speech (default is True) or display (False).
        use_24hour: Output in 24-hour/military or 12-hour format.
        use_ampm: Include the am/pm for 12-hour format.
        variant: Optional variant for Catalan (ca).

    Returns:
        The formatted time string.
    """
    if lang.startswith("az"):
        return nice_time_az(dt, speech, use_24hour, use_ampm)
    if lang.startswith("ca"):
        return nice_time_ca(dt, speech, use_24hour, use_ampm, variant=variant)
    if lang.startswith("cs"):
        return nice_time_cs(dt, speech, use_24hour, use_ampm)
    if lang.startswith("da"):
        return nice_time_da(dt, speech, use_24hour, use_ampm)
    if lang.startswith("de"):
        return nice_time_de(dt, speech, use_24hour, use_ampm)
    if lang.startswith("en"):
        return nice_time_en(dt, speech, use_24hour, use_ampm)
    if lang.startswith("es"):
        return nice_time_es(dt, speech, use_24hour, use_ampm)
    if lang.startswith("eu"):
        return nice_time_eu(dt, speech, use_24hour, use_ampm)
    if lang.startswith("fa"):
        return nice_time_fa(dt, speech, use_24hour, use_ampm)
    if lang.startswith("fr"):
        return nice_time_fr(dt, speech, use_24hour, use_ampm)
    if lang.startswith("hu"):
        return nice_time_hu(dt, speech, use_24hour, use_ampm)
    if lang.startswith("it"):
        return nice_time_it(dt, speech, use_24hour, use_ampm)
    if lang.startswith("nl"):
        return nice_time_nl(dt, speech, use_24hour, use_ampm)
    if lang.startswith("pl"):
        return nice_time_pl(dt, speech, use_24hour, use_ampm)
    if lang.startswith("pt"):
        return nice_time_pt(dt, speech, use_24hour, use_ampm)
    if lang.startswith("ru"):
        return nice_time_ru(dt, speech, use_24hour, use_ampm)
    if lang.startswith("sv"):
        return nice_time_sv(dt, speech, use_24hour, use_ampm)
    if lang.startswith("uk"):
        return nice_time_uk(dt, speech, use_24hour, use_ampm)
    raise NotImplementedError(f"Unsupported language: {lang}")


def nice_relative_time(when, relative_to, lang):
    """Create a relative phrase to roughly describe a datetime

    Examples are "25 seconds", "tomorrow", "7 days".

    Args:
        when (datetime): Local timezone
        relative_to (datetime): Baseline for relative time, default is now()
        lang (str, optional): Defaults to "en-us".
    Returns:
        str: Relative description of the given time
    """
    if lang.startswith("eu"):
        return nice_relative_time_eu(when, relative_to)
    raise NotImplementedError(f"Unsupported language: {lang}")


def nice_duration(
        duration: Union[int, float], lang: str, speech: bool = True
) -> str:
    """
    Convert duration in seconds to a nice spoken timespan.

    Args:
        duration: Time in seconds.
        lang: A BCP-47 language code.
        speech: Format for speech (True) or display (False).

    Returns:
        Timespan as a string.
    """
    if lang.startswith("az"):
        return nice_duration_az(duration, speech)
    if lang.startswith("pl"):
        return nice_duration_pl(duration, speech)
    if lang.startswith("ru"):
        return nice_duration_ru(duration, speech)
    if lang.startswith("uk"):
        return nice_duration_uk(duration, speech)
    raise NotImplementedError(f"Unsupported language: {lang}")


def extract_duration(
        text: str, lang: str
) -> Tuple[Optional[timedelta], str]:
    """
    Convert a phrase into a number of seconds and return the remainder text.

    Args:
        text: String containing a duration.
        lang: A BCP-47 language code.

    Returns:
        A tuple containing the duration as timedelta and the remaining text.
    """
    if lang.startswith("az"):
        return extract_duration_az(text)
    if lang.startswith("cs"):
        return extract_duration_cs(text)
    if lang.startswith("de"):
        return extract_duration_de(text)
    if lang.startswith("en"):
        return extract_duration_en(text)
    if lang.startswith("es"):
        return extract_duration_es(text)
    if lang.startswith("fa"):
        return extract_duration_fa(text)
    if lang.startswith("nl"):
        return extract_duration_nl(text)
    if lang.startswith("pl"):
        return extract_duration_pl(text)
    if lang.startswith("pt"):
        return extract_duration_pt(text)
    if lang.startswith("ru"):
        return extract_duration_ru(text)
    if lang.startswith("sv"):
        return extract_duration_sv(text)
    if lang.startswith("uk"):
        return extract_duration_uk(text)
    raise NotImplementedError(f"Unsupported language: {lang}")


def extract_datetime(
        text: str,
        lang: str,
        anchorDate: Optional[datetime] = None,
        default_time: Optional[time] = None,
) -> Optional[Tuple[datetime, str]]:
    """
    Extract date and time information from a sentence.

    Args:
        text: The text to be interpreted.
        lang: The BCP-47 code for the language to use.
        anchorDate: Date to use for relative dating.
        default_time: Time to use if none was found in the input string.

    Returns:
        A tuple with the extracted date as datetime and the leftover string,
        or None if no date or time related text is found.
    """
    if lang.startswith("az"):
        return extract_datetime_az(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("ca"):
        return extract_datetime_ca(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("cs"):
        return extract_datetime_cs(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("da"):
        return extract_datetime_da(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("de"):
        return extract_datetime_de(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("en"):
        return extract_datetime_en(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("es"):
        return extract_datetime_es(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("fa"):
        return extract_datetime_fa(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("fr"):
        return extract_datetime_fr(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("it"):
        return extract_datetime_it(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("nl"):
        return extract_datetime_nl(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("pl"):
        return extract_datetime_pl(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("pt"):
        return extract_datetime_pl(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("ru"):
        return extract_datetime_ru(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("sv"):
        return extract_datetime_sv(text, anchorDate=anchorDate, default_time=default_time)
    if lang.startswith("uk"):
        return extract_datetime_uk(text, anchorDate=anchorDate, default_time=default_time)
    raise NotImplementedError(f"Unsupported language: {lang}")
