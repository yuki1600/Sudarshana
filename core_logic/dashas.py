"""
core_logic/dashas.py
====================
Modularized Calculation Engine for Planetary and Rasi Dasa Systems.
Sources (docs/SOURCES.md section 9): Vimshottari BPHS 46.12-16 and its antardasas 51.1-2; Yogini BPHS 46.195-199;
Chara BPHS 46.158-167; Narayana JUS 1.1 as PVR ch. 18 teaches it; the year lengths section 9.1.
"""

from __future__ import annotations
import math
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Tuple, Optional, Any
from .natal_chart import RASI_NAMES_EN, RASI_LORDS

# ---------------------------------------------------------------------------
# Vimshottari Dasa Constants & Configuration
# ---------------------------------------------------------------------------

VIMSHOTTARI_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

VIMSHOTTARI_YEARS = {
    "Ketu": 7.0,
    "Venus": 20.0,
    "Sun": 6.0,
    "Moon": 10.0,
    "Mars": 7.0,
    "Rahu": 18.0,
    "Jupiter": 16.0,
    "Saturn": 19.0,
    "Mercury": 17.0
}

TOTAL_VIMSHOTTARI_YEARS = 120.0
DAYS_PER_YEAR = 365.2425  # Modern Gregorian calendar standard

YEAR_STANDARDS = {
    "SAVANA": 360.0,              # 360 solar days
    "SIDEREAL_SOLAR": 365.256364, # mean sidereal solar year (Settings > Dasa years, definition 6)
    "TROPICAL_SOLAR": 365.24219,  # Sayana tropical solar year
    "GREGORIAN": 365.2425,        # Modern calendar standard
    "TITHI_YEAR": 354.36708       # 360 tithis = 12 mean synodic months (SS 14.12-13, lunar time)
}

# Nakshatra offset applied to the seed longitude.  The fraction left always comes from the
# seed itself (utpanna/kshema/adhana keep the Moon's fraction; PVR 16.4).
# Seeds other than the three Moon-derived taras take the body's own longitude, offset 0:
# pass e.g. Gulika's or a planet's longitude (see ephemeris.vimsottari_seed_longitude).
DASA_START_SEEDS = {
    "MOON": 0,       # Standard Janma Nakshatra
    "LAGNA": 0,      # Lagna Nakshatra
    "UTPANNA": 4,    # 5th nakshatra from Moon (offset +4)
    "KSHEMA": 3,     # 4th nakshatra from Moon (offset +3)
    "ADHANA": 7      # 8th nakshatra from Moon (offset +7)
}

from .utils import norm360

def compute_vimshottari_balance(
    seed_lon: float,
    seed_type: str = "MOON"
) -> Dict[str, Any]:
    """
    Computes the starting Mahadasa lord and balance of dasa at birth.
    Each nakshatra spans 13°20' (13.33333°).
    Balance fraction = (remaining degrees in nakshatra) / (13.33333°).
    Supports alternative starting seeds (Lagna, Utpanna, Kshema, Adhana).
    """
    lon = norm360(seed_lon)
    nak_span = 360.0 / 27.0
    raw_nak_idx = int(lon // nak_span)
    
    seed_offset = DASA_START_SEEDS.get(seed_type.upper(), 0)
    nak_idx = (raw_nak_idx + seed_offset) % 27
    
    deg_in_nak = lon - (raw_nak_idx * nak_span)
    frac_elapsed = deg_in_nak / nak_span
    frac_remaining = 1.0 - frac_elapsed
    
    lord_idx = nak_idx % 9
    start_lord = VIMSHOTTARI_LORDS[lord_idx]
    full_years = VIMSHOTTARI_YEARS[start_lord]
    balance_years = full_years * frac_remaining
    
    # Convert balance years to years, months, days
    y = int(balance_years)
    rem_m = (balance_years - y) * 12.0
    m = int(rem_m)
    d = round((rem_m - m) * 30.4375, 1)
    
    return {
        "start_lord": start_lord,
        "lord_index": lord_idx,
        "nakshatra_index": nak_idx,
        "seed_type": seed_type,
        "balance_years_decimal": balance_years,
        "balance_ymd": (y, m, d),
        "fraction_remaining": frac_remaining
    }

_VIM_LEVELS = [("Mahadasa", "antardasas"), ("Antardasa", "pratyantardasas"),
               ("Pratyantardasa", "sookshma_dasas"), ("Sookshma", "prana_dasas"), ("Prana", None)]
_VIM_UNITS = [("duration_years", None), ("duration_years", None), ("duration_days", 1.0),
              ("duration_hours", 24.0), ("duration_minutes", 1440.0)]


def _vimshottari_children(lord_i: int, start_y: float, years: float) -> List[Tuple[int, float, float]]:
    """The 9 sub-periods (lord index, start, length in years) of a period ruled by lord_i."""
    out, t = [], start_y
    for k in range(9):
        li = (lord_i + k) % 9
        d = years * VIMSHOTTARI_YEARS[VIMSHOTTARI_LORDS[li]] / TOTAL_VIMSHOTTARI_YEARS
        out.append((li, t, d))
        t += d
    return out


def _vimshottari_setup(seed_lon, birth_dt, year_type, days_per_year, seed_type, tribhagi, to_date):
    eff_dpy = days_per_year if days_per_year is not None else YEAR_STANDARDS.get(year_type.upper(), DAYS_PER_YEAR)
    date = to_date or (lambda y: birth_dt + timedelta(days=y * eff_dpy))
    bal = compute_vimshottari_balance(seed_lon, seed_type=seed_type)
    scale = 1.0 / 3.0 if tribhagi else 1.0
    # The first mahadasa began before birth; its elapsed part is (1 - fraction left).
    first_start = -(1.0 - bal["fraction_remaining"]) * VIMSHOTTARI_YEARS[bal["start_lord"]] * scale
    if hasattr(date, "rebased"):   # the Moon year (ephemeris.dasa_year_mapper) counts from the dasa's start
        date = date.rebased(first_start)
    return date, bal, scale, first_start


def _vimshottari_entry(level, lord_i, start_y, years, date):
    start, end = date(start_y), date(start_y + years)
    key, mult = _VIM_UNITS[level]
    value = years if mult is None else round((end - start).total_seconds() / 86400.0 * mult, 2)
    return {"level": _VIM_LEVELS[level][0], "lord": VIMSHOTTARI_LORDS[lord_i],
            "start": start.isoformat(), "end": end.isoformat(), key: value}, start, end


def compute_vimshottari_tree(
    moon_lon: float,
    birth_dt: datetime,
    max_cycles: int = 1,
    include_antardasa: bool = True,
    subperiod_depth: int = 2,
    year_type: str = "GREGORIAN",
    days_per_year: Optional[float] = None,
    seed_type: str = "MOON",
    tribhagi: bool = False,
    to_date: Optional[Callable[[float], datetime]] = None
) -> List[Dict[str, Any]]:
    """
    Generates the complete Vimshottari Dasa timeline with multi-level subperiod tree:
    - Level 1: Mahadasa (MD)
    - Level 2: Antardasa (AD)
    - Level 3: Pratyantardasa (PD)
    - Level 4: Sookshma Dasa (SD)
    - Level 5: Prana Dasa (PAD)
    Supports configurable year lengths (SAVANA 360d, SIDEREAL_SOLAR, TROPICAL_SOLAR)
    and starting seed points (MOON, LAGNA, UTPANNA, KSHEMA, ADHANA, or any longitude).

    Every period carries its true dates: the first mahadasa starts
    before birth (its ``balance_years`` is the part left at birth) and its antardasas keep
    their full proportions.
    ``tribhagi``: Tribhagi variation: three 40-year cycles,
    each dasa one third of its normal length.
    ``to_date``: maps years since birth to a datetime; overrides the fixed year length and
    allows the nonlinear solar-longitude / tithi years (see ephemeris.dasa_year_mapper).
    """
    date, bal, scale, t = _vimshottari_setup(moon_lon, birth_dt, year_type, days_per_year,
                                             seed_type, tribhagi, to_date)
    depth = subperiod_depth if include_antardasa else 1

    def node(level, lord_i, start_y, years):
        entry, _, _ = _vimshottari_entry(level, lord_i, start_y, years, date)
        if level + 1 < depth:
            entry[_VIM_LEVELS[level][1]] = [node(level + 1, li, s0, d)
                                           for li, s0, d in _vimshottari_children(lord_i, start_y, years)]
        return entry

    timeline = []
    for step in range(9 * (3 if tribhagi else 1) * max_cycles):
        lord_i = (bal["lord_index"] + step) % 9
        years = VIMSHOTTARI_YEARS[VIMSHOTTARI_LORDS[lord_i]] * scale
        md = node(0, lord_i, t, years)
        if step == 0:
            md["balance_years"] = bal["balance_years_decimal"] * scale
        timeline.append(md)
        t += years
    return timeline


def get_active_vimshottari_subperiod(
    moon_lon: float,
    birth_dt: datetime,
    target_dt: datetime,
    seed_type: str = "MOON",
    year_type: str = "GREGORIAN",
    days_per_year: Optional[float] = None,
    tribhagi: bool = False,
    to_date: Optional[Callable[[float], datetime]] = None
) -> Dict[str, Any]:
    """
    The 5-level Vimshottari hierarchy (MD, AD, PD, SD, PAD) running at ``target_dt``
    ("Locate an event").  Same options as the tree.
    """
    if target_dt < birth_dt:
        target_dt = birth_dt
    date, bal, scale, t = _vimshottari_setup(moon_lon, birth_dt, year_type, days_per_year,
                                             seed_type, tribhagi, to_date)
    # Mahadasa: walk forward from the first one (cycles repeat every 120 years)
    lord_i, years = bal["lord_index"], VIMSHOTTARI_YEARS[bal["start_lord"]] * scale
    while date(t + years) <= target_dt:
        t += years
        lord_i = (lord_i + 1) % 9
        years = VIMSHOTTARI_YEARS[VIMSHOTTARI_LORDS[lord_i]] * scale
    path = [_vimshottari_entry(0, lord_i, t, years, date)[0]]
    for level in range(1, 5):
        kids = _vimshottari_children(lord_i, t, years)
        for li, s0, d in kids:
            if date(s0 + d) > target_dt or (li, s0, d) == kids[-1]:
                lord_i, t, years = li, s0, d
                break
        path.append(_vimshottari_entry(level, lord_i, t, years, date)[0])
    for e in path[:2]:
        e["duration_years"] = round(e["duration_years"], 4)
    keys = ["mahadasha", "antardasha", "pratyantardasha", "sookshma", "prana"]
    out = {"target_datetime": target_dt.isoformat()}
    for k, e in zip(keys, path):
        out[k] = {f: v for f, v in e.items() if f != "level"}
    out["hierarchy_string"] = " - ".join(e["lord"] for e in path)
    return out


def locate_dasa_period(timeline: List[Dict[str, Any]], target_dt: datetime) -> List[Dict[str, Any]]:
    """
    "Locate an event" for any dasa timeline of this package: the chain of periods (outermost
    first) whose [start, end) contains ``target_dt``.  Sub-period lists are found as any
    list of dicts with ``start``/``end`` keys.  Entries are returned without their children.
    """
    path: List[Dict[str, Any]] = []
    level = timeline
    while level:
        hit = next((p for p in level if datetime.fromisoformat(p["start"]) <= target_dt
                    < datetime.fromisoformat(p["end"])), None)
        if hit is None:
            break
        children = [v for v in hit.values() if isinstance(v, list) and v and isinstance(v[0], dict)
                    and "start" in v[0]]
        path.append({k: v for k, v in hit.items() if not (isinstance(v, list) and v and isinstance(v[0], dict))})
        level = children[0] if children else None
    return path


def shift_dasa_timeline(timeline: List[Dict[str, Any]], delta: timedelta) -> List[Dict[str, Any]]:
    """"Shift dasa dates" (rectification aid): a copy of any timeline with every start/end moved by delta."""
    def shift(p):
        q = {}
        for k, v in p.items():
            if k in ("start", "end") and isinstance(v, str):
                q[k] = (datetime.fromisoformat(v) + delta).isoformat()
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                q[k] = [shift(c) for c in v]
            else:
                q[k] = v
        return q
    return [shift(p) for p in timeline]


def compare_vimshottari_seeds(
    seed_longitudes: Dict[str, float],
    planet_longitudes: Dict[str, float],
    pada_houses: bool = False
) -> Dict[str, List[str]]:
    """
    Vimsottari seed strength comparison: the planets
    in quadrants (houses 1, 4, 7, 10) from each candidate seed.  Houses are signs, or with
    ``pada_houses`` blocks of nine nakshatra padas starting at the seed's pada.
    """
    pada = 360.0 / 108.0
    out = {}
    for seed, s_lon in seed_longitudes.items():
        hits = []
        for p, lon in planet_longitudes.items():
            if pada_houses:
                house = int(((lon - math.floor(norm360(s_lon) / pada) * pada) % 360.0) // 30.0) + 1
            else:
                house = (int(norm360(lon) // 30) - int(norm360(s_lon) // 30)) % 12 + 1
            if house in (1, 4, 7, 10):
                hits.append(p)
        out[seed] = hits
    return out

# ---------------------------------------------------------------------------
# Yogini Dasa Engine (36-year cycle)
# ---------------------------------------------------------------------------

YOGINI_NAMES = [
    "Mangala", "Pingala", "Dhanya", "Bhramari",
    "Bhadrika", "Ulka", "Siddha", "Sankata"
]

YOGINI_LORDS = [
    "Moon", "Sun", "Jupiter", "Mars",
    "Mercury", "Saturn", "Venus", "Rahu"
]

YOGINI_YEARS = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0] # Sum = 36 years

def compute_yogini_dasa(moon_lon: float, birth_dt: datetime) -> List[Dict[str, Any]]:
    """
    Computes 36-year Yogini Dasa.
    Formula: (Nakshatra number + 3) mod 8 = Starting Yogini.
    Balance calculated from remaining fraction in nakshatra.
    """
    lon = norm360(moon_lon)
    nak_span = 360.0 / 27.0
    nak_idx = int(lon // nak_span) + 1  # 1-indexed (1 to 27)
    
    frac_remaining = 1.0 - ((lon % nak_span) / nak_span)
    
    start_yogini_idx = (nak_idx + 3) % 8
    if start_yogini_idx == 0:
        start_yogini_idx = 8
    start_yogini_idx -= 1  # 0-indexed
    
    timeline = []
    current_dt = birth_dt
    for i in range(8):
        idx = (start_yogini_idx + i) % 8
        name = YOGINI_NAMES[idx]
        lord = YOGINI_LORDS[idx]
        full_y = YOGINI_YEARS[idx]
        dur_y = full_y * frac_remaining if i == 0 else full_y
        
        end_dt = current_dt + timedelta(days=dur_y * DAYS_PER_YEAR)
        timeline.append({
            "yogini": name,
            "lord": lord,
            "start": current_dt.isoformat(),
            "end": end_dt.isoformat(),
            "duration_years": dur_y
        })
        current_dt = end_dt
    return timeline

# ---------------------------------------------------------------------------
# Narayana Dasa Progression Engine
# Source: JUS 1.1 (the rasi dasas), as PVR ch. 18 teaches Narayana dasa
# ---------------------------------------------------------------------------

DUAL_RULERSHIP = {
    7: ("Mars", "Ketu"),      # Scorpio (Vrischika)
    10: ("Saturn", "Rahu"),   # Aquarius (Kumbha)
}

def compute_narayana_sign_order(start_sign: int) -> List[int]:
    """
    Determines Narayana Dasa sign progression:
    - Odd signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius): progression is direct (forward).
    - Even signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces): progression is indirect (backward).
    Exceptions for Aquarius and Taurus apply per Jaimini Sutras.
    """
    is_odd = (start_sign % 2 == 0) # 0=Aries (odd)
    if is_odd:
        return [(start_sign + i) % 12 for i in range(12)]
    else:
        return [(start_sign - i) % 12 for i in range(12)]

def compute_narayana_dasa_years(sign_idx: int, lord_sign_idx: int) -> int:
    """
    Computes duration of Narayana Dasa for a sign:
    Count from sign to its lord. Subtract 1 if progression is direct.
    If lord is in own sign, period is 12 years.
    """
    if sign_idx == lord_sign_idx:
        return 12
    count = (lord_sign_idx - sign_idx) % 12
    if count == 0:
        count = 12
    return count

def compute_narayana_dasa_timeline(
    lagna_sign: int,
    planetary_signs: Dict[str, int],
    birth_dt: datetime,
    max_cycles: int = 1
) -> List[Dict[str, Any]]:
    """
    Computes complete dated timeline for Narayana Dasa (Jaimini Rasi progression; JUS 1.1, PVR ch. 18).
    """
    sign_order = compute_narayana_sign_order(lagna_sign)
    timeline = []
    current_dt = birth_dt
    
    for cycle in range(max_cycles):
        for s_idx in sign_order:
            lord = RASI_LORDS[s_idx]
            lord_sign = planetary_signs.get(lord, s_idx)
            years = compute_narayana_dasa_years(s_idx, lord_sign)
            end_dt = current_dt + timedelta(days=years * DAYS_PER_YEAR)
            timeline.append({
                "cycle": cycle + 1,
                "sign_index": s_idx,
                "sign_name": RASI_NAMES_EN[s_idx],
                "lord": lord,
                "duration_years": years,
                "start": current_dt.isoformat(),
                "end": end_dt.isoformat()
            })
            current_dt = end_dt
            
    return timeline

_CHARA_DIRECT_SIGNS = {0, 1, 2, 6, 7, 8}


def chara_sign_years(sign: int, planetary_signs: Dict[str, int]) -> int:
    """Chara-dasa length of ``sign``: count to its lord (forward from direct signs, backward from
    indirect ones), minus one; a lord in its own sign gives 12 (BPHS Ch. 46)."""
    lord = RASI_LORDS[sign]
    lord_sign = planetary_signs.get(lord, sign)
    if sign == lord_sign:
        return 12
    if sign in _CHARA_DIRECT_SIGNS:
        count = ((lord_sign - sign) % 12) + 1
    else:
        count = ((sign - lord_sign) % 12) + 1
    years = count - 1
    return years if years > 0 else 12


def compute_chara_dasa(
    lagna_sign: int,
    planetary_signs: Dict[str, int],
    birth_dt: datetime,
    max_cycles: int = 1
) -> List[Dict[str, Any]]:
    """
    Computes complete dated timeline for Jaimini Chara Dasa.
    - Starting sign is Lagna sign.
    - Direct signs (Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius): forward progression.
    - Indirect signs (Cancer, Leo, Virgo, Capricorn, Aquarius, Pisces): backward progression.
    - Dasa duration: count from sign to its lord; if lord in own sign, 12 years; else count - 1.
    """
    direct_signs = {0, 1, 2, 6, 7, 8}
    is_direct = (lagna_sign in direct_signs)
    
    if is_direct:
        sign_order = [(lagna_sign + i) % 12 for i in range(12)]
    else:
        sign_order = [(lagna_sign - i) % 12 for i in range(12)]
        
    timeline = []
    current_dt = birth_dt
    for cycle in range(max_cycles):
        for s_idx in sign_order:
            lord = RASI_LORDS[s_idx]
            years = chara_sign_years(s_idx, planetary_signs)
            end_dt = current_dt + timedelta(days=years * DAYS_PER_YEAR)
            timeline.append({
                "cycle": cycle + 1,
                "sign_index": s_idx,
                "sign_name": RASI_NAMES_EN[s_idx],
                "lord": lord,
                "duration_years": years,
                "start": current_dt.isoformat(),
                "end": end_dt.isoformat()
            })
            current_dt = end_dt
            
    return timeline
