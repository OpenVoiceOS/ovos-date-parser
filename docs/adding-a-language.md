# Adding a language

<!-- agent-hint
covers: the two paths for a new language, reading in chronologia and writing in a nice_* module here
source: ovos_date_parser/__init__.py:CHRONOLOGIA_LOCALES, nice_time, nice_date, nice_duration; ovos_date_parser/dates_ms.py; ovos_date_parser/res/
generated: no
verify: diff <(sed -n '/^\x60\x60\x60python/,/^\x60\x60\x60$/p' docs/adding-a-language.md | sed '1d;$d' | .venv/bin/python -I -) <(sed -n '/^\x60\x60\x60text/,/^\x60\x60\x60$/p' docs/adding-a-language.md | sed '1d;$d')
see: languages.md, api.md
-->

A language has two independent paths in this package: reading, which chronologia owns, and writing, which lives here. This page walks both. Do the path you need, or both.

## Which path do you need

Run this check first. It lists which functions already work for a language code.

```python
import logging
from datetime import datetime, timedelta
import ovos_date_parser as p

logging.disable(logging.CRITICAL)  # a missing resource file logs a warning

dt = datetime(2024, 1, 5, 15, 30)
for name, call in {
    "nice_time": lambda c: p.nice_time(dt, c),
    "nice_date": lambda c: p.nice_date(dt, c),
    "nice_year": lambda c: p.nice_year(dt, c),
    "nice_duration": lambda c: p.nice_duration(3690, c),
    "nice_relative_time": lambda c: p.nice_relative_time(dt + timedelta(days=5), dt, c),
}.items():
    try:
        call("id")
        print(name, "ok")
    except Exception as error:
        print(name, type(error).__name__)
print("reads:", "id" in p.CHRONOLOGIA_LOCALES)
```

For Indonesian the output is:

```text
nice_time ok
nice_date NotImplementedError
nice_year NotImplementedError
nice_duration ok
nice_relative_time ok
reads: True
```

A language with `reads: False` needs the reading path. A language that raises `NotImplementedError` needs the writing path.

## Reading: add the language to chronologia

This package holds no reader for a chronologia locale. `extract_datetime` and `extract_duration` normalize the tag and call chronologia, so the language must exist there first. Follow
[chronologia's guide](https://github.com/TigreGotico/chronologia/blob/dev/docs/adding-a-language.md). It covers the vocabulary files, their sources and their tests.

When the chronologia release that reads the language is published, make two changes here:

1. Raise the floor of `chronologia` in `pyproject.toml` to that release.
2. Add the code to `CHRONOLOGIA_LOCALES` in `ovos_date_parser/__init__.py`. A locale outside the set goes to the dateparser fallback for dates and answers `(None, text)` for durations.

The same entry gives the language `extract_duration`. A month or a year counts on the calendar from the day of the call. The `resolution` and `replace_token` options convert chronologia's answer.

Phrase files that this package adds on top of chronologia, such as era and calendar-scoped phrases, live in `ovos_date_parser/locale/<code>/*.voc`. A file there overrides the file of the same name in chronologia.

## Writing: add a nice_* module

Write the clock first, then the date family, then the duration words.

1. Create `ovos_date_parser/dates_<code>.py`. Start from a language that is close to yours: `dates_pt.py`, `dates_es.py` and `dates_eu.py` share a lineage, and so do `dates_en.py`, `dates_nl.py` and `dates_de.py`. Put the sources of every word in the module docstring, as `dates_kab.py` does.

2. Write `nice_time_<code>(dt, speech=True, use_24hour=False, use_ampm=False)`. With `speech=False` it returns the digit clock.

3. Import it in `ovos_date_parser/__init__.py`, add the code to `_WRITER_LANGS` in `ovos_date_parser/common.py`, and add a `code == "<code>"` branch to `nice_time`. Without the branch, `nice_time` raises `NotImplementedError: Unsupported language`.

4. Add the date family. Two routes work.

   - Write `nice_date_<code>`, `nice_date_time_<code>`, `nice_day_<code>`, `nice_weekday_<code>`, `nice_month_<code>` and `nice_year_<code>`. Add a branch for each to the matching `nice_*` function in `__init__.py`, as Romanian and Hebrew do.

   - Or write `ovos_date_parser/res/<code>/date_time.json`. The generic engine `DateTimeFormat` reads it for `nice_date`, `nice_date_time`, `nice_day`, `nice_weekday`, `nice_month` and `nice_year`. Copy `res/en/date_time.json` and translate it. The loader requires the keys `decade_format`, `hundreds_format`, `thousand_format` and `year_format`.

5. Write `ovos_date_parser/res/<code>/date_words.json` with the nine keys of `res/en/date_words.json`: one word for the moment of the call, and the singular and plural of second, minute, hour and day. The shared `nice_duration` and `nice_relative_time` read it. Add a `nice_duration_<code>` function and a branch in `nice_duration` only when the shared writer cannot say the language, as Polish and Russian need.

6. Number words come from [ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser). Add the language there first when it lacks them.

Run the check from the first section again. Every line must read `ok`.

## Tests

Test files sit in `test/`. Writers go in `test/format_tests/test_format_<code>.py` or `test/test_dates_<code>.py`. Cover:

- `nice_time` for the special minutes (00, 15, 30, 45), with and without `use_24hour` and `use_ampm`
- `nice_date` against the reference date: today, tomorrow and yesterday
- `nice_duration` and `nice_relative_time`
- a `NotImplementedError` check for every form the language does not write

Take every expected string from a source and not from the output of the code. Never pin an unverified output as gold. A reader test belongs in chronologia. Here, only the routing test `test/test_chronologia_routing.py` runs over `CHRONOLOGIA_LOCALES`, and it picks up the new code by itself.

Add the language code to `LANGS` in `test/test_lang_parity.py` when it writes every function.

Then update the language lists in [languages.md](languages.md).

---
[← Languages](languages.md) · [Home](index.md)
