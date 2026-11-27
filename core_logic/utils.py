"""
core_logic/utils.py
===================
Shared Mathematical Utilities for the Sudarshana Core Calculation Engines.

Centralizes common helper functions that were previously duplicated across
up to 6 different modules (norm360 appeared in natal_chart, house_systems,
dashas, transits, tajika, and shadbala). This module has ZERO dependencies
on other core_logic modules to prevent circular imports.
"""

from __future__ import annotations
from typing import Tuple


def norm360(deg: float) -> float:
    """Normalize angle to [0, 360) degrees."""
    d = deg % 360.0
    return d + 360.0 if d < 0 else d


def deg_to_dms(deg: float) -> Tuple[int, int, float]:
    """Convert decimal degrees to (degrees, minutes, seconds): seconds rounded to 0.01, with the carry into minutes
    and degrees, as printed values are split."""
    deg = norm360(deg)
    d = int(deg)
    rem = (deg - d) * 60.0
    m = int(rem)
    s = round((rem - m) * 60.0, 2)
    if s >= 60.0:
        s = 0.0
        m += 1
    if m >= 60:
        m = 0
        d = (d + 1) % 360
    return d, m, s


def get_house_of_sign(lagna_sign: int, target_sign: int) -> int:
    """Returns the 1-based house number of target_sign counted from lagna_sign, the count inclusive as the
    texts count houses (the same sign is the 1st)."""
    return ((target_sign - lagna_sign) % 12) + 1


def angular_distance(lon1: float, lon2: float) -> float:
    """
    Returns the shortest angular distance between two longitudes (0 to 180°).
    Always positive.
    """
    sep = abs(norm360(lon1 - lon2))
    return sep if sep <= 180.0 else 360.0 - sep


# --- Arc arithmetic shared by the engines

def norm360_diff(a: float, b: float) -> float:
    """a - b in [0, 360): the arc from b forward to a."""
    return (a - b) % 360.0


def norm360_sum(a: float, b: float) -> float:
    """a + b in [0, 360)."""
    return (a + b) % 360.0


def norm360_mid(a: float, b: float, c: float = 0.0) -> float:
    """The midpoint of the arc from b forward to a, plus c, in [0, 360)."""
    return (((a - b) % 360.0) * 0.5 + b + c) % 360.0


def fold180(a: float, b: float = 0.0) -> float:
    """|a - b| folded to [0, 180]: the shorter arc between two longitudes."""
    d = abs(a - b) % 360.0
    return 360.0 - d if d > 180.0 else d


def mod_one_based(a: int, n: int) -> int:
    """a mod n in 1 .. n (a count that runs 1 .. n, as houses and nakshatras are counted)."""
    return a % n or n


def nakshatra_to_28(nak: int, pada: int) -> int:
    """27-nakshatra index (0 Ashwini) to the 28-star wheel with Abhijit, which is the last quarter of Uttarashadha
    (``pada`` 0-based 3; PVR ch. 25, docs/SOURCES.md section 2)."""
    return nak + 1 if nak > 20 or (nak == 20 and pada == 3) else nak


def split_sign_dms(lon: float) -> Tuple[int, int, int, float]:
    """Sign, degrees, minutes, seconds of a longitude; seconds within 1e-4 of 60 carry into the minutes (and 60
    minutes into the degrees), seconds below 1e-4 become 0."""
    lon %= 360.0
    s = int(lon / 30.0)
    x = lon - s * 30.0
    d = int(x)
    m = int((x - d) * 60.0)
    sec = (x - d - m * 0.016666666666666666) * 3600.0
    if 60.0 - sec < 1e-4:
        sec, m = 0.0, m + 1
        if m == 60:
            m, d = 0, d + 1
    if sec < 1e-4:
        sec = 0.0
    return s, d, m, sec


def from_sign_dms(sign: int, d: int, m: int, sec: float) -> float:
    """Longitude from sign, degrees, minutes and seconds (sign 0 for a plain angle)."""
    return sign * 30.0 + d + m / 60.0 + sec / 3600.0
