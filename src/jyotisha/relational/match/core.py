# src/jyotisha/relational/match/core.py

from .constants import NAKSHATRAS
from .utils import get_nakshatra_idx, get_rashi_idx
from .kutas import (
    check_dina, check_gana, check_mahendra, check_stree_deergha,
    check_yoni, check_rasi, check_rasi_adhipati, check_vashya,
    check_rajju, check_vedha
)
from .ashtakoota import (
    check_varna, check_ashtakoota_vashya, check_ashtakoota_tara,
    check_ashtakoota_yoni, check_graha_maitri, check_ashtakoota_gana,
    check_ashtakoota_bhakoot, check_ashtakoota_nadi
)

def calculate_match(boy_lon_moon, girl_lon_moon):
    """
    Calculate compatibility using both Ashtakoota (8 Kutas) and Dashakoota (10 Kutas).
    """
    b_nak = get_nakshatra_idx(boy_lon_moon)
    g_nak = get_nakshatra_idx(girl_lon_moon)
    b_rasi = get_rashi_idx(boy_lon_moon)
    g_rasi = get_rashi_idx(girl_lon_moon)
    
    # ----------------------------------------------------
    # 1. Dashakoota (10 Poruthams)
    # ----------------------------------------------------
    d_dina, d_dina_stat = check_dina(b_nak, g_nak)
    d_gana, d_gana_stat = check_gana(b_nak, g_nak)
    d_mahendra, d_mahendra_stat = check_mahendra(b_nak, g_nak)
    d_stree, d_stree_stat = check_stree_deergha(b_nak, g_nak)
    d_yoni, d_yoni_stat = check_yoni(b_nak, g_nak)
    d_rasi_score, d_rasi_stat = check_rasi(boy_lon_moon, girl_lon_moon)
    d_rasilord, d_rasilord_stat = check_rasi_adhipati(boy_lon_moon, girl_lon_moon)
    d_vashya, d_vashya_stat = check_vashya(boy_lon_moon, girl_lon_moon)
    
    d_rajju, d_rajju_stat = check_rajju(b_nak, g_nak)
    d_vedha, d_vedha_stat = check_vedha(b_nak, g_nak)
    
    has_rajju_dosha = (d_rajju == 0.0)
    has_vedha_dosha = (d_vedha == 0.0)
    
    # All 10 kutas contribute to score (Rajju 5pts, Vedha 1pt awarded when clear)
    rajju_score = 5.0 if not has_rajju_dosha else 0.0
    vedha_score = 1.0 if not has_vedha_dosha else 0.0
    dashakoota_score = d_dina + d_gana + d_mahendra + d_stree + d_yoni + d_rasi_score + d_rasilord + d_vashya + rajju_score + vedha_score
    dashakoota_compatible = (dashakoota_score >= 18.0) and not has_rajju_dosha and not has_vedha_dosha
    
    # ----------------------------------------------------
    # 2. Ashtakoota (8 Kutas)
    # ----------------------------------------------------
    a_varna, a_varna_stat = check_varna(b_rasi, g_rasi)
    a_vashya, a_vashya_stat = check_ashtakoota_vashya(b_rasi, g_rasi)
    a_tara, a_tara_stat = check_ashtakoota_tara(b_nak, g_nak)
    a_yoni, a_yoni_stat = check_ashtakoota_yoni(b_nak, g_nak)
    a_maitri, a_maitri_stat = check_graha_maitri(b_rasi, g_rasi)
    a_gana, a_gana_stat = check_ashtakoota_gana(b_nak, g_nak)
    a_bhakoot, a_bhakoot_stat = check_ashtakoota_bhakoot(b_rasi, g_rasi)
    a_nadi, a_nadi_stat = check_ashtakoota_nadi(b_nak, g_nak)
    
    ashtakoota_score = a_varna + a_vashya + a_tara + a_yoni + a_maitri + a_gana + a_bhakoot + a_nadi
    has_nadi_dosha = (a_nadi == 0.0)
    has_bhakoot_dosha = (a_bhakoot == 0.0)
    
    ashtakoota_compatible = (ashtakoota_score >= 18.0) and not has_nadi_dosha
    
    # Legacy compatibility check (backward compatibility)
    legacy_kutas = {
        "dina": {"score": d_dina, "max": 3, "status": d_dina_stat},
        "gana": {"score": d_gana, "max": 6, "status": d_gana_stat},
        "mahendra": {"score": d_mahendra, "max": 2, "status": d_mahendra_stat},
        "stree_deergha": {"score": d_stree, "max": 1, "status": d_stree_stat},
        "yoni": {"score": d_yoni, "max": 4, "status": d_yoni_stat},
        "rasi": {"score": d_rasi_score, "max": 7, "status": d_rasi_stat},
        "rasi_lord": {"score": d_rasilord, "max": 5, "status": d_rasilord_stat},
        "vashya": {"score": d_vashya, "max": 2, "status": d_vashya_stat},
        "rajju": {"status": d_rajju_stat, "dosha": has_rajju_dosha},
        "vedha": {"status": d_vedha_stat, "dosha": has_vedha_dosha}
    }
    
    return {
        "boy_nak": NAKSHATRAS[b_nak],
        "girl_nak": NAKSHATRAS[g_nak],
        "boy_rasi": b_rasi,
        "girl_rasi": g_rasi,
        
        # Legacy/Flat response compatibility
        "kutas": legacy_kutas,
        "total_score": dashakoota_score,
        "is_compatible": dashakoota_compatible,
        
        # Unified Dual Structures
        "dashakoota": {
            "score": round(dashakoota_score, 1),
            "max": 36,
            "is_compatible": dashakoota_compatible,
            "kutas": {
                "dina": {"name": "Dina / Tara", "score": d_dina, "max": 3, "status": d_dina_stat, "desc": "Day-to-day fortune, health, and longevity"},
                "gana": {"name": "Gana", "score": d_gana, "max": 6, "status": d_gana_stat, "desc": "Mental temperament, behavior, and lifestyle"},
                "mahendra": {"name": "Mahendra", "score": d_mahendra, "max": 2, "status": d_mahendra_stat, "desc": "Progeny, family wealth, and legacy"},
                "stree_deergha": {"name": "Stree Deergha", "score": d_stree, "max": 1, "status": d_stree_stat, "desc": "Welfare, protection, and longevity of the woman"},
                "yoni": {"name": "Yoni", "score": d_yoni, "max": 4, "status": d_yoni_stat, "desc": "Physical and intimate sexual compatibility"},
                "rasi": {"name": "Rasi", "score": d_rasi_score, "max": 7, "status": d_rasi_stat, "desc": "Emotional matching, familial affinity, and harmony"},
                "rasi_lord": {"name": "Rasi Lord", "score": d_rasilord, "max": 5, "status": d_rasilord_stat, "desc": "Friendship of ruling planets, intellect, and respect"},
                "vashya": {"name": "Vashya", "score": d_vashya, "max": 2, "status": d_vashya_stat, "desc": "Mutual attraction, control, and dominance"},
                "rajju": {"name": "Rajju", "score": rajju_score, "max": 5, "status": d_rajju_stat, "dosha": has_rajju_dosha, "desc": "Longevity of spouse and absolute union of lives"},
                "vedha": {"name": "Vedha", "score": vedha_score, "max": 1, "status": d_vedha_stat, "dosha": has_vedha_dosha, "desc": "Obstacles, affliction, and spiritual interference"}
            }
        },
        
        "ashtakoota": {
            "score": ashtakoota_score,
            "max": 36,
            "is_compatible": ashtakoota_compatible,
            "kutas": {
                "varna": {"name": "Varna", "score": a_varna, "max": 1, "status": a_varna_stat, "desc": "Work temperament, spiritual grade, and ego compatibility"},
                "vashya": {"name": "Vashya", "score": a_vashya, "max": 2, "status": a_vashya_stat, "desc": "Mutual attraction, dominance, and willingness to submit"},
                "tara": {"name": "Tara / Dina", "score": a_tara, "max": 3, "status": a_tara_stat, "desc": "Destiny, health, and mutual longevity of the couple"},
                "yoni": {"name": "Yoni", "score": a_yoni, "max": 4, "status": a_yoni_stat, "desc": "Instinctive biological nature and sexual compatibility"},
                "graha_maitri": {"name": "Graha Maitri", "score": a_maitri, "max": 5, "status": a_maitri_stat, "desc": "Intellectual affinity, mental wavelength, and friendship"},
                "gana": {"name": "Gana", "score": a_gana, "max": 6, "status": a_gana_stat, "desc": "Temperament matching (Deva/Manushya/Rakshasa)"},
                "bhakoot": {"name": "Bhakoot", "score": a_bhakoot, "max": 7, "status": a_bhakoot_stat, "dosha": has_bhakoot_dosha, "desc": "Emotional attachment, love, longevity, and family harmony"},
                "nadi": {"name": "Nadi", "score": a_nadi, "max": 8, "status": a_nadi_stat, "dosha": has_nadi_dosha, "desc": "Genetic compatibility, progeny, health, and nervous systems"}
            }
        }
    }
