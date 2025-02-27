import unittest
from datetime import timedelta
from ovos_date_parser.dates_gl import extract_duration_gl


class TestExtractDurationGL(unittest.TestCase):
    def test_single_unit(self):
        self.assertEqual(extract_duration_gl("10 minutos"), (timedelta(minutes=10), ""))
        self.assertEqual(extract_duration_gl("3 días"), (timedelta(days=3), ""))
        self.assertEqual(extract_duration_gl("8 horas"), (timedelta(hours=8), ""))
        self.assertEqual(extract_duration_gl("49 segundos"), (timedelta(seconds=49), ""))

    def test_multiple_units(self):
        self.assertEqual(extract_duration_gl("3 días 8 horas 10 minutos e 49 segundos"),
                         (timedelta(days=3, hours=8, minutes=10, seconds=49), "e"))
        self.assertEqual(extract_duration_gl("2 semanas 5 días"),
                         (timedelta(weeks=2, days=5), ""))

    def test_with_extra_text(self):
        self.assertEqual(extract_duration_gl("pon un temporizador de 5 minutos"),
                         (timedelta(minutes=5), "pon un temporizador de"))
        self.assertEqual(extract_duration_gl("avisame en 1 hora"),
                         (timedelta(hours=1), "avisame en"))

    def test_non_standard_units(self):
        self.assertEqual(extract_duration_gl("2 meses"), (timedelta(days=60), ""))
        self.assertEqual(extract_duration_gl("1 ano"), (timedelta(days=365), ""))
        self.assertEqual(extract_duration_gl("1 década"), (timedelta(days=10 * 365), ""))
        self.assertEqual(extract_duration_gl("1 século"), (timedelta(days=100 * 365), ""))
        self.assertEqual(extract_duration_gl("1 milenio"), (timedelta(days=1000 * 365), ""))

    def test_no_duration_found(self):
        self.assertEqual(extract_duration_gl("isto non ten tempo"), (None, "isto non ten tempo"))
        self.assertEqual(extract_duration_gl(""), (None, ""))


if __name__ == "__main__":
    unittest.main()
