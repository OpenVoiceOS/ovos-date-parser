# Documentation index

<!-- agent-hint
covers: the list of every page under docs/ in reading order
source: docs/*.md
generated: no
verify: for f in api languages adding-a-language; do test -f docs/$f.md && grep -q "($f.md)" docs/index.md && echo ok $f; done
see: ../README.md, ../AGENTS.md
-->

These pages describe `ovos-date-parser`, a library that reads date, time and duration phrases through chronologia and writes them back as words. The [README](../README.md) holds the install steps and a first example.

| Page | What you get |
|---|---|
| [API reference](api.md) | Every public function with its signature, defaults and real output, and the deprecated reader names |
| [Languages](languages.md) | The languages that read, the languages that write, how a tag resolves, and notes on single writers |
| [Adding a language](adding-a-language.md) | A check for what a language lacks, then a path for reading and a path for writing |

---
[← README](../README.md) · [Home](index.md) · [API reference →](api.md)
