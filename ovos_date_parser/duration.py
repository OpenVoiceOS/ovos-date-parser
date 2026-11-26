"""Duration resolutions and the conversion of a length to one of them."""
from datetime import timedelta
from enum import Enum
from typing import Union

from dateutil.relativedelta import relativedelta
from ovos_utils.time import DAYS_IN_1_MONTH, DAYS_IN_1_YEAR


class DurationResolution(Enum):
    TIMEDELTA = 0
    RELATIVEDELTA = 1
    RELATIVEDELTA_STRICT = 1
    RELATIVEDELTA_FALLBACK = 2
    RELATIVEDELTA_APPROXIMATE = 3
    TOTAL_SECONDS = 4
    TOTAL_MICROSECONDS = 5
    TOTAL_MILLISECONDS = 6
    TOTAL_MINUTES = 7
    TOTAL_HOURS = 8
    TOTAL_DAYS = 9
    TOTAL_WEEKS = 10
    TOTAL_MONTHS = 11
    TOTAL_YEARS = 12
    TOTAL_DECADES = 13
    TOTAL_CENTURIES = 14
    TOTAL_MILLENNIUMS = 15


#: the length of the unit a ``TOTAL_*`` resolution counts
_TOTAL_UNIT = {
    DurationResolution.TOTAL_MICROSECONDS: timedelta(microseconds=1),
    DurationResolution.TOTAL_MILLISECONDS: timedelta(milliseconds=1),
    DurationResolution.TOTAL_SECONDS: timedelta(seconds=1),
    DurationResolution.TOTAL_MINUTES: timedelta(minutes=1),
    DurationResolution.TOTAL_HOURS: timedelta(hours=1),
    DurationResolution.TOTAL_DAYS: timedelta(days=1),
    DurationResolution.TOTAL_WEEKS: timedelta(weeks=1),
    DurationResolution.TOTAL_MONTHS: timedelta(days=DAYS_IN_1_MONTH),
    DurationResolution.TOTAL_YEARS: timedelta(days=DAYS_IN_1_YEAR),
    DurationResolution.TOTAL_DECADES: timedelta(days=10 * DAYS_IN_1_YEAR),
    DurationResolution.TOTAL_CENTURIES: timedelta(days=100 * DAYS_IN_1_YEAR),
    DurationResolution.TOTAL_MILLENNIUMS: timedelta(days=1000 * DAYS_IN_1_YEAR),
}

_RELATIVEDELTA = frozenset({
    DurationResolution.RELATIVEDELTA,
    DurationResolution.RELATIVEDELTA_FALLBACK,
    DurationResolution.RELATIVEDELTA_APPROXIMATE,
})


def convert_duration(length: timedelta, resolution: DurationResolution
                     ) -> Union[timedelta, relativedelta, float]:
    """Express a length in the requested resolution."""
    if resolution == DurationResolution.TIMEDELTA:
        return length
    if resolution in _RELATIVEDELTA:
        return relativedelta(days=length.days, seconds=length.seconds,
                             microseconds=length.microseconds)
    if resolution in _TOTAL_UNIT:
        return length / _TOTAL_UNIT[resolution]
    raise ValueError(f"invalid resolution: {resolution}")
