# API reference

All public functions live in the top-level `ovos_date_parser` package and take
a BCP-47 language code (`lang`). Dialects resolve by prefix (`"pt-BR"`,
`"pt-PT"` and `"pt"` all reach the Portuguese parser). Unsupported languages
raise `NotImplementedError`; `extract_datetime` falls back to
[dateparser](https://dateparser.readthedocs.io) before giving up.

```python
from ovos_date_parser import (
    extract_datetime, extract_duration,
    nice_time, nice_date, nice_date_time,
    nice_day, nice_weekday, nice_month, nice_year,
    nice_duration, nice_relative_time, get_date_strings,
)
```

Nothing here needs a running OVOS stack; the package is pure Python plus a few
small parsing dependencies.

## Parsing (text → structured value)

### `extract_datetime(text, lang, anchorDate=None, default_time=None)`

Extract a datetime from a phrase. Returns `[datetime, remaining_text]`, or
`None` when the text contains no date or time.

```python
>>> from datetime import datetime, time
>>> extract_datetime("lets meet next friday at 8am", "en",
...                  anchorDate=datetime(2023, 1, 15))
[datetime.datetime(2023, 1, 20, 8, 0), 'lets meet']
>>> extract_datetime("amanhã às 15h30", "pt", anchorDate=datetime(2023, 1, 15))
[datetime.datetime(2023, 1, 16, 15, 30), '']
>>> extract_datetime("this has no date", "en")
None
```

- `anchorDate` (`datetime`) — the "now" that relative expressions
  ("tomorrow", "in 2 hours", "next tuesday") are resolved against; defaults to
  the current local time. Pass a fixed value for deterministic extraction.
- `default_time` (`datetime.time`) — used when the phrase names a day but no
  time. `extract_datetime("on friday", "en", default_time=time(9, 0))`
  resolves to friday at 09:00 instead of midnight.

The returned `remaining_text` is the input with the recognized date/time words
removed — the non-temporal payload, handy for intent parsing or NER.

### `extract_duration(text, lang, *, resolution=DurationResolution.TIMEDELTA, replace_token="")`

Parse a duration. Returns `(duration, remaining_text)`; `duration` is `None`
when nothing is found.

```python
>>> extract_duration("set a timer for 5 minutes", "en")
(datetime.timedelta(seconds=300), 'set a timer for')
>>> extract_duration("nothing here", "en")
(None, 'nothing here')
```

`resolution` and `replace_token` are keyword-only and only supported for the
languages on the **shared duration engine** (ar, ast, fa, kab and sv use a
simpler dedicated parser and accept neither — passing them raises
`NotImplementedError`).

- `resolution` (`DurationResolution`) — the type to return:
  - `TIMEDELTA` (default) — a `datetime.timedelta`.
  - `RELATIVEDELTA` — a calendar-accurate `dateutil.relativedelta`, so
    "2 months" stays 2 months rather than an approximate day count.
  - single-unit totals such as `TOTAL_SECONDS`, `TOTAL_MINUTES`,
    `TOTAL_HOURS`, `TOTAL_DAYS` — a `float` in that unit.
- `replace_token` (`str`) — string that each consumed duration is replaced
  with in `remaining_text`, marking where it was found.

```python
>>> from ovos_date_parser.duration import DurationResolution
>>> extract_duration("meeting in 2 weeks", "en",
...                  resolution=DurationResolution.RELATIVEDELTA,
...                  replace_token="__DUR__")
(relativedelta(days=+14), 'meeting in __DUR__')
```

Import `DurationResolution` from `ovos_date_parser.duration`.

## Formatting (datetime → text)

### `nice_time(dt, lang, speech=True, use_24hour=False, use_ampm=False, variant=None)`

Speakable or display form of a time.

```python
>>> nice_time(datetime(2023, 1, 15, 13, 30), "en")
'half past one'
>>> nice_time(datetime(2023, 1, 15, 13, 30), "en", speech=False)
'1:30'
>>> nice_time(datetime(2023, 1, 15, 13, 30), "en", use_24hour=True)
'thirteen thirty'
```

- `speech` — words for TTS (`True`) or a digit clock string (`False`).
- `use_24hour` — 24-hour reading ("thirteen thirty") instead of 12-hour.
- `use_ampm` — add the am/pm / part-of-day marker in 12-hour mode.
- `variant` — Catalan-only register selector (`TimeVariantCA`, see below).
  Ignored by other languages.

**Catalan registers.** Catalan can read the clock in several styles. Import the
enum and pass it as `variant`:

```python
>>> from ovos_date_parser.dates_ca import TimeVariantCA
>>> nice_time(datetime(2023, 1, 15, 15, 30), "ca")                          # DEFAULT
'les tres i trenta'
>>> nice_time(datetime(2023, 1, 15, 15, 30), "ca", variant=TimeVariantCA.BELL)
'dos quarts de quatre de la tarda'
```

`TimeVariantCA` members: `DEFAULT`, `BELL`, `FULL_BELL`, `SPANISH_LIKE`.

### `nice_date(dt, lang, now=None, include_weekday=True)`

Pronounceable date. When `now` is given, the output is shortened relative to
it — same day returns "today", adjacent days "tomorrow"/"yesterday", the year
is omitted when it matches `now`. `include_weekday=False` drops the weekday.

```python
>>> nice_date(datetime(2024, 1, 5), "en")
'friday, january fifth, twenty twenty four'
```

### `nice_date_time(dt, lang, now=None, use_24hour=False, use_ampm=False)`

Date and time combined ("tuesday, june fifth at half past one"). `now`,
`use_24hour` and `use_ampm` behave as in `nice_date` / `nice_time`.

### `nice_day(dt, lang, date_format='DMY', include_month=True)`

Day number, optionally with the month, ordered by `date_format` (`'DMY'`,
`'MDY'` or `'YMD'`).

### `nice_weekday(dt, lang)` / `nice_month(dt, lang, date_format='MDY')` / `nice_year(dt, lang, bc=False, ad=False)`

Individual components in speakable form. `nice_year` appends a B.C. marker when
`bc=True` (Python `datetime` cannot itself represent B.C. years). Some locales
(currently Danish) also support an explicit A.D./C.E. marker via `ad=True`;
`bc` takes precedence if both are set. `ad` is a no-op for locales that don't
define one.

```python
>>> nice_year(datetime(1984, 1, 1), "en")
'nineteen eighty four'
```

### `nice_duration(duration, lang, speech=True)`

Speakable timespan. Accepts seconds (`int`/`float`) or a `timedelta`.

```python
>>> nice_duration(61, "en")
'one minute one second'
>>> nice_duration(5000, "en", speech=False)
'1:23:20'
```

### `nice_relative_time(when, relative_to=None, lang="en-us")`

Short relative description of an instant relative to `relative_to` (default:
now) — "twenty four hours", "five days" style. Every language except Basque
uses a shared, functional-but-generic implementation.

### `get_date_strings(dt, lang, date_format=None, time_format="full")`

Dict of display strings for GUI clients:

```python
{'date_string', 'time_string', 'month_string',
 'day_string', 'year_string', 'weekday_string'}
```

`date_format` defaults to the OVOS configuration value (or `'DMY'`);
`time_format="full"` selects a 24-hour `time_string`.
