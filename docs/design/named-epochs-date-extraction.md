# Named epochs & the extract_date / extract_time split

Scope for extending date extraction to understand **named eras, epochs, named
dates and calendar-scoped ordinals** ("the third century", "44 BC", "2000 years
before present", "Easter", "the second Tuesday of March"), built on the range
and resolution primitives already in the library.

This document is scope, not implementation. It defines the target surface, the
gap, the salvageable prior art, a phased plan, and the open decisions.

## Why

`extract_datetime_xx` today resolves points and simple offsets ("tomorrow at
five", "in 3 weeks"). It cannot resolve a period named by an era or a calendar
scope, and the primitives that would let it — `ranges.py` and its
`DateTimeResolution` — are present but unused by any scanner. A voice assistant
asked "what happened in the third century BC" or "how long ago is 10000 BP" has
no path to an answer.

## What is already landed

`ovos_date_parser/ranges.py` (from the duration/ranges salvage) exports, and
`__init__.py` re-exports, a complete calendar-scope toolbox that no extractor
yet consumes:

- `DateTimeResolution` — `DAY … MILLENNIUM`, each also `_OF_{scope}` (day of
  century, week of millennium, …), plus `BEFORE_PRESENT_{unit}` counting back
  from the radiocarbon epoch `BEFORE_PRESENT_EPOCH = 1950-01-01`.
- `get_date_ordinal(ordinal, ref_date, resolution)` — resolves "the Nth {unit}
  of {scope}" to a `date`. This is the engine for calendar-scoped ordinals.
- `get_{week,weekend,month,year,decade,century,millennium,season}_range`,
  `get_week_number`.
- `Season`, `Hemisphere`, `date_to_season`, `season_to_date`,
  `next_season_date`, `last_season_date` (meteorological, hemisphere-aware).

`ovos_date_parser/duration.py` provides `DurationResolution`
(`RELATIVEDELTA*`, totals) — the duration half of the same refactor, already
consumed by the per-language `extract_duration_xx`.

**Conclusion:** the arithmetic layer exists and is tested. The missing piece is
the **natural-language parsing layer** that maps era / epoch / scope phrases
onto these primitives, plus the scanner split that makes room for it.

## The gap

1. **No `extract_date` / `extract_time` split.** Each `extract_datetime_xx` is
   one monolithic token loop (`dates_en.py` is ~1150 lines). Era and
   calendar-scope parsing does not belong bolted onto that; it belongs in a
   dedicated date scanner that can return a `(date, resolution)` pair.
2. **No era / epoch vocabulary or parsing.** Nothing recognises "BC/AD",
   "BCE/CE", "before present", "anno domini", or resolves them against a
   reference epoch. `nice_year_xx(bc=…)` only *formats* a BC year; the inverse
   parse does not exist.
3. **No named-date (holiday) parsing.** "Easter", "Christmas" → a date in a
   given year is absent.
4. **The primitives are orphaned.** `get_date_ordinal` / the ranges / seasons
   are wired to nothing in extraction.

## Salvageable prior art — upstream PR #96

MycroftAI/lingua-franca PR **#96** (`refactor/date_extract`, +5751, CLOSED) is
reachable at commit `b013a832e74f1362a4ea83d059b2e3c02542224a`
(`git fetch https://github.com/MycroftAI/lingua-franca <sha>`). It prototypes
exactly this layer. The **design and data**, not the English token-loop bodies,
are the salvage:

- `_NAMED_ERAS_EN` — an era-name → reference-`date` table: `common era` /
  `anno domini` / `christian era` (year 1), `unix time` (1970-01-01),
  `lilian date` (1582-10-15), `rata die`, and a long tail of calendar eras
  (Armenian, Bahá'í, Yazdegerd, French Republican, Human/Holocene, …). Negative
  eras (`before present` = 1950) are a separate table.
- `get_named_eras_en(location_code)`, `get_negative_named_eras_en()`,
  `get_named_dates_en(location_code, year)` (holidays) — location-scoped
  accessors.
- `extract_date_en(date_str, ref_date, resolution, hemisphere, location_code,
  greedy)` — the split-out date scanner: qualifier tables (`ago`, `from/after/
  since`, `before`, `of`, `is/was`, `plus/minus`), multi-word era names
  normalised to a single token before scanning, then resolved via the ranges
  primitives.
- `parse_common.py` documents the numbering schemes to support: Julian day
  (4713 BC epoch), Before Present (1950), Alexandrian (5493 BC), Byzantine
  (5509 BC), Human/Holocene Era, and AD/BC ↔ CE/BCE.

Our `ranges.py` already absorbed the resolution/season/ordinal half of #96; the
era/named-date/`extract_date` half is what remains to port — adapted to the
current data-driven, per-language layout, not copied wholesale.

## Target architecture

```
extract_datetime_xx(text, ref)            # kept; thin wrapper over the two below
  ├── extract_date_xx(text, ref, resolution, hemisphere, location_code)
  │       → (date, DateTimeResolution)     # consumes ranges.py + eras
  └── extract_time_xx(text, ref)
          → time
```

- **`eras.py`** (new, language-agnostic core + per-language name tables):
  the era → reference-`date` model, positive and negative, plus
  `resolve_era(name, value, ref)` mapping "44 <era>" or "<era>" to a
  `(date, resolution)` using `BEFORE_PRESENT_EPOCH` and friends. Era *names*
  are locale data (like months); the arithmetic is shared.
- **`extract_date_xx`**: a scanner that recognises, in one pass — explicit
  dates, relative offsets (existing behaviour), calendar-scoped ordinals
  ("third century", "second week of the month" → `get_date_ordinal`), seasons,
  named dates/holidays, and era-qualified values ("44 BC", "2000 BP"). Dates
  built numerically; never via English `strptime` (an anti-pattern several
  current scanners still use).
- **`extract_time_xx`**: the clock-time remainder, reusing the number parser
  and the existing `HourFractionSystem` idea from the wider parser refactor.
- **Era output** already has a home: `nice_year_xx(bc=…)`; extend the
  `date_time.json` schema for era suffixes rather than hand-coding.

## Phasing

Each phase is independently shippable and reference-tested. English leads;
other languages follow the same data-driven shape once the English scanner is
proven.

1. **`eras.py` foundation** — era data model + accessors + `resolve_era`, unit
   tested against the reference epochs. No scanner changes. (Smallest first
   brick; low risk, immediately testable.)
2. **`extract_date_en` split** — carve the date logic out of
   `extract_datetime_en` into `extract_date_en` returning `(date, resolution)`;
   `extract_datetime_en` becomes `extract_date_en` + `extract_time_en`.
   Gate: byte-identical `extract_datetime_en` output on the existing test
   corpus (a frozen oracle, as used for the French pronunciation migration).
3. **Calendar-scoped ordinals & seasons** — wire `get_date_ordinal` and the
   season helpers into `extract_date_en` ("the third century", "next summer").
4. **Named eras & epochs** — "44 BC", "2000 before present", "anno domini",
   BCE/CE, resolved via `eras.py`. Decide the BC representation (see below).
5. **Named dates / holidays** — `get_named_dates_en`, location-scoped.
6. **Per-language rollout** — port the scanner shape + name tables to the next
   languages, each gated byte-identical on its existing corpus before new
   behaviour is enabled.

## Testing & references

- **No-regression gate at every phase**: freeze current `extract_datetime_xx`
  output over the test corpus into an oracle; the split must reproduce it
  byte-identical before new capability is switched on (same method that proved
  the French pronunciation migration zero-regression).
- **Round-trip** where a formatter exists: `nice_year(extract(...))`.
- **Differential**: `dateparser` and `dateutil` for the non-era date cases;
  era/epoch expectations are anchored to the numbering-scheme definitions
  (Julian day, BP, Holocene …) and cited, never to a single library.
- **Adversarial**: ambiguous era words, out-of-range years, mixed
  era+relative ("300 years after anno domini").

## Open decisions (need a call before phase 4)

1. **BC / years < 1 and > 9999.** `datetime.date` cannot represent them.
   Options: return a sentinel `(year:int, resolution)` pair for out-of-range
   years; carry a proleptic offset; or restrict to representable ranges and
   surface the rest as "unsupported". #96 left this a TODO. **This is the main
   blocker for full era support and should be decided first.**
2. **Calendar plurality.** The era table mixes Gregorian-anchored reference
   dates for non-Gregorian calendars (Armenian, Bahá'í, …). Ship
   Gregorian-anchored only, or model calendar conversion? Recommend
   Gregorian-anchored reference points now, conversion out of scope.
3. **Location scope.** `location_code` gates holidays and some eras. Where does
   it come from — Session config, an argument, or dropped for v1? Recommend an
   optional argument defaulting to none (global eras only) for v1.
4. **Ambiguity policy.** "may" (month vs modal), "BC" inside other tokens,
   era words that are also common words — reuse the number parser's
   permissive-parse-then-validate stance.

## Non-goals

- No new calendar systems or calendar conversion (reference points only).
- No astronomical/geological period names ("Jurassic") — a data problem for a
  later, separate table if wanted.
- No change to the duration half (`duration.py`) — already landed.
- No bus messages or Session coupling; pure parsing.
