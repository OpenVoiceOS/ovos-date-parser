"""Basque part of the day with use_ampm.

The part of the day belongs to the hour that is said. After half past the
12-hour reading counts down to the next hour, so 12:40 is "ordu bata hogei
gutxi", twenty to one in the afternoon.

The bands come from Euskaltzaindia Araua 35 and the EBE entry "orduak
nola esan":

- 0: "00:00, gaueko nahiz gauerdiko hamabiak", "00:30 = gauerdiko/gaueko
  hamabi eta erdiak"
- 1 to 11: "01:00 = goiz(ald)eko ordu bata da", "Goizeko bostak laurden
  gutxiagotan", "goizeko 11,30etan"
- 12: "Eguardiko amabiak laurden gutxitan" (G. Mujica, quoted in Araua 35);
  "eguerdi" is the standard spelling, as in "Eguerdi laurden guti zen"
- 13 to 19: "arratsaldeko 5etan", "Arratsaldeko hiruretan"
- 20 to 23: "iluntzeko 8etatik 11k arte". This range example is the only
  source for 21 to 23."""
import itertools
import unittest
from datetime import datetime

from ovos_date_parser import nice_date_time, nice_time

NOW = datetime(2020, 1, 1)
BANDS = [(0, 0, "gaueko"), (1, 11, "goizeko"), (12, 12, "eguerdiko"),
         (13, 19, "arratsaldeko"), (20, 23, "iluntzeko")]


def band(said_hour):
    return next(word for low, high, word in BANDS if low <= said_hour <= high)


class TestBasquePartOfDay(unittest.TestCase):

    def test_every_minute(self):
        for hour, minute in itertools.product(range(24), range(60)):
            said_hour = (hour + (minute > 30)) % 24
            dt = datetime(2024, 3, 12, hour, minute)
            with self.subTest(hour=hour, minute=minute):
                self.assertEqual(
                    nice_time(dt, "eu", use_ampm=True).split()[0],
                    band(said_hour))
                date_time = nice_date_time(dt, "eu", now=NOW, use_ampm=True)
                self.assertIn(f" {band(said_hour)} ", date_time)

    def test_examples(self):
        for hour, minute, spoken in (
                (0, 30, "gaueko hamabi eta erdiak"),
                (1, 0, "goizeko ordu bata"),
                (4, 45, "goizeko bostak laurden gutxi"),
                (11, 30, "goizeko hamaika eta erdiak"),
                (11, 45, "eguerdiko hamabiak laurden gutxi"),
                (12, 15, "eguerdiko hamabiak eta laurden"),
                (12, 40, "arratsaldeko ordu bata hogei gutxi"),
                (17, 0, "arratsaldeko bostak"),
                (20, 0, "iluntzeko zortziak"),
                (23, 40, "gaueko hamabiak hogei gutxi")):
            with self.subTest(hour=hour, minute=minute):
                self.assertEqual(
                    nice_time(datetime(2024, 3, 12, hour, minute), "eu",
                              use_ampm=True),
                    spoken)


if __name__ == "__main__":
    unittest.main()
