"""nice_date, nice_date_time and nice_year pass the full language tag to the
resource formatter, so a regional folder (``res/<lang>-<region>/``) can
change the output for that region and every other region falls back to
``res/<lang>/``."""
import json
import os
import tempfile
import unittest
from datetime import datetime
from unittest import mock

import ovos_date_parser
from ovos_date_parser import (DateTimeFormat, nice_date, nice_date_time,
                              nice_year)

RES = os.path.join(os.path.dirname(ovos_date_parser.__file__), "res")
DT = datetime(2024, 3, 12, 14, 30)


class TestRegionTagReachesResources(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        with open(os.path.join(RES, "en", "date_time.json"),
                  encoding="utf8") as f:
            base = json.load(f)
        regional = json.loads(json.dumps(base))
        regional["date_format"]["date_full"] = \
            "{weekday}, the {day} of {month}, {formatted_year}"
        regional["year_format"]["default"] = "regional year {year}"
        for i in range(1, 100):
            regional["year_format"].pop(str(i), None)
        for folder, data in (("en", base), ("en-gb", regional)):
            os.makedirs(os.path.join(cls.tmp.name, folder))
            with open(os.path.join(cls.tmp.name, folder, "date_time.json"),
                      "w", encoding="utf8") as f:
                json.dump(data, f)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        patcher = mock.patch.object(ovos_date_parser, "date_time_format",
                                    DateTimeFormat(self.tmp.name))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_regional_folder_is_used(self):
        self.assertEqual(nice_date(DT, "en-GB", include_weekday=False),
                         "the twelfth of march, regional year 2024")

    def test_other_regions_fall_back(self):
        for lang in ("en", "en-US", "en-us"):
            with self.subTest(lang=lang):
                self.assertEqual(nice_date(DT, lang, include_weekday=False),
                                 "march twelfth, twenty twenty four")

    def test_nice_year(self):
        self.assertEqual(nice_year(DT, "en-GB"), "regional year 2024")
        self.assertEqual(nice_year(DT, "en-US"), "twenty twenty four")

    def test_nice_date_time(self):
        self.assertEqual(nice_date_time(DT, "en-GB", now=datetime(2020, 1, 1)),
                         "tuesday, the twelfth of march, regional year 2024 "
                         "at half past two")


if __name__ == "__main__":
    unittest.main()
