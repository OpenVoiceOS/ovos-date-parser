import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime


class TestExtractDateTimeCS(unittest.TestCase):
    # Tuesday, 27 June 2017, 10:00
    ANCHOR = datetime(2017, 6, 27, 10, 0)

    def extract(self, text, expected_dt, expected_leftover=""):
        result = extract_datetime(text, "cs", anchorDate=self.ANCHOR)
        self.assertIsNotNone(result, text)
        self.assertEqual(result[0], expected_dt, text)
        self.assertEqual(result[1], expected_leftover, text)

    def test_today(self):
        self.extract("dnes", datetime(2017, 6, 27, 0, 0))

    def test_tomorrow(self):
        self.extract("zítra", datetime(2017, 6, 28, 0, 0))

    def test_yesterday(self):
        self.extract("včera", datetime(2017, 6, 26, 0, 0))

    def test_weekday_nominative(self):
        # anchor is Tuesday; forthcoming Friday and Monday
        self.extract("v pátek", datetime(2017, 6, 30, 0, 0))
        self.extract("v pondělí", datetime(2017, 7, 3, 0, 0))

    def test_weekday_accusative(self):
        # the natural spoken forms decline the weekday noun
        self.extract("ve středu", datetime(2017, 6, 28, 0, 0))
        self.extract("v sobotu", datetime(2017, 7, 1, 0, 0))
        self.extract("v neděli", datetime(2017, 7, 2, 0, 0))

    def test_next_weekday(self):
        self.extract("příští neděli", datetime(2017, 7, 2, 0, 0))

    def test_weekday_in_sentence(self):
        self.extract("schůzka v sobotu", datetime(2017, 7, 1, 0, 0),
                     "schůzka")

    def test_month_genitive_day(self):
        self.extract("27 ledna", datetime(2018, 1, 27, 0, 0))
        self.extract("3 července", datetime(2017, 7, 3, 0, 0))

    def test_february_genitive(self):
        # genitive of únor is irregular ("února", not "únoen")
        self.extract("15 února", datetime(2018, 2, 15, 0, 0))
        self.extract("1 února", datetime(2018, 2, 1, 0, 0))
        self.extract("28 února", datetime(2018, 2, 28, 0, 0))

    def test_february_leap_day(self):
        self.extract("29 února 2020", datetime(2020, 2, 29, 0, 0))

    def test_ordinal_day_month(self):
        self.extract("prvního května", datetime(2018, 5, 1, 0, 0))
        self.extract("druhého února", datetime(2018, 2, 2, 0, 0))
        self.extract("patnáctého února", datetime(2018, 2, 15, 0, 0))

    def test_noon(self):
        self.extract("v poledne", datetime(2017, 6, 27, 12, 0))

    def test_next_week(self):
        self.extract("příští týden", datetime(2017, 7, 4, 0, 0))

    def test_no_date(self):
        self.assertIsNone(extract_datetime("ahoj jak se máš", "cs",
                                           anchorDate=self.ANCHOR))

    def test_empty(self):
        self.assertIsNone(extract_datetime("", "cs", anchorDate=self.ANCHOR))

    def test_lang_code_variant(self):
        result = extract_datetime("zítra", "cs-cz", anchorDate=self.ANCHOR)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], datetime(2017, 6, 28, 0, 0))


if __name__ == "__main__":
    unittest.main()
