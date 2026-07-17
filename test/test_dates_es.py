"""Spanish datetime extraction: natural phrasing, clock words and edge cases."""
import unittest
from datetime import datetime, timedelta

from ovos_config.locale import get_default_tz as default_timezone
from ovos_utils.time import DAYS_IN_1_YEAR, DAYS_IN_1_MONTH

import ovos_date_parser as _odp

ANCHOR = datetime(1998, 1, 1)
TZ = default_timezone()


def extract(text, lang="es", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0):
    return datetime(y, mo, d, h, mi, tzinfo=TZ)


class TestSpokenClockNumbers(unittest.TestCase):
    """Times spelled out in words must parse like their digit equivalents."""

    def test_bare_hour(self):
        self.assertEqual(extract("a las tres")[0], dt(1998, 1, 1, 3))

    def test_bare_hour_five(self):
        self.assertEqual(extract("reunión a las cinco")[0], dt(1998, 1, 1, 5))

    def test_hour_matches_digits(self):
        for word, hour in [("dos", 2), ("tres", 3), ("cuatro", 4),
                           ("cinco", 5), ("seis", 6), ("siete", 7), ("ocho", 8),
                           ("nueve", 9), ("diez", 10), ("once", 11), ("doce", 12)]:
            with self.subTest(word=word):
                self.assertEqual(extract(f"a las {word}")[0].hour, hour)

    def test_one_oclock_feminine(self):
        # "la una" is the canonical Spanish rendering of one o'clock
        self.assertEqual(extract("a la una")[0], dt(1998, 1, 1, 1))
        self.assertEqual(extract("a la una y media")[0], dt(1998, 1, 1, 1, 30))
        self.assertEqual(extract("a la una de la tarde")[0], dt(1998, 1, 1, 13))

    def test_afternoon_applies_pm(self):
        # "de la tarde" adds 12h to the spoken hour
        self.assertEqual(extract("a las cinco de la tarde")[0], dt(1998, 1, 1, 17))
        self.assertEqual(extract("a las tres de la tarde")[0], dt(1998, 1, 1, 15))

    def test_morning_stays_am(self):
        self.assertEqual(extract("a las ocho de la mañana")[0], dt(1998, 1, 1, 8))

    def test_night(self):
        self.assertEqual(extract("a las nueve de la noche")[0], dt(1998, 1, 1, 21))

    def test_spoken_day_of_month(self):
        self.assertEqual(extract("once de enero")[0], dt(1998, 1, 11))


class TestQuarterAndHalf(unittest.TestCase):
    """'y cuarto' / 'y media' and explicit spoken minutes."""

    def test_quarter_past(self):
        self.assertEqual(extract("a las tres y cuarto")[0], dt(1998, 1, 1, 3, 15))

    def test_half_past(self):
        self.assertEqual(extract("a las tres y media")[0], dt(1998, 1, 1, 3, 30))

    def test_quarter_past_seven(self):
        self.assertEqual(extract("ponme una alarma a las siete y cuarto")[0],
                         dt(1998, 1, 1, 7, 15))

    def test_half_past_afternoon(self):
        self.assertEqual(extract("a las tres y media de la tarde")[0],
                         dt(1998, 1, 1, 15, 30))

    def test_explicit_minutes(self):
        self.assertEqual(extract("a las tres y veinte")[0], dt(1998, 1, 1, 3, 20))

    def test_minutes_with_night(self):
        self.assertEqual(extract("a las nueve y diez de la noche")[0],
                         dt(1998, 1, 1, 21, 10))


class TestDateWithClock(unittest.TestCase):
    """A trailing spoken clock time must not be swallowed by the date."""

    def test_date_plus_hour(self):
        res = extract("cita el quince de junio a las tres")
        self.assertEqual(res[0], dt(1998, 6, 15, 3))

    def test_digit_date_plus_hour(self):
        res = extract("el 15 de junio a las 3")
        self.assertEqual(res[0], dt(1998, 6, 15, 3))


class TestNiceTimeRoundTrip(unittest.TestCase):
    """nice_time output for representative clocks must extract back."""

    def test_round_trip(self):
        for h, m in [(3, 15), (3, 30), (7, 15), (9, 10), (3, 20),
                     (1, 5), (1, 30), (11, 0), (8, 0)]:
            spoken = _odp.nice_time(datetime(1998, 1, 1, h, m, tzinfo=TZ),
                                    lang="es")
            with self.subTest(spoken=spoken):
                res = extract(spoken)
                self.assertIsNotNone(res, spoken)
                self.assertEqual((res[0].hour, res[0].minute), (h, m), spoken)


class TestLangVariants(unittest.TestCase):
    def test_region_codes_agree(self):
        base = extract("a las tres de la tarde", lang="es")[0]
        for code in ("es-es", "es-ES", "es-MX", "es-419"):
            with self.subTest(code=code):
                self.assertEqual(extract("a las tres de la tarde", lang=code)[0],
                                 base)


class TestAdversarial(unittest.TestCase):
    def test_empty_string(self):
        self.assertIsNone(_odp.extract_datetime("", lang="es"))

    def test_none_input(self):
        self.assertIsNone(_odp.extract_datetime(None, lang="es"))

    def test_pure_junk(self):
        self.assertIsNone(extract("asdf qwerty zxcv"))

    def test_no_time_words(self):
        self.assertIsNone(extract("hola cómo estás"))

    def test_uppercase(self):
        self.assertEqual(extract("A LAS TRES DE LA TARDE")[0], dt(1998, 1, 1, 15))


class TestNumericTimeSuffix(unittest.TestCase):
    """Digit tokens glued to a letter suffix ("20h") must not crash the parser.

    These tokens reach the numeric time-of-day branch, where only the leading
    digits carry meaning; the trailing letters must be ignored, not fed to int().
    """

    def test_bare_hour_h_suffix(self):
        self.assertEqual(extract("20h")[0], dt(1998, 1, 1, 20))

    def test_a_las_hour_h_suffix(self):
        self.assertEqual(extract("a las 20h")[0], dt(1998, 1, 1, 20))

    def test_hour_minute_h_suffix(self):
        self.assertEqual(extract("21h30")[0], dt(1998, 1, 1, 21, 30))

    def test_hour_h_suffix_matches_plain_digits(self):
        for glued, hour in [("8h", 8), ("13h", 13), ("20h", 20), ("23h", 23)]:
            with self.subTest(token=glued):
                self.assertEqual(extract(f"a las {glued}")[0].hour, hour)

    def test_impossible_hour_does_not_crash(self):
        # 99h is not a valid clock time; must not raise, either None or ignored
        res = extract("a las 99h")
        if res is not None:
            self.assertNotEqual(res[0].hour, 99)

    def test_letters_before_digits_gibberish(self):
        # leading letters mean the digit-branch is never entered; must not crash
        self.assertIsNone(extract("xyz123h"))

    def test_lone_suffix_token_no_crash(self):
        # only letters after stripping digits -> nothing usable, must not raise
        self.assertIsNone(extract("hhh"))


class TestDurations(unittest.TestCase):
    def test_basic_units(self):
        self.assertEqual(_odp.extract_duration("10 segundos", lang="es"),
                         (timedelta(seconds=10), ""))
        self.assertEqual(_odp.extract_duration("5 minutos", lang="es"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(_odp.extract_duration("2 horas", lang="es"),
                         (timedelta(hours=2), ""))

    def test_media_hora(self):
        self.assertEqual(_odp.extract_duration("media hora", lang="es"),
                         (timedelta(minutes=30), ""))

    def test_spoken_ninety_minutes(self):
        self.assertEqual(_odp.extract_duration("noventa minutos", lang="es"),
                         (timedelta(minutes=90), ""))

    def test_month_year_units(self):
        self.assertEqual(_odp.extract_duration("1 mes", lang="es"),
                         (timedelta(days=DAYS_IN_1_MONTH), ""))
        self.assertEqual(_odp.extract_duration("1 año", lang="es"),
                         (timedelta(days=DAYS_IN_1_YEAR), ""))

    def test_empty(self):
        self.assertIsNone(_odp.extract_duration("", lang="es"))


if __name__ == "__main__":
    unittest.main()
