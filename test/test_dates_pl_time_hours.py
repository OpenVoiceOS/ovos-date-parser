"""The pl hour is a feminine ordinal, as "godzina" is feminine.

CLDR RBNF pl %spellout-ordinal-feminine: "1: pierwsza; 2: druga;
3: trzecia;" and "20: <%%ordinal-tens<$(cardinal,few{dziesta}other{dziesiąta})$[ >>];".
For 20 that rule gives "dwudziesta", so 21:30 is "dwudziesta pierwsza
trzydzieści". The expected hour names below are the values of that rule
set for 1 to 23.

Only the 24-hour reading is asserted. nice_time_pl does not read 12-hour
mode; a test of that mode belongs with its fix."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_time

CLDR_FEMININE_ORDINALS = (
    "pierwsza", "druga", "trzecia", "czwarta", "piąta", "szósta", "siódma",
    "ósma", "dziewiąta", "dziesiąta", "jedenasta", "dwunasta", "trzynasta",
    "czternasta", "piętnasta", "szesnasta", "siedemnasta", "osiemnasta",
    "dziewiętnasta", "dwudziesta", "dwudziesta pierwsza", "dwudziesta druga",
    "dwudziesta trzecia")


class TestPolishTimeHours(unittest.TestCase):

    def test_every_hour(self):
        for hour, name in enumerate(CLDR_FEMININE_ORDINALS, start=1):
            with self.subTest(hour=hour):
                self.assertEqual(
                    nice_time(datetime(2024, 1, 1, hour, 30), "pl",
                              use_24hour=True),
                    name + " trzydzieści")

    def test_midnight(self):
        self.assertEqual(nice_time(datetime(2024, 1, 1, 0, 30), "pl"),
                         "trzydzieści po północy")


if __name__ == "__main__":
    unittest.main()
