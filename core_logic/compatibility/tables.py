"""tables: part of compatibility (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Optional
from ..utils import norm360

# ---------------------------------------------------------------------------
# 1. Ashta Kuta Reference Data & Classifications
# ---------------------------------------------------------------------------

# 1.1 Varna: 0=Brahmin, 1=Kshatriya, 2=Vaishya, 3=Shudra
# Rasis: Cancer(3), Scorpio(7), Pisces(11) = Brahmin (Highest spiritual ego)
#        Aries(0), Leo(4), Sag(8) = Kshatriya
#        Taurus(1), Virgo(5), Cap(9) = Vaishya
#        Gemini(2), Libra(6), Aqua(10) = Shudra
VARNA_BY_RASI = {
    3: 0, 7: 0, 11: 0,  # Brahmin
    0: 1, 4: 1, 8: 1,   # Kshatriya
    1: 2, 5: 2, 9: 2,   # Vaishya
    2: 3, 6: 3, 10: 3   # Shudra
}
VARNA_NAMES = ["Brahmin", "Kshatriya", "Vaishya", "Shudra"]

# 1.2 Vashya: 0=Chatushpada (Quadruped), 1=Manava (Biped/Human), 2=Jalachara (Water),
#             3=Vanachara (Lion/Beast), 4=Keeta (Insect)
VASHYA_BY_RASI = {
    0: 0,               # Aries: Quadruped
    1: 0,               # Taurus: Quadruped
    2: 1,               # Gemini: Human
    3: 2,               # Cancer: Water
    4: 3,               # Leo: Forest Beast
    5: 1,               # Virgo: Human
    6: 1,               # Libra: Human
    7: 4,               # Scorpio: Insect
    8: 0,               # Sagittarius: 1st half Human, 2nd half Quadruped (default Quadruped)
    9: 2,               # Capricorn: 1st half Quadruped, 2nd half Water (default Water)
    10: 1,              # Aquarius: Human
    11: 2               # Pisces: Water
}
VASHYA_NAMES = ["Chatushpada", "Manava", "Jalachara", "Vanachara", "Keeta"]

# Vashya compatibility matrix [Bride][Groom] -> points out of 2.0
VASHYA_MATRIX = [     # the usual table (symmetric); Leo with a quadruped ½, with a water sign 1
    # Quadruped, Human, Water, Beast, Insect
    [2.0, 1.0, 1.0, 0.5, 1.0],  # Quadruped
    [1.0, 2.0, 0.5, 0.0, 1.0],  # Human
    [1.0, 0.5, 2.0, 1.0, 1.0],  # Water
    [0.5, 0.0, 1.0, 2.0, 0.0],  # Forest Beast (Leo)
    [1.0, 1.0, 1.0, 0.0, 2.0],  # Insect (Scorpio)
]


def vashya_class(rasi: int, lon: Optional[float] = None) -> int:
    """The Moon's vashya: Sagittarius is human to 15° and quadruped after, Capricorn quadruped to 15° and watery after (by sign alone: the defaults)."""
    if lon is not None and rasi % 12 in (8, 9):
        first = norm360(lon) % 30.0 < 15.0
        return (1 if first else 0) if rasi % 12 == 8 else (0 if first else 2)
    return VASHYA_BY_RASI[rasi % 12]

# 1.3 Yoni: 14 Animal classes (each nakshatra has a specific male/female yoni)
# 0=Horse, 1=Elephant, 2=Sheep, 3=Serpent, 4=Dog, 5=Cat, 6=Rat, 7=Cow,
# 8=Buffalo, 9=Tiger, 10=Hare, 11=Monkey, 12=Mongoose, 13=Lion
YONI_NAMES = [
    "Horse (Ashva)", "Elephant (Gaja)", "Sheep (Mesha)", "Serpent (Sarpa)",
    "Dog (Shvan)", "Cat (Marjara)", "Rat (Mushaka)", "Cow (Gau)",
    "Buffalo (Mahisha)", "Tiger (Vyaghra)", "Hare (Shashaka)",
    "Monkey (Vanara)", "Mongoose (Nakula)", "Lion (Simha)"
]

NAKSHATRA_YONI = [
    0,   # 0: Ashwini -> Horse
    1,   # 1: Bharani -> Elephant
    2,   # 2: Krittika -> Sheep
    3,   # 3: Rohini -> Serpent
    3,   # 4: Mrigashira -> Serpent
    4,   # 5: Ardra -> Dog
    5,   # 6: Punarvasu -> Cat
    2,   # 7: Pushya -> Sheep
    5,   # 8: Ashlesha -> Cat
    6,   # 9: Magha -> Rat
    6,   # 10: Purva Phalguni -> Rat
    7,   # 11: Uttara Phalguni -> Cow
    8,   # 12: Hasta -> Buffalo
    9,   # 13: Chitra -> Tiger
    8,   # 14: Swati -> Buffalo
    9,   # 15: Vishakha -> Tiger
    10,  # 16: Anuradha -> Hare
    10,  # 17: Jyeshtha -> Hare
    4,   # 18: Moola -> Dog
    11,  # 19: Purva Ashadha -> Monkey
    12,  # 20: Uttara Ashadha -> Mongoose
    11,  # 21: Shravana -> Monkey
    13,  # 22: Dhanishta -> Lion
    0,   # 23: Shatabhisha -> Horse
    13,  # 24: Purva Bhadrapada -> Lion
    7,   # 25: Uttara Bhadrapada -> Cow
    1    # 26: Revati -> Elephant
]

# Yoni points [bride's yoni][groom's yoni], the usual 14 x 14 table (the animals in YONI_NAMES' order)
YONI_POINTS = [
    [4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1], [2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0], [2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1],
    [3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2], [2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1], [2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1],
    [2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2], [1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1], [0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1],
    [1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1], [3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1], [3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2],
    [2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2], [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4]]

# Graha Maitri points between the Moon signs' lords [bride's lord][groom's lord], Sun .. Saturn (the usual table)
MAITRI_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
MAITRI_POINTS = [[5, 5, 5, 4, 5, 0, 0], [5, 5, 4, 1, 4, 0.5, 0.5], [5, 4, 5, 0.5, 5, 3, 0.5], [4, 1, 0.5, 5, 0.5, 5, 4],
                 [5, 4, 5, 0.5, 5, 0.5, 3], [0, 0.5, 3, 5, 0.5, 5, 5], [0, 0.5, 0.5, 4, 3, 5, 5]]

# Sworn mutual enmity pairs in Yoni (Score = 0):
SWORN_YONI_ENEMIES = {
    (0, 8), (8, 0),    # Horse - Buffalo
    (1, 13), (13, 1),  # Elephant - Lion
    (2, 11), (11, 2),  # Sheep - Monkey
    (3, 12), (12, 3),  # Serpent - Mongoose
    (4, 10), (10, 4),  # Dog - Hare
    (5, 6), (6, 5),    # Cat - Rat
    (7, 9), (9, 7)     # Cow - Tiger
}

# 1.4 Gana: 0=Deva, 1=Manushya, 2=Rakshasa
GANA_NAMES = ["Deva", "Manushya", "Rakshasa"]
NAKSHATRA_GANA = [
    0, 1, 2, 1, 0, 1, 0, 0, 2,  # 0..8
    2, 1, 1, 0, 2, 0, 2, 0, 2,  # 9..17
    2, 1, 1, 0, 2, 2, 1, 1, 0   # 18..26
]

# 1.5 Nadi: 0=Adi (Vata), 1=Madhya (Pitta), 2=Antya (Kapha)
NADI_NAMES = ["Adi (Vata)", "Madhya (Pitta)", "Antya (Kapha)"]
NAKSHATRA_NADI = [         # the count snakes: Adi, Madhya, Antya, Antya, Madhya, Adi, ..., so the middle nine run backward
    0, 1, 2, 2, 1, 0, 0, 1, 2,  # 0..8 (Ashwini to Ashlesha)
    2, 1, 0, 0, 1, 2, 2, 1, 0,  # 9..17 (Magha to Jyeshtha): Magha, Svati, Vishakha Antya; U.Phalguni, Hasta, Jyeshtha Adi
    0, 1, 2, 2, 1, 0, 0, 1, 2   # 18..26 (Moola to Revati)
]

# 1.6 Rajju: 5 cords
RAJJU_NAMES = ["Pada (Feet)", "Kati (Waist)", "Nabhi (Navel)", "Kantha (Neck)", "Shiro (Head)"]
NAKSHATRA_RAJJU = [
    0, 1, 2, 3, 4, 3, 2, 1, 0,  # 0..8
    0, 1, 2, 3, 4, 3, 2, 1, 0,  # 9..17
    0, 1, 2, 3, 4, 3, 2, 1, 0   # 18..26
]

# 1.7 Vedha (Piercing nakshatras pairs)
VEDHA_PAIRS = {
    (0, 17), (17, 0),  # Ashwini - Jyeshtha
    (1, 16), (16, 1),  # Bharani - Anuradha
    (2, 15), (15, 2),  # Krittika - Vishakha
    (3, 14), (14, 3),  # Rohini - Swati
    (4, 13), (13, 4),  # Mrigashira - Chitra
    (4, 22), (22, 4),  # Mrigashira - Dhanishta
    (5, 12), (12, 5),  # Ardra - Shravana
    (6, 21), (21, 6),  # Punarvasu - Uttarashadha
    (7, 20), (20, 7),  # Pushya - Purvashadha
    (8, 19), (19, 8),  # Ashlesha - Moola
    (9, 26), (26, 9),  # Magha - Revati
    (10, 25), (25, 10),# Purva Phalguni - Uttara Bhadrapada
    (11, 24), (24, 11),# Uttara Phalguni - Purva Bhadrapada
    (12, 23), (23, 12),# Hasta - Shatabhisha
    (13, 22), (22, 13),# Chitra - Dhanishta (Mrigashira, Chitra, Dhanishta pierce one another)
}



def _ordinal(n: int) -> str:
    return "%d%s" % (n, "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))
