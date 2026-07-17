# ovos-date-parser

Multilingual parsing, extraction and formatting of human date, time and duration
expressions — a two-way bridge between machine timestamps and the way people
actually speak and write about time.

- **Text → datetime**: pull a `datetime` out of "next friday at 3pm" or
  "amanhã às 15h30", and keep the leftover words.
- **Text → duration**: turn "two hours and thirty minutes" into a `timedelta`.
- **datetime → speech**: render `2024-01-05 15:30` as "January fifth twenty
  twenty four at half past three".
- **Dozens of languages**, resolved by BCP-47 code, with an automatic
  [dateparser](https://dateparser.readthedocs.io) fallback for the rest.

It powers date/time understanding in [OpenVoiceOS](https://openvoiceos.org), but
it is a **plain Python library with no voice-assistant dependency at runtime** —
equally useful in an NER pipeline, a TTS front-end, an ASR post-processor, or a
scheduling/calendar/logging tool.

## Installation

```bash
pip install ovos-date-parser
# or
uv pip install ovos-date-parser
```

## 30-second quickstart

```python
from datetime import datetime
from ovos_date_parser import extract_datetime, extract_duration, nice_time, nice_duration

# 1. text -> datetime (+ the words left over)
when, leftover = extract_datetime("lets meet next friday at 8am", "en",
                                  anchorDate=datetime(2024, 1, 5))
print(when)      # 2024-01-12 08:00:00
print(leftover)  # 'lets meet'

# 2. text -> timedelta
delta, leftover = extract_duration("set a timer for 5 minutes", "en")
print(delta)     # 0:05:00

# 3. datetime -> speakable words
print(nice_time(datetime(2024, 1, 5, 15, 30), "en"))   # 'half past three'
print(nice_duration(3690, "en"))                       # 'one hour one minute thirty seconds'
```

Every snippet above and in [`examples/`](examples/) runs with nothing installed
but this package.

## Use it outside OVOS

The same handful of functions solve everyday text/speech problems that have
nothing to do with voice assistants.

### Temporal entity extraction (NER)

Tag dates, times and durations in free text and keep the non-temporal
remainder — useful for log mining, ticket triage or note-taking apps.

```python
from datetime import datetime
from ovos_date_parser import extract_datetime

text = "call the supplier next monday at 2pm about the delayed order"
when, rest = extract_datetime(text, "en", anchorDate=datetime(2024, 1, 5))
# when -> 2024-01-08 14:00 ; rest -> 'call supplier delayed order'
```

`anchorDate` is the "now" that relative phrases resolve against — pass a fixed
value for reproducible extraction, or `datetime.now()` live. See
[`examples/ner_temporal.py`](examples/ner_temporal.py).

### TTS normalization

Speech engines mangle raw digits. Normalize a timestamp to words *before*
synthesis:

```python
from datetime import datetime
from ovos_date_parser import nice_date, nice_time

dt = datetime(2024, 1, 5, 15, 30)
spoken = f"{nice_date(dt, 'en')} at {nice_time(dt, 'en')}"
# 'friday, january fifth, twenty twenty four at half past three'
```

See [`examples/tts_normalization.py`](examples/tts_normalization.py).

### ASR post-processing

Speech-to-text emits words; downstream logic needs structure. Convert a
transcript into a real datetime and an action payload:

```python
from datetime import datetime
from ovos_date_parser import extract_datetime

utterance = "remind me next tuesday at nine thirty to water the plants"
when, action = extract_datetime(utterance, "en", anchorDate=datetime(2024, 1, 5))
# when -> 2024-01-09 09:30 ; action -> 'remind me to water plants'
```

See [`examples/asr_postproc.py`](examples/asr_postproc.py).

### In an OVOS skill vs. standalone

The library behaves identically in both settings; only who calls it changes.

```python
# In an OVOS skill: language and anchor come from the session
when, _ = extract_datetime(utterance, self.lang)

# Standalone scheduler / calendar / cron generator: you supply them
when, _ = extract_datetime(user_text, "en", anchorDate=datetime.now())
```

## Core API

| Function | Direction | Purpose |
|----------|-----------|---------|
| `extract_datetime(text, lang, anchorDate=None, default_time=None)` | text → datetime | Date/time from a phrase + leftover text |
| `extract_duration(text, lang, *, resolution=..., replace_token="")` | text → duration | `timedelta`/`relativedelta`/float + leftover text |
| `nice_time(dt, lang, speech=True, use_24hour=False, use_ampm=False, variant=None)` | datetime → text | Speakable or digit clock time |
| `nice_date(dt, lang, now=None, include_weekday=True)` | datetime → text | Speakable date, shortened against `now` |
| `nice_date_time(dt, lang, now=None, use_24hour=False, use_ampm=False)` | datetime → text | Date and time combined |
| `nice_day` / `nice_weekday` / `nice_month` / `nice_year` | datetime → text | Individual date components |
| `nice_duration(duration, lang, speech=True)` | seconds/timedelta → text | Speakable timespan |
| `nice_relative_time(when, relative_to=None, lang="en-us")` | datetime → text | Short "N minutes/days" phrase |
| `get_date_strings(dt, lang, date_format=None, time_format="full")` | datetime → dict | Display strings for GUI clients |

Full signatures, return shapes and examples: [docs/api.md](docs/api.md).

Dialects resolve by prefix — `"pt-BR"`, `"pt-PT"` and `"pt"` all reach the
Portuguese implementation. Unsupported languages raise `NotImplementedError`,
except `extract_datetime`, which first tries the `dateparser` fallback.

## Language support

Twenty-plus languages have dedicated, idiomatic implementations. Extraction for
any other language falls back to `dateparser`; formatting falls back to a
generic word-table.

- ✅ dedicated implementation
- 🚧 partial / generic (language-agnostic helper or external library)
- ❌ not available (raises `NotImplementedError`)

**Parsing**

| Language | `extract_datetime` | `extract_duration` |
|----------|:---:|:---:|
| ar Arabic       | ✅ | ✅ |
| ast Asturian    | ✅ | ✅ |
| az Azerbaijani  | ✅ | ✅ |
| ca Catalan      | ✅ | ✅ |
| cs Czech        | ✅ | ✅ |
| da Danish       | ✅ | ✅ |
| de German       | ✅ | ✅ |
| en English      | ✅ | ✅ |
| es Spanish      | ✅ | ✅ |
| eu Basque       | ✅ | ✅ |
| fa Persian      | ✅ | ✅ |
| fr French       | ✅ | ✅ |
| gl Galician     | 🚧 | ✅ |
| hu Hungarian    | 🚧 | ✅ |
| it Italian      | ✅ | ✅ |
| kab Kabyle      | ✅ | ✅ |
| nl Dutch        | ✅ | ✅ |
| oc Occitan      | ✅ | ✅ |
| pl Polish       | ✅ | ✅ |
| pt Portuguese   | ✅ | ✅ |
| ro Romanian     | ✅ | ✅ |
| ru Russian      | ✅ | ✅ |
| sl Slovenian    | ✅ | ✅ |
| sv Swedish      | ✅ | ✅ |
| uk Ukrainian    | ✅ | ✅ |

> Any language not listed uses the `dateparser` fallback for `extract_datetime`
> (good at absolute dates, weak at conversational relative phrases). The
> languages on the shared duration engine (all of the above except ar, ast, fa,
> kab, sv) also support the `resolution` and `replace_token` options of
> `extract_duration` — see [docs/api.md](docs/api.md).

**Formatting**

| Language | `nice_date` family | `nice_time` | `nice_duration` | `nice_relative_time` |
|----------|:---:|:---:|:---:|:---:|
| ar Arabic       | 🚧 | ✅ | ✅ | 🚧 |
| ast Asturian    | ✅ | ✅ | ✅ | 🚧 |
| az Azerbaijani  | ✅ | ✅ | ✅ | 🚧 |
| ca Catalan      | ✅ | ✅ | ✅ | 🚧 |
| cs Czech        | ✅ | ✅ | ✅ | 🚧 |
| da Danish       | ✅ | ✅ | ✅ | 🚧 |
| de German       | ✅ | ✅ | ✅ | 🚧 |
| en English      | ✅ | ✅ | ✅ | 🚧 |
| es Spanish      | ✅ | ✅ | ✅ | 🚧 |
| eu Basque       | ✅ | ✅ | ✅ | ✅ |
| fa Persian      | ✅ | ✅ | ✅ | 🚧 |
| fr French       | ✅ | ✅ | ✅ | 🚧 |
| gl Galician     | ✅ | ✅ | ✅ | 🚧 |
| hu Hungarian    | ✅ | ✅ | ✅ | 🚧 |
| it Italian      | ✅ | ✅ | ✅ | 🚧 |
| kab Kabyle      | 🚧 | ✅ | ✅ | 🚧 |
| nl Dutch        | ✅ | ✅ | ✅ | 🚧 |
| oc Occitan      | ✅ | ✅ | ✅ | 🚧 |
| pl Polish       | ✅ | ✅ | ✅ | 🚧 |
| pt Portuguese   | ✅ | ✅ | ✅ | 🚧 |
| ro Romanian     | ✅ | ✅ | ✅ | 🚧 |
| ru Russian      | ✅ | ✅ | ✅ | 🚧 |
| sl Slovenian    | ✅ | ❌ | ✅ | 🚧 |
| sv Swedish      | ✅ | ✅ | ✅ | 🚧 |
| uk Ukrainian    | ✅ | ✅ | ✅ | 🚧 |

> `nice_relative_time` uses a shared implementation for every language except
> Basque, which has a dedicated one; the shared version is functional but not
> idiomatically tuned per language.

Per-language quirks (Catalan bell-tower time, Occitan quarter idioms, Romanian
"fără un sfert", Kabyle calendar names, Portuguese `15h30` style, ...) are
documented in [docs/languages.md](docs/languages.md).

## Examples

Runnable, dependency-free scripts in [`examples/`](examples/):

| Script | Shows |
|--------|-------|
| [`ner_temporal.py`](examples/ner_temporal.py) | Extract date/time/duration entities from free text |
| [`tts_normalization.py`](examples/tts_normalization.py) | Render timestamps to speakable words before synthesis |
| [`asr_postproc.py`](examples/asr_postproc.py) | Turn spoken transcripts into structured datetimes |
| [`multilingual.py`](examples/multilingual.py) | Parse-then-render round trip across many languages |
| [`extract.py`](examples/extract.py) | Minimal extraction reference |
| [`format.py`](examples/format.py) | Minimal formatting reference |

```bash
python examples/ner_temporal.py
```

## Documentation

- [API reference](docs/api.md) — every public function and its parameters
- [Language notes](docs/languages.md) — per-language behaviour and known gaps
- [Adding a language](docs/adding-a-language.md) — implementation guide

## Related projects

- [ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser) — numbers
- [ovos-lang-parser](https://github.com/OVOSHatchery/ovos-lang-parser) — languages
- [ovos-color-parser](https://github.com/OVOSHatchery/ovos-color-parser) — colors

## License

Apache 2.0.
