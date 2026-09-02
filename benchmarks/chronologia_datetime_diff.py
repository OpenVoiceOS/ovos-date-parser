"""Differential: ovos-date-parser's ``extract_datetime`` vs chronologia's
``extract_timespan``, phrase by phrase, at one fixed anchor.

Routing extraction through chronologia has to keep ``extract_datetime``'s
signature and its public answers, so the work is not writing the routing --
it is knowing where the two engines already disagree. This harness sizes
that: every phrase lands in one of five buckets.

    SAME                both answer and the instant matches
    DIFFERENT           both answer, the instants differ  <- adoption work
    DATE-PARSER-ONLY    only we answer                    <- adoption work
    CHRONOLOGIA-ONLY    only chronologia answers          <- adoption work
    BOTH-NONE           neither answers (agreement by refusal)

The phrases are harvested from what the repo already asserts, so every one
of them is attested. An AST walk collects the first string literal of each
call to the extraction helpers in the test files, taking the language from
the file name (``test_dates_<lang>*.py``,
``parse_tests/test_parse_<lang>.py``); the two sibling harnesses contribute
their own corpora on top -- the English template sweep from
``en_datetime_oracle`` and the era phrases from ``multi_date_diff``.
Nothing is invented, and no language appears that the repo does not already
cover.

chronologia answers a span where we answer an instant; the span's start is
the comparable value. A span wider than a day is a coarser reading of the
same phrase, which the row shows as its width.

Usage: python benchmarks/chronologia_datetime_diff.py [lang ...]
"""
import ast
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import chronologia as c

from ovos_date_parser import extract_datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))
import en_datetime_oracle  # noqa: E402
import multi_date_diff  # noqa: E402

#: The anchor the repo's own differential harnesses use.
ANCHOR = datetime(2017, 6, 27, 13, 4)

TEST_ROOT = Path(__file__).resolve().parent.parent / "test"

#: The helper names the test files call with the phrase as first argument.
#: Every ``extract*`` entry point counts except the duration ones, whose
#: phrases are spans of time rather than points on the calendar.
EXTRACTORS = {"_dt", "testExtract", "_ex", "_parse", "_date", "when",
              "_check", "_extract", "extract_dt", "assertDate", "_assert_dt",
              "_hm"}


def _is_extractor(name):
    if name in EXTRACTORS:
        return True
    return bool(name) and name.startswith("extract") \
        and not name.startswith("extract_duration")


def _lang_of(path):
    name = path.stem
    for prefix in ("test_dates_", "test_parse_"):
        if name.startswith(prefix):
            return name[len(prefix):].split("_")[0]
    return None


def harvest():
    """phrases per language, from the repo's own test files."""
    found = defaultdict(list)
    for path in sorted(TEST_ROOT.rglob("test_*.py")):
        lang = _lang_of(path)
        if lang is None or len(lang) > 3:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else \
                getattr(func, "id", None)
            if not _is_extractor(name):
                continue
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                phrase = arg.value.strip()
                # strftime patterns share the call shape but are not phrases
                if phrase and "%" not in phrase and phrase not in found[lang]:
                    found[lang].append(phrase)
    for lang, phrases in multi_date_diff.PHRASES.items():
        _add(found[lang], phrases)
    _add(found["en"], en_datetime_oracle.corpus())
    return {k: v for k, v in found.items() if v}


def _add(bucket, phrases):
    for phrase in phrases:
        phrase = phrase.strip()
        if phrase and phrase not in bucket:
            bucket.append(phrase)


def _ours(phrase, lang):
    try:
        res = extract_datetime(phrase, lang=lang, anchorDate=ANCHOR)
    except Exception as exc:
        return None, f"raised {type(exc).__name__}"
    if not res or res[0] is None:
        return None, ""
    dt = res[0]
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt, (res[1] or "")


def _theirs(phrase, lang):
    try:
        res = c.extract_timespan(phrase, lang, ANCHOR)
    except Exception as exc:
        return None, None, f"raised {type(exc).__name__}"
    if res is None:
        return None, None, ""
    span, remainder = res
    try:
        start = span.start.datetime()
    except Exception:
        start = None
    if start is None:
        # a span outside the datetime range (deep BC, far future) still counts
        # as an answer; it simply has no comparable instant
        return None, span, (remainder or "")
    return start.replace(tzinfo=None), span, (remainder or "")


def _width(span):
    try:
        return str(span.end.datetime() - span.start.datetime())
    except Exception:
        return "?"


def classify(phrase, lang):
    ours, our_rem = _ours(phrase, lang)
    theirs, span, their_rem = _theirs(phrase, lang)
    if theirs is None and span is not None:
        # chronologia answered a span no datetime can hold
        note = f"them {span.start}..{span.end} (outside the datetime range)"
        if ours is None:
            return "CHRONOLOGIA-ONLY", note
        return "DIFFERENT", f"us {ours.isoformat()} | " + note
    if ours is None and theirs is None:
        return "BOTH-NONE", ""
    if theirs is None:
        return "DATE-PARSER-ONLY", f"us {ours.isoformat()} rem={our_rem!r}"
    if ours is None:
        return "CHRONOLOGIA-ONLY", (f"them {theirs.isoformat()} "
                                    f"width={_width(span)} rem={their_rem!r}")
    if ours == theirs:
        return "SAME", ""
    return "DIFFERENT", (f"us {ours.isoformat()} | them {theirs.isoformat()} "
                         f"width={_width(span)}")


def main(argv):
    corpus = harvest()
    langs = argv or sorted(corpus)
    grand = Counter()
    detail = []
    for lang in langs:
        phrases = corpus.get(lang)
        if not phrases:
            print(f"# {lang}: no attested phrases in the test corpus")
            continue
        tally = Counter()
        for phrase in phrases:
            bucket, note = classify(phrase, lang)
            tally[bucket] += 1
            if bucket != "SAME" and bucket != "BOTH-NONE":
                detail.append((lang, bucket, phrase, note))
        grand.update(tally)
        summary = "  ".join(f"{k}={tally[k]}" for k in
                            ("SAME", "DIFFERENT", "DATE-PARSER-ONLY",
                             "CHRONOLOGIA-ONLY", "BOTH-NONE") if tally[k])
        print(f"{lang:5} n={len(phrases):4}  {summary}")

    print()
    print("TOTAL  " + "  ".join(f"{k}={grand[k]}" for k in
                                ("SAME", "DIFFERENT", "DATE-PARSER-ONLY",
                                 "CHRONOLOGIA-ONLY", "BOTH-NONE")))
    print()
    print("-- rows that are adoption work " + "-" * 45)
    for lang, bucket, phrase, note in detail:
        print(f"{lang:5} {bucket:17} {phrase!r}")
        if note:
            print(f"{'':23} {note}")


if __name__ == "__main__":
    main(sys.argv[1:])
