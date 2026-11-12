"""Brazilian Portuguese spells 16, 17 and 19 apart from European Portuguese.

Dicionário Priberam da Língua Portuguesa, "dezesseis": "Grafia no Brasil:
dezesseis. Grafia em Portugal: dezasseis." The entries "dezessete" and
"dezenove" give "dezessete"/"dezassete" and "dezenove"/"dezanove" the same
way. A pt-BR tag reads the Brazilian forms in the year, the day and the clock;
every other Portuguese tag keeps the European forms."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date, nice_date_time, nice_time, nice_year

DT = datetime(2016, 3, 16, 16, 17)
NOW = datetime(2016, 1, 1)


class TestBrazilianNumbers(unittest.TestCase):

    def test_year(self):
        self.assertEqual(nice_year(DT, "pt-BR"), "dois mil e dezesseis")
        self.assertEqual(nice_year(datetime(2019, 1, 1), "pt-BR"),
                         "dois mil e dezenove")

    def test_day(self):
        self.assertEqual(
            nice_date(DT, "pt-BR", now=NOW, include_weekday=False),
            "dezesseis de março")

    def test_time_24_hour(self):
        self.assertEqual(nice_time(DT, "pt-BR", use_24hour=True),
                         "dezesseis e dezessete")
        self.assertEqual(
            nice_time(datetime(2016, 3, 16, 19, 16), "pt-BR",
                      use_24hour=True),
            "dezenove e dezesseis")

    def test_time_12_hour(self):
        self.assertEqual(nice_time(DT, "pt-BR"), "quatro e dezessete")

    def test_date_time(self):
        self.assertEqual(
            nice_date_time(DT, "pt-BR", now=NOW, use_24hour=True),
            "quarta-feira, dezesseis de março às dezesseis e dezessete")

    def test_tag_spellings(self):
        for tag in ("pt-br", "pt_BR", "pt-Latn-BR"):
            with self.subTest(tag=tag):
                self.assertEqual(nice_year(DT, tag), "dois mil e dezesseis")


class TestEuropeanNumbers(unittest.TestCase):

    def test_other_tags_keep_the_european_forms(self):
        for tag in ("pt", "pt-PT", "pt-AO", "pt-MZ"):
            with self.subTest(tag=tag):
                self.assertEqual(nice_year(DT, tag), "dois mil e dezasseis")
                self.assertEqual(nice_time(DT, tag, use_24hour=True),
                                 "dezasseis e dezassete")
                self.assertEqual(
                    nice_date_time(DT, tag, now=NOW, use_24hour=True),
                    "quarta-feira, dezasseis de março às dezasseis e "
                    "dezassete")


if __name__ == "__main__":
    unittest.main()
