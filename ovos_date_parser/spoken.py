"""The spoken form of a date, a clock time or a year.

Each function takes the full language tag and only the fields that a text
writes. None of them reads the clock, a time zone or the current date. The
output is words only: no digit, no punctuation, single spaces.

A language, field, style or case with no reading raises UnsupportedForm. A
value that is out of range, or a date that does not exist, raises ValueError.
"""
import calendar
from typing import Optional

from ovos_date_parser.dates_pt import (
    portuguese_variant, spoken_date_pt, spoken_time_pt, spoken_year_pt
)


class UnsupportedForm(NotImplementedError):
    """This language has no reading for this form, field, style or case."""

    def __init__(self, lang: str, form: str, detail: str):
        super().__init__(f"{lang}: no {form} reading for {detail}")
        self.lang = lang
        self.form = form
        self.detail = detail


def _language(lang: str) -> str:
    return lang.lower().replace("_", "-").split("-")[0]


def _check_year(year: int):
    if not 1 <= year <= 9999:
        raise ValueError(f"year {year} is outside 1 to 9999")


def _check_date(day: Optional[int], month: Optional[int],
                year: Optional[int], weekday: Optional[int]):
    if day is None and month is None and year is None:
        raise ValueError("a date needs a day, a month or a year")
    if year is not None:
        _check_year(year)
    if month is not None and not 1 <= month <= 12:
        raise ValueError(f"month {month} is outside 1 to 12")
    if day is not None:
        if month is None and year is not None:
            raise ValueError("a day and a year need a month")
        # with no year, 29 February exists
        last = calendar.monthrange(year or 2000, month)[1] if month else 31
        if not 1 <= day <= last:
            raise ValueError(f"day {day} does not exist in month {month}")
    if weekday is not None:
        if not 0 <= weekday <= 6:
            raise ValueError(f"weekday {weekday} is outside 0 to 6")
        if None not in (day, month, year) \
                and calendar.weekday(year, month, day) != weekday:
            raise ValueError("the weekday does not match the date")


def spoken_date(lang: str, *, day: Optional[int] = None,
                month: Optional[int] = None, year: Optional[int] = None,
                weekday: Optional[int] = None, case: Optional[str] = None,
                declension: Optional[str] = None) -> str:
    """The spoken form of a full or partial date.

    Args:
        lang: a BCP-47 tag; the region selects its own reading.
        day, month, year: the fields the text writes. A day alone gives the
            day reading ("primeiro"), a month alone the month name.
        weekday: 0 = Monday, as ``datetime.weekday()``; spoken only if given.
        case: a case the language marks, for the head field (the day, or the
            month when there is no day).
        declension: "strong", "weak" or "mixed", for a language whose ordinal
            ending depends on the word before it.
    """
    _check_date(day, month, year, weekday)
    if _language(lang) == "pt":
        if case is not None or declension is not None:
            raise UnsupportedForm(lang, "date", f"case={case} declension={declension}")
        return spoken_date_pt(day, month, year, weekday,
                              variant=portuguese_variant(lang))
    raise UnsupportedForm(lang, "date", "this language")


def spoken_time(lang: str, hour: int, minute: int = 0,
                second: Optional[int] = None, *, clock: str = "24h",
                style: str = "digits", period: bool = False,
                case: Optional[str] = None) -> str:
    """The spoken form of a clock time.

    Args:
        lang: a BCP-47 tag; the region selects its own reading.
        hour, minute, second: the clock; the second is spoken only if given.
        clock: "24h" or "12h".
        style: "digits" (the clock as numbers), "units" (with the words for
            hour, minute and second) or "phrase" (the conversational reading).
        period: in a 12-hour reading, say the part of the day.
        case: a case the language marks.
    """
    if not 0 <= hour <= 23 or not 0 <= minute <= 59 \
            or (second is not None and not 0 <= second <= 59):
        raise ValueError(f"{hour}:{minute}:{second} is not a clock time")
    if clock not in ("24h", "12h") or style not in ("digits", "units", "phrase"):
        raise ValueError(f"unknown clock {clock!r} or style {style!r}")
    if _language(lang) == "pt":
        if case is not None:
            raise UnsupportedForm(lang, "time", f"case={case}")
        reading = spoken_time_pt(hour, minute, second, clock=clock,
                                 style=style, period=period,
                                 variant=portuguese_variant(lang))
        if reading is None:
            raise UnsupportedForm(lang, "time", f"{style} style, {clock} clock"
                                  + (", seconds" if second is not None else ""))
        return reading
    raise UnsupportedForm(lang, "time", "this language")


def spoken_year(lang: str, year: int, *, ordinal: bool = False,
                case: Optional[str] = None,
                declension: Optional[str] = None) -> str:
    """The spoken form of a year (1 to 9999), as a cardinal or an ordinal."""
    _check_year(year)
    if _language(lang) == "pt":
        if ordinal or case is not None or declension is not None:
            raise UnsupportedForm(lang, "year",
                                  f"ordinal={ordinal} case={case} declension={declension}")
        return spoken_year_pt(year, variant=portuguese_variant(lang))
    raise UnsupportedForm(lang, "year", "this language")
