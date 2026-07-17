import unittest
from datetime import datetime

from ovos_date_parser import (
    nice_year, nice_weekday, nice_month, nice_day, nice_date,
    nice_date_time, nice_time,
)
from ovos_date_parser.dates_fy import (
    nice_time_fy, nice_weekday_fy, nice_month_fy, nice_part_of_day_fy,
    WEEKDAYS_FY, MONTHS_FY, HOURS_FY,
)

# A Tuesday, so weekday()==1
REF = datetime(2018, 6, 5, 16, 30)


class TestFrisianAnchors(unittest.TestCase):
    """Verified word<->value anchors (Wikivoyage phrasebook, Wikipedia,
    funwithfrisian time guide)."""

    def test_weekdays(self):
        expected = ["Moandei", "Tiisdei", "Woansdei", "Tongersdei",
                    "Freed", "Sneon", "Snein"]
        for i, name in enumerate(expected):
            # 2018-06-04 is a Monday
            dt = datetime(2018, 6, 4 + i)
            self.assertEqual(nice_weekday(dt, "fy"), name)

    def test_months(self):
        expected = {
            1: "Jannewaris", 2: "Febrewaris", 3: "Maart", 4: "April",
            5: "Maaie", 6: "Juny", 7: "July", 8: "Augustus",
            9: "Septimber", 10: "Oktober", 11: "Novimber", 12: "Desimber",
        }
        for m, name in expected.items():
            self.assertEqual(nice_month(datetime(2018, m, 1), "fy"), name)

    def test_time_oclock(self):
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 4, 0)), "fjouwer oere")
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 1, 0)), "ien oere")
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 12, 0)), "tolve oere")
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 0, 0)), "tolve oere")

    def test_time_quarters_and_half(self):
        # look-ahead system: half/quarter-to point to the coming hour
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 4, 15)), "kertier oer fjouweren")
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 4, 30)), "healwei fiven")
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 4, 45)), "kertier foar fiven")
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 13, 15)), "kertier oer ienen")

    def test_time_minutes(self):
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 4, 20)), "tweintich oer fjouweren")
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 4, 40)), "tweintich foar fiven")

    def test_time_24hour(self):
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 16, 15), use_24hour=True),
                         "sechstjin oere fyftjin")
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 13, 0), use_24hour=True),
                         "trettjin oere")

    def test_part_of_day(self):
        self.assertEqual(nice_part_of_day_fy(datetime(2018, 6, 5, 3)), " nachts")
        self.assertEqual(nice_part_of_day_fy(datetime(2018, 6, 5, 9)), " moarns")
        self.assertEqual(nice_part_of_day_fy(datetime(2018, 6, 5, 15)), " middeis")
        self.assertEqual(nice_part_of_day_fy(datetime(2018, 6, 5, 20)), " jûns")

    def test_date_order_is_germanic(self):
        # day month year
        self.assertEqual(nice_date(datetime(2018, 6, 5), "fy", include_weekday=False),
                         "fiif Juny twatûzenachttjin")

    def test_datetime_uses_om(self):
        self.assertIn(" om ", nice_date_time(REF, "fy"))


class TestFrisianAdversarial(unittest.TestCase):

    def test_bad_input_raises(self):
        for bad in (None, "not a date", 12345, [], {}):
            with self.assertRaises((AttributeError, TypeError)):
                nice_weekday(bad, "fy")

    def test_speech_false_is_language_neutral(self):
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 4, 30), speech=False), "4:30")
        self.assertEqual(nice_time_fy(datetime(2018, 6, 5, 16, 5), speech=False,
                                      use_24hour=True), "16:05")

    def test_lang_code_variants_route(self):
        for code in ("fy", "fy-NL", "FY", "FY-nl"):
            self.assertEqual(nice_weekday(REF, code), "Tiisdei")

    def test_leap_day(self):
        self.assertEqual(nice_month(datetime(2020, 2, 29), "fy"), "Febrewaris")
        self.assertEqual(nice_day(datetime(2020, 2, 29), "fy"), "29 Febrewaris")

    def test_bc_year(self):
        self.assertTrue(nice_year(datetime(44, 3, 15), "fy", bc=True).endswith("f.Kr."))

    def test_full_minute_sweep_never_crashes(self):
        # every wall-clock minute must produce a non-empty spoken form that
        # is anchored on a Frisian time particle
        for hour in range(24):
            for minute in range(60):
                dt = datetime(2018, 6, 5, hour, minute)
                spoken = nice_time_fy(dt)
                self.assertTrue(spoken)
                self.assertTrue(
                    "oere" in spoken or " oer " in spoken
                    or "foar" in spoken or "healwei" in spoken,
                    f"{hour}:{minute} -> {spoken}")

    def test_full_year_date_sweep_never_crashes(self):
        from datetime import timedelta
        dt = datetime(2019, 1, 1)
        seen = 0
        while dt.year == 2019:
            out = nice_date(dt, "fy")
            self.assertTrue(out)
            seen += 1
            dt = dt + timedelta(days=1)
        self.assertEqual(seen, 365)

    def test_hour_tables_complete(self):
        self.assertEqual(set(HOURS_FY), set(range(1, 13)))
        self.assertEqual(set(WEEKDAYS_FY), set(range(7)))
        self.assertEqual(set(MONTHS_FY), set(range(1, 13)))


if __name__ == "__main__":
    unittest.main()
