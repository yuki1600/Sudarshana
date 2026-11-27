"""engine: part of shadbala (split from one module; see __init__.py)."""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Any
from .. import sign_strength as _SS
from ..utils import norm360
from ..natal_chart import get_graha_dignity, is_combust

# ===========================================================================
# The Shadbala of BPHS 27 (verse by part below);
# mean planets of cheshta bala from B. V. Raman's tables (Graha and Bhava Balas, epoch 1 Jan 1900, 76 deg E)
# ===========================================================================
_SEVEN_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
_SIGN_LORD_INDEX = (2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4)          # 0 = Sun .. 6 = Saturn
_DEBILITATION_POINT = (190.0, 213.0, 118.0, 345.0, 275.0, 177.0, 20.0)
_MT_RANGE = ((120.0, 140.0), (34.0, 50.0), (0.0, 12.0), (166.0, 170.0), (240.0, 250.0), (180.0, 195.0),
                (300.0, 320.0))                                   # moolatrikona ranges (BPHS 3.51-54; the Moon and Mercury by the option)
_MT_BPHS = False      # saptavargaja's rasi moolatrikona by BPHS's degrees (get_graha_dignity: the Moon 3-30 Taurus, Mercury 15-20 Virgo) instead


def set_moolatrikona_bphs(bphs: bool) -> None:
    """Which moolatrikona degrees shadbala_and_bhava_bala's saptavargaja uses; process-wide like sign_strength.set_nodal_exaltation."""
    global _MT_BPHS
    _MT_BPHS = bphs
_NATURAL = ((3, 1, 1, 0, 1, -1, -1), (1, 3, 0, 1, 0, 0, 0), (1, 1, 3, -1, 1, 0, 0), (1, -1, 0, 3, 0, 1, 0),
               (1, 1, 1, -1, 3, -1, 0), (-1, -1, 0, 1, 0, 3, 1), (-1, -1, -1, 1, 0, 1, 3))
_SAPTAVARGAJA = {-2: 1.875, -1: 3.75, 0: 7.5, 1: 15.0, 2: 22.5, 3: 30.0}
_NAISARGIKA = (60.0, 51.43, 17.14, 25.70, 34.28, 42.85, 8.57)   # the rounded values
_REQUIRED_RUPAS = (5.0, 6.0, 5.0, 7.0, 6.5, 5.5, 5.0)   # required rupas, B. V. Raman, Graha and Bhava Balas section 122
# (BPHS 27.32-33 gives the Sun 6.5: SHADBALA_REQUIREMENTS)
_DIG_OFFSET = (90.0, 270.0, 90.0, 180.0, 180.0, 270.0, 0.0)   # weakest point from the lagna
_KRANTI_CUM = (0.0, 362.0, 703.0, 1002.0, 1238.0, 1388.0)     # declination (arc-min) per 15 deg of bhuja
_KRANTI_DIFF = (362.0, 341.0, 299.0, 236.0, 150.0, 52.0)
_AYANA_SIGN = (1, -1, 1, 1, 1, 1, -1)
# cheshta (BPHS 27.24-25): (base, rate per day, add, per year) of the two mean longitudes of Mars .. Saturn, from
# Raman's tables (Graha and Bhava Balas: Sun 257.4568, Mars 270.22, Jupiter 220.04, Saturn 236.74 ... at the epoch)
_CHESHTA = (((257.4568, 0.98560265, 0.0, 0.0), (270.22, 0.524019, 0.0, 0.0)),
               ((164.0, 4.092318, 6.67, -0.00133), (257.4568, 0.98560265, 0.0, 0.0)),
               ((257.4568, 0.98560265, 0.0, 0.0), (220.04, 0.083096, -3.33, -0.0067)),
               ((328.51, 1.602146, -5.0, -0.001), (257.4568, 0.98560265, 0.0, 0.0)),
               ((257.4568, 0.98560265, 0.0, 0.0), (236.74, 0.033439, 5.0, 0.001)))
_SPECIAL_ASPECTS = {2: (90.0, 210.0), 4: (120.0, 240.0), 6: (60.0, 270.0)}


def _fold180(x: float) -> float:
    x = norm360(x)
    return 360.0 - x if x > 180.0 else x


def aspect_value(d: float, planet: int, full_curves: bool = True) -> float:
    """Aspect (BPHS 26.6-12) of a planet (1 = Sun .. 7 = Saturn) on a point ``d`` deg ahead, on a 0..100 scale.
    ``full_curves`` (default on) gives Mars / Jupiter / Saturn their own curves of BPHS 26.9-12
    curves; off, they add 15 / 30 / 45 in 30-deg special ranges."""
    d = norm360(d)
    if d >= 300.0:
        v = 0.0
    elif d >= 180.0:
        v = (300.0 - d) * 0.5
    elif d >= 150.0:
        v = (d - 150.0) * 2.0
    elif d >= 120.0:
        v = 150.0 - d
    elif d >= 90.0:
        v = (120.0 - d) * 0.5 + 30.0
    elif d >= 60.0:
        v = d - 60.0 + 15.0
    elif d >= 30.0:
        v = (d - 30.0) * 0.5
    else:
        v = 0.0
    if full_curves:
        if planet == 5:
            if 90.0 <= d < 120.0:
                v = (d - 90.0) * 0.5 + 45.0
            elif 120.0 <= d < 150.0:
                v = 60.0 - (d - 120.0) * 2.0
            elif 210.0 <= d < 240.0:
                v = (d - 210.0) * 0.5 + 45.0
            elif 240.0 <= d < 270.0:
                v = 60.0 - (d - 240.0) * 1.5
        elif planet == 3:
            if 60.0 <= d < 90.0:
                v = (d - 60.0) * 1.5 + 15.0
            elif 90.0 <= d < 120.0:
                v = 60.0 - (d - 90.0)
            elif 180.0 <= d < 210.0:
                return 100.0
            elif 210.0 <= d < 240.0:
                v = 60.0 - (d - 210.0)
        elif planet == 7:
            if 30.0 <= d < 60.0:
                v = (d - 30.0) * 2.0
            elif 60.0 <= d < 90.0:
                v = 60.0 - (d - 60.0) * 0.5
            elif 240.0 <= d < 270.0:
                v = d - 240.0 + 30.0
            elif 270.0 <= d < 300.0:
                v = (300.0 - d) * 2.0
    elif planet in (3, 5, 7):
        for lo in _SPECIAL_ASPECTS[planet - 1]:
            if lo <= d < lo + 30.0:
                v += {3: 15.0, 5: 30.0, 7: 45.0}[planet]
    return min(v, 60.0) * (5.0 / 3.0)


def _jh_days_since_1900(year: int, month: int, day: int, hour: float, longitude_west: float) -> Tuple[int, float]:
    """(whole years since 1900, days since 1900-01-01 counted from the place, with the +76 deg meridian of Raman's
    epoch). For years before 1900 only the days of the year are counted."""
    leap = lambda y: (y % 4 == 0 and y % 100 != 0) or y % 400 == 0  # noqa: E731
    days, y = 0.0, 1900
    while y < year:
        days += 366.0 if leap(y) else 365.0
        y += 1
    months = [31.0, 29.0 if leap(y) else 28.0, 31.0, 30.0, 31.0, 30.0, 31.0, 31.0, 30.0, 31.0, 30.0, 31.0]
    days += sum(months[:month - 1])
    return int(year - 1900), (day - 1.0) + days + ((longitude_west + 76.0) / 15.0 + hour) / 24.0


def shadbala_and_bhava_bala(lons: Dict[str, float], lagna_lon: float, varga_signs: Dict[str, List[int]], is_day: bool,
                   ghatis_since_sunrise: float, day_ghatis: float, night_ghatis: float, day_count: int,
                   year: int, month: int, day: int, hour_local: float, longitude_east: float) -> Dict[str, Any]:
    """
    Shadbala and Bhava Bala (BPHS 27). ``lons``: sidereal longitudes of Sun .. Saturn; ``varga_signs``: signs
    of Sun .. Saturn in "D1", "D2" (the default hora), "D3", "D7", "D9", "D12", "D30"; the day timings are
    the sunrise-based day (ghatis); ``day_count``: its weekday day number (ephemeris.day_lords); the date
    and local clock hour feed the mean planets of cheshta bala. Returns {"planets": {name: parts}, "bhavas": [..]}.
    """
    P = [lons[p] for p in _SEVEN_PLANETS]
    d1 = varga_signs["D1"]
    lagna_sign = int(norm360(lagna_lon) // 30.0)
    # natures for paksha / drig bala (BPHS 3.11): Moon by its distance from the Sun, Mercury by its associations
    moon_benefic = 1 if _fold180(P[1] - P[0]) >= 90.0 else -1
    nature = [-1, moon_benefic, -1, 0, 1, 1, -1]
    score, touched = 0.0, False
    for j in range(7):
        if j == 3:
            continue
        dd = norm360(P[3] - P[j])
        if dd <= 15.0 or dd >= 345.0:
            touched, score = True, score + nature[j]
        if 165.0 <= dd <= 195.0:
            touched, score = True, score + nature[j]
        for a in _SPECIAL_ASPECTS.get(j, ()):
            if a - 15.0 <= dd <= a + 15.0:
                touched, score = True, score + nature[j] * 0.75
    nature[3] = 1 if score >= 0.0 and (score != 0.0 or not touched) else -1
    # compound relationships from the rasi signs (BPHS 3.55-58)
    comp = [list(r) for r in _NATURAL]
    for a in range(7):
        for b in range(a + 1, 7):
            x = (d1[a] - d1[b]) % 12
            x = min(x, 12 - x)
            t = 1 if 0 < x < 4 else -1
            comp[a][b] += t
            comp[b][a] += t
    out = {}
    paksha = _fold180(P[1] - P[0]) / 3.0  # BPHS 27.10-11 (Moon's doubled below)
    natonnata = _fold180(lagna_lon - P[0] + 90.0) / 3.0  # BPHS 27.8-9
    years, days = _jh_days_since_1900(year, month, day, hour_local, -longitude_east)
    abda = (((day_count // 360) * 3 + 1) % 7 or 7) + 2
    masa = (((day_count // 30) * 2 + 1) % 7 or 7) + 2  # year and month lords: SS 1.51-52, BPHS 27.13
    vara = (day_count % 7 or 7) + 2
    abda, masa, vara = abda % 7, masa % 7, vara % 7
    hours = int(ghatis_since_sunrise * 24.0 / 60.0)
    hora = (6, 4, 2, 0, 5, 3, 1)[((3, 6, 2, 5, 1, 4, 0)[vara] + hours) % 7]  # the hora lord, BPHS 27.13
    if is_day:  # tribhaga, BPHS 27.12
        tri = (3, 0, 6)[int(ghatis_since_sunrise / (day_ghatis / 3.0)) % 3]
    else:
        tri = (1, 5, 2)[int((ghatis_since_sunrise - day_ghatis) / (night_ghatis / 3.0)) % 3]
    for p, name in enumerate(_SEVEN_PLANETS):
        lon = P[p]
        uchcha = _fold180(lon - _DEBILITATION_POINT[p]) / 3.0
        sapta = 0.0
        for v in ("D1", "D2", "D3", "D7", "D9", "D12", "D30"):
            if v == "D1" and (get_graha_dignity(name, lon) == "Moolatrikona" if _MT_BPHS else _MT_RANGE[p][0] <= lon <= _MT_RANGE[p][1]):
                sapta += 45.0
            else:
                sapta += _SAPTAVARGAJA[comp[p][_SIGN_LORD_INDEX[varga_signs[v][p]]]]
        pref = 1 if p in (1, 5) else 0
        # oja-yugma BPHS 27.4.5, kendra 27.5, drekkana 27.6
        oja = 15.0 * (d1[p] % 2 == pref) + 15.0 * (varga_signs["D9"][p] % 2 == pref)
        kendra = (60.0, 30.0, 15.0)[((d1[p] - lagna_sign) % 12) % 3]
        drekkana = 15.0 if varga_signs["D3"][p] == (d1[p] + (0, 8, 0, 4, 0, 8, 4)[p]) % 12 else 0.0
        sthana = uchcha + sapta + oja + kendra + drekkana  # BPHS 27.1-6
        dig = _fold180(lon - (_DIG_OFFSET[p] + lagna_lon)) / 3.0
        nat = {0: natonnata, 4: natonnata, 5: natonnata, 3: 60.0}.get(p, 60.0 - natonnata)
        pak = paksha if nature[p] >= 1 else 60.0 - paksha
        if p == 1:
            pak *= 2.0
        tribhaga = 60.0 if p in (4, tri) else 0.0
        x = norm360(lon + 23.0)
        bhuja = x if x <= 180.0 else 360.0 - x
        if bhuja > 90.0:
            bhuja = 180.0 - bhuja
        k = int(bhuja / 15.0)
        dec = ((bhuja - k * 15.0) * _KRANTI_DIFF[k] / 15.0 + _KRANTI_CUM[k]) / 60.0 if k < 6 else 24.0
        if x >= 180.0:
            dec = -dec
        dec *= _AYANA_SIGN[p]
        if p == 3 and dec < 0.0:
            dec = -dec
        ayana = (dec + 24.0) * 1.25 * (2.0 if p == 0 else 1.0)  # BPHS 27.15-17 (the Sun's doubled)
        parts = {"natonnata": nat, "paksha": pak, "tribhaga": tribhaga, "abda": 15.0 * (p == abda),
                 "masa": 30.0 * (p == masa), "vara": 45.0 * (p == vara), "hora": 60.0 * (p == hora),
                 "ayana": ayana, "yuddha": 0.0}
        kala = sum(parts.values())  # BPHS 27.8-17; yuddha is left at 0
        if p == 0:
            cheshta = _fold180(lon + 113.0) / 3.0
        elif p == 1:
            cheshta = _fold180(P[1] - P[0]) / 3.0
        else:
            (b1, r1, a1, y1), (b2, r2, a2, y2) = _CHESHTA[p - 2]
            first = norm360(days * r1 + years * y1 + b1 + a1)
            second = norm360(years * y2 + days * r2 + a2 + b2)
            cheshta = _fold180(first - (second + lon) * 0.5) / 3.0
        # drig, BPHS 27.19
        drig = 0.25 * sum(nature[j] * aspect_value(lon - P[j], j + 1) * 0.6 for j in range(7))
        total = sthana + dig + kala + (cheshta if p >= 2 else 0.0) + _NAISARGIKA[p] + drig
        out[name] = {"uchcha": uchcha, "saptavargaja": sapta, "oja_yugma": oja, "kendra": kendra,
                     "drekkana": drekkana, "sthana": sthana, "dig": dig, **parts, "kala": kala,
                     "cheshta": cheshta, "naisargika": _NAISARGIKA[p], "drig": drig, "total": total,
                     "rupas": total / 60.0, "percent": total / 60.0 * 100.0 / _REQUIRED_RUPAS[p],
                     "ishta": math.sqrt(uchcha * cheshta), "kashta": math.sqrt((60.0 - uchcha) * (60.0 - cheshta))}
    # bhava bala (BPHS 27.26-31: dig and drig; houses are lagna + 30 deg)
    kind = [2, 2, 0, 1, 2, 0, 0, 3, 0, 2, 0, 1]
    if lagna_lon % 30.0 >= 15.0:
        kind[8], kind[9] = 2, 1
    strongest = (6, 9, 3, 0)
    bhavas = []
    for i in range(12):
        sign = (lagna_sign + i) % 12
        lord = _SEVEN_PLANETS[_SIGN_LORD_INDEX[sign]]
        h = (i - strongest[kind[sign]] + 12) % 12
        bdig = (0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 50.0, 40.0, 30.0, 20.0, 10.0)[h]
        point = i * 30.0 + lagna_lon
        bdrig = 0.0
        for j in range(7):
            v = aspect_value(point - P[j], j + 1) * 0.6
            if nature[j] < 1:
                bdrig += v if j == 3 else -v * 0.25
            else:
                bdrig += v if j in (3, 4) else v * 0.25
        total = out[lord]["total"] + bdig + bdrig
        bhavas.append({"lord": lord, "sign": sign, "lord_bala": out[lord]["total"], "dig": bdig, "drig": bdrig, "total": total,
                       "rupas": total / 60.0})
    return {"planets": out, "bhavas": bhavas, "natures": nature}


# Vimsopaka bala (BPHS 7.17-27) over the compound relationships, computed in every varga (INI
# CompoundRelationshipsFromRasi=0)
VARGA_ORDER = ("D1", "D9", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D10", "D11", "D12", "D16", "D20",
                     "D24", "D27", "D30", "D40", "D45", "D60")
# natural relationships of Sun .. Ketu (aspects_friendships.NAISARGIKA_MATRIX, BPHS 3.55): 0 own, 2 friend, 3 neutral, 4 enemy
NATURAL_RELATIONS_9 = ((0, 2, 2, 3, 2, 4, 4, 4, 4), (2, 0, 3, 2, 3, 3, 3, 4, 4), (2, 2, 0, 4, 2, 3, 3, 4, 2),
                   (2, 4, 3, 0, 3, 2, 3, 3, 3), (2, 2, 2, 4, 0, 4, 3, 3, 3), (4, 4, 3, 2, 3, 0, 2, 2, 2),
                   (4, 4, 4, 2, 3, 2, 0, 2, 4), (4, 4, 4, 3, 3, 2, 2, 0, 2), (4, 4, 4, 3, 3, 2, 2, 0, 2))
_VIMSOPAKA_POINTS = (20.0, 18.0, 15.0, 10.0, 7.0, 5.0)        # own, great friend .. great enemy
_VIMSOPAKA_GROUPS = (
    ("dasa", (0, 2, 3, 7, 1, 9, 11, 12, 16, 19), (3, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 5)),
    ("shodasa", (0, 2, 3, 4, 7, 1, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19),
     (3.5, 1, 1, 0.5, 0.5, 3, 0.5, 0.5, 2, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 4)),
    ("sapta", (0, 2, 3, 7, 1, 11, 16), (5, 2, 3, 1, 2.5, 4.5, 2)),
    ("shad", (0, 2, 3, 1, 11, 16), (6, 2, 4, 5, 2, 1)))
_LORD_POINT = (2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4)             # natural sign lords as indices 0 = Sun .. 6


def compound_relationships(signs: List[int]) -> List[List[int]]:
    """Compound relationship codes (0 own, 1 great friend .. 5 great enemy) of Sun .. Ketu in one chart:
    natural code minus one when the other planet is 2/3/4/10/11/12 signs away, plus one otherwise."""
    out = []
    for i in range(9):
        row = []
        for j in range(9):
            code = NATURAL_RELATIONS_9[i][j]
            if i != j:
                code += -1 if (signs[j] - signs[i]) % 12 in (1, 2, 3, 9, 10, 11) else 1
            row.append(code)
        out.append(row)
    return out


def rashmis_ishta_kashta(planets: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """Rashmis and Parasara's Ishta / Kashta (BPHS 28.2-6) from ``shadbala_and_bhava_bala(...)["planets"]``:
    uchcha / cheshta rashmi = 2 (bala / 10 + 1), subha = their sum / 4, asubha = 8 - subha, ishta =
    5 (rashmis / 2 - 2), kashta = 60 - ishta."""
    out = {}
    for name, p in planets.items():
        ru, rc = 2.0 * (p["uchcha"] / 10.0 + 1.0), 2.0 * (p["cheshta"] / 10.0 + 1.0)
        ishta = (ru * 0.5 - 1.0 + rc * 0.5 - 1.0) * 5.0
        out[name] = {"uchcha_rashmi": ru, "cheshta_rashmi": rc, "subha": (ru + rc) * 0.25,
                     "asubha": 8.0 - (ru + rc) * 0.25, "ishta": ishta, "kashta": 60.0 - ishta}
    return out


def vimsopaka_balas(varga_signs: Dict[str, List[int]], from_rasi: bool = False) -> Dict[str, Dict[str, float]]:
    """Vimsopaka bala (0..20) of Sun .. Ketu in the dasa / shodasa / sapta / shad varga groups.
    ``varga_signs``: for every varga of VARGA_ORDER the signs of Sun .. Ketu. ``from_rasi``: INI
    CompoundRelationshipsFromRasi (the rasi chart's relationships in every varga)."""
    rel = [compound_relationships(varga_signs["D1" if from_rasi else v]) for v in VARGA_ORDER]
    names = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
    out = {}
    for i, name in enumerate(names):
        pts = [_VIMSOPAKA_POINTS[rel[v][i][_LORD_POINT[varga_signs[VARGA_ORDER[v]][i]]]] for v in range(20)]
        out[name] = {g: sum(pts[v] * w for v, w in zip(idx, ws)) * 0.05 for g, idx, ws in _VIMSOPAKA_GROUPS}
    return out


# Vaiseshikamsa counts (BPHS 6.42-53: the good vargas and their annulments).
# SwarudhaInAmsaBala=0 (the default) counts own sign — Rahu / Ketu co-own Aquarius / Scorpio — exaltation
# or moolatrikona, and returns before the combustion / defeat / debility flags.
_VAISESHIKAMSA_GROUPS = (("shad", (0, 2, 3, 1, 11, 16)), ("sapta", (0, 2, 3, 7, 1, 11, 16)),
                         ("dasa", (0, 2, 3, 7, 1, 9, 11, 12, 16, 19)),
                         ("shodasa", (0, 2, 3, 4, 7, 1, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19)))
_MOOLATRIKONA_9 = (4, 1, 0, 5, 8, 6, 10, 5, 11)  # moolatrikona signs (BPHS 3.51-54, 47.34-39)
_BAD_SAYANADI = (0, 1, 2, 4, 5, 11)              # SayanadiBadInAmsaBala
_NINE = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")


@dataclass
class AmsaBala:
    """The good-varga options (Settings > Balas; BPHS 6.42-53). The bools are the ini defaults and only cancel a
    placement that the swarudha rule added; own sign, exaltation and moolatrikona still count.
    ``swarudha`` (SwarudhaInAmsaBala): 0 off; 1 a kendra from the rasi arudha lagna; 2 from the varga's
    arudha lagna; 3 from the planet's rasi graha arudha; 4 from its graha arudha in that varga; 5 from the
    varga position of the rasi arudha lagna's lord; 6 / 7 the planet rules a kendra from 1 / 2.
    ``rasi_lons`` are Sun .. Ketu. ``lagna_signs`` is one lagna sign per varga of VARGA_ORDER
    (only varga 0 is read for swarudha 1, 3, 5 and 6).
    ``past_table``: the rasi arudha signs (points 59, 83..91 of varga 0) are
    still 0 when the counts are made, so swarudha 1, 3, 5 and 6 count kendras from Aries (the varga arudhas for 2, 4, 7 are not reproduced in this mode)."""
    swarudha: int = 0
    past_table: bool = False
    combustion: bool = True
    dispositor_combustion: bool = False
    combustion_classical: bool = False      # combust by the classical orbs (natal_chart.is_combust), not the 6-degree rule
    defeat: bool = True
    dispositor_defeat: bool = False
    neecha: bool = True
    dispositor_neecha: bool = False
    dispositor_neecha_rasi: bool = False
    poor_vimsopaka: bool = True
    dispositor_poor_vimsopaka: bool = False
    sayanadi: bool = True
    dispositor_sayanadi: bool = False
    rasi_lons: Optional[Sequence[float]] = None
    retrograde: Optional[Sequence[bool]] = None
    lagna_signs: Optional[Sequence[int]] = None
    lagna_lon: Optional[float] = None
    ghatis_since_sunrise: float = 0.0


def _amsa_context(varga_signs: Dict[str, List[int]], amsa: AmsaBala):
    """Arudha signs, longitudes and sayanadi the swarudha rule reads. Raises if a used input is missing."""
    from .. import sign_strength as SS
    mode = amsa.swarudha
    if amsa.rasi_lons is None or len(amsa.rasi_lons) != 9 or amsa.lagna_lon is None:
        raise ValueError("swarudha vaiseshikamsa needs rasi_lons (Sun .. Ketu) and lagna_lon")
    if amsa.lagna_signs is None:
        raise ValueError("swarudha vaiseshikamsa needs lagna_signs")
    lons = (amsa.lagna_lon,) + tuple(amsa.rasi_lons)          # index 0 lagna, 1 Sun .. 9 Ketu
    retro = (False,) + tuple(amsa.retrograde or (False,) * 9)
    need_all = mode in (2, 4, 7)
    if need_all and len(amsa.lagna_signs) < len(VARGA_ORDER):
        raise ValueError("swarudha 2, 4 and 7 need a lagna sign for every varga")
    als, graha = {}, {}
    for vi, v in enumerate(VARGA_ORDER):
        if not need_all and vi:
            continue
        signs = [amsa.lagna_signs[vi]] + list(varga_signs[v])
        als[vi] = SS.bhava_arudhas(signs, lons)[0]
        if mode in (3, 4):
            graha[vi] = [SS.graha_arudha(p, signs, lons) for p in range(1, 10)]
        if amsa.past_table and vi == 0:
            als[0], graha[0] = 0, [0] * 9
    activity = None
    if amsa.sayanadi or amsa.dispositor_sayanadi:
        from ..avasthas import graha_avasthas
        av = graha_avasthas(list(amsa.rasi_lons), amsa.lagna_lon, amsa.ghatis_since_sunrise)
        activity = [av[n]["activity"] for n in _NINE]
    return {"lons": lons, "retro": retro, "als": als, "graha": graha, "activity": activity}


def _defeated(p: int, lons) -> bool:
    """Another of Sun .. Ketu is 0..1 deg ahead (GrahaYuddha loses, Norm360Diff <= 1)."""
    return any(q != p and (lons[q] - lons[p]) % 360.0 <= 1.0 for q in range(1, 10))


def _swarudha_good(planet: int, vi: int, sign: int, varga_signs, ctx, amsa: AmsaBala) -> bool:
    """The swarudha cases (BPHS 6.42-53: "the Rasis owned by the Lord of a Kendra from the Arudha Lagn") after own /
    exaltation / moolatrikona have failed."""
    from ..sign_strength import SIGN_LORDS
    mode, al = amsa.swarudha, ctx["als"]
    ref_v = 0 if mode in (1, 3, 5, 6) else vi
    if mode in (1, 2):
        ok = (sign - al[ref_v] + 12) % 3 == 0
    elif mode in (3, 4):
        ok = (sign - ctx["graha"][ref_v][planet] + 12) % 3 == 0
    elif mode == 5:
        lord = SIGN_LORDS[al[0]]
        ok = (sign - varga_signs[VARGA_ORDER[vi]][lord - 1] + 12) % 3 == 0
    elif mode in (6, 7):
        ok = any(SIGN_LORDS[(al[ref_v] + 3 * k) % 12] == planet + 1 for k in range(4))
    else:
        return False
    if not ok:
        return False
    lord = SIGN_LORDS[sign]
    here = varga_signs[VARGA_ORDER[vi]]
    rel = compound_relationships(here) if amsa.poor_vimsopaka or amsa.dispositor_poor_vimsopaka else None
    p = planet + 1
    if amsa.combustion and vi == 0 and is_combust(p, ctx["lons"], ctx["retro"], classical=amsa.combustion_classical):
        return False
    if amsa.dispositor_combustion and is_combust(lord, ctx["lons"], ctx["retro"], classical=amsa.combustion_classical):
        return False
    if amsa.defeat and vi == 0 and _defeated(p, ctx["lons"]):
        return False
    if amsa.dispositor_defeat and _defeated(lord, ctx["lons"]):
        return False
    if amsa.neecha and sign == _SS.DEBILITATION[planet + 1]:
        return False
    if amsa.dispositor_neecha and here[lord - 1] == _SS.DEBILITATION[lord]:
        return False
    if amsa.dispositor_neecha_rasi and varga_signs["D1"][lord - 1] == _SS.DEBILITATION[lord]:
        return False
    if rel is not None and amsa.poor_vimsopaka and rel[planet][lord - 1] in (4, 5):
        return False
    if rel is not None and amsa.dispositor_poor_vimsopaka:
        lord2 = SIGN_LORDS[here[lord - 1]]
        if rel[lord - 1][lord2 - 1] in (4, 5):
            return False
    act = ctx["activity"]
    if act is not None and amsa.sayanadi and act[planet] in _BAD_SAYANADI:
        return False
    if act is not None and amsa.dispositor_sayanadi and act[lord - 1] in _BAD_SAYANADI:
        return False
    return True


def vaiseshikamsa_counts(varga_signs: Dict[str, List[int]],
                        amsa: Optional[AmsaBala] = None) -> Dict[str, Dict[str, int]]:
    """Number of vargas of the shad / sapta / dasa / shodasa groups in which Sun .. Ketu are well placed.
    ``amsa`` left out (or swarudha 0) is the default. See ``AmsaBala`` for the other modes."""
    use = amsa is not None and bool(amsa.swarudha)
    ctx = _amsa_context(varga_signs, amsa) if use else None
    out = {}
    for i, name in enumerate(_NINE):
        good = []
        for vi, v in enumerate(VARGA_ORDER):
            s = varga_signs[v][i]
            owns = _LORD_POINT[s] == i or (s == 10 and i == 7) or (s == 7 and i == 8)
            basic = owns or _SS.EXALTATION[i + 1] == s or _MOOLATRIKONA_9[i] == s
            good.append(basic or (use and _swarudha_good(i, vi, s, varga_signs, ctx, amsa)))
        out[name] = {g: sum(good[v] for v in idx) for g, idx in _VAISESHIKAMSA_GROUPS}
    return out
