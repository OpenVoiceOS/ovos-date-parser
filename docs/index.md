# Documentation index

<!-- agent-hint
covers: the list of every page under docs/ in reading order
source: docs/*.md
generated: no
verify: diff <(ls docs/*.md | sed 's#docs/##' | grep -v '^index.md$' | sort) <(grep -o '^| \[[^]]*\]([a-z-]*\.md)' docs/index.md | sed 's/.*(\(.*\))/\1/' | sort)
see: ../README.md, ../AGENTS.md
-->

These pages describe `ovos-date-parser`, a library that reads date, time and duration phrases through chronologia and writes them back as words. How-to pages come first, then the explanation, then the reference pages. The [README](../README.md) holds the install steps and a first example.

| Page | What you get |
|---|---|
| [Getting started](getting-started.md) | Install, then read a date and a duration, write a time, a date and a duration, and change the language, in five steps |
| [Adding a language](adding-a-language.md) | A check for what a language lacks, then a path for reading and a path for writing |
| [How it works](how-it-works.md) | The call path of each function, which calls pass to chronologia, and a plot of which function each writer implements |
| [API reference](api.md) | Every public function with its signature, defaults and real output, and the engine that answers it |
| [Language writers](writers.md) | The functions and data of each of the 40 writer languages, the shared writers and the format of the `res/` files |
| [Languages](languages.md) | The languages that read, the languages that write, how a tag resolves, and notes on single writers |
| [Calendar helpers](helpers.md) | Calendar ranges and seasons, the era and scoped-date scanners, and the names that chronologia owns |

The script that builds the plot is [`plots/writer_coverage.py`](plots/writer_coverage.py). Runnable scripts are in [`examples/`](../examples/).

---
[Home](../README.md) · [Getting started →](getting-started.md)
