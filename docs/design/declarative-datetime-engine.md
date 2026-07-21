# Declarative datetime engine: one scanner, data-only languages

## Problem

Every supported language carries its own hand-written `extract_datetime_xx`
token loop (200–1000 lines). The loops re-implement the same semantics —
relative offsets, weekday resolution, calendar dates, clock times — with
independently-written control flow, so every defect is repeated per
language and every feature must be ported per language. Recent audits
measured the cost directly:

- the past-marker ("N units ago") direction bug existed independently in
  20 scanners;
- month + bare year is dropped or ignored in most languages while working
  in a handful;
- plural/inflected unit nouns fail in languages whose loop only lists
  singular forms;
- five scanners returned a different result type than the rest;
- two languages ship formatters but no extractor at all, and one
  number-parser language has no date support of any kind.

Per-language code makes parity structurally impossible to maintain: the
defect surface is `languages × features`.

## Goal

A single language-agnostic engine that consumes **per-language data**:

- `locale/<lang>/*.voc` — every translatable surface form, loaded with
  ovos-spec-tools (the convention already used by the era and scoped
  layers in this codebase, which are the proof of concept for this
  design).
- `locale/<lang>/lang.json` — non-translatable structural facts:
  ordering, conventions, normalisation tables, feature switches.

Adding a language becomes authoring data, reviewable by a speaker
without reading Python. Fixing an engine bug fixes every language at
once. The defect surface becomes `features + languages`.

## Non-goals

- No change to any public API signature or return contract.
- No new natural-language capabilities in the migration itself: the
  engine must first reproduce current behaviour per language (bug fixes
  land separately, before or after, never silently inside a migration).
- No general-purpose morphology: only the closed class of temporal
  vocabulary is normalised.
- No behaviour encoded in JSON (see Schema philosophy).

## Architecture

```
text
 └─ tokenizer (per-language mode flags)
     └─ normaliser pipeline
         ├─ number normaliser        (binding to ovos-number-parser)
         └─ temporal-lemma normaliser (data: inflection tables)
             └─ pattern engine
                 ├─ construction table (data: slot orders + markers)
                 ├─ resolver           (engine: pure date math)
                 └─ escape hatch       (optional per-language hook)
                     └─ (datetime | date | AstroDate, remainder)
```

### Constructions, not regexes

The engine's core is a table of **semantic constructions**, each a typed
slot sequence resolved by shared date math:

| construction | slots | example instantiations |
|---|---|---|
| `relative_offset` | NUM UNIT ± DIRECTION_MARKER | "in 3 days", "hace 2 semanas", "2 settimane fa", "för 2 veckor sedan" |
| `named_day` | DAY_WORD | "tomorrow", "avant-hier", "etzi" |
| `weekday_ref` | REL_MARKER WEEKDAY | "next friday", "datorren ostiralean" |
| `calendar_date` | MONTH DAY? YEAR? in language order | "june 5 2027", "5 de junho", "2027ko ekainean" |
| `iso_date` | validated pre-pass | "2017-06-30" |
| `clock_time` | fraction system per language | "half past ten", "kwart voor vijf" |
| `era_date` | NUM ERA_MARKER | "44 BC", "500 antes de nuestra era" |
| `scoped_ordinal` | ORD UNIT of SCOPE | "the 3rd week of june" |
| `season_ref` | REL_MARKER? SEASON YEAR? | "summer of 1969" |

A language's data declares, per construction: whether it's enabled, the
slot order(s), and which `.voc` sets fill each slot. The engine compiles
this into matchers once at load time. Marker position (prefix, suffix,
circumfix) is data; the *sign of the offset* is engine logic keyed to the
marker's declared direction — the ago-direction bug class becomes
unwritable.

### Vocabulary layer (`*.voc`)

One file per slot vocabulary: months, weekdays, units per resolution,
named days (with their offsets as part of the entry), direction markers,
relative markers, seasons, clock words, era phrases. The existing
`(a|b)` / `[optional]` expansion from ovos-spec-tools applies. The era
and scoped layers already ship exactly this shape for six languages.

### Structure layer (`lang.json`)

States facts only:

```jsonc
{
  "tokenizer": {"split_contractions": true, "ordinal_dot": false},
  "numbers": "ovos_number_parser.numbers_xx:normalize",   // dotted binding
  "lemmas": {"tygodnie": "tydzień", "tygodni": "tydzień"}, // irregulars
  "suffix_strip": [["-aren", ""], ["-ean", ""]],           // rule-based
  "constructions": {
    "relative_offset": {"orders": ["MARKER NUM UNIT", "NUM UNIT MARKER"]},
    "calendar_date":   {"orders": ["DAY of MONTH of YEAR"], "prefer_future": true},
    "clock_time":      {"fractions": "half_past"}
  },
  "conventions": {"week_start": "monday", "dmy": true, "hemisphere": null},
  "guards": {"bare_holocene_min_digits": 5},
  "hook": null                                             // escape hatch
}
```

### Object model

The engine decomposes into small helper classes with one well-defined
subtask each; all value types are frozen dataclasses, so every stage
consumes and produces immutable, hashable, comparable values and the
pipeline stays trivially testable stage-by-stage.

```python
@dataclass(frozen=True)
class Token:
    text: str          # normalised form
    raw: str           # original surface form (for remainder rebuild)
    index: int
    is_number: bool
    value: Optional[float] = None

@dataclass(frozen=True)
class LangSpec:          # the parsed lang.json + loaded vocabularies
    lang: str
    vocab: Mapping[str, frozenset[str]]     # slot name -> surface forms
    lemmas: Mapping[str, str]
    orders: Mapping[str, tuple[SlotOrder, ...]]
    conventions: Conventions                # itself a frozen dataclass
    hook: Optional[Callable] = None

@dataclass(frozen=True)
class Match:             # one construction claiming a token span
    construction: str
    span: tuple[int, int]
    slots: Mapping[str, Token | tuple[Token, ...]]

@dataclass(frozen=True)
class Resolution:        # the semantic value, before formatting
    value: date | datetime | AstroDate
    resolution: DateTimeResolution
    consumed: tuple[int, ...]               # token indices for remainder
```

Helper classes, one per pipeline stage — each stateless or configured
once from a `LangSpec`, each independently unit-testable with a
synthetic locale:

- `Tokenizer` — text → `tuple[Token, ...]`, per-language mode flags.
- `TemporalNormaliser` — applies lemma map and suffix-strip rules;
  pure `Token → Token`.
- `ConstructionCompiler` — `LangSpec` → compiled matcher table; runs
  once per language, cached.
- `ConstructionMatcher` — tokens → `tuple[Match, ...]` with the
  precedence rules (era before scoped before calendar, longest span
  wins).
- `Resolver` — `Match` + anchor + `Conventions` → `Resolution`; all
  date math lives here and nowhere else, shared by every language.
- `ExplainTrace` — the `explain(text, lang)` debug API: replays the
  pipeline and reports which construction matched, slot bindings, and
  why competing matches lost.

Plain functions where a class would be ceremony (loading, remainder
reconstruction); comprehensions and early returns over guard scaffolding
— the helpers exist because each has a real contract, not for
decoration.

### Schema philosophy

The JSON states **facts** — orders, markers, maps, thresholds, switches.
All logic lives in the engine. The moment a conditional wants to live in
the data, that is a missing engine concept, not a reason to grow a DSL.
(This mirrors the orthography2ipa split of generic engine vs language
specs, which has held up across dozens of languages.)

### Escape hatch

A language may declare one `hook` — a dotted reference to a function that
receives the token stream before the construction pass and may claim one
construction the schema cannot express (Catalan bell-system clock times,
Turkish suffixed numbers). Budget: a hook materially smaller than a
scanner (~50 lines). A hook that grows toward a scanner is a schema gap
to be fixed in the engine, and blocks further migration until designed.

## Migration plan

Strangler pattern, per language, always shippable:

1. **Freeze an oracle** per language: dump current `extract_datetime`
   output over that language's full test corpus plus generated sentence
   sweeps (the method that gated the English date/time split at
   1112/1112).
2. **Author the data** for the language; register it with the engine.
3. **Gate**: engine output byte-identical to the oracle, full suite
   green, three-way differential (vs dateparser/dateutil) shows no new
   leads. Known-bug oracle entries are annotated, never silently
   "fixed" in migration.
4. **Cut over**: the dispatcher routes the language to the engine; the
   legacy scanner is deleted in the same change (no dual maintenance).
5. Languages not yet migrated keep their legacy scanner untouched.

Order: `en` + `pt` + `fi` first — one reference implementation, one
romance, one agglutinative — so the schema is forced honest before it
ossifies. Then waves by family. New languages (`mwl`, and `an`/`fy` if
their extractors have not landed by then) are authored engine-native and
never get a legacy scanner.

Every construction/vocab entry must trace to a downloaded canonical
grammar or dictionary source, cited from the data directory's test file
— unchanged from the per-language citation rule.

## Testing

- Per-language natural-sentence suites with exact asserted values remain
  the contract (the current bug-wave regression files become the seed
  corpora).
- Engine unit tests per construction, language-independent, using a
  synthetic test locale.
- A parity matrix test generated from the data: every enabled
  construction in every language must have at least N asserted natural
  sentences; a language cannot silently ship with a feature untested.
- Frozen oracles retained under `benchmarks/` for regression gating of
  future engine changes.

## Risks

| risk | mitigation |
|---|---|
| schema designed on romance languages, breaks on agglutinative | fi in the first migration wave |
| JSON grows a DSL | facts-only rule; hooks; schema review on every new key |
| engine regexes become undebuggable | constructions compiled from named slots; `explain(text, lang)` debug API emitting the matched construction and slot bindings |
| performance (compiled matchers per language) | compile once at first use per language, cache; benchmark against legacy scanner before first cutover |
| oracle enshrines bugs | oracles annotate known bugs from the parity audit; bug fixes land as separate changes with their own tests |
| long dual-world period | per-language cutover deletes the legacy scanner immediately; dispatcher is the single seam |

## Relationship to existing layers

`eras_scan.py` and `scoped_scan.py` are early instances of this design
and merge into the engine as the `era_date` and `scoped_ordinal`
constructions; their `locale/<lang>/*.voc` files carry over unchanged.
The `AstroDate` return rule and the `extract_date`/`extract_time` split
are orthogonal and unaffected.
