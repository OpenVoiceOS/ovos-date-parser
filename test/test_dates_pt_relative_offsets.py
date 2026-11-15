"""Relative day and period offsets followed by a weekday, pt-PT and pt-BR.

Expected datetimes are derived by hand from the anchors, never from engine
output. Saturday 2026-10-17 12:00 is the anchor unless a test names another.
"""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from ovos_date_parser import extract_datetime

TZ = ZoneInfo("Europe/Lisbon")
SATURDAY = datetime(2026, 10, 17, 12, 0, tzinfo=TZ)
WEDNESDAY = datetime(2026, 10, 14, 12, 0, tzinfo=TZ)
FRIDAY = datetime(2026, 10, 16, 10, 0, tzinfo=TZ)
SUNDAY = datetime(2026, 10, 18, 10, 0, tzinfo=TZ)
MONDAY = datetime(2026, 10, 19, 9, 0, tzinfo=TZ)
JAN31 = datetime(2026, 1, 31, 12, 0, tzinfo=TZ)
DEC31 = datetime(2026, 12, 31, 12, 0, tzinfo=TZ)
FEB29 = datetime(2028, 2, 29, 12, 0, tzinfo=TZ)
LANGS = ("pt-PT", "pt-BR")


class TestPtRelativeOffsets(unittest.TestCase):
    def assertParses(self, text, expected, anchor=SATURDAY):
        for lang in LANGS:
            with self.subTest(text=text, lang=lang):
                res = extract_datetime(text, anchorDate=anchor, lang=lang)
                self.assertIsNotNone(res)
                self.assertEqual(res[0].replace(tzinfo=None), expected)

    def assertNoDate(self, text, anchor=SATURDAY):
        for lang in LANGS:
            with self.subTest(text=text, lang=lang):
                self.assertIsNone(extract_datetime(text, anchorDate=anchor, lang=lang))

    def test_spelled_period_offsets(self):
        self.assertParses("daqui a uma semana", datetime(2026, 10, 24))
        self.assertParses("daqui a duas semanas", datetime(2026, 10, 31))
        self.assertParses("daqui a três dias", datetime(2026, 10, 20))
        self.assertParses("daqui a um mês", datetime(2026, 11, 17))
        self.assertParses("daqui a um ano", datetime(2027, 10, 17))
        self.assertParses("dentro de uma semana", datetime(2026, 10, 24))
        self.assertParses("dentro de três dias", datetime(2026, 10, 20))

    def test_period_offset_then_weekday(self):
        self.assertParses("é daqui a uma semana sábado", datetime(2026, 10, 24))
        self.assertParses("daqui a uma semana sábado", datetime(2026, 10, 24))
        self.assertParses("daqui a uma semana quarta-feira", datetime(2026, 10, 21),
                          anchor=WEDNESDAY)

    def test_day_after_tomorrow_then_weekday(self):
        self.assertParses("depois de amanhã segunda-feira", datetime(2026, 10, 19))
        self.assertParses("depois de amanhã segunda - feira", datetime(2026, 10, 19))
        self.assertParses("depois de amanhã terça-feira", datetime(2026, 10, 20))
        self.assertParses("é depois de amanhã segunda-feira?", datetime(2026, 10, 19))
        self.assertParses("depois de amanhã sexta-feira", datetime(2026, 10, 16),
                          anchor=WEDNESDAY)

    def test_day_before_yesterday_then_weekday(self):
        self.assertParses("foi anteontem quinta-feira", datetime(2026, 10, 15))
        self.assertParses("foi antes de ontem quinta-feira", datetime(2026, 10, 15))
        self.assertParses("ontem sexta-feira", datetime(2026, 10, 16))

    def test_day_offsets_alone(self):
        self.assertParses("depois de amanhã", datetime(2026, 10, 19))
        self.assertParses("depois de amanhã de manhã", datetime(2026, 10, 19, 8))
        self.assertParses("depois de amanhã às 10h", datetime(2026, 10, 19, 10))
        self.assertParses("antes de ontem", datetime(2026, 10, 15))
        self.assertParses("anteontem", datetime(2026, 10, 15))

    def test_confusables_keep_their_value(self):
        self.assertParses("amanhã", datetime(2026, 10, 18))
        self.assertParses("hoje", datetime(2026, 10, 17))
        self.assertParses("ontem", datetime(2026, 10, 16))
        self.assertParses("segunda-feira", datetime(2026, 10, 19))
        self.assertParses("sábado", datetime(2026, 10, 17))
        self.assertParses("amanhã sexta-feira", datetime(2026, 10, 23))
        self.assertParses("daqui a 3 dias", datetime(2026, 10, 20))
        self.assertParses("em 2 semanas", datetime(2026, 10, 31))

    def test_sunday_after_relative_day(self):
        self.assertParses("amanhã domingo", datetime(2026, 10, 18))
        self.assertParses("amanhã, domingo, às 9", datetime(2026, 10, 18, 9))
        self.assertParses("depois de amanhã domingo", datetime(2026, 10, 18), anchor=FRIDAY)
        self.assertParses("daqui a uma semana domingo", datetime(2026, 10, 25), anchor=SUNDAY)
        self.assertParses("hoje domingo", datetime(2026, 10, 18), anchor=SUNDAY)

    def test_weekday_after_month_and_year_offsets(self):
        self.assertParses("daqui a dois anos sexta-feira", datetime(2028, 10, 20))
        self.assertParses("daqui a 2 anos sexta-feira", datetime(2028, 10, 20))
        self.assertParses("daqui a um mês sexta-feira", datetime(2026, 11, 20))
        self.assertParses("daqui a 1 mês sexta-feira", datetime(2026, 11, 20))

    def test_weekday_in_the_week_that_many_weeks_out(self):
        self.assertParses("daqui a duas semanas sexta-feira", datetime(2026, 10, 30))
        self.assertParses("daqui a 2 semanas sexta-feira", datetime(2026, 10, 30))
        self.assertParses("há uma semana sexta-feira", datetime(2026, 10, 9))

    def test_only_offset_markers_make_a_count(self):
        self.assertParses("faz um ano que não te vejo", datetime(2025, 10, 17))
        self.assertParses("há três dias", datetime(2026, 10, 14))
        self.assertParses("em duas semanas", datetime(2026, 10, 31))
        self.assertParses("daqui a quinze dias", datetime(2026, 10, 31))
        for text in ("tenho vinte anos", "ele tem trinta anos",
                     "a casa tem cem anos", "mil anos",
                     "o meu filho tem cinco anos",
                     "passei duas semanas em paris", "tive uma semana difícil",
                     "uma semana de férias", "fiquei três dias em casa",
                     "demorou três dias", "estive dois meses no brasil",
                     "sete dias por semana"):
            self.assertNoDate(text)

    def test_next_and_last_month_and_year(self):
        self.assertParses("no próximo mês", datetime(2026, 11, 17))
        self.assertParses("o mês que vem", datetime(2026, 11, 17))
        self.assertParses("o mês seguinte", datetime(2026, 11, 17))
        self.assertParses("o mês passado", datetime(2026, 9, 17))
        self.assertParses("no próximo ano", datetime(2027, 10, 17))
        self.assertParses("o ano que vem", datetime(2027, 10, 17))
        self.assertParses("o ano passado", datetime(2025, 10, 17))

    def test_next_and_last_week(self):
        self.assertParses("na próxima semana", datetime(2026, 10, 24))
        self.assertParses("a semana que vem", datetime(2026, 10, 24))
        self.assertParses("a semana passada", datetime(2026, 10, 10))

    def test_month_and_year_end_clamping(self):
        self.assertParses("no próximo mês", datetime(2026, 2, 28), anchor=JAN31)
        self.assertParses("o mês passado", datetime(2025, 12, 31), anchor=JAN31)
        self.assertParses("o mês que vem", datetime(2027, 1, 31), anchor=DEC31)
        self.assertParses("o mês passado", datetime(2026, 11, 30), anchor=DEC31)
        self.assertParses("na próxima semana", datetime(2027, 1, 7), anchor=DEC31)
        self.assertParses("no próximo ano", datetime(2029, 2, 28), anchor=FEB29)
        self.assertParses("o ano passado", datetime(2027, 2, 28), anchor=FEB29)
        self.assertParses("no próximo mês", datetime(2028, 3, 29), anchor=FEB29)

    def test_month_offsets_with_a_count_keep_their_value(self):
        self.assertParses("daqui a um mês", datetime(2026, 11, 17))
        self.assertParses("há um mês", datetime(2026, 9, 17))
        self.assertParses("daqui a um mês", datetime(2026, 2, 28), anchor=JAN31)
        self.assertParses("há um mês", datetime(2025, 12, 31), anchor=JAN31)

    def test_last_period_with_and_without_accent(self):
        for text, expected in (("o último mês", datetime(2026, 9, 17)),
                               ("o ultimo mes", datetime(2026, 9, 17)),
                               ("a última semana", datetime(2026, 10, 10)),
                               ("a ultima semana", datetime(2026, 10, 10)),
                               ("o último ano", datetime(2025, 10, 17)),
                               ("o ultimo ano", datetime(2025, 10, 17)),
                               ("o último sábado", datetime(2026, 10, 10)),
                               ("o ultimo sabado", datetime(2026, 10, 10)),
                               ("a última sexta-feira", datetime(2026, 10, 16))):
            self.assertParses(text, expected)

    def test_last_weekday_of_the_month(self):
        self.assertParses("a última sexta-feira do mês", datetime(2026, 10, 30))
        self.assertParses("a ultima sexta-feira do mes", datetime(2026, 10, 30))
        self.assertParses("o último sábado do mês", datetime(2026, 10, 31))
        self.assertParses("o último domingo do mês", datetime(2026, 10, 25))
        self.assertParses("a última segunda-feira do mês", datetime(2026, 10, 26))
        self.assertParses("a última sexta-feira do mês", datetime(2026, 1, 30), anchor=JAN31)

    def test_faz_before_a_count_is_ago_only_for_elapsed_time(self):
        self.assertParses("faz dois dias", datetime(2026, 10, 15))
        self.assertParses("faz dois dias que não como", datetime(2026, 10, 15))
        self.assertParses("faz um mês", datetime(2026, 9, 17))
        self.assertParses("faz uma semana e dois dias", datetime(2026, 10, 8))

    def test_faz_as_the_verb_fazer_keeps_the_stated_day(self):
        self.assertParses("o bebé faz um ano amanhã", datetime(2026, 10, 18))
        self.assertParses("o bebê faz um ano amanhã", datetime(2026, 10, 18))
        self.assertParses("hoje faz um dia de sol", datetime(2026, 10, 17))
        self.assertParses("faz um dia bonito hoje", datetime(2026, 10, 17))
        self.assertNoDate("faz um dia lindo")

    def test_faz_after_a_subject_or_a_date_word_is_the_verb(self):
        for text, expected in (
                ("amanhã o bebé faz um ano", datetime(2026, 10, 18)),
                ("hoje a maria faz trinta anos", datetime(2026, 10, 17)),
                ("a minha filha faz dez anos", datetime(2026, 10, 17)),
                ("amanhã faz um ano", datetime(2026, 10, 18)),
                ("amanhã faz um ano que nos casámos", datetime(2026, 10, 18)),
                ("no sábado o bebé faz um ano", datetime(2026, 10, 17))):
            self.assertParses(text, expected)
        self.assertNoDate("o bebé faz dois meses")

    def test_faz_keeps_its_word_in_the_remainder(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                _, rest = extract_datetime("no sábado o bebé faz um ano",
                                           anchorDate=SATURDAY, lang=lang)
                self.assertIn("faz", rest.split())
                self.assertNotIn("ha", rest.split())

    def test_ja_faz_counts_back(self):
        self.assertParses("já faz dois dias", datetime(2026, 10, 15))

    def test_birthday_after_a_month_keeps_the_anchor_day(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                res = extract_datetime("em março faz três anos",
                                       anchorDate=SATURDAY, lang=lang)
                self.assertEqual(res[0].date(), SATURDAY.date())

    def test_birthday_in_a_month_is_not_in_the_past(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                res = extract_datetime("ela faz dois anos em maio",
                                       anchorDate=SATURDAY, lang=lang)
                self.assertGreaterEqual(res[0].date(), SATURDAY.date())

    def test_short_weekday_of_another_week(self):
        for text, expected in (
                ("na sexta da semana que vem", datetime(2026, 10, 30)),
                ("a sexta da semana que vem", datetime(2026, 10, 30)),
                ("sexta da semana que vem", datetime(2026, 10, 30)),
                ("na sexta-feira da semana que vem", datetime(2026, 10, 30)),
                ("na segunda da próxima semana", datetime(2026, 10, 26)),
                ("na quinta da semana passada", datetime(2026, 10, 15)),
                ("no sábado da semana passada", datetime(2026, 10, 17))):
            self.assertParses(text, expected, anchor=MONDAY)

    def test_weekday_then_week_that_comes(self):
        self.assertParses("na segunda semana que vem", datetime(2026, 10, 19))

    def test_ordinal_week_is_still_not_a_weekday(self):
        self.assertNoDate("a segunda semana")

    def test_not_a_date(self):
        self.assertNoDate("depois do almoço")
        self.assertNoDate("daqui a pouco")
        self.assertNoDate("segunda vez")
        self.assertNoDate("foi a segunda vez que ele veio")


if __name__ == "__main__":
    unittest.main()
