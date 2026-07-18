"""Impossible calendar dates must return None rather than crashing.

An explicit date that does not exist on the calendar - day 30 of February,
day 31 of a thirty-day month - reaches ``datetime.strptime`` (or ``datetime``
construction) and would raise ``ValueError``. Every language extractor must
absorb that and report nothing, exactly as the calendar-hardened extractors do.

Each case is expressed in the target language's own month words. A valid date
and a real leap day (29 February 2020) are checked alongside so the guard can
never be satisfied by silently swallowing good parses.
"""
import unittest
from datetime import datetime

import ovos_date_parser as odp

ANCHOR = datetime(1998, 1, 1)

# lang -> (impossible dates, valid "15 March 2020", real leap "29 Feb 2020")
CASES = {
    "az": (["30 fevral 2020", "31 aprel 2020"], "15 mart 2020", "29 fevral 2020"),
    "cs": (["30 únor 2020", "31 duben 2020"], "15 březen 2020", "29 únor 2020"),
    "sk": (["30 február 2020", "31 apríl 2020"], "15 marec 2020", "29 február 2020"),
    "hr": (["30 veljača 2020", "31 travanj 2020"], "15 ožujak 2020", "29 veljača 2020"),
    "bg": (["30 февруари 2020", "31 април 2020"], "15 март 2020", "29 февруари 2020"),
    "el": (["30 φεβρουαριου 2020", "31 απριλιου 2020"], "15 μαρτιου 2020", "29 φεβρουαριου 2020"),
    "he": (["30 פברואר 2020", "31 אפריל 2020"], "15 מרץ 2020", "29 פברואר 2020"),
    "pl": (["30 luty 2020", "31 kwiecień 2020"], "15 marzec 2020", "29 luty 2020"),
    "ru": (["30 февраль 2020", "31 апрель 2020"], "15 март 2020", "29 февраль 2020"),
    "sl": (["30 februar 2020", "31 april 2020"], "15 marec 2020", "29 februar 2020"),
    "uk": (["30 лютий 2020", "31 квітень 2020"], "15 березень 2020", "29 лютий 2020"),
    "ms": (["30 februari 2020", "31 april 2020"], "15 mac 2020", "29 februari 2020"),
    "id": (["30 februari 2020", "31 april 2020"], "15 maret 2020", "29 februari 2020"),
    "tr": (["30 şubat 2020", "31 nisan 2020"], "15 mart 2020", "29 şubat 2020"),
}


class TestImpossibleDatesReturnNone(unittest.TestCase):
    def test_impossible_dates_return_none(self):
        for lang, (impossible, _valid, _leap) in CASES.items():
            for token in impossible:
                with self.subTest(lang=lang, token=token):
                    self.assertIsNone(
                        odp.extract_datetime(token, lang=lang, anchorDate=ANCHOR))

    def test_valid_date_still_parses(self):
        for lang, (_impossible, valid, _leap) in CASES.items():
            with self.subTest(lang=lang, token=valid):
                res = odp.extract_datetime(valid, lang=lang, anchorDate=ANCHOR)
                self.assertIsNotNone(res, valid)
                self.assertEqual(res[0].strftime("%Y-%m-%d"), "2020-03-15")

    def test_real_leap_day_still_parses(self):
        for lang, (_impossible, _valid, leap) in CASES.items():
            with self.subTest(lang=lang, token=leap):
                res = odp.extract_datetime(leap, lang=lang, anchorDate=ANCHOR)
                self.assertIsNotNone(res, leap)
                self.assertEqual(res[0].strftime("%Y-%m-%d"), "2020-02-29")


if __name__ == "__main__":
    unittest.main()
