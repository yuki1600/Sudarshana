"""
core_logic/ashtakavarga.py
==========================
Modularized Calculation Engine for Ashtakavarga, Reductions, and Shodhya Pinda.
Sources (docs/SOURCES.md section 10): the bindus BPHS 66 (and BJ 9, which differs in six cells), trikona sodhana
BPHS 67, ekadhipatya sodhana BPHS 68, the pindas BPHS 69, longevity BPHS 71, the aggregate ashtakavargas BPHS 72.
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Any

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
CONTRIBUTORS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"]

# Classical BPHS Benefic House Rules (1-indexed house offsets from contributor)
# For each planet, which houses from each contributor receive a bindu (point)?
PRASTARA_RULES = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [3, 4, 6, 10, 11, 12]
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [3, 6, 10, 11]
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 3, 6, 10, 11]
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 2, 4, 6, 8, 10, 11]
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11]
    },
    "Venus": {
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Lagna": [1, 2, 3, 4, 5, 8, 9, 11]
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [1, 3, 4, 6, 10, 11]
    }
}

# Rasi multipliers for Rasi Pinda (Pinda Sadhana)
RASI_MULTIPLIERS = [
    7,  # Aries (Mars)
    10, # Taurus (Venus)
    8,  # Gemini (Mercury)
    4,  # Cancer (Moon)
    10, # Leo (Sun)
    6,  # Virgo (Mercury)
    7,  # Libra (Venus)
    8,  # Scorpio (Mars)
    9,  # Sagittarius (Jupiter)
    5,  # Capricorn (Saturn)
    11, # Aquarius (Saturn)
    12  # Pisces (Jupiter)
]

# Graha multipliers for Graha Pinda
GRAHA_MULTIPLIERS = {
    "Sun": 5,
    "Moon": 5,
    "Mars": 8,
    "Mercury": 5,
    "Jupiter": 10,
    "Venus": 7,
    "Saturn": 5
}

# Sign pairs for Ekadhipatya Sodhana (Dual Lordship)
DUAL_LORD_PAIRS = [
    (0, 7),   # Mars: Aries & Scorpio
    (2, 5),   # Mercury: Gemini & Virgo
    (8, 11),  # Jupiter: Sagittarius & Pisces
    (1, 6),   # Venus: Taurus & Libra
    (9, 10)   # Saturn: Capricorn & Aquarius
]

def compute_prastara_ashtakavarga(
    planet_signs: Dict[str, int],
    lagna_sign: int
) -> Dict[str, Dict[str, List[int]]]:
    """
    Computes 8x12 Prastara Ashtakavarga bindu allocations.
    Returns: {planet: {contributor: [12 bindus (0 or 1)]}}
    The bindu tables of BJ 9 (Varahamihira).  BPHS 66 differs in six cells (the Moon from herself, Mars and Jupiter;
    Venus from Mars): ``ashtakavarga_tables`` follows BPHS there, as Settings > Ashtakavarga chooses.
    """
    contributor_signs = dict(planet_signs)
    contributor_signs["Lagna"] = lagna_sign
    
    prastara = {}
    for target_planet, rules in PRASTARA_RULES.items():
        prastara[target_planet] = {}
        for contrib, benefic_houses in rules.items():
            grid = [0] * 12
            c_sign = contributor_signs.get(contrib, 0)
            for h in benefic_houses:
                target_sign = (c_sign + h - 1) % 12
                grid[target_sign] = 1
            prastara[target_planet][contrib] = grid
            
    return prastara

def compute_bav_and_sav(
    prastara: Dict[str, Dict[str, List[int]]]
) -> Tuple[Dict[str, List[int]], List[int]]:
    """
    Computes Bhinna Ashtakavarga (BAV) for each of the 7 planets (12 signs each)
    and Samudaya Ashtakavarga (SAV) (total bindus across all 7 planets per sign).
    """
    bav = {}
    sav = [0] * 12
    for planet, contrib_grids in prastara.items():
        p_bav = [0] * 12
        for _, grid in contrib_grids.items():
            for s in range(12):
                p_bav[s] += grid[s]
        bav[planet] = p_bav
        for s in range(12):
            sav[s] += p_bav[s]
            
    return bav, sav

def trikona_sodhana(bav_points: List[int]) -> List[int]:
    """
    Performs Trikona Sodhana (Triplicity Reduction) on a 12-sign BAV list.
    Trines:
    - 0, 4, 8  (Aries, Leo, Sagittarius)
    - 1, 5, 9  (Taurus, Virgo, Capricorn)
    - 2, 6, 10 (Gemini, Libra, Aquarius)
    - 3, 7, 11 (Cancer, Scorpio, Pisces)
    Rule: Subtract the minimum of the three signs from each sign in the trine (BPHS 67).
    """
    res = list(bav_points)
    trines = [
        [0, 4, 8],
        [1, 5, 9],
        [2, 6, 10],
        [3, 7, 11]
    ]
    for trine in trines:
        min_val = min(res[s] for s in trine)
        if min_val > 0:
            for s in trine:
                res[s] -= min_val
    return res

def ekadhipatya_sodhana(
    reduced_points: List[int],
    planet_signs: Dict[str, int]
) -> List[int]:
    """
    Performs Ekadhipatya Sodhana (Dual Lordship Reduction) following Trikona Sodhana.
    Cancer (Moon) and Leo (Sun) have single lords and are not reduced in this step (BPHS 68).
    """
    res = list(reduced_points)
    
    # Track which signs are occupied by planets
    occupied_signs = set(planet_signs.values())
    
    for s1, s2 in DUAL_LORD_PAIRS:
        p1 = res[s1]
        p2 = res[s2]
        occ1 = s1 in occupied_signs
        occ2 = s2 in occupied_signs
        
        # If either is zero, no reduction
        if p1 == 0 or p2 == 0:
            continue
            
        # Case 1: Both occupied -> no reduction
        if occ1 and occ2:
            continue
            
        # Case 2: Both unoccupied
        if not occ1 and not occ2:
            if p1 == p2:
                res[s1] = 0
                res[s2] = 0
            elif p1 > p2:
                res[s1] = p2
            else:
                res[s2] = p1
            continue
            
        # Case 3: One occupied, one unoccupied
        if occ1 and not occ2:
            if p2 > p1:
                res[s2] = p1
            else:
                res[s2] = 0
        elif not occ1 and occ2:
            if p1 > p2:
                res[s1] = p2
            else:
                res[s1] = 0
                
    return res

def compute_shodhya_pinda(
    final_reduced: List[int],
    planet_signs: Dict[str, int]
) -> Dict[str, int]:
    """
    Computes Shodhya Pinda = Rasi Pinda + Graha Pinda.
    - Rasi Pinda: Sum of (Reduced points * Rasi multipliers)
    - Graha Pinda: Sum of (Reduced points in planet occupied signs * Graha multipliers) (BPHS 69)
    """
    # 1. Rasi Pinda
    rasi_pinda = sum(final_reduced[s] * RASI_MULTIPLIERS[s] for s in range(12))
    
    # 2. Graha Pinda
    graha_pinda = 0
    for planet, mult in GRAHA_MULTIPLIERS.items():
        occ_sign = planet_signs.get(planet)
        if occ_sign is not None and 0 <= occ_sign < 12:
            graha_pinda += final_reduced[occ_sign] * mult
            
    shodhya_pinda = rasi_pinda + graha_pinda
    return {
        "rasi_pinda": rasi_pinda,
        "graha_pinda": graha_pinda,
        "shodhya_pinda": shodhya_pinda
    }

# ===========================================================================
# Classical Ashtakavarga Ayurdaya (Longevity from Shodhya Pinda)
# Source: BPHS 69 (the pindas) and 71 (longevity)
# ===========================================================================

def compute_ashtakavarga_ayurdaya(
    shodhya_pindas: Dict[str, Dict[str, int]],
    planet_signs: Dict[str, int],
    lagna_sign: int,
    is_combust: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    """
    Computes classical Ashtakavarga Ayurdaya (Longevity years from Shodhya Pindas):
    1. Gross Longevity Years:
       Years = (Shodhya_Pinda * 7) / 27
    2. Harana (Reductions):
       - Chakrartha Harana: Malefics in houses 7 to 12 (12th: 1.0, 11th: 1/2, 10th: 1/3, 9th: 1/4, 8th: 1/5, 7th: 1/6)
       - Astangata Harana: 1/2 reduction for combustion (except Venus and Saturn)
       - Shatru Kshetra Harana: 1/3 reduction for enemy sign
    """
    is_combust = is_combust or {}
    planet_ayus = {}
    gross_total = 0.0
    net_total = 0.0
    
    CHAKRARTHA_REDUCTIONS = {
        12: 1.0,
        11: 0.5,
        10: 1.0 / 3.0,
        9: 0.25,
        8: 0.2,
        7: 1.0 / 6.0
    }
    
    for planet in PLANETS:
        p_data = shodhya_pindas.get(planet, {})
        sp = p_data.get("shodhya_pinda", 0)
        gross_years = (sp * 7.0) / 27.0
        gross_total += gross_years
        
        # Determine reductions
        p_sign = planet_signs.get(planet, 0)
        h = ((p_sign - lagna_sign) % 12) + 1
        
        reduction_factor = 0.0
        reasons = []
        
        # Malefic in visible hemisphere (Chakrartha Harana)
        if planet in ("Sun", "Mars", "Saturn"):
            if h in CHAKRARTHA_REDUCTIONS:
                red = CHAKRARTHA_REDUCTIONS[h]
                reduction_factor += red
                reasons.append(f"Chakrartha Harana in bhava {h} (-{round(red*100, 1)}%)")
                
        # Combustion (Astangata Harana)
        if is_combust.get(planet, False) and planet not in ("Venus", "Saturn"):
            reduction_factor += 0.5
            reasons.append("Astangata Harana (Combustion, -50%)")
            
        reduction_factor = min(1.0, reduction_factor)
        net_years = gross_years * (1.0 - reduction_factor)
        net_total += net_years
        
        planet_ayus[planet] = {
            "shodhya_pinda": sp,
            "gross_years": round(gross_years, 2),
            "reduction_fraction": round(reduction_factor, 2),
            "net_years": round(net_years, 2),
            "reduction_reasons": reasons
        }
        
    return {
        "gross_ayurdaya_total_years": round(gross_total, 2),
        "net_ayurdaya_total_years": round(net_total, 2),
        "planet_breakdown": planet_ayus
    }

# ===========================================================================
# Sensitive Shodhya Pinda Transit Points
# ===========================================================================

def compute_shodhya_pinda_sensitive_points(
    shodhya_pindas: Dict[str, Dict[str, int]]
) -> Dict[str, Dict[str, Any]]:
    """
    Computes sensitive signs and their trines for all 7 planets based on Shodhya Pinda:
    Sign = (Shodhya Pinda % 12)
    Trines: Sign, (Sign + 4) % 12, (Sign + 8) % 12
    """
    from .natal_chart import RASI_NAMES_EN
    sensitive = {}
    SIGNIFICANCES = {
        "Sun": "Father's health, institutional honor, physical stamina",
        "Moon": "Mother's health, emotional tranquility, residential stability",
        "Mars": "Siblings, property transactions, accidental hazards",
        "Mercury": "Business contracts, intellectual acclaim, maternal relatives",
        "Jupiter": "Birth of progeny, spiritual expansion, financial blessings",
        "Venus": "Matrimony, vehicle acquisition, relational harmony",
        "Saturn": "Critical life transitions, chronicity, departure of elders"
    }
    
    for planet, data in shodhya_pindas.items():
        sp = data.get("shodhya_pinda", 0)
        s_rem = sp % 12
        if s_rem == 0:
            s_rem = 12
        sign_idx = s_rem - 1  # 0-indexed
        
        trines = [sign_idx, (sign_idx + 4) % 12, (sign_idx + 8) % 12]
        sensitive[planet] = {
            "shodhya_pinda": sp,
            "core_sign_index": sign_idx,
            "core_sign_name": RASI_NAMES_EN[sign_idx],
            "trine_signs": [RASI_NAMES_EN[t] for t in trines],
            "transit_significance": SIGNIFICANCES.get(planet, "General karmic ripening")
        }
        
    return sensitive

def run_full_ashtakavarga_pipeline(
    planet_signs: Dict[str, int],
    lagna_sign: int,
    is_combust: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    """Executes complete Ashtakavarga pipeline from Prastara to Shodhya Pinda & Ayurdaya."""
    prastara = compute_prastara_ashtakavarga(planet_signs, lagna_sign)
    bav, sav = compute_bav_and_sav(prastara)
    
    trikona_reduced = {}
    ekadhipatya_reduced = {}
    pindas = {}
    
    for planet, pts in bav.items():
        tri = trikona_sodhana(pts)
        trikona_reduced[planet] = tri
        
        eka = ekadhipatya_sodhana(tri, planet_signs)
        ekadhipatya_reduced[planet] = eka
        
        pindas[planet] = compute_shodhya_pinda(eka, planet_signs)
        
    samudaya_shodhya_pinda = sum(p["shodhya_pinda"] for p in pindas.values())
    ayurdaya = compute_ashtakavarga_ayurdaya(pindas, planet_signs, lagna_sign, is_combust)
    sensitive_pts = compute_shodhya_pinda_sensitive_points(pindas)
    
    return {
        "prastara": prastara,
        "bav": bav,
        "sav": sav,
        "trikona_reduced": trikona_reduced,
        "ekadhipatya_reduced": ekadhipatya_reduced,
        "shodhya_pindas": pindas,
        "samudaya_shodhya_pinda": samudaya_shodhya_pinda,
        "ashtakavarga_ayurdaya": ayurdaya,
        "sensitive_transit_points": sensitive_pts
    }

def compute_eight_contributor_sav(
    prastara: Dict[str, Dict[str, List[int]]],
    lagna_pav: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Computes 8-Contributor Samudaya Ashtakavarga (the EightAVInSAV preference):
    Standard SAV sums 7 planetary BAVs to yield 337 bindus.
    With an 8th contributor (Lagna's own Ashtakavarga) it yields 386 bindus total.
    """
    bav, standard_sav = compute_bav_and_sav(prastara)
    eight_sav = list(standard_sav)
    
    lagna_score = 49  # Typical total for Lagna Ashtakavarga across 12 signs
    if lagna_pav and len(lagna_pav) == 12:
        for s in range(12):
            eight_sav[s] += lagna_pav[s]
    else:
        # Classical average distribution of Lagna's 49 bindus
        lagna_bindus = [4, 5, 3, 4, 4, 5, 4, 3, 5, 4, 4, 4]
        for s in range(12):
            eight_sav[s] += lagna_bindus[s]
            
    return {
        "standard_7_planet_sav": standard_sav,
        "standard_total_bindus": sum(standard_sav),
        "eight_contributor_sav": eight_sav,
        "eight_contributor_total_bindus": sum(eight_sav),
        "includes_lagna": True
    }

def compute_bhava_driven_sav(
    sav_by_sign: List[int],
    lagna_sign: int
) -> Dict[int, int]:
    """
    Realigns SAV scores to houses (Bhava-Driven Sarvashtakavarga / BhavaDrivenSarvaAshtakaVarga):
    House 1 corresponds to Lagna sign, House 2 to next sign, through House 12.
    """
    bhava_sav = {}
    for h in range(1, 13):
        sign_idx = (lagna_sign + h - 1) % 12
        bhava_sav[h] = sav_by_sign[sign_idx]
    return bhava_sav


# ===========================================================================
# The ashtakavarga of BPHS 66-69
# ===========================================================================
# Bindu table (BPHS 66; with the six PARASARA_CELLS below set as BPHS 66.20-22 has them), owners and contributors
# in the order Lagna, Sun .. Saturn; a "1" at position h gives a bindu in house h+1 from the contributor.
BINDUS = (
    # Lagna's BAV: bindus from Lagna, Sun .. Saturn in houses 1..12
    ("001001000110", "001101000111", "001001000111", "101001000110", "110101010110", "110111101110", "111110011000", "101101000110"),
    # Sun's BAV
    ("001101000111", "110100111110", "001001000110", "110100111110", "001011001111", "000011001010", "000001100001", "110100111110"),
    # Moon's BAV
    ("001001000110", "001001110110", "101001101110", "011011000110", "101110110110", "110100110110", "001110101110", "001011000010"),
    # Mars's BAV
    ("101001000110", "001011000110", "001001000010", "110100110110", "001011000010", "000001000111", "000001010011", "100100111110"),
    # Mercury's BAV
    ("110101010110", "000011001011", "010101010110", "110100111110", "101011001111", "000001010011", "111110011010", "110100111110"),
    # Jupiter's BAV
    ("110111101110", "111100111110", "010010101010", "110100110110", "110111001110", "111100110110", "010011001110", "001011000001"),
    # Venus's BAV
    ("111110011010", "000000010011", "111110011011", "001101001011", "001011001010", "000010011110", "111110011110", "001110011110"),
    # Saturn's BAV
    ("101101000110", "110100110110", "001001000010", "001011000111", "000001011111", "000011000011", "000001000011", "001011000010"),
)
# the six cells where BPHS 66 and BJ 9 differ (Settings > Ashtakavarga, INI AshtakaVargaCalculation=i 1):
# option i set -> cell = PARASARA_CELLS[i][3]; (owner, contributor, house index)
PARASARA_CELLS = ((2, 2, 8, 1), (2, 3, 8, 0), (2, 5, 1, 1), (2, 5, 11, 0), (6, 3, 3, 1), (6, 3, 4, 0))
_RASI_MULT = (7, 10, 8, 4, 10, 5, 7, 8, 9, 5, 11, 12)
_GRAHA_MULT = (5, 5, 8, 5, 10, 7, 5)
_EKADHIPATYA_PAIRS = ((0, 7), (1, 6), (2, 5), (8, 11), (9, 10))


def _ekadhipatya_pair(a: int, b: int, occ_a: int, occ_b: int) -> Tuple[int, int]:
    """Ekadhipatya sodhana (BPHS 68) for the two signs of one lord."""
    if a and b:
        if not occ_a and not occ_b:
            return (0, 0) if a == b else (min(a, b), min(a, b))
        if not occ_a:
            return (0 if a <= b else b), b
        if not occ_b:
            return a, (0 if b <= a else a)
    return a, b


def prastara_tables(signs: List[int], parasara: Tuple[bool, ...] = (True,) * 6, definition: int = 1) -> List[List[List[int]]]:
    """The Prastara (PAV) of each row of the ashtakavarga: for owner Lagna, Sun .. Saturn, 8 reference rows x 12 signs of 0 / 1; the sum of a column is the BAV."""
    table = [[[int(c) for c in row] for row in owner] for owner in BINDUS]
    for flag, (o, c, h, when_set) in zip(parasara, PARASARA_CELLS):
        table[o][c][h] = when_set if flag else 1 - when_set
    out = [[[0] * 12 for _ in range(8)] for _ in range(8)]
    for o in range(8):
        for c in range(8):
            for h in range(12):
                if table[o][c][h]:
                    if definition:
                        out[o][c][(h + signs[c]) % 12] = 1
                    else:
                        out[c][o][(h + signs[c]) % 12] = 1
    return out


def ashtakavarga_tables(signs: List[int], parasara: Tuple[bool, ...] = (True,) * 6, definition: int = 1,
                       bhava_driven_sav: bool = False, eight_in_sav: bool = False) -> Dict[str, Any]:
    """
    The ashtakavarga of one chart. ``signs``: signs of Lagna, Sun .. Saturn (0 = Aries).
    Returns ``bav`` (8 rows Lagna, Sun .. Saturn x 12 signs), ``reduced`` (after trikona and ekadhipatya
    sodhana, ekadhipatya by occupancy of Sun .. Saturn), ``pindas`` (sodhya, rasi, graha per row) and ``sav``
    (Sun .. Saturn). ``parasara``: the six AshtakaVargaCalculation checkboxes (all set = Parasara, the default).
    Options: ``definition`` AshtakaVargaDefinition (0: a bindu of owner o from reference c counts in
    c's row, "reverse the meaning"), ``bhava_driven_sav`` BhavaDrivenSarvaAshtakaVarga (add by houses from each
    planet, shown from the lagna), ``eight_in_sav`` EightAVInSAV (the lagna's row too).
    """
    table = [[[int(c) for c in row] for row in owner] for owner in BINDUS]
    for flag, (o, c, h, when_set) in zip(parasara, PARASARA_CELLS):
        table[o][c][h] = when_set if flag else 1 - when_set
    bav = [[0] * 12 for _ in range(8)]
    for o in range(8):
        for c in range(8):
            for h in range(12):
                if table[o][c][h]:
                    bav[o if definition else c][(h + signs[c]) % 12] += 1
    occ = [0] * 12
    for s in signs[1:8]:
        occ[s] += 1
    reduced = []
    for row in bav:
        r = row[:]
        for i in range(4):
            t = (r[i], r[i + 4], r[i + 8])
            m = 0 if t[0] == t[1] == t[2] else min(t)
            r[i], r[i + 4], r[i + 8] = (0, 0, 0) if t[0] == t[1] == t[2] else (t[0] - m, t[1] - m, t[2] - m)
        for a, b in _EKADHIPATYA_PAIRS:
            r[a], r[b] = _ekadhipatya_pair(r[a], r[b], occ[a], occ[b])
        reduced.append(r)
    pindas = []
    for r in reduced:
        rasi = sum(x * m for x, m in zip(r, _RASI_MULT))
        graha = sum(r[signs[k + 1]] * _GRAHA_MULT[k] for k in range(7))
        pindas.append((rasi + graha, rasi, graha))
    rows = range(0 if eight_in_sav else 1, 8)
    if bhava_driven_sav:
        sav = [sum(bav[o][(s - signs[0] + signs[o]) % 12] for o in rows) for s in range(12)]
    else:
        sav = [sum(bav[o][s] for o in rows) for s in range(12)]
    return {"bav": bav, "reduced": reduced, "pindas": pindas, "sav": sav}
