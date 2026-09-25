"""Three-way differential: ovos-date-parser vs dateparser vs dateutil.

The same vote logic as the number parser's multi-reference harness: one
reference implementation can be wrong or absent for a phrase, so two
independent ones turn the comparison into a signal:

* both references agree with us            -> almost certainly correct
* both agree with EACH OTHER but not us    -> strongest bug signal; a lead
* the references disagree with each other  -> genuinely contested
  (locale conventions, relative-date semantics); adjudicate by hand,
  never auto-trust either library.

Nothing is pinned to a library: a disagreement is a lead, and the
expected value in any test still comes from a documented convention.

dateutil only handles absolute formats, so it abstains from relative
phrases; dateparser handles both (RELATIVE_BASE pins "2 days ago" to the
anchor).  Both abstain by returning None, which never counts as a vote.

Usage: python benchmarks/multi_date_diff.py [lang ...]   (default: en pt
es fr de it — languages with era vocabularies)
"""
import sys
from datetime import datetime

import dateparser
from dateutil import parser as dateutil_parser

from ovos_date_parser import extract_datetime

ANCHOR = datetime(2017, 6, 27, 13, 4)

#: phrases per language: absolute dates (all three can vote), relative
#: dates (dateparser + us), and era phrases (ours alone -- listed to
#: document that the references abstain, not to score them)
PHRASES = {
    "en": ["june 5 2027", "5 december 2030", "march 5th", "2017-06-30",
           "tomorrow", "yesterday", "in 3 days", "2 weeks ago",
           "next friday", "in 2 months", "44 bc", "in the year 12000"],
    "pt": ["5 de junho de 2027", "5 de dezembro de 2030", "amanhã",
           "ontem", "daqui a 3 dias", "há 2 semanas", "44 a.C."],
    "es": ["5 de junio de 2027", "mañana", "ayer", "en 3 días",
           "hace 2 semanas", "44 a. C."],
    "fr": ["5 juin 2027", "demain", "hier", "dans 3 jours",
           "il y a 2 semaines", "44 av. J.-C."],
    "de": ["5. juni 2027", "morgen", "gestern", "in 3 tagen",
           "vor 2 wochen", "44 v. Chr."],
    "it": ["5 giugno 2027", "domani", "ieri", "tra 3 giorni",
           "2 settimane fa", "44 a.C."],
}


def ours(text, lang):
    try:
        out = extract_datetime(text, lang, anchorDate=ANCHOR)
    except Exception as exc:
        return f"<raise {type(exc).__name__}>"
    return out and out[0].date().isoformat()


def ref_dateparser(text, lang):
    try:
        out = dateparser.parse(text, languages=[lang],
                               settings={"RELATIVE_BASE": ANCHOR,
                                         "PREFER_DATES_FROM": "future"})
    except Exception:
        return None
    return out and out.date().isoformat()


def ref_dateutil(text):
    try:
        return dateutil_parser.parse(text, default=ANCHOR).date().isoformat()
    except Exception:
        return None


def main(langs):
    for lang in langs:
        leads, contested, agree = [], 0, 0
        for text in PHRASES.get(lang, []):
            us = ours(text, lang)
            votes = {v for v in (ref_dateparser(text, lang),
                                 ref_dateutil(text) if lang == "en" else
                                 None) if v}
            if not votes:
                continue
            if len(votes) > 1:
                contested += 1
            elif us in votes:
                agree += 1
            else:
                leads.append((text, us, votes.pop()))
        print(f"\n### {lang}: {agree} agree, {len(leads)} leads, "
              f"{contested} contested")
        for text, us, ref in leads:
            print(f"  LEAD {text!r}: ours={us!r} refs={ref!r}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["en", "pt", "es", "fr", "de", "it"])
