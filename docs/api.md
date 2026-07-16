# API reference

All public functions live in the top-level `ovos_date_parser` package and take
a BCP-47 language code (`lang`). Dialects resolve by prefix (`"pt-BR"`,
`"pt-PT"` and `"pt"` all reach the Portuguese parser). Unsupported languages
raise `NotImplementedError`; `extract_datetime` falls back to
[dateparser](https://dateparser.readthedocs.io) before giving up.

## Parsing

### `extract_datetime(text, lang, anchorDate=None, default_time=None)`

Extract a datetime from a phrase. Returns `[datetime, remaining_text]`, or
`None` when the text contains no date or time.

```python
>>> from datetime import datetime
>>> extract_datetime("lets meet next friday at 8am", "en",
...                  anchorDate=datetime(2023, 1, 15))
[datetime.datetime(2023, 1, 20, 8, 0), 'lets meet']
>>> extract_datetime("amanhã às 15h30", "pt", anchorDate=datetime(2023, 1, 15))
[datetime.datetime(2023, 1, 16, 15, 30), '']
>>> extract_datetime("this has no date", "en")
None
```

- `anchorDate` — the "now" that relative expressions are resolved against;
  defaults to the current local time.
- `default_time` — `datetime.time` used when the phrase names a day but no
  time ("on friday" → friday at `default_time`).

### `extract_duration(text, lang)`

Parse a duration. Returns `(timedelta, remaining_text)`; the timedelta is
`None` when no duration is found.

```python
>>> extract_duration("set a timer for 5 minutes", "en")
(datetime.timedelta(seconds=300), 'set a timer for')
>>> extract_duration("nothing here", "en")
(None, 'nothing here')
```

## Formatting

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

### `nice_date(dt, lang, now=None)`

Pronounceable date. When `now` is given, the output is shortened relative to
it — same day returns "today", adjacent days "tomorrow"/"yesterday", the year
is omitted when it matches.

### `nice_date_time(dt, lang, now=None, use_24hour=False, use_ampm=False)`

Date and time combined ("tuesday, june fifth at half past one").

### `nice_day(dt, lang, date_format='DMY', include_month=True)` / `nice_weekday(dt, lang)` / `nice_month(dt, lang)` / `nice_year(dt, lang, bc=False)`

Individual date components in speakable form.

### `nice_duration(duration, lang, speech=True)`

Speakable timespan. Accepts seconds (int/float) or a `timedelta`.

```python
>>> nice_duration(61, "en")
'one minute one second'
>>> nice_duration(5000, "en", speech=False)
'1:23:20'
```

### `nice_relative_time(when, relative_to=None, lang="en-us")`

Short relative description of a future or past instant ("in 2 hours",
"in 5 days").

### `get_date_strings(dt, lang, date_format='MDY', time_format='full')`

Dict of display strings for GUI clients (`date_string`, `time_string`,
`weekday_string`, `day_string`, `month_string`, `year_string`).
