"""German words for the past that the de engine did not read.

Sources:
- Duden, "vorvorgestern": Adverb, "vor drei Tagen".
- Duden, "vorletzte": "dem Letzten (4), Vorigen unmittelbar vorausgehend",
  Beispiele "vorletzte Woche", "im vorletzten Jahr".
- Duden, "vorvorletzte": "dem Vorletzten (b) unmittelbar vorausgehend",
  Beispiele "vorvorletztes Jahr", "am vorvorletzten Wochenende, Dienstag".
- CLDR 49, de, gregorian dateFormats: medium "dd.MM.y", short "dd.MM.yy".
- POSIX.1-2017 strptime, %y: "values in the range [69,99] shall refer to
  years 1969 to 1999 inclusive" and "[00,68] shall refer to years 2000 to
  2068 inclusive".

The anchor is Wednesday 23 September 2026. Every expected date is counted by
hand from it. A period named with "letzte" is the anchor minus that many
periods in this engine ("letzte Woche" is 16 September), and "vorletzte" and
"vorvorletzte" go one and two periods further back the same way.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2026, 9, 23, 12, 0)


def _read(text):
    return extract_datetime(text, lang="de-DE", anchorDate=ANCHOR)


class TestPastWords(unittest.TestCase):
    CASES = (
        ("vorvorgestern", datetime(2026, 9, 20)),
        ("vorletzte Woche", datetime(2026, 9, 9)),
        ("vorvorletzte Woche", datetime(2026, 9, 2)),
        ("im letzten Monat", datetime(2026, 8, 23)),
        ("im vorletzten Monat", datetime(2026, 7, 23)),
        ("im vorvorletzten Monat", datetime(2026, 6, 23)),
        ("im letzten Jahr", datetime(2025, 9, 23)),
        ("im vorletzten Jahr", datetime(2024, 9, 23)),
        ("im vorvorletzten Jahr", datetime(2023, 9, 23)),
        ("vorletzten Montag", datetime(2026, 9, 14)),
        ("vorvorletzten Dienstag", datetime(2026, 9, 8)),
    )

    def test_the_date_and_an_empty_remainder(self):
        for text, day in self.CASES:
            with self.subTest(text=text):
                self.assertEqual(tuple(_read(text)), (day, ""))

    def test_the_words_that_already_read_stay(self):
        for text, day in (("gestern", datetime(2026, 9, 22)),
                          ("vorgestern", datetime(2026, 9, 21)),
                          ("letzte Woche", datetime(2026, 9, 16)),
                          ("letzten Montag", datetime(2026, 9, 21)),
                          ("vor einer Woche", datetime(2026, 9, 16)),
                          ("vor sieben Tagen", datetime(2026, 9, 16))):
            with self.subTest(text=text):
                self.assertEqual(tuple(_read(text)), (day, ""))

    def test_vorletzte_beside_another_noun_is_not_a_date(self):
        self.assertIsNone(_read("die vorletzte Seite"))

    def test_a_noun_that_starts_with_stunde_after_im_is_not_an_hour(self):
        # "Stundenplan" (timetable) names no time
        self.assertIsNone(_read("schau im Stundenplan nach"))

    def test_im_stundentakt_keeps_the_date_and_the_noun(self):
        # "im Stundentakt" (every hour) is no offset; "ab morgen" is the date
        self.assertEqual(tuple(_read("Busse fahren im Stundentakt ab morgen")),
                         (datetime(2026, 9, 24), "busse fahren im stundentakt"))


class TestNumericDates(unittest.TestCase):
    def test_day_month_year_in_digits(self):
        for text in ("23.09.2023", "23.9.2023", "23.9.23"):
            with self.subTest(text=text):
                self.assertEqual(tuple(_read(text)),
                                 (datetime(2023, 9, 23), ""))

    def test_in_a_sentence_with_a_clock(self):
        self.assertEqual(tuple(_read("Termin am 23.09.2023 um 10 Uhr")),
                         (datetime(2023, 9, 23, 10, 0), "termin"))

    def test_two_digit_year_century(self):
        self.assertEqual(_read("1.1.68")[0], datetime(2068, 1, 1))
        self.assertEqual(_read("1.1.69")[0], datetime(1969, 1, 1))

    def test_a_version_number_is_not_a_date(self):
        # no month 15 and no day 40, so the version is no date and "morgen" is
        for version in ("1.15.20", "40.2.10"):
            with self.subTest(version=version):
                self.assertEqual(
                    tuple(_read("Installiere Version %s morgen" % version)),
                    (datetime(2026, 9, 24), "installiere version " + version))

    def test_an_impossible_date_is_none(self):
        self.assertIsNone(_read("31.02.2023"))

    def test_a_clock_with_a_dot_stays_a_clock(self):
        self.assertEqual(_read("um 10.30 Uhr")[0], datetime(2026, 9, 24, 10, 30))
