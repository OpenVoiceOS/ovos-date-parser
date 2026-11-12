"""Spanish month and weekday names are lowercase.

The Ortografía de la lengua española (RAE and ASALE, 2010) makes the
lowercase initial the norm for days and months, with the example "Hoy es
martes 13 de febrero". A classroom digest of the book gives this text and
the locator p. 502; the book itself was not read."""
import unittest
from datetime import datetime

from ovos_date_parser import (nice_date, nice_date_time, nice_day,
                              nice_month, nice_weekday)

TUESDAY = datetime(2024, 3, 12, 14, 30)


class TestSpanishLowercaseNames(unittest.TestCase):

    def test_nice_date(self):
        self.assertEqual(nice_date(TUESDAY, "es-ES", include_weekday=False),
                         "doce de marzo, dos mil veinticuatro")

    def test_nice_date_with_weekday(self):
        self.assertEqual(nice_date(TUESDAY, "es-ES"),
                         "martes, doce de marzo, dos mil veinticuatro")

    def test_nice_date_time(self):
        date_part = "martes, doce de marzo, dos mil veinticuatro "
        spoken = nice_date_time(TUESDAY, "es-ES", now=datetime(2020, 1, 1))
        self.assertEqual(spoken[:len(date_part)], date_part)

    def test_labels(self):
        self.assertEqual(nice_month(TUESDAY, "es-ES"), "marzo")
        self.assertEqual(nice_weekday(TUESDAY, "es-ES"), "martes")
        self.assertEqual(nice_day(TUESDAY, "es-ES"), "12 de marzo")


if __name__ == "__main__":
    unittest.main()
