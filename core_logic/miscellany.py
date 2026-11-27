"""
core_logic/miscellany.py
========================
Modularized Calculation Engine for the "Miscellany" tab (sources: docs/SOURCES.md sections 13-14).

The Five Specialized Miscellany Engines:
1. Angular Returns & Planetary Ingress Returns:
   - Planetary Returns: Solar (Varsha), Lunar (Masa), Mars, Mercury, Jupiter, Venus, Saturn
   - Exact angular separation returns (e.g., Tithi Pravesha Sun-Moon phase angle)
2. Astrological Progressions (the help's "Progressions (taught by Manu)"; Manusmriti 1.67, a human year a day of the gods):
   - Secondary Progressions (Day-for-a-Year: 1 solar day after birth = 1 tropical year of life)
   - Degree-per-Year (Symbolic / Manu Progression: 1.0° = 1.0 year, 30.0° = 1 rasi = 30.0 years)
   - Sudarshana Chakra Progression (1 sign = 1 year simultaneously for Lagna, Moon, Sun)
3. Prashna / Horary Astrology (Prasna Marga):
   - Prashna Lagna from timestamp or querent query number (1-108 or 1-249 KP)
   - Classical Kerala Sphutas: Trisphuta, Chatusphuta, Panchasphuta, Prana, Deha, Mrityu
   - Karya Siddhi (Fructification) judgment between Lagnesha and Karyesha
   - Tamboola Prashna (Betel leaf analysis) & Ashtamangala Prashna
4. Vedic Panchanga & Muhurta:
   - Tithi, Vaara, Nakshatra, Yoga, Karana, Choghadiya (Day/Night), and 24 Horas
5. Laghu Parasari:
   - Functional nature, Yogakarakas, Marakas, and Kendra-Trikonadhipati Raja Yogas

The Kerala sphutas follow PM ch. 5; Laghu Parasari is laghu_parasari.py.
"""

from __future__ import annotations
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Callable

from .natal_chart import (
    norm360,
    RASI_NAMES_EN,
    RASI_LORDS,
    NAKSHATRA_NAMES,
    NAKSHATRA_LORDS,
    OWN_SIGNS,
    EXALTATION,
    DEBILITATION
)
from .panchanga import compute_full_panchanga
from .laghu_parasari import evaluate_functional_nature_for_lagna, find_laghu_parasari_raja_yogas, evaluate_maraka_grahas
from .mundane import solve_longitude_crossing

PLANETS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# ===========================================================================
# 1. Angular Returns & Planetary Returns Engine
# ===========================================================================

def compute_planetary_return(
    planet: str,
    natal_lon: float,
    current_lon_func: Callable[[float], float],
    approx_jd: float,
    search_window_days: float = 400.0
) -> Dict[str, Any]:
    """
    Computes exact Julian Day when a transiting planet returns to its natal longitude.
    Supported: Solar Return (Sun), Lunar Return (Moon), Mars, Mercury, Jupiter, Venus, Saturn.
    """
    exact_jd = solve_longitude_crossing(
        calc_func=current_lon_func,
        target_lon=natal_lon,
        jd_approx=approx_jd,
        step_days=1.0 if planet not in ("Moon", "Mercury") else 0.25,
        max_days=search_window_days
    )
    
    return {
        "event_type": f"{planet} Return",
        "planet": planet,
        "natal_longitude": round(natal_lon, 4),
        "exact_return_jd": exact_jd,
        "sign_index": int(natal_lon // 30.0),
        "sign_name": RASI_NAMES_EN[int(natal_lon // 30.0)]
    }

def compute_angular_separation_return(
    body1_lon_func: Callable[[float], float],
    body2_lon_func: Callable[[float], float],
    target_separation_deg: float,
    approx_jd: float,
    search_window_days: float = 40.0
) -> Dict[str, Any]:
    """
    Finds exact moment when the angular separation (Body2 - Body1) returns to target angle.
    Used for Tithi Pravesha (Sun-Moon angle return) and planetary cycle returns.
    """
    def separation(jd: float) -> float:
        return norm360(body2_lon_func(jd) - body1_lon_func(jd))
        
    exact_jd = solve_longitude_crossing(
        calc_func=separation,
        target_lon=target_separation_deg,
        jd_approx=approx_jd,
        step_days=0.5,
        max_days=search_window_days
    )
    
    return {
        "event_type": "Angular Separation Return",
        "target_separation": round(target_separation_deg, 4),
        "exact_jd": exact_jd
    }


# ===========================================================================
# 2. Astrological Progressions Engine
# ===========================================================================

def compute_secondary_progression(
    birth_dt: datetime,
    current_age_years: float,
    natal_longitudes: Dict[str, float],
    natal_daily_speeds: Dict[str, float],
    natal_lagna_lon: float
) -> Dict[str, Any]:
    """
    Computes Secondary Progression (Day-for-a-Year / 1 solar day = 1 year of life):
    Progressed_Date = Birth_Date + Age_in_Days
    Progressed_Longitude = Natal_Longitude + (Daily_Speed * Age_Years)
    Progressed_Lagna moves ~361° per day (approx 1° per year progression rate).
    """
    progressed_dt = birth_dt + timedelta(days=current_age_years)
    progressed_positions = {}
    
    for p, lon in natal_longitudes.items():
        spd = natal_daily_speeds.get(p, 1.0)
        p_lon = norm360(lon + (spd * current_age_years))
        p_sign = int(p_lon // 30.0)
        progressed_positions[p] = {
            "longitude": round(p_lon, 2),
            "sign_index": p_sign,
            "sign_name": RASI_NAMES_EN[p_sign],
            "deg_in_sign": round(p_lon % 30.0, 2)
        }
        
    # Progressed Lagna: moves ~0.9856° to 1.0° per year
    prog_lagna_lon = norm360(natal_lagna_lon + (0.9856 * current_age_years))
    prog_lagna_sign = int(prog_lagna_lon // 30.0)
    
    return {
        "progression_type": "Secondary Progression (Day-for-a-Year)",
        "current_age_years": current_age_years,
        "equivalent_progressed_date": progressed_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "progressed_lagna": {
            "longitude": round(prog_lagna_lon, 2),
            "sign_index": prog_lagna_sign,
            "sign_name": RASI_NAMES_EN[prog_lagna_sign]
        },
        "progressed_planets": progressed_positions
    }

def compute_symbolic_manu_progression(
    natal_longitudes: Dict[str, float],
    natal_lagna_lon: float,
    current_age_years: float,
    rate_deg_per_year: float = 1.0
) -> Dict[str, Any]:
    """
    Computes Symbolic / Manu Progression:
    Rate = 1.0° per year (30° = 1 sign = 30 years).
    Advances all natal planets and Lagna uniformly along the zodiac.
    """
    offset = norm360(rate_deg_per_year * current_age_years)
    prog_lagna = norm360(natal_lagna_lon + offset)
    prog_positions = {}
    
    for p, lon in natal_longitudes.items():
        plon = norm360(lon + offset)
        psign = int(plon // 30.0)
        prog_positions[p] = {
            "longitude": round(plon, 2),
            "sign_index": psign,
            "sign_name": RASI_NAMES_EN[psign]
        }
        
    return {
        "progression_type": f"Symbolic Manu Progression ({rate_deg_per_year}° / Year)",
        "current_age_years": current_age_years,
        "total_progression_arc": round(offset, 2),
        "progressed_lagna": {
            "longitude": round(prog_lagna, 2),
            "sign_name": RASI_NAMES_EN[int(prog_lagna // 30.0)]
        },
        "progressed_planets": prog_positions
    }

def compute_sudarshana_progression(
    lagna_sign: int,
    moon_sign: int,
    sun_sign: int,
    current_age_years: float
) -> Dict[str, Any]:
    """
    Computes Sudarshana Chakra Progression:
    Each year advances 1 sign (30°) simultaneously from:
    1. Lagna (Physical body & health)
    2. Moon (Mind, emotions & society)
    3. Sun (Soul, authority & father)
    """
    elapsed_years = int(current_age_years)
    prog_lagna_sign = (lagna_sign + elapsed_years) % 12
    prog_moon_sign = (moon_sign + elapsed_years) % 12
    prog_sun_sign = (sun_sign + elapsed_years) % 12
    
    return {
        "progression_type": "Sudarshana Chakra 1-Sign/Year Progression",
        "age_year": elapsed_years + 1,
        "physical_lagna_sign": RASI_NAMES_EN[prog_lagna_sign],
        "emotional_moon_sign": RASI_NAMES_EN[prog_moon_sign],
        "spiritual_sun_sign": RASI_NAMES_EN[prog_sun_sign]
    }

BHRIGU_DIVISORS = {"Sun": 19, "Moon": 45, "Mars": 14, "Mercury": 46, "Jupiter": 83, "Venus": 27, "Saturn": 30}


def progression_sun_arc(natal_sun: float, sun_now: float, years: int, days: float) -> float:
    """The Sun's arc since birth of the progressions: (Sun now - natal Sun) +
    (years - 4) x 360, raised by 360 until within 30 deg of the mean motion ``days`` x 0.98564736 (``years`` =
    progressed year - birth year, ``days`` since birth)."""
    arc = (sun_now - natal_sun) + (years - 4) * 360.0
    while abs(arc - days * 0.9856473590852141) > 30.0:
        arc += 360.0
    return arc


def compute_bhrigu_pada_progression(natal_longitudes: Dict[str, float], natal_sun: float, sun_now: float,
                                    years: int, days: float) -> Dict[str, float]:
    """The "Progressed (Bhrigu)" chart (a convention; no text found): Sun .. Saturn move on
    by the Sun's arc (``progression_sun_arc``) / 19, 45, 14, 46, 83, 27, 30 from their natal (chosen varga) longitudes;
    the lagna and the nodes are the chart's at the progressed moment.  Returns {planet: progressed longitude}."""
    arc = progression_sun_arc(natal_sun, sun_now, years, days)
    return {p: norm360(lon + arc / BHRIGU_DIVISORS[p]) for p, lon in natal_longitudes.items() if p in BHRIGU_DIVISORS}


def solar_progression_years(natal_sun: float, sun_now: float, years: int, days: float,
                                  division: int = 1) -> float:
    """The "Progressed (30 deg)" chart ('Solar Progression (1 sign per year in chosen
    varga)'): the birth chart advanced by this many true solar years (definition 3): the Sun's arc / 360 years
    of life, at 30 / ``division`` deg a year."""
    return progression_sun_arc(natal_sun, sun_now, years, days) * (30.0 / division) / 129600.0


def sudarsana_progression_arc(natal_sun: float, sun_now: float, years: int, days: float) -> float:
    """"Sudarsana Chakra Dasa Progression" (BPHS 74; PVR ch. 31): every body and lagna of the natal chart moves by this arc:
    the Sun's arc of life, a sign a year (1/12 of it, the cycle of 4320 degrees)."""
    return (progression_sun_arc(natal_sun, sun_now, years, days) % 4320.0) / 12.0


def compute_kalachakra_progression(
    moon_longitude: float,
    planet_longitudes: Dict[str, float],
    current_age_years: float
) -> Dict[str, Any]:
    """
    Computes Kalachakra Dasa Based Progression:
    The "Progressed (KCD)" chart ('Showing Kalachakra Dasa Based Progression'; the Kalachakra of BPHS 46.52-95).
    Moon and physical planetary longitudes progress based on the Savya/Apasavya progression of the
    Kalachakra wheel (Deha/Jeeva signs and movement jumps).
    """
    # 100-year canonical Kalachakra cycle speed: ~3.6° per year
    k_rate = 360.0 / 100.0  # 3.6° per year
    shift_deg = norm360(current_age_years * k_rate)
    prog_moon = norm360(moon_longitude + shift_deg)
    prog_planets = {}
    for p, lon in planet_longitudes.items():
        p_prog = norm360(lon + shift_deg)
        prog_planets[p] = {
            "natal_longitude": round(lon, 4),
            "progressed_longitude": round(p_prog, 4),
            "progressed_sign": RASI_NAMES_EN[int(p_prog // 30.0)]
        }
    return {
        "progression_type": "Kalachakra Dasa Based Progression",
        "current_age_years": current_age_years,
        "shift_degrees": round(shift_deg, 4),
        "progressed_moon": {
            "longitude": round(prog_moon, 4),
            "sign": RASI_NAMES_EN[int(prog_moon // 30.0)]
        },
        "progressed_planets": prog_planets
    }


# ===========================================================================
# 3. Prashna (Horary Astrology) Engine
# ===========================================================================

def fertility_reading(sphuta: float, male: bool) -> str:
    """Phaladeepika 12.14: a man's Beeja sphuta (Sun + Venus + Jupiter) in an odd sign and an odd navamsa, a woman's
    Kshetra sphuta (Moon + Mars + Jupiter) in an even sign and an even navamsa, gives children ("good"); the sign and
    the navamsa of different kinds, children with effort ("mid"); both of the other kind, "bad"."""
    lon = norm360(sphuta)
    odd_sign, odd_nav = int(lon // 30.0) % 2 == 0, int(lon // (10.0 / 3.0)) % 12 % 2 == 0     # index 0, Aries, is odd
    if odd_sign != odd_nav:
        return "mid"
    return "good" if odd_sign == male else "bad"


def compute_prashna_sphutas(
    lagna_lon: float,
    moon_lon: float,
    sun_lon: float,
    gulika_lon: float,
    rahu_lon: float,
    mars_lon: float = 0.0,
    venus_lon: float = 0.0,
    jupiter_lon: float = 0.0
) -> Dict[str, Any]:
    """
    Kerala Prashna Sphutas (PM ch. 5; points 33..44):
    1. Trisphuta = Lagna + Moon + Gulika
    2. Chatusphuta = Trisphuta + Sun
    3. Panchasphuta = Chatusphuta + Rahu
    4. Prana Sphuta = Lagna * 5 + Gulika
    5. Deha Sphuta = Moon * 8 + Gulika
    6. Mrityu Sphuta = Gulika * 7 + Sun
    7. Sookshma TriSphuta = Prana + Deha + Mrityu
    8. Tithi Sphuta = Moon - Sun
    9. Yoga Sphuta (Sun+Moon) = Sun + Moon
    10. Rahu Tithi Sphuta = Rahu - Sun
    11. Beeja Sphuta (Male virility) = Sun + Venus + Jupiter
    12. Kshetra Sphuta (Female fertility) = Moon + Mars + Jupiter
    13. Yogi Sphuta = Sun + Moon + 93°20'
    14. Avayogi Sphuta = Yogi Sphuta + 186°40' (6th nakshatra from Yogi)
    """
    l = norm360(lagna_lon)
    m = norm360(moon_lon)
    s = norm360(sun_lon)
    g = norm360(gulika_lon)
    r = norm360(rahu_lon)
    ma = norm360(mars_lon)
    ve = norm360(venus_lon)
    ju = norm360(jupiter_lon)
    
    tri = norm360(l + m + g)
    chatu = norm360(tri + s)
    pancha = norm360(chatu + r)
    prana = norm360(l * 5.0 + g)
    deha = norm360(m * 8.0 + g)
    mrityu = norm360(g * 7.0 + s)
    sookshma_tri = norm360(prana + deha + mrityu)

    tithi_sphuta = norm360(m - s)
    yoga_sphuta = norm360(s + m)
    rahu_tithi_sphuta = norm360(r - s)
    
    beeja_sphuta = norm360(s + ve + ju)
    kshetra_sphuta = norm360(m + ma + ju)
    
    # Yogi point (a modern rule; no classical verse found): Pushya 0° offset = 93°20' (93.3333°)
    yogi_point = norm360(s + m + 93.0 + (20.0 / 60.0))
    # Avayogi point: 6th nakshatra = + (360 * 6 / 27) = + 186°40'
    avayogi_point = norm360(yogi_point + 186.0 + (40.0 / 60.0))
    
    # Fertility (Phaladeepika 12.14): Beeja odd sign and odd navamsa, Kshetra even and even; one of each, with effort
    beeja_verdict = {"good": "Fertile (odd sign and odd navamsa)", "mid": "With effort (sign and navamsa differ)",
                     "bad": "Weak (even sign and even navamsa)"}[fertility_reading(beeja_sphuta, male=True)]
    kshetra_verdict = {"good": "Fertile (even sign and even navamsa)", "mid": "With effort (sign and navamsa differ)",
                       "bad": "Weak (odd sign and odd navamsa)"}[fertility_reading(kshetra_sphuta, male=False)]

    # Longevity / Fructification Check:
    vitality = (prana + deha) / 2.0
    fructification = "Favorable (Vitality Prana/Deha exceeds Mrityu Sphuta)" if vitality > mrityu else "Obstacles Expected (Mrityu Sphuta dominates, remedies needed)"

    def pack(lon_val: float) -> Dict[str, Any]:
        s_i = int(lon_val // 30.0)
        nak_i = int(lon_val // (360.0 / 27.0))
        return {
            "longitude": lon_val,
            "sign": RASI_NAMES_EN[s_i],
            "sign_index": s_i,
            "nakshatra_index": nak_i,
            "nakshatra_name": NAKSHATRA_NAMES[nak_i],
            "nakshatra_lord": NAKSHATRA_LORDS[nak_i]
        }

    return {
        "trisphuta": pack(tri),
        "chatusphuta": pack(chatu),
        "panchasphuta": pack(pancha),
        "sookshma_trisphuta": pack(sookshma_tri),
        "prana_sphuta": pack(prana),
        "deha_sphuta": pack(deha),
        "mrityu_sphuta": pack(mrityu),
        "tithi_sphuta": pack(tithi_sphuta),
        "yoga_sphuta": pack(yoga_sphuta),
        "rahu_tithi_sphuta": pack(rahu_tithi_sphuta),
        "beeja_sphuta": {**pack(beeja_sphuta), "virility_verdict": beeja_verdict},
        "kshetra_sphuta": {**pack(kshetra_sphuta), "fertility_verdict": kshetra_verdict},
        "yogi_sphuta": {**pack(yogi_point), "yogi_graha": NAKSHATRA_LORDS[int(yogi_point // (360.0 / 27.0))]},
        "avayogi_sphuta": {**pack(avayogi_point), "avayogi_graha": NAKSHATRA_LORDS[int(avayogi_point // (360.0 / 27.0))]},
        "fructification_judgment": fructification
    }

def evaluate_karya_siddhi(
    lagnesha: str,
    karyesha: str,
    lagnesha_house: int,
    karyesha_house: int,
    mutual_aspect: bool = True
) -> Dict[str, Any]:
    """
    Evaluates Prashna Karya Siddhi (Success of Undertaking):
    Relates the querent (Lagnesha) with the significator of the question (Karyesha).
    - 7th house for marriage / partnership
    - 10th house for career / government job
    - 4th house for property / vehicles
    - 5th house for progeny / education
    """
    is_success = False
    reasons = []
    
    # 1. Conjunction in same house
    if lagnesha_house == karyesha_house:
        is_success = True
        reasons.append(f"Lagnesha ({lagnesha}) and Karyesha ({karyesha}) are conjoined in bhava {lagnesha_house} (Direct Fructification).")
        
    # 2. Both placed in Kendras or Trikonas
    kendra_trikona = {1, 4, 7, 10, 5, 9, 11}
    if lagnesha_house in kendra_trikona and karyesha_house in kendra_trikona:
        is_success = True
        reasons.append(f"Both significators are favorably stationed in auspicious bhavas ({lagnesha_house} & {karyesha_house}).")
        
    # 3. Dusthana placement
    if lagnesha_house in (6, 8, 12) or karyesha_house in (6, 8, 12):
        reasons.append("One or both significators placed in Dusthana (6, 8, 12), indicating delay or requiring sustained effort.")
        
    outcome = "Karya Siddhi Assured (Success and Achievement)" if is_success else "Delayed or Qualified Result"
    
    return {
        "querent_lord": lagnesha,
        "karyesha_lord": karyesha,
        "lagnesha_house": lagnesha_house,
        "karyesha_house": karyesha_house,
        "outcome": outcome,
        "rationale": reasons
    }

def compute_tamboola_prashna(number_of_leaves: int) -> Dict[str, Any]:
    """
    Classical Kerala Tamboola Prashna (Betel Leaf Divination):
    - Multiplies number of leaves by 2, adds 1, divides by 7: Remainder identifies Tamboola Lord.
    - 1=Sun (fever/honor), 2=Moon (peace/water), 3=Mars (disputes), 4=Mercury (commerce),
      5=Jupiter (auspicious gain), 6=Venus (luxury/marriage), 7/0=Saturn (sorrow/delay).
    """
    rem = ((number_of_leaves * 2) + 1) % 7
    TAMBOOLA_LORDS = {
        1: ("Sun", "Auspicious, high government honor, vitality"),
        2: ("Moon", "Mental tranquility, maternal blessings, prosperity"),
        3: ("Mars", "Litigation, friction, courage, energetic breakthrough"),
        4: ("Mercury", "Commercial profit, scholastic success, diplomatic solution"),
        5: ("Jupiter", "Supreme auspiciousness, divine blessings, wealth, children"),
        6: ("Venus", "Matrimony, artistic acclaim, vehicles, contentment"),
        0: ("Saturn", "Delays, chronic obstacles, lessons in perseverance")
    }
    lord, meaning = TAMBOOLA_LORDS.get(rem, ("Jupiter", "Auspiciousness"))
    
    return {
        "betel_leaves_count": number_of_leaves,
        "tamboola_remainder": rem,
        "tamboola_lord": lord,
        "prognosis": meaning
    }


# ===========================================================================
# 4. Choghadiya Muhurta Timings (Day & Night)
# ===========================================================================

CHOGHADIYA_ORDER_DAY = {
    0: ["Udvega", "Chara", "Labha", "Amrita", "Kala", "Shubha", "Roga"],    # Sunday
    1: ["Amrita", "Kala", "Shubha", "Roga", "Udvega", "Chara", "Labha"],    # Monday
    2: ["Roga", "Udvega", "Chara", "Labha", "Amrita", "Kala", "Shubha"],    # Tuesday
    3: ["Labha", "Amrita", "Kala", "Shubha", "Roga", "Udvega", "Chara"],    # Wednesday
    4: ["Shubha", "Roga", "Udvega", "Chara", "Labha", "Amrita", "Kala"],    # Thursday
    5: ["Chara", "Labha", "Amrita", "Kala", "Shubha", "Roga", "Udvega"],    # Friday
    6: ["Kala", "Shubha", "Roga", "Udvega", "Chara", "Labha", "Amrita"]     # Saturday
}

CHOGHADIYA_QUALITY = {
    "Amrita": ("Nectar / Best", True),
    "Shubha": ("Auspicious / Excellent", True),
    "Labha": ("Gain / Very Good", True),
    "Chara": ("Variable / Mobile - Good for travel", True),
    "Roga": ("Disease / Harmful", False),
    "Kala": ("Destruction / Inauspicious", False),
    "Udvega": ("Anxiety / Inauspicious", False)
}

def compute_choghadiya_muhurta(
    weekday_idx: int,
    sunrise_dt: datetime,
    sunset_dt: datetime
) -> List[Dict[str, Any]]:
    """
    Computes 8 daytime Choghadiya muhurtas (each ~1.5 hours):
    The daytime (Dinamana) is divided into 8 equal parts.
    The sequence is cyclically determined by weekday.
    """
    total_day_seconds = (sunset_dt - sunrise_dt).total_seconds()
    span_seconds = total_day_seconds / 8.0
    
    order = CHOGHADIYA_ORDER_DAY.get(weekday_idx % 7, CHOGHADIYA_ORDER_DAY[0])
    
    choghadiyas = []
    curr = sunrise_dt
    for i in range(8):
        name = order[i % 7]
        quality, is_good = CHOGHADIYA_QUALITY.get(name, ("Neutral", True))
        nxt = curr + timedelta(seconds=span_seconds)
        
        choghadiyas.append({
            "slot": i + 1,
            "name": name,
            "quality": quality,
            "is_auspicious": is_good,
            "start": curr.strftime("%H:%M:%S"),
            "end": nxt.strftime("%H:%M:%S")
        })
        curr = nxt
        
    return choghadiyas
