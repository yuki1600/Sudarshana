"""
core_logic/aspects_friendships.py
=================================
Modularized Calculation Engine for Planetary Aspects (Graha Drishti), Aspect Orbs & Percentages,
Natural Friendships (Naisargika Maitri), Temporary Friendships (Tatkalika Maitri),
Compound Relationships (Panchadha Maitri), and Sambandha.

Sources (docs/SOURCES.md sections 2 and 6): natural, temporary and compound relationships BPHS 3.55-58; graha
drishti and its virupas BPHS 26.2-12 with B. V. Raman's reading of the special aspects (Graha and Bhava Balas,
sections 109-120); rasi drishti BPHS 8.1-5.
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional, Any

from .natal_chart import EXALTATION, MOOLATRIKONA, norm360, RASI_NAMES_EN, RASI_LORDS

# Standard 9 Grahas used in classical Maitri and Drishti
GRAHA_LIST = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# ===========================================================================
# 1. Natural Friendships (Naisargika Maitri), BPHS 3.55
# The friends of a graha are the lords of the 2nd, 4th, 5th, 8th, 9th and 12th from its moolatrikona sign and the
# lord of its exaltation sign; the lords of the other signs are its enemies; a lord that is both is neutral.  The
# seven grahas' table is computed from that rule.  Rahu and Ketu: BPHS 3.55 covers the seven only, so their rows and
# columns are the table in common use (Ketu's row the same as Rahu's), a convention (docs/SOURCES.md section 2).
# Encoding:
#  2: Mitra (Friend)
#  3: Sama (Neutral)
#  4: Satru (Enemy)
#  0: Svakshetra / Self
# ===========================================================================

# Rahu and Ketu's columns of the seven grahas' rows (Rahu, Ketu), and the nodes' own row
_NODE_COLUMNS = {"Sun": (4, 4), "Moon": (4, 4), "Mars": (4, 2), "Mercury": (3, 3), "Jupiter": (3, 3), "Venus": (2, 2),
                 "Saturn": (2, 4)}
_NODE_ROW = (4, 4, 4, 3, 3, 2, 2, 0, 2)


def _bphs_natural_row(p: str) -> List[int]:
    mt, ex = MOOLATRIKONA[p][0], EXALTATION[p][0]
    friend = {RASI_LORDS[(mt + h - 1) % 12] for h in (2, 4, 5, 8, 9, 12)} | {RASI_LORDS[ex]}
    enemy = {RASI_LORDS[(mt + h - 1) % 12] for h in (1, 3, 6, 7, 10, 11)}
    return [0 if q == p else 3 if q in friend and q in enemy else 2 if q in friend else 4
            for q in GRAHA_LIST[:7]] + list(_NODE_COLUMNS[p])


# Matrix rows and columns: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
NAISARGIKA_MATRIX = [_bphs_natural_row(p) for p in GRAHA_LIST[:7]] + [list(_NODE_ROW), list(_NODE_ROW)]

REL_NAME_MAP = {
    2: "Friend",
    3: "Neutral",
    4: "Enemy",
    0: "Self"
}

def get_natural_relationship(p1: str, p2: str) -> str:
    """
    Returns natural friendship ('Friend', 'Neutral', 'Enemy', 'Self')
    of p1 towards p2 according to Brihat Parasara Hora Shastra 3.55 (the nodes by convention).
    """
    if p1 == p2:
        return "Self"
    if p1 not in GRAHA_LIST or p2 not in GRAHA_LIST:
        return "Neutral"
    idx1 = GRAHA_LIST.index(p1)
    idx2 = GRAHA_LIST.index(p2)
    val = NAISARGIKA_MATRIX[idx1][idx2]
    return REL_NAME_MAP.get(val, "Neutral")


# ===========================================================================
# 2. Temporary Friendships (Tatkalika Maitri), BPHS 3.56:
# Planets situated in 2nd, 3rd, 4th, 10th, 11th, 12th from reference planet
# are Temporary Friends (+1). In 1st, 5th, 6th, 7th, 8th, 9th are Enemies (-1).
# ===========================================================================

TATKALIKA_FRIEND_HOUSES = {2, 3, 4, 10, 11, 12}

def compute_tatkalika_relationship(p1_sign: int, p2_sign: int) -> str:
    """
    Computes temporary relationship between two planets based on their rasi positions.
    House is 1-based distance from p1 to p2.
    """
    house = ((p2_sign - p1_sign) % 12) + 1
    if house in TATKALIKA_FRIEND_HOUSES:
        return "Temporary Friend"
    return "Temporary Enemy"


# ===========================================================================
# 3. Five-Fold Compound Relationships (Panchadha Maitri), BPHS 3.57-58:
# Natural (Friend, Neutral, Enemy) + Temporary (Friend, Enemy)
# ===========================================================================

COMPOUND_RELATIONSHIP_SCORES = {
    ("Friend", "Temporary Friend"):  (2, "Great Friend", "Ati-Mitra"),
    ("Friend", "Temporary Enemy"):   (0, "Neutral",      "Sama"),
    ("Neutral", "Temporary Friend"): (1, "Friend",       "Mitra"),
    ("Neutral", "Temporary Enemy"):  (-1, "Enemy",       "Satru"),
    ("Enemy", "Temporary Friend"):   (0, "Neutral",      "Sama"),
    ("Enemy", "Temporary Enemy"):    (-2, "Great Enemy", "Ati-Satru"),
    ("Self", "Temporary Friend"):    (1, "Friend",       "Mitra"),
    ("Self", "Temporary Enemy"):     (-1, "Enemy",       "Satru"),
}

def compute_panchadha_maitri(
    p1: str,
    p2: str,
    p1_sign: int,
    p2_sign: int
) -> Dict[str, Any]:
    """
    Computes complete 5-fold compound friendship (Panchadha Maitri) of p1 towards p2.
    It is kept per varga; with CompoundRelationshipsFromRasi every varga uses the rasi chart's (pass the rasi
    signs here for that).
    """
    if p1 == p2:
        return {
            "planet_1": p1,
            "planet_2": p2,
            "natural": "Self",
            "temporary": "Self",
            "compound_score": 0,
            "compound_name_en": "Self",
            "compound_name_sa": "Svastha"
        }
    
    natural = get_natural_relationship(p1, p2)
    temporary = compute_tatkalika_relationship(p1_sign, p2_sign)
    score, en_name, sa_name = COMPOUND_RELATIONSHIP_SCORES.get(
        (natural, temporary), (0, "Neutral", "Sama")
    )
    
    return {
        "planet_1": p1,
        "planet_2": p2,
        "natural": natural,
        "temporary": temporary,
        "compound_score": score,
        "compound_name_en": en_name,
        "compound_name_sa": sa_name
    }

def compute_all_planetary_friendships(
    planetary_signs: Dict[str, int]
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Generates the complete N x N friendship matrix for all available planets.
    """
    res: Dict[str, Dict[str, Dict[str, Any]]] = {}
    planets = [p for p in GRAHA_LIST if p in planetary_signs]
    
    for p1 in planets:
        res[p1] = {}
        s1 = planetary_signs[p1]
        for p2 in planets:
            s2 = planetary_signs[p2]
            res[p1][p2] = compute_panchadha_maitri(p1, p2, s1, s2)
            
    return res


# ===========================================================================
# 4. Planetary Aspects (Graha Drishti) & Exact Virupas / Percentages
# Classical rules (BPHS 26.2-12). The 0..100 curve of the Key Info views is shadbala.aspect_value.
# ===========================================================================

# Special full aspects (60 virupas / 100%):
# All grahas cast full aspect on 7th house (180°).
# Mars has special full aspect on 4th (90°) and 8th (210°).
# Jupiter has special full aspect on 5th (120°) and 9th (240°).
# Saturn has special full aspect on 3rd (60°) and 10th (270°).
# Rahu & Ketu cast aspect on 5th, 9th, and 12th houses: a convention (BPHS 26 gives the special aspects of Mars,
# Jupiter and Saturn only).

SPECIAL_ASPECT_HOUSES: Dict[str, List[int]] = {
    "Sun":     [7],
    "Moon":    [7],
    "Mars":    [4, 7, 8],
    "Mercury": [7],
    "Jupiter": [5, 7, 9],
    "Venus":   [7],
    "Saturn":  [3, 7, 10],
    "Rahu":    [5, 7, 9, 12],
    "Ketu":    [5, 7, 9, 12],
}

# Special-aspect bonus (virupas) and the angular range it applies to (Dr. B.V. Raman,
# "Graha and Bhava Balas", sections 109-120, the visesha dristi; the standard Shadbala drik-bala rule).
_SPECIAL_ASPECT_BONUS = {
    "Mars": (15.0, ((90.0, 120.0), (210.0, 240.0))),      # 4th and 8th
    "Jupiter": (30.0, ((120.0, 150.0), (240.0, 270.0))),  # 5th and 9th
    "Saturn": (45.0, ((60.0, 90.0), (270.0, 300.0))),     # 3rd and 10th
}


def compute_parasara_drik_virupas(diff_deg: float, planet: str = "Jupiter", full_aspect: float = 60.0) -> float:
    """
    Sphuta drishti (aspect strength) of a planet on a point ``diff_deg`` ahead of it
    (BPHS Ch. 26): 0 at 0-30 deg, rising to 15 at 60, 45 at 90, 30 at 120, 0 at 150, full (60)
    at 180, then falling linearly to 0 at 300.  Mars, Jupiter and Saturn add 15/30/45 virupas
    in their special-aspect ranges, which makes their 4/8, 5/9 and 3/10 aspects full.
    ``full_aspect`` rescales the result (60 or 100 as the full value).
    """
    d = norm360(diff_deg)
    if d < 30.0 or d >= 300.0:
        virupas = 0.0
    elif d < 60.0:
        virupas = (d - 30.0) / 2.0
    elif d < 90.0:
        virupas = d - 60.0 + 15.0
    elif d < 120.0:
        virupas = (120.0 - d) / 2.0 + 30.0
    elif d < 150.0:
        virupas = 150.0 - d
    elif d < 180.0:
        virupas = (d - 150.0) * 2.0
    else:
        virupas = (300.0 - d) / 2.0

    bonus, ranges = _SPECIAL_ASPECT_BONUS.get(planet, (0.0, ()))
    if any(lo <= d < hi for lo, hi in ranges):
        virupas += bonus

    return max(0.0, min(60.0, virupas)) * full_aspect / 60.0

def compute_aspect_details(
    p1: str,
    p1_lon: float,
    p2: str,
    p2_lon: float,
    orb_limit_deg: float = 12.0
) -> Dict[str, Any]:
    """
    Computes exact aspect from planet p1 to target planet / body p2.
    Includes house aspect, angular distance, exact Virupas, aspect percentage, and orb.
    """
    diff = norm360(p2_lon - p1_lon)
    house_dist = int(diff // 30.0) + 1
    
    special_houses = SPECIAL_ASPECT_HOUSES.get(p1, [7])
    is_special_full_house = house_dist in special_houses
    
    virupas = compute_parasara_drik_virupas(diff, planet=p1)
    aspect_percentage = (virupas / 60.0) * 100.0
    
    # Check orb from nearest aspect center (30°, 60°, 90°, 120°, 150°, 180°, etc.)
    nearest_aspect_center = round(diff / 30.0) * 30.0
    orb = abs(diff - nearest_aspect_center)
    is_within_orb = orb <= orb_limit_deg

    return {
        "aspecting_planet": p1,
        "aspected_body": p2,
        "angular_difference": diff,
        "house_distance": house_dist,
        "is_full_aspect_house": is_special_full_house,
        "virupas": round(virupas, 2),
        "aspect_percentage": round(aspect_percentage, 1),
        "nearest_aspect_center": nearest_aspect_center,
        "orb_deg": round(orb, 2),
        "is_within_orb": is_within_orb
    }


# ===========================================================================
# 5. Jaimini Rasi Drishti (Sign Aspects)
# - Movable signs aspect all Fixed signs except the adjacent one.
# - Fixed signs aspect all Movable signs except the adjacent one.
# - Dual signs aspect all other Dual signs.
# ===========================================================================

def compute_rasi_drishti(sign_index: int) -> List[int]:
    """
    Returns list of sign indices (0..11) aspected by the given sign via Jaimini Rasi Drishti.
    """
    mod3 = sign_index % 3
    aspected: List[int] = []
    
    if mod3 == 0:
        # Movable (Aries, Cancer, Libra, Capricorn)
        # Aspects all Fixed signs except the adjacent one
        adjacent_fixed = (sign_index + 1) % 12
        for s in [1, 4, 7, 10]:
            if s != adjacent_fixed:
                aspected.append(s)
    elif mod3 == 1:
        # Fixed (Taurus, Leo, Scorpio, Aquarius)
        # Aspects all Movable signs except the adjacent one
        adjacent_movable = (sign_index - 1) % 12
        for s in [0, 3, 6, 9]:
            if s != adjacent_movable:
                aspected.append(s)
    else:
        # Dual (Gemini, Virgo, Sagittarius, Pisces)
        # Aspects all other Dual signs
        for s in [2, 5, 8, 11]:
            if s != sign_index:
                aspected.append(s)
                
    return aspected


# ===========================================================================
# 6. Planetary Sambandha (Relationships)
# Evaluates 4 classical types of Sambandha:
# 1. Parivartana (Mutual reception / exchange of signs)
# 2. Yuti (Conjunction in same sign)
# 3. Drishti (Mutual aspect)
# 4. Eka-drishti (One-sided aspect on lord's own sign)
# ===========================================================================

def evaluate_planetary_sambandha(
    p1: str,
    p1_lon: float,
    p2: str,
    p2_lon: float
) -> List[str]:
    """
    Identifies all astrological sambandhas between two planets.
    """
    sambandhas = []
    s1 = int(norm360(p1_lon) // 30.0)
    s2 = int(norm360(p2_lon) // 30.0)
    
    lord1 = RASI_LORDS[s1]
    lord2 = RASI_LORDS[s2]
    
    # 1. Yuti (Conjunction)
    if s1 == s2:
        sambandhas.append("Yuti (Conjunction in same sign)")
        
    # 2. Parivartana (Exchange of signs)
    if lord1 == p2 and lord2 == p1:
        sambandhas.append("Parivartana (Mutual sign exchange)")
        
    # 3. Drishti (Aspect)
    asp_1_to_2 = compute_aspect_details(p1, p1_lon, p2, p2_lon)
    asp_2_to_1 = compute_aspect_details(p2, p2_lon, p1, p1_lon)
    
    if asp_1_to_2["is_full_aspect_house"] and asp_2_to_1["is_full_aspect_house"]:
        sambandhas.append("Mutual Full Aspect (Parasara Drishti)")
    elif asp_1_to_2["is_full_aspect_house"]:
        sambandhas.append(f"{p1} aspects {p2} with full aspect")
    elif asp_2_to_1["is_full_aspect_house"]:
        sambandhas.append(f"{p2} aspects {p1} with full aspect")
        
    return sambandhas
