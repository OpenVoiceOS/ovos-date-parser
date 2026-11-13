"""A Portuguese numeric date after "dia" ("no dia 25/12/2023") is a date.

Unicode CLDR 49 short date patterns put the day first: pt_PT "dd/MM/yy",
pt "dd/MM/y". A two-digit year falls in the 100 years from 80 before the
anchor to 19 after it, the window chronologia uses. Expected values are read
off the sentence by hand.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime
from ovos_date_parser.dates_pt import extract_datetime_pt

ANCHOR = datetime(2026, 11, 12, 10, 0)


class TestPortugueseNumericDate(unittest.TestCase):
    #: sentence, expected date and time
    ROWS = [("no dia 25/12/2023 às 19h30", datetime(2023, 12, 25, 19, 30)),
            ("dia 25/12/2023", datetime(2023, 12, 25, 0, 0)),
            ("no dia 1/2/2027", datetime(2027, 2, 1, 0, 0)),
            ("no dia 25/12 às 19h30", datetime(2026, 12, 25, 19, 30)),
            ("dia 24/12/26 às 20h", datetime(2026, 12, 24, 20, 0)),
            ("dia 24/12/2026 às 20h", datetime(2026, 12, 24, 20, 0)),
            ("no dia 24/12/99", datetime(1999, 12, 24, 0, 0)),
            ("no dia 1/1/45", datetime(2045, 1, 1, 0, 0)),
            ("no dia 1/1/46", datetime(1946, 1, 1, 0, 0))]

    def test_day_month_year(self):
        for lang in ("pt-PT", "pt-BR"):
            for text, expected in self.ROWS:
                with self.subTest(lang=lang, text=text):
                    found = extract_datetime(text, anchorDate=ANCHOR,
                                             lang=lang)
                    self.assertEqual(found[0], expected)

    def test_the_date_leaves_the_remainder(self):
        for lang in ("pt-PT", "pt-BR"):
            with self.subTest(lang=lang):
                self.assertEqual(
                    extract_datetime(
                        "marca reunião no dia 5/1/27 às 15h30 por favor",
                        anchorDate=ANCHOR, lang=lang),
                    [datetime(2027, 1, 5, 15, 30), "marca reunião por favor"])

    def test_a_slash_number_before_a_unit_is_no_count(self):
        # "25/12" or "1/2" before "dia", "semana", "mês" or "ano" is not a
        # whole count of that unit; the legacy reader reads no date from it
        for text in ("em 25/12, dia de natal", "daqui a 1/2 semana",
                     "daqui a 1/2 mês", "daqui a 1/2 ano", "há 1/2 ano",
                     "há 1/2 semana"):
            with self.subTest(text=text):
                self.assertIsNone(extract_datetime_pt(text,
                                                      anchorDate=ANCHOR))

    def test_a_day_of_the_month(self):
        # "no dia 3" is the next 3rd of a month (ruling 13 of the chronologia
        # disagreement classes); pt routes to chronologia, which reads it.
        self.assertEqual(
            extract_datetime("no dia 3 às 10h", anchorDate=ANCHOR,
                             lang="pt-PT")[0],
            datetime(2026, 12, 3, 10, 0))

    def test_a_month_above_twelve_is_no_date(self):
        for lang in ("pt-PT", "pt-BR"):
            with self.subTest(lang=lang):
                self.assertIsNone(extract_datetime(
                    "no dia 25/13/2023", anchorDate=ANCHOR, lang=lang))


if __name__ == "__main__":
    unittest.main()
