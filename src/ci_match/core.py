# src/ci_match/core.py

from .constants import NAKSHATRAS
from .utils import get_nakshatra_idx, get_rashi_idx
from .kutas import (
    check_dina, check_gana, check_mahendra, check_stree_deergha,
    check_yoni, check_rasi, check_rasi_adhipati, check_vashya,
    check_rajju, check_vedha
)

def calculate_match(boy_lon_moon, girl_lon_moon):
    """
    Calculate 10 Poruthams and final score.
    Returns dict.
    """
    # Get Nakshatra Indexes (0-26)
    b_nak = get_nakshatra_idx(boy_lon_moon)
    g_nak = get_nakshatra_idx(girl_lon_moon)
    
    # Calculate
    score_dina, stat_dina = check_dina(b_nak, g_nak)
    score_gana, stat_gana = check_gana(b_nak, g_nak)
    score_mahendra, stat_mahendra = check_mahendra(b_nak, g_nak)
    score_stree, stat_stree = check_stree_deergha(b_nak, g_nak)
    score_yoni, stat_yoni = check_yoni(b_nak, g_nak)
    score_rasi, stat_rasi = check_rasi(boy_lon_moon, girl_lon_moon)
    score_rasilord, stat_rasilord = check_rasi_adhipati(boy_lon_moon, girl_lon_moon)
    score_vashya, stat_vashya = check_vashya(boy_lon_moon, girl_lon_moon)
    
    # Doshas (Score 0 or 1 used for flag, but strictly boolean)
    score_rajju, stat_rajju = check_rajju(b_nak, g_nak) # 0 means Bad!
    score_vedha, stat_vedha = check_vedha(b_nak, g_nak) # 0 means Bad!
    
    # Total Score
    total_points = score_dina + score_gana + score_mahendra + score_stree + score_yoni + score_rasi + score_rasilord + score_vashya
    
    has_rajju_dosha = (score_rajju == 0.0)
    has_vedha_dosha = (score_vedha == 0.0)
    
    return {
        "boy_nak": NAKSHATRAS[b_nak],
        "girl_nak": NAKSHATRAS[g_nak],
        "boy_rasi": get_rashi_idx(boy_lon_moon),
        "girl_rasi": get_rashi_idx(girl_lon_moon),
        "kutas": {
            "dina": {"score": score_dina, "max": 3, "status": stat_dina},
            "gana": {"score": score_gana, "max": 4, "status": stat_gana},
            "mahendra": {"score": score_mahendra, "max": 0, "status": stat_mahendra}, # Max 0 as flag kuta
            "stree_deergha": {"score": score_stree, "max": 1, "status": stat_stree},
            "yoni": {"score": score_yoni, "max": 4, "status": stat_yoni},
            "rasi": {"score": score_rasi, "max": 7, "status": stat_rasi},
            "rasi_lord": {"score": score_rasilord, "max": 5, "status": stat_rasilord},
            "vashya": {"score": score_vashya, "max": 2, "status": stat_vashya},
            "rajju": {"status": stat_rajju, "dosha": has_rajju_dosha},
            "vedha": {"status": stat_vedha, "dosha": has_vedha_dosha}
        },
        "total_score": total_points,
        "is_compatible": (total_points > 18) and not has_rajju_dosha and not has_vedha_dosha
    }
