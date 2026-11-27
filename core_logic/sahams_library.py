"""
core_logic/sahams_library.py
============================
Complete Classical Tajika Sahams (Sensitive Arabic / Tajika Points) Library.
Formulas of the 36 sahamas of the main list: PVR 28.8 (the sahama table); the method is Tajika Neelakanthi's (VAR ch. VII art. 64 on).

Core Mechanics:
For diurnal births (Day):   Saham = (A - B) + C   (C is usually the lagna)
For nocturnal births (Night): Saham = (B - A) + C
Tajika Condition:
If C is not within the arc from B to A moving forward, an adjustment of 30° (1 sign) is added.

The reference list has 36 sahamas; this library defines 53, of which 17 are from other Tajika texts
(docs/SOURCES.md section 13).
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional, Any

from .natal_chart import norm360, RASI_NAMES_EN

# Saham definitions: (Name, A, B, C, reverses_at_night, meaning)  ->  A - B + C (day).
# The 36 sahamas of the main list follow the sahama table of PVR 28.8; the remaining 17 come from other texts
# and are reported with ``in_main_list: False``.
SAHAM_DEFINITIONS = [
    ("Punya (Fortune / Merit)", "Moon", "Sun", "Lagna", True, "General fortune, divine grace, righteous credit"),
    ("Vidya (Education / Knowledge)", "Sun", "Moon", "Lagna", True, "Academic learning, wisdom, comprehension"),
    ("Yashas (Fame / Renown)", "Jupiter", "Punya", "Lagna", True, "Public reputation, social glory, acclaim"),
    ("Mitra (Friendship)", "Jupiter", "Punya", "Venus", True, "True allies, helpful companions, alliances"),
    ("Mahatmya (Greatness)", "Punya", "Mars", "Lagna", True, "High standing, nobility, spiritual stature"),
    ("Asha (Desire / Hope)", "Saturn", "Mars", "Lagna", True, "Fulfillment of heartfelt ambitions and dreams"),
    ("Samartha (Enterprise / Capability)", "Mars", "Lord1", "Lagna", True, "Competence to accomplish difficult tasks"),
    ("Bhratri (Brothers / Siblings)", "Jupiter", "Saturn", "Lagna", False, "Co-borns, siblings, fraternal support"),
    ("Gaurava (Respect / Status)", "Jupiter", "Moon", "Sun", True, "Dignity, honor, societal deference"),
    ("Pitri (Father)", "Saturn", "Sun", "Lagna", True, "Paternal longevity, relationship, inheritance"),
    ("Raja (Rulership / Royalty)", "Saturn", "Sun", "Lagna", True, "Executive authority, political power"),
    ("Matri (Mother)", "Moon", "Venus", "Lagna", True, "Maternal affection, nourishment, lineage"),
    ("Putra (Children / Progeny)", "Jupiter", "Moon", "Lagna", True, "Birth, joy, and success of progeny"),
    ("Jeeva (Life / Vitality)", "Saturn", "Jupiter", "Lagna", True, "Life breath, physical longevity, survival"),
    ("Karma (Action / Profession)", "Mars", "Mercury", "Lagna", True, "Vocational success, enterprise, career deeds"),
    ("Roga (Illness / Disease)", "Lagna", "Moon", "Lagna", False, "Bodily ailments, bodily weakness, afflictions"),
    ("Kali (Strife / Conflict)", "Jupiter", "Mars", "Lagna", True, "Great misfortune, domestic discord, litigation"),
    ("Sastra (Sciences)", "Jupiter", "Saturn", "Mercury", True, "Sciences, scriptures, learning of sastras"),
    ("Bandhu (Relatives / Kin)", "Mercury", "Moon", "Lagna", True, "Maternal relatives, cousins, community"),
    ("Mrityu (Death / Mortality)", "H8", "Moon", "Lagna", False, "Vulnerability, critical lifespan transitions"),
    ("Paradesa (Foreign Travel)", "H9", "Lord9", "Lagna", False, "Long journeys, overseas living, migration"),
    ("Artha (Wealth / Money)", "H2", "Lord2", "Lagna", False, "Financial liquidity, liquid assets, treasures"),
    ("Paradara (Adultery)", "Venus", "Sun", "Lagna", True, "Illicit relationships"),
    ("Vanik (Commerce)", "Moon", "Mercury", "Lagna", True, "Trade and commerce"),
    ("Karyasiddhi (Success in Undertakings)", "Saturn", "Sun", "SunSignLord", False, "Accomplishment of worldly enterprises"),
    ("Vivaha (Marriage / Union)", "Venus", "Saturn", "Lagna", True, "Spousal union, wedlock, partnership"),
    ("Santapa (Distress / Grief)", "Saturn", "Moon", "H6", True, "Emotional sorrow, heartbreak, depression"),
    ("Sraddha (Devotion / Faith)", "Venus", "Mars", "Lagna", True, "Devotion, sincerity"),
    ("Preeti (Love / Affection)", "Sastra", "Punya", "Lagna", True, "Love, attachment"),
    ("Jadatha (Chronic Disease)", "Mars", "Saturn", "Mercury", True, "Chronic disease, mental inertia"),
    ("Vyapar (Trade / Business)", "Mars", "Saturn", "Lagna", False, "Commercial ventures, mercantile trade"),
    ("Shatru (Enemies)", "Mars", "Saturn", "Lagna", True, "Hostile opposition, adversaries, combatants"),
    ("Jalapatha (Voyage / Crossing Waters)", "Cancer15", "Saturn", "Lagna", True, "Maritime transport, overseas journeys"),
    ("Bandhana (Imprisonment / Confinement)", "Punya", "Saturn", "Lagna", True, "Restrictions, incarceration, bondage"),
    ("Apamrityu (Bad Death)", "H8", "Mars", "Lagna", True, "Untimely or violent death"),
    ("Labha (Gains / Profit)", "H11", "Lord11", "Lagna", False, "Inflow of profits, revenues, windfalls"),
    # Not in the main list (other Tajika texts):
    ("Bhojana (Food / Feast)", "Moon", "Jupiter", "Lagna", True, "Gourmet dining, food availability, banquets"),
    ("Sukha (Happiness / Comfort)", "Jupiter", "Venus", "Lagna", True, "Mental tranquility, luxurious ease"),
    ("Agni (Fire Hazard)", "Mars", "Sun", "Lagna", True, "Thermal burns, fire hazards, explosions"),
    ("Bhaya (Fear / Anxiety)", "Saturn", "Mars", "Lagna", True, "Terror, dread, psychological distress"),
    ("Yuvati (Attraction to Women)", "Moon", "Sun", "Lagna", True, "Feminine company, romance, companionship"),
    ("Dharma (Righteousness / Morality)", "Jupiter", "Sun", "Lagna", True, "Virtue, ethical rectitude, duty"),
    ("Vitta (Liquid Capital)", "Jupiter", "Mercury", "Lagna", True, "Commercial securities, bank reserves"),
    ("Upapatti (Invention / Discovery)", "Mercury", "Jupiter", "Lagna", True, "Scientific ingenuity, patentable ideas"),
    ("Kshama (Forgiveness / Patience)", "Jupiter", "Saturn", "Lagna", True, "Compassion, endurance, forbearance"),
    ("Udyoga (Diligence / Industry)", "Mars", "Saturn", "Lagna", True, "Work ethic, physical labor, perseverance"),
    ("Vairagya (Dispassion / Detachment)", "Saturn", "Moon", "Lagna", True, "Renunciation, detachment, moksha"),
    ("Sangeeta (Music / Fine Arts)", "Venus", "Moon", "Lagna", True, "Musical talent, poetic artistic flair"),
    ("Kavya (Poetry / Literature)", "Mercury", "Venus", "Lagna", True, "Creative writing, rhetoric, authorship"),
    ("Swarga (Heavenly Realm)", "Jupiter", "Sun", "Lagna", False, "Afterlife elevation, pious merit"),
    ("Apaswara (Bad Reputation)", "Rahu", "Jupiter", "Lagna", True, "Scandal, infamy, loss of dignity"),
    ("Asru (Tears / Weeping)", "Saturn", "Venus", "Lagna", True, "Bereavement, crying, severe disappointment"),
    ("Kanya (Bride / Virgin)", "Venus", "Moon", "Lagna", True, "Eligible matches, auspicious bridehood")
]

# Table 9 exceptions that are not a plain day/night swap
_KARYASIDDHI_NIGHT = ("Saturn", "Moon", "MoonSignLord")   # night formula, not reversed
_SAMARTHA_MARS_LAGNA = ("Jupiter", "Mars")                # when Mars owns the lagna

def resolve_body_coord(
    token: str,
    coords: Dict[str, float],
    lagna_lon: float,
    punya_lon: Optional[float] = None,
    sree_lagna_lon: Optional[float] = None,
    derived: Optional[Dict[str, float]] = None
) -> float:
    """Resolves token name into absolute celestial longitude.

    Tokens: planet names, Lagna, Punya, SreeLagna, H<n> (lagna + 30(n-1)), Lord<n>,
    SunSignLord / MoonSignLord, Cancer15 (105 deg), or a saham already in ``derived``."""
    from .natal_chart import RASI_LORDS
    if token == "Lagna":
        return lagna_lon
    if token == "Punya":
        return punya_lon if punya_lon is not None else lagna_lon
    if token == "SreeLagna":
        return sree_lagna_lon if sree_lagna_lon is not None else lagna_lon
    if token == "Cancer15":
        return 105.0
    if derived and token in derived:
        return derived[token]
    if token in ("SunSignLord", "MoonSignLord"):
        body = coords.get(token[:-8], lagna_lon)
        return coords.get(RASI_LORDS[int(norm360(body) // 30.0)], lagna_lon)
    if token.startswith("H"):
        h_num = int(token[1:])
        return norm360(lagna_lon + (h_num - 1) * 30.0)
    if token.startswith("Lord"):
        h_num = int(token[4:])
        s_idx = int(norm360(lagna_lon + (h_num - 1) * 30.0) // 30.0)
        lord = RASI_LORDS[s_idx]
        return coords.get(lord, lagna_lon)
    return coords.get(token, lagna_lon)

def compute_single_saham(
    lon_a: float,
    lon_b: float,
    lagna_lon: float,
    is_night: bool,
    reverses_at_night: bool = True
) -> float:
    """
    Computes a single Saham according to classical Tajika rules:
    Day: (A - B) + C
    Night (if reverses): (B - A) + C
    Adds 30° if C is not in the forward arc from B to A (from A to B when reversed).
    ``lagna_lon`` is the C term, which is the lagna for most sahamas.
    """
    if is_night and reverses_at_night:
        diff = norm360(lon_b - lon_a)
        start_pt = lon_a
        end_pt = lon_b
    else:
        diff = norm360(lon_a - lon_b)
        start_pt = lon_b
        end_pt = lon_a

    saham = norm360(diff + lagna_lon)

    # Tajika arc containment check: is C in the forward arc between start_pt and end_pt?
    arc_len = (end_pt - start_pt) % 360.0
    c_offset = (lagna_lon - start_pt) % 360.0
    if not (0.0 <= c_offset <= arc_len):
        saham = norm360(saham + 30.0)

    return saham

def compute_all_50_sahams(
    planetary_longitudes: Dict[str, float],
    lagna_lon: float,
    is_night: bool,
    sree_lagna_lon: Optional[float] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Computes all classical Tajika Sahams (the 36 of the main list + 17 from other texts) for a
    birth or annual chart.  Each result carries ``in_main_list``.
    """
    from .natal_chart import RASI_LORDS
    coords = dict(planetary_longitudes)
    wanted = {SPELLING.get(n, n) for n in SAHAMA_NAMES}
    derived: Dict[str, float] = {}
    results = {}
    for name, body_a, body_b, body_c, rev, desc in SAHAM_DEFINITIONS:
        short = name.split(" (")[0]
        if short == "Samartha" and RASI_LORDS[int(norm360(lagna_lon) // 30.0)] == "Mars":
            body_a, body_b = _SAMARTHA_MARS_LAGNA
        if short == "Karyasiddhi" and is_night:
            body_a, body_b, body_c = _KARYASIDDHI_NIGHT
        lon_a, lon_b, lon_c = (resolve_body_coord(t, coords, lagna_lon, derived.get("Punya"),
                                                  sree_lagna_lon, derived)
                               for t in (body_a, body_b, body_c))
        saham_val = compute_single_saham(lon_a, lon_b, lon_c, is_night, rev)
        derived[short] = saham_val
        s_idx = int(saham_val // 30.0)

        results[name] = {
            "longitude": round(saham_val, 4),
            "sign_index": s_idx,
            "sign_name": RASI_NAMES_EN[s_idx],
            "degree_in_sign": round(saham_val % 30.0, 4),
            "description": desc,
            "formula": f"{body_a} - {body_b} + {body_c}",
            "in_main_list": short in wanted,
        }
    return results


# ---------------------------------------------------------------------------
# Coverage against the main saham list
# ---------------------------------------------------------------------------
# The reference list (Key Info's "Sahamas") names exactly 36 sahamas.  SAHAM_DEFINITIONS above has 53: all 36
# (9 under different spellings; the formulas follow PVR 28.8) and 17 entries from other Tajika texts.
SAHAMA_NAMES = [
    "Labha", "Apamrityu", "Bandhana", "Jalapatana", "Satru", "Vyapara", "Jadya", "Preeti", "Sraddha",
    "Santapa", "Vivaha", "Karyasiddhi", "Vanik", "Paradara", "Artha", "Paradesa", "Mrityu", "Bandhu",
    "Sastra", "Kali", "Roga", "Karma", "Jeeva", "Putra", "Matru", "Rajya", "Pitru", "Gaurava", "Bhratru",
    "Samartha", "Asha", "Mahatmya", "Mitra", "Yasas", "Vidya", "Punya",
]
SPELLING = {"Jalapatana": "Jalapatha", "Vyapara": "Vyapar", "Jadya": "Jadatha", "Rajya": "Raja",
                  "Satru": "Shatru", "Matru": "Matri", "Pitru": "Pitri", "Bhratru": "Bhratri", "Yasas": "Yashas"}


def saham_coverage() -> Dict[str, List[str]]:
    """Which of the main list's 36 sahamas are defined here, which are missing, and which extras are not in it."""
    local = {d[0].split(" (")[0] for d in SAHAM_DEFINITIONS}
    present, missing = [], []
    for name in SAHAMA_NAMES:
        (present if SPELLING.get(name, name) in local else missing).append(name)
    wanted = {SPELLING.get(n, n) for n in SAHAMA_NAMES}
    return {"present": present, "missing": missing, "not_in_main_list": sorted(local - wanted)}


# The 36 sahamas (PVR 28.8) in the reference list's order (SAHAMA_NAMES reversed):
# (A, B, C) with ints = point indices (0 lagna, 1 Sun .. 7 Saturn), "Sn" = saham n, "Hn" = lagna + 30 x (n-1),
# "Ln" = lord of the nth sign from the lagna, a float = that longitude; NO_SWAP: A and B kept at night.
SAHAMS = [
    (2, 1, 0), (1, 2, 0), (5, "S0", 0), (5, "S0", 6), ("S0", 3, 0), (7, 3, 0), (3, "L1", 0), (5, 7, 0),
    (5, 2, 1), (7, 1, 0), (7, 1, 0), (2, 6, 0), (5, 2, 0), (7, 5, 0), (3, 4, 0), (0, 2, 0), (5, 3, 0), (5, 7, 4),
    (4, 2, 0), ("H8", 2, 0), ("H9", "L9", 0), ("H2", "L2", 0), (6, 1, 0), (2, 4, 0), (7, 1, "LSun"), (6, 7, 0),
    (7, 2, "H6"), (6, 3, 0), ("S17", "S0", 0), (3, 7, 4), (3, 7, 0), (3, 7, 0), (105.0, 7, 0), ("S0", 7, 0),
    ("H8", 3, 0), ("H11", "L11", 0)]
SAHAMS_NO_SWAP = {7, 15, 19, 20, 21, 30, 35}
_LORDS = [3, 6, 4, 2, 1, 4, 6, 3, 5, 7, 7, 5]          # sign lords (BPHS 4.6-24)


def saham_longitude(i: int, a: float, b: float, c: float, lons: List[float], is_day: bool) -> float:
    """A sahama (PVR 28.8.1): A - B + C by day (B - A + C at night, unless saham ``i`` keeps them), + 30
    when the lagna is not on the arc from B forward to A; reduced to [0, 360).  Samartha (6) uses Jupiter - Mars
    when the lagna lord is Mars; Karyasiddhi (24) at night is Saturn - Moon + the lord of the Moon's sign."""
    lag = lons[0]
    if i == 6 and _LORDS[int(lag // 30)] == 3:
        a, b, c = lons[5], lons[3], lag
    if i == 24 and not is_day:
        b, c = lons[2], lons[_LORDS[int(lons[2] // 30)]]
    elif i not in SAHAMS_NO_SWAP and not is_day:
        a, b = b, a
    v = a - b + c
    if (lag <= a or a <= b) and (b <= lag or (a <= b and lag <= a)):
        pass
    else:
        v += 30.0
    while v < 0.0:
        v += 360.0
    while v >= 360.0:
        v -= 360.0
    return v


def saham_longitudes(lons: List[float], is_day: bool) -> List[float]:
    """The 36 sahamas of SAHAMS from ``lons`` (points 0 lagna .. 7 Saturn, sidereal rasi longitudes) and
    day / night birth."""
    lag = lons[0]
    out: List[float] = []

    def val(x):
        if isinstance(x, float):
            return x
        if isinstance(x, int):
            return lons[x]
        if x[0] == "S":
            return out[int(x[1:])]
        if x[0] == "H":
            return (lag + 30.0 * (int(x[1:]) - 1)) % 360.0
        if x == "LSun":
            return lons[_LORDS[int(lons[1] // 30)]]
        return lons[_LORDS[(int(lag // 30) + int(x[1:]) - 1) % 12]]
    for i, (a, b, c) in enumerate(SAHAMS):
        out.append(saham_longitude(i, val(a), val(b), val(c), lons, is_day))
    return out
