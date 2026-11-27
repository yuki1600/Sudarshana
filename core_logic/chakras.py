"""
core_logic/chakras.py
=====================
Modularized Calculation Engine and Visual Layout Generators for Classical Vedic Chakras.
Sources (docs/SOURCES.md section 17): Sarvatobhadra PD 26.48 and PVR 26.8, the 28 stars PVR ch. 25; Sudarshana
BPHS 74; the stars over the body's limbs PD 26.35-40; Kurma BS 14 (see ``KURMA_CHAKRA_REGIONS``); Kota, Kalanala,
Shoola and Tripataki as taught in the Svarodaya tradition (Narapati's), no verse checked.


Supported Chakras:
1. Sarvatobhadra Chakra (SBC): 9x9 Grid (81 cells), 28 Nakshatras (with Abhijit),
   Consonants, Vowels, Rasis, and 4 Types of Vedha (Frontal, Right, Left, Corner).
2. Kota Chakra (Fortress Chakra): 4 Concentric Divisions (Stambha, Madhya, Prakaara, Bahya),
   Kota Swami, Kota Pala, Pravesha (Entry) vs Nirgamana (Exit) Roads.
3. Sudarshana Chakra: 3 Concentric Wheels (Lagna, Moon, Sun) unifying physical,
   emotional, and spiritual houses into a single 12-house diagnostic wheel.
4. Kalachakra (Directional Wheel): 8 Spokes, 28 Nakshatras, Special Transit Points
   (Janma, Karma, Sanghatika, Samudayika, Vainashika, Manasa).
5. Surya Kalanal & Chandra Kalanal Chakras: Solar and Lunar battle/conflict transit wheels.

"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Any

from .natal_chart import norm360, NAKSHATRA_NAMES, RASI_NAMES_EN

# 28 Nakshatras of Sarvatobhadra Chakra (including Abhijit):
SBC_28_NAKSHATRAS = [
    "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Svati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Abhijit", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati", "Ashwini", "Bharani"
]

# Coordinate mapping in 9x9 Sarvatobhadra Grid:
NAKSHATRA_TO_SBC_COORD = {
    "Krittika": (1, 0), "Rohini": (2, 0), "Mrigashira": (3, 0), "Ardra": (4, 0), "Punarvasu": (5, 0), "Pushya": (6, 0), "Ashlesha": (7, 0),
    "Magha": (8, 1), "Purva Phalguni": (8, 2), "Uttara Phalguni": (8, 3), "Hasta": (8, 4), "Chitra": (8, 5), "Svati": (8, 6), "Vishakha": (8, 7),
    "Anuradha": (7, 8), "Jyeshtha": (6, 8), "Mula": (5, 8), "Purva Ashadha": (4, 8), "Uttara Ashadha": (3, 8), "Abhijit": (2, 8), "Shravana": (1, 8),
    "Dhanishta": (0, 7), "Shatabhisha": (0, 6), "Purva Bhadrapada": (0, 5), "Uttara Bhadrapada": (0, 4), "Revati": (0, 3), "Ashwini": (0, 2), "Bharani": (0, 1)
}

# ===========================================================================
# 1. Sarvatobhadra Chakra (SBC) Engine & 9x9 Layout Generator
# ===========================================================================

def compute_sarvatobhadra_vedhas(planet_nakshatra: str) -> Dict[str, Any]:
    """
    Computes the 4 classical cross-aspects (Vedhas) cast by a planet in SBC:
    1. Samukha Vedha (Direct / Opposite Frontal Vedha, distance = 14)
    2. Dakshina Vedha (Right Lateral Diagonal Vedha, distance = +7)
    3. Vama Vedha (Left Lateral Diagonal Vedha, distance = -7)
    4. Kona Vedha (Corner / Trinal Vedha)
    """
    if planet_nakshatra not in NAKSHATRA_TO_SBC_COORD:
        return {"error": f"Unknown nakshatra {planet_nakshatra}"}
        
    x, y = NAKSHATRA_TO_SBC_COORD[planet_nakshatra]
    idx = SBC_28_NAKSHATRAS.index(planet_nakshatra)
    
    samukha_nak = SBC_28_NAKSHATRAS[(idx + 14) % 28]
    dakshina_nak = SBC_28_NAKSHATRAS[(idx + 7) % 28]
    vama_nak = SBC_28_NAKSHATRAS[(idx - 7) % 28]
    kona_nak = SBC_28_NAKSHATRAS[(idx + 21) % 28]
    
    return {
        "aspecting_nakshatra": planet_nakshatra,
        "grid_coordinate": (x, y),
        "samukha_vedha": samukha_nak,
        "dakshina_vedha": dakshina_nak,
        "vama_vedha": vama_nak,
        "kona_vedha": kona_nak,
        "vedha_summary": (
            f"{planet_nakshatra} casts Frontal Vedha on {samukha_nak}, "
            f"Right Vedha on {dakshina_nak}, Left Vedha on {vama_nak}, and Corner Vedha on {kona_nak}."
        )
    }

def generate_sarvatobhadra_grid_data() -> List[List[Dict[str, Any]]]:
    """
    Constructs the canonical 9x9 (81-cell) Sarvatobhadra matrix with Nakshatras on perimeter,
    Rasis in 2nd layer, Consonants in 3rd layer, and Vowels at the core.
    """
    grid: List[List[Dict[str, Any]]] = [[{} for _ in range(9)] for _ in range(9)]
    
    # 1. Fill Perimeter Nakshatras
    for nak, (x, y) in NAKSHATRA_TO_SBC_COORD.items():
        grid[y][x] = {"type": "Nakshatra", "label": nak, "short": nak[:3]}
        
    # 2. Four Corners
    grid[0][0] = {"type": "Corner", "label": "NE Corner", "short": "NE"}
    grid[0][8] = {"type": "Corner", "label": "SE Corner", "short": "SE"}
    grid[8][8] = {"type": "Corner", "label": "SW Corner", "short": "SW"}
    grid[8][0] = {"type": "Corner", "label": "NW Corner", "short": "NW"}
    
    # 3. Inner Rasis & Consonants (Ring 2)
    inner_labels = [
        (1, 1, "Vrishabha (Taurus)"), (1, 2, "A"), (1, 3, "U"), (1, 4, "Mithuna (Gemini)"),
        (1, 5, "Ka"), (1, 6, "Karka (Cancer)"), (1, 7, "Simha (Leo)"),
        (2, 7, "Kanya (Virgo)"), (3, 7, "Tula (Libra)"), (4, 7, "Vrischika (Scorpio)"),
        (5, 7, "Dhanus (Sagittarius)"), (6, 7, "Makara (Capricorn)"), (7, 7, "Kumbha (Aquarius)"),
        (7, 6, "Meena (Pisces)"), (7, 5, "Mesha (Aries)"), (7, 4, "Ta"), (7, 3, "Tha"),
        (7, 2, "Da"), (7, 1, "Dha"), (6, 1, "Na"), (5, 1, "Pa"), (4, 1, "Pha"),
        (3, 1, "Ba"), (2, 1, "Bha")
    ]
    for y, x, lbl in inner_labels:
        grid[y][x] = {"type": "Internal", "label": lbl, "short": lbl[:3]}
        
    # 4. Central Core Cells
    for cy in range(2, 7):
        for cx in range(2, 7):
            if not grid[cy][cx]:
                grid[cy][cx] = {"type": "Core", "label": f"Brahma ({cx},{cy})", "short": "BR"}
                
    return grid

def render_sarvatobhadra_ascii_grid() -> str:
    """Renders the 9x9 Sarvatobhadra Grid in readable text/ASCII format."""
    grid = generate_sarvatobhadra_grid_data()
    lines = ["+-----+-----+-----+-----+-----+-----+-----+-----+-----+"]
    for row in grid:
        row_str = "|" + "|".join(f"{c.get('short', '   '):^5}" for c in row) + "|"
        lines.append(row_str)
        lines.append("+-----+-----+-----+-----+-----+-----+-----+-----+-----+")
    return "\n".join(lines)


# ===========================================================================
# 2. Kota Chakra (Fortress Chakra) Engine
# ===========================================================================

def compute_kota_chakra_structure(
    janma_nakshatra_idx: int,
    planet_nakshatras: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Constructs the 4 concentric regions of Kota Chakra from native's Janma Nakshatra:
    - Stambha (Center): 4 Nakshatras (Inner sanctum / seat of vitality)
    - Madhya (Middle): 4 Nakshatras (Inner defense courtyard)
    - Prakaara (Walls): 8 Nakshatras (Ramparts and fortifications)
    - Bahya (Outside): 11 Nakshatras (Surrounding territory)
    
    Assigns Kota Swami (Lord of the Fort) and Kota Pala (Guardian of the Fort).
    """
    nak_list = NAKSHATRA_NAMES  # 27 standard nakshatras
    j_idx = janma_nakshatra_idx % 27
    
    stambha_indices = [(j_idx) % 27, (j_idx + 7) % 27, (j_idx + 14) % 27, (j_idx + 21) % 27]
    madhya_indices = [(j_idx + 1) % 27, (j_idx + 8) % 27, (j_idx + 15) % 27, (j_idx + 22) % 27]
    prakaara_indices = [
        (j_idx + 2) % 27, (j_idx + 6) % 27,
        (j_idx + 9) % 27, (j_idx + 13) % 27,
        (j_idx + 16) % 27, (j_idx + 20) % 27,
        (j_idx + 23) % 27, (j_idx + 26) % 27
    ]
    
    stambha = [nak_list[i] for i in stambha_indices]
    madhya = [nak_list[i] for i in madhya_indices]
    prakaara = [nak_list[i] for i in prakaara_indices]
    bahya = [n for n in nak_list if n not in stambha and n not in madhya and n not in prakaara]
    
    # Analyze planetary distribution across fortress
    zone_planets = {"stambha": [], "madhya": [], "prakaara": [], "bahya": []}
    if planet_nakshatras:
        for p, n_idx in planet_nakshatras.items():
            nak_name = nak_list[n_idx % 27]
            if nak_name in stambha:
                zone_planets["stambha"].append(p)
            elif nak_name in madhya:
                zone_planets["madhya"].append(p)
            elif nak_name in prakaara:
                zone_planets["prakaara"].append(p)
            else:
                zone_planets["bahya"].append(p)

    return {
        "stambha": stambha,
        "madhya": madhya,
        "prakaara": prakaara,
        "bahya": bahya,
        "stambha_nakshatras": stambha,
        "madhya_nakshatras": madhya,
        "prakaara_nakshatras": prakaara,
        "bahya_nakshatras": bahya,
        "kota_swami_role": "Lord of the Fort (governs central Stambha)",
        "kota_pala_role": "Guardian of the Fort (guards outer ramparts)",
        "zone_occupants": zone_planets,
        "defense_evaluation": (
            "Fortress Secure: Stambha is guarded by benefics."
            if not any(p in ("Mars", "Saturn", "Rahu", "Ketu") for p in zone_planets["stambha"])
            else "Fortress Under Siege: Malefics penetrated central Stambha!"
        )
    }


# ===========================================================================
# 3. Sudarshana Chakra Engine (Concentric Lagna, Moon, Sun Wheels)
# ===========================================================================

def compute_sudarshana_chakra(
    lagna_sign: int,
    moon_sign: int,
    sun_sign: int,
    planet_signs: Dict[str, int]
) -> Dict[str, Any]:
    """
    Constructs the 3 concentric 12-house Sudarshana Chakra:
    - Wheel 1 (Physical / Deha): Lagna
    - Wheel 2 (Mind / Jeeva): Moon
    - Wheel 3 (Soul / Atma): Sun
    Unifies the three fundamental reference points into a single 12-house diagnostic.
    """
    houses = {}
    benefics = {"Jupiter", "Venus", "Moon", "Mercury"}
    malefics = {"Mars", "Saturn", "Sun", "Rahu", "Ketu"}
    
    for h in range(1, 13):
        l_sign = (lagna_sign + h - 1) % 12
        m_sign = (moon_sign + h - 1) % 12
        s_sign = (sun_sign + h - 1) % 12
        
        # Planets in corresponding sign of each wheel
        p_lagna = [p for p, s in planet_signs.items() if s == l_sign]
        p_moon = [p for p, s in planet_signs.items() if s == m_sign]
        p_sun = [p for p, s in planet_signs.items() if s == s_sign]
        
        total_b = sum(1 for p in p_lagna + p_moon + p_sun if p in benefics)
        total_m = sum(1 for p in p_lagna + p_moon + p_sun if p in malefics)
        
        net_strength = "Highly Fortified" if total_b > total_m else ("Afflicted" if total_m > total_b else "Balanced")
        
        houses[h] = {
            "house_number": h,
            "physical_wheel_sign": RASI_NAMES_EN[l_sign],
            "physical_occupants": p_lagna,
            "emotional_wheel_sign": RASI_NAMES_EN[m_sign],
            "emotional_occupants": p_moon,
            "spiritual_wheel_sign": RASI_NAMES_EN[s_sign],
            "spiritual_occupants": p_sun,
            "net_house_status": net_strength
        }
        
    return {
        "chakra_type": "Sudarshana Chakra",
        "description": "3 concentric 12-house wheels unifying Lagna (Body), Moon (Mind), and Sun (Soul)",
        "houses": houses
    }


# ===========================================================================
# 4. Kalachakra (Directional Wheel of Time)
# ===========================================================================

DIRECTIONAL_SPOKES = [
    "East (Indra / Purva)",
    "South-East (Agni / Agneya)",
    "South (Yama / Dakshina)",
    "South-West (Nirriti / Nairritya)",
    "West (Varuna / Paschima)",
    "North-West (Vayu / Vayavya)",
    "North (Kubera / Uttara)",
    "North-East (Ishana / Aishanya)"
]

def compute_kalachakra_directional_wheel(
    janma_nakshatra_idx: int
) -> Dict[str, Any]:
    """
    Constructs the 8-directional Kalachakra spoke wheel mapping 28 nakshatras,
    and isolates critical transit sensitive asterisms:
    - Janma Nakshatra (1st: Physical Self)
    - Karma Nakshatra (10th: Occupation & Worldly Duty)
    - Sanghatika (16th: Alliance & Destruction of Wealth)
    - Samudayika (18th: Collective Karma & Family Welfare)
    - Vainashika (23rd: Critical Crisis & Danger)
    - Manasa (25th: Mental Equilibrium & Stability)
    - Rajyabhisheka (26th: Sovereign Power & Coronation)
    """
    nak_list = NAKSHATRA_NAMES
    j_idx = janma_nakshatra_idx % 27
    
    sensitive_points = {
        "Janma (Self & Body)": nak_list[j_idx],
        "Karma (10th - Profession & Actions)": nak_list[(j_idx + 9) % 27],
        "Sanghatika (16th - Partnerships & Assets)": nak_list[(j_idx + 15) % 27],
        "Samudayika (18th - Family & Communal Karma)": nak_list[(j_idx + 17) % 27],
        "Vainashika (23rd - Peril & Mortality)": nak_list[(j_idx + 22) % 27],
        "Manasa (25th - Mental Peace)": nak_list[(j_idx + 24) % 27],
        "Rajyabhisheka (26th - Authority & Victory)": nak_list[(j_idx + 25) % 27],
        "Desha (27th - Native Homeland)": nak_list[(j_idx + 26) % 27]
    }
    
    # Distribute nakshatras across 8 cardinal/diagonal spokes
    spoke_map = {}
    for i, spoke in enumerate(DIRECTIONAL_SPOKES):
        spoke_naks = [nak_list[(j_idx + i + (j * 8)) % 27] for j in range(3)]
        spoke_map[spoke] = spoke_naks
        
    return {
        "chakra_type": "Kalachakra (Directional Wheel of Time)",
        "directional_spokes": spoke_map,
        "sensitive_nakshatra_points": sensitive_points
    }


# ===========================================================================
# 5. Surya Kalanal & Chandra Kalanal Chakras
# ===========================================================================

def compute_surya_kalanal_chakra(
    sun_nakshatra_idx: int,
    transit_nakshatras: Dict[str, int]
) -> Dict[str, Any]:
    """
    Surya Kalanal Chakra (Sun's Cosmic Fire Wheel):
    Used for political conflicts, litigation, elections, and military battles.
    The Sun's transit nakshatra is placed at the Hub (Center).
    Remaining 27 nakshatras radiate outward along 4 cardinal and 4 diagonal rays.
    """
    nak_list = NAKSHATRA_NAMES
    s_idx = sun_nakshatra_idx % 27
    center_nak = nak_list[s_idx]
    
    # Assess planets placed at the central hub with Sun
    hub_occupants = [p for p, n in transit_nakshatras.items() if n % 27 == s_idx]
    
    return {
        "chakra_type": "Surya Kalanal Chakra",
        "central_hub_nakshatra": center_nak,
        "hub_occupants": hub_occupants,
        "evaluation": (
            "Sun is solitary at the hub: Royal triumph and authoritative supremacy."
            if not hub_occupants
            else f"Hub occupied by {hub_occupants}: Fierce struggle and contention for authority."
        )
    }

def compute_chandra_kalanal_chakra(
    moon_nakshatra_idx: int,
    transit_nakshatras: Dict[str, int]
) -> Dict[str, Any]:
    """
    Chandra Kalanal Chakra (Moon's Cosmic Fire Wheel):
    Used for psychological peace, health, emotional stability, and mass sentiment.
    Moon's natal or transiting nakshatra is placed at the Hub (Center).
    Benefics at the hub bring tranquility and comfort; malefics at the hub bring anxiety and distress.
    """
    nak_list = NAKSHATRA_NAMES
    m_idx = moon_nakshatra_idx % 27
    center_nak = nak_list[m_idx]

    hub_occupants = [p for p, n in transit_nakshatras.items() if n % 27 == m_idx and p != "Moon"]
    malefics_at_hub = [p for p in hub_occupants if p in ["Mars", "Saturn", "Rahu", "Ketu", "Sun"]]
    benefics_at_hub = [p for p in hub_occupants if p in ["Jupiter", "Venus", "Mercury"]]

    return {
        "chakra_type": "Chandra Kalanal Chakra",
        "central_hub_nakshatra": center_nak,
        "hub_occupants": hub_occupants,
        "malefics_at_hub": malefics_at_hub,
        "benefics_at_hub": benefics_at_hub,
        "evaluation": (
            "Severe Mental/Emotional Agitation: Malefics afflict the Moon's Kalanal hub!"
            if malefics_at_hub
            else ("Fortified Peace and Auspicious Ease: Benefics grace the central hub."
                  if benefics_at_hub else "Serene & Unafflicted: Moon rules the hub peacefully.")
        )
    }


# ===========================================================================
# 6. Kurma Chakra Engine (Earth / Tortoise Wheel)
# BS 14 (Kurma-vibhaga) groups the stars in threes from Krittika, the first three in the middle, then east,
# south-east ... north-east.  This table is grouped differently (four stars in the middle, Ashwini-Krittika in the
# north-east); the app's Chakras page draws BS 14's grouping (server/chakras.py).
# ===========================================================================

KURMA_CHAKRA_REGIONS = {
    "Center (Kukshi / Heart)": [3, 4, 5, 6],           # Rohini, Mrigashira, Ardra, Punarvasu
    "East (Mukha / Face)": [7, 8, 9],                  # Pushya, Ashlesha, Magha
    "South-East (Agneya / Right Foreleg)": [10, 11, 12],# Purva Phalguni, Uttara Phalguni, Hasta
    "South (Dakshina / Right Flank)": [13, 14, 15],     # Chitra, Swati, Vishakha
    "South-West (Nairritya / Right Hindleg)": [16, 17, 18],# Anuradha, Jyeshtha, Mula
    "West (Puccha / Tail)": [19, 20, 27],              # Purva Ashadha, Uttara Ashadha, Abhijit (27)
    "North-West (Vayavya / Left Hindleg)": [21, 22, 23],# Shravana, Dhanishta, Shatabhisha
    "North (Uttara / Left Flank)": [24, 25, 26],       # Purva Bhadrapada, Uttara Bhadrapada, Revati
    "North-East (Ishanya / Left Foreleg)": [0, 1, 2]   # Ashwini, Bharani, Krittika
}

def compute_kurma_chakra(
    transit_nakshatras: Dict[str, int]
) -> Dict[str, Any]:
    """
    Computes Kurma Chakra (Earth Tortoise Wheel) transit mapping across 9 geopolitical sectors (BS 14; see the
    table's note).
    Maps transiting celestial bodies to the 9 compass directions / organs of the Earth Kurma.
    """
    region_occupants = {region: [] for region in KURMA_CHAKRA_REGIONS}

    for planet, n_idx in transit_nakshatras.items():
        nak_28 = n_idx % 28
        for region, naks in KURMA_CHAKRA_REGIONS.items():
            if nak_28 in naks or (nak_28 % 27) in naks:
                region_occupants[region].append(planet)
                break

    afflicted_regions = []
    benefic_regions = []
    for region, occupants in region_occupants.items():
        has_malefic = any(p in ["Mars", "Saturn", "Rahu", "Ketu", "Sun"] for p in occupants)
        has_benefic = any(p in ["Jupiter", "Venus", "Moon", "Mercury"] for p in occupants)
        if has_malefic:
            afflicted_regions.append(region)
        if has_benefic:
            benefic_regions.append(region)

    return {
        "chakra_type": "Kurma Chakra (Earth Tortoise Wheel)",
        "region_occupants": region_occupants,
        "afflicted_regions": afflicted_regions,
        "benefic_regions": benefic_regions,
        "summary": f"{len(afflicted_regions)} sectors under tension/earth tremor or conflict risk; {len(benefic_regions)} sectors fortified."
    }


# ===========================================================================
# 7. Tripataki Chakra Engine (3-Flag Annual Vedha Wheel)
# The Tripataki chakra of the Varshaphala (annual) tradition; no verse checked
# ===========================================================================

def compute_tripataki_chakra(
    natal_moon_nak_idx: int,
    natal_lagna_nak_idx: int,
    natal_sun_nak_idx: int,
    transit_nakshatras: Dict[str, int]
) -> Dict[str, Any]:
    """
    Computes Tripataki Chakra (3-Flag Varshaphal Transit Vedha Wheel).
    Erects 3 Patakas (Flags):
    - Moon Flag (Natal Moon Star): Emotional balance & health
    - Lagna Flag (Natal Lagna Star): Vitality & social prestige
    - Sun Flag (Natal Sun Star): Soul power & professional authority
    
    Casts 3 Vedha rays from transiting planets:
    - Direct Frontal (Samukha Vedha): Opposite nakshatra (+14)
    - Left Diagonal (Vama Vedha): -7 nakshatras
    - Right Diagonal (Dakshina Vedha): +7 nakshatras
    """
    flags = {
        "Moon Flag (Health & Mind)": natal_moon_nak_idx % 27,
        "Lagna Flag (Body & Honor)": natal_lagna_nak_idx % 27,
        "Sun Flag (Soul & Status)": natal_sun_nak_idx % 27
    }
    
    flag_vedhas = {f_name: {"malefics": [], "benefics": [], "details": []} for f_name in flags}
    
    malefic_names = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
    benefic_names = {"Jupiter", "Venus", "Mercury", "Moon"}
    
    for f_name, f_nak in flags.items():
        # Vedha trigger nakshatras for this flag:
        # Samukha (+14), Vama (-7), Dakshina (+7)
        samukha = (f_nak + 14) % 27
        vama = (f_nak - 7) % 27
        dakshina = (f_nak + 7) % 27
        
        target_map = {
            samukha: "Samukha Vedha (Direct Frontal)",
            vama: "Vama Vedha (Left Diagonal)",
            dakshina: "Dakshina Vedha (Right Diagonal)",
            f_nak: "Sannidhi Vedha (Conjunction on Flag)"
        }
        
        for p, p_nak in transit_nakshatras.items():
            p_nak_27 = p_nak % 27
            if p_nak_27 in target_map:
                ray_type = target_map[p_nak_27]
                is_m = p in malefic_names
                if is_m:
                    flag_vedhas[f_name]["malefics"].append(p)
                else:
                    flag_vedhas[f_name]["benefics"].append(p)
                    
                flag_vedhas[f_name]["details"].append({
                    "planet": p,
                    "nature": "Malefic" if is_m else "Benefic",
                    "ray": ray_type,
                    "transit_nakshatra": NAKSHATRA_NAMES[p_nak_27]
                })
                
    # Overall summary assessment
    annual_alerts = []
    for f_name, data in flag_vedhas.items():
        if data["malefics"] and not data["benefics"]:
            annual_alerts.append(f"Vulnerable: {f_name} afflicted by {', '.join(data['malefics'])} without benefic relief!")
        elif data["benefics"] and not data["malefics"]:
            annual_alerts.append(f"Fortified: {f_name} blessed by {', '.join(data['benefics'])} rays.")
            
    return {
        "chakra_type": "Tripataki Chakra (3-Flag Varshaphal Wheel)",
        "flags": {k: NAKSHATRA_NAMES[v] for k, v in flags.items()},
        "vedha_breakdown": flag_vedhas,
        "annual_alerts": annual_alerts
    }


# ===========================================================================
# 8. Shoola Chakra Engine (3-Prong Trident Bodily Affliction Wheel)
# The Shoola chakra of the Svarodaya tradition; no verse checked
# ===========================================================================

SHOOLA_ANATOMY = {
    "Left Prong (Vama Shoola)": {
        "nak_offsets": [-6, -5, -4, -3],
        "limbs": ["Right Hand", "Right Leg", "Right Eye", "Face"]
    },
    "Center Prong (Madhya Shoola)": {
        "nak_offsets": [-1, 0, 1],  # 0 is Janma Nakshatra
        "limbs": ["Head", "Chest / Heart", "Stomach", "Privities"]
    },
    "Right Prong (Dakshina Shoola)": {
        "nak_offsets": [3, 4, 5, 6],
        "limbs": ["Left Hand", "Left Leg", "Left Eye", "Back"]
    }
}

def compute_shoola_chakra(
    janma_nakshatra_idx: int,
    transit_nakshatras: Dict[str, int]
) -> Dict[str, Any]:
    """
    Computes Shoola Chakra (Trident Bodily Affliction Wheel).
    Maps human anatomy across 3 prongs of the trident relative to Janma Nakshatra.
    Identifies vulnerable physical organs and injury/disease warnings.
    """
    j_nak = janma_nakshatra_idx % 27
    prong_occupants = {prong: {"malefics": [], "benefics": [], "limbs": data["limbs"]} for prong, data in SHOOLA_ANATOMY.items()}
    
    malefic_names = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
    
    for prong, p_data in SHOOLA_ANATOMY.items():
        prong_naks = [(j_nak + off) % 27 for off in p_data["nak_offsets"]]
        for planet, p_nak in transit_nakshatras.items():
            p_nak_27 = p_nak % 27
            if p_nak_27 in prong_naks:
                if planet in malefic_names:
                    prong_occupants[prong]["malefics"].append(planet)
                else:
                    prong_occupants[prong]["benefics"].append(planet)
                    
    vulnerabilities = []
    for prong, data in prong_occupants.items():
        if data["malefics"]:
            vulnerabilities.append({
                "prong": prong,
                "afflicting_malefics": data["malefics"],
                "vulnerable_limbs": data["limbs"]
            })
            
    return {
        "chakra_type": "Shoola Chakra (Trident Bodily Affliction Wheel)",
        "janma_nakshatra": NAKSHATRA_NAMES[j_nak],
        "prongs": prong_occupants,
        "physical_vulnerabilities": vulnerabilities,
        "status": (
            f"Caution: Malefic spikes detected on {len(vulnerabilities)} trident prongs!"
            if vulnerabilities else "All 3 prongs serene and free of malefic attack."
        )
    }

# ---------------------------------------------------------------------------
# 9. Lagna-Based Navatara & Special Nakshatras Subsystem
# The nine taras (PVR 26.4.1) and the special nakshatras (PVR 26.4.2) counted from the
# lagna's nakshatra instead of the Moon's, as the options 'Nava Taras (from lagna)', 'Special Taras/Nakshatras
# (from lagna)' and 'Aspects on special nakshatras (lagna)' show them
# ---------------------------------------------------------------------------

NAVATARA_NAMES = [
    "Janma (Birth/Body)",
    "Sampat (Wealth/Prosperity)",
    "Vipat (Danger/Peril)",
    "Kshema (Well-being/Security)",
    "Pratyak (Obstacles/Resistance)",
    "Sadhana (Accomplishment/Achievement)",
    "Naidhana (Destruction/Mortality)",
    "Mitra (Friendship/Allies)",
    "Parama Mitra (Supreme Benefactor)"
]

def compute_lagna_navatara_and_special_nakshatras(
    lagna_nakshatra_idx: int
) -> Dict[str, Any]:
    """
    Computes Navatara (9-Taras across 3 cycles = 27 nakshatras) and Special Sensitive Asterisms
    reckoned from the Ascendant (Lagna) Nakshatra rather than Moon Nakshatra.
    Essential for evaluating transits on the native's physical status, health, and worldly throne.
    """
    nak_list = NAKSHATRA_NAMES
    l_idx = lagna_nakshatra_idx % 27
    
    # 9 Special Asterisms from Lagna
    special_points_lagna = {
        "Janma (Lagna Body Star)": nak_list[l_idx],
        "Karma (10th - Throne & Authority)": nak_list[(l_idx + 9) % 27],
        "Sanghatika (16th - Material Foundation)": nak_list[(l_idx + 15) % 27],
        "Samudayika (18th - Social Domain)": nak_list[(l_idx + 17) % 27],
        "Vainashika (23rd - Severe Hazard)": nak_list[(l_idx + 22) % 27],
        "Manasa (25th - Outer Intellect)": nak_list[(l_idx + 24) % 27],
        "Rajyabhisheka (26th - Sovereign Coronation)": nak_list[(l_idx + 25) % 27],
        "Desha (27th - Homeland & Territory)": nak_list[(l_idx + 26) % 27]
    }
    
    # 27 Nakshatras categorized into 9 Navatara groups from Lagna
    tara_groups = {name: [] for name in NAVATARA_NAMES}
    for i in range(27):
        target_nak_idx = (l_idx + i) % 27
        tara_idx = i % 9
        cycle_idx = (i // 9) + 1  # Cycle 1: Pratyaksha, Cycle 2: Madhyama, Cycle 3: Adhana
        tara_name = NAVATARA_NAMES[tara_idx]
        tara_groups[tara_name].append({
            "cycle": cycle_idx,
            "nakshatra_index": target_nak_idx,
            "nakshatra_name": nak_list[target_nak_idx]
        })
        
    return {
        "reference": "Ascendant (Lagna)",
        "lagna_nakshatra": nak_list[l_idx],
        "lagna_special_asterisms": special_points_lagna,
        "lagna_navatara_groups": tara_groups
    }


