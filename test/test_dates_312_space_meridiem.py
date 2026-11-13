"""Space-separated ``H MM <meridiem>`` clock forms in es/pt/de.

Regression coverage for issue #312. Before the fix, "hour minute
<meridiem>" phrasing (two plain digit groups followed by a word like
"tarde"/"madrugada"/"nachmittags") either crashed (es "madrugada" is the
last word in the sentence) or produced the wrong hour because the
already-parsed 12-hour value was never converted to 24-hour once the
meridiem word was found.
"""
import unittest
from datetime import datetime

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2024, 6, 15, 10, 0)


class TestIssue312Es(unittest.TestCase):
    def test_madrugada_last_word_does_not_crash(self):
        # this used to raise IndexError: list assignment index out of range
        result = extract_datetime("12 05 de la madrugada", lang="es",
                                   anchorDate=ANCHOR)
        self.assertIsNotNone(result)

    def test_tarde_converts_to_24h(self):
        result = extract_datetime("11 55 de la tarde", lang="es",
                                   anchorDate=ANCHOR)
        dt, remainder = result
        self.assertEqual((dt.hour, dt.minute), (23, 55))

    def test_twelve_oclock_madrugada_is_midnight(self):
        dt, remainder = extract_datetime("12 05 de la madrugada", lang="es",
                                          anchorDate=ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (0, 5))

    def test_twelve_oclock_noche_is_midnight(self):
        dt, remainder = extract_datetime("12 05 de la noche", lang="es",
                                          anchorDate=ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (0, 5))

    def test_one_oclock_madrugada_is_unchanged(self):
        dt, remainder = extract_datetime("1 05 de la madrugada", lang="es",
                                          anchorDate=ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (1, 5))

    def test_twelve_oclock_tarde_is_unchanged(self):
        dt, remainder = extract_datetime("12 05 de la tarde", lang="es",
                                          anchorDate=ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (12, 5))

    def test_twelve_oclock_manana_is_noon(self):
        dt, remainder = extract_datetime("12 05 de la mañana", lang="es",
                                          anchorDate=ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (12, 5))


class TestIssue312Pt(unittest.TestCase):
    def test_tarde_converts_to_24h(self):
        result = extract_datetime("11 55 da tarde", lang="pt",
                                   anchorDate=ANCHOR)
        dt, remainder = result
        self.assertEqual((dt.hour, dt.minute), (23, 55))

    def test_twelve_oclock_noite_is_midnight(self):
        dt, remainder = extract_datetime("12 05 da noite", lang="pt",
                                          anchorDate=ANCHOR)
        self.assertEqual((dt.hour, dt.minute), (0, 5))
