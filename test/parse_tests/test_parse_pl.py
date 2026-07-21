import datetime
import unittest

from ovos_config.locale import get_default_tz as default_timezone

from ovos_date_parser import extract_datetime, extract_duration


def _anchor():
    # Tuesday, 27 June 2017, 13:04 local
    return datetime.datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())


class TestExtractDatetimePolishMonths(unittest.TestCase):
    """Genitive month names with spoken ordinal days.

    "piętnastego stycznia" means the 15th of January and must not raise.
    """

    def _extract(self, text):
        return extract_datetime(text, anchorDate=_anchor(), lang="pl")

    def test_spoken_ordinal_day_with_month(self):
        cases = {
            'piętnastego stycznia': (2018, 1, 15),
            'dwudziestego lutego': (2018, 2, 20),
            'trzeciego sierpnia': (2017, 8, 3),
            'pierwszego stycznia': (2018, 1, 1),
            'dwudziestego pierwszego marca': (2018, 3, 21),
            'trzydziestego kwietnia': (2018, 4, 30),
            'trzydziestego pierwszego grudnia': (2017, 12, 31),
        }
        for text, (y, m, d) in cases.items():
            with self.subTest(text=text):
                res = self._extract(text)
                self.assertIsNotNone(res)
                self.assertEqual((res[0].year, res[0].month, res[0].day),
                                 (y, m, d))

    def test_numeric_day_with_month(self):
        res = self._extract('15 stycznia 2020')
        self.assertEqual((res[0].year, res[0].month, res[0].day),
                         (2020, 1, 15))

    def test_bare_month_does_not_crash(self):
        # a month with no parseable day must degrade, not raise
        res = self._extract('stycznia')
        self.assertIsNotNone(res)
        self.assertEqual(res[0].month, 1)


class TestExtractDatetimePolishLeapDay(unittest.TestCase):
    """29 February must resolve to a leap year, not raise."""

    def _extract(self, text):
        return extract_datetime(text, anchorDate=_anchor(), lang="pl")

    def test_leap_day_no_year(self):
        for text in ['29 lutego', 'dwudziestego dziewiątego lutego']:
            with self.subTest(text=text):
                res = self._extract(text)
                self.assertEqual((res[0].year, res[0].month, res[0].day),
                                 (2020, 2, 29))

    def test_leap_day_with_valid_year(self):
        res = self._extract('29 lutego 2020')
        self.assertEqual((res[0].year, res[0].month, res[0].day),
                         (2020, 2, 29))


class TestExtractDatetimePolishRelative(unittest.TestCase):
    def _extract(self, text):
        return extract_datetime(text, anchorDate=_anchor(), lang="pl")

    def test_weekdays_accusative(self):
        cases = {
            'we wtorek': (2017, 6, 27),
            'w środę': (2017, 6, 28),
            'w piątek': (2017, 6, 30),
        }
        for text, (y, m, d) in cases.items():
            with self.subTest(text=text):
                res = self._extract(text)
                self.assertEqual((res[0].year, res[0].month, res[0].day),
                                 (y, m, d))

    def test_relative_days(self):
        self.assertEqual(self._extract('pojutrze')[0].day, 29)
        self.assertEqual(self._extract('przedwczoraj')[0].day, 25)

    def test_part_of_day_applies_hour(self):
        self.assertEqual(self._extract('jutro rano')[0].hour, 8)
        self.assertEqual(self._extract('jutro wieczorem')[0].hour, 19)
        self.assertEqual(self._extract('dzisiaj po południu')[0].hour, 15)

    def test_digit_offsets(self):
        self.assertEqual(self._extract('za 5 minut')[0].strftime("%H:%M"),
                         "13:09")
        self.assertEqual(self._extract('za 2 godziny')[0].strftime("%H:%M"),
                         "15:04")


class TestExtractDatetimePolishAdversarial(unittest.TestCase):
    def test_empty_and_no_date(self):
        for text in ['', 'cześć jak się masz', '   ']:
            with self.subTest(text=text):
                self.assertIsNone(
                    extract_datetime(text, anchorDate=_anchor(), lang="pl"))


class TestExtractDurationPolish(unittest.TestCase):
    def test_durations(self):
        self.assertEqual(
            extract_duration('ustaw minutnik na pięć minut', lang="pl")[0],
            datetime.timedelta(minutes=5))
        self.assertEqual(
            extract_duration('trzy dni', lang="pl")[0],
            datetime.timedelta(days=3))
        self.assertEqual(
            extract_duration('za dwie godziny', lang="pl")[0],
            datetime.timedelta(hours=2))


if __name__ == "__main__":
    unittest.main()
