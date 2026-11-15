"""Basque time in the inessive case, as nice_date_time writes it.

Euskaltzaindia Araua 35, "Orduak nola esan" (Bilbo, 1995), decides:

1. "ordu bata, ordu biak, hirurak, laurak, bostak, seiak, zazpiak", and in
   the inessive "ordu batean, bietan / ordu bietan, ... hiruretan".
2. "bost eta erdiak", "ordu bat eta erdietan", "bost eta erdietan".
3. "hirurak eta laurden", "hirurak eta laurdenetan".
4. "hamarrak hamar gutxitan", "seiak eta bostean", "laurak eta hogeian",
   "hirurak eta hemezortzian". Section 4 adds "hamarrak eta hamarrean".

The EBE entry "orduak nola esan" marks "*seirak, *zazpirak, *zortzirak" and
"*zortziretan" wrong, and gives "zortziak, zortzietan". Elhuyar gives "a las
siete en punto: zazpietan puntuan"."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date_time, nice_time

NOW = datetime(2020, 1, 1)
DATE = "asteartea, bi mila eta hogeita lauko martxoaren hamabia"


def at(hour, minute, use_ampm=False):
    spoken = nice_date_time(datetime(2024, 3, 12, hour, minute), "eu",
                            now=NOW, use_ampm=use_ampm)
    assert spoken.startswith(DATE + " "), spoken
    return spoken[len(DATE) + 1:]


class TestBasqueHourWords(unittest.TestCase):

    def test_decision_1(self):
        for hour, spoken in ((1, "ordu bata"), (2, "ordu biak"),
                             (6, "seiak"), (7, "zazpiak"), (8, "zortziak")):
            with self.subTest(hour=hour):
                self.assertEqual(
                    nice_time(datetime(2024, 3, 12, hour, 0), "eu"),
                    f"{spoken} puntuan")

    def test_half_plural_on_erdi(self):
        self.assertEqual(nice_time(datetime(2024, 3, 12, 5, 30), "eu"),
                         "bost eta erdiak")
        self.assertEqual(nice_time(datetime(2024, 3, 12, 1, 30), "eu"),
                         "ordu bat eta erdiak")


class TestBasqueTimeInessive(unittest.TestCase):

    def test_on_the_hour(self):
        for hour, spoken in ((9, "bederatzietan puntuan"),
                             (7, "zazpietan puntuan"),
                             (8, "zortzietan puntuan"),
                             (3, "hiruretan puntuan"),
                             (1, "ordu batean puntuan"),
                             (14, "ordu bietan puntuan")):
            with self.subTest(hour=hour):
                self.assertEqual(at(hour, 0), spoken)

    def test_part_of_day(self):
        self.assertEqual(at(15, 0, use_ampm=True), "arratsaldeko hiruretan")
        self.assertEqual(at(15, 5, use_ampm=True),
                         "arratsaldeko hirurak eta bostean")

    def test_half_and_quarter(self):
        self.assertEqual(at(5, 30), "bost eta erdietan")
        self.assertEqual(at(1, 30), "ordu bat eta erdietan")
        self.assertEqual(at(3, 15), "hirurak eta laurdenetan")

    def test_minutes_before(self):
        self.assertEqual(at(9, 50), "hamarrak hamar gutxitan")
        self.assertEqual(at(4, 45), "bostak laurden gutxitan")

    def test_minutes_after(self):
        self.assertEqual(at(6, 5), "seiak eta bostean")
        self.assertEqual(at(4, 20), "laurak eta hogeian")
        self.assertEqual(at(3, 18), "hirurak eta hemezortzian")
        self.assertEqual(at(10, 10), "hamarrak eta hamarrean")

    def test_minute_ending_in_a(self):
        # Not in Araua 35: a stem with a final -a takes only -n in the
        # singular inessive, as eliza gives elizan
        self.assertEqual(at(5, 11), "bostak eta hamaikan")


if __name__ == "__main__":
    unittest.main()
