"""
The Key Info list modes and the transit view's special nakshatra modes: taras, special nakshatras, latta and
nakshatra aspects, special tithis (sources: PVR ch. 26; docs/SOURCES.md section 12).

Stars are counted on the 28-nakshatra wheel (Abhijit between Uttarashadha and Sravana) for the special nakshatras
and latta, and on the 27-nakshatra wheel for the nava taras. Every function returns plain rows.
"""
from typing import Dict, List, Tuple

NAK = 360.0 / 27.0
NAKSHATRAS_27 = ["Aswi", "Bhar", "Krit", "Rohi", "Mrig", "Ardr", "Puna", "Push", "Asre", "Magh", "PPha", "UPha", "Hast",
                 "Chit", "Swat", "Visa", "Anu", "Jye", "Mool", "PSha", "USha", "Srav", "Dhan", "Sata", "PBha", "UBha", "Reva"]
NAKSHATRAS_28 = NAKSHATRAS_27[:21] + ["Abhi"] + NAKSHATRAS_27[21:]
TARA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
NAVA_TARAS = [("Janma", "Birth"), ("Sampat", "Wealth"), ("Vipat", "Danger"), ("Kshema", "Well-being"),
              ("Pratyak", "Obstacles"), ("Saadhana", "Achievement"), ("Naidhana", "Death"), ("Mitra", "Friend"),
              ("Parama Mitra", "Good friend")]
# (name, meaning, steps forward on the 28-star wheel): PVR 26.4.2
SPECIAL_TARAS = [("Janma", "Existence", 0), ("Karma", "Work", 9), ("Samudayika", "Collective", 17),
                 ("Sanghatika", "Social", 15), ("Jaati", "Family", 3), ("Naidhana", "Death", 6), ("Desa", "Nation", 11),
                 ("Abhisheka", "Coronation", 27), ("Aadhaana", "Kindling", 18), ("Vainasika", "Destructive", 21),
                 ("Maanasa", "Mental", 24)]
# Sun .. Rahu; latta direction and count (inclusive; PVR 26.7), and the aspected stars (inclusive counts; PVR 26.5)
LATTA = [(1, 12), (-1, 22), (1, 3), (-1, 7), (1, 6), (-1, 5), (1, 8), (-1, 9)]
NAK_ASPECTS = [(14, 15), (14, 15), (1, 3, 7, 8, 15), (1, 15), (10, 15, 19), (1, 15), (3, 5, 15, 19), ()]


def nak27(lon: float) -> int:
    return int((lon % 360.0) / NAK)


def nak28(lon: float) -> int:
    """The star on the 28-star wheel: Abhijit is the last quarter of Uttarashadha (276 deg 40 min to 280 deg)."""
    x = lon % 360.0
    if 276.0 + 2.0 / 3.0 <= x < 280.0:
        return 21
    k = nak27(x)
    return k + 1 if k >= 21 else k


def _lord28(k: int) -> str:
    """The Vimsottari lord of a star of the 28-star wheel; Abhijit's is shown as Uttarashadha's."""
    return TARA_LORDS[(k - 1 if k > 21 else min(k, 20)) % 9]


def nava_taras(lon: float) -> List[Tuple[str, str, str, str, str, str]]:
    """Nava Taras from a point's star: (tara, meaning, lord, star 1, star 2, star 3)."""
    k = nak27(lon)
    return [(name, mean, TARA_LORDS[(k + i) % 9], *(NAKSHATRAS_27[(k + i + 9 * j) % 27] for j in range(3)))
            for i, (name, mean) in enumerate(NAVA_TARAS)]


def special_taras(lon: float) -> List[Tuple[str, str, str, str]]:
    """Special nakshatras from a point's star: (name, meaning, star, its lord), on the 28-star wheel."""
    k = nak28(lon)
    return [(name, mean, NAKSHATRAS_28[(k + d) % 28], _lord28((k + d) % 28)) for name, mean, d in SPECIAL_TARAS]


def latta_star(planet: int, lon: float) -> str:
    """The star a planet (0 Sun .. 7 Rahu, in that order) kicks."""
    sign, count = LATTA[planet]
    return NAKSHATRAS_28[(nak28(lon) + sign * (count - 1)) % 28]


def aspected_stars(planet: int, lon: float) -> List[str]:
    """The stars a planet (0 Sun .. 7 Rahu) aspects from its star."""
    return [NAKSHATRAS_28[(nak28(lon) + c - 1) % 28] for c in NAK_ASPECTS[planet]]


def nakshatra_aspects(lons: Dict[int, float]) -> List[Tuple[str, str, List[str]]]:
    """The Nakshatra Aspects & Latta mode: (latta star, occupied star, aspected stars) of Sun .. Rahu ``lons[0..7]``."""
    return [(latta_star(p, lons[p]), NAKSHATRAS_28[nak28(lons[p])], aspected_stars(p, lons[p])) for p in range(8)]


# Tithis 1 .. 30: name, lord, deity (the Special Tithis mode prints them for the 36 multiples)
TITHI_NAMES = ["Pratipat", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Sapthami", "Ashtami", "Navami",
               "Dasami", "Ekadasi", "Dwadasi", "Trayodasi", "Chaturdasi"]
TITHI_DEITIES = ["Kaameswari", "Bhaga Maalini", "Nitya Klinna", "Bherunda", "Vahni Vaasini", "Vajreswari", "Siva Dooti",
                 "Tvarita", "Kula Sundari", "Nitya", "Neela Pataaka", "Vijaya", "Sarva Mangala", "Jwaalaa Maalini", "Chitra"]
TITHI_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]
SEEDS_31_36 = [3, 6, 4, 2, 1, 4]                   # the view's seed column after 30, as it prints it
SPECIAL_TITHI_NAMES = ["Janma", "Dhana", "Bhratri", "Matri", "Putra", "Satru", "Kalatra", "Mrityu", "Bhagya", "Karma",
                       "Laabha", "Vyaya"]


def tithi_name(n: int) -> str:
    """Tithi ``n`` (1 .. 30)."""
    if n == 15:
        return "Pournimasya"
    if n == 30:
        return "Amavasya"
    return ("Sukla " if n < 15 else "Krishna ") + TITHI_NAMES[(n - 1) % 15]


def tithi_lord(n: int) -> str:
    """Tithi ``n``'s lord: Sun .. Rahu from each half's start, with Saturn on the 15th and Rahu on the 30th."""
    return "Rahu" if n == 30 else TITHI_PLANETS[(n - 1) % 15 % 8]


def special_tithis(moon: float, sun: float) -> List[Dict[str, object]]:
    """The 36 special tithis: seed ``k`` is the tithi of k x (Moon - Sun) (a convention; docs/SOURCES.md section 8)."""
    out = []
    for k in range(1, 37):
        x = ((moon - sun) % 360.0 * k) % 360.0
        i = int(x / 12.0)
        n = i + 1
        name = SPECIAL_TITHI_NAMES[(k - 1) % 12] + " tithi"
        if k > 12:
            name += " (cycle %d)" % ((k - 1) // 12 + 1)
        out.append({"special": name, "seed": k if k <= 30 else SEEDS_31_36[k - 31], "tithi": n, "name": tithi_name(n), "left": (12.0 * n - x) / 12.0,
                    "lord": tithi_lord(n), "deity": TITHI_DEITIES[(n - 1) % 15],
                    "paksha_index": n - 15 if n > 15 else n, "paksha": "Brighter" if n <= 15 else "Darker"})
    return out


def lords_of_sign(sign: int) -> str:
    """The lord's name as the view prints it: both lords for Aquarius only."""
    return "Saturn and Rahu" if sign == 10 else ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars",
                                                 "Jupiter", "Saturn", "Saturn", "Jupiter"][sign]


def malicious_divisions(lagna: float, moon: float) -> List[Tuple[str, str]]:
    """The "malicious divisions": the lords of the 64th navamsa (PM 8.61) and the 22nd drekkana (PM 9.4; all 5
    drekkana schemes) from the lagna and from the Moon; both are the point + 210 degrees."""
    from . import varga_charts as V
    x, y = (lagna + 210.0) % 360.0, (moon + 210.0) % 360.0
    rows = [("The 64th navamsa", lords_of_sign(V.d9(x)))]
    rows += [("The 22nd %s drekkana" % n, lords_of_sign(V.d3(x, s)))
             for n, s in (("Pararsara", 0), ("Parivritti traya", 1), ("Somanatha", 2), ("Uma-Shambhu", 4))]
    rows.append(("The 64th navamsa from Moon", lords_of_sign(V.d9(y))))
    rows += [("The 22nd %s drekkana from Moon" % n, lords_of_sign(V.d3(y, s)))
             for n, s in (("Parasara", 0), ("Parivritti traya", 1), ("Somanatha", 2), ("Uma-Shambhu", 4), ("Jagannatha", 3))]
    rows.append(("The 22nd Jagannatha drekkana", lords_of_sign(V.d3(x, 3))))
    return rows


def brahma_rudra_maheswara(jc) -> Tuple[int, int, int]:
    """JUS 2.1: Brahma (``dasa_systems.brahma_planet``; BPHS 46.170-173); Rudra, the stronger of the lords of the 8th from the
    lagna and from the 7th; Maheswara from the lord of the 8th from the atmakaraka (the 6th if a node is in either):
    in that sign, or exalted, or lord of the sign it is in, the lord of the 8th from it; otherwise itself."""
    from . import dasa_systems as J, sign_strength as S
    sg, lons = jc.signs[0], jc.lons
    rudra = S.stronger_by_dignity(S.sign_lord((sg[0] + 7) % 12, sg, lons), S.sign_lord((sg[0] + 1) % 12, sg, lons), sg, lons)
    ak = sg[jc.atmakaraka()]
    h = (ak + 7) % 12
    if h in (sg[8], sg[9]) or ak in (sg[8], sg[9]):
        h = (ak + 5) % 12
    lord = S.sign_lord(h, sg, lons)
    s = sg[lord]
    if s == h or s == S.EXALTATION[lord] or S.sign_lord(s, sg, lons) == lord:
        mahes = S.sign_lord((s + 7) % 12, sg, lons)
    else:
        mahes = lord
    return J.brahma_planet(jc), rudra, mahes


def _special_name(star: int, table: List[Tuple[str, str, str, str]]) -> str:
    for name, mean, s, _ in table:
        if NAKSHATRAS_28.index(s) == star:
            return "%s (%s)" % (name, mean)
    return "-"


def transit_special_nakshatras(transit: Dict[int, float], natal_ref: float) -> List[str]:
    """"Transits in special nakshatras" (PVR 26.4.2; Sun .. Ketu in ``transit[0..8]``): the special nakshatra of the
    natal reference (Moon or lagna) each occupies, or "-"."""
    table = special_taras(natal_ref)
    return [_special_name(nak28(transit[p]), table) for p in sorted(transit)]


def transit_special_aspects(transit: Dict[int, float], natal_ref: float) -> List[Tuple[str, List[str]]]:
    """"Aspects on special nakshatras": (occupied special nakshatra, special nakshatras among the aspected stars) of
    Sun .. Saturn and the nodes; the nodes have no star aspects."""
    table = special_taras(natal_ref)
    out = []
    for p in sorted(transit):
        stars = NAK_ASPECTS[p] if p < 7 else ()
        hits = [_special_name((nak28(transit[p]) + c - 1) % 28, table) for c in stars]
        out.append((_special_name(nak28(transit[p]), table), [h for h in hits if h != "-"]))
    return out


def transit_latta(transit: Dict[int, float], natal_moon: float, natal_lagna: float) -> List[Tuple[str, str]]:
    """"Latta": (star kicked, what is special about it) of Sun .. Rahu, and Ketu as the 9th row (it has no latta rule:
    its own star): the natal Moon's special nakshatras, or the star of the natal lagna."""
    table = special_taras(natal_moon)
    lagna = NAKSHATRAS_28[nak28(natal_lagna)]
    out = []
    for p in sorted(transit):
        star = NAKSHATRAS_28[nak28(transit[p])] if p == 8 else latta_star(p, transit[p])
        if star == lagna:
            out.append((star, "Lagna nakshatra (nakshatra of natal lagna)"))
            continue
        name = _special_name(NAKSHATRAS_28.index(star), table)
        out.append((star, name.replace(" (", " nakshatra (", 1) if name != "-" else "-"))
    return out


# "Anga graha transits" (PD 26.35-40, the Sun's table 26.35; PVR 26.6): the limb a planet's transit star falls on, by its count from the natal star; one
# table per planet (Sun .. Ketu), on the 27-star wheel
_ANGA_SIX = [0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5]
_ANGA_NINE = [0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 7, 7, 8, 8]
ANGA_INDEX = [[0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 7, 7],
              [0, 0, 1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 6, 6, 6, 6, 6, 6, 7, 7, 7],
              [0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7],
              _ANGA_SIX, _ANGA_SIX, _ANGA_SIX, _ANGA_NINE, _ANGA_NINE, _ANGA_NINE]
_LIMBS_SIX = ["Head", "Face", "Two hands", "Stomach", "Privities", "Two feet", "-", "-", "-"]
_LIMBS_NINE = ["Face", "Right hand", "Right leg", "Left leg", "Left hand", "Stomach", "Head", "Eyes", "Back"]
_RES_SIX = ["Grief", "Gains", "Untoward events", "Influx of wealth", "Loss", "Honor and fame", "-", "-", "-"]
_RES_NINE = ["Sorrow", "Happiness", "Travel", "Loss", "Profit", "Sexual union", "Joy", "Comforts", "Danger to life"]
ANGA_LIMBS = [["Face", "Head", "Chest", "Right hand", "Two feet", "Left hand", "Two eyes", "Privities", "-"],
              ["Face", "Head", "Back", "Tow eyes", "Chest", "Left hand", "Two feet", "Right hand", "-"],
              ["Face", "Two feet", "Chest", "Left hand", "Head", "Face", "Right hand", "Two eyes", "-"],
              _LIMBS_SIX, _LIMBS_SIX, _LIMBS_SIX, _LIMBS_NINE, _LIMBS_NINE, _LIMBS_NINE]
ANGA_RESULTS = [["Destruction", "Influx of wealth", "Success", "Monetary benefits", "Loss of wealth", "Physical ailments",
                 "Gain", "Danger to life", "-"],
                ["Great fear", "Safety", "Defeat of enemies", "Monetary gains", "Calm of mind", "Quarrel", "Going abroad",
                 "Financial gain", "-"],
                ["Death", "Quarrel", "Success", "Poverty", "Gain", "Great fear", "Happiness", "Going abroad", "-"],
                _RES_SIX, _RES_SIX, _RES_SIX, _RES_NINE, _RES_NINE, _RES_NINE]


def anga_graha(transit: Dict[int, float], natal_ref: float) -> List[Tuple[str, str]]:
    """(limb, result) of Sun .. Ketu (``transit[0..8]``) from a natal reference's star (the view shows the Moon, the
    lagna and the Sun)."""
    k = nak27(natal_ref)
    out = []
    for p in sorted(transit):
        i = ANGA_INDEX[p][(nak27(transit[p]) - k) % 27]
        out.append((ANGA_LIMBS[p][i], ANGA_RESULTS[p][i]))
    return out


# Pachakadi relationships (no verse checked; docs/SOURCES.md section 12): the house from a planet holding its Pachaka, Bodhaka, Karaka
# and Vedhaka; Sun .. Saturn (points 1 .. 7)
PACHAKADI_NAMES = ["Pachaka", "Bodhaka", "Karaka", "Vedhaka"]
PACHAKADI_HOUSES = {1: (6, 7, 9, 11), 2: (7, 9, 11, 3), 3: (2, 6, 11, 12), 4: (2, 4, 5, 3), 5: (6, 5, 7, 12), 6: (2, 6, 12, 4),
                    7: (3, 11, 6, 7)}


def pachakadi_signs(planet: int, signs) -> Dict[str, int]:
    """The sign of each relationship of ``planet`` (1 Sun .. 7 Saturn), ``signs`` the chart's signs by point index."""
    return {n: (h + signs[planet] - 1) % 12 for n, h in zip(PACHAKADI_NAMES, PACHAKADI_HOUSES[planet])}


def pachakadi_of_rasi(rasi: int, signs) -> Dict[str, list]:
    """Which planets (1 .. 7) have ``rasi`` as each relationship: the chart menu's "of this rasi" mode."""
    out = {n: [] for n in PACHAKADI_NAMES}
    for p in range(1, 8):
        for n, s in pachakadi_signs(p, signs).items():
            if s == rasi:
                out[n].append(p)
    return out


# Planetary drekkanas: the labels of each of the 36 drekkanas (their forms, BJ ch. 27: weapon, animal, serpent, fetter ..),
# (all 36 cells)
DREKKANA_LABELS = [
    ["Ayudha (weapon), Kroora (cruel)", "Mriga (animal), Subha (auspicious)", "Ayudha (weapon), Misra (mixed)"],
    ["Agni (fire), Misra (mixed)", "Mriga (animal)", "-"],
    ["-", "Pakshi (bird)", "Ayudha (weapon)"],
    ["Chatushpada (quadruped)", "Sarpa (snake)", "Sarpa (snake)"],
    ["Chatushpada (quadruped), Kroora (cruel), Pakshi (bird)", "Ayudha (weapon)", "Ayudha (weapon), Kroora (cruel)"],
    ["Agni (fire)", "-", "-"],
    ["-", "Pakshi (bird)", "Ayudha (weapon), Chatushpada (quadruped)"],
    ["Sarpa (snake), Kroora (cruel)", "Sarpa (snake), Kroora (cruel)", "Chatushpada (quadruped), Kroora (cruel)"],
    ["Ayudha (weapon), Chatushpada (quadruped)", "-", "Ayudha (weapon)"],
    ["Nigala, Kroora (cruel), Chatushpada (quadruped)", "-", "Ayudha (weapon)"],
    ["Pakshi (bird), Kroora (cruel)", "Agni (fire)", "-"],
    ["-", "-", "Sarpa (snake)"]]


def drekkana_labels(lon: float) -> str:
    """The Planetary drekkanas mode: what the drekkana holding ``lon`` is, or "-"."""
    x = lon % 360.0
    return DREKKANA_LABELS[int(x // 30.0)][int((x % 30.0) // 10.0)]


def aspect_evaluation_row(target: float, planets: Dict[int, float]) -> List[float]:
    """The Planetary Aspect Evaluation mode (BPHS 26.6-12): the aspect of Sun .. Ketu (``planets[1..9]``)
    on a point, in percent (0 is printed as "-")."""
    from .shadbala import aspect_value
    return [aspect_value(target - planets[p], p) for p in range(1, 10)]
