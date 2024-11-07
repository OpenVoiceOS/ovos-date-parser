#
# Copyright 2017 Mycroft AI Inc.
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
import unittest
from datetime import datetime, timedelta

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    extract_duration, extract_datetime
)


class TestNormalize(unittest.TestCase):

    def test_extract_duration_cs(self):
        self.assertEqual(extract_duration("10 sekund"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minut"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 hodiny"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 dny"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 týdnů"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("sedm hodin"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 sekund"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("osm a polovina dne třicet"
                                          " devět sekund"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("Nastav časovač na 30 minut"),
                         (timedelta(minutes=30), "nastav časovač na"))
        self.assertEqual(extract_duration("Čtyři a půl minuty do"
                                          " západu"),
                         (timedelta(minutes=4.5), "do západu"))
        self.assertEqual(extract_duration("devatenáct minut po hodině"),
                         (timedelta(minutes=19), "po hodině"))
        self.assertEqual(extract_duration("vzbuď mě za tři týdny, čtyři"
                                          " sto devadesát sedm dní, a"
                                          " tři sto 91.6 sekund"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "vzbuď mě za  ,  , a"))
        self.assertEqual(extract_duration("film je jedna hodina, padesát sedm"
                                          " a půl minuty dlouhý"),
                         (timedelta(hours=1, minutes=57.5),
                          "film je  ,  dlouhý"))
        self.assertEqual(extract_duration("10-sekund"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-minut"),
                         (timedelta(minutes=5), ""))

    def test_extractdatetime_cs(self):
        def extractWithFormat(text):
            # Tue June 27, 2017 @ 1:04pm
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("nyní je čas",
                    "2017-06-27 13:04:00", "je čas")
        testExtract("za sekundu",
                    "2017-06-27 13:04:01", "")
        testExtract("za minutu",
                    "2017-06-27 13:05:00", "")
        # testExtract("ve dvou minutách",
        #            "2017-06-27 13:06:00", "")
        # testExtract("in a couple of minutes",
        #            "2017-06-27 13:06:00", "")
        # testExtract("ve dvou hodinách",
        #            "2017-06-27 15:04:00", "")
        # testExtract("in a couple of hours",
        #            "2017-06-27 15:04:00", "")
        # testExtract("v dvoje týden",
        #            "2017-07-11 00:00:00", "")
        # testExtract("in a couple of weeks",
        #            "2017-07-11 00:00:00", "")
        # testExtract("v dvoje měsíc",
        #            "2017-08-27 00:00:00", "")
        # testExtract("v dvoje rok",
        #            "2019-06-27 00:00:00", "")
        # testExtract("in a couple of months",
        #            "2017-08-27 00:00:00", "")
        # testExtract("in a couple of years",
        #            "2019-06-27 00:00:00", "")
        testExtract("v desetiletí",
                    "2027-06-27 00:00:00", "")
        # testExtract("in a couple of decades",
        #            "2037-06-27 00:00:00", "")
        testExtract("další desetiletí",
                    "2027-06-27 00:00:00", "")
        testExtract("v století",
                    "2117-06-27 00:00:00", "")
        testExtract("v tisíciletí",
                    "3017-06-27 00:00:00", "")
        testExtract("v dvoje desetiletí",
                    "2037-06-27 00:00:00", "")
        testExtract("v 5 desetiletí",
                    "2067-06-27 00:00:00", "")
        testExtract("v dvoje století",
                    "2217-06-27 00:00:00", "")
        # testExtract("in a couple of centuries",
        #            "2217-06-27 00:00:00", "")
        testExtract("v 2 století",
                    "2217-06-27 00:00:00", "")
        testExtract("v dvoje tisíciletí",
                    "4017-06-27 00:00:00", "")
        # testExtract("in a couple of millenniums",
        #            "4017-06-27 00:00:00", "")
        testExtract("v hodina",
                    "2017-06-27 14:04:00", "")
        testExtract("chci to během hodiny",
                    "2017-06-27 14:04:00", "chci to")
        testExtract("za 1 sekundu",
                    "2017-06-27 13:04:01", "")
        testExtract("za 2 sekundy",
                    "2017-06-27 13:04:02", "")
        testExtract("Nastav časovač na 1 minutu",
                    "2017-06-27 13:05:00", "nastav časovač")
        testExtract("Nastav časovač na půl hodina",
                    "2017-06-27 13:34:00", "nastav časovač")
        testExtract("Nastav časovač na 5 den od dnes",
                    "2017-07-02 00:00:00", "nastav časovač")
        testExtract("den po zítřku",
                    "2017-06-29 00:00:00", "")
        testExtract("Jaké je počasí den po zítřku?",
                    "2017-06-29 00:00:00", "jaké je počasí")
        testExtract("Připomeň mi v 10:45 pm",
                    "2017-06-27 22:45:00", "připomeň mi")
        testExtract("jaké je počasí v pátek ráno",
                    "2017-06-30 08:00:00", "jaké je počasí")
        testExtract("jaké je zítřejší počasí",
                    "2017-06-28 00:00:00", "jaké je počasí")
        testExtract("jaké je počasí toto odpoledne",
                    "2017-06-27 15:00:00", "jaké je počasí")
        testExtract("jaké je počasí tento večer",
                    "2017-06-27 19:00:00", "jaké je počasí")
        testExtract("jaké bylo počasí toto ráno",
                    "2017-06-27 08:00:00", "jaké bylo počasí")
        testExtract("připomeň mi abych zavolal mámě v 8 týden a 2 dny",
                    "2017-08-24 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v srpen 3",
                    "2017-08-03 00:00:00", "připomeň mi abych zavolal mámě")  # přidat i třetího slovně
        testExtract("připomeň mi zítra abych zavolal mámě v 7am",
                    "2017-06-28 07:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi zítra abych zavolal mámě v 10pm",
                    "2017-06-28 22:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 7am",
                    "2017-06-28 07:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v hodina",
                    "2017-06-27 14:04:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 1730",
                    "2017-06-27 17:30:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 0630",
                    "2017-06-28 06:30:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 06 30 hodina",
                    "2017-06-28 06:30:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 06 30",
                    "2017-06-28 06:30:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 06 30 hodina",
                    "2017-06-28 06:30:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 7 hodin",
                    "2017-06-27 19:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě večer v 7 hodin",
                    "2017-06-27 19:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě  v 7 hodin večer",
                    "2017-06-27 19:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 7 hodin ráno",
                    "2017-06-28 07:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v Čtvrtek večer v 7 hodin",
                    "2017-06-29 19:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v Čtvrtek ráno v 7 hodin",
                    "2017-06-29 07:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 7 hodin Čtvrtek ráno",
                    "2017-06-29 07:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 7:00 Čtvrtek ráno",
                    "2017-06-29 07:00:00", "připomeň mi abych zavolal mámě")
        # TODO: This test is imperfect due to "at 7:00" still in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("připomeň mi abych zavolal mámě v 7:00 Čtvrtek večer",
                    "2017-06-29 19:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 8 Středa večer",
                    "2017-06-28 20:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 8 Středa v večer",
                    "2017-06-28 20:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě Středa večer v 8",
                    "2017-06-28 20:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za dvě hodiny",
                    "2017-06-27 15:04:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za 2 hodiny",
                    "2017-06-27 15:04:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za 15 minut",
                    "2017-06-27 13:19:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za patnáct minut",
                    "2017-06-27 13:19:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za půl hodina",
                    "2017-06-27 13:34:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za půl hodina",
                    "2017-06-27 13:34:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za čtvrt hodina",
                    "2017-06-27 13:19:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za čtvrt hodina",
                    "2017-06-27 13:19:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 10am 2 den po této sobota",
                    "2017-07-03 10:00:00", "připomeň mi abych zavolal mámě")
        testExtract("Přehraj Rick Astley hudbu 2 dny od Pátek",
                    "2017-07-02 00:00:00", "přehraj rick astley hudbu")
        testExtract("Začni invazi v 3:45 pm v Čtvrtek",
                    "2017-06-29 15:45:00", "začni invazi")
        testExtract("V Pondělí, objednej koláč z pekárny",
                    "2017-07-03 00:00:00", "objednej koláč z pekárny")
        testExtract("Přehraj Happy Birthday hudbu 5 roků od dnes",
                    "2022-06-27 00:00:00", "přehraj happy birthday hudbu")
        testExtract("Skype Mámě v 12:45 pm další Čtvrtek",
                    "2017-07-06 12:45:00", "skype mámě")
        testExtract("Jaké je počasí příští Pátek?",
                    "2017-06-30 00:00:00", "jaké je počasí")
        testExtract("Jaké je počasí příští Středa?",
                    "2017-07-05 00:00:00", "jaké je počasí")
        testExtract("Jaké je počasí příští Čtvrtek?",
                    "2017-07-06 00:00:00", "jaké je počasí")
        testExtract("Jaké je počasí příští pátek ráno",
                    "2017-06-30 08:00:00", "jaké je počasí")
        testExtract("jaké je počasí příští pátek večer",
                    "2017-06-30 19:00:00", "jaké je počasí")
        testExtract("jaké je počasí příští pátek odpoledne",
                    "2017-06-30 15:00:00", "jaké je počasí")
        testExtract("připomeň mi abych zavolal mámě v srpen třetího",
                    "2017-08-03 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("Kup ohňostroj v 4 Červenec",
                    "2017-07-04 00:00:00", "kup ohňostroj")
        testExtract("jaké je počasí 2 týdny od další pátek",
                    "2017-07-14 00:00:00", "jaké je počasí")
        testExtract("jaké je počasí Středa v 0700 hodina",
                    "2017-06-28 07:00:00", "jaké je počasí")
        testExtract("Nastav budík Středa v 7 hodin",
                    "2017-06-28 07:00:00", "nastav budík")
        testExtract("Nastav schůzku v 12:45 pm další Čtvrtek",
                    "2017-07-06 12:45:00", "nastav schůzku")
        testExtract("Jaké je počasí tento Čtvrtek?",
                    "2017-06-29 00:00:00", "jaké je počasí")
        testExtract("nastav návštěvu na 2 týdny a 6 dní od Sobota",
                    "2017-07-21 00:00:00", "nastav návštěvu")
        testExtract("Zahaj invazi v 03 45 v Čtvrtek",
                    "2017-06-29 03:45:00", "zahaj invazi")
        testExtract("Zahaj invazi v 800 hodin v Čtvrtek",
                    "2017-06-29 08:00:00", "zahaj invazi")
        testExtract("Zahaj párty v 8 hodin v večer v Čtvrtek",
                    "2017-06-29 20:00:00", "zahaj párty")
        testExtract("Zahaj invazi v 8 v večer v Čtvrtek",
                    "2017-06-29 20:00:00", "zahaj invazi")
        testExtract("Zahaj invazi v Čtvrtek v poledne",
                    "2017-06-29 12:00:00", "zahaj invazi")
        testExtract("Zahaj invazi v Čtvrtek v půlnoc",
                    "2017-06-29 00:00:00", "zahaj invazi")
        testExtract("Zahaj invazi v Čtvrtek v 0500",
                    "2017-06-29 05:00:00", "zahaj invazi")
        testExtract("připomeň mi abych vstal v 4 roky",
                    "2021-06-27 00:00:00", "připomeň mi abych vstal")
        testExtract("připomeň mi abych vstal v 4 roky a 4 dny",
                    "2021-07-01 00:00:00", "připomeň mi abych vstal")
        testExtract("jaké je počasí 3 dny po zítra?",
                    "2017-07-01 00:00:00", "jaké je počasí")
        testExtract("prosinec 3",
                    "2017-12-03 00:00:00", "")
        testExtract("sejdeme se v 8:00 dnes večer",
                    "2017-06-27 20:00:00", "sejdeme se")
        testExtract("sejdeme se v 5pm",
                    "2017-06-27 17:00:00", "sejdeme se")
        testExtract("sejdeme se v 8 am",
                    "2017-06-28 08:00:00", "sejdeme se")
        testExtract("připomeň mi abych vstal v 8 am",
                    "2017-06-28 08:00:00", "připomeň mi abych vstal")
        testExtract("jaké je počasí v úterý",
                    "2017-06-27 00:00:00", "jaké je počasí")
        testExtract("jaké je počasí v pondělí",
                    "2017-07-03 00:00:00", "jaké je počasí")
        testExtract("jaké je počasí toto Středa",
                    "2017-06-28 00:00:00", "jaké je počasí")
        testExtract("v Čtvrtek jaké je počasí",
                    "2017-06-29 00:00:00", "jaké je počasí")
        testExtract("tento Čtvrtek jaké je počasí",
                    "2017-06-29 00:00:00", "jaké je počasí")
        testExtract("poslední pondělí jaké bylo počasí",
                    "2017-06-26 00:00:00", "jaké bylo počasí")
        testExtract("nastav budík na Středa večer v 8",
                    "2017-06-28 20:00:00", "nastav budík")
        testExtract("nastav budík na Středa v 3 hodiny v odpoledne",
                    "2017-06-28 15:00:00", "nastav budík")
        testExtract("nastav budík na Středa v 3 hodiny v ráno",
                    "2017-06-28 03:00:00", "nastav budík")
        testExtract("nastav budík na Středa ráno v 7 hodin",
                    "2017-06-28 07:00:00", "nastav budík")
        testExtract("nastav budík na dnes v 7 hodin",
                    "2017-06-27 19:00:00", "nastav budík")
        testExtract("nastav budík na tento večer v 7 hodin",
                    "2017-06-27 19:00:00", "nastav budík")
        # TODO: This test is imperfect due to the "at 7:00" still in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("nastav budík na tento večer v 7:00",
                    "2017-06-27 19:00:00", "nastav budík v 7:00")
        testExtract("večer v červen 5 2017 připomeň mi" +
                    " abych zavolal mámě",
                    "2017-06-05 19:00:00", "připomeň mi abych zavolal mámě")
        # TODO: This test is imperfect due to the missing "for" in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("aktualizuj můj kalendář na ranní schůzku s julius" +
                    " v březnu 4",
                    "2018-03-04 08:00:00",
                    "aktualizuj můj kalendář schůzku s julius")
        testExtract("připomeň mi abych zavolal mámě další úterý",
                    "2017-07-04 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě  3 týdny",
                    "2017-07-18 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 8 týdny",
                    "2017-08-22 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 8 týdny a 2 dny",
                    "2017-08-24 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 4 dny",
                    "2017-07-01 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 3 měsíce",
                    "2017-09-27 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 2 roky a 2 dny",
                    "2019-06-29 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě další týden",
                    "2017-07-04 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 10am v Sobota",
                    "2017-07-01 10:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 10am tato Sobota",
                    "2017-07-01 10:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 10 další Sobota",
                    "2017-07-01 10:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 10am další Sobota",
                    "2017-07-01 10:00:00", "připomeň mi abych zavolal mámě")
        # test yesterday
        testExtract("jaký den byl včera",
                    "2017-06-26 00:00:00", "jaký den byl")
        testExtract("jaký den byl den před včera",
                    "2017-06-25 00:00:00", "jaký den byl")
        testExtract("měl jsem večeři včera v 6",
                    "2017-06-26 06:00:00", "měl jsem večeři")
        testExtract("měl jsem večeři včera v 6 am",
                    "2017-06-26 06:00:00", "měl jsem večeři")
        testExtract("měl jsem večeři včera v 6 pm",
                    "2017-06-26 18:00:00", "měl jsem večeři")

        # Below two tests, ensure that time is picked
        # even if no am/pm is specified
        # in case of weekdays/tonight

        testExtract("nastav budík na 9 o víkendech",
                    "2017-06-27 21:00:00", "nastav budík víkendech")
        testExtract("na 8 dnes večer",
                    "2017-06-27 20:00:00", "")
        testExtract("na 8:30pm dnes večer",
                    "2017-06-27 20:30:00", "")
        # Tests a time with ':' & without am/pm
        testExtract("nastav budík na dnes večer 9:30",
                    "2017-06-27 21:30:00", "nastav budík")
        testExtract("nastav budík na 9:00 na dnes večer",
                    "2017-06-27 21:00:00", "nastav budík")
        # Check if it picks intent irrespective of correctness
        testExtract("nastav budík na 9 hodin dnes večer",
                    "2017-06-27 21:00:00", "nastav budík")
        testExtract("připomeň mi hru dnes v noci v 11:30",
                    "2017-06-27 23:30:00", "připomeň mi hru")
        testExtract("nastav budík v 7:30 o výkendech",
                    "2017-06-27 19:30:00", "nastav budík o výkendech")

        #  "# days <from X/after X>"
        testExtract("mé narozeniny jsou 2 dny od dnes",
                    "2017-06-29 00:00:00", "mé narozeniny jsou")
        testExtract("mé narozeniny jsou 2 dny po dnes",
                    "2017-06-29 00:00:00", "mé narozeniny jsou")
        testExtract("mé narozeniny jsou 2 dny od zítra",
                    "2017-06-30 00:00:00", "mé narozeniny jsou")
        testExtract("mé narozeniny jsou 2 dny od zítra",
                    "2017-06-30 00:00:00", "mé narozeniny jsou")
        testExtract("připomeň mi abych zavolal mámě v 10am 2 dny po další Sobota",
                    "2017-07-10 10:00:00", "připomeň mi abych zavolal mámě")
        testExtract("mé narozeniny jsou 2 dny od včera",
                    "2017-06-28 00:00:00", "mé narozeniny jsou")
        testExtract("mé narozeniny jsou 2 dny po včera",
                    "2017-06-28 00:00:00", "mé narozeniny jsou")

        #  "# days ago>"
        testExtract("mé narozeniny byly před 1 den",
                    "2017-06-26 00:00:00", "mé narozeniny byly")
        testExtract("mé narozeniny byly před 2 dny",
                    "2017-06-25 00:00:00", "mé narozeniny byly")
        testExtract("mé narozeniny byly před 3 dny",
                    "2017-06-24 00:00:00", "mé narozeniny byly")
        testExtract("mé narozeniny byly před 4 dny",
                    "2017-06-23 00:00:00", "mé narozeniny byly")
        # TODO this test is imperfect due to "tonight" in the reminder, but let is pass since the date is correct
        testExtract("sejdeme se dnes v noci",
                    "2017-06-27 22:00:00", "sejdeme se noci")
        # TODO this test is imperfect due to "at night" in the reminder, but let is pass since the date is correct
        testExtract("sejdeme se později v noci",
                    "2017-06-27 22:00:00", "sejdeme se později v noci")
        # TODO this test is imperfect due to "night" in the reminder, but let is pass since the date is correct
        testExtract("Jaké bude počasí zítra v noci",
                    "2017-06-28 22:00:00", "jaké bude počasí v noci")
        # TODO this test is imperfect due to "night" in the reminder, but let is pass since the date is correct
        testExtract("jaké bude počasí příští úterý v noci",
                    "2017-07-04 22:00:00", "jaké bude počasí v noci")

    def test_extract_ambiguous_time_cs(self):
        morning = datetime(2017, 6, 27, 8, 1, 2, tzinfo=default_timezone())
        večer = datetime(2017, 6, 27, 20, 1, 2, tzinfo=default_timezone())
        noonish = datetime(2017, 6, 27, 12, 1, 2, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('krmení ryb'), None)
        self.assertEqual(
            extract_datetime('den'), None)
        self.assertEqual(
            extract_datetime('týden'), None)
        self.assertEqual(
            extract_datetime('měsíc'), None)
        self.assertEqual(
            extract_datetime('rok'), None)
        self.assertEqual(
            extract_datetime(' '), None)
        self.assertEqual(
            extract_datetime('nakrmit ryby v 10 hodin', morning)[0],
            datetime(2017, 6, 27, 10, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('nakrmit ryby v 10 hodin', noonish)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('nakrmit ryby v 10 hodin', večer)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))

    """
    In Czech is May and may have different format
    def test_extract_date_with_may_I_cs(self):
        now = datetime(2019, 7, 4, 8, 1, 2)
        may_date = datetime(2019, 5, 2, 10, 11, 20)
        self.assertEqual(
            extract_datetime('Můžu vědět jaký je to čas zítra', now)[0],
            datetime(2019, 7, 5, 0, 0, 0))
        self.assertEqual(
            extract_datetime('Můžu vědět kdy je 10 hodin', now)[0],
            datetime(2019, 7, 4, 10, 0, 0))
        self.assertEqual(
            extract_datetime('24. můžu chtít připomenutí', may_date)[0],
            datetime(2019, 5, 24, 0, 0, 0))
    """

    def test_extract_relativedatetime_cs(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("sejdeme se za 5 minut",
                    "2017-06-27 10:06:02", "sejdeme se")
        testExtract("sejdeme se za 5minut",
                    "2017-06-27 10:06:02", "sejdeme se")
        testExtract("sejdeme se za 5 sekund",
                    "2017-06-27 10:01:07", "sejdeme se")
        testExtract("sejdeme se za 1 hodinu",
                    "2017-06-27 11:01:02", "sejdeme se")
        testExtract("sejdeme se za 2 hodiny",
                    "2017-06-27 12:01:02", "sejdeme se")
        print("TODO")  # Need better normaliting procedure for czech inflexion
        # testExtract("sejdeme se za 2hodiny",
        #            "2017-06-27 12:01:02", "sejdeme se")
        testExtract("sejdeme se za 1 minutu",
                    "2017-06-27 10:02:02", "sejdeme se")
        testExtract("sejdeme se za 1 sekundu",
                    "2017-06-27 10:01:03", "sejdeme se")
        testExtract("sejdeme se za 5sekund",
                    "2017-06-27 10:01:07", "sejdeme se")


if __name__ == "__main__":
    unittest.main()
