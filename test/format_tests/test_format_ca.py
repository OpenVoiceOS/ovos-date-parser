#
# Copyright 2019 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
import unittest

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    nice_time
)
from ovos_date_parser.dates_ca import TimeVariantCA


class TestNiceDateFormat(unittest.TestCase):
    def test_pm(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt, lang="ca"), "la una i vint-i-dos")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "la una i vint-i-dos de la tarda")
        self.assertEqual(nice_time(dt, lang="ca", speech=False), "1:22")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "1:22 PM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "13:22")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True, use_ampm=True), "13:22")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les tretze i vint-i-dos")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les tretze i vint-i-dos")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca"), "la una en punt")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "la una en punt de la tarda")
        self.assertEqual(nice_time(dt, lang="ca", speech=False), "1:00")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "1:00 PM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "13:00")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True, use_ampm=True), "13:00")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les tretze")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True),
                         "les tretze i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "la una i dos de la tarda")
        self.assertEqual(nice_time(dt, lang="ca", speech=False), "1:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "1:02 PM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "13:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True, use_ampm=True), "13:02")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les tretze i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les tretze i dos")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 0, tzinfo=default_timezone())
        # Default Watch system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les dotze i quinze")
        # Spanish-like time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.SPANISH_LIKE),
                         "les dotze i quart")
        # Catalan Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant=TimeVariantCA.BELL),
                         "un quart d'una de la tarda")
        # Catalan Full Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant=TimeVariantCA.BELL),
                         "un quart d'una de la tarda")

        dt = datetime.datetime(2017, 1, 31,
                               00, 14, 0, tzinfo=default_timezone())
        # Default Watch system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les zero i catorze")
        # Spanish-like time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.SPANISH_LIKE),
                         "les dotze i catorze")
        # Catalan Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant=TimeVariantCA.BELL),
                         "les dotze i catorze minuts de la nit")
        # Catalan Full Bell time system: 00:31
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.FULL_BELL),
                         "un quart d'una de la matinada")
        # Catalan Full Bell time system: 16:31                 
        dt = datetime.datetime(2017, 1, 31,
                               16, 31, 0, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.FULL_BELL),
                         "dos quarts de cinc de la tarda")
        # Catalan Full Bell time system: 5:32                 
        dt = datetime.datetime(2017, 1, 31,
                               5, 32, 0, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.FULL_BELL),
                         "dos quarts tocats de sis del matí")
        # Catalan Full Bell time system: 19:19                 
        dt = datetime.datetime(2017, 1, 31,
                               19, 19, 0, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.FULL_BELL),
                         "un quart tocat de vuit del vespre")

    def test_midnight(self):
        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca"),
                         "les dotze i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "les dotze i dos de la nit")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True),
                         "les zero i dos")
        self.assertEqual(nice_time(dt, lang="ca", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "12:02 AM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "00:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True,
                                   use_ampm=True), "00:02")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les zero i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les zero i dos")

    def test_midday(self):
        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les dotze i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es", use_ampm=True),
                         "les dotze i quinze del migdia")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=True),
                         "les dotze i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=False),
                         "les dotze i quinze")

    def test_minutes_to_hour(self):
        # "twenty minutes to midnight"
        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les set i quaranta")
        self.assertEqual(nice_time(dt, lang="ca-es", use_ampm=True),
                         "les set i quaranta del vespre")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False),
                         "7:40")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_ampm=True),
                         "7:40 PM")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=True),
                         "les dinou i quaranta")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=False),
                         "les dinou i quaranta")

    def test_minutes_past_hour(self):
        # "quarter past ten"
        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True),
                         "la una i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "la una i quinze")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "la una i trenta-cinc")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "la una i quaranta-cinc")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les quatre i cinquanta")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les cinc i cinquanta-cinc")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es", use_ampm=True),
                         "les cinc i trenta de la matinada")

        dt = datetime.datetime(2017, 1, 31,
                               23, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=True),
                         "les vint-i-tres i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=False,
                                   use_ampm=True),
                         "les onze i quinze de la nit")

    def test_variant_strings(self):
        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 0, tzinfo=default_timezone())
        # Default variant
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant="default"),
                         "les dotze i quinze")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False),
                         "les dotze i quinze")

        dt = datetime.datetime(2017, 1, 31,
                               00, 14, 0, tzinfo=default_timezone())
        # Spanish-like time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.SPANISH_LIKE),
                         "les dotze i catorze")
        # Catalan Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant=TimeVariantCA.BELL),
                         "les dotze i catorze minuts de la nit")

        # Catalan Full Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.FULL_BELL),
                         "un quart d'una de la matinada")

    # --- register-split anchor tests -------------------------------------
    # Catalan tells time in two well-known registers:
    #   * "standard"/central:  les quatre i quart / i mitja / menys quart
    #   * traditional "quarts": quarters counted toward the NEXT hour,
    #     un quart de cinc (4:15), dos quarts de cinc (4:30),
    #     tres quarts de cinc (4:45)
    # Sources: IEC grammar; Optimot fitxa "Les hores"; Wikipedia
    # "Catalan time system". Expected forms below are the reference idiom,
    # never pinned from engine output.

    # de-<next hour> phrase as it surfaces (with elision before a vowel)
    _NEXT_HOUR_DE = {
        1: "d'una", 2: "de dues", 3: "de tres", 4: "de quatre",
        5: "de cinc", 6: "de sis", 7: "de set", 8: "de vuit",
        9: "de nou", 10: "de deu", 11: "d'onze", 12: "de dotze",
    }

    def test_quarts_full_clock(self):
        # For every hour of the 12h clock, each quarter is counted toward the
        # NEXT hour: un quart / dos quarts / tres quarts de <next hour>.
        for h in range(1, 13):
            nxt = (h % 12) + 1
            de = self._NEXT_HOUR_DE[nxt]
            for minute, count in ((15, "un quart"),
                                  (30, "dos quarts"),
                                  (45, "tres quarts")):
                dt = datetime.datetime(2017, 1, 31, h, minute,
                                       tzinfo=default_timezone())
                out = nice_time(dt, lang="ca", use_24hour=True,
                                variant="quarts")
                self.assertTrue(
                    out.startswith(f"{count} {de}"),
                    f"{h:02d}:{minute:02d} quarts -> {out!r} "
                    f"expected to start with {count!r} {de!r}")

    def test_quarts_on_the_hour_and_loose_minutes(self):
        # On the hour: plain "les X en punt". Loose minutes still hang off the
        # quart already begun ("un quart i cinc minuts de ...").
        dt = datetime.datetime(2017, 1, 31, 4, 0, tzinfo=default_timezone())
        self.assertTrue(
            nice_time(dt, lang="ca", use_24hour=True,
                      variant="quarts").startswith("les quatre en punt"))
        dt = datetime.datetime(2017, 1, 31, 4, 20, tzinfo=default_timezone())
        self.assertTrue(
            nice_time(dt, lang="ca", use_24hour=True,
                      variant="quarts").startswith("un quart i cinc minuts de cinc"))

    def test_standard_full_clock(self):
        # Central/standard register: i quart (:15), i mitja (:30),
        # menys quart (:45), plain "i <n>" for loose minutes.
        cases = {15: " i quart", 30: " i mitja", 45: "menys quart",
                 20: " i vint"}
        for h in range(1, 13):
            for minute, suffix in cases.items():
                dt = datetime.datetime(2017, 1, 31, h, minute,
                                       tzinfo=default_timezone())
                out = nice_time(dt, lang="ca", use_24hour=True,
                                variant="standard")
                self.assertTrue(
                    out.endswith(suffix),
                    f"{h:02d}:{minute:02d} standard -> {out!r} "
                    f"expected to end with {suffix!r}")

    def test_standard_reference_anchors(self):
        # Exact reference forms for the canonical example hour (4 -> 5).
        anchors = {
            15: "les quatre i quart",
            30: "les quatre i mitja",
            45: "les cinc menys quart",
        }
        for minute, expected in anchors.items():
            dt = datetime.datetime(2017, 1, 31, 4, minute,
                                   tzinfo=default_timezone())
            self.assertEqual(
                nice_time(dt, lang="ca", use_24hour=True, variant="standard"),
                expected)

    def test_quarts_reference_anchors(self):
        # Exact reference forms for the canonical example hour (-> 5).
        anchors = {
            15: "un quart de cinc",
            30: "dos quarts de cinc",
            45: "tres quarts de cinc",
        }
        for minute, expected in anchors.items():
            dt = datetime.datetime(2017, 1, 31, 4, minute,
                                   tzinfo=default_timezone())
            self.assertEqual(
                nice_time(dt, lang="ca", use_24hour=True, variant="quarts"),
                expected)

    def test_alias_case_insensitive_and_enum_names(self):
        dt = datetime.datetime(2017, 1, 31, 4, 30, tzinfo=default_timezone())
        # aliases resolve regardless of case / surrounding whitespace
        self.assertEqual(
            nice_time(dt, lang="ca", use_24hour=True, variant="QUARTS"),
            nice_time(dt, lang="ca", use_24hour=True,
                      variant=TimeVariantCA.BELL))
        self.assertEqual(
            nice_time(dt, lang="ca", use_24hour=True, variant="  Standard "),
            nice_time(dt, lang="ca", use_24hour=True,
                      variant=TimeVariantCA.SPANISH_LIKE))
        # exact enum member names are also accepted as strings
        self.assertEqual(
            nice_time(dt, lang="ca", use_24hour=True, variant="FULL_BELL"),
            nice_time(dt, lang="ca", use_24hour=True,
                      variant=TimeVariantCA.FULL_BELL))

    def test_unknown_variant_falls_back_to_default(self):
        # Adversarial: garbage variants must not raise and must reproduce the
        # default watch-time register.
        for h in range(0, 24):
            for minute in (0, 15, 30, 45, 7, 59):
                dt = datetime.datetime(2017, 1, 31, h, minute,
                                       tzinfo=default_timezone())
                baseline = nice_time(dt, lang="ca", use_24hour=True)
                for bad in ("invalid", "bad_VARIANT", "", "quart", None, 99, -1):
                    self.assertEqual(
                        nice_time(dt, lang="ca", use_24hour=True, variant=bad),
                        baseline,
                        f"variant={bad!r} at {h:02d}:{minute:02d} "
                        f"should fall back to default")

    def test_default_backcompat_identical(self):
        # Back-compat: the default output (no variant) is byte-identical to an
        # explicit DEFAULT enum and to the "default"/"watch" aliases, for every
        # minute of the clock and across the flag matrix.
        for h in range(0, 24):
            for minute in range(0, 60, 3):
                dt = datetime.datetime(2017, 1, 31, h, minute,
                                       tzinfo=default_timezone())
                for u24 in (True, False):
                    for ampm in (True, False):
                        base = nice_time(dt, lang="ca", use_24hour=u24,
                                         use_ampm=ampm)
                        for eq in (TimeVariantCA.DEFAULT, "default", "watch"):
                            self.assertEqual(
                                nice_time(dt, lang="ca", use_24hour=u24,
                                          use_ampm=ampm, variant=eq),
                                base)


    # --- real natural-sentence suite -------------------------------------
    # Each case is a full utterance a native speaker would say, with the
    # copula ("Són" plural / "És" singular) that Catalan grammar requires, and
    # the correct part-of-day tail. The engine's time phrase must complete the
    # sentence exactly. Sentences are drawn from IEC "Gramàtica de la llengua
    # catalana" (les hores) and the Optimot fitxa "Les hores"; day-period
    # boundaries follow the same references. Never pinned from engine output.
    #
    # tuple: (hour, minute, variant, copula, natural_sentence)

    NATURAL_SENTENCES = [
        # -- quarts register: quarters counted toward the NEXT hour ---------
        # morning (del matí)
        (6, 15, "quarts", "És", "És un quart de set del matí"),
        (6, 30, "quarts", "Són", "Són dos quarts de set del matí"),
        (6, 45, "quarts", "Són", "Són tres quarts de set del matí"),
        (7, 45, "quarts", "Són", "Són tres quarts de vuit del matí"),
        (8, 15, "quarts", "És", "És un quart de nou del matí"),
        (9, 30, "quarts", "Són", "Són dos quarts de deu del matí"),
        # elision d' before onze
        (10, 15, "quarts", "És", "És un quart d'onze del matí"),
        (10, 45, "quarts", "Són", "Són tres quarts d'onze del matí"),
        (22, 30, "quarts", "Són", "Són dos quarts d'onze de la nit"),
        # midday (del migdia)
        (11, 15, "quarts", "És", "És un quart de dotze del migdia"),
        # elision d' before una
        (12, 15, "quarts", "És", "És un quart d'una de la tarda"),
        (12, 45, "quarts", "Són", "Són tres quarts d'una de la tarda"),
        # afternoon (de la tarda)
        (15, 30, "quarts", "Són", "Són dos quarts de quatre de la tarda"),
        (16, 15, "quarts", "És", "És un quart de cinc de la tarda"),
        (17, 45, "quarts", "Són", "Són tres quarts de sis de la tarda"),
        # evening (del vespre)
        (18, 15, "quarts", "És", "És un quart de set del vespre"),
        (19, 30, "quarts", "Són", "Són dos quarts de vuit del vespre"),
        # night (de la nit)
        (21, 45, "quarts", "Són", "Són tres quarts de deu de la nit"),
        (23, 15, "quarts", "És", "És un quart de dotze de la nit"),
        (1, 15, "quarts", "És", "És un quart de dues de la nit"),

        # -- central/standard register: i quart / i mitja / menys quart -----
        (1, 15, "standard", "És", "És la una i quart"),
        (1, 30, "standard", "És", "És la una i mitja"),
        (3, 15, "standard", "Són", "Són les tres i quart"),
        (3, 30, "standard", "Són", "Són les tres i mitja"),
        (3, 45, "standard", "Són", "Són les quatre menys quart"),
        (4, 15, "standard", "Són", "Són les quatre i quart"),
        (4, 30, "standard", "Són", "Són les quatre i mitja"),
        (4, 45, "standard", "Són", "Són les cinc menys quart"),
        (5, 45, "standard", "Són", "Són les sis menys quart"),
        (6, 15, "standard", "Són", "Són les sis i quart"),
        (7, 20, "standard", "Són", "Són les set i vint"),
        (8, 30, "standard", "Són", "Són les vuit i mitja"),
        (9, 45, "standard", "Són", "Són les deu menys quart"),
        (10, 15, "standard", "Són", "Són les deu i quart"),
        (11, 30, "standard", "Són", "Són les onze i mitja"),
        (11, 45, "standard", "Són", "Són les dotze menys quart"),
        (12, 15, "standard", "Són", "Són les dotze i quart"),
        (12, 45, "standard", "És", "És la una menys quart"),
    ]

    def test_natural_sentences(self):
        for h, m, variant, copula, sentence in self.NATURAL_SENTENCES:
            dt = datetime.datetime(2017, 1, 31, h, m,
                                   tzinfo=default_timezone())
            phrase = nice_time(dt, lang="ca", use_24hour=True, variant=variant)
            self.assertEqual(
                f"{copula} {phrase}", sentence,
                f"{h:02d}:{m:02d} [{variant}] -> {phrase!r} does not complete "
                f"the natural sentence {sentence!r}")

    def test_natural_sentences_cover_full_clock(self):
        # Sanity: the curated utterances between the two registers exercise
        # every hour of the 12h clock (as spoken) and every quarter.
        spoken_hours = set()
        quarters = set()
        for h, m, variant, _copula, sentence in self.NATURAL_SENTENCES:
            quarters.add(m)
            if variant == "quarts":
                spoken_hours.add(((h % 12) + 1))  # the hour being approached
            else:
                # central names the current hour, except menys-quart cases
                spoken_hours.add((h % 12) or 12 if m < 35 else ((h % 12) + 1))
        self.assertEqual(spoken_hours, set(range(1, 13)))
        self.assertTrue({15, 30, 45}.issubset(quarters))

    def test_natural_sentence_register_contrast(self):
        # The SAME instant reads differently in each register — the whole point
        # of letting the caller choose. 4:30 -> central "i mitja" vs quarts
        # "dos quarts de cinc"; 4:45 -> "menys quart" vs "tres quarts de cinc".
        dt = datetime.datetime(2017, 1, 31, 4, 30, tzinfo=default_timezone())
        self.assertEqual(
            "Són " + nice_time(dt, lang="ca", use_24hour=True, variant="standard"),
            "Són les quatre i mitja")
        self.assertEqual(
            "Són " + nice_time(dt, lang="ca", use_24hour=True, variant="quarts"),
            "Són dos quarts de cinc")
        dt = datetime.datetime(2017, 1, 31, 4, 45, tzinfo=default_timezone())
        self.assertEqual(
            "Són " + nice_time(dt, lang="ca", use_24hour=True, variant="standard"),
            "Són les cinc menys quart")
        self.assertEqual(
            "Són " + nice_time(dt, lang="ca", use_24hour=True, variant="quarts"),
            "Són tres quarts de cinc")

    def test_natural_sentence_backcompat_and_aliases(self):
        # Real usage: default watch-time utterance is unchanged, and the same
        # utterance is reachable via every default alias and the enum.
        dt = datetime.datetime(2017, 1, 31, 4, 15, tzinfo=default_timezone())
        watch = nice_time(dt, lang="ca", use_24hour=True)
        self.assertEqual("Són " + watch, "Són les quatre i quinze")
        for alias in ("default", "watch", None, TimeVariantCA.DEFAULT,
                      "invalid", "", "  ", 999):
            self.assertEqual(
                nice_time(dt, lang="ca", use_24hour=True, variant=alias),
                watch,
                f"variant={alias!r} should reproduce the default utterance")
        # case-insensitive / whitespace-padded aliases pick the right register
        for spelling in ("quarts", "QUARTS", " Quarts "):
            self.assertEqual(
                "És " + nice_time(dt, lang="ca", use_24hour=True,
                                  variant=spelling),
                "És un quart de cinc")
        for spelling in ("standard", "CENTRAL", " Standard "):
            self.assertEqual(
                "Són " + nice_time(dt, lang="ca", use_24hour=True,
                                   variant=spelling),
                "Són les quatre i quart")


if __name__ == "__main__":
    unittest.main()
