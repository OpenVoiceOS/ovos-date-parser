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
