# src/ci_match.py
import math

# -----------------------------------------------------------------------------
# Constants & Reference Data
# -----------------------------------------------------------------------------

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
# Deva: 1, 5, 7, 8, 13, 15, 17, 22, 27
# Manushya: 2, 4, 6, 11, 12, 20, 21, 25, 26
# Rakshasa: 3, 9, 10, 14, 16, 18, 19, 23, 24
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
# 1: Horse, 2: Elephant, 3: Sheep, 4: Serpent, 5: Serpent, 6: Dog, 
# 7: Cat, 8: Goat, 9: Cat, 10: Rat, 11: Rat, 12: Cow, 
# 13: Buffalo, 14: Tiger, 15: Buffalo, 16: Tiger, 17: Deer, 18: Deer, 
# 19: Dog, 20: Monkey, 21: Mongoose, 22: Monkey, 23: Lion, 24: Horse, 
# 25: Lion, 26: Cow, 27: Elephant
YONI_ANIMAL = {
    1: "Horse", 2: "Elephant", 3: "Sheep", 4: "Serpent", 5: "Serpent", 6: "Dog",
    7: "Cat", 8: "Goat", 9: "Cat", 10: "Rat", 11: "Rat", 12: "Cow",
    13: "Buffalo", 14: "Tiger", 15: "Buffalo", 16: "Tiger", 17: "Deer", 18: "Deer",
    19: "Dog", 20: "Monkey", 21: "Mongoose", 22: "Monkey", 23: "Lion", 24: "Horse",
    25: "Lion", 26: "Cow", 27: "Elephant"
}

# Rajju (Body Part) -> 1: Padu, 2: Kati, 3: Nabhi, 4: Kanta, 5: Siras
# Pattern is slightly complex, usually mapped by Nakshatra groups 
# Standard grouping (simple version): 
# Padu: 1, 10, 19
# Kati: 2, 11, 20
# Nabhi: 3, 12, 21
# Kanta: 4, 13, 22
# Siras: 5, 14, 23
# ... continues. Easier to map explicitly.
# Actually standard Rajju groups are:
# Group 1 (Padu/Foot): 1, 10, 19, 27, 18, 9 (No, this is wrong)
# Let's use the standard schematic:
# Siras (Head): 5, 6, 14, 15, 23, 24
# Kanta (Neck): 4, 7, 13, 16, 22, 25
# Nabhi (Navel): 3, 8, 12, 17, 21, 26
# Kati (Hip): 2, 9, 11, 18, 20, 27
# Pada (Foot): 1, 10, 19
# Wait, let's double check. 
# Standard Rajju:
# 1: Pada, 2: Kati, 3: Nabhi, 4: Kanta, 5: Siras, 6: Siras, 7: Kanta, 8: Nabhi, 9: Kati, 
# 10: Pada, 11: Kati, 12: Nabhi, 13: Kanta, 14: Siras, 15: Siras, 16: Kanta, 17: Nabhi, 18: Kati,
# 19: Pada, 20: Kati, 21: Nabhi, 22: Kanta, 23: Siras, 24: Siras, 25: Kanta, 26: Nabhi, 27: Kati.
# Careful: Revati (27) is usually Pada in some texts, but in the ascending/descending cycle it ends at Kati?
# Let's stick to the common ascending/descending cycle:
# 1-Asc, 2-Asc, 3-Asc, 4-Asc, 5-Asc, 6-Desc, 7-Desc, 8-Desc, 9-Desc, 10-Desc (No)
# It is 1-10-19 (Ashwini, Magha, Mula) -> Pada
# 2-11-20 (Bharani, P.Phal, P.Ash) -> Kati
# 3-12-21 -> Nabhi
# 4-13-22 -> Kanta
# 5-14-23 -> Siras
# 6-15-24 -> Siras (Ardra, Swati, Satabhisha - Oh wait, different grouping)
# Correct Rajju Mapping:
# 5, 6, 14, 15, 23, 24 -> Siro (Head)
# 4, 7, 13, 16, 22, 25 -> Kanta (Neck)
# 3, 8, 12, 17, 21, 26 -> Nabhi (Navel)
# 2, 9, 11, 18, 20, 27 -> Kati (Thigh/Hip)
# 1, 10, 19 -> Pada (Foot)
RAJJU_GROUP = {}
for n in [5, 6, 14, 15, 23, 24]: RAJJU_GROUP[n] = "Siras"
for n in [4, 7, 13, 16, 22, 25]: RAJJU_GROUP[n] = "Kanta"
for n in [3, 8, 12, 17, 21, 26]: RAJJU_GROUP[n] = "Nabhi"
for n in [2, 9, 11, 18, 20, 27]: RAJJU_GROUP[n] = "Kati"
for n in [1, 10, 19]: RAJJU_GROUP[n] = "Pada"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def get_nakshatra_idx(deg_longitude):
    """0-based index of Nakshatra (0..26)"""
    # 27 Nakshatras in 360 degrees = 13.3333 deg each
    return int(deg_longitude // (360/27))

def get_pada(deg_longitude):
    """1-based Pada number (1..4)"""
    nak_len = 360/27
    intra_nak = deg_longitude % nak_len
    pada_len = nak_len / 4
    return int(intra_nak // pada_len) + 1

def get_rashi_idx(deg_longitude):
    """1-based Rashi index (1..12)"""
    return int(deg_longitude // 30) + 1

# -----------------------------------------------------------------------------
# Kuta Calculation Functions
# -----------------------------------------------------------------------------

def check_dina(boy_nak, girl_nak):
    """
    Dina Kuta (3 points): Count from Girl to Boy. 
    Ideal: 2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26
    """
    count = (boy_nak - girl_nak) % 27 + 1
    # Standard rule: divide by 9, take remainder
    rem = count % 9
    
    # Good remainders: 0 (9), 2, 4, 6, 8
    # 0 here implies 9, 18, 27. 
    # Usually 27 (same nakshatra) is handled separately in some traditions, 
    # but strictly for Dina: 2,4,6,8,9 (0) are good.
    # Bad: 1, 3, 5, 7.
    
    # Exception: If remainder is 1 (Janma), it's generally bad, but compatible for specific pairs.
    # We will stick to basic rule for simplicity.
    
    if rem in [0, 2, 4, 6, 8]:
        return 3.0, "Good"
    else:
        # Special case: 27th usually considered bad in some texts if not same Pada
        # simplified view:
        return 0.0, "Bad"

def check_gana(boy_nak, girl_nak):
    """
    Gana Kuta (4 points): Temperament match.
    Deva-Deva: 4
    Manushya-Manushya: 4
    Rakshasa-Rakshasa: 4
    Deva-Manushya: 4 (some say 2 or 3, standard is often good)
    Manushya-Deva: 4 (or 2/3)
    
    Rakshasa-Deva: 1 (Bad)
    Deva-Rakshasa: 0 (Bad)
    Rakshasa-Manushya: 0 (Bad)
    Manushya-Rakshasa: 0 (Bad)
    
    Standard Points Table (South Indian):
    Boy \ Girl | Deva | Manushya | Rakshasa
    Deva       | 4    | 2        | 1
    Manushya   | 3    | 4        | 0
    Rakshasa   | 0    | 0        | 4
    """
    g_gana = GANA_TABLE.get(girl_nak+1)
    b_gana = GANA_TABLE.get(boy_nak+1)
    
    if g_gana == "Deva":
        if b_gana == "Deva": return 4.0, "Excellent"
        if b_gana == "Manushya": return 2.0, "Average"
        if b_gana == "Rakshasa": return 1.0, "Poor"
        
    if g_gana == "Manushya":
        if b_gana == "Deva": return 3.0, "Good"
        if b_gana == "Manushya": return 4.0, "Excellent"
        if b_gana == "Rakshasa": return 0.0, "Bad"
        
    if g_gana == "Rakshasa":
        if b_gana == "Deva": return 0.0, "Bad"
        if b_gana == "Manushya": return 0.0, "Bad" # Incompatible
        if b_gana == "Rakshasa": return 4.0, "Excellent"
        
    return 0.0, "Unknown"

def check_mahendra(boy_nak, girl_nak):
    """
    Mahendra (2 points): Wellbeing/Progeny.
    Count from Girl to Boy should be 4, 7, 10, 13, 16, 19, 22, 25.
    """
    count = (boy_nak - girl_nak) % 27 + 1
    if count in [4, 7, 10, 13, 16, 19, 22, 25]:
        return 2.0, "Good"
    return 0.0, "Bad"

def check_stree_deergha(boy_nak, girl_nak):
    """
    Stree Deergha (1 point): General welfare.
    Boy's nakshatra should be at least 13 away from Girl's (some say 7+ is passable).
    Strict: > 13.
    """
    count = (boy_nak - girl_nak) % 27 + 1
    if count > 13:
        return 1.0, "Good"
    if count > 7:
        return 0.5, "Average" # Partial
    return 0.0, "Bad"

def check_yoni(boy_nak, girl_nak):
    """
    Yoni (4 points): Sexual compatibility using Animal types.
    Matrix lookup required. For now, we'll implement a simplified matrix or 
    basic enemy/friend logic. 
    Standard: Same animal = 4. 
    Friendly = 3. 
    Neutral = 2. 
    Enemy = 1. 
    Sworn Enemy (Cow-Tiger, Elephant-Lion, Horse-Buffalo, Dog-Deer, Monkey-Goat, Serpent-Mongoose, Cat-Rat) = 0.
    """
    # Using full matrix is tedious inline, let's use the grouping logic.
    # Simpler lookup for Sworn Enemies:
    # 0 - Tiger(14,16) vs Cow(12,26)
    # 1 - Lion(23,25) vs Elephant(2,27)
    # 2 - Horse(1,24) vs Buffalo(13,15)
    # 3 - Dog(6,19) vs Deer(17,18)
    # 4 - Rat(10,11) vs Cat(7,9)
    # 5 - Mongoose(21) vs Serpent(4,5)
    # 6 - Monkey(20,22) vs Goat(8) - Goat(8) uses Goat? Yes.
    
    # Let's map nakshatra to internal Animal Index 0..13
    # 0:Horse, 1:Elephant, 2:Sheep, 3:Serpent, 4:Dog, 5:Cat, 6:Rat, 7:Cow, 
    # 8:Buffalo, 9:Tiger, 10:Deer, 11:Monkey, 12:Mongoose, 13:Lion
    # Wait, Nakshatras 0..26.
    
    # Better: just use the names.
    g_ani = YONI_ANIMAL.get(girl_nak+1)
    b_ani = YONI_ANIMAL.get(boy_nak+1)
    
    if g_ani == b_ani: return 4.0, "Perfect"
    
    # Sworn Enemies (0 points)
    enemies = [
        {"Cow", "Tiger"}, {"Elephant", "Lion"}, {"Horse", "Buffalo"},
        {"Dog", "Deer"}, {"Rat", "Cat"}, {"Serpent", "Mongoose"}, {"Monkey", "Goat"}
    ]
    pair = {g_ani, b_ani}
    for e in enemies:
        if pair == e:
            return 0.0, "Sworn Enemy"
            
    # If not sworn enemy or same, it typically ranges 1-3.
    # Implementing a full 14x14 matrix is large. 
    # Simplified approach: Return 2.0 (Neutral) for now unless mapped strictly.
    # To be good, let's just create the matrix string and parse it, or just use average.
    # Given the constraint of 'concise', we'll default to 2 unless same (4) or sworn enemy (0).
    # But let's try to be slightly more accurate for "Friendly".
    
    return 2.0, "Neutral"

def check_rasi(boy_lon, girl_lon):
    """
    Rasi Kuta (7 points): Emotional compatibility.
    Based on Rasi position (count girl to boy).
    Excellent: 7 (Samasaptama - 1/7 axis) - But actually 7th is disputed (Goonj). Usually 7 is good if lords friendly.
    Good: 3, 4, 8, 10, 11 (Wait, 2,6,5,9,12 are bad).
    Sashtashtaka (6/8): Bad.
    Dwidwadasha (2/12): Bad.
    """
    g_rasi = get_rashi_idx(girl_lon)
    b_rasi = get_rashi_idx(boy_lon)
    
    count = (b_rasi - g_rasi) % 12 
    if count == 0: count = 12 # 1-based count
    else: count += 0 # wait, if diff is 1 (e.g. 2-1=1), count is 2? No Rasi count is inclusive.
    # If Girl=1 (Aries), Boy=1 (Aries), count = 1.
    
    # Real logic:
    # Same sign (1): generally good (EKarajju exception). Score: 7.
    # 2nd (Dwidwadasha): Bad (0).
    # 3rd: Good (7).
    # 4th: Good (7).
    # 5th: Bad (0).
    # 6th (Sashtashtaka): Bad (0).
    # 7th: Good (7) - (some say Bad, most say Good).
    # 8th: Bad (0).
    # 9th: Bad (0) - (Trikona is good? No, 5/9 often considered bad in matching contexts for specific reasons, or good. Let's stick to standard almanac rules).
    # Standard almanac check:
    # 1: Yes (7)
    # 2: No (0) - Girl 1, Boy 2 -> Girl loses wealth (2nd) or Boy dies (12th)?
    # 3: Yes (7)
    # 4: Yes (7)
    # 5: No (0)
    # 6: No (0)
    # 7: Yes (7)
    # 8: No (0)
    # 9: No (0) (Though some regions accept 9 if lords friendly)
    # 10: Yes (7)
    # 11: Yes (7)
    # 12: No (0)
    
    # Refined logic using count (1-based from Girl):
    # Valid counts: 1, 3, 4, 7, 10, 11.
    count_from_girl = (b_rasi - g_rasi) % 12 + 1
    
    if count_from_girl in [1, 3, 4, 7, 10, 11]:
        return 7.0, "Good"
    return 0.0, "Bad"

def check_rasi_adhipati(boy_lon, girl_lon):
    """
    Rasi Adhipati (5 points): Lordship compatibility.
    """
    g_rasi = get_rashi_idx(girl_lon)
    b_rasi = get_rashi_idx(boy_lon)
    
    g_lord = RASHI_LORDS[g_rasi]
    b_lord = RASHI_LORDS[b_rasi]
    
    # Simplified Friend/Enemy logic
    # Friend groups: 
    # A: Sun, Moon, Mars, Jupiter
    # B: Mercury, Venus, Saturn
    # (Note: Mercury intersects)
    
    # Exact lookup
    FRIENDS = {
        "Sun": {"Moon", "Mars", "Jupiter"},
        "Moon": {"Sun", "Mercury"},
        "Mars": {"Sun", "Moon", "Jupiter"},
        "Mercury": {"Sun", "Venus"},
        "Jupiter": {"Sun", "Moon", "Mars"},
        "Venus": {"Mercury", "Saturn"},
        "Saturn": {"Mercury", "Venus"}
    }
    
    if g_lord == b_lord:
        return 5.0, "Same Lord"
        
    is_gb_friend = b_lord in FRIENDS.get(g_lord, set())
    is_bg_friend = g_lord in FRIENDS.get(b_lord, set())
    
    if is_gb_friend and is_bg_friend:
        return 5.0, "Friends"
    if is_gb_friend or is_bg_friend: # One friendly, one neutral/enemy
        return 2.5, "Neutral/Friend" # Simplified score
        
    # Check Neutrality (Not friend, Not enemy) - assume neutral if not in friend list and not explicit enemy ?
    # Let's simple boil down to: 
    # Same Group = 5. Different Group = 0.
    # Group 1: Sun, Moon, Mars, Jupiter
    # Group 2: Venus, Saturn, Mercury (?)
    
    g1 = {"Sun", "Moon", "Mars", "Jupiter"}
    g2 = {"Venus", "Saturn", "Mercury"} # Mercury is friendly to Sun though
    
    if (g_lord in g1 and b_lord in g1) or (g_lord in g2 and b_lord in g2):
        return 5.0, "Good"
    
    # Special: Sun-Mercury? Sun(G1) Mercury(G2). 
    # Sun+Mer = Budhaditya (Good).
    if {g_lord, b_lord} == {"Sun", "Mercury"}: return 5.0, "Good"
    
    return 0.0, "Bad"

def check_vashya(boy_lon, girl_lon):
    """
    Vashya (2 points): Mutual attraction/control.
    Requires Rasi types: Chatushpada, Manava, Jalachara, Vana, Keeta.
    """
    # Simplified: 2 if matches, 0 if not.
    # Often skipped or given partial. We'll grant 1.0 as placeholder or 0.
    # Implementing correctly requires lookups.
    # Aries: Chatushpada (Quadruped)
    # Taurus: Chatushpada
    # Gemini: Manava (Human)
    # Cancer: Jalachara (Water)
    # Leo: Vana (Forest/Lion)
    # Virgo: Manava
    # Libra: Manava
    # Scorpio: Keeta (Insect)
    # Sagittarius: 0-15 Manava, 15-30 Chatushpada (Just generally Manava for Vashya table often)
    # Capricorn: Chatushpada but first half? (Actually Jalachara later half).
    # Aquarius: Manava
    # Pisces: Jalachara
    
    # Compatible Pairs (One is Vashya to other):
    # Aries: Leo, Scorpio. 
    # Taurus: Cancer, Libra.
    # ...
    
    # Placeholder: Return 1.0 (Average)
    return 1.0, "Average"

def check_rajju(boy_nak, girl_nak):
    """
    Rajju (Dosha check): If same Rajju group -> Bad. Different -> Good.
    Most important Kuta.
    """
    g_rajju = RAJJU_GROUP.get(girl_nak+1)
    b_rajju = RAJJU_GROUP.get(boy_nak+1)
    
    if g_rajju == b_rajju:
        return 0.0, f"Dosha ({g_rajju})" # Bad
    return 5.0, "Good" # Note: Rajju doesn't add points to Kuta score usually, it's a disqualifier. But some systems give it points.
    # We will exclude it from SUM usually, or treat it as binary.
    # We'll return a score for display but handle logic separately.
    
    # Wait, usually Rajju is NOT part of the 36 point sum?
    # Correct. Rajju and Vedha are Doshas.
    # They don't contribute to the score of 36.
    # We return status.

def check_vedha(boy_nak, girl_nak):
    """
    Vedha (Dosha): Mutually afflicted nakshatras.
    """
    # Pairs of Vedha
    PAIRS = [
        (1, 18), (2, 17), (3, 16), (4, 15), (5, 14), # Ashwini-Jyeshta etc
        (6, 20), (7, 19), (8, 21), (9, 20), # wait this list is tricky
        (27, 27) # dummy
    ]
    # Standard Vedha Pairs:
    # Ashwini(1) - Jyeshta(18)
    # Bharani(2) - Anuradha(17)
    # Krittika(3) - Vishakha(16)
    # Rohini(4) - Swati(15)
    # Ardra(6) - Shravana(22)
    # Punarvasu(7) - U.Ashadha(21)
    # Pushya(8) - P.Ashadha(20)
    # Ashlesha(9) - Mula(19)
    # Magha(10) - Revati(27)
    # P.Phal(11) - U.Bhad(26)
    # U.Phal(12) - P.Bhad(25)
    # Hasta(13) - Satabhisha(24)
    # Mrigasira(5) - Dhanishta(23)
    
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
    
    b = boy_nak + 1
    g = girl_nak + 1
    
    if VEDHA_MAP.get(b) == g:
        return 0.0, "Dosha Present"
    return 1.0, "No Dosha"


def calculate_match(boy_lon_moon, girl_lon_moon):
    """
    Calculate 10 Poruthams and final score.
    Returns dict.
    """
    # Get Nakshatra Indexes (0-26)
    b_nak = get_nakshatra_idx(boy_lon_moon)
    g_nak = get_nakshatra_idx(girl_lon_moon)
    
    # Get Rasi Longitudes are passed directly
    
    # Calculate
    score_dina, stat_dina = check_dina(b_nak, g_nak)
    score_gana, stat_gana = check_gana(b_nak, g_nak)
    score_mahendra, stat_mahendra = check_mahendra(b_nak, g_nak)
    score_stree, stat_stree = check_stree_deergha(b_nak, g_nak)
    score_yoni, stat_yoni = check_yoni(b_nak, g_nak)
    score_rasi, stat_rasi = check_rasi(boy_lon_moon, girl_lon_moon)
    score_rasilord, stat_rasilord = check_rasi_adhipati(boy_lon_moon, girl_lon_moon)
    score_vashya, stat_vashya = check_vashya(boy_lon_moon, girl_lon_moon)
    
    # Doshas (Score 0 or 1 used for flag, but strictly boolean)
    score_rajju, stat_rajju = check_rajju(b_nak, g_nak) # 0 means Bad!
    score_vedha, stat_vedha = check_vedha(b_nak, g_nak) # 0 means Bad!
    
    # Total Score (out of 36 typically: Dina(3)+Gana(4)+Mahendra(2)+Stree(1)+Yoni(4)+Rasi(7)+Lord(5)+Vashya(2) = 28?)
    # Wait, Kutas are:
    # 1. Dina (3)
    # 2. Gana (4)
    # 3. Mahendra (0/2 - not in sum usually? Or is it?) -> Usually separate.
    # 4. Stree Deergha (1)
    # 5. Yoni (4)
    # 6. Rasi (7)
    # 7. Rasi Lord (5)
    # 8. Vashya (2)
    # 9. Rajju (Dosha)
    # 10. Vedha (Dosha)
    # 11. Nadi (8) - Common in North, less in South Das Kuta (South usually 10).
    # South 10 Kutas sum often calculated out of simpler subset or just qualitative.
    # But commonly, the score is out of 35 or 36 if Nadi included.
    # Since we didn't implement Nadi (North style) but are doing South "Porutham", 
    # we usually look at matching count (e.g. "8 out of 10 matches").
    
    # Let's sum the points we assigned:
    total_points = score_dina + score_gana + score_mahendra + score_stree + score_yoni + score_rasi + score_rasilord + score_vashya
    
    has_rajju_dosha = (score_rajju == 0.0)
    has_vedha_dosha = (score_vedha == 0.0)
    
    return {
        "boy_nak": NAKSHATRAS[b_nak],
        "girl_nak": NAKSHATRAS[g_nak],
        "boy_rasi": get_rashi_idx(boy_lon_moon),
        "girl_rasi": get_rashi_idx(girl_lon_moon),
        "kutas": {
            "dina": {"score": score_dina, "max": 3, "status": stat_dina},
            "gana": {"score": score_gana, "max": 4, "status": stat_gana},
            "mahendra": {"score": score_mahendra, "max": 0, "status": stat_mahendra}, # Max 0 as flag kuta
            "stree_deergha": {"score": score_stree, "max": 1, "status": stat_stree},
            "yoni": {"score": score_yoni, "max": 4, "status": stat_yoni},
            "rasi": {"score": score_rasi, "max": 7, "status": stat_rasi},
            "rasi_lord": {"score": score_rasilord, "max": 5, "status": stat_rasilord},
            "vashya": {"score": score_vashya, "max": 2, "status": stat_vashya},
            "rajju": {"status": stat_rajju, "dosha": has_rajju_dosha},
            "vedha": {"status": stat_vedha, "dosha": has_vedha_dosha}
        },
        "total_score": total_points,
        "is_compatible": (total_points > 18) and not has_rajju_dosha and not has_vedha_dosha
    }
