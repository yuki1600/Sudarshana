"""
core_logic/avasthas.py
======================
Modularized Calculation Engine for Planetary States (Avasthas):
- Baalaadi Avasthas (5 Age States: Baala, Kumara, Yuva, Vriddha, Mrita)
- Jagrataadi Avasthas (3 Consciousness States: Jagrata, Swapna, Sushupti)
- Deeptaadi Avasthas (9 Dignity States: Deepta, Svastha, Mudita, Shanta, Dina, etc.)
- Sayanadi 12 Avasthas (12 Parasari Activity States: Sayana, Sabha, Bhojana, Nidra, etc.)

Sources (docs/SOURCES.md section 10): age BPHS 45.3-4, alertness 45.5-6, the nine moods 45.7-10, Lajjitadi
45.11-18, Sayanadi and its three sub-states 45.30-37; the moods "Swastha" and "Khala" also as PD 3.18-19 has them.
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional, Any

from . import sign_strength as _SS
from .natal_chart import (
    norm360,
    RASI_NAMES_EN,
    EXALTATION,
    DEBILITATION,
    OWN_SIGNS,
    get_graha_dignity
)
from .aspects_friendships import get_natural_relationship


# ===========================================================================
# 1. Baalaadi Avasthas (5 Age / Maturity States)
# ===========================================================================

BAALAADI_ODD = ["Baala (Infant)", "Kumara (Youth)", "Yuva (Adult - Peak)", "Vriddha (Old)", "Mrita (Dead)"]
BAALAADI_FRUIT = [0.25, 0.50, 1.00, 0.10, 0.00]

def compute_baalaadi_avastha(longitude: float) -> Dict[str, Any]:
    """
    Computes Baalaadi avastha based on degree in sign:
    Odd Signs:
      0-6°: Baala (25%), 6-12°: Kumara (50%), 12-18°: Yuva (100%), 18-24°: Vriddha (10%), 24-30°: Mrita (0%)
    Even Signs:
      Reversed order (0-6° is Mrita, 24-30° is Baala)
    """
    lon = norm360(longitude)
    sign = int(lon // 30.0)
    deg = lon % 30.0
    seg = min(4, int(deg // 6.0))
    is_odd_sign = (sign % 2 == 0)  # 0-indexed: Aries(0) is odd sign
    
    idx = seg if is_odd_sign else (4 - seg)
    name = BAALAADI_ODD[idx]
    fruit = BAALAADI_FRUIT[idx]
    
    return {
        "degree_in_sign": deg,
        "sign_index": sign,
        "is_odd_sign": is_odd_sign,
        "avastha_name": name,
        "potency_fraction": fruit,
        "potency_percentage": int(fruit * 100)
    }


# ===========================================================================
# 2. Jagrataadi Avasthas (3 States of Alertness)
# ===========================================================================

def compute_jagrataadi_avastha(planet: str, dignity: str) -> Dict[str, Any]:
    """
    Computes Jagrataadi avastha:
    - Jagrata (Awake / Alert): In Exaltation or Own sign (100% potency)
    - Swapna (Dreaming): In Friendly or Neutral sign (50% potency)
    - Sushupti (Sleeping / Dormant): In Debilitation or Inimical sign (0% potency)
    """
    d_lower = dignity.lower()
    if "exalt" in d_lower or "own" in d_lower or "moolatrikona" in d_lower:
        name = "Jagrata (Awake / Alert)"
        potency = 1.0
    elif "friend" in d_lower or "neutral" in d_lower:
        name = "Swapna (Dreaming)"
        potency = 0.5
    else:
        name = "Sushupti (Sleeping / Dormant)"
        potency = 0.0
        
    return {
        "planet": planet,
        "dignity": dignity,
        "avastha_name": name,
        "potency_fraction": potency
    }


# ===========================================================================
# 3. Deeptaadi Avasthas (9 Dignity States)
# ===========================================================================

def compute_deeptaadi_avastha(
    planet: str,
    sign_index: int,
    is_retrograde: bool = False,
    is_combust: bool = False
) -> Dict[str, str]:
    """
    Computes the 9 Deeptaadi avasthas based on planetary dignity:
    1. Deepta (Radiant): In Exaltation
    2. Svastha (Comfortable): In Own Sign
    3. Mudita (Delighted): In Great Friend's sign
    4. Shanta (Peaceful): In Friend's sign
    5. Sakta (Capable): Retrograde
    6. Nipidita (Troubled): Defeated in planetary war
    7. Dina (Miserable): In Debilitation
    8. Khala (Wicked): In Enemy's sign
    9. Suduhkhita (Extremely Afflicted): In Great Enemy's sign or Combust
    """
    if is_combust:
        return {"avastha": "Suduhkhita (Extremely Afflicted)", "meaning": "Burnt by Sun (Combust)"}
    if is_retrograde and planet not in ("Sun", "Moon", "Rahu", "Ketu"):
        return {"avastha": "Sakta (Capable / Powerful)", "meaning": "Retrograde motion"}
        
    # Check exaltation & debilitation
    ex_sign, _ = EXALTATION.get(planet, (-1, 0))
    deb_sign, _ = DEBILITATION.get(planet, (-1, 0))
    own = OWN_SIGNS.get(planet, [])
    
    if sign_index == ex_sign:
        return {"avastha": "Deepta (Radiant / Exalted)", "meaning": "Exalted, full auspiciousness"}
    if sign_index == deb_sign:
        return {"avastha": "Dina (Miserable / Debilitated)", "meaning": "Debilitated, lack of bala"}
    if sign_index in own:
        return {"avastha": "Svastha (Comfortable / Content)", "meaning": "Own sign, peaceful dignity"}
        
    # Check sign ruler relationship
    from .natal_chart import RASI_LORDS
    sign_lord = RASI_LORDS[sign_index % 12]
    rel = get_natural_relationship(planet, sign_lord)
    
    if rel == "Friend":
        return {"avastha": "Shanta (Peaceful)", "meaning": "Friendly sign, gentle support"}
    elif rel == "Enemy":
        return {"avastha": "Khala (Agitated / Troubled)", "meaning": "Enemy's sign, internal conflict"}
        
    return {"avastha": "Mudita (Content / Neutral)", "meaning": "Neutral sign"}



# ===========================================================================
# 5. Lajjitadi 6 Psychological Avasthas (BPHS Ch. 45)
# ===========================================================================

def compute_lajjitadi_avastha(
    planet: str,
    planet_sign: int,
    house_num: int,
    conjoined_planets: List[str],
    aspecting_planets: List[str],
    dignity: str
) -> Dict[str, Any]:
    """
    Computes the 6 Lajjitadi Avasthas per Maharishi Parasara:
    1. Lajjita (Ashamed): In 5th house with Rahu/Ketu, or with Sun/Saturn/Mars.
    2. Garvita (Proud): In Exaltation or Moolatrikona.
    3. Kshudhita (Starved): In Enemy's sign, aspected by enemy, or with Saturn.
    4. Trushita (Thirsty): In Watery sign (Cancer, Scorpio, Pisces), aspected by enemy, no benefic aspect.
    5. Mudita (Delighted): In Friendly sign, or with/aspected by Jupiter or benefics.
    6. Kshobhita (Agitated): Conjoined with Sun and aspected by malefics.
    """
    d_lower = dignity.lower()
    active_states = []
    
    # 1. Garvita
    if "exalt" in d_lower or "moolatrikona" in d_lower:
        active_states.append(("Garvita (Proud / Majestic)", "Endowed with high confidence, nobility, and majestic success."))
        
    # 2. Lajjita
    if house_num == 5 and any(p in ("Rahu", "Ketu", "Sun", "Mars", "Saturn") for p in conjoined_planets):
        active_states.append(("Lajjita (Ashamed / Hesitant)", "Mental reserve, aversion to scandal, or delayed progeny blessings."))
        
    # 3. Kshudhita
    if "enemy" in d_lower or "Saturn" in conjoined_planets or any(p in ("Mars", "Saturn", "Rahu") for p in aspecting_planets):
        active_states.append(("Kshudhita (Starved / Distressed)", "Deprivation, feeling unappreciated, struggles in early enterprise."))
        
    # 4. Trushita
    watery_signs = {3, 7, 11} # Cancer, Scorpio, Pisces
    has_benefic_aspect = any(p in ("Jupiter", "Venus", "Mercury") for p in aspecting_planets)
    if planet_sign in watery_signs and not has_benefic_aspect and any(p in ("Mars", "Saturn") for p in aspecting_planets):
        active_states.append(("Trushita (Thirsty / Yearning)", "Deep yearning, thirst for emotional fulfillment, vulnerability."))
        
    # 5. Mudita
    if "friend" in d_lower or "own" in d_lower or "Jupiter" in conjoined_planets or "Jupiter" in aspecting_planets:
        active_states.append(("Mudita (Delighted / Joyful)", "Contentment, agreeable temperament, generous friendships."))
        
    # 6. Kshobhita
    if "Sun" in conjoined_planets and any(p in ("Mars", "Saturn", "Rahu") for p in aspecting_planets):
        active_states.append(("Kshobhita (Agitated / Shaken)", "Internal tension, authoritative friction, restless mind."))
        
    if not active_states:
        primary = ("Shanta (Peaceful / Neutral)", "Equable state without acute affliction or exaltation.")
    else:
        primary = active_states[0]
        
    return {
        "planet": planet,
        "primary_lajjitadi_avastha": primary[0],
        "meaning": primary[1],
        "all_qualifying_states": [s[0] for s in active_states]
    }


# ===========================================================================
# 6. Master Comprehensive Planetary Avastha Evaluator
# ===========================================================================

def compute_comprehensive_planetary_avasthas(
    planet: str,
    planet_lon: float,
    lagna_sign: int,
    moon_lon: float,
    is_retrograde: bool = False,
    is_combust: bool = False,
    conjoined_planets: Optional[List[str]] = None,
    aspecting_planets: Optional[List[str]] = None,
    ghati_of_birth: float = 15.0
) -> Dict[str, Any]:
    """
    Computes all classical Parasari Avasthas for a planet:
    1. Baalaadi (5 Age States)
    2. Jagrataadi (3 Alertness States)
    3. Deeptaadi (9 Dignity States)
    4. Lajjitadi (6 Psychological States)
    6. Vimsopaka Bala Integration (Divisional dignity score)
    """
    lon = norm360(planet_lon)
    sign_idx = int(lon // 30.0)
    house_num = ((sign_idx - lagna_sign) % 12) + 1
    
    # 1. Baalaadi
    baala = compute_baalaadi_avastha(lon)
    
    # 2. Deeptaadi & Dignity
    deepta = compute_deeptaadi_avastha(planet, sign_idx, is_retrograde, is_combust)
    dignity_str = deepta["avastha"]
    
    # 3. Jagrataadi
    jagrata = compute_jagrataadi_avastha(planet, dignity_str)
    
    # 5. Lajjitadi
    lajjita = compute_lajjitadi_avastha(
        planet=planet,
        planet_sign=sign_idx,
        house_num=house_num,
        conjoined_planets=conjoined_planets or [],
        aspecting_planets=aspecting_planets or [],
        dignity=dignity_str
    )
    
    # 6. Vimsopaka Bala
    from .shadbala import compute_vimsopaka_bala
    vimsopaka = compute_vimsopaka_bala(planet, lon)
    
    return {
        "planet": planet,
        "longitude": round(lon, 2),
        "sign_name": RASI_NAMES_EN[sign_idx],
        "house_from_lagna": house_num,
        "baalaadi": baala,
        "jagrataadi": jagrata,
        "deeptaadi": deepta,
        "lajjitadi": lajjita,
        "vimsopaka_bala_scores": vimsopaka["scheme_scores"]
    }


# ===========================================================================
# The avasthas of BPHS 45
# ===========================================================================
_LORDS_1 = (3, 6, 4, 2, 1, 4, 6, 3, 5, 7, 7, 5)        # sign lords as point indices 1 = Sun .. 7 = Saturn
_MT_1 = (4, 1, 0, 5, 8, 6, 10, 5, 11)
_MALEFIC = (True, False, True, False, False, False, True, True, True)
# the names of the states: age BPHS 45.3, alertness 45.5, mood 45.7-18 (with PD 3.18-19), activity 45.30-37
AGE = ("Baala (infant)", "Kumara (adolescent)", "Yuva (young)", "Vriddha (old)", "Mrita (dead)")
ALERTNESS = ("Jaagrita (awake)", "Swapna (dreaming)", "Sushupta (asleep)")
MOOD = ("Deepta (glowing)", "Swastha (comfortable)", "Mudita (delighted)", "Saanta (peaceful)",
              "Deena (sad)", "Duhkhita (distressed)", "Vikala (crippled)", "Khala (mischievous)",
              "Kopita (angry)", "Lajjita (ashamed)", "Garvita (proud)")
# BPHS 45.8-10: Parashara's nine moods, in his order
PARASHARA_MOOD = ("Deepta (glowing)", "Swastha (comfortable)", "Pramudita (delighted)", "Saanta (peaceful)", "Deena (sad)",
                  "Vikala (crippled)", "Duhkhita (distressed)", "Khala (mischievous)", "Kopa (angry)")
_SHORT = ("Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke")
_RELATION = {1: "great friend", 2: "friend", 3: "neutral", 4: "enemy", 5: "great enemy"}
ACTIVITY = ("Sayana (lying down)", "Upavesana (sitting)", "Netrapani (eyes and hands)",
                  "Prakasana (glowing)", "Gamana (on the move)", "Aagamana (coming)", "Sabha (at an assembly)",
                  "Aagama (returning)", "Bhojana (eating)", "NrityaLipsa (desirous of dancing)", "Kautuka (eager)",
                  "Nidra (sleeping)")
INTENSITY = ("Drishti (medium)", "Cheshta (full)", "Vicheshta (little)")
_SAYANADI_ADD = (5, 2, 2, 3, 5, 3, 3, 4, 4)            # Sun .. Ketu: BPHS 45.30-37's additives (Rahu's for Ketu too)


def _jh_owns(planet: int, sign: int) -> bool:
    """Whether ``planet`` owns ``sign``, Rahu co-owning Aquarius and Ketu Scorpio (BPHS 47.34-39); planet 1 = Sun .. 9 = Ketu."""
    return _LORDS_1[sign] == planet or (sign == 10 and planet == 8) or (sign == 7 and planet == 9)


def graha_avasthas(lons: List[float], lagna_lon: float, ghatis_since_sunrise: float,
                   compound: bool = False, varga_signs: List[int] = None, combust: List[bool] = None) -> Dict[str, Dict[str, Any]]:
    """Age (Baaladi), alertness (Jagradadi), mood (Deeptadi flags, compound relationships) and activity
    (Sayanadi) of Sun .. Ketu in the rasi chart. ``lons``: sidereal longitudes of Sun .. Ketu.
    ``compound`` is INI UseCompundRelationshipInAvasthas (Settings): off, the natural relationship with the sign's
    lord (BPHS 3.55); on, the compound one of this rasi chart (BPHS 3.57-58).
    ``varga_signs``: Sun .. Ketu in the chart chosen by "Change varga for avasthas related to alertness and mood"; age and activity stay the rasi's.
    ``combust``: Sun .. Ketu eclipsed by the Sun, for Parashara's Kopa (``parashara_mood_names``, BPHS 45.8-10, beside the default list)."""
    from .shadbala import NATURAL_RELATIONS_9, compound_relationships
    signs = [int(norm360(x) // 30.0) for x in lons]
    lagna_sign = int(norm360(lagna_lon) // 30.0)
    comp = compound_relationships(varga_signs or signs)
    malefics_in = lambda s: sum(1 for k in range(9) if _MALEFIC[k] and signs[k] == s)  # noqa: E731
    names = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
    out = {}
    for k in range(9):
        lon, sign, planet = norm360(lons[k]), signs[k], k + 1
        deg = lon - sign * 30.0
        age = int((30.0 - deg if sign % 2 else deg) / 6.0)
        rasi_sign, sign = sign, (varga_signs[k] if varga_signs else sign)
        lord = _LORDS_1[sign]
        if _jh_owns(planet, sign) or sign == _SS.EXALTATION[k + 1]:  # BPHS 45.5: own sign or exaltation, awake
            alert = 0
        else:
            rel_alert = comp[k][lord - 1] if compound else NATURAL_RELATIONS_9[k][lord - 1]
            alert = 1 if rel_alert in (1, 2, 3) else 2
        rel = comp[k][lord - 1]
        need = 2 if _MALEFIC[k] else 1
        # Deeptadi flags: Deepta exalted, Swastha own (BPHS 45.8-10); Mudita, Saanta, Deena, Duhkhita by the lord's
        # relationship (45.8-10); Vikala with a malefic (45.8-10); Khala in a malefic's sign (PD 3.19, "union with the
        # Varga of a malefic"); Kopita within 6 degrees of the Sun (a convention for 45.8-10's "eclipsed by the Sun");
        # Lajjita in the 5th with a malefic and Garvita exalted or in moolatrikona (45.11-18)
        mood = [sign == _SS.EXALTATION[k + 1], _jh_owns(planet, sign), rel == 1, rel == 2, rel == 3, rel in (4, 5),
                malefics_in(sign) > need, lord in (1, 3, 7),
                k != 0 and abs(((lon - lons[0] + 180.0) % 360.0) - 180.0) <= 6.0,
                (sign - lagna_sign) % 12 == 4 and malefics_in(sign) > need - 1,
                sign == _SS.EXALTATION[k + 1] or sign == _MT_1[k]]
        # Parashara: the sign's dignity by the compound relationship, the company of a malefic (in the rasi) and the Sun's eclipse
        own, exalted, debilitated = _jh_owns(planet, sign), sign == _SS.EXALTATION[k + 1], sign == _SS.DEBILITATION[k + 1]
        mt = False
        if k < 7 and not varga_signs:     # BPHS's degrees in the rasi: Moon 0-3 Taurus and Mercury 0-15 Virgo exalted, then moolatrikona (counted as own)
            d = get_graha_dignity(names[k], lon)
            mt = d == "Moolatrikona"
            exalted, own = d == "Exalted", own or mt
        evil = [_SHORT[q] for q in range(9) if _MALEFIC[q] and q != k and signs[q] == rasi_sign]
        burnt = bool(combust and combust[k])
        bphs = [exalted, own, not own and rel == 1, not own and rel == 2, not own and rel == 3, bool(evil), not own and rel == 4, not own and rel == 5, burnt]
        lord_is = "%s's sign: %s" % (_SHORT[lord - 1], _RELATION.get(rel, "neutral"))
        why = ["Exalted", "Moolatrikona" if mt else "Own sign", lord_is, lord_is, lord_is, "With " + ", ".join(evil),
               lord_is, lord_is, "Combust: %.0f\u00b0 from Su" % abs(((lon - lons[0] + 180.0) % 360.0) - 180.0)]
        # BPHS 45.5: awake in own or exaltation, dreaming in a friend's or neutral's, asleep in an enemy's or in debilitation
        p_alert = 0 if own or exalted else 2 if debilitated else alert
        alert_why = (("Moolatrikona" if mt else "Own sign") if own else "Exalted") if own or exalted else "Debilitated" if debilitated else "%s's sign: %s" % (
            _SHORT[lord - 1], _RELATION.get(rel_alert, "neutral"))
        lo = age * 6 if not rasi_sign % 2 else 24 - age * 6
        age_why = "%d\u00b0 in an %s sign (%d\u2013%d\u00b0%s)" % (int(deg), "even" if rasi_sign % 2 else "odd", lo, lo + 6, ", counted back" if rasi_sign % 2 else "")
        sign = rasi_sign
        nav_no = int(0.3 * deg) + 1
        nak = int(lon * 0.075)
        moon_nak = int(norm360(lons[1]) * 0.075)
        act = ((nav_no * (nak + 1) * planet + lagna_sign + 1 + int(ghatis_since_sunrise) + 1 + moon_nak + 1)
               - 1) % 12
        # BPHS 45.30-37: the sub-state = ((avastha)^2 + the first syllable's anka value i) mod 12, plus the graha's
        # additive, mod 3 (1 Drishti, 2 Cheshta, 0 Vicheshta); one value for each anka value i = 1 .. 5
        inten = [((((act + 1) ** 2 + i - 1) % 12 + 1 + _SAYANADI_ADD[k]) - 1) % 3 for i in range(1, 6)]
        out[names[k]] = {"age": age, "alertness": alert, "mood": [i for i, f in enumerate(mood) if f],
                         "activity": act, "age_name": AGE[age], "alertness_name": ALERTNESS[alert],
                         "mood_names": ", ".join(MOOD[i] for i, f in enumerate(mood) if f),
                         "parashara_mood_names": ", ".join(PARASHARA_MOOD[i] for i, f in enumerate(bphs) if f),
                         "parashara_mood_why": list(dict.fromkeys(why[i] for i, f in enumerate(bphs) if f)),
                         "parashara_alertness_name": ALERTNESS[p_alert], "parashara_alertness_why": alert_why, "age_why": age_why,
                         "activity_name": ACTIVITY[act], "intensity": inten,
                         "intensity_names": [INTENSITY[i] for i in inten]}
    return out
