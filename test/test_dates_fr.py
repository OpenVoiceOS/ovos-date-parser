"""French datetime extraction: natural phrasing, clock notation and edge cases.

Anchors verified against French usage (24-hour clock, "1er" for the first of
the month), not pinned from engine output.
"""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2117, 9, 3, 13, 30)  # a fixed non-midnight anchor
TZ = default_timezone()


def extract(text, lang="fr", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0):
    return datetime(y, mo, d, h, mi, tzinfo=TZ)


class TestClockNotation(unittest.TestCase):
    """The "h" hour separator is the standard French clock notation."""

    def test_bare_hour_h_suffix(self):
        self.assertEqual(extract("20h")[0], dt(2117, 9, 3, 20))

    def test_a_hour_h_suffix(self):
        self.assertEqual(extract("à 20h")[0], dt(2117, 9, 3, 20))

    def test_hour_minute_h_separator(self):
        self.assertEqual(extract("20h30")[0], dt(2117, 9, 3, 20, 30))

    def test_spelled_hours(self):
        self.assertEqual(extract("à trois heures")[0].hour, 3)


class TestOrdinalFirstOfMonth(unittest.TestCase):
    """"1er" is the ordinary way to say the first day of a month."""

    def test_premier_janvier(self):
        self.assertEqual(extract("1er janvier")[0], dt(2118, 1, 1))

    def test_le_premier_janvier(self):
        self.assertEqual(extract("le 1er janvier")[0], dt(2118, 1, 1))

    def test_premier_janvier_with_time(self):
        self.assertEqual(extract("1er janvier à 20h")[0], dt(2118, 1, 1, 20))

    def test_plain_day_month(self):
        self.assertEqual(extract("15 juillet")[0], dt(2118, 7, 15))


class TestRelativeOffsets(unittest.TestCase):
    """Relative offsets keep the anchor time of day."""

    def test_in_hours(self):
        self.assertEqual(extract("dans 3 heures")[0], dt(2117, 9, 3, 16, 30))

    def test_in_minutes(self):
        self.assertEqual(extract("dans 10 minutes")[0], dt(2117, 9, 3, 13, 40))


class TestAdversarial(unittest.TestCase):
    """Malformed digit-leading tokens must not crash the extractor."""

    def test_digit_letter_tokens(self):
        for token in ["10sept", "7d", "5m", "20h99z"]:
            with self.subTest(token=token):
                # must not raise; a non-time gibberish token yields no match
                extract(token)

    def test_slash_date_tokens(self):
        for token in ["15/06/20", "3/0/0", "0/0/0"]:
            with self.subTest(token=token):
                extract(token)

    def test_empty_and_gibberish(self):
        self.assertIsNone(extract(""))
        self.assertIsNone(extract("   "))
        self.assertIsNone(extract("azerty qwerty"))

    def test_impossible_hour_no_crash(self):
        res = extract("à 99h")
        if res is not None and res[0] is not None:
            self.assertNotEqual(res[0].hour, 99)

    def test_impossible_dates_return_none(self):
        for token in ["30 février", "31 avril", "30 février 2020",
                      "février 30", "31 avril 2020"]:
            with self.subTest(token=token):
                self.assertIsNone(extract(token))

    def test_valid_dates_still_parse(self):
        self.assertEqual(extract("15 juillet 2020")[0], dt(2020, 7, 15))


class TestYesterdayWords(unittest.TestCase):
    """"hier": le jour qui précède immédiatement celui où l'on est
    (Larousse, papers/linguistics/french/larousse_hier.html).  Regression
    for the three-way differential lead: "hier"/"avant-hier" returned
    None while "ontem"/"ayer" worked in the sibling languages."""

    def test_hier(self):
        self.assertEqual(extract("hier")[0], dt(2117, 9, 2))
        self.assertEqual(extract("avant-hier")[0], dt(2117, 9, 1))

    def test_in_sentences(self):
        res = extract("que s'est-il passé hier")
        self.assertEqual(res[0], dt(2117, 9, 2))
        res = extract("le match d'avant-hier")
        self.assertEqual(res[0], dt(2117, 9, 1))

    def test_hier_with_time(self):
        self.assertEqual(extract("hier à 17 heures")[0],
                         dt(2117, 9, 2, 17, 0))

    def test_symmetry_with_demain(self):
        # demain/hier must be symmetric around the anchor day
        self.assertEqual((extract("demain")[0] - extract("hier")[0]).days, 2)


if __name__ == "__main__":
    unittest.main()
