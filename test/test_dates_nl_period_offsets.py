"""Dutch period-offset units: singular and plural noun matching.

Dutch pluralizes "maand" (month) as "maanden" and "jaar" (year) as "jaren";
those plurals go through irregular/en-suffixed forms rather than a simple
"-en" strip, so the parser must list them explicitly alongside the singular.
"week"/"weken" and "dag"/"dagen" already covered both forms.

Plurals confirmed against Woordenlijst.org headword entries, downloaded to
~/AgentWorkspaces/papers/linguistics/nl/woorden_maanden.html and
woorden_jaren.html.
"""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2017, 6, 27, 13, 4)
TZ = default_timezone()


def extract(text, anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang="nl", anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestPeriodOffsetPlurals(unittest.TestCase):
    def test_month_singular(self):
        self.assertEqual(extract("over 1 maand")[0], dt(2017, 7, 27))

    def test_month_plural(self):
        self.assertEqual(extract("ik zie je over 2 maanden")[0], dt(2017, 8, 27))

    def test_year_singular(self):
        self.assertEqual(extract("over 1 jaar")[0], dt(2018, 6, 27))

    def test_year_plural(self):
        self.assertEqual(extract("we spreken af over 2 jaren")[0], dt(2019, 6, 27))

    def test_week_plural_already_worked(self):
        self.assertEqual(extract("over 2 weken")[0], dt(2017, 7, 11))

    def test_day_plural_already_worked(self):
        self.assertEqual(extract("over 2 dagen")[0], dt(2017, 6, 29))

    def test_adversarial_maanden_as_substring_does_not_match(self):
        # "maandenlang" is a different word (adjective "months-long"); the
        # exact-token match must not fire on it.
        self.assertIsNone(extract("dit duurt maandenlang"))

    def test_adversarial_bare_number_without_unit_does_not_offset(self):
        # No unit noun at all -> no month/year offset should be inferred.
        res = extract("2")
        self.assertNotEqual(res[0] if res else None, dt(2019, 6, 27))
        self.assertNotEqual(res[0] if res else None, dt(2017, 8, 27))


if __name__ == "__main__":
    unittest.main()
