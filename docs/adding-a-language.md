# Adding a language

Every language lives in its own module, `ovos_date_parser/dates_<code>.py`,
and is wired into the dispatcher functions in `ovos_date_parser/__init__.py`.

## 1. Functions to provide

Parsing:

- `extract_datetime_<code>(text, anchorDate=None, default_time=None)`:
  returns `[datetime, remaining_text]` or `None`. Handle at least: weekday
  names, month plus day (plus optional year), today/tomorrow/yesterday,
  relative offsets ("in N hours/days/weeks"), morning/afternoon/evening
  qualifiers, and digit times.
- Duration parsing: the preferred path is the shared duration engine.
  Register a `DurationLexicon` (unit words and conjunctions) with
  `register_duration_lexicon(...)` in `ovos_date_parser/duration.py`, then have
  `extract_duration_<code>` delegate to
  `extract_duration_generic(text, DURATION_LEXICONS["<code>"], ...)`. Languages
  on this engine get `resolution` and `replace_token` support for free. A
  standalone `extract_duration_<code>(text) -> (timedelta, remaining_text)` is
  needed only when a language cannot use the shared lexicon.

Formatting:

- `nice_time_<code>(dt, speech=True, use_24hour=False, use_ampm=False)`
- `nice_date_<code>`, `nice_date_time_<code>`, `nice_year_<code>`,
  `nice_weekday_<code>`, `nice_month_<code>`, `nice_day_<code>`
- `nice_duration_<code>` (optional. `nice_duration_generic` covers basic
  needs via a unit-word table)

Use a structurally close existing language as the template. The es/pt/eu
modules share one lineage, and en/nl/de share another.

Number words come from
[ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser).
Add the language there first if it is missing.

## 2. Resources

Display formats (dates as strings for GUIs) live in
`ovos_date_parser/res/<lang>/date_time.json`. Copy `res/en/date_time.json`
and translate it.

## 3. Dispatcher

Add the language-prefix branch to each matching top-level function in
`__init__.py` (`extract_datetime`, `extract_duration`, `nice_time`,
`nice_date`, and the rest).

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

Anchor expectations must come from reference material or native usage.
Never pin unverified engine output as gold.

### Relative weeks, months and years

"Next week" is the week after the current one. It opens on that week's first
day as the locale reckons it -- Monday in most of Europe, Sunday in the United
States, Saturday in much of the Arabic-speaking world -- and it is seven days
wide. It does not mean this same weekday one week from now. The same holds for
"next month" and "next year": the month after this one, opening on its first
day, not thirty days out.

The two readings agree only when the anchor falls on the week's first day,
which is why an offset of seven days passes a test written on a Monday and
fails on every other day. Several locales here pin the offset reading; they
were written against an anchor where both readings agree, so the check passed
and could not distinguish the two meanings.

Two things make the assertion discriminating. Choose an anchor deliberately
mid-week, so the readings cannot coincide. And derive the expected date from
the locale's declared week start rather than by arithmetic on the anchor -- a
pin that computes its expectation the way the code computes its answer
confirms only that the two agree.

Take the week start from CLDR, not from the locale's neighbours. Getting it
wrong is invisible in a suite whose anchor happens to be the right weekday.

`next <weekday>` is the same word doing the same job, and it resolves the same
way: find the week after the current one, then take that weekday within it.
Said on a Wednesday, "next Thursday" is eight days out, not tomorrow. The
reading that answers tomorrow makes "next Thursday" and "tomorrow" mean the
same thing one day in seven.

A minimum-distance rule -- refusing anything closer than forty-eight hours,
say -- approximates this well enough to pass most tests, because it agrees
with the calendar reading everywhere except close to the week boundary. It is
worth knowing that is what such a rule is doing: a heuristic standing in for
the calendar, not a definition, and it diverges exactly where the two
disagree.

## 5. README

Add the language rows to the parse and format matrices in `README.md`.

---
[← Language notes](languages.md) · [Home](../README.md)
