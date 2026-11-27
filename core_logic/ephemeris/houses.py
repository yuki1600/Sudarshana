"""houses: part of ephemeris (split from one module; see __init__.py)."""
from __future__ import annotations
import math
from typing import Any, Dict, Optional
from ..utils import norm360
from .config import EphemerisConfig, HOUSE_SYSTEM_CODES, _SWE_LOCK, _delta_t, _require_swe, _sss_chart, ayanamsa_value

# ---------------------------------------------------------------------------
# Houses
# ---------------------------------------------------------------------------
def house_cusps(
    jd_ut: float,
    latitude: float,
    longitude_east: float,
    system: str = "PLACIDUS",
    cfg: Optional[EphemerisConfig] = None,
) -> Dict[str, Any]:
    """
    12 sidereal house cusps + Lagna/MC via swe_houses (Swiss Ephemeris doc 6.2).

    ``system`` is a key of HOUSE_SYSTEM_CODES.  Returns {cusps, ascendant, mc, armc, vertex, system}.
    Equal-by-pada: house 1 starts at the start of the ascendant's nakshatra pada (docs/SOURCES.md section 1.4).
    """
    cfg = cfg or EphemerisConfig()
    s = _require_swe(cfg.ephe_path)
    key = system.upper()
    if key not in HOUSE_SYSTEM_CODES:
        raise ValueError(f"unknown bhava system {system!r}; choose from {list(HOUSE_SYSTEM_CODES)}")
    letter = HOUSE_SYSTEM_CODES[key] or "E"
    if cfg.siddhanta == 1:   # SSS mode: the SSS lagna and meridian, Porphyry split, whatever the system
        with _SWE_LOCK:
            sss = _sss_chart(jd_ut, cfg, longitude_east, latitude)
        asc, mc, cusps = sss["lagna"], sss["mc"], list(sss["cusps"])
        ascmc = (0.0, 0.0, sss["sidereal_time"] * 15.0, 0.0)
        ay = 0.0
    else:
        with _SWE_LOCK:
            ay = ayanamsa_value(jd_ut, cfg, longitude_east)
            with _delta_t(s, jd_ut, cfg):
                cusps_t, ascmc = s.houses(jd_ut, latitude, longitude_east, letter.encode())
        asc = norm360(ascmc[0] - ay)
        mc = norm360(ascmc[1] - ay)
        cusps = [norm360(c - ay) for c in cusps_t[:12]]
    if key == "RASI":
        cusps = [(int(asc // 30) + i) % 12 * 30.0 for i in range(12)]
    elif key == "EQUAL_PADA":
        pada = 360.0 / 108.0
        start = math.floor(asc / pada) * pada
        cusps = [norm360(start + 30.0 * i) for i in range(12)]
    return {"system": key, "cusps": cusps, "ascendant": asc, "mc": mc,
            "armc": ascmc[2], "vertex": norm360(ascmc[3] - ay)}
