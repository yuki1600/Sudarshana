# src/ci_match/kutas.py

from .constants import (
    GANA_TABLE, YONI_ANIMAL, RAJJU_GROUP, RASHI_LORDS, 
    FRIENDS, VEDHA_MAP, YONI_ENEMIES, PLANET_FRIENDLINESS
)
from .utils import get_rashi_idx

def check_dina(boy_nak, girl_nak):
    """
    Dina Kuta (3 points): Count from Girl to Boy. 
    Ideal: 2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26
    """
    count = (boy_nak - girl_nak) % 27 + 1
    # Standard rule: divide by 9, take remainder
    rem = count % 9
    
    # Good remainders: 0 (9), 2, 4, 6, 8
    # 0 here implies 9, 18, 27. 
    # Usually 27 (same nakshatra) is handled separately in some traditions, 
    # but strictly for Dina: 2,4,6,8,9 (0) are good.
    # Bad: 1, 3, 5, 7.
    
    # Exception: If remainder is 1 (Janma), it's generally bad, but compatible for specific pairs.
    # We will stick to basic rule for simplicity.
    
    if rem in [0, 2, 4, 6, 8]:
        return 3.0, "Good"
    else:
        # Special case: 27th usually considered bad in some texts if not same Pada
        # simplified view:
        return 0.0, "Bad"

def check_gana(boy_nak, girl_nak):
    """
    Gana Kuta (6 points): Temperament match (Deva / Manushya / Rakshasa).
    Max 6 points per Dashakoota standard.
    """
    g_gana = GANA_TABLE.get(girl_nak+1)
    b_gana = GANA_TABLE.get(boy_nak+1)
    
    if g_gana == b_gana:
        return 6.0, "Excellent"
    if {g_gana, b_gana} == {"Deva", "Manushya"}:
        return 5.0, "Good"
    return 0.0, "Bad"


def check_mahendra(boy_nak, girl_nak):
    """
    Mahendra (2 points): Wellbeing/Progeny.
    Count from Girl to Boy should be 4, 7, 10, 13, 16, 19, 22, 25.
    """
    count = (boy_nak - girl_nak) % 27 + 1
    if count in [4, 7, 10, 13, 16, 19, 22, 25]:
        return 2.0, "Good"
    return 0.0, "Bad"

def check_stree_deergha(boy_nak, girl_nak):
    """
    Stree Deergha (1 point): General welfare.
    Boy's nakshatra should be at least 13 away from Girl's (some say 7+ is passable).
    Strict: > 13.
    """
    count = (boy_nak - girl_nak) % 27 + 1
    if count > 13:
        return 1.0, "Good"
    if count > 7:
        return 0.5, "Average" # Partial
    return 0.0, "Bad"

def check_yoni(boy_nak, girl_nak):
    """
    Yoni (4 points): Sexual compatibility using Animal types.
    """
    g_ani = YONI_ANIMAL.get(girl_nak+1)
    b_ani = YONI_ANIMAL.get(boy_nak+1)
    
    if g_ani == b_ani: return 4.0, "Perfect"
    
    # Sworn Enemies (0 points)
    pair = {g_ani, b_ani}
    for e in YONI_ENEMIES:
        if pair == e:
            return 0.0, "Sworn Enemy"
            
    # If not sworn enemy or same, it typically ranges 1-3.
    return 2.0, "Neutral"

def check_rasi(boy_lon, girl_lon):
    """
    Rasi Kuta (7 points): Emotional compatibility.
    Based on Rasi position (count girl to boy).
    """
    g_rasi = get_rashi_idx(girl_lon)
    b_rasi = get_rashi_idx(boy_lon)
    
    # Refined logic using count (1-based from Girl):
    # Valid counts: 1, 3, 4, 7, 10, 11.
    count_from_girl = (b_rasi - g_rasi) % 12 + 1
    
    if count_from_girl in [1, 3, 4, 7, 10, 11]:
        return 7.0, "Good"
    return 0.0, "Bad"

def check_rasi_adhipati(boy_lon, girl_lon):
    """
    Rasi Adhipati (5 points): Lordship compatibility.
    """
    g_rasi = get_rashi_idx(girl_lon)
    b_rasi = get_rashi_idx(boy_lon)
    
    g_lord = RASHI_LORDS[g_rasi]
    b_lord = RASHI_LORDS[b_rasi]
    
    rel_g_to_b = PLANET_FRIENDLINESS[g_lord].get(b_lord, 1)
    rel_b_to_g = PLANET_FRIENDLINESS[b_lord].get(g_lord, 1)
    
    total = rel_g_to_b + rel_b_to_g
    
    if total == 4: # Friend-Friend
        return 5.0, "Excellent"
    if total == 3: # Friend-Neutral
        return 4.0, "Good"
    if total == 2:
        if rel_g_to_b == 1 and rel_b_to_g == 1:
            return 3.0, "Neutral"
        return 1.0, "Poor" # Friend-Enemy
    if total == 1: # Neutral-Enemy
        return 0.5, "Very Poor"
    return 0.0, "Bad" # Enemy-Enemy

def check_vashya(boy_lon, girl_lon):
    """
    Vashya (2 points): Mutual attraction/control.
    """
    # Placeholder: Return 1.0 (Average)
    return 1.0, "Average"

def check_rajju(boy_nak, girl_nak):
    """
    Rajju (Dosha check): If same Rajju group -> Bad. Different -> Good.
    Most important Kuta.
    """
    g_rajju = RAJJU_GROUP.get(girl_nak+1)
    b_rajju = RAJJU_GROUP.get(boy_nak+1)
    
    if g_rajju == b_rajju:
        return 0.0, f"Dosha ({g_rajju})" # Bad
    return 5.0, "Good" 

def check_vedha(boy_nak, girl_nak):
    """
    Vedha (Dosha): Mutually afflicted nakshatras.
    """
    b = boy_nak + 1
    g = girl_nak + 1
    
    if VEDHA_MAP.get(b) == g:
        return 0.0, "Dosha Present"
    return 1.0, "No Dosha"
