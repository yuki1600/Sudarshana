"""
Classical Yoga Detection Engine — BPHS Ch. 34–42, 75, 79.

Detects:
  - Pancha Mahapurusha Yogas (Ch. 75)
  - Nabhasha Yogas (Ch. 35)
  - Chandra Yogas (Ch. 37)
  - Surya Yogas (Ch. 38)
  - Raja Yogas (Ch. 39–40)
  - Dhana Yogas (Ch. 41)
  - Daridra Yogas (Ch. 42)
  - Pravrajya / Ascetism Yogas (Ch. 79)
  - Yoga Karakas per lagna (Ch. 34)
"""

from __future__ import annotations
from typing import Any

from src.jyotisha.base.constants import (
    SIGN_LORD, EXALT, DEBIL, MOOLATR, BENEFICS, MALEFICS
)
from src.jyotisha.base.utils import lon_to_sign_idx

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_KENDRA_HOUSES = {1, 4, 7, 10}
_TRIKONA_HOUSES = {1, 5, 9}
_DUSTHANA_HOUSES = {6, 8, 12}
_UPACHAYA_HOUSES = {3, 6, 10, 11}

# Classical planets only (no outer planets for yoga logic)
_CLASSICAL = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
_CLASSICAL_NO_LUMI = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Own signs (sign_idx → lord)
_OWN_SIGNS: dict[str, list[int]] = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10],
}

# Exaltation sign indices
_EXALT_SIGN: dict[str, int] = {
    "Sun": 0, "Moon": 1, "Mars": 10, "Mercury": 5,
    "Jupiter": 3, "Venus": 11, "Saturn": 6,
}

def _house_of(planet: str, lons: dict[str, float], asc_sign_idx: int) -> int:
    """1-based house number of planet from Ascendant."""
    si = lon_to_sign_idx(lons[planet])
    return ((si - asc_sign_idx) % 12) + 1

def _sign_idx(planet: str, lons: dict[str, float]) -> int:
    return lon_to_sign_idx(lons[planet])

def _is_own(planet: str, lons: dict[str, float]) -> bool:
    si = _sign_idx(planet, lons)
    return si in _OWN_SIGNS.get(planet, []) or si == MOOLATR.get(planet, -1)

def _is_exalted(planet: str, lons: dict[str, float]) -> bool:
    return _sign_idx(planet, lons) == _EXALT_SIGN.get(planet, -99)

def _is_in_kendra(planet: str, lons: dict[str, float], asc_sign_idx: int) -> bool:
    return _house_of(planet, lons, asc_sign_idx) in _KENDRA_HOUSES

def _lord_of_house(house_num: int, asc_sign_idx: int) -> str:
    sign_idx = (asc_sign_idx + house_num - 1) % 12
    return SIGN_LORD.get(sign_idx, "Sun")

def _planets_in_house(house_num: int, lons: dict[str, float], asc_sign_idx: int,
                      planet_list: list[str] | None = None) -> list[str]:
    pl = planet_list or _CLASSICAL
    return [p for p in pl if p in lons and _house_of(p, lons, asc_sign_idx) == house_num]

def _planets_from_ref(ref_sign_idx: int, offset: int, lons: dict[str, float],
                      planet_list: list[str] | None = None) -> list[str]:
    """Planets in the sign that is `offset` signs from ref_sign_idx."""
    target = (ref_sign_idx + offset) % 12
    pl = planet_list or _CLASSICAL_NO_LUMI
    return [p for p in pl if p in lons and lon_to_sign_idx(lons[p]) == target]

def _are_conjunct(p1: str, p2: str, lons: dict[str, float]) -> bool:
    return lon_to_sign_idx(lons[p1]) == lon_to_sign_idx(lons[p2])

def _signs_of(planet_list: list[str], lons: dict[str, float]) -> list[int]:
    return [lon_to_sign_idx(lons[p]) for p in planet_list if p in lons]

def _yoga(name: str, category: str, planets: list[str], desc: str,
          strength: str = "present") -> dict:
    return {
        "name": name,
        "category": category,
        "planets_involved": planets,
        "description": desc,
        "strength": strength,
    }


# ---------------------------------------------------------------------------
# A. Pancha Mahapurusha Yogas (Ch. 75)
# ---------------------------------------------------------------------------

def _pancha_mahapurusha(lons: dict[str, float], asc_sign_idx: int) -> list[dict]:
    yogas = []
    configs = [
        ("Jupiter", "Hamsa", "Guru in own/exalt in Kendra → wisdom, dharma, teaching"),
        ("Venus",   "Malavya", "Shukra in own/exalt in Kendra → beauty, luxury, art"),
        ("Mars",    "Ruchaka", "Mangal in own/exalt in Kendra → courage, leadership"),
        ("Mercury", "Bhadra", "Budha in own/exalt in Kendra → intellect, communication"),
        ("Saturn",  "Sasha", "Shani in own/exalt in Kendra → discipline, authority"),
    ]
    for planet, yoga_name, desc in configs:
        if planet not in lons:
            continue
        if (_is_own(planet, lons) or _is_exalted(planet, lons)) and _is_in_kendra(planet, lons, asc_sign_idx):
            strength = "strong" if _is_exalted(planet, lons) else "moderate"
            yogas.append(_yoga(yoga_name, "Pancha Mahapurusha", [planet], desc, strength))
    return yogas


# ---------------------------------------------------------------------------
# B. Nabhasha Yogas (Ch. 35)
# ---------------------------------------------------------------------------

_MOVABLE = {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn
_FIXED   = {1, 4, 7, 10}   # Taurus, Leo, Scorpio, Aquarius
_DUAL    = {2, 5, 8, 11}   # Gemini, Virgo, Sagittarius, Pisces

def _nabhasha(lons: dict[str, float], asc_sign_idx: int) -> list[dict]:
    yogas = []
    pl = [p for p in _CLASSICAL if p in lons]
    signs = _signs_of(pl, lons)
    sign_set = set(signs)

    # Ashraya group — all planets in one modality
    if all(s in _MOVABLE for s in signs):
        yogas.append(_yoga("Rajju", "Nabhasha (Ashraya)", pl,
            "All planets in movable signs → frequent travel, instability, dynamism"))
    elif all(s in _FIXED for s in signs):
        yogas.append(_yoga("Musala", "Nabhasha (Ashraya)", pl,
            "All planets in fixed signs → determination, stubbornness, stability"))
    elif all(s in _DUAL for s in signs):
        yogas.append(_yoga("Nala", "Nabhasha (Ashraya)", pl,
            "All planets in dual signs → versatility, indecisiveness, adaptability"))

    # Sankhya group — count of occupied signs
    occupied = len(sign_set)
    sankhya_map = {
        1: ("Gola", "All planets in 1 sign → extreme focus, isolation"),
        2: ("Yuga", "Planets in 2 signs → dual nature, partnerships"),
        3: ("Shoola", "Planets in 3 signs → suffering, challenges"),
        4: ("Kedara", "Planets in 4 signs → agriculture, patience, prosperity"),
        5: ("Pasha", "Planets in 5 signs → bondage, worldly entanglements"),
        6: ("Dama", "Planets in 6 signs → self-control, restraint"),
        7: ("Veena", "Planets in 7 signs (Vallaki) → arts, music, fine life"),
    }
    if occupied in sankhya_map:
        name, desc = sankhya_map[occupied]
        yogas.append(_yoga(name, "Nabhasha (Sankhya)", pl, desc))

    # Dala group — benefics in Kendra = Mala; malefics = Sarpa
    bens_in_k = [p for p in BENEFICS if p in lons and _is_in_kendra(p, lons, asc_sign_idx)]
    mals_in_k = [p for p in MALEFICS if p in lons and _is_in_kendra(p, lons, asc_sign_idx)]
    if len(bens_in_k) >= 3:
        yogas.append(_yoga("Mala", "Nabhasha (Dala)", bens_in_k,
            "3+ benefics in Kendras → garlands of good fortune, happiness"))
    if len(mals_in_k) >= 3:
        yogas.append(_yoga("Sarpa", "Nabhasha (Dala)", mals_in_k,
            "3+ malefics in Kendras → serpent energy, struggles, hidden power"))

    return yogas


# ---------------------------------------------------------------------------
# C. Chandra (Moon) Yogas (Ch. 37)
# ---------------------------------------------------------------------------

def _chandra_yogas(lons: dict[str, float], asc_sign_idx: int) -> list[dict]:
    yogas = []
    if "Moon" not in lons:
        return yogas

    moon_si = lon_to_sign_idx(lons["Moon"])
    in_2nd  = _planets_from_ref(moon_si, 1,  lons, _CLASSICAL_NO_LUMI)
    in_12th = _planets_from_ref(moon_si, -1, lons, _CLASSICAL_NO_LUMI)

    if in_2nd and in_12th:
        yogas.append(_yoga("Durudhura", "Chandra", in_2nd + in_12th,
            "Planets 2nd and 12th from Moon → prosperity sandwiched by support and expenditure", "strong"))
    elif in_2nd:
        yogas.append(_yoga("Sunapha", "Chandra", in_2nd,
            "Planet(s) in 2nd from Moon → wealth, self-made prosperity"))
    elif in_12th:
        yogas.append(_yoga("Anapha", "Chandra", in_12th,
            "Planet(s) in 12th from Moon → renown, physical well-being"))
    else:
        # Kemadruma — no planet 2nd/12th and no classical planet in Kendra
        kendras_occupied = [p for p in _CLASSICAL_NO_LUMI
                            if p in lons and _is_in_kendra(p, lons, asc_sign_idx)]
        if not kendras_occupied:
            yogas.append(_yoga("Kemadruma", "Chandra", ["Moon"],
                "No planet 2nd/12th from Moon, none in Kendra → poverty, hardship (check cancellation)"))

    return yogas


# ---------------------------------------------------------------------------
# D. Surya (Sun) Yogas (Ch. 38)
# ---------------------------------------------------------------------------

def _surya_yogas(lons: dict[str, float], asc_sign_idx: int) -> list[dict]:
    yogas = []
    if "Sun" not in lons:
        return yogas

    sun_si = lon_to_sign_idx(lons["Sun"])
    in_2nd  = _planets_from_ref(sun_si, 1,  lons, _CLASSICAL_NO_LUMI)
    in_12th = _planets_from_ref(sun_si, -1, lons, _CLASSICAL_NO_LUMI)

    if in_2nd and in_12th:
        yogas.append(_yoga("Ubhayachari", "Surya", in_2nd + in_12th,
            "Planets both 2nd and 12th from Sun → royal bearing, fame, self-reliance", "strong"))
    elif in_2nd:
        yogas.append(_yoga("Vesi", "Surya", in_2nd,
            "Planet(s) in 2nd from Sun → eloquence, wealth accumulation"))
    elif in_12th:
        yogas.append(_yoga("Vasi", "Surya", in_12th,
            "Planet(s) in 12th from Sun → charitable, spiritual nature"))

    return yogas


# ---------------------------------------------------------------------------
# E. Raja Yogas (Ch. 39–40)
# ---------------------------------------------------------------------------

def _raja_yogas(lons: dict[str, float], asc_sign_idx: int) -> list[dict]:
    yogas = []

    kendra_lords = [_lord_of_house(h, asc_sign_idx) for h in [1, 4, 7, 10]]
    trikona_lords = [_lord_of_house(h, asc_sign_idx) for h in [1, 5, 9]]

    # 1st house lord is both Kendra and Trikona — pair it with others
    for kl in set(kendra_lords):
        for tl in set(trikona_lords):
            if kl == tl:
                continue  # same planet
            if kl not in lons or tl not in lons:
                continue
            # Conjunction
            if _are_conjunct(kl, tl, lons):
                h = _house_of(kl, lons, asc_sign_idx)
                strength = "strong" if h in _KENDRA_HOUSES | _TRIKONA_HOUSES else "moderate"
                yogas.append(_yoga(
                    "Raja Yoga",
                    "Raja",
                    [kl, tl],
                    f"{kl} (Kendra lord) conjunct {tl} (Trikona lord) → power, authority, success",
                    strength
                ))
            # Mutual exchange (Parivartana)
            kl_sign = _sign_idx(kl, lons)
            tl_sign = _sign_idx(tl, lons)
            kl_own = _OWN_SIGNS.get(kl, [])
            tl_own = _OWN_SIGNS.get(tl, [])
            if kl_sign in tl_own and tl_sign in kl_own:
                yogas.append(_yoga(
                    "Parivartana Raja Yoga",
                    "Raja",
                    [kl, tl],
                    f"{kl} and {tl} exchange signs (Kendra/Trikona lords) → powerful mutual empowerment",
                    "strong"
                ))

    return yogas


# ---------------------------------------------------------------------------
# F. Dhana Yogas (Ch. 41)
# ---------------------------------------------------------------------------

def _dhana_yogas(lons: dict[str, float], asc_sign_idx: int) -> list[dict]:
    yogas = []
    l2 = _lord_of_house(2, asc_sign_idx)
    l11 = _lord_of_house(11, asc_sign_idx)

    # 2nd and 11th lords conjunct
    if l2 in lons and l11 in lons and _are_conjunct(l2, l11, lons) and l2 != l11:
        yogas.append(_yoga("Dhana Yoga", "Dhana", [l2, l11],
            f"{l2} (2nd lord) and {l11} (11th lord) conjunct → wealth accumulation, financial success", "strong"))

    # 2nd or 11th lord with Jupiter
    for lx, hn in [(l2, 2), (l11, 11)]:
        if lx in lons and "Jupiter" in lons and lx != "Jupiter" and _are_conjunct(lx, "Jupiter", lons):
            yogas.append(_yoga("Dhana Yoga (Guru)", "Dhana", [lx, "Jupiter"],
                f"{lx} ({hn}th lord) with Jupiter → blessings of wealth, education, fortune"))

    # 2nd lord in own/exalt
    if l2 in lons and (_is_own(l2, lons) or _is_exalted(l2, lons)):
        yogas.append(_yoga("Dhana Yoga (Swa/Ucha 2L)", "Dhana", [l2],
            f"{l2} (2nd lord) in own/exalt sign → strong financial house"))

    return yogas


# ---------------------------------------------------------------------------
# G. Daridra Yogas (Ch. 42)
# ---------------------------------------------------------------------------

def _daridra_yogas(lons: dict[str, float], asc_sign_idx: int) -> list[dict]:
    yogas = []
    for hn in [6, 8, 12]:
        lord = _lord_of_house(hn, asc_sign_idx)
        if lord not in lons:
            continue
        h = _house_of(lord, lons, asc_sign_idx)
        if h in _KENDRA_HOUSES or h in _TRIKONA_HOUSES:
            yogas.append(_yoga(
                f"Daridra Yoga ({hn}th lord in {h}th)",
                "Daridra",
                [lord],
                f"{lord} ({hn}th lord) in {h}th house → financial struggles, losses, debts"
            ))
    return yogas


# ---------------------------------------------------------------------------
# H. Pravrajya / Ascetism Yogas (Ch. 79)
# ---------------------------------------------------------------------------

def _pravrajya_yogas(lons: dict[str, float], asc_sign_idx: int) -> list[dict]:
    yogas = []
    pl = [p for p in _CLASSICAL if p in lons]

    # 4+ planets in one sign
    from collections import Counter
    sign_counts = Counter(lon_to_sign_idx(lons[p]) for p in pl)
    for si, count in sign_counts.items():
        if count >= 4:
            clustered = [p for p in pl if lon_to_sign_idx(lons[p]) == si]
            has_sat = "Saturn" in clustered
            yogas.append(_yoga(
                "Pravrajya Yoga" if has_sat else "Sannyasa Yoga",
                "Pravrajya",
                clustered,
                f"{count} planets in sign {si+1} {'with Saturn dominance' if has_sat else ''} → renunciation, spiritual path"
            ))

    # Moon with Saturn, no benefic aspect (simplified)
    if "Moon" in lons and "Saturn" in lons:
        if _are_conjunct("Moon", "Saturn", lons):
            yogas.append(_yoga("Vairagya Yoga", "Pravrajya", ["Moon", "Saturn"],
                "Moon conjunct Saturn → detachment, sorrow leading to renunciation"))

    return yogas


# ---------------------------------------------------------------------------
# I. Yoga Karakas per Lagna (Ch. 34)
# ---------------------------------------------------------------------------

# Planets that become Yoga Karakas (lord of both Kendra AND Trikona) for each lagna
_YOGA_KARAKA_MAP: dict[int, list[str]] = {
    0: [],           # Aries — no single planet owns both
    1: ["Saturn"],   # Taurus — Saturn owns 9th (Trikona) and 10th (Kendra)
    2: [],           # Gemini
    3: ["Mars"],     # Cancer — Mars owns 5th (Trikona) and 10th (Kendra)
    4: [],           # Leo — no pure Yoga Karaka
    5: [],           # Virgo
    6: ["Saturn"],   # Libra — Saturn owns 4th (Kendra) and 5th (Trikona)
    7: [],           # Scorpio
    8: [],           # Sagittarius
    9: ["Venus"],    # Capricorn — Venus owns 5th (Trikona) and 10th (Kendra)
    10: ["Venus"],   # Aquarius — Venus owns 4th (Kendra) and 9th (Trikona)
    11: [],          # Pisces
}

def _yoga_karaka_info(lons: dict[str, float], asc_sign_idx: int) -> list[dict]:
    yogas = []
    yks = _YOGA_KARAKA_MAP.get(asc_sign_idx, [])
    for yk in yks:
        if yk not in lons:
            continue
        h = _house_of(yk, lons, asc_sign_idx)
        strength = "strong" if h in _KENDRA_HOUSES | _TRIKONA_HOUSES else "moderate"
        yogas.append(_yoga(
            f"Yoga Karaka ({yk})",
            "Yoga Karaka",
            [yk],
            f"{yk} is the Yoga Karaka for this lagna (lord of both Kendra and Trikona house)",
            strength
        ))
    return yogas


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_yogas(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Detect all classical yogas from chart data.

    Args:
        chart: dict with keys 'points' (DataFrame) and optionally 'asc_sign_idx'.

    Returns:
        List of yoga dicts: name, category, planets_involved, description, strength.
    """
    points_df = chart.get("points")
    if points_df is None or len(points_df) == 0:
        return []

    # Build numeric_lons from points DataFrame
    lons: dict[str, float] = {}
    for _, row in points_df.iterrows():
        name = row.get("Point", "")
        lon = row.get("Longitude (Dec)", None)
        if name and lon is not None:
            lons[name] = float(lon)

    asc_sign_idx = chart.get("asc_sign_idx")
    if asc_sign_idx is None:
        asc_lon = lons.get("Ascendant (1st House Cusp)", 0.0)
        asc_sign_idx = lon_to_sign_idx(asc_lon)

    yogas: list[dict] = []
    yogas += _pancha_mahapurusha(lons, asc_sign_idx)
    yogas += _nabhasha(lons, asc_sign_idx)
    yogas += _chandra_yogas(lons, asc_sign_idx)
    yogas += _surya_yogas(lons, asc_sign_idx)
    yogas += _raja_yogas(lons, asc_sign_idx)
    yogas += _dhana_yogas(lons, asc_sign_idx)
    yogas += _daridra_yogas(lons, asc_sign_idx)
    yogas += _pravrajya_yogas(lons, asc_sign_idx)
    yogas += _yoga_karaka_info(lons, asc_sign_idx)

    return yogas
