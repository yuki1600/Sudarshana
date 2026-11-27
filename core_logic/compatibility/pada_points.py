"""pada_points: part of compatibility (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Dict, List, Tuple, Any
from ..natal_chart import NAKSHATRA_NAMES, RASI_NAMES_EN
from .matching import evaluate_horoscope_matching

# ---------------------------------------------------------------------------
# The "Horoscope Matching Score": the eight kutas' points (MC, Vivaha prakarana) tabulated once for every pair of Moons
# ---------------------------------------------------------------------------
# A precomputed 36 x 36 table of points (of 36): the 36 nakshatra / rasi parts (27 nakshatras, 9 of them split
# where the rasi changes), each pada of each nakshatra mapped to its part (nakshatra x 4 + pada).
PADA_MATCH_PART = [0, 0, 0, 0, 1, 1, 1, 1, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13, 14, 15, 15, 15, 16, 16, 16, 16, 17, 17, 18, 18, 19, 19, 19, 19, 20, 20, 20, 21, 22, 22, 22, 22, 23, 23, 23, 23, 24, 24, 24, 24, 25, 25, 25, 25, 26, 27, 27, 27, 28, 28, 28, 28, 29, 29, 30, 30, 31, 31, 31, 31, 32, 32, 32, 33, 34, 34, 34, 34, 35, 35, 35, 35]
PADA_MATCH_POINTS = [
    [28, 33, 28, 18, 21, 22, 26, 17, 18, 22, 31, 27, 21, 26, 17, 11, 9, 13, 22, 26, 22, 19, 26, 15, 13, 27, 24, 26, 24, 21, 21, 15, 16, 14, 24, 26],
    [34, 28, 29, 19, 22, 15, 18, 26, 26, 30, 23, 24, 21, 19, 28, 21, 19, 6, 14, 29, 22, 19, 17, 19, 20, 20, 27, 28, 26, 10, 10, 20, 24, 22, 16, 28],
    [27, 27, 28, 17, 9, 15, 19, 20, 21, 25, 26, 23, 17, 21, 22, 15, 15, 18, 27, 15, 19, 16, 20, 26, 24, 19, 14, 15, 10, 25, 25, 27, 19, 17, 19, 11],
    [18, 18, 19, 28, 19, 25, 16, 17, 18, 22, 23, 20, 19, 23, 24, 21, 21, 23, 22, 10, 14, 21, 25, 31, 20, 13, 9, 14, 10, 23, 29, 31, 23, 20, 22, 14],
    [23, 23, 10, 19, 28, 36, 27, 23, 23, 27, 26, 13, 12, 26, 28, 25, 26, 20, 19, 15, 9, 16, 30, 24, 14, 20, 11, 17, 18, 20, 26, 24, 30, 27, 26, 19],
    [22, 13, 15, 27, 34, 28, 20, 25, 23, 26, 19, 22, 21, 17, 25, 23, 27, 13, 10, 25, 17, 23, 22, 25, 15, 11, 18, 21, 24, 13, 19, 27, 29, 26, 17, 27],
    [27, 18, 21, 18, 25, 20, 28, 33, 31, 19, 10, 15, 24, 20, 28, 30, 34, 21, 14, 27, 19, 14, 11, 13, 23, 18, 24, 20, 25, 12, 13, 21, 23, 27, 17, 27],
    [19, 27, 21, 18, 24, 26, 34, 28, 25, 13, 20, 13, 23, 29, 22, 24, 24, 27, 20, 27, 20, 13, 17, 4, 16, 27, 27, 22, 22, 17, 18, 11, 16, 19, 27, 27],
    [19, 26, 22, 19, 23, 24, 32, 24, 28, 16, 23, 16, 22, 27, 21, 23, 24, 25, 18, 27, 21, 13, 20, 5, 13, 26, 27, 27, 23, 17, 18, 11, 17, 19, 27, 28],
    [21, 28, 23, 20, 24, 25, 19, 10, 14, 28, 35, 28, 15, 20, 14, 18, 18, 20, 20, 27, 20, 19, 26, 10, 8, 20, 21, 28, 27, 21, 12, 7, 11, 17, 25, 25],
    [30, 21, 26, 23, 24, 17, 10, 18, 21, 35, 28, 30, 18, 14, 23, 26, 27, 12, 11, 26, 21, 20, 19, 22, 17, 11, 22, 26, 25, 13, 4, 14, 18, 24, 18, 27],
    [25, 23, 22, 19, 12, 21, 13, 12, 15, 28, 28, 28, 15, 15, 17, 20, 20, 26, 25, 11, 16, 15, 20, 26, 22, 16, 8, 12, 13, 27, 18, 18, 12, 18, 20, 12],
    [21, 21, 17, 18, 11, 19, 22, 22, 21, 16, 18, 16, 28, 30, 26, 16, 16, 22, 25, 11, 17, 24, 26, 34, 24, 21, 11, 5, 4, 18, 24, 25, 18, 17, 18, 12],
    [27, 19, 21, 22, 25, 17, 20, 28, 27, 22, 16, 16, 30, 28, 34, 24, 22, 8, 11, 25, 19, 26, 24, 24, 19, 19, 27, 21, 18, 4, 11, 19, 24, 23, 16, 24],
    [18, 27, 22, 23, 27, 25, 28, 21, 21, 16, 25, 18, 26, 34, 28, 18, 16, 14, 17, 26, 17, 24, 32, 19, 10, 27, 28, 22, 20, 11, 18, 12, 16, 15, 26, 24],
    [13, 21, 16, 21, 25, 23, 30, 23, 23, 19, 28, 21, 17, 25, 19, 28, 25, 24, 16, 25, 16, 18, 27, 13, 15, 28, 29, 26, 25, 16, 16, 10, 14, 18, 29, 27],
    [11, 20, 16, 21, 26, 26, 33, 23, 23, 19, 28, 21, 17, 22, 17, 26, 28, 27, 19, 36, 17, 19, 26, 12, 14, 26, 27, 23, 24, 19, 19, 7, 14, 19, 27, 27],
    [13, 6, 19, 25, 20, 12, 19, 26, 24, 20, 12, 26, 23, 9, 15, 24, 27, 28, 20, 19, 26, 28, 11, 25, 28, 13, 21, 17, 19, 18, 18, 24, 18, 22, 11, 21],
    [22, 15, 28, 23, 20, 12, 13, 20, 18, 20, 12, 26, 25, 10, 17, 17, 20, 21, 28, 27, 34, 24, 7, 21, 28, 13, 21, 25, 27, 26, 20, 26, 20, 15, 4, 13],
    [27, 29, 17, 12, 16, 27, 27, 26, 26, 28, 28, 15, 13, 25, 25, 25, 27, 21, 28, 28, 20, 10, 23, 18, 23, 26, 18, 22, 23, 27, 21, 20, 25, 19, 20, 13],
    [22, 22, 20, 15, 10, 18, 19, 21, 21, 22, 21, 19, 17, 19, 18, 17, 18, 27, 34, 18, 28, 18, 17, 21, 28, 21, 13, 17, 17, 32, 26, 26, 22, 16, 13, 5],
    [16, 16, 14, 19, 14, 22, 13, 14, 14, 19, 18, 15, 21, 23, 21, 18, 19, 28, 23, 8, 17, 28, 27, 31, 23, 17, 9, 12, 12, 27, 27, 26, 22, 21, 18, 9],
    [24, 14, 19, 24, 27, 20, 11, 16, 21, 26, 18, 21, 24, 20, 29, 26, 27, 12, 7, 22, 17, 28, 28, 31, 16, 14, 22, 25, 26, 12, 12, 22, 24, 24, 18, 27],
    [12, 18, 24, 29, 22, 22, 13, 3, 6, 10, 20, 26, 31, 23, 16, 13, 12, 25, 20, 17, 20, 31, 30, 28, 15, 17, 17, 20, 20, 25, 25, 18, 11, 9, 21, 21],
    [12, 20, 24, 19, 13, 14, 21, 15, 12, 8, 17, 24, 25, 19, 9, 13, 13, 27, 27, 21, 27, 24, 26, 16, 28, 27, 25, 15, 15, 21, 25, 21, 11, 17, 25, 27],
    [27, 20, 19, 13, 20, 12, 18, 26, 26, 23, 13, 17, 21, 19, 27, 27, 26, 11, 11, 26, 19, 18, 18, 19, 27, 28, 34, 24, 23, 8, 15, 22, 29, 32, 23, 32],
    [25, 27, 14, 8, 11, 18, 24, 26, 26, 23, 24, 9, 11, 27, 28, 28, 27, 20, 20, 19, 12, 11, 25, 19, 25, 34, 28, 18, 15, 15, 22, 22, 28, 31, 32, 23],
    [28, 29, 16, 14, 17, 22, 20, 22, 22, 27, 28, 13, 6, 22, 23, 26, 25, 17, 24, 23, 16, 14, 28, 22, 16, 25, 19, 28, 25, 25, 17, 17, 23, 30, 32, 23],
    [27, 26, 13, 10, 17, 26, 23, 21, 23, 28, 26, 15, 17, 18, 20, 23, 25, 18, 25, 23, 16, 14, 28, 23, 17, 25, 15, 24, 28, 30, 20, 18, 23, 32, 31, 24],
    [20, 10, 26, 23, 20, 12, 8, 17, 17, 22, 13, 28, 18, 5, 12, 16, 18, 16, 24, 26, 30, 28, 14, 28, 21, 9, 16, 25, 21, 28, 18, 23, 21, 26, 15, 22],
    [20, 11, 26, 30, 27, 19, 10, 19, 19, 14, 5, 20, 25, 11, 19, 17, 21, 18, 19, 22, 25, 28, 12, 26, 29, 16, 13, 18, 21, 20, 28, 33, 28, 18, 7, 14],
    [15, 21, 28, 32, 25, 25, 18, 10, 10, 7, 15, 20, 26, 20, 13, 11, 8, 26, 26, 19, 26, 26, 21, 19, 22, 23, 23, 18, 18, 25, 33, 28, 19, 9, 17, 16],
    [18, 25, 20, 24, 31, 31, 24, 17, 17, 13, 20, 14, 19, 25, 17, 15, 17, 18, 19, 28, 21, 21, 27, 12, 15, 30, 29, 24, 25, 20, 27, 19, 28, 18, 23, 20],
    [14, 21, 16, 19, 26, 26, 25, 18, 18, 18, 25, 18, 16, 22, 14, 16, 18, 19, 12, 20, 14, 21, 27, 11, 15, 31, 30, 28, 30, 25, 17, 7, 16, 28, 33, 30],
    [24, 15, 18, 21, 25, 17, 16, 25, 27, 26, 19, 20, 17, 15, 25, 27, 26, 9, 3, 19, 12, 19, 20, 22, 24, 22, 31, 29, 29, 14, 6, 16, 21, 33, 28, 34],
    [25, 24, 11, 14, 17, 26, 25, 24, 25, 24, 27, 13, 12, 22, 22, 24, 26, 20, 13, 11, 5, 12, 27, 22, 27, 30, 21, 19, 22, 22, 14, 16, 18, 29, 33, 28]]


def pada_match_points(nak_a: int, pada_a: int, nak_b: int, pada_b: int, swap: bool = False) -> int:
    """The table's score for the Moons of two charts (nakshatra 0..26,
    pada 0..3): row = first chart's part, column = second's (swap, its first argument, exchanges them)."""
    a, b = PADA_MATCH_PART[nak_a * 4 + pada_a], PADA_MATCH_PART[nak_b * 4 + pada_b]
    return PADA_MATCH_POINTS[b][a] if swap else PADA_MATCH_POINTS[a][b]


def pada_match_level(points: int) -> str:
    """The level of a Horoscope Matching Score (the bands
    the bounds as its output shows them on 4 charts x 216 partners)."""
    return ("Excellent" if points >= 31 else "Good" if points >= 26 else "Fair" if points >= 22
            else "Average" if points >= 18 else "Below Average")


def moon_longitude_of(nak: int, pada: int) -> float:
    """Mid-pada Moon longitude for a nakshatra (0..26) and pada (0..3)."""
    return nak * (360.0 / 27.0) + pada * (10.0 / 3.0) + (10.0 / 6.0)


def match_from_padas(bride_nak: int, bride_pada: int, groom_nak: int, groom_pada: int) -> Dict[str, Any]:
    """Ashta Kuta breakdown + pada table score for a bride/groom Moon pada pair (no full charts)."""
    result = evaluate_horoscope_matching(
        {"moon_longitude": moon_longitude_of(bride_nak, bride_pada)},
        {"moon_longitude": moon_longitude_of(groom_nak, groom_pada)},
    )
    score = pada_match_points(bride_nak, bride_pada, groom_nak, groom_pada)
    result["pada_score"] = score
    result["pada_level"] = pada_match_level(score)
    result["bride_pada"] = bride_pada + 1
    result["groom_pada"] = groom_pada + 1
    return result


def match_parts() -> List[Dict[str, Any]]:
    """The 36 Moon parts of the table: a nakshatra pada-run that stays inside one rasi.
    Nine nakshatras that cross a sign boundary are split (e.g. Krittika Ar p1 vs Ta p2-4)."""
    SIGNS = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]
    buckets: Dict[int, List[Tuple[int, int]]] = {}
    for i, part in enumerate(PADA_MATCH_PART):
        buckets.setdefault(part, []).append(divmod(i, 4))
    out = []
    for part in range(36):
        slots = buckets[part]
        nak, first_pada = slots[0]
        mid = nak * (360.0 / 27.0) + first_pada * (10.0 / 3.0) + (10.0 / 6.0)
        sign = int(mid // 30.0)
        padas = [p + 1 for _, p in slots]
        out.append({
            "index": part,
            "nakshatra": nak,
            "nakshatra_name": NAKSHATRA_NAMES[nak],
            "pada": first_pada,                 # representative (0-based) for lookups
            "padas": padas,                     # 1-based pada numbers in this part
            "rasi": sign,
            "rasi_name": RASI_NAMES_EN[sign],
            "rasi_abbr": SIGNS[sign],
            "label": "%s · %s p%s" % (
                NAKSHATRA_NAMES[nak], SIGNS[sign],
                str(padas[0]) if len(padas) == 1 else "%d–%d" % (padas[0], padas[-1])),
        })
    return out


def match_matrix() -> Dict[str, Any]:
    """The 36×36 pada matching table: rows = bride part, columns = groom part (zodiac-split nakshatras)."""
    parts = match_parts()
    scores = [row[:] for row in PADA_MATCH_POINTS]
    return {"parts": parts, "scores": scores, "stars": list(NAKSHATRA_NAMES)}
