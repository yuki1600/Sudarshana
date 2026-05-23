"""
Jaimini Chara Karakas (Ch. 32) and Karakamsha (Ch. 33).

Chara Karakas rank 7 classical planets by their intra-sign degree (descending).
Highest degree = Atmakaraka (AK) … lowest = Darakaraka (DK).

Karakamsha = Atmakaraka's Navamsha sign; the Navamsha lagna of the AK becomes
the Karakamsha Lagna for interpretation.
"""

from __future__ import annotations
from typing import Any

from src.jyotisha.base.utils import lon_to_sign_idx
from src.jyotisha.identity.vargas import navamsa_for
from src.jyotisha.base.constants import RASHI_SA

# Classical 7 planets used for Chara Karakas (no Rahu/Ketu)
_CK_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# 8-karaka scheme includes Rahu (some traditions)
_CK_PLANETS_8 = _CK_PLANETS + ["Rahu (true)"]

KARAKA_NAMES_7 = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
KARAKA_FULL_7 = [
    "Atmakaraka",
    "Amatyakaraka",
    "Bhratrukaraka",
    "Matrukaraka",
    "Putrakaraka",
    "Gnatikaraka",
    "Darakaraka",
]


def _intra_sign_deg(lon: float) -> float:
    """Degrees within the current sign (0–30)."""
    return lon % 30.0


def compute_chara_karakas(
    numeric_lons: dict[str, float],
    use_8_karaka: bool = False,
) -> list[dict[str, Any]]:
    """
    Compute Jaimini Chara Karakas.

    Args:
        numeric_lons: sidereal planet longitudes (0–360).
        use_8_karaka: if True, include Rahu (reversed degree) for 8-karaka scheme.

    Returns:
        List of dicts: rank, abbr, full_name, planet, intra_deg, sign, navamsha.
    """
    planet_list = _CK_PLANETS_8 if use_8_karaka else _CK_PLANETS
    available = [(p, numeric_lons[p]) for p in planet_list if p in numeric_lons]

    # For Rahu, intra-sign degree is REVERSED (30 - deg), per Jaimini tradition
    def effective_deg(planet: str, lon: float) -> float:
        d = _intra_sign_deg(lon)
        return (30.0 - d) if planet in ("Rahu (true)", "Rahu") else d

    ranked = sorted(available, key=lambda x: effective_deg(x[0], x[1]), reverse=True)

    names = KARAKA_NAMES_7[:len(ranked)]
    full_names = KARAKA_FULL_7[:len(ranked)]

    results = []
    for i, (planet, lon) in enumerate(ranked):
        intra = effective_deg(planet, lon)
        sign_idx = lon_to_sign_idx(lon)
        nav_idx, _ = navamsa_for(lon)
        results.append({
            "Rank": i + 1,
            "Karaka": names[i],
            "Full Name": full_names[i],
            "Planet": planet,
            "Intra-Sign Deg": round(intra, 4),
            "Sign": RASHI_SA[sign_idx],
            "Navamsha": RASHI_SA[nav_idx],
        })

    return results


def compute_karakamsha(
    chara_karakas: list[dict[str, Any]],
    numeric_lons: dict[str, float],
) -> dict[str, Any]:
    """
    Derive Karakamsha Lagna = Atmakaraka's Navamsha sign.

    Returns dict with karakamsha_sign (Sanskrit name) and sign index.
    """
    ak = next((r for r in chara_karakas if r["Karaka"] == "AK"), None)
    if ak is None:
        return {"karakamsha_sign": "Unknown", "karakamsha_idx": -1, "ak_planet": "Unknown"}

    ak_lon = numeric_lons.get(ak["Planet"], 0.0)
    nav_idx, _ = navamsa_for(ak_lon)
    return {
        "ak_planet": ak["Planet"],
        "karakamsha_sign": RASHI_SA[nav_idx],
        "karakamsha_idx": nav_idx,
    }
