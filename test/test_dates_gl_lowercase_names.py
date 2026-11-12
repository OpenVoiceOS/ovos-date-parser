"""Galician weekday and month names take a lowercase initial.

RAG, Normas ortográficas e morfolóxicas do idioma galego, 4 "O uso das
maiúsculas": "Escríbese inicial maiúscula nos seguintes casos:" -- the
start of a text, proper names, abbreviated forms of address, titles and
institutions. Weekday and month names are not among them. The RAG
dictionary writes "En xaneiro fago eu anos" (xaneiro, substantivo
masculino) and "O luns é día de traballo" (luns, substantivo masculino).
"""
import unittest
from datetime import datetime

from ovos_date_parser import (nice_date, nice_date_time, nice_day,
                              nice_month, nice_weekday)

MONTHS = ["xaneiro", "febreiro", "marzo", "abril", "maio", "xuño", "xullo",
          "agosto", "setembro", "outubro", "novembro", "decembro"]
WEEKDAYS = ["luns", "martes", "mércores", "xoves", "venres", "sábado",
            "domingo"]


class TestGalicianLowercaseNames(unittest.TestCase):
    def test_month_names(self):
        for month, name in enumerate(MONTHS, 1):
            self.assertEqual(nice_month(datetime(2018, month, 5), "gl"), name)
            self.assertEqual(nice_day(datetime(2018, month, 5), "gl-ES"),
                             f"5 {name}")

    def test_weekday_names(self):
        # 2018-03-05 is a Monday
        for i, name in enumerate(WEEKDAYS):
            self.assertEqual(nice_weekday(datetime(2018, 3, 5 + i), "gl"), name)

    def test_names_inside_a_date(self):
        dt = datetime(2018, 3, 5, 16, 20)
        self.assertEqual(nice_date(dt, "gl"),
                         "luns, cinco de marzo de dous mil e dezaoito")
        self.assertTrue(nice_date_time(dt, "gl").startswith(
            "luns, cinco de marzo de dous mil e dezaoito "))


if __name__ == "__main__":
    unittest.main()
