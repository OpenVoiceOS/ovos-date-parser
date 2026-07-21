"""Basque calendar-date extraction: case-inflected month/day/year forms.

Basque marks the date word, not a preposition. The canonical, recommended
composition (Euskaltzaindia Araua 37 "Data nola adierazi", approved
Donostia 1995-07-28) is "1983ko martxoaren 7an":

    * year  -> relational suffix -ko   ("2027ko")
    * month -> genitive suffix   -aren ("ekainaren")
    * day   -> inessive suffix   -an/-ean ("7an", "5ean")

The bare apposition "urtarrilak 20" is licensed only where no case suffix
is required. Weekdays take the inessive too ("datorren ostegunean").

Source (downloaded, text-verified):
    papers/linguistics/eu/INDEX.md ->
    papers/iberian/euskaltzaindia_araua37_data_nola_adierazi.pdf
    https://www.euskaltzaindia.eus/dok/arauak/Araua_0037.pdf

The anchor is a Tuesday (2017-06-27) so weekday and year-rollover maths
are unambiguous.
"""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2017, 6, 27, 13, 4, 0)  # a Tuesday
TZ = default_timezone()


def extract(text, lang="eu", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestMonthDayInessive(unittest.TestCase):
    """"ekainaren 5ean" = the 5th of June (month genitive + day inessive)."""

    def test_month_genitive_day_inessive(self):
        # June 5 is already past the June 27 anchor, so it rolls to next year
        res = extract("ekainaren 5ean")
        self.assertEqual(res[0], dt(2018, 6, 5, 0, 0))
        self.assertEqual(res[1], "")

    def test_july_20_inessive(self):
        res = extract("uztailaren 20an")
        self.assertEqual(res[0], dt(2017, 7, 20, 0, 0))
        self.assertEqual(res[1], "")

    def test_february_18_rolls_forward(self):
        res = extract("otsailaren 18an")
        self.assertEqual(res[0], dt(2018, 2, 18, 0, 0))
        self.assertEqual(res[1], "")

    def test_bare_apposition_form(self):
        # "urtarrilak 20" apposition form (Araua 37) still resolves
        self.assertEqual(extract("urtarrilak 20")[0], dt(2018, 1, 20, 0, 0))

    def test_inside_a_sentence_leaves_remainder(self):
        res = extract("bilera ekainaren 5ean izango da")
        self.assertEqual(res[0], dt(2018, 6, 5, 0, 0))
        self.assertEqual(res[1], "bilera izango da")


class TestMonthDayYear(unittest.TestCase):
    """"2027ko ekainaren 5ean" = year -ko + month genitive + day inessive."""

    def test_full_natural_date(self):
        res = extract("2027ko ekainaren 5ean")
        self.assertEqual(res[0], dt(2027, 6, 5, 0, 0))
        self.assertEqual(res[1], "")

    def test_bare_year_after(self):
        self.assertEqual(extract("ekaina 5 2027")[0], dt(2027, 6, 5, 0, 0))

    def test_year_is_not_taken_as_day(self):
        # the 4-digit year must never be parsed as the day of the month
        res = extract("2027ko ekainaren 5ean")
        self.assertEqual(res[0].year, 2027)
        self.assertEqual(res[0].day, 5)


class TestMonthYearOnly(unittest.TestCase):
    """"2027ko ekainean" = a month + year with no day -> defaults to the 1st."""

    def test_year_ko_month_inessive(self):
        res = extract("2027ko ekainean")
        self.assertEqual(res[0], dt(2027, 6, 1, 0, 0))
        self.assertEqual(res[1], "")

    def test_bare_month_year(self):
        self.assertEqual(extract("ekaina 2027")[0], dt(2027, 6, 1, 0, 0))


class TestInflectedWeekday(unittest.TestCase):
    """"datorren ostiralean" = next Friday (weekday inessive + next marker)."""

    def test_next_friday(self):
        # anchor is Tuesday 2017-06-27; the coming Friday marker adds a week
        self.assertEqual(extract("datorren ostiralean")[0], dt(2017, 7, 7, 0, 0))

    def test_last_friday(self):
        self.assertEqual(extract("aurreko ostiralean")[0], dt(2017, 6, 23, 0, 0))

    def test_ondorengo_thursday(self):
        # osteguna = Thursday; this-week Thursday is the 29th, next is +7
        self.assertEqual(extract("ondorengo ostegunean")[0], dt(2017, 7, 6, 0, 0))


class TestAdversarialNonMatches(unittest.TestCase):
    """Inflection must not turn impossible or non-date input into a date."""

    def test_impossible_inflected_days_return_none(self):
        for phrase in ("otsailaren 30ean", "urtarrilaren 45ean",
                       "otsailak 30", "maiatza 32"):
            with self.subTest(phrase=phrase):
                self.assertIsNone(extract(phrase))

    def test_oclock_is_not_a_day(self):
        # "5ak" is o'clock (plural), NOT the inessive day "5ean"
        self.assertEqual(extract("arratsaldeko 5ak")[0], dt(2017, 6, 27, 17, 0))

    def test_locative_hour_is_not_a_day(self):
        # "3etan" = at 3 o'clock, a clock time not the 3rd of the month
        res = extract("3etan")
        self.assertEqual(res[0].hour, 3)
        self.assertEqual(res[0].month, 6)  # not day-3 of some other month

    def test_non_date_returns_none(self):
        self.assertIsNone(extract("kaixo zer moduz"))


if __name__ == "__main__":
    unittest.main()
