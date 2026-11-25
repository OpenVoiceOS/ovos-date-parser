# Calendar helpers

<!-- agent-hint
covers: the calendar range functions, the era and scoped-date scanners, and the chronologia names that this package re-exports
source: ovos_date_parser/ranges.py, ovos_date_parser/eras_scan.py, ovos_date_parser/scoped_scan.py, ovos_date_parser/scoped_en.py, ovos_date_parser/eras_<code>.py, ovos_date_parser/astrodate.py, ovos_date_parser/eras.py
generated: no
verify: sed '/^\x60\x60\x60/d' docs/helpers.md | .venv/bin/python -I -m doctest -o ELLIPSIS -o NORMALIZE_WHITESPACE /dev/stdin
see: api.md, how-it-works.md, languages.md
-->

This page documents the helpers that sit beside the main readers and writers:
the calendar range functions, the scanners for era and scoped phrases, and the
chronologia names that this package re-exports. Read it when you need the
first and last day of a week or a season, or when you read dates before the
year 1.

## Calendar ranges

The functions in `ovos_date_parser.ranges` return an inclusive `(start, end)`
pair of the same type as the reference date. A decade, a century and a
millennium follow the calendar convention: the 1990s are 1990 to 1999, and the
1900s are 1900 to 1999.

```python
>>> from datetime import date
>>> from ovos_date_parser.ranges import (get_week_range, get_weekend_range, get_month_range,
...                                      get_year_range, get_decade_range, get_century_range,
...                                      get_millennium_range, get_week_number)
>>> d = date(2024, 1, 5)
>>> get_week_range(d)
(datetime.date(2024, 1, 1), datetime.date(2024, 1, 7))
>>> get_weekend_range(d)
(datetime.date(2024, 1, 6), datetime.date(2024, 1, 7))
>>> get_month_range(d), get_year_range(d)
((datetime.date(2024, 1, 1), datetime.date(2024, 1, 31)), (datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)))
>>> get_decade_range(d), get_century_range(d), get_millennium_range(d)
((datetime.date(2020, 1, 1), datetime.date(2029, 12, 31)), (datetime.date(2000, 1, 1), datetime.date(2099, 12, 31)), (datetime.date(2000, 1, 1), datetime.date(2999, 12, 31)))
>>> get_week_number(d)
1

```

`get_week_range` runs from Monday to Sunday. `get_weekend_range` gives the
weekend that contains the date or follows it. `get_week_number` gives the
ISO 8601 week number and uses today when you pass no date.

Seasons are meteorological, so they align with months. Northern spring starts
on 1 March and southern spring starts on 1 September. The enums `Season`
(`SPRING`, `SUMMER`, `FALL`, `WINTER`) and `Hemisphere` (`NORTH`, `SOUTH`)
select the table. Each season function takes a `hemisphere` argument that
defaults to `Hemisphere.NORTH`, and a `ref_date` that defaults to today.

```python
>>> from ovos_date_parser.ranges import (Season, Hemisphere, date_to_season, get_season_range,
...                                      season_to_date, next_season_date, last_season_date)
>>> date_to_season(d), date_to_season(d, Hemisphere.SOUTH)
(<Season.WINTER: 3>, <Season.SUMMER: 1>)
>>> get_season_range(d)
(datetime.date(2023, 12, 1), datetime.date(2024, 2, 29))
>>> season_to_date(Season.SUMMER, 2024)
datetime.date(2024, 6, 1)
>>> next_season_date(Season.SPRING, d), last_season_date(Season.SPRING, d)
(datetime.date(2024, 3, 1), datetime.date(2023, 3, 1))

```

`get_date_ordinal(ordinal, ref_date=None, resolution=DateTimeResolution.DAY_OF_MONTH)`
resolves "the Nth unit of a scope" into a date. The `resolution` names the unit
and the scope, such as `DAY_OF_MONTH` or `WEEK_OF_MONTH`.

```python
>>> from ovos_date_parser import get_date_ordinal, DateTimeResolution
>>> get_date_ordinal(3, d)
datetime.date(2024, 1, 3)
>>> get_date_ordinal(3, d, DateTimeResolution.WEEK_OF_MONTH)
datetime.date(2024, 1, 15)

```

## Era phrases

An era phrase names a year with a calendar era, such as "44 BC" or "2000 years
before present". The scanner `extract_era_date(text, patterns, normalize=None)`
returns `(value, remainder, resolution)`, or `None` when the text holds no era
phrase. The value is a `date` when a `datetime` can hold it and an `AstroDate`
otherwise. `load_era_patterns(lang, locale_dir=...)` builds the pattern table
of a language from its `.voc` phrase files.

Six languages have a ready function: `extract_era_date_en`, `extract_era_date_pt`,
`extract_era_date_es`, `extract_era_date_fr`, `extract_era_date_de` and
`extract_era_date_it`. Each takes the text and answers like `extract_era_date`.
The pattern tables are the lazy names `ERA_PATTERNS_EN`, `ERA_PATTERNS_PT`,
`ERA_PATTERNS_ES`, `ERA_PATTERNS_FR`, `ERA_PATTERNS_DE` and `ERA_PATTERNS_IT`.

```python
>>> from ovos_date_parser import extract_era_date_en, extract_era_date_pt, extract_era_date, load_era_patterns
>>> extract_era_date_en("44 BC")
(AstroDate(year=-43, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None), '', <DateTimeResolution.YEAR: 17>)
>>> extract_era_date_pt("44 a.c.") == extract_era_date_en("44 BC")
True
>>> print(extract_era_date_en("hello"))
None
>>> extract_era_date("44 a.c.", load_era_patterns("pt")) == extract_era_date_en("44 BC")
True

```

The year of 44 BC is the astronomical year -43, because astronomical numbering
has a year 0.

## Scoped dates

A scoped phrase names a unit inside a larger scope: "the third week of may",
"last summer", "the 21st century". `extract_scoped_date(text, vocab, ref_date=None,
hemisphere=Hemisphere.NORTH, lang=None)` reads such a phrase with the forms in a
`ScopedVocabulary`, which `load_scoped_vocabulary(lang, locale_dir=...)` builds
from the `.voc` files of a language. It returns `(date, remainder, resolution)`,
or `None`. A named holiday is read only when you pass `lang`.
`extract_scoped_date_en(text, ref_date=None, hemisphere=Hemisphere.NORTH)` is the
English binding, and `SCOPED_VOCAB_EN` is its vocabulary.

```python
>>> from ovos_date_parser import extract_scoped_date_en, extract_scoped_date, load_scoped_vocabulary
>>> extract_scoped_date_en("the third week of may", ref_date=d)
(datetime.date(2024, 5, 20), '', <DateTimeResolution.WEEK_OF_MONTH: 7>)
>>> extract_scoped_date_en("last summer", ref_date=d)
(datetime.date(2023, 6, 1), '', <DateTimeResolution.MONTH: 12>)
>>> print(extract_scoped_date_en("hello", ref_date=d))
None

```

The `.voc` files that these loaders read are in `ovos_date_parser/locale/<code>/`
for de, es, fr, it, kab and pt. Each file holds one phrase per line. A file
here replaces the file of the same name in chronologia, and chronologia supplies
the files that this package does not ship, such as all the English ones.

## Names that chronologia owns

This package re-exports the names below so that old import paths keep working.
[chronologia](https://github.com/TigreGotico/chronologia) defines them and
documents them. The modules `ovos_date_parser.astrodate`, `calendars`, `cycles`,
`eras`, `regnal` and `roman` re-export further names in the same way.

| Name | What it is |
|---|---|
| `AstroDate` | A date and time that has no limit on the year, like a `datetime` |
| `DateSpan` | A start and an end of `AstroDate` values, with the basis of the answer |
| `DateTimeResolution` | The width that a reading answers, from a day to a millennium and beyond |
| `Era`, `EraCounting`, `ERAS` | The named eras, their counting modes and the table of them |
| `resolve_era`, `resolve_bp`, `astro_year_range`, `julian_day_to_date` | Era arithmetic: a value in an era, a Before-Present count, the span of a decade or a century, a Julian day |
| `calibrate_c14` | A coarse radiocarbon calibration to a span |
| `civil_add`, `resolve_wall_clock`, `is_leap_year` | Civil calendar arithmetic, a DST-aware wall clock and the leap-year test |
| `extract_timespan`, `explain` | The span reader of chronologia and its parse trace |
| `DAY_PARTS`, `PERIODS`, `TIMELINES` | The tables of day parts, deep-time periods and calendar timelines |
| `BEFORE_PRESENT_EPOCH` | The date from which a Before-Present year counts, 1 January 1950 |

```python
>>> from ovos_date_parser import resolve_era, resolve_bp, astro_year_range, julian_day_to_date, civil_add
>>> from ovos_date_parser import is_leap_year, BEFORE_PRESENT_EPOCH
>>> from datetime import datetime
>>> print(resolve_era("before_christ", 44))
-000043-01-01T00:00:00
>>> print(resolve_bp(2000))
-000050-01-01 – -000049-01-01
>>> print(julian_day_to_date(2460315))
2024-01-05
>>> print(civil_add(datetime(2024, 1, 31), months=1))
2024-02-29T00:00:00
>>> is_leap_year(2024), BEFORE_PRESENT_EPOCH
(True, datetime.date(1950, 1, 1))

```

---
[Index](index.md) · [← Language notes](languages.md) · [Home →](../README.md)
