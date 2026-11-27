"""vimsopaka: part of shadbala (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Dict, Optional, Any
from ..natal_chart import EXALTATION, DEBILITATION, OWN_SIGNS, compute_all_vargas
from ..aspects_friendships import get_natural_relationship
from .common import SIGN_RULERS

# ===========================================================================
# 9. Vimsopaka Bala (Divisional Dignity Strength)
# Source: BPHS 7.17-27 (Vimsopaka); the Vaiseshikamsa names BPHS 6.42-53
# ===========================================================================

# Canonical weights for Vimsopaka schemes (Total sum = 20.0)
VIMSOPAKA_SCHEMES = {
    "Shadvarga": {
        "D1": 6.0, "D2": 2.0, "D3": 4.0, "D9": 5.0, "D12": 2.0, "D30": 1.0
    },
    "Saptavarga": {
        "D1": 5.0, "D2": 2.0, "D3": 3.0, "D7": 2.5, "D9": 4.5, "D12": 2.0, "D30": 1.0
    },
    "Dasavarga": {
        "D1": 3.0, "D2": 1.5, "D3": 1.5, "D7": 1.5, "D9": 1.5,
        "D10": 1.5, "D12": 1.5, "D16": 1.5, "D30": 1.5, "D60": 5.0
    },
    "Shodashavarga": {
        "D1": 3.5, "D2": 1.0, "D3": 1.0, "D4": 0.5, "D7": 0.5,
        "D9": 3.0, "D10": 0.5, "D12": 0.5, "D16": 2.0, "D20": 0.5,
        "D24": 0.5, "D27": 0.5, "D30": 1.0, "D40": 0.5, "D45": 0.5, "D60": 4.0
    }
}

# Dignity points out of 20 Virupas per division
DIGNITY_POINTS = {
    "Exalted": 20.0,
    "Moolatrikona": 20.0,
    "Own": 20.0,
    "Great Friend": 18.0,
    "Friend": 15.0,
    "Neutral": 10.0,
    "Enemy": 7.0,
    "Bitter Enemy": 5.0,
    "Debilitated": 0.0
}

def compute_vimsopaka_bala(
    planet: str,
    planet_lon: float,
    planetary_signs: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Computes Vimsopaka Bala across 4 canonical Parasari schemes:
    - Shadvarga (6 vargas, max 20)
    - Saptavarga (7 vargas, max 20)
    - Dasavarga (10 vargas, max 20)
    - Shodashavarga (16 vargas, max 20)
    """
    moolatrikona_signs = {
        "Sun": 4, "Moon": 1, "Mars": 0, "Mercury": 5,
        "Jupiter": 8, "Venus": 6, "Saturn": 10
    }

    vargas = compute_all_vargas(planet_lon)
    
    # Evaluate dignity of the planet in each varga
    varga_dignities = {}
    for vid, vdata in vargas.items():
        v_sign = vdata.get("sign_idx", vdata.get("sign_index", 0))
        lord = SIGN_RULERS[v_sign]
        
        ex_s, _ = EXALTATION.get(planet, (-1, 0))
        deb_s, _ = DEBILITATION.get(planet, (-1, 0))
        own_s = OWN_SIGNS.get(planet, [])
        mt_s = moolatrikona_signs.get(planet, -1)
        
        if v_sign == ex_s:
            dignity = "Exalted"
        elif v_sign == deb_s:
            dignity = "Debilitated"
        elif v_sign == mt_s:
            dignity = "Moolatrikona"
        elif v_sign in own_s:
            dignity = "Own"
        else:
            rel = get_natural_relationship(planet, lord)
            if rel == "Friend":
                dignity = "Friend"
            elif rel == "Enemy":
                dignity = "Enemy"
            else:
                dignity = "Neutral"
                
        pts = DIGNITY_POINTS.get(dignity, 10.0)
        varga_dignities[vid] = {
            "varga": vid,
            "sign_index": v_sign,
            "sign_lord": lord,
            "dignity": dignity,
            "raw_points": pts
        }
        
    scheme_scores = {}
    for s_name, weights in VIMSOPAKA_SCHEMES.items():
        weighted_sum = 0.0
        total_w = sum(weights.values())
        for vid, w in weights.items():
            if vid in varga_dignities:
                weighted_sum += (varga_dignities[vid]["raw_points"] / 20.0) * w
        scheme_scores[s_name] = round((weighted_sum / total_w) * 20.0, 2)
        
    vaiseshikamsa = compute_vaiseshikamsa(varga_dignities)

    return {
        "planet": planet,
        "scheme_scores": scheme_scores,
        "varga_dignities": varga_dignities,
        "vaiseshikamsa": vaiseshikamsa
    }

VAISESHIKAMSA_DASA_NAMES = {
    2: "Parijata", 3: "Uttama", 4: "Gopura", 5: "Simhasana",
    6: "Paravata", 7: "Devaloka", 8: "Brahmaloka", 9: "Sakravahana", 10: "Sridhama"
}

VAISESHIKAMSA_SHODASA_NAMES = {
    2: "Bhedaka", 3: "Kusuma", 4: "Nagapushpa", 5: "Kandali",
    6: "Kerala", 7: "Kalpavriksha", 8: "Chandanavana", 9: "PoornaChandra",
    10: "Uchchaisrava", 11: "Dhanvantari", 12: "Suryakanta", 13: "Vidruma",
    14: "Sakrasana", 15: "Goloka", 16: "Sri Vallabha"
}

VAISESHIKAMSA_SHAD_NAMES = {
    2: "Kimsuka", 3: "Vyanjana", 4: "Chamara", 5: "Chhatra", 6: "Kundala"
}

def compute_vaiseshikamsa(varga_dignities: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes classical Vaiseshikamsa planetary dignity attainments across varga groups.
    Source: BPHS 6.42-53:
    Counts auspicious divisions (Exalted, Moolatrikona, Own, Friend).
    """
    good_dignities = {"Exalted", "Moolatrikona", "Own", "Friend"}
    
    # 1. Dasa Varga (10 harmonic vargas)
    dasa_vargas = ["D1", "D2", "D3", "D7", "D9", "D10", "D12", "D16", "D30", "D60"]
    good_dasa = sum(1 for v in dasa_vargas if v in varga_dignities and varga_dignities[v]["dignity"] in good_dignities)
    dasa_tier = VAISESHIKAMSA_DASA_NAMES.get(good_dasa, "Ordinary" if good_dasa < 2 else "Sridhama")

    # 2. Shodasa Varga (16 harmonic vargas)
    shodasa_vargas = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D60"]
    good_shodasa = sum(1 for v in shodasa_vargas if v in varga_dignities and varga_dignities[v]["dignity"] in good_dignities)
    shodasa_tier = VAISESHIKAMSA_SHODASA_NAMES.get(good_shodasa, "Ordinary" if good_shodasa < 2 else "Sri Vallabha")

    # 3. Shad Varga (6 vargas)
    shad_vargas = ["D1", "D2", "D3", "D9", "D12", "D30"]
    good_shad = sum(1 for v in shad_vargas if v in varga_dignities and varga_dignities[v]["dignity"] in good_dignities)
    shad_tier = VAISESHIKAMSA_SHAD_NAMES.get(good_shad, "Ordinary" if good_shad < 2 else "Kundala")

    return {
        "dasa_varga": {
            "good_vargas_count": good_dasa,
            "total_vargas": len(dasa_vargas),
            "tier_name": dasa_tier
        },
        "shodasa_varga": {
            "good_vargas_count": good_shodasa,
            "total_vargas": len(shodasa_vargas),
            "tier_name": shodasa_tier
        },
        "shad_varga": {
            "good_vargas_count": good_shad,
            "total_vargas": len(shad_vargas),
            "tier_name": shad_tier
        }
    }
