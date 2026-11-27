"""vargas: part of natal_chart (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Any, Dict
from .signs import RASI_LORDS, RASI_NAMES_EN, RASI_NAMES_SA, norm360

# ---------------------------------------------------------------------------
# Divisional Vargas (Harmonics D-1 through D-60): BPHS 6.5-41 and PVR 6.2 (docs/SOURCES.md section 3);
# varga_charts holds every scheme of Settings > Divisional charts, these the defaults
# ---------------------------------------------------------------------------

def compute_varga_d1(lon: float) -> int:
    """D-1 (Rasi): Sign index (0-11)."""
    return int(norm360(lon) // 30.0)

def compute_varga_d2(lon: float, mode: str = "parasara") -> int:
    """
    D-2 (Hora).
    "parasara": odd signs 0-15° Sun (Leo=4), 15-30° Moon (Cancer=3); even signs the reverse (BPHS 6.5-6).
    "us" (the default, HoraPreference=6, the Uma-Shambhu hora of P. V. R. Narasimha Rao): cyclic horas,
    int(lon / 15) mod 12, with the degrees mirrored inside even signs.
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    deg = lon - (sign * 30.0)
    is_odd = (sign % 2 == 0) # 0-indexed (0=Aries is odd)
    if mode == "us":
        return int((sign * 30.0 + (deg if is_odd else 30.0 - deg)) / 15.0) % 12
    if is_odd:
        return 4 if deg < 15.0 else 3
    else:
        return 3 if deg < 15.0 else 4

def compute_varga_d3(lon: float, mode: str = "parasara") -> int:
    """
    D-3 (Drekkana):
    Parasara: 0-10° same sign, 10-20° 5th from sign, 20-30° 9th from sign.
    Somnath & Jagannath variations also supported.
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    deg = lon - (sign * 30.0)
    part = int(deg // 10.0)
    if mode.lower() == "somnath":
        # Somnath: Aries to Pisces regular zodiacal order
        step = (sign * 3 + part) % 12
        return step
    # Parasara standard:
    offset = part * 4  # 0, 4 (5th house), 8 (9th house)
    return (sign + offset) % 12

def compute_varga_d4(lon: float) -> int:
    """
    D-4 (Chaturthamsa):
    0-7.5° 1st, 7.5-15° 4th, 15-22.5° 7th, 22.5-30° 10th from natal sign.
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // 7.5)
    return (sign + part * 3) % 12

def compute_varga_d7(lon: float) -> int:
    """
    D-7 (Saptamsa):
    Odd signs: starts from same sign.
    Even signs: starts from 7th from sign.
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // (30.0 / 7.0))
    is_odd = (sign % 2 == 0)
    start = sign if is_odd else (sign + 6) % 12
    return (start + part) % 12

def compute_varga_d9(lon: float) -> int:
    """
    D-9 (Navamsa):
    Master 9-fold harmonic. Each division is 3°20' (3.3333°).
    Fiery signs (Aries, Leo, Sag): start from Aries (0).
    Earthy signs (Taurus, Virgo, Cap): start from Capricorn (9).
    Airy signs (Gemini, Libra, Aqu): start from Libra (6).
    Watery signs (Cancer, Scorpio, Pis): start from Cancer (3).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    pada_span = 30.0 / 9.0
    part = int((lon % 30.0) // pada_span)
    element = sign % 4
    element_starts = {0: 0, 1: 9, 2: 6, 3: 3}
    return (element_starts[element] + part) % 12

def compute_varga_d10(lon: float) -> int:
    """
    D-10 (Dasamsa - Career / Mahaphalamsa):
    Odd signs: starts from same sign.
    Even signs: starts from 9th from sign.
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // 3.0)
    is_odd = (sign % 2 == 0)
    start = sign if is_odd else (sign + 8) % 12
    return (start + part) % 12

def compute_varga_d12(lon: float) -> int:
    """
    D-12 (Dwadasamsa - Parents):
    Starts from natal sign and moves continuously.
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // 2.5)
    return (sign + part) % 12

def compute_varga_d16(lon: float) -> int:
    """
    D-16 (Shodasamsa / Kalamsa - Vehicles & Luxuries):
    Movable signs (0, 3, 6, 9): start from Aries (0).
    Fixed signs (1, 4, 7, 10): start from Leo (4).
    Dual signs (2, 5, 8, 11): start from Sagittarius (8).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // (30.0 / 16.0))
    modality = sign % 3
    starts = {0: 0, 1: 4, 2: 8}
    return (starts[modality] + part) % 12

def compute_varga_d20(lon: float) -> int:
    """
    D-20 (Vimsamsa - Spiritual progress):
    Movable signs: start from Aries (0).
    Fixed signs: start from Sagittarius (8).
    Dual signs: start from Leo (4).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // 1.5)
    modality = sign % 3
    starts = {0: 0, 1: 8, 2: 4}
    return (starts[modality] + part) % 12

def compute_varga_d24(lon: float) -> int:
    """
    D-24 (Chaturvimsamsa / Siddhamsa - Higher Learning):
    Odd signs: start from Leo (4).
    Even signs: start from Cancer (3).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // 1.25)
    is_odd = (sign % 2 == 0)
    start = 4 if is_odd else 3
    return (start + part) % 12

def compute_varga_d27(lon: float) -> int:
    """
    D-27 (Saptavimsamsa / Bhamsa - Strengths & Weaknesses):
    Fiery signs: start from Aries (0).
    Earthy signs: start from Cancer (3).
    Airy signs: start from Libra (6).
    Watery signs: start from Capricorn (9).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // (30.0 / 27.0))
    element = sign % 4
    starts = {0: 0, 1: 3, 2: 6, 3: 9}
    return (starts[element] + part) % 12

def compute_varga_d30(lon: float) -> int:
    """
    D-30 (Trimsamsa - Arishta / Misfortunes):
    Degrees in Odd Signs:
      0-5°: Mars (Aries=0)
      5-10°: Saturn (Aquarius=10)
      10-18°: Jupiter (Sagittarius=8)
      18-25°: Mercury (Gemini=2)
      25-30°: Venus (Libra=6)
    Degrees in Even Signs:
      0-5°: Venus (Taurus=1)
      5-12°: Mercury (Virgo=5)
      12-20°: Jupiter (Pisces=11)
      20-25°: Saturn (Capricorn=9)
      25-30°: Mars (Scorpio=7)
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    deg = lon - (sign * 30.0)
    is_odd = (sign % 2 == 0)
    if is_odd:
        if deg < 5.0: return 0
        if deg < 10.0: return 10
        if deg < 18.0: return 8
        if deg < 25.0: return 2
        return 6
    else:
        if deg < 5.0: return 1
        if deg < 12.0: return 5
        if deg < 20.0: return 11
        if deg < 25.0: return 9
        return 7

def compute_varga_d60(lon: float) -> int:
    """
    D-60 (Shastiamsa - Karma & Past Life):
    Each shastiamsa = 30' (0.5 degrees).
    Starts from the natal sign and counts continuously.
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // 0.5)
    return (sign + part) % 12

def compute_varga_d5(lon: float) -> int:
    """
    D-5 (Panchamsa, D5Preference=0; PVR 6.2.5): parts of 6° ruled like the trimsamsa —
    odd signs Mars, Saturn, Jupiter, Mercury, Venus (Ar, Aq, Sg, Ge, Li); even signs counted from the end of the
    sign. The 12° and 24° boundaries belong to the lower part (compared with <=).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    deg = lon - sign * 30.0
    is_odd = sign % 2 == 0
    if not is_odd:
        deg = 30.0 - deg
    part = 0 if deg < 6.0 else 1 if deg <= 12.0 else 2 if deg <= 18.0 else 3 if deg <= 24.0 else 4
    return (0, 10, 8, 2, 6)[part] if is_odd else (7, 9, 11, 5, 1)[part]

def compute_varga_d6(lon: float) -> int:
    """
    D-6 (Shashthamsa - Health, Debts, Litigation & Enemies):
    Each division is 5°00'.
    Odd signs: start from Aries (0).
    Even signs: start from Libra (6).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // 5.0)
    is_odd = (sign % 2 == 0)
    start = 0 if is_odd else 6
    return (start + part) % 12

def compute_varga_d8(lon: float) -> int:
    """
    D-8 (Ashtamsa - Longevity, Hidden Obstacles & Sudden Events):
    Each division is 3°45' (3.75°).
    Movable signs (0, 3, 6, 9): start from Aries (0).
    Fixed signs (1, 4, 7, 10): start from Sagittarius (8).
    Dual signs (2, 5, 8, 11): start from Leo (4).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // 3.75)
    modality = sign % 3
    starts = {0: 0, 1: 8, 2: 4}
    return (starts[modality] + part) % 12

def compute_varga_d11(lon: float) -> int:
    """
    D-11 (Rudramsa - Challenges, Wars, Force Majeure):
    Each division is 30/11 = 2°43'38.18" (2.72727°).
    Counted from Aries in regular order or reverse from Pisces.
    Standard Parasara: Movable from Aries (0), Fixed from Taurus (1), Dual from Gemini (2).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // (30.0 / 11.0))
    start = (12 - sign) % 12
    return (start + part) % 12

def compute_varga_d40(lon: float) -> int:
    """
    D-40 (Khavedamsa / Swavedamsa - Auspicious/Inauspicious Karma):
    Each division is 45' (0.75°).
    Odd signs: start from Aries (0).
    Even signs: start from Libra (6).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // 0.75)
    is_odd = (sign % 2 == 0)
    start = 0 if is_odd else 6
    return (start + part) % 12

def compute_varga_d45(lon: float) -> int:
    """
    D-45 (Akshavedamsa - Overall Character, Integrity & Purity):
    Each division is 40' (0.6667°).
    Movable signs: start from Aries (0).
    Fixed signs: start from Leo (4).
    Dual signs: start from Sagittarius (8).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    part = int((lon % 30.0) // (40.0 / 60.0))
    modality = sign % 3
    starts = {0: 0, 1: 4, 2: 8}
    return (starts[modality] + part) % 12

def compute_varga_d81(lon: float) -> int:
    """D-81 (Nava-navamsa): the navamsa (BPHS 6.12) of the navamsa."""
    lon = norm360(lon)
    n = int(lon * 0.3)
    within = (lon - n * (10.0 / 3.0)) * 9.0
    return int(((n % 12) * 30.0 + within) * 0.3) % 12


def compute_varga_d108(lon: float, mode: int = 1) -> int:
    """
    D-108 (Ashtottaramsa): 108 parts of 16'40" per sign, counted from the navamsa sign (mode 1, the default
    D108Preference=1: the dwadasamsa of the navamsa) or from the sign itself (mode 0).
    """
    lon = norm360(lon)
    sign = int(lon // 30.0)
    start = compute_varga_d9(lon) if mode == 1 else sign
    return (start + int((lon - sign * 30.0) * 3.6)) % 12

def compute_varga_d144(lon: float) -> int:
    """D-144 (Dwadasa-dwadasamsa): 144 parts of 12'30" per sign counted from the dwadasamsa (D-12, BPHS 6.15)
    sign, i.e. the dwadasamsa of the dwadasamsa."""
    lon = norm360(lon)
    sign = int(lon // 30.0)
    return (compute_varga_d12(lon) + int((lon - sign * 30.0) * 4.8)) % 12

def compute_all_vargas(lon: float) -> Dict[str, Dict[str, Any]]:
    """All divisional signs of a longitude with the default schemes (the 23 charts of Key Info:
    D-2 "US", D-108 from the navamsa)."""
    varga_funcs = {
        "D1": compute_varga_d1,
        "D2": lambda x: compute_varga_d2(x, "us"),
        "D3": compute_varga_d3,
        "D4": compute_varga_d4,
        "D5": compute_varga_d5,
        "D6": compute_varga_d6,
        "D7": compute_varga_d7,
        "D8": compute_varga_d8,
        "D9": compute_varga_d9,
        "D10": compute_varga_d10,
        "D11": compute_varga_d11,
        "D12": compute_varga_d12,
        "D16": compute_varga_d16,
        "D20": compute_varga_d20,
        "D24": compute_varga_d24,
        "D27": compute_varga_d27,
        "D30": compute_varga_d30,
        "D40": compute_varga_d40,
        "D45": compute_varga_d45,
        "D60": compute_varga_d60,
        "D81": compute_varga_d81,
        "D108": compute_varga_d108,
        "D144": compute_varga_d144
    }
    res = {}
    for vid, fn in varga_funcs.items():
        s_idx = fn(lon)
        res[vid] = {
            "sign_idx": s_idx,
            "sign_sa": RASI_NAMES_SA[s_idx],
            "sign_en": RASI_NAMES_EN[s_idx],
            "lord": RASI_LORDS[s_idx]
        }
    return res
