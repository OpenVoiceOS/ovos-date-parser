"""Language-agnostic calendar range and season utilities.

Ranges are inclusive ``(start, end)`` tuples of the same type as the
reference date passed in. Decades, centuries and millennia follow the
calendar convention (the 1990s are 1990-1999, the 1900s are 1900-1999).

Seasons are meteorological (month-aligned) and hemisphere-aware: northern
spring starts March 1st, southern spring starts September 1st.
"""
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional, Tuple, Union

from dateutil.relativedelta import relativedelta
from ovos_utils.time import now_local


class Hemisphere(Enum):
    NORTH = 0
    SOUTH = 1


class Season(Enum):
    SPRING = 0
    SUMMER = 1
    FALL = 2
    WINTER = 3
    AUTUMN = 2


class DateTimeResolution(Enum):
    """Granularity for :func:`get_date_ordinal`.

    ``UNIT`` counts from the start of the calendar (ordinal 1 = year 1);
    ``UNIT_OF_SCOPE`` counts inside the scope containing the reference
    date; ``BEFORE_PRESENT_UNIT`` counts backwards from the before-present
    reference epoch (January 1st 1950).
    """
    DAY = 0
    DAY_OF_MONTH = 1
    DAY_OF_YEAR = 2
    DAY_OF_DECADE = 3
    DAY_OF_CENTURY = 4
    DAY_OF_MILLENNIUM = 5

    WEEK = 6
    WEEK_OF_MONTH = 7
    WEEK_OF_YEAR = 8
    WEEK_OF_DECADE = 9
    WEEK_OF_CENTURY = 10
    WEEK_OF_MILLENNIUM = 11

    MONTH = 12
    MONTH_OF_YEAR = 13
    MONTH_OF_DECADE = 14
    MONTH_OF_CENTURY = 15
    MONTH_OF_MILLENNIUM = 16

    YEAR = 17
    YEAR_OF_DECADE = 18
    YEAR_OF_CENTURY = 19
    YEAR_OF_MILLENNIUM = 20

    DECADE = 21
    DECADE_OF_CENTURY = 22
    DECADE_OF_MILLENNIUM = 23

    CENTURY = 24
    CENTURY_OF_MILLENNIUM = 25

    MILLENNIUM = 26

    BEFORE_PRESENT_DAY = 27
    BEFORE_PRESENT_WEEK = 28
    BEFORE_PRESENT_MONTH = 29
    BEFORE_PRESENT_YEAR = 30
    BEFORE_PRESENT_DECADE = 31
    BEFORE_PRESENT_CENTURY = 32
    BEFORE_PRESENT_MILLENNIUM = 33


# before-present reference epoch (as in radiocarbon dating)
BEFORE_PRESENT_EPOCH = date(year=1950, day=1, month=1)

DateRange = Tuple[date, date]


def get_week_range(ref_date: date) -> DateRange:
    """Monday..Sunday range of the week containing ``ref_date``."""
    start = ref_date - timedelta(days=ref_date.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_weekend_range(ref_date: date) -> DateRange:
    """Saturday..Sunday of the weekend containing or following ``ref_date``.

    During the week this is the upcoming weekend; on a weekend day it is
    the current weekend.
    """
    if ref_date.weekday() == 5:
        start = ref_date
    elif ref_date.weekday() == 6:
        start = ref_date - timedelta(days=1)
    else:
        start = get_week_range(ref_date)[0] + timedelta(days=5)
    return start, start + timedelta(days=1)


def get_month_range(ref_date: date) -> DateRange:
    """First..last day of the month containing ``ref_date``."""
    start = ref_date.replace(day=1)
    if ref_date.month == 12:
        end = ref_date.replace(day=31)
    else:
        end = ref_date.replace(day=1, month=ref_date.month + 1) - \
            timedelta(days=1)
    return start, end


def get_year_range(ref_date: date) -> DateRange:
    """January 1st..December 31st of the year containing ``ref_date``."""
    return (ref_date.replace(day=1, month=1),
            ref_date.replace(day=31, month=12))


def get_decade_range(ref_date: date) -> DateRange:
    """Calendar decade containing ``ref_date`` (1990s = 1990-1999)."""
    start = date(day=1, month=1, year=(ref_date.year // 10) * 10)
    end = date(day=31, month=12, year=start.year + 9)
    return start, end


def get_century_range(ref_date: date) -> DateRange:
    """Calendar century containing ``ref_date`` (1900s = 1900-1999)."""
    start = date(day=1, month=1, year=(ref_date.year // 100) * 100)
    end = date(day=31, month=12, year=start.year + 99)
    return start, end


def get_millennium_range(ref_date: date) -> DateRange:
    """Calendar millennium containing ``ref_date`` (1000-1999)."""
    start = date(day=1, month=1, year=(ref_date.year // 1000) * 1000)
    end = date(day=31, month=12, year=start.year + 999)
    return start, end


def get_week_number(ref_date: Optional[date] = None) -> int:
    """ISO-8601 week number of ``ref_date`` (default: today)."""
    ref_date = ref_date or now_local()
    return ref_date.isocalendar()[1]


def _as_date(ref_date: Union[date, datetime]) -> date:
    if isinstance(ref_date, datetime):
        return ref_date.date()
    return ref_date


# meteorological season boundaries: {season: (start_month, end_month)}
# northern hemisphere; the southern hemisphere is shifted by two seasons
_NORTH_SEASONS = {
    Season.SPRING: (3, 5),
    Season.SUMMER: (6, 8),
    Season.FALL: (9, 11),
}
_SOUTH_SEASONS = {
    Season.FALL: (3, 5),
    Season.WINTER: (6, 8),
    Season.SPRING: (9, 11),
}
# season starting in December, wrapping over the new year
_NORTH_WRAP = Season.WINTER
_SOUTH_WRAP = Season.SUMMER


def date_to_season(ref_date: Optional[date] = None,
                   hemisphere: Hemisphere = Hemisphere.NORTH) -> Season:
    """Meteorological season containing ``ref_date`` (default: today)."""
    ref_date = _as_date(ref_date or now_local().date())
    seasons = _NORTH_SEASONS if hemisphere == Hemisphere.NORTH \
        else _SOUTH_SEASONS
    for season, (first, last) in seasons.items():
        if first <= ref_date.month <= last:
            return season
    return _NORTH_WRAP if hemisphere == Hemisphere.NORTH else _SOUTH_WRAP


def season_to_date(season: Season, year: Optional[Union[int, date]] = None,
                   hemisphere: Hemisphere = Hemisphere.NORTH) -> date:
    """Start date of ``season`` in ``year`` (default: current year)."""
    if year is None:
        year = now_local().year
    elif not isinstance(year, int):
        year = year.year
    seasons = _NORTH_SEASONS if hemisphere == Hemisphere.NORTH \
        else _SOUTH_SEASONS
    wrap = _NORTH_WRAP if hemisphere == Hemisphere.NORTH else _SOUTH_WRAP
    season = Season(season.value) if isinstance(season, Season) \
        else Season(season)
    if season == wrap:
        return date(day=1, month=12, year=year)
    if season not in seasons:
        raise ValueError(f"Unknown Season: {season}")
    return date(day=1, month=seasons[season][0], year=year)


def next_season_date(season: Season, ref_date: Optional[date] = None,
                     hemisphere: Hemisphere = Hemisphere.NORTH) -> date:
    """Next start date of ``season`` on or after ``ref_date``."""
    ref_date = _as_date(ref_date or now_local().date())
    start = season_to_date(season, ref_date, hemisphere)
    if ref_date <= start:
        return start
    return season_to_date(season, ref_date.year + 1, hemisphere)


def last_season_date(season: Season, ref_date: Optional[date] = None,
                     hemisphere: Hemisphere = Hemisphere.NORTH) -> date:
    """Most recent start date of ``season`` before ``ref_date``."""
    ref_date = _as_date(ref_date or now_local().date())
    start = season_to_date(season, ref_date, hemisphere)
    if ref_date <= start:
        return season_to_date(season, ref_date.year - 1, hemisphere)
    return start


def get_season_range(ref_date: Optional[date] = None,
                     hemisphere: Hemisphere = Hemisphere.NORTH) -> DateRange:
    """First..last day of the season containing ``ref_date``.

    The December-starting season wraps the new year: its range runs from
    December 1st to the last day of the following February (the 29th on
    leap years).
    """
    ref_date = _as_date(ref_date or now_local().date())
    seasons = _NORTH_SEASONS if hemisphere == Hemisphere.NORTH \
        else _SOUTH_SEASONS
    for first, last in seasons.values():
        if first <= ref_date.month <= last:
            start = date(day=1, month=first, year=ref_date.year)
            end = date(day=1, month=last + 1, year=ref_date.year) - \
                timedelta(days=1)
            return start, end
    # December..February wrap-around season
    if ref_date.month == 12:
        start = date(day=1, month=12, year=ref_date.year)
    else:
        start = date(day=1, month=12, year=ref_date.year - 1)
    end = date(day=1, month=3, year=start.year + 1) - timedelta(days=1)
    return start, end


def get_date_ordinal(ordinal: int, ref_date: Optional[date] = None,
                     resolution: DateTimeResolution =
                     DateTimeResolution.DAY_OF_MONTH) -> date:
    """Resolve "the Nth {unit} of {scope}" into a date.

    Args:
        ordinal: 1-based ordinal; -1 selects the last unit in the scope.
        ref_date: reference date the containing scope is derived from
            (default: today).
        resolution: which unit/scope pair the ordinal refers to.

    Returns:
        The date of the requested unit (weeks resolve to their Monday,
        months/years/decades/centuries/millennia to their first day).
    """
    ordinal = int(ordinal)
    ref_date = _as_date(ref_date or now_local())

    _decade = (ref_date.year // 10) * 10 or 1
    _century = (ref_date.year // 100) * 100 or 1
    _mil = (ref_date.year // 1000) * 1000 or 1

    if resolution == DateTimeResolution.DAY:
        if ordinal < 0:
            raise OverflowError("The last day of existence can not be "
                                "represented")
        return date(year=1, day=1, month=1) + timedelta(days=ordinal - 1)
    if resolution == DateTimeResolution.DAY_OF_MONTH:
        if ordinal == -1:
            return get_month_range(ref_date)[1]
        return ref_date.replace(day=ordinal)
    if resolution == DateTimeResolution.DAY_OF_YEAR:
        if ordinal == -1:
            return date(year=ref_date.year, day=31, month=12)
        return date(year=ref_date.year, day=1, month=1) + \
            timedelta(days=ordinal - 1)
    if resolution == DateTimeResolution.DAY_OF_DECADE:
        if ordinal == -1:
            return date(year=_decade + 9, day=31, month=12)
        return date(year=_decade, day=1, month=1) + \
            timedelta(days=ordinal - 1)
    if resolution == DateTimeResolution.DAY_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century + 99, day=31, month=12)
        return date(year=_century, day=1, month=1) + \
            timedelta(days=ordinal - 1)
    if resolution == DateTimeResolution.DAY_OF_MILLENNIUM:
        if ordinal == -1:
            return date(year=_mil + 999, day=31, month=12)
        return date(year=_mil, day=1, month=1) + timedelta(days=ordinal - 1)

    if resolution == DateTimeResolution.WEEK:
        if ordinal < 0:
            raise OverflowError("The last week of existence can not be "
                                "represented")
        _day = date(1, 1, 1) + relativedelta(weeks=ordinal) - \
            timedelta(days=1)
        return get_week_range(_day)[0]
    if resolution == DateTimeResolution.WEEK_OF_MONTH:
        if ordinal == -1:
            _day = get_month_range(ref_date)[1]
        else:
            if not 0 < ordinal <= 4:
                raise ValueError("months only have 4 weeks")
            _day = ref_date.replace(day=1) + relativedelta(weeks=ordinal) - \
                timedelta(days=1)
        return get_week_range(_day)[0]
    if resolution == DateTimeResolution.WEEK_OF_YEAR:
        if ordinal == -1:
            _day = ref_date.replace(day=31, month=12)
        else:
            _day = ref_date.replace(day=1, month=1) + \
                relativedelta(weeks=ordinal) - timedelta(days=1)
        return get_week_range(_day)[0]
    if resolution == DateTimeResolution.WEEK_OF_DECADE:
        if ordinal == -1:
            _day = date(day=31, month=12, year=_decade + 9)
        else:
            _day = date(day=1, month=1, year=_decade) + \
                relativedelta(weeks=ordinal) - timedelta(days=1)
        return get_week_range(_day)[0]
    if resolution == DateTimeResolution.WEEK_OF_CENTURY:
        if ordinal == -1:
            _day = date(day=31, month=12, year=_century + 99)
        else:
            _day = date(day=1, month=1, year=_century) + \
                relativedelta(weeks=ordinal) - timedelta(days=1)
        return get_week_range(_day)[0]
    if resolution == DateTimeResolution.WEEK_OF_MILLENNIUM:
        if ordinal == -1:
            _day = date(day=31, month=12, year=_mil + 999)
        else:
            _day = date(day=1, month=1, year=_mil) + \
                relativedelta(weeks=ordinal) - timedelta(days=1)
        return get_week_range(_day)[0]

    if resolution == DateTimeResolution.MONTH:
        if ordinal < 0:
            raise OverflowError("The last month of existence can not be "
                                "represented")
        return date(year=1, day=1, month=1) + \
            relativedelta(months=ordinal - 1)
    if resolution == DateTimeResolution.MONTH_OF_YEAR:
        if ordinal == -1:
            return ref_date.replace(month=12, day=1)
        return ref_date.replace(day=1, month=1) + \
            relativedelta(months=ordinal - 1)
    if resolution == DateTimeResolution.MONTH_OF_DECADE:
        if ordinal == -1:
            return date(year=_decade + 9, day=1, month=12)
        return date(year=_decade, month=1, day=1) + \
            relativedelta(months=ordinal - 1)
    if resolution == DateTimeResolution.MONTH_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century + 99, day=1, month=12)
        return date(year=_century, month=1, day=1) + \
            relativedelta(months=ordinal - 1)
    if resolution == DateTimeResolution.MONTH_OF_MILLENNIUM:
        if ordinal == -1:
            return date(year=_mil + 999, day=1, month=12)
        return date(year=_mil, month=1, day=1) + \
            relativedelta(months=ordinal - 1)

    if resolution == DateTimeResolution.YEAR:
        if ordinal == -1:
            raise OverflowError("The last year of existence can not be "
                                "represented")
        if ordinal == 0:
            # NOTE: no year 0
            return date(year=1, day=1, month=1)
        return date(year=ordinal, day=1, month=1)
    if resolution == DateTimeResolution.YEAR_OF_DECADE:
        if ordinal == -1:
            return date(year=_decade + 9, day=1, month=1)
        if not 0 < ordinal <= 10:
            raise ValueError("decades only have 10 years")
        return date(year=_decade + ordinal - 1, day=1, month=1)
    if resolution == DateTimeResolution.YEAR_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century + 99, day=1, month=1)
        if not 0 < ordinal <= 100:
            raise ValueError("centuries only have 100 years")
        return date(year=_century + ordinal - 1, day=1, month=1)
    if resolution == DateTimeResolution.YEAR_OF_MILLENNIUM:
        if ordinal == -1:
            return date(year=_mil + 999, day=1, month=1)
        if not 0 < ordinal <= 1000:
            raise ValueError("millennia only have 1000 years")
        return date(year=_mil + ordinal - 1, day=1, month=1)

    if resolution == DateTimeResolution.DECADE:
        if ordinal == -1:
            raise OverflowError("The last decade of existence can not be "
                                "represented")
        if ordinal == 1:
            return date(day=1, month=1, year=1)
        return date(year=(ordinal - 1) * 10, day=1, month=1)
    if resolution == DateTimeResolution.DECADE_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century + 90, day=1, month=1)
        if not 0 < ordinal <= 10:
            raise ValueError("centuries only have 10 decades")
        if ordinal == 1:
            return date(day=1, month=1, year=_century)
        return date(year=_century + (ordinal - 1) * 10, day=1, month=1)
    if resolution == DateTimeResolution.DECADE_OF_MILLENNIUM:
        if ordinal == -1:
            return date(year=_mil + 990, day=1, month=1)
        if not 0 < ordinal <= 100:
            raise ValueError("millennia only have 100 decades")
        if ordinal == 1:
            return date(day=1, month=1, year=_mil)
        return date(year=_mil + (ordinal - 1) * 10, day=1, month=1)

    if resolution == DateTimeResolution.CENTURY:
        if ordinal == -1:
            raise OverflowError("The last century of existence can not be "
                                "represented")
        if ordinal == 1:
            # NOTE: no century 0 / year 0
            return date(day=1, month=1, year=1)
        return date(year=(ordinal - 1) * 100, day=1, month=1)
    if resolution == DateTimeResolution.CENTURY_OF_MILLENNIUM:
        if ordinal == -1:
            return date(year=_mil + 900, day=1, month=1)
        if not 0 < ordinal <= 10:
            raise ValueError("millennia only have 10 centuries")
        if ordinal == 1:
            return date(day=1, month=1, year=_mil)
        return date(year=_mil + (ordinal - 1) * 100, day=1, month=1)

    if resolution == DateTimeResolution.MILLENNIUM:
        if ordinal < 0:
            raise OverflowError("The last millennium of existence can not "
                                "be represented")
        if ordinal == 1:
            return date(day=1, month=1, year=1)
        return date(year=(ordinal - 1) * 1000, day=1, month=1)

    if resolution == DateTimeResolution.BEFORE_PRESENT_DAY:
        if ordinal < 0:
            raise OverflowError("Can not represent dates BC")
        return BEFORE_PRESENT_EPOCH - relativedelta(days=ordinal)
    if resolution == DateTimeResolution.BEFORE_PRESENT_WEEK:
        if ordinal < 0:
            raise OverflowError("Can not represent dates BC")
        _week = BEFORE_PRESENT_EPOCH - relativedelta(weeks=ordinal)
        return get_week_range(_week)[1]
    if resolution == DateTimeResolution.BEFORE_PRESENT_MONTH:
        if ordinal < 0:
            raise OverflowError("Can not represent dates BC")
        return BEFORE_PRESENT_EPOCH - relativedelta(months=ordinal)
    if resolution == DateTimeResolution.BEFORE_PRESENT_YEAR:
        if ordinal < 0:
            raise OverflowError("Can not represent dates BC")
        return BEFORE_PRESENT_EPOCH - relativedelta(years=ordinal)
    if resolution == DateTimeResolution.BEFORE_PRESENT_DECADE:
        if ordinal < 0:
            raise OverflowError("Can not represent dates BC")
        return BEFORE_PRESENT_EPOCH - relativedelta(years=10 * ordinal)
    if resolution == DateTimeResolution.BEFORE_PRESENT_CENTURY:
        if ordinal < 0:
            raise OverflowError("Can not represent dates BC")
        return BEFORE_PRESENT_EPOCH - relativedelta(years=100 * ordinal)
    if resolution == DateTimeResolution.BEFORE_PRESENT_MILLENNIUM:
        if ordinal < 0:
            raise OverflowError("Can not represent dates BC")
        return BEFORE_PRESENT_EPOCH - relativedelta(years=1000 * ordinal)

    raise ValueError(f"Invalid DateTimeResolution: {resolution}")
