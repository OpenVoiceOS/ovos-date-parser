# Languages

<!-- agent-hint
covers: which languages the package reads, which it writes, and what each writer does
source: ovos_date_parser/__init__.py:CHRONOLOGIA_LOCALES, nice_time; ovos_date_parser/duration.py:convert_duration; ovos_date_parser/res/*/
generated: no
verify: sed '/^\x60\x60\x60/d' docs/languages.md | .venv/bin/python -I -m doctest -o ELLIPSIS -o NORMALIZE_WHITESPACE /dev/stdin
see: api.md, adding-a-language.md
-->

This page lists the languages that `extract_datetime` and `extract_duration` read, the languages that the `nice_*` functions write, and the notes that apply to single writers.

## Language tags

Readers and writers read the tag with [linguatag](https://github.com/TigreGotico/linguatag). A tag reads the same in any letter case, with `_` or `-`, and with white space around it.

A reader standardizes the tag, then replaces its language with the closest locale of `CHRONOLOGIA_LOCALES`. So `deu` becomes `de`, `iw` becomes `he`, an individual Arabic or Azerbaijani language such as `arb` or `azj` becomes its macrolanguage, and `no` becomes `nb`, the written standard Bokmål. The region and the rest of the tag stay as they are. This is the function `_reader_lang` in `ovos_date_parser/__init__.py`.

```python
>>> from ovos_date_parser import _reader_lang
>>> _reader_lang("  DEU "), _reader_lang("no"), _reader_lang("arb-XX"), _reader_lang("pt_BR")
('de', 'nb', 'ar-XX', 'pt-BR')
```

A writer finds its language with `writer_lang` in `ovos_date_parser/common.py`. It picks the writer language that the language subtag of the tag is closest to, so `PT_BR` reaches Portuguese in every writer, `no` and `nob` reach Bokmål, `deu` reaches German and `arz` reaches Arabic. A language within linguatag's match distance of a writer reads as that writer: `lb` as German, `mo` as Romanian and `prs` as Persian. Bosnian has a writer of its own, so `bs` and `bs-BA` write the Bosnian month and weekday names (`mart`, not `ožujak`). Its clock follows the Croatian one. A tag that no writer language is close to, such as `fil` or `xx`, raises `NotImplementedError`. Filipino does not reach Finnish, and South Ndebele (`nbl`) does not reach Bokmål.

The Portuguese writers speak the Brazilian forms when the region of the tag is `BR`. A bare `pt` has the region `PT`.

## Languages that read

`extract_datetime` reads the 61 locales in `CHRONOLOGIA_LOCALES`:

```text
an Aragonese, ar Arabic, ast Asturian, az Azerbaijani, be Belarusian, bg Bulgarian, ca Catalan
cs Czech, cy Welsh, da Danish, de German, el Greek, en English, eo Esperanto
es Spanish, et Estonian, eu Basque, fa Persian, fi Finnish, fil Filipino, fr French
fy Western Frisian, ga Irish, gl Galician, ha Hausa, he Hebrew, hi Hindi, hr Croatian
hu Hungarian, hy Armenian, id Indonesian, is Icelandic, it Italian, ka Georgian, kab Kabyle
ko Korean, lt Lithuanian, lv Latvian, mk Macedonian, ms Malay, mt Maltese, mwl Mirandese
nb Norwegian Bokmål, nl Dutch, nn Norwegian Nynorsk, oc Occitan, pl Polish, pt Portuguese, ro Romanian
ru Russian, sk Slovak, sl Slovenian, sq Albanian, sr Serbian, sv Swedish, sw Swahili
ta Tamil, th Thai, tr Turkish, uk Ukrainian, vi Vietnamese
```

The set has 61 codes.

```python
>>> from ovos_date_parser import CHRONOLOGIA_LOCALES
>>> len(CHRONOLOGIA_LOCALES)
61
```

Any other language goes to [dateparser](https://dateparser.readthedocs.io). Japanese has its own weekday reader in front of dateparser. Chinese has an unspaced-text reader behind it. The fallback reads absolute dates well and conversational phrases poorly, and it logs a warning.

`extract_duration` reads the same locales through chronologia. A month or a year counts from the day of the call. A locale outside the set answers `(None, text)`. The `resolution` and `replace_token` options convert chronologia's answer, so a month or a year reaches them as a day count.

## Languages that write

All writers but `bs` are also reader locales, and `bs` reads as Croatian. The 40 writers have the codes `an, ar, ast, az, bg, bs, ca, cs, da, de, el, en, es, et, eu, fa, fi, fr, fy, gl, he, hr, hu, id, it, kab, ms, nb, nl, nn, oc, pl, pt, ro, ru, sk, sl, sv, tr, uk`. Thirty-six of them write the whole set of functions. Four write less:

| Language | Missing |
|---|---|
| an Aragonese, fy Western Frisian | `nice_duration` and `nice_relative_time` raise `NotImplementedError` |
| id Indonesian, ms Malay | `nice_date`, `nice_date_time` and `nice_year` raise `NotImplementedError` |

The `spoken_time`, `spoken_date` and `spoken_year` functions in `ovos_date_parser/spoken.py` write Dutch, Italian and Portuguese only. Any other language raises `UnsupportedForm`.

The function `nice_relative_time` uses one shared implementation, with a dedicated one for Basque. The function `nice_duration` has dedicated writers for ar, az, pl, ru and uk. A shared writer that reads `res/<lang>/date_words.json` serves the rest.

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
[Index](index.md) · [← Language writers](writers.md) · [Calendar helpers →](helpers.md)
