"""
core_logic/panchanga.py
=======================
Modularized Calculation Engine for the Vedic Panchanga (Five Limbs of Time)
and Classical Muhurta Timings.
Sources (docs/SOURCES.md section 8): nakshatra SS 2.64, yoga SS 2.65, tithi SS 2.66, karana SS 2.67-69, the
weekday and horas SS 1.51-52 and BPHS 27.13; Rahu kala, Gulika and Yamaghanta Kalaprakasika ch. 33 (and UK's
notes: a South Indian practice); tyajya (varjyam) PM 2.21 notes and UK's notes; muhurtas PM 2.21 notes.

The Five Limbs of Panchanga:
1. Tithi (Lunar day: 360° / 30 = 12° Sun-Moon separation)
2. Vaara (Solar weekday & planetary ruler, Hora cycle)
3. Nakshatra (Lunar mansion: 360° / 27 = 13°20' Moon longitude)
4. Yoga (Nitya Soli-Lunar Yoga: (Sun + Moon) / 13°20')
5. Karana (Half-tithi: 6° separation, 4 fixed + 7 repeating)

Additional Muhurta Engines:
- Rahu Kalam, Yama Ghantam, Gulika Kalam
- Abhijit Muhurta & Brahma Muhurta
- Dina Mana & Ratri Mana

"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional, Any

from .natal_chart import norm360, RASI_NAMES_EN

# ===========================================================================
# 1. Tithi (Lunar Phase Day)
# ===========================================================================

TITHI_NAMES = [
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shasthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shasthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Amavasya"
]

TITHI_GROUPS = {
    1: ("Nanda", "Prosperity & Joy", "Venus"),
    2: ("Bhadra", "Auspicious & Steady", "Mercury"),
    3: ("Jaya", "Victory & Success", "Mars"),
    4: ("Rikta", "Hollow / Obstacles", "Saturn"),
    5: ("Poorna", "Fullness & Completion", "Jupiter"),
    6: ("Nanda", "Prosperity & Joy", "Venus"),
    7: ("Bhadra", "Auspicious & Steady", "Mercury"),
    8: ("Jaya", "Victory & Success", "Mars"),
    9: ("Rikta", "Hollow / Obstacles", "Saturn"),
    10: ("Poorna", "Fullness & Completion", "Jupiter"),
    11: ("Nanda", "Prosperity & Joy", "Venus"),
    12: ("Bhadra", "Auspicious & Steady", "Mercury"),
    13: ("Jaya", "Victory & Success", "Mars"),
    14: ("Rikta", "Hollow / Obstacles", "Saturn"),
    15: ("Poorna", "Fullness & Completion", "Saturn / Moon"),
}

def compute_tithi(sun_lon: float, moon_lon: float) -> Dict[str, Any]:
    """
    Computes Tithi (1 to 30), Paksha, and elapsed percentage.
    Elongation = (Moon - Sun) % 360.
    Each Tithi spans 12.0°.
    """
    elongation = norm360(moon_lon - sun_lon)
    t_idx = int(elongation // 12.0)  # 0 to 29
    t_num = t_idx + 1               # 1 to 30
    
    paksha = "Shukla (Waxing)" if t_num <= 15 else "Krishna (Waning)"
    name = TITHI_NAMES[t_idx]
    
    deg_in_tithi = elongation - (t_idx * 12.0)
    elapsed_pct = round((deg_in_tithi / 12.0) * 100.0, 2)
    rem_pct = round(100.0 - elapsed_pct, 2)
    
    mod15 = ((t_num - 1) % 15) + 1
    group_name, nature, ruler = TITHI_GROUPS.get(mod15, ("Poorna", "Fullness", "Jupiter"))
    
    return {
        "tithi_number": t_num,
        "tithi_name": name,
        "paksha": paksha,
        "full_name": f"{paksha.split()[0]} {name}",
        "group": group_name,
        "nature": nature,
        "ruler": ruler,
        "elongation_deg": round(elongation, 4),
        "deg_in_tithi": round(deg_in_tithi, 4),
        "elapsed_percent": elapsed_pct,
        "remaining_percent": rem_pct
    }


# ===========================================================================
# 2. Vaara (Solar Weekday & Horas)
# ===========================================================================

VAARA_NAMES = [
    ("Ravivara", "Sunday", "Sun"),
    ("Somavara", "Monday", "Moon"),
    ("Mangalavara", "Tuesday", "Mars"),
    ("Budhavara", "Wednesday", "Mercury"),
    ("Guruvara", "Thursday", "Jupiter"),
    ("Shukravara", "Friday", "Venus"),
    ("Shanivara", "Saturday", "Saturn")
]

# Order of Horas from Sun (descending planetary speed/distance)
HORA_ORDER = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

def compute_vaara(
    weekday_idx: int,
    birth_hour_decimal: float = 12.0,
    sunrise_hour_decimal: float = 6.0
) -> Dict[str, Any]:
    """
    Computes Vaara (weekday from local sunrise) and current Hora ruler.
    weekday_idx: 0=Sunday, 1=Monday ... 6=Saturday.
    If birth is before sunrise, the astrological vaara belongs to the previous day.
    """
    effective_idx = weekday_idx
    if birth_hour_decimal < sunrise_hour_decimal:
        effective_idx = (effective_idx - 1) % 7
        
    sa_name, en_name, ruler = VAARA_NAMES[effective_idx]
    
    # Calculate Hora ruler (1-hour planetary period starting at sunrise)
    hours_from_sunrise = birth_hour_decimal - sunrise_hour_decimal
    if hours_from_sunrise < 0.0:
        hours_from_sunrise += 24.0
    hora_idx = int(hours_from_sunrise) % 24
    
    day_ruler_idx = HORA_ORDER.index(ruler)
    hora_ruler = HORA_ORDER[(day_ruler_idx + hora_idx) % 7]
    
    return {
        "weekday_index": effective_idx,
        "vaara_sanskrit": sa_name,
        "vaara_english": en_name,
        "day_lord": ruler,
        "hora_number": hora_idx + 1,
        "hora_lord": hora_ruler
    }


# ===========================================================================
# 3. Nakshatra (Lunar Mansion)
# ===========================================================================

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun",
    "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury"
]

def compute_nakshatra(moon_lon: float) -> Dict[str, Any]:
    """
    Computes Nakshatra (0 to 26), Pada (1 to 4), and degrees elapsed.
    Each Nakshatra spans 13°20' (13.33333°).
    Each Pada spans 3°20' (3.33333°).
    """
    lon = norm360(moon_lon)
    span = 360.0 / 27.0
    nak_idx = int(lon // span)
    deg_in_nak = lon - (nak_idx * span)
    
    pada_span = span / 4.0
    pada_idx = int(deg_in_nak // pada_span)  # 0 to 3
    pada_num = pada_idx + 1                 # 1 to 4
    
    elapsed_pct = round((deg_in_nak / span) * 100.0, 2)
    
    return {
        "nakshatra_index": nak_idx,
        "nakshatra_name": NAKSHATRA_NAMES[nak_idx],
        "lord": NAKSHATRA_LORDS[nak_idx],
        "pada": pada_num,
        "deg_in_nakshatra": round(deg_in_nak, 4),
        "elapsed_percent": elapsed_pct,
        "remaining_percent": round(100.0 - elapsed_pct, 2)
    }


# ===========================================================================
# 4. Yoga (Nitya Soli-Lunar Yoga)
# ===========================================================================

NITYA_YOGA_NAMES = [
    ("Vishkambha", False), ("Priti", True), ("Ayushman", True), ("Saubhagya", True),
    ("Shobhana", True), ("Atiganda", False), ("Sukarma", True), ("Dhriti", True),
    ("Shoola", False), ("Ganda", False), ("Vriddhi", True), ("Dhruva", True),
    ("Vyaghata", False), ("Harshana", True), ("Vajra", False), ("Siddhi", True),
    ("Vyatipata", False), ("Variyan", True), ("Parigha", False), ("Shiva", True),
    ("Siddha", True), ("Sadhya", True), ("Shubha", True), ("Shukla", True),
    ("Brahma", True), ("Indra", True), ("Vaidhriti", False)
]

def compute_yoga(sun_lon: float, moon_lon: float) -> Dict[str, Any]:
    """
    Computes Nitya Yoga (1 to 27) from the sum of Sun and Moon longitudes.
    Each Yoga spans 13°20' (13.33333°).
    """
    total_lon = norm360(sun_lon + moon_lon)
    span = 360.0 / 27.0
    y_idx = int(total_lon // span)  # 0 to 26
    y_num = y_idx + 1              # 1 to 27
    
    name, is_auspicious = NITYA_YOGA_NAMES[y_idx]
    deg_in_yoga = total_lon - (y_idx * span)
    elapsed_pct = round((deg_in_yoga / span) * 100.0, 2)
    
    return {
        "yoga_number": y_num,
        "yoga_name": name,
        "is_auspicious": is_auspicious,
        "nature": "Shubha (Auspicious)" if is_auspicious else "Ashubha (Inauspicious)",
        "deg_in_yoga": round(deg_in_yoga, 4),
        "elapsed_percent": elapsed_pct,
        "remaining_percent": round(100.0 - elapsed_pct, 2)
    }


# ===========================================================================
# 5. Karana (Half-Tithi Engine)
# ===========================================================================

CHARA_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti (Bhadra)"]

def compute_karana(sun_lon: float, moon_lon: float) -> Dict[str, Any]:
    """
    Computes Karana (1 to 60) based on 6.0° increments of elongation.
    4 Fixed Karanas: Shakuni, Chatushpada, Naga, Kintughna.
    7 Repeating Karanas: Bava, Balava, Kaulava, Taitila, Gara, Vanija, Vishti (Bhadra).
    """
    elongation = norm360(moon_lon - sun_lon)
    k_idx = int(elongation // 6.0)  # 0 to 59
    k_num = k_idx + 1
    
    if k_idx == 0:
        name = "Kintughna"
        k_type = "Fixed (Sthira)"
        is_auspicious = True
    elif k_idx == 57:
        name = "Shakuni"
        k_type = "Fixed (Sthira)"
        is_auspicious = False
    elif k_idx == 58:
        name = "Chatushpada"
        k_type = "Fixed (Sthira)"
        is_auspicious = False
    elif k_idx == 59:
        name = "Naga"
        k_type = "Fixed (Sthira)"
        is_auspicious = False
    else:
        c_idx = (k_idx - 1) % 7
        name = CHARA_KARANAS[c_idx]
        k_type = "Movable (Chara)"
        is_auspicious = (name != "Vishti (Bhadra)")
        
    deg_in_karana = elongation - (k_idx * 6.0)
    elapsed_pct = round((deg_in_karana / 6.0) * 100.0, 2)
    
    return {
        "karana_number": k_num,
        "karana_name": name,
        "karana_type": k_type,
        "is_bhadra": (name == "Vishti (Bhadra)"),
        "is_auspicious": is_auspicious,
        "deg_in_karana": round(deg_in_karana, 4),
        "elapsed_percent": elapsed_pct
    }


# ===========================================================================
# 6. Muhurta Timings: Rahu Kalam, Yama Ghantam, Abhijit Muhurta
# ===========================================================================

# 1-based eighth-part of daytime for each weekday (0=Sun, 1=Mon, ..., 6=Sat)
RAHU_KALAM_PARTS = {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 4, 6: 3}
YAMA_GHANTAM_PARTS = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 7, 6: 6}
GULIKA_KALAM_PARTS = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}

# Durmuhurta 1-based 15th-part indices for each weekday (0=Sun..6=Sat)
# (no verse checked: PM 2.21's notes name the 15 day muhurtas but not a weekday list); common lists give
# Wednesday the 5th and Thursday the 6th and 13th.
DURMUHURTA_PARTS = {
    0: [14],         # Sunday: 14th Muhurta
    1: [8, 12],      # Monday: 8th and 12th Muhurtas
    2: [4, 11],      # Tuesday: 4th and 11th Muhurtas
    3: [8],          # Wednesday: 8th Muhurta
    4: [12, 13],     # Thursday: 12th and 13th Muhurtas
    5: [4, 9],       # Friday: 4th and 9th Muhurtas
    6: [1, 2]        # Saturday: 1st and 2nd Muhurtas
}

# Tyajya (varjyam, visha ghatika) of each nakshatra: starts this many ghatis (of 60 in the nakshatra's span) into it
# and lasts 4 of them, a 15th of the nakshatra (UK's notes; PM 2.21's notes and table).  The texts' list is
# 50 24 30 40 14 11 30 20 32 30 20 18 22 20 14 14 10 14 20 24 20 10 10 18 16 24 30; this table, the app's,
# differs at Bharani 4, Ardra 21, U.Phalguni 1, Hasta 21, P.Ashadha 20, U.Bhadra 30.
TYAJYA_GHATIS = [50, 4, 30, 40, 14, 21, 30, 20, 32, 30, 20, 1, 21, 20, 14, 14, 10, 14, 20, 20, 20, 10, 10, 18, 16,
                 30, 30]


def tyajya_time(nak: int, nak_start_jd: float, nak_end_jd: float) -> Tuple[float, float]:
    """Tyajya time of nakshatra ``nak`` (0 = Aswini) running from ``nak_start_jd`` to ``nak_end_jd``: the
    panchanga lists it on a day when it overlaps the day (the nakshatra at the day's start and the next)."""
    span = nak_end_jd - nak_start_jd
    start = TYAJYA_GHATIS[nak] * span * 0.016666666666666666 + nak_start_jd
    return start, span * 0.06666666666666667 + start

# 8 Gowri Panchanga periods (Auspicious: Uthama, Amrutha, Labha, Shubha; Inauspicious: Roga, Bhaya, Visha, Chora)
# The Gowri panchangam of the Tamil almanacs (a regional practice; no verse checked)
GOWRI_DAY_ORDER = [
    ["Uthama", "Amrutha", "Roga", "Labha", "Shubha", "Visha", "Chora", "Bhaya"],      # Sun
    ["Amrutha", "Roga", "Labha", "Shubha", "Visha", "Chora", "Bhaya", "Uthama"],      # Mon
    ["Roga", "Labha", "Shubha", "Visha", "Chora", "Bhaya", "Uthama", "Amrutha"],      # Tue
    ["Labha", "Shubha", "Visha", "Chora", "Bhaya", "Uthama", "Amrutha", "Roga"],      # Wed
    ["Shubha", "Visha", "Chora", "Bhaya", "Uthama", "Amrutha", "Roga", "Labha"],      # Thu
    ["Visha", "Chora", "Bhaya", "Uthama", "Amrutha", "Roga", "Labha", "Shubha"],      # Fri
    ["Chora", "Bhaya", "Uthama", "Amrutha", "Roga", "Labha", "Shubha", "Visha"]       # Sat
]

GOWRI_NIGHT_ORDER = [
    ["Shubha", "Amrutha", "Roga", "Bhaya", "Chora", "Uthama", "Labha", "Visha"],      # Sun
    ["Amrutha", "Roga", "Bhaya", "Chora", "Uthama", "Labha", "Visha", "Shubha"],      # Mon
    ["Roga", "Bhaya", "Chora", "Uthama", "Labha", "Visha", "Shubha", "Amrutha"],      # Tue
    ["Bhaya", "Chora", "Uthama", "Labha", "Visha", "Shubha", "Amrutha", "Roga"],      # Wed
    ["Chora", "Uthama", "Labha", "Visha", "Shubha", "Amrutha", "Roga", "Bhaya"],      # Thu
    ["Uthama", "Labha", "Visha", "Shubha", "Amrutha", "Roga", "Bhaya", "Chora"],      # Fri
    ["Labha", "Visha", "Shubha", "Amrutha", "Roga", "Bhaya", "Chora", "Uthama"]       # Sat
]

GOWRI_QUALITIES = {
    "Uthama": ("Best / Supreme", True),
    "Amrutha": ("Nectar / Highly Auspicious", True),
    "Labha": ("Gains / Profit", True),
    "Shubha": ("Good / Auspicious", True),
    "Roga": ("Disease / Affliction", False),
    "Bhaya": ("Fear / Anxiety", False),
    "Visha": ("Poison / Extreme Hazard", False),
    "Chora": ("Theft / Loss", False)
}

def format_hour_decimal(hour_dec: float) -> str:
    """Formats decimal hour (e.g. 14.5) to HH:MM:SS format."""
    h = int(hour_dec) % 24
    m = int((hour_dec - int(hour_dec)) * 60.0)
    s = int(round((((hour_dec - int(hour_dec)) * 60.0) - m) * 60.0))
    return f"{h:02d}:{m:02d}:{s:02d}"

def compute_durmuhurta_timings(
    weekday_idx: int,
    sunrise_hours: float = 6.0,
    sunset_hours: float = 18.0
) -> List[Dict[str, Any]]:
    """
    Computes inauspicious Durmuhurta intervals for the given weekday.
    Each daytime is divided into 15 equal Muhurtas.
    """
    dina_mana = (sunset_hours - sunrise_hours) % 24.0
    muhurta_15th = dina_mana / 15.0
    
    parts = DURMUHURTA_PARTS.get(weekday_idx % 7, [14])
    durmuhurtas = []
    for p in parts:
        start_h = sunrise_hours + (p - 1) * muhurta_15th
        end_h = start_h + muhurta_15th
        durmuhurtas.append({
            "muhurta_index": p,
            "start": format_hour_decimal(start_h),
            "end": format_hour_decimal(end_h)
        })
    return durmuhurtas

def compute_gowri_panchangam(
    weekday_idx: int,
    sunrise_hours: float = 6.0,
    sunset_hours: float = 18.0,
    is_night: bool = False
) -> List[Dict[str, Any]]:
    """
    Computes 8 Gowri Panchanga Yamas (Day or Night): eighths of the day or night, named in the weekday's order
    of the Tamil almanacs (no verse checked).
    """
    dina_mana = (sunset_hours - sunrise_hours) % 24.0
    ratrimana = (24.0 - dina_mana)
    part_length = (ratrimana / 8.0) if is_night else (dina_mana / 8.0)
    base_time = sunset_hours if is_night else sunrise_hours
    
    order = GOWRI_NIGHT_ORDER[weekday_idx % 7] if is_night else GOWRI_DAY_ORDER[weekday_idx % 7]
    periods = []
    for i, name in enumerate(order):
        start_h = (base_time + i * part_length) % 24.0
        end_h = (start_h + part_length) % 24.0
        desc, is_good = GOWRI_QUALITIES.get(name, ("Neutral", True))
        periods.append({
            "part": i + 1,
            "name": name,
            "quality": desc,
            "is_auspicious": is_good,
            "start": format_hour_decimal(start_h),
            "end": format_hour_decimal(end_h)
        })
    return periods

def compute_muhurta_timings(
    weekday_idx: int,
    sunrise_hours: float = 6.0,
    sunset_hours: float = 18.0
) -> Dict[str, Any]:
    """
    Computes precise daytime Muhurta intervals:
    - Dina Mana (Duration of daytime)
    - Rahu Kalam (Inauspicious 1/8th period)
    - Yama Ghantam (Death/inauspicious period)
    - Gulika Kalam (Saturn son period)
    - Abhijit Muhurta (8th of 15 daytime muhurtas, highly auspicious)
    - Brahma Muhurta (Pre-dawn spiritual window)
    - Durmuhurta (Inauspicious 15th-part periods for the weekday)
    - Gowri Panchangam (8 day periods)
    """
    dina_mana = sunset_hours - sunrise_hours
    if dina_mana < 0.0:
        dina_mana += 24.0
    part_8th = dina_mana / 8.0
    muhurta_15th = dina_mana / 15.0
    
    def get_interval(part_idx: int) -> Tuple[str, str]:
        start = sunrise_hours + (part_idx - 1) * part_8th
        end = start + part_8th
        return format_hour_decimal(start), format_hour_decimal(end)
        
    rahu_start, rahu_end = get_interval(RAHU_KALAM_PARTS[weekday_idx % 7])
    yama_start, yama_end = get_interval(YAMA_GHANTAM_PARTS[weekday_idx % 7])
    gulika_start, gulika_end = get_interval(GULIKA_KALAM_PARTS[weekday_idx % 7])
    
    # Abhijit Muhurta is the 8th Muhurta out of 15 (centered around midday)
    abhijit_start_h = sunrise_hours + 7 * muhurta_15th
    abhijit_end_h = abhijit_start_h + muhurta_15th
    
    # Brahma Muhurta: 2 Muhurtas (96 mins) before sunrise
    brahma_start_h = sunrise_hours - (96.0 / 60.0)
    brahma_end_h = sunrise_hours - (48.0 / 60.0)
    
    durmuhurtas = compute_durmuhurta_timings(weekday_idx, sunrise_hours, sunset_hours)
    gowri_day = compute_gowri_panchangam(weekday_idx, sunrise_hours, sunset_hours, is_night=False)
    
    return {
        "dina_mana_hours": round(dina_mana, 2),
        "dina_mana_formatted": format_hour_decimal(dina_mana),
        "rahu_kalam": {"start": rahu_start, "end": rahu_end},
        "yama_ghantam": {"start": yama_start, "end": yama_end},
        "gulika_kalam": {"start": gulika_start, "end": gulika_end},
        "abhijit_muhurta": {
            "start": format_hour_decimal(abhijit_start_h),
            "end": format_hour_decimal(abhijit_end_h),
            "is_applicable": (weekday_idx != 2) # Abhijit is tainted on Wednesday
        },
        "brahma_muhurta": {
            "start": format_hour_decimal(brahma_start_h),
            "end": format_hour_decimal(brahma_end_h)
        },
        "durmuhurta": durmuhurtas,
        "gowri_panchangam_day": gowri_day
    }


# ===========================================================================
# Master Panchanga Evaluator
# ===========================================================================

def compute_full_panchanga(
    sun_lon: float,
    moon_lon: float,
    weekday_idx: int,
    birth_hour_decimal: float = 12.0,
    sunrise_hours: float = 6.0,
    sunset_hours: float = 18.0
) -> Dict[str, Any]:
    """
    Evaluates the complete Panchanga (All 5 Limbs) plus Muhurta Timings.
    """
    tithi = compute_tithi(sun_lon, moon_lon)
    vaara = compute_vaara(weekday_idx, birth_hour_decimal, sunrise_hours)
    nakshatra = compute_nakshatra(moon_lon)
    yoga = compute_yoga(sun_lon, moon_lon)
    karana = compute_karana(sun_lon, moon_lon)
    muhurta = compute_muhurta_timings(vaara["weekday_index"], sunrise_hours, sunset_hours)
    
    return {
        "tithi": tithi,
        "vaara": vaara,
        "nakshatra": nakshatra,
        "yoga": yoga,
        "karana": karana,
        "muhurta_timings": muhurta
    }

BHAVA_TITHI_NAMES = [
    ("Janma Tithi", "1st Bhava - Self & Vitality"),
    ("Dhana Tithi", "2nd Bhava - Wealth & Speech"),
    ("Bhratri Tithi", "3rd Bhava - Siblings & Enterprise"),
    ("Matri Tithi", "4th Bhava - Mother & Inner Happiness"),
    ("Putra Tithi", "5th Bhava - Children & Intelligence"),
    ("Satru Tithi", "6th Bhava - Enemies & Disease"),
    ("Kalatra Tithi", "7th Bhava - Spouse & Partnerships"),
    ("Mrityu Tithi", "8th Bhava - Longevity & Vulnerabilities"),
    ("Bhagya Tithi", "9th Bhava - Dharma, Father & Fortune"),
    ("Karma Tithi", "10th Bhava - Profession & Worldly Duty"),
    ("Laabha Tithi", "11th Bhava - Gains & Aspirations"),
    ("Vyaya Tithi", "12th Bhava - Losses, Foreign Realms & Moksha")
]

def compute_bhava_tithis(
    moon_lon: float,
    sun_lon: float
) -> Dict[str, Any]:
    """
    Computes the 12 Bhava Tithis (Special Karaka Tithis) across 3 cycles:
    A convention of the 'Special Tithis' option, no verse checked (docs/SOURCES.md section 8).
    Tithi angle = ((Moon - Sun) * House) % 360° -> mapped into Tithi 1..30.
    Cycles 1, 2, and 3 correspond to physical, mental, and spiritual manifestations.
    """
    base_diff = norm360(moon_lon - sun_lon)
    cycles_data = {1: {}, 2: {}, 3: {}}
    
    for cycle in (1, 2, 3):
        for h in range(1, 13):
            # Angular multiplier: House * Cycle
            multiplier = h * cycle
            h_angle = norm360(base_diff * multiplier)
            tithi_idx = int(h_angle // 12.0) + 1
            tithi_name = TITHI_NAMES[tithi_idx - 1]
            t_title, t_desc = BHAVA_TITHI_NAMES[h - 1]
            
            cycles_data[cycle][f"House_{h}_{t_title}"] = {
                "house": h,
                "tithi_title": t_title,
                "signification": t_desc,
                "cycle": cycle,
                "angle": round(h_angle, 2),
                "tithi_number": tithi_idx,
                "tithi_name": tithi_name,
                "is_shukla": (tithi_idx <= 15)
            }
            
    return {
        "base_sun_moon_diff": round(base_diff, 4),
        "cycle_1_physical": cycles_data[1],
        "cycle_2_mental": cycles_data[2],
        "cycle_3_spiritual": cycles_data[3]
    }
