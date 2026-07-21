import unittest
from datetime import datetime, timedelta

from ovos_date_parser import (
    nice_year, nice_weekday, nice_month, nice_day, nice_date,
    nice_time, nice_date_time,
)
from ovos_date_parser.dates_an import (
    nice_date_an, WEEKDAYS_AN, MONTHS_AN,
)

# A Tuesday
REF = datetime(2018, 6, 5)


class TestAragoneseAnchors(unittest.TestCase):
    """Verified anchors: Biquipedia "Nombre d'os días d'a semana", "Semana",
    "Mes"; Aragonese Wiktionary."""

    def test_weekdays(self):
        expected = ["Luns", "Martes", "Miercres", "Chueves",
                    "Viernes", "Sabado", "Dominche"]
        for i, name in enumerate(expected):
            # 2018-06-04 is a Monday
            self.assertEqual(nice_weekday(datetime(2018, 6, 4 + i), "an"), name)

    def test_months(self):
        expected = {
            1: "Chinero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Chunyo", 7: "Chuliol", 8: "Agosto",
            9: "Setiembre", 10: "Octubre", 11: "Noviembre", 12: "Deciembre",
        }
        for m, name in expected.items():
            self.assertEqual(nice_month(datetime(2018, m, 1), "an"), name)

    def test_full_date(self):
        # weekday, day "de" month "de" year
        out = nice_date(datetime(2018, 6, 5), "an")
        self.assertTrue(out.startswith("Martes,"))
        self.assertIn("de Chunyo de", out)

    def test_date_connector_elision(self):
        # "de" elides to "d'" before a vowel-initial month, else stays "de"
        self.assertIn("d'Abril", nice_date(datetime(2018, 4, 2), "an"))
        self.assertIn("d'Agosto", nice_date(datetime(2018, 8, 2), "an"))
        self.assertIn("d'Octubre", nice_date(datetime(2018, 10, 2), "an"))
        self.assertIn("de Chinero", nice_date(datetime(2018, 1, 2), "an"))
        self.assertIn("de Deciembre", nice_date(datetime(2018, 12, 2), "an"))
        # the connector before the year is always "de"
        self.assertNotIn("d'2018", nice_date(datetime(2018, 4, 2), "an"))

    def test_date_relative_now_drops_same_year(self):
        now = datetime(2018, 6, 1)
        out = nice_date_an(datetime(2018, 6, 5), now=now)
        # same month and year -> just weekday + day
        self.assertNotIn("Chunyo", out)
        self.assertNotIn("mil", out)


class TestAragoneseClock(unittest.TestCase):
    """Spoken-clock idiom per the Aragonese review."""

    def _t(self, h, m):
        return nice_time(datetime(2018, 1, 1, h, m), "an")

    def test_on_the_hour(self):
        self.assertEqual(self._t(1, 0), "Ye la una")
        self.assertEqual(self._t(2, 0), "Son las dos")
        self.assertEqual(self._t(3, 0), "Son las tres")

    def test_half_past_counts_to_next(self):
        self.assertEqual(self._t(4, 30), "Ye la meya pa las cinco")
        self.assertEqual(self._t(7, 30), "Ye la meya pa las ueito")

    def test_quarters(self):
        self.assertEqual(self._t(4, 15), "Ye lo cuarto pa las cinco")
        self.assertEqual(self._t(4, 45), "Son los tres cuartos pa las cinco")

    def test_loose_minutes(self):
        self.assertEqual(self._t(4, 10), "Son las cuatro y diez")
        self.assertEqual(self._t(4, 50), "Son las cinco menos diez")

    def test_wraparound_to_one_and_twelve(self):
        self.assertEqual(self._t(11, 15), "Ye lo cuarto pa las doce")
        self.assertEqual(self._t(12, 15), "Ye lo cuarto pa las una")

    def test_display_form(self):
        self.assertEqual(
            nice_time(datetime(2018, 1, 1, 4, 30), "an", speech=False), "4:30")

    def test_date_time_combines(self):
        out = nice_date_time(datetime(2018, 6, 5, 4, 30), "an")
        self.assertIn("Ye la meya pa las cinco", out)
        self.assertIn("de Chunyo", out)

    def test_bad_time_input_raises(self):
        for bad in (None, "nope", 123):
            with self.assertRaises((AttributeError, TypeError)):
                nice_time(bad, "an")


class TestAragoneseAdversarial(unittest.TestCase):

    def test_bad_input_raises(self):
        for bad in (None, "not a date", 12345, [], {}):
            with self.assertRaises((AttributeError, TypeError, KeyError)):
                nice_weekday(bad, "an")

    def test_lang_code_variants_route(self):
        for code in ("an", "an-ES", "AN"):
            self.assertEqual(nice_weekday(REF, code), "Martes")

    def test_leap_day(self):
        self.assertEqual(nice_month(datetime(2020, 2, 29), "an"), "Febrero")
        self.assertEqual(nice_day(datetime(2020, 2, 29), "an"), "29 Febrero")

    def test_bc_year(self):
        self.assertTrue(nice_year(datetime(44, 3, 15), "an", bc=True).endswith("a.C."))

    def test_full_year_date_sweep_never_crashes(self):
        dt = datetime(2019, 1, 1)
        seen = 0
        while dt.year == 2019:
            out = nice_date(dt, "an")
            self.assertTrue(out)
            self.assertRegex(out, r",")  # weekday prefix + comma
            seen += 1
            dt = dt + timedelta(days=1)
        self.assertEqual(seen, 365)

    def test_tables_complete(self):
        self.assertEqual(set(WEEKDAYS_AN), set(range(7)))
        self.assertEqual(set(MONTHS_AN), set(range(1, 13)))


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# extract_datetime_an / extract_duration_an
#
# Temporal vocabulary is grounded in downloaded canonical sources:
#   ~/AgentWorkspaces/papers/linguistics/an/wiktionary_hue.html,
#   ~/AgentWorkspaces/papers/linguistics/an/glosbe_hoy.html    (hoy -> hue/güe)
#   ~/AgentWorkspaces/papers/linguistics/an/wiktionary_ahiere.html,
#   ~/AgentWorkspaces/papers/linguistics/an/glosbe_ayer.html   (ayer -> ahiere)
#   ~/AgentWorkspaces/papers/linguistics/an/glosbe_manana.html (mañana -> demá)
#   ~/AgentWorkspaces/papers/linguistics/an/glosbe_semana.html (semana)
#   ~/AgentWorkspaces/papers/linguistics/an/glosbe_proximo.html(próximo->vinient)
#   ~/AgentWorkspaces/papers/linguistics/an/glosbe_pasado.html (pasado -> pasau)
#
# The anchor is a Tuesday (2017-06-27 13:04). Past markers must resolve
# strictly backwards.
import ovos_date_parser as _odp
from ovos_date_parser.dates_an import (
    extract_datetime_an, extract_duration_an
)

_ANCHOR = datetime(2017, 6, 27, 13, 4)  # Tuesday


def _ex(text, anchor=_ANCHOR):
    return extract_datetime_an(text, anchorDate=anchor)


def _dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s)


class TestAragoneseExtractDatetime(unittest.TestCase):
    def test_today_hue(self):
        self.assertEqual(_ex("qué femos hue"), [_dt(2017, 6, 27), "qué femos"])

    def test_today_variant_gue(self):
        self.assertEqual(_ex("güe")[0], _dt(2017, 6, 27))

    def test_tomorrow(self):
        self.assertEqual(_ex("veyremos demán"), [_dt(2017, 6, 28), "veyremos"])

    def test_day_after_tomorrow(self):
        self.assertEqual(_ex("pasadoman")[0], _dt(2017, 6, 29))

    def test_yesterday_is_backward(self):
        self.assertEqual(_ex("ahiere plevió"), [_dt(2017, 6, 26), "plevió"])

    def test_yesterday_variant(self):
        self.assertEqual(_ex("ayere")[0], _dt(2017, 6, 26))

    def test_day_before_yesterday_is_backward(self):
        self.assertEqual(_ex("antesahiere")[0], _dt(2017, 6, 25))

    def test_day_before_yesterday_phrase(self):
        self.assertEqual(_ex("antes de ahiere")[0], _dt(2017, 6, 25))

    def test_offset_days(self):
        self.assertEqual(_ex("en 3 días")[0], _dt(2017, 6, 30))

    def test_offset_weeks(self):
        self.assertEqual(_ex("2 semanas")[0], _dt(2017, 7, 11))

    def test_offset_hours(self):
        self.assertEqual(_ex("en 3 horas")[0], _dt(2017, 6, 27, 16, 4))

    def test_offset_minutes(self):
        self.assertEqual(_ex("en 5 minutos")[0], _dt(2017, 6, 27, 13, 9))

    def test_next_week_vinient(self):
        self.assertEqual(_ex("a semana vinient")[0], _dt(2017, 7, 4))

    def test_next_week_que_viene(self):
        self.assertEqual(_ex("a semana que viene")[0], _dt(2017, 7, 4))

    def test_last_week_is_backward(self):
        self.assertEqual(_ex("a semana pasada")[0], _dt(2017, 6, 20))

    def test_next_month(self):
        self.assertEqual(_ex("o mes vinient")[0], _dt(2017, 7, 27))

    def test_last_month_is_backward(self):
        self.assertEqual(_ex("o mes pasau")[0], _dt(2017, 5, 27))

    def test_next_year(self):
        self.assertEqual(_ex("l'anyo vinient")[0], _dt(2018, 6, 27))

    def test_last_year_is_backward(self):
        self.assertEqual(_ex("l'anyo pasau")[0], _dt(2016, 6, 27))

    def test_plain_weekday(self):
        self.assertEqual(_ex("o viernes")[0], _dt(2017, 6, 30))

    def test_next_weekday(self):
        self.assertEqual(_ex("o martes que viene")[0], _dt(2017, 7, 4))

    def test_next_weekday_vinient(self):
        self.assertEqual(_ex("o luns vinient")[0], _dt(2017, 7, 3))

    def test_last_weekday_is_backward(self):
        self.assertEqual(_ex("o viernes pasau")[0], _dt(2017, 6, 23))

    def test_day_month_rolls_to_next_year(self):
        self.assertEqual(_ex("o 5 de chunyo")[0], _dt(2018, 6, 5))

    def test_day_month_this_year(self):
        self.assertEqual(_ex("o 15 de chuliol")[0], _dt(2017, 7, 15))

    def test_day_month_year(self):
        self.assertEqual(_ex("o 15 de chuliol de 2018")[0], _dt(2018, 7, 15))

    def test_month_bare_year_keeps_year(self):
        self.assertEqual(_ex("chinero de 2020")[0], _dt(2020, 1, 1))

    def test_colon_time(self):
        self.assertEqual(_ex("a las 15:30")[0], _dt(2017, 6, 27, 15, 30))

    def test_bare_hour_rolls_to_pm(self):
        self.assertEqual(_ex("a las 8")[0], _dt(2017, 6, 27, 20))

    def test_morning_qualifier(self):
        self.assertEqual(_ex("a las 9 de la maitín")[0], _dt(2017, 6, 28, 9))

    def test_afternoon_qualifier(self):
        self.assertEqual(_ex("a las 5 de la tardi")[0], _dt(2017, 6, 27, 17))

    def test_date_and_time(self):
        self.assertEqual(
            _ex("o 15 de chuliol de 2018 a las 9 de la maitín")[0],
            _dt(2018, 7, 15, 9))

    def test_remainder_kept(self):
        self.assertEqual(_ex("reunión demán a las 5 de la tardi"),
                         [_dt(2017, 6, 28, 17), "reunión"])


class TestAragoneseAgoMarker(unittest.TestCase):
    """The Aragonese ago-marker "fa" precedes and negates numeric offsets.

    Source: ~/AgentWorkspaces/papers/linguistics/an/glosbe_hace.html
    (Spanish temporal "hace" -> Aragonese "fa", "en el pasado" sense).
    """

    def test_weeks_ago_is_backward(self):
        self.assertEqual(_ex("fa 2 semanas")[0], _dt(2017, 6, 13))

    def test_weeks_future_stays_forward(self):
        # same phrase without "fa" must remain forward
        self.assertEqual(_ex("2 semanas")[0], _dt(2017, 7, 11))

    def test_days_ago_is_backward(self):
        self.assertEqual(_ex("fa 3 días")[0], _dt(2017, 6, 24))

    def test_months_ago_is_backward(self):
        self.assertEqual(_ex("fa 2 meses")[0], _dt(2017, 4, 27))

    def test_years_ago_is_backward(self):
        self.assertEqual(_ex("fa 2 anyos")[0], _dt(2015, 6, 27))

    def test_minutes_ago_is_backward(self):
        self.assertEqual(_ex("fa 5 minutos")[0], _dt(2017, 6, 27, 12, 59))

    def test_hours_ago_is_backward(self):
        self.assertEqual(_ex("fa 2 horas")[0], _dt(2017, 6, 27, 11, 4))

    def test_marker_without_number_is_not_a_date(self):
        self.assertIsNone(_ex("fa"))
        self.assertIsNone(_ex("fa semanas"))


class TestAragoneseExtractAdversarial(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(_ex(""))

    def test_no_date(self):
        self.assertIsNone(_ex("fabas con tomate"))

    def test_impossible_calendar_date(self):
        self.assertIsNone(_ex("o 31 de febrero"))

    def test_out_of_range_clock(self):
        self.assertIsNone(_ex("a las 25:00"))

    def test_absurd_offset_does_not_crash(self):
        _ex("en 999999999999 horas")


class TestAragoneseExtractRouting(unittest.TestCase):
    def test_routes_an(self):
        self.assertEqual(
            _odp.extract_datetime("demán", "an", anchorDate=_ANCHOR)[0],
            _dt(2017, 6, 28))

    def test_routes_an_region(self):
        self.assertEqual(
            _odp.extract_datetime("ahiere", "an-ES", anchorDate=_ANCHOR)[0],
            _dt(2017, 6, 26))

    def test_duration_routes_an(self):
        dur, _rem = _odp.extract_duration("esperar 3 horas y 20 minutos", "an")
        self.assertEqual(dur.total_seconds(), 3 * 3600 + 20 * 60)

    def test_duration_an_direct(self):
        dur, _rem = extract_duration_an("2 semanas")
        self.assertEqual(dur.days, 14)
