"""common: part of shadbala (split from one module; see __init__.py)."""
from __future__ import annotations
from ..natal_chart import RASI_LORDS

SIGN_RULERS = RASI_LORDS

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Deep Debilitation Points (Degrees)
DEEP_DEBILITATION_DEGS = {
    "Sun": 190.0,       # Libra 10°
    "Moon": 213.0,      # Scorpio 3°
    "Mars": 118.0,      # Cancer 28°
    "Mercury": 345.0,   # Pisces 15°
    "Jupiter": 275.0,   # Capricorn 5°
    "Venus": 177.0,     # Virgo 27°
    "Saturn": 20.0      # Aries 20°
}

# Dig Bala Zero-Strength Points (Opposite to maximum strength angle)
# Max strength: Sun/Mars in 10th (MC), Jup/Merc in 1st (Lagna), Moon/Ven in 4th (IC), Sat in 7th (Desc)
DIG_BALA_ZERO_OFFSETS = {
    "Sun": 270.0,      # 4th house cusp from Lagna (IC)
    "Mars": 270.0,
    "Jupiter": 180.0,  # 7th house cusp from Lagna (Descendant)
    "Mercury": 180.0,
    "Moon": 90.0,      # 10th house cusp from Lagna (MC)
    "Venus": 90.0,
    "Saturn": 0.0      # 1st house cusp (Lagna)
}

# Naisargika Bala (Natural Fixed Strength in Virupas)
NAISARGIKA_BALA = {
    "Sun": 60.0,
    "Moon": 51.43,
    "Venus": 42.86,
    "Jupiter": 34.29,
    "Mercury": 25.71,
    "Mars": 17.14,
    "Saturn": 8.57
}

# Minimum Required Shadbala Thresholds (in Virupas)
SHADBALA_REQUIREMENTS = {
    "Sun": 390.0,
    "Moon": 360.0,
    "Mars": 300.0,
    "Mercury": 420.0,
    "Jupiter": 390.0,
    "Venus": 330.0,
    "Saturn": 300.0
}
