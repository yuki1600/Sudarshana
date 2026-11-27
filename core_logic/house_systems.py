"""
core_logic/house_systems.py
===========================
House systems, sunrise-based day/night helpers and sandhyas.

Sources (docs/SOURCES.md section 1.4): Sripati's trisection of the quadrants (Sripati Paddhati,
Bhavadhyaya); the quadrant systems' published definitions (Swiss Ephemeris doc 6.2), whose closed
forms here are checked against Swiss Ephemeris in tests/test_house_systems_swe.py; the units of
time of the Surya Siddhanta (1.11-12).  For the full list of Settings > Bhavas (Alcabitus, Axial
rotation, Polich/Page, equal-by-pada ...) use ``ephemeris.house_cusps``.
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional, Any

# Swiss Ephemeris sidereal-mode numbers (kept for backwards compatibility; the authoritative,
# complete table of the 22 ayanamsa choices is ephemeris.AYANAMSAS).
AYANAMSA_MODES = {
    "Lahiri": 1,         # SE_SIDM_LAHIRI (Traditional Lahiri)
    "Krishnamurti": 5,   # SE_SIDM_KRISHNAMURTI
    "Raman": 3,          # SE_SIDM_RAMAN
    "Yukteshwar": 7,     # SE_SIDM_YUKTESHWAR
    "True_Chitra": 27,   # SE_SIDM_TRUE_CITRA (Spica at 180 deg = "True Lahiri")
    "Fagan_Bradley": 0,  # SE_SIDM_FAGAN_BRADLEY
    "Tropical": -1,      # sayana (no ayanamsa)
    "Pushya_Paksha": 29  # SE_SIDM_TRUE_PUSHYA (delta Cancri at 106 deg, the middle of Pushya)
}

# Standard House Systems
HOUSE_SYSTEMS = {
    "Equal": "E",        # Equal 30-degree houses from Ascendant
    "Whole_Sign": "W",   # Whole sign houses (Lagna sign = House 1)
    "Sripathi": "O",     # Porphyry / Sripati Bhava Chalita
    "Placidus": "P",     # Placidus
    "Koch": "K",         # Koch
    "Campanus": "C",     # Campanus
    "Regiomontanus": "R",# Regiomontanus
    "Topocentric": "T",  # Polich-Page
    "Alcabitus": "B",
    "Axial_Rotation": "X",
}

from .utils import norm360, deg_to_dms

def compute_equal_houses(ascendant_deg: float) -> List[float]:
    """
    Computes 12 Equal house cusps starting from Ascendant.
    Each house cusp is spaced exactly 30 degrees apart.
    """
    asc = norm360(ascendant_deg)
    return [norm360(asc + i * 30.0) for i in range(12)]

def compute_whole_sign_houses(ascendant_deg: float) -> List[float]:
    """
    Computes Whole Sign house cusps.
    The cusp of each house is set to the start of the sign (0 degrees of that sign).
    """
    asc_sign = int(norm360(ascendant_deg) // 30)
    return [norm360((asc_sign + i) * 30.0) for i in range(12)]

def compute_sripathi_houses(ascendant_deg: float, mc_deg: float) -> Dict[str, Any]:
    """
    Computes traditional Vedic Sripathi (Sripati / Porphyry) Bhava Chalita house cusps
    and Bhava Sandhis (boundaries between houses).
    
    In Sripathi:
    - House 1 (Lagna) = Ascendant
    - House 10 (Madhya Lagna) = Midheaven (MC)
    - House 7 (Astha Lagna) = Ascendant + 180°
    - House 4 (Patala Lagna) = MC + 180°
    - Quadrants are trisected:
      - Arc from MC (10) to Lagna (1) is divided into 3 equal parts for houses 11 and 12.
      - Arc from Lagna (1) to IC (4) is divided into 3 equal parts for houses 2 and 3.
      - Sandhis (cusp boundaries) are the arithmetic midpoints between adjacent cusps.

    Source: Sripati Paddhati, Bhavadhyaya (the bhava sphuta by trisecting each quadrant).
    """
    asc = norm360(ascendant_deg)
    mc = norm360(mc_deg)
    ic = norm360(mc + 180.0)
    desc = norm360(asc + 180.0)
    
    cusps = [0.0] * 12
    cusps[0] = asc      # 1st house (Lagna)
    cusps[9] = mc       # 10th house (MC)
    cusps[6] = desc     # 7th house (Descendant)
    cusps[3] = ic       # 4th house (Nadir/IC)
    
    # Quadrant 4: 10th (MC) to 1st (Ascendant)
    arc_10_to_1 = norm360(asc - mc)
    step_quad4 = arc_10_to_1 / 3.0
    cusps[10] = norm360(mc + step_quad4)          # 11th house
    cusps[11] = norm360(mc + 2.0 * step_quad4)    # 12th house
    
    # Quadrant 1: 1st (Ascendant) to 4th (IC)
    arc_1_to_4 = norm360(ic - asc)
    step_quad1 = arc_1_to_4 / 3.0
    cusps[1] = norm360(asc + step_quad1)          # 2nd house
    cusps[2] = norm360(asc + 2.0 * step_quad1)    # 3rd house
    
    # Opposite quadrants are symmetrical (+ 180°)
    cusps[4] = norm360(cusps[10] + 180.0)        # 5th house
    cusps[5] = norm360(cusps[11] + 180.0)        # 6th house
    cusps[7] = norm360(cusps[1] + 180.0)         # 8th house
    cusps[8] = norm360(cusps[2] + 180.0)         # 9th house
    
    # Sandhis (midpoints between consecutive cusps)
    sandhis = [0.0] * 12
    for i in range(12):
        next_i = (i + 1) % 12
        arc = norm360(cusps[next_i] - cusps[i])
        sandhis[i] = norm360(cusps[i] + arc / 2.0)
        
    return {
        "cusps": cusps,
        "sandhis": sandhis,
        "ascendant": asc,
        "midheaven": mc
    }

# ---------------------------------------------------------------------------
# Quadrant house systems (closed forms / iteration; tropical in -> tropical out)
#
# These replace earlier hand-rolled versions that were off by 15-25 degrees.  The formulas
# below follow the published definitions (Swiss Ephemeris doc 6.2) and are verified against Swiss Ephemeris in
# tests/test_house_systems_swe.py.  Inputs must be TROPICAL (subtract the ayanamsa
# afterwards), or use ``ephemeris.house_cusps`` which does it for you.
# ---------------------------------------------------------------------------
MEAN_OBLIQUITY_DEG = 23.4392911  # J2000; true obliquity differs by < 0.005 deg this century


def _asc_from_armc(armc_deg: float, lat_deg: float, eps_deg: float) -> float:
    """Ecliptic longitude rising at sidereal-time ``armc_deg`` for pole height ``lat_deg``."""
    x, e, f = math.radians(armc_deg), math.radians(eps_deg), math.radians(lat_deg)
    return norm360(math.degrees(math.atan2(math.cos(x), -(math.sin(x) * math.cos(e) + math.tan(f) * math.sin(e)))))


def _asc1(x_deg: float, lat_deg: float, eps_deg: float) -> float:
    """Swiss-Ephemeris ``Asc1`` convention: ``_asc1(ARMC + 90)`` is the ascendant."""
    return _asc_from_armc(x_deg - 90.0, lat_deg, eps_deg)


def _armc_from_mc(mc_deg: float, eps_deg: float) -> float:
    m, e = math.radians(mc_deg), math.radians(eps_deg)
    return norm360(math.degrees(math.atan2(math.sin(m) * math.cos(e), math.cos(m))))


def _fill_quadrants(asc: float, mc: float, c11: float, c12: float, c2: float, c3: float) -> List[float]:
    cusps = [0.0] * 12
    cusps[0], cusps[9] = asc, mc
    cusps[10], cusps[11], cusps[1], cusps[2] = c11, c12, c2, c3
    cusps[6] = norm360(asc + 180.0)
    cusps[3] = norm360(mc + 180.0)
    cusps[4], cusps[5] = norm360(c11 + 180.0), norm360(c12 + 180.0)
    cusps[7], cusps[8] = norm360(c2 + 180.0), norm360(c3 + 180.0)
    return cusps


def _check_latitude(geo_lat_deg: float, eps_deg: float, system: str) -> None:
    if abs(geo_lat_deg) >= 90.0 - eps_deg:
        raise ValueError(f"{system} bhavas are undefined inside the polar circles (lat {geo_lat_deg})")


def compute_regiomontanus_houses(asc_deg: float, mc_deg: float, geo_lat_deg: float = 0.0,
                                 eps_deg: float = MEAN_OBLIQUITY_DEG) -> List[float]:
    """Regiomontanus: equator divided into 30-degree arcs, projected through the horizon poles."""
    _check_latitude(geo_lat_deg, eps_deg, "Regiomontanus")
    th = _armc_from_mc(mc_deg, eps_deg)
    t = math.tan(math.radians(geo_lat_deg))
    pole = lambda k: math.degrees(math.atan(t * math.sin(math.radians(k))))
    asc_at = lambda off, k: _asc1(th + off, pole(k), eps_deg)
    return _fill_quadrants(norm360(asc_deg), norm360(mc_deg),
                           asc_at(30, 30), asc_at(60, 60), asc_at(120, 120), asc_at(150, 150))


def compute_campanus_houses(asc_deg: float, mc_deg: float, geo_lat_deg: float = 0.0,
                            eps_deg: float = MEAN_OBLIQUITY_DEG) -> List[float]:
    """Campanus: prime vertical divided into 30-degree arcs."""
    _check_latitude(geo_lat_deg, eps_deg, "Campanus")
    th = _armc_from_mc(mc_deg, eps_deg)
    f = math.radians(geo_lat_deg)
    fh1 = math.degrees(math.asin(math.sin(f) / 2.0))
    fh2 = math.degrees(math.asin(math.sqrt(3.0) / 2.0 * math.sin(f)))
    xh1 = math.degrees(math.atan(math.sqrt(3.0) / math.cos(f)))
    xh2 = math.degrees(math.atan(1.0 / math.sqrt(3.0) / math.cos(f)))
    return _fill_quadrants(norm360(asc_deg), norm360(mc_deg),
                           _asc1(th + 90 - xh1, fh1, eps_deg),
                           _asc1(th + 90 - xh2, fh2, eps_deg),
                           _asc1(th + 90 + xh2, fh2, eps_deg),
                           _asc1(th + 90 + xh1, fh1, eps_deg))


def compute_koch_houses(asc_deg: float, mc_deg: float, geo_lat_deg: float = 0.0,
                        eps_deg: float = MEAN_OBLIQUITY_DEG) -> List[float]:
    """Koch (birthplace) houses: time-trisection of the MC's diurnal arc."""
    _check_latitude(geo_lat_deg, eps_deg, "Koch")
    th = _armc_from_mc(mc_deg, eps_deg)
    f = math.radians(geo_lat_deg)
    sina = max(-1.0, min(1.0, math.sin(math.radians(mc_deg)) * math.sin(math.radians(eps_deg)) / math.cos(f)))
    cosa = math.sqrt(1.0 - sina * sina)
    c = math.atan(math.tan(f) / cosa)
    ad3 = math.degrees(math.asin(math.sin(c) * sina)) / 3.0
    return _fill_quadrants(norm360(asc_deg), norm360(mc_deg),
                           _asc1(th + 30 - 2 * ad3, geo_lat_deg, eps_deg),
                           _asc1(th + 60 - ad3, geo_lat_deg, eps_deg),
                           _asc1(th + 120 + ad3, geo_lat_deg, eps_deg),
                           _asc1(th + 150 + 2 * ad3, geo_lat_deg, eps_deg))


def compute_placidus_houses(asc_deg: float, mc_deg: float, geo_lat_deg: float = 0.0,
                            eps_deg: float = MEAN_OBLIQUITY_DEG) -> List[float]:
    """Placidus: each cusp divides its own semi-arc in thirds (solved by fixed-point iteration)."""
    _check_latitude(geo_lat_deg, eps_deg, "Placidus")
    th = _armc_from_mc(mc_deg, eps_deg)
    e, f = math.radians(eps_deg), math.radians(geo_lat_deg)

    def cusp(frac: float, above: bool) -> float:
        # ra = th + frac*DSA (houses 11, 12) or th + 180 - frac*NSA (houses 2, 3)
        lam = math.radians(norm360(th + (frac * 90.0 if above else 180.0 - frac * 90.0)))
        for _ in range(60):
            dec = math.asin(math.sin(e) * math.sin(lam))
            x = max(-1.0, min(1.0, -math.tan(f) * math.tan(dec)))
            dsa = math.degrees(math.acos(x))
            ra = th + frac * dsa if above else th + 180.0 - frac * (180.0 - dsa)
            new = math.atan2(math.sin(math.radians(ra)), math.cos(math.radians(ra)) * math.cos(e))
            if abs(math.atan2(math.sin(new - lam), math.cos(new - lam))) < 1e-12:
                lam = new
                break
            lam = new
        return norm360(math.degrees(lam))

    return _fill_quadrants(norm360(asc_deg), norm360(mc_deg),
                           cusp(1.0 / 3.0, True), cusp(2.0 / 3.0, True),
                           cusp(2.0 / 3.0, False), cusp(1.0 / 3.0, False))

def compute_house_cusps(
    system: str,
    ascendant_deg: float,
    mc_deg: Optional[float] = None,
    geo_lat_deg: float = 0.0,
    *,
    jd_ut: Optional[float] = None,
    longitude_east: Optional[float] = None,
    cfg: Any = None,
) -> List[float]:
    """
    Unified dispatcher.

    * With ``jd_ut`` and ``longitude_east`` it calls Swiss Ephemeris (``ephemeris.house_cusps``)
      and supports every system of Settings > Bhavas (add Alcabitus, Axial_Rotation, Polich_Page,
      Equal_Pada).  Output is sidereal using ``cfg``'s ayanamsa; ``ascendant_deg`` is ignored.
    * Without them it uses the geometric implementations above; inputs/outputs are in
      whatever zodiac ``ascendant_deg``/``mc_deg`` are in, but Placidus/Koch/Campanus/
      Regiomontanus need TROPICAL asc/mc (they derive sidereal time from the MC).
    """
    key = system.upper().replace("-", "_").replace(" ", "_")
    aliases = {"WHOLE_SIGN": "RASI", "SRIPATHI": "PORPHYRY", "SRIPATI": "PORPHYRY",
               "TOPOCENTRIC": "POLICH_PAGE", "AXIAL": "AXIAL_ROTATION", "EQUAL_PADA": "EQUAL_PADA"}
    key = aliases.get(key, key)
    if jd_ut is not None and longitude_east is not None:
        from .ephemeris import house_cusps
        return house_cusps(jd_ut, geo_lat_deg, longitude_east, key, cfg)["cusps"]
    mc = mc_deg if mc_deg is not None else norm360(ascendant_deg + 270.0)
    if key == "EQUAL":
        return compute_equal_houses(ascendant_deg)
    if key == "RASI":
        return compute_whole_sign_houses(ascendant_deg)
    if key == "PORPHYRY":
        return compute_sripathi_houses(ascendant_deg, mc)["cusps"]
    if key == "PLACIDUS":
        return compute_placidus_houses(ascendant_deg, mc, geo_lat_deg)
    if key == "KOCH":
        return compute_koch_houses(ascendant_deg, mc, geo_lat_deg)
    if key == "CAMPANUS":
        return compute_campanus_houses(ascendant_deg, mc, geo_lat_deg)
    if key == "REGIOMONTANUS":
        return compute_regiomontanus_houses(ascendant_deg, mc, geo_lat_deg)
    raise ValueError(f"{system!r} needs jd_ut/longitude_east (Swiss Ephemeris) to be computed")


def compute_dinamana_ratrimana(sunrise_hours: float, sunset_hours: float) -> Dict[str, float]:
    """
    Computes Dinamana (length of day in hours & ghatis) and 
    Ratrimana (length of night in hours & ghatis).
    1 day = 60 Ghatis (1 hour = 2.5 Ghatis).
    """
    if sunset_hours >= sunrise_hours:
        dinamana_hours = sunset_hours - sunrise_hours
    else:
        dinamana_hours = (24.0 - sunrise_hours) + sunset_hours
        
    ratrimana_hours = 24.0 - dinamana_hours
    dinamana_ghatis = dinamana_hours * 2.5
    ratrimana_ghatis = ratrimana_hours * 2.5
    
    return {
        "dinamana_hours": dinamana_hours,
        "dinamana_ghatis": dinamana_ghatis,
        "ratrimana_hours": ratrimana_hours,
        "ratrimana_ghatis": ratrimana_ghatis,
    }

def compute_ishta_kala(birth_time_hours: float, sunrise_hours: float) -> Dict[str, float]:
    """
    Computes Ishta Kala (elapsed time from local sunrise to birth time)
    in hours, minutes, and ghatis/vighatis.
    """
    if birth_time_hours >= sunrise_hours:
        elapsed_hours = birth_time_hours - sunrise_hours
    else:
        elapsed_hours = (24.0 - sunrise_hours) + birth_time_hours
        
    ghatis_total = elapsed_hours * 2.5
    ghatis = int(ghatis_total)
    vighatis = (ghatis_total - ghatis) * 60.0
    
    return {
        "ishta_kala_hours": elapsed_hours,
        "ghatis": ghatis,
        "vighatis": vighatis,
        "total_ghatis": ghatis_total
    }

def compute_trikuta_sandhyas(sunrise_hours: float, sunset_hours: float) -> Dict[str, Tuple[float, float]]:
    """
    Calculates Brahma Muhurta and the 3 Vedic Sandhyas (Pratah, Madhyahna, Sayam).
    - Brahma Muhurta: 2 Muhurtas (96 min = 1.6 hrs) before sunrise.
    - Pratah Sandhya: 1 Muhurta (48 min = 0.8 hrs) before to 1 Muhurta after sunrise.
    - Madhyahna Sandhya: Centered at solar noon (midpoint between sunrise and sunset).
    - Sayam Sandhya: 1 Muhurta before to 1 Muhurta after sunset.
    """
    noon = (sunrise_hours + sunset_hours) / 2.0
    brahma_start = (sunrise_hours - 1.6) % 24.0
    brahma_end = (sunrise_hours - 0.8) % 24.0
    pratah_start = (sunrise_hours - 0.8) % 24.0
    pratah_end = (sunrise_hours + 0.8) % 24.0
    madhyahna_start = (noon - 0.8) % 24.0
    madhyahna_end = (noon + 0.8) % 24.0
    sayam_start = (sunset_hours - 0.8) % 24.0
    sayam_end = (sunset_hours + 0.8) % 24.0
    
    return {
        "brahma_muhurta": (brahma_start, brahma_end),
        "pratah_sandhya": (pratah_start, pratah_end),
        "madhyahna_sandhya": (madhyahna_start, madhyahna_end),
        "sayam_sandhya": (sayam_start, sayam_end)
    }


# --- The bhavas of Settings > Bhavas: start, middle and end of each (docs/SOURCES.md section 1.4)

def bhava_spans(ref_lon: float, house_type: int = 1, cusps: Optional[List[float]] = None,
                 cusp_in_middle: bool = True) -> List[Tuple[float, float, float]]:
    """(start, middle, end) of the 12 bhavas.  ``house_type`` (HouseTypeWanted): 0 rasi houses (BPHS 11.2:
    start = (sign of ref + i) x 30, middle = ref + 30 i); 2 equal houses from the middle of the ref's nakshatra
    pada (trunc(ref x 0.3) x 3.33 + 1.67); otherwise ``cusps`` (the 12 cusps of the house system, swe_houses):
    with ``cusp_in_middle`` (HouseCuspsInMiddle) each cusp is a middle and the ends are halfway to the next /
    previous cusp, as Sripati's sandhis are, else the cusps are starts and the middles halfway."""
    out = []
    if house_type == 0:
        s = int(ref_lon // 30.0)
        return [(((s + i) * 30.0) % 360.0, (ref_lon + 30.0 * i) % 360.0, ((s + i + 1) * 30.0) % 360.0)
                for i in range(12)]
    if house_type == 2:
        base = int(ref_lon * 0.3) * 3.3333333333333335 + 1.6666666666666667
        for i in range(12):
            x = (base + 30.0 * i) % 360.0
            out.append(((x - 15.0) % 360.0, x, (x + 15.0) % 360.0) if cusp_in_middle
                       else (x, (x + 15.0) % 360.0, (x + 30.0) % 360.0))
        return out
    c = list(cusps)
    for i in range(12):
        nxt, prv = c[(i + 1) % 12], c[(i - 1) % 12]
        if cusp_in_middle:
            out.append((((c[i] - prv) % 360.0 * 0.5 + prv) % 360.0, c[i], ((nxt - c[i]) % 360.0 * 0.5 + c[i]) % 360.0))
        else:
            out.append((c[i], ((nxt - c[i]) % 360.0 * 0.5 + c[i]) % 360.0, nxt))
    return out


def arc_contains(start: float, end: float, lon: float) -> bool:
    """``lon`` on the arc from ``start`` to ``end`` (zodiacal order)."""
    return (lon - start) % 360.0 <= (end - start) % 360.0


def house_of(lon: float, bhavas: List[Tuple[float, float, float]]) -> int:
    """The first bhava (0 = 1st) whose arc holds ``lon`` (the bhava chart's house of a point).
    Houses counted backward (from Rahu or Ketu, anti-zodiacally) run from their start down to their end."""
    back = sum((e - s) % 360.0 for s, _, e in bhavas) > 361.0     # forward, the twelve arcs add up to the circle
    return next((i for i, (s, _, e) in enumerate(bhavas) if (arc_contains(e, s, lon) if back else arc_contains(s, e, lon))), 0)
