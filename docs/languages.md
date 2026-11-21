# Languages

<!-- agent-hint
covers: which languages the package reads, which it writes, and what each writer does
source: ovos_date_parser/__init__.py:CHRONOLOGIA_LOCALES, nice_time; ovos_date_parser/duration.py:convert_duration; ovos_date_parser/res/*/
generated: no
verify: sed '/^\x60\x60\x60/d' docs/languages.md | python -m doctest -o ELLIPSIS -o NORMALIZE_WHITESPACE /dev/stdin
see: api.md, adding-a-language.md
-->

This page lists the languages that `extract_datetime` and `extract_duration` read, the languages that the `nice_*` functions write, and the notes that apply to single writers.

## Language tags

Reading and writing treat the tag in different ways. A reader normalizes the tag before it looks at the language. A writer lower-cases the tag and then finds its language in one of two ways, described below.

The reader steps are, in order:

1. Strip white space and lower-case the tag.
2. Replace `_` with `-`.
3. Standardize the language part, so `deu` becomes `de` and `iw` becomes `he`.
4. Map an individual Arabic or Azerbaijani language to its macrolanguage, so `arb` becomes `ar` and `azj` becomes `az`.
5. Map `no` to `nb`, the written standard Bokmål.

The region and the rest of the tag stay as they are. This is the function `_reader_lang` in `ovos_date_parser/__init__.py`.

```python
>>> from ovos_date_parser import _reader_lang
>>> _reader_lang("  DEU "), _reader_lang("no"), _reader_lang("arb-XX"), _reader_lang("pt_BR")
('de', 'nb', 'ar-xx', 'pt-br')
```

A writer lower-cases the tag. Then it finds the language in one of two ways.

1. `nice_time`, `nice_year` and the per-language branches of the other `nice_*` functions test which writer code the tag starts with. A tag that starts with a writer code reaches that writer, even when the tag names another language. The Filipino tag `fil` starts with `fi`, so `nice_time` and `nice_year` answer in Finnish.
2. The generic writers read the folder `res/<code>/`. They take the part of the tag before the first `-` and look for that folder by exact name. These writers are the generic date family, `nice_duration` and `nice_relative_time`. The tag `PT_BR` gives the folder `pt_br`, which does not exist.

The result for each function, with a tag that starts with a writer code and a tag with an underscore:

| Function | `fil` | `PT_BR` |
|---|---|---|
| `nice_time` | Finnish | Portuguese |
| `nice_year` | Finnish | Portuguese |
| `nice_date`, `nice_date_time` | `NotImplementedError` | Portuguese |
| `nice_day`, `nice_weekday`, `nice_month`, `get_date_strings` | English | Portuguese |
| `nice_duration`, `nice_relative_time` | `NotImplementedError` | `NotImplementedError` |

`nice_time` raises `NotImplementedError` for a tag that starts with no writer code, such as `xx`. A writer does not map three-letter codes, so use `de` and not `deu`. Write the region with `-`, as in `pt-BR`.

The tag `"no"` reaches Bokmål in `nice_time`, `nice_date`, `nice_date_time`, `nice_day`, `nice_weekday`, `nice_month` and `nice_year`. In `nice_duration` and `nice_relative_time` it raises `NotImplementedError`, so pass `nb` there.

## Languages that read

`extract_datetime` reads the 61 locales in `CHRONOLOGIA_LOCALES`:

| Codes |
|---|
| an Aragonese, ar Arabic, ast Asturian, az Azerbaijani, be Belarusian, bg Bulgarian, ca Catalan, cs Czech, cy Welsh, da Danish, de German |
| el Greek, en English, eo Esperanto, es Spanish, et Estonian, eu Basque, fa Persian, fi Finnish, fil Filipino, fr French, fy Western Frisian |
| ga Irish, gl Galician, ha Hausa, he Hebrew, hi Hindi, hr Croatian, hu Hungarian, hy Armenian, id Indonesian, is Icelandic, it Italian |
| ka Georgian, kab Kabyle, ko Korean, lt Lithuanian, lv Latvian, mk Macedonian, ms Malay, mt Maltese, mwl Mirandese, nb Norwegian Bokmål |
| nl Dutch, nn Norwegian Nynorsk, oc Occitan, pl Polish, pt Portuguese, ro Romanian, ru Russian, sk Slovak, sl Slovenian, sq Albanian |
| sr Serbian, sv Swedish, sw Swahili, ta Tamil, th Thai, tr Turkish, uk Ukrainian, vi Vietnamese |

Any other language goes to [dateparser](https://dateparser.readthedocs.io). Japanese has a weekday reader of its own in front of dateparser, and Chinese has an unspaced-text reader behind it. The fallback reads absolute dates well and conversational phrases poorly, and it logs a warning.

`extract_duration` reads the same locales through chronologia. A month or a year counts from the day of the call. A locale outside the set answers `(None, text)`. The `resolution` and `replace_token` options convert chronologia's answer, so a month or a year reaches them as a day count.

## Languages that write

All 39 writers are also reader locales. The code list is `an, ar, ast, az, bg, ca, cs, da, de, el, en, es, et, eu, fa, fi, fr, fy, gl, he, hr, hu, id, it, kab, ms, nb, nl, nn, oc, pl, pt, ro, ru, sk, sl, sv, tr, uk`. Thirty-five of them write the whole set of functions. Four write less:

| Language | Missing |
|---|---|
| an Aragonese, fy Western Frisian | `nice_duration` and `nice_relative_time` raise `NotImplementedError` |
| id Indonesian, ms Malay | `nice_date`, `nice_date_time` and `nice_year` raise `NotImplementedError` |

The `spoken_time`, `spoken_date` and `spoken_year` functions in `ovos_date_parser/spoken.py` write Dutch, Italian and Portuguese only. Any other language raises `UnsupportedForm`.

`nice_relative_time` uses one shared implementation, with a dedicated one for Basque. `nice_duration` has dedicated writers for ar, az, pl, ru and uk, and a shared writer that reads `res/<lang>/date_words.json` for the rest.

## Notes on single writers

These examples ran against the code.

French reads the 12-hour clock by default.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_time
>>> nice_time(datetime(2024, 1, 5, 1, 22), "fr"), nice_time(datetime(2024, 1, 5, 7, 40), "fr")
('une heure vingt-deux', 'huit heures moins vingt')
```

Catalan has four registers, selected with `TimeVariantCA`.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_time
>>> from ovos_date_parser.dates_ca import TimeVariantCA
>>> nice_time(datetime(2024, 1, 5, 15, 30), "ca")
'les tres i trenta'
>>> nice_time(datetime(2024, 1, 5, 15, 30), "ca", variant=TimeVariantCA.BELL)
'dos quarts de quatre de la tarda'
```

Occitan uses the traditional quarter idioms, with the quarter-to form naming the next hour, and "miègjorn" and "mièjanuèch" for noon and midnight.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_time
>>> [nice_time(datetime(2024, 1, 5, h, m), "oc") for h, m in [(1, 15), (5, 30), (1, 45), (12, 0), (0, 0)]]
['una ora e quart', 'cinc oras e mièja', 'doas oras manca un quart', 'miègjorn', 'mièjanuèch']
```

Romanian says a quarter-hour with "un sfert" and "fără un sfert", where "fără" means minus. An exact hour takes "fix", and `use_ampm=True` adds a part of the day.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_time
>>> [nice_time(datetime(2024, 1, 5, 8, m), "ro") for m in (15, 30, 45, 0)]
['opt și un sfert', 'opt și jumătate', 'nouă fără un sfert', 'opt fix']
>>> nice_time(datetime(2024, 1, 5, 8, 15), "ro", use_ampm=True)
'opt și un sfert dimineața'
```

Asturian follows the feminine-article convention, and `use_ampm=True` adds "de la madrugada", "de la mañana", "de la tarde" or "de la nueche".

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_time
>>> nice_time(datetime(2024, 1, 5, 1, 0), "ast"), nice_time(datetime(2024, 1, 5, 7, 45), "ast")
('la una en puntu', 'les ocho menos cuartu')
```

Norwegian Bokmål uses the tens-first number forms, so a year reads "to tusen og tjueen".

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_year
>>> nice_year(datetime(2021, 1, 1), "nb"), nice_year(datetime(1984, 1, 1), "nb")
('to tusen og tjueen', 'nitten hundre og åttifire')
```

Danish `nice_year` takes `ad=True` to add "e.kr." and `bc=True` to add "f.kr.". When both are set, `bc` wins. The `ad` option has no effect in a language whose `year_format` resource has no `ad` key.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_year
>>> nice_year(datetime(1984, 1, 1), "da", ad=True)
'nitten hundrede og fire og firs e.kr.'
```

Kabyle writes a clock time with the conjunction `d` and the weekday and month names of the Kabyle calendar.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_time
>>> nice_time(datetime(2024, 1, 5, 15, 30), "kab")
'd ttlata u neṣṣ'
```

## Known gaps

- `nice_year`, `nice_date` and `nice_date_time` do not exist for id and ms.
- The decade and century labels of `nice_span` exist for English only, plus Arabic and Hebrew decades of the 20th century.
- `nice_relative_time` uses one shared implementation, so its phrasing is not tuned to each language.

---
[← API reference](api.md) · [Home](index.md) · [Adding a language →](adding-a-language.md)
