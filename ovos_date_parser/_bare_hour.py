"""The clock hour that stands before more words, with no mark to end it."""
from typing import Collection


def stands_alone(word: str, number: str, next_word: str, next_next_word: str,
                 day_parts: Collection[str], hour_word: str,
                 joiners: Collection[str]) -> bool:
    """True when ``word`` is the whole hour and the words after it add none.

    No mark is glued to the hour ("5pm\\""). The next word is a plain word,
    without a mark glued to it ("pm;"), and it is not a joiner ("y media"),
    a part of the day, or followed by one ("por la noche") or by a duration
    ("una hora antes"). Those continue the hour, and the engine's own rules
    for them apply.
    """
    return (word == number
            and next_word.isalpha()
            and next_word not in joiners
            and next_word not in day_parts
            and next_next_word not in day_parts
            and next_next_word != hour_word)
