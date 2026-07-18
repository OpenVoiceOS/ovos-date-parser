"""Danish datetime extraction: clock notation and adversarial input.

Anchors reflect Danish 24-hour usage, not pinned from engine output.
"""
import unittest
from datetime import datetime

from ovos_config.locale import get_default_tz as default_timezone

import ovos_date_parser as _odp

ANCHOR = datetime(2117, 9, 3, 13, 30)  # a fixed non-midnight anchor
TZ = default_timezone()


def extract(text, lang="da", anchor=ANCHOR):
    res = _odp.extract_datetime(text, lang=lang, anchorDate=anchor)
    if res is not None and res[0] is not None and res[0].tzinfo is None:
        res = [res[0].replace(tzinfo=TZ), res[1]]
    return res


def dt(y, mo, d, h=0, mi=0):
    return datetime(y, mo, d, h, mi, tzinfo=TZ)


class TestBareHour(unittest.TestCase):
    def test_bare_number_hour(self):
        self.assertEqual(extract("20")[0], dt(2117, 9, 3, 20))


class TestAdversarial(unittest.TestCase):
    """Digit-leading tokens with trailing letters or slashes must not crash."""

    def test_hour_letter_suffix(self):
        for token in ["20h", "klokken 20h", "3h30"]:
            with self.subTest(token=token):
                extract(token)  # must not raise

    def test_slash_and_glued_tokens(self):
        for token in ["15/06/20", "3/0/0", "0/0/0", "10sept", "7d"]:
            with self.subTest(token=token):
                extract(token)  # must not raise

    def test_empty_and_gibberish(self):
        self.assertIsNone(extract(""))
        self.assertIsNone(extract("   "))
        self.assertIsNone(extract("qwerty asdf"))


if __name__ == "__main__":
    unittest.main()
