import datetime
import unittest

from ovos_date_parser import nice_month, nice_relative_time
from ovos_config.locale import get_default_tz as default_timezone


class TestFrenchFormatting(unittest.TestCase):
    def test_nice_relative_time_now(self):
        now = datetime.datetime(2026, 3, 8, 12, 0, tzinfo=default_timezone())
        self.assertEqual(nice_relative_time(now, now, lang="fr"), "maintenant")

    def test_nice_month_october(self):
        dt = datetime.datetime(2026, 10, 1, 12, 0, tzinfo=default_timezone())
        self.assertEqual(nice_month(dt, lang="fr"), "octobre")


if __name__ == "__main__":
    unittest.main()
