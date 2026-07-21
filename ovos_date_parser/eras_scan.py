"""Language-agnostic era-phrase scanning machinery.

A language module contributes only *vocabulary*: an ordered list of
``(era_key, compiled_pattern)`` pairs plus an optional text normaliser
(typically the language's spelled-number-to-digit function).  Everything
else — value extraction, epoch resolution, the in-range/AstroDate return
rule, remainder cleanup — lives here, so adding a language never means
re-implementing era logic (the same core/vocabulary split used by the
number parser's shared extractor engine).

Pattern contract:

* exactly one capturing group must match, holding the digits of the value
  (multiple alternative groups are fine as long as a single one matches);
* patterns are tried in order, first match wins — put longer, more
  specific phrasing first;
* ``era_key`` is either a key into :data:`ovos_date_parser.eras.ERAS` or
  one of the pseudo-keys handled structurally for every language:

  - ``__bare_year__`` — "in the year N": claimed only when N is outside
    the ``datetime`` range (representable years belong to the ordinary
    scanner);
  - ``__century_bc__`` / ``__millennium_bc__`` — ordinal periods on the
    BC axis; the earliest year of the period is returned, mirroring
    ``get_date_ordinal`` on the AD axis.
"""
import re
from datetime import date, datetime
from typing import Callable, List, Optional, Pattern, Tuple, Union

from ovos_date_parser.eras import AstroDate, resolve_era
from ovos_date_parser.ranges import DateTimeResolution

EraPatterns = List[Tuple[str, Pattern]]


def extract_era_date(text: str, patterns: EraPatterns,
                     normalize: Optional[Callable[[str], str]] = None
                     ) -> Optional[Tuple[Union[date, datetime, AstroDate],
                                         str,
                                         DateTimeResolution]]:
    """Extract an era-qualified date from ``text`` using a language's
    vocabulary.

    Args:
        text: phrase possibly containing an era-qualified year/count.
        patterns: the language's ordered ``(era_key, pattern)`` vocabulary.
        normalize: optional text normaliser applied first (typically the
            language's spelled-number-to-digits function).

    Returns:
        ``(value, remainder, resolution)`` — ``value`` is a plain
        ``datetime.date`` (or aware UTC ``datetime`` for second-counted
        eras) when representable and an :class:`AstroDate` otherwise;
        ``remainder`` is the normalised text with the era phrase removed —
        or ``None`` when no era phrasing is present.
    """
    if not text:
        return None
    normalized = normalize(text) if normalize else text

    for key, pattern in patterns:
        match = pattern.search(normalized)
        if not match:
            continue
        value = int(next(g for g in match.groups() if g is not None))

        if key == "__bare_year__":
            # representable years belong to the ordinary scanner
            if date.min.year <= value <= date.max.year:
                continue
            result = resolve_era("common_era", value)
            resolution = DateTimeResolution.YEAR
        elif key in ("__century_bc__", "__millennium_bc__"):
            if value < 1:
                continue
            span = 100 if key == "__century_bc__" else 1000
            # the Nth century BC spans 100N BC .. (100N-99) BC; the
            # earliest year is returned (astronomical 1 - span*N)
            resolution = DateTimeResolution.CENTURY if span == 100 \
                else DateTimeResolution.MILLENNIUM
            result = AstroDate(1 - span * value, 1, 1, resolution=resolution)
        else:
            # DateTimeResolution has no sub-day members; second-counted
            # eras return an aware datetime that carries the precision
            resolution = DateTimeResolution.DAY \
                if key in ("unix", "julian_day") else DateTimeResolution.YEAR
            result = resolve_era(key, value)

        remainder = (normalized[:match.start()] +
                     normalized[match.end():]).strip()
        remainder = re.sub(r"\s{2,}", " ", remainder)
        return result, remainder, resolution
    return None
