"""Basque 24-hour time, read as Euskaltzaindia Araua 35, section 5 c).

The formal reading is "Hamabostetan", "Hamabostak eta bostean",
"Hamabostak eta hamabostean", "Hamabostak eta hogeita hamarrean", "Zero
orduan / orenean" and "Zero ordua / orena eta hogeita hamarrean". Decision 5
adds "hiruretan, hirurak eta hiruan".

The EBE entry "lau (4) eta hiru (3) zenbakiak" keeps the old -r- for hiru
and lau only, "ez hamahiru / hamalau, hogeita hiru / hogeita lau":
"hamahiruetatik hogeita lauetara". It declines lau as a vowel-final word:
"lauan"."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date_time, nice_time
from ovos_date_parser.dates_eu import nice_time_inessive_eu

NOW = datetime(2020, 1, 1)
DATE = "asteartea, bi mila eta hogeita lauko martxoaren hamabia"


def inessive(hour, minute):
    return nice_time_inessive_eu(datetime(2024, 3, 12, hour, minute),
                                 use_24hour=True)


class TestBasque24HourInessive(unittest.TestCase):

    def test_araua_35_5c(self):
        for hour, minute, spoken in ((15, 0, "hamabostetan"),
                                     (15, 5, "hamabostak eta bostean"),
                                     (15, 15, "hamabostak eta hamabostean"),
                                     (15, 30,
                                      "hamabostak eta hogeita hamarrean"),
                                     (0, 0, "zero orduan"),
                                     (0, 30,
                                      "zero ordua eta hogeita hamarrean"),
                                     (3, 0, "hiruretan"),
                                     (3, 3, "hirurak eta hiruan")):
            with self.subTest(hour=hour, minute=minute):
                self.assertEqual(inessive(hour, minute), spoken)

    def test_no_r_after_hama_and_hogeita(self):
        self.assertEqual(inessive(13, 0), "hamahiruetan")
        self.assertEqual(inessive(23, 0), "hogeita hiruetan")
        self.assertEqual(inessive(4, 4), "laurak eta lauan")

    def test_date_time(self):
        self.assertEqual(
            nice_date_time(datetime(2024, 3, 12, 15, 5), "eu", now=NOW,
                           use_24hour=True),
            f"{DATE} hamabostak eta bostean")


class TestBasque24HourTime(unittest.TestCase):

    def test_nominative(self):
        for hour, minute, spoken in ((15, 0, "hamabostak"),
                                     (15, 5, "hamabostak eta bost"),
                                     (0, 30, "zero ordua eta hogeita hamar"),
                                     (13, 0, "hamahiruak")):
            with self.subTest(hour=hour, minute=minute):
                self.assertEqual(
                    nice_time(datetime(2024, 3, 12, hour, minute), "eu",
                              use_24hour=True),
                    spoken)


if __name__ == "__main__":
    unittest.main()
