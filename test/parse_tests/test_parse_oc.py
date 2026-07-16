import unittest
from datetime import datetime, timedelta

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

LANG = "oc"


def extract_datetime(text, anchorDate=None, lang=LANG, default_time=None):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchorDate,
                                default_time=default_time)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=default_timezone()), res[1]]
    return res


def extract_duration(text, lang=LANG):
    return _odp.extract_duration(text, lang=lang)


class TestDatetimeOC(unittest.TestCase):
    # anchor: 1998-01-01 was a thursday
    ANCHOR = datetime(1998, 1, 1)
    ANCHOR_NOON = datetime(1998, 1, 1, 12, 0)

    def test_weekday(self):
        # next friday after thursday jan 1st is jan 2nd
        self.assertEqual(
            extract_datetime("divendres", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 2, tzinfo=default_timezone()))
        # next monday after thursday jan 1st is jan 5th
        self.assertEqual(
            extract_datetime("diluns", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 5, tzinfo=default_timezone()))
        # "que ven" == next occurrence
        self.assertEqual(
            extract_datetime("diluns que ven", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 5, tzinfo=default_timezone()))

    def test_today_tomorrow_yesterday(self):
        self.assertEqual(
            extract_datetime("uèi", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("deman", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 2, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("ièr", anchorDate=self.ANCHOR)[0],
            datetime(1997, 12, 31, tzinfo=default_timezone()))
        # deman passat = day after tomorrow
        self.assertEqual(
            extract_datetime("deman passat", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 3, tzinfo=default_timezone()))
        # abans-ièr = day before yesterday
        self.assertEqual(
            extract_datetime("abans-ièr", anchorDate=self.ANCHOR)[0],
            datetime(1997, 12, 30, tzinfo=default_timezone()))

    def test_next_week(self):
        self.assertEqual(
            extract_datetime("la setmana que ven", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 8, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("la setmana passada", anchorDate=self.ANCHOR)[0],
            datetime(1997, 12, 25, tzinfo=default_timezone()))

    def test_in_x_days(self):
        # "d'aquí 5 jorns" = in 5 days
        self.assertEqual(
            extract_datetime("d'aquí 5 jorns", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 6, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("en 2 setmanas", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 15, tzinfo=default_timezone()))

    def test_month_and_year_offsets(self):
        self.assertEqual(
            extract_datetime("lo mes que ven", anchorDate=self.ANCHOR)[0],
            datetime(1998, 2, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("l'an passat", anchorDate=self.ANCHOR)[0],
            datetime(1997, 1, 1, tzinfo=default_timezone()))

    def test_explicit_dates(self):
        self.assertEqual(
            extract_datetime("lo 3 de junh", anchorDate=self.ANCHOR)[0],
            datetime(1998, 6, 3, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("11 de agost de 1998", anchorDate=self.ANCHOR)[0],
            datetime(1998, 8, 11, tzinfo=default_timezone()))

    def test_times(self):
        self.assertEqual(
            extract_datetime("a las 8 e mièja", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 8, 30, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("a las 8 e quart", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 8, 15, tzinfo=default_timezone()))
        # "a las 8 manca un quart" = 7:45
        self.assertEqual(
            extract_datetime("a las 8 manca un quart",
                             anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 7, 45, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("15:30", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 15, 30, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("miègjorn", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 12, 0, tzinfo=default_timezone()))
        # midnight resolves to the anchor day, matching the other languages
        self.assertEqual(
            extract_datetime("mièjanuèch", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 0, 0, tzinfo=default_timezone()))

    def test_time_qualifiers(self):
        self.assertEqual(
            extract_datetime("deman a las 9 del matin",
                             anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 2, 9, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("a las 8 del vespre", anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 20, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("a las 3 de l'aprèp-miègjorn",
                             anchorDate=self.ANCHOR)[0],
            datetime(1998, 1, 1, 15, 0, tzinfo=default_timezone()))

    def test_relative_time_offsets(self):
        # offsets are applied from the day's start, matching dates_gl
        self.assertEqual(
            extract_datetime("en 10 minutas", anchorDate=self.ANCHOR_NOON)[0],
            datetime(1998, 1, 1, 0, 10, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("en 3 oras", anchorDate=self.ANCHOR_NOON)[0],
            datetime(1998, 1, 1, 3, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime("en 5 segondas", anchorDate=self.ANCHOR_NOON)[0],
            datetime(1998, 1, 1, 0, 0, 5, tzinfo=default_timezone()))

    def test_no_date(self):
        self.assertIsNone(extract_datetime("adiu amics", anchorDate=self.ANCHOR))
        self.assertIsNone(extract_datetime("", anchorDate=self.ANCHOR))


class TestDurationOC(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(extract_duration("10 minutas"),
                         (timedelta(minutes=10), ""))
        self.assertEqual(extract_duration("3 jorns"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 segondas"),
                         (timedelta(seconds=25), ""))
        self.assertEqual(extract_duration("2 setmanas"),
                         (timedelta(weeks=2), ""))

    def test_singular(self):
        self.assertEqual(extract_duration("1 ora"),
                         (timedelta(hours=1), ""))
        self.assertEqual(extract_duration("1 minuta"),
                         (timedelta(minutes=1), ""))

    def test_composed(self):
        duration, _ = extract_duration(
            "3 jorns 8 oras 10 minutas e 49 segondas")
        self.assertEqual(duration,
                         timedelta(days=3, hours=8, minutes=10, seconds=49))

    def test_leftover_text(self):
        duration, rest = extract_duration("met un temporizador de 5 minutas")
        self.assertEqual(duration, timedelta(minutes=5))
        self.assertEqual(rest, "met un temporizador de")

    def test_nonstandard_units(self):
        from ovos_date_parser.duration import DAYS_IN_1_MONTH, DAYS_IN_1_YEAR
        self.assertEqual(extract_duration("1 an"),
                         (timedelta(days=DAYS_IN_1_YEAR), ""))
        self.assertEqual(extract_duration("2 mes"),
                         (timedelta(days=2 * DAYS_IN_1_MONTH), ""))

    def test_no_duration(self):
        duration, rest = extract_duration("adiu amics")
        self.assertIsNone(duration)


if __name__ == "__main__":
    unittest.main()
