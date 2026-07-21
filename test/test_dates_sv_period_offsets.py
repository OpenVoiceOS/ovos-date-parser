"""Swedish period-offset units: singular and plural noun matching.

Swedish pluralizes "månad" (month) as "månader"; "vecka"/"veckor" and
"dag"/"dagar" already covered both forms, and "år" (year) is invariant
between singular and plural.

Plural confirmed against the Wiktionary "månader" entry, downloaded to
~/AgentWorkspaces/papers/linguistics/sv/wiktionary_manader.html.
"""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2017, 6, 27, 13, 4)
TZ = default_timezone()


def extract(text, anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang="sv", anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestPeriodOffsetPlurals(unittest.TestCase):
    def test_month_singular(self):
        self.assertEqual(extract("om 1 månad")[0], dt(2017, 7, 27))

    def test_month_plural(self):
        self.assertEqual(extract("vi ses om 2 månader")[0], dt(2017, 8, 27))

    def test_week_plural_already_worked(self):
        self.assertEqual(extract("om 2 veckor")[0], dt(2017, 7, 11))

    def test_day_plural_already_worked(self):
        self.assertEqual(extract("om 2 dagar")[0], dt(2017, 6, 29))

    def test_year_invariant_plural(self):
        self.assertEqual(extract("om 2 år")[0], dt(2019, 6, 27))

    def test_adversarial_manadsvis_does_not_match(self):
        # "månadsvis" (monthly, adverb) must not fire the month-offset match.
        self.assertIsNone(extract("hon betalar hyran månadsvis"))


if __name__ == "__main__":
    unittest.main()
