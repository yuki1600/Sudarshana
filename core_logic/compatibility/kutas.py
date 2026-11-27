"""kutas: part of compatibility (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Dict, Optional, Any
from ..natal_chart import NAKSHATRA_NAMES, RASI_LORDS
from ..aspects_friendships import get_natural_relationship
from .tables import GANA_NAMES, MAITRI_LORDS, MAITRI_POINTS, NADI_NAMES, NAKSHATRA_GANA, NAKSHATRA_NADI, NAKSHATRA_YONI, SWORN_YONI_ENEMIES, VARNA_BY_RASI, VARNA_NAMES, VASHYA_MATRIX, VASHYA_NAMES, YONI_NAMES, YONI_POINTS, vashya_class

# ---------------------------------------------------------------------------
# 2. Individual Kuta Calculation Functions
# ---------------------------------------------------------------------------

def compute_varna_kuta(bride_rasi: int, groom_rasi: int) -> Dict[str, Any]:
    """
    Computes Varna Kuta (1 point max).
    Spiritual development and ego harmony.
    Groom's Varna must be equal or higher (lower index) than Bride's Varna.
    """
    b_v = VARNA_BY_RASI[bride_rasi % 12]
    g_v = VARNA_BY_RASI[groom_rasi % 12]
    
    if g_v <= b_v:
        points = 1.0
        status = "Favorable (Groom Varna is equal or superior)"
    else:
        points = 0.0
        status = "Unfavorable (Varna Anuloma deficit)"
        
    return {
        "kuta": "Varna",
        "max_points": 1.0,
        "obtained_points": points,
        "bride_varna": VARNA_NAMES[b_v],
        "groom_varna": VARNA_NAMES[g_v],
        "status": status
    }

def compute_vashya_kuta(bride_rasi: int, groom_rasi: int, bride_lon: Optional[float] = None, groom_lon: Optional[float] = None) -> Dict[str, Any]:
    """
    Computes Vashya Kuta (2 points max).
    Mutual magnetic attraction and natural deference. With the Moons' longitudes, Sagittarius and Capricorn split at 15°.
    """
    b_v = vashya_class(bride_rasi, bride_lon)
    g_v = vashya_class(groom_rasi, groom_lon)
    
    points = VASHYA_MATRIX[b_v][g_v]
    return {
        "kuta": "Vashya",
        "max_points": 2.0,
        "obtained_points": points,
        "bride_vashya": VASHYA_NAMES[b_v],
        "groom_vashya": VASHYA_NAMES[g_v],
        "status": "Favorable" if points >= 1.0 else "Weak"
    }

def compute_tara_kuta(bride_nak: int, groom_nak: int) -> Dict[str, Any]:
    """
    Computes Tara Kuta (Dina Kuta, 3 points max).
    Evaluates mutual auspiciousness of destiny stars.
    Bride to Groom gives 1.5 pts if in auspicious Tara.
    Groom to Bride gives 1.5 pts if in auspicious Tara.
    Auspicious Taras: 2 (Sampat), 4 (Kshema), 6 (Sadhana), 8 (Mitra), 9 (Parama Mitra).
    """
    dist_b_to_g = ((groom_nak - bride_nak) % 27) + 1
    dist_g_to_b = ((bride_nak - groom_nak) % 27) + 1
    
    tara_b_to_g = (dist_b_to_g % 9) or 9
    tara_g_to_b = (dist_g_to_b % 9) or 9
    
    auspicious = {2, 4, 6, 8, 9}
    
    p1 = 1.5 if tara_b_to_g in auspicious else 0.0
    p2 = 1.5 if tara_g_to_b in auspicious else 0.0
    
    total = 3.0 if tara_b_to_g == 1 else p1 + p2     # the 1st, 10th or 19th star (janma, anujanma, trijanma; 1 both ways): full, as the pada table gives it
    return {
        "kuta": "Tara",
        "max_points": 3.0,
        "obtained_points": total,
        "bride_to_groom_tara": tara_b_to_g,
        "groom_to_bride_tara": tara_g_to_b,
        "status": "Excellent" if total == 3.0 else ("Average" if total == 1.5 else "Inauspicious")
    }

def compute_yoni_kuta(bride_nak: int, groom_nak: int) -> Dict[str, Any]:
    """
    Computes Yoni Kuta (4 points max).
    Physical, biological, and intimate sexual harmony.
    Based on 14 animal classifications and natural enmity table.
    """
    b_y = NAKSHATRA_YONI[bride_nak % 27]
    g_y = NAKSHATRA_YONI[groom_nak % 27]
    
    points = float(YONI_POINTS[b_y][g_y])
    status = ("Same Yoni (Perfect Physical Harmony)" if b_y == g_y else "Sworn Enmity (Severe Yoni Dosha)" if (b_y, g_y) in SWORN_YONI_ENEMIES
              else "Friendly Yonis" if points >= 3 else "Neutral Yonis" if points == 2 else "Inimical Yonis")
            
    return {
        "kuta": "Yoni",
        "max_points": 4.0,
        "obtained_points": points,
        "bride_yoni": YONI_NAMES[b_y],
        "groom_yoni": YONI_NAMES[g_y],
        "status": status
    }

def compute_graha_maitri_kuta(bride_rasi: int, groom_rasi: int) -> Dict[str, Any]:
    """
    Computes Graha Maitri Kuta (5 points max).
    Mental outlook, communication, and psychological friendship
    between the ruling planets of the bride's and groom's Moon signs.
    """
    b_lord = RASI_LORDS[bride_rasi % 12]
    g_lord = RASI_LORDS[groom_rasi % 12]
    
    points = float(MAITRI_POINTS[MAITRI_LORDS.index(b_lord)][MAITRI_LORDS.index(g_lord)])
    if b_lord == g_lord:
        status = "Same Sign Lord (Perfect Psychological Harmony)"
    else:
        status = f"{get_natural_relationship(b_lord, g_lord)} / {get_natural_relationship(g_lord, b_lord)} Relationship"
        
    return {
        "kuta": "Graha Maitri",
        "max_points": 5.0,
        "obtained_points": points,
        "bride_lord": b_lord,
        "groom_lord": g_lord,
        "status": status
    }

def compute_gana_kuta(bride_nak: int, groom_nak: int) -> Dict[str, Any]:
    """
    Computes Gana Kuta (6 points max).
    Temperament, behavioral pattern, and social harmony.
    Deva (0), Manushya (1), Rakshasa (2).
    """
    b_g = NAKSHATRA_GANA[bride_nak % 27]
    g_g = NAKSHATRA_GANA[groom_nak % 27]
    
    if b_g == g_g:
        points = 6.0
        status = f"Both {GANA_NAMES[b_g]} (Excellent)"
    elif b_g == 1 and g_g == 0:
        points = 6.0
        status = "Manushya Bride - Deva Groom (Excellent)"
    elif b_g == 0 and g_g == 1:
        points = 5.0
        status = "Deva Bride - Manushya Groom (Good)"
    elif b_g == 2 and g_g == 0:
        points = 0.0
        status = "Rakshasa Bride - Deva Groom (Severe Gana Dosha)"
    elif b_g == 2 and g_g == 1:
        points = 0.0
        status = "Rakshasa Bride - Manushya Groom (Severe Gana Dosha)"
    elif b_g == 0 and g_g == 2:
        points = 1.0
        status = "Deva Bride - Rakshasa Groom (Partial Gana Dosha)"
    else:
        points = 0.0
        status = "Manushya Bride - Rakshasa Groom (Gana Dosha)"
        
    return {
        "kuta": "Gana",
        "max_points": 6.0,
        "obtained_points": points,
        "bride_gana": GANA_NAMES[b_g],
        "groom_gana": GANA_NAMES[g_g],
        "status": status
    }

def compute_bhakoota_kuta(bride_rasi: int, groom_rasi: int) -> Dict[str, Any]:
    """
    Computes Bhakoota Kuta (7 points max).
    Emotional welfare, family prosperity, and longevity of union.
    Favorable: 1/1, 3/11, 4/10, 5/9, 7/7 (7 points).
    Dosha:
      - 2/12 (Dwirdwadasa) -> Financial drain / sorrow
      - 6/8 (Shadashtaka) -> Strife / physical danger
      - 9/5 (Navapanchama) -> Loss of children / disharmony
    Classical Cancellations:
      - If sign lords are identical (Aries-Scorpio: Mars, Taurus-Libra: Venus)
      - If sign lords are mutual friends
    """
    b_r = bride_rasi % 12
    g_r = groom_rasi % 12
    
    dist_b_to_g = ((g_r - b_r) % 12) + 1
    dist_g_to_b = ((b_r - g_r) % 12) + 1
    
    pair = tuple(sorted([dist_b_to_g, dist_g_to_b]))
    
    is_dosha = pair in [(2, 12), (6, 8), (5, 9)]
    cancellation = False
    cancellation_reason = ""
    
    b_lord = RASI_LORDS[b_r]
    g_lord = RASI_LORDS[g_r]
    
    if is_dosha:
        if b_lord == g_lord:
            cancellation = True
            cancellation_reason = f"Cancelled: Same ruling lord ({b_lord})"
        else:
            rel1 = get_natural_relationship(b_lord, g_lord)
            rel2 = get_natural_relationship(g_lord, b_lord)
            if rel1 in ("Friend", "Neutral") and rel2 in ("Friend", "Neutral"):
                cancellation = True
                cancellation_reason = f"Cancelled: Friendly/Neutral lords ({b_lord} & {g_lord})"
                
    if not is_dosha:
        points = 7.0
        status = f"Favorable {pair[0]}/{pair[1]} Placement"
    elif cancellation:     # the points stay lost, as in the pada table: the cancellation is a note for the reader
        points = 0.0
        status = f"Bhakoota Dosha ({pair[0]}/{pair[1]}), but {cancellation_reason.lower()}"
    else:
        points = 0.0
        status = f"Bhakoota Dosha Active ({pair[0]}/{pair[1]} Inauspicious)"
        
    return {
        "kuta": "Bhakoota",
        "max_points": 7.0,
        "obtained_points": points,
        "placement": f"{pair[0]}/{pair[1]}",
        "has_dosha": is_dosha,
        "is_cancelled": cancellation,
        "cancellation_reason": cancellation_reason,
        "status": status
    }

def compute_nadi_kuta(
    bride_nak: int,
    groom_nak: int,
    bride_rasi: int,
    groom_rasi: int
) -> Dict[str, Any]:
    """
    Computes Nadi Kuta (8 points max).
    Genetic, hereditary, and physiological vitality.
    Adi (Vata), Madhya (Pitta), Antya (Kapha).
    Same Nadi causes Nadi Dosha (0 points).
    Exceptions:
      1. Different signs but same nakshatra (e.g. Krittika in Aries vs Taurus).
      2. Same sign but different nakshatras.
      3. Classical exempt nakshatras (Rohini, Mrigashira, Ardra, Punarvasu, Pushya, Shravana).
    """
    b_n = NAKSHATRA_NADI[bride_nak % 27]
    g_n = NAKSHATRA_NADI[groom_nak % 27]
    
    if b_n != g_n:
        points = 8.0
        status = f"Different Nadis ({NADI_NAMES[b_n]} & {NADI_NAMES[g_n]}) - Fully Auspicious"
        has_dosha = False
        is_cancelled = False
        reason = ""
    else:
        has_dosha = True
        is_cancelled = False
        reason = ""
        
        if (bride_nak % 27 == groom_nak % 27) and (bride_rasi % 12 != groom_rasi % 12):
            is_cancelled = True
            reason = "Cancelled: Same nakshatra in different rasis"
        elif (bride_rasi % 12 == groom_rasi % 12) and (bride_nak % 27 != groom_nak % 27):
            is_cancelled = True
            reason = "Cancelled: Different nakshatras in the same rasi"
        elif bride_nak % 27 in [3, 4, 5, 6, 7, 21]:
            is_cancelled = True
            reason = f"Cancelled: Special classical exemption for {NAKSHATRA_NAMES[bride_nak % 27]}"
            
        if is_cancelled:     # as Bhakoota: noted, not scored
            points = 0.0
            status = f"Nadi Dosha ({NADI_NAMES[b_n]}), but {reason.lower()}"
        else:
            points = 0.0
            status = f"Severe Nadi Dosha ({NADI_NAMES[b_n]} identical)"
            
    return {
        "kuta": "Nadi",
        "max_points": 8.0,
        "obtained_points": points,
        "bride_nadi": NADI_NAMES[b_n],
        "groom_nadi": NADI_NAMES[g_n],
        "has_dosha": has_dosha,
        "is_cancelled": is_cancelled,
        "cancellation_reason": reason,
        "status": status
    }
