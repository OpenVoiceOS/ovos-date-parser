"""Portuguese day periods in 12-hour speech (nice_time with use_ampm).

Unicode CLDR 49, supplemental dayPeriods.xml, rules for "pt" (pt_PT has
no rules of its own and inherits them): morning1 "da manhã" from 06:00
before 12:00, afternoon1 "da tarde" from 12:00 before 19:00, evening1
"da noite" from 19:00 before 24:00, night1 "da madrugada" from 00:00
before 06:00. The Brazilian Senado style manual, "Hora", agrees from
19:00: "A noite, das 18h às 24h", and it accepts "seis da tarde" for the
hour from 18h. The period qualifies the hour the phrase names.
"""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date_time, nice_time


class TestPortugueseDayPeriods(unittest.TestCase):
    #: hour, minute, expected 12-hour speech with the day period
    ROWS = [(0, 0, "meia-noite"),
            (1, 0, "uma da madrugada"),
            (5, 59, "cinco e cinquenta e nove da madrugada"),
            (6, 0, "seis da manhã"),
            (11, 59, "onze e cinquenta e nove da manhã"),
            (12, 0, "meio-dia"),
            (13, 0, "uma da tarde"),
            (18, 0, "seis da tarde"),
            (18, 30, "seis e meia da tarde"),
            (18, 59, "seis e cinquenta e nove da tarde"),
            (19, 0, "sete da noite"),
            (19, 40, "oito menos vinte da noite"),
            (20, 0, "oito da noite"),
            (20, 59, "oito e cinquenta e nove da noite"),
            (21, 0, "nove da noite"),
            (23, 15, "onze e um quarto da noite")]

    def test_day_period_boundaries(self):
        for lang in ("pt-PT", "pt-BR"):
            for hour, minute, expected in self.ROWS:
                dt = datetime(2024, 3, 5, hour, minute)
                with self.subTest(lang=lang, time=f"{hour:02}:{minute:02}"):
                    self.assertEqual(
                        nice_time(dt, lang=lang, use_ampm=True), expected)

    def test_named_hour_sets_the_period(self):
        # 18:45 names seven o'clock, which is "da noite"
        for lang in ("pt-PT", "pt-BR"):
            with self.subTest(lang=lang):
                self.assertEqual(
                    nice_time(datetime(2024, 3, 5, 18, 45), lang=lang,
                              use_ampm=True),
                    "sete menos um quarto da noite")

    def test_date_time_uses_the_same_period(self):
        dt = datetime(2024, 3, 5, 20, 0)
        for lang in ("pt-PT", "pt-BR"):
            with self.subTest(lang=lang):
                self.assertEqual(
                    nice_date_time(dt, lang=lang, use_ampm=True,
                                   now=datetime(2024, 3, 1, 9, 0)),
                    "terça-feira, cinco às oito da noite")

    def test_no_period_without_ampm(self):
        dt = datetime(2024, 3, 5, 20, 0)
        self.assertEqual(nice_time(dt, lang="pt-PT"), "oito em ponto")
        self.assertNotIn("noite", nice_time(dt, lang="pt-PT",
                                            use_24hour=True, use_ampm=True))


if __name__ == "__main__":
    unittest.main()
