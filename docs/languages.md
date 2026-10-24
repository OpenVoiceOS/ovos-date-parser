# Language notes

Per-language behavior that goes beyond the support matrix in the README.

## Relative expressions

Every `extract_datetime` implementation resolves relative phrases against
`anchorDate`: "tomorrow morning", "next tuesday", "in 2 hours", "day before
yesterday", and their equivalents. Purely relative offsets ("in 2 hours")
keep the anchor's time of day. Day-level expressions ("tomorrow") resolve to
midnight unless a time is present or `default_time` is passed.

## Time formats understood

Digit forms (`15:30`, `3:30 pm`) parse in every language alongside the
spoken forms. Portuguese also understands the `15h30` / `14h30min`
style. Explicit years parse in the languages with full date support
("11 de agosto de 1998").

## nice_time conventions

- Languages with a 12-hour speech habit (en, pt, es, and others) speak
  "half past one" style with an optional am/pm marker
  (`use_ampm=True` produces "in the morning" equivalents).
- `use_24hour=True` produces military-style readings ("thirteen thirty").
- French reads 12-hour by default ("une heure vingt-deux",
  "huit heures moins vingt").
- Basque, Catalan, and Persian have their own idiomatic readings. Catalan
  supports `TimeVariantCA` for bell-tower style.
- Occitan (classical orthography, Lengadocian variety) reads 12-hour with
  the traditional quarter idioms: "una ora e quart", "cinc oras e mièja",
  and the quarter-to form naming the next hour ("doas oras manca un quart"
  for 1:45). Noon and midnight are "miègjorn" and "mièjanuèch".

## Asturian (ast)

Full support: `nice_time`, `nice_date`, `nice_date_time`, `nice_day`,
`nice_weekday`, `nice_month`, `nice_year`, `extract_datetime`, and
`extract_duration`. Spoken time follows the feminine-article convention
("la una", "les cinco y media", "les ocho menos cuartu", "en puntu") with
`use_ampm=True` adding "de la madrugada / mañana / tarde / nueche".
Duration parsing handles the Asturian plurals in `-es` (hores, selmanes,
díes) as well as the singular forms. "mañana" is ambiguous between
"tomorrow" and "morning" and resolves the same way as in Spanish.

## Kabyle

Weekdays are the everyday Arabic-derived names (`letnayen` through
`lḥedd`). Months follow the Kabyle calendar spellings (`yennayer`, `fuṛar`,
through `dujembeṛ`). `extract_datetime` covers the relative day words
(`azekka` "tomorrow", `iḍelli` "yesterday", `ass-a` "today"), weekday and
month names with day numbers, digit clock times, and spoken clock phrases
(see below). It does not yet cover year words. `extract_duration`
accepts both the Amazigh neologisms (`tasint` second, `amalas` week) and
the Arabic-derived units in daily use (`ddqiqa` minute, `ssaɛa` hour),
with an optional genitive `n` between quantity and unit (`10 n
tesdidin`). `nice_time` joins hour and minutes with the conjunction `d`.
Day parts use `ssbeḥ` (morning) and `tameddit` (evening). Years are
given in digits. A verified spoken-year formulation is not available.

### Spoken clock phrases

`extract_datetime` understands the native "presentative" clock grammar
built around `d` ("it is"), not just digit times.

- Bare hours: `d lweḥda` (1:00), `d lɛecṛa` (10:00).
- Exact: `swaswa` marks the hour precisely (`d lɛecṛa swaswa`).
- Quarter/half: `u ṛbeɛ` (+15), `u neṣṣ`/`azgen`/`nofc`/`nofç`/`nefs`
  (+30). All four spellings of "half" are accepted, spanning the
  Amazigh word, the old Arabic borrowing, and two contemporary variants.
- Minus: `ɣiṛ` plus a number subtracts from the next hour (`d lɛecṛa ɣiṛ
  xemsa` = 9:55). `ɣiṛ ṛbeɛ` is quarter-to. Bare `ɣiṛ` with no number is
  a vague "almost the hour" and resolves to a fixed 10-minute-to offset,
  matching the source grammar's own description of it as indeterminate
  rather than a specific count.
- Vague plus: `u wac` / `u ci` ("and a bit") resolve the same way, as a
  fixed 10 minutes past.
- Day-period disambiguation: a trailing `n <period>` both attaches a
  period and resolves 12h/24h ambiguity. `d juǧ` alone stays 2:00, but
  `d juǧ n uzal` resolves to 14:00. Periods recognized: `ṣṣbeḥ` (early
  morning, 4-8h), `ssbeḥ` (morning, 8-12h), `uzal` (midday, 12-15h),
  `tameddit`/`tmeddit` (afternoon/evening, 15-20h), `iḍ`/`yiḍ` (night,
  20-4h).
- Regional variant: `ssaɛtin` is accepted as an alternative to `juǧ` for
  "two o'clock" (Soummam valley usage), for example `d ssaɛtin ɣiṛ xemsa`
  (1:55).
- Midnight set phrases: `nṣaf n yiḍ` and `ttnaṣfa n yiḍ` both resolve
  directly to 00:00.

Clock-hour nouns carry a fused definite article that the parser strips
before handing the word to the number extractor. This surfaces two
ways, mirroring Arabic sun/moon letters: a plain `l-` before some
consonants (`lɛecṛa`, `lxemsa`) and gemination of the noun's own first
consonant before others (`ttnac` = article + `tnac` "12", `ttlata` =
article + `tlata` "3"). "One o'clock" also uses the feminine
loan-numeral `weḥda`, agreeing with the feminine noun `ssaɛa` (hour),
rather than the masculine `waḥed` used elsewhere.

Not yet handled: the preposition `af` ("at") as an alternative to `d`
(`Af ttlata n ṣṣbeḥ`, "at three in the early morning"). Only one
example of this construction is attested, and it is unclear whether it
behaves identically to `d` in every pattern above. `nice_time` also
does not yet generate these forms (fractions, day-periods beyond
`ssbeḥ`/`tameddit`, the vague markers). Extraction is currently richer
than generation for this language.

## Norwegian Bokmål (nb)

Bokmål is supported with `no` accepted as an alias. It covers `nice_time`,
`nice_date`, `nice_date_time`, `nice_day`, `nice_weekday`, `nice_month`,
`nice_year`, `nice_duration`, `nice_relative_time`, `extract_datetime`, and
`extract_duration`. Number and ordinal words use the modern tens-first
counting reform (`tjueen` = 21) with decimal tens (`femti`, `åtti`), so
years read "nitten hundre og åttifire" and "to tusen og tjueen". Weekdays
are `mandag` through `søndag`. One o'clock reads with the neuter `ett`
(`klokka ett`). `extract_datetime` covers relative day words, weekdays
with `neste`/`forrige`, month names with day and optional year, and digit
clock times.

## Fallbacks

If a language has no `extract_datetime` implementation, the
[dateparser](https://dateparser.readthedocs.io) library is tried. It handles
absolute dates well but not conversational relative phrases.

`nice_duration` uses a generic per-language unit table
(`nice_duration_generic`) for languages without a dedicated implementation.
Plural declension may be imperfect (for example, Slovenian dual forms).

## Romanian

- `nice_time` speaks quarter-hours idiomatically: "opt și un sfert" (8:15),
  "opt și jumătate" (8:30, half past), "nouă fără un sfert" (8:45, "fără"
  means minus, quarter to nine). Exact hours take "fix". `use_ampm=True`
  appends "dimineața" / "după-amiaza" / "seara" / "noaptea".
- "luni" is both Monday and the plural of "lună" (month). A numeric context
  ("3 luni") selects the month unit, otherwise it is the weekday.
- "mai" is both May and a very common adverb. It only parses as a month next
  to a day or year number ("3 mai", "mai 2019").
- Spoken numbers are understood in dates, times, and durations
  ("peste trei zile", "douăzeci de minute").

## Danish (da)

- `nice_year` supports an explicit AD/CE marker via `nice_year(dt, "da",
  ad=True)`, appending "e.Kr." the same way `bc=True` appends "f.Kr.". The two
  are mutually exclusive. If both are passed, `bc` wins. Years are implicitly
  AD when neither flag is set, as before.
- The `ad` parameter is part of the generic `year_format` engine and is a
  no-op for any locale that does not define an `"ad"` key in its
  `year_format` resource, so it does not affect other languages.

## Known gaps

- Relative past wording ("anoche", "bart", "last night") is not handled in
  es/eu. The corresponding tests are skipped.
- `nice_time` is missing for sl.
- `gl` and `hu` `extract_datetime` are partial (see the README matrix).
- The `resolution` / `replace_token` options of `extract_duration` are only
  available on the shared duration engine. ar, ast, fa, kab, and sv use a
  dedicated parser that returns a plain `timedelta` and rejects those options.

---
[← API reference](api.md) · [Home](../README.md) · [Adding a language →](adding-a-language.md)
