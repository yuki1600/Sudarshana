"""signs: part of natal_chart (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Any, Dict

# Rasis (Zodiac signs in Sanskrit and English)
RASI_NAMES_SA = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrischika",
    "Dhanus", "Makara", "Kumbha", "Meena"
]

RASI_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

RASI_LORDS = [
    "Mars", "Venus", "Mercury", "Moon",
    "Sun", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Saturn", "Jupiter"
]

# 27 Nakshatras and their Vimshottari Lords
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Svati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

# Exaltation signs and deep exaltation degrees
EXALTATION = {
    "Sun": (0, 10.0),       # Aries 10°
    "Moon": (1, 3.0),       # Taurus 3°
    "Mars": (9, 28.0),      # Capricorn 28°
    "Mercury": (5, 15.0),   # Virgo 15°
    "Jupiter": (3, 5.0),    # Cancer 5°
    "Venus": (11, 27.0),    # Pisces 27°
    "Saturn": (6, 20.0),    # Libra 20°
    "Rahu": (1, 20.0),      # Taurus 20° (or Gemini)
    "Ketu": (7, 20.0),      # Scorpio 20° (or Sagittarius)
}

# Debilitation signs are exactly opposite (180°)
DEBILITATION = {
    graha: ((sign + 6) % 12, deg)
    for graha, (sign, deg) in EXALTATION.items()
}

# Moolatrikona zones: (sign, start_deg, end_deg)
MOOLATRIKONA = {
    "Sun": (4, 0.0, 20.0),       # Leo 0-20°
    "Moon": (1, 3.0, 30.0),      # Taurus 3-30°
    "Mars": (0, 0.0, 12.0),      # Aries 0-12°
    "Mercury": (5, 15.0, 20.0),  # Virgo 15-20°
    "Jupiter": (8, 0.0, 10.0),   # Sagittarius 0-10°
    "Venus": (6, 0.0, 15.0),     # Libra 0-15°
    "Saturn": (10, 0.0, 20.0),   # Aquarius 0-20°
}

# Own Signs
OWN_SIGNS = {
    "Sun": [4],
    "Moon": [3],
    "Mars": [0, 7],
    "Mercury": [2, 5],
    "Jupiter": [8, 11],
    "Venus": [1, 6],
    "Saturn": [9, 10],
    "Rahu": [10],
    "Ketu": [7],
}

from ..utils import norm360, deg_to_dms, get_house_of_sign  # noqa: F401 — re-exported for backward compatibility

def get_rasi_info(longitude: float) -> Dict[str, Any]:
    """Returns sign index (0-11), sign names, and degree within sign (0-30°)."""
    lon = norm360(longitude)
    sign_idx = int(lon // 30.0)
    deg_in_sign = lon - (sign_idx * 30.0)
    return {
        "sign_idx": sign_idx,
        "sign_sa": RASI_NAMES_SA[sign_idx],
        "sign_en": RASI_NAMES_EN[sign_idx],
        "deg_in_sign": deg_in_sign,
        "lord": RASI_LORDS[sign_idx]
    }

def get_nakshatra_info(longitude: float) -> Dict[str, Any]:
    """
    Returns nakshatra index (0-26), name, lord, and pada (1-4).
    Each nakshatra = 13°20' (13.3333°). Each pada = 3°20' (3.3333°).
    """
    lon = norm360(longitude)
    nak_span = 360.0 / 27.0
    pada_span = nak_span / 4.0
    nak_idx = int(lon // nak_span)
    deg_in_nak = lon - (nak_idx * nak_span)
    pada = int(deg_in_nak // pada_span) + 1
    return {
        "nakshatra_idx": nak_idx,
        "nakshatra_name": NAKSHATRA_NAMES[nak_idx],
        "nakshatra_lord": NAKSHATRA_LORDS[nak_idx],
        "pada": pada,
        "deg_in_nak": deg_in_nak
    }

def get_graha_dignity(planet: str, longitude: float) -> str:
    """Evaluates dignities: Exalted, Moolatrikona, Own Sign, Debilitated, or General Sign."""
    if planet not in EXALTATION:
        return "Neutral"
    lon = norm360(longitude)
    sign = int(lon // 30.0)
    deg_in_sign = lon - (sign * 30.0)
    
    # 0. The moolatrikona sign is split by degree (BPHS): Mercury's Virgo exalted 0-15, moolatrikona 15-20, own 20-30;
    #    the Moon's Taurus exalted 0-3, moolatrikona 3-30; the others' moolatrikona then own sign. Never two at once.
    if planet in MOOLATRIKONA and sign == MOOLATRIKONA[planet][0]:
        _, mt_start, mt_end = MOOLATRIKONA[planet]
        if mt_start <= deg_in_sign < mt_end:
            return "Moolatrikona"
        return "Exalted" if sign == EXALTATION[planet][0] and deg_in_sign < mt_start else "Own Sign"

    # 1. Exaltation
    ex_sign, _ = EXALTATION[planet]
    if sign == ex_sign:
        return "Exalted"
        
    # 2. Debilitation
    deb_sign, _ = DEBILITATION[planet]
    if sign == deb_sign:
        return "Debilitated"
        
    # 3. Moolatrikona
    if planet in MOOLATRIKONA:
        mt_sign, mt_start, mt_end = MOOLATRIKONA[planet]
        if sign == mt_sign and mt_start <= deg_in_sign <= mt_end:
            return "Moolatrikona"
            
    # 4. Own Sign
    if sign in OWN_SIGNS.get(planet, []):
        return "Own Sign"
        
    return "General Sign"
