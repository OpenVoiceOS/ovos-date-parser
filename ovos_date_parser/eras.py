"""Named eras, epochs, and out-of-range dates.

``datetime.date`` only represents years 1..9999, so phrases like
"3000 BC", "10000 years before present" or "in the year 12000" cannot be
resolved into stdlib types.  This module provides the representation and the
arithmetic for those cases:

* :class:`AstroDate` — a frozen, date-like value using **astronomical year
  numbering** and an unbounded year.
* :func:`astro_year_range` — decade/century/millennium ranges for any year,
  the out-of-range counterpart of ``get_decade_range`` and friends.
* :class:`Era` / :data:`ERAS` / :func:`resolve_era` — a language-agnostic
  registry of calendar eras and epochs ("anno domini", "before present",
  "unix time", "julian day", ...) and the conversion of a count in an era
  into a concrete date.

Conventions
-----------
* **Astronomical year numbering** (ISO 8601 expanded / astronomical usage):
  there is a year 0, and ``X BC`` maps to year ``1 - X`` (1 BC = 0,
  4713 BC = -4712).  This keeps decade/century/millennium arithmetic pure
  floor division with no "no year zero" special case.
* **Proleptic Gregorian calendar** throughout, matching Python's ``datetime``.
  There is no Julian/Gregorian switch in 1582; historical Julian-calendar
  dates are out of scope.
* **Date-only precision** out of range: no time-of-day and no timezone on
  :class:`AstroDate` — civil timezones are meaningless in 3000 BC.  The
  ``resolution`` field records how precise the extraction actually was.

Only results that ``datetime`` cannot represent become :class:`AstroDate`;
everything in range is returned as plain ``datetime.date`` / ``datetime``
so existing consumers never see the new type unless they parse era phrases.
"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Tuple, Union

from ovos_date_parser.ranges import DateTimeResolution

_DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def is_leap_year(year: int) -> bool:
    """Proleptic Gregorian leap rule, valid for any year including <= 0.

    ``calendar.isleap`` implements the same formula but is documented for the
    stdlib range only; this spelling makes the negative-year contract explicit.
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


@dataclass(frozen=True)
class AstroDate:
    """A date-like value with an unbounded, astronomical-numbered year.

    ``month``/``day`` are optional because era phrases usually carry only
    year precision ("3000 BC"); ``resolution`` records the precision the
    source text actually had.

    Comparison: ``<``, ``<=``, ``>``, ``>=`` accept another :class:`AstroDate`
    or a ``datetime.date``/``datetime`` (compared by ``(year, month, day)``
    with missing fields defaulting to January 1st).  ``==``/``hash`` are
    deliberately AstroDate-only: cross-type ``==`` with ``date`` cannot be
    made consistent with ``date.__hash__`` and would corrupt dict/set use.
    """
    year: int
    month: Optional[int] = None
    day: Optional[int] = None
    resolution: DateTimeResolution = DateTimeResolution.YEAR

    def __post_init__(self):
        if self.month is not None and not 1 <= self.month <= 12:
            raise ValueError(f"month must be in 1..12, got {self.month}")
        if self.day is not None:
            if self.month is None:
                raise ValueError("day given without month")
            limit = _DAYS_IN_MONTH[self.month - 1]
            if self.month == 2 and is_leap_year(self.year):
                limit = 29
            if not 1 <= self.day <= limit:
                raise ValueError(f"day must be in 1..{limit} for "
                                 f"year={self.year} month={self.month}, "
                                 f"got {self.day}")

    # -- era conversions ---------------------------------------------------
    @property
    def is_bc(self) -> bool:
        """True for years before the common era (astronomical year <= 0)."""
        return self.year <= 0

    @property
    def bc_year(self) -> int:
        """The year in BC counting (1 BC = year 0, so BC = 1 - year)."""
        if not self.is_bc:
            raise ValueError(f"year {self.year} is not BC")
        return 1 - self.year

    # -- datetime interop --------------------------------------------------
    @property
    def in_datetime_range(self) -> bool:
        return date.min.year <= self.year <= date.max.year

    @property
    def date(self) -> Optional[date]:
        """The equivalent ``datetime.date``, or None when unrepresentable.

        Missing month/day default to January 1st, i.e. the start of the
        period this value names at its resolution.
        """
        if not self.in_datetime_range:
            return None
        return date(self.year, self.month or 1, self.day or 1)

    @classmethod
    def from_date(cls, d: Union[date, datetime],
                  resolution: DateTimeResolution = DateTimeResolution.DAY
                  ) -> "AstroDate":
        return cls(d.year, d.month, d.day, resolution=resolution)

    # -- ordering ----------------------------------------------------------
    def _key(self) -> Tuple[int, int, int]:
        return self.year, self.month or 1, self.day or 1

    @staticmethod
    def _coerce(other) -> Optional[Tuple[int, int, int]]:
        if isinstance(other, AstroDate):
            return other._key()
        if isinstance(other, (date, datetime)):
            return other.year, other.month, other.day
        return None

    def __lt__(self, other):
        key = self._coerce(other)
        return NotImplemented if key is None else self._key() < key

    def __le__(self, other):
        key = self._coerce(other)
        return NotImplemented if key is None else self._key() <= key

    def __gt__(self, other):
        key = self._coerce(other)
        return NotImplemented if key is None else self._key() > key

    def __ge__(self, other):
        key = self._coerce(other)
        return NotImplemented if key is None else self._key() >= key

    def __str__(self):
        # ISO 8601 expanded representation: explicit sign, >=4 year digits
        y = f"{self.year:+05d}" if (self.year < 0 or self.year > 9999) \
            else f"{self.year:04d}"
        if self.month is None:
            return y
        if self.day is None:
            return f"{y}-{self.month:02d}"
        return f"{y}-{self.month:02d}-{self.day:02d}"


def astro_year_range(year: int, resolution: DateTimeResolution
                     ) -> Tuple[AstroDate, AstroDate]:
    """Decade/century/millennium containing ``year``, for any year.

    Out-of-range counterpart of ``get_decade_range``/``get_century_range``/
    ``get_millennium_range``; matches their convention that a period is the
    floor-division bucket (the 1980s are 1980..1989).  Astronomical numbering
    makes this exact for BC years with no special case: the century containing
    2999 BC (year -2998) is -3000..-2901.
    """
    span = {DateTimeResolution.YEAR: 1,
            DateTimeResolution.DECADE: 10,
            DateTimeResolution.CENTURY: 100,
            DateTimeResolution.MILLENNIUM: 1000}.get(resolution)
    if span is None:
        raise ValueError(f"unsupported resolution for a year range: "
                         f"{resolution}")
    start = (year // span) * span
    return (AstroDate(start, resolution=resolution),
            AstroDate(start + span - 1, resolution=resolution))


# --------------------------------------------------------------------------
# Era registry
# --------------------------------------------------------------------------

class EraCounting:
    """How a numeric value counts within an era (plain constants, not Enum,
    so per-language tables can be trivially serialized later)."""
    YEARS_SINCE = "years_since"      # "year N of the era"; year 1 = epoch year
    YEARS_BEFORE = "years_before"    # "N years before the epoch" (e.g. BP)
    DAYS_SINCE = "days_since"        # day count from a fixed origin (Julian day)
    SECONDS_SINCE = "seconds_since"  # second count from a fixed origin (unix)


@dataclass(frozen=True)
class Era:
    """A calendar era: an epoch plus how counts are reckoned against it.

    ``epoch.year`` is the astronomical year of **era year 1** for
    YEARS_SINCE eras, or the reference point for the other counting modes.
    """
    key: str
    epoch: AstroDate
    counting: str = EraCounting.YEARS_SINCE


#: Language-agnostic era registry.  Keys are stable identifiers that
#: per-language vocabularies map surface forms onto ("avant J.-C." ->
#: "before_christ").  Epochs are cited to canonical sources saved under
#: ``~/AgentWorkspaces/papers/calendars/`` where noted.
ERAS = {
    # Common/Christian era.  Era year 1 == astronomical year 1 by definition
    # of astronomical numbering.
    "common_era": Era("common_era", AstroDate(1, 1, 1)),
    # BC/BCE counts years *backwards* ending at 1 BC (astronomical 0):
    # "X BC" = year 1 - X, which is YEARS_BEFORE reckoned from year 1.
    "before_christ": Era("before_christ", AstroDate(1, 1, 1),
                         EraCounting.YEARS_BEFORE),
    # Radiocarbon "Before Present": present fixed at AD 1950.
    # Stuiver & Polach 1977, "Discussion: Reporting of 14C Data",
    # Radiocarbon 19(3):355-363 (papers/calendars/
    # stuiver_polach_1977_reporting_c14_data.pdf).
    "before_present": Era("before_present", AstroDate(1950, 1, 1),
                          EraCounting.YEARS_BEFORE),
    # Unix time: seconds since 1970-01-01T00:00:00Z, "the Epoch" per
    # POSIX.1-2017 §4.16 (papers/calendars/opengroup_epoch_seconds.html).
    "unix": Era("unix", AstroDate(1970, 1, 1),
                EraCounting.SECONDS_SINCE),
    # Julian day number: JD 0 begins Greenwich noon, 1 January 4713 BC
    # proleptic *Julian* calendar = astronomical -4712 (USNO, "Converting
    # Between Julian Dates and Gregorian Calendar Dates",
    # papers/calendars/usno_julian_date.html).  Resolution to a Gregorian
    # date is done by integer algorithm, not epoch arithmetic — see
    # julian_day_to_date().
    "julian_day": Era("julian_day", AstroDate(-4712, 1, 1),
                      EraCounting.DAYS_SINCE),
    # Holocene/Human Era (Emiliani 1993, Nature 366:716): HE = CE + 10000,
    # hence HE year 1 = 10000 BC = astronomical -9999.  (Upstream
    # lingua-franca #96 had -10000 — an off-by-one.)
    "holocene": Era("holocene", AstroDate(-9999, 1, 1)),
    # Anno Mundi (Hebrew calendar year count): AM 1 = 3761 BC =
    # astronomical -3760 (epoch Tishri 1, 3761 BC; year precision only —
    # no Hebrew-calendar conversion is attempted).
    "anno_mundi": Era("anno_mundi", AstroDate(-3760, 1, 1)),
    # French Republican era: An I began 22 September 1792 (décret of the
    # Convention nationale, 1793).  Year precision only.
    "french_republican": Era("french_republican", AstroDate(1792, 9, 22)),
    # Bahá'í (Badí') era: BE 1 began 21 March 1844.
    "bahai": Era("bahai", AstroDate(1844, 3, 21)),
    # Thai (Rattanakosin-era solar) year count as fixed by the 1941 act:
    # BE = CE + 543; era year 1 = 543 BC = astronomical -542.
    "buddhist": Era("buddhist", AstroDate(-542, 1, 1)),
}


def julian_day_to_date(jd: int) -> Union[date, AstroDate]:
    """Convert an integral Julian day number to a proleptic Gregorian date.

    Integer algorithm of Fliegel & Van Flandern (1968) as presented by
    Richards in the Explanatory Supplement to the Astronomical Almanac
    (3rd ed., ch. 15); Python floor division extends it to negative years.
    The day returned is the civil date on which that Julian day *begins*
    (Julian days start at noon).
    """
    f = jd + 1401 + (((4 * jd + 274277) // 146097) * 3) // 4 - 38
    e = 4 * f + 3
    g = (e % 1461) // 4
    h = 5 * g + 2
    day = (h % 153) // 5 + 1
    month = (h // 153 + 2) % 12 + 1
    year = e // 1461 - 4716 + (14 - month) // 12
    if date.min.year <= year <= date.max.year:
        return date(year, month, day)
    return AstroDate(year, month, day, resolution=DateTimeResolution.DAY)


def resolve_era(era: Union[str, Era], value: Union[int, float]
                ) -> Union[date, datetime, AstroDate]:
    """Resolve "value in era" into a concrete date.

    Returns plain ``datetime.date`` (or, for second-counted eras, an aware
    UTC ``datetime``) whenever the result is representable; an
    :class:`AstroDate` otherwise.  Never raises ``OverflowError``.
    """
    if isinstance(era, str):
        era = ERAS[era]

    if era.counting == EraCounting.SECONDS_SINCE:
        # sub-year precision is meaningful here; epochs are in range
        epoch = datetime(era.epoch.year, era.epoch.month or 1,
                         era.epoch.day or 1, tzinfo=timezone.utc)
        return epoch + timedelta(seconds=value)

    if era.counting == EraCounting.DAYS_SINCE:
        # julian_day is the only day-counted era; its origin is baked into
        # the conversion algorithm rather than derived from the epoch field
        return julian_day_to_date(int(value))

    value = int(value)
    if era.counting == EraCounting.YEARS_BEFORE:
        year = era.epoch.year - value
    else:  # YEARS_SINCE: era year 1 is the epoch year
        year = era.epoch.year + value - 1

    result = AstroDate(year, resolution=DateTimeResolution.YEAR)
    return result.date or result
