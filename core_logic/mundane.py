"""
core_logic/mundane.py
=====================
Modularized Calculation Engine for Mundane Astrology, Ingress Charts, and Planetary Transit Events.
Sources (docs/SOURCES.md section 17): the Sun's entry into a sign (sankranti) and the solar month SS 14.3; the
lunar month and its first tithi SS 14.12-14; the year of each graha and its effects BS 19, the year's king and
minister by the weekdays of Chaitra Shukla Pratipat and Mesha Sankranti as the almanacs reckon them (no verse
checked); the "Meteorological year" chart, the Sun's entry into Ardra (66 deg 40'), almanac practice (no verse
checked); stations and conjunctions are astronomy.  The charts of the Modes menu ("Retro change",
"Meteorological Yr", "Solar Month") are found by the event searches of ``time_search`` (0.0035-day steps); the
solvers below are generic root finders.
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional, Any, Callable

from .natal_chart import norm360, RASI_NAMES_EN, RASI_NAMES_SA

# Standard planetary motion mean speeds (degrees / day)
MEAN_DAILY_SPEEDS: Dict[str, float] = {
    "Sun": 0.9856,
    "Moon": 13.1764,
    "Mars": 0.5240,
    "Mercury": 1.3833,
    "Jupiter": 0.0831,
    "Venus": 1.2000,
    "Saturn": 0.0335,
    "Rahu": -0.0529,
    "Ketu": -0.0529,
}

WEEKDAY_LORDS = [
    "Sun",      # 0: Ravivara (Sunday)
    "Moon",     # 1: Somavara (Monday)
    "Mars",     # 2: Mangalavara (Tuesday)
    "Mercury",  # 3: Budhavara (Wednesday)
    "Jupiter",  # 4: Guruvara (Thursday)
    "Venus",    # 5: Sukravara (Friday)
    "Saturn"    # 6: Shanivara (Saturday)
]

# ===========================================================================
# 1. Ingress Target Calculation & Root Finding Helpers
# ===========================================================================

def solve_longitude_crossing(
    calc_func: Callable[[float], float],
    target_lon: float,
    jd_approx: float,
    step_days: float = 1.0,
    max_days: float = 40.0,
    tolerance_deg: float = 0.0001
) -> Optional[float]:
    """
    Finds the exact Julian Day when calc_func(jd) reaches target_lon (0..360°).
    Uses a robust 2-phase approach: coarse step bracket followed by bisection/secant refinement.
    """
    target = norm360(target_lon)
    
    # 1. Find bracket [t1, t2] where target is crossed
    t_curr = jd_approx - step_days
    t_end = jd_approx + max_days
    
    prev_t = t_curr
    prev_val = norm360(calc_func(t_curr))
    
    bracket: Optional[Tuple[float, float]] = None
    
    while t_curr <= t_end:
        t_curr += step_days
        curr_val = norm360(calc_func(t_curr))
        
        # Check if target is crossed during this step, in either direction (retrograde
        # motion gives a negative step; taking it mod 360 would look like a near-full circle).
        step = (curr_val - prev_val + 180.0) % 360.0 - 180.0
        if step >= 0.0:
            crossed = (target - prev_val) % 360.0 <= step
        else:
            crossed = (prev_val - target) % 360.0 <= -step

        if crossed:
            bracket = (prev_t, t_curr)
            break
            
        prev_t = t_curr
        prev_val = curr_val
        
    if not bracket:
        return None
        
    # 2. Bisection refinement
    low, high = bracket
    for _ in range(60):
        mid = (low + high) / 2.0
        mid_val = norm360(calc_func(mid))
        err = (mid_val - target + 180.0) % 360.0 - 180.0
        
        if abs(err) < tolerance_deg:
            return mid
            
        low_val = norm360(calc_func(low))
        err_low = (low_val - target + 180.0) % 360.0 - 180.0
        
        if (err_low * err) <= 0:
            high = mid
        else:
            low = mid
            
    return (low + high) / 2.0


# ===========================================================================
# 2. Solar New Year (Mesha Sankranti)
# Finds the exact moment the Sun reaches 0°00'00" (Aries ingress).
# ===========================================================================

def compute_solar_new_year(
    sun_lon_func: Callable[[float], float],
    approx_jd: float
) -> Dict[str, Any]:
    """
    Computes exact Julian Day and moment of Solar New Year (Mesha Sankranti / Sun entering Aries 0°).
    """
    exact_jd = solve_longitude_crossing(
        calc_func=sun_lon_func,
        target_lon=0.0,
        jd_approx=approx_jd,
        step_days=1.0,
        max_days=35.0
    )
    
    return {
        "event_type": "Solar New Year (Mesha Sankranti)",
        "ingress_sign": "Aries",
        "ingress_sign_sa": "Mesha",
        "ingress_degree": 0.0,
        "exact_jd": exact_jd,
    }


# ===========================================================================
# 3. Lunar New Year (Chaitra Shukla Pratipat)
# Finds the exact moment when Sun and Moon conjoin in Pisces (angular diff = 0°)
# preceding the Solar New Year.
# ===========================================================================

def compute_lunar_new_year(
    sun_lon_func: Callable[[float], float],
    moon_lon_func: Callable[[float], float],
    approx_jd: float
) -> Dict[str, Any]:
    """
    Computes exact Julian Day and moment of Lunar New Year (Chaitra Shukla Pratipat).
    This occurs at the exact Amavasya conjunction (Moon - Sun = 0°) in Pisces (Meena)
    before or around Mesha Sankranti.
    """
    def sun_moon_diff(jd: float) -> float:
        s = norm360(sun_lon_func(jd))
        m = norm360(moon_lon_func(jd))
        return norm360(m - s)
        
    exact_jd = solve_longitude_crossing(
        calc_func=sun_moon_diff,
        target_lon=0.0,
        jd_approx=approx_jd,
        step_days=1.0,
        max_days=32.0
    )
    
    return {
        "event_type": "Lunar New Year (Chaitra Shukla Pratipat)",
        "sun_moon_angle": 0.0,
        "tithi": "Shukla Pratipat (Tithi 1)",
        "exact_jd": exact_jd,
    }


# ===========================================================================
# 4. Solar Month Ingress (12 Sankrantis)
# Finds the exact moment the Sun enters each of the 12 signs (the "Solar Month" chart; SS 14.3).
# ===========================================================================

def compute_solar_month_ingress(
    sun_lon_func: Callable[[float], float],
    sign_index: int,
    approx_jd: float
) -> Dict[str, Any]:
    """
    Computes exact Julian Day of Sun ingress into the specified zodiac sign (0..11).
    sign_index 0 = Mesha (Aries), 1 = Vrishabha (Taurus), etc.
    """
    target_lon = (sign_index % 12) * 30.0
    exact_jd = solve_longitude_crossing(
        calc_func=sun_lon_func,
        target_lon=target_lon,
        jd_approx=approx_jd,
        step_days=1.0,
        max_days=35.0
    )
    
    return {
        "event_type": "Solar Month Ingress (Sankranti)",
        "sign_index": sign_index % 12,
        "sign_name_en": RASI_NAMES_EN[sign_index % 12],
        "sign_name_sa": RASI_NAMES_SA[sign_index % 12],
        "target_longitude": target_lon,
        "exact_jd": exact_jd
    }


# ===========================================================================
# 5. Fortnight (Paksha) Ingress Charts
# - Shukla Paksha Pratipat: Moon - Sun = 0°
# - Krishna Paksha Pratipat: Moon - Sun = 180°
# ===========================================================================

def compute_fortnight_ingress(
    sun_lon_func: Callable[[float], float],
    moon_lon_func: Callable[[float], float],
    paksha_type: str,
    approx_jd: float
) -> Dict[str, Any]:
    """
    Computes exact Julian Day of Fortnight (Paksha) ingress:
    - 'shukla': Sun-Moon conjunction (0°)
    - 'krishna': Sun-Moon opposition (180°)
    """
    target = 0.0 if paksha_type.lower() == "shukla" else 180.0
    
    def diff(jd: float) -> float:
        return norm360(moon_lon_func(jd) - sun_lon_func(jd))
        
    exact_jd = solve_longitude_crossing(
        calc_func=diff,
        target_lon=target,
        jd_approx=approx_jd,
        step_days=1.0,
        max_days=20.0
    )
    
    return {
        "event_type": f"Fortnight Ingress ({paksha_type.capitalize()} Paksha)",
        "paksha": paksha_type.capitalize(),
        "target_phase_angle": target,
        "exact_jd": exact_jd
    }


# ===========================================================================
# 6. Planetary Conjunctions & Oppositions Search Engine
# (Astronomy: the moment two longitudes are a given angle apart.)
# ===========================================================================

def find_planetary_aspect_event(
    p1_lon_func: Callable[[float], float],
    p2_lon_func: Callable[[float], float],
    p1_name: str,
    p2_name: str,
    event_type: str,  # 'conjunction' (0°) or 'opposition' (180°)
    start_jd: float,
    search_window_days: float = 365.0
) -> Optional[Dict[str, Any]]:
    """
    Finds the next exact conjunction (0°) or opposition (180°) between two planets.
    Includes check preventing Rahu-Ketu conjunction.
    """
    if p1_name in ("Rahu", "Ketu") and p2_name in ("Rahu", "Ketu"):
        if event_type.lower() == "conjunction":
            return {
                "error": "Rahu and Ketu never conjoin (always 180° opposite)",
                "p1": p1_name,
                "p2": p2_name
            }
            
    target = 0.0 if event_type.lower() == "conjunction" else 180.0
    
    def rel_pos(jd: float) -> float:
        return norm360(p1_lon_func(jd) - p2_lon_func(jd))
        
    exact_jd = solve_longitude_crossing(
        calc_func=rel_pos,
        target_lon=target,
        jd_approx=start_jd,
        step_days=2.0,
        max_days=search_window_days
    )
    
    if not exact_jd:
        return None
        
    lon1 = norm360(p1_lon_func(exact_jd))
    lon2 = norm360(p2_lon_func(exact_jd))
    sign1 = int(lon1 // 30.0)
    
    return {
        "event_type": event_type.capitalize(),
        "planet_1": p1_name,
        "planet_2": p2_name,
        "target_angle": target,
        "exact_jd": exact_jd,
        "planet_1_lon": lon1,
        "planet_2_lon": lon2,
        "sign_index": sign1,
        "sign_name": RASI_NAMES_EN[sign1]
    }


# ===========================================================================
# 7. Planetary Stations (Zero Velocity / Stationary Transit) & Retrogrades
# The "Retro change" chart (the previous / next station of a planet); the app warns, as its reference did:
# "Stationary transit of nodes can occur only if true nodes are used.
#  Rahu and Ketu are always retrograde with mean nodes."
# ===========================================================================

def find_planetary_station_event(
    planet: str,
    speed_func: Callable[[float], float],
    start_jd: float,
    search_window_days: float = 120.0,
    is_true_node: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Finds the next station (velocity = 0.0 deg/day) where planet changes motion:
    - Direct to Retrograde (D -> R)
    - Retrograde to Direct (R -> D)
    """
    if planet in ("Rahu", "Ketu") and not is_true_node:
        return {
            "error": "Stationary transit cannot occur with mean nodes (always retrograde)",
            "planet": planet
        }
        
    # Search for zero crossing of velocity
    step = 0.5  # half-day steps
    t = start_jd
    t_end = start_jd + search_window_days
    
    prev_speed = speed_func(t)
    bracket: Optional[Tuple[float, float]] = None
    
    while t <= t_end:
        t += step
        curr_speed = speed_func(t)
        if (prev_speed * curr_speed) <= 0.0 and prev_speed != 0.0:
            bracket = (t - step, t)
            break
        prev_speed = curr_speed
        
    if not bracket:
        return None
        
    # Bisection on speed function
    low, high = bracket
    for _ in range(40):
        mid = (low + high) / 2.0
        spd = speed_func(mid)
        if abs(spd) < 0.00001:
            exact_jd = mid
            break
        if (speed_func(low) * spd) <= 0:
            high = mid
        else:
            low = mid
    else:
        exact_jd = (low + high) / 2.0
        
    speed_before = speed_func(exact_jd - 0.5)
    speed_after = speed_func(exact_jd + 0.5)
    
    if speed_before > 0 and speed_after < 0:
        station_type = "Stationary (Turning Retrograde)"
        direction_transition = "Direct -> Retrograde"
    else:
        station_type = "Stationary (Turning Direct)"
        direction_transition = "Retrograde -> Direct"
        
    return {
        "planet": planet,
        "station_type": station_type,
        "direction_transition": direction_transition,
        "exact_jd": exact_jd,
        "speed_at_station": round(speed_func(exact_jd), 6)
    }


# ===========================================================================
# 8. Mundane Year Lordship: King (Raja) and Minister (Mantri)
# Classical rules:
# - King (Raja): Lord of the weekday at sunrise of Chaitra Shukla Pratipat
# - Minister (Mantri): Lord of the weekday at sunrise of Mesha Sankranti
# ===========================================================================

def compute_year_lords(chaitra_pratipat_weekday: int, mesha_sankranti_weekday: int) -> Dict[str, str]:
    """
    Computes Raja (King) and Mantri (Minister) of the astrological year:
    chaitra_pratipat_weekday: 0=Sunday, 1=Monday, ..., 6=Saturday
    mesha_sankranti_weekday: 0=Sunday, 1=Monday, ..., 6=Saturday
    """
    raja = WEEKDAY_LORDS[chaitra_pratipat_weekday % 7]
    mantri = WEEKDAY_LORDS[mesha_sankranti_weekday % 7]
    
    return {
        "King (Raja)": raja,
        "Minister (Mantri)": mantri
    }
