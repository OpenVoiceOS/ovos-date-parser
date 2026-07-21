import unittest
from datetime import datetime, timedelta

# Import all the functions from the actual dates_pt module
from ovos_date_parser.dates_pt import (
    nice_year_pt, nice_weekday_pt, nice_month_pt, nice_day_pt,
    nice_date_time_pt, nice_date_pt, nice_time_pt,
    extract_datetime_pt, extract_duration_pt,
    WEEKDAYS_PT, MONTHS_PT
)


class TestNiceYearPt(unittest.TestCase):
    """Test cases for nice_year_pt function - using unittest framework"""
    
    def test_nice_year_current_era(self):
        """Test formatting of current era years"""
        dt = datetime(2023, 1, 1)
        result = nice_year_pt(dt)
        self.assertIsInstance(result, str)
        self.assertNotIn("a.C.", result)
    
    def test_nice_year_bc(self):
        """Test formatting of BC years"""
        dt = datetime(100, 1, 1)
        result = nice_year_pt(dt, bc=True)
        self.assertIsInstance(result, str)
        self.assertIn("a.C.", result)
    
    def test_nice_year_edge_cases(self):
        """Test edge cases for year formatting"""
        # Year 1
        dt = datetime(1, 1, 1)
        result = nice_year_pt(dt)
        self.assertIsInstance(result, str)
        
        # Year 2000
        dt = datetime(2000, 1, 1)
        result = nice_year_pt(dt)
        self.assertIsInstance(result, str)


class TestNiceWeekdayPt(unittest.TestCase):
    """Test cases for nice_weekday_pt function"""
    
    def test_all_weekdays(self):
        """Test all weekdays are properly formatted"""
        expected_weekdays = [
            "Segunda-feira", "Terça-feira", "Quarta-feira",
            "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
        ]
        
        for i in range(7):
            # Create a datetime for each weekday (starting from Monday = 0)
            dt = datetime(2023, 1, 2 + i)  # Jan 2, 2023 is a Monday
            result = nice_weekday_pt(dt)
            self.assertEqual(result, expected_weekdays[i])
    
    def test_weekday_capitalization(self):
        """Test that weekdays are properly capitalized"""
        dt = datetime(2023, 1, 2)  # Monday
        result = nice_weekday_pt(dt)
        self.assertTrue(result[0].isupper())
        self.assertTrue(result.startswith("Segunda-feira"))


class TestNiceMonthPt(unittest.TestCase):
    """Test cases for nice_month_pt function"""
    
    def test_all_months(self):
        """Test all months are properly formatted"""
        expected_months = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        
        for i in range(1, 13):
            dt = datetime(2023, i, 1)
            result = nice_month_pt(dt)
            self.assertEqual(result, expected_months[i-1])
    
    def test_month_capitalization(self):
        """Test that months are properly capitalized"""
        dt = datetime(2023, 1, 1)
        result = nice_month_pt(dt)
        self.assertTrue(result[0].isupper())


class TestNiceDayPt(unittest.TestCase):
    """Test cases for nice_day_pt function"""
    
    def test_day_with_month_dmy(self):
        """Test day formatting with month in DMY format"""
        dt = datetime(2023, 1, 15)
        result = nice_day_pt(dt, date_format='DMY', include_month=True)
        self.assertIn("15", result)
        self.assertIn("Janeiro", result)
        # Should be "15 Janeiro" format
        self.assertTrue(result.startswith("15"))
    
    def test_day_with_month_mdy(self):
        """Test day formatting with month in MDY format"""
        dt = datetime(2023, 1, 15)
        result = nice_day_pt(dt, date_format='MDY', include_month=True)
        self.assertIn("15", result)
        self.assertIn("Janeiro", result)
        # Should be "Janeiro 15" format
        self.assertTrue(result.startswith("Janeiro"))
    
    def test_day_without_month(self):
        """Test day formatting without month"""
        dt = datetime(2023, 1, 15)
        result = nice_day_pt(dt, include_month=False)
        self.assertEqual(result, "15")
    
    def test_day_edge_cases(self):
        """Test edge cases for day formatting"""
        # First day of month
        dt = datetime(2023, 1, 1)
        result = nice_day_pt(dt, include_month=False)
        self.assertEqual(result, "01")
        
        # Last day of month
        dt = datetime(2023, 1, 31)
        result = nice_day_pt(dt, include_month=False)
        self.assertEqual(result, "31")


class TestNiceDateTimePt(unittest.TestCase):
    """Test cases for nice_date_time_pt function"""
    
    def test_nice_date_time_basic(self):
        """Test basic date time formatting"""
        dt = datetime(2023, 1, 15, 14, 30)
        
        result = nice_date_time_pt(dt)
        self.assertIn("ás", result)  # Should contain time separator
        self.assertIsInstance(result, str)
    
    def test_nice_date_time_24hour(self):
        """Test 24-hour format"""
        dt = datetime(2023, 1, 15, 14, 30)
        result = nice_date_time_pt(dt, use_24hour=True)
        self.assertIsInstance(result, str)
    
    def test_nice_date_time_ampm(self):
        """Test AM/PM format"""
        dt = datetime(2023, 1, 15, 14, 30)
        result = nice_date_time_pt(dt, use_ampm=True)
        self.assertIsInstance(result, str)


class TestNiceDatePt(unittest.TestCase):
    """Test cases for nice_date_pt function"""
    
    def test_nice_date_today(self):
        """Test formatting for today"""
        now = datetime(2023, 1, 15, 12, 0)
        dt = datetime(2023, 1, 15, 14, 0)
        
        result = nice_date_pt(dt, now=now)
        self.assertEqual(result, "hoje")
    
    def test_nice_date_tomorrow(self):
        """Test formatting for tomorrow"""
        now = datetime(2023, 1, 15, 12, 0)
        dt = datetime(2023, 1, 16, 14, 0)
        
        result = nice_date_pt(dt, now=now)
        self.assertEqual(result, "amanhã")
    
    def test_nice_date_yesterday(self):
        """Test formatting for yesterday"""
        now = datetime(2023, 1, 15, 12, 0)
        dt = datetime(2023, 1, 14, 14, 0)
        
        result = nice_date_pt(dt, now=now)
        self.assertEqual(result, "ontem")
    
    def test_nice_date_different_month(self):
        """Test date in different month"""
        now = datetime(2023, 1, 15, 12, 0)
        dt = datetime(2023, 2, 10, 14, 0)
        
        result = nice_date_pt(dt, now=now)
        self.assertIn("Fevereiro", result)
    
    def test_nice_date_different_year(self):
        """Test date in different year"""
        now = datetime(2023, 1, 15, 12, 0)
        dt = datetime(2024, 1, 10, 14, 0)
        
        result = nice_date_pt(dt, now=now)
        self.assertIn("Janeiro", result)
        self.assertIn("dois mil e vinte e quatro", result)
    
    def test_nice_date_without_weekday(self):
        """Test date formatting without weekday"""
        dt = datetime(2023, 1, 15, 12, 0)
        
        result = nice_date_pt(dt, include_weekday=False)
        # Should not contain weekday names
        weekdays = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
        for weekday in weekdays:
            self.assertNotIn(weekday.lower(), result.lower())
    
    def test_nice_date_with_weekday(self):
        """Test date formatting with weekday"""
        dt = datetime(2023, 1, 15, 12, 0)  # Sunday
        
        result = nice_date_pt(dt, include_weekday=True)
        self.assertIn("Domingo", result)


class TestNiceTimePt(unittest.TestCase):
    """Test cases for nice_time_pt function"""
    
    def test_nice_time_24hour_display(self):
        """Test 24-hour format for display"""
        dt = datetime(2023, 1, 1, 14, 30)
        result = nice_time_pt(dt, speech=False, use_24hour=True)
        self.assertEqual(result, "14:30")
    
    def test_nice_time_12hour_display(self):
        """Test 12-hour format for display"""
        dt = datetime(2023, 1, 1, 14, 30)
        result = nice_time_pt(dt, speech=False, use_24hour=False)
        self.assertEqual(result, "2:30")
    
    def test_nice_time_12hour_ampm_display(self):
        """Test 12-hour format with AM/PM for display"""
        dt = datetime(2023, 1, 1, 14, 30)
        result = nice_time_pt(dt, speech=False, use_24hour=False, use_ampm=True)
        self.assertEqual(result, "2:30 PM")
    
    def test_nice_time_midnight_speech(self):
        """Test midnight in speech format"""
        dt = datetime(2023, 1, 1, 0, 0)
        result = nice_time_pt(dt, speech=True, use_24hour=False)
        self.assertIn("meia noite", result)
    
    def test_nice_time_noon_speech(self):
        """Test noon in speech format"""
        dt = datetime(2023, 1, 1, 12, 0)
        result = nice_time_pt(dt, speech=True, use_24hour=False)
        self.assertIn("meio dia", result)
    
    def test_nice_time_quarter_past(self):
        """Test quarter past in speech format"""
        dt = datetime(2023, 1, 1, 10, 15)
        result = nice_time_pt(dt, speech=True, use_24hour=False)
        self.assertIn("um quarto", result)
    
    def test_nice_time_half_past(self):
        """Test half past in speech format"""
        dt = datetime(2023, 1, 1, 10, 30)
        result = nice_time_pt(dt, speech=True, use_24hour=False)
        self.assertIn("meia", result)
    
    def test_nice_time_quarter_to(self):
        """Test quarter to in speech format"""
        dt = datetime(2023, 1, 1, 10, 45)
        result = nice_time_pt(dt, speech=True, use_24hour=False)
        self.assertIn("menos um quarto", result)
    
    def test_nice_time_exact_hour(self):
        """Test exact hour in speech format"""
        dt = datetime(2023, 1, 1, 10, 0)
        result = nice_time_pt(dt, speech=True, use_24hour=False, use_ampm=False)
        self.assertIn("em ponto", result)
    
    def test_nice_time_ampm_periods(self):
        """Test AM/PM period identification"""
        # Early morning
        dt = datetime(2023, 1, 1, 3, 0)
        result = nice_time_pt(dt, speech=True, use_24hour=False, use_ampm=True)
        self.assertIn("madrugada", result)
        
        # Morning
        dt = datetime(2023, 1, 1, 8, 0)
        result = nice_time_pt(dt, speech=True, use_24hour=False, use_ampm=True)
        self.assertIn("manhã", result)
        
        # Afternoon
        dt = datetime(2023, 1, 1, 15, 0)
        result = nice_time_pt(dt, speech=True, use_24hour=False, use_ampm=True)
        self.assertIn("tarde", result)
        
        # Night
        dt = datetime(2023, 1, 1, 22, 0)
        result = nice_time_pt(dt, speech=True, use_24hour=False, use_ampm=True)
        self.assertIn("noite", result)


class TestExtractDatetimePt(unittest.TestCase):
    """Test cases for extract_datetime_pt function"""
    
    def test_extract_empty_string(self):
        """Test extraction from empty string"""
        result = extract_datetime_pt("")
        self.assertIsNone(result)
    
    def test_extract_today(self):
        """Test extracting 'hoje' (today)"""
        anchor = datetime(2023, 1, 15, 12, 0)
        result = extract_datetime_pt("hoje", anchorDate=anchor)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        extracted_date, remaining_text = result
        self.assertEqual(extracted_date.date(), anchor.date())
    
    def test_extract_tomorrow(self):
        """Test extracting 'amanhã' (tomorrow)"""
        anchor = datetime(2023, 1, 15, 12, 0)
        result = extract_datetime_pt("amanhã", anchorDate=anchor)
        
        self.assertIsNotNone(result)
        extracted_date, remaining_text = result
        expected_date = anchor + timedelta(days=1)
        self.assertEqual(extracted_date.date(), expected_date.date())
    
    def test_extract_yesterday(self):
        """Test extracting 'ontem' (yesterday)"""
        anchor = datetime(2023, 1, 15, 12, 0)
        result = extract_datetime_pt("ontem", anchorDate=anchor)
        
        self.assertIsNotNone(result)
        extracted_date, remaining_text = result
        expected_date = anchor - timedelta(days=1)
        self.assertEqual(extracted_date.date(), expected_date.date())
    
    def test_extract_weekday(self):
        """Test extracting weekday names"""
        anchor = datetime(2023, 1, 15, 12, 0)  # Sunday
        result = extract_datetime_pt("segunda", anchorDate=anchor)
        
        self.assertIsNotNone(result)
        extracted_date, remaining_text = result
        # Should extract next Monday
        self.assertEqual(extracted_date.weekday(), 0)  # Monday = 0
    
    def test_extract_time_colon_format(self):
        """Test extracting time in colon format"""
        anchor = datetime(2023, 1, 15, 12, 0)
        result = extract_datetime_pt("14:30", anchorDate=anchor)
        
        self.assertIsNotNone(result)
        extracted_date, remaining_text = result
        self.assertEqual(extracted_date.hour, 14)
        self.assertEqual(extracted_date.minute, 30)
    
    def test_extract_time_with_period(self):
        """Test extracting time with period indicators"""
        anchor = datetime(2023, 1, 15, 12, 0)
        result = extract_datetime_pt("meio dia", anchorDate=anchor)
        
        self.assertIsNotNone(result)
        extracted_date, remaining_text = result
        self.assertEqual(extracted_date.hour, 12)
    
    def test_extract_complex_datetime(self):
        """Test extracting complex datetime expressions"""
        anchor = datetime(2023, 1, 15, 12, 0)
        result = extract_datetime_pt("amanhã às 14:30", anchorDate=anchor)
        
        self.assertIsNotNone(result)
        extracted_date, remaining_text = result
        expected_date = anchor + timedelta(days=1)
        self.assertEqual(extracted_date.date(), expected_date.date())
        self.assertEqual(extracted_date.hour, 14)
        self.assertEqual(extracted_date.minute, 30)
    
    def test_extract_month_day(self):
        """Test extracting month and day"""
        anchor = datetime(2023, 1, 15, 12, 0)
        result = extract_datetime_pt("15 janeiro", anchorDate=anchor)
        
        self.assertIsNotNone(result)
        extracted_date, remaining_text = result
        self.assertEqual(extracted_date.month, 1)
        self.assertEqual(extracted_date.day, 15)
    
    def test_extract_relative_time(self):
        """Test extracting relative time expressions"""
        anchor = datetime(2023, 1, 15, 12, 0)
        result = extract_datetime_pt("em 2 horas", anchorDate=anchor)
        
        self.assertIsNotNone(result)
        extracted_date, remaining_text = result
        expected_date = anchor + timedelta(hours=2)
        self.assertEqual(extracted_date, expected_date)
    
    def test_extract_no_match(self):
        """Test extraction when no datetime is found"""
        result = extract_datetime_pt("isto não tem data")
        self.assertIsNone(result)
    
    def test_extract_ante_ontem_variations(self):
        """Test extracting 'anteontem' and variations"""
        anchor = datetime(2023, 1, 15, 12, 0)
        
        # Test "anteontem"
        result = extract_datetime_pt("anteontem", anchorDate=anchor)
        self.assertIsNotNone(result)
        extracted_date, _ = result
        expected = anchor - timedelta(days=2)
        self.assertEqual(extracted_date.date(), expected.date())
        
        # Test "ante ontem"
        result = extract_datetime_pt("ante ontem", anchorDate=anchor)
        self.assertIsNotNone(result)
        extracted_date, _ = result
        expected = anchor - timedelta(days=2)
        self.assertEqual(extracted_date.date(), expected.date())
    
    def test_extract_week_references(self):
        """Test extracting week-based references"""
        anchor = datetime(2023, 1, 15, 12, 0)
        
        # Test "próxima semana"
        result = extract_datetime_pt("proxima semana", anchorDate=anchor)
        self.assertIsNotNone(result)
        extracted_date, _ = result
        expected = anchor + timedelta(days=7)
        self.assertEqual(extracted_date.date(), expected.date())
    
    def test_extract_month_references(self):
        """Test extracting month-based references"""
        anchor = datetime(2023, 1, 15, 12, 0)
        
        # Test "próximo mês"
        result = extract_datetime_pt("proximo mes", anchorDate=anchor)
        self.assertIsNotNone(result)
        extracted_date, _ = result
        # Should be approximately one month later
        self.assertGreater(extracted_date, anchor)


class TestExtractDurationPt(unittest.TestCase):
    """Test cases for extract_duration_pt function"""
    
    def test_extract_empty_string(self):
        """Test extraction from empty string"""
        result = extract_duration_pt("")
        self.assertIsNone(result)
    
    def test_extract_empty_none(self):
        """Test extraction from None"""
        result = extract_duration_pt(None)
        self.assertIsNone(result)
    
    def test_extract_seconds(self):
        """Test extracting seconds"""
        result = extract_duration_pt("30 segundos")
        
        self.assertIsNotNone(result)
        duration, remaining_text = result
        self.assertEqual(duration.total_seconds(), 30)
        self.assertEqual(remaining_text.strip(), "")
    
    def test_extract_minutes(self):
        """Test extracting minutes"""
        result = extract_duration_pt("5 minutos")
        
        self.assertIsNotNone(result)
        duration, remaining_text = result
        self.assertEqual(duration.total_seconds(), 300)  # 5 * 60
    
    def test_extract_hours(self):
        """Test extracting hours"""
        result = extract_duration_pt("2 horas")
        
        self.assertIsNotNone(result)
        duration, remaining_text = result
        self.assertEqual(duration.total_seconds(), 7200)  # 2 * 60 * 60
    
    def test_extract_days(self):
        """Test extracting days"""
        result = extract_duration_pt("3 dias")
        
        self.assertIsNotNone(result)
        duration, remaining_text = result
        self.assertEqual(duration.days, 3)
    
    def test_extract_weeks(self):
        """Test extracting weeks"""
        result = extract_duration_pt("2 semanas")
        
        self.assertIsNotNone(result)
        duration, remaining_text = result
        self.assertEqual(duration.days, 14)  # 2 * 7
    
    def test_extract_months(self):
        """Test extracting months"""
        result = extract_duration_pt("6 meses")
        
        self.assertIsNotNone(result)
        duration, remaining_text = result
        # Should convert months to days
        self.assertGreater(duration.days, 150)  # Approximately 6 months
    
    def test_extract_years(self):
        """Test extracting years"""
        result = extract_duration_pt("2 anos")
        
        self.assertIsNotNone(result)
        duration, remaining_text = result
        # Should convert years to days
        self.assertGreater(duration.days, 700)  # Approximately 2 years
    
    def test_extract_complex_duration(self):
        """Test extracting complex duration expressions"""
        result = extract_duration_pt("3 dias 8 horas 10 minutos e 49 segundos")
        
        self.assertIsNotNone(result)
        duration, remaining_text = result
        
        # Calculate expected total seconds
        expected_seconds = (3 * 24 * 60 * 60) + (8 * 60 * 60) + (10 * 60) + 49
        self.assertEqual(duration.total_seconds(), expected_seconds)
    
    def test_extract_decimal_values(self):
        """Test extracting decimal duration values"""
        result = extract_duration_pt("2.5 horas")
        
        self.assertIsNotNone(result)
        duration, remaining_text = result
        self.assertEqual(duration.total_seconds(), 9000)  # 2.5 * 60 * 60
    
    def test_extract_with_remaining_text(self):
        """Test extraction with remaining text"""
        result = extract_duration_pt("definir um timer por 5 minutos")
        
        self.assertIsNotNone(result)
        duration, remaining_text = result
        self.assertEqual(duration.total_seconds(), 300)
        self.assertIn("timer por", remaining_text)
    
    def test_extract_no_duration(self):
        """Test extraction when no duration is found"""
        duration, remaining = extract_duration_pt("isto não tem duração")
        self.assertIsNone(duration)
        self.assertEqual(remaining, "isto não tem duração")
    
    def test_extract_singular_forms(self):
        """Test extraction of singular forms"""
        # Test singular forms
        test_cases = [
            ("1 segundo", 1),
            ("1 minuto", 60),
            ("1 hora", 3600),
            ("1 dia", 86400),
        ]
        
        for text, expected_seconds in test_cases:
            with self.subTest(text=text):
                result = extract_duration_pt(text)
                self.assertIsNotNone(result)
                duration, remaining_text = result
                self.assertEqual(duration.total_seconds(), expected_seconds)
    
    def test_extract_special_replacements(self):
        """Test the special word replacements in duration extraction"""
        # Test the special handling of "segundo" (second) vs número "segundo" (2nd)
        result = extract_duration_pt("5 segundo")
        self.assertIsNotNone(result)
        duration, _ = result
        self.assertEqual(duration.total_seconds(), 5)


class TestConstantsAndDataStructures(unittest.TestCase):
    """Test cases for constants and data structures"""
    
    def test_weekdays_pt_structure(self):
        """Test WEEKDAYS_PT dictionary structure"""
        self.assertEqual(len(WEEKDAYS_PT), 7)
        self.assertIn(0, WEEKDAYS_PT)
        self.assertIn(6, WEEKDAYS_PT)
        self.assertEqual(WEEKDAYS_PT[0], "segunda-feira")
        self.assertEqual(WEEKDAYS_PT[6], "domingo")
    
    def test_months_pt_structure(self):
        """Test MONTHS_PT dictionary structure"""
        self.assertEqual(len(MONTHS_PT), 12)
        self.assertIn(1, MONTHS_PT)
        self.assertIn(12, MONTHS_PT)
        self.assertEqual(MONTHS_PT[1], "janeiro")
        self.assertEqual(MONTHS_PT[12], "dezembro")
    
    def test_weekdays_all_strings(self):
        """Test all weekdays are strings"""
        for _key, value in WEEKDAYS_PT.items():
            self.assertIsInstance(value, str)
            self.assertTrue(len(value) > 0)
    
    def test_months_all_strings(self):
        """Test all months are strings"""
        for _key, value in MONTHS_PT.items():
            self.assertIsInstance(value, str)
            self.assertTrue(len(value) > 0)


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test cases for edge cases and error handling"""
    
    def test_nice_year_extreme_years(self):
        """Test extreme year values"""
        # Very old date
        dt = datetime(1, 1, 1)
        result = nice_year_pt(dt)
        self.assertIsInstance(result, str)
        
        # Far future date
        dt = datetime(9999, 12, 31)
        result = nice_year_pt(dt)
        self.assertIsInstance(result, str)
    
    def test_nice_time_edge_minutes(self):
        """Test edge cases for minute handling"""
        # Test special minute values (35, 40, 45, 50, 55)
        special_minutes = [35, 40, 45, 50, 55]
        for minute in special_minutes:
            with self.subTest(minute=minute):
                dt = datetime(2023, 1, 1, 10, minute)
                result = nice_time_pt(dt, speech=True, use_24hour=False)
                self.assertIsInstance(result, str)
    
    def test_extract_datetime_clean_string_edge_cases(self):
        """Test string cleaning with various edge cases"""
        # Test with special characters and accents
        test_cases = [
            "hoje às 15:30",
            "amanhã de manhã",
            "próxima terça-feira",
            "15 de janeiro às 14h30min",
        ]
        
        anchor = datetime(2023, 1, 15, 12, 0)
        for text in test_cases:
            with self.subTest(text=text):
                result = extract_datetime_pt(text, anchorDate=anchor)
                # Should not raise exceptions
                self.assertTrue(result is None or len(result) == 2)
    
    def test_extract_duration_malformed_input(self):
        """Test duration extraction with malformed input"""
        test_cases = [
            "abc def ghi",
            "123 xyz",
            "minutos 5",  # Reversed order
            "5 minutoss",  # Typo
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                result = extract_duration_pt(text)
                # Should either return None or handle gracefully
                self.assertTrue(result is None or len(result) == 2)
    
    def test_nice_time_24hour_speech_format(self):
        """Test 24-hour speech format edge cases"""
        # Test midnight in 24-hour format
        dt = datetime(2023, 1, 1, 0, 30)
        result = nice_time_pt(dt, speech=True, use_24hour=True)
        self.assertIsInstance(result, str)
        
        # Test late evening in 24-hour format
        dt = datetime(2023, 1, 1, 23, 45)
        result = nice_time_pt(dt, speech=True, use_24hour=True)
        self.assertIsInstance(result, str)
    
    def test_extract_datetime_boundary_conditions(self):
        """Test boundary conditions in datetime extraction"""
        anchor = datetime(2023, 12, 31, 23, 59)  # End of year
        
        # Test tomorrow at year boundary
        result = extract_datetime_pt("amanhã", anchorDate=anchor)
        self.assertIsNotNone(result)
        extracted_date, _ = result
        self.assertEqual(extracted_date.year, 2024)
        self.assertEqual(extracted_date.month, 1)
        self.assertEqual(extracted_date.day, 1)


class TestComplexDateTimeExtractionScenarios(unittest.TestCase):
    """Additional test cases for complex datetime extraction scenarios"""
    
    def test_extract_time_periods_speech(self):
        """Test extracting various time periods in speech format"""
        anchor = datetime(2023, 1, 15, 12, 0)
        
        time_periods = [
            ("manha", 8),
            ("tarde", 15),
            ("noite", 22),
            ("meio tarde", 17),
            ("fim tarde", 19),
        ]
        
        for period, expected_hour in time_periods:
            with self.subTest(period=period):
                result = extract_datetime_pt(period, anchorDate=anchor)
                if result is not None:
                    extracted_date, _ = result
                    self.assertEqual(extracted_date.hour, expected_hour)
    
    def test_extract_multiple_time_formats(self):
        """Test extracting various time formats"""
        anchor = datetime(2023, 1, 15, 12, 0)
        
        time_formats = [
            "15:30",
            "3:30 pm",
            "15h30",
            "15 30",
        ]
        
        for time_format in time_formats:
            with self.subTest(time_format=time_format):
                result = extract_datetime_pt(time_format, anchorDate=anchor)
                # Should extract some valid time or return None gracefully
                self.assertTrue(result is None or len(result) == 2)
    
    def test_nice_date_complex_scenarios(self):
        """Test nice_date_pt with complex scenarios"""
        now = datetime(2023, 1, 15, 12, 0)
        
        # Test same day, different times
        same_day = datetime(2023, 1, 15, 18, 0)
        result = nice_date_pt(same_day, now=now)
        self.assertEqual(result, "hoje")
        
        # Test leap year scenarios
        leap_year_date = datetime(2024, 2, 29, 12, 0)
        result = nice_date_pt(leap_year_date)
        self.assertIn("Fevereiro", result)
        self.assertIn("vinte e nove", result)
    
    def test_duration_extraction_edge_cases(self):
        """Test duration extraction with edge cases"""
        edge_cases = [
            ("0 segundos", 0),
            ("1 milénio", 365000 * 1000),  # Very large duration
            ("0.1 segundo", 0.1),
            ("meio minuto", None),  # Should handle gracefully
        ]
        
        for text, expected in edge_cases:
            with self.subTest(text=text):
                result = extract_duration_pt(text)
                if expected is None:
                    # Should handle gracefully, either None or valid result
                    self.assertTrue(result is None or len(result) == 2)
                elif expected == 0:
                    if result is not None:
                        duration, _ = result
                        if duration is not None:
                            self.assertEqual(duration.total_seconds(), 0)
                elif result is not None:
                    duration, _ = result
                    if expected > 1000000:  # Very large durations
                        self.assertGreater(duration.total_seconds(), 100000)
                    else:
                        self.assertAlmostEqual(duration.total_seconds(), expected, places=1)


class TestExtractDatetimeAbsoluteHours(unittest.TestCase):
    """'às N horas' should be an absolute clock time, not an offset."""

    def setUp(self):
        # a Friday at noon
        self.anchor = datetime(2026, 7, 17, 12, 0, 0)

    def _time(self, text):
        result = extract_datetime_pt(text, anchorDate=self.anchor)
        self.assertIsNotNone(result, f"no datetime found in {text!r}")
        return result[0]

    def test_as_14_horas_is_two_pm(self):
        # "às 14 horas" is 14:00, never "in 14 hours"
        self.assertEqual(self._time("às 14 horas").hour, 14)

    def test_pelas_14_horas_is_two_pm(self):
        self.assertEqual(self._time("pelas 14 horas").hour, 14)

    def test_as_nine_horas_is_nine(self):
        self.assertEqual(self._time("às 9 horas").hour, 9)

    def test_as_nine_horas_manha_applies_am(self):
        # part of day must not be dropped
        self.assertEqual(self._time("às 9 horas da manhã").hour, 9)

    def test_as_three_horas_tarde_applies_pm(self):
        self.assertEqual(self._time("às 3 horas da tarde").hour, 15)

    def test_as_midnight_hour(self):
        self.assertEqual(self._time("às 0 horas").hour, 0)

    def test_em_n_horas_still_offset(self):
        # "em 3 horas" stays a relative offset from the anchor
        self.assertEqual(self._time("em 3 horas").hour, 15)

    def test_em_14_horas_still_offset(self):
        dt = self._time("em 14 horas")
        # 12:00 + 14h wraps to the next day at 02:00
        self.assertEqual((dt.day, dt.hour), (18, 2))

    def test_date_with_absolute_hour(self):
        dt = self._time("2 de maio às 20 horas")
        self.assertEqual((dt.month, dt.day, dt.hour), (5, 2, 20))


class TestExtractDatetimeMonthSpelling(unittest.TestCase):
    """Correctly spelled Portuguese months and their abbreviations."""

    def setUp(self):
        self.anchor = datetime(2026, 7, 17, 12, 0, 0)

    def _date(self, text):
        result = extract_datetime_pt(text, anchorDate=self.anchor)
        self.assertIsNotNone(result, f"no datetime found in {text!r}")
        return result[0]

    def test_fevereiro_full(self):
        dt = self._date("3 de fevereiro")
        self.assertEqual((dt.month, dt.day), (2, 3))

    def test_fevereiro_short(self):
        dt = self._date("15 de fev")
        self.assertEqual((dt.month, dt.day), (2, 15))

    def test_agosto_short(self):
        dt = self._date("1 de ago às 14 horas")
        self.assertEqual((dt.month, dt.day, dt.hour), (8, 1, 14))

    def test_dezembro_short(self):
        dt = self._date("3 de dez às 9 horas")
        self.assertEqual((dt.month, dt.day, dt.hour), (12, 3, 9))

    def test_all_full_months_recognized(self):
        months = {
            "janeiro": 1, "fevereiro": 2, "abril": 4, "maio": 5,
            "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
            "outubro": 10, "novembro": 11, "dezembro": 12,
        }
        for name, num in months.items():
            dt = self._date(f"10 de {name}")
            self.assertEqual(dt.month, num, f"{name} -> month {dt.month}")


class TestExtractDatetimeRobustness(unittest.TestCase):
    """Adversarial / malformed inputs must never raise."""

    def setUp(self):
        self.anchor = datetime(2026, 7, 17, 12, 0, 0)

    def _no_crash(self, text):
        try:
            return extract_datetime_pt(text, anchorDate=self.anchor)
        except Exception as e:  # noqa
            self.fail(f"{text!r} raised {type(e).__name__}: {e}")

    def test_trailing_number_not_year(self):
        # a bare non-four-digit trailing number must not be fed to strptime
        for text in ["15 de junho 10", "20 de dezembro 45", "3 de março 99",
                     "dia 15 de junho 30", "15 janeiro 14:30",
                     "consulta 15 de junho 3"]:
            self._no_crash(text)

    def test_impossible_dates_do_not_crash(self):
        for text in ["31 de abril", "30 de fevereiro", "29 de fevereiro"]:
            self._no_crash(text)

    def test_four_digit_year_still_parsed(self):
        result = extract_datetime_pt("15 de junho de 2030", anchorDate=self.anchor)
        self.assertIsNotNone(result)
        self.assertEqual(result[0].year, 2030)

    def test_trailing_number_used_as_time(self):
        # without an explicit year, a following number is the clock time
        result = extract_datetime_pt("15 de junho às 10", anchorDate=self.anchor)
        self.assertIsNotNone(result)
        self.assertEqual((result[0].month, result[0].day, result[0].hour),
                         (6, 15, 10))

    def test_junk_and_none_like_inputs(self):
        for text in ["", "isto não tem data nenhuma", "   ",
                     "xyz 999999", "de de de", "à à à"]:
            # must not raise; empty/junk should yield None
            self._no_crash(text)

    def test_mixed_case_preserved(self):
        result = extract_datetime_pt("AMANHÃ", anchorDate=self.anchor)
        self.assertIsNotNone(result)
        self.assertEqual(result[0].date(),
                         (self.anchor + timedelta(days=1)).date())


class TestExtractDatetimeRealSentences(unittest.TestCase):
    """End to end sentences a user would actually say."""

    def setUp(self):
        self.anchor = datetime(2026, 7, 17, 12, 0, 0)

    def _dt(self, text):
        result = extract_datetime_pt(text, anchorDate=self.anchor)
        self.assertIsNotNone(result, f"no datetime found in {text!r}")
        return result[0]

    def test_appointment_date(self):
        dt = self._dt("consulta a 15 de junho às 15:30")
        self.assertEqual((dt.month, dt.day, dt.hour, dt.minute), (6, 15, 15, 30))

    def test_reminder_full_date(self):
        dt = self._dt("reunião a 20 de dezembro de 2027")
        self.assertEqual((dt.year, dt.month, dt.day), (2027, 12, 20))

    def test_christmas(self):
        dt = self._dt("no dia 25 de dezembro")
        self.assertEqual((dt.month, dt.day), (12, 25))

    def test_relative_offset_minutes(self):
        dt = self._dt("em 10 minutos")
        self.assertEqual((dt - self.anchor), timedelta(minutes=10))

    def test_day_after_tomorrow(self):
        dt = self._dt("depois de amanhã")
        self.assertEqual(dt.date(), (self.anchor + timedelta(days=2)).date())


if __name__ == '__main__':
    unittest.main()