"""
core_logic/special_lagnas_upagrahas.py
======================================
Modularized Calculation Engine for Special Lagnas (Visesha Lagnas), Aprakash Grahas (Shadow Planets),
and Kalavelas (Sub-Planets/Upagrahas).

Sources (docs/SOURCES.md section 5): Bhava, Hora and Ghati lagnas BPHS 5.2-8; Varnada BPHS 5.10-24; Sree lagna
PVR 5.7; Indu lagna UK ch. 4; Pranapada BPHS 3.71-74; the five shadow points BPHS 3.61-64; the kalavelas BPHS
3.66-70; Kunda PM 5.8.
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional, Any

from .natal_chart import norm360, RASI_NAMES_EN, RASI_NAMES_SA, RASI_LORDS

# Standard planetary rays for Indu Lagna calculation (Kala/Rays per Brihat Parasara Hora Shastra)
INDU_LAGNA_RAYS: Dict[str, int] = {
    "Sun": 30,
    "Moon": 16,
    "Mars": 6,
    "Mercury": 8,
    "Jupiter": 10,
    "Venus": 12,
    "Saturn": 1,
}

# Kalavelas (BPHS 3.66-70; PVR ch. 4): the day (night) is cut into 8 equal
# parts ruled in weekday order Sun..Saturn followed by one lord-less part.  The first day part
# belongs to the weekday lord, the first night part to the 5th planet from it.  Kaala, Mrityu,
# Artha Prahara, Yama Ghantaka and Maandi rise at the middle of the part of Sun, Mars, Mercury,
# Jupiter and Saturn; Gulika at the beginning of Saturn's part (BPHS 3.70: "the degree ascending at the time of
# start of Gulika's portion").  These are the defaults (INI UpagrahaRiseMethod=1 1 1 1 1 0);
# PVR ch. 4 has the reverse for Gulika and Maandi.
_PART_CYCLE = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", None]
KALAVELA_LORDS = {"Kaala": "Sun", "Mrityu": "Mars", "Artha_Prahara": "Mercury",
                  "Yama_Ghantaka": "Jupiter", "Gulika": "Saturn", "Mandi": "Saturn"}
KALAVELA_DEFAULT_POINT = {"Kaala": "middle", "Mrityu": "middle", "Artha_Prahara": "middle",
                          "Yama_Ghantaka": "middle", "Gulika": "beginning", "Mandi": "middle"}
_POINT_FRACTION = {"beginning": 0.0, "middle": 0.5, "end": 1.0}


def kalavela_part(weekday: int, is_night: bool, lord: str) -> int:
    """1-based part (of 8) of the day or night ruled by ``lord``; weekday 0 = Sunday."""
    first = (weekday + 4) % 7 if is_night else weekday % 7
    return (_PART_CYCLE.index(lord) - first) % 8 + 1


def kalavela_offset_fraction(weekday: int, is_night: bool, body_name: str, point: Optional[str] = None,
                             eighth: bool = False) -> float:
    """Rising moment of a kalavela as a fraction (0..1) of the day or night length; ``eighth``: in the lord-less
    8th part instead of its lord's (Mandi- / GulikaInSaturnPortion=0)."""
    part = kalavela_part(weekday, is_night, None if eighth else KALAVELA_LORDS[body_name])
    return (part - 1 + _POINT_FRACTION[point or KALAVELA_DEFAULT_POINT[body_name]]) / 8.0

# ===========================================================================
# 1. Special Lagnas (Visesha Lagnas)
# ===========================================================================

def compute_sree_lagna(lagna_lon: float, moon_lon: float) -> float:
    """
    Sree Lagna (SL): Signifies wealth, prosperity, and Lakshmi's blessings.
    Formula: For the elapsed fraction of Moon in its current Nakshatra (13°20'),
    traverse the same fraction across the zodiac from Lagna:
    SL = Lagna + (Moon_fraction_in_nakshatra * 360°)
    """
    nak_span = 360.0 / 27.0  # 13.3333°
    moon_in_nak = norm360(moon_lon) % nak_span
    fraction = moon_in_nak / nak_span
    return norm360(lagna_lon + (fraction * 360.0))

def compute_indu_lagna(lagna_lon: float, moon_lon: float) -> Tuple[int, str, int]:
    """
    Indu Lagna (IL): Signifies financial wealth and abundance.
    Formula:
    1. Determine the 9th house from Lagna and its lord's planetary rays.
    2. Determine the 9th house from Moon and its lord's planetary rays.
    3. Sum the rays: total_rays.
    4. Remainder = total_rays % 12 (if 0, treated as 12).
    5. Count remainder houses from Moon's rasi.
    Returns: (indu_lagna_sign_index, indu_lagna_sign_name, total_rays)
    """
    lagna_sign = int(norm360(lagna_lon) // 30.0)
    moon_sign = int(norm360(moon_lon) // 30.0)
    
    lord_from_lagna_9th = RASI_LORDS[(lagna_sign + 8) % 12]
    lord_from_moon_9th = RASI_LORDS[(moon_sign + 8) % 12]
    
    rays1 = INDU_LAGNA_RAYS.get(lord_from_lagna_9th, 6)
    rays2 = INDU_LAGNA_RAYS.get(lord_from_moon_9th, 6)
    total_rays = rays1 + rays2
    
    rem = total_rays % 12
    if rem == 0:
        rem = 12
        
    indu_sign = (moon_sign + rem - 1) % 12
    return indu_sign, RASI_NAMES_EN[indu_sign], total_rays

def compute_bhrigu_bindu(moon_lon: float, rahu_lon: float) -> float:
    """
    Bhrigu Bindu (BB): The destiny point / sensitive karmic axis.
    Midpoint between Rahu and the Moon, forward along the zodiac from Rahu to the Moon
    """
    r = norm360(rahu_lon)
    return norm360(r + ((norm360(moon_lon) - r) % 360.0) / 2.0)

def compute_kunda(lagna_lon: float) -> Tuple[float, int, str]:
    """
    Kunda: Birth time rectification sensitive point.
    Formula: Lagna longitude * 81 (modulo 360°).
    Kunda nakshatra should ideally align with natal Moon nakshatra or trines.
    """
    kunda_lon = norm360(norm360(lagna_lon) * 81.0)
    nak_idx = int(kunda_lon // (360.0 / 27.0))
    return kunda_lon, nak_idx, RASI_NAMES_EN[int(kunda_lon // 30.0)]

def compute_pranapada_lagna(
    sun_lon: float,
    sunrise_hours: float,
    birth_hours: float
) -> float:
    """
    Pranapada Lagna (PP): Signifies life force and vital breath.
    1 Ghati = 24 minutes. 1 Vighati = 24 seconds = 0.4 minutes = 1/150 hours.
    Pranapada moves 1 sign (30°) for every 15 Vighatis (6 minutes).
    Hence it moves 360° every 180 Vighatis (72 minutes).
    """
    elapsed_hours = (birth_hours - sunrise_hours) % 24.0
    vighatis = elapsed_hours * 150.0  # 1 hour = 150 vighatis
    # Base movement: vighatis * 2° (since 1 vighati = 2° = 120 arcmin)
    base_lon = norm360(vighatis * 2.0)
    
    # Sign of Sun determines addition:
    sun_sign = int(norm360(sun_lon) // 30.0)
    mod3 = sun_sign % 3
    if mod3 == 0:      # Movable sign: start from Sun
        start = sun_lon
    elif mod3 == 1:    # Fixed sign: start from 9th from Sun
        start = norm360(sun_lon + 240.0)
    else:              # Dual sign: start from 5th from Sun
        start = norm360(sun_lon + 120.0)
        
    return norm360(start + base_lon)

def compute_vighati_lagna(
    sun_lon: float,
    sunrise_hours: float,
    birth_hours: float,
    continuous: bool = True
) -> float:
    """
    Vighati Lagna (ViGL): 4 signs per ghati (2 deg per vighati of 24 s) from the Sun, the rate of
    Pranapada (BPHS 3.71-74) (a convention; no verse names it). ``continuous=False`` advances in whole vighatis.
    """
    elapsed_hours = (birth_hours - sunrise_hours) % 24.0
    vighatis = elapsed_hours * 150.0  # 1 hour = 60 mins = 150 vighatis
    if not continuous:
        vighatis = math.floor(vighatis)
    return norm360(sun_lon + vighatis * 2.0)

def compute_varnada_lagna(lagna_lon: float, hora_lagna_lon: float) -> Tuple[int, str]:
    """
    Varnada Lagna (VL): Key longevity and socio-spiritual status ascendant.
    Formula (Jaimini / BPHS Ch. 29):
    If Lagna is in odd sign: count forward from Aries to Lagna sign (count_L).
    If Lagna is in even sign: count backward from Pisces to Lagna sign.
    Similarly for Hora Lagna (count_HL).
    Combine counts: if both odd/even or mixed, calculate resulting sign.
    """
    l_sign = int(norm360(lagna_lon) // 30.0)
    hl_sign = int(norm360(hora_lagna_lon) // 30.0)
    
    cL = (l_sign + 1) if (l_sign % 2 == 0) else (12 - l_sign)
    cHL = (hl_sign + 1) if (hl_sign % 2 == 0) else (12 - hl_sign)
    
    if (l_sign % 2) == (hl_sign % 2):
        vl_val = (cL + cHL) % 12
    else:
        vl_val = abs(cL - cHL) % 12
        
    if vl_val == 0:
        vl_val = 12
        
    vl_sign = (vl_val - 1) if (l_sign % 2 == 0) else (12 - vl_val)
    vl_sign = vl_sign % 12
    return vl_sign, RASI_NAMES_EN[vl_sign]


def compute_varnada_lagnas(lagna_lon: float, hora_lagna_lon: float) -> List[float]:
    """Varnada lagnas of the 12 houses (V1 = Varnada Lagna .. V12; BPHS 5.21-24 "for the Varnad of each Bhava"):
    house i uses the signs Lagna + i and Hora Lagna + i; the longitude keeps the lagna's degrees in its sign."""
    deg = norm360(lagna_lon) % 30.0
    return [compute_varnada_lagna(lagna_lon + 30.0 * i, hora_lagna_lon + 30.0 * i)[0] * 30.0 + deg for i in range(12)]


def compute_indu_lagna_longitude(lagna_lon: float, moon_lon: float) -> float:
    """Indu Lagna as a longitude (UK ch. 4 counts the remainder of the rays from the Moon's sign): Moon + (rays - 1) signs."""
    _, _, rays = compute_indu_lagna(lagna_lon, moon_lon)
    return norm360(moon_lon + (rays - 1) * 30.0)


# ===========================================================================
# 2. Aprakash Grahas (Secondary Sun Shadow Upagrahas)
# Formulas according to BPHS 3.61-64:
# ===========================================================================

def compute_aprakash_grahas(sun_lon: float, method: int = 0) -> Dict[str, Dict[str, Any]]:
    """
    Calculates the 5 classical mathematical shadow planets derived from the Sun:
    1. Dhuma = Sun + 133°20' (4 signs 13°20')
    2. Vyatipata = 360° - Dhuma
    3. Parivesha = Vyatipata + 180°
    4. Indra Chapa (Kodanda) = 360° - Parivesha
    5. Upaketu (Sikhi) = Indra Chapa + 16°40'
    (Verification: Upaketu + 30° = Sun)
    ``method`` VyatipataMethod (a convention, no verse found): 1 gives Vyatipata = Dhuma + 53°20' and Parivesha =
    Vyatipata + 180°; Dhuma, Indra Chapa and Upaketu stay.
    """
    s = norm360(sun_lon)
    
    dhuma = norm360(s + 133.0 + (20.0 / 60.0))
    vyatipata = norm360(360.0 - dhuma)
    parivesha = norm360(vyatipata + 180.0)
    indrachapa = norm360(360.0 - parivesha)
    upaketu = norm360(indrachapa + 16.0 + (40.0 / 60.0))
    if method == 1:
        vyatipata = norm360(s + 560.0 / 3.0)
        parivesha = norm360(s + 1100.0 / 3.0)
    
    results = {}
    for name, lon in [
        ("Dhuma", dhuma),
        ("Vyatipata", vyatipata),
        ("Parivesha", parivesha),
        ("Indra Chapa", indrachapa),
        ("Upaketu", upaketu)
    ]:
        s_idx = int(lon // 30.0)
        results[name] = {
            "longitude": lon,
            "sign_index": s_idx,
            "sign_name": RASI_NAMES_EN[s_idx],
            "degree_in_sign": lon % 30.0,
            "lord": RASI_LORDS[s_idx]
        }
    return results


# ===========================================================================
# 3. Kalavelas & Upagrahas (Gulika, Mandi, Kaala, Mrityu, etc.)
# Portions of Day/Night based on planetary weekday rulerships
# ===========================================================================

def compute_kalavela_time(
    sunrise_hours: float,
    sunset_hours: float,
    weekday: int,            # 0=Sunday, 1=Monday, ..., 6=Saturday (Vedic day: from sunrise)
    is_night: bool,
    body_name: str,          # "Gulika", "Mandi", "Kaala", "Mrityu", "Artha_Prahara", "Yama_Ghantaka"
    point: Optional[str] = None   # "beginning" | "middle" | "end" of the part (Settings > Upagrahas)
) -> float:
    """
    Calculates the local clock time (in hours) when a Kalavela rises.
    Divides Dinamana (day duration) or Ratrimana (night duration) into 8 equal parts.
    The night length is approximated as 24h - day length; ``ephemeris.kalavela_longitudes``
    uses the real next sunrise.
    """
    dinamana = (sunset_hours - sunrise_hours) % 24.0
    span = (24.0 - dinamana) if is_night else dinamana
    base_time = sunset_hours if is_night else sunrise_hours
    return (base_time + kalavela_offset_fraction(weekday, is_night, body_name, point) * span) % 24.0

def compute_all_special_lagnas_and_upagrahas(
    lagna_lon: float,
    sun_lon: float,
    moon_lon: float,
    rahu_lon: float,
    hora_lagna_lon: float,
    sunrise_hours: float,
    birth_hours: float,
    sunset_hours: float,
    weekday: int
) -> Dict[str, Any]:
    """
    Master coordinator returning all Special Lagnas and Upagrahas.
    Point names as in data/point_names.csv.
    """
    is_night = (birth_hours < sunrise_hours or birth_hours >= sunset_hours)
    
    sree_lagna = compute_sree_lagna(lagna_lon, moon_lon)
    indu_sign, indu_name, indu_rays = compute_indu_lagna(lagna_lon, moon_lon)
    bhrigu_bindu = compute_bhrigu_bindu(moon_lon, rahu_lon)
    kunda_lon, kunda_nak, kunda_sign = compute_kunda(lagna_lon)
    pranapada = compute_pranapada_lagna(sun_lon, sunrise_hours, birth_hours)
    vighati_lagna = compute_vighati_lagna(sun_lon, sunrise_hours, birth_hours)
    varnada_sign, varnada_name = compute_varnada_lagna(lagna_lon, hora_lagna_lon)
    
    aprakash = compute_aprakash_grahas(sun_lon)
    
    kalavelas = {}
    for body in ["Gulika", "Mandi", "Kaala", "Mrityu", "Artha_Prahara", "Yama_Ghantaka"]:
        kalavelas[body] = {
            "rising_hour": compute_kalavela_time(sunrise_hours, sunset_hours, weekday, is_night, body),
            "is_night": is_night
        }
        
    return {
        "special_lagnas": {
            "Sree_Lagna": {"longitude": sree_lagna, "sign": RASI_NAMES_EN[int(sree_lagna // 30.0)]},
            "Indu_Lagna": {"sign_index": indu_sign, "sign_name": indu_name, "total_rays": indu_rays},
            "Bhrigu_Bindu": {"longitude": bhrigu_bindu, "sign": RASI_NAMES_EN[int(bhrigu_bindu // 30.0)]},
            "Kunda": {"longitude": kunda_lon, "sign": kunda_sign, "nakshatra_index": kunda_nak},
            "Pranapada": {"longitude": pranapada, "sign": RASI_NAMES_EN[int(pranapada // 30.0)]},
            "Vighati_Lagna": {"longitude": vighati_lagna, "sign": RASI_NAMES_EN[int(vighati_lagna // 30.0)]},
            "Varnada_Lagna": {"sign_index": varnada_sign, "sign_name": varnada_name}
        },
        "aprakash_grahas": aprakash,
        "kalavelas": kalavelas
    }
