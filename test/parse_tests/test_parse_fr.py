import unittest
from datetime import datetime, timedelta

from ovos_date_parser.dates_fr import (
    extract_datetime_fr,
    extract_duration_fr,
    normalize_fr,
)

# fixed anchor: Friday 17 July 2026, 10:00
ANCHOR = datetime(2026, 7, 17, 10, 0, 0)


def when(text, anchor=ANCHOR):
    res = extract_datetime_fr(text, anchor)
    return res[0] if res else None


def rest(text, anchor=ANCHOR):
    res = extract_datetime_fr(text, anchor)
    return res[1] if res else None


class TestExtractDatetimeFr(unittest.TestCase):
    def test_clock_with_quarter_and_half(self):
        self.assertEqual(when("à quatre heures et quart").time(),
                         datetime(1, 1, 1, 4, 15).time())
        self.assertEqual(when("à quatre heures et demi").time(),
                         datetime(1, 1, 1, 4, 30).time())
        # "et demie" is the standard feminine spelling after "heures"
        self.assertEqual(when("à quatre heures et demie").time(),
                         datetime(1, 1, 1, 4, 30).time())
        self.assertEqual(rest("à quatre heures et demie"), "")

    def test_moins_le_quart_and_moins_vingt(self):
        self.assertEqual(when("à quatre heures moins le quart").time(),
                         datetime(1, 1, 1, 3, 45).time())
        self.assertEqual(when("à cinq heures moins vingt").time(),
                         datetime(1, 1, 1, 4, 40).time())

    def test_midi_minuit(self):
        self.assertEqual(when("à midi").time(),
                         datetime(1, 1, 1, 12, 0).time())
        self.assertEqual(when("à minuit").time(),
                         datetime(1, 1, 1, 0, 0).time())
        self.assertEqual(when("à midi et quart").time(),
                         datetime(1, 1, 1, 12, 15).time())
        self.assertEqual(when("à midi et demi").time(),
                         datetime(1, 1, 1, 12, 30).time())
        self.assertEqual(when("à midi et demie").time(),
                         datetime(1, 1, 1, 12, 30).time())
        self.assertEqual(when("à minuit et demie").time(),
                         datetime(1, 1, 1, 0, 30).time())
        self.assertEqual(when("à minuit moins le quart").time(),
                         datetime(1, 1, 1, 23, 45).time())

    def test_part_of_day_pm(self):
        self.assertEqual(when("à trois heures de l'après-midi").time(),
                         datetime(1, 1, 1, 15, 0).time())
        self.assertEqual(when("à sept heures du soir").time(),
                         datetime(1, 1, 1, 19, 0).time())
        self.assertEqual(when("à onze heures du soir").time(),
                         datetime(1, 1, 1, 23, 0).time())

    def test_part_of_day_am(self):
        self.assertEqual(when("à huit heures du matin").time(),
                         datetime(1, 1, 1, 8, 0).time())
        self.assertEqual(when("à sept heures et demie du soir").time(),
                         datetime(1, 1, 1, 19, 30).time())

    def test_bare_part_of_day_defaults(self):
        # a bare part-of-day qualifier keeps today and applies its default hour
        self.assertEqual(when("cet après-midi"),
                         datetime(2026, 7, 17, 15, 0))
        self.assertEqual(when("ce soir"),
                         datetime(2026, 7, 17, 19, 0))
        self.assertEqual(when("ce matin"),
                         datetime(2026, 7, 17, 8, 0))
        self.assertEqual(when("cette nuit"),
                         datetime(2026, 7, 17, 2, 0))
        self.assertEqual(rest("cet après-midi"), "")

    def test_bare_part_of_day_with_offset_day(self):
        self.assertEqual(when("demain après-midi"),
                         datetime(2026, 7, 18, 15, 0))
        self.assertEqual(when("demain soir"),
                         datetime(2026, 7, 18, 19, 0))

    def test_h_format(self):
        self.assertEqual(when("à 14h30").time(),
                         datetime(1, 1, 1, 14, 30).time())
        self.assertEqual(when("à 15h45").time(),
                         datetime(1, 1, 1, 15, 45).time())
        self.assertEqual(when("à 8h05").time(),
                         datetime(1, 1, 1, 8, 5).time())

    def test_day_offsets(self):
        self.assertEqual(when("aujourd'hui").date(), datetime(2026, 7, 17).date())
        self.assertEqual(when("demain").date(), datetime(2026, 7, 18).date())
        self.assertEqual(when("après-demain").date(), datetime(2026, 7, 19).date())
        self.assertEqual(when("dans deux jours").date(),
                         datetime(2026, 7, 19).date())

    def test_weekday(self):
        # anchor is a Friday; lundi prochain is the Monday of next week
        self.assertEqual(when("lundi prochain").weekday(), 0)
        self.assertTrue(when("lundi prochain") > ANCHOR)

    def test_dates(self):
        self.assertEqual(when("le 25 décembre").date(),
                         datetime(2026, 12, 25).date())
        # 15 June has already passed relative to the anchor -> next year
        self.assertEqual(when("le 15 juin").date(),
                         datetime(2027, 6, 15).date())

    def test_date_and_time_combined(self):
        dt = when("rendez-vous le 15 juin à trois heures")
        self.assertEqual(dt.date(), datetime(2027, 6, 15).date())
        self.assertEqual(dt.time(), datetime(1, 1, 1, 3, 0).time())

    def test_remainder_is_cleaned(self):
        self.assertEqual(rest("mets une alarme à quatre heures et quart"),
                         "mets 1 alarme")
        self.assertEqual(rest("réveille-moi à sept heures du matin"),
                         "réveille-moi")

    def test_lang_variant_marker_insensitive(self):
        # the extractor takes no locale sub-tag; the same phrasing is stable
        self.assertEqual(when("à quatorze heures").time(),
                         datetime(1, 1, 1, 14, 0).time())

    def test_empty_and_junk(self):
        self.assertIsNone(extract_datetime_fr(""))
        self.assertIsNone(extract_datetime_fr("bonjour tout le monde"))
        self.assertIsNone(extract_datetime_fr("un chat noir"))

    def test_case_insensitive(self):
        self.assertEqual(when("À MIDI").time(),
                         datetime(1, 1, 1, 12, 0).time())
        self.assertEqual(when("Demain").date(), datetime(2026, 7, 18).date())

    def test_wraparound_next_day(self):
        # a clock time already passed today rolls to tomorrow when no day given
        early = datetime(2026, 7, 17, 20, 0, 0)
        self.assertEqual(when("à trois heures", early).date(),
                         datetime(2026, 7, 18).date())


class TestExtractDurationFr(unittest.TestCase):
    def test_basic_units(self):
        self.assertEqual(extract_duration_fr("deux heures")[0],
                         timedelta(hours=2))
        self.assertEqual(extract_duration_fr("trente minutes")[0],
                         timedelta(minutes=30))
        self.assertEqual(extract_duration_fr("dix secondes")[0],
                         timedelta(seconds=10))
        self.assertEqual(extract_duration_fr("trois jours")[0],
                         timedelta(days=3))
        self.assertEqual(extract_duration_fr("une semaine")[0],
                         timedelta(weeks=1))

    def test_compound(self):
        self.assertEqual(extract_duration_fr("2 heures 30 minutes")[0],
                         timedelta(hours=2, minutes=30))

    def test_remainder_retained(self):
        dur, remainder = extract_duration_fr("cinq minutes de repos")
        self.assertEqual(dur, timedelta(minutes=5))
        self.assertEqual(remainder, "de repos")

    def test_empty_and_none_duration(self):
        self.assertIsNone(extract_duration_fr(""))
        self.assertEqual(extract_duration_fr("bonjour")[0], None)


class TestNormalizeFr(unittest.TestCase):
    def test_numbers_to_digits(self):
        self.assertEqual(normalize_fr("j'ai vingt et un ans"),
                         "j'ai 21 ans")
        self.assertEqual(normalize_fr("quatre-vingt-dix euros"),
                         "90 euros")

    def test_articles_removed(self):
        self.assertEqual(normalize_fr("le chat", remove_articles=True),
                         "chat")
        self.assertEqual(normalize_fr("le chat", remove_articles=False),
                         "le chat")


if __name__ == "__main__":
    unittest.main()
