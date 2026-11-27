"""lagnas: part of natal_chart (split from one module; see __init__.py)."""
from __future__ import annotations
from .signs import norm360

# ---------------------------------------------------------------------------
# Special Lagnas: BPHS 5.2-8 (bhava lagna a sign per 5 ghatis, hora lagna per 2.5 ghatis, ghati lagna per ghati,
# from the Sun at sunrise)
# ---------------------------------------------------------------------------

def compute_hora_lagna(sunrise_hours: float, birth_hours: float, sun_lon: float) -> float:
    """
    Hora Lagna (HL):
    Moves 1 sign (30°) every 1 Hora (1 hour / 2.5 ghatis) from Sun at sunrise.
    """
    elapsed = (birth_hours - sunrise_hours) % 24.0
    return norm360(sun_lon + (elapsed * 30.0))

def compute_ghati_lagna(sunrise_hours: float, birth_hours: float, sun_lon: float) -> float:
    """
    Ghati Lagna (GL):
    Moves 1 sign (30°) every 1 Ghati (24 minutes = 0.4 hours) from Sun at sunrise.
    1 hour = 2.5 Ghatis => 2.5 * 30° = 75° per hour.
    """
    elapsed = (birth_hours - sunrise_hours) % 24.0
    return norm360(sun_lon + (elapsed * 75.0))

def compute_bhava_lagna(sunrise_hours: float, birth_hours: float, sun_lon: float) -> float:
    """
    Bhava Lagna (BL):
    Moves 1 sign (30°) every 2 hours (120 minutes) from Sun at sunrise.
    """
    elapsed = (birth_hours - sunrise_hours) % 24.0
    return norm360(sun_lon + (elapsed * 15.0))
