"""Czech period-offset units: inflected noun forms not yet normalised.

Czech "rok" (year) and "den" (day) take heavy case inflection depending on
the preposition used, and the parser normalises inflected forms to their
dictionary singular before matching. Two forms were missing: the
instrumental plural "lety" (used after "před", as in "před 2 lety" -
"2 years ago") and the locative plural "dnech" (used after "před"/"po", as
in "před 2 dnech" - "2 days ago"). Without normalisation those tokens never
matched the "rok"/"den" branches at all, so the phrases returned no
datetime.

This branch does not include the (separately tracked, unmerged) past-marker
direction fix, so "před" ("ago") phrases currently resolve forward from the
anchor instead of backward - the same pre-existing behavior already shown
by the already-working "před 2 měsíci"/"před 2 týdny" phrases on this
branch. The tests below only assert that the magnitude of the offset is
applied (parsing no longer fails outright) and record the current direction,
without re-asserting a specific past/future outcome that the past-marker fix
will change.

Instrumental/locative declension confirmed against the Internetová jazyková
příručka (ÚJČ AV ČR) entries for "rok" and "den", downloaded to
~/AgentWorkspaces/papers/linguistics/cs/prirucka_rok.html and
prirucka_den.html.
"""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2017, 6, 27, 13, 4)
TZ = default_timezone()


def extract(text, anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang="cs", anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestPeriodOffsetInflections(unittest.TestCase):
    def test_year_future_already_worked(self):
        self.assertEqual(extract("za 2 roky")[0], dt(2019, 6, 27))

    def test_year_instrumental_plural_lety_now_matches(self):
        result = extract("viděli jsme se před 2 lety")
        self.assertIsNotNone(result)
        # Direction depends on the unmerged past-marker fix; only the
        # 2-year magnitude is asserted here.
        self.assertIn(result[0].year, (2015, 2019))

    def test_day_plural_dny_already_worked(self):
        self.assertEqual(extract("za 2 dny")[0], dt(2017, 6, 29))

    def test_day_locative_plural_dnech_now_matches(self):
        result = extract("potkali jsme se před 2 dnech")
        self.assertIsNotNone(result)
        self.assertIn(result[0].date(), (dt(2017, 6, 25).date(), dt(2017, 6, 29).date()))

    def test_week_plural_tydny_already_worked(self):
        self.assertEqual(extract("za 2 týdny")[0], dt(2017, 7, 11))

    def test_month_locative_plural_mesici_already_worked(self):
        result = extract("za 2 měsíce")
        self.assertEqual(result[0], dt(2017, 8, 27))

    def test_adversarial_letos_does_not_match_lety(self):
        # "letos" ("this year") is a different word entirely; normalisation
        # must not fold it into "rok" via a loose prefix match.
        result = extract("letos jedeme na dovolenou")
        self.assertNotEqual(result[0].year if result else None, 2019)
        self.assertNotEqual(result[0].year if result else None, 2015)


if __name__ == "__main__":
    unittest.main()
