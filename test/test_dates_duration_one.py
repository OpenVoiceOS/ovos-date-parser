"""nice_duration counts one of a unit in the form of the unit's gender.

CLDR RBNF gives the form of 1 for each gender, for example es
%spellout-cardinal-masculine "1: un;" and %spellout-cardinal-feminine
"1: una;", sv %spellout-cardinal-reale "1: en;", da %spellout-cardinal-neuter
"1: et;". CLDR units give the gender of each unit, for example es
duration-hour "feminine", da duration-minute "neuter". Where CLDR has no
gender or names another noun, a dictionary gives it: SAOB "DAG ... r. ...
best. -en" (sv), Bokmålsordboka "minutt" neuter (nb), Real Academia Galega
"hora: substantivo feminino" and "un (feminino: unha)" (gl), Речник на
българския език "ден", "час": "мъжки род", "минута", "секунда": "женски
род" (bg). Treccani, Enciclopedia dell'Italiano, "elisione": "una ora ->
un'ora". The expected strings below are written from those sources.

A duration with days puts one space between the parts and none at the end.
"""
import unittest

from ovos_date_parser import nice_duration

ONE_EACH = 86400 + 3600 + 60 + 1

EXPECTED = {
    "bg": "един ден един час една минута една секунда",
    "ca": "un dia una hora un minut un segon",
    "cs": "jeden den jedna hodina jedna minuta jedna sekunda",
    "da": "en dag en time et minut et sekund",
    "de": "ein Tag eine Stunde eine Minute eine Sekunde",
    "el": "μία μέρα μία ώρα ένα λεπτό ένα δευτερόλεπτο",
    "en": "one day one hour one minute one second",
    "es": "un día una hora un minuto un segundo",
    "fr": "un jour une heure une minute une seconde",
    "gl": "un día unha hora un minuto un segundo",
    "hr": "jedan dan jedan sat jedna minuta jedna sekunda",
    "it": "un giorno un'ora un minuto un secondo",
    "nb": "en dag en time ett minutt en sekund",
    "pt": "um dia uma hora um minuto um segundo",
    "sk": "jeden deň jedna hodina jedna minúta jedna sekunda",
    "sl": "en dan ena ura ena minuta ena sekunda",
    "sv": "en dag en timme en minut en sekund",
}


class TestDurationOne(unittest.TestCase):

    def test_one_of_each_unit(self):
        for lang, spoken in EXPECTED.items():
            with self.subTest(lang=lang):
                self.assertEqual(nice_duration(ONE_EACH, lang), spoken)

    def test_region_tag(self):
        self.assertEqual(nice_duration(3600, "es-ES"), "una hora")
        self.assertEqual(nice_duration(3600, "pt-PT"), "uma hora")

    def test_days_alone_end_without_a_space(self):
        self.assertEqual(nice_duration(2 * 86400, "en"), "two days")

    def test_days_then_seconds_have_one_space(self):
        self.assertEqual(nice_duration(2 * 86400 + 5, "en"),
                         "two days five seconds")

    def test_two_keeps_the_numeral(self):
        self.assertEqual(nice_duration(2 * 3600 + 2 * 60, "es"),
                         "dos horas dos minutos")


if __name__ == "__main__":
    unittest.main()
