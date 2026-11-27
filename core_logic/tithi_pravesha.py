"""
core_logic/tithi_pravesha.py
============================
Modularized Calculation Engine for Tithi Pravesha (Vedic Annual & Monthly Lunar Return Charts): the method of
P. V. R. Narasimha Rao (a modern teaching; docs/SOURCES.md section 14), the
charts found by an event search over time (time_search).

Core Principle of Tithi Pravesha:
1. The Sun returns to the natal sidereal solar month / sign (Mesha, Vrishabha, etc.).
2. The phase angle (angular separation) between Moon and Sun:
   Δθ = (Moon - Sun) % 360°
   must match the natal birth Δθ_natal EXACTLY down to the arcsecond.
3. The weekday and Hora at the moment of Tithi Pravesha determine the Ruler of the Year.

The tithi is SS 2.66's (Moon - Sun in parts of 12 degrees).
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional, Any, Callable

from .natal_chart import norm360, RASI_NAMES_EN
from .mundane import solve_longitude_crossing

TITHI_NAMES = [
    "Shukla Pratipat", "Shukla Dvitiya", "Shukla Tritiya", "Shukla Chaturthi", "Shukla Panchami",
    "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami", "Shukla Navami", "Shukla Dashami",
    "Shukla Ekadashi", "Shukla Dvadashi", "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
    "Krishna Pratipat", "Krishna Dvitiya", "Krishna Tritiya", "Krishna Chaturthi", "Krishna Panchami",
    "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami", "Krishna Navami", "Krishna Dashami",
    "Krishna Ekadashi", "Krishna Dvadashi", "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya"
]

def get_tithi_info(moon_lon: float, sun_lon: float) -> Dict[str, Any]:
    """Computes exact Tithi index (1..30), name, and elapsed percentage."""
    diff = norm360(moon_lon - sun_lon)
    tithi_span = 12.0  # 12° per tithi
    tithi_num = int(diff // tithi_span) + 1
    fraction = (diff % tithi_span) / tithi_span
    
    return {
        "angular_difference": diff,
        "tithi_number": tithi_num,
        "tithi_name": TITHI_NAMES[tithi_num - 1],
        "is_shukla_paksha": (tithi_num <= 15),
        "tithi_fraction": fraction,
        "tithi_percentage": round(fraction * 100.0, 2)
    }

def solve_tithi_pravesha_chart(
    natal_sun_lon: float,
    natal_moon_lon: float,
    sun_lon_func: Callable[[float], float],
    moon_lon_func: Callable[[float], float],
    approx_return_jd: float
) -> Dict[str, Any]:
    """
    Finds the exact moment when Sun is in the natal solar month and the Moon-Sun separation
    matches the natal phase angle.
    """
    natal_diff = norm360(natal_moon_lon - natal_sun_lon)
    natal_tithi_info = get_tithi_info(natal_moon_lon, natal_sun_lon)
    
    def current_diff(jd: float) -> float:
        return norm360(moon_lon_func(jd) - sun_lon_func(jd))
        
    exact_jd = solve_longitude_crossing(
        calc_func=current_diff,
        target_lon=natal_diff,
        jd_approx=approx_return_jd,
        step_days=0.5,
        max_days=35.0,
        tolerance_deg=0.0001
    )
    
    if not exact_jd:
        return {"error": "Could not locate exact Tithi Pravesha return moment"}
        
    sun_at_tp = sun_lon_func(exact_jd)
    moon_at_tp = moon_lon_func(exact_jd)
    
    return {
        "event_type": "Tithi Pravesha (Annual Lunar Return)",
        "exact_jd": exact_jd,
        "target_phase_angle": natal_diff,
        "natal_tithi": natal_tithi_info["tithi_name"],
        "sun_longitude": round(sun_at_tp, 4),
        "moon_longitude": round(moon_at_tp, 4),
        "solar_month": RASI_NAMES_EN[int(norm360(sun_at_tp) // 30.0)]
    }

def solve_yoga_pravesha_chart(
    natal_sun_lon: float,
    natal_moon_lon: float,
    sun_lon_func: Callable[[float], float],
    moon_lon_func: Callable[[float], float],
    approx_return_jd: float
) -> Dict[str, Any]:
    """
    Finds exact moment of Yoga Pravesha (Annual Soli-Lunar Yoga Return):
    Sun + Moon sum returns to natal (Sun + Moon) sum while Sun is in the natal solar month.
    (Settings: "Find Yoga Pravesha Chart"; the yoga of SS 2.65.)
    """
    natal_yoga_angle = norm360(natal_sun_lon + natal_moon_lon)
    
    def current_yoga_sum(jd: float) -> float:
        return norm360(sun_lon_func(jd) + moon_lon_func(jd))
        
    exact_jd = solve_longitude_crossing(
        calc_func=current_yoga_sum,
        target_lon=natal_yoga_angle,
        jd_approx=approx_return_jd,
        step_days=0.5,
        max_days=35.0,
        tolerance_deg=0.0001
    )
    
    if not exact_jd:
        return {"error": "Could not locate exact Yoga Pravesha return moment"}
        
    sun_at_yp = sun_lon_func(exact_jd)
    moon_at_yp = moon_lon_func(exact_jd)
    
    return {
        "event_type": "Yoga Pravesha (Annual Soli-Lunar Yoga Return)",
        "exact_jd": exact_jd,
        "target_yoga_angle": natal_yoga_angle,
        "sun_longitude": round(sun_at_yp, 4),
        "moon_longitude": round(moon_at_yp, 4),
        "solar_month": RASI_NAMES_EN[int(norm360(sun_at_yp) // 30.0)]
    }

def solve_nakshatra_pravesha_chart(
    natal_moon_lon: float,
    sun_lon_func: Callable[[float], float],
    moon_lon_func: Callable[[float], float],
    approx_return_jd: float
) -> Dict[str, Any]:
    """
    Finds exact moment of Nakshatra Pravesha (Annual Sidereal Lunar Return):
    Moon returns to natal sidereal longitude while Sun is in the natal solar month.
    (Settings: "Find Nakshatra Pravesha".)
    """
    exact_jd = solve_longitude_crossing(
        calc_func=moon_lon_func,
        target_lon=natal_moon_lon,
        jd_approx=approx_return_jd,
        step_days=0.5,
        max_days=35.0,
        tolerance_deg=0.0001
    )
    
    if not exact_jd:
        return {"error": "Could not locate exact Nakshatra Pravesha return moment"}
        
    sun_at_np = sun_lon_func(exact_jd)
    moon_at_np = moon_lon_func(exact_jd)
    
    return {
        "event_type": "Nakshatra Pravesha (Annual Sidereal Lunar Return)",
        "exact_jd": exact_jd,
        "target_moon_longitude": natal_moon_lon,
        "sun_longitude": round(sun_at_np, 4),
        "moon_longitude": round(moon_at_np, 4),
        "solar_month": RASI_NAMES_EN[int(norm360(sun_at_np) // 30.0)]
    }

KARANA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

def compute_karana_chaturaseeti_dasa(
    moon_lon: float,
    sun_lon: float,
    birth_year: float = 0.0
) -> Dict[str, Any]:
    """
    Computes Karana Chaturaseeti Sama Dasa (84-year conditional dasa):
    Applicable in Tithi Pravesha and Karana Pravesha charts for timing career & karmic events.
    Seed lord is derived from the Karana active at the return moment.
    """
    diff = norm360(moon_lon - sun_lon)
    karana_idx = int(diff // 6.0) % 60
    karana_lord_idx = karana_idx % 7
    seed_lord = KARANA_LORDS[karana_lord_idx]
    
    timeline = []
    curr_yr = birth_year
    for i in range(7):
        lord = KARANA_LORDS[(karana_lord_idx + i) % 7]
        timeline.append({
            "order": i + 1,
            "lord": lord,
            "start_year": round(curr_yr, 2),
            "end_year": round(curr_yr + 12.0, 2),
            "duration_years": 12.0
        })
        curr_yr += 12.0
        
    return {
        "dasa_system": "Karana Chaturaseeti Sama Dasa (84 Years)",
        "karana_index": karana_idx + 1,
        "seed_lord": seed_lord,
        "total_cycle_years": 84.0,
        "timeline": timeline
    }


def annual_tithi_pravesha(birth, years: int, cfg=None, solar_month: bool = True) -> Tuple[float, float]:
    """The annual Tithi Pravesha chart ("Find Tithi Pravesha Chart" with no month): the
    UT moments (start, end) of the chart ``years`` after birth and of the next one, whose span the dasas fill.
    From birth + (years + 0.2464) x 365.24219 days (90 days on) search back (``time_search.reaches_longitude``)
    for Moon - Sun at its natal value, 0.0035 day before the last one each time, until the Sun is in
    its natal sign (``solar_month``, SolarMonthUsedInTP=1; else until the lunar month is the natal one); if the
    other of the two then differs, the previous recurrence is taken when both match there.  The lunar month is
    the Sun's sign at the new moon before (LunarYrDef=2)."""
    from . import ephemeris as E, time_search as S
    natal = E.planet_positions(birth.jd_ut, cfg)
    target = (natal["Moon"]["lon"] - natal["Sun"]["lon"]) % 360.0
    sun_sign = lambda jd: int(E.planet_positions(jd, cfg)["Sun"]["lon"] // 30.0)  # noqa: E731
    month = lambda jd: sun_sign(S.longitude_event(jd, 2, 0.0, 1, "diff", True, cfg))  # noqa: E731
    sign0, month0 = sun_sign(birth.jd_ut), month(birth.jd_ut)
    first, second = (sun_sign, sign0), (month, month0)
    if not solar_month:
        first, second = second, first

    def find(y: float) -> float:
        start = birth.jd_ut + (y + 0.24641183977130354) * 365.24219
        while True:
            jd = S.longitude_event(start, 2, target, 1, "diff", True, cfg)
            start = jd - 0.0035
            if first[0](jd) == first[1]:
                break
        if second[0](jd) != second[1]:
            prev = S.longitude_event(start, 2, target, 1, "diff", True, cfg)
            if sun_sign(prev) == sign0 and month(prev) == month0:
                jd = prev
        return jd
    return find(years), find(years + 1)


def next_pravesha(birth, jd_from: float, kind: str = "tithi", period: str = "annual", cfg=None) -> float:
    """The Tithi Pravesha form's second route (the kind and period choices): JD UT of the first chart after
    ``jd_from``. ``kind``: "tithi" (Moon - Sun at its natal value), "nakshatra" (the Moon at its natal longitude), "yoga" (Moon +
    Sun at its natal value). ``period``: "annual" (the Sun also in its natal sign), "monthly" (the next recurrence),
    "fortnightly" (the natal value or 180 degrees from it), "daily" (the natal value modulo a tithi)."""
    from . import ephemeris as E, time_search as S
    natal = E.planet_positions(birth.jd_ut, cfg)
    moon, sun = natal["Moon"]["lon"], natal["Sun"]["lon"]
    sign0 = int(sun // 30.0)
    if kind == "nakshatra":
        event = lambda jd, target: S.longitude_event(jd, 2, target, backward=False, cfg=cfg)  # noqa: E731
        target = moon
    elif kind == "yoga":
        event = lambda jd, target: S.sum_event(jd, 2, 1, target, backward=False, cfg=cfg)  # noqa: E731
        target = (moon + sun) % 360.0
    else:
        event = lambda jd, target: S.longitude_event(jd, 2, target, 1, "diff", False, cfg)  # noqa: E731
        target = (moon - sun) % 360.0
    if period == "fortnightly":
        return min(event(jd_from, target), event(jd_from, (target + 180.0) % 360.0))
    if period == "daily":
        p = E.planet_positions(jd_from, cfg)
        elong = (p["Moon"]["lon"] - p["Sun"]["lon"]) % 360.0
        step = target % 12.0
        k = int((elong - step) // 12.0) + 1
        return event(jd_from, (step + k * 12.0) % 360.0)
    jd = event(jd_from, target)
    while period == "annual" and int(E.planet_positions(jd, cfg)["Sun"]["lon"] // 30.0) != sign0:
        jd = event(jd + 0.0035, target)
    return jd
