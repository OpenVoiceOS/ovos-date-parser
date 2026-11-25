# Getting started

<!-- agent-hint
covers: the path from install to a first date read from text and a first time written as words, in five steps
source: ovos_date_parser/__init__.py (public functions), ovos_date_parser/duration.py
generated: no
verify: diff <(grep -E '^(from |import |[a-z_, ]+ = |print\()' docs/getting-started.md | .venv/bin/python -I -) <(grep -E '^print\(' docs/getting-started.md | sed 's/^print(.*)  *# //')
see: how-it-works.md, api.md, languages.md, ../README.md
-->

This page takes you from an empty directory to your first date read from text
and your first time written as words, in five steps. Each comment after a
`print` shows the output of a run in a fresh environment.

## Step 1: Install

Make an environment and install the package. It needs no voice assistant.

```bash
uv venv
uv pip install --prerelease=allow ovos-date-parser
```

## Step 2: Read a date from text

`extract_datetime` gives the `datetime` that a phrase names and the words that
are left over. A phrase like "next friday" counts from `anchorDate`. Pass a
fixed anchor to get the same answer on every run.

```python
from datetime import datetime
from ovos_date_parser import extract_datetime

anchor = datetime(2024, 1, 5)
when, leftover = extract_datetime("lets meet next friday at 8am", "en", anchorDate=anchor)
print(when)  # 2024-01-12 08:00:00
print(leftover)  # lets meet
```

## Step 3: Read a duration from text

`extract_duration` gives a `timedelta` and the words that are left over.

```python
from ovos_date_parser import extract_duration

delta, leftover = extract_duration("set a timer for 5 minutes", "en")
print(delta)  # 0:05:00
print(leftover)  # set a timer
```

## Step 4: Write a time, a date and a duration as words

`nice_time`, `nice_date` and `nice_duration` give words that a speech engine can
say.

```python
from datetime import datetime
from ovos_date_parser import nice_time, nice_date, nice_duration

print(nice_time(datetime(2024, 1, 5, 15, 30), "en"))  # half past three
print(nice_date(datetime(2024, 1, 5), "en"))  # friday, january fifth, twenty twenty four
print(nice_duration(3690, "en"))  # one hour one minute thirty seconds
```

## Step 5: Change the language

Each call takes a language code as its second argument. Reading and writing
cover different sets of languages, and [languages.md](languages.md) lists both.

```python
from datetime import datetime
from ovos_date_parser import extract_datetime, nice_time

print(nice_time(datetime(2024, 1, 5, 15, 30), "de"))  # halb vier
print(extract_datetime("amanhã às 15h30", "pt", anchorDate=datetime(2024, 1, 5)))  # [datetime.datetime(2024, 1, 6, 15, 30), '']
```

## Where to go next

[How it works](how-it-works.md) shows which calls pass to chronologia and which
code writes each language. The [API reference](api.md) lists every function with
its parameters.

---
[Index](index.md) · [← Home](../README.md) · [Adding a language →](adding-a-language.md)
