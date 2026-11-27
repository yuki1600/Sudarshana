"""matching: part of compatibility (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Dict, Any
from ..utils import norm360
from ..natal_chart import NAKSHATRA_NAMES, RASI_NAMES_EN
from .ancillary import compute_ancillary_kootas, compute_dashakoota
from .kutas import compute_bhakoota_kuta, compute_gana_kuta, compute_graha_maitri_kuta, compute_nadi_kuta, compute_tara_kuta, compute_varna_kuta, compute_vashya_kuta, compute_yoni_kuta
from .kuja import evaluate_kuja_dosha

# ---------------------------------------------------------------------------
# 5. Master Horoscope Matching Pipeline
# ---------------------------------------------------------------------------

def evaluate_horoscope_matching(
    bride_data: Dict[str, Any],
    groom_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Executes complete Horoscope Matching (Ashta Kuta + Ancillary Kutas + Kuja Dosha).
    
    bride_data / groom_data:
    {
        "moon_longitude": float,
        "lagna_longitude": Optional[float],
        "planet_longitudes": Optional[Dict[str, float]],
        "mars_bhavas": Optional[Dict[str, int]],    # Mars's bhava from Lagna, Moon, Venus (evaluate_kuja_dosha)
        "name": Optional[str]
    }
    
    Returns:
    - gunanka_score: float (0.0 to 36.0)
    - match_level: "Below Average", "Average", "Fair", "Good", "Excellent"
    - ashta_kuta_breakdown: detailed scores for all 8 factors
    - ancillary_kootas: Mahendra, Stree Deergha, Rajju, Vedha
    - kuja_dosha: mutual Kuja Dosha balance
    """
    nak_span = 360.0 / 27.0
    
    b_lon = norm360(bride_data["moon_longitude"])
    g_lon = norm360(groom_data["moon_longitude"])
    
    b_nak = int(b_lon // nak_span)
    g_nak = int(g_lon // nak_span)
    
    b_rasi = int(b_lon // 30.0)
    g_rasi = int(g_lon // 30.0)
    
    varna = compute_varna_kuta(b_rasi, g_rasi)
    vashya = compute_vashya_kuta(b_rasi, g_rasi, b_lon, g_lon)
    tara = compute_tara_kuta(b_nak, g_nak)
    yoni = compute_yoni_kuta(b_nak, g_nak)
    maitri = compute_graha_maitri_kuta(b_rasi, g_rasi)
    gana = compute_gana_kuta(b_nak, g_nak)
    bhakoota = compute_bhakoota_kuta(b_rasi, g_rasi)
    nadi = compute_nadi_kuta(b_nak, g_nak, b_rasi, g_rasi)
    
    total_score = (
        varna["obtained_points"] +
        vashya["obtained_points"] +
        tara["obtained_points"] +
        yoni["obtained_points"] +
        maitri["obtained_points"] +
        gana["obtained_points"] +
        bhakoota["obtained_points"] +
        nadi["obtained_points"]
    )
    
    # the usual bands (31+ excellent, 21-30 very good, 17-20 middling); a Bhakoota dosha keeps it from excellent
    if total_score >= 31.0 and bhakoota["obtained_points"]:
        match_level = "Excellent"
    elif total_score >= 21.0:
        match_level = "Very Good"
    elif total_score >= 17.0:
        match_level = "Middling"
    else:
        match_level = "Inauspicious"
        
    ancillary = compute_ancillary_kootas(b_nak, g_nak)
    
    b_kuja = {"status": "Not calculated"}
    g_kuja = {"status": "Not calculated"}
    kuja_balance = "Unknown"
    
    if "planet_longitudes" in bride_data and "lagna_longitude" in bride_data:
        b_kuja = evaluate_kuja_dosha(bride_data["planet_longitudes"], bride_data["lagna_longitude"], bride_data.get("mars_bhavas"), bride_data.get("aspect_parasara", True))
    if "planet_longitudes" in groom_data and "lagna_longitude" in groom_data:
        g_kuja = evaluate_kuja_dosha(groom_data["planet_longitudes"], groom_data["lagna_longitude"], groom_data.get("mars_bhavas"), groom_data.get("aspect_parasara", True))
        
    if "has_kuja_dosha" in b_kuja and "has_kuja_dosha" in g_kuja:
        b_act = b_kuja["has_kuja_dosha"] and not b_kuja["is_cancelled"]
        g_act = g_kuja["has_kuja_dosha"] and not g_kuja["is_cancelled"]
        if b_act and g_act:
            kuja_balance = "Balanced (Both partners have active Kuja Dosha)"
        elif not b_act and not g_act:
            kuja_balance = "Harmonious (Neither partner has active Kuja Dosha)"
        elif b_act:
            kuja_balance = "Imbalanced (Bride has active Kuja Dosha)"
        else:
            kuja_balance = "Imbalanced (Groom has active Kuja Dosha)"
            
    return {
        "gunanka_score": round(total_score, 1),
        "max_score": 36.0,
        "match_level": match_level,
        "bride": {
            "name": bride_data.get("name", "Bride"),
            "moon_rasi": RASI_NAMES_EN[b_rasi],
            "nakshatra": NAKSHATRA_NAMES[b_nak]
        },
        "groom": {
            "name": groom_data.get("name", "Groom"),
            "moon_rasi": RASI_NAMES_EN[g_rasi],
            "nakshatra": NAKSHATRA_NAMES[g_nak]
        },
        "ashta_kuta_breakdown": {
            "varna": varna,
            "vashya": vashya,
            "tara": tara,
            "yoni": yoni,
            "graha_maitri": maitri,
            "gana": gana,
            "bhakoota": bhakoota,
            "nadi": nadi
        },
        "ancillary_kootas": ancillary,
        "dashakoota": compute_dashakoota(b_nak, g_nak, b_rasi, g_rasi),
        "kuja_dosha": {
            "bride": b_kuja,
            "groom": g_kuja,
            "balance_status": kuja_balance
        }
    }
