import unittest
from datetime import datetime, timedelta

from ovos_date_parser.dates_it import extract_datetime_it, extract_duration_it

# Tuesday, June 27, 2017, 13:04
ANCHOR = datetime(2017, 6, 27, 13, 4)


class TestExtractDatetimeIT(unittest.TestCase):
    def _dt(self, text):
        result = extract_datetime_it(text, anchorDate=ANCHOR)
        self.assertIsNotNone(result, text)
        return result[0]

    def test_day_words(self):
        self.assertEqual(self._dt("oggi").date(), ANCHOR.date())
        self.assertEqual(self._dt("domani").date(),
                         (ANCHOR + timedelta(days=1)).date())
        self.assertEqual(self._dt("ieri").date(),
                         (ANCHOR - timedelta(days=1)).date())
        self.assertEqual(self._dt("dopodomani").date(),
                         (ANCHOR + timedelta(days=2)).date())

    def test_weekday_next(self):
        # anchor is a Tuesday
        self.assertEqual(self._dt("lunedì prossimo").date(),
                         datetime(2017, 7, 10).date())

    def test_relative_weeks(self):
        self.assertEqual(self._dt("tra tre settimane").date(),
                         (ANCHOR + timedelta(days=21)).date())

    def test_explicit_date_with_year(self):
        dt = self._dt("15 giugno 2020")
        self.assertEqual((dt.year, dt.month, dt.day), (2020, 6, 15))

    def test_explicit_date_no_year(self):
        dt = self._dt("il 25 dicembre")
        self.assertEqual((dt.month, dt.day), (12, 25))

    def test_spoken_hour(self):
        # spoken clock hours must parse like their digit form
        self.assertEqual(extract_datetime_it("alle tre", anchorDate=ANCHOR),
                         extract_datetime_it("alle 3", anchorDate=ANCHOR))
        self.assertEqual(extract_datetime_it("alle ventuno", anchorDate=ANCHOR),
                         extract_datetime_it("alle 21", anchorDate=ANCHOR))

    def test_spoken_hour_with_day(self):
        # day fixed by "domani" so the hour is unambiguous
        dt = self._dt("domani alle otto")
        self.assertEqual(dt.date(), (ANCHOR + timedelta(days=1)).date())
        self.assertEqual((dt.hour, dt.minute), (8, 0))

    def test_part_of_day_applies_pm(self):
        dt = self._dt("alle quattro del pomeriggio")
        self.assertEqual((dt.hour, dt.minute), (16, 0))

    def test_half_past_spoken(self):
        dt = self._dt("metti una sveglia alle quattro e mezza")
        self.assertEqual(dt.minute, 30)
        self.assertIn(dt.hour, (4, 16))

    def test_date_and_spoken_hour_together(self):
        # trailing clock hour must not be swallowed as a year (no crash)
        dt = self._dt("appuntamento il 15 giugno alle tre")
        self.assertEqual((dt.month, dt.day), (6, 15))
        self.assertEqual(dt.hour, 15)

    def test_no_date(self):
        for junk in ["", "ciao come stai", "gattopardo", "!!!"]:
            with self.subTest(junk=junk):
                self.assertIsNone(
                    extract_datetime_it(junk, anchorDate=ANCHOR))

    def test_malformed_does_not_raise(self):
        for junk in ["alle giugno", "il 99 dicembre", "tre giugno tre",
                     "giugno alle otto", "quindici sedici diciassette"]:
            with self.subTest(junk=junk):
                # must return a value or None, never raise
                extract_datetime_it(junk, anchorDate=ANCHOR)


class TestExtractDurationIT(unittest.TestCase):
    def test_days(self):
        self.assertEqual(extract_duration_it("tre giorni")[0],
                         timedelta(days=3))

    def test_minutes(self):
        self.assertEqual(extract_duration_it("dieci minuti")[0],
                         timedelta(minutes=10))

    def test_no_duration(self):
        self.assertEqual(extract_duration_it("ciao")[0], None)


if __name__ == "__main__":
    unittest.main()
