"""
core_logic/transits.py
======================
Modularized Calculation Engine for Transits (Gochara, Vedha, Sade Sati),
Sarvatobhadra Chakra, and Kota Chakra.

Sources (docs/SOURCES.md section 12): gochara and vedha PD 26.1-8; murthis, taras, special nakshatras, nakshatra
aspects, latta and the Sarvatobhadra chakra PVR ch. 26; kakshyas PVR 25.5.2 and PM; Sapta Shalaka PD 26.26-27.
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Any

# Favorable Gochara transit houses from natal Moon (1-indexed)
# and their corresponding Vedha (obstruction) houses
GOCHARA_AND_VEDHA = {
    "Sun": {
        3: 9, 6: 12, 10: 4, 11: 5
    },
    "Moon": {
        1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8
    },
    "Mars": {
        3: 12, 6: 9, 11: 5
    },
    "Mercury": {
        2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12
    },
    "Jupiter": {
        2: 12, 5: 4, 7: 3, 9: 10, 11: 8
    },
    "Venus": {
        1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3
    },
    "Saturn": {
        3: 12, 6: 9, 11: 5
    },
    "Rahu": {
        3: 12, 6: 9, 11: 5
    },
    "Ketu": {
        3: 12, 6: 9, 11: 5
    }
}

# Father-son pairs exempt from causing Vedha to each other
EXEMPT_VEDHA_PAIRS = [
    ("Sun", "Saturn"),
    ("Saturn", "Sun"),
    ("Moon", "Mercury"),
    ("Mercury", "Moon")
]

MURTHI_CLASSES = {
    # House from natal Moon at moment of ingress -> (Murthi Name, Metal, Quality, Score Multiplier)
    1: ("Swarna", "Gold", "Very Auspicious (Supreme Favorable)", 1.5),
    6: ("Swarna", "Gold", "Very Auspicious (Supreme Favorable)", 1.5),
    11: ("Swarna", "Gold", "Very Auspicious (Supreme Favorable)", 1.5),
    2: ("Rajata", "Silver", "Auspicious (Favorable)", 1.25),
    5: ("Rajata", "Silver", "Auspicious (Favorable)", 1.25),
    9: ("Rajata", "Silver", "Auspicious (Favorable)", 1.25),
    3: ("Taamra", "Copper", "Neutral / Mediocre", 1.0),
    7: ("Taamra", "Copper", "Neutral / Mediocre", 1.0),
    10: ("Taamra", "Copper", "Neutral / Mediocre", 1.0),
    4: ("Loha", "Iron", "Inauspicious / Adversity", 0.5),
    8: ("Loha", "Iron", "Inauspicious / Adversity", 0.5),
    12: ("Loha", "Iron", "Inauspicious / Adversity", 0.5),
}

def compute_murthi_nirnaya(
    ingress_moon_sign_idx: int,
    natal_moon_sign_idx: int
) -> Dict[str, Any]:
    """
    Computes Murthi Nirnaya (Metallic Form Determination) for a transiting planet.
    The murthis of PVR 26.2: the Moon's sign at the planet's last entry into its current sign, counted from the
    natal reference body (default Moon).

    When a planet ingresses into a sign, its Murthi is evaluated by the Moon's house position
    relative to the natal Moon at that ingress moment:
    - 1st, 6th, 11th from natal Moon: Swarna (Gold - Very Good)
    - 2nd, 5th, 9th from natal Moon: Rajata (Silver - Good)
    - 3rd, 7th, 10th from natal Moon: Taamra (Copper - Average/Mediocre)
    - 4th, 8th, 12th from natal Moon: Loha (Iron - Very Bad)
    """
    house = ((ingress_moon_sign_idx - natal_moon_sign_idx) % 12) + 1
    name, metal, quality, mult = MURTHI_CLASSES.get(house, ("Taamra", "Copper", "Neutral", 1.0))
    return {
        "murthi_name": name,
        "metal": metal,
        "quality": quality,
        "house_from_natal_moon": house,
        "multiplier": mult,
        "description": f"Graha is a {name} Murthi ({metal.lower()}) in transit ({quality.lower()})."
    }

from .utils import norm360

def evaluate_gochara_transit(
    planet: str,
    transit_sign_idx: int,
    natal_moon_sign_idx: int,
    all_transit_signs: Dict[str, int],
    ingress_moon_sign_idx: Optional[int] = None
) -> Dict[str, Any]:
    """
    Evaluates whether a planet's transit is auspicious (Gochara Phala)
    and whether it is obstructed by Vedha from another transiting body.
    Also computes Murthi Nirnaya if ingress_moon_sign_idx is provided.
    Source: PD 26.2-8 (good houses and their vedha places).
    """
    house_from_moon = ((transit_sign_idx - natal_moon_sign_idx) % 12) + 1
    rules = GOCHARA_AND_VEDHA.get(planet, {})
    
    is_favorable = house_from_moon in rules
    has_vedha = False
    vedha_planet = None
    vedha_house = None
    
    if is_favorable:
        vedha_house = rules[house_from_moon]
        target_vedha_sign = (natal_moon_sign_idx + vedha_house - 1) % 12
        
        # Check if any transiting planet occupies this vedha sign
        for other_p, other_sign in all_transit_signs.items():
            if other_p == planet:
                continue
            if other_sign == target_vedha_sign:
                # Check exemption
                if (planet, other_p) in EXEMPT_VEDHA_PAIRS:
                    continue
                has_vedha = True
                vedha_planet = other_p
                break

    # Vipareeta Vedha (Reverse Vedha):
    # When a transit is in an unfavorable house that acts as a Vedha house,
    # a planet in the corresponding favorable house obstructs the malefic effect.
    rev_rules = {v_h: f_h for f_h, v_h in rules.items()}
    vipareeta_vedha_active = False
    vipareeta_vedha_planet = None
    vipareeta_neutralizing_house = None
    
    if not is_favorable and house_from_moon in rev_rules:
        vipareeta_neutralizing_house = rev_rules[house_from_moon]
        target_vip_sign = (natal_moon_sign_idx + vipareeta_neutralizing_house - 1) % 12
        for other_p, other_sign in all_transit_signs.items():
            if other_p == planet:
                continue
            if other_sign == target_vip_sign:
                if (planet, other_p) in EXEMPT_VEDHA_PAIRS:
                    continue
                vipareeta_vedha_active = True
                vipareeta_vedha_planet = other_p
                break
                
    if is_favorable and not has_vedha:
        status = "Favorable"
    elif is_favorable and has_vedha:
        status = "Obstructed by Vedha"
    elif not is_favorable and vipareeta_vedha_active:
        status = "Unfavorable (Nullified by Vipareeta Vedha)"
    else:
        status = "Unfavorable"

    murthi = None
    if ingress_moon_sign_idx is not None:
        murthi = compute_murthi_nirnaya(ingress_moon_sign_idx, natal_moon_sign_idx)
    
    return {
        "planet": planet,
        "house_from_moon": house_from_moon,
        "is_naturally_favorable": is_favorable,
        "vedha_house": vedha_house,
        "has_vedha": has_vedha,
        "vedha_planet": vedha_planet,
        "vipareeta_vedha_active": vipareeta_vedha_active,
        "vipareeta_vedha_planet": vipareeta_vedha_planet,
        "vipareeta_neutralizing_house": vipareeta_neutralizing_house,
        "status": status,
        "murthi_nirnaya": murthi
    }

def check_sade_sati(saturn_sign_idx: int, natal_moon_sign_idx: int) -> Dict[str, Any]:
    """
    Evaluates Saturn's 7.5-year Sade Sati cycle:
    - 12th from Moon: Phase 1 (Rising / Arising)
    - 1st from Moon (Janma Shani): Phase 2 (Peak / Core)
    - 2nd from Moon: Phase 3 (Setting / Final)
    Also checks Kantaka Shani (4th, 8th) and Ashtama Shani (8th).
    """
    house_from_moon = ((saturn_sign_idx - natal_moon_sign_idx) % 12) + 1
    
    is_sade_sati = house_from_moon in [12, 1, 2]
    phase_names = {
        12: "Phase 1 - Rising (12th from Moon)",
        1:  "Phase 2 - Peak (Janma Shani, on Moon)",
        2:  "Phase 3 - Setting (2nd from Moon)"
    }
    phase = phase_names.get(house_from_moon, "None")
    
    is_kantaka = house_from_moon in [4, 8]
    is_ashtama = (house_from_moon == 8)
    
    return {
        "house_from_moon": house_from_moon,
        "is_sade_sati": is_sade_sati,
        "sade_sati_phase": phase,
        "is_kantaka_shani": is_kantaka,
        "is_ashtama_shani": is_ashtama
    }

# ---------------------------------------------------------------------------
# Kota Chakra Subsystem (no verse checked; docs/SOURCES.md section 12)
# ---------------------------------------------------------------------------

KOTA_SECTORS = ["Stambha", "Madhya", "Prakaara", "Bahya"]

def compute_kota_chakra_placement(transit_nakshatra_idx: int, janma_nakshatra_idx: int) -> Dict[str, Any]:
    """
    Computes Kota Chakra (Fort Wheel) placement for a transiting planet:
    Delegates to the authentic 4-concentric fortress engine:
    1. Stambha (Center Pillar) - Vital health core (j, j+7, j+14, j+21)
    2. Madhya (Inner Defense Courtyard)
    3. Prakaara (Fort Walls / Ramparts)
    4. Bahya (Surrounding Exterior Field)
    """
    from .chakras import compute_kota_chakra_structure, NAKSHATRA_NAMES
    
    struct = compute_kota_chakra_structure(janma_nakshatra_idx)
    target_nak = NAKSHATRA_NAMES[transit_nakshatra_idx % 27]
    
    stambha_list = struct.get("stambha", struct.get("stambha_nakshatras", []))
    madhya_list = struct.get("madhya", struct.get("madhya_nakshatras", []))
    prakaara_list = struct.get("prakaara", struct.get("prakaara_nakshatras", []))
    
    if target_nak in stambha_list:
        zone_name = "Stambha"
        zone_idx = 0
    elif target_nak in madhya_list:
        zone_name = "Madhya"
        zone_idx = 1
    elif target_nak in prakaara_list:
        zone_name = "Prakaara"
        zone_idx = 2
    else:
        zone_name = "Bahya"
        zone_idx = 3
        
    dist = (transit_nakshatra_idx - janma_nakshatra_idx) % 27
    is_entry_road = (dist % 2 == 0)
    
    return {
        "zone": zone_name,
        "zone_index": zone_idx,
        "road_direction": "Praveesha (Entry)" if is_entry_road else "Nirgamana (Exit)",
        "is_critical": zone_name in ["Stambha", "Prakaara"]
    }

# ---------------------------------------------------------------------------
# Latta (Planetary Kick) Engine
# PD 26.42-47 (the forward and rear lattas, their effects, and lattas together); the options 'Latta (planetary
# kick)' and 'Highlight lattas'
# ---------------------------------------------------------------------------

# Forward (Puro-Latta) & Backward (Prishto-Latta) kick offsets in 27 Nakshatras:
# Sun kicks 12th forward; Mars kicks 3rd forward; Jupiter kicks 6th forward; Saturn kicks 8th forward
# Moon kicks 22nd backward; Mercury kicks 7th backward; Venus kicks 5th backward; Rahu kicks 9th backward
LATTA_RULES = {
    "Sun":     {"direction": "forward",  "count": 12},
    "Mars":    {"direction": "forward",  "count": 3},
    "Jupiter": {"direction": "forward",  "count": 6},
    "Saturn":  {"direction": "forward",  "count": 8},
    "Moon":    {"direction": "backward", "count": 22},
    "Mercury": {"direction": "backward", "count": 7},
    "Venus":   {"direction": "backward", "count": 5},
    "Rahu":    {"direction": "backward", "count": 9}
}

def compute_latta_afflictions(
    transit_nakshatras: Dict[str, int],
    target_nakshatra_idx: int
) -> Dict[str, Any]:
    """
    Computes Latta (Planetary Kick) afflictions on a target asterism (e.g. Janma Nakshatra or Lagna star).
    A planet kicks another star either forward (Puro-Latta) or backward (Prishto-Latta).
    If the target asterism receives a kick from a malefic, heavy obstacles and sudden distress occur.
    """
    kicking_planets = []
    latta_details = {}
    
    for planet, rule in LATTA_RULES.items():
        if planet not in transit_nakshatras:
            continue
        p_nak = transit_nakshatras[planet] % 27
        if rule["direction"] == "forward":
            kicked_nak = (p_nak + rule["count"] - 1) % 27
        else:
            kicked_nak = (p_nak - rule["count"] + 1) % 27
            
        hits_target = (kicked_nak == (target_nakshatra_idx % 27))
        info = {
            "planet": planet,
            "planet_nakshatra": p_nak,
            "direction": rule["direction"],
            "count": rule["count"],
            "kicked_nakshatra": kicked_nak,
            "afflicts_target": hits_target
        }
        latta_details[planet] = info
        if hits_target:
            kicking_planets.append(planet)
            
    return {
        "target_nakshatra_idx": target_nakshatra_idx % 27,
        "is_afflicted_by_latta": len(kicking_planets) > 0,
        "kicking_planets": kicking_planets,
        "latta_details": latta_details
    }

# ---------------------------------------------------------------------------
# Anga Graha Transits (Planetary Limb Placement)
# A simple head-to-foot list of the 27 stars from the janma star (no verse checked).  The app's "Anga graha"
# view uses key_info.anga_graha instead, the per-graha tables of PD 26.35-40 (the Sun's is 26.35)
# ---------------------------------------------------------------------------

ANGA_REGIONS = [
    (1, "Head (Murdha)"),
    (3, "Eyes & Face (Mukha)"),
    (5, "Neck & Throat (Kantha)"),
    (7, "Chest & Heart (Hridaya)"),
    (9, "Right Hand (Dakshina Hasta)"),
    (11, "Left Hand (Vama Hasta)"),
    (13, "Belly & Navel (Udara)"),
    (15, "Waist & Generative Organs (Kati)"),
    (18, "Thighs (Uru)"),
    (21, "Knees & Calves (Janu)"),
    (24, "Ankles (Gulpha)"),
    (27, "Feet (Pada)")
]

def compute_anga_graha_transits(
    transit_nakshatras: Dict[str, int],
    janma_nakshatra_idx: int
) -> Dict[str, Any]:
    """
    Computes Anga Graha transits: Allocates transiting bodies to physiological limb regions
    reckoned from Janma Nakshatra (Moon star).
    Benefics in favorable limbs bless those faculties; malefics cause physiological strain.
    """
    limb_placements = {}
    for planet, nak_idx in transit_nakshatras.items():
        rel_nak = ((nak_idx - janma_nakshatra_idx) % 27) + 1
        matched_limb = "Feet (Pada)"
        for max_n, limb_name in ANGA_REGIONS:
            if rel_nak <= max_n:
                matched_limb = limb_name
                break
        limb_placements[planet] = {
            "nakshatra_offset_from_janma": rel_nak,
            "anatomical_limb": matched_limb
        }
    return {
        "janma_nakshatra_idx": janma_nakshatra_idx % 27,
        "anga_placements": limb_placements
    }


# ---------------------------------------------------------------------------
# Transit aspects of the Transits tab (a convention: the orbs and thresholds below)
# ---------------------------------------------------------------------------
# The mode picks the test: 1 graha drishti, 2 squares, 3 trines, otherwise drik virupas >= 80; orbs 4 deg.
TRANSIT_ORB = 4.0
TRANSIT_MIN_VIRUPAS = 80.0


def _fold(d: float) -> float:
    while d < 0.0:
        d += 360.0
    while d >= 360.0:
        d -= 360.0
    return d


def transit_aspect_orb(natal: float, transit: float, planet: int, orb: float = TRANSIT_ORB) -> Tuple[float, str]:
    """(orb, strength) of planet ``planet`` (1 Sun .. 9 Ketu) at ``transit`` on a
    point at ``natal``: "Full" at 0 / 180, the special aspects "Full" and the others 3/4, 1/2, 1/4 (Rahu counted
    back, and also full at 330 - where the orb is taken from 60); Ketu none."""
    d = _fold(natal - transit)
    if planet == 9:
        return d, "None"
    if planet == 8:
        d = 360.0 - d
    if d < orb:
        return abs(d), "Full"
    if 360.0 - orb <= d:
        return abs(360.0 - d), "Full"
    if 180.0 - orb <= d < orb + 180.0:
        return abs(d - 180.0), "Full"
    if 330.0 - orb <= d < orb + 330.0:
        return abs(d - 60.0), "Full" if planet == 8 else "None"
    for centre, full, part in ((60.0, (7,), "1/4"), (90.0, (3,), "3/4"), (120.0, (5, 8), "1/2"),
                               (210.0, (3,), "3/4"), (240.0, (5, 8), "1/2"), (270.0, (7,), "1/4")):
        if centre - orb <= d < orb + centre:
            return abs(d - centre), "Full" if planet in full else part
    return d, "None"


def _orb_to(natal: float, transit: float, planet: int, orb: float, centres) -> float:
    d = _fold(natal - transit)
    if planet in (8, 9):
        d = 360.0 - d
    if d < orb:
        return abs(d)
    if 360.0 - orb <= d:
        return abs(360.0 - d)
    for c in centres:
        if c - orb <= d < orb + c:
            return abs(d - c)
    return 360.0


def transit_orb_square(natal: float, transit: float, planet: int, orb: float = TRANSIT_ORB) -> float:
    """Orb to the nearest of 0 / 90 / 180 / 270 (nodes counted back),
    360 when none is within ``orb``."""
    return _orb_to(natal, transit, planet, orb, (90.0, 180.0, 270.0))


def transit_orb_trine(natal: float, transit: float, planet: int, orb: float = TRANSIT_ORB) -> float:
    """Orb to the nearest of 0 / 120 / 240 / 180 (nodes counted back),
    360 when none is within ``orb``."""
    return _orb_to(natal, transit, planet, orb, (120.0, 240.0, 180.0))


def transit_aspect_hit(natal: float, transit: float, planet: int, mode: int = 1,
                       orb: float = TRANSIT_ORB) -> Optional[float]:
    """Whether the Transits tab lists the pair, and the orb (mode 1: graha drishti of strength Full, 3/4 or 1/2;
    2 squares; 3 trines) or the virupas (else: shadbala.aspect_value, truncated, at least 80)."""
    if mode == 1:
        o, s = transit_aspect_orb(natal, transit, planet, orb)
        return o if s not in ("None", "1/4") else None
    if mode in (2, 3):
        o = (transit_orb_square if mode == 2 else transit_orb_trine)(natal, transit, planet, orb)
        return o if o < 360.0 else None
    from .shadbala import aspect_value
    v = abs(int(aspect_value(natal - transit, planet)))
    return float(v) if v >= TRANSIT_MIN_VIRUPAS else None


# The transit calendar (15 rows, 1 day apart). Good houses (> 0) from the Moon or lagna, planets 1 Sun .. 9 Ketu,
# houses 1..12: PD 26.2-8 (Rahu and Ketu as Saturn):
GOCHARA_GOOD = {
    1: [0, 0, 1, 0, 0, 1, 0, -1, 0, 1, 1, -1], 2: [1, 0, 1, 0, 0, 1, 1, -1, 0, 1, 1, -1],
    3: [0, 0, 1, 0, 0, 1, 0, -1, 0, 0, 1, -1], 4: [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, -1],
    5: [0, 1, 0, 0, 1, 0, 1, -1, 1, 0, 1, -1], 6: [1, 1, 1, 1, 1, -1, 0, 1, 1, 0, 1, 1],
    7: [-1, -1, 1, -1, 0, 1, 0, -1, 0, 0, 1, -1], 8: [0, 0, 1, 0, 0, 1, 0, -1, 0, 0, 1, -1],
    9: [0, 0, 1, 0, 0, 1, 0, -1, 0, 0, 1, -1]}
# Vedha house of each good house (PD 26.3-8). Two entries differ from PD as the reference table has them: Mercury's
# 10th takes vedha from the 7th (PD 26.6: the 8th), and Venus's 11th and 12th from the 6th and 3rd (PD 26.8: the 3rd
# and 6th). The table has no rows for Rahu / Ketu; the bytes that follow it are read, and those
# values are kept so the results match (none is a house, so nothing obstructs them).
GOCHARA_VEDHA = {
    1: [0, 0, 9, 0, 0, 12, 0, 0, 0, 4, 5, 0], 2: [5, 0, 9, 0, 0, 12, 2, 0, 0, 4, 8, 0],
    3: [0, 0, 12, 0, 0, 9, 0, 0, 0, 0, 5, 0], 4: [0, 5, 0, 3, 0, 9, 0, 1, 0, 7, 12, 0],
    5: [0, 12, 0, 0, 4, 0, 3, 0, 10, 0, 8, 0], 6: [8, 7, 1, 10, 9, 0, 0, 5, 11, 0, 6, 3],
    7: [0, 0, 12, 0, 0, 9, 0, 0, 0, 0, 5, 0],
    8: [0, 0, 543973748, 0, 0, 1668179314, 0, 0, 0, 0, 2716453, 0],
    9: [0, 0, 1869881441, 0, 0, 1702240370, 0, 0, 0, 0, 26984, 0]}
TARA_GOOD = (1, 1, 0, 1, 0, 1, 0, 1, 1)                   # Janma .. Parama Mitra (PVR 26.4.1)
KAKSHYA_LORDS = (7, 5, 3, 1, 6, 4, 2, 0)                  # Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna (PVR 25.5.2)


def gochara_vedha(transit_signs: List[int], planet: int, house: int) -> bool:
    """Whether ``planet`` (1..9) in ``house`` (0-based, from the Moon or lagna) is in a good house obstructed by a
    graha in its vedha sign (counting Sun .. Ketu of ``transit_signs``, points 0..9); a lone Saturn does not
    obstruct the Sun and vice versa, nor Mercury the Moon and vice versa (PD 26.3-5)."""
    if GOCHARA_GOOD[planet][house] <= 0:
        return False
    sign = (transit_signs[planet] + GOCHARA_VEDHA[planet][house] - house + 143) % 12
    n = sum(1 for p in range(1, 10) if transit_signs[p] == sign)
    if n == 1 and ((planet == 1 and transit_signs[7] == sign) or (planet == 7 and transit_signs[1] == sign)
                   or (planet == 2 and transit_signs[4] == sign)):
        return False
    return n > 0 and not (n == 1 and planet == 4 and transit_signs[2] == sign)


def gochara_row(transit_signs: List[int], transit_lons: List[float], transit_naks: List[int],
                      natal_signs: List[int], natal_moon_nak: int, planet: int) -> Dict[str, Any]:
    """One planet's columns of the transit calendar: house from the natal Moon and lagna (0-based),
    whether good and obstructed, the tara from the natal Moon's nakshatra (and whether good) and the kakshya lord
    (eighths of the sign, KAKSHYA_LORDS).  The bindu columns come from the natal ashtakavarga (not here)."""
    hm = (transit_signs[planet] - natal_signs[2] + 12) % 12
    hl = (transit_signs[planet] - natal_signs[0] + 12) % 12
    tara = (transit_naks[planet] - natal_moon_nak + 27) % 9
    return {"house_moon": hm, "good_moon": GOCHARA_GOOD[planet][hm] > 0,
            "vedha_moon": gochara_vedha(transit_signs, planet, hm),
            "house_lagna": hl, "good_lagna": GOCHARA_GOOD[planet][hl] > 0,
            "vedha_lagna": gochara_vedha(transit_signs, planet, hl),
            "tara": tara, "tara_good": bool(TARA_GOOD[tara]),
            "kakshya_lord": KAKSHYA_LORDS[int((transit_lons[planet] % 30.0) / 3.75)]}


_YOGINI_START = (0, 6, 5, 7, 2, 4, 1)                    # by vedic weekday (Sunday 0)
_YOGINI_NAKS = (0, 20, 7, 27, 14, 6, 21, 13)              # nakshatras of 28 by yamardha


def yogini_mrityu(janma_ghatis: float, weekday: int) -> Tuple[int, int]:
    """The nakshatras (of 28, 0 = Aswini) of the Yogini and of Mrityu at birth (PM ch. 16)
    for the chakra view: the yamardha (3.75 ghatis from sunrise) picks a nakshatra of _YOGINI_NAKS (Yogini from
    the weekday's start), the sixth of it (1.6 per ghati) moves away from it, folding back from the next one
    past the middle; the 16th yamardha takes the next weekday's start (Mrityu: 20)."""
    k = int(janma_ghatis * 0.26666666666666666)
    part = int((janma_ghatis - k * 3.75) * 1.6)

    def place(first: int, nxt: int) -> int:
        n, p = first, part
        if p > 3:
            n, p = nxt, 6 - p
        return ((p + n) if n % 7 == 0 else (n - p)) % 28
    s = _YOGINI_START[weekday]
    yogini = place(_YOGINI_NAKS[(k + s) % 8],
                   _YOGINI_NAKS[_YOGINI_START[(weekday + 1) % 7]] if k == 15 else _YOGINI_NAKS[(k + s + 1) % 8])
    mrityu = place(_YOGINI_NAKS[(k + 1) % 8], 20 if k == 15 else _YOGINI_NAKS[(k + 2) % 8])
    return yogini, mrityu


# The Longitude Correlation tab's natal points and vargas
CORRELATION_VARGAS = (1, 9, 7, 10, 11, 12, 16, 20, 24, 30, 60)
CORRELATION_ORDER = ("Jupiter", "Saturn", "Rahu", "Ketu", "Mars", "Sun", "Venus", "Mercury", "Moon")
_PLANET_INDEX = {"Sun": 1, "Moon": 2, "Mars": 3, "Mercury": 4, "Jupiter": 5, "Venus": 6, "Saturn": 7, "Rahu": 8, "Ketu": 9}


def longitude_correlation(transit: Dict[str, float], natal_points: Dict[str, float], varga_points: Dict[str, float] = None,
                          threshold: float = TRANSIT_MIN_VIRUPAS) -> Dict[str, Dict[tuple, float]]:
    """{transit planet: {(natal point, division): aspect %}} of the pairs at or above ``threshold``, by Parasara's aspects
    (the tab's first rule). ``natal_points`` give the D-1 rows. ``varga_points`` give the other vargas' rows: they are read
    from the chart cache, which then holds the transit chart, so pass the transit chart's points to reproduce it, and leave
    it out (the natal points) for what the tab says it shows."""
    from .varga_charts import varga_longitude
    from .shadbala import aspect_value
    source = varga_points or natal_points
    out = {}
    for p in CORRELATION_ORDER:
        rows = {}
        for name, lon in natal_points.items():
            for d in CORRELATION_VARGAS:
                x = lon if d == 1 else varga_longitude(source[name], d)
                v = aspect_value(x - transit[p], _PLANET_INDEX[p])
                if v >= threshold:
                    rows[(name, d)] = v
        out[p] = rows
    return out
