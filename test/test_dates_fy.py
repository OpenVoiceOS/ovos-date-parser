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


# ---------------------------------------------------------------------------
# extract_datetime_fy / extract_duration_fy
#
# Temporal vocabulary is grounded in downloaded canonical sources:
#   ~/AgentWorkspaces/papers/linguistics/fy/wikivoyage_phrasebook.html
#     (hjoed=today, moarn=tomorrow, juster=yesterday, wike=week,
#      moanne=month, jier=year, dei=day, "dizze/ôfrûne/oare wike",
#      no=now, morning/afternoon/evening/night)
#   ~/AgentWorkspaces/papers/linguistics/fy/wiktionary_juster.html
#     (Wiktionary "juster" — West Frisian adverb "yesterday")
#
# The anchor is a Tuesday (2017-06-27 13:04). Past markers ("juster",
# "foarige", "ôfrûne", "eargister") must resolve strictly backwards.
import ovos_date_parser as _odp
from ovos_date_parser.dates_fy import (
    extract_datetime_fy, extract_duration_fy
)

_ANCHOR = datetime(2017, 6, 27, 13, 4)  # Tuesday


def _ex(text, anchor=_ANCHOR):
    return extract_datetime_fy(text, anchorDate=anchor)


def _dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s)


class TestFrisianExtractDatetime(unittest.TestCase):
    def test_today(self):
        self.assertEqual(_ex("wat dogge wy hjoed"), [_dt(2017, 6, 27),
                                                     "wat dogge wy"])

    def test_tomorrow(self):
        self.assertEqual(_ex("moarn")[0], _dt(2017, 6, 28))

    def test_day_after_tomorrow(self):
        self.assertEqual(_ex("oaremoarn")[0], _dt(2017, 6, 29))

    def test_yesterday_is_backward(self):
        self.assertEqual(_ex("wat ite wy juster"), [_dt(2017, 6, 26),
                                                    "wat ite wy"])

    def test_day_before_yesterday_is_backward(self):
        self.assertEqual(_ex("eargister")[0], _dt(2017, 6, 25))

    def test_offset_days(self):
        self.assertEqual(_ex("3 dagen")[0], _dt(2017, 6, 30))

    def test_offset_weeks(self):
        self.assertEqual(_ex("2 wiken")[0], _dt(2017, 7, 11))

    def test_offset_hours(self):
        self.assertEqual(_ex("oer 3 oere")[0], _dt(2017, 6, 27, 16, 4))

    def test_offset_minutes(self):
        self.assertEqual(_ex("oer 5 minuten")[0], _dt(2017, 6, 27, 13, 9))

    def test_next_week(self):
        self.assertEqual(_ex("oare wike")[0], _dt(2017, 7, 4))

    def test_last_week_is_backward(self):
        self.assertEqual(_ex("foarige wike")[0], _dt(2017, 6, 20))

    def test_last_week_ofrune_is_backward(self):
        self.assertEqual(_ex("ôfrûne wike")[0], _dt(2017, 6, 20))

    def test_next_month(self):
        self.assertEqual(_ex("oare moanne")[0], _dt(2017, 7, 27))

    def test_last_month_is_backward(self):
        self.assertEqual(_ex("foarige moanne")[0], _dt(2017, 5, 27))

    def test_next_year(self):
        self.assertEqual(_ex("oar jier")[0], _dt(2018, 6, 27))

    def test_last_year_is_backward(self):
        self.assertEqual(_ex("foarich jier")[0], _dt(2016, 6, 27))

    def test_plain_weekday(self):
        self.assertEqual(_ex("freed")[0], _dt(2017, 6, 30))

    def test_next_weekday(self):
        self.assertEqual(_ex("oare tongersdei")[0], _dt(2017, 7, 6))

    def test_last_weekday_is_backward(self):
        self.assertEqual(_ex("foarige freed")[0], _dt(2017, 6, 23))

    def test_day_month_rolls_to_next_year(self):
        self.assertEqual(_ex("5 juny")[0], _dt(2018, 6, 5))

    def test_day_month_this_year(self):
        self.assertEqual(_ex("15 july")[0], _dt(2017, 7, 15))

    def test_day_month_year(self):
        self.assertEqual(_ex("15 july 2018")[0], _dt(2018, 7, 15))

    def test_month_bare_year_keeps_year(self):
        self.assertEqual(_ex("juny 2020")[0], _dt(2020, 6, 1))

    def test_colon_time(self):
        self.assertEqual(_ex("om 15:30")[0], _dt(2017, 6, 27, 15, 30))

    def test_bare_hour_clock(self):
        self.assertEqual(_ex("moarn om 5 oere")[0], _dt(2017, 6, 28, 5))

    def test_morning_qualifier(self):
        self.assertEqual(_ex("om 9 oere moarns")[0], _dt(2017, 6, 28, 9))

    def test_afternoon_qualifier(self):
        self.assertEqual(_ex("moarn middeis")[0], _dt(2017, 6, 28, 15))


class TestFrisianAgoMarker(unittest.TestCase):
    """The West Frisian ago-postposition "lyn" negates numeric offsets.

    Source: ~/AgentWorkspaces/papers/linguistics/fy/wiktionary_lyn.html
    (Wiktionary "lyn" -> "ago", "twa jier lyn" = two years ago).
    """

    def test_weeks_ago_is_backward(self):
        self.assertEqual(_ex("2 wiken lyn")[0], _dt(2017, 6, 13))

    def test_weeks_future_stays_forward(self):
        # same phrase without "lyn" must remain forward
        self.assertEqual(_ex("2 wiken")[0], _dt(2017, 7, 11))

    def test_days_ago_is_backward(self):
        self.assertEqual(_ex("3 dagen lyn")[0], _dt(2017, 6, 24))

    def test_months_ago_is_backward(self):
        self.assertEqual(_ex("2 moannen lyn")[0], _dt(2017, 4, 27))

    def test_years_ago_is_backward(self):
        self.assertEqual(_ex("2 jierren lyn")[0], _dt(2015, 6, 27))

    def test_minutes_ago_is_backward(self):
        self.assertEqual(_ex("5 minuten lyn")[0], _dt(2017, 6, 27, 12, 59))

    def test_marker_without_number_is_not_a_date(self):
        self.assertIsNone(_ex("lyn"))
        self.assertIsNone(_ex("wiken lyn"))


class TestFrisianExtractAdversarial(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(_ex(""))

    def test_no_date(self):
        self.assertIsNone(_ex("bôle en tsiis"))

    def test_impossible_calendar_date(self):
        self.assertIsNone(_ex("31 febrewaris"))

    def test_out_of_range_clock(self):
        self.assertIsNone(_ex("om 25:00"))

    def test_absurd_offset_does_not_crash(self):
        _ex("oer 999999999999 oere")


class TestFrisianExtractRouting(unittest.TestCase):
    def test_routes_fy(self):
        self.assertEqual(
            _odp.extract_datetime("moarn", "fy", anchorDate=_ANCHOR)[0],
            _dt(2017, 6, 28))

    def test_routes_fy_region(self):
        self.assertEqual(
            _odp.extract_datetime("juster", "fy-NL", anchorDate=_ANCHOR)[0],
            _dt(2017, 6, 26))

    def test_duration_routes_fy(self):
        dur, _rem = _odp.extract_duration("wachtsje 3 oeren en 20 minuten", "fy")
        self.assertEqual(dur.total_seconds(), 3 * 3600 + 20 * 60)

    def test_duration_fy_direct(self):
        dur, _rem = extract_duration_fy("2 wiken")
        self.assertEqual(dur.days, 14)
