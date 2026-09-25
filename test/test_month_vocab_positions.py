"""T-4498: every month spelling answers its own month, in every locale.

``scoped_scan`` reads the month from the position of its line in
``months.voc`` and built one capture group per line. German shipped 13 lines
and French 15, because a spelling variant sat on a line of its own, so every
month after the first variant answered one too late and the ones past the
twelfth had no group at all:

    de 'der 1 tag von maerz'    -> 1 April
    de 'der 1 tag von april'    -> 1 May
    de 'der 1 tag von dezember' -> StopIteration
    fr 'le 1 jour de octobre'   -> 1 December
    fr 'le 1 jour de novembre'  -> StopIteration

``extract_scoped_date`` is exported from ``ovos_date_parser``, so the raise
reached the public API on ordinary German and French input.

A month's spellings now share one line, separated by ``|``, and a file that
does not hold twelve lines is refused rather than mis-read. This drives
every spelling of every locale rather than a sample, because a sample is
what let a shift of one go unseen.
"""
import os
import unittest
from datetime import date

import pytest

from ovos_date_parser.scoped_scan import (extract_scoped_date,
                                          load_scoped_vocabulary)

PACKAGE_DIR = os.path.dirname(
    os.path.abspath(__import__("ovos_date_parser").__file__))
LOCALE_DIR = os.path.join(PACKAGE_DIR, "locale")
LANGS = sorted(d for d in os.listdir(LOCALE_DIR)
               if os.path.isdir(os.path.join(LOCALE_DIR, d)))

REF = date(2026, 9, 25)

#: a phrase that names one day of a named month, per locale. Only locales
#: with one here are driven end to end; the vocabulary checks below cover
#: every locale in the tree.
DAY_OF_MONTH = {
    "de": "der 1 tag von {}",
    "fr": "le 1 jour de {}",
    "es": "el 1 dia de {}",
    "it": "il 1 giorno di {}",
    "pt": "o 1 dia de {}",
}


def _voc_lines(lang):
    path = os.path.join(LOCALE_DIR, lang, "months.voc")
    with open(path, encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


class TestMonthsVocShape(unittest.TestCase):
    """Every locale in the tree, not only the ones with a phrase above."""

    def test_every_locale_holds_twelve_lines(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.assertEqual(
                    len(_voc_lines(lang)), 12,
                    f"locale/{lang}/months.voc must hold 12 lines, January "
                    f"first, with a month's spellings on one line")

    def test_every_locale_loads_twelve_months(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                self.assertEqual(len(load_scoped_vocabulary(lang).months), 12)

    def test_a_file_of_the_wrong_length_is_refused(self, ):
        """The guard that keeps this from coming back. A thirteenth line is
        how the defect was written in the first place, and it has to fail
        loudly rather than shift the months."""
        from ovos_date_parser.scoped_scan import _month_alternations
        with self.assertRaises(ValueError) as caught:
            _month_alternations(["a"] * 13, "xx", LOCALE_DIR)
        self.assertIn("13 lines", str(caught.exception))
        self.assertIn("must hold 12", str(caught.exception))


@pytest.mark.parametrize("lang", sorted(DAY_OF_MONTH))
def test_every_spelling_answers_its_own_month(lang):
    """Drive all twelve months, and every variant of each, through the
    public extractor."""
    vocab = load_scoped_vocabulary(lang)
    template = DAY_OF_MONTH[lang]
    for index, line in enumerate(_voc_lines(lang)):
        want = index + 1
        for spelling in line.split("|"):
            result = extract_scoped_date(template.format(spelling), vocab,
                                         ref_date=REF)
            assert result is not None, \
                f"{lang}: {spelling!r} read as no date"
            assert result[0].month == want, (
                f"{lang}: {spelling!r} is month {want} and answered "
                f"{result[0].month}")


@pytest.mark.parametrize("lang", sorted(DAY_OF_MONTH))
def test_the_last_month_does_not_raise(lang):
    """The twelfth line held the spellings that had no capture group, so
    the generator ran off the end and raised out of the parser."""
    vocab = load_scoped_vocabulary(lang)
    for spelling in _voc_lines(lang)[11].split("|"):
        text = DAY_OF_MONTH[lang].format(spelling)
        result = extract_scoped_date(text, vocab, ref_date=REF)
        assert result is not None and result[0].month == 12, text


def test_a_variant_and_its_canonical_form_agree():
    """The two locales that ship variants, named rather than discovered, so
    this test still means something if a future edit drops them."""
    for lang, pairs in (("de", [("märz", "maerz")]),
                        ("fr", [("février", "fevrier"), ("août", "aout"),
                                ("décembre", "decembre")])):
        vocab = load_scoped_vocabulary(lang)
        template = DAY_OF_MONTH[lang]
        for canonical, variant in pairs:
            first = extract_scoped_date(template.format(canonical), vocab,
                                        ref_date=REF)
            second = extract_scoped_date(template.format(variant), vocab,
                                         ref_date=REF)
            assert first is not None and second is not None, (lang, variant)
            assert first[0] == second[0], (
                f"{lang}: {canonical!r} and {variant!r} are the same month "
                f"and answered {first[0]} and {second[0]}")
