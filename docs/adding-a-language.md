# Adding a language

Every language lives in its own module, `ovos_date_parser/dates_<code>.py`,
and is wired into the dispatcher functions in `ovos_date_parser/__init__.py`.

## 1. Functions to provide

Parsing:

- `extract_datetime_<code>(text, anchorDate=None, default_time=None)` —
  returns `[datetime, remaining_text]` or `None`. Handle at least: weekday
  names, month + day (+ optional year), today/tomorrow/yesterday, relative
  offsets ("in N hours/days/weeks"), morning/afternoon/evening qualifiers,
  and digit times.
- Duration parsing — the preferred path is the **shared duration engine**:
  register a `DurationLexicon` (unit words + conjunctions) with
  `register_duration_lexicon(...)` in `ovos_date_parser/duration.py`, then have
  `extract_duration_<code>` delegate to
  `extract_duration_generic(text, DURATION_LEXICONS["<code>"], ...)`. Languages
  on this engine get `resolution` and `replace_token` support for free. A
  standalone `extract_duration_<code>(text) -> (timedelta, remaining_text)` is
  only needed when a language cannot use the shared lexicon.

Formatting:

- `nice_time_<code>(dt, speech=True, use_24hour=False, use_ampm=False)`
- `nice_date_<code>`, `nice_date_time_<code>`, `nice_year_<code>`,
  `nice_weekday_<code>`, `nice_month_<code>`, `nice_day_<code>`
- `nice_duration_<code>` (optional — `nice_duration_generic` covers basic
  needs via a unit-word table)

Use a structurally close existing language as the template; the es/pt/eu
modules share one lineage, en/nl/de another.

Number words come from
[ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser) —
add the language there first if it is missing.

## 2. Resources

Display formats (dates as strings for GUIs) live in
`ovos_date_parser/res/<lang>/date_time.json`. Copy `res/en/date_time.json`
and translate.

## 3. Dispatcher

Add the language-prefix branch to each matching top-level function in
`__init__.py` (`extract_datetime`, `extract_duration`, `nice_time`,
`nice_date`, ...).

## 4. Tests

Add `test/parse_tests/test_parse_<code>.py` and
`test/format_tests/test_format_<code>.py`. Cover:

- absolute dates ("june 5th 2023"), with and without year
- relative dates against a fixed `anchorDate`
- times in spoken and digit form, morning/evening disambiguation
- durations, including fractions ("half an hour")
- `None` returns for date-less input
- `nice_time` across the special minutes (00, 15, 30, 45, o'clock styles)
- `nice_date` shortening against `now` (today/tomorrow/yesterday)

Anchor expectations must come from reference material or native usage —
never pin unverified engine output as gold.

## 5. README

Add the language rows to the parse and format matrices in `README.md`.
