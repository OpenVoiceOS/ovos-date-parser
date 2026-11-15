"""Basque nice_time and nice_date_time accept every minute of the day.

After half past, the 12-hour reading counts down to the next hour. The hour
after 12 is 1: 0:40 and 12:40 are twenty minutes before one, "ordu bata
hogei gutxi" (Araua 35, "hamarrak hamar gutxi")."""
import itertools
import unittest
from datetime import datetime

from ovos_date_parser import nice_date_time, nice_time

NOW = datetime(2020, 1, 1)


class TestBasqueTimeEveryMinute(unittest.TestCase):

    def test_no_minute_raises(self):
        for hour, minute in itertools.product(range(24), range(60)):
            dt = datetime(2024, 3, 12, hour, minute)
            for speech, use_24hour, use_ampm in itertools.product(
                    (True, False), repeat=3):
                with self.subTest(hour=hour, minute=minute, speech=speech,
                                  use_24hour=use_24hour, use_ampm=use_ampm):
                    nice_time(dt, "eu", speech=speech,
                              use_24hour=use_24hour, use_ampm=use_ampm)
                    nice_date_time(dt, "eu", now=NOW,
                                   use_24hour=use_24hour, use_ampm=use_ampm)

    def test_before_one(self):
        for hour in (0, 12):
            with self.subTest(hour=hour):
                self.assertEqual(
                    nice_time(datetime(2024, 3, 12, hour, 40), "eu"),
                    "ordu bata hogei gutxi")
                self.assertEqual(
                    nice_time(datetime(2024, 3, 12, hour, 45), "eu"),
                    "ordu bata laurden gutxi")

    def test_before_twelve(self):
        self.assertEqual(nice_time(datetime(2024, 3, 12, 11, 40), "eu"),
                         "hamabiak hogei gutxi")


if __name__ == "__main__":
    unittest.main()
