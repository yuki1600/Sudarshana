"""
core_logic/kp_astrology.py
==========================
Krishnamurti Paddhati (KP System) Calculation Engine.
Sources (docs/SOURCES.md section 15): K. S. Krishnamurti, Krishnamurti Padhdhati (KSK) vol. I: the sign, star and
sub lords (each star divided in Vimshottari proportions), Placidus cusps; the four levels of significators, the
ruling planets and the 1-249 horary numbers as KSK's later Readers teach them (not checked page by page).

Features:
1. Complete 249 Sub-Lord & Sub-Sub Lord Zodiacal Division:
   - Unequal sub-divisions proportional to Vimshottari Dasa years
   - Nakshatra Lord -> Sub Lord -> Sub-Sub Lord (Prati-sub)
2. Planetary KP Sign, Star, Sub, and Sub-Sub Lords
3. Cuspal Sub-Lords for the 12 Placidus House Cusps
4. 4-Fold House Significators (Level A, Level B, Level C, Level D)
5. KP Ruling Planets (Lagna Star/Sign, Moon Star/Sign, Day Lord)
6. KP 1..249 Horary Prasna Seed Number Resolver
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional, Any

from .utils import norm360
from .natal_chart import (
    NAKSHATRA_NAMES,
    NAKSHATRA_LORDS,
    RASI_NAMES_EN,
    RASI_LORDS
)

# ---------------------------------------------------------------------------
# KP Constants & Vimshottari Proportions
# ---------------------------------------------------------------------------

KP_DASA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17
}

VIMSHOTTARI_CYCLE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
TOTAL_DASA_YEARS = 120.0
NAKSHATRA_SPAN_DEG = 360.0 / 27.0  # 13.333333333333334 degrees = 13°20'

def _build_249_sub_table() -> List[Dict[str, Any]]:
    """
    Constructs the classical 249 KP Sub-Lord boundaries across the zodiac.
    When a sub crosses a sign boundary (30° multiples), it splits into two,
    producing exactly 249 distinct contiguous regions in the 360° circle.
    """
    table = []
    sub_number = 1
    
    for nak_idx in range(27):
        nak_start = nak_idx * NAKSHATRA_SPAN_DEG
        nak_lord = NAKSHATRA_LORDS[nak_idx]
        nak_name = NAKSHATRA_NAMES[nak_idx]
        
        # Start sub sequence from the nakshatra lord
        start_lord_idx = VIMSHOTTARI_CYCLE.index(nak_lord)
        
        curr_deg = nak_start
        for step in range(9):
            sub_lord = VIMSHOTTARI_CYCLE[(start_lord_idx + step) % 9]
            sub_years = KP_DASA_YEARS[sub_lord]
            sub_span_deg = (sub_years / TOTAL_DASA_YEARS) * NAKSHATRA_SPAN_DEG
            sub_end = curr_deg + sub_span_deg
            
            curr_sign = int(curr_deg // 30.0) % 12
            boundary = (int(curr_deg // 30.0) + 1) * 30.0
            
            # Check if this sub strictly crosses a 30° sign boundary
            if (curr_deg < boundary - 1e-6) and (sub_end > boundary + 1e-6):
                # Part 1 (in curr_sign)
                table.append({
                    "sub_number": sub_number,
                    "start_deg": curr_deg,
                    "end_deg": boundary,
                    "sign_idx": curr_sign,
                    "sign_name": RASI_NAMES_EN[curr_sign],
                    "sign_lord": RASI_LORDS[curr_sign],
                    "nakshatra_idx": nak_idx,
                    "nakshatra_name": nak_name,
                    "star_lord": nak_lord,
                    "sub_lord": sub_lord
                })
                sub_number += 1
                
                # Part 2 (in next sign)
                next_sign = (curr_sign + 1) % 12
                table.append({
                    "sub_number": sub_number,
                    "start_deg": boundary,
                    "end_deg": min(sub_end, 360.0),
                    "sign_idx": next_sign,
                    "sign_name": RASI_NAMES_EN[next_sign],
                    "sign_lord": RASI_LORDS[next_sign],
                    "nakshatra_idx": nak_idx,
                    "nakshatra_name": nak_name,
                    "star_lord": nak_lord,
                    "sub_lord": sub_lord
                })
                sub_number += 1
            else:
                table.append({
                    "sub_number": sub_number,
                    "start_deg": curr_deg,
                    "end_deg": min(sub_end, 360.0),
                    "sign_idx": curr_sign,
                    "sign_name": RASI_NAMES_EN[curr_sign],
                    "sign_lord": RASI_LORDS[curr_sign],
                    "nakshatra_idx": nak_idx,
                    "nakshatra_name": nak_name,
                    "star_lord": nak_lord,
                    "sub_lord": sub_lord
                })
                sub_number += 1
                
            curr_deg = sub_end
            
    return table

KP_249_TABLE = _build_249_sub_table()

# ---------------------------------------------------------------------------
# 1. Planetary Sub-Lord and Sub-Sub Lord Calculator
# ---------------------------------------------------------------------------

def get_kp_sub_lords(longitude_deg: float) -> Dict[str, Any]:
    """
    Computes the 4-tier KP hierarchical lords for any celestial longitude:
    1. Sign Lord (Rasi Lord)
    2. Star Lord (Nakshatra Lord)
    3. Sub Lord
    4. Sub-Sub Lord (Prati-sub)
    The sub-lord table is computed from the Vimshottari years (KSK vol. I), not stored.
    """
    lon = norm360(longitude_deg)
    sign_idx = int(lon // 30.0)
    sign_lord = RASI_LORDS[sign_idx]
    
    nak_idx = int(lon // NAKSHATRA_SPAN_DEG)
    nak_lord = NAKSHATRA_LORDS[nak_idx]
    nak_start = nak_idx * NAKSHATRA_SPAN_DEG
    rem_in_nak = lon - nak_start
    
    # 1. Resolve Sub Lord
    start_sub_idx = VIMSHOTTARI_CYCLE.index(nak_lord)
    sub_lord = nak_lord
    sub_start_deg = nak_start
    sub_span_deg = 0.0
    
    accum = 0.0
    for step in range(9):
        p = VIMSHOTTARI_CYCLE[(start_sub_idx + step) % 9]
        span = (KP_DASA_YEARS[p] / TOTAL_DASA_YEARS) * NAKSHATRA_SPAN_DEG
        if accum + span >= rem_in_nak - 1e-9:
            sub_lord = p
            sub_start_deg = nak_start + accum
            sub_span_deg = span
            break
        accum += span
        
    rem_in_sub = lon - sub_start_deg
    
    # 2. Resolve Sub-Sub Lord (Prati-sub)
    start_sub_sub_idx = VIMSHOTTARI_CYCLE.index(sub_lord)
    sub_sub_lord = sub_lord
    accum_ss = 0.0
    for step in range(9):
        p_ss = VIMSHOTTARI_CYCLE[(start_sub_sub_idx + step) % 9]
        span_ss = (KP_DASA_YEARS[p_ss] / TOTAL_DASA_YEARS) * sub_span_deg
        if accum_ss + span_ss >= rem_in_sub - 1e-9:
            sub_sub_lord = p_ss
            break
        accum_ss += span_ss
        
    # Find matching entry in 249 table
    sub_num = 1
    for entry in KP_249_TABLE:
        if entry["start_deg"] - 1e-8 <= lon < entry["end_deg"] + 1e-8:
            sub_num = entry["sub_number"]
            break
            
    return {
        "longitude": round(lon, 4),
        "sign_name": RASI_NAMES_EN[sign_idx],
        "sign_lord": sign_lord,
        "nakshatra_name": NAKSHATRA_NAMES[nak_idx],
        "star_lord": nak_lord,
        "sub_lord": sub_lord,
        "sub_sub_lord": sub_sub_lord,
        "sub_number_249": sub_num,
        "ruling_string": f"{sign_lord} - {nak_lord} - {sub_lord} - {sub_sub_lord}"
    }

def kp_period_date(birth, years: float, cfg=None, span_days: Optional[float] = None):
    """The local date ``years`` true sidereal solar years after ``birth`` (dasa year definition 3, section 9.1).
    With ``span_days`` (an annual or other event chart: the days it covers) the years become
    ``years * span_days / (120 * 365.24219)``: 120 Vimshottari years fitted into the span (a convention), then
    walked as true solar years."""
    from .ephemeris import dasa_year_mapper
    if span_days is not None:
        years *= span_days / (120.0 * 365.24219)
    return dasa_year_mapper(birth, cfg, "SOLAR")(years)


def get_kp_sub_levels(longitude_deg: float, levels: int = 5) -> Dict[str, Any]:
    """
    Star lord plus up to five nested Vimshottari sub-lords for a longitude (the option
    "Nakshatra and sub lords of each planet (upto 5 levels of subs)"; the levels past the sub are a convention).

    Level names: sub, prati-sub (2nd), sookshma-sub (3rd), praana-sub (4th), deha-sub (5th).
    Each level divides its parent span in Vimshottari proportions, starting with the parent's lord.
    Levels 1-2 agree with :func:`get_kp_sub_lords` (checked in tests).
    """
    if not 0 <= levels <= 5:
        raise ValueError("levels must be 0..5")
    lon = norm360(longitude_deg)
    nak_idx = int(lon // NAKSHATRA_SPAN_DEG)
    lord = NAKSHATRA_LORDS[nak_idx]
    start, span = nak_idx * NAKSHATRA_SPAN_DEG, NAKSHATRA_SPAN_DEG
    names = ["sub_lord", "prati_sub_lord", "sookshma_sub_lord", "praana_sub_lord", "deha_sub_lord"]
    out: Dict[str, Any] = {"longitude": round(lon, 6), "star_lord": lord}
    for level in range(levels):
        first = VIMSHOTTARI_CYCLE.index(lord)
        offset = lon - start
        accum = 0.0
        chosen, chosen_span, chosen_start = lord, span, start
        for step in range(9):
            p = VIMSHOTTARI_CYCLE[(first + step) % 9]
            seg = KP_DASA_YEARS[p] / TOTAL_DASA_YEARS * span
            if accum + seg > offset or step == 8:
                chosen, chosen_span, chosen_start = p, seg, start + accum
                break
            accum += seg
        out[names[level]] = chosen
        lord, start, span = chosen, chosen_start, chosen_span
    return out


# ---------------------------------------------------------------------------
# 2. Cuspal Sub-Lords Calculator
# ---------------------------------------------------------------------------

def compute_cuspal_sub_lords(house_cusps_deg: List[float]) -> List[Dict[str, Any]]:
    """
    Computes KP 4-tier lords for all 12 house cusps (typically Placidus cusps).
    In KP astrology, the sub-lord of a house cusp dictates whether that house
    will bear positive fruition, and which houses it connects to.
    """
    cuspal_lords = []
    for h_idx, cusp in enumerate(house_cusps_deg, 1):
        info = get_kp_sub_lords(cusp)
        info["house_number"] = h_idx
        cuspal_lords.append(info)
    return cuspal_lords

# ---------------------------------------------------------------------------
# 3. 4-Fold House Significators Engine
# ---------------------------------------------------------------------------

def compute_kp_significators(
    planet_longitudes: Dict[str, float],
    house_cusps_deg: List[float]
) -> Dict[str, Any]:
    """
    Computes the classical 4-tier KP House Significators:
    Level A: Planets in the star (constellation) of the occupants of the house (Strongest)
    Level B: Occupants of the house
    Level C: Planets in the star of the house lord
    Level D: The house lord itself (Weakest)
    
    Also computes planet-wise significations (which houses each planet signifies).
    """
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    planet_stars = {}
    planet_houses = {}
    
    # 1. Determine planet house placement and star lords
    for p in planets:
        if p not in planet_longitudes:
            continue
        lon = norm360(planet_longitudes[p])
        star_info = get_kp_sub_lords(lon)
        planet_stars[p] = star_info["star_lord"]
        
        # Determine house occupancy (cusp h to cusp h+1)
        assigned_h = 12
        for h in range(12):
            c_curr = house_cusps_deg[h]
            c_next = house_cusps_deg[(h + 1) % 12]
            if c_curr < c_next:
                if c_curr <= lon < c_next:
                    assigned_h = h + 1
                    break
            else:  # crosses 0° Aries
                if lon >= c_curr or lon < c_next:
                    assigned_h = h + 1
                    break
        planet_houses[p] = assigned_h
        
    # 2. Determine house lords (from cusp sign)
    house_lords = {}
    for h in range(12):
        cusp_lon = house_cusps_deg[h]
        s_idx = int(norm360(cusp_lon) // 30.0)
        house_lords[h + 1] = RASI_LORDS[s_idx]
        
    # 3. Build 4-level house significators
    house_significators = {}
    for h in range(1, 13):
        # Level B: Occupants
        occupants = [p for p, p_h in planet_houses.items() if p_h == h]
        
        # Level A: Planets in the star of occupants
        level_a = [p for p, s_lord in planet_stars.items() if s_lord in occupants]
        
        # Level D: House lord
        h_lord = house_lords[h]
        
        # Level C: Planets in the star of the house lord
        level_c = [p for p, s_lord in planet_stars.items() if s_lord == h_lord]
        
        house_significators[h] = {
            "house": h,
            "level_a": sorted(list(set(level_a))),
            "level_b": sorted(list(set(occupants))),
            "level_c": sorted(list(set(level_c))),
            "level_d": [h_lord],
            "combined": sorted(list(set(level_a + occupants + level_c + [h_lord])))
        }
        
    # 4. Invert to planet-wise significations
    planet_significations = {}
    for p in planets:
        if p not in planet_longitudes:
            continue
        sig_houses = []
        for h, data in house_significators.items():
            if p in data["combined"]:
                sig_houses.append(h)
        planet_significations[p] = {
            "planet": p,
            "star_lord": planet_stars.get(p, ""),
            "occupied_house": planet_houses.get(p, 0),
            "signified_houses": sorted(sig_houses)
        }
        
    return {
        "house_significators": house_significators,
        "planet_significations": planet_significations,
        "house_lords": house_lords
    }

# ---------------------------------------------------------------------------
# 4. KP Ruling Planets (RP) Engine
# ---------------------------------------------------------------------------

VAARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

def get_kp_ruling_planets(
    lagna_lon: float,
    moon_lon: float,
    weekday_idx: int  # 0=Sunday, 1=Monday, ... 6=Saturday
) -> Dict[str, Any]:
    """
    Computes KP Ruling Planets (RP) at the time of query or birth:
    1. Lagna Star Lord
    2. Lagna Sign Lord
    3. Moon Star Lord
    4. Moon Sign Lord
    5. Day Lord (Vaara Lord)
    """
    l_info = get_kp_sub_lords(lagna_lon)
    m_info = get_kp_sub_lords(moon_lon)
    day_lord = VAARA_LORDS[weekday_idx % 7]
    
    ruling_order = [
        l_info["star_lord"],
        l_info["sign_lord"],
        m_info["star_lord"],
        m_info["sign_lord"],
        day_lord
    ]
    
    return {
        "lagna_star_lord": l_info["star_lord"],
        "lagna_sign_lord": l_info["sign_lord"],
        "moon_star_lord": m_info["star_lord"],
        "moon_sign_lord": m_info["sign_lord"],
        "day_lord": day_lord,
        "ruling_planets_order": ruling_order,
        "unique_ruling_planets": list(dict.fromkeys(ruling_order))
    }

# ---------------------------------------------------------------------------
# 5. KP 1..249 Horary Prasna Seed Resolver
# ---------------------------------------------------------------------------

def resolve_kp_horary_number(horary_seed: int) -> Dict[str, Any]:
    """
    Resolves a KP Horary Query seed number (1 to 249):
    Returns the exact starting longitude, sign, star lord, and sub lord.
    The 249 numbers of KP horary: each sub, split where it crosses a sign (KSK's Readers).
    """
    if not (1 <= horary_seed <= 249):
        raise ValueError(f"KP Horary seed must be between 1 and 249, got {horary_seed}")
        
    entry = KP_249_TABLE[horary_seed - 1]
    return {
        "horary_number": horary_seed,
        "start_longitude": round(entry["start_deg"], 4),
        "end_longitude": round(entry["end_deg"], 4),
        "sign_name": entry["sign_name"],
        "sign_lord": entry["sign_lord"],
        "nakshatra_name": entry["nakshatra_name"],
        "star_lord": entry["star_lord"],
        "sub_lord": entry["sub_lord"],
        "formatted_span": f"{entry['sign_name']} {round(entry['start_deg'] % 30.0, 2)}° - {round(entry['end_deg'] % 30.0, 2)}°"
    }
