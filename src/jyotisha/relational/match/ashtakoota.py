# src/jyotisha/relational/match/ashtakoota.py

from .utils import get_rashi_idx
from .constants import GANA_TABLE, PLANET_FRIENDLINESS

# 1. Varna Groups (Brahmin=4, Kshatriya=3, Vaishya=2, Shudra=1)
VARNA_GRADES = {
    4: 4, 8: 4, 12: 4, # Water = Brahmin
    1: 3, 5: 3, 9: 3,  # Fire = Kshatriya
    2: 2, 6: 2, 10: 2, # Earth = Vaishya
    3: 1, 7: 1, 11: 1  # Air = Shudra
}

def check_varna(b_rasi, g_rasi):
    b_v = VARNA_GRADES.get(b_rasi, 1)
    g_v = VARNA_GRADES.get(g_rasi, 1)
    if b_v >= g_v:
        return 1.0, "Good"
    return 0.0, "Bad"

# 2. Vashya Groups (0=Chatushpada, 1=Manav, 2=Jalachar, 3=Vanachar, 4=Keeta)
VASHYA_GROUPS = {
    1: 0, 2: 0, 9: 0, 10: 0, # Chatushpada
    3: 1, 6: 1, 7: 1, 11: 1, # Manav
    4: 2, 12: 2,             # Jalachar
    5: 3,                    # Vanachar
    8: 4                     # Keeta
}

VASHYA_MATRIX = [
    # Chatu, Manav, Jala, Vana, Keeta
    [2.0,   1.0,   1.0,  0.5,  1.0],  # Chatushpada
    [1.0,   2.0,   0.5,  0.0,  1.0],  # Manav
    [1.0,   1.0,   2.0,  1.0,  1.0],  # Jalachar
    [1.0,   0.0,   0.0,  2.0,  0.0],  # Vanachar
    [1.0,   1.0,   1.0,  0.0,  2.0]   # Keeta
]

def check_ashtakoota_vashya(b_rasi, g_rasi):
    b_g = VASHYA_GROUPS.get(b_rasi, 0)
    g_g = VASHYA_GROUPS.get(g_rasi, 0)
    score = VASHYA_MATRIX[g_g][b_g]
    if score == 2.0:
        return 2.0, "Excellent"
    if score >= 1.0:
        return score, "Average"
    return score, "Bad"

# 3. Tara / Dina (max 3 points)
def check_ashtakoota_tara(b_nak, g_nak):
    count_g_to_b = (b_nak - g_nak) % 27 + 1
    count_b_to_g = (g_nak - b_nak) % 27 + 1
    
    r1 = count_g_to_b % 9
    r2 = count_b_to_g % 9
    if r1 == 0: r1 = 9
    if r2 == 0: r2 = 9
    
    malefics = {1, 3, 5, 7} # Janma, Vipat, Pratyak, Naidhana
    
    is_r1_mal = r1 in malefics
    is_r2_mal = r2 in malefics
    
    if is_r1_mal and is_r2_mal:
        return 0.0, "Bad"
    if is_r1_mal or is_r2_mal:
        return 1.5, "Average"
    return 3.0, "Good"

# 4. Yoni (max 4 points)
YONI_NAMES = [
    "Horse", "Elephant", "Sheep", "Serpent", "Dog", "Cat", "Rat",
    "Cow", "Buffalo", "Tiger", "Deer", "Monkey", "Mongoose", "Lion"
]

# Nakshatra (0-26) to Yoni Animal Index mapping
NAK_YONI_INDEX = {
    0: 0, 23: 0, # Horse
    1: 1, 26: 1, # Elephant
    2: 2, 7: 2,  # Sheep
    3: 3, 4: 3,  # Serpent
    5: 4, 18: 4, # Dog
    6: 5, 8: 5,  # Cat
    9: 6, 10: 6, # Rat
    11: 7, 25: 7,# Cow
    12: 8, 14: 8,# Buffalo
    13: 9, 15: 9,# Tiger
    16: 10, 17: 10,# Deer
    19: 11, 21: 11,# Monkey
    20: 12,      # Mongoose
    22: 13, 24: 13 # Lion
}

YONI_MATRIX = {
    "Horse":      [4, 2, 2, 3, 2, 2, 2, 3, 0, 1, 3, 3, 2, 1],
    "Elephant":   [2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0],
    "Sheep":      [2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1],
    "Serpent":    [3, 3, 2, 4, 2, 1, 1, 1, 2, 2, 2, 2, 0, 2],
    "Dog":        [2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1],
    "Cat":        [2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 2, 1, 2],
    "Rat":        [2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2],
    "Cow":        [3, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1],
    "Buffalo":    [0, 3, 3, 2, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1],
    "Tiger":      [1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 2],
    "Deer":       [3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 2],
    "Monkey":     [3, 3, 0, 2, 2, 2, 2, 2, 2, 1, 2, 4, 3, 2],
    "Mongoose":   [2, 2, 3, 0, 1, 1, 1, 2, 2, 2, 2, 3, 4, 2],
    "Lion":       [1, 0, 1, 2, 1, 2, 2, 1, 1, 2, 2, 2, 2, 4]
}

def check_ashtakoota_yoni(b_nak, g_nak):
    b_animal_idx = NAK_YONI_INDEX.get(b_nak, 0)
    g_animal_idx = NAK_YONI_INDEX.get(g_nak, 0)
    b_animal = YONI_NAMES[b_animal_idx]
    g_animal = YONI_NAMES[g_animal_idx]
    
    score = YONI_MATRIX[g_animal][b_animal_idx]
    
    if score == 4:
        return 4.0, "Perfect"
    if score == 3:
        return 3.0, "Friendly"
    if score == 2:
        return 2.0, "Neutral"
    if score == 1:
        return 1.0, "Unfriendly"
    return 0.0, "Sworn Enemy"

# 5. Graha Maitri (max 5 points)

RASHI_LORDS_1 = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
    7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

def check_graha_maitri(b_rasi, g_rasi):
    b_lord = RASHI_LORDS_1[b_rasi]
    g_lord = RASHI_LORDS_1[g_rasi]
    
    rel_g_to_b = PLANET_FRIENDLINESS[g_lord].get(b_lord, 1)
    rel_b_to_g = PLANET_FRIENDLINESS[b_lord].get(g_lord, 1)
    
    total = rel_g_to_b + rel_b_to_g
    
    if total == 4: # Friend-Friend
        return 5.0, "Excellent"
    if total == 3: # Friend-Neutral
        return 4.0, "Good"
    if total == 2:
        if rel_g_to_b == 1 and rel_b_to_g == 1:
            return 3.0, "Neutral" # Neutral-Neutral
        return 1.0, "Poor" # Friend-Enemy
    if total == 1: # Neutral-Enemy
        return 0.5, "Very Poor"
    return 0.0, "Bad" # Enemy-Enemy

# 6. Gana (max 6 points)
def check_ashtakoota_gana(b_nak, g_nak):
    g_gana = GANA_TABLE.get(g_nak + 1, "Deva")
    b_gana = GANA_TABLE.get(b_nak + 1, "Deva")
    
    if g_gana == b_gana:
        return 6.0, "Excellent"
    if {g_gana, b_gana} == {"Deva", "Manushya"}:
        return 5.0, "Good"
    return 0.0, "Bad"

# 7. Bhakoot (max 7 points)
def check_ashtakoota_bhakoot(b_rasi, g_rasi):
    count = (b_rasi - g_rasi) % 12 + 1
    if count in [1, 3, 4, 7, 10, 11]:
        return 7.0, "Good"
    return 0.0, "Bad"

# 8. Nadi (max 8 points)
ADI_NADI = {0, 5, 6, 11, 12, 17, 18, 23, 24}
MADHYA_NADI = {1, 4, 7, 10, 13, 16, 19, 22, 25}
ANTYA_NADI = {2, 3, 8, 9, 14, 15, 20, 21, 26}

def get_nadi_type(nak):
    if nak in ADI_NADI: return "Adi"
    if nak in MADHYA_NADI: return "Madhya"
    return "Antya"

def check_ashtakoota_nadi(b_nak, g_nak):
    b_n = get_nadi_type(b_nak)
    g_n = get_nadi_type(g_nak)
    
    if b_n != g_n:
        return 8.0, "Good"
    return 0.0, f"Dosha ({b_n})"
