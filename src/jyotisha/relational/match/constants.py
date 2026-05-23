# src/ci_match/constants.py

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
    "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

RASHI_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
    7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

# Gana (Temperament)
GANA_TABLE = {
    # Deva
    1: "Deva", 5: "Deva", 7: "Deva", 8: "Deva", 13: "Deva", 
    15: "Deva", 17: "Deva", 22: "Deva", 27: "Deva",
    # Manushya
    2: "Manushya", 4: "Manushya", 6: "Manushya", 11: "Manushya", 
    12: "Manushya", 20: "Manushya", 21: "Manushya", 25: "Manushya", 26: "Manushya",
    # Rakshasa
    3: "Rakshasa", 9: "Rakshasa", 10: "Rakshasa", 14: "Rakshasa", 
    16: "Rakshasa", 18: "Rakshasa", 19: "Rakshasa", 23: "Rakshasa", 24: "Rakshasa"
}

# Yoni (Animal Species)
YONI_ANIMAL = {
    1: "Horse", 2: "Elephant", 3: "Sheep", 4: "Serpent", 5: "Serpent", 6: "Dog",
    7: "Cat", 8: "Goat", 9: "Cat", 10: "Rat", 11: "Rat", 12: "Cow",
    13: "Buffalo", 14: "Tiger", 15: "Buffalo", 16: "Tiger", 17: "Deer", 18: "Deer",
    19: "Dog", 20: "Monkey", 21: "Mongoose", 22: "Monkey", 23: "Lion", 24: "Horse",
    25: "Lion", 26: "Cow", 27: "Elephant"
}

# Rajju (Body Part) initialization
RAJJU_GROUP = {}
for n in [5, 6, 14, 15, 23, 24]: RAJJU_GROUP[n] = "Siras"
for n in [4, 7, 13, 16, 22, 25]: RAJJU_GROUP[n] = "Kanta"
for n in [3, 8, 12, 17, 21, 26]: RAJJU_GROUP[n] = "Nabhi"
for n in [2, 9, 11, 18, 20, 27]: RAJJU_GROUP[n] = "Kati"
for n in [1, 10, 19]: RAJJU_GROUP[n] = "Pada"

# Vedha (Dosha) Map
VEDHA_MAP = {
    1:18, 18:1,
    2:17, 17:2,
    3:16, 16:3,
    4:15, 15:4,
    5:23, 23:5,
    6:22, 22:6,
    7:21, 21:7,
    8:20, 20:8,
    9:19, 19:9,
    10:27, 27:10,
    11:26, 26:11,
    12:25, 25:12,
    13:24, 24:13
}

# Friendships for Rasi Adhipati
FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"}
}

# Sworn Enemies for Yoni
YONI_ENEMIES = [
    {"Cow", "Tiger"}, {"Elephant", "Lion"}, {"Horse", "Buffalo"},
    {"Dog", "Deer"}, {"Rat", "Cat"}, {"Serpent", "Mongoose"}, {"Monkey", "Goat"}
]

# 2=Friend, 1=Neutral, 0=Enemy
PLANET_FRIENDLINESS = {
    "Sun":     {"Sun": 2, "Moon": 2, "Mars": 2, "Mercury": 1, "Jupiter": 2, "Venus": 0, "Saturn": 0},
    "Moon":    {"Sun": 2, "Moon": 2, "Mars": 1, "Mercury": 2, "Jupiter": 1, "Venus": 1, "Saturn": 1},
    "Mars":    {"Sun": 2, "Moon": 2, "Mars": 2, "Mercury": 0, "Jupiter": 2, "Venus": 1, "Saturn": 1},
    "Mercury": {"Sun": 2, "Moon": 0, "Mars": 1, "Mercury": 2, "Jupiter": 1, "Venus": 2, "Saturn": 1},
    "Jupiter": {"Sun": 2, "Moon": 2, "Mars": 2, "Mercury": 0, "Jupiter": 2, "Venus": 0, "Saturn": 1},
    "Venus":   {"Sun": 0, "Moon": 0, "Mars": 1, "Mercury": 2, "Jupiter": 1, "Venus": 2, "Saturn": 2},
    "Saturn":  {"Sun": 0, "Moon": 0, "Mars": 0, "Mercury": 2, "Jupiter": 1, "Venus": 2, "Saturn": 2}
}
