"""
core_logic/sign_strength.py
===========================
The Jaimini strength rules (docs/SOURCES.md section 7):

* ``rasi_drishti``  - sign a aspects sign b (a sign "aspects" itself): BPHS 8.1-5.
* ``stronger_co_lord`` - the lord of Scorpio (Mars / Ketu) and Aquarius (Saturn / Rahu) in a divisional chart:
  PVR 15.5.1 (the stronger co-lord); the co-lordship itself BPHS 47.34-39.
* ``stronger_sign`` - the stronger of two signs: PVR 15.5.2, the rules taught from the Jaimini Upadesa Sutras.
* ``bhava_arudhas`` - the arudhas of the 12 houses of a divisional chart (BPHS 29.1-5) with the defaults
  NodesInArudhas=1 (co-lords resolved) and ExceptionsInBhavaArudhas=1.

Points are indexed as in the chart object: 0 Lagna, 1 Sun .. 7 Saturn, 8 Rahu, 9 Ketu.  ``signs`` lists the
sign (0 = Aries) of points 0..9 in the divisional chart; ``rasi_lons`` their rasi (D-1) longitudes.
"""
import contextlib
import contextvars
from typing import Callable, List, Sequence

SIGN_LORDS = [3, 6, 4, 2, 1, 4, 6, 3, 5, 7, 7, 5]       # natural lords (BPHS 4.6-24), point indices
EXALTATION = [12, 0, 1, 9, 5, 3, 11, 6, 2, 8]            # exaltation signs by point (BPHS 3.49-50; Rahu Gemini, Ketu
DEBILITATION = [12, 6, 7, 3, 11, 9, 5, 0, 8, 2]          # Sagittarius until set_nodal_exaltation), the 7th of them
MOOLATRIKONA = [12, 4, 1, 0, 5, 8, 6, 10, 5, 11]         # moolatrikona signs (BPHS 3.51-54; the nodes BPHS 47.34-39)


def set_nodal_exaltation(parasara: bool) -> None:
    """INI NodalExaltationParasara: Rahu / Ketu exalted in Taurus / Scorpio (debilitated in Scorpio / Taurus; BPHS
    47.34-39) instead of Gemini / Sagittarius. It changes the shared tables in place, so every engine that reads
    them follows."""
    # shortcut: process-wide tables; pass a per-call option if charts with both settings must coexist
    EXALTATION[8], EXALTATION[9] = (1, 7) if parasara else (2, 8)
    DEBILITATION[8], DEBILITATION[9] = (7, 1) if parasara else (8, 2)
_LORDS_13 = SIGN_LORDS + [0]   # Sudasa can pass "sign 12"; it then reads the next table's first entry (0)
_PAIR_SIGN = {7: 10, 8: 10, 3: 7, 9: 7}                  # Saturn / Rahu own Aquarius, Mars / Ketu Scorpio


def rasi_drishti(a: int, b: int) -> bool:
    """Whether sign ``a`` aspects sign ``b`` by rasi drishti (movable <-> fixed except the adjacent one,
    dual <-> dual); a sign counts as aspecting itself."""
    if a == b:
        return True
    if a % 3 == 2:
        return b % 3 == 2
    if (a % 3 == 0 and b % 3 == 1) or (a % 3 == 1 and b % 3 == 0):
        return (a + 1) % 12 != b and (b + 1) % 12 != a
    return False


def _aspect_score(sign: int, signs: Sequence[int]) -> int:
    """PVR 15.5.2 rule 2: aspects on a sign from Mercury, Jupiter and its lord (for Scorpio /
    Aquarius the node co-lord when the lord does not aspect)."""
    score = int(rasi_drishti(sign, signs[4])) + int(rasi_drishti(sign, signs[5]))
    if rasi_drishti(sign, signs[_LORDS_13[sign]]):
        return score + 1
    if sign == 7:
        return score + int(rasi_drishti(7, signs[9]))
    if sign == 10:
        return score + int(rasi_drishti(10, signs[8]))
    return score


def stronger_co_lord(a: int, b: int, signs: Sequence[int], rasi_lons: Sequence[float]) -> int:
    """The stronger of the two co-lords ``a``, ``b`` ((7, 8) for Aquarius, (3, 9) for Scorpio)."""
    own_a, own_b = _PAIR_SIGN[a], _PAIR_SIGN[b]
    sa, sb = signs[a], signs[b]
    if sa == own_a:
        if sb != own_b:
            return b                      # one co-lord in the sign: the other one rules it
    elif sb == own_b:
        return a
    grahas = signs[1:10]
    na, nb = grahas.count(sa), grahas.count(sb)
    if na != nb:
        return a if na > nb else b
    xa, xb = _aspect_score(sa, signs), _aspect_score(sb, signs)
    if xa != xb:
        return a if xa > xb else b
    ea, eb = EXALTATION[a] == sa, EXALTATION[b] == sb
    if ea != eb:
        return a if ea else b
    da, db = DEBILITATION[a] == sa, DEBILITATION[b] == sb
    if da != db:
        return b if da else a
    if sa % 3 != sb % 3:
        return a if sa % 3 > sb % 3 else b   # dual > fixed > movable
    deg_a, deg_b = rasi_lons[a] % 30.0, rasi_lons[b] % 30.0
    if a in (8, 9):
        deg_a = 30.0 - deg_a
    if b in (8, 9):
        deg_b = 30.0 - deg_b
    return b if deg_a < deg_b else a


def _deg(p: int, rasi_lons: Sequence[float]) -> float:
    """Degrees of point ``p`` in its rasi sign, counted backwards for the nodes."""
    d = rasi_lons[p] % 30.0
    return 30.0 - d if p in (8, 9) else d


def _sign_count(lord_sign: int, own: int, p: int) -> int:
    """The dasa years of a sign (PVR 18, Narayana dasa; the co-lord step of ``stronger_co_lord_dasa``): signs from
    ``own`` to ``lord_sign`` (forward for Ar..Ge, Li..Sg; backward for the others), 1..12, +1 if ``p`` is exalted
    there, -1 if debilitated."""
    n = (lord_sign - own if (own // 3) % 2 == 0 else own - lord_sign) % 12 or 12
    if EXALTATION[p] == lord_sign and n < 12:
        n += 1
    if DEBILITATION[p] == lord_sign and n > 0:
        n -= 1
    return n


def stronger_co_lord_dasa(a: int, b: int, signs: Sequence[int]) -> int:
    """The co-lord ((7, 8) Aquarius, (3, 9) Scorpio) the rasi dasas use (PVR 15.5.1 with its rule 5a: on a tie,
    the one giving the longer dasa)."""
    own_a, own_b = _PAIR_SIGN[a], _PAIR_SIGN[b]
    sa, sb = signs[a], signs[b]
    if sa == own_a:
        if sb != own_b:
            return b
    elif sb == own_b:
        return a
    grahas = signs[1:10]
    na, nb = grahas.count(sa), grahas.count(sb)
    if na != nb:
        return a if na > nb else b
    xa, xb = _aspect_score(sa, signs), _aspect_score(sb, signs)
    if xa != xb:
        return a if xa > xb else b
    ea, eb = EXALTATION[a] == sa, EXALTATION[b] == sb
    if ea != eb:
        return a if ea else b
    da, db = DEBILITATION[a] == sa, DEBILITATION[b] == sb
    if da != db:
        return b if da else a
    if sa % 3 != sb % 3:
        return a if sa % 3 > sb % 3 else b
    return b if _sign_count(sa, own_a, a) < _sign_count(sb, own_b, b) else a


# What the rasi dasas' Options type over the chart's strength tables: "aq", "sc" the co-lords,
# "start" the sign the dasas start from, "start_exception", and per pair (Ar/Li .. Vi/Pi) "stronger" (0 first, 1 second, None computed) and "exception" (0, 1 Saturn, 2 Ketu, None computed)
_TYPED = contextvars.ContextVar("sign_strength_typed", default=None)


@contextlib.contextmanager
def typed_strengths(typed):
    token = _TYPED.set(typed)
    try:
        yield
    finally:
        _TYPED.reset(token)


def typed_start():
    t = _TYPED.get()
    return t.get("start") if t else None


def dasa_sign_lord(sign: int, signs: Sequence[int]) -> int:
    """The lord of a sign for the rasi dasas: the natural lord, the Aquarius / Scorpio co-lord by
    ``stronger_co_lord_dasa``."""
    t = _TYPED.get()
    if t and sign in (10, 7) and t.get("aq" if sign == 10 else "sc") is not None:
        return t["aq" if sign == 10 else "sc"]
    if sign == 10:
        return stronger_co_lord_dasa(7, 8, signs)
    if sign == 7:
        return stronger_co_lord_dasa(3, 9, signs)
    return _LORDS_13[sign]


def stronger_sign(a: int, b: int, signs: Sequence[int], rasi_lons: Sequence[float], rule: str = "A") -> int:
    """The stronger of signs ``a`` and ``b`` (``a`` on a tie; PVR 15.5.2).  A: more grahas, aspects
    (``_aspect_score``), more exalted, fewer debilitated, lord in a sign of the other parity, dual > fixed >
    movable, lord further in its sign.  B moves the aspect rule after debilitation (the order some rasi dasas
    use); callers pick the rule."""
    grahas = signs[1:10]
    na, nb = grahas.count(a), grahas.count(b)
    if na != nb:
        return a if na > nb else b
    rules = [lambda s: _aspect_score(s, signs),
             lambda s: sum(1 for p in range(1, 10) if signs[p] == s and EXALTATION[p] == s),
             lambda s: -sum(1 for p in range(1, 10) if signs[p] == s and DEBILITATION[p] == s)]
    if rule == "B":
        rules = rules[1:] + rules[:1]
    for f in rules:
        fa, fb = f(a), f(b)
        if fa != fb:
            return a if fa > fb else b
    la, lb = dasa_sign_lord(a, signs), dasa_sign_lord(b, signs)
    pa, pb = signs[la] % 2 != a % 2, signs[lb] % 2 != b % 2
    if pa != pb:
        return b if pb else a
    if a % 3 != b % 3:
        return a if a % 3 > b % 3 else b
    return b if _deg(la, rasi_lons) < _deg(lb, rasi_lons) else a


def stronger_by_dignity(p: int, q: int, signs: Sequence[int], rasi_lons: Sequence[float]) -> int:
    """The stronger of two grahas by dignity (PVR 15.5): exalted, not debilitated, moolatrikona, own sign, then further in
    its sign (``p`` on a tie)."""
    sp, sq = signs[p], signs[q]
    for table, good in ((EXALTATION, True), (DEBILITATION, False), (MOOLATRIKONA, True)):
        ip, iq = table[p] == sp, table[q] == sq
        if ip != iq:
            return p if ip == good else q
    op, oq = owns_sign(p, sp), owns_sign(q, sq)
    if op != oq:
        return p if op else q
    return q if _deg(p, rasi_lons) < _deg(q, rasi_lons) else p


def stronger_own_sign(p: int, signs: Sequence[int], rasi_lons: Sequence[float]) -> int:
    """The stronger (rule A) of a planet's two own signs (BPHS 29.6-7: "consider the stronger"); Sun / Moon / the
    nodes have one (Rahu Aquarius, Ketu Scorpio)."""
    a, b = (12, 4, 3, 0, 5, 8, 6, 10, 10, 7)[p], (12, 4, 3, 7, 2, 11, 1, 9, 10, 7)[p]
    return a if a == b else stronger_sign(a, b, signs, rasi_lons)


def stronger_for_sthira(p: int, q: int, signs: Sequence[int], rasi_lons: Sequence[float]) -> int:
    """The sthira karaka pick of the Parasara chara karaka scheme (Moon / Mars and Sun / Venus): more grahas in its sign,
    exalted, not debilitated, moolatrikona, own sign, further in its sign (nodes counted back); ``p`` on a tie."""
    sp, sq = signs[p], signs[q]
    np_, nq = signs[1:10].count(sp), signs[1:10].count(sq)
    if np_ != nq:
        return p if np_ > nq else q
    for table, good in ((EXALTATION, True), (DEBILITATION, False), (MOOLATRIKONA, True)):
        ip, iq = table[p] == sp, table[q] == sq
        if ip != iq:
            return p if ip == good else q
    op, oq = owns_sign(p, sp), owns_sign(q, sq)
    if op != oq:
        return p if op else q
    return q if _deg(p, rasi_lons) < _deg(q, rasi_lons) else p


def owns_sign(p: int, sign: int) -> bool:
    """Natural lord (BPHS 4.6-24), Rahu co-owns Aquarius, Ketu Scorpio (BPHS 47.34-39)."""
    return SIGN_LORDS[sign] == p or (sign == 10 and p == 8) or (sign == 7 and p == 9)


def sort_signs(items: Sequence[int], signs: Sequence[int], rasi_lons: Sequence[float], rule: str = "A") -> List[int]:
    """Signs sorted strongest first (stable insertion sort by ``stronger_sign``)."""
    out: List[int] = []
    for s in items:
        k = 0
        while k < len(out) and stronger_sign(out[k], s, signs, rasi_lons, rule) != s:
            k += 1
        out.insert(k, s)
    return out


def planets_in_sign(sign: int, signs: Sequence[int], rasi_lons: Sequence[float]) -> List[int]:
    """The grahas in ``sign``, strongest first by ``stronger_by_dignity``."""
    out: List[int] = []
    for p in range(1, 10):
        if signs[p] != sign:
            continue
        k = 0
        while k < len(out) and stronger_by_dignity(out[k], p, signs, rasi_lons) != p:
            k += 1
        out.insert(k, p)
    return out


def stronger_of_7th(sign: int, signs: Sequence[int], rasi_lons: Sequence[float]) -> int:
    """The stronger of a sign and its 7th by rule A, evaluated as (s, s + 6) for s in Aries .. Virgo."""
    s = sign % 6
    t = _TYPED.get()
    if t and t.get("stronger") and t["stronger"][s] is not None:
        return s + 6 * t["stronger"][s]
    return stronger_sign(s, s + 6, signs, rasi_lons)


def direction_override(sign: int, signs: Sequence[int], rasi_lons: Sequence[float]) -> int:
    """The rasi dasa direction exception (PVR 18, Narayana dasa): 1 if Saturn is in the sign (forward), 2 if Ketu
    (reversed), Saturn and Ketu together by ``stronger_by_dignity``; 0 otherwise."""
    t = _TYPED.get()
    if t:
        if sign == t.get("start") and t.get("start_exception") is not None:
            return t["start_exception"]
        if t.get("exception") and t["exception"][sign % 6] is not None:
            return t["exception"][sign % 6]
    sat, ket = signs[7] == sign, signs[9] == sign
    if sat and ket:
        return 2 if stronger_by_dignity(7, 9, signs, rasi_lons) == 9 else 1
    return 1 if sat else 2 if ket else 0


def sign_lord(sign: int, signs: Sequence[int], rasi_lons: Sequence[float]) -> int:
    """Lord of a sign in a divisional chart, Scorpio / Aquarius resolved by ``stronger_co_lord``."""
    t = _TYPED.get()
    if t and sign in (10, 7) and t.get("aq" if sign == 10 else "sc") is not None:
        return t["aq" if sign == 10 else "sc"]
    if sign == 10:
        return stronger_co_lord(7, 8, signs, rasi_lons)
    if sign == 7:
        return stronger_co_lord(3, 9, signs, rasi_lons)
    return SIGN_LORDS[sign]


def longitude_bhava_arudhas(base_lon: float, lord_lon: Callable[[int], float], exceptions: bool = True,
                            reverse: bool = False) -> List[float]:
    """Longitude-based arudhas of houses 1..12 (LongitudeBasedBhavaArudhas=1; BPHS 29.1-5 by degrees): house i starts at the
    base point (ArudhaBasePlanet) + 30 i degrees (- 30 i for ``reverse``, a node as the base); twice the arc to the
    sign's lord (``lord_lon(sign)``, its longitude in the chart used); an arc within 15 deg of 0 or 180 moves on 270."""
    out = []
    for i in range(12):
        start = (base_lon - 30.0 * i if reverse else base_lon + 30.0 * i) % 360.0
        arc = 2.0 * ((lord_lon(int(start // 30.0)) - start) % 360.0) % 360.0
        if exceptions and (arc >= 345.0 or arc < 15.0 or 165.0 <= arc < 195.0):
            arc += 270.0
        out.append((arc + start) % 360.0)
    return out


def graha_arudha(planet: int, signs: Sequence[int], rasi_lons: Sequence[float], exceptions: bool = True) -> int:
    """Graha arudha of point ``planet`` (1 Sun .. 9 Ketu) in this divisional chart (BPHS 29.6-7):
    twice the stronger own sign minus the planet's sign; the 1st / 7th exception
    (ExceptionsInGrahaArudhas, on by default)."""
    sign = signs[planet]
    arudha = (stronger_own_sign(planet, signs, rasi_lons) * 2 + 144 - sign) % 12
    if exceptions and (arudha - sign) % 6 == 0:
        arudha = (arudha + 141) % 12
    return arudha


def bhava_arudhas(signs: Sequence[int], rasi_lons: Sequence[float], exceptions: bool = True,
                  nodes: bool = True) -> List[int]:
    """Arudha signs of houses 1..12 (index 0 = Arudha Lagna) of a divisional chart (BPHS 29.1-5):
    twice the lord's sign minus the house sign; in the house itself or the 7th from it, 10 signs further.
    ``exceptions`` ExceptionsInBhavaArudhas; ``nodes`` NodesInArudhas (off: Mars and Saturn always own Sc and Aq)."""
    out = []
    for i in range(12):
        house = (signs[0] + i) % 12
        lord_sign = signs[sign_lord(house, signs, rasi_lons) if nodes else SIGN_LORDS[house]]
        arudha = (lord_sign * 2 + 144 - house) % 12
        if exceptions and (arudha - house) % 6 == 0:   # in the house or the 7th from it
            arudha = (arudha + 141) % 12
        out.append(arudha)
    return out
