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
from datetime import datetime, time, timedelta

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import (
    extract_duration, extract_datetime
)


class TestNormalize_fr(unittest.TestCase):

    def test_extractdatetime_fr(self):
        def extractWithFormat_fr(text):
            date = datetime(2017, 6, 27, 0, 0, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang="fr-fr")
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract_fr(text, expected_date, expected_leftover):
            res = extractWithFormat_fr(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        def extractWithFormatDate2_fr(text):
            date = datetime(2017, 6, 30, 17, 0, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang="fr-fr")
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtractDate2_fr(text, expected_date, expected_leftover):
            res = extractWithFormatDate2_fr(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        def extractWithFormatNoDate_fr(text):
            [extractedDate, leftover] = extract_datetime(text, lang="fr-fr")
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtractNoDate_fr(text, expected_date, expected_leftover):
            res = extractWithFormatNoDate_fr(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        testExtract_fr("Planifier l'embûche dans 5 jours",
                       "2017-07-02 00:00:00", "planifier embûche")
        testExtract_fr("Quel temps fera-t-il après-demain ?",
                       "2017-06-29 00:00:00", "quel temps fera-t-il")
        testExtract_fr("Met un rappel à 10:45 du soir",
                       "2017-06-27 22:45:00", "met 1 rappel")
        testExtract_fr("quel temps est prévu pour vendredi matin ?",
                       "2017-06-30 08:00:00", "quel temps est prévu pour")
        testExtract_fr("quel temps fait-il demain",
                       "2017-06-28 00:00:00", "quel temps fait-il")
        testExtract_fr("rappelle-moi d'appeler maman dans 8 semaines et"
                       " 2 jours", "2017-08-24 00:00:00",
                       "rappelle-moi appeler maman")
        testExtract_fr("Jouer des musiques de Beyonce 2 jours après vendredi",
                       "2017-07-02 00:00:00", "jouer musiques beyonce")
        testExtract_fr("Commencer l'invasion à 15 heures 45 jeudi",
                       "2017-06-29 15:45:00", "commencer invasion")
        testExtract_fr("Lundi, commander le gâteau à la boulangerie",
                       "2017-07-03 00:00:00", "commander gâteau à boulangerie")
        testExtract_fr("Jouer la chanson Joyeux anniversaire dans 5 ans",
                       "2022-06-27 00:00:00", "jouer chanson joyeux"
                                              " anniversaire")
        testExtract_fr("Skyper Maman à 12 heures 45 jeudi prochain",
                       "2017-07-06 12:45:00", "skyper maman")
        testExtract_fr("Quel temps fera-t-il jeudi prochain ?",
                       "2017-07-06 00:00:00", "quel temps fera-t-il")
        testExtract_fr("Quel temps fera-t-il vendredi matin ?",
                       "2017-06-30 08:00:00", "quel temps fera-t-il")
        testExtract_fr("Quel temps fera-t-il vendredi soir",
                       "2017-06-30 19:00:00", "quel temps fera-t-il")
        testExtract_fr("Quel temps fera-t-il vendredi après-midi",
                       "2017-06-30 15:00:00", "quel temps fera-t-il")
        testExtract_fr("rappelle-moi d'appeler maman le 3 août",
                       "2017-08-03 00:00:00", "rappelle-moi appeler maman")
        testExtract_fr("Acheter des feux d'artifice pour le 14 juil",
                       "2017-07-14 00:00:00", "acheter feux artifice pour")
        testExtract_fr("Quel temps fera-t-il 2 semaines après vendredi",
                       "2017-07-14 00:00:00", "quel temps fera-t-il")
        testExtract_fr("Quel temps fera-t-il mercredi à 7 heures",
                       "2017-06-28 07:00:00", "quel temps fera-t-il")
        testExtract_fr("Quel temps fera-t-il mercredi à 7 heures",
                       "2017-06-28 07:00:00", "quel temps fera-t-il")
        testExtract_fr("Prendre rendez-vous à 12:45 jeudi prochain",
                       "2017-07-06 12:45:00", "prendre rendez-vous")
        testExtract_fr("Quel temps fait-il ce jeudi ?",
                       "2017-06-29 00:00:00", "quel temps fait-il")
        testExtract_fr("Organiser une visite 2 semaines et 6 jours après"
                       " samedi",
                       "2017-07-21 00:00:00", "organiser 1 visite")
        testExtract_fr("Commencer l'invasion à 3 heures 45 jeudi",
                       "2017-06-29 03:45:00", "commencer invasion")
        testExtract_fr("Commencer l'invasion à 20 heures jeudi",
                       "2017-06-29 20:00:00", "commencer invasion")
        testExtract_fr("Lancer la fête jeudi à 8 heures du soir",
                       "2017-06-29 20:00:00", "lancer fête")
        testExtract_fr("Commencer l'invasion à 4 heures de l'après-midi jeudi",
                       "2017-06-29 16:00:00", "commencer invasion")
        testExtract_fr("Commencer l'invasion jeudi à midi",
                       "2017-06-29 12:00:00", "commencer invasion")
        testExtract_fr("Commencer l'invasion jeudi à minuit",
                       "2017-06-29 00:00:00", "commencer invasion")
        testExtract_fr("Commencer l'invasion jeudi à dix-sept heures",
                       "2017-06-29 17:00:00", "commencer invasion")
        testExtract_fr("rappelle-moi de me réveiller dans 4 années",
                       "2021-06-27 00:00:00", "rappelle-moi me réveiller")
        testExtract_fr("rappelle-moi de me réveiller dans 4 ans et 4 jours",
                       "2021-07-01 00:00:00", "rappelle-moi me réveiller")
        testExtract_fr("Quel temps fera-t-il 3 jours après demain ?",
                       "2017-07-01 00:00:00", "quel temps fera-t-il")
        testExtract_fr("3 décembre",
                       "2017-12-03 00:00:00", "")
        testExtract_fr("retrouvons-nous à 8:00 ce soir",
                       "2017-06-27 20:00:00", "retrouvons-nous")
        testExtract_fr("retrouvons-nous demain à minuit et demi",
                       "2017-06-28 00:30:00", "retrouvons-nous")
        testExtract_fr("retrouvons-nous à midi et quart",
                       "2017-06-27 12:15:00", "retrouvons-nous")
        testExtract_fr("retrouvons-nous à midi moins le quart",
                       "2017-06-27 11:45:00", "retrouvons-nous")
        testExtract_fr("retrouvons-nous à midi moins dix",
                       "2017-06-27 11:50:00", "retrouvons-nous")
        testExtract_fr("retrouvons-nous à midi dix",
                       "2017-06-27 12:10:00", "retrouvons-nous")
        testExtract_fr("retrouvons-nous à minuit moins 23",
                       "2017-06-27 23:37:00", "retrouvons-nous")
        testExtract_fr("mangeons à 3 heures moins 23 minutes",
                       "2017-06-27 02:37:00", "mangeons")
        testExtract_fr("mangeons aussi à 4 heures moins le quart du matin",
                       "2017-06-27 03:45:00", "mangeons aussi")
        testExtract_fr("mangeons encore à minuit moins le quart",
                       "2017-06-27 23:45:00", "mangeons encore")
        testExtract_fr("buvons à 4 heures et quart",
                       "2017-06-27 04:15:00", "buvons")
        testExtract_fr("buvons également à 18 heures et demi",
                       "2017-06-27 18:30:00", "buvons également")
        testExtract_fr("dormons à 20 heures moins le quart",
                       "2017-06-27 19:45:00", "dormons")
        testExtract_fr("buvons le dernier verre à 10 heures moins 12 du soir",
                       "2017-06-27 21:48:00", "buvons dernier verre")
        testExtract_fr("s'échapper de l'île à 15h45",
                       "2017-06-27 15:45:00", "s'échapper île")
        testExtract_fr("s'échapper de l'île à 3h45min de l'après-midi",
                       "2017-06-27 15:45:00", "s'échapper île")
        testExtract_fr("décale donc ça à 3h48min cet après-midi",
                       "2017-06-27 15:48:00", "décale donc ça")
        testExtract_fr("construire un bunker à 9h42min du matin",
                       "2017-06-27 09:42:00", "construire 1 bunker")
        testExtract_fr("ou plutôt à 9h43 ce matin",
                       "2017-06-27 09:43:00", "ou plutôt")
        testExtract_fr("faire un feu à 8h du soir",
                       "2017-06-27 20:00:00", "faire 1 feu")
        testExtract_fr("faire la fête jusqu'à 18h cette nuit",
                       "2017-06-27 18:00:00", "faire fête jusqu'à")
        testExtract_fr("cuver jusqu'à 4h cette nuit",
                       "2017-06-27 04:00:00", "cuver jusqu'à")
        testExtract_fr("réveille-moi dans 20 secondes aujourd'hui",
                       "2017-06-27 00:00:20", "réveille-moi")
        testExtract_fr("réveille-moi dans 33 minutes",
                       "2017-06-27 00:33:00", "réveille-moi")
        testExtract_fr("tais-toi dans 12 heures et 3 minutes",
                       "2017-06-27 12:03:00", "tais-toi")
        testExtract_fr("ouvre-la dans 1 heure 3",
                       "2017-06-27 01:03:00", "ouvre-la")
        testExtract_fr("ferme-la dans 1 heure et quart",
                       "2017-06-27 01:15:00", "ferme-la")
        testExtract_fr("scelle-la dans 1 heure et demi",
                       "2017-06-27 01:30:00", "scelle-la")
        testExtract_fr("zippe-la dans 2 heures moins 12",
                       "2017-06-27 01:48:00", "zippe-la")
        testExtract_fr("soude-la dans 3 heures moins le quart",
                       "2017-06-27 02:45:00", "soude-la")
        testExtract_fr("mange la semaine prochaine",
                       "2017-07-04 00:00:00", "mange")
        testExtract_fr("bois la semaine dernière",
                       "2017-06-20 00:00:00", "bois")
        testExtract_fr("mange le mois prochain",
                       "2017-07-27 00:00:00", "mange")
        testExtract_fr("bois le mois dernier",
                       "2017-05-27 00:00:00", "bois")
        testExtract_fr("mange l'an prochain",
                       "2018-06-27 00:00:00", "mange")
        testExtract_fr("bois l'année dernière",
                       "2016-06-27 00:00:00", "bois")
        testExtract_fr("reviens à lundi dernier",
                       "2017-06-26 00:00:00", "reviens")
        testExtract_fr("capitule le 8 mai 1945",
                       "1945-05-08 00:00:00", "capitule")
        testExtract_fr("rédige le contrat 3 jours après jeudi prochain",
                       "2017-07-09 00:00:00", "rédige contrat")
        testExtract_fr("signe le contrat 2 semaines après jeudi dernier",
                       "2017-07-06 00:00:00", "signe contrat")
        testExtract_fr("lance le four dans un quart d'heure",
                       "2017-06-27 00:15:00", "lance four")
        testExtract_fr("enfourne la pizza dans une demi-heure",
                       "2017-06-27 00:30:00", "enfourne pizza")
        testExtract_fr("arrête le four dans trois quarts d'heure",
                       "2017-06-27 00:45:00", "arrête four")
        testExtract_fr("mange la pizza dans une heure",
                       "2017-06-27 01:00:00", "mange pizza")
        testExtract_fr("bois la bière dans 2h23",
                       "2017-06-27 02:23:00", "bois bière")
        testExtract_fr("faire les plantations le 3ème jour de mars",
                       "2018-03-03 00:00:00", "faire plantations")
        testExtract_fr("récolter dans 10 mois",
                       "2018-04-27 00:00:00", "récolter")
        testExtract_fr("point 6a: dans 10 mois",
                       "2018-04-27 06:00:00", "point")
        testExtract_fr("l'après-midi démissionner à 4:59",
                       "2017-06-27 16:59:00", "démissionner")
        testExtract_fr("cette nuit dormir",
                       "2017-06-27 02:00:00", "dormir")
        testExtract_fr("ranger son bureau à 1700 heures",
                       "2017-06-27 17:00:00", "ranger son bureau")

        testExtractDate2_fr("range le contrat 2 semaines après lundi",
                            "2017-07-17 00:00:00", "range contrat")
        testExtractDate2_fr("achète-toi de l'humour à 15h",
                            "2017-07-01 15:00:00", "achète-toi humour")
        # Disabling test until French Extract-date incorporates the fixes for
        # UTC / Local timezones.  Until then this test fails periodically
        # whenever test is run and the date in the local timezone (where the
        # test is being run) is a different than the date in UTC.
        #
        # testExtractNoDate_fr("tais-toi aujourd'hui",
        #                   datetime.now().strftime("%Y-%m-%d") + " 00:00:00",
        #                   "tais-toi")
        self.assertEqual(extract_datetime("", lang="fr-fr"), None)
        self.assertEqual(extract_datetime("phrase inutile", lang="fr-fr"),
                         None)
        self.assertEqual(extract_datetime(
            "apprendre à compter à 37 heures", lang="fr-fr"), None)

    def test_extractdatetime_default_fr(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime("faire les plantations le 3ème jour de mars",
                               anchor, lang='fr-fr', default_time=default)
        self.assertEqual(default, res[0].time())

    def test_extract_duration_fr(self):
        self.assertEqual(extract_duration("10 secondes", lang="fr-fr"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minutes", lang="fr-fr"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 heures", lang="fr-fr"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 jours", lang="fr-fr"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 semaines", lang="fr-fr"),
                         (timedelta(weeks=25), ""))
        # No conversion for work to number yet for fr
        self.assertEqual(extract_duration("sept heures"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 secondes", lang="fr-fr"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("5 jours et vingt-neuf secondes"),
                         (timedelta(days=5, seconds=29), "et"))
        # Fraction not yet implemented
        # self.assertEqual(extract_duration("huit jours et demi et trente-neuf secondes"),
        #                 (timedelta(days=8.5, seconds=39), "et "))
        self.assertEqual(extract_duration("démarre un minuteur pour 30 minutes", lang="fr-fr"),
                         (timedelta(minutes=30), "démarre 1 minuteur pour"))
        # self.assertEqual(extract_duration("Quatre minutes et demi avant le coucher du soleil"),
        #                 (timedelta(minutes=4.5), "avant le coucher du soleil"))
        self.assertEqual(extract_duration("Une heure dix-neuf minutes"),
                         (timedelta(hours=1, minutes=19), ""))
        self.assertEqual(extract_duration("réveille moi dans 3 semaines, "
                                          " 497 jours et"
                                          " 391.6 secondes", lang="fr-fr"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "réveille moi dans  et"))
        self.assertEqual(extract_duration("Le film dure une heure, cinquante-sept minutes"),
                         (timedelta(hours=1, minutes=57),
                          "film dure"))
        self.assertEqual(extract_duration("10-secondes", lang="fr-fr"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-minutes", lang="fr-fr"),
                         (timedelta(minutes=5), ""))


if __name__ == "__main__":
    unittest.main()