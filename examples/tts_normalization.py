"""TTS normalization — turn machine dates/times into speakable words.

Speech synthesizers read digits poorly ("2024-01-05" -> "two thousand
twenty four dash zero one..."). Normalize timestamps and durations into
natural spoken words *before* handing text to any TTS engine. Standalone —
no OVOS, no speech engine needed to run this.
"""
from datetime import datetime, timedelta

from ovos_date_parser import (nice_date, nice_time, nice_date_time,
                              nice_duration, nice_year)

dt = datetime(2024, 1, 5, 15, 30)

print("Raw timestamp:", dt.isoformat())
print()

for lang in ["en", "es", "pt", "de", "fr", "it"]:
    print(f"--- {lang} ---")
    print("  date :", nice_date(dt, lang))
    print("  time :", nice_time(dt, lang))            # speakable, 12h
    print("  24h  :", nice_time(dt, lang, use_24hour=True))
    print("  year :", nice_year(dt, lang))
    print("  full :", nice_date_time(dt, lang))

print()
print("Durations rendered for speech:")
for secs in (90, 3690, 86400 * 2 + 3600 * 3):
    print(f"  {secs:>7}s ->", nice_duration(secs, "en"))
print("  timedelta ->", nice_duration(timedelta(hours=1, minutes=45), "en"))

# A minimal 'normalize before synthesis' helper.
def speak_timestamp(dt, lang="en"):
    return f"{nice_date(dt, lang)} at {nice_time(dt, lang)}"

print()
print("speak_timestamp:", speak_timestamp(dt))
