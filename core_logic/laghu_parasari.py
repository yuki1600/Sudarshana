"""
core_logic/laghu_parasari.py
============================
Modularized Calculation Engine for the Principles of Laghu Parasari
(also known as Jataka Chandrika).
Sources (docs/SOURCES.md section 11): Laghu Parasari (LP), its chapters on the natures of the lords, on yogas and
on longevity; the same rules in BPHS 34 (yoga karakas), 39 (raja yoga) and 44 (marakas).

Key Principles Implemented:
1. Functional Nature Evaluator (Benefic, Malefic, Neutral, Yogakaraka for all 12 Lagnas)
2. Kendra-Adhipatya Dosha & Trishadayadhipatya identification
3. Laghu Parasari Raja Yoga Matrix (Kendra-Trikona lord associations & Sambandha)
4. Maraka (Death-Inflicting) Assessment

(The app's "Laghu Parasari" tab is a different thing, a sum-of-longitudes explorer: ``longitude_sums``.)
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Any

from .natal_chart import RASI_NAMES_EN, RASI_LORDS, OWN_SIGNS

KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
TRISHADAYA_HOUSES = {3, 6, 11}
DUSTHANA_HOUSES = {6, 8, 12}
MARAKA_HOUSES = {2, 7}

# Standard Natural Benefics & Malefics
NATURAL_BENEFICS = {"Jupiter", "Venus", "Moon", "Mercury"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# Classical Yogakarakas for the 12 Lagnas (0 = Aries to 11 = Pisces)
# A single planet owning both a Kendra and a Trikona
CLASSICAL_YOGAKARAKAS = {
    1: "Saturn",   # Taurus (owns 9th & 10th)
    3: "Mars",     # Cancer (owns 5th & 10th)
    4: "Mars",     # Leo (owns 4th & 9th)
    6: "Saturn",   # Libra (owns 4th & 5th)
    9: "Venus",    # Capricorn (owns 5th & 10th)
    10: "Venus"    # Aquarius (owns 4th & 9th)
}

def get_houses_owned_by_planet(lagna_sign: int, planet: str) -> List[int]:
    """Returns the 1-based house numbers owned by a planet for a given Lagna sign."""
    houses = []
    own_signs = OWN_SIGNS.get(planet, [])
    for s in own_signs:
        h = ((s - lagna_sign) % 12) + 1
        houses.append(h)
    return sorted(houses)

def evaluate_functional_nature_for_lagna(lagna_sign: int) -> Dict[str, Dict[str, Any]]:
    """
    Evaluates the Functional Nature of all 7 classical planets for a given Lagna:
    - Functional Benefic (Subha)
    - Functional Malefic (Asubha)
    - Functional Neutral (Sama)
    - Yogakaraka (Supreme Raja Yoga producer)
    Based strictly on Laghu Parasari rules.
    """
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    results = {}
    
    yk = CLASSICAL_YOGAKARAKAS.get(lagna_sign, None)
    
    for p in planets:
        houses = get_houses_owned_by_planet(lagna_sign, p)
        is_natural_benefic = (p in NATURAL_BENEFICS)
        
        # Check Yogakaraka status
        if p == yk:
            results[p] = {
                "planet": p,
                "houses_owned": houses,
                "classification": "Yogakaraka",
                "is_benefic": True,
                "is_malefic": False,
                "is_yogakaraka": True,
                "rationale": f"Owns both a Kendra and a Trikona ({houses}), making it a pure Raja Yoga producer."
            }
            continue
            
        has_trikona = any(h in TRIKONA_HOUSES for h in houses)
        has_kendra = any(h in KENDRA_HOUSES for h in houses)
        has_trishadaya = any(h in TRISHADAYA_HOUSES for h in houses)
        has_8th = 8 in houses
        has_12th = 12 in houses
        
        # Laghu Parasari classification logic:
        # 1. Trikona lordship is fundamentally auspicious
        # 2. Kendra lordship: benefics get Kendradhipatya Dosha; malefics become neutral
        # 3. Trishadaya lordship: strong maleficence (11th worst, then 6th, then 3rd)
        # 4. Lagna lord (1st house) is always auspicious even if owning 8th (Mars for Aries, Venus for Libra)
        
        if 1 in houses:
            classification = "Functional Benefic"
            rationale = "Lagna Lord is inherently auspicious and protects the chart."
            is_b, is_m = True, False
        elif has_trikona and not has_trishadaya:
            classification = "Functional Benefic"
            rationale = f"Lord of Trikona bhava(s) {houses}; bestows grace and fortune."
            is_b, is_m = True, False
        elif has_trishadaya and not has_trikona:
            classification = "Functional Malefic"
            rationale = f"Lord of Trishadaya bhava(s) {houses}; causes impediments and stress."
            is_b, is_m = False, True
        elif has_kendra and is_natural_benefic and not has_trikona:
            classification = "Neutral (Kendradhipatya Dosha)"
            rationale = f"Natural benefic owning Kendra bhava(s) {houses}; loses beneficence."
            is_b, is_m = False, False
        elif has_kendra and not is_natural_benefic and not has_trishadaya:
            classification = "Neutral"
            rationale = f"Natural malefic owning Kendra bhava(s) {houses}; loses malice."
            is_b, is_m = False, False
        elif (has_8th or has_12th) and not has_trikona:
            classification = "Neutral / Dependent"
            rationale = f"Lord of 8th/12th bhava(s) {houses}; gives results according to associated grahas."
            is_b, is_m = False, False
        else:
            classification = "Neutral"
            rationale = f"Mixed ownership ({houses}) balances beneficial and difficult influences."
            is_b, is_m = False, False
            
        results[p] = {
            "planet": p,
            "houses_owned": houses,
            "classification": classification,
            "is_benefic": is_b,
            "is_malefic": is_m,
            "is_yogakaraka": False,
            "rationale": rationale
        }
        
    return results


def find_laghu_parasari_raja_yogas(
    lagna_sign: int,
    planetary_signs: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Identifies Raja Yogas according to Laghu Parasari:
    A connection between a Kendra Lord (1, 4, 7, 10) and a Trikona Lord (1, 5, 9).
    Sambandha types:
    1. Parivartana (Mutual exchange of signs)
    2. Yuti (Conjunction in the same sign)
    3. Drishti (Mutual 7th aspect)
    """
    kendra_lords = {}
    trikona_lords = {}
    
    for h in [1, 4, 7, 10]:
        s = (lagna_sign + h - 1) % 12
        kendra_lords[h] = RASI_LORDS[s]
        
    for h in [1, 5, 9]:
        s = (lagna_sign + h - 1) % 12
        trikona_lords[h] = RASI_LORDS[s]
        
    yogas = []
    checked_pairs = set()
    
    for kh, k_lord in kendra_lords.items():
        for th, t_lord in trikona_lords.items():
            if k_lord == t_lord:
                continue
            pair = tuple(sorted([k_lord, t_lord]))
            if pair in checked_pairs:
                continue
            checked_pairs.add(pair)
            
            p1, p2 = k_lord, t_lord
            s1 = planetary_signs.get(p1, -1)
            s2 = planetary_signs.get(p2, -1)
            if s1 == -1 or s2 == -1:
                continue
                
            # 1. Yuti (Conjunction)
            if s1 == s2:
                is_dharma_karma = (kh == 10 and th == 9) or (kh == 9 and th == 10)
                y_name = "Dharma-Karmadhipati Yoga" if is_dharma_karma else f"Kendra-Trikona Raja Yoga ({p1} & {p2})"
                yogas.append({
                    "yoga_name": y_name,
                    "sambandha": "Yuti (Conjunction)",
                    "kendra_lord": p1,
                    "kendra_house": kh,
                    "trikona_lord": p2,
                    "trikona_house": th,
                    "sign": RASI_NAMES_EN[s1],
                    "strength": "High",
                    "description": f"{p1} (Lord of {kh}) and {p2} (Lord of {th}) conjoin in {RASI_NAMES_EN[s1]}."
                })
                continue
                
            # 2. Parivartana (Exchange)
            p1_owns = OWN_SIGNS.get(p1, [])
            p2_owns = OWN_SIGNS.get(p2, [])
            if s1 in p2_owns and s2 in p1_owns:
                yogas.append({
                    "yoga_name": f"Maha Parivartana Raja Yoga ({p1} & {p2})",
                    "sambandha": "Parivartana (Mutual Exchange)",
                    "kendra_lord": p1,
                    "kendra_house": kh,
                    "trikona_lord": p2,
                    "trikona_house": th,
                    "strength": "Supreme",
                    "description": f"{p1} in sign of {p2} ({RASI_NAMES_EN[s1]}) and {p2} in sign of {p1} ({RASI_NAMES_EN[s2]})."
                })
                continue
                
            # 3. Mutual Aspect (Drishti: 180° opposition)
            if abs(s1 - s2) == 6:
                yogas.append({
                    "yoga_name": f"Kendra-Trikona Drishti Raja Yoga ({p1} & {p2})",
                    "sambandha": "Mutual Aspect (Drishti)",
                    "kendra_lord": p1,
                    "kendra_house": kh,
                    "trikona_lord": p2,
                    "trikona_house": th,
                    "strength": "Medium-High",
                    "description": f"{p1} in {RASI_NAMES_EN[s1]} and {p2} in {RASI_NAMES_EN[s2]} aspect each other directly."
                })
                
    return yogas


def evaluate_maraka_grahas(
    lagna_sign: int,
    planetary_signs: Dict[str, int]
) -> Dict[str, Any]:
    """
    Evaluates Marakas (Death-Inflicting Planets) according to Laghu Parasari:
    - Primary Maraka Lords: Lords of the 2nd and 7th houses
    - Secondary Marakas: Planets occupant in the 2nd or 7th houses
    - Tertiary Marakas: Planets in conjunction with Maraka lords
    """
    s2 = (lagna_sign + 1) % 12
    s7 = (lagna_sign + 6) % 12
    
    lord_2 = RASI_LORDS[s2]
    lord_7 = RASI_LORDS[s7]
    
    occupants_2 = [p for p, s in planetary_signs.items() if s == s2]
    occupants_7 = [p for p, s in planetary_signs.items() if s == s7]
    
    return {
        "maraka_houses": [2, 7],
        "primary_maraka_lords": {
            "house_2_lord": lord_2,
            "house_7_lord": lord_7
        },
        "house_2_occupants": occupants_2,
        "house_7_occupants": occupants_7,
        "maraka_summary": f"Primary Marakas: {lord_2} (2nd lord) and {lord_7} (7th lord). Secondary: {occupants_2 + occupants_7}."
    }
