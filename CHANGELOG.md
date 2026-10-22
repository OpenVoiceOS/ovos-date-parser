# Changelog

## [0.34.8a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.34.8a1) (2026-10-22)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.34.7a1...0.34.8a1)

**Closed issues:**

- pt-PT: "31 de novembro" parses as the anchor day, expected None [\#504](https://github.com/OpenVoiceOS/ovos-date-parser/issues/504)
- pt-PT: "sexta-feira da semana que vem" parses as 23 October on a Monday, expected 30 October [\#503](https://github.com/OpenVoiceOS/ovos-date-parser/issues/503)
- pt-PT: "daqui a uma semana e dois dias" returns None, expected 26 October [\#483](https://github.com/OpenVoiceOS/ovos-date-parser/issues/483)
- pt-PT: "sexta-feira daqui a duas semanas" parses as 23 October, expected 30 October \(word order changes the answer\) [\#482](https://github.com/OpenVoiceOS/ovos-date-parser/issues/482)
- pt-PT: "o dia 5 do mês que vem" parses as 22 March 2027, expected 5 November 2026 [\#481](https://github.com/OpenVoiceOS/ovos-date-parser/issues/481)
- pt-PT: "a segunda semana de outubro" parses as the anchor day, expected the Monday that starts that week [\#475](https://github.com/OpenVoiceOS/ovos-date-parser/issues/475)
- pt-PT: "a próxima semana" leaves the article "a" in the remainder [\#470](https://github.com/OpenVoiceOS/ovos-date-parser/issues/470)
- pt-PT: "o primeiro dia do mês" returns None, expected 1 November [\#469](https://github.com/OpenVoiceOS/ovos-date-parser/issues/469)
- pt-PT: "a segunda opção" parses as Monday 19 October, expected None \(ordinal read as weekday\) [\#468](https://github.com/OpenVoiceOS/ovos-date-parser/issues/468)
- pt-PT: "o último dia do mês" returns None, expected 31 October [\#463](https://github.com/OpenVoiceOS/ovos-date-parser/issues/463)
- pt-PT: "a última sexta-feira de novembro" parses as 23 October, expected 27 November [\#462](https://github.com/OpenVoiceOS/ovos-date-parser/issues/462)
- pt-PT: "próximo sábado" said on a Saturday parses as today, expected 24 October [\#461](https://github.com/OpenVoiceOS/ovos-date-parser/issues/461)
- pt-PT: "sexta-feira passada" parses as 23 October, expected 16 October [\#460](https://github.com/OpenVoiceOS/ovos-date-parser/issues/460)
- pt-PT: "a última sexta-feira do mês" parses as 16 October, expected 30 October [\#448](https://github.com/OpenVoiceOS/ovos-date-parser/issues/448)
- pt-PT: "o último mês" returns None, expected 17 September 2026 \("último" with accent is not recognised\) [\#447](https://github.com/OpenVoiceOS/ovos-date-parser/issues/447)
- pt-PT: "o mês que vem" returns None, expected 17 November 2026 [\#446](https://github.com/OpenVoiceOS/ovos-date-parser/issues/446)
- pt-PT: "o mês passado" parses as 17 March 2026, expected 17 September 2026 [\#445](https://github.com/OpenVoiceOS/ovos-date-parser/issues/445)
- pt-PT: "no próximo mês" parses as 17 May 2027, expected 17 November 2026 [\#444](https://github.com/OpenVoiceOS/ovos-date-parser/issues/444)
- pt-PT: "depois de amanhã segunda-feira" parses as 14 October, expected 19 October [\#405](https://github.com/OpenVoiceOS/ovos-date-parser/issues/405)
- pt-PT: "é daqui a uma semana sábado" parses as today, expected 24 October [\#400](https://github.com/OpenVoiceOS/ovos-date-parser/issues/400)

**Merged pull requests:**

- fix\(pt\): resolve weekdays after relative days and periods, parse spelled counts [\#409](https://github.com/OpenVoiceOS/ovos-date-parser/pull/409) ([JarbasAl](https://github.com/JarbasAl))

## [0.34.7a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.34.7a1) (2026-10-22)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.34.6a1...0.34.7a1)

**Closed issues:**

- en-US: "after july 4th" returns today at 16:00, expected 4 July 2027 [\#484](https://github.com/OpenVoiceOS/ovos-date-parser/issues/484)
- en-US: "july fourth" parses as 1 July 2027, expected 4 July 2027 [\#422](https://github.com/OpenVoiceOS/ovos-date-parser/issues/422)
- en-US: "the fourth of july" parses as 1 July 2027, expected 4 July 2027 [\#404](https://github.com/OpenVoiceOS/ovos-date-parser/issues/404)
- en-US: "the first of the month" returns None, expected 1 November [\#403](https://github.com/OpenVoiceOS/ovos-date-parser/issues/403)
- en-US: "the last day of the month" parses as yesterday, expected 31 October [\#402](https://github.com/OpenVoiceOS/ovos-date-parser/issues/402)

**Merged pull requests:**

- fix\(en\): read "the fourth of july", "july fourth", "the first of the month" and "the last day of the month" [\#411](https://github.com/OpenVoiceOS/ovos-date-parser/pull/411) ([JarbasAl](https://github.com/JarbasAl))

## [0.34.6a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.34.6a1) (2026-10-22)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.34.5a1...0.34.6a1)

**Closed issues:**

- it-IT: "stasera alle 9 in 4" parses as 16:00, expected 21:00 [\#507](https://github.com/OpenVoiceOS/ovos-date-parser/issues/507)
- it-IT: "ne voglio 3" parses as 15:00, expected no date [\#506](https://github.com/OpenVoiceOS/ovos-date-parser/issues/506)
- it-IT: "siamo in 10" parses as 22:00, expected no date [\#505](https://github.com/OpenVoiceOS/ovos-date-parser/issues/505)
- it-IT: "dal 10 al 15 marzo" raises IndexError, expected no error [\#494](https://github.com/OpenVoiceOS/ovos-date-parser/issues/494)
- it-IT: "alle 0 meno 10" parses as 18 October 22:00, expected 17 October 23:50 [\#493](https://github.com/OpenVoiceOS/ovos-date-parser/issues/493)
- it-IT: "quanto fa 5 meno 2" parses as 14:00, expected no date [\#492](https://github.com/OpenVoiceOS/ovos-date-parser/issues/492)
- it-IT: "due giorni fa" parses as 14:00, expected 15 October [\#491](https://github.com/OpenVoiceOS/ovos-date-parser/issues/491)
- it-IT: "tre ore fa" parses as 15:00, expected 09:00 [\#490](https://github.com/OpenVoiceOS/ovos-date-parser/issues/490)
- it-IT: "tra un quarto d'ora" returns None, expected 12:15 [\#480](https://github.com/OpenVoiceOS/ovos-date-parser/issues/480)
- it-IT: "tre quarti" raises ValueError, expected None [\#479](https://github.com/OpenVoiceOS/ovos-date-parser/issues/479)
- it-IT: "alle tre meno dieci" parses as 22:00, expected 14:50 [\#478](https://github.com/OpenVoiceOS/ovos-date-parser/issues/478)
- it-IT: "alle tre e venti" parses as 20:00, expected 15:20 [\#477](https://github.com/OpenVoiceOS/ovos-date-parser/issues/477)
- it-IT: "alle tre e un quarto" parses as 15:00, expected 15:15 [\#476](https://github.com/OpenVoiceOS/ovos-date-parser/issues/476)
- it-IT: "compra tre pani domani" parses as 03:00, expected no time of day [\#474](https://github.com/OpenVoiceOS/ovos-date-parser/issues/474)
- it-IT: "è tardi" raises TypeError, expected None [\#467](https://github.com/OpenVoiceOS/ovos-date-parser/issues/467)

**Merged pull requests:**

- fix\(it\): read minutes around an hour, "fa" after a duration, and do not raise [\#472](https://github.com/OpenVoiceOS/ovos-date-parser/pull/472) ([JarbasAl](https://github.com/JarbasAl))

## [0.34.5a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.34.5a1) (2026-10-22)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.34.4a1...0.34.5a1)

## [0.34.4a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.34.4a1) (2026-10-22)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.34.3a1...0.34.4a1)

**Closed issues:**

- es-ES: "mañana a las 22:30" parses as today 22:30, expected tomorrow 22:30 [\#488](https://github.com/OpenVoiceOS/ovos-date-parser/issues/488)
- es-ES: "mañana a las 10:30" raises TypeError, expected 18 October 10:30 [\#487](https://github.com/OpenVoiceOS/ovos-date-parser/issues/487)
- de-DE: "ein Tag vor morgen" parses as tomorrow, expected today [\#458](https://github.com/OpenVoiceOS/ovos-date-parser/issues/458)
- es-ES: "el viernes de la semana pasada" parses as 10 October, expected 9 October [\#427](https://github.com/OpenVoiceOS/ovos-date-parser/issues/427)
- es-ES: "la semana que viene" returns None, expected 24 October [\#413](https://github.com/OpenVoiceOS/ovos-date-parser/issues/413)
- es-ES: "el viernes pasado" parses as 23 October, expected 16 October [\#412](https://github.com/OpenVoiceOS/ovos-date-parser/issues/412)
- es-ES: "el siguiente viernes" parses as 30 October, expected 23 October [\#401](https://github.com/OpenVoiceOS/ovos-date-parser/issues/401)
- nl-NL: "de dag na vandaag" parses as today, expected tomorrow [\#399](https://github.com/OpenVoiceOS/ovos-date-parser/issues/399)
- de-DE: "der tag nach morgen" parses as tomorrow, expected the day after tomorrow [\#398](https://github.com/OpenVoiceOS/ovos-date-parser/issues/398)

**Merged pull requests:**

- fix\(de,nl\): parse "der Tag nach morgen" and "de dag na vandaag" as the day after [\#410](https://github.com/OpenVoiceOS/ovos-date-parser/pull/410) ([JarbasAl](https://github.com/JarbasAl))
- fix\(es\): read "siguiente", "pasado" and "que viene" around weekdays and weeks [\#408](https://github.com/OpenVoiceOS/ovos-date-parser/pull/408) ([JarbasAl](https://github.com/JarbasAl))

## [0.34.3a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.34.3a1) (2026-10-22)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.34.2a1...0.34.3a1)

**Closed issues:**

- nl-NL: a number that is not a time moves the result to tomorrow \("3 mensen 4 uur"\) [\#508](https://github.com/OpenVoiceOS/ovos-date-parser/issues/508)
- nl-NL: "morgen om 10, want vanavond kan ik niet" parses as 19:00, expected 10:00 [\#502](https://github.com/OpenVoiceOS/ovos-date-parser/issues/502)
- nl-NL: "om kwart over half 9" parses as 21:00, expected 20:45 [\#501](https://github.com/OpenVoiceOS/ovos-date-parser/issues/501)
- nl-NL: "om 25 uur" parses as a time, expected none [\#486](https://github.com/OpenVoiceOS/ovos-date-parser/issues/486)
- nl-NL: "om tien over half drie" returns None, expected 14:40 [\#485](https://github.com/OpenVoiceOS/ovos-date-parser/issues/485)
- nl-NL: "om half 9" parses as 21:00, expected 20:30 \(half, kwart over, kwart voor not read\) [\#471](https://github.com/OpenVoiceOS/ovos-date-parser/issues/471)
- nl-NL: "om 7 aan de afspraak" drops the hour when a word follows [\#457](https://github.com/OpenVoiceOS/ovos-date-parser/issues/457)
- nl-NL: a day-part word in an earlier clause overrides "morgen om 9" [\#456](https://github.com/OpenVoiceOS/ovos-date-parser/issues/456)
- nl-NL: spelled-out numbers before a unit are not read \("om tien uur" parses as 13:00\) [\#455](https://github.com/OpenVoiceOS/ovos-date-parser/issues/455)
- nl-NL: "3 uur geleden" parses as 15:00, expected 09:00 \(hours, minutes and seconds ago are added\) [\#454](https://github.com/OpenVoiceOS/ovos-date-parser/issues/454)
- nl-NL: "om 0:00" parses as 12:00 today, expected the next midnight [\#443](https://github.com/OpenVoiceOS/ovos-date-parser/issues/443)
- nl-NL: "om 21:00" returns None once the anchor has reached 21:00, expected the next 21:00 [\#442](https://github.com/OpenVoiceOS/ovos-date-parser/issues/442)
- nl-NL: "vanavond om 9:00" parses as tomorrow 09:00 after 21:00, expected today 21:00 \(evening word ignored for a bare hour\) [\#441](https://github.com/OpenVoiceOS/ovos-date-parser/issues/441)
- nl-NL: "vanochtend om 9:00" parses as 21:00, expected 09:00 \(morning word ignored for a bare hour\) [\#440](https://github.com/OpenVoiceOS/ovos-date-parser/issues/440)
- nl-NL: "vanmorgen" returns None, expected today 08:00 [\#437](https://github.com/OpenVoiceOS/ovos-date-parser/issues/437)
- nl-NL: "vanochtend" parses as tomorrow 08:00 after 08:00, expected today [\#436](https://github.com/OpenVoiceOS/ovos-date-parser/issues/436)
- nl-NL: "overmorgenavond" parses as today 19:00, expected 19 October 19:00 [\#426](https://github.com/OpenVoiceOS/ovos-date-parser/issues/426)
- nl-NL: "eergisteravond" parses as today 19:00, expected 15 October 19:00 [\#425](https://github.com/OpenVoiceOS/ovos-date-parser/issues/425)
- nl-NL: "gisteravond" parses as today 19:00, expected 16 October 19:00 [\#424](https://github.com/OpenVoiceOS/ovos-date-parser/issues/424)
- nl-NL: "morgen om 8 uur" parses as 20:00, expected 08:00 \("om N uur" read as "in N hours"\) [\#420](https://github.com/OpenVoiceOS/ovos-date-parser/issues/420)
- nl-NL: "gisteren" and "eergisteren" return None, expected 16 and 15 October [\#419](https://github.com/OpenVoiceOS/ovos-date-parser/issues/419)

**Merged pull requests:**

- fix\(nl\): parse "gisteren" and "eergisteren", and read "om N uur" as a clock time [\#423](https://github.com/OpenVoiceOS/ovos-date-parser/pull/423) ([JarbasAl](https://github.com/JarbasAl))

## [0.34.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.34.2a1) (2026-10-22)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.34.1a1...0.34.2a1)

**Closed issues:**

- es-ES: "reserva mañana el check-in" returns the remainder "reserva check in", expected "reserva check-in" [\#466](https://github.com/OpenVoiceOS/ovos-date-parser/issues/466)
- it-IT: "ricordami domani di comprare il pane perché" returns the remainder with "perche'", expected "perché" [\#465](https://github.com/OpenVoiceOS/ovos-date-parser/issues/465)
- pt-PT: "compra pão amanhã" returns the remainder "compra pao", expected "compra pão" [\#464](https://github.com/OpenVoiceOS/ovos-date-parser/issues/464)
- ast-ES: "recuérdame mañana mercar pan" returns the remainder "recuerdame mercar pan", expected "recuérdame mercar pan" [\#453](https://github.com/OpenVoiceOS/ovos-date-parser/issues/453)
- gl-ES: "recórdame mañá mercar pan" returns the remainder "recordame mercar pan", expected "recórdame mercar pan" [\#452](https://github.com/OpenVoiceOS/ovos-date-parser/issues/452)
- es-ES: "recuérdame mañana comprar pan" returns the remainder "recuerdame comprar pan", expected "recuérdame comprar pan" [\#451](https://github.com/OpenVoiceOS/ovos-date-parser/issues/451)

**Merged pull requests:**

- fix\(es,gl,ast,pt,it\): keep the user's words in the remainder [\#459](https://github.com/OpenVoiceOS/ovos-date-parser/pull/459) ([JarbasAl](https://github.com/JarbasAl))
- fix\(fr\): read an unaccented "a" before an hour as "à" [\#397](https://github.com/OpenVoiceOS/ovos-date-parser/pull/397) ([goldyfruit](https://github.com/goldyfruit))

## [0.34.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.34.1a1) (2026-10-08)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.34.0a1...0.34.1a1)

**Merged pull requests:**

- fix: nice\_duration accepts a timedelta in pl, ru, uk [\#391](https://github.com/OpenVoiceOS/ovos-date-parser/pull/391) ([openvoiceos-bot](https://github.com/openvoiceos-bot))
- fix\(ja\): read 次の金曜日 as the coming Friday, not the last one [\#390](https://github.com/OpenVoiceOS/ovos-date-parser/pull/390) ([goldyfruit](https://github.com/goldyfruit))

## [0.34.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.34.0a1) (2026-10-08)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.33.5a1...0.34.0a1)

## [0.33.5a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.33.5a1) (2026-10-08)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.33.4a1...0.33.5a1)

**Merged pull requests:**

- fix\(zh\): read a relative day written straight against 星期几 [\#389](https://github.com/OpenVoiceOS/ovos-date-parser/pull/389) ([goldyfruit](https://github.com/goldyfruit))
- fix\(fr\): a bare duration is not a clock time [\#384](https://github.com/OpenVoiceOS/ovos-date-parser/pull/384) ([openvoiceos-bot](https://github.com/openvoiceos-bot))

## [0.33.4a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.33.4a1) (2026-10-08)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.33.3a1...0.33.4a1)

**Merged pull requests:**

- fix: speak Basque years as words in nice\_year [\#387](https://github.com/OpenVoiceOS/ovos-date-parser/pull/387) ([openvoiceos-bot](https://github.com/openvoiceos-bot))

## [0.33.3a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.33.3a1) (2026-10-02)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.33.2a1...0.33.3a1)

**Merged pull requests:**

- fix\(kab\): keep compound cardinal intact in extract\_datetime\_kab [\#385](https://github.com/OpenVoiceOS/ovos-date-parser/pull/385) ([openvoiceos-bot](https://github.com/openvoiceos-bot))

## [0.33.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.33.2a1) (2026-09-28)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.33.1a1...0.33.2a1)

## [0.33.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.33.1a1) (2026-09-25)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.33.0a1...0.33.1a1)

## [0.33.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.33.0a1) (2026-09-25)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.32.3a1...0.33.0a1)

## [0.32.3a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.32.3a1) (2026-09-25)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.32.2a1...0.32.3a1)

## [0.32.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.32.2a1) (2026-09-25)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.32.1a1...0.32.2a1)

## [0.32.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.32.1a1) (2026-09-24)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.32.0a1...0.32.1a1)

## [0.32.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.32.0a1) (2026-09-23)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.5a9...0.32.0a1)

## [0.31.5a9](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.5a9) (2026-09-23)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.5a8...0.31.5a9)

## [0.31.5a8](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.5a8) (2026-09-23)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.5a7...0.31.5a8)

## [0.31.5a7](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.5a7) (2026-09-23)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.5a6...0.31.5a7)

## [0.31.5a6](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.5a6) (2026-09-23)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.5a5...0.31.5a6)

## [0.31.5a5](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.5a5) (2026-09-23)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.5a4...0.31.5a5)

## [0.31.5a4](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.5a4) (2026-09-23)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.5a3...0.31.5a4)

## [0.31.5a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.5a3) (2026-09-23)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.5a2...0.31.5a3)

## [0.31.5a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.5a2) (2026-09-23)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.5a1...0.31.5a2)

## [0.31.5a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.5a1) (2026-09-21)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.4a1...0.31.5a1)

## [0.31.4a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.4a1) (2026-09-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.3a7...0.31.4a1)

## [0.31.3a7](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.3a7) (2026-09-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.3a6...0.31.3a7)

## [0.31.3a6](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.3a6) (2026-09-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.3a5...0.31.3a6)

## [0.31.3a5](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.3a5) (2026-09-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.3a4...0.31.3a5)

## [0.31.3a4](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.3a4) (2026-09-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.3a3...0.31.3a4)

## [0.31.3a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.3a3) (2026-09-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.3a2...0.31.3a3)

## [0.31.3a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.3a2) (2026-09-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.3a1...0.31.3a2)

## [0.31.3a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.3a1) (2026-09-12)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.2a1...0.31.3a1)

## [0.31.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.2a1) (2026-09-11)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.1a3...0.31.2a1)

## [0.31.1a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.1a3) (2026-09-10)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.1a2...0.31.1a3)

## [0.31.1a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.1a2) (2026-09-10)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.1a1...0.31.1a2)

## [0.31.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.1a1) (2026-09-07)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.31.0a1...0.31.1a1)

## [0.31.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.31.0a1) (2026-09-06)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.30.3a1...0.31.0a1)

## [0.30.3a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.30.3a1) (2026-09-03)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.30.2a2...0.30.3a1)

## [0.30.2a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.30.2a2) (2026-09-02)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.30.2a1...0.30.2a2)

## [0.30.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.30.2a1) (2026-09-01)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.30.1a1...0.30.2a1)

## [0.30.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.30.1a1) (2026-09-01)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.30.0a1...0.30.1a1)

## [0.30.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.30.0a1) (2026-09-01)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.29.2a1...0.30.0a1)

## [0.29.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.29.2a1) (2026-09-01)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.29.1a1...0.29.2a1)

## [0.29.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.29.1a1) (2026-09-01)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.29.0...0.29.1a1)

## [0.29.0](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.29.0) (2026-07-21)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.29.0a1...0.29.0)

## [0.29.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.29.0a1) (2026-07-21)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.10a1...0.29.0a1)

## [0.28.10a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.10a1) (2026-07-21)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.9a1...0.28.10a1)

## [0.28.9a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.9a1) (2026-07-21)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.8a1...0.28.9a1)

## [0.28.8a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.8a1) (2026-07-21)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.7a1...0.28.8a1)

## [0.28.7a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.7a1) (2026-07-20)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.6a1...0.28.7a1)

## [0.28.6a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.6a1) (2026-07-20)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.5a1...0.28.6a1)

## [0.28.5a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.5a1) (2026-07-20)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.4a1...0.28.5a1)

## [0.28.4a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.4a1) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.3a1...0.28.4a1)

## [0.28.3a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.3a1) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.2a1...0.28.3a1)

## [0.28.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.2a1) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a22...0.28.2a1)

## [0.28.1a22](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a22) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a21...0.28.1a22)

## [0.28.1a21](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a21) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a20...0.28.1a21)

## [0.28.1a20](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a20) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a19...0.28.1a20)

## [0.28.1a19](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a19) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a18...0.28.1a19)

## [0.28.1a18](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a18) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a17...0.28.1a18)

## [0.28.1a17](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a17) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a16...0.28.1a17)

## [0.28.1a16](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a16) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a15...0.28.1a16)

## [0.28.1a15](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a15) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a14...0.28.1a15)

## [0.28.1a14](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a14) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a13...0.28.1a14)

## [0.28.1a13](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a13) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a12...0.28.1a13)

## [0.28.1a12](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a12) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a11...0.28.1a12)

## [0.28.1a11](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a11) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a10...0.28.1a11)

## [0.28.1a10](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a10) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a9...0.28.1a10)

## [0.28.1a9](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a9) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a8...0.28.1a9)

## [0.28.1a8](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a8) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a7...0.28.1a8)

## [0.28.1a7](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a7) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a6...0.28.1a7)

## [0.28.1a6](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a6) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a5...0.28.1a6)

## [0.28.1a5](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a5) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a4...0.28.1a5)

## [0.28.1a4](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a4) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a3...0.28.1a4)

## [0.28.1a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a3) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a2...0.28.1a3)

## [0.28.1a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a2) (2026-07-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.1a1...0.28.1a2)

## [0.28.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.1a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.28.0a1...0.28.1a1)

## [0.28.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.28.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.27.1a1...0.28.0a1)

## [0.27.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.27.1a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.27.0a1...0.27.1a1)

## [0.27.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.27.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.26.0a1...0.27.0a1)

## [0.26.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.26.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.25.0a1...0.26.0a1)

## [0.25.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.25.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.24.0a1...0.25.0a1)

## [0.24.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.24.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.23.1a1...0.24.0a1)

## [0.23.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.23.1a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.23.0a1...0.23.1a1)

## [0.23.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.23.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.22.0a1...0.23.0a1)

## [0.22.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.22.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.21.0a1...0.22.0a1)

## [0.21.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.21.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.20.0a1...0.21.0a1)

## [0.20.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.20.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.19.0a1...0.20.0a1)

## [0.19.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.19.0a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.18.1a3...0.19.0a1)

## [0.18.1a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.18.1a3) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.18.1a2...0.18.1a3)

## [0.18.1a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.18.1a2) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.18.1a1...0.18.1a2)

## [0.18.1a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.18.1a1) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.18.0a3...0.18.1a1)

## [0.18.0a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.18.0a3) (2026-07-17)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.18.0a1...0.18.0a3)

## [0.18.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.18.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.17.0a1...0.18.0a1)

## [0.17.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.17.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.16.0a1...0.17.0a1)

## [0.16.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.16.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.15.0a2...0.16.0a1)

## [0.15.0a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.15.0a2) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.15.0a1...0.15.0a2)

## [0.15.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.15.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.14.0a1...0.15.0a1)

## [0.14.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.14.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.13.0a2...0.14.0a1)

## [0.13.0a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.13.0a2) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.13.0a1...0.13.0a2)

## [0.13.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.13.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.12.0a1...0.13.0a1)

## [0.12.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.12.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.11.0a5...0.12.0a1)

## [0.11.0a5](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.11.0a5) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.11.0a4...0.11.0a5)

## [0.11.0a4](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.11.0a4) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.11.0a3...0.11.0a4)

## [0.11.0a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.11.0a3) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.11.0a2...0.11.0a3)

## [0.11.0a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.11.0a2) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.11.0a1...0.11.0a2)

## [0.11.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.11.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.10.0a1...0.11.0a1)

## [0.10.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.10.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.9.0a1...0.10.0a1)

## [0.9.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.9.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.8.0a1...0.9.0a1)

## [0.8.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.8.0a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.2a1...0.8.0a1)

## [0.7.2a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.2a1) (2026-07-16)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.0a5...0.7.2a1)

## [0.7.0a5](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.0a5) (2025-12-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.0a4...0.7.0a5)

## [0.7.0a4](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.0a4) (2025-12-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.0a3...0.7.0a4)

## [0.7.0a3](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.0a3) (2025-12-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.0a2...0.7.0a3)

## [0.7.0a2](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.0a2) (2025-12-18)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.7.0a1...0.7.0a2)

## [0.7.0a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.7.0a1) (2025-08-04)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.5...0.7.0a1)

## [0.6.5](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.5) (2025-08-04)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.5a1...0.6.5)

## [0.6.5a1](https://github.com/OpenVoiceOS/ovos-date-parser/tree/0.6.5a1) (2025-08-04)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-date-parser/compare/0.6.4...0.6.5a1)

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
