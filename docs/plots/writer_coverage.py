"""Plot which `nice_*` functions each writer language implements.

Run from the repository root:

    .venv/bin/python docs/plots/writer_coverage.py

It needs matplotlib (`uv pip install matplotlib`). The script calls each
`nice_*` function for each of the writer languages and records the result:
a function `nice_*_<code>` in the language module `dates_<code>.py` (for Bosnian
`nice_time`, the Croatian module `dates_hr.py`), the shared
writer that reads `res/<code>/*.json`, or `NotImplementedError`. It writes
docs/img/writer_coverage.png. With --table it prints the table and writes no
image. The table says `module`, `shared` or `missing` in each cell.
"""
import importlib
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

import ovos_date_parser as p
from ovos_date_parser.common import _WRITER_LANGS

logging.disable(logging.CRITICAL)

MISSING, SHARED, OWN = range(3)
LABELS = {OWN: "function in the language module", SHARED: "shared writer and res/ data",
          MISSING: "NotImplementedError"}
COLORS = ["#eeeeee", "#8ab17d", "#2a9d8f"]
TABLE_WORDS = {OWN: "module", SHARED: "shared", MISSING: "missing"}

WHEN = datetime(2024, 1, 5, 15, 30)
CALLS = {
    "nice_time": lambda code: p.nice_time(WHEN, code),
    "nice_date": lambda code: p.nice_date(WHEN, code),
    "nice_date_time": lambda code: p.nice_date_time(WHEN, code),
    "nice_day": lambda code: p.nice_day(WHEN, code),
    "nice_weekday": lambda code: p.nice_weekday(WHEN, code),
    "nice_month": lambda code: p.nice_month(WHEN, code),
    "nice_year": lambda code: p.nice_year(WHEN, code),
    "nice_duration": lambda code: p.nice_duration(3690, code),
    "nice_relative_time": lambda code: p.nice_relative_time(WHEN + timedelta(days=5), WHEN, code),
}


def state(name, call, code):
    """MISSING, SHARED or OWN for one function of one language."""
    try:
        call(code)
    except NotImplementedError:
        return MISSING
    owner = "hr" if name == "nice_time" and code == "bs" else code
    module = importlib.import_module(f"ovos_date_parser.dates_{owner}") \
        if (Path(p.__file__).parent / f"dates_{owner}.py").exists() else None
    return OWN if module is not None and hasattr(module, f"{name}_{owner}") else SHARED


def main():
    langs = sorted(_WRITER_LANGS)
    columns = list(CALLS)
    grid = [[state(name, call, code) for name, call in CALLS.items()] for code in langs]

    print("language", *columns, sep="\t")
    for code, row in zip(langs, grid):
        print(code, *(TABLE_WORDS[value] for value in row), sep="\t")
    if "--table" in sys.argv:
        return

    fig, axis = plt.subplots(figsize=(7.2, 11))
    axis.imshow(grid, cmap=ListedColormap(COLORS), vmin=0, vmax=2, aspect="auto")
    axis.set_xticks(range(len(columns)), columns, rotation=35, ha="right")
    axis.set_yticks(range(len(langs)), langs)
    axis.set_xticks([x - 0.5 for x in range(1, len(columns))], minor=True)
    axis.set_yticks([y - 0.5 for y in range(1, len(langs))], minor=True)
    axis.grid(which="minor", color="white", linewidth=1.5)
    axis.tick_params(which="minor", length=0)
    axis.set_title("Writer coverage, per language and function")
    axis.legend(handles=[Patch(color=COLORS[key], label=LABELS[key]) for key in sorted(LABELS, reverse=True)],
                loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False)
    out = Path(__file__).resolve().parent.parent / "img" / "writer_coverage.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")


if __name__ == "__main__":
    main()
