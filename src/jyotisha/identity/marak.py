"""
Marak Grahas — Death-Inflicting Planets (BPHS Ch. 44).

Primary Maraks : lords of 2nd and 7th houses
Secondary Maraks : planets occupying 2nd or 7th houses
Natural Marak  : Saturn (general significator of death/endings)
"""

from __future__ import annotations
from typing import Any

from src.jyotisha.base.constants import SIGN_LORD
from src.jyotisha.base.utils import lon_to_sign_idx

_CLASSICAL = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _house_of(planet: str, lons: dict[str, float], asc_sign_idx: int) -> int:
    si = lon_to_sign_idx(lons[planet])
    return ((si - asc_sign_idx) % 12) + 1


def _lord_of_house(house_num: int, asc_sign_idx: int) -> str:
    sign_idx = (asc_sign_idx + house_num - 1) % 12
    return SIGN_LORD.get(sign_idx, "Sun")


def compute_marak_grahas(
    numeric_lons: dict[str, float],
    asc_sign_idx: int,
) -> list[dict[str, Any]]:
    """
    Identify Marak Grahas for the chart.

    Returns:
        list of dicts: planet, type, reason, house
    """
    results = []
    seen = set()

    # Primary Maraks: lords of 2nd and 7th
    for hn in [2, 7]:
        lord = _lord_of_house(hn, asc_sign_idx)
        if lord not in numeric_lons:
            continue
        placement_house = _house_of(lord, numeric_lons, asc_sign_idx)
        key = (lord, "primary")
        if key not in seen:
            seen.add(key)
            results.append({
                "Planet": lord,
                "Type": "Primary",
                "Reason": f"Lord of {hn}th house (Marak sthana)",
                "Placed In House": placement_house,
                "Marak House": hn,
            })

    # Secondary Maraks: planets sitting in 2nd or 7th
    for hn in [2, 7]:
        for p in _CLASSICAL:
            if p not in numeric_lons:
                continue
            if _house_of(p, numeric_lons, asc_sign_idx) == hn:
                lord = _lord_of_house(hn, asc_sign_idx)
                if p == lord:
                    continue  # Already captured as primary
                key = (p, "secondary")
                if key not in seen:
                    seen.add(key)
                    results.append({
                        "Planet": p,
                        "Type": "Secondary",
                        "Reason": f"Placed in {hn}th house (Marak sthana)",
                        "Placed In House": hn,
                        "Marak House": hn,
                    })

    # Natural Marak: Saturn (when not already listed)
    if "Saturn" in numeric_lons and ("Saturn", "primary") not in seen and ("Saturn", "secondary") not in seen:
        sat_house = _house_of("Saturn", numeric_lons, asc_sign_idx)
        results.append({
            "Planet": "Saturn",
            "Type": "Natural",
            "Reason": "Natural significator of longevity and death (Ayushkaraka)",
            "Placed In House": sat_house,
            "Marak House": None,
        })

    return results
