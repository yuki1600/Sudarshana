"""
core_logic/kakshyas.py
======================
Modularized Calculation Engine for Ashtakavarga Kakshyas and Real-Time Transit Scoring.
Sources (docs/SOURCES.md section 12): the eight kakshyas of a sign and their use in transits PVR 25.5.2;
the bindus of the Prastara Ashtakavarga BPHS 66.

Each zodiac sign (30°) is divided into 8 equal Kakshyas (3°45' = 3.75° each).
Order of Kakshya rulers in every sign:
1. Saturn  (0°00' - 3°45')
2. Jupiter (3°45' - 7°30')
3. Mars    (7°30' - 11°15')
4. Sun     (11°15' - 15°00')
5. Venus   (15°00' - 18°45')
6. Mercury (18°45' - 22°30')
7. Moon    (22°30' - 26°15')
8. Lagna   (26°15' - 30°00')

A planet's transit through a kakshya is auspicious if that kakshya ruler contributed a bindu (1)
in the transiting planet's Prastara Ashtakavarga (BAV). If 0 bindus, the transit is inauspicious.
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Any

from .natal_chart import norm360, RASI_NAMES_EN

KAKSHYA_LORDS = [
    "Saturn",
    "Jupiter",
    "Mars",
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
    "Lagna"
]

KAKSHYA_SPAN = 30.0 / 8.0  # 3.75 degrees = 3° 45'

def get_kakshya_info(longitude: float) -> Dict[str, Any]:
    """
    Given a celestial longitude (0..360°), determines:
    - Sign index and name
    - Degree within sign
    - Kakshya index (0..7) and Kakshya lord
    - Exact start and end degree of the Kakshya
    """
    lon = norm360(longitude)
    sign_idx = int(lon // 30.0)
    deg_in_sign = lon % 30.0
    
    kakshya_idx = min(7, int(deg_in_sign // KAKSHYA_SPAN))
    lord = KAKSHYA_LORDS[kakshya_idx]
    
    start_deg = kakshya_idx * KAKSHYA_SPAN
    end_deg = start_deg + KAKSHYA_SPAN
    
    return {
        "longitude": lon,
        "sign_index": sign_idx,
        "sign_name": RASI_NAMES_EN[sign_idx],
        "degree_in_sign": deg_in_sign,
        "kakshya_index": kakshya_idx,
        "kakshya_number": kakshya_idx + 1,
        "kakshya_lord": lord,
        "kakshya_start_deg": start_deg,
        "kakshya_end_deg": end_deg
    }

def evaluate_kakshya_transit(
    planet: str,
    transit_lon: float,
    prastara_matrix: Dict[str, Dict[str, List[int]]]
) -> Dict[str, Any]:
    """
    Evaluates whether a transiting planet is in a favorable or unfavorable Kakshya.
    prastara_matrix: {planet: {contributor: [12 signs 0/1]}} from ashtakavarga engine.
    """
    k_info = get_kakshya_info(transit_lon)
    s_idx = k_info["sign_index"]
    k_lord = k_info["kakshya_lord"]
    
    # Check if this contributor gave a bindu (1) in this sign for this planet
    has_bindu = False
    if planet in prastara_matrix:
        contrib_map = prastara_matrix[planet]
        if k_lord in contrib_map:
            bindu_val = contrib_map[k_lord][s_idx]
            has_bindu = (bindu_val == 1)
            
    status = "Favorable Kakshya (Bindu Present)" if has_bindu else "Unfavorable Kakshya (Kshaya / 0 Bindu)"
    
    return {
        **k_info,
        "transiting_planet": planet,
        "has_bindu": has_bindu,
        "transit_status": status,
        "description": f"{planet} is transiting in the kakshya of {k_lord} in {k_info['sign_name']} and it is a {'good' if has_bindu else 'bad'} kakshya."
    }

def evaluate_all_transit_kakshyas(
    transit_longitudes: Dict[str, float],
    prastara_matrix: Dict[str, Dict[str, List[int]]]
) -> Dict[str, Dict[str, Any]]:
    """Evaluates Kakshya transit status for all active planets."""
    res = {}
    for p, lon in transit_longitudes.items():
        res[p] = evaluate_kakshya_transit(p, lon, prastara_matrix)
    return res
