"""A Portuguese numeric date after "dia" ("no dia 25/12/2023") is a date.

Unicode CLDR 49, pt.xml, short date pattern "dd/MM/y" (pt_PT medium
"dd/MM/y"): the day comes first, then the month, then the year. Expected
values are read off the sentence by hand.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 11, 12, 10, 0)


class TestPortugueseNumericDate(unittest.TestCase):
    #: sentence, expected date and time
    ROWS = [("no dia 25/12/2023 às 19h30", datetime(2023, 12, 25, 19, 30)),
            ("dia 25/12/2023", datetime(2023, 12, 25, 0, 0)),
            ("no dia 1/2/2027", datetime(2027, 2, 1, 0, 0)),
            ("no dia 25/12 às 19h30", datetime(2026, 12, 25, 19, 30))]

    def test_day_month_year(self):
        for lang in ("pt-PT", "pt-BR"):
            for text, expected in self.ROWS:
                with self.subTest(lang=lang, text=text):
                    found = extract_datetime(text, anchorDate=ANCHOR,
                                             lang=lang)
                    self.assertEqual(found[0], expected)

    def test_a_day_count_still_counts(self):
        # the legacy reader reads "dia" before a bare number as a day count;
        # that reading is unchanged
        self.assertEqual(
            extract_datetime("no dia 3 às 10h", anchorDate=ANCHOR,
                             lang="pt-PT")[0],
            datetime(2026, 11, 15, 10, 0))

    def test_a_month_above_twelve_is_no_date(self):
        for lang in ("pt-PT", "pt-BR"):
            with self.subTest(lang=lang):
                self.assertIsNone(extract_datetime(
                    "no dia 25/13/2023", anchorDate=ANCHOR, lang=lang))


if __name__ == "__main__":
    unittest.main()
