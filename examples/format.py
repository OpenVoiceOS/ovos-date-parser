"""Format dates, times and durations for speech or display."""
from datetime import datetime, timedelta

from ovos_date_parser import (nice_time, nice_date, nice_date_time,
                              nice_duration, nice_relative_time)

dt = datetime(2023, 6, 5, 13, 30)
now = datetime(2023, 6, 5, 9, 0)

for lang in ["en", "es", "pt", "de", "fr"]:
    print(f"--- {lang}")
    print(" ", nice_time(dt, lang))
    print(" ", nice_time(dt, lang, speech=False))
    print(" ", nice_time(dt, lang, use_24hour=True))
    print(" ", nice_date(dt, lang, now=now))

# durations
print(nice_duration(61, "en"))                    # one minute one second
print(nice_duration(5000, "en", speech=False))    # 1:23:20
print(nice_duration(timedelta(days=2, hours=3), "en"))

# relative time
print(nice_relative_time(dt + timedelta(hours=2), relative_to=dt, lang="en"))

# span-native formatting: a DateSpan's width is its precision, so nice_span
# labels it at the right granularity -- and for English it round-trips back
# through extract_timespan.
from ovos_date_parser import nice_span, extract_timespan

for text in ["July 21st, 2026", "July 2026", "2026", "the 1980s",
             "the 19th century", "300 BC"]:
    span, _ = extract_timespan(text, "en")
    label = nice_span(span, "en")
    print(f"{text!r:22} -> {span.start} .. {span.end} -> {label!r}")
    assert label == text  # round-trips

# the datetime formatters accept an AstroDate point directly
from ovos_date_parser.astrodate import AstroDate

when = AstroDate(2026, 7, 21, 15, 30)
print(nice_date(when, "en"), "at", nice_time(when, "en"))
