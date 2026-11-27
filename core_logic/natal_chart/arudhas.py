"""arudhas: part of natal_chart (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Any, Dict
from .signs import RASI_NAMES_EN

# ---------------------------------------------------------------------------
# Arudha Padas (AL, UL, A1-A12): BPHS 29.1-5
# ---------------------------------------------------------------------------

def compute_arudha_pada(house_num: int, house_sign_idx: int, lord_sign_idx: int) -> int:
    """
    Computes Arudha Pada for a given house (1-12).
    Rule: Count from house sign to its lord sign.
    Count the same number of signs forward from the lord sign.
    Parasara Exception:
    If Arudha falls in the same house or 7th from it:
    Move it 10 signs forward.
    """
    dist = (lord_sign_idx - house_sign_idx) % 12
    if dist < 0:
        dist += 12
    raw_arudha = (lord_sign_idx + dist) % 12
    
    # Exceptions: 1st or 7th from house
    if raw_arudha == house_sign_idx or raw_arudha == (house_sign_idx + 6) % 12:
        arudha = (raw_arudha + 9) % 12 # 10th sign (0-indexed +9)
    else:
        arudha = raw_arudha
    return arudha

# ---------------------------------------------------------------------------
# Graha Arudhas (Planetary Arudha Padas): BPHS 29.6-7
# ---------------------------------------------------------------------------

GRAHA_OWNED_SIGNS = {
    "Sun": [4],             # Leo
    "Moon": [3],            # Cancer
    "Mars": [0, 7],         # Aries, Scorpio
    "Mercury": [2, 5],      # Gemini, Virgo
    "Jupiter": [8, 11],     # Sagittarius, Pisces
    "Venus": [1, 6],        # Taurus, Libra
    "Saturn": [9, 10],      # Capricorn, Aquarius
    "Rahu": [10],           # Aquarius (co-lord with Saturn)
    "Ketu": [7]             # Scorpio (co-lord with Mars)
}

def compute_graha_arudha(planet: str, planet_sign_idx: int, target_owned_sign_idx: int) -> int:
    """
    Computes Graha Arudha (Planetary Arudha Pada) for a given planet from an owned sign.
    Rule (BPHS 29.6-7): Count from planet's occupied sign to the owned sign.
    Count the same distance forward from the owned sign.
    Parasara Exception: If it falls in the planet's sign or 7th from it, move 10 signs forward (+9) (the
    exceptions of BPHS 29.4-5, applied to grahas as for bhavas).
    """
    dist = (target_owned_sign_idx - planet_sign_idx) % 12
    raw = (target_owned_sign_idx + dist) % 12
    if raw == planet_sign_idx or raw == (planet_sign_idx + 6) % 12:
        return (raw + 9) % 12
    return raw

def compute_all_graha_arudhas(planet_signs: Dict[str, int]) -> Dict[str, Any]:
    """
    Computes Graha Arudhas for all 9 planets (Sun through Ketu),
    including dual-sign arudhas for Mars, Mercury, Jupiter, Venus, and Saturn.
    """
    results = {}
    for p, owned_list in GRAHA_OWNED_SIGNS.items():
        if p not in planet_signs:
            continue
        p_sign = planet_signs[p] % 12
        arudha_list = []
        for owned_s in owned_list:
            ar_idx = compute_graha_arudha(p, p_sign, owned_s)
            arudha_list.append({
                "owned_sign": owned_s,
                "owned_sign_name": RASI_NAMES_EN[owned_s],
                "graha_arudha_sign": ar_idx,
                "graha_arudha_name": RASI_NAMES_EN[ar_idx]
            })
        primary = arudha_list[0]["graha_arudha_sign"]
        results[p] = {
            "planet": p,
            "planet_sign": p_sign,
            "planet_sign_name": RASI_NAMES_EN[p_sign],
            "primary_arudha_sign": primary,
            "primary_arudha_name": RASI_NAMES_EN[primary],
            "all_arudhas": arudha_list
        }
    return results
