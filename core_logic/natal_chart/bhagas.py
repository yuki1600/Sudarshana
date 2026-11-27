"""bhagas: part of natal_chart (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Any, Dict, List, Tuple
from .signs import RASI_LORDS, RASI_NAMES_EN, norm360
from .vargas import compute_varga_d9

# ===========================================================================
# 1. Mrityu Bhagas (Fatal Degrees)
# docs/SOURCES.md section 4. The texts give the Moon's and the lagna's lists (PD 13.10-11, SAR ch. 5, HS 5.46-47)
# and differ among themselves; this full table, every graha and the lagna, is the one Settings > Mrityu Bhaga
# attributes to Saravali, Jataka Parijata and Sarvartha Chintamani. Its lagna row differs from PD 13.11 and
# HS 5.46-47 in Aries (1 against 8), Virgo (2 against 14) and Aquarius (24 against 21).
# ===========================================================================

MRITYU_BHAGA_PARASARA: Dict[str, List[float]] = {
    "Sun":     [20.0,  9.0, 12.0,  6.0,  8.0, 24.0, 16.0, 17.0, 22.0,  2.0,  3.0, 23.0],
    "Moon":    [ 8.0, 25.0, 22.0, 22.0, 21.0,  1.0,  4.0, 23.0, 18.0, 20.0, 20.0, 10.0],
    "Mars":    [19.0, 28.0, 25.0, 23.0, 29.0, 28.0, 14.0, 21.0,  2.0, 15.0, 11.0,  6.0],
    "Mercury": [15.0, 14.0, 13.0, 12.0,  8.0, 18.0, 20.0, 10.0, 21.0, 22.0,  7.0,  5.0],
    "Jupiter": [19.0, 29.0, 12.0, 27.0,  6.0,  4.0, 13.0, 10.0, 17.0, 11.0, 15.0, 28.0],
    "Venus":   [28.0, 15.0, 11.0, 17.0, 10.0, 13.0,  4.0,  6.0, 27.0, 12.0, 29.0, 19.0],
    "Saturn":  [10.0,  4.0,  7.0,  9.0, 12.0, 16.0,  3.0, 18.0, 28.0, 14.0, 13.0, 15.0],
    "Rahu":    [14.0, 13.0, 12.0, 11.0, 24.0, 23.0, 22.0, 21.0, 10.0, 20.0, 18.0,  8.0],
    "Ketu":    [ 8.0, 18.0, 20.0, 10.0, 21.0, 22.0, 23.0, 24.0, 11.0, 12.0, 13.0, 14.0],
    "Lagna":   [ 1.0,  9.0, 22.0, 22.0, 25.0,  2.0,  4.0, 23.0, 18.0, 20.0, 24.0, 10.0],
}

# The second table (Settings: "Follow Phala Deepika and Brihat Prajapatyam"): the Moon's degrees of PD 13.10,
# 26 12 13 25 24 11 26 14 13 25 5 12 (also UK's notes; SAR ch. 5 and HS 5.47 read 4 for Virgo)
MRITYU_BHAGA_SARAVALI: Dict[str, List[float]] = {
    **MRITYU_BHAGA_PARASARA,
    "Moon":    [26.0, 12.0, 13.0, 25.0, 24.0, 11.0, 26.0, 14.0, 13.0, 25.0,  5.0, 12.0],
}

def get_mrityu_bhaga_degree(graha_or_lagna: str, sign_index: int, scheme: str = "parasara") -> float:
    """
    Returns the fatal degree (0.0 to 30.0) for a planet or Lagna in a given sign (0..11).
    """
    table = MRITYU_BHAGA_SARAVALI if scheme.lower() == "saravali" else MRITYU_BHAGA_PARASARA
    degrees = table.get(graha_or_lagna, table.get("Lagna", [15.0]*12))
    return degrees[sign_index % 12]

def evaluate_mrityu_bhaga(
    graha_or_lagna: str,
    longitude: float,
    scheme: str = "parasara",
    orb_deg: float = 1.0
) -> Dict[str, Any]:
    """
    Evaluates whether a celestial body or Lagna is in Mrityu Bhaga (fatal degree).
    Computes exact angular distance from the Mrityu Bhaga center and detects if
    within trimsamsa / custom orb.
    """
    norm_lon = norm360(longitude)
    sign_idx = int(norm_lon // 30.0)
    deg_in_sign = norm_lon % 30.0
    center_deg = get_mrityu_bhaga_degree(graha_or_lagna, sign_idx, scheme)
    
    distance = abs(deg_in_sign - center_deg)
    is_in_orb = distance <= orb_deg
    is_exact_degree = int(deg_in_sign) == int(center_deg)

    return {
        "graha": graha_or_lagna,
        "longitude": norm_lon,
        "sign_index": sign_idx,
        "sign_name": RASI_NAMES_EN[sign_idx],
        "degree_in_sign": deg_in_sign,
        "mrityu_bhaga_center": center_deg,
        "distance_from_center": distance,
        "is_in_orb": is_in_orb,
        "is_exact_degree": is_exact_degree,
        "scheme": scheme
    }


# ===========================================================================
# 2. Pushkara Bhagas & Pushkaramshas (docs/SOURCES.md section 4)
# ===========================================================================

# Scheme 1, the default (Settings: "Given in Jataka Parijatam"): the Moon's Pushkara degrees of JP 1.58, the
# "auspicious degrees" UK's notes pair with the Mrityu bhagas
PUSHKARA_BHAGA_SCHEME1: List[float] = [
    21.0, 14.0, 18.0,  8.0, 19.0,  9.0, 24.0, 11.0, 23.0, 14.0, 19.0,  9.0
]

# Scheme 2 (Settings: "Given by Sri CS Patel in Nadi & Navamsha Astrology"): 21, 14, 24, 7 by element (fire, earth,
# air, water). The scheme names get_pushkara_bhaga_degree accepts are kept as they were
PUSHKARA_BHAGA_SCHEME2: List[float] = [
    21.0, 14.0, 24.0,  7.0, 21.0, 14.0, 24.0,  7.0, 21.0, 14.0, 24.0,  7.0
]

def get_pushkara_bhaga_degree(sign_index: int, scheme: str = "vidyamadhaviyam") -> float:
    """
    Returns the Pushkara Bhaga central degree in the given sign (0..11).
    """
    if scheme.lower() in ("jataka_parijata", "scheme2", "raman"):
        return PUSHKARA_BHAGA_SCHEME2[sign_index % 12]
    return PUSHKARA_BHAGA_SCHEME1[sign_index % 12]

def is_in_pushkaramsha(longitude: float) -> Tuple[bool, int, str]:
    """
    Evaluates if a longitude falls in a Pushkaramsha (auspicious Navamsa), by the common list (no verse
    checked; docs/SOURCES.md section 4):
    - Fire signs (Aries, Leo, Sag): 7th (Libra) & 9th (Sagittarius) navamsas
    - Earth signs (Taurus, Virgo, Cap): 3rd (Pisces) & 5th (Taurus) navamsas
    - Air signs (Gemini, Libra, Aqua): 6th (Pisces) & 8th (Taurus) navamsas
    - Water signs (Cancer, Scorpio, Pisces): 1st (Cancer) & 3rd (Virgo) navamsas
    
    Returns: (is_pushkaramsha, navamsa_sign_index, navamsa_sign_name)
    """
    norm_lon = norm360(longitude)
    sign_idx = int(norm_lon // 30.0)
    deg_in_sign = norm_lon % 30.0
    navamsa_idx = int(deg_in_sign // (30.0 / 9.0))  # 0 to 8
    
    element = sign_idx % 4
    elem_starts = [0, 9, 6, 3]
    actual_nav_sign = (elem_starts[element] + navamsa_idx) % 12

    pushkara_navamsas_by_element = [
        [6, 8],     # Fire: Libra, Sagittarius
        [11, 1],    # Earth: Pisces, Taurus
        [11, 1],    # Air: Pisces, Taurus
        [3, 5],     # Water: Cancer, Virgo
    ]
    
    is_pushkara = actual_nav_sign in pushkara_navamsas_by_element[element]
    return is_pushkara, actual_nav_sign, RASI_NAMES_EN[actual_nav_sign]

def evaluate_pushkara_bhaga(
    longitude: float,
    scheme: str = "vidyamadhaviyam",
    orb_deg: float = 1.0
) -> Dict[str, Any]:
    """
    Full evaluation of both Pushkara Bhaga degree center and Pushkaramsha.
    """
    norm_lon = norm360(longitude)
    sign_idx = int(norm_lon // 30.0)
    deg_in_sign = norm_lon % 30.0
    center_deg = get_pushkara_bhaga_degree(sign_idx, scheme)
    distance = abs(deg_in_sign - center_deg)
    is_in_bhaga = distance <= orb_deg
    
    is_pushkaramsha, nav_sign_idx, nav_sign_name = is_in_pushkaramsha(norm_lon)
    
    return {
        "longitude": norm_lon,
        "sign_index": sign_idx,
        "sign_name": RASI_NAMES_EN[sign_idx],
        "degree_in_sign": deg_in_sign,
        "pushkara_bhaga_center": center_deg,
        "distance_from_center": distance,
        "is_in_pushkara_bhaga": is_in_bhaga,
        "is_in_pushkaramsha": is_pushkaramsha,
        "navamsha_sign_index": nav_sign_idx,
        "navamsha_sign_name": nav_sign_name,
        "scheme": scheme
    }


# The Key Info rows: Sun .. Ketu, Maandi, Lagna (the tables above, the second Moon list with MBTablePreference 1)
# and the 2nd .. 12th house cusps (the lagna row).  A table degree N is taken as the N-th degree: its centre is
# N - 0.5 (MBLocationPreference 2, the default; 0: N + 0.5, 1: N), the three readings of Settings > Mrityu Bhaga.
# Maandi's row: as the Settings tables have it; no verse checked.
MRITYU_BHAGA_MAANDI = [23.0, 24.0, 11.0, 12.0, 13.0, 14.0, 8.0, 18.0, 20.0, 10.0, 21.0, 22.0]
_MB_ROWS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Maandi", "Lagna"]


def mrityu_bhaga_distance(row: str, lon: float, saravali: bool = False, location: int = 2) -> Tuple[float, bool]:
    """(distance from the mrityu bhaga centre, within 0.5 deg of it) as Key Info lists them; ``row`` one of
    _MB_ROWS (a house cusp uses "Lagna")."""
    sign = int(norm360(lon) // 30.0)
    table = MRITYU_BHAGA_MAANDI if row == "Maandi" else (MRITYU_BHAGA_SARAVALI if saravali else
                                                          MRITYU_BHAGA_PARASARA)[row]
    centre = table[sign] + (0.5 if location == 0 else 0.0 if location == 1 else -0.5)
    d = (lon - (sign * 30.0 + centre)) % 360.0
    if d > 180.0:
        d = 360.0 - d
    return d, d <= 0.5


def pushkara_position(lon: float, raman: bool = False) -> Tuple[bool, bool, float]:
    """(in pushkaramsa, in pushkara bhaga, distance from the bhaga centre): the bhaga table of JP 1.58 (scheme 1;
    ``raman`` picks scheme 2, C. S. Patel's) with its degree N centred at N - 0.5, within 0.5 deg; pushkaramsa by
    ``is_in_pushkaramsha``."""
    sign = int(norm360(lon) // 30.0)
    centre = (PUSHKARA_BHAGA_SCHEME2 if raman else PUSHKARA_BHAGA_SCHEME1)[sign] - 0.5
    d = (lon - (sign * 30.0 + centre)) % 360.0
    if d > 180.0:
        d = 360.0 - d
    return is_in_pushkaramsha(lon)[0], d <= 0.5, d


# ===========================================================================
# 3. Drekkana Systems (5 Variations) & 22nd Drekkana Engine (docs/SOURCES.md section 3; the 22nd drekkana's
# lord among the killers: PM 9.4)
# ===========================================================================

# Uma-Shambhu sign transposition: the cyclical drekkana with even signs counted backwards (signs 3-5 and 9-11
# swapped end for end)
UMA_SHAMBHU_SIGN_MAP = [0, 1, 2, 5, 4, 3, 6, 7, 8, 11, 10, 9]

def compute_drekkana(longitude: float, method: str = "parasara") -> Tuple[int, int, str]:
    """
    Calculates D-3 Drekkana sign and ruler under all 5 systems:
    - 'parasara' (Case 0): Traditional Parasara (1st=1st, 2nd=5th, 3rd=9th)
    - 'parivritti' (Case 1): Parivritti-traya (continuous 1..12 cycle)
    - 'somanatha' (Case 2): Direct for odd signs, reverse for even signs
    - 'jagannatha' (Case 3): Movable from same, fixed from 9th, dual from 5th
    - 'uma_shambhu' (Case 4): Re-interpreted Parasara with Uma-Shambhu mapping
    
    Returns: (drekkana_sign_index, decanate_num_1_to_3, drekkana_lord)
    """
    norm_lon = norm360(longitude)
    sign_idx = int(norm_lon // 30.0)
    deg_in_sign = norm_lon % 30.0
    decanate = int(deg_in_sign // 10.0)  # 0, 1, 2
    
    m = method.lower()
    if m in ("parivritti", "parivritti_traya", "cyclic"):
        d3_sign = (sign_idx * 3 + decanate) % 12
    elif m in ("somanatha", "somnath"):
        if sign_idx % 2 == 0:
            d3_sign = (sign_idx + decanate * 4) % 12
        else:
            base = (sign_idx + decanate * 4) % 12
            d3_sign = (11 - base) % 12
    elif m in ("jagannatha", "jagannath"):
        mod3 = sign_idx % 3
        if mod3 == 0:
            start_sign = sign_idx
        elif mod3 == 1:
            start_sign = (sign_idx + 8) % 12
        else:
            start_sign = (sign_idx + 4) % 12
        d3_sign = (start_sign + decanate * 4) % 12
    elif m in ("uma_shambhu", "uma_sambu"):
        p_sign = (sign_idx + decanate * 4) % 12
        d3_sign = UMA_SHAMBHU_SIGN_MAP[p_sign]
    else:
        d3_sign = (sign_idx + decanate * 4) % 12
        
    return d3_sign, decanate + 1, RASI_LORDS[d3_sign]

def compute_22nd_drekkana(
    reference_longitude: float,
    method: str = "parasara"
) -> Dict[str, Any]:
    """
    Computes the 22nd Drekkana (Kharesha) from a reference point (Lagna or Moon).
    The 22nd Drekkana spans the 1st decanate of the 8th house (reference + 210° to 220°).
    """
    norm_lon = norm360(reference_longitude)
    target_lon = norm360(norm_lon + 210.0)
    d3_sign, decanate_num, lord = compute_drekkana(target_lon, method=method)
    
    return {
        "drekkana_number": 22,
        "method": method,
        "target_longitude": target_lon,
        "d3_sign_index": d3_sign,
        "d3_sign_name": RASI_NAMES_EN[d3_sign],
        "decanate_num": decanate_num,
        "lord": lord,
        "span_start": target_lon,
        "span_end": norm360(target_lon + 10.0)
    }


# ===========================================================================
# 4. 64th Navamsha Engine (PM 8.61: the 64th navamsa from the Moon's navamsa)
# ===========================================================================

def compute_64th_navamsha(reference_longitude: float) -> Dict[str, Any]:
    """
    Computes the 64th Navamsha (Kharesha) from a reference point (Lagna or Moon).
    The 64th Navamsha is the 8th house from D-9 Lagna/Moon (reference + 210°).
    63 completed navamsas = 63 * 3°20' = 210°.
    """
    norm_lon = norm360(reference_longitude)
    target_lon = norm360(norm_lon + 210.0)
    d9_sign = compute_varga_d9(target_lon)
    lord = RASI_LORDS[d9_sign]
    
    return {
        "navamsha_number": 64,
        "target_longitude": target_lon,
        "d9_sign_index": d9_sign,
        "d9_sign_name": RASI_NAMES_EN[d9_sign],
        "lord": lord,
        "span_start": target_lon,
        "span_end": norm360(target_lon + (30.0 / 9.0))
    }

def compute_all_malicious_divisions(lagna_longitude: float, moon_longitude: float) -> Dict[str, Any]:
    """
    Coordinates calculation of all 22nd Drekkana variants and 64th Navamshas
    for both Lagna and Moon (as Key Info's "Malicious Divisions" rows show them).
    """
    drekkana_methods = [
        "parasara", "parivritti", "somanatha", "jagannatha", "uma_shambhu"
    ]
    
    lagna_drekkanas = {
        m: compute_22nd_drekkana(lagna_longitude, method=m)
        for m in drekkana_methods
    }
    moon_drekkanas = {
        m: compute_22nd_drekkana(moon_longitude, method=m)
        for m in drekkana_methods
    }
    
    lagna_64th = compute_64th_navamsha(lagna_longitude)
    moon_64th = compute_64th_navamsha(moon_longitude)
    
    return {
        "lagna_22nd_drekkanas": lagna_drekkanas,
        "moon_22nd_drekkanas": moon_drekkanas,
        "lagna_64th_navamsha": lagna_64th,
        "moon_64th_navamsha": moon_64th,
    }

# Marana Karaka Sthana (MKS / Death-Inflicting Placements): Sanjay Rath, Crux of Vedic Astrology (1998), as his
# school teaches the list (docs/SOURCES.md section 2)
MKS_HOUSES = {
    "Sun": 12,
    "Moon": 8,
    "Mars": 7,
    "Mercury": 7,
    "Jupiter": 3,
    "Venus": 6,
    "Saturn": 1,
    "Rahu": 9
}

def detect_marana_karaka_sthana(
    lagna_sign: int,
    planetary_signs: Dict[str, int]
) -> Dict[str, Any]:
    """
    Evaluates Marana Karaka Sthana (MKS) for all planets.
    A planet in MKS feels like death regarding its portfolio and natural significations.
    - Sun in 12th (Loss of Vitality/Ego)
    - Moon in 8th (Mental Agony/Depression)
    - Mars in 7th (Destruction of Marital Harmony/Kuja Dosha root)
    - Mercury in 7th (Loss of Business/Impotence in Relationships)
    - Jupiter in 3rd (Destruction of Wisdom in impulsive courage)
    - Venus in 6th (Affliction of Reproductive vitality/Disease in Romance)
    - Saturn in 1st (Cold misery/Physical suffering on the body)
    - Rahu in 9th (Affliction of Dharma and Father)
    """
    mks_afflicted = []
    status = {}
    
    for planet, mks_house in MKS_HOUSES.items():
        if planet not in planetary_signs:
            continue
        p_sign = planetary_signs[planet]
        actual_house = ((p_sign - lagna_sign) % 12) + 1
        is_in_mks = (actual_house == mks_house)
        
        info = {
            "planet": planet,
            "house": actual_house,
            "mks_house": mks_house,
            "is_mks": is_in_mks
        }
        if is_in_mks:
            mks_afflicted.append(planet)
        status[planet] = info
        
    return {
        "mks_planets": mks_afflicted,
        "total_mks_count": len(mks_afflicted),
        "details": status
    }
