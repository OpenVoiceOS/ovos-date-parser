# Documentation index

<!-- agent-hint
covers: the list of every page under docs/ in reading order
source: docs/*.md
generated: no
verify: diff <(ls docs/*.md | sed 's#docs/##' | grep -v '^index.md$' | sort) <(grep -o '^| \[[^]]*\]([a-z-]*\.md)' docs/index.md | sed 's/.*(\(.*\))/\1/' | sort)
see: ../README.md, ../AGENTS.md
-->

These pages describe `ovos-date-parser`, a library that reads date, time and duration phrases through chronologia and writes them back as words. The [README](../README.md) holds the install steps and a first example.

| Page | What you get |
|---|---|
| [API reference](api.md) | Every public function with its signature, defaults and real output, and the engine that answers it |
| [Languages](languages.md) | The languages that read, the languages that write, how a tag resolves, and notes on single writers |
| [Adding a language](adding-a-language.md) | A check for what a language lacks, then a path for reading and a path for writing |

---
[← README](../README.md) · [Home](index.md) · [API reference →](api.md)
