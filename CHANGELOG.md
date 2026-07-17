# Changelog

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

**Closed issues:**

- Typo in French month name for October in  [\#14](https://github.com/OpenVoiceOS/ovos-date-parser/issues/14)

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



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
