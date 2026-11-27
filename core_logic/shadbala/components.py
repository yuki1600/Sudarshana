"""components: part of shadbala (split from one module; see __init__.py)."""
from __future__ import annotations
import math
from typing import Dict, Optional, Tuple, Any
from ..utils import norm360
from ..natal_chart import EXALTATION, DEBILITATION, OWN_SIGNS, compute_all_vargas
from ..aspects_friendships import get_natural_relationship, compute_tatkalika_relationship, compute_parasara_drik_virupas
from .common import DEEP_DEBILITATION_DEGS, DIG_BALA_ZERO_OFFSETS, NAISARGIKA_BALA, PLANETS, SHADBALA_REQUIREMENTS, SIGN_RULERS

def compute_uchcha_bala(planet: str, longitude: float) -> float:
    """
    Computes Uchcha Bala (Exaltation Strength) in Virupas (0 to 60).
    Formula: Distance from deep debilitation point / 3.
    Max 60 Virupas at deep exaltation, 0 Virupas at deep debilitation.
    Source: BPHS 27.1-1.5 (docs/SOURCES.md section 10).
    """
    if planet not in DEEP_DEBILITATION_DEGS:
        return 0.0
    lon = norm360(longitude)
    deb_deg = DEEP_DEBILITATION_DEGS[planet]
    diff = abs(norm360(lon - deb_deg))
    if diff > 180.0:
        diff = 360.0 - diff
    return round(diff / 3.0, 2)

def compute_kendradi_bala(house_num: int) -> float:
    """
    Computes Kendradi Bala in Virupas:
    - Kendra (1, 4, 7, 10): 60 Virupas
    - Panapara (2, 5, 8, 11): 30 Virupas
    - Apoklima (3, 6, 9, 12): 15 Virupas
    """
    if house_num in [1, 4, 7, 10]:
        return 60.0
    elif house_num in [2, 5, 8, 11]:
        return 30.0
    else:
        return 15.0

def compute_dig_bala(planet: str, planet_lon: float, lagna_lon: float) -> float:
    """
    Computes Dig Bala (Directional Strength) in Virupas (0 to 60).
    Formula: Angular distance from zero-strength point / 3.
    Source: BPHS 27.7-7.5 (docs/SOURCES.md section 10).
    """
    if planet not in DIG_BALA_ZERO_OFFSETS:
        return 0.0
    zero_angle = norm360(lagna_lon + DIG_BALA_ZERO_OFFSETS[planet])
    arc = abs(norm360(planet_lon - zero_angle))
    if arc > 180.0:
        arc = 360.0 - arc
    return round(arc / 3.0, 2)

def compute_nathonnatha_bala(planet: str, birth_time_hours: float, sunrise_hours: float, sunset_hours: float) -> float:
    """
    Computes Nathonnatha (Diurnal/Nocturnal) Bala in Virupas.
    - Sun, Jupiter, Venus: Strong during day (60 virupas at solar noon).
    - Moon, Mars, Saturn: Strong during night (60 virupas at midnight).
    - Mercury: Always strong (60 virupas day and night).
    Source: BPHS 27.8-9 (docs/SOURCES.md section 10).
    """
    if planet == "Mercury":
        return 60.0
        
    is_day = sunrise_hours <= birth_time_hours <= sunset_hours
    day_planets = ["Sun", "Jupiter", "Venus"]
    
    if (planet in day_planets and is_day) or (planet not in day_planets and not is_day):
        return 60.0
    else:
        return 0.0

def compute_paksha_bala(planet: str, sun_lon: float, moon_lon: float) -> float:
    """
    Computes Paksha Bala (Lunar Phase Strength) in Virupas (0 to 60).
    - Angular separation between Sun and Moon (0° to 180° = Shukla Paksha, 180° to 360° = Krishna Paksha).
    - Benefics (Jupiter, Venus) get higher score in Shukla Paksha.
    - Malefics (Sun, Mars, Saturn) get higher score in Krishna Paksha.
    - Moon gets direct score = diff / 3.
    """
    diff = norm360(moon_lon - sun_lon)
    if diff > 180.0:
        shukla_val = (360.0 - diff) / 3.0
    else:
        shukla_val = diff / 3.0
        
    krishna_val = 60.0 - shukla_val
    
    if planet in ["Jupiter", "Venus"]:
        return round(shukla_val, 2)
    elif planet in ["Sun", "Mars", "Saturn"]:
        return round(krishna_val, 2)
    elif planet == "Moon":
        return round(shukla_val * 2.0, 2)
    else: # Mercury
        return 30.0

# ---------------------------------------------------------------------------
# Sthana Bala Sub-Components (Parasara BPHS Ch. 27; the full engine is shadbala_and_bhava_bala in engine.py)
# ---------------------------------------------------------------------------

def compute_ojayugmarasyamsa_bala(planet: str, rasi_sign: int, navamsha_sign: int) -> float:
    """
    Computes Ojayugmarasyamsa Bala (Odd/Even sign and Navamsha strength in Virupas).
    Source: BPHS 27.4.5 (docs/SOURCES.md section 10).
    Odd astrological signs (Aries=0, Gemini=2, Leo=4, Libra=6, Sag=8, Aqu=10).
    Even astrological signs (Taurus=1, Cancer=3, Virgo=5, Scorpio=7, Cap=9, Pisces=11).
    - Male planets (Sun, Mars, Jupiter, Mercury) get 15 virupas in odd Rasi, 15 in odd Navamsha (max 30).
    - Female planets (Moon, Venus, Saturn) get 15 virupas in even Rasi, 15 in even Navamsha (max 30).
    """
    is_odd_rasi = (rasi_sign % 2 == 0)
    is_odd_nav = (navamsha_sign % 2 == 0)
    score = 0.0
    if planet in ["Sun", "Mars", "Jupiter", "Mercury"]:
        if is_odd_rasi:
            score += 15.0
        if is_odd_nav:
            score += 15.0
    else:  # Moon, Venus, Saturn
        if not is_odd_rasi:
            score += 15.0
        if not is_odd_nav:
            score += 15.0
    return score

def compute_drekkana_bala(planet: str, longitude: float) -> float:
    """
    Computes Drekkana Bala (Decanate strength, 0 or 15 virupas).
    Source: BPHS 27.6 (docs/SOURCES.md section 10).
    Decanate 1 (0° - 10°): Male planets (Sun, Mars, Jupiter) get 15 virupas.
    Decanate 2 (10° - 20°): Neutral planets (Mercury, Saturn) get 15 virupas.
    Decanate 3 (20° - 30°): Female planets (Moon, Venus) get 15 virupas.
    """
    deg_in_sign = norm360(longitude) % 30.0
    if deg_in_sign < 10.0:
        return 15.0 if planet in ["Sun", "Mars", "Jupiter"] else 0.0
    elif deg_in_sign < 20.0:
        return 15.0 if planet in ["Mercury", "Saturn"] else 0.0
    else:
        return 15.0 if planet in ["Moon", "Venus"] else 0.0

def compute_saptavargaja_bala(
    planet: str,
    longitude: float,
    planetary_longitudes: Optional[Dict[str, float]] = None
) -> float:
    """
    Computes Saptavargaja Bala across the 7 classical vargas (D1, D2, D3, D7, D9, D12, D30).
    Source: BPHS 27.2-4 (docs/SOURCES.md section 10).
    In each varga:
    - Moolatrikona / Exalted: 45.0 virupas
    - Own sign: 30.0 virupas
    - Great Friend (Adhi Mitra): 20.0 virupas
    - Friend (Mitra): 15.0 virupas
    - Neutral (Sama): 10.0 virupas
    - Enemy (Shatru): 4.0 virupas
    - Great Enemy (Adhi Shatru): 2.0 virupas
    - Debilitated: 0.0 virupas
    """
    moolatrikona_signs = {
        "Sun": 4, "Moon": 1, "Mars": 0, "Mercury": 5,
        "Jupiter": 8, "Venus": 6, "Saturn": 10
    }
    vargas = compute_all_vargas(longitude)
    saptavarga_keys = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]
    total = 0.0

    ex_s, _ = EXALTATION.get(planet, (-1, 0))
    deb_s, _ = DEBILITATION.get(planet, (-1, 0))
    own_s = OWN_SIGNS.get(planet, [])
    mt_s = moolatrikona_signs.get(planet, -1)

    for vid in saptavarga_keys:
        if vid not in vargas:
            continue
        v_sign = vargas[vid].get("sign_index", 0)
        lord = SIGN_RULERS[v_sign]

        if v_sign == ex_s:
            pts = 45.0
        elif v_sign == deb_s:
            pts = 0.0
        elif v_sign == mt_s:
            pts = 45.0
        elif v_sign in own_s:
            pts = 30.0
        else:
            nat_rel = get_natural_relationship(planet, lord)
            if planetary_longitudes and lord in planetary_longitudes:
                p_s = int(norm360(longitude) // 30.0)
                l_s = int(norm360(planetary_longitudes[lord]) // 30.0)
                tat_rel = compute_tatkalika_relationship(p_s, l_s)
                if nat_rel == "Friend" and tat_rel == "Friend":
                    pts = 20.0  # Great Friend
                elif nat_rel == "Enemy" and tat_rel == "Enemy":
                    pts = 2.0   # Great Enemy
                elif (nat_rel == "Friend" and tat_rel == "Enemy") or (nat_rel == "Enemy" and tat_rel == "Friend"):
                    pts = 10.0  # Neutral
                elif nat_rel == "Friend" or tat_rel == "Friend":
                    pts = 15.0  # Friend
                elif nat_rel == "Enemy" or tat_rel == "Enemy":
                    pts = 4.0   # Enemy
                else:
                    pts = 10.0  # Neutral
            else:
                if nat_rel == "Friend":
                    pts = 15.0
                elif nat_rel == "Enemy":
                    pts = 4.0
                else:
                    pts = 10.0
        total += pts

    return round(total, 2)

# ---------------------------------------------------------------------------
# Kala Bala Sub-Components (Parasara BPHS Ch. 27; the full engine is shadbala_and_bhava_bala in engine.py)
# ---------------------------------------------------------------------------

def compute_tribhaga_bala(
    planet: str,
    birth_time_hours: float,
    sunrise_hours: float,
    sunset_hours: float
) -> float:
    """
    Computes Tribhaga Bala (Three-part day/night division strength) in Virupas.
    Source: BPHS 27.12 (docs/SOURCES.md section 10).
    - Day (sunrise to sunset) divided into 3 equal parts:
        Part 1: Jupiter (60)
        Part 2: Sun (60)
        Part 3: Saturn (60)
    - Night (sunset to next sunrise) divided into 3 equal parts:
        Part 1: Moon (60)
        Part 2: Venus (60)
        Part 3: Mars (60)
    Mercury always receives 60 virupas at all times.
    """
    if planet == "Mercury":
        return 60.0

    t = birth_time_hours % 24.0
    sr = sunrise_hours % 24.0
    ss = sunset_hours % 24.0

    is_day = (sr <= t < ss) if sr < ss else (t >= sr or t < ss)

    if is_day:
        day_length = (ss - sr) if ss > sr else (24.0 - sr + ss)
        elapsed = (t - sr) if t >= sr else (24.0 - sr + t)
        part = int((elapsed / max(day_length, 0.0001)) * 3.0)
        part = min(max(part, 0), 2)
        day_rulers = ["Jupiter", "Sun", "Saturn"]
        return 60.0 if planet == day_rulers[part] else 0.0
    else:
        night_length = (24.0 - ss + sr) if ss > sr else (sr - ss)
        elapsed = (t - ss) if t >= ss else (24.0 - ss + t)
        part = int((elapsed / max(night_length, 0.0001)) * 3.0)
        part = min(max(part, 0), 2)
        night_rulers = ["Moon", "Venus", "Mars"]
        return 60.0 if planet == night_rulers[part] else 0.0

def compute_temporal_lords_bala(
    planet: str,
    varsha_lord: Optional[str] = None,
    masa_lord: Optional[str] = None,
    dina_lord: Optional[str] = None,
    hora_lord: Optional[str] = None
) -> Dict[str, float]:
    """
    Computes strength awarded to temporal rulers:
    - Varsha Lord (Lord of the year): 15 virupas
    - Masa Lord (Lord of the month): 30 virupas
    - Dina Lord (Vaara Lord of the day): 45 virupas
    - Hora Lord (Lord of the planetary hour): 60 virupas
    Source: BPHS 27.13 (docs/SOURCES.md section 10).
    """
    v = 15.0 if planet == varsha_lord else 0.0
    m = 30.0 if planet == masa_lord else 0.0
    d = 45.0 if planet == dina_lord else 0.0
    h = 60.0 if planet == hora_lord else 0.0
    return {
        "varsha_bala": v,
        "masa_bala": m,
        "dina_bala": d,
        "hora_bala": h,
        "total_temporal_bala": v + m + d + h
    }

def compute_ayana_bala(
    planet: str,
    longitude: float,
    ayanamsa: float = 23.85
) -> float:
    """
    Computes Ayana Bala (Equinoctial / Seasonal strength in Virupas, 0 to 60).
    Source: BPHS 27.15-17 (docs/SOURCES.md section 10).
    Based on tropical declination:
    Sun, Mars, Jupiter, Venus, Mercury: strong in Northern declination (Uttarayana).
    Moon, Saturn: strong in Southern declination (Dakshinayana).
    """
    sayana_lon = norm360(longitude + ayanamsa)
    rad_lon = math.radians(sayana_lon)
    sin_delta = math.sin(math.radians(23.44)) * math.sin(rad_lon)
    delta = math.degrees(math.asin(max(min(sin_delta, 1.0), -1.0)))

    if planet in ["Sun", "Mars", "Jupiter", "Venus", "Mercury"]:
        virupas = 60.0 * (23.44 + delta) / 46.88
    else:  # Moon, Saturn
        virupas = 60.0 * (23.44 - delta) / 46.88

    virupas = max(0.0, min(60.0, virupas))
    if planet == "Sun":
        virupas = min(60.0, virupas * 2.0)
    return round(virupas, 2)

def compute_graha_yuddha_bala(
    planet_longitudes: Dict[str, float],
    planet_shadbala_pre_war: Dict[str, float],
    latitudes: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Computes Graha Yuddha (Planetary War) adjustments.
    Source: BPHS 27.20; the war itself SS 7.18-21 (docs/SOURCES.md section 10).
    Applies only to the 5 Taragrahas: Mars, Mercury, Jupiter, Venus, Saturn.
    Occurs when angular separation between two planets <= 1.0°.
    The victor gains points transferred from the loser.
    """
    taragrahas = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    adjustments = {p: 0.0 for p in PLANETS}

    active_combatants = [p for p in taragrahas if p in planet_longitudes]
    n = len(active_combatants)
    for i in range(n):
        p1 = active_combatants[i]
        lon1 = planet_longitudes[p1]
        for j in range(i + 1, n):
            p2 = active_combatants[j]
            lon2 = planet_longitudes[p2]

            diff = abs(norm360(lon1 - lon2))
            ang_dist = diff if diff <= 180.0 else 360.0 - diff
            if ang_dist <= 1.0:
                if p1 == "Venus":
                    winner, loser = p1, p2
                elif p2 == "Venus":
                    winner, loser = p2, p1
                else:
                    lat1 = latitudes.get(p1, 0.0) if latitudes else 0.0
                    lat2 = latitudes.get(p2, 0.0) if latitudes else 0.0
                    if lat1 != lat2:
                        winner, loser = (p1, p2) if lat1 > lat2 else (p2, p1)
                    else:
                        b1 = planet_shadbala_pre_war.get(p1, 0.0)
                        b2 = planet_shadbala_pre_war.get(p2, 0.0)
                        winner, loser = (p1, p2) if b1 >= b2 else (p2, p1)

                diff_points = abs(planet_shadbala_pre_war.get(winner, 0.0) - planet_shadbala_pre_war.get(loser, 0.0))
                transfer = round(diff_points * 0.5, 2)
                adjustments[winner] += transfer
                adjustments[loser] -= transfer

    return adjustments

# ---------------------------------------------------------------------------
# Cheshta Bala & Drik Bala (approximations of BPHS 27.18-19, 27.21-25; the full forms are in shadbala_and_bhava_bala)
# ---------------------------------------------------------------------------

def compute_cheshta_bala(
    planet: str,
    longitude: float,
    sun_longitude: float,
    is_retrograde: bool = False,
    speed_ratio: Optional[float] = None
) -> float:
    """
    Computes Cheshta Bala (Motional strength, 0 to 60 virupas).
    - Sun receives Ayana Bala.
    - Moon receives Paksha Bala.
    - Taragrahas (Mars, Mercury, Jupiter, Venus, Saturn):
      - Retrograde: 60.0 virupas.
      - Direct: proportional to elongation from Sun (opposition = 60.0).
    """
    if planet == "Sun":
        return compute_ayana_bala("Sun", longitude)
    elif planet == "Moon":
        return compute_paksha_bala("Moon", sun_longitude, longitude)

    if is_retrograde:
        return 60.0
    if speed_ratio is not None:
        return round(max(0.0, min(60.0, speed_ratio * 30.0)), 2)

    elongation = norm360(longitude - sun_longitude)
    if elongation > 180.0:
        elongation = 360.0 - elongation
    cheshta = (elongation / 180.0) * 60.0
    return round(max(7.5, min(60.0, cheshta)), 2)

def compute_drik_bala(
    target_planet: str,
    planet_longitudes: Dict[str, float]
) -> float:
    """
    Computes Drik Bala (Aspectual strength in Virupas) for target_planet.
    Aspects from benefics (Jupiter, Venus, Mercury, Moon) add virupas (+).
    Aspects from malefics (Sun, Mars, Saturn) reduce virupas (-).
    """
    target_lon = planet_longitudes.get(target_planet, 0.0)
    benefics = {"Jupiter", "Venus", "Mercury", "Moon"}
    malefics = {"Sun", "Mars", "Saturn"}
    total_drik = 0.0

    for aspecting_planet, lon in planet_longitudes.items():
        if aspecting_planet == target_planet or aspecting_planet not in PLANETS:
            continue
        diff = norm360(target_lon - lon)
        virupas = compute_parasara_drik_virupas(diff, aspecting_planet)
        net_virupas = virupas / 4.0
        if aspecting_planet in benefics:
            total_drik += net_virupas
        elif aspecting_planet in malefics:
            total_drik -= net_virupas

    return round(total_drik, 2)

# ---------------------------------------------------------------------------
# Master 6-fold Shadbala Engine
# ---------------------------------------------------------------------------

def compute_full_shadbala(
    planet_longitudes: Dict[str, float],
    lagna_lon: float,
    birth_time_hours: float,
    sunrise_hours: float,
    sunset_hours: float,
    varsha_lord: Optional[str] = None,
    masa_lord: Optional[str] = None,
    dina_lord: Optional[str] = None,
    hora_lord: Optional[str] = None,
    ayanamsa: float = 23.85,
    retrograde_status: Optional[Dict[str, bool]] = None,
    latitudes: Optional[Dict[str, float]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Computes complete 6-fold Shadbala for all 7 classical planets:
    1. Sthana Bala (Uchcha + Saptavargaja + Ojayugmarasyamsa + Kendradi + Drekkana)
    2. Dig Bala (Directional strength)
    3. Kala Bala (Nathonnatha + Paksha + Tribhaga + Temporal Lords + Ayana + Yuddha)
    4. Cheshta Bala (Motional strength)
    5. Naisargika Bala (Natural fixed strength)
    6. Drik Bala (Aspectual strength)
    Source: BPHS 27 (the six parts) (docs/SOURCES.md section 10).
    Returns scores in Virupas, Rupas (Virupas / 60), and % of required minimum.
    """
    sun_lon = planet_longitudes.get("Sun", 0.0)
    moon_lon = planet_longitudes.get("Moon", 0.0)

    # First pass: compute preliminary values
    prelim_res = {}
    for planet in PLANETS:
        lon = planet_longitudes.get(planet, 0.0)
        house = int(norm360(lon - lagna_lon) // 30.0) + 1
        rasi_sign = int(norm360(lon) // 30.0)
        nav_sign = compute_all_vargas(lon).get("D9", {}).get("sign_index", 0)

        # 1. Sthana Bala components
        uchcha = compute_uchcha_bala(planet, lon)
        saptavargaja = compute_saptavargaja_bala(planet, lon, planet_longitudes)
        ojayugma = compute_ojayugmarasyamsa_bala(planet, rasi_sign, nav_sign)
        kendradi = compute_kendradi_bala(house)
        drekkana = compute_drekkana_bala(planet, lon)
        sthana = round(uchcha + saptavargaja + ojayugma + kendradi + drekkana, 2)

        # 2. Dig Bala
        dig = round(compute_dig_bala(planet, lon, lagna_lon), 2)

        # 3. Kala Bala preliminary components
        natho = compute_nathonnatha_bala(planet, birth_time_hours, sunrise_hours, sunset_hours)
        paksha = compute_paksha_bala(planet, sun_lon, moon_lon)
        tribhaga = compute_tribhaga_bala(planet, birth_time_hours, sunrise_hours, sunset_hours)
        temp_dict = compute_temporal_lords_bala(planet, varsha_lord, masa_lord, dina_lord, hora_lord)
        temporal = temp_dict["total_temporal_bala"]
        ayana = compute_ayana_bala(planet, lon, ayanamsa)
        kala_pre = round(natho + paksha + tribhaga + temporal + ayana, 2)

        # 4. Cheshta Bala
        is_retro = retrograde_status.get(planet, False) if retrograde_status else False
        cheshta = round(compute_cheshta_bala(planet, lon, sun_lon, is_retrograde=is_retro), 2)

        # 5. Naisargika Bala
        naisargika = NAISARGIKA_BALA.get(planet, 10.0)

        # 6. Drik Bala
        drik = round(compute_drik_bala(planet, planet_longitudes), 2)

        pre_total = sthana + dig + kala_pre + cheshta + naisargika + drik
        prelim_res[planet] = {
            "sthana": sthana,
            "sthana_breakdown": {
                "uchcha": uchcha,
                "saptavargaja": saptavargaja,
                "ojayugmarasyamsa": ojayugma,
                "kendradi": kendradi,
                "drekkana": drekkana
            },
            "dig": dig,
            "kala_pre": kala_pre,
            "kala_components": {
                "nathonnatha": natho,
                "paksha": paksha,
                "tribhaga": tribhaga,
                "temporal": temp_dict,
                "ayana": ayana
            },
            "cheshta": cheshta,
            "naisargika": naisargika,
            "drik": drik,
            "pre_total": pre_total,
            "uchcha_raw": uchcha
        }

    # Graha Yuddha (Planetary War) adjustments
    pre_war_totals = {p: prelim_res[p]["pre_total"] for p in PLANETS}
    yuddha_adjustments = compute_graha_yuddha_bala(planet_longitudes, pre_war_totals, latitudes)

    res = {}
    for planet in PLANETS:
        p_data = prelim_res[planet]
        yuddha = yuddha_adjustments.get(planet, 0.0)
        kala = round(p_data["kala_pre"] + yuddha, 2)
        p_data["kala_components"]["yuddha"] = yuddha

        total_virupas = round(
            p_data["sthana"] + p_data["dig"] + kala + p_data["cheshta"] + p_data["naisargika"] + p_data["drik"],
            2
        )
        total_rupas = round(total_virupas / 60.0, 2)

        req = SHADBALA_REQUIREMENTS.get(planet, 300.0)
        ratio = round((total_virupas / req) * 100.0, 1)

        # Parasara Ishta / Kashta Phala
        ishta_phala, kashta_phala = compute_ishta_kashta_parasara(p_data["uchcha_raw"], p_data["cheshta"])

        res[planet] = {
            "sthana_bala": p_data["sthana"],
            "sthana_breakdown": p_data["sthana_breakdown"],
            "dig_bala": p_data["dig"],
            "kala_bala": kala,
            "kala_breakdown": p_data["kala_components"],
            "cheshta_bala": p_data["cheshta"],
            "naisargika_bala": p_data["naisargika"],
            "drik_bala": p_data["drik"],
            "total_virupas": total_virupas,
            "total_rupas": total_rupas,
            "required_virupas": req,
            "percent_strength": ratio,
            "is_strong": total_virupas >= req,
            "ishta_phala": ishta_phala,
            "kashta_phala": kashta_phala
        }

    return res




def compute_ishta_kashta_parasara(uchcha_bala: float, cheshta_bala: float) -> Tuple[float, float]:
    """
    Parasara classical formula for Ishta Phala and Kashta Phala:
    - Ishta Phala = sqrt(Uchcha_Bala * Cheshta_Bala)
    - Kashta Phala = sqrt((60 - Uchcha_Bala) * (60 - Cheshta_Bala))
    Values range from 0 to 60.
    """
    u = max(0.0, min(60.0, uchcha_bala))
    c = max(0.0, min(60.0, cheshta_bala))
    ishta = round(math.sqrt(u * c), 2)
    kashta = round(math.sqrt((60.0 - u) * (60.0 - c)), 2)
    return ishta, kashta


NATURAL_BENEFICS = {"Jupiter", "Venus", "Moon", "Mercury"}
