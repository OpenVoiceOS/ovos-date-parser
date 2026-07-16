import unittest
from datetime import datetime
from ovos_date_parser.dates_ast import nice_year_ast, nice_weekday_ast, nice_month_ast, nice_day_ast, nice_date_ast, nice_time_ast

class TestNiceDateTimeAST(unittest.TestCase):
    def setUp(self):
        self.test_date = datetime(2023, 6, 5, 17, 30)  # Monday, June 5, 2023, 17:30
        self.test_now = datetime(2023, 6, 5)  # Same day as test_date

    def test_nice_year_ast(self):
        self.assertEqual(nice_year_ast(self.test_date), "dos mil y ventitrés")
        self.assertEqual(nice_year_ast(self.test_date, bc=True), "dos mil y ventitrés a.C.")

    def test_nice_weekday_ast(self):
        self.assertEqual(nice_weekday_ast(self.test_date), "Llunes")

    def test_nice_month_ast(self):
        self.assertEqual(nice_month_ast(self.test_date), "Xunu")

    def test_nice_day_ast(self):
        self.assertEqual(nice_day_ast(self.test_date, date_format='DMY'), "5 Xunu")
        self.assertEqual(nice_day_ast(self.test_date, date_format='MDY'), "Xunu 5")
        self.assertEqual(nice_day_ast(self.test_date, include_month=False), "5")

    def test_nice_date_ast(self):
        self.assertEqual(nice_date_ast(self.test_date, self.test_now), "güei")
        future_date = datetime(2023, 6, 6)
        self.assertEqual(nice_date_ast(future_date, self.test_now), "mañana")
        past_date = datetime(2023, 6, 4)
        self.assertEqual(nice_date_ast(past_date, self.test_now), "ayeri")

    def test_nice_time_ast(self):
        self.assertEqual(nice_time_ast(self.test_date, speech=True, use_24hour=True), "les diecisiete trenta")
        self.assertEqual(nice_time_ast(self.test_date, speech=True, use_24hour=False), "les cinco y media")
        self.assertEqual(nice_time_ast(self.test_date, speech=False, use_24hour=True), "17:30")
        self.assertEqual(nice_time_ast(self.test_date, speech=False, use_24hour=False), "5:30")
        # one o'clock uses the singular article
        one = datetime(2023, 6, 5, 13, 0)
        self.assertEqual(nice_time_ast(one, speech=True, use_24hour=False), "la una en puntu")
        # quarter past / quarter to
        self.assertEqual(nice_time_ast(datetime(2023, 6, 5, 8, 15), use_24hour=False), "les ocho y cuartu")
        self.assertEqual(nice_time_ast(datetime(2023, 6, 5, 7, 45), use_24hour=False), "les ocho menos cuartu")
        # am/pm day periods
        self.assertEqual(nice_time_ast(datetime(2023, 6, 5, 9, 30), use_ampm=True), "les nueve y media de la mañana")
        self.assertEqual(nice_time_ast(datetime(2023, 6, 5, 22, 30), use_ampm=True), "les diez y media de la nueche")

if __name__ == '__main__':
    unittest.main()
