import unittest
from datetime import timedelta
from ovos_date_parser.dates_da import extract_duration_da


class TestExtractDurationDA(unittest.TestCase):
    def test_single_unit(self):
        self.assertEqual(extract_duration_da("10 minutter"), (timedelta(minutes=10), ""))
        self.assertEqual(extract_duration_da("3 dage"), (timedelta(days=3), ""))
        self.assertEqual(extract_duration_da("8 timer"), (timedelta(hours=8), ""))
        self.assertEqual(extract_duration_da("49 sekunder"), (timedelta(seconds=49), ""))

    def test_multiple_units(self):
        self.assertEqual(extract_duration_da("3 dage 8 timer 10 minutter og 49 sekunder"),
                         (timedelta(days=3, hours=8, minutes=10, seconds=49), "og"))
        self.assertEqual(extract_duration_da("2 uger 5 dage"),
                         (timedelta(weeks=2, days=5), ""))

    def test_with_extra_text(self):
        self.assertEqual(extract_duration_da("sæt en timer på 5 minutter"),
                         (timedelta(minutes=5), "sæt en timer på"))
        self.assertEqual(extract_duration_da("giv besked om en time"),
                         (timedelta(hours=1), "giv besked om"))

    def test_non_standard_units(self):
        self.assertEqual(extract_duration_da("2 måneder"), (timedelta(days=60), ""))
        self.assertEqual(extract_duration_da("1 år"), (timedelta(days=365), ""))
        self.assertEqual(extract_duration_da("1 årti"), (timedelta(days=10 * 365), ""))
        self.assertEqual(extract_duration_da("1 århundrede"), (timedelta(days=100 * 365), ""))
        self.assertEqual(extract_duration_da("1 årtusinde"), (timedelta(days=1000 * 365), ""))

    def test_no_duration_found(self):
        self.assertEqual(extract_duration_da("der er ikke nogen tid"), (None, "der er ikke nogen tid"))
        self.assertEqual(extract_duration_da(""), (None, ""))


if __name__ == "__main__":
    unittest.main()
