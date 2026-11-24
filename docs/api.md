# API reference

<!-- agent-hint
covers: every public function of ovos_date_parser with its signature, defaults and real output
source: ovos_date_parser/__init__.py, ovos_date_parser/holidays.py, ovos_date_parser/spoken.py, ovos_date_parser/duration.py
generated: no
verify: sed '/^\x60\x60\x60/d' docs/api.md | .venv/bin/python -I -m doctest -o ELLIPSIS -o NORMALIZE_WHITESPACE /dev/stdin
see: languages.md, adding-a-language.md
-->

This page lists the public functions of `ovos_date_parser`: the readers that turn text into values, and the writers that turn values into words. Every function takes a BCP-47 language code in `lang`.

Three engines answer the functions.

| Functions | Answered by |
|---|---|
| `extract_datetime`, `extract_duration`, `extract_datetime_spans`, `extract_duration_spans`, `holidays.*`, `extract_timespan` | [chronologia](https://github.com/TigreGotico/chronologia), for the 61 locales in `ovos_date_parser.CHRONOLOGIA_LOCALES` |
| `extract_datetime` for any other locale | [dateparser](https://dateparser.readthedocs.io), the fallback |
| `nice_*`, `spoken_*`, `get_date_strings`, `nice_span` | The writers in this package |

`extract_timespan`, `explain`, `AstroDate` and `DateSpan` are chronologia names that this package re-exports. `extract_duration` answers `(None, text)` for a locale outside the set.

Readers and writers resolve the code in different ways, and [languages.md](languages.md#language-tags) gives the steps. A reader accepts a tag in any case, with `_` or `-`, and maps `deu` to `de` and `no` to `nb`. A writer lower-cases the tag.

`nice_time`, `nice_year` and the per-language branches of the other `nice_*` functions test which writer code the tag starts with, so `"pt-BR"` and `"pt"` reach Portuguese. The writers that read `res/<code>/` take the code before the first `-` and look for that folder by exact name. The table in [languages.md](languages.md#language-tags) shows the result for each function. The region `BR` selects the Brazilian number spelling (`dezesseis`, where every other Portuguese tag says `dezasseis`).

`nice_time` raises `NotImplementedError` for a tag that starts with no writer code.

```python
from ovos_date_parser import (
    extract_datetime, extract_duration,
    nice_time, nice_date, nice_date_time,
    nice_day, nice_weekday, nice_month, nice_year,
    nice_duration, nice_relative_time, get_date_strings,
)
```

Nothing here needs a running OVOS stack. The package is pure Python plus a few small parsing dependencies.

## Parsing (text to structured value)

### `extract_datetime(text, lang, anchorDate=None, default_time=None)`

Extract a datetime from a phrase. The answer is a pair of the `datetime` and the remaining text, or `None` when the text holds no date or time.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import extract_datetime
>>> extract_datetime("lets meet next friday at 8am", "en",
...                  anchorDate=datetime(2023, 1, 15))
[datetime.datetime(2023, 1, 20, 8, 0), 'lets meet']

>>> extract_datetime("amanhã às 15h30", "pt", anchorDate=datetime(2023, 1, 15))
[datetime.datetime(2023, 1, 16, 15, 30), '']

>>> print(extract_datetime("this has no date", "en"))
None
```

The pair is a list when chronologia reads the date. It is a tuple when the holiday layer answers because the reader found no date. `"christmas"` in en and `"noël"` in fr give a list. `"noel"` in fr gives a tuple.

- `anchorDate` (`datetime`): the reference instant that relative expressions ("tomorrow", "in 2 hours", "next tuesday") resolve against. It defaults to the current local time. Pass a fixed value for a repeatable result.
- `default_time` (`datetime.time`): the time of day that a phrase gets when it names a day and no time. `extract_datetime("on friday", "en", default_time=time(9, 0))` gives friday at 09:00 and not midnight.

The remaining text is the input with the recognized date and time words removed. It is the part of the phrase that is not temporal, which is useful for intent parsing or NER.

A named holiday is read too. "christmas", "next easter", the French "noel" and the Portuguese "proxima pascoa" all resolve to a date. The rule behind the name and the surfaces that each language speaks it by belong to [chronologia](https://github.com/TigreGotico/chronologia). This library copies no holiday table.

A locale in `CHRONOLOGIA_LOCALES` keeps the answer of chronologia, which reads the holiday name together with a time of day beside it. For any other locale, the holiday reading runs in one case. The language engine must read no date, and chronologia must say that a holiday construction matched. A transcript that lost its accents names the holiday as well as one that kept them: "noel" and "noël" read the same date.

Only the holiday phrase leaves the remainder. A word that the question owns stays in it, so the same question reads the same way in every language.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import extract_datetime
>>> extract_datetime("how many days until christmas", "en-US",
...                  anchorDate=datetime(2026, 9, 25))
[datetime.datetime(2026, 12, 25, 0, 0), 'how many days until']

>>> extract_datetime("combien de jours avant noel", "fr-FR",
...                  anchorDate=datetime(2026, 9, 25))
(datetime.datetime(2026, 12, 25, 0, 0), 'combien de jours avant')
```

A tense that the phrase states inside itself is still read. "next easter", "last christmas" and "christmas eve" each name their own date.

### `holidays.extract_holiday_span(text, lang, anchorDate=None)` and `holidays.extract_holiday_date(text, lang, ref_date=None)`

These functions are the holiday layer on its own, for a caller that wants a holiday and nothing else. They answer `(datetime, remainder)` and `(date, remainder)`. They answer `None` when the text names no holiday in its own language.

`holidays.holiday_surfaces(lang)` returns the table of chronologia with the holiday names that the language speaks, mapped to its language-neutral keys. A language that chronologia has no holiday data for gets an empty map, and not a guess at English.

```python
>>> from datetime import datetime
>>> from ovos_date_parser.holidays import extract_holiday_date, holiday_surfaces
>>> extract_holiday_date("christmas", "en", ref_date=datetime(2023, 1, 15))
(datetime.date(2023, 12, 25), '')

>>> print(extract_holiday_date("hello", "en"))
None

>>> holiday_surfaces("xx")
{}
```

### `extract_duration(text, lang, *, resolution=DurationResolution.TIMEDELTA, replace_token="")`

Parse a duration. The answer is `(duration, remaining_text)`. The duration is `None` when the text holds none.

```python
>>> from ovos_date_parser import extract_duration
>>> extract_duration("set a timer for 5 minutes", "en")
(datetime.timedelta(seconds=300), 'set a timer')

>>> extract_duration("nothing here", "en")
(None, 'nothing here')
```

chronologia reads every locale in `CHRONOLOGIA_LOCALES`. A month or a year is a calendar length that starts on the day of the call. "2 months" said on 27 June 2017 is 61 days. A locale outside the set answers `(None, text)`. [languages.md](languages.md) lists the locales.

`resolution` and `replace_token` are keyword-only. Both convert the answer of chronologia, a `timedelta` and the text left over, so a month or a year reaches them as a day count.

- `resolution` (`DurationResolution`): the type to return.
  - `TIMEDELTA` (default): a `datetime.timedelta`.
  - `RELATIVEDELTA`, `RELATIVEDELTA_FALLBACK` and `RELATIVEDELTA_APPROXIMATE`: a `dateutil.relativedelta` of the same length, in days and the units below a day. `RELATIVEDELTA_STRICT` is another name for `RELATIVEDELTA`.
  - `TOTAL_MICROSECONDS`, `TOTAL_MILLISECONDS`, `TOTAL_SECONDS`, `TOTAL_MINUTES`, `TOTAL_HOURS`, `TOTAL_DAYS`, `TOTAL_WEEKS`, `TOTAL_MONTHS`, `TOTAL_YEARS`, `TOTAL_DECADES`, `TOTAL_CENTURIES` and `TOTAL_MILLENNIUMS`: a `float` in that unit.
- `replace_token` (`str`): the string that replaces each consumed duration in `remaining_text`, to mark where it was found.

```python
>>> from ovos_date_parser import extract_duration
>>> from ovos_date_parser.duration import DurationResolution

>>> extract_duration("meeting in 2 weeks", "en",
...                  resolution=DurationResolution.RELATIVEDELTA,
...                  replace_token="__DUR__")
(relativedelta(days=+14), 'meeting in __DUR__')

>>> extract_duration("two hours", "en", resolution=DurationResolution.TOTAL_MINUTES)
(120.0, '')
```

Import `DurationResolution` from `ovos_date_parser.duration`.

### `extract_datetime_spans(text, lang, anchor_date=None, default_time=None)`

Extract every date or time expression in a text together with where it sits. The answer is a list of frozen `DateTimeSpan` objects with `start`, `end`, `surface` and `value`. `start` and `end` are half-open code-point offsets, so `text[start:end] == surface` always holds. The list is sorted by `start`.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import extract_datetime_spans

>>> extract_datetime_spans("wake me next friday at 5 pm", "en",
...                        anchor_date=datetime(2023, 1, 18))
[DateTimeSpan(start=8, end=27, surface='next friday at 5 pm', value=...),
 DateTimeSpan(start=13, end=27, surface='friday at 5 pm', value=...)]

>>> extract_datetime_spans("from monday to friday", "en",
...                        anchor_date=datetime(2023, 1, 15))
[DateTimeSpan(start=5, end=21, surface='monday to friday', value=...)]
```

Each span covers a whole expression, so "next friday at 5 pm" is one expression however many entries it gives, and two dates in one sentence are two expressions. `anchor_date` and `default_time` mean what they mean for `extract_datetime`. A naive anchor is read as local time, and the values come back in the zone of the anchor.

A word joins an expression when the extractor consumes it, which it reports through the leftover text. So the surface is the written phrase and not only the words that move the value: "next", "this", "at" and "pm" belong to it. A range such as "monday to friday" is one expression, and the "from" before it stays in the leftover.

Framing words are reported both ways. The template that captured the text decides which text a consumer holds. The parser does not decide it. `next {date}` captures "friday at 5 pm", where the written phrase is "next friday at 5 pm". When the framing words can go without a change of reading, the expression comes back twice. One entry holds the written phrase and one holds its core. Both entries carry the same value.

An expression with nothing to drop comes back once.

A single word left behind can still bridge two halves that need each other, as in "in two weeks and three days". Punctuation between two words is no boundary on its own. So "3 uur 's middags" and "2 hours, 30 minutes, and 10 seconds" each stay whole. An expression can run up to twenty words, long enough for "in two weeks and three days and four hours".

The cost of a scan grows with the length of the text, and each expression in the text adds to it.

The offsets are what `extract_datetime` cannot give. Its remaining text says which words it consumed. It does not say where they sat. A text with a repeated word cannot be aligned back to the input from it.

### `extract_duration_spans(text, lang)`

The same for durations. The answer holds `DurationSpan` objects whose `value` is a `timedelta`. A compound duration is one expression. Framing words such as "for" come back both ways, as they do for `extract_datetime_spans`.

```python
>>> from ovos_date_parser import extract_duration_spans
>>> extract_duration_spans("nap for two hours and thirty minutes", "en")
[DurationSpan(start=4, end=36, surface='for two hours and thirty minutes',
              value=datetime.timedelta(seconds=9000)),
 DurationSpan(start=8, end=36, surface='two hours and thirty minutes',
              value=datetime.timedelta(seconds=9000))]
```

A length of time that follows "in" is also a point in time relative to the anchor. So "in 20 minutes" comes back from both scans, with its own value in each. A bare "20 minutes" is a duration only. A spoken zero is a length like any other: "0 seconds" is a span whose value is `timedelta(0)`.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import extract_datetime_spans, extract_duration_spans
>>> anchor = datetime(2023, 1, 15)
>>> [span.surface for span in extract_datetime_spans("in 20 minutes", "en", anchor_date=anchor)]
['in 20 minutes']

>>> [span.surface for span in extract_duration_spans("in 20 minutes", "en")]
['20 minutes']

>>> extract_datetime_spans("20 minutes", "en", anchor_date=anchor)
[]
```

Two durations in one sentence stay two spans. Read as one expression, "in ten minutes and again in half an hour" is ten and a half hours, a length that nobody said. So a phrase in which the extractor lost the thread counts as one duration only when nothing inside it reads as a duration of its own.

## Deprecated reader names

The per-language reader names `extract_datetime_<lang>` and `extract_duration_<lang>` are deprecated. Each one calls `extract_datetime(text, lang)` or `extract_duration(text, lang)` and gives a `DeprecationWarning` that names the removal version. The names exist for these codes:

`extract_datetime_<lang>` exists for these codes:

```text
an ar ast az bg ca cs da de el en es et eu fa fi fr fy gl he hr hu id it kab ms nb nl nn oc pl pt ro ru sk sl sv tr uk
```

`extract_duration_<lang>` exists for these codes:

```text
an ar ast az bg ca cs da de el en es et eu fa fi fr fy gl he hr hu it kab nb nl nn pl pt ro ru sk sl sv uk
```

```python
>>> from datetime import datetime
>>> import warnings
>>> import ovos_date_parser

>>> with warnings.catch_warnings(record=True) as caught:
...     warnings.simplefilter("always")
...     reader = ovos_date_parser.extract_datetime_pt

>>> str(caught[0].message)
"extract_datetime_pt is deprecated and is removed in 1.0.0; use extract_datetime(text, 'pt')"

>>> reader("amanhã às 15h30", anchorDate=datetime(2023, 1, 15))
[datetime.datetime(2023, 1, 16, 15, 30), '']
```

The reader takes `anchorDate` and `default_time` for dates, and `resolution` and `replace_token` for durations. The warning fires when you look the name up, and not when you call the reader.

## Formatting (datetime to text)

### `nice_time(dt, lang, speech=True, use_24hour=False, use_ampm=False, variant=None)`

The speakable or display form of a time.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_time
>>> nice_time(datetime(2023, 1, 15, 13, 30), "en")
'half past one'

>>> nice_time(datetime(2023, 1, 15, 13, 30), "en", speech=False)
'1:30'

>>> nice_time(datetime(2023, 1, 15, 13, 30), "en", use_24hour=True)
'thirteen thirty'
```

- `speech`: words for TTS (`True`) or a digit clock string (`False`).
- `use_24hour`: a 24-hour reading ("thirteen thirty") and not a 12-hour reading.
- `use_ampm`: add the am/pm or part-of-day marker in 12-hour mode.
- `variant`: a time-telling register for ca, sk, hr and bg. ca takes a `TimeVariantCA` member or one of the strings `"standard"`, `"central"` and `"quarts"`. sk, hr and bg take `"traditional"` or `"analog"`. Other languages ignore it.

Catalan can read the clock in several styles. Import the enum and pass it as `variant`.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_time
>>> from ovos_date_parser.dates_ca import TimeVariantCA
>>> nice_time(datetime(2023, 1, 15, 15, 30), "ca")
'les tres i trenta'

>>> nice_time(datetime(2023, 1, 15, 15, 30), "ca", variant=TimeVariantCA.BELL)
'dos quarts de quatre de la tarda'
```

`TimeVariantCA` members are `DEFAULT`, `BELL`, `FULL_BELL` and `SPANISH_LIKE`. Slovak, Croatian and Bulgarian read the minutes as numbers by default. With `variant="traditional"` or `variant="analog"` on the 12-hour clock, they read the last quarter against the next hour: `trištvrte na štyri` (sk), `petnaest do četiri` (hr) and `четири без четвърт` (bg).

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_time
>>> [nice_time(datetime(2023, 1, 15, 15, 45), "sk", variant=v) for v in (None, "analog")]
['tri štyridsaťpäť', 'trištvrte na štyri']

>>> [nice_time(datetime(2023, 1, 15, 15, 45), lang, variant="analog") for lang in ("hr", "bg")]
['petnaest do četiri', 'четири без четвърт']
```

### `nice_date(dt, lang, now=None, include_weekday=True)`

The pronounceable date. When you pass the third argument, a reference datetime, the output gets shorter relative to it. The same day gives "today", the adjacent days give "tomorrow" or "yesterday", and the year drops when it matches the reference. `include_weekday=False` drops the weekday.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_date
>>> nice_date(datetime(2024, 1, 5), "en")
'friday, january fifth, twenty twenty four'

>>> today = datetime(2023, 1, 15)
>>> nice_date(datetime(2023, 1, 16), "en", today)
'tomorrow'

>>> nice_date(datetime(2023, 3, 5), "en", today), nice_date(datetime(2023, 3, 5), "en", today, include_weekday=False)
('sunday, march fifth', 'march fifth')
```

### `nice_date_time(dt, lang, now=None, use_24hour=False, use_ampm=False)`

The date and the time together. The reference datetime, `use_24hour` and `use_ampm` behave as they do in `nice_date` and `nice_time`.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_date_time
>>> nice_date_time(datetime(2023, 6, 6, 13, 30), "en")
'tuesday, june sixth, twenty twenty three at half past one'
```

### `nice_day(dt, lang, date_format='DMY', include_month=True)`

The day number, with the month when `include_month` is true. `date_format` (`'DMY'`, `'MDY'` or `'YMD'`) sets the order.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_day
>>> nice_day(datetime(2023, 6, 6), "en"), nice_day(datetime(2023, 6, 6), "en", date_format="MDY")
('06 June', 'June 06')
```

### `nice_weekday(dt, lang)`, `nice_month(dt, lang, date_format='MDY')` and `nice_year(dt, lang, bc=False, ad=False)`

These functions write the single components of a date in speakable form.

`nice_year` appends a B.C. marker when `bc=True`, because a Python `datetime` cannot represent B.C. years directly. An `AstroDate` in the B.C. range is spoken as its era year: 300 BC, not the astronomical -299. Some locales, Danish among them, take `ad=True` to add a marker for the Christian era. When you set both, `bc` wins. A locale that defines no marker ignores `ad`.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_year, nice_weekday, nice_month
>>> nice_year(datetime(1984, 1, 1), "en")
'nineteen eighty four'

>>> nice_weekday(datetime(2023, 6, 6), "en"), nice_month(datetime(2023, 6, 6), "en")
('Tuesday', 'June')
```

The datetime formatters (`nice_time`, `nice_date`, `nice_date_time`, `nice_day`, `nice_weekday`, `nice_month`, `nice_year` and `nice_relative_time`) also accept an `AstroDate`. This is the unbounded `datetime` that a `DateSpan` holds. A point that fits the `datetime` range is projected without a change. A year-only call (`nice_year`) works even for a year that no `datetime` can hold.

### `nice_span(span, lang="en-us")`

`nice_span` labels a `DateSpan` at the granularity that its width carries, because the width is the precision. A one-day span reads as a date and a month-wide span as a month. A year reads as a bare year, a decade as "the 1980s" and a century as "the Nth century". The rule holds down to BC eras, which carry their era year ("300 BC"). The function is the inverse of `extract_timespan`: in English a label from a day up reads back to the same span.

```python
>>> from ovos_date_parser import extract_timespan, nice_span
>>> span, _ = extract_timespan("the 19th century", "en")
>>> nice_span(span, "en")
'the 19th century'

>>> span, _ = extract_timespan("July 2026", "en")
>>> nice_span(span, "en")
'July 2026'
```

Other languages get labels in their own words for the day, week, month and year widths. Arabic and Hebrew also name decades of the 20th century, the only century that their bare decade word can express. Coarser widths have no localised construction, so `nice_span` raises `NotImplementedError` and does not fall back to English.

The round-trip guarantee is English-only. It covers the day width and up, for years from 1000 AD onward and from 32 BC back. Outside that range the year numeral is ambiguous. A one-digit or two-digit year reads as a day of the month. A bare three-digit year does not read as a year. A decade below 1000 resolves against the century of the anchor. 

A sub-day span reads as a spoken date and time. A BC week cannot be read back, because the week resolver projects to a `datetime`. Those widths still get a correct label, and only the inverse is missing.

### `nice_duration(duration, lang, speech=True)`

The speakable form of a length of time. It accepts seconds (`int` or `float`) or a `timedelta`.

```python
>>> from ovos_date_parser import nice_duration
>>> nice_duration(61, "en")
'one minute one second'

>>> nice_duration(5000, "en", speech=False)
'1:23:20'
```

### `nice_relative_time(when, relative_to=None, lang="en-us")`

A short description of an instant relative to `relative_to` (default: the current time), in a "twenty four hours" or "five days" style. Every language except Basque uses one shared writer.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_relative_time
>>> nice_relative_time(datetime(2023, 1, 20), datetime(2023, 1, 15), "en")
'five days'

>>> nice_relative_time(datetime(2023, 1, 20), datetime(2023, 1, 15), "eu")
'bost egun'
```

### `get_date_strings(dt, lang, date_format=None, time_format="full")`

A dict of display strings for GUI clients. `date_format` defaults to the value in the OVOS configuration, or `'DMY'`. `time_format="full"` selects a 24-hour `time_string`.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import get_date_strings
>>> get_date_strings(datetime(2023, 1, 15, 13, 30), "en", date_format="DMY")
{'date_string': '15/1/2023', 'time_string': '13:30', 'month_string': 'January', 'day_string': '15', 'year_string': '2023', 'weekday_string': 'Sunday'}
```

## Spoken forms

The `spoken_time`, `spoken_date` and `spoken_year` functions in `ovos_date_parser.spoken` write Dutch, Italian and Portuguese. They take the language tag first and then only the fields that a text writes. None of them reads the clock or the current date. The output is words only. A language, field, style or case with no reading raises `UnsupportedForm`, a subclass of `NotImplementedError`. A value out of range raises `ValueError`.

```python
>>> from ovos_date_parser.spoken import spoken_date, spoken_time, spoken_year
>>> spoken_time("nl", 15, 45)
'vijftien uur vijfenveertig'

>>> spoken_time("pt-BR", 15, 30, clock="12h", style="phrase", period=True)
'três e meia da tarde'

>>> spoken_date("pt", day=5, month=1, year=2024, weekday=4)
'sexta-feira cinco de janeiro de dois mil e vinte e quatro'

>>> spoken_year("nl", 2024)
'tweeduizend vierentwintig'
```

- `spoken_time(lang, hour, minute=0, second=None, *, clock="24h", style="digits", period=False, case=None)`: `clock` is `"24h"` or `"12h"`. `style` is `"digits"`, `"units"` or `"phrase"`. `period=True` adds the part of the day in a 12-hour reading. The second is spoken only when you pass it.
- `spoken_date(lang, *, day=None, month=None, year=None, weekday=None, case=None, declension=None)`: you must pass a day, a month or a year. `weekday` counts from 0 for Monday.
- `spoken_year(lang, year, *, ordinal=False, case=None, declension=None)`: the year is from 1 to 9999.

---
[← README](../README.md) · [Home](index.md) · [Languages →](languages.md)
