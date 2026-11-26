# ovos-date-parser

<!-- agent-hint
covers: what the package does, how to install it, a first example, and where the docs are
source: ovos_date_parser/__init__.py (extract_datetime, extract_duration, nice_time, nice_duration, CHRONOLOGIA_LOCALES); pyproject.toml
generated: no
verify: diff <(sed -n '/^\x60\x60\x60python/,/^\x60\x60\x60$/p' README.md | sed '1d;$d' | .venv/bin/python -I -) <(sed -n '/^\x60\x60\x60python/,/^\x60\x60\x60$/s/^print(.*)  *# //p' README.md)
see: docs/index.md, docs/getting-started.md, docs/how-it-works.md, docs/api.md, docs/writers.md, docs/languages.md, docs/helpers.md
-->

This library turns date, time and duration phrases into `datetime` and
`timedelta` values, and turns those values back into words. It reads 61
languages through [chronologia](https://github.com/TigreGotico/chronologia)
and writes 40 languages with its own `nice_*` formatters.

The library is a plain Python package. It needs no voice assistant at runtime.
[OpenVoiceOS](https://openvoiceos.org) uses it, and so can an NER pipeline, a
TTS front end, an ASR post-processor or a scheduler.

## Install

```bash
uv pip install --prerelease=allow ovos-date-parser
```

## Getting started

Reading a phrase gives a `datetime` and the words left over. Writing a value
gives words that a speech engine can say.

```python
from datetime import datetime
from ovos_date_parser import extract_datetime, extract_duration, nice_time, nice_duration

# text to datetime, plus the leftover words
when, leftover = extract_datetime("lets meet next friday at 8am", "en",
                                  anchorDate=datetime(2024, 1, 5))
print(when)      # 2024-01-12 08:00:00
print(leftover)  # lets meet

# text to timedelta
delta, leftover = extract_duration("set a timer for 5 minutes", "en")
print(delta)     # 0:05:00

# datetime to speakable words
print(nice_time(datetime(2024, 1, 5, 15, 30), "en"))   # half past three
print(nice_duration(3690, "en"))                       # one hour one minute thirty seconds
```

`anchorDate` is the reference time that relative phrases resolve against. Pass a fixed
value for repeatable results.

## Who does what

Reading is the job of chronologia. The function `extract_datetime` normalizes the language tag and calls chronologia for every locale it reads. The function `extract_duration` calls chronologia for the same locales. [docs/languages.md](docs/languages.md) lists each locale.

This package adds the `datetime` shape of the answer, the leftover text, named holidays, the `resolution` and `replace_token` options of `extract_duration`, and the span scans `extract_datetime_spans` and `extract_duration_spans`. The names `extract_datetime_<code>` and `extract_duration_<code>` are deprecated shims over the two reading functions. The modules `astrodate`, `calendars`, `cycles`, `eras`, `regnal` and `roman` re-export chronologia names.

Writing is the job of this package. The `nice_*` functions and the `spoken_*`
functions say a time, a date, a year or a duration in the words of a language.
The package writes 40 languages, Bosnian among them, and the top-level
functions are the stable API. [How it works](docs/how-it-works.md) shows the
path of a call, and [Language writers](docs/writers.md) names the writer of each
language.

A language that chronologia does not read, such as Japanese or Chinese, goes to
[dateparser](https://dateparser.readthedocs.io). That fallback reads absolute
dates well and conversational phrases poorly.

## Languages

`extract_datetime` reads the 61 locales in `CHRONOLOGIA_LOCALES`. The `nice_*` formatters write 40 languages, and chronologia reads every one of them except Bosnian, which reads as Croatian. [docs/languages.md](docs/languages.md) lists both sets. A tag in any case, with `_` or `-`, reaches the same reader: `"EN-US"`, `"pt_br"` and `"deu"` all work for reading.

## Documentation

[docs/index.md](docs/index.md) lists every page. The main ones:

- [Getting started](docs/getting-started.md): install to a first result in five steps
- [Adding a language](docs/adding-a-language.md): the path for reading and the path for writing
- [How it works](docs/how-it-works.md): which calls pass to chronologia and which code writes each language
- [API reference](docs/api.md): every public function, with real output
- [Language writers](docs/writers.md): the functions and data of each of the 40 writers
- [Languages](docs/languages.md): which languages read, which write, and how
- [Calendar helpers](docs/helpers.md): ranges, seasons and era scanners

Runnable scripts are in [`examples/`](examples/). Run one with
`python examples/ner_temporal.py`.

## Related projects

- [chronologia](https://github.com/TigreGotico/chronologia): reads dates, times and durations
- [ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser): numbers

## License

Apache 2.0.
