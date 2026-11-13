"""T-4158: the article alternation needs its own group.

``_art`` built ``(?:{article}\\s+)?`` where ``article`` is an alternation.
``\\s+`` then bound to the last alternative alone, so every other article
matched with no space after it and stayed in the remainder. German "der",
French "la", "le" and "l'", Italian "la" and "il", Spanish "el" and
Portuguese "o" were all affected; only the alternative written last in each
language came out clean, which is why a one-article check never found it.
``eras_scan._era_pattern`` writes the same construct with the inner group.
"""
import re
import unittest
from datetime import date

from ovos_date_parser.scoped_scan import (extract_scoped_date, _art,
                                          load_scoped_vocabulary)

REF = date(2026, 9, 25)

#: (lang, line, the article the line opens with). Each language is covered
#: by an article that is NOT the last alternative of its own .voc, which is
#: the case the missing group broke, and by the last one, which is the
#: control that was already clean.
LINES = [
    ("de", "der 3 tag von märz", "der", False),
    ("de", "die 3 woche von märz", "die", True),
    ("fr", "le 3 jour de mars", "le", False),
    ("fr", "la 3 semaine de mars", "la", False),
    ("fr", "l' 3 semaine de mars", "l'", False),
    ("it", "il 3 giorno di marzo", "il", False),
    ("it", "la 3 settimana di marzo", "la", False),
    ("es", "el 3 dia de marzo", "el", False),
    ("es", "la 3 semana de marzo", "la", True),
    ("pt", "o 3 dia de março", "o", False),
    ("pt", "a 3 semana de março", "a", True),
]


class TestArticleLeavesNoRemainder(unittest.TestCase):

    def test_no_article_stays_in_the_remainder(self):
        for lang, line, article, _ in LINES:
            with self.subTest(lang=lang, article=article):
                vocab = load_scoped_vocabulary(lang)
                out = extract_scoped_date(line, vocab, ref_date=REF)
                self.assertIsNotNone(out, f"{lang}: {line!r} read as no date")
                self.assertEqual(out[1], "", f"{lang}: {line!r}")

    def test_the_last_alternative_was_always_clean(self):
        """The control that tells the fix from a coincidence. These lines
        passed before the group was added, because ``\\s+`` bound to their
        article. If the fix had broken them the suite would say so here and
        not in the test above."""
        for lang, line, article, was_clean in LINES:
            if not was_clean:
                continue
            with self.subTest(lang=lang, article=article):
                vocab = load_scoped_vocabulary(lang)
                out = extract_scoped_date(line, vocab, ref_date=REF)
                self.assertEqual(out[1], "")

    def test_at_least_one_line_per_language_was_broken(self):
        """The fail-before control. If every line here happened to end in
        its language's last alternative, the test above would pass on the
        unfixed code and prove nothing."""
        broken = {lang for lang, _, _, was_clean in LINES if not was_clean}
        self.assertEqual(broken, {"de", "fr", "it", "es", "pt"})


#: an elided article is written against its noun with nothing between
#: them, so it must match without whitespace after it.
ELIDED = [
    ("fr", "le 2eme jour de l'annee", date(2026, 1, 2)),
    ("fr", "le 3eme jour de janvier", date(2026, 1, 3)),
]


class TestAnElidedArticleNeedsNoSpace(unittest.TestCase):
    """The case the plain ``(?:(?:article)\\s+)?`` broke.

    French writes ``l'annee`` with nothing between the article and the
    noun. Requiring whitespace after every article stopped that phrase
    resolving at all. The unwrapped pattern carried it by accident, because
    ``l'`` is not the last alternative and so matched bare.
    """

    def test_the_elided_form_still_resolves(self):
        for lang, line, expected in ELIDED:
            with self.subTest(lang=lang, line=line):
                vocab = load_scoped_vocabulary(lang)
                out = extract_scoped_date(line, vocab, ref_date=date(2026, 9, 25))
                self.assertIsNotNone(out, f"{lang}: {line!r} read as no date")
                self.assertEqual(out[0], expected)
                self.assertEqual(out[1], "", f"{lang}: {line!r}")

    def test_only_an_apostrophe_waives_the_space(self):
        """The control. A non-elided article must still need its space, or
        the waiver would just restore the defect under another name."""
        for lang in ("de", "fr", "it", "es", "pt"):
            vocab = load_scoped_vocabulary(lang)
            pattern = re.compile(_art(vocab) + "$")
            for alt in vocab.article.split("|"):
                word = alt.replace("\\", "")
                if word.endswith("'"):
                    continue
                with self.subTest(lang=lang, article=word):
                    self.assertIsNone(pattern.fullmatch(word),
                                      f"{lang}: {word!r} matches with no space")


class TestArtGroupsTheAlternation(unittest.TestCase):
    """The pattern itself, so the defect cannot come back through a
    different call site."""

    def test_the_alternation_is_grouped(self):
        for lang in ("de", "fr", "it", "es", "pt"):
            with self.subTest(lang=lang):
                vocab = load_scoped_vocabulary(lang)
                self.assertEqual(
                    _art(vocab),
                    rf"(?:(?:{vocab.article})(?:\s+|(?<=')))?")

    def test_every_article_takes_its_space(self):
        """Read off the pattern, not off one parse: every alternative must
        accept whitespace after it, so the group covers all of them and not
        only the one written last."""
        for lang in ("de", "fr", "it", "es", "pt"):
            vocab = load_scoped_vocabulary(lang)
            pattern = re.compile(_art(vocab) + "$")
            for alt in vocab.article.split("|"):
                word = alt.replace("\\", "")
                with self.subTest(lang=lang, article=word):
                    self.assertIsNotNone(pattern.fullmatch(word + " "))


if __name__ == "__main__":
    unittest.main()
