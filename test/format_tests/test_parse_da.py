import unittest
from datetime import datetime, timedelta
from ovos_date_parser.dates_da import extract_duration_da, extract_datetime_da
from ovos_utils.time import now_local, DAYS_IN_1_YEAR, DAYS_IN_1_MONTH


# a Tuesday, early afternoon, used as a stable anchor for relative phrases
_ANCHOR = datetime(2017, 6, 27, 13, 0, 0)


class TestExtractDurationDA(unittest.TestCase):
    def test_single_unit(self):
        self.assertEqual(extract_duration_da("ti minutter"), (timedelta(minutes=10), ""))
        self.assertEqual(extract_duration_da("tre dage"), (timedelta(days=3), ""))
        self.assertEqual(extract_duration_da("8 timer"), (timedelta(hours=8), ""))
        self.assertEqual(extract_duration_da("ni og fyrre sekunder"), (timedelta(seconds=49), ""))

    def test_multiple_units(self):
        self.assertEqual(extract_duration_da("3 dage 8 timer 10 minutter og 49 sekunder"),
                         (timedelta(days=3, hours=8, minutes=10, seconds=49), "og"))
        self.assertEqual(extract_duration_da("2 uger 5 dage"),
                         (timedelta(weeks=2, days=5), ""))

    def test_with_extra_text(self):
        self.assertEqual(extract_duration_da("sæt en timer på fem minutter"),
                         (timedelta(minutes=5), "sæt en timer på"))
        self.assertEqual(extract_duration_da("giv besked om 1 time"),
                         (timedelta(hours=1), "giv besked om"))

    def test_non_standard_units(self):
        self.assertEqual(extract_duration_da("to måneder"), (timedelta(days=DAYS_IN_1_MONTH * 2), ""))
        self.assertEqual(extract_duration_da("1 år"), (timedelta(days=DAYS_IN_1_YEAR), ""))
        self.assertEqual(extract_duration_da("1 årti"), (timedelta(days=10 * DAYS_IN_1_YEAR), ""))
        self.assertEqual(extract_duration_da("1 århundrede"), (timedelta(days=100 * DAYS_IN_1_YEAR), ""))
        self.assertEqual(extract_duration_da("1 årtusinde"), (timedelta(days=1000 * DAYS_IN_1_YEAR), ""))

    def test_no_duration_found(self):
        self.assertEqual(extract_duration_da("der er ikke nogen tid"), (None, "der er ikke nogen tid"))
        self.assertEqual(extract_duration_da(""), None)


class TestExtractDatetimeDA(unittest.TestCase):
    def _dt(self, text):
        res = extract_datetime_da(text, anchorDate=_ANCHOR)
        self.assertIsNotNone(res, f"no datetime extracted from {text!r}")
        return res[0]

    def test_spoken_clock_hour(self):
        # spelled-out cardinal hours must be understood, not just digits
        self.assertEqual(self._dt("klokken tre").hour, 3)
        self.assertEqual(self._dt("klokken syv").hour, 7)
        self.assertEqual(self._dt("klokken ti").hour, 10)
        self.assertEqual(self._dt("klokken 19").hour, 19)

    def test_part_of_day_sets_pm(self):
        # an explicit evening hour must land in the evening, not default to 19
        self.assertEqual(self._dt("syv om aftenen").hour, 19)
        self.assertEqual(self._dt("otte om aftenen").hour, 20)
        self.assertEqual(self._dt("ni om aftenen").hour, 21)
        # morning keeps the stated hour
        self.assertEqual(self._dt("fem om morgenen").hour, 5)
        # afternoon promotes the stated hour into the afternoon
        self.assertEqual(self._dt("klokken tre om eftermiddagen").hour, 15)

    def test_date_with_spoken_time(self):
        dt = self._dt("møde den 15. juni klokken tre")
        self.assertEqual((dt.month, dt.day, dt.hour), (6, 15, 3))
        dt = self._dt("møde den 15. juni klokken tre om eftermiddagen")
        self.assertEqual((dt.month, dt.day, dt.hour), (6, 15, 15))

    def test_remainder_preserved(self):
        # non-time words survive as the returned remainder
        res = extract_datetime_da("møde den 15. juni klokken tre",
                                  anchorDate=_ANCHOR)
        self.assertEqual(res[1], "møde")

    def test_relative_offsets_spoken(self):
        self.assertEqual(self._dt("om tre timer"),
                         datetime(2017, 6, 27, 16, 0))
        self.assertEqual(self._dt("om ti minutter"),
                         datetime(2017, 6, 27, 13, 10))

    def test_tomorrow(self):
        self.assertEqual(self._dt("i morgen").date(),
                         (_ANCHOR + timedelta(days=1)).date())
        self.assertEqual(self._dt("i overmorgen").date(),
                         (_ANCHOR + timedelta(days=2)).date())

    def test_weekday(self):
        # "næste mandag" must resolve to a Monday
        self.assertEqual(self._dt("næste mandag klokken ni").weekday(), 0)
        self.assertEqual(self._dt("næste mandag klokken ni").hour, 9)

    def test_no_datetime(self):
        self.assertIsNone(extract_datetime_da("hej med dig", anchorDate=_ANCHOR))
        self.assertIsNone(extract_datetime_da("", anchorDate=_ANCHOR))

    def test_none_input(self):
        # empty string is defined to yield None
        self.assertIsNone(extract_datetime_da("", anchorDate=_ANCHOR))


if __name__ == "__main__":
    unittest.main()
