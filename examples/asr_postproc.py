"""ASR post-processing — spoken time phrases into structured datetimes.

Speech-to-text engines emit words, not structured values. A transcript says
"remind me next tuesday at nine thirty", and a downstream scheduler needs a
real datetime. `extract_datetime` / `extract_duration` bridge that gap.

Fully standalone: pretend the strings below came off any ASR engine.
"""
from datetime import datetime

from ovos_date_parser import extract_datetime, extract_duration

# The moment the utterance was transcribed — relative phrases resolve to it.
NOW = datetime(2024, 1, 5, 9, 0)

transcripts = [
    ("en", "remind me next tuesday at nine thirty to water the plants"),
    ("en", "wake me up in eight hours"),
    ("pt", "marca uma reunião amanhã às 15h30"),
    ("de", "weck mich morgen um sieben uhr"),
]

for lang, utterance in transcripts:
    parsed = extract_datetime(utterance, lang, anchorDate=NOW)
    if parsed is None:
        print(f"[{lang}] no time understood: {utterance!r}")
        continue
    when, remainder = parsed
    # `remainder` is the intent payload with the time expression stripped out.
    print(f"[{lang}] {utterance!r}")
    print(f"       when   = {when.isoformat()}")
    print(f"       action = {remainder!r}")

print()
print("Spoken durations -> timedelta:")
for lang, utterance in [("en", "cook it for twenty five minutes"),
                        ("fr", "minuteur de deux heures et trente minutes")]:
    delta, remainder = extract_duration(utterance, lang)
    print(f"[{lang}] {delta}  (action: {remainder!r})")
