import unittest
from datetime import datetime, timedelta

from ovos_date_parser import extract_datetime, extract_duration


class TestExtractDatetimeEN(unittest.TestCase):
    anchor = datetime(2017, 6, 27, 13, 4, 0)

    def _extract(self, text, lang="en-us"):
        return extract_datetime(text, lang=lang, anchorDate=self.anchor)

    def _assert_dt(self, text, expected, leftover=None, lang="en-us"):
        res = self._extract(text, lang=lang)
        self.assertIsNotNone(res, f"no datetime extracted from {text!r}")
        got = res[0].strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(got, expected, f"{text!r} -> {got}")
        if leftover is not None:
            self.assertEqual(res[1], leftover)

    def test_natural_time_of_day(self):
        # an explicit hour plus a part-of-day must resolve to PM
        self._assert_dt("seven in the evening", "2017-06-27 19:00:00")
        self._assert_dt("eight tonight", "2017-06-27 20:00:00")
        self._assert_dt("nine in the morning", "2017-06-28 09:00:00")
        self._assert_dt("meeting on June 15 at three in the afternoon",
                        "2018-06-15 15:00:00")

    def test_meeting_with_month_day_and_clock(self):
        # a trailing clock number must not be swallowed as the year
        self._assert_dt("meeting on June 15 at three", "2018-06-15 15:00:00")
        self._assert_dt("dinner on December 24 at eight", "2017-12-24 20:00:00")

    def test_relative_offsets(self):
        self._assert_dt("remind me in two hours", "2017-06-27 15:04:00")
        self._assert_dt("wake me in half an hour", "2017-06-27 13:34:00")
        self._assert_dt("in ten minutes", "2017-06-27 13:14:00")

    def test_explicit_leap_day(self):
        self._assert_dt("february 29 2020 at noon", "2020-02-29 12:00:00")

    def test_lang_code_variants(self):
        for lang in ("en", "en-us", "en-gb"):
            res = extract_datetime("in ten minutes", lang=lang,
                                   anchorDate=self.anchor)
            self.assertIsNotNone(res)
            self.assertEqual(res[0].strftime("%H:%M"), "13:14")

    def test_impossible_dates_return_none(self):
        # dates that do not exist on the calendar must not crash and must
        # report nothing rather than a plausible-looking wrong date
        for text in ("february 29 2019", "february 30", "april 31 2020",
                     "june 31", "november 31 2021"):
            self.assertIsNone(self._extract(text),
                              f"expected None for {text!r}")

    def test_empty_and_junk_input(self):
        self.assertIsNone(self._extract(""))
        self.assertIsNone(self._extract("the quick brown fox"))

    def test_now(self):
        res = self._extract("what time is it now")
        self.assertIsNotNone(res)
        self.assertEqual(res[0].strftime("%Y-%m-%d %H:%M:%S"),
                         "2017-06-27 13:04:00")


class TestExtractDurationEN(unittest.TestCase):
    def _assert_dur(self, text, seconds, lang="en-us"):
        res = extract_duration(text, lang=lang)
        self.assertIsNotNone(res)
        self.assertEqual(res[0], timedelta(seconds=seconds), f"{text!r} -> {res}")

    def test_spoken_durations(self):
        self._assert_dur("two hours", 7200)
        self._assert_dur("half an hour", 1800)
        self._assert_dur("two and a half hours", 9000)
        self._assert_dur("in two hours and thirty minutes", 9000)
        self._assert_dur("ninety minutes", 5400)

    def test_empty_duration(self):
        # empty input yields nothing at all
        self.assertIsNone(extract_duration("", lang="en-us"))
        # no duration present -> None delta, text returned untouched
        self.assertEqual(extract_duration("hello there", lang="en-us"),
                         (None, "hello there"))


if __name__ == "__main__":
    unittest.main()
