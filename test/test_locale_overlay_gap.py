"""What ``ovos_date_parser/locale/`` still supplies that chronologia does not.

The five folders de, es, fr, it and pt overlay chronologia's packaged locale
file by file. They exist to be deleted: the reckoning core is the one home for
date vocabulary. The delete is safe only while no surface is lost, so the
surfaces the overlay alone carries are pinned here by value.

``GAP`` empty for a language means that language's folder can go. A new entry
means the overlay grew a surface that belongs upstream instead. A missing entry
means chronologia gained the surface, and the delete moved one language closer.

The apostrophe rows are not a plain gap. chronologia tokenises punctuation away
and registers ``l``, ``d`` and the un-elided articles; this package escapes each
surface into a regex alternation, so it needs the written ``l'``, ``d'`` and
``dell'``. Which side carries an elided article is an open question, and
``marker_article``/``marker_of`` wait on its answer.
"""
import os
from functools import lru_cache

import pytest
from ovos_spec_tools import LocaleResources

from ovos_date_parser.eras_scan import LOCALE_DIR, _chronologia_locale_dir

OVERLAY_LANGS = ["de", "es", "fr", "it", "pt"]

#: surface -> only in this package's overlay, per language and phrase set
GAP = {
    "de": {"months": ["maerz"]},
    "es": {},
    "fr": {
        "era_julian_prefix": ["jour julien numéro"],
        "marker_article": ["l'"],
        "marker_of": ["d'"],
        "months": ["aout", "decembre", "fevrier"],
    },
    "it": {
        "marker_article": ["l'"],
        "marker_of": ["dell", "dell'"],
    },
    "pt": {"era_julian_prefix": ["dia juliano número"]},
}


def _phrase_sets(lang):
    """The ``.voc`` base names the overlay ships for ``lang``."""
    folder = os.path.join(LOCALE_DIR, lang)
    return sorted(name[:-4] for name in os.listdir(folder)
                  if name.endswith(".voc"))


@lru_cache(maxsize=None)
def _resources(root):
    """One reader per root: building it indexes the whole locale tree."""
    return LocaleResources(root)


def _surfaces(root, name, lang):
    try:
        return set(_resources(root).load_vocabulary(name, lang))
    except FileNotFoundError:
        return None


@pytest.mark.parametrize("lang", OVERLAY_LANGS)
def test_every_overlaid_phrase_set_also_exists_upstream(lang):
    """Deleting the folder never removes a whole phrase set.

    A base name the overlay alone holds would turn a form off for the
    language, or raise for the two sets ``scoped_scan`` reads without a guard.
    """
    chronologia = _chronologia_locale_dir()
    absent = [name for name in _phrase_sets(lang)
              if _surfaces(chronologia, name, lang) is None]
    assert absent == [], (
        f"chronologia has no {absent} for {lang!r}; deleting "
        f"locale/{lang} would drop the phrase set, not just shadow it")


@pytest.mark.parametrize("lang", OVERLAY_LANGS)
def test_the_overlay_only_gap_is_the_recorded_one(lang):
    """Every surface the overlay alone carries is named in ``GAP``."""
    chronologia = _chronologia_locale_dir()
    measured = {}
    for name in _phrase_sets(lang):
        own = _surfaces(LOCALE_DIR, name, lang) or set()
        upstream = _surfaces(chronologia, name, lang) or set()
        only_here = sorted(own - upstream)
        if only_here:
            measured[name] = only_here
    assert measured == GAP[lang]
