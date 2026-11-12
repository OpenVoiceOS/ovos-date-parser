"""pt and es day labels follow the Unicode CLDR 47 day-month pattern.

CLDR pt and es, gregorian availableFormats MMMMd, are both "d 'de' MMMM".
The field "d" is the day of the month with no padding, so 5 March is
"5 de março" and "5 de marzo"."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_day

FIFTH = datetime(2024, 3, 5)


class TestNiceDayCLDR(unittest.TestCase):

    def test_pt(self):
        self.assertEqual(nice_day(FIFTH, "pt-PT"), "5 de março")
        self.assertEqual(nice_day(FIFTH, "pt-PT", date_format="MDY"),
                         "março 5")

    def test_es(self):
        self.assertEqual(nice_day(FIFTH, "es-ES"), "5 de marzo")
        self.assertEqual(nice_day(datetime(2024, 3, 12), "es-ES"),
                         "12 de marzo")
        self.assertEqual(nice_day(FIFTH, "es-ES", date_format="MDY"),
                         "marzo 5")


if __name__ == "__main__":
    unittest.main()
