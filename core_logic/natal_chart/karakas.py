"""karakas: part of natal_chart (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Dict, List, Sequence, Tuple

# ---------------------------------------------------------------------------
# Chara Karakas (Jaimini 7 & 8 Karaka Schemes)
# ---------------------------------------------------------------------------

def compute_chara_karakas(planets_deg_in_sign: Dict[str, float], use_8_karakas: bool = False) -> Dict[str, str]:
    """
    Computes Jaimini Chara Karakas sorted by degrees in sign in descending order:
    AK: Atmakaraka (Highest)
    AmK: Amatyakaraka
    BK: Bhratrikaraka
    MK: Matrikaraka
    PiK: Pitrikaraka (only in 8-karaka scheme)
    PK: Putrakaraka
    GK: Gnatikaraka
    DK: Darakaraka (Lowest)
    """
    valid_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    if use_8_karakas:
        valid_planets.append("Rahu")
        karaka_names = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]
    else:
        karaka_names = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
        
    filtered = [(p, planets_deg_in_sign.get(p, 0.0)) for p in valid_planets]
    sorted_planets = sorted(filtered, key=lambda x: x[1], reverse=True)
    
    res = {}
    for i, (p, deg) in enumerate(sorted_planets):
        if i < len(karaka_names):
            res[karaka_names[i]] = p
    return res

def chara_karaka_slots(rasi_lons: Sequence[float], signs: Sequence[int], definition: int = 0) -> List[int]:
    """The chara karakas (BPHS 32.1-17): the eight karaka slots AK, AmK, BK, MK, PiK, PK, GK, DK as point indices
    (1 Sun .. 8 Rahu; 0 = none), ``rasi_lons`` / ``signs`` of points 0 .. 9 (lagna first).
    CharaKarakaDefinition: 0 eight karakas with Rahu counted from the end of its sign (BPHS 32.3-8; default);
    1 seven, no PiK; 2 seven with the 5th as PiK and PK = MK; 3 Parasara: seven, but when two adjacent ranks share
    a whole degree Rahu joins and the later of each such pair takes the earlier one's rank while the earlier gets
    its sthira karaka (Mercury, Mars, Moon / Mars, Sun / Venus, Saturn, Mercury, Venus by rank)."""
    from ..sign_strength import stronger_for_sthira
    deg = [0.0] + [rasi_lons[p] - int(rasi_lons[p] / 30.0) * 30.0 for p in range(1, 8)]
    rahu = 30.0 - (rasi_lons[8] - int(rasi_lons[8] / 30.0) * 30.0)

    def ranked(points, value):
        out = []
        for p in points:
            k = next((i for i, o in enumerate(out) if value(o) < value(p)), len(out))
            out.insert(k, p)
        return out
    deg8 = deg + [rahu]
    if definition != 3:
        if definition == 0:
            return ranked(range(1, 9), lambda p: deg8[p])
        k = ranked(range(1, 8), lambda p: deg[p])
        return k[:4] + ([0, k[4]] if definition == 1 else [k[4], k[3]]) + k[5:7]
    k = ranked(range(1, 8), lambda p: deg[p])
    if not any(int(deg[k[i + 1]]) == int(deg[k[i]]) for i in range(6)):
        return k[:5] + [k[3], k[5], k[6]]                      # 7 karakas: PK = MK
    k = ranked(range(1, 9), lambda p: deg8[p])
    sthira = [4, 3, stronger_for_sthira(2, 3, signs, rasi_lons), stronger_for_sthira(1, 6, signs, rasi_lons), 7, 4, 6]
    for i in range(6):
        if int(deg8[k[i + 2]]) == int(deg8[k[i + 1]]):
            k[i + 2], k[i + 1] = k[i + 1], sthira[i]
    return k


def planetary_war(rasi_lons: Sequence[float]) -> Dict[int, Tuple[bool, bool]]:
    """The planetary-war list (Key Info "graha yuddha" view): for points 1 Sun .. 9 Ketu, (wins, loses): wins when it is 0..1
    deg ahead of another of them, loses when another is 0..1 deg ahead of it (the war within 1 deg of SS 7.19; the
    winner by longitude is a convention, docs/SOURCES.md section 2)."""
    out = {}
    for p in range(1, 10):
        others = [q for q in range(1, 10) if q != p]
        out[p] = (any((rasi_lons[p] - rasi_lons[q]) % 360.0 <= 1.0 for q in others),
                  any((rasi_lons[q] - rasi_lons[p]) % 360.0 <= 1.0 for q in others))
    return out


def is_combust_by_orbs(p: int, rasi_lons: Sequence[float], retrograde: Sequence[bool] = (),
                     by_motion: bool = True) -> bool:
    """Combustion by fixed orbs (a convention, docs/SOURCES.md section 2): Mars .. Saturn (points 3 .. 7)
    within 6 deg of the Sun either way; with ``by_motion`` (on by default) Mercury is not combust when retrograde
    and Venus only when retrograde."""
    if not 3 <= p <= 7:
        return False
    c = (rasi_lons[p] - rasi_lons[1]) % 360.0 <= 6.0 or (rasi_lons[1] - rasi_lons[p]) % 360.0 <= 6.0
    if by_motion and retrograde:
        if p == 4 and retrograde[4]:
            return False
        if p == 6 and not retrograde[6]:
            return False
    return c


# Surya Siddhanta's combustion orbs (SS 9.6-9, the Moon 10.1), degrees from the Sun, (direct, retrograde)
CLASSICAL_COMBUSTION = {2: (12.0, 12.0), 3: (17.0, 17.0), 4: (14.0, 12.0), 5: (11.0, 11.0), 6: (10.0, 8.0), 7: (15.0, 15.0)}


def is_combust(p: int, rasi_lons: Sequence[float], retrograde: Sequence[bool] = (), by_motion: bool = True, classical: bool = False) -> bool:
    """Combustion by the classical orbs (the Moon .. Saturn, the retrograde orb when retrograde, the edge included),
    or the fixed-orb rule (is_combust_by_orbs, ``by_motion`` its Mercury / Venus exception)."""
    if not classical:
        return is_combust_by_orbs(p, rasi_lons, retrograde, by_motion)
    if p not in CLASSICAL_COMBUSTION:
        return False
    orb = CLASSICAL_COMBUSTION[p][1 if p < len(retrograde) and retrograde[p] else 0]
    return abs((rasi_lons[p] - rasi_lons[1] + 180.0) % 360.0 - 180.0) <= orb
