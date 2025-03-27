import unittest
from datetime import timedelta
from ovos_date_parser.dates_da import extract_duration_da
from ovos_utils.time import now_local, DAYS_IN_1_YEAR, DAYS_IN_1_MONTH


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
        self.assertEqual(extract_duration_da(""), (None, ""))


if __name__ == "__main__":
    unittest.main()
