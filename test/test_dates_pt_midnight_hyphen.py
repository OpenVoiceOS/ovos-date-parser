"""Portuguese midnight and noon, and the day label.

Priberam writes "meia-noite" (nome feminino) and "meio-dia" (nome
masculino), each with a hyphen. The Acordo Ortográfico de 1990, Base XV 1.º,
hyphenates a compound by juxtaposition whose elements "constituem uma
unidade sintagmática e semântica e mantêm acento próprio".

From 23:35 the 12-hour reading counts down to the next hour, which is
midnight: 23:35 is 25 minutes before 24:00, so it reads "meia-noite menos
vinte e cinco".

Unicode CLDR 47, pt, availableFormats MMMMd, is "d 'de' MMMM", so the day
label is "12 de março"."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date_time, nice_day, nice_time

NOW = datetime(2020, 1, 1)
DATE = "terça-feira, doze de março, dois mil e vinte e quatro"


class TestPortugueseMidnightAndNoon(unittest.TestCase):

    def test_hyphenated(self):
        self.assertEqual(nice_time(datetime(2024, 3, 12, 0, 2), "pt-PT"),
                         "meia-noite e dois")
        self.assertEqual(nice_time(datetime(2024, 3, 12, 12, 15), "pt-PT"),
                         "meio-dia e um quarto")

    def test_before_midnight(self):
        for minute, spoken in ((35, "meia-noite menos vinte e cinco"),
                               (40, "meia-noite menos vinte"),
                               (45, "meia-noite menos um quarto"),
                               (50, "meia-noite menos dez"),
                               (55, "meia-noite menos cinco")):
            with self.subTest(minute=minute):
                self.assertEqual(
                    nice_time(datetime(2024, 3, 12, 23, minute), "pt-PT"),
                    spoken)

    def test_before_noon(self):
        self.assertEqual(nice_time(datetime(2024, 3, 12, 11, 40), "pt-PT"),
                         "meio-dia menos vinte")

    def test_date_time_joiner(self):
        for hour, minute, spoken in ((0, 30, "à meia-noite e meia"),
                                     (23, 40, "à meia-noite menos vinte"),
                                     (12, 30, "ao meio-dia e meia")):
            with self.subTest(hour=hour, minute=minute):
                self.assertEqual(
                    nice_date_time(datetime(2024, 3, 12, hour, minute),
                                   "pt-PT", now=NOW),
                    f"{DATE} {spoken}")


class TestPortugueseDayLabel(unittest.TestCase):

    def test_day_month(self):
        self.assertEqual(nice_day(datetime(2024, 3, 12), "pt-PT"),
                         "12 de março")


if __name__ == "__main__":
    unittest.main()
