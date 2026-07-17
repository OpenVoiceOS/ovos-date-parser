"""Basque datetime extraction: relative offsets, clock words and edge cases."""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2117, 9, 3, 13, 30, 0)
TZ = default_timezone()


def extract(text, lang="eu", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestRelativeFuture(unittest.TestCase):
    """"<n> <unit> barru" means "in <n> <unit>" and keeps the anchor clock."""

    def test_seconds(self):
        res = extract("15 segundo barru")
        self.assertEqual(res[0], dt(2117, 9, 3, 13, 30, 15))
        self.assertEqual(res[1], "")

    def test_minutes(self):
        res = extract("15 minutu barru")
        self.assertEqual(res[0], dt(2117, 9, 3, 13, 45, 0))
        self.assertEqual(res[1], "")

    def test_hours(self):
        res = extract("3 ordu barru")
        self.assertEqual(res[0], dt(2117, 9, 3, 16, 30, 0))
        self.assertEqual(res[1], "")

    def test_one_minute(self):
        self.assertEqual(extract("1 minutu barru")[0], dt(2117, 9, 3, 13, 31, 0))

    def test_one_hour(self):
        self.assertEqual(extract("1 ordu barru")[0], dt(2117, 9, 3, 14, 30, 0))

    def test_one_second(self):
        self.assertEqual(extract("1 segundo barru")[0], dt(2117, 9, 3, 13, 30, 1))

    def test_five_minutes(self):
        self.assertEqual(extract("5 minutu barru")[0], dt(2117, 9, 3, 13, 35, 0))

    def test_marker_consumed(self):
        for phrase in ("15 segundo barru", "15 minutu barru", "3 ordu barru"):
            with self.subTest(phrase=phrase):
                self.assertEqual(extract(phrase)[1], "")


class TestRelativeAndClock(unittest.TestCase):
    """Absolute day words reset the clock; part-of-day shifts to pm."""

    def test_afternoon_hour(self):
        self.assertEqual(extract("arratsaldeko 5ak")[0], dt(2117, 9, 3, 17, 0))

    def test_bare_day_words(self):
        self.assertEqual(extract("bihar")[0], dt(2117, 9, 4, 0, 0))
        self.assertEqual(extract("gaur")[0], dt(2117, 9, 3, 0, 0))
        self.assertEqual(extract("atzo")[0], dt(2117, 9, 2, 0, 0))


class TestImpossibleDates(unittest.TestCase):
    """Impossible or empty inputs must return None, never crash."""

    def test_impossible_dates_return_none(self):
        for phrase in ("otsailak 30", "urtarrilak 45", "", "xyzzy", "ordu barru"):
            with self.subTest(phrase=phrase):
                self.assertIsNone(extract(phrase))


if __name__ == "__main__":
    unittest.main()
