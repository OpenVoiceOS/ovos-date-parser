import unittest
from datetime import datetime

import pytest

from ovos_date_parser.dates_oc import (nice_year_oc, nice_weekday_oc, nice_month_oc,
                                       nice_day_oc, nice_date_oc, nice_time_oc)


class TestNiceDateTimeOC(unittest.TestCase):
    def setUp(self):
        self.test_date = datetime(2023, 6, 5, 17, 30)  # Monday, June 5, 2023, 17:30
        self.test_now = datetime(2023, 6, 5)  # Same day as test_date

    # the "e" after "mila" is set by ovos-number-parser's scale-remainder
    # joiner, not here; strict xfail until that flag flips
    @pytest.mark.xfail(reason="ovos-number-parser JOINER_ON_SCALE_REMAINDER", strict=True)
    def test_nice_year_oc(self):
        self.assertEqual(nice_year_oc(self.test_date), "dos mila vint e tres")
        self.assertEqual(nice_year_oc(self.test_date, bc=True), "dos mila vint e tres a.C.")

    def test_nice_weekday_oc(self):
        self.assertEqual(nice_weekday_oc(self.test_date), "Diluns")

    def test_nice_month_oc(self):
        self.assertEqual(nice_month_oc(self.test_date), "Junh")

    def test_nice_day_oc(self):
        self.assertEqual(nice_day_oc(self.test_date, date_format='DMY'), "5 Junh")
        self.assertEqual(nice_day_oc(self.test_date, date_format='MDY'), "Junh 5")
        self.assertEqual(nice_day_oc(self.test_date, include_month=False), "5")

    def test_nice_date_oc(self):
        self.assertEqual(nice_date_oc(self.test_date, self.test_now), "uèi")
        future_date = datetime(2023, 6, 6)
        self.assertEqual(nice_date_oc(future_date, self.test_now), "deman")
        past_date = datetime(2023, 6, 4)
        self.assertEqual(nice_date_oc(past_date, self.test_now), "ièr")

    def test_nice_time_oc(self):
        self.assertEqual(nice_time_oc(self.test_date, speech=True, use_24hour=True),
                         "dètz-e-sèt oras trenta")
        self.assertEqual(nice_time_oc(self.test_date, speech=True, use_24hour=False),
                         "cinc oras e mièja")
        self.assertEqual(nice_time_oc(self.test_date, speech=False, use_24hour=True), "17:30")
        self.assertEqual(nice_time_oc(self.test_date, speech=False, use_24hour=False), "5:30")

    # same ovos-number-parser joiner as test_nice_year_oc, inside the full
    # date-time string
    @pytest.mark.xfail(reason="ovos-number-parser JOINER_ON_SCALE_REMAINDER", strict=True)
    def test_nice_date_time_oc(self):
        from ovos_date_parser.dates_oc import nice_date_time_oc
        # the docstring example: 5 June 2018 was a Tuesday (dimarts)
        self.assertEqual(
            nice_date_time_oc(datetime(2018, 6, 5, 17, 30)),
            "dimarts, cinc de junh de dos mila dètz-e-uèch a las cinc oras e mièja")

    def test_nice_time_idioms(self):
        # quarter past: "una ora e quart"
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 13, 15)), "una ora e quart")
        # quarter to names the next hour: 1:45 -> "doas oras manca un quart"
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 1, 45)),
                         "doas oras manca un quart")
        # noon and midnight
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 12, 0)), "miègjorn")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 0, 0)), "mièjanuèch")

    def test_nice_time_ampm(self):
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 9, 5), use_ampm=True),
                         "nòu oras e cinc del matin")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 15, 0), use_ampm=True),
                         "tres oras de l'aprèp-miègjorn")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 20, 0), use_ampm=True),
                         "uèch oras del ser")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 23, 0), use_ampm=True),
                         "onze oras de la nuèch")

    def test_nice_date_year_join(self):
        # the year joins with "de", and "de" elides before abril/agost/octòbre
        self.assertEqual(nice_date_oc(datetime(2000, 4, 5), include_weekday=False),
                         "cinc d'Abril de dos mila")
        self.assertEqual(nice_date_oc(datetime(2000, 6, 5), include_weekday=False),
                         "cinc de Junh de dos mila")
        self.assertEqual(nice_date_oc(datetime(2000, 8, 5), include_weekday=False),
                         "cinc d'Agost de dos mila")
        self.assertEqual(nice_date_oc(datetime(2000, 10, 5), include_weekday=False),
                         "cinc d'Octòbre de dos mila")
        # a different month within the same year drops the year
        self.assertEqual(
            nice_date_oc(datetime(2023, 4, 5), datetime(2023, 6, 20),
                         include_weekday=False),
            "cinc d'Abril")

    def test_nice_time_24h_idioms(self):
        # midnight and noon are named, never "zèro oras" / "dotze oras"
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 0, 0), use_24hour=True),
                         "mièjanuèch")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 12, 0), use_24hour=True),
                         "miègjorn")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 0, 30), use_24hour=True),
                         "mièjanuèch e mièg")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 12, 30), use_24hour=True),
                         "miègjorn e mièg")

    def test_nice_time_half_idiom(self):
        # after the midnight/noon idioms the half is "mièg", elsewhere "mièja"
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 0, 30)),
                         "mièjanuèch e mièg")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 12, 30)),
                         "miègjorn e mièg")
        self.assertEqual(nice_time_oc(datetime(2023, 6, 5, 3, 30)),
                         "tres oras e mièja")


if __name__ == '__main__':
    unittest.main()
