"""
core_logic/tajika.py
====================
Modularized Calculation Engine for Tajika Varshaphal (Annual Horoscopy),
16 Classical Yogas, 50+ Sahams, Muntha, and Varsheshwara.

Sources (docs/SOURCES.md section 13): Tajika Neelakanthi (TN), cited through B. V. Raman's English account,
Varshaphal (1941; VAR): aspects and balas VAR ch. III arts. 12-40, the year lord ch. IV arts. 42-47, the Tajika
yogas ch. VII arts. 57-63, the sahams ch. VII art. 64 on; PVR ch. 27-30.
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional, Any

# Planetary Deeptamsas (Orbs of influence in degrees) per Tajika Neelakanthi
DEEPTAMSA = {
    "Sun": 15.0,
    "Moon": 12.0,
    "Mars": 8.0,
    "Mercury": 7.0,
    "Jupiter": 9.0,
    "Venus": 7.0,
    "Saturn": 9.0
}

# Mean daily motion in longitude (degrees/day)
PLANET_DAILY_SPEEDS = {
    "Moon": 13.176,
    "Mercury": 1.383,
    "Venus": 1.200,
    "Sun": 0.9856,
    "Mars": 0.524,
    "Jupiter": 0.083,
    "Saturn": 0.033
}

from .utils import norm360
from .natal_chart import RASI_LORDS

# Sign Rulers alias for backward compatibility
SIGN_LORDS = RASI_LORDS

def compute_muntha(natal_asc_lon: float, birth_year: int, target_year: int) -> Dict[str, Any]:
    """
    Computes Muntha sign and longitude for a solar return year:
    Formula: Muntha sign = (Natal Ascendant Sign + Completed Years) % 12.
    Degrees in Muntha sign match degrees in natal Ascendant.
    Source: TN (VAR ch. IV art. 45; PVR ch. 27).
    """
    completed_years = target_year - birth_year
    natal_asc_sign = int(norm360(natal_asc_lon) // 30.0)
    deg_in_sign = natal_asc_lon - (natal_asc_sign * 30.0)
    
    muntha_sign = (natal_asc_sign + completed_years) % 12
    muntha_lon = norm360((muntha_sign * 30.0) + deg_in_sign)
    muntha_lord = SIGN_LORDS[muntha_sign]
    
    return {
        "muntha_sign_idx": muntha_sign,
        "muntha_lon": muntha_lon,
        "deg_in_sign": deg_in_sign,
        "lord": muntha_lord,
        "completed_years": completed_years
    }

# ---------------------------------------------------------------------------
# 16 Tajika Yogas Detection Engine (TN; VAR ch. VII arts. 57-63)
# ---------------------------------------------------------------------------

TAJIKA_ASPECTS = {
    # Sextile (friendly)
    60.0: ("Friendly", "Mitra"),
    # Trine (very friendly)
    120.0: ("Very Friendly", "Pratyaksha Mitra"),
    # Square (hostile)
    90.0: ("Hostile", "Shatru"),
    # Opposition (very hostile)
    180.0: ("Very Hostile", "Pratyaksha Shatru"),
    # Conjunction (direct union)
    0.0: ("Conjunction", "Samyukta")
}

def is_within_tajika_orb(planet1: str, planet2: str, angular_dist: float) -> Tuple[bool, float]:
    """
    Checks if two planets are within their mutual orb of aspect:
    Orb threshold = (Deeptamsa(P1) + Deeptamsa(P2)) / 2.
    """
    orb = (DEEPTAMSA.get(planet1, 8.0) + DEEPTAMSA.get(planet2, 8.0)) / 2.0
    return angular_dist <= orb, orb

def check_ithasala_ishrafa_yoga(
    p1: str, lon1: float,
    p2: str, lon2: float
) -> Dict[str, Any]:
    """
    Detects Ithasala (Muthasila) or Ishrafa (Musaripha) Yoga between two planets:
    - P1 and P2 must be in aspect (0°, 60°, 90°, 120°, 180°).
    - Faster planet must be behind slower planet for Ithasala (applying aspect).
    - If faster planet has moved ahead, it forms Ishrafa (separating aspect).
    """
    # Identify faster and slower planet
    s1 = PLANET_DAILY_SPEEDS.get(p1, 0.5)
    s2 = PLANET_DAILY_SPEEDS.get(p2, 0.5)
    faster, slower = (p1, p2) if s1 >= s2 else (p2, p1)
    f_lon, s_lon = (lon1, lon2) if s1 >= s2 else (lon2, lon1)
    
    # Calculate minimal angular separation
    sep = abs(norm360(f_lon - s_lon))
    if sep > 180.0:
        sep = 360.0 - sep
        
    in_orb, max_orb = is_within_tajika_orb(faster, slower, sep)
    
    # Check if aspect is applying (faster planet behind slower in sign degrees)
    f_deg = f_lon % 30.0
    s_deg = s_lon % 30.0
    is_applying = f_deg < s_deg
    
    if in_orb:
        if is_applying:
            yoga = "Ithasala (Muthasila)"
            desc = f"{faster} (faster) is applying to {slower} within orb {sep:.2f}° (max {max_orb:.1f}°). Promises fulfillment."
        else:
            yoga = "Ishrafa (Musaripha)"
            desc = f"{faster} (faster) is separating from {slower} within orb {sep:.2f}°. Indicates missed opportunity."
    else:
        yoga = "No Aspect"
        desc = "Separation exceeds mutual Tajika orb."
        
    return {
        "yoga": yoga,
        "faster_planet": faster,
        "slower_planet": slower,
        "separation_deg": sep,
        "max_orb_deg": max_orb,
        "is_applying": is_applying,
        "description": desc
    }

def check_tajika_aspect(lon1: float, lon2: float) -> Tuple[bool, float, str]:
    """
    Checks if two planetary longitudes form a classical Tajika aspect:
    - Conjunction (0°): Neutral/Union
    - Sextile (60°): Friendly (Mitra)
    - Square (90°): Hostile (Shatru)
    - Trine (120°): Very Friendly (Pratyaksha Mitra)
    - Opposition (180°): Very Hostile (Pratyaksha Shatru)
    Source: TN (VAR ch. III art. 13).
    """
    sep = abs(norm360(lon1 - lon2))
    if sep > 180.0:
        sep = 360.0 - sep

    for angle, (nature, sa_name) in TAJIKA_ASPECTS.items():
        if abs(sep - angle) <= 12.0:
            return True, sep, f"{nature} ({sa_name})"
    return False, sep, "No Aspect"

def detect_16_tajika_yogas(
    planet_longitudes: Dict[str, float],
    lagna_lon: float,
    p1: str,
    p2: str,
    is_retrograde: Optional[Dict[str, bool]] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates all classical 16 Tajika Yogas between two primary query significators (e.g., Lagnesha & Karyesha).
    Source: TN (VAR ch. VII arts. 57-63).
    
    The 16 Classical Tajika Yogas (Tajika Neelakanthi):
    1. Ithasala (Muthasila) - Applying aspect within orb
    2. Ishrafa (Musaripha) - Separating aspect within orb
    3. Nakta - Faster intermediary planet transfers light from P1 to P2
    4. Yamaya - Slower intermediary planet collects light from P1 and P2
    5. Manahoo - Malefic planet intervenes and spoils the Ithasala
    6. Kamboola - Moon joins Ithasala between P1 and P2
    7. Gairi-Kamboola - Exalted/swakshetra Moon joins Kamboola
    8. Khallasara - Complete lack of aspect and kendra occupation (isolation)
    9. Radda - Ithasala cancelled by retrograde, combustion, or debilitation
    10. Duhphali-Kuttha - Unequal dignity (one dignified, one debilitated)
    11. Dutthotta - Both significators weakened in dusthanas (6/8/12)
    12. Tambira - Faster planet at the very end of sign (29°+) about to ingress
    13. Kuttha - Powerful planet in kendra/trikona aspects succedent house
    14. Durphali - Friendly aspect marred by retrograde departure
    15. Manau - Intervening planet cuts off aspect rays
    16. Induvara - Moon and Lagna lord devoid of aspect and afflicted
    """
    if p1 not in planet_longitudes or p2 not in planet_longitudes:
        return []

    lon1 = planet_longitudes[p1]
    lon2 = planet_longitudes[p2]
    lagna_sign = int(norm360(lagna_lon) // 30.0)
    retro = is_retrograde or {}
    sun_lon = planet_longitudes.get("Sun", 0.0)
    moon_lon = planet_longitudes.get("Moon", 0.0)

    yogas_found = []
    base_ith = check_ithasala_ishrafa_yoga(p1, lon1, p2, lon2)

    # 1 & 2: Ithasala or Ishrafa
    if base_ith["yoga"] != "No Aspect":
        yogas_found.append({
            "name": base_ith["yoga"],
            "type": "Primary Aspect",
            "is_auspicious": "Ithasala" in base_ith["yoga"],
            "details": base_ith["description"]
        })

    is_ithasala = "Ithasala" in base_ith["yoga"]

    # 3. Nakta Yoga (Transfer of Light)
    # If P1 and P2 don't form direct Ithasala, a faster 3rd planet transfers light
    if not is_ithasala:
        for p3, lon3 in planet_longitudes.items():
            if p3 in [p1, p2, "Rahu", "Ketu"]:
                continue
            s3 = PLANET_DAILY_SPEEDS.get(p3, 0.5)
            s1 = PLANET_DAILY_SPEEDS.get(p1, 0.5)
            s2 = PLANET_DAILY_SPEEDS.get(p2, 0.5)
            if s3 > s1 and s3 > s2:
                ith1 = check_ithasala_ishrafa_yoga(p3, lon3, p1, lon1)
                ith2 = check_ithasala_ishrafa_yoga(p3, lon3, p2, lon2)
                if "Ithasala" in ith1["yoga"] and "Ithasala" in ith2["yoga"]:
                    yogas_found.append({
                        "name": "Nakta Yoga (Transfer of Light)",
                        "type": "Mediated Fulfillment",
                        "is_auspicious": True,
                        "intermediary": p3,
                        "details": f"{p3} (faster) transfers light between {p1} and {p2}, guaranteeing success through a mediator."
                    })
                    break

    # 4. Yamaya Yoga (Collection of Light)
    # Slower 3rd planet receives aspects from both P1 and P2
    if not is_ithasala:
        for p3, lon3 in planet_longitudes.items():
            if p3 in [p1, p2, "Rahu", "Ketu"]:
                continue
            s3 = PLANET_DAILY_SPEEDS.get(p3, 0.5)
            s1 = PLANET_DAILY_SPEEDS.get(p1, 0.5)
            s2 = PLANET_DAILY_SPEEDS.get(p2, 0.5)
            if s3 < s1 and s3 < s2:
                ith1 = check_ithasala_ishrafa_yoga(p1, lon1, p3, lon3)
                ith2 = check_ithasala_ishrafa_yoga(p2, lon2, p3, lon3)
                if "Ithasala" in ith1["yoga"] and "Ithasala" in ith2["yoga"]:
                    yogas_found.append({
                        "name": "Yamaya Yoga (Collection of Light)",
                        "type": "Mediated Fulfillment",
                        "is_auspicious": True,
                        "collector": p3,
                        "details": f"{p3} (slower) collects light from both {p1} and {p2}, realizing the objective through a common patron."
                    })
                    break

    # 5. Manahoo Yoga (Malefic Intervention)
    if is_ithasala:
        faster_p = base_ith["faster_planet"]
        slower_p = base_ith["slower_planet"]
        f_deg = (lon1 if faster_p == p1 else lon2) % 30.0
        s_deg = (lon2 if faster_p == p1 else lon1) % 30.0
        for malefic in ["Mars", "Saturn"]:
            if malefic in [p1, p2] or malefic not in planet_longitudes:
                continue
            m_lon = planet_longitudes[malefic]
            m_deg = m_lon % 30.0
            if f_deg < m_deg < s_deg:
                yogas_found.append({
                    "name": "Manahoo Yoga (Malefic Obstruction)",
                    "type": "Affliction",
                    "is_auspicious": False,
                    "malefic": malefic,
                    "details": f"{malefic} intervenes between {faster_p} and {slower_p}, destroying the anticipated outcome."
                })
                break

    # 6 & 7. Kamboola & Gairi-Kamboola Yogas
    if is_ithasala and "Moon" not in [p1, p2] and "Moon" in planet_longitudes:
        moon_ith1 = check_ithasala_ishrafa_yoga("Moon", moon_lon, p1, lon1)
        moon_ith2 = check_ithasala_ishrafa_yoga("Moon", moon_lon, p2, lon2)
        if "Ithasala" in moon_ith1["yoga"] or "Ithasala" in moon_ith2["yoga"]:
            moon_sign = int(norm360(moon_lon) // 30.0)
            is_gairi = (moon_sign == 1) or (moon_sign == 3)  # Taurus (exalted) or Cancer (own)
            yoga_name = "Gairi-Kamboola Yoga" if is_gairi else "Kamboola Yoga"
            yogas_found.append({
                "name": yoga_name,
                "type": "Reinforced Fulfillment",
                "is_auspicious": True,
                "details": f"Moon joins the Ithasala between {p1} and {p2} ({'exalted/own sign' if is_gairi else 'standard'}), ensuring crowning success."
            })

    # 8. Khallasara Yoga (Isolation)
    aspects_count = 0
    for other_p, o_lon in planet_longitudes.items():
        if other_p != p1:
            has_asp, sep, _ = check_tajika_aspect(lon1, o_lon)
            in_orb, _ = is_within_tajika_orb(p1, other_p, sep)
            if has_asp and in_orb:
                aspects_count += 1
    if aspects_count == 0:
        yogas_found.append({
            "name": "Khallasara Yoga (Significator Isolation)",
            "type": "Impotence / Isolation",
            "is_auspicious": False,
            "details": f"{p1} has no Tajika aspects with any celestial body within orb, leaving the matter unsupported."
        })

    # 9. Radda Yoga (Spoiled Ithasala)
    if is_ithasala:
        is_p1_retro = retro.get(p1, False)
        is_p2_retro = retro.get(p2, False)
        p1_combust = (p1 != "Sun") and (abs(norm360(lon1 - sun_lon)) <= 8.0 or abs(norm360(lon1 - sun_lon)) >= 352.0)
        p2_combust = (p2 != "Sun") and (abs(norm360(lon2 - sun_lon)) <= 8.0 or abs(norm360(lon2 - sun_lon)) >= 352.0)
        if is_p1_retro or is_p2_retro or p1_combust or p2_combust:
            yogas_found.append({
                "name": "Radda Yoga (Frustration / Nullification)",
                "type": "Affliction",
                "is_auspicious": False,
                "details": f"Ithasala between {p1} and {p2} is spoiled by retrograde motion or combustion."
            })

    # 10. Duhphali-Kuttha Yoga (Unequal Dignity)
    if is_ithasala:
        h1 = ((int(lon1 // 30.0) - lagna_sign) % 12) + 1
        h2 = ((int(lon2 // 30.0) - lagna_sign) % 12) + 1
        one_dusthana = (h1 in [6, 8, 12]) != (h2 in [6, 8, 12])
        if one_dusthana:
            yogas_found.append({
                "name": "Duhphali-Kuttha Yoga (Unequal Dignity)",
                "type": "Imbalance",
                "is_auspicious": False,
                "details": f"One significator is in a supportive bhava while the other is trapped in a Dusthana ({h1} vs {h2})."
            })

    # 11. Dutthotta Yoga (Mutual Dusthana Affliction)
    if is_ithasala:
        h1 = ((int(lon1 // 30.0) - lagna_sign) % 12) + 1
        h2 = ((int(lon2 // 30.0) - lagna_sign) % 12) + 1
        if h1 in [6, 8, 12] and h2 in [6, 8, 12]:
            yogas_found.append({
                "name": "Dutthotta Yoga (Mutual Weakness)",
                "type": "Failure",
                "is_auspicious": False,
                "details": f"Both {p1} and {p2} are debilitated in Dusthana bhavas ({h1} and {h2}), causing failure."
            })

    # 12. Tambira Yoga (Sign Ingress Transition)
    if is_ithasala:
        f_deg = (lon1 if base_ith["faster_planet"] == p1 else lon2) % 30.0
        if f_deg >= 29.0:
            yogas_found.append({
                "name": "Tambira Yoga (Sign Ingress Horizon)",
                "type": "Uncertainty",
                "is_auspicious": False,
                "details": f"Faster graha {base_ith['faster_planet']} is at {f_deg:.2f}° (about to cross sign boundary before aspect completes)."
            })

    # 13. Kuttha Yoga (Kendra Benefactor Aspect)
    h1 = ((int(lon1 // 30.0) - lagna_sign) % 12) + 1
    h2 = ((int(lon2 // 30.0) - lagna_sign) % 12) + 1
    if (h1 in [1, 4, 7, 10, 5, 9]) and (h2 in [2, 5, 8, 11]):
        has_asp, _, _ = check_tajika_aspect(lon1, lon2)
        if has_asp:
            yogas_found.append({
                "name": "Kuttha Yoga (Kendra Benefactor)",
                "type": "Auspicious Support",
                "is_auspicious": True,
                "details": f"{p1} in powerful Kendra/Trikona ({h1}) aspects and uplifts {p2} in Panaphara ({h2})."
            })

    # 14. Durphali Yoga (Retrograde Departure)
    if not is_ithasala and (retro.get(p1, False) or retro.get(p2, False)):
        has_asp, _, _ = check_tajika_aspect(lon1, lon2)
        if has_asp:
            yogas_found.append({
                "name": "Durphali Yoga (Retrograde Parting)",
                "type": "Separation",
                "is_auspicious": False,
                "details": f"Grahas have mutual Tajika aspect, but retrograde motion moves them away from union."
            })

    # 15. Manau Yoga (Aspect Ray Cutoff)
    for third_p, t_lon in planet_longitudes.items():
        if third_p in [p1, p2, "Rahu", "Ketu"]:
            continue
        has_asp1, sep1, _ = check_tajika_aspect(lon1, t_lon)
        has_asp2, sep2, _ = check_tajika_aspect(lon2, t_lon)
        if has_asp1 and has_asp2 and (sep1 < 5.0 or sep2 < 5.0):
            yogas_found.append({
                "name": "Manau Yoga (Ray Interception)",
                "type": "Intervention",
                "is_auspicious": False,
                "interceptor": third_p,
                "details": f"{third_p} closely intercepts the aspectual rays between {p1} and {p2}."
            })
            break

    # 16. Induvara Yoga (Afflicted Moon & Lagnesha)
    if "Moon" in planet_longitudes:
        m_house = ((int(moon_lon // 30.0) - lagna_sign) % 12) + 1
        l_house = ((int(lon1 // 30.0) - lagna_sign) % 12) + 1
        if m_house in [6, 8, 12] and l_house in [6, 8, 12]:
            yogas_found.append({
                "name": "Induvara Yoga (Afflicted Mind & Body)",
                "type": "Severe Affliction",
                "is_auspicious": False,
                "details": f"Both Moon ({m_house}th bhava) and Lagna Lord {p1} ({l_house}th bhava) are trapped in dusthanas."
            })

    return yogas_found

def evaluate_all_tajika_yogas(
    planet_longitudes: Dict[str, float],
    lagna_lon: float,
    is_retrograde: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    """
    Evaluates all active 16 Tajika Yogas across key query significators:
    Lagna Lord, 10th Lord (Karya), Moon, Jupiter, Venus.
    Source: TN (VAR ch. VII).
    """
    lagna_sign = int(norm360(lagna_lon) // 30.0)
    lagnesha = SIGN_LORDS[lagna_sign]
    karyesha_10 = SIGN_LORDS[(lagna_sign + 9) % 12]

    results = {
        "lagnesha": lagnesha,
        "karyesha_10th": karyesha_10,
        "primary_pair_yogas": detect_16_tajika_yogas(planet_longitudes, lagna_lon, lagnesha, karyesha_10, is_retrograde),
        "all_combinations": []
    }

    pairs_checked = set()
    planets = [p for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"] if p in planet_longitudes]
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            pa, pb = planets[i], planets[j]
            yogas = detect_16_tajika_yogas(planet_longitudes, lagna_lon, pa, pb, is_retrograde)
            if yogas:
                results["all_combinations"].append({
                    "planet_a": pa,
                    "planet_b": pb,
                    "yogas": yogas
                })

    return results

# ---------------------------------------------------------------------------
# 50+ Sahams (Sensitive Points) Engine (TN; VAR ch. VII art. 64 on)
# ---------------------------------------------------------------------------

def compute_sahams(
    planet_longitudes: Dict[str, float],
    ascendant_lon: float,
    is_day_birth: bool
) -> Dict[str, float]:
    """
    Computes Classical Tajika Sahams.
    Delegates to the saham library in sahams_library.py.
    """
    from .sahams_library import compute_all_50_sahams
    return compute_all_50_sahams(planet_longitudes, ascendant_lon, is_night=not is_day_birth)


# ---------------------------------------------------------------------------
# Varsheshwara (Lord of the Year) Selection (TN; VAR ch. IV arts. 42-47)
# ---------------------------------------------------------------------------

def evaluate_varsheshwara_candidates(
    natal_asc_sign: int,
    varsha_asc_sign: int,
    muntha_sign: int,
    is_day_return: bool,
    sun_sign: int,
    moon_sign: int
) -> List[Dict[str, Any]]:
    """
    Evaluates the 5 Candidate Office Bearers for Lord of the Year (Varsheshwara):
    1. Muntha Pati (Lord of Muntha sign)
    2. Janma Lagna Pati (Lord of natal Ascendant)
    3. Varsha Lagna Pati (Lord of annual Ascendant)
    4. Tri-Rasi Pati (Trirasi ruler of annual Ascendant)
    5. Dina/Ratri Pati (Sun if day return, Moon if night return)
    """
    candidates = [
        {"role": "Muntha Pati", "lord": SIGN_LORDS[muntha_sign]},
        {"role": "Janma Lagna Pati", "lord": SIGN_LORDS[natal_asc_sign]},
        {"role": "Varsha Lagna Pati", "lord": SIGN_LORDS[varsha_asc_sign]},
        {"role": "Tri-Rasi Pati", "lord": SIGN_LORDS[(varsha_asc_sign + 4) % 12]}, # Triplicity ruler
        {"role": "Dina/Ratri Pati", "lord": "Sun" if is_day_return else "Moon"}
    ]
    return candidates


# ===========================================================================
# The Tajaka balas (VAR ch. III arts. 31-40)
# ===========================================================================
# Tajaka friendship of Sun .. Saturn (rows) with the lords Sun .. Saturn: 2 itself, 1 friend, 0 other
# (the Tajika friendship of TN, VAR ch. III art. 12)
TAJAKA_FRIENDS = ((2, 1, 1, 0, 1, 0, 0), (1, 2, 1, 0, 1, 0, 0), (1, 1, 2, 0, 1, 0, 0), (0, 0, 0, 2, 0, 1, 1),
                        (1, 1, 1, 0, 2, 0, 0), (0, 0, 0, 1, 0, 2, 1), (0, 0, 0, 1, 0, 1, 2))
# Hadda (Tajaka terms, VAR ch. III arts. 36-37; varga slot 27): ends of the first four terms and the five lords per sign
HADDA_ENDS = ((6, 12, 20, 25), (8, 14, 22, 27), (6, 12, 17, 24), (7, 13, 19, 26), (6, 11, 18, 24),
                    (7, 17, 21, 28), (6, 14, 21, 28), (7, 11, 19, 24), (12, 17, 21, 26), (7, 14, 22, 26),
                    (7, 13, 20, 25), (12, 16, 19, 28))
HADDA_LORDS = ((5, 6, 4, 3, 7), (6, 4, 5, 7, 3), (4, 6, 5, 3, 7), (3, 6, 4, 5, 7), (5, 6, 7, 4, 3),
                     (4, 6, 5, 3, 7), (7, 4, 5, 6, 3), (3, 6, 4, 5, 7), (5, 6, 4, 3, 7), (4, 5, 6, 7, 3),
                     (4, 6, 5, 3, 7), (6, 5, 4, 3, 7))
HARSHA_CLASS = ("Nil", "Little", "Average", "Full", "Excess")
PANCHA_CLASS = ("Weak", "Ordinary", "Powerful", "Very Strong", "Extraordinary")
_HOUSE_LORDS = (3, 6, 4, 2, 1, 4, 6, 3, 5, 7, 7, 5)
_EXALT = (0, 1, 9, 5, 3, 11, 6)
_DEBIL = (6, 7, 3, 11, 9, 5, 0)
_HARSHA_HOUSE = (8, 2, 5, 0, 10, 4, 11)        # 9th, 3rd, 6th, 1st, 11th, 5th, 12th from the lagna


def hadda_lord(lon: float) -> int:
    """Lord (1 Sun .. 7 Saturn) of the Tajaka term (hadda) a longitude falls in."""
    sign = int(norm360(lon) // 30.0)
    deg = norm360(lon) - sign * 30.0
    k = sum(1 for end in HADDA_ENDS[sign] if deg >= end)
    return HADDA_LORDS[sign][k]


def tajaka_balas(varga_signs: List[List[int]], lons: List[float], uchcha: List[float],
                       is_day: bool) -> Dict[str, Dict[str, Any]]:
    """Harsha, Pancha-vargeeya (VAR ch. III arts. 32-40) and Dwadasa-vargeeya (art. 31) balas of Sun ..
    Saturn (TN).  ``varga_signs[v][p]``: signs of points 0 Lagna .. 9 Ketu in the varga order (D1, D9, D2, D3, D4,
    D5, D6, D7, D8, D10, D11, D12, ...; ``dasa_systems.JChart.signs``); ``lons``: rasi longitudes of points
    0 .. 9; ``uchcha``: uchcha bala (virupas) of Sun .. Saturn; ``is_day``: born between sunrise and sunset."""
    names = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    d1 = varga_signs[0]
    out = {}
    for i, name in enumerate(names):
        p = i + 1
        sign, house = d1[p], (d1[p] - d1[0]) % 12
        # Harsha: 5 each for the joy house, own / exaltation sign, gender quarter (houses 4-6 and 10-12 for the
        # Sun, Mars, Jupiter; 1-3 and 7-9 for the others) and day (male) / night (female) birth
        h = 5 * (house == _HARSHA_HOUSE[i])
        h += 5 * (_HOUSE_LORDS[sign] == p or sign == _EXALT[i])
        male = p in (1, 3, 5)
        h += 5 * (((house // 3) % 2 == 1) == male)
        h += 5 * (is_day == male)
        rel = lambda lord: TAJAKA_FRIENDS[i][lord - 1]
        pv = (uchcha[i] / 3.0 + (7.5, 15.0, 30.0)[rel(_HOUSE_LORDS[sign])]
              + (3.75, 7.5, 15.0)[rel(hadda_lord(lons[p]))]
              + (2.5, 5.0, 10.0)[rel(_HOUSE_LORDS[varga_signs[3][p]])]
              + (1.25, 2.5, 5.0)[rel(_HOUSE_LORDS[varga_signs[1][p]])]) * 0.25
        dw = 0
        for v in range(12):
            s = varga_signs[v][p]
            dw += 1 if s == _EXALT[i] else 0 if s == _DEBIL[i] else int(rel(_HOUSE_LORDS[s]) != 0)
        out[name] = {"harsha": h, "harsha_class": HARSHA_CLASS[h // 5], "pancha_vargeeya": pv,
                     "pancha_class": PANCHA_CLASS[sum(pv >= t for t in (5.0, 10.0, 15.0, 20.0))],
                     "dwadasa_vargeeya": dw}
    return out


# ---------------------------------------------------------------------------
# Tajaka chart periods and Muntha (TN; PVR ch. 27: annual, monthly and the finer charts, each 1/12 of the one above)
# ---------------------------------------------------------------------------

TAJAKA_LEVELS = ("annual", "monthly", "2.5 day", "5 hr", "25 min", "2 min")
TAJAKA_LEVEL_YEARS = (1.0, 0.08333333333333333, 0.006944444444444444, 0.0005787037037037037,
                      4.8225308641975306e-05, 4.018775720164609e-06)       # 1, 1/12, 1/144 .. of a year


def tajaka_year_definition(tropical: bool = False, true_year: bool = True) -> int:
    """Dasa year definition the Tajaka chart moments use (Settings > Tajaka; default 3 = true sidereal solar year):
    6 mean sidereal, 7 true tropical, 0 mean tropical."""
    return (7 if true_year else 0) if tropical else (3 if true_year else 6)


def tajaka_period(years: int, months: int = 0, d25: int = 0, h5: int = 0, m25: int = 0,
                  m2: int = 0) -> Tuple[str, float, float, List[int]]:
    """The Tajaka chart: (level name, start and end in years since birth, counts per level).
    ``years`` = chart year - birth year, ``months`` = chart month - birth month (both as the reference takes them: a
    negative month borrows a year), the finer levels 1-based (0 = not used; each needs the one above).  Each level
    is 1/12 of the one above."""
    start, counts, name = float(years), [years], TAJAKA_LEVELS[0]
    for lvl, n in enumerate((months, d25, h5, m25, m2), 1):
        if not n:
            break
        k = n if lvl == 1 else n - 1
        start += k * TAJAKA_LEVEL_YEARS[lvl]
        counts.append(k)
        name = TAJAKA_LEVELS[lvl]
    if len(counts) > 1 and counts[1] < 0:
        counts[0] -= 1
        counts[1] += 12
    return name, start, start + TAJAKA_LEVEL_YEARS[len(counts) - 1], counts


def muntha_position(ref_lon: float, ref_signs: List[int], counts: List[int], start_years: float = 0.0,
                 method: int = 1, signs_of=None) -> Tuple[float, List[int]]:
    """Muntha (TN; Settings > Tajaka > Muntha, default 1) from a reference point (the
    lagna by default): its longitude and its sign in each of the chart's 29 varga slots (``ref_signs``).
      0  the point progressed by ``start_years`` x 30 deg; every slot gets the rasi sign
      1  the point moved one sign per count of every level (``tajaka_period`` counts)
      2  per level: from the sign reached, the lord's sign in that slot (``signs_of(planet)`` -> its 29 slot
         signs), plus that level's count."""
    if method == 0:
        lon = start_years * 30.0 + ref_lon
        return lon % 360.0, [int(lon * 0.03333333333333333) % 12] * len(ref_signs)
    if method == 1:
        total = sum(counts)
        return (total * 30.0 + ref_lon) % 360.0, [(s + total) % 12 for s in ref_signs]
    out = []
    for v, s in enumerate(ref_signs):
        s = (s + counts[0]) % 12
        for c in counts[1:]:
            s = (signs_of(RASI_LORD_INDEX[s])[v] + c) % 12
        out.append(s)
    return ((out[0] - ref_signs[0]) * 30.0 + ref_lon) % 360.0, out


RASI_LORD_INDEX = [3, 6, 4, 2, 1, 4, 6, 3, 5, 7, 7, 5]       # sign lords (BPHS 4.6-24), point indices
