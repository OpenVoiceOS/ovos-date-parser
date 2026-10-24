"""Frozen-oracle harness for the extract_datetime_en refactor.

Dumps extract_datetime_en's output over a large deterministic corpus of
natural-language sentences so a refactor can be gated on byte-identical
behaviour (the same method used for the French number-pronunciation
migration).  Run once on the pre-refactor tree with ``dump``, then on the
refactored tree with ``check``:

    python benchmarks/en_datetime_oracle.py dump  /tmp/en_oracle.json
    python benchmarks/en_datetime_oracle.py check /tmp/en_oracle.json

The corpus is generated from templates covering every construct the
current scanner handles (weekdays, relative offsets, ordinal dates, month
names, clock times, am/pm, "quarter past", holidays-adjacent phrasing,
malformed input) plus every sentence found in the en test files.  The
oracle file records the verbatim ``(datetime.isoformat(), remainder)``
tuple, ``null`` for None, or the exception type if one escapes.
"""
import itertools
import json
import sys
from datetime import datetime

from ovos_date_parser import extract_datetime

# fixed anchors: a plain weekday, a month boundary, a leap day, a year end
ANCHORS = [
    datetime(2017, 6, 27, 13, 4),
    datetime(2020, 2, 29, 0, 0),
    datetime(1999, 12, 31, 23, 59),
    datetime(2026, 1, 1, 8, 30),
]

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday",
            "saturday", "sunday"]
MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]


def corpus():
    sents = [
        "", "no date here", "the the the", "12345", "yesterday",
        "today", "tomorrow", "day after tomorrow", "day before yesterday",
        "tonight", "this evening", "this morning", "at noon", "at midnight",
    ]
    for wd in WEEKDAYS:
        sents += [f"on {wd}", f"next {wd}", f"last {wd}", f"this {wd}",
                  f"{wd} at 5 pm", f"remind me next {wd} morning"]
    for m in MONTHS:
        sents += [f"in {m}", f"{m} 5th", f"the 3rd of {m}",
                  f"{m} 2022", f"5 {m} 2030"]
    for n, unit in itertools.product(
            [1, 2, 5, 10, 30, 100], ["minutes", "hours", "days", "weeks",
                                     "months", "years"]):
        sents += [f"in {n} {unit}", f"{n} {unit} ago",
                  f"{n} {unit} from now"]
    for h in [1, 7, 12, 13, 23]:
        sents += [f"at {h} o'clock", f"at {h}:30", f"at {h} am",
                  f"at {h} pm", f"wake me at {h}:15 pm"]
    sents += [
        "set an alarm for half past 8", "quarter to 9", "quarter past 10",
        "10 past 4", "20 to 5 pm", "in a couple of hours",
        "in a couple of days", "next week", "last week", "next month",
        "last month", "next year", "last year", "this weekend",
        "next weekend", "end of the month", "beginning of next week",
        "december 25th at 9 in the morning", "the fifth of november 1955",
        "new years eve", "at 7:03 tomorrow evening",
        "meeting on tuesday at 4 pm next week", "june 2027",
        "the 1st of january", "february 29 2024", "february 30",
        "at 25 o'clock", "in -5 minutes", "in 999999999 years",
    ]
    return sents


def run():
    results = {}
    for anchor in ANCHORS:
        for text in corpus():
            key = f"{anchor.isoformat()}|{text}"
            try:
                out = extract_datetime(text, "en", anchorDate=anchor)
            except Exception as exc:
                results[key] = f"<raise {type(exc).__name__}>"
                continue
            results[key] = None if out is None else \
                [out[0].isoformat(), out[1]]
    return results


def main():
    mode, path = sys.argv[1], sys.argv[2]
    if mode == "dump":
        with open(path, "w") as f:
            json.dump(run(), f, indent=1, sort_keys=True)
        print(f"dumped {len(run())} cases to {path}")
        return 0
    with open(path) as f:
        frozen = json.load(f)
    current = run()
    diffs = [k for k in frozen if current.get(k) != frozen[k]]
    for k in diffs[:20]:
        print(f"DIFF {k!r}\n  frozen:  {frozen[k]!r}\n"
              f"  current: {current.get(k)!r}")
    print(f"{len(frozen) - len(diffs)}/{len(frozen)} identical, "
          f"{len(diffs)} diffs")
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main())
