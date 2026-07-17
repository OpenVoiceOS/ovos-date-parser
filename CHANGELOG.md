# Changelog

## [0.28.1a4](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a4) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a1...0.28.1a4)

**Merged pull requests:**

- fix: harden Arabic datetime extraction \(proclitics, within, out-of-range clock\) [\#222](https://github.com/OpenVoiceOS/ovos-date-parser/pull/222) ([JarbasAl](https://github.com/JarbasAl))
- fix: guard Spanish datetime extractor against numeric time tokens with letter suffixes [\#221](https://github.com/OpenVoiceOS/ovos-date-parser/pull/221) ([JarbasAl](https://github.com/JarbasAl))
- fix: guard Italian datetime extractor against numeric time tokens with letter suffixes [\#220](https://github.com/OpenVoiceOS/ovos-date-parser/pull/220) ([JarbasAl](https://github.com/JarbasAl))
- fix: guard Romanian datetime extractor against numeric time tokens with letter suffixes [\#219](https://github.com/OpenVoiceOS/ovos-date-parser/pull/219) ([JarbasAl](https://github.com/JarbasAl))
- fix: guard Galician datetime extractor against numeric time tokens with letter suffixes [\#218](https://github.com/OpenVoiceOS/ovos-date-parser/pull/218) ([JarbasAl](https://github.com/JarbasAl))
- fix: guard Catalan datetime extractor against numeric time tokens with letter suffixes [\#217](https://github.com/OpenVoiceOS/ovos-date-parser/pull/217) ([JarbasAl](https://github.com/JarbasAl))
- fix: guard Asturian datetime extractor against numeric time tokens with letter suffixes [\#216](https://github.com/OpenVoiceOS/ovos-date-parser/pull/216) ([JarbasAl](https://github.com/JarbasAl))
- fix: guard Greek datetime extractor against numeric time tokens with letter suffixes [\#215](https://github.com/OpenVoiceOS/ovos-date-parser/pull/215) ([JarbasAl](https://github.com/JarbasAl))
- fix: return None for empty Swedish duration input instead of crashing [\#214](https://github.com/OpenVoiceOS/ovos-date-parser/pull/214) ([JarbasAl](https://github.com/JarbasAl))
- fix: guard generic duration resolver against overflow from huge values [\#213](https://github.com/OpenVoiceOS/ovos-date-parser/pull/213) ([JarbasAl](https://github.com/JarbasAl))
- fix: guard Occitan datetime extractor against numeric time tokens with letter suffixes [\#212](https://github.com/OpenVoiceOS/ovos-date-parser/pull/212) ([JarbasAl](https://github.com/JarbasAl))
- fix: resolve Swedish relative-future datetime offsets and guard impossible dates [\#211](https://github.com/OpenVoiceOS/ovos-date-parser/pull/211) ([JarbasAl](https://github.com/JarbasAl))
- fix: return None for malformed Dutch datetimes instead of crashing [\#210](https://github.com/OpenVoiceOS/ovos-date-parser/pull/210) ([JarbasAl](https://github.com/JarbasAl))
- fix: guard Italian datetime extractor against malformed clock tokens [\#209](https://github.com/OpenVoiceOS/ovos-date-parser/pull/209) ([JarbasAl](https://github.com/JarbasAl))
- fix: add Estonian relative second offsets [\#208](https://github.com/OpenVoiceOS/ovos-date-parser/pull/208) ([JarbasAl](https://github.com/JarbasAl))
- fix: guard English datetime extractor against malformed clock and offset input [\#207](https://github.com/OpenVoiceOS/ovos-date-parser/pull/207) ([JarbasAl](https://github.com/JarbasAl))
- fix: add Finnish relative seconds offset to extract\_datetime\_fi [\#206](https://github.com/OpenVoiceOS/ovos-date-parser/pull/206) ([JarbasAl](https://github.com/JarbasAl))
- fix: Catalan relative time offsets and impossible dates [\#205](https://github.com/OpenVoiceOS/ovos-date-parser/pull/205) ([JarbasAl](https://github.com/JarbasAl))
- fix: preserve anchor clock and guard impossible dates in Asturian datetime [\#204](https://github.com/OpenVoiceOS/ovos-date-parser/pull/204) ([JarbasAl](https://github.com/JarbasAl))
- fix: preserve anchor time of day for Hungarian relative offsets [\#203](https://github.com/OpenVoiceOS/ovos-date-parser/pull/203) ([JarbasAl](https://github.com/JarbasAl))
- fix: compute Occitan relative time offsets from the anchor time [\#202](https://github.com/OpenVoiceOS/ovos-date-parser/pull/202) ([JarbasAl](https://github.com/JarbasAl))
- fix: preserve anchor time of day for relative German offsets [\#201](https://github.com/OpenVoiceOS/ovos-date-parser/pull/201) ([JarbasAl](https://github.com/JarbasAl))
- fix: resolve Basque relative-future datetime offsets [\#200](https://github.com/OpenVoiceOS/ovos-date-parser/pull/200) ([JarbasAl](https://github.com/JarbasAl))

## [0.28.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.0a1...0.28.1a1)

**Merged pull requests:**

- fix: keep Italian duration-unit words out of ordinal digit conversion [\#198](https://github.com/OpenVoiceOS/ovos-date-parser/pull/198) ([JarbasAl](https://github.com/JarbasAl))

## [0.28.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.27.1a1...0.28.0a1)

**Merged pull requests:**

- feat: Aragonese date formatting [\#140](https://github.com/OpenVoiceOS/ovos-date-parser/pull/140) ([JarbasAl](https://github.com/JarbasAl))

## [0.27.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.27.1a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.27.0a1...0.27.1a1)

**Merged pull requests:**

- fix: compute Romance relative time offsets from the anchor time [\#185](https://github.com/OpenVoiceOS/ovos-date-parser/pull/185) ([JarbasAl](https://github.com/JarbasAl))

## [0.27.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.27.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.26.0a1...0.27.0a1)

**Merged pull requests:**

- feat: Norwegian Nynorsk \(nn\) date formatting/parsing [\#155](https://github.com/OpenVoiceOS/ovos-date-parser/pull/155) ([JarbasAl](https://github.com/JarbasAl))

## [0.26.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.26.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.25.0a1...0.26.0a1)

**Merged pull requests:**

- feat: add Bulgarian \(bg\) date support [\#154](https://github.com/OpenVoiceOS/ovos-date-parser/pull/154) ([JarbasAl](https://github.com/JarbasAl))

## [0.25.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.25.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.24.0a1...0.25.0a1)

**Merged pull requests:**

- feat: add Croatian \(hr\) date support [\#150](https://github.com/OpenVoiceOS/ovos-date-parser/pull/150) ([JarbasAl](https://github.com/JarbasAl))

## [0.24.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.24.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.23.1a1...0.24.0a1)

**Merged pull requests:**

- feat: Estonian \(et\) date formatting and parsing [\#152](https://github.com/OpenVoiceOS/ovos-date-parser/pull/152) ([JarbasAl](https://github.com/JarbasAl))

## [0.23.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.23.1a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.23.0a1...0.23.1a1)

**Merged pull requests:**

- fix: close dates\_el import tuple in package init [\#190](https://github.com/OpenVoiceOS/ovos-date-parser/pull/190) ([JarbasAl](https://github.com/JarbasAl))

## [0.23.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.23.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.22.0a1...0.23.0a1)

**Merged pull requests:**

- feat: add Greek \(el\) date support [\#149](https://github.com/OpenVoiceOS/ovos-date-parser/pull/149) ([JarbasAl](https://github.com/JarbasAl))

## [0.22.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.22.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.21.0a1...0.22.0a1)

## [0.21.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.21.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.20.0a1...0.21.0a1)

**Merged pull requests:**

- feat: Malay date formatting and parsing [\#158](https://github.com/OpenVoiceOS/ovos-date-parser/pull/158) ([JarbasAl](https://github.com/JarbasAl))

## [0.20.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.20.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.19.0a1...0.20.0a1)

**Merged pull requests:**

- feat: Indonesian date formatting and parsing [\#157](https://github.com/OpenVoiceOS/ovos-date-parser/pull/157) ([JarbasAl](https://github.com/JarbasAl))
- feat: Norwegian Bokmål \(nb\) date formatting/parsing [\#153](https://github.com/OpenVoiceOS/ovos-date-parser/pull/153) ([JarbasAl](https://github.com/JarbasAl))
- feat: Finnish \(fi\) date formatting and parsing [\#151](https://github.com/OpenVoiceOS/ovos-date-parser/pull/151) ([JarbasAl](https://github.com/JarbasAl))
- feat: add Hebrew \(he\) date support [\#148](https://github.com/OpenVoiceOS/ovos-date-parser/pull/148) ([JarbasAl](https://github.com/JarbasAl))

## [0.19.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.19.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.18.1a3...0.19.0a1)

**Merged pull requests:**

- feat: Turkish date formatting and parsing [\#156](https://github.com/OpenVoiceOS/ovos-date-parser/pull/156) ([JarbasAl](https://github.com/JarbasAl))
- feat: add Slovak \(sk\) date support [\#147](https://github.com/OpenVoiceOS/ovos-date-parser/pull/147) ([JarbasAl](https://github.com/JarbasAl))
- feat: expose Catalan time registers by name \(standard vs quarts\) [\#146](https://github.com/OpenVoiceOS/ovos-date-parser/pull/146) ([JarbasAl](https://github.com/JarbasAl))
- feat: West Frisian date formatting [\#145](https://github.com/OpenVoiceOS/ovos-date-parser/pull/145) ([JarbasAl](https://github.com/JarbasAl))

## [0.18.1a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.18.1a3) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.18.1a2...0.18.1a3)

**Merged pull requests:**

- docs: polish docs and examples for beginners, advanced users and standalone use [\#179](https://github.com/OpenVoiceOS/ovos-date-parser/pull/179) ([JarbasAl](https://github.com/JarbasAl))

## [0.18.1a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.18.1a2) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.18.1a1...0.18.1a2)

**Merged pull requests:**

- fix: parse spoken clock times in Spanish datetime extraction [\#180](https://github.com/OpenVoiceOS/ovos-date-parser/pull/180) ([JarbasAl](https://github.com/JarbasAl))

## [0.18.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.18.1a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.18.0a3...0.18.1a1)

**Merged pull requests:**

- fix: harden Arabic time and duration parsing [\#178](https://github.com/OpenVoiceOS/ovos-date-parser/pull/178) ([JarbasAl](https://github.com/JarbasAl))
- fix: Polish spoken ordinal dates and leap-day crash in extract\_datetime [\#177](https://github.com/OpenVoiceOS/ovos-date-parser/pull/177) ([JarbasAl](https://github.com/JarbasAl))
- fix: correct Ukrainian morning hours and guard bogus year in datetime [\#176](https://github.com/OpenVoiceOS/ovos-date-parser/pull/176) ([JarbasAl](https://github.com/JarbasAl))
- fix: convert spelled-out numbers in Galician durations [\#175](https://github.com/OpenVoiceOS/ovos-date-parser/pull/175) ([JarbasAl](https://github.com/JarbasAl))
- fix: correct Portuguese month names and clock-time parsing [\#174](https://github.com/OpenVoiceOS/ovos-date-parser/pull/174) ([JarbasAl](https://github.com/JarbasAl))
- fix: Dutch date parsing of month names, part-of-day and clock hours [\#173](https://github.com/OpenVoiceOS/ovos-date-parser/pull/173) ([JarbasAl](https://github.com/JarbasAl))
- fix: robust English datetime extraction for impossible dates [\#172](https://github.com/OpenVoiceOS/ovos-date-parser/pull/172) ([JarbasAl](https://github.com/JarbasAl))
- fix: Czech accusative weekdays and February genitive in extract\_datetime [\#171](https://github.com/OpenVoiceOS/ovos-date-parser/pull/171) ([JarbasAl](https://github.com/JarbasAl))
- fix: build Hungarian explicit dates without crashing on invalid days [\#170](https://github.com/OpenVoiceOS/ovos-date-parser/pull/170) ([JarbasAl](https://github.com/JarbasAl))
- fix\(sl\): leap-day dates and night-hour qualifiers in Slovene [\#169](https://github.com/OpenVoiceOS/ovos-date-parser/pull/169) ([JarbasAl](https://github.com/JarbasAl))
- fix: robust German date extraction for clock hours and invalid dates [\#168](https://github.com/OpenVoiceOS/ovos-date-parser/pull/168) ([JarbasAl](https://github.com/JarbasAl))
- fix: parse spoken Italian clock hours and guard malformed dates [\#167](https://github.com/OpenVoiceOS/ovos-date-parser/pull/167) ([JarbasAl](https://github.com/JarbasAl))
- fix: recognise "et demie" and bare part-of-day in French dates [\#166](https://github.com/OpenVoiceOS/ovos-date-parser/pull/166) ([JarbasAl](https://github.com/JarbasAl))
- fix: harden Basque datetime extraction against crashes and wrong hours [\#165](https://github.com/OpenVoiceOS/ovos-date-parser/pull/165) ([JarbasAl](https://github.com/JarbasAl))
- fix: handle 29 of february and None input in Asturian datetime extraction [\#164](https://github.com/OpenVoiceOS/ovos-date-parser/pull/164) ([JarbasAl](https://github.com/JarbasAl))
- fix: parse leap-day dates without a year \(ru\) [\#163](https://github.com/OpenVoiceOS/ovos-date-parser/pull/163) ([JarbasAl](https://github.com/JarbasAl))
- fix: Swedish datetime parsing crashes \(named months, bare clock, leap day\) [\#162](https://github.com/OpenVoiceOS/ovos-date-parser/pull/162) ([JarbasAl](https://github.com/JarbasAl))
- fix: understand spoken Danish clock times and evening hours [\#161](https://github.com/OpenVoiceOS/ovos-date-parser/pull/161) ([JarbasAl](https://github.com/JarbasAl))
- fix: correct Azerbaijani clock and date parsing [\#160](https://github.com/OpenVoiceOS/ovos-date-parser/pull/160) ([JarbasAl](https://github.com/JarbasAl))
- fix: correct "ago" direction and None handling in Persian date parsing [\#159](https://github.com/OpenVoiceOS/ovos-date-parser/pull/159) ([JarbasAl](https://github.com/JarbasAl))

## [0.18.0a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.18.0a3) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.18.0a1...0.18.0a3)

**Merged pull requests:**

- ci: modernize the release workflows onto the shared uv-build path [\#137](https://github.com/OpenVoiceOS/ovos-date-parser/pull/137) ([JarbasAl](https://github.com/JarbasAl))
- chore: migrate packaging to pyproject.toml and add LICENSE [\#136](https://github.com/OpenVoiceOS/ovos-date-parser/pull/136) ([JarbasAl](https://github.com/JarbasAl))

## [0.18.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.18.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.17.0a1...0.18.0a1)

**Merged pull requests:**

- feat: add Occitan \(oc\) date support [\#132](https://github.com/OpenVoiceOS/ovos-date-parser/pull/132) ([JarbasAl](https://github.com/JarbasAl))

## [0.17.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.17.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.16.0a1...0.17.0a1)

**Merged pull requests:**

- feat\(ro\): Romanian date and time parsing and formatting [\#130](https://github.com/OpenVoiceOS/ovos-date-parser/pull/130) ([JarbasAl](https://github.com/JarbasAl))

## [0.16.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.16.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.15.0a2...0.16.0a1)

**Merged pull requests:**

- feat: calendar range, season and date-ordinal utilities [\#131](https://github.com/OpenVoiceOS/ovos-date-parser/pull/131) ([JarbasAl](https://github.com/JarbasAl))

## [0.15.0a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.15.0a2) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.15.0a1...0.15.0a2)

**Merged pull requests:**

- refactor: port Slavic and Turkic durations to the shared engine [\#126](https://github.com/OpenVoiceOS/ovos-date-parser/pull/126) ([JarbasAl](https://github.com/JarbasAl))

## [0.15.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.15.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.14.0a1...0.15.0a1)

**Merged pull requests:**

- feat: Kabyle \(kab\) date and time support [\#125](https://github.com/OpenVoiceOS/ovos-date-parser/pull/125) ([JarbasAl](https://github.com/JarbasAl))

## [0.14.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.14.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.13.0a2...0.14.0a1)

## [0.13.0a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.13.0a2) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.13.0a1...0.13.0a2)

**Merged pull requests:**

- refactor: port Romance and Germanic durations to the shared engine [\#124](https://github.com/OpenVoiceOS/ovos-date-parser/pull/124) ([JarbasAl](https://github.com/JarbasAl))
- feat: asturian date and time support [\#122](https://github.com/OpenVoiceOS/ovos-date-parser/pull/122) ([JarbasAl](https://github.com/JarbasAl))

## [0.13.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.13.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.12.0a1...0.13.0a1)

**Merged pull requests:**

- feat: shared duration extraction engine with DurationResolution [\#119](https://github.com/OpenVoiceOS/ovos-date-parser/pull/119) ([JarbasAl](https://github.com/JarbasAl))

## [0.12.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.12.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.11.0a5...0.12.0a1)

**Merged pull requests:**

- feat: arabic date and time support [\#120](https://github.com/OpenVoiceOS/ovos-date-parser/pull/120) ([JarbasAl](https://github.com/JarbasAl))

## [0.11.0a5](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.11.0a5) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.11.0a4...0.11.0a5)

## [0.11.0a4](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.11.0a4) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.11.0a3...0.11.0a4)

**Merged pull requests:**

- ci: install setuptools for the release workflow [\#117](https://github.com/OpenVoiceOS/ovos-date-parser/pull/117) ([JarbasAl](https://github.com/JarbasAl))

## [0.11.0a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.11.0a3) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.11.0a2...0.11.0a3)

## [0.11.0a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.11.0a2) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.11.0a1...0.11.0a2)

**Merged pull requests:**

- feat: language parity test and display duration for polish, russian and ukrainian [\#116](https://github.com/OpenVoiceOS/ovos-date-parser/pull/116) ([JarbasAl](https://github.com/JarbasAl))

## [0.11.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.11.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.10.0a1...0.11.0a1)

**Merged pull requests:**

- feat: slovenian datetime extraction [\#115](https://github.com/OpenVoiceOS/ovos-date-parser/pull/115) ([JarbasAl](https://github.com/JarbasAl))

## [0.10.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.10.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.9.0a1...0.10.0a1)

**Merged pull requests:**

- feat: galician datetime extraction [\#114](https://github.com/OpenVoiceOS/ovos-date-parser/pull/114) ([JarbasAl](https://github.com/JarbasAl))

## [0.9.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.9.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.8.0a1...0.9.0a1)

**Merged pull requests:**

- feat: hungarian datetime extraction [\#113](https://github.com/OpenVoiceOS/ovos-date-parser/pull/113) ([JarbasAl](https://github.com/JarbasAl))

## [0.8.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.8.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.2a1...0.8.0a1)

**Merged pull requests:**

- feat: duration extraction for basque, french, hungarian, italian and slovenian [\#112](https://github.com/OpenVoiceOS/ovos-date-parser/pull/112) ([JarbasAl](https://github.com/JarbasAl))

## [0.7.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.2a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.0a5...0.7.2a1)

**Merged pull requests:**

- fix: datetime extraction bugs across languages + full multilingual test suites [\#111](https://github.com/OpenVoiceOS/ovos-date-parser/pull/111) ([JarbasAl](https://github.com/JarbasAl))
- Fix French runtime date resources [\#108](https://github.com/OpenVoiceOS/ovos-date-parser/pull/108) ([goldyfruit](https://github.com/goldyfruit))

## [0.7.0a5](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.0a5) (2025-12-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.0a4...0.7.0a5)

## [0.7.0a4](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.0a4) (2025-12-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.0a3...0.7.0a4)

**Merged pull requests:**

- chore\(deps\): update dependency python to 3.14 [\#102](https://github.com/OpenVoiceOS/ovos-date-parser/pull/102) ([renovate[bot]](https://github.com/apps/renovate))

## [0.7.0a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.0a3) (2025-12-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.0a2...0.7.0a3)

**Merged pull requests:**

- chore\(deps\): update actions/setup-python action to v6 [\#106](https://github.com/OpenVoiceOS/ovos-date-parser/pull/106) ([renovate[bot]](https://github.com/apps/renovate))
- chore\(deps\): update actions/checkout action to v6 [\#103](https://github.com/OpenVoiceOS/ovos-date-parser/pull/103) ([renovate[bot]](https://github.com/apps/renovate))

## [0.7.0a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.0a2) (2025-12-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.0a1...0.7.0a2)

**Merged pull requests:**

- chore: Configure Renovate [\#101](https://github.com/OpenVoiceOS/ovos-date-parser/pull/101) ([renovate[bot]](https://github.com/apps/renovate))

## [0.7.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.0a1) (2025-08-04)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.5...0.7.0a1)

**Merged pull requests:**

- feat: optional weekday in nice\_date [\#97](https://github.com/OpenVoiceOS/ovos-date-parser/pull/97) ([JarbasAl](https://github.com/JarbasAl))

## [0.6.5](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.5) (2025-08-04)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.5a1...0.6.5)

**Merged pull requests:**

- Release 0.6.5a1 [\#96](https://github.com/OpenVoiceOS/ovos-date-parser/pull/96) ([github-actions[bot]](https://github.com/apps/github-actions))

## [0.6.5a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.5a1) (2025-08-04)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.4...0.6.5a1)

**Merged pull requests:**

- fix: pt number grammatical gender [\#95](https://github.com/OpenVoiceOS/ovos-date-parser/pull/95) ([JarbasAl](https://github.com/JarbasAl))

## [0.6.4](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.4) (2025-08-03)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.4a1...0.6.4)

## [0.6.4a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.4a1) (2025-08-03)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.3...0.6.4a1)

## [0.6.3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.3) (2025-07-30)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.3a1...0.6.3)

## [0.6.3a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.3a1) (2025-07-30)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.2...0.6.3a1)

## [0.6.2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.2) (2025-03-27)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.2a1...0.6.2)

## [0.6.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.2a1) (2025-03-27)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.1...0.6.2a1)

## [0.6.1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.1) (2025-02-27)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.0...0.6.1)

## [0.6.0](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.0) (2025-02-27)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.0a1...0.6.0)

## [0.6.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.0a1) (2025-02-27)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.5.0...0.6.0a1)

## [0.5.0](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.5.0) (2025-02-27)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.5.0a1...0.5.0)

## [0.5.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.5.0a1) (2025-02-27)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.4.0...0.5.0a1)

## [0.4.0](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.4.0) (2024-11-15)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.4.0a1...0.4.0)

## [0.4.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.4.0a1) (2024-11-15)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.3.0...0.4.0a1)

## [0.3.0](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.3.0) (2024-11-14)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.3.0a1...0.3.0)

## [0.3.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.3.0a1) (2024-11-14)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.2.1...0.3.0a1)

## [0.2.1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.2.1) (2024-11-13)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.2.1a1...0.2.1)

## [0.2.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.2.1a1) (2024-11-13)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.2.0...0.2.1a1)

## [0.2.0](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.2.0) (2024-11-13)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.2.0a1...0.2.0)

## [0.2.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.2.0a1) (2024-11-13)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.1.0...0.2.0a1)

## [0.1.0](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.1.0) (2024-11-11)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.1.0a1...0.1.0)

## [0.1.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.1.0a1) (2024-11-11)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.0.4...0.1.0a1)

## [0.0.4](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.0.4) (2024-11-11)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.0.4a1...0.0.4)

## [0.0.4a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.0.4a1) (2024-11-11)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.0.3...0.0.4a1)

## [0.0.3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.0.3) (2024-11-11)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.0.3a1...0.0.3)

## [0.0.3a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.0.3a1) (2024-11-11)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.0.2...0.0.3a1)

## [0.0.2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.0.2) (2024-11-11)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.0.2a1...0.0.2)

## [0.0.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.0.2a1) (2024-11-11)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.0.1...0.0.2a1)

## [0.0.1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.0.1) (2024-11-07)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.0.1a2...0.0.1)

## [0.0.1a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.0.1a2) (2024-11-07)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/8c7f8b9ec6500133f19b6af33196beeb1c57aa3b...0.0.1a2)



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
