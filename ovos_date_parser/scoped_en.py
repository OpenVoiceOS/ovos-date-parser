"""English calendar-scoped ordinal and season extraction.

The surface forms live in chronologia's packaged ``locale/en/*.voc`` (unit
names, month names, season names, markers), since this package ships no
``locale/en`` of its own, and are composed by the shared grammar in
:mod:`ovos_date_parser.scoped_scan`.  This module only binds the English
spelled-number normaliser.

Recognised phrasing: "the 21st century", "the 3rd millennium", "the 3rd
week of june", "the last day of february 2024", "the 100th day of the
year", "the first decade of the 21st century", "summer of 1969",
"next winter", "last spring", "this autumn"/"this fall", and the
named holidays English binds in chronologia ("christmas", "next easter").
"""
from functools import lru_cache

from ovos_number_parser.numbers_en import numbers_to_digits_en

from ovos_date_parser.ranges import Hemisphere
from ovos_date_parser.scoped_scan import (ScopedVocabulary,
                                          extract_scoped_date,
                                          load_scoped_vocabulary)

@lru_cache(maxsize=None)
def _scoped_vocab_en() -> ScopedVocabulary:
    return load_scoped_vocabulary("en")


def __getattr__(name):
    # The vocabulary loads on first use, so importing the package does not
    # read every phrase set.
    if name == "SCOPED_VOCAB_EN":
        return _scoped_vocab_en()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def extract_scoped_date_en(text: str, ref_date=None,
                           hemisphere: Hemisphere = Hemisphere.NORTH):
    """Extract a scoped ordinal or season from English text.

    Thin wrapper binding :data:`SCOPED_VOCAB_EN` and the English
    spelled-number normaliser to the shared scanner — see
    :func:`ovos_date_parser.scoped_scan.extract_scoped_date`.
    """
    return extract_scoped_date(
        numbers_to_digits_en(text, ordinals=True), _scoped_vocab_en(),
        ref_date=ref_date, hemisphere=hemisphere, lang="en")
