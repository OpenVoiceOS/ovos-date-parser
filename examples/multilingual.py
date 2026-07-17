"""Multilingual round-trip across several supported languages.

Parse a spoken phrase into a datetime, then render it back to natural words
in the same language. Shows the breadth of language coverage in one pass.
Standalone — no OVOS.
"""
from datetime import datetime

from ovos_date_parser import extract_datetime, nice_date_time, nice_duration

ANCHOR = datetime(2024, 1, 5, 9, 0)

phrases = [
    ("en", "next friday at 3pm"),
    ("es", "el 11 de agosto de 1998"),
    ("pt", "amanhã às 15h30"),
    ("de", "übermorgen um 10 Uhr"),
    ("fr", "demain à 15h30"),
    ("it", "dopodomani alle 10"),
    ("nl", "morgen om negen uur"),
    ("ru", "завтра в десять утра"),
]

print("== parse -> re-render ==")
for lang, phrase in phrases:
    parsed = extract_datetime(phrase, lang, anchorDate=ANCHOR)
    if not parsed:
        print(f"[{lang}] could not parse {phrase!r}")
        continue
    when, _ = parsed
    print(f"[{lang}] {phrase!r}")
    print(f"       -> {when.isoformat()}")
    print(f"       -> {nice_date_time(when, lang)}")

print("\n== the same duration in several languages ==")
for lang in ["en", "es", "pt", "de", "fr", "it", "ru", "uk"]:
    print(f"  [{lang}] {nice_duration(3690, lang)}")
