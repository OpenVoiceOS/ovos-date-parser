"""French datetime extraction: natural phrasing, clock notation and edge cases.

Anchors verified against French usage (24-hour clock, "1er" for the first of
the month), not pinned from engine output.
"""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2117, 9, 3, 13, 30)  # a fixed non-midnight anchor
TZ = default_timezone()


def extract(text, lang="fr", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0):
    return datetime(y, mo, d, h, mi, tzinfo=TZ)


class TestClockNotation(unittest.TestCase):
    """The "h" hour separator is the standard French clock notation."""

    def test_bare_hour_h_suffix(self):
        self.assertEqual(extract("20h")[0], dt(2117, 9, 3, 20))

    def test_a_hour_h_suffix(self):
        self.assertEqual(extract("à 20h")[0], dt(2117, 9, 3, 20))

    def test_hour_minute_h_separator(self):
        self.assertEqual(extract("20h30")[0], dt(2117, 9, 3, 20, 30))

    def test_spelled_hours(self):
        self.assertEqual(extract("à trois heures")[0].hour, 3)


class TestSpacedClockNotation(unittest.TestCase):
    """French typography puts a space before the "h" ("20 h 30"), and so does
    speech-to-text; it is the same clock as "20h30"."""

    def test_a_hour_spaced_h(self):
        self.assertEqual(extract("à 18 h")[0], dt(2117, 9, 3, 18))

    def test_bare_hour_spaced_h(self):
        self.assertEqual(extract("20 h")[0], dt(2117, 9, 3, 20))

    def test_hour_minute_spaced_h(self):
        self.assertEqual(extract("20 h 30")[0], dt(2117, 9, 3, 20, 30))

    def test_tomorrow_spaced_h(self):
        self.assertEqual(extract("demain à 20 h")[0], dt(2117, 9, 4, 20))

    def test_tomorrow_spaced_h_minutes(self):
        self.assertEqual(extract("demain à 20 h 30")[0],
                         dt(2117, 9, 4, 20, 30))

    def test_spaced_h_evening(self):
        self.assertEqual(extract("demain à 8 h du soir")[0],
                         dt(2117, 9, 4, 20))

    def test_spaced_h_morning(self):
        self.assertEqual(extract("demain à 7 h du matin")[0],
                         dt(2117, 9, 4, 7))

    def test_spaced_h_quarter(self):
        self.assertEqual(extract("demain à 9 h et quart")[0],
                         dt(2117, 9, 4, 9, 15))

    def test_spaced_h_in_sentence(self):
        date, rest = extract("rappelle-moi de sortir le chien demain à 20 h")
        self.assertEqual(date, dt(2117, 9, 4, 20))
        self.assertEqual(rest, "rappelle-moi sortir chien")

    def test_spaced_h_same_as_joined(self):
        for spaced, joined in [("à 18 h", "à 18h"), ("20 h 30", "20h30"),
                               ("demain à 20 h", "demain à 20h"),
                               ("demain à 20 h", "demain à 20 heures")]:
            with self.subTest(spaced=spaced):
                self.assertEqual(extract(spaced)[0], extract(joined)[0])

    def test_spaced_h_offset(self):
        self.assertEqual(extract("dans 2 h")[0], dt(2117, 9, 3, 15, 30))

    def test_fr_ca(self):
        self.assertEqual(extract("demain à 20 h", lang="fr-ca")[0],
                         dt(2117, 9, 4, 20))

    def test_lone_h_is_not_a_time(self):
        self.assertIsNone(extract("la bombe h"))


class TestOrdinalFirstOfMonth(unittest.TestCase):
    """"1er" is the ordinary way to say the first day of a month."""

    def test_premier_janvier(self):
        self.assertEqual(extract("1er janvier")[0], dt(2118, 1, 1))

    def test_le_premier_janvier(self):
        self.assertEqual(extract("le 1er janvier")[0], dt(2118, 1, 1))

    def test_premier_janvier_with_time(self):
        self.assertEqual(extract("1er janvier à 20h")[0], dt(2118, 1, 1, 20))

    def test_plain_day_month(self):
        self.assertEqual(extract("15 juillet")[0], dt(2118, 7, 15))


class TestRelativeOffsets(unittest.TestCase):
    """Relative offsets keep the anchor time of day."""

    def test_in_hours(self):
        self.assertEqual(extract("dans 3 heures")[0], dt(2117, 9, 3, 16, 30))

    def test_in_minutes(self):
        self.assertEqual(extract("dans 10 minutes")[0], dt(2117, 9, 3, 13, 40))


class TestAdversarial(unittest.TestCase):
    """Malformed digit-leading tokens must not crash the extractor."""

    def test_digit_letter_tokens(self):
        for token in ["10sept", "7d", "5m", "20h99z"]:
            with self.subTest(token=token):
                # must not raise; a non-time gibberish token yields no match
                extract(token)

    def test_slash_date_tokens(self):
        for token in ["15/06/20", "3/0/0", "0/0/0"]:
            with self.subTest(token=token):
                extract(token)

    def test_empty_and_gibberish(self):
        self.assertIsNone(extract(""))
        self.assertIsNone(extract("   "))
        self.assertIsNone(extract("azerty qwerty"))

    def test_impossible_hour_no_crash(self):
        res = extract("à 99h")
        if res is not None and res[0] is not None:
            self.assertNotEqual(res[0].hour, 99)

    def test_impossible_dates_return_none(self):
        for token in ["30 février", "31 avril", "30 février 2020",
                      "février 30", "31 avril 2020"]:
            with self.subTest(token=token):
                self.assertIsNone(extract(token))

    def test_valid_dates_still_parse(self):
        self.assertEqual(extract("15 juillet 2020")[0], dt(2020, 7, 15))


class TestYesterdayWords(unittest.TestCase):
    """"hier": le jour qui précède immédiatement celui où l'on est
    (Larousse, papers/linguistics/french/larousse_hier.html).  Regression
    for the three-way differential lead: "hier"/"avant-hier" returned
    None while "ontem"/"ayer" worked in the sibling languages."""

    def test_hier(self):
        self.assertEqual(extract("hier")[0], dt(2117, 9, 2))
        self.assertEqual(extract("avant-hier")[0], dt(2117, 9, 1))

    def test_in_sentences(self):
        res = extract("que s'est-il passé hier")
        self.assertEqual(res[0], dt(2117, 9, 2))
        res = extract("le match d'avant-hier")
        self.assertEqual(res[0], dt(2117, 9, 1))

    def test_hier_with_time(self):
        self.assertEqual(extract("hier à 17 heures")[0],
                         dt(2117, 9, 2, 17, 0))

    def test_symmetry_with_demain(self):
        # demain/hier must be symmetric around the anchor day
        self.assertEqual((extract("demain")[0] - extract("hier")[0]).days, 2)


class TestBareDurationNotClock(unittest.TestCase):
    """A bare "N heures"/"Nh" with no preposition before it is a duration,
    not a clock time, unless a marker word ("à", "dans"...) introduces it
    or it opens the sentence as its own clock notation ("20h")."""

    def test_un_film_de_n_heures(self):
        self.assertIsNone(extract("un film de 2 heures"))

    def test_un_film_de_nh(self):
        self.assertIsNone(extract("un film de 2h"))

    def test_pendant_n_heures(self):
        self.assertIsNone(extract("pendant 3 heures"))

    def test_il_reste_n_heures(self):
        self.assertIsNone(extract("il reste 3 heures"))

    def test_n_heures_de_travail(self):
        self.assertIsNone(extract("3 heures de travail"))

    def test_chapitre_n_heures(self):
        self.assertIsNone(extract("mets le chapitre 3 heures"))

    def test_marker_still_reads_as_clock(self):
        self.assertEqual(extract("à 3 heures")[0], dt(2117, 9, 4, 3))

    def test_offset_marker_still_works(self):
        self.assertEqual(extract("dans 3 heures")[0], dt(2117, 9, 3, 16, 30))

    def test_sentence_initial_h_notation_still_a_clock(self):
        self.assertEqual(extract("20h")[0], dt(2117, 9, 3, 20))

    def test_sentence_initial_spelled_hour_still_a_clock(self):
        self.assertEqual(extract("20 heures")[0], dt(2117, 9, 3, 20))
        self.assertEqual(extract("3 heures")[0], dt(2117, 9, 4, 3))

    def test_sentence_initial_number_word_hour_still_a_clock(self):
        self.assertEqual(extract("dix heures")[0], dt(2117, 9, 4, 10))
        self.assertEqual(extract("trois heures")[0], dt(2117, 9, 4, 3))
        self.assertEqual(extract("vingt heures")[0], dt(2117, 9, 3, 20))

    def test_sentence_initial_bare_h_with_trailing_words_is_duration(self):
        self.assertIsNone(extract("2h de route"))
        self.assertIsNone(extract("2 h de route"))

    def test_il_est_n_heures_still_a_clock(self):
        self.assertEqual(extract("il est 3 heures")[0], dt(2117, 9, 4, 3))
        self.assertEqual(extract("il est trois heures")[0], dt(2117, 9, 4, 3))

    def test_il_est_n_heures_with_trailing_word_still_a_clock(self):
        date, rest = extract("il est 20 heures pile")
        self.assertEqual(date, dt(2117, 9, 3, 20))
        self.assertEqual(rest, "il est pile")

    def test_cest_n_heures_still_a_clock(self):
        self.assertEqual(extract("c'est 3 heures")[0], dt(2117, 9, 4, 3))


if __name__ == "__main__":
    unittest.main()
