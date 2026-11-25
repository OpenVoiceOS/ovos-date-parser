# Language writers

<!-- agent-hint
covers: the writer of each of the 40 languages, the function families, the shared writers, the res/ data formats and the writer helpers
source: ovos_date_parser/__init__.py (dispatchers, DateTimeFormat), ovos_date_parser/common.py, ovos_date_parser/dates_<code>.py, ovos_date_parser/res/<code>/
generated: no
verify: .venv/bin/python -I -c "import re, ovos_date_parser as p; t = open('docs/writers.md').read(); rows = re.findall(r'^\| \x60[a-z]+\x60 \| [^|]+\| [^|]+\| [^|]+\| (.*) \|$', t, re.M); assert len(rows) == 40; [getattr(p, n) for row in rows for n in re.findall(r'\x60(nice_\w+)\x60', row)]" && sed '/^\x60\x60\x60/d' docs/writers.md | .venv/bin/python -I -m doctest -o ELLIPSIS -o NORMALIZE_WHITESPACE /dev/stdin
see: how-it-works.md, api.md, languages.md, adding-a-language.md
-->

This page names the code and the data that write each language. Read it when
you need the writer of one language, a helper that the top-level functions do
not expose, or the format of a `res/` data file.

The top-level `nice_*` functions call these writers for you. Call a writer
directly to skip the language dispatch.

## The writer of each language

A language has a module `dates_<code>.py`, a folder `res/<code>/` of data, or
both. The module holds the functions that need code. The data drives the shared
writers for everything else. Bosnian has data only, and its clock follows the
Croatian writer.

| Code | Language | Module | Data in `res/` | Functions of the module |
|---|---|---|---|---|
| `an` | Aragonese | `dates_an.py` | none | `nice_date_an`, `nice_date_time_an`, `nice_day_an`, `nice_month_an`, `nice_time_an`, `nice_weekday_an`, `nice_year_an` |
| `ar` | Arabic | `dates_ar.py` | `date_time.json`, `date_words.json` | `nice_duration_ar`, `nice_time_ar` |
| `ast` | Asturian | `dates_ast.py` | `date_words.json` | `nice_date_ast`, `nice_date_time_ast`, `nice_day_ast`, `nice_month_ast`, `nice_time_ast`, `nice_weekday_ast`, `nice_year_ast` |
| `az` | Azerbaijani | `dates_az.py` | `date_time.json`, `date_words.json` | `nice_duration_az`, `nice_time_az` |
| `bg` | Bulgarian | `dates_bg.py` | `date_time.json`, `date_words.json` | `nice_time_bg` |
| `bs` | Bosnian | none | `date_time.json`, `date_words.json` | none |
| `ca` | Catalan | `dates_ca.py` | `date_time.json`, `date_words.json` | `nice_time_ca` |
| `cs` | Czech | `dates_cs.py` | `date_time.json`, `date_words.json` | `nice_time_cs`, `nice_year_cs` |
| `da` | Danish | `dates_da.py` | `date_time.json`, `date_words.json` | `nice_time_da` |
| `de` | German | `dates_de.py` | `date_time.json`, `date_words.json` | `nice_time_de` |
| `el` | Greek | `dates_el.py` | `date_words.json` | `nice_date_el`, `nice_date_time_el`, `nice_day_el`, `nice_month_el`, `nice_time_el`, `nice_weekday_el`, `nice_year_el` |
| `en` | English | `dates_en.py` | `date_time.json`, `date_words.json` | `nice_time_en` |
| `es` | Spanish | `dates_es.py` | `date_words.json` | `nice_date_es`, `nice_date_time_es`, `nice_day_es`, `nice_month_es`, `nice_time_es`, `nice_weekday_es`, `nice_year_es` |
| `et` | Estonian | `dates_et.py` | `date_time.json`, `date_words.json` | `nice_time_et`, `nice_year_et` |
| `eu` | Basque | `dates_eu.py` | `date_time.json`, `date_words.json` | `nice_date_day_eu`, `nice_date_year_eu`, `nice_relative_time_eu`, `nice_time_eu`, `nice_time_inessive_eu`, `nice_year_eu` |
| `fa` | Persian | `dates_fa.py` | `date_time.json`, `date_words.json` | `nice_time_fa` |
| `fi` | Finnish | `dates_fi.py` | `date_time.json`, `date_words.json` | `nice_time_fi`, `nice_year_fi` |
| `fr` | French | `dates_fr.py` | `date_time.json`, `date_words.json` | `nice_time_fr` |
| `fy` | Western Frisian | `dates_fy.py` | none | `nice_date_fy`, `nice_date_time_fy`, `nice_day_fy`, `nice_month_fy`, `nice_part_of_day_fy`, `nice_time_fy`, `nice_weekday_fy`, `nice_year_fy` |
| `gl` | Galician | `dates_gl.py` | `date_words.json` | `nice_date_gl`, `nice_date_time_gl`, `nice_day_gl`, `nice_month_gl`, `nice_time_gl`, `nice_weekday_gl`, `nice_year_gl` |
| `he` | Hebrew | `dates_he.py` | `date_words.json` | `nice_date_he`, `nice_date_time_he`, `nice_day_he`, `nice_month_he`, `nice_time_he`, `nice_weekday_he`, `nice_year_he` |
| `hr` | Croatian | `dates_hr.py` | `date_time.json`, `date_words.json` | `nice_time_hr` |
| `hu` | Hungarian | `dates_hu.py` | `date_time.json`, `date_words.json` | `nice_time_hu` |
| `id` | Indonesian | `dates_id.py` | `date_words.json` | `nice_time_id` |
| `it` | Italian | `dates_it.py` | `date_time.json`, `date_words.json` | `nice_time_it` |
| `kab` | Kabyle | `dates_kab.py` | `date_time.json`, `date_words.json` | `nice_time_kab` |
| `ms` | Malay | `dates_ms.py` | `date_words.json` | `nice_time_ms` |
| `nb` | Norwegian Bokmål | `dates_nb.py` | `date_time.json`, `date_words.json` | `nice_time_nb` |
| `nl` | Dutch | `dates_nl.py` | `date_time.json`, `date_words.json` | `nice_part_of_day_nl`, `nice_time_nl` |
| `nn` | Norwegian Nynorsk | `dates_nn.py` | `date_time.json`, `date_words.json` | `nice_time_nn` |
| `oc` | Occitan | `dates_oc.py` | `date_words.json` | `nice_date_oc`, `nice_date_time_oc`, `nice_day_oc`, `nice_month_oc`, `nice_time_oc`, `nice_weekday_oc`, `nice_year_oc` |
| `pl` | Polish | `dates_pl.py` | `date_time.json`, `date_words.json` | `nice_duration_pl`, `nice_time_pl`, `nice_year_pl` |
| `pt` | Portuguese | `dates_pt.py` | `date_words.json` | `nice_date_pt`, `nice_date_time_pt`, `nice_day_pt`, `nice_month_pt`, `nice_time_pt`, `nice_weekday_pt`, `nice_year_pt` |
| `ro` | Romanian | `dates_ro.py` | `date_time.json`, `date_words.json` | `nice_date_ro`, `nice_date_time_ro`, `nice_day_ro`, `nice_month_ro`, `nice_time_ro`, `nice_weekday_ro`, `nice_year_ro` |
| `ru` | Russian | `dates_ru.py` | `date_time.json`, `date_words.json` | `nice_duration_ru`, `nice_time_ru` |
| `sk` | Slovak | `dates_sk.py` | `date_time.json`, `date_words.json` | `nice_time_sk` |
| `sl` | Slovenian | `dates_sl.py` | `date_time.json`, `date_words.json` | `nice_time_sl` |
| `sv` | Swedish | `dates_sv.py` | `date_time.json`, `date_words.json` | `nice_time_sv`, `nice_year_sv` |
| `tr` | Turkish | `dates_tr.py` | `date_time.json`, `date_words.json` | `nice_time_tr` |
| `uk` | Ukrainian | `dates_uk.py` | `date_time.json`, `date_words.json` | `nice_duration_uk`, `nice_time_uk` |

[how-it-works.md](how-it-works.md#which-code-writes-each-language) has a plot of
which language implements which function.

## Writer functions

A function of a language module takes no language code. `nice_time_<code>(dt,
speech=True, use_24hour=False, use_ampm=False)` writes a time. The writers for
bg, hr and sk add `variant`, the Catalan writer adds `variant` with a
`TimeVariantCA` value, and the Portuguese writers add `variant` with a
`PortugueseVariant` value. The defaults of `use_24hour` are `True` for bg, cs,
pl, ru, sk and uk.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_time_en, nice_time_de, nice_year_cs, nice_year_pl
>>> dt = datetime(2024, 1, 5, 15, 30)
>>> nice_time_en(dt), nice_time_en(dt, speech=False, use_24hour=True), nice_time_de(dt)
('half past three', '15:30', 'halb vier')
>>> nice_year_cs(dt), nice_year_pl(dt), nice_year_pl(dt, genitive=True)
('dva tisíce dvacet čtyři', 'dwa tysiące dwudziesty czwarty', 'dwa tysiące dwudziestego czwartego')

```

The date family has one function per output. `nice_date_<code>` takes `dt`, an
optional reference datetime and `include_weekday=True`. `nice_date_time_<code>`
takes `dt`, the reference datetime, `use_24hour=False` and `use_ampm=False`. The
others are `nice_day_<code>(dt, date_format='DMY', include_month=True)`,
`nice_weekday_<code>(dt)`, `nice_month_<code>(dt)` and `nice_year_<code>(dt,
bc=False)`. The ten languages with the full family are an, ast, el, es, fy, gl,
he, oc, pt and ro.

```python
>>> from ovos_date_parser import nice_date_es, nice_day_es, nice_weekday_es, nice_month_es, nice_date_time_es
>>> nice_date_es(dt)
'viernes, cinco de enero de dos mil veinticuatro'
>>> nice_day_es(dt), nice_weekday_es(dt), nice_month_es(dt)
('5 de enero', 'viernes', 'enero')
>>> nice_date_time_es(dt)
'viernes, cinco de enero de dos mil veinticuatro a las tres y media'

```

The year writers of cs, et, eu, fi, pl and sv take the place of the shared year
writer. The duration writers `nice_duration_<code>(duration, speech=True)` exist
for ar, az, pl, ru and uk, because their numerals decline.

```python
>>> from ovos_date_parser import nice_duration_ru
>>> nice_duration_ru(3690)
'один час одна минута тридцать секунд'

```

Basque writes dates from the shared data and adds three helpers. The functions
`nice_date_day_eu(dt)` and `nice_date_year_eu(dt)` give the day and the year
with the Basque suffixes, and `nice_time_inessive_eu(dt, use_24hour=False,
use_ampm=False)` gives the time in the inessive case. `nice_relative_time_eu(when,
relative_to)` is the only relative-time writer of a single language.

```python
>>> from ovos_date_parser import nice_date_day_eu, nice_date_year_eu, nice_time_inessive_eu
>>> nice_date_day_eu(dt), nice_date_year_eu(dt)
('bosta', 'bi mila eta hogeita lauko')
>>> nice_time_inessive_eu(dt)
'hiru eta erdietan'

```

Dutch and Western Frisian add a part-of-day writer, `nice_part_of_day_nl(dt,
speech=True)` and `nice_part_of_day_fy(dt, speech=True)`. They give the adverb for the part of the day, with a leading space,
such as `'s middags` in Dutch.

```python
>>> from ovos_date_parser import nice_part_of_day_nl
>>> nice_part_of_day_nl(dt)
" 's middags"

```

## The shared writers

The shared writers serve every language whose module has no function of its own.

- `nice_duration_generic(lang, duration, speech=True)` writes a duration from the
  number words of ovos-number-parser and the unit words in
  `res/<code>/date_words.json`.
- `nice_relative_time_generic(lang, when, relative_to)` writes a relative time in
  the same way.
- The object `date_time_format`, an instance of `DateTimeFormat`, writes the
  date, the date and time, the day and the year from `res/<code>/date_time.json`.
  Call `date_time_format.cache(lang)` once per language before you use its
  methods.

```python
>>> from datetime import datetime
>>> from ovos_date_parser import nice_duration_generic, nice_relative_time_generic, date_time_format
>>> nice_duration_generic("en", 3690), nice_duration_generic("de", 3690, speech=False)
('one hour one minute thirty seconds', '1:01:30')
>>> nice_relative_time_generic("en", datetime(2024, 1, 10), datetime(2024, 1, 5))
'five days'
>>> date_time_format.cache("en")
'en'
>>> date_time_format.year_format(datetime(1984, 1, 1), "en", False)
'nineteen eighty four'
>>> date_time_format.year_format(datetime(44, 1, 1), "en", True)
'forty four b.c.'

```

## The data of the shared writers

`res/<code>/date_time.json` holds ten sections.

| Section | Holds |
|---|---|
| `number` | Number words for 0 to 20, the tens and the hundreds, keyed by the number as a string |
| `weekday` | The weekday names, keyed `"0"` for Monday to `"6"` |
| `month` | The month names, keyed `"1"` to `"12"` |
| `date` | The day-of-month words, keyed `"1"` to `"31"` |
| `decade_format`, `hundreds_format`, `thousand_format` | Numbered rules `"1"`, `"2"` and so on, each with a `match` regular expression and a `format` template, and a `default` template |
| `year_format` | The same rules for a whole year, with the extra key `ad` in some languages |
| `date_format` | The templates `date_full`, `date_full_no_year`, `date_full_no_year_month`, `today`, `tomorrow` and `yesterday` |
| `date_time_format` | The template `date_time` that joins a date and a time |

The first rule of a section whose `match` fits the number wins. The templates
use the placeholders `{weekday}`, `{month}`, `{day}`, `{formatted_year}`,
`{formatted_date}`, `{formatted_time}` and `{bc}`, and the number
placeholders `{x}`, `{xx}`, `{x0}`, `{x_in_x0}`, `{xxx}`, `{x00}`, `{x_in_x00}`,
`{xx00}`, `{xx_in_xx00}`, `{x000}`, `{x_in_x000}`, `{x0_in_x000}` and
`{x_in_0x00}`. The `NUMBER_TUPLE` named tuple holds those number placeholders
for one year. Two languages also carry `month_format`, and one carries
`time_format`.

`res/<code>/date_words.json` holds the unit words of the shared duration and
relative-time writers: `second`, `seconds`, `minute`, `minutes`, `hour`,
`hours`, `day` and `days`. Some languages add a key for the present moment.

`res/<code>/date_time_test.json` holds the cases of the format tests, in the
sections `test_nice_year`, `test_nice_date` and `test_nice_date_time`. A case
gives `datetime_param`, the arguments to build the `datetime`, and `assertEqual`,
the expected text. It adds `bc`, a reference datetime, `use_24hour` and `use_ampm` where the
call needs them. The tests in `test/format_tests/` read these files.

## Helpers

`writer_lang(lang)` gives the writer language of a tag, or `None`.
`primary_language(lang)` gives the language subtag in canonical form.
`portuguese_variant(lang)` gives `PortugueseVariant.BR` for a Brazilian tag and
`PortugueseVariant.PT` for every other Portuguese tag. `TimeVariantCA` selects
the Catalan clock register.

```python
>>> from ovos_date_parser import writer_lang, primary_language, portuguese_variant
>>> writer_lang("PT_br"), writer_lang("bs-BA"), writer_lang("no"), writer_lang("fil")
('pt', 'bs', 'nb', None)
>>> primary_language("PT_br")
'pt'
>>> portuguese_variant("pt-BR").value, portuguese_variant("pt").value
('br', 'pt')

```

---
[Index](index.md) · [← API reference](api.md) · [Language notes →](languages.md)
