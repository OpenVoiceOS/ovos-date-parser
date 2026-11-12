"""The gl and an date-time joins do not repeat the article or the verb.

Galician contracts the preposition "a" with the article: Real Academia
Galega, Normas ortográficas e morfolóxicas do idioma galego, 23rd edition
(2012), 2.7.1: "á (a + a artigo; subst.)", "ás (a + as artigo; subst.)". nice_time_gl gives the hour with its article ("a unha e vinte",
"as catro e vinte"), so the date-time says "á unha e vinte" and "ás catro
e vinte", not "ás a unha" or "ás as catro".

In 12-hour form nice_time_an gives a whole clause ("Son las cuatro y
vinte"), so it cannot follow "a las". The date-time puts it after the date
as a clause of its own. In 24-hour form the time is a bare number
("trece quince"), and the join stays "a las" as before."""
import unittest
from datetime import datetime

from ovos_date_parser import nice_date, nice_date_time, nice_time

NOW = datetime(2024, 1, 1)


class TestDateTimeJoin(unittest.TestCase):

    def test_gl_examples(self):
        for hour, spoken in ((1, "á unha e vinte"), (13, "á unha e vinte"),
                             (16, "ás catro e vinte")):
            with self.subTest(hour=hour):
                dt = datetime(2024, 3, 5, hour, 20)
                self.assertEqual(nice_date_time(dt, "gl", now=NOW),
                                 nice_date(dt, "gl", now=NOW) + " " + spoken)

    def test_gl_every_time(self):
        contraction = {"a": "á", "as": "ás"}
        wrong = []
        for hour in range(24):
            for minute in range(0, 60, 5):
                for use_24hour in (False, True):
                    dt = datetime(2024, 3, 5, hour, minute)
                    article, _, rest = nice_time(
                        dt, "gl", use_24hour=use_24hour).partition(" ")
                    expected = (nice_date(dt, "gl", now=NOW) + " "
                                + contraction[article] + " " + rest)
                    if nice_date_time(dt, "gl", now=NOW,
                                      use_24hour=use_24hour) != expected:
                        wrong.append((hour, minute, use_24hour))
        self.assertEqual(wrong, [])

    def test_an(self):
        dt = datetime(2024, 3, 5, 16, 20)
        self.assertEqual(nice_date_time(dt, "an"),
                         nice_date(dt, "an") + ", son las cuatro y vinte")
        dt = datetime(2024, 3, 5, 1, 20)
        self.assertEqual(nice_date_time(dt, "an"),
                         nice_date(dt, "an") + ", ye la una y vinte")

    def test_an_24_hour_keeps_a_las(self):
        for hour in range(24):
            for minute in range(0, 60, 5):
                dt = datetime(2024, 3, 5, hour, minute)
                with self.subTest(hour=hour, minute=minute):
                    self.assertEqual(
                        nice_date_time(dt, "an", use_24hour=True),
                        nice_date(dt, "an") + " a las "
                        + nice_time(dt, "an", use_24hour=True))


if __name__ == "__main__":
    unittest.main()
