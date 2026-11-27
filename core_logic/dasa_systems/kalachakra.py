"""kalachakra: part of dasa_systems (split from one module; see __init__.py)."""
from typing import Any, Callable, Dict, List, Tuple
from .. import sign_strength as S
from .chart import JChart, periods

# per pada) and the pada -> row table (one option gives every pada the row (pada % 24) * 9)
KALACHAKRA_YEARS = [7, 16, 9, 21, 5, 9, 16, 7, 10, 4, 4, 10]
_KC_A, _KC_B = list(range(12)), [7, 6, 5, 3, 4, 2, 1, 0, 11, 10, 9, 8]
_KC_C, _KC_D = [8, 9, 10, 11, 0, 1, 2, 4, 3, 5, 6, 7], [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
KALACHAKRA_SIGNS = (_KC_A + _KC_B) * 4 + _KC_A + _KC_C + _KC_D + _KC_C + _KC_D + _KC_C + _KC_D + _KC_D + _KC_C + _KC_D
PADA = 360.0 / 108.0


def kalachakra_pada(index: int) -> int:
    """The nakshatra pada (0 .. 107) a Kalachakra table entry is labelled with."""
    if index < 108:
        return index
    return 179 - index if index < 180 else 287 - index


def _kc_wrap(e: int, half: int) -> int:
    """Entry ``e`` kept in the savya (0 .. 107) or apasavya (108 .. 215) half of entry ``half``."""
    return e % 108 + (108 if half >= 108 else 0)


def _kc_table_row(e: int, rohini_4_leo: bool = True) -> int:
    """The pada table's row of pada ``e`` (BPHS 46.52-95): off, Rohini's 4th pada and the next swap rows."""
    k = e % 24
    if not rohini_4_leo and k in (15, 16):
        k = 31 - k
    return k


def kalachakra_row(r: int, method: int = 5, rohini_4_leo: bool = True) -> List[int]:
    """The 9 entries below table entry ``r`` (the sub-period table of the Kalachakra builder, KalachakraDasaCalculation
    ``method``): 0 / 1 its own row from itself; 2 / 3 the next entries of its half; 4 .. 6 the row
    (r % 24) * 9, an apasavya entry (108 ..) the row of its savya mirror (179 - r, 287 - r from 180) backwards."""
    if method in (0, 1):
        return [(r % 9 + j) % 9 + r // 9 * 9 for j in range(9)]
    if method in (2, 3):
        return [_kc_wrap(r + j, r) for j in range(9)]
    if r < 108:
        return [_kc_table_row(r, rohini_4_leo) * 9 + j for j in range(9)]
    e = 179 - r if r < 180 else 287 - r
    return [_kc_table_row(e, rohini_4_leo) * 9 + 8 - j for j in range(9)]


def kalachakra_rule(p: Dict[str, Any], method: int = 5, rohini_4_leo: bool = True) -> List[Tuple[Dict[str, Any], float]]:
    """The sub-periods of table entry ``p["lord"]`` for ``sub_periods``: ``kalachakra_row``, in proportion to their
    years."""
    row = kalachakra_row(p["lord"], method, rohini_4_leo)
    tot = float(sum(KALACHAKRA_YEARS[KALACHAKRA_SIGNS[r]] for r in row))
    return [({"lord": r, "sign": KALACHAKRA_SIGNS[r]}, KALACHAKRA_YEARS[KALACHAKRA_SIGNS[r]] / tot) for r in row]


def sudarsana_rule(jc: JChart, varga: int = 0, ad_from_lord: bool = True) -> Callable[[Dict[str, Any]], List[Tuple[Dict[str, Any], float]]]:
    """``sub_periods`` rule of ``sudarsana_chakra_dasa``: the 12 signs, 1/12 each, each column forward from the sign
    of its sign's lord (``ad_from_lord`` off: from its own sign)."""
    sg = jc.signs[varga]
    start = (lambda s: sg[S.SIGN_LORDS[s]]) if ad_from_lord else (lambda s: s)
    return lambda p: [({k: (start(p[k]) + j) % 12 for k in ("lord", "moon", "sun")}, 1 / 12.0) for j in range(12)]


def kalachakra_dasa(jc: JChart, to_date, method: int = 5, rohini_4_leo: bool = True) -> List[Dict[str, Any]]:
    """Kalachakra dasa (BPHS 46.52-95).  KalachakraDasaCalculation=5 (default): from the Moon's pada, one mahadasa per
    pada with the years of its sign, balance of the pada.  1, 3, 4: the 9 entries from the first of the pada's
    row ((pada % 24) * 9) on, in its half, balance of the pada; 0, 2: the same, started where the Moon's elapsed part
    of the pada times the row's total (paramayush) falls, balance of that entry; 6: likewise, within the row.
    Antardasas: ``kalachakra_row`` of each, in proportion to their years.  ``lord`` is the table index; ``sign``
    its sign.  ``rohini_4_leo`` KCDRohini4NavamsaInLeo: see ``_kc_table_row``."""
    moon = jc.moon()
    p = int(moon / PADA) % 108
    elapsed = (moon % PADA) / PADA
    yrs = lambda e: float(KALACHAKRA_YEARS[KALACHAKRA_SIGNS[e]])  # noqa: E731
    if method == 5:
        idx, bal = [(p + i) % 108 for i in range(9)], 1 - elapsed
    else:
        e0 = _kc_table_row(p, rohini_4_leo) * 9
        step = (lambda k: e0 // 9 * 9 + (e0 + k) % 9) if method == 6 else (lambda k: _kc_wrap(e0 + k, e0))
        k, bal = 0, 1 - elapsed
        if method in (0, 2, 6):
            rem = elapsed * sum(yrs(e0 // 9 * 9 + j) for j in range(9))
            while k < 8 and rem >= yrs(step(k)):
                rem -= yrs(step(k))
                k += 1
            bal = (yrs(step(k)) - rem) / yrs(step(k))
        idx = [step(k + i) for i in range(9)]
    ys = [yrs(e) for e in idx]
    out = periods(to_date, idx, ys, -(1 - bal) * ys[0])
    for md in out:
        md["sign"] = KALACHAKRA_SIGNS[md["lord"]]
        a, md["antardasas"] = md["t"], []
        for ad, w in kalachakra_rule(md, method, rohini_4_leo):
            ay = md["years"] * w
            md["antardasas"].append(dict(ad, start=to_date(a), end=to_date(a + ay), years=ay, t=a))
            a += ay
    return out
