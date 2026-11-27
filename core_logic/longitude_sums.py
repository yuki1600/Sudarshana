"""
core_logic/longitude_sums.py
==============================
The "Laghu Parasari" tab: sums of the longitudes of 1 .. 5 bodies (and optionally a lagna) within a division,
and the ages at which that sum repeats, as dasa-year dates.  A research aid "like simple progression techniques"
(the tab's own description), with no classical source (docs/SOURCES.md section 14: a convention).

* ``part_in_division``: a body's longitude inside its division, and the span it runs over;
* ``rows``: the six lists (1 body of 20, 2 of the 9 grahas, 2 of 20, 3 of 9, 4 of 9, 5 of 9);
* dates: birth + the age in dasa years of definition 3, the true sidereal solar year (``ephemeris.dasa_year_mapper``).

Points are the app's point indices (1 Sun .. 9 Ketu, 13 Bhava Lagna .. 19 Indu Lagna, 22 Dhooma .. 32 Gulika).
"""
from itertools import combinations
from typing import Callable, Dict, List, Optional, Tuple

from .varga_charts import MULTIPLIER

BODIES = (1, 2, 3, 4, 5, 6, 7, 8, 9, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32)   # the 9 grahas and 11 upagrahas
# the tab's choices: (bodies considered, how many are summed)
MODES = {0: (BODIES, 1), 1: (BODIES[:9], 2), 2: (BODIES, 2), 3: (BODIES[:9], 3), 4: (BODIES[:9], 4),
         5: (BODIES[:9], 5)}
# point names of the row labels (data/point_names.csv "english", indices 0 .. 32)
NAMES = ("Asc", "Sun", "Moon", "Mars", "Merc", "Jup", "Ven", "Sat", "Rah", "Ket", "Ura", "Nep", "Plu", "BL", "HL",
         "GL", "VGL", "PPL", "SL", "IL", "BB", "Ku", "Dhu", "Vya", "PaV", "ICh", "UpK", "Kal", "Mri", "APr", "YGh",
         "Mnd", "Glk")
ADDED_LAGNAS = {"Lagna": 0, "Bhava Lagna": 13, "Hora Lagna": 14, "Ghati Lagna": 15, "Vighati Lagna": 16,
                "Pranapada Lagna": 17, "Sree Lagna": 18, "Indu Lagna": 19}   # the lagna added, by its point index


def part_in_division(lon: float, varga: int = 0, count_signs: bool = True) -> Tuple[float, float]:
    """(value, span) of a longitude in the division with varga index ``varga``: counting signs
    (the tab's default) in a division other than D-1: parts of the sign gone (0 .. n, span n); otherwise
    (finding longitudes) the position inside the current part scaled to 0 .. 30 (span 30)."""
    w = 30.0 / MULTIPLIER[varga]
    if count_signs and varga != 0:
        s = int(lon * 0.03333333333333333)
        return (lon - s * 30.0) / w, float(MULTIPLIER[varga])
    k = int(lon / w)
    return (lon - k * w) * 30.0 / w, 30.0


def label(combo, added: Optional[int] = 0) -> str:
    """Row label: the added lagna first, then the bodies, joined by '-' (e.g. "Asc-Sun")."""
    return "-".join(NAMES[p] for p in ((added,) if added is not None else ()) + tuple(combo))


def rows(lons: Dict[int, float], to_date: Callable[[float], object], mode: int = 0,
         added: Optional[int] = 0, varga: int = 0, count_signs: bool = True) -> List[Tuple[Tuple[int, ...], list]]:
    """The view's rows: (bodies, [(age, date), ...]) for every combination of ``mode`` (MODES).  ``lons``:
    longitudes by point index; ``added``: the lagna point added to each sum (None = none; default the lagna);
    ``to_date``: years since birth -> date (dasa year definition 3).  Ages: the sum folded into [0, span), then
    + span per column; trunc(120 / span + 0.5) columns."""
    pool, k = MODES[mode]
    span = part_in_division(0.0, varga, count_signs)[1]
    ncol = int(120.0 / span + 0.5)
    out = []
    for combo in combinations(pool, k):
        v = sum(part_in_division(lons[p], varga, count_signs)[0] for p in combo)
        if added is not None:
            v += part_in_division(lons[added], varga, count_signs)[0]
        while v >= span:
            v -= span
        while v < 0.0:
            v += span
        out.append((combo, [(v + i * span, to_date(v + i * span)) for i in range(ncol)]))
    return out
