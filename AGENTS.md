# ovos-date-parser: agent guide

<!-- agent-hint
covers: the purpose, repository map, setup, test commands and hard rules for a change to ovos-date-parser
source: ovos_date_parser/__init__.py:CHRONOLOGIA_LOCALES, test/test_reader_lang.py, test/test_deprecated_readers.py, test/test_lang_parity.py
generated: no
verify: grep -oP '^\| \x60\K[^\x60,]*' AGENTS.md | grep -v '<' | xargs ls -d > /dev/null || exit 1
see: docs/index.md, docs/api.md, docs/languages.md, docs/adding-a-language.md
-->

Read this file before you change anything in the repository. It gives the map,
the setup, the rules and the checks to run before a push. The documentation
index is [docs/index.md](docs/index.md).

`ovos-date-parser` reads date, time and duration phrases and writes values
back as words. Reading goes to [chronologia](https://github.com/TigreGotico/chronologia).
Writing lives in this package.

## Repository map

The public code:

| Path | Holds |
|---|---|
| `ovos_date_parser/__init__.py` | The public functions, the reader routing (`CHRONOLOGIA_LOCALES`, `_reader_lang`), the dispatch of every `nice_*` function and the deprecated reader names |
| `ovos_date_parser/duration.py` | `DurationResolution` and `convert_duration` |
| `ovos_date_parser/spoken.py` | `spoken_time`, `spoken_date` and `spoken_year` for nl, it and pt |
| `ovos_date_parser/holidays.py` | Named holidays, answered through chronologia |

The writers, the data and the re-exports:

| Path | Holds |
|---|---|
| `ovos_date_parser/dates_<code>.py` | The writers of one language: `nice_time_<code>` and the date family |
| `ovos_date_parser/res/<code>/` | `date_time.json` for the generic date writer, `date_words.json` for the generic duration writer |
| `ovos_date_parser/locale/<code>/*.voc` | Phrase files that overlay chronologia's, file by file |
| `ovos_date_parser/astrodate.py`, `eras.py`, `calendars.py`, `cycles.py`, `regnal.py`, `roman.py` | Import paths that re-export chronologia |

The tests, the docs and the scripts:

| Path | Holds |
|---|---|
| `test/` | The tests. Writers in `test/format_tests/`, reader routing in `test/test_chronologia_*.py` |
| `docs/` | The documentation |
| `examples/` | Runnable scripts |

## Setup

```bash
unset VIRTUAL_ENV
uv venv .venv
uv pip install -p .venv/bin/python --prerelease=allow -e . pytest
```

Use [uv](https://docs.astral.sh/uv/), never pip. Build the venv inside the
checkout.

## Tests

```bash
PYTHONPATH=$PWD .venv/bin/python -m pytest test/test_reader_lang.py test/test_deprecated_readers.py
PYTHONPATH=$PWD .venv/bin/python -m pytest test
```

Run the first line while you work. Run the second before you push.

## Rules

1. Dates and durations read through chronologia. The ja and zh fallbacks have readers in this package. A reading defect belongs in chronologia. A language joins the reading set only through `CHRONOLOGIA_LOCALES` ([adding-a-language](docs/adding-a-language.md)).

2. A writer takes every word from a source. Name the sources in the module docstring, as `dates_kab.py` does. Take expected strings in tests from a source, never from the output of the code ([adding-a-language](docs/adding-a-language.md#writing-add-a-nice_-module)).

3. A new writer has a branch in `nice_time` in `__init__.py`. It has a branch in another `nice_*` function only when no `res/<code>/` file serves it. It has a branch in `nice_duration` only when the shared writer cannot say the language ([adding-a-language](docs/adding-a-language.md#writing-add-a-nice_-module)).

   `test/test_lang_parity.py` checks the 26 languages in its last `LANGS` assignment. It skips bg, el, et, fi, he, hr, nb, nn and tr, and the four languages that write less (an, fy, id and ms).

4. A per-language reader name such as `extract_datetime_pt` is a deprecated name that warns and carries a computed removal version ([api](docs/api.md#deprecated-reader-names)). Do not add a reader of its own to a `dates_<code>.py` module.

5. Never edit `ovos_date_parser/version.py`. The workflow `.github/workflows/release_workflow.yml` bumps it.

## Documentation

- [Index](docs/index.md)
- [API reference](docs/api.md)
- [Languages](docs/languages.md)
- [Adding a language](docs/adding-a-language.md)
