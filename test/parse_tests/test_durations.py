"""Duration extraction for basque, french, hungarian, italian and slovenian."""
import unittest
from datetime import datetime, timedelta
from unittest import mock

from dateutil.relativedelta import relativedelta
from ovos_utils.time import DAYS_IN_1_MONTH, DAYS_IN_1_YEAR

import ovos_date_parser
from ovos_date_parser import extract_duration, DurationResolution

#: months and years are counted from this day, a Tuesday
NOW = datetime(2017, 6, 27, 13, 4)
pinned_now = mock.patch.object(ovos_date_parser, "now_local", lambda: NOW)


class TestExtractDurationFr(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(extract_duration("dix minutes", "fr"),
                         (timedelta(minutes=10), ""))
        self.assertEqual(extract_duration("trois jours", "fr"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 heures", "fr"),
                         (timedelta(hours=25), ""))

    def test_composite(self):
        self.assertEqual(
            extract_duration("3 jours 8 heures 10 minutes et 49 secondes", "fr"),
            (timedelta(days=3, hours=8, minutes=10, seconds=49), ""))

    def test_in_sentence(self):
        duration, remainder = extract_duration(
            "règle un minuteur de dix minutes", "fr")
        self.assertEqual(duration, timedelta(minutes=10))
        self.assertIn("minuteur", remainder)

    def test_calendar_units(self):
        duration, _ = extract_duration("deux semaines", "fr")
        self.assertEqual(duration, timedelta(weeks=2))
        duration, _ = extract_duration("un mois", "fr")
        self.assertAlmostEqual(duration.days, 30, delta=1)
        duration, _ = extract_duration("deux ans", "fr")
        self.assertAlmostEqual(duration.days, 730, delta=2)

    def test_no_duration(self):
        self.assertEqual(extract_duration("bonjour tout le monde", "fr"),
                         (None, "bonjour tout le monde"))
        self.assertEqual(extract_duration("", "fr"), (None, ""))


class TestExtractDurationIt(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(extract_duration("dieci minuti", "it"),
                         (timedelta(minutes=10), ""))
        self.assertEqual(extract_duration("tre giorni", "it"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("un'ora", "it"),
                         (timedelta(hours=1), ""))
        self.assertEqual(extract_duration("2 ore", "it"),
                         (timedelta(hours=2), ""))

    def test_composite(self):
        self.assertEqual(
            extract_duration("3 giorni 8 ore 10 minuti e 49 secondi", "it"),
            (timedelta(days=3, hours=8, minutes=10, seconds=49), ""))

    def test_in_sentence(self):
        duration, remainder = extract_duration(
            "imposta un timer di dieci minuti", "it")
        self.assertEqual(duration, timedelta(minutes=10))
        self.assertIn("timer", remainder)

    def test_calendar_units(self):
        duration, _ = extract_duration("due settimane", "it")
        self.assertEqual(duration, timedelta(weeks=2))
        duration, _ = extract_duration("un anno", "it")
        self.assertAlmostEqual(duration.days, 365, delta=1)

    def test_no_duration(self):
        self.assertEqual(extract_duration("ciao a tutti", "it"),
                         (None, "ciao a tutti"))


class TestExtractDurationEu(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(extract_duration("hamar minutu", "eu"),
                         (timedelta(minutes=10), ""))
        self.assertEqual(extract_duration("bost aste", "eu"),
                         (timedelta(weeks=5), ""))

    def test_composite(self):
        self.assertEqual(extract_duration("3 egun 8 ordu 10 minutu", "eu"),
                         (timedelta(days=3, hours=8, minutes=10), ""))

    def test_calendar_units(self):
        duration, _ = extract_duration("bi hilabete", "eu")
        self.assertAlmostEqual(duration.days, 61, delta=1)
        duration, _ = extract_duration("hiru urte", "eu")
        self.assertAlmostEqual(duration.days, 1096, delta=2)

    def test_no_duration(self):
        self.assertEqual(extract_duration("egun on", "eu"), (None, "egun on"))


class TestExtractDurationHu(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(extract_duration("tíz perc", "hu"),
                         (timedelta(minutes=10), ""))
        self.assertEqual(extract_duration("3 nap 8 óra 10 perc", "hu"),
                         (timedelta(days=3, hours=8, minutes=10), ""))

    def test_het_is_week_after_number(self):
        self.assertEqual(extract_duration("öt hét", "hu"),
                         (timedelta(weeks=5), ""))

    def test_het_is_seven_before_unit(self):
        self.assertEqual(extract_duration("hét perc", "hu"),
                         (timedelta(minutes=7), ""))

    def test_case_suffixes(self):
        duration, remainder = extract_duration("öt órát aludtam", "hu")
        self.assertEqual(duration, timedelta(hours=5))
        self.assertEqual(remainder, "aludtam")

    def test_calendar_units(self):
        duration, _ = extract_duration("két hónap", "hu")
        self.assertAlmostEqual(duration.days, 61, delta=1)
        duration, _ = extract_duration("egy év", "hu")
        self.assertAlmostEqual(duration.days, 365, delta=1)

    def test_no_duration(self):
        self.assertEqual(extract_duration("jó reggelt", "hu"),
                         (None, "jó reggelt"))


class TestExtractDurationSl(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(extract_duration("deset minut", "sl"),
                         (timedelta(minutes=10), ""))
        self.assertEqual(extract_duration("3 dni 8 ur 10 minut", "sl"),
                         (timedelta(days=3, hours=8, minutes=10), ""))

    def test_declined_units(self):
        self.assertEqual(extract_duration("dva tedna", "sl"),
                         (timedelta(weeks=2), ""))
        self.assertEqual(extract_duration("ena ura", "sl"),
                         (timedelta(hours=1), ""))

    def test_in_sentence(self):
        duration, remainder = extract_duration(
            "nastavi časovnik za deset minut", "sl")
        self.assertEqual(duration, timedelta(minutes=10))
        self.assertIn("časovnik", remainder)

    def test_calendar_units(self):
        duration, _ = extract_duration("en mesec", "sl")
        self.assertAlmostEqual(duration.days, 30, delta=1)
        duration, _ = extract_duration("pet let", "sl")
        self.assertAlmostEqual(duration.days, 1826, delta=2)

    def test_no_duration(self):
        self.assertEqual(extract_duration("dobro jutro", "sl"),
                         (None, "dobro jutro"))


if __name__ == "__main__":
    unittest.main()


class TestDurationResolution(unittest.TestCase):
    def test_relativedelta(self):
        self.assertEqual(
            extract_duration("3 tedne", "sl",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(weeks=3), ""))
        self.assertEqual(
            extract_duration("2 ure in 30 minut", "sl",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(hours=2, minutes=30), ""))

    @pinned_now
    def test_relativedelta_counts_a_month_in_days(self):
        # 27 June to 27 August 2017 is 61 days
        self.assertEqual(
            extract_duration("2 mois", "fr",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(days=61), ""))

    @pinned_now
    def test_totals(self):
        self.assertEqual(
            extract_duration("2 heures", "fr",
                             resolution=DurationResolution.TOTAL_MINUTES),
            (120.0, ""))
        self.assertEqual(
            extract_duration("1 jour", "fr",
                             resolution=DurationResolution.TOTAL_SECONDS),
            (86400.0, ""))
        # 27 June 2017 to 27 June 2027 is 10 * 365 + 2 (2020 and 2024) days
        self.assertEqual(
            extract_duration("1 décennie", "fr",
                             resolution=DurationResolution.TOTAL_YEARS),
            (3652 / DAYS_IN_1_YEAR, ""))
        # 27 June 2017 to 27 June 2019 is 730 days
        self.assertEqual(
            extract_duration("2 urte", "eu",
                             resolution=DurationResolution.TOTAL_MONTHS),
            (730 / DAYS_IN_1_MONTH, ""))

    def test_replace_token(self):
        self.assertEqual(
            extract_duration("attends 2 minutes puis parle", "fr",
                             replace_token="_"),
            (timedelta(minutes=2), "attends _ puis parle"))

    def test_replace_token_marks_each_separate_length(self):
        self.assertEqual(
            extract_duration("attends 2 minutes puis 3 heures", "fr",
                             replace_token="_"),
            (timedelta(hours=3, minutes=2), "attends _ puis _"))

    def test_every_locale_takes_the_options(self):
        self.assertEqual(
            extract_duration("دو ساعت", "fa",
                             resolution=DurationResolution.TOTAL_MINUTES),
            (120.0, ""))
        self.assertEqual(
            extract_duration("برای ۱۰ دقیقه صبر کن", "fa", replace_token="_"),
            (timedelta(minutes=10), "_ صبر کن"))

    def test_an_invalid_resolution_raises(self):
        with self.assertRaises(ValueError):
            extract_duration("2 heures", "fr", resolution="minutes")
