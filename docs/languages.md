# Languages

<!-- agent-hint
covers: which languages the package reads, which it writes, and what each writer does
source: ovos_date_parser/__init__.py:CHRONOLOGIA_LOCALES, CHRONOLOGIA_DURATION_LOCALES, nice_time; ovos_date_parser/duration.py:DURATION_LEXICONS; ovos_date_parser/res/*/
generated: no
verify: python -m pytest test/test_chronologia_routing.py test/test_chronologia_duration_routing.py test/test_lang_parity.py
see: api.md, adding-a-language.md
-->

This page lists the languages that `extract_datetime` and `extract_duration` read, the languages that the `nice_*` functions write, and the notes that apply to single writers.

## Language tags

Reading and writing treat the tag in different ways. A reader normalizes the tag before it looks at the language. A writer lower-cases the tag and matches its first letters.

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

A writer reads the two-letter code and the region. `nice_time(dt, "pt-BR")` and `nice_time(dt, "PT_BR")` both work, and `"no"` reaches Bokmål. A writer does not map three-letter codes, so use `de` and not `deu`. A language with no writer raises `NotImplementedError`.

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

`extract_duration` takes one of four paths, chosen by the language and the options:

| Path | Languages | Options |
|---|---|---|
| chronologia | an, ast, bg, ca, cs, el, en, fi, fr, fy, hr, id, it, ms, nb, nn, oc, pl, ro, ru, sk, sl, tr, uk | The default call only. A month or a year counts from the moment of the call |
| shared duration engine | az, da, de, es, et, eu, gl, he, hu, nl, pt, and every chronologia-path language except ast when the call sets `resolution` or `replace_token` | `resolution` and `replace_token` work |
| reader of its own | ar, fa, kab, sv | A plain `timedelta` only. Other options raise `NotImplementedError` |
| none | be, cy, eo, fil, ga, ha, hi, hy, is, ka, ko, lt, lv, mk, mt, mwl, sq, sr, sw, ta, th, vi | The call returns `(None, text)` |

A call on ast with `resolution` or `replace_token` raises `NotImplementedError`, because ast has no lexicon.

The shared engine keeps one `DurationLexicon` per language in `ovos_date_parser/duration.py`.

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
>>> nice_time(datetime(2024, 1, 5, 1, 22), "fr"), nice_time(datetime(2024, 1, 5, 7, 40), "fr")
('une heure vingt-deux', 'huit heures moins vingt')
```

Catalan has four registers, selected with `TimeVariantCA`.

```python
>>> nice_time(datetime(2024, 1, 5, 15, 30), "ca")
'les tres i trenta'
>>> nice_time(datetime(2024, 1, 5, 15, 30), "ca", variant=TimeVariantCA.BELL)
'dos quarts de quatre de la tarda'
```

Occitan uses the traditional quarter idioms, with the quarter-to form naming the next hour, and "miègjorn" and "mièjanuèch" for noon and midnight.

```python
>>> [nice_time(datetime(2024, 1, 5, h, m), "oc") for h, m in [(1, 15), (5, 30), (1, 45), (12, 0), (0, 0)]]
['una ora e quart', 'cinc oras e mièja', 'doas oras manca un quart', 'miègjorn', 'mièjanuèch']
```

Romanian says a quarter-hour with "un sfert" and "fără un sfert", where "fără" means minus. An exact hour takes "fix", and `use_ampm=True` adds a part of the day.

```python
>>> [nice_time(datetime(2024, 1, 5, 8, m), "ro") for m in (15, 30, 45, 0)]
['opt și un sfert', 'opt și jumătate', 'nouă fără un sfert', 'opt fix']
>>> nice_time(datetime(2024, 1, 5, 8, 15), "ro", use_ampm=True)
'opt și un sfert dimineața'
```

Asturian follows the feminine-article convention, and `use_ampm=True` adds "de la madrugada", "de la mañana", "de la tarde" or "de la nueche".

```python
>>> nice_time(datetime(2024, 1, 5, 1, 0), "ast"), nice_time(datetime(2024, 1, 5, 7, 45), "ast")
('la una en puntu', 'les ocho menos cuartu')
```

Norwegian Bokmål uses the tens-first number forms, so a year reads "to tusen og tjueen".

```python
>>> nice_year(datetime(2021, 1, 1), "nb"), nice_year(datetime(1984, 1, 1), "nb")
('to tusen og tjueen', 'nitten hundre og åttifire')
```

Danish `nice_year` takes `ad=True` to add "e.kr." and `bc=True` to add "f.kr.". When both are set, `bc` wins. The `ad` option has no effect in a language whose `year_format` resource has no `ad` key.

```python
>>> nice_year(datetime(1984, 1, 1), "da", ad=True)
'nitten hundrede og fire og firs e.kr.'
```

Kabyle writes a clock time with the conjunction `d` and the weekday and month names of the Kabyle calendar.

```python
>>> nice_time(datetime(2024, 1, 5, 15, 30), "kab")
'd ttlata u neṣṣ'
```

## Known gaps

- `nice_year`, `nice_date` and `nice_date_time` do not exist for id and ms.
- The decade and century labels of `nice_span` exist for English only, plus Arabic and Hebrew decades of the 20th century.
- `nice_relative_time` uses one shared implementation, so its phrasing is not tuned to each language.

---
[← API reference](api.md) · [Home](index.md) · [Adding a language →](adding-a-language.md)
