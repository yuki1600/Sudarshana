"""
Upagrahas / Shadow Planets (BPHS Ch. 25).

Two families:
  1. Sun-formula based: Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu
  2. Time-division based (from sunrise/sunset span):
       Gulika (Mandi), Yamaghantaka, Ardhaprahara, Kaala, Mrityu

References: BPHS Ch. 25; Phaladeepika; Mantreswara.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any

from src.jyotisha.base.utils import norm360, lon_to_sign_idx, sign_dms_str, rashi_name
from src.jyotisha.identity.vargas import get_nakshatra_details, navamsa_for
from src.jyotisha.base.constants import RASHI_SA


# ---------------------------------------------------------------------------
# 1. Sun-formula Upagrahas
# ---------------------------------------------------------------------------

def _sun_formula_upagrahas(sun_lon: float) -> dict[str, float]:
    """
    Compute Dhuma family from Sun's sidereal longitude.

    Dhuma      = Sun + 133°20'
    Vyatipata  = 360° − Dhuma
    Parivesha  = Vyatipata + 180°
    Indrachapa = 360° − Parivesha  (also called Kodanda)
    Upaketu    = Indrachapa + 16°40'
    """
    dhuma       = norm360(sun_lon + 133.0 + 20.0 / 60.0)
    vyatipata   = norm360(360.0 - dhuma)
    parivesha   = norm360(vyatipata + 180.0)
    indrachapa  = norm360(360.0 - parivesha)
    upaketu     = norm360(indrachapa + 16.0 + 40.0 / 60.0)
    return {
        "Dhuma":      dhuma,
        "Vyatipata":  vyatipata,
        "Parivesha":  parivesha,
        "Indrachapa": indrachapa,
        "Upaketu":    upaketu,
    }


# ---------------------------------------------------------------------------
# 2. Time-division Upagrahas (Gulika etc.)
# ---------------------------------------------------------------------------

# Each planet rules one of the 8 day-segments (from Saturday order)
# Day rulers for each weekday (0=Monday per Python, so we align to Sun=0):
# Weekday → planet ruling first hora
_WEEKDAY_TO_FIRST_HORA = {
    6: "Sun",    # Sunday
    0: "Moon",   # Monday
    1: "Mars",   # Tuesday
    2: "Mercury",# Wednesday
    3: "Jupiter",# Thursday
    4: "Venus",  # Friday
    5: "Saturn", # Saturday
}

# Chaldean order of planets
_CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# Segment index (within the 8 day-parts) for each Upagraha, by weekday
# BPHS: Gulika = 8th day-part.  Different texts vary slightly.
# Using Parashara's assignment (Gulika = Saturn's part):
#
# Gulika/Mandi: Saturn's segment in the day (8 parts of daytime; at night offset by 4)
# Yamaghantaka: Saturn's segment at night (some versions)

def _segment_lord_sequence(weekday: int) -> list[str]:
    """Return the sequence of 8 planetary lords for day-segments for given weekday."""
    first = _WEEKDAY_TO_FIRST_HORA.get(weekday, "Sun")
    start_idx = _CHALDEAN.index(first)
    return [_CHALDEAN[(start_idx + i) % 7] for i in range(8)]

def _gulika_longitude(
    sunrise_local: datetime,
    sunset_local: datetime,
    weekday: int,
    is_daytime: bool = True,
) -> float:
    """
    Calculate Gulika (Mandi) longitude.

    The day is divided into 8 equal parts.
    Saturn rules one of these segments depending on weekday.
    Gulika's longitude = start of Saturn's segment mapped to the zodiac
    (using the Sun's longitude at the midpoint of that segment is one method;
    another is simply: segment_start / total_day * 360 + Asc at that time).

    Simplified BPHS approach: Express Gulika as a fraction of the day
    converted to a "house position" approximation.
    We return the Sun's approximate longitude at that moment using linear interpolation.
    """
    day_lords = _segment_lord_sequence(weekday)
    # Find Saturn's segment (0-indexed)
    try:
        sat_seg = day_lords.index("Saturn")
    except ValueError:
        sat_seg = 0

    day_secs = (sunset_local - sunrise_local).total_seconds()
    if day_secs <= 0:
        day_secs = 43200  # 12h fallback

    seg_duration = day_secs / 8.0
    gulika_seconds_from_sunrise = sat_seg * seg_duration + seg_duration / 2.0
    return gulika_seconds_from_sunrise  # Return seconds from sunrise for caller to use


def _time_based_upagraha_lon(sun_lon_at_sr: float, fraction_of_day: float) -> float:
    """
    Approximate upagraha longitude: Sun's position advances ~1°/day.
    Gulika's position ≈ Sun's position + (fraction_of_day × 360°/365.25)
    is a rough approximation. Classical texts use Ascendant at that time,
    but without recomputing houses we use Sun-fraction method.
    """
    daily_sun_motion = 360.0 / 365.25  # ~0.9856°/day
    return norm360(sun_lon_at_sr + fraction_of_day * daily_sun_motion)


# Gulika segment indices per weekday (0-indexed within 8 day parts), from BPHS
_GULIKA_DAY_SEG = {6: 6, 0: 4, 1: 2, 2: 0, 3: 5, 4: 3, 5: 1}  # Sun=6,Mon=0,...
_YAMAGHANTAKA_DAY_SEG = {6: 2, 0: 0, 1: 5, 2: 3, 3: 1, 4: 6, 5: 4}
_ARDHAPRAHARA_DAY_SEG = {6: 0, 0: 5, 1: 3, 2: 1, 3: 6, 4: 4, 5: 2}
_KAALA_DAY_SEG = {6: 4, 0: 2, 1: 0, 2: 5, 3: 3, 4: 1, 5: 6}
_MRITYU_DAY_SEG = {6: 3, 0: 1, 1: 6, 2: 4, 3: 2, 4: 0, 5: 5}

def _seg_to_lon(seg_idx: int, total_secs: float, sun_lon_sr: float) -> float:
    """Convert segment index to approximate longitude."""
    fraction = (seg_idx * (total_secs / 8.0) + (total_secs / 16.0)) / 86400.0
    return _time_based_upagraha_lon(sun_lon_sr, fraction)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _make_row(name: str, lon: float, family: str) -> dict[str, Any]:
    sign_idx = lon_to_sign_idx(lon)
    nak = get_nakshatra_details(lon)
    nav_idx, _ = navamsa_for(lon)
    return {
        "Upagraha": name,
        "Family": family,
        "Longitude (Sign DMS)": sign_dms_str(lon),
        "Longitude (Dec)": round(lon, 4),
        "Sign": rashi_name(lon),
        "Nakshatra": nak["nakshatra"],
        "Pada": nak["pada"],
        "Navamsha": RASHI_SA[nav_idx],
    }


def compute_upagrahas(
    sun_lon: float,
    sunrise_local: datetime,
    sunset_local: datetime,
    local_dt: datetime,
) -> list[dict[str, Any]]:
    """
    Compute all Upagrahas.

    Args:
        sun_lon: Sun's sidereal longitude at birth.
        sunrise_local: Sunrise datetime (local).
        sunset_local: Sunset datetime (local).
        local_dt: Birth datetime (local).

    Returns:
        List of upagraha row dicts.
    """
    rows = []

    # Family 1: Sun-formula
    sun_family = _sun_formula_upagrahas(sun_lon)
    for name, lon in sun_family.items():
        rows.append(_make_row(name, lon, "Sun-formula"))

    # Family 2: Time-division
    weekday = sunrise_local.weekday()  # 0=Monday
    day_secs = (sunset_local - sunrise_local).total_seconds()
    if day_secs <= 0:
        day_secs = 43200

    # Sun's longitude at sunrise (approximate — we use birth sun_lon as proxy)
    sun_lon_sr = sun_lon  # good enough for intraday

    time_based = [
        ("Gulika (Mandi)", _GULIKA_DAY_SEG),
        ("Yamaghantaka",   _YAMAGHANTAKA_DAY_SEG),
        ("Ardhaprahara",   _ARDHAPRAHARA_DAY_SEG),
        ("Kaala",          _KAALA_DAY_SEG),
        ("Mrityu Sahama",  _MRITYU_DAY_SEG),
    ]
    for name, seg_map in time_based:
        seg = seg_map.get(weekday, 0)
        lon = _seg_to_lon(seg, day_secs, sun_lon_sr)
        rows.append(_make_row(name, lon, "Time-division"))

    return rows
