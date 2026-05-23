"""
Panchabhutas (Five Elements) and Gunas (Three Qualities) — BPHS Ch. 76–77.

Each sign and planet carries an element (Agni/Jala/Prithvi/Vayu/Akasha)
and a guna (Sattva/Rajas/Tamas).

Aggregating these over the birth chart gives the native's elemental
temperament and psychological constitution.
"""

from __future__ import annotations
from typing import Any

from src.jyotisha.base.utils import lon_to_sign_idx

# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

# Sign → Element (by sign index 0–11, i.e. Aries=0 … Pisces=11)
# Fire signs: Aries(0), Leo(4), Sagittarius(8)
# Earth signs: Taurus(1), Virgo(5), Capricorn(9)
# Air signs: Gemini(2), Libra(6), Aquarius(10)
# Water signs: Cancer(3), Scorpio(7), Pisces(11)
# Ether (Akasha): traditionally associated with specific nakshatras;
#   at sign level we map Jupiter-ruled signs as having Akasha quality.
_SIGN_ELEMENT: dict[int, str] = {
    0: "Agni (Fire)",    # Aries
    1: "Prithvi (Earth)",# Taurus
    2: "Vayu (Air)",     # Gemini
    3: "Jala (Water)",   # Cancer
    4: "Agni (Fire)",    # Leo
    5: "Prithvi (Earth)",# Virgo
    6: "Vayu (Air)",     # Libra
    7: "Jala (Water)",   # Scorpio
    8: "Agni (Fire)",    # Sagittarius
    9: "Prithvi (Earth)",# Capricorn
    10: "Vayu (Air)",    # Aquarius
    11: "Jala (Water)",  # Pisces
}

# Sign → Guna
# Movable signs (Aries, Cancer, Libra, Capricorn) → Rajas
# Fixed signs (Taurus, Leo, Scorpio, Aquarius) → Tamas
# Dual signs (Gemini, Virgo, Sagittarius, Pisces) → Sattva
_SIGN_GUNA: dict[int, str] = {
    0: "Rajas", 1: "Tamas", 2: "Sattva",
    3: "Rajas", 4: "Tamas", 5: "Sattva",
    6: "Rajas", 7: "Tamas", 8: "Sattva",
    9: "Rajas", 10: "Tamas", 11: "Sattva",
}

# Planet → Element (natural signification)
_PLANET_ELEMENT: dict[str, str] = {
    "Sun":     "Agni (Fire)",
    "Moon":    "Jala (Water)",
    "Mars":    "Agni (Fire)",
    "Mercury": "Prithvi (Earth)",
    "Jupiter": "Akasha (Ether)",
    "Venus":   "Jala (Water)",
    "Saturn":  "Vayu (Air)",
    "Rahu (true)": "Vayu (Air)",
    "Ketu (true)": "Agni (Fire)",
}

# Planet → Guna
_PLANET_GUNA: dict[str, str] = {
    "Sun":     "Sattva",
    "Moon":    "Sattva",
    "Mars":    "Tamas",
    "Mercury": "Rajas",
    "Jupiter": "Sattva",
    "Venus":   "Rajas",
    "Saturn":  "Tamas",
    "Rahu (true)": "Tamas",
    "Ketu (true)": "Tamas",
}

_ALL_ELEMENTS = ["Agni (Fire)", "Prithvi (Earth)", "Vayu (Air)", "Jala (Water)", "Akasha (Ether)"]
_ALL_GUNAS = ["Sattva", "Rajas", "Tamas"]

_CLASSICAL = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
              "Rahu (true)", "Ketu (true)"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_elements_gunas(
    numeric_lons: dict[str, float],
) -> dict[str, Any]:
    """
    Compute elemental and guna profile for the chart.

    Returns:
        {
          "per_planet": [ {planet, element, guna, sign_element, sign_guna, sign} ],
          "element_counts": { "Agni": N, "Prithvi": N, ... },
          "guna_counts":    { "Sattva": N, "Rajas": N, "Tamas": N },
          "dominant_element": str,
          "dominant_guna": str,
        }
    """
    per_planet = []
    elem_counts: dict[str, int] = {e: 0 for e in _ALL_ELEMENTS}
    guna_counts: dict[str, int] = {g: 0 for g in _ALL_GUNAS}

    for planet in _CLASSICAL:
        if planet not in numeric_lons:
            continue
        lon = numeric_lons[planet]
        si = lon_to_sign_idx(lon)

        p_elem = _PLANET_ELEMENT.get(planet, "Unknown")
        p_guna = _PLANET_GUNA.get(planet, "Unknown")
        s_elem = _SIGN_ELEMENT.get(si, "Unknown")
        s_guna = _SIGN_GUNA.get(si, "Unknown")

        # Count both planet's intrinsic element AND sign element (weighted)
        for e in [p_elem, s_elem]:
            if e in elem_counts:
                elem_counts[e] += 1
        for g in [p_guna, s_guna]:
            if g in guna_counts:
                guna_counts[g] += 1

        from src.jyotisha.base.constants import RASHI_SA
        per_planet.append({
            "Planet": planet,
            "Planet Element": p_elem,
            "Planet Guna": p_guna,
            "Sign": RASHI_SA[si],
            "Sign Element": s_elem,
            "Sign Guna": s_guna,
        })

    dominant_element = max(elem_counts, key=lambda k: elem_counts[k])
    dominant_guna = max(guna_counts, key=lambda k: guna_counts[k])

    return {
        "per_planet": per_planet,
        "element_counts": elem_counts,
        "guna_counts": guna_counts,
        "dominant_element": dominant_element,
        "dominant_guna": dominant_guna,
    }
