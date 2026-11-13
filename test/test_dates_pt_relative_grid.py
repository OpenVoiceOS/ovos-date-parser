"""Grid of relative dates in pt-PT and pt-BR.

Phrases are built from a marker, a unit, an optional weekday and an optional
period tail. Every expected date comes from the calendar rules below, which
are independent of the parser. The numbered rulings are those of the
chronologia disagreement classes, which ``extract_datetime`` follows for a
locale it routes to chronologia:

* next <weekday> is the first such weekday after the anchor day, last or
  past <weekday> the most recent one before it, this <weekday> the first on
  or after it (ruling 12);
* next, last and "que vem" on a week, month or year name the calendar unit
  one step on or back, and the week starts on the locale's first day of the
  week: Monday in pt-PT and Sunday in pt-BR, as the CLDR week data gives
  them (class 2b);
* a count with daqui a, dentro de or em moves forward, and with há or faz
  backward, from the anchor's own wall clock, the day of month clamped to
  the month length (class 1);
* a weekday after a count of weeks is that weekday of the Monday-first week
  the count lands in; after days, months or years it is the first one on or
  after the date reached;
* a weekday after amanhã, depois de amanhã, ontem or anteontem names that
  day when the two agree, and no day when they do not (ruling 15);
* the first, second or third day or weekday of a period is counted from its
  start, and the last one back from its end; said of "o mês" it moves to
  the next month when the day or week has already ended, and said of "deste
  mês" it stays in the anchor's month (ruling 13);
* a week of a month starts on a Monday and counts only when that Monday
  is inside the month: the first week starts on the first Monday on or
  after the first day, and the last week on the last Monday;
* a week of a year is an ISO 8601 week: the first is the week with 4
  January in it, and the last the week with 28 December in it (ruling 14);
* a weekday read before a count lands where it would after the count;
* counts joined by "e" add up, forward after daqui a, dentro de or em and
  backward after há or faz, from the anchor's wall clock (class 1);
* a weekday "da semana que vem", "da próxima semana" or "da semana
  passada" is that weekday of the calendar week one week on or back
  (class 2b);
* "o dia N" of a month is that day of the month, and moves to the next month
  when it has passed, like the other days of "o mês".
"""
import unittest
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from ovos_date_parser import extract_datetime

TZ = ZoneInfo("Europe/Lisbon")
ANCHORS = {
    "saturday": datetime(2026, 10, 17, 12, 0, tzinfo=TZ),
    "friday": datetime(2026, 10, 16, 10, 0, tzinfo=TZ),
    "monday": datetime(2026, 10, 19, 9, 0, tzinfo=TZ),
    "jan31": datetime(2026, 1, 31, 12, 0, tzinfo=TZ),
    "feb29": datetime(2028, 2, 29, 12, 0, tzinfo=TZ),
    "dec31": datetime(2026, 12, 31, 23, 50, tzinfo=TZ),
}
LANGS = ("pt-PT", "pt-BR")
WEEKDAYS = [  # Monday is 0
    ("segunda-feira", "f"), ("terça-feira", "f"), ("quarta-feira", "f"),
    ("quinta-feira", "f"), ("sexta-feira", "f"), ("sábado", "m"),
    ("domingo", "m")]
MONTHS = {"novembro": 11, "dezembro": 12}
SPELLED = {1: ("um", "uma"), 2: ("dois", "duas"), 3: ("três", "três")}
UNITS = {"dia": ("dia", "dias", "m"), "semana": ("semana", "semanas", "f"),
         "mês": ("mês", "meses", "m"), "ano": ("ano", "anos", "m")}

WEEKDAY_SENTENCES = (
    ("segunda aqui no escritório", 19),
    ("segunda cedo", 19),
    ("sexta à noite", 23),
    ("quinta vou ao médico", 22),
    ("terça tenho reunião", 20),
    ("na segunda vou", 19),
    ("a segunda sessão é na quinta", 22),
    ("a segunda aula é sexta", 23),
    ("na segunda", 19),
    ("segunda", 19),
)

CONFUSABLES = (
    "ganhei um ano e três meses de bónus",
    "comprei um ano e dois meses de assinatura",
    "a segunda dose da vacina",
    "a quarta onda da pandemia",
    "a sexta sinfonia de beethoven",
    "a segunda maior cidade",
    "a segunda metade do jogo",
    "a segunda pergunta",
    "a segunda filha dela",
    "pela segunda vez",
    "a segunda opinião",
    "uma segunda opinião",
    "a sexta etapa do rali",
    "minha segunda casa",
    "a quarta vez",
    "quinta vez",
    "a segunda mensagem",
    "a terceira versão",
    "na segunda vez",
    "a segunda opção",
    "a terça parte",
    "a quarta vez",
    "a quinta casa",
    "a sexta posição",
    "a segunda semana",
    "o último a sair apaga a luz",
    "a última vez que o vi",
    "o próximo passo é simples",
    "a próxima pergunta é difícil",
    "o que vem a seguir",
    "o mês é longo",
    "o ano é bissexto",
    "a semana é curta",
    "o dia foi longo",
    "o último dia de escola foi triste",
    "passado, presente e futuro",
    "o que passou, passou",
    "ele tem vinte e cinco anos",
    "tenho dois irmãos e três irmãs",
    "quem vem aí",
    "daqui a pouco",
    "depois do almoço",
    "o seguinte capítulo",
    "a última página",
    "que vem fazer aqui",
    "a terceira vez",
    "o último a chegar",
    "uma semana de férias",
    "tenho vinte anos",
    "ele tem trinta anos",
    "a casa tem cem anos",
    "mil anos",
    "o meu filho tem cinco anos",
    "passei duas semanas em paris",
    "tive uma semana difícil",
    "fiquei três dias em casa",
    "demorou três dias",
    "estive dois meses no brasil",
    "sete dias por semana",
)


def midnight(d):
    return datetime(d.year, d.month, d.day)


def wall_clock(d):
    return d.replace(tzinfo=None)


def week_start(a, lang):
    """The first day of the anchor's week: Sunday in pt-BR, Monday in pt-PT."""
    first = 6 if lang == "pt-BR" else 0
    return midnight(a) - timedelta(days=(a.weekday() - first) % 7)


def count_from(a, delta):
    """A counted offset keeps the anchor's wall clock (class 1)."""
    return wall_clock(a) + relativedelta(**delta)


def iso_week(year, n):
    """The Monday of ISO 8601 week n, or of the last week when n is -1."""
    if n == -1:
        dec28 = date(year, 12, 28)
        monday = dec28 - timedelta(days=dec28.weekday())
    else:
        monday = date.fromisocalendar(year, n, 1)
    return datetime(monday.year, monday.month, monday.day)


def shift(a, unit, n):
    kw = {"dia": "days", "semana": "weeks", "mês": "months", "ano": "years"}
    return midnight(a) + relativedelta(**{kw[unit]: n})


def after(a, d):
    return midnight(a) + timedelta(days=(d - a.weekday() - 1) % 7 + 1)


def before(a, d):
    return midnight(a) - timedelta(days=(a.weekday() - d - 1) % 7 + 1)


def on_or_after(day, d):
    return day + timedelta(days=(d - day.weekday()) % 7)


def last_on_or_before(end, d):
    return end - timedelta(days=(end.weekday() - d) % 7)


def month_end(a, k=0):
    return midnight(a) + relativedelta(months=k, day=31)


def nth(kind, n, begin, d=None):
    """The nth day, weekday d, or Monday-started week from the period start."""
    if kind in ("dia", "number"):
        return begin + timedelta(days=n - 1)
    if kind == "weekday":
        return on_or_after(begin, d) + timedelta(days=7 * (n - 1))
    return on_or_after(begin, 0) + timedelta(days=7 * (n - 1))


def period(a, k):
    begin = midnight(a).replace(day=1) + relativedelta(months=k)
    return begin, begin + relativedelta(day=31)


def calendar_unit(a, unit, step, lang):
    """The start of the calendar week, month or year step units on (2b)."""
    if unit == "semana":
        return week_start(a, lang) + timedelta(days=7 * step)
    if unit == "mês":
        return midnight(a).replace(day=1) + relativedelta(months=step)
    return datetime(a.year + step, 1, 1)


def cases(a, lang):
    """Yield (text, expected datetime or None) for one anchor and locale."""
    out = []
    # a week, month or year, next and last
    for unit in ("semana", "mês", "ano"):
        sing, _, g = UNITS[unit]
        art, nxt, lst = ("a", "próxima", "última") if g == "f" else \
            ("o", "próximo", "último")
        pas = "passada" if g == "f" else "passado"
        nextd = calendar_unit(a, unit, 1, lang)
        lastd = calendar_unit(a, unit, -1, lang)
        for t in (f"{nxt} {sing}", f"{art} {nxt} {sing}",
                  f"n{art} {nxt} {sing}", f"{art} {sing} que vem",
                  f"{art} {sing} seguinte"):
            out.append((t, nextd))
        for t in (f"{art} {sing} {pas}", f"{art} {lst} {sing}",
                  f"n{art} {lst} {sing}"):
            out.append((t, lastd))
    # counts of days, weeks, months and years
    for unit, (sing, plur, g) in UNITS.items():
        for n in (1, 2, 3):
            word = SPELLED[n][g == "f"]
            noun = sing if n == 1 else plur
            kw = {"dia": "days", "semana": "weeks", "mês": "months",
                  "ano": "years"}[unit]
            for form in (f"{n} {noun}", f"{word} {noun}"):
                for marker in ("daqui a", "dentro de", "em"):
                    out.append((f"{marker} {form}", count_from(a, {kw: n})))
                for marker in ("há", "faz"):
                    out.append((f"{marker} {form}", count_from(a, {kw: -n})))
    # weekdays: next, last, this, in both orders
    for d, (name, g) in enumerate(WEEKDAYS):
        nxt, lst, this, pas = (("próxima", "última", "esta", "passada")
                               if g == "f" else
                               ("próximo", "último", "este", "passado"))
        art = "a" if g == "f" else "o"
        for t in (f"{nxt} {name}", f"{art} {nxt} {name}",
                  f"n{art} {nxt} {name}", f"{name} que vem",
                  f"{art} {name} que vem"):
            out.append((t, after(a, d)))
        for t in (f"{name} {pas}", f"{art} {name} {pas}", f"{lst} {name}",
                  f"{art} {lst} {name}", f"n{art} {lst} {name}"):
            out.append((t, before(a, d)))
        out.append((f"{this} {name}", on_or_after(midnight(a), d)))
        for t in (f"n{art} {name} {pas}", f"n{art} {name} que vem"):
            out.append((t, before(a, d) if pas in t else after(a, d)))
        short = name.split("-")[0]
        if short != name:
            out.append((f"{nxt} {short}", after(a, d)))
            out.append((f"{short} que vem", after(a, d)))
            out.append((f"{short} {pas}", before(a, d)))
            out.append((f"{lst} {short}", before(a, d)))
            out.append((f"{this} {short}", on_or_after(midnight(a), d)))
    # a weekday after a relative day
    for d in (0, 4, 6):
        name = WEEKDAYS[d][0]
        for word, off in (("amanhã", 1), ("depois de amanhã", 2),
                          ("ontem", -1), ("anteontem", -2)):
            day = midnight(a) + timedelta(days=off)
            out.append((f"{word} {name}",
                        day if day.weekday() == d else None))
    # a weekday after a count
    for d in (0, 4, 6):
        name = WEEKDAYS[d][0]
        for n in (1, 2):
            word = SPELLED[n][1]
            for sign, markers in ((1, ("daqui a", "dentro de")), (-1, ("há",))):
                landed = midnight(a) + timedelta(days=7 * n * sign)
                monday = landed - timedelta(days=landed.weekday())
                for marker in markers:
                    out.append((f"{marker} {word} semana{'s' if n > 1 else ''}"
                                f" {name}", monday + timedelta(days=d)))
        for unit in ("mês", "ano"):
            reached = shift(a, unit, 1)
            out.append((f"daqui a um {unit} {name}", on_or_after(reached, d)))
    # a weekday read before the count
    for d in (0, 4, 6):
        name = WEEKDAYS[d][0]
        for n in (1, 2):
            landed = midnight(a) + timedelta(days=7 * n)
            monday = landed - timedelta(days=landed.weekday())
            out.append((f"{name} daqui a {SPELLED[n][1]} semana"
                        f"{'s' if n > 1 else ''}", monday + timedelta(days=d)))
        for unit in ("mês", "ano"):
            reached = shift(a, unit, 1)
            out.append((f"{name} daqui a um {unit}",
                        on_or_after(reached, d)))
    # a weekday of the week before or after this one
    for d, (name, g) in enumerate(WEEKDAYS):
        art = "a" if g == "f" else "o"
        spaced = name.replace("-", " ")
        for k, tail in ((1, "da semana que vem"), (1, "da próxima semana"),
                        (-1, "da semana passada")):
            start = calendar_unit(a, "semana", k, lang)
            day = start + timedelta(days=(d - start.weekday()) % 7)
            for lead in ("", art + " "):
                out.append((f"{lead}{name} {tail}", day))
            if spaced != name:
                out.append((f"{art} {spaced} {tail}", day))
    # two counts joined by "e"
    for words, delta in (("uma semana e dois dias", dict(days=9)),
                         ("duas semanas e um dia", dict(days=15)),
                         ("um mês e três dias", dict(months=1, days=3)),
                         ("um ano e um mês", dict(years=1, months=1))):
        out.append((f"daqui a {words}", count_from(a, delta)))
        out.append((f"dentro de {words}", count_from(a, delta)))
        negative = {k: -v for k, v in delta.items()}
        out.append((f"há {words}", count_from(a, negative)))
    # the first, nth and last day or weekday of a period
    tails = [("do mês", midnight(a).replace(day=1), month_end(a)),
             ("deste mês", midnight(a).replace(day=1), month_end(a)),
             ("do mês que vem", *period(a, 1)),
             ("do próximo mês", *period(a, 1)),
             ("do mês passado", *period(a, -1)),
             ("do ano", datetime(a.year, 1, 1), datetime(a.year, 12, 31)),
             ("deste ano", datetime(a.year, 1, 1), datetime(a.year, 12, 31)),
             (f"de {a.year}", datetime(a.year, 1, 1),
              datetime(a.year, 12, 31)),
             (f"de {a.year + 1}", datetime(a.year + 1, 1, 1),
              datetime(a.year + 1, 12, 31))]
    for name, num in MONTHS.items():
        if num >= a.month:
            begin = datetime(a.year, num, 1)
            tails.append((f"de {name}", begin, begin + relativedelta(day=31)))
        begin = datetime(a.year + 1, num, 1)
        tails.append((f"de {name} de {a.year + 1}", begin,
                      begin + relativedelta(day=31)))
    for tail, begin, end in tails:
        rolls = tail == "do mês"
        of_year = tail in ("do ano", "deste ano", f"de {a.year}",
                           f"de {a.year + 1}")

        def pick(kind, n, d=None):
            day = nth(kind, n, begin, d)
            length = timedelta(days=7 if kind == "semana" else 1)
            if rolls and day + length <= midnight(a):
                day = nth(kind, n, begin + relativedelta(months=1), d)
            return day

        def last_weekday(d):
            day = last_on_or_before(end, d)
            if rolls and day < midnight(a):
                day = last_on_or_before(month_end(a, 1), d)
            return day

        out.append(("o último dia " + tail, end))
        if tail.split()[-1] in ("mês", "vem", "passado") and \
                "ano" not in tail:
            for n in (5, 20):
                for lead in ("o dia", "dia"):
                    out.append((f"{lead} {n} {tail}", pick("number", n)))
        if of_year:
            out.append(("a última semana " + tail, iso_week(end.year, -1)))
        else:
            out.append(("a última semana " + tail,
                        end - timedelta(end.weekday())))
        out.append(("o primeiro dia " + tail, pick("dia", 1)))
        for word, n in (("primeira", 1), ("segunda", 2), ("terceira", 3)):
            out.append((f"a {word} semana {tail}",
                        iso_week(end.year, n) if of_year
                        else pick("semana", n)))
        for d in (1, 4, 6):
            name, g = WEEKDAYS[d]
            lst, fst = ("última", "primeira") if g == "f" else \
                ("último", "primeiro")
            art = "a" if g == "f" else "o"
            out.append((f"{art} {lst} {name} {tail}", last_weekday(d)))
            out.append((f"{art} {fst} {name} {tail}", pick("weekday", 1, d)))
            if g == "f":
                for word, n in (("segunda", 2), ("terceira", 3)):
                    out.append((f"a {word} {name} {tail}",
                                pick("weekday", n, d)))
    return out


class TestPtRelativeGrid(unittest.TestCase):
    def test_grid(self):
        total = 0
        for key, anchor in ANCHORS.items():
            for lang in LANGS:
                for text, expected in cases(anchor, lang):
                    total += 1
                    with self.subTest(anchor=key, text=text, lang=lang):
                        res = extract_datetime(text, anchorDate=anchor,
                                               lang=lang)
                        if expected is None:
                            self.assertIsNone(res)
                            continue
                        self.assertIsNotNone(res)
                        self.assertEqual(res[0].replace(tzinfo=None), expected)
                        self.assertEqual(res[1], "")
        self.assertGreater(total, 4000)

    def test_a_weekday_in_a_sentence_is_a_weekday(self):
        for text, day in WEEKDAY_SENTENCES:
            for lang in LANGS:
                with self.subTest(text=text, lang=lang):
                    res = extract_datetime(
                        text, anchorDate=ANCHORS["saturday"], lang=lang)
                    self.assertIsNotNone(res)
                    self.assertEqual(res[0].date(),
                                     datetime(2026, 10, day).date())

    def test_a_day_that_the_rolled_month_lacks_moves_on(self):
        jan31 = ANCHORS["jan31"]
        jan31_leap = datetime(2028, 1, 31, 12, 0, tzinfo=TZ)
        for text, anchor, expected in (
                ("o dia 30 do mês", jan31, datetime(2026, 3, 30)),
                ("o dia 29 do mês", jan31, datetime(2026, 3, 29)),
                ("o dia 28 do mês", jan31, datetime(2026, 2, 28)),
                ("o dia 29 do mês", jan31_leap, datetime(2028, 2, 29)),
                ("o dia 30 do mês", jan31_leap, datetime(2028, 3, 30))):
            for lang in LANGS:
                with self.subTest(text=text, lang=lang, anchor=anchor):
                    res = extract_datetime(text, anchorDate=anchor, lang=lang)
                    self.assertEqual(res[0].replace(tzinfo=None), expected)

    def test_a_named_month_that_lacks_the_day_is_no_date(self):
        saturday = ANCHORS["saturday"]
        dec31 = ANCHORS["dec31"]
        for text, anchor in (("o dia 31 do próximo mês", saturday),
                             ("o dia 31 do mês que vem", saturday),
                             ("o dia 31 do mês passado", saturday),
                             ("o dia 29 do próximo mês", ANCHORS["jan31"]),
                             ("o dia 31 de novembro", saturday),
                             ("dia 31 de novembro", saturday),
                             ("31 de abril", saturday),
                             ("o dia 30 de fevereiro", saturday)):
            for lang in LANGS:
                with self.subTest(text=text, lang=lang):
                    self.assertIsNone(extract_datetime(
                        text, anchorDate=anchor, lang=lang))
        # "29 de fevereiro" said in October 2026 is the next 29 February,
        # in 2028: class 3 takes the next occurrence after the anchor, and
        # ruling 13 skips a year that lacks the day as it skips a month.
        for text, anchor, expected in (
                ("29 de fevereiro", saturday, datetime(2028, 2, 29)),
                ("o dia 31 do próximo mês", dec31, datetime(2027, 1, 31)),
                ("o dia 30 do mês que vem", saturday, datetime(2026, 11, 30)),
                ("29 de fevereiro", datetime(2028, 1, 31, 12, 0, tzinfo=TZ),
                 datetime(2028, 2, 29)),
                ("o dia 31 de outubro", saturday, datetime(2026, 10, 31))):
            for lang in LANGS:
                with self.subTest(text=text, lang=lang):
                    res = extract_datetime(text, anchorDate=anchor, lang=lang)
                    self.assertEqual(res[0].replace(tzinfo=None), expected)

    def test_a_bare_weekday_is_still_a_weekday(self):
        # a part of the day answers the middle of its band, and the CLDR
        # morning1 of pt runs from 06:00 to 12:00, so "de manhã" is 09:00
        for text, expected in (("segunda", datetime(2026, 10, 19)),
                               ("na segunda", datetime(2026, 10, 19)),
                               ("na terça", datetime(2026, 10, 20)),
                               ("quarta de manhã", datetime(2026, 10, 21, 9)),
                               ("sexta às 10", datetime(2026, 10, 23, 10))):
            for lang in LANGS:
                with self.subTest(text=text, lang=lang):
                    res = extract_datetime(
                        text, anchorDate=ANCHORS["saturday"], lang=lang)
                    self.assertEqual(res[0].replace(tzinfo=None), expected)

    def test_ordinary_sentences_are_not_dates(self):
        for key, anchor in ANCHORS.items():
            for text in CONFUSABLES:
                for lang in LANGS:
                    with self.subTest(anchor=key, text=text, lang=lang):
                        self.assertIsNone(extract_datetime(
                            text, anchorDate=anchor, lang=lang))


if __name__ == "__main__":
    unittest.main()
