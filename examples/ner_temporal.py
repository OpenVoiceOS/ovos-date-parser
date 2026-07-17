"""Temporal entity extraction (NER) from free text — no OVOS required.

Pull dates, times and durations out of unstructured strings the way a
named-entity recognizer would, then keep the leftover text. Everything here
runs with just `pip install ovos-date-parser`.

Typical standalone uses: tagging log lines, mining meeting notes, enriching
support tickets, or feeding a calendar/scheduling tool.
"""
from datetime import datetime

from ovos_date_parser import extract_datetime, extract_duration

# A fixed anchor makes relative phrases ("tomorrow", "in 2 weeks")
# deterministic. In a live tool you would pass datetime.now() instead.
ANCHOR = datetime(2024, 1, 5, 9, 0)  # a friday, 09:00

notes = [
    ("en", "call the supplier next monday at 2pm about the delayed order"),
    ("en", "the maintenance window lasts 3 hours and 30 minutes"),
    ("pt", "reunião amanhã às 15h30 na sala azul"),
    ("es", "entregar el informe el 11 de agosto de 1998"),
    ("de", "der Termin ist übermorgen um 10 Uhr"),
]

print("== date / time entities ==")
for lang, text in notes:
    found = extract_datetime(text, lang, anchorDate=ANCHOR)
    if found is None:
        print(f"[{lang}] no temporal entity in: {text!r}")
        continue
    when, leftover = found
    print(f"[{lang}] {when.isoformat()}  <-  {text!r}")
    print(f"       leftover (non-temporal) text: {leftover!r}")

print("\n== duration entities ==")
durations = [
    ("en", "set a timer for 5 minutes"),
    ("en", "3 days 8 hours and 10 minutes of processing time"),
    ("fr", "la recette prend deux heures et trente minutes"),
    ("it", "il corso dura due ore e trenta minuti"),
]
for lang, text in durations:
    delta, leftover = extract_duration(text, lang)
    print(f"[{lang}] {delta}  <-  {text!r}")
    print(f"       leftover text: {leftover!r}")
