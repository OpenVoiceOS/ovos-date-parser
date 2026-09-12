"""Regression tests for the Occitan observations on issue #300.

Every form here was reported or confirmed by a native speaker (oc-FR).
Expected datetimes are hand-derived from the fixed anchor, never pinned
from engine output.
"""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2117, 9, 3, 13, 30, 0)
TZ = default_timezone()


def extract(text, lang="oc", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=TZ)


class TestHourWordVariants(unittest.TestCase):
    """8 has variant spellings: uech (reference), ueit, uoch."""

    def test_ueit(self):
        self.assertEqual(extract("a las ueit")[0], dt(2117, 9, 4, 8, 0))

    def test_uoch(self):
        self.assertEqual(extract("a las uoch")[0], dt(2117, 9, 4, 8, 0))

    def test_ueit_with_half(self):
        self.assertEqual(extract("a las ueit e mièja")[0], dt(2117, 9, 4, 8, 30))


class TestNightVariants(unittest.TestCase):
    """Night has variant spellings, with and without an initial a."""

    def test_nueit(self):
        self.assertEqual(extract("a las 9 de la nueit")[0], dt(2117, 9, 3, 21, 0))

    def test_neit(self):
        self.assertEqual(extract("a las 9 de la neit")[0], dt(2117, 9, 3, 21, 0))

    def test_net(self):
        self.assertEqual(extract("a las 9 de la net")[0], dt(2117, 9, 3, 21, 0))

    def test_nech(self):
        self.assertEqual(extract("a las 9 de la nech")[0], dt(2117, 9, 3, 21, 0))

    def test_nuoch(self):
        self.assertEqual(extract("a las 9 de la nuoch")[0], dt(2117, 9, 3, 21, 0))

    def test_aneit(self):
        self.assertEqual(extract("aneit")[0], dt(2117, 9, 3, 21, 0))

    def test_anet(self):
        self.assertEqual(extract("anet")[0], dt(2117, 9, 3, 21, 0))

    def test_anech(self):
        self.assertEqual(extract("anech")[0], dt(2117, 9, 3, 21, 0))

    def test_anuoch(self):
        self.assertEqual(extract("anuoch")[0], dt(2117, 9, 3, 21, 0))


class TestMonthVariants(unittest.TestCase):
    """April and July have variant spellings: abrial, julh."""

    def test_abrial(self):
        self.assertEqual(extract("15 de abrial")[0], dt(2118, 4, 15, 0, 0))

    def test_julh(self):
        self.assertEqual(extract("15 de julh")[0], dt(2118, 7, 15, 0, 0))


class TestDaypartExpressions(unittest.TestCase):
    """Afternoon dayparts name a meal or the late afternoon.

    14:00, 16:00 and 17:00 are all ahead of the 13:30 anchor, so they
    resolve to the anchor day.
    """

    def test_aprep_dinnar(self):
        self.assertEqual(extract("aprèp dinnar")[0], dt(2117, 9, 3, 14, 0))

    def test_apres_dinnar(self):
        self.assertEqual(extract("après dinnar")[0], dt(2117, 9, 3, 14, 0))

    def test_aprep_merende(self):
        self.assertEqual(extract("aprèp merende")[0], dt(2117, 9, 3, 16, 0))

    def test_apres_merende(self):
        self.assertEqual(extract("après merende")[0], dt(2117, 9, 3, 16, 0))

    def test_vesprada(self):
        self.assertEqual(extract("vesprada")[0], dt(2117, 9, 3, 17, 0))


class TestLastMarkerVariants(unittest.TestCase):
    """"last" and "previous" have variant spellings."""

    def test_darrer_setmana(self):
        self.assertEqual(extract("darrèr setmana")[0], dt(2117, 8, 27, 0, 0))

    def test_darrieir_mes(self):
        self.assertEqual(extract("darrièir mes")[0], dt(2117, 8, 3, 0, 0))

    def test_precedent_mes(self):
        self.assertEqual(extract("lo mes precedent")[0], dt(2117, 8, 3, 0, 0))

    def test_precedenta_setmana(self):
        self.assertEqual(extract("la setmana precedenta")[0], dt(2117, 8, 27, 0, 0))

    def test_precedent_an(self):
        self.assertEqual(extract("l'an precedent")[0], dt(2116, 9, 3, 0, 0))


class TestPostNominalLastMarkers(unittest.TestCase):
    """Occitan puts the adjective after the noun: "la setmana darrièra"."""

    def test_setmana_darrera(self):
        self.assertEqual(extract("la setmana darrièra")[0], dt(2117, 8, 27, 0, 0))

    def test_setmana_darrera_alt(self):
        self.assertEqual(extract("la setmana darrèra")[0], dt(2117, 8, 27, 0, 0))

    def test_setmana_darrieira(self):
        self.assertEqual(extract("la setmana darrièira")[0], dt(2117, 8, 27, 0, 0))

    def test_mes_darrier(self):
        self.assertEqual(extract("lo mes darrier")[0], dt(2117, 8, 3, 0, 0))

    def test_an_darrer(self):
        self.assertEqual(extract("l'an darrèr")[0], dt(2116, 9, 3, 0, 0))

    def test_setmana_ultim(self):
        self.assertEqual(extract("la setmana ultima")[0], dt(2117, 8, 27, 0, 0))

    def test_feigned_old_order_still_works(self):
        self.assertEqual(extract("darrèr setmana")[0], dt(2117, 8, 27, 0, 0))
        self.assertEqual(extract("la setmana passada")[0], dt(2117, 8, 27, 0, 0))


class TestPostNominalNextMarkers(unittest.TestCase):
    """Next has feminine and prochan variants the masculine order gets."""

    def test_setmana_seguenta(self):
        self.assertEqual(extract("la setmana seguenta")[0], dt(2117, 9, 10, 0, 0))

    def test_setmana_venenta(self):
        self.assertEqual(extract("la setmana venenta")[0], dt(2117, 9, 10, 0, 0))

    def test_setmana_prochana(self):
        self.assertEqual(extract("la setmana prochana")[0], dt(2117, 9, 10, 0, 0))

    def test_setmana_seguentas(self):
        self.assertEqual(extract("las setmanas seguentas")[0], dt(2117, 9, 10, 0, 0))

    def test_masculine_order_still_works(self):
        self.assertEqual(extract("la setmana seguent")[0], dt(2117, 9, 10, 0, 0))
        self.assertEqual(extract("lo mes seguent")[0], dt(2117, 10, 3, 0, 0))
        self.assertEqual(extract("l'an seguent")[0], dt(2118, 9, 3, 0, 0))

    def test_mes_prochan(self):
        self.assertEqual(extract("lo mes prochan")[0], dt(2117, 10, 3, 0, 0))

    def test_an_prochan(self):
        self.assertEqual(extract("l'an prochan")[0], dt(2118, 9, 3, 0, 0))

    def test_pre_nominal_prochan_still_works(self):
        self.assertEqual(extract("prochan mes")[0], dt(2117, 10, 3, 0, 0))


class TestElidedArticleLeftover(unittest.TestCase):
    """The elided article must not leak into the leftover text.

    clean_string turns l'an into l an; l sat outside the noise words, so
    the article survived consumption and polluted every leftover.
    """

    def test_an_passat_leftover(self):
        d, rest = extract("l'an passat")
        self.assertEqual(d, dt(2116, 9, 3, 0, 0))
        self.assertEqual(rest, "")

    def test_an_darrer_leftover(self):
        d, rest = extract("l'an darrièr")
        self.assertEqual(d, dt(2116, 9, 3, 0, 0))
        self.assertEqual(rest, "")

    def test_an_seguent_leftover(self):
        d, rest = extract("l'an seguent")
        self.assertEqual(d, dt(2118, 9, 3, 0, 0))
        self.assertEqual(rest, "")

    def test_prefix_context_leftover(self):
        d, rest = extract("reunion l'an passat")
        self.assertEqual(d, dt(2116, 9, 3, 0, 0))
        self.assertEqual(rest, "reunion")

    def test_time_words_survive(self):
        d, rest = extract("reunion l'an seguent a las tres")
        self.assertEqual(d, dt(2118, 9, 3, 3, 0))
        self.assertEqual(rest, "reunion")


class TestDayBeforeYesterday(unittest.TestCase):
    """The day before yesterday: ièr delà/delai, passat ièr, abans-ièr."""

    def test_ier_dela(self):
        self.assertEqual(extract("ièr delà")[0], dt(2117, 9, 1, 0, 0))

    def test_ier_delai(self):
        self.assertEqual(extract("ièr delai")[0], dt(2117, 9, 1, 0, 0))

    def test_passat_ier(self):
        self.assertEqual(extract("passat ièr")[0], dt(2117, 9, 1, 0, 0))

    def test_abans_ier(self):
        self.assertEqual(extract("abans ièr")[0], dt(2117, 9, 1, 0, 0))

    def test_davant_ier(self):
        self.assertEqual(extract("davant ièr")[0], dt(2117, 9, 1, 0, 0))


class TestUnchangedSemantics(unittest.TestCase):
    """Existing readings the report did not ask to change."""

    def test_en_5_jorns_still_future(self):
        # "en 5 jorns" reads as future here; the duration reading is
        # recorded in the issue, not changed in this parser
        self.assertEqual(extract("en 5 jorns")[0], dt(2117, 9, 8, 0, 0))

    def test_abrial_does_not_break_abril(self):
        self.assertEqual(extract("15 de abril")[0], dt(2118, 4, 15, 0, 0))

    def test_julhet_unchanged(self):
        self.assertEqual(extract("15 de julhet")[0], dt(2118, 7, 15, 0, 0))

    def test_octobre_unchanged(self):
        self.assertEqual(extract("15 d'octobre")[0], dt(2117, 10, 15, 0, 0))


if __name__ == "__main__":
    unittest.main()
