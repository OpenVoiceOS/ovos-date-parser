# Language notes

Per-language behaviour that goes beyond the support matrix in the README.

## Relative expressions

Every `extract_datetime` implementation resolves relative phrases against
`anchorDate`: "tomorrow morning", "next tuesday", "in 2 hours", "day before
yesterday" and their equivalents. Purely relative offsets ("in 2 hours")
keep the anchor's time of day; day-level expressions ("tomorrow") resolve to
midnight unless a time is present or `default_time` is passed.

## Time formats understood

Digit forms (`15:30`, `3:30 pm`) parse in every language alongside the
spoken forms. Portuguese additionally understands the `15h30` / `14h30min`
style. Explicit years parse in the languages with full date support
("11 de agosto de 1998").

## nice_time conventions

- Languages with a 12-hour speech habit (en, pt, es, ...) speak
  "half past one" style with an optional am/pm marker
  (`use_ampm=True` → "in the morning" equivalents).
- `use_24hour=True` produces military-style readings ("thirteen thirty").
- French reads 12-hour by default ("une heure vingt-deux",
  "huit heures moins vingt").
- Basque, Catalan and Persian have their own idiomatic readings
  (Catalan supports `TimeVariantCA` for bell-tower style).

## Asturian (ast)

Full support: `nice_time`, `nice_date`, `nice_date_time`, `nice_day`,
`nice_weekday`, `nice_month`, `nice_year`, `extract_datetime` and
`extract_duration`. Spoken time follows the feminine-article convention
("la una", "les cinco y media", "les ocho menos cuartu", "en puntu") with
`use_ampm=True` adding "de la madrugada / mañana / tarde / nueche".
Duration parsing handles the Asturian plurals in `-es` (hores, selmanes,
díes) as well as the singular forms. "mañana" is ambiguous between
"tomorrow" and "morning" and is disambiguated the same way as in Spanish.

## Fallbacks

If a language has no `extract_datetime` implementation, the
[dateparser](https://dateparser.readthedocs.io) library is tried. It handles
absolute dates well but not conversational relative phrases.

`nice_duration` uses a generic per-language unit table
(`nice_duration_generic`) for languages without a dedicated implementation;
plural declension may be imperfect (e.g. Slovenian dual forms).

## Known gaps

- Relative *past* wording ("anoche", "bart", "last night") is not handled in
  es/eu; the corresponding tests are skipped.
- `extract_duration` is missing for eu, fr, hu, it.
- `nice_time` is missing for sl.
- Duration parsing understands "2 weeks", "3 months", "4 years" in most
  languages, but common.py's generic helper only covers seconds through
  days.
