import unittest
from datetime import datetime, timedelta

from ovos_utils.time import DAYS_IN_1_MONTH, DAYS_IN_1_YEAR

from ovos_date_parser.dates_ro import extract_datetime_ro, extract_duration_ro

# Tuesday, June 27, 2017, 13:04
ANCHOR = datetime(2017, 6, 27, 13, 4)


class TestExtractDatetimeRO(unittest.TestCase):
    def _date(self, text):
        result = extract_datetime_ro(text, anchorDate=ANCHOR)
        self.assertIsNotNone(result, text)
        return result[0]

    def test_day_words(self):
        self.assertEqual(self._date("azi").date(), ANCHOR.date())
        self.assertEqual(self._date("astăzi").date(), ANCHOR.date())
        self.assertEqual(self._date("mâine").date(),
                         (ANCHOR + timedelta(days=1)).date())
        self.assertEqual(self._date("ieri").date(),
                         (ANCHOR - timedelta(days=1)).date())
        self.assertEqual(self._date("poimâine").date(),
                         (ANCHOR + timedelta(days=2)).date())
        self.assertEqual(self._date("alaltăieri").date(),
                         (ANCHOR - timedelta(days=2)).date())

    def test_weekdays(self):
        # anchor is a Tuesday
        self.assertEqual(self._date("vineri").date(),
                         datetime(2017, 6, 30).date())
        self.assertEqual(self._date("luni").date(),
                         datetime(2017, 7, 3).date())
        self.assertEqual(self._date("sâmbătă").date(),
                         datetime(2017, 7, 1).date())
        self.assertEqual(self._date("luni viitoare").date(),
                         datetime(2017, 7, 10).date())

    def test_weeks(self):
        self.assertEqual(self._date("săptămâna viitoare").date(),
                         (ANCHOR + timedelta(days=7)).date())
        self.assertEqual(self._date("săptămâna trecută").date(),
                         (ANCHOR - timedelta(days=7)).date())

    def test_relative_days(self):
        self.assertEqual(self._date("peste 3 zile").date(),
                         (ANCHOR + timedelta(days=3)).date())
        # spoken numbers
        self.assertEqual(self._date("peste trei zile").date(),
                         (ANCHOR + timedelta(days=3)).date())
        self.assertEqual(self._date("peste douăzeci și una de zile").date(),
                         (ANCHOR + timedelta(days=21)).date())

    def test_month_year_offsets(self):
        self.assertEqual(self._date("luna viitoare").month, 7)
        self.assertEqual(self._date("anul viitor").year, 2018)
        self.assertEqual(self._date("anul trecut").year, 2016)

    def test_explicit_dates(self):
        self.assertEqual(self._date("3 martie").date(),
                         datetime(2018, 3, 3).date())
        self.assertEqual(self._date("pe 15 august").date(),
                         datetime(2017, 8, 15).date())
        self.assertEqual(self._date("11 august 1998").date(),
                         datetime(1998, 8, 11).date())

    def test_may_needs_numeric_context(self):
        # "mai" is a month only next to a number
        self.assertEqual(self._date("3 mai").date(),
                         datetime(2018, 5, 3).date())
        self.assertIsNone(extract_datetime_ro("mai vorbim",
                                              anchorDate=ANCHOR))
        self.assertIsNone(extract_datetime_ro("vreau mai mult",
                                              anchorDate=ANCHOR))

    def test_times(self):
        self.assertEqual(self._date("la ora opt").time().hour, 8)
        dt = self._date("opt și jumătate")
        self.assertEqual((dt.hour, dt.minute), (8, 30))
        dt = self._date("opt și un sfert")
        self.assertEqual((dt.hour, dt.minute), (8, 15))
        # "fără" = minus: quarter to nine is 8:45
        dt = self._date("nouă fără un sfert")
        self.assertEqual((dt.hour, dt.minute), (8, 45))
        dt = self._date("nouă fără zece")
        self.assertEqual((dt.hour, dt.minute), (8, 50))
        dt = self._date("la 17:30")
        self.assertEqual((dt.hour, dt.minute), (17, 30))

    def test_time_of_day_periods(self):
        dt = self._date("mâine la ora 8 dimineața")
        self.assertEqual((dt.date(), dt.hour),
                         ((ANCHOR + timedelta(days=1)).date(), 8))
        dt = self._date("mâine la ora 8 seara")
        self.assertEqual((dt.date(), dt.hour),
                         ((ANCHOR + timedelta(days=1)).date(), 20))
        self.assertEqual(self._date("la prânz").hour, 12)
        self.assertEqual(self._date("la miezul nopții").hour, 0)

    def test_relative_time(self):
        self.assertEqual(self._date("peste 10 minute"),
                         ANCHOR + timedelta(minutes=10))
        self.assertEqual(self._date("peste două ore"),
                         ANCHOR + timedelta(hours=2))
        self.assertEqual(self._date("peste 30 de secunde"),
                         ANCHOR + timedelta(seconds=30))

    def test_no_date(self):
        self.assertIsNone(extract_datetime_ro("salut ce faci",
                                              anchorDate=ANCHOR))
        self.assertIsNone(extract_datetime_ro("", anchorDate=ANCHOR))


class TestExtractDurationRO(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(extract_duration_ro("10 minute"),
                         (timedelta(minutes=10), ""))
        self.assertEqual(extract_duration_ro("3 zile"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration_ro("25 de ore"),
                         (timedelta(hours=25), ""))
        self.assertEqual(extract_duration_ro("2 săptămâni"),
                         (timedelta(weeks=2), ""))

    def test_spoken_numbers(self):
        self.assertEqual(extract_duration_ro("zece minute"),
                         (timedelta(minutes=10), ""))
        self.assertEqual(extract_duration_ro("douăzeci și cinci de minute"),
                         (timedelta(minutes=25), ""))

    def test_singular_units(self):
        self.assertEqual(extract_duration_ro("un minut"),
                         (timedelta(minutes=1), ""))
        self.assertEqual(extract_duration_ro("o oră"),
                         (timedelta(hours=1), ""))
        self.assertEqual(extract_duration_ro("o zi"),
                         (timedelta(days=1), ""))
        self.assertEqual(extract_duration_ro("o secundă"),
                         (timedelta(seconds=1), ""))

    def test_half_and_quarter_hour(self):
        self.assertEqual(extract_duration_ro("jumătate de oră"),
                         (timedelta(minutes=30), ""))
        self.assertEqual(extract_duration_ro("un sfert de oră"),
                         (timedelta(minutes=15), ""))

    def test_combined(self):
        duration, _ = extract_duration_ro(
            "3 zile 8 ore 10 minute și 49 de secunde")
        self.assertEqual(duration,
                         timedelta(days=3, hours=8, minutes=10, seconds=49))

    def test_months_luni_numeric_context(self):
        # "luni" is the month unit only with a number in front
        self.assertEqual(extract_duration_ro("3 luni"),
                         (timedelta(days=3 * DAYS_IN_1_MONTH), ""))
        duration, remainder = extract_duration_ro("ne vedem luni")
        self.assertIsNone(duration)
        self.assertEqual(remainder, "ne vedem luni")

    def test_non_standard_units(self):
        self.assertEqual(extract_duration_ro("un an")[0],
                         timedelta(days=DAYS_IN_1_YEAR))
        self.assertEqual(extract_duration_ro("2 ani")[0],
                         timedelta(days=2 * DAYS_IN_1_YEAR))
        self.assertEqual(extract_duration_ro("un deceniu")[0],
                         timedelta(days=10 * DAYS_IN_1_YEAR))

    def test_remainder(self):
        duration, remainder = extract_duration_ro(
            "pornește un cronometru de 5 minute")
        self.assertEqual(duration, timedelta(minutes=5))
        # normalization spells numerals as digits, including "un"
        self.assertEqual(remainder, "pornește 1 cronometru de")

    def test_no_duration(self):
        self.assertEqual(extract_duration_ro("salut ce faci"),
                         (None, "salut ce faci"))


if __name__ == "__main__":
    unittest.main()
