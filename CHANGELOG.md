# Changelog

## [0.31.1a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.1a3) (2026-09-10)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.1a2...0.31.1a3)

**Merged pull requests:**

- ci: run build, coverage and license checks through gh-automations at @dev [\#323](https://github.com/OpenVoiceOS/ovos-date-parser/pull/323) ([openvoiceos-bot](https://github.com/openvoiceos-bot))

## [0.31.1a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.1a2) (2026-09-10)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.1a1...0.31.1a2)

**Merged pull requests:**

- fix\(de\): 'letztes Jahr' \(last year\) never resolved - dead duplicate elif [\#321](https://github.com/OpenVoiceOS/ovos-date-parser/pull/321) ([andlo](https://github.com/andlo))
- fix\(da\): several extract\_datetime bugs, crashes, and add idiomatic quarter/half hours [\#320](https://github.com/OpenVoiceOS/ovos-date-parser/pull/320) ([andlo](https://github.com/andlo))
- docs: what a relative week, month, year or weekday names [\#318](https://github.com/OpenVoiceOS/ovos-date-parser/pull/318) ([JarbasAl](https://github.com/JarbasAl))

## [0.31.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.1a1) (2026-09-07)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.0a1...0.31.1a1)

**Closed issues:**

- es/pt/de share the space-separated meridiem defect; es crashes [\#312](https://github.com/OpenVoiceOS/ovos-date-parser/issues/312)

**Merged pull requests:**

- fix: crash and unconverted hour in es/pt space-separated meridiem \(\#312\) [\#317](https://github.com/OpenVoiceOS/ovos-date-parser/pull/317) ([JarbasAl](https://github.com/JarbasAl))

## [0.31.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.0a1) (2026-09-06)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.30.3a1...0.31.0a1)

**Merged pull requests:**

- feat: extract\_datetime\_spans and extract\_duration\_spans return code-point spans [\#314](https://github.com/OpenVoiceOS/ovos-date-parser/pull/314) ([JarbasAl](https://github.com/JarbasAl))

## [0.30.3a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.30.3a1) (2026-09-03)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.30.2a2...0.30.3a1)

**Closed issues:**

- Space-separated "H MM am/pm" times skip 12→24h conversion [\#310](https://github.com/OpenVoiceOS/ovos-date-parser/issues/310)

**Merged pull requests:**

- fix: 12h to 24h conversion for space-separated "H MM meridiem" clock forms [\#311](https://github.com/OpenVoiceOS/ovos-date-parser/pull/311) ([JarbasAl](https://github.com/JarbasAl))

## [0.30.2a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.30.2a2) (2026-09-02)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.30.2a1...0.30.2a2)

**Merged pull requests:**

- chore: pin chronologia 0.27.7a1 and promote the BC-day round-trips [\#308](https://github.com/OpenVoiceOS/ovos-date-parser/pull/308) ([JarbasAl](https://github.com/JarbasAl))

## [0.30.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.30.2a1) (2026-09-01)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.30.1a1...0.30.2a1)

**Merged pull requests:**

- fix: strip dangling conjunctions from extract\_duration remainder [\#293](https://github.com/OpenVoiceOS/ovos-date-parser/pull/293) ([JarbasAl](https://github.com/JarbasAl))

## [0.30.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.30.1a1) (2026-09-01)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.30.0a1...0.30.1a1)

**Merged pull requests:**

- fix: restore nice\_date\_an forms pinned by the tests [\#305](https://github.com/OpenVoiceOS/ovos-date-parser/pull/305) ([JarbasAl](https://github.com/JarbasAl))

## [0.30.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.30.0a1) (2026-09-01)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.29.2a1...0.30.0a1)

**Merged pull requests:**

- feat: declarative datetime engine with chronologia reckoning core [\#284](https://github.com/OpenVoiceOS/ovos-date-parser/pull/284) ([JarbasAl](https://github.com/JarbasAl))

## [0.29.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.29.2a1) (2026-09-01)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.29.1a1...0.29.2a1)

## [0.29.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.29.1a1) (2026-09-01)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.29.0...0.29.1a1)

**Closed issues:**

- Declarative datetime engine: design and 1.0.0 roadmap [\#291](https://github.com/OpenVoiceOS/ovos-date-parser/issues/291)

**Merged pull requests:**

- fix: remove committed diff marker from dates\_an.py [\#301](https://github.com/OpenVoiceOS/ovos-date-parser/pull/301) ([JarbasAl](https://github.com/JarbasAl))
- docs: rewrite README in Simplified Technical English [\#299](https://github.com/OpenVoiceOS/ovos-date-parser/pull/299) ([JarbasAl](https://github.com/JarbasAl))
- Improved kabyle data [\#295](https://github.com/OpenVoiceOS/ovos-date-parser/pull/295) ([athmanemokraoui](https://github.com/athmanemokraoui))
- Refine duration parser regex and correct typos [\#294](https://github.com/OpenVoiceOS/ovos-date-parser/pull/294) ([Juanpabl](https://github.com/Juanpabl))
- Change Aragonese date parser with improved synonyms and tests [\#292](https://github.com/OpenVoiceOS/ovos-date-parser/pull/292) ([Juanpabl](https://github.com/Juanpabl))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
