"""In ast, "de" before a month elides to "d'" when the month starts with a
vowel.

CLDR ast gives the full date "EEEE, d MMMM 'de' y" with the format months
"de xineru, de febreru, de marzu, d’abril, de mayu, de xunu, de xunetu,
d’agostu, de setiembre, d’ochobre, de payares, d’avientu". The four months
that start with a vowel take "d’"; the code writes the apostrophe as "'",
as the an dates do."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date, nice_month

CLDR_CONNECTOR = {1: "de ", 2: "de ", 3: "de ", 4: "d'", 5: "de ", 6: "de ",
                  7: "de ", 8: "d'", 9: "de ", 10: "d'", 11: "de ", 12: "d'"}


class TestAsturianDeElision(unittest.TestCase):

    def test_every_month(self):
        for month, connector in CLDR_CONNECTOR.items():
            dt = datetime(2024, month, 5)
            spoken = connector + nice_month(dt, "ast")
            with self.subTest(month=month):
                self.assertIn(f"cinco {spoken} de ", nice_date(dt, "ast"))
                self.assertEqual(
                    nice_date(dt, "ast", now=datetime(2024, month % 12 + 1, 20),
                              include_weekday=False),
                    f"cinco {spoken}")


if __name__ == "__main__":
    unittest.main()
