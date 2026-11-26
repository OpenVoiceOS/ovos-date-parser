"""Date and time tools for Modern Standard Arabic.

Time is told with the feminine ordinal hour names after "الساعة"
(e.g. "الساعة الثالثة" = 3 o'clock) using half-past semantics:
"التاسعة والنصف" = 9:30, "التاسعة إلا ربعاً" = quarter to nine.

Counted-noun agreement follows Wright, "A Grammar of the Arabic
Language" Vol. I: the dual endings -āni (nominative) / -aini (oblique)
give يومان/يومين = "two days" (§299), and cardinal numerals 3-10 take
the gender opposite the counted noun (§319-§321), so the feminine
nouns ساعة/دقيقة/ثانية take the bare numeral forms ثلاث/أربع/خمس while
the masculine يوم takes ثلاثة/أربعة/خمسة.
"""
from datetime import timedelta

from ovos_number_parser.numbers_ar import (
    pronounce_number_ar,
    _normalize_ar,
    _ONES_FEM_AR,
    _TENS_AR,
)

# feminine cardinals for counting feminine nouns like دقيقة (gender polarity)
_FEM_TEENS_AR = {11: "إحدى عشرة", 12: "اثنتا عشرة"}

# Feminine hour names, spoken with the definite article after "الساعة".
# Arabic Without Walls (UC Davis), chapter 9 grammar note: "To tell time in
# Standard Arabic, ordinal numbers are used. Since the ordinal number
# functions as an adjective after الساعة, the feminine form of the number is
# used"; "The only exception is (one o' clock) الساعة الواحدة, which does not
# use the ordinal الأولى but uses instead the cardinal الواحدة".
# https://arabicwithoutwalls.ucdavis.edu/chapter9/grammar_note9.html
_HOUR_NAMES_AR = {1: "الواحدة", 2: "الثانية", 3: "الثالثة", 4: "الرابعة",
                  5: "الخامسة", 6: "السادسة", 7: "السابعة", 8: "الثامنة",
                  9: "التاسعة", 10: "العاشرة", 11: "الحادية عشرة",
                  12: "الثانية عشرة"}

_TO_THE_HOUR_AR = {40: "إلا ثلثاً", 45: "إلا ربعاً"}

_MONTHS_AR = {1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو",
              6: "يونيو", 7: "يوليو", 8: "أغسطس", 9: "سبتمبر",
              10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"}
# python weekday(): 0 = Monday
_WEEKDAYS_AR = {0: "الاثنين", 1: "الثلاثاء", 2: "الأربعاء", 3: "الخميس",
                4: "الجمعة", 5: "السبت", 6: "الأحد"}

_MONTHS_LOOKUP_AR = {_normalize_ar(v): k for k, v in _MONTHS_AR.items()}
_MONTHS_LOOKUP_AR[_normalize_ar("اثنين")] = None  # guard, see weekdays
del _MONTHS_LOOKUP_AR[_normalize_ar("اثنين")]
_WEEKDAYS_LOOKUP_AR = {}
for _i, _w in _WEEKDAYS_AR.items():
    _name = _normalize_ar(_w)  # e.g. "الجمعه" (article + bare noun)
    _bare = _name[2:]  # drop the "ال" article -> "جمعه"
    _WEEKDAYS_LOOKUP_AR[_name] = _i
    _WEEKDAYS_LOOKUP_AR[_bare] = _i  # without the article
    # ب/ل proclitics fused onto the article: "بالجمعة" (on Friday),
    # "للجمعة" (for/until Friday). With ل the article's alif elides
    # (li + al -> lil), so build it from the bare noun.
    _WEEKDAYS_LOOKUP_AR["ب" + _name] = _i
    _WEEKDAYS_LOOKUP_AR["لل" + _bare] = _i

_HOUR_LOOKUP_AR = {}
for _n, _name in _HOUR_NAMES_AR.items():
    if _n <= 10:
        _HOUR_LOOKUP_AR[_normalize_ar(_name)] = _n


def _fem_cardinal_ar(number):
    """1-99 in the feminine forms used for counting feminine nouns."""
    if number <= 10:
        return _ONES_FEM_AR[number]
    if number in _FEM_TEENS_AR:
        return _FEM_TEENS_AR[number]
    if number < 20:
        return _ONES_FEM_AR[number - 10] + " عشرة"
    tens, unit = divmod(number, 10)
    if unit == 0:
        return _TENS_AR[tens * 10]
    return _ONES_FEM_AR[unit] + " و" + _TENS_AR[tens * 10]


# Arabic Without Walls, the same note: "For minute quantities from three to
# ten, the plural دقائق is used ... For quantities above ten, the singular
# دقيقة is used".
def _nice_minutes_ar(minutes):
    """Minutes with the gender-polarity agreement of دقيقة (feminine)."""
    if minutes == 1:
        return "دقيقة"
    if minutes == 2:
        return "دقيقتان"
    if minutes <= 10:
        return _fem_cardinal_ar(minutes) + " دقائق"
    return _fem_cardinal_ar(minutes) + " دقيقة"


def nice_time_ar(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format in Modern Standard Arabic.

    Uses the feminine hour names after "الساعة" with half-past semantics:
    9:30 is "الساعة التاسعة والنصف", 8:45 is "الساعة التاسعة إلا ربعاً".

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
    Returns:
        (str): The formatted time string
    """
    if use_24hour:
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            string = dt.strftime("%I:%M %p")
        else:
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # strip leading zeros

    if not speech:
        return string

    if use_24hour:
        speak = pronounce_number_ar(dt.hour)
        if dt.minute:
            speak += " و" + _nice_minutes_ar(dt.minute)
        return speak

    if dt.hour == 0 and dt.minute == 0:
        return "منتصف الليل"
    if dt.hour == 12 and dt.minute == 0:
        # Arabic Wikipedia, "نظام 12 ساعة": "الثانية عشرة ظهراً (12PM)".
        return "الساعة الثانية عشرة ظهراً" if use_ampm else "الظهر"

    hour = dt.hour % 12 or 12
    # "All The Arabic You Never Learned The First Time Around", "How to Tell
    # Time": "إلاّ is used before رُبع and ثُلث to express the equivalent of
    # 'quarter to' the hour or 'twenty minutes' to the hour. When preceded by
    # إلاّ these words are in the indefinite accusative." (الساعة العاشرة إلا
    # ثُلثاً). https://allthearabicyouneverlearnedthefirsttimearound.com/p3/how-to-tell-time/
    if dt.minute in _TO_THE_HOUR_AR:
        next_hour = (dt.hour + 1) % 12 or 12
        speak = ("الساعة " + _HOUR_NAMES_AR[next_hour] + " "
                 + _TO_THE_HOUR_AR[dt.minute])
    else:
        speak = "الساعة " + _HOUR_NAMES_AR[hour]
        if dt.minute == 15:
            speak += " والربع"
        elif dt.minute == 20:
            speak += " والثلث"
        elif dt.minute == 30:
            speak += " والنصف"
        elif dt.minute:
            speak += " و" + _nice_minutes_ar(dt.minute)

    if use_ampm:
        speak += " مساءً" if dt.hour >= 12 else " صباحاً"
    return speak


def _count_unit_ar(count, singular, dual, plural, feminine):
    """A counted noun with Arabic number agreement.

    1 and 2 use the bare singular/dual, 3-10 take the plural with the
    polarity-opposed numeral, 11+ take the singular. The reverse gender
    polarity of 3-10 follows Wright, "A Grammar of the Arabic Language"
    Vol. I §319: the numeral takes the gender opposite the counted noun."""
    if count == 1:
        return singular
    if count == 2:
        return dual
    number = _fem_cardinal_ar(count) if feminine \
        else pronounce_number_ar(count)
    if 3 <= count <= 10:
        return f"{number} {plural}"
    return f"{number} {singular}"


def nice_duration_ar(duration, speech=True):
    """Convert duration in seconds to a nice spoken timespan in Arabic.

    Examples:
       duration = 60  ->  "1:00" or "دقيقة"
       duration = 163  ->  "2:43" or "دقيقتان وثلاث وأربعون ثانية"

    Args:
        duration: time, in seconds, or a timedelta
        speech (bool): format for speech (True) or display (False)

    Returns:
        str: timespan as a string
    """
    if isinstance(duration, timedelta):
        duration = duration.total_seconds()
    duration += 0.5  # traditional rounding

    days = int(duration // 86400)
    hours = int(duration // 3600 % 24)
    minutes = int(duration // 60 % 60)
    seconds = int(duration % 60)

    if not speech:
        out = ""
        if days > 0:
            out = str(days) + "d "
        if hours > 0 or days > 0:
            out += str(hours) + ":"
        if minutes < 10 and (hours > 0 or days > 0):
            out += "0"
        out += str(minutes) + ":"
        if seconds < 10:
            out += "0"
        out += str(seconds)
        return out

    parts = []
    if days > 0:
        parts.append(_count_unit_ar(days, "يوم", "يومان", "أيام", False))
    if hours > 0:
        parts.append(_count_unit_ar(hours, "ساعة", "ساعتان", "ساعات", True))
    if minutes > 0:
        parts.append(_count_unit_ar(minutes, "دقيقة", "دقيقتان", "دقائق",
                                    True))
    if seconds > 0:
        # 3-10 seconds use the broken plural ثوان with a feminine numeral
        if seconds == 1:
            parts.append("ثانية")
        elif seconds == 2:
            parts.append("ثانيتان")
        elif seconds <= 10:
            parts.append(f"{_fem_cardinal_ar(seconds)} ثوان")
        else:
            parts.append(f"{_fem_cardinal_ar(seconds)} ثانية")
    return " و".join(parts)


