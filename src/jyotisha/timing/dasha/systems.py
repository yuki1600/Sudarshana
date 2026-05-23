# src/dasa_systems.py
"""
Additional Dasa Systems based on BPHS (Brihat Parashara Hora Shastra)
"""
from datetime import datetime, timedelta
import pandas as pd

# Nakshatra names in order
NAK_NAMES = [
    "Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "P.Phalguni", "U.Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "P.Ashadha", "U.Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "P.Bhadra", "U.Bhadra", "Revati"
]

# Rashi names in Sanskrit
RASHI_SA = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
            "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"]

# ---------------------------------
# Additional Dasa Systems (Nakshatra-based)
# ---------------------------------

# Nakshatra indices for reference
NAK_INDEX = {name: idx for idx, name in enumerate(NAK_NAMES)}

# ---------------------------------
# Ashtottari Dasa (108 years, 8 planets - excludes Ketu)
# Start from 4 nakshatras after Ardra
# ---------------------------------
ASHTOTTARI_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Saturn", "Jupiter", "Rahu", "Venus"]
ASHTOTTARI_YEARS = {"Sun": 6, "Moon": 15, "Mars": 8, "Mercury": 17, "Saturn": 10, "Jupiter": 19, "Rahu": 12, "Venus": 21}
ASHTOTTARI_TOTAL = 108

# Ashtottari nakshatra spans: Sun starts 4 after Ardra, then 3, 4, 3, 4, 3, 4, 3 pattern
# Ardra = 5, so Sun starts at 5+4=9 (P.Phalguni)
ASHTOTTARI_NAK_SPANS = [4, 3, 4, 3, 4, 3, 4, 3]  # Each planet's nakshatra count
ASHTOTTARI_NAK_START = 5  # Ardra index

def build_ashtottari(moon_lon, local_start, cycles=2):
    """
    Build Ashtottari Dasa (108-year cycle, 8 planets excluding Ketu).
    """
    NAK_STEP = 360.0 / 27.0
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    
    # Find which dasa lord the birth nakshatra falls under
    # Count from Ardra (5) in the pattern 4,3,4,3,4,3,4,3 nakshatras per planet
    def get_lord_for_nak(nak_idx):
        # Normalize nakshatra index relative to Ashtottari start (Ardra)
        rel_nak = (nak_idx - ASHTOTTARI_NAK_START + 27) % 27
        cumulative = 0
        for i, span in enumerate(ASHTOTTARI_NAK_SPANS):
            cumulative += span
            if rel_nak < cumulative:
                within_lord_nak = rel_nak - (cumulative - span)
                return i, within_lord_nak, span
        return 0, 0, ASHTOTTARI_NAK_SPANS[0]
    
    lord_idx, within_nak, span = get_lord_for_nak(nak_index)
    start_lord = ASHTOTTARI_ORDER[lord_idx]
    
    # Calculate fraction of dasa remaining
    # within_nak is how many complete nakshatras passed within this lord's span
    completed_nak_frac = (within_nak + frac_in) / span
    remaining_frac = 1.0 - completed_nak_frac
    start_years_left = ASHTOTTARI_YEARS[start_lord] * remaining_frac
    
    rows = []
    cur = local_start
    
    # First (partial) period
    if start_years_left > 0.001:
        end = cur + timedelta(days=start_years_left * 365.25)
        rows.append({
            "Mahadasa": start_lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(start_years_left, 6)
        })
        cur = end
    
    # Subsequent periods
    j = (lord_idx + 1) % 8
    for _ in range(cycles * 8 - 1):
        lord = ASHTOTTARI_ORDER[j]
        years = ASHTOTTARI_YEARS[lord]
        end = cur + timedelta(days=years * 365.25)
        rows.append({
            "Mahadasa": lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(years, 6)
        })
        cur = end
        j = (j + 1) % 8
    
    return pd.DataFrame(rows)


# ---------------------------------
# Shodshottari Dasa (116 years, 8 planets)
# Count from Pushya (7), divide by 8, remainder determines lord
# ---------------------------------
SHODSHOTTARI_ORDER = ["Sun", "Mars", "Jupiter", "Saturn", "Ketu", "Moon", "Mercury", "Venus"]
SHODSHOTTARI_YEARS = {"Sun": 11, "Mars": 12, "Jupiter": 13, "Saturn": 14, "Ketu": 15, "Moon": 16, "Mercury": 17, "Venus": 18}
SHODSHOTTARI_TOTAL = 116
SHODSHOTTARI_START_NAK = 7  # Pushya

def build_shodshottari(moon_lon, local_start, cycles=2):
    """
    Build Shodshottari Dasa (116-year cycle).
    Count from Pushya to birth nakshatra, divide by 8.
    """
    NAK_STEP = 360.0 / 27.0
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    
    # Count from Pushya to birth nakshatra
    count = (nak_index - SHODSHOTTARI_START_NAK + 27) % 27 + 1
    remainder = count % 8
    if remainder == 0:
        remainder = 8
    lord_idx = remainder - 1
    
    start_lord = SHODSHOTTARI_ORDER[lord_idx]
    start_years_left = SHODSHOTTARI_YEARS[start_lord] * frac_left
    
    rows = []
    cur = local_start
    
    if start_years_left > 0.001:
        end = cur + timedelta(days=start_years_left * 365.25)
        rows.append({
            "Mahadasa": start_lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(start_years_left, 6)
        })
        cur = end
    
    j = (lord_idx + 1) % 8
    for _ in range(cycles * 8 - 1):
        lord = SHODSHOTTARI_ORDER[j]
        years = SHODSHOTTARI_YEARS[lord]
        end = cur + timedelta(days=years * 365.25)
        rows.append({
            "Mahadasa": lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(years, 6)
        })
        cur = end
        j = (j + 1) % 8
    
    return pd.DataFrame(rows)


# ---------------------------------
# Dwadashottari Dasa (112 years, 8 planets)
# Count from birth nakshatra to Revati, divide by 8
# ---------------------------------
DWADASHOTTARI_ORDER = ["Sun", "Jupiter", "Ketu", "Mercury", "Rahu", "Mars", "Saturn", "Moon"]
DWADASHOTTARI_YEARS = {"Sun": 7, "Jupiter": 9, "Ketu": 11, "Mercury": 13, "Rahu": 15, "Mars": 17, "Saturn": 19, "Moon": 21}
DWADASHOTTARI_TOTAL = 112
DWADASHOTTARI_END_NAK = 26  # Revati

def build_dwadashottari(moon_lon, local_start, cycles=2):
    """
    Build Dwadashottari Dasa (112-year cycle).
    Count from birth nakshatra to Revati, divide by 8.
    """
    NAK_STEP = 360.0 / 27.0
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    
    # Count from birth nakshatra to Revati
    count = (DWADASHOTTARI_END_NAK - nak_index + 27) % 27 + 1
    remainder = count % 8
    if remainder == 0:
        remainder = 8
    lord_idx = remainder - 1
    
    start_lord = DWADASHOTTARI_ORDER[lord_idx]
    start_years_left = DWADASHOTTARI_YEARS[start_lord] * frac_left
    
    rows = []
    cur = local_start
    
    if start_years_left > 0.001:
        end = cur + timedelta(days=start_years_left * 365.25)
        rows.append({
            "Mahadasa": start_lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(start_years_left, 6)
        })
        cur = end
    
    j = (lord_idx + 1) % 8
    for _ in range(cycles * 8 - 1):
        lord = DWADASHOTTARI_ORDER[j]
        years = DWADASHOTTARI_YEARS[lord]
        end = cur + timedelta(days=years * 365.25)
        rows.append({
            "Mahadasa": lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(years, 6)
        })
        cur = end
        j = (j + 1) % 8
    
    return pd.DataFrame(rows)


# ---------------------------------
# Panchottari Dasa (105 years, 7 planets)
# Count from Anuradha to birth nakshatra, divide by 7
# ---------------------------------
PANCHOTTARI_ORDER = ["Sun", "Mercury", "Saturn", "Mars", "Venus", "Moon", "Jupiter"]
PANCHOTTARI_YEARS = {"Sun": 12, "Mercury": 13, "Saturn": 14, "Mars": 15, "Venus": 16, "Moon": 17, "Jupiter": 18}
PANCHOTTARI_TOTAL = 105
PANCHOTTARI_START_NAK = 16  # Anuradha

def build_panchottari(moon_lon, local_start, cycles=2):
    """
    Build Panchottari Dasa (105-year cycle, 7 planets).
    Count from Anuradha to birth nakshatra, divide by 7.
    """
    NAK_STEP = 360.0 / 27.0
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    
    count = (nak_index - PANCHOTTARI_START_NAK + 27) % 27 + 1
    remainder = count % 7
    if remainder == 0:
        remainder = 7
    lord_idx = remainder - 1
    
    start_lord = PANCHOTTARI_ORDER[lord_idx]
    start_years_left = PANCHOTTARI_YEARS[start_lord] * frac_left
    
    rows = []
    cur = local_start
    
    if start_years_left > 0.001:
        end = cur + timedelta(days=start_years_left * 365.25)
        rows.append({
            "Mahadasa": start_lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(start_years_left, 6)
        })
        cur = end
    
    j = (lord_idx + 1) % 7
    for _ in range(cycles * 7 - 1):
        lord = PANCHOTTARI_ORDER[j]
        years = PANCHOTTARI_YEARS[lord]
        end = cur + timedelta(days=years * 365.25)
        rows.append({
            "Mahadasa": lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(years, 6)
        })
        cur = end
        j = (j + 1) % 7
    
    return pd.DataFrame(rows)


# ---------------------------------
# Shatabdik Dasa (100 years, 7 planets)
# Count from Revati to birth nakshatra, divide by 7
# ---------------------------------
SHATABDIK_ORDER = ["Sun", "Moon", "Venus", "Mercury", "Jupiter", "Mars", "Saturn"]
SHATABDIK_YEARS = {"Sun": 5, "Moon": 5, "Venus": 10, "Mercury": 10, "Jupiter": 20, "Mars": 20, "Saturn": 30}
SHATABDIK_TOTAL = 100
SHATABDIK_START_NAK = 26  # Revati

def build_shatabdik(moon_lon, local_start, cycles=2):
    """
    Build Shatabdik Dasa (100-year cycle, 7 planets).
    Count from Revati to birth nakshatra, divide by 7.
    """
    NAK_STEP = 360.0 / 27.0
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    
    count = (nak_index - SHATABDIK_START_NAK + 27) % 27 + 1
    remainder = count % 7
    if remainder == 0:
        remainder = 7
    lord_idx = remainder - 1
    
    start_lord = SHATABDIK_ORDER[lord_idx]
    start_years_left = SHATABDIK_YEARS[start_lord] * frac_left
    
    rows = []
    cur = local_start
    
    if start_years_left > 0.001:
        end = cur + timedelta(days=start_years_left * 365.25)
        rows.append({
            "Mahadasa": start_lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(start_years_left, 6)
        })
        cur = end
    
    j = (lord_idx + 1) % 7
    for _ in range(cycles * 7 - 1):
        lord = SHATABDIK_ORDER[j]
        years = SHATABDIK_YEARS[lord]
        end = cur + timedelta(days=years * 365.25)
        rows.append({
            "Mahadasa": lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(years, 6)
        })
        cur = end
        j = (j + 1) % 7
    
    return pd.DataFrame(rows)


# ---------------------------------
# Chaturashiti-sama Dasa (84 years, 7 planets, each 12 years)
# Count from Swati to birth nakshatra, divide by 7
# ---------------------------------
CHATURASHITI_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
CHATURASHITI_YEARS = {"Sun": 12, "Moon": 12, "Mars": 12, "Mercury": 12, "Jupiter": 12, "Venus": 12, "Saturn": 12}
CHATURASHITI_TOTAL = 84
CHATURASHITI_START_NAK = 14  # Swati

def build_chaturashiti_sama(moon_lon, local_start, cycles=2):
    """
    Build Chaturashiti-sama Dasa (84-year cycle, 7 planets, each 12 years).
    Count from Swati to birth nakshatra, divide by 7.
    """
    NAK_STEP = 360.0 / 27.0
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    
    count = (nak_index - CHATURASHITI_START_NAK + 27) % 27 + 1
    remainder = count % 7
    if remainder == 0:
        remainder = 7
    lord_idx = remainder - 1
    
    start_lord = CHATURASHITI_ORDER[lord_idx]
    start_years_left = 12.0 * frac_left  # All planets have 12 years
    
    rows = []
    cur = local_start
    
    if start_years_left > 0.001:
        end = cur + timedelta(days=start_years_left * 365.25)
        rows.append({
            "Mahadasa": start_lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(start_years_left, 6)
        })
        cur = end
    
    j = (lord_idx + 1) % 7
    for _ in range(cycles * 7 - 1):
        lord = CHATURASHITI_ORDER[j]
        end = cur + timedelta(days=12 * 365.25)
        rows.append({
            "Mahadasa": lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": 12.0
        })
        cur = end
        j = (j + 1) % 7
    
    return pd.DataFrame(rows)


# ---------------------------------
# Dwisaptati-sama Dasa (72 years, 8 planets, each 9 years)
# Count from Mula to birth nakshatra, divide by 8
# ---------------------------------
DWISAPTATI_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]
DWISAPTATI_YEARS = {"Sun": 9, "Moon": 9, "Mars": 9, "Mercury": 9, "Jupiter": 9, "Venus": 9, "Saturn": 9, "Rahu": 9}
DWISAPTATI_TOTAL = 72
DWISAPTATI_START_NAK = 18  # Mula

def build_dwisaptati_sama(moon_lon, local_start, cycles=2):
    """
    Build Dwisaptati-sama Dasa (72-year cycle, 8 planets, each 9 years).
    Count from Mula to birth nakshatra, divide by 8.
    """
    NAK_STEP = 360.0 / 27.0
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    
    count = (nak_index - DWISAPTATI_START_NAK + 27) % 27 + 1
    remainder = count % 8
    if remainder == 0:
        remainder = 8
    lord_idx = remainder - 1
    
    start_lord = DWISAPTATI_ORDER[lord_idx]
    start_years_left = 9.0 * frac_left  # All planets have 9 years
    
    rows = []
    cur = local_start
    
    if start_years_left > 0.001:
        end = cur + timedelta(days=start_years_left * 365.25)
        rows.append({
            "Mahadasa": start_lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(start_years_left, 6)
        })
        cur = end
    
    j = (lord_idx + 1) % 8
    for _ in range(cycles * 8 - 1):
        lord = DWISAPTATI_ORDER[j]
        end = cur + timedelta(days=9 * 365.25)
        rows.append({
            "Mahadasa": lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": 9.0
        })
        cur = end
        j = (j + 1) % 8
    
    return pd.DataFrame(rows)


# ---------------------------------
# Shastihayani Dasa (60 years, 8 planets)
# Nakshatra groups define lords directly
# ---------------------------------
SHASTIHAYANI_ORDER = ["Jupiter", "Sun", "Mars", "Moon", "Mercury", "Venus", "Saturn", "Rahu"]
SHASTIHAYANI_YEARS = {"Jupiter": 10, "Sun": 10, "Mars": 10, "Moon": 6, "Mercury": 6, "Venus": 6, "Saturn": 6, "Rahu": 6}
SHASTIHAYANI_TOTAL = 60

# Nakshatra to lord mapping (as per BPHS)
SHASTIHAYANI_NAK_LORD = {
    0: "Jupiter", 1: "Jupiter", 2: "Jupiter", 5: "Jupiter",  # Ashvini, Bharani, Krittika, Punarvasu
    3: "Sun", 4: "Sun", 5: "Sun", 20: "Sun",  # Rohini, Mrigashira, Ardra, U.Ashadha
    6: "Mars", 7: "Mars", 8: "Mars", 26: "Mars",  # Pushya, Ashlesha, Magha, Revati
    10: "Moon", 11: "Moon", 12: "Moon",  # P.Phalguni, U.Phalguni, Hasta
    14: "Mercury", 15: "Mercury", 16: "Mercury",  # Swati, Vishakha, Anuradha
    17: "Venus", 18: "Venus", 19: "Venus",  # Jyeshtha, Mula, P.Ashadha
    21: "Saturn", 22: "Saturn", 23: "Saturn",  # Shravana, Dhanishtha, Shatabhisha
    24: "Rahu", 25: "Rahu", 26: "Rahu",  # P.Bhadra, U.Bhadra, (Revati already assigned to Mars)
}

def build_shastihayani(moon_lon, local_start, cycles=2):
    """
    Build Shastihayani Dasa (60-year cycle, 8 planets).
    Nakshatra groups determine the lord directly.
    """
    NAK_STEP = 360.0 / 27.0
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    
    # Proper nakshatra group mapping
    nak_groups = [
        [0, 1, 2, 6],    # Jupiter: Ashvini, Bharani, Krittika, Punarvasu
        [3, 4, 5, 20],   # Sun: Rohini, Mrigashira, Ardra, U.Ashadha
        [7, 8, 9, 26],   # Mars: Pushya, Ashlesha, Magha, Revati
        [10, 11, 12],    # Moon: P.Phalguni, U.Phalguni, Hasta
        [14, 15, 16],    # Mercury: Swati, Vishakha, Anuradha
        [17, 18, 19],    # Venus: Jyeshtha, Mula, P.Ashadha
        [21, 22, 23],    # Saturn: Shravana, Dhanishtha, Shatabhisha (includes Abhijit conceptually)
        [24, 25, 13],    # Rahu: P.Bhadra, U.Bhadra, Chitra
    ]
    
    # Find which group contains our nakshatra
    lord_idx = 0
    for i, group in enumerate(nak_groups):
        if nak_index in group:
            lord_idx = i
            break
    
    start_lord = SHASTIHAYANI_ORDER[lord_idx]
    start_years_left = SHASTIHAYANI_YEARS[start_lord] * frac_left
    
    rows = []
    cur = local_start
    
    if start_years_left > 0.001:
        end = cur + timedelta(days=start_years_left * 365.25)
        rows.append({
            "Mahadasa": start_lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(start_years_left, 6)
        })
        cur = end
    
    j = (lord_idx + 1) % 8
    for _ in range(cycles * 8 - 1):
        lord = SHASTIHAYANI_ORDER[j]
        years = SHASTIHAYANI_YEARS[lord]
        end = cur + timedelta(days=years * 365.25)
        rows.append({
            "Mahadasa": lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(years, 6)
        })
        cur = end
        j = (j + 1) % 8
    
    return pd.DataFrame(rows)


# ---------------------------------
# Shat-trimshat-sama Dasa (36 years, 8 planets)
# Count from Shravana to birth nakshatra, divide by 8
# ---------------------------------
SHATTRIMSHAT_ORDER = ["Moon", "Sun", "Jupiter", "Mars", "Mercury", "Saturn", "Venus", "Rahu"]
SHATTRIMSHAT_YEARS = {"Moon": 1, "Sun": 2, "Jupiter": 3, "Mars": 4, "Mercury": 5, "Saturn": 6, "Venus": 7, "Rahu": 8}
SHATTRIMSHAT_TOTAL = 36
SHATTRIMSHAT_START_NAK = 21  # Shravana

def build_shattrimshat_sama(moon_lon, local_start, cycles=3):
    """
    Build Shat-trimshat-sama Dasa (36-year cycle, 8 planets).
    Count from Shravana to birth nakshatra, divide by 8.
    """
    NAK_STEP = 360.0 / 27.0
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    
    count = (nak_index - SHATTRIMSHAT_START_NAK + 27) % 27 + 1
    remainder = count % 8
    if remainder == 0:
        remainder = 8
    lord_idx = remainder - 1
    
    start_lord = SHATTRIMSHAT_ORDER[lord_idx]
    start_years_left = SHATTRIMSHAT_YEARS[start_lord] * frac_left
    
    rows = []
    cur = local_start
    
    if start_years_left > 0.001:
        end = cur + timedelta(days=start_years_left * 365.25)
        rows.append({
            "Mahadasa": start_lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(start_years_left, 6)
        })
        cur = end
    
    j = (lord_idx + 1) % 8
    for _ in range(cycles * 8 - 1):
        lord = SHATTRIMSHAT_ORDER[j]
        years = SHATTRIMSHAT_YEARS[lord]
        end = cur + timedelta(days=years * 365.25)
        rows.append({
            "Mahadasa": lord,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": round(years, 6)
        })
        cur = end
        j = (j + 1) % 8
    
    return pd.DataFrame(rows)


# ---------------------------------
# Chakra Dasa (120 years, 12 rashis, each 10 years)
# Rashi-based dasa, starts from Lagna, Lagna Lord's sign, or 2nd house
# ---------------------------------
def build_chakra(asc_rashi_idx, lagna_lord_rashi_idx, local_start, is_night=False, is_sandhya=False, cycles=2):
    """
    Build Chakra Dasa (120-year cycle, 12 rashis, each 10 years).
    
    Args:
        asc_rashi_idx: Index of Lagna rashi (0-11)
        lagna_lord_rashi_idx: Index of rashi where Lagna lord is placed
        local_start: datetime of birth
        is_night: True if birth is at night
        is_sandhya: True if birth is during sandhya (twilight)
    """
    # Determine starting rashi based on birth time
    if is_sandhya:
        # Start from 2nd house rashi
        start_rashi = (asc_rashi_idx + 1) % 12
    elif is_night:
        # Start from Lagna rashi
        start_rashi = asc_rashi_idx
    else:
        # Day birth: start from rashi where Lagna lord is placed
        start_rashi = lagna_lord_rashi_idx
    
    rows = []
    cur = local_start
    
    for cycle in range(cycles):
        for i in range(12):
            rashi_idx = (start_rashi + i) % 12
            rashi_name = RASHI_SA[rashi_idx]
            years = 10.0
            end = cur + timedelta(days=years * 365.25)
            rows.append({
                "Mahadasa": rashi_name,
                "Rashi_Idx": rashi_idx,
                "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
                "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
                "Duration (years)": years
            })
            cur = end
    
    return pd.DataFrame(rows)


# ---------------------------------
# Generic Sub-period Calculation Logic
# ---------------------------------

# Vimshottari & Yogini constants (mirrored here for generic access)
VIMSHOTTARI_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
VIMSHOTTARI_TOTAL = 120

YOGINI_ORDER = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOGINI_YEARS = {"Mangala": 1, "Pingala": 2, "Dhanya": 3, "Bhramari": 4, "Bhadrika": 5, "Ulka": 6, "Siddha": 7, "Sankata": 8}
YOGINI_TOTAL = 36

def get_dasa_config(system_name):
    """
    Returns configuration (Order List, Years Dict, Total Years) for a given Dasa system.
    """
    if system_name == 'vimshottari': return VIMSHOTTARI_ORDER, VIMSHOTTARI_YEARS, VIMSHOTTARI_TOTAL
    if system_name == 'yogini': return YOGINI_ORDER, YOGINI_YEARS, YOGINI_TOTAL
    if system_name == 'ashtottari': return ASHTOTTARI_ORDER, ASHTOTTARI_YEARS, ASHTOTTARI_TOTAL
    if system_name == 'shodshottari': return SHODSHOTTARI_ORDER, SHODSHOTTARI_YEARS, SHODSHOTTARI_TOTAL
    if system_name == 'dwadashottari': return DWADASHOTTARI_ORDER, DWADASHOTTARI_YEARS, DWADASHOTTARI_TOTAL
    if system_name == 'panchottari': return PANCHOTTARI_ORDER, PANCHOTTARI_YEARS, PANCHOTTARI_TOTAL
    if system_name == 'shatabdik': return SHATABDIK_ORDER, SHATABDIK_YEARS, SHATABDIK_TOTAL
    if system_name == 'chaturashiti_sama': return CHATURASHITI_ORDER, CHATURASHITI_YEARS, CHATURASHITI_TOTAL
    if system_name == 'dwisaptati_sama': return DWISAPTATI_ORDER, DWISAPTATI_YEARS, DWISAPTATI_TOTAL
    if system_name == 'shastihayani': return SHASTIHAYANI_ORDER, SHASTIHAYANI_YEARS, SHASTIHAYANI_TOTAL
    if system_name == 'shattrimshat_sama': return SHATTRIMSHAT_ORDER, SHATTRIMSHAT_YEARS, SHATTRIMSHAT_TOTAL
    if system_name == 'chakra': 
        return RASHI_SA, {r: 10 for r in RASHI_SA}, 120
    return None, None, None

def calculate_generic_sub_periods(system_name, parent_lord, parent_start, parent_duration_years):
    """
    Calculate sub-periods (Antardasha/Pratyantardasha) for a given parent period.
    returns list of dicts.
    """
    order, years_map, total_years = get_dasa_config(system_name)
    if not order: return []
    
    # Determine start index based on parent lord
    # Rule: Sub-periods typically start with the Parent Lord himself/herself
    try:
        start_idx = order.index(parent_lord)
    except ValueError:
        # Fallback if parent lord not found (e.g. spelling mismatch), start from 0
        start_idx = 0

    rows = []
    # Parse start time if string
    if isinstance(parent_start, str):
        try:
            cur = datetime.strptime(parent_start, "%Y-%m-%d %H:%M:%S")
        except:
             # Try simpler format if relevant, or fail
             try:
                 cur = datetime.fromisoformat(parent_start)
             except:
                 # Last resort fallback if parsing fails, shouldn't happen with valid API use
                 return []
    else:
        cur = parent_start

    # Iterate through all sub-lords in order, starting from parent_lord
    num_lords = len(order)
    for i in range(num_lords):
        idx = (start_idx + i) % num_lords
        sub_lord = order[idx]
        
        # Calculate duration
        # Formula: Sub Duration = (Parent Duration * Sub Lord Years) / Total Dasa Years
        sub_lord_years = years_map.get(sub_lord, 0)
        
        if total_years > 0:
            sub_duration_years = (parent_duration_years * sub_lord_years) / total_years
        else:
            sub_duration_years = 0
            
        sub_duration_days = sub_duration_years * 365.25
        
        end = cur + timedelta(days=sub_duration_days)
        
        rows.append({
            "Lord": sub_lord,
            "Start": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (days)": round(sub_duration_days, 2),
            "Duration (years)": round(sub_duration_years, 6)
        })
        cur = end
        

# ---------------------------------
# Jaimini / Rashi-based Dasa Utilities
# ---------------------------------

def get_planet_longitude(planet_name, points):
    for p in points:
        if p["Point"] == planet_name:
            if "Longitude (Dec)" in p:
                return p["Longitude (Dec)"]
            # Fallback if only Sign DMS is available (parse logic needed? usually Dec is there)
    return 0.0

def get_planet_rashi(planet_name, points):
    for p in points:
        if p["Point"] == planet_name:
            return p.get("Rashi_Idx", 0)
    return 0

def get_planets_in_rashi(rashi_idx, points):
    # Filter for main 7 planets + Rahu/Ketu
    main_grahas = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu (true)", "Ketu (true)"]
    in_sign = []
    for p in points:
        if p["Point"] in main_grahas and p.get("Rashi_Idx") == rashi_idx:
            in_sign.append(p)
    return in_sign

def get_sign_strength_score(rashi_idx, points):
    """
    Calculate rough Jaimini strength score for a sign.
    1. Count planets (more is stronger).
    2. Presence of benefic/malefic can be added?
    3. Exaltation status of occupants.
    5. For simple comparison: Number of planets > Exalted Planet Present > Strength of Lord (skipped for now).
    """
    occupants = get_planets_in_rashi(rashi_idx, points)
    score = len(occupants) * 100
    
    # Exaltation bonus
    # Sun: Aries(0), Moon: Taurus(1), Mars: Capricorn(9), Merc: Virgo(5), Jup: Cancer(3), Ven: Pisces(11), Sat: Libra(6)
    exalt_map = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6, "Rahu (true)": 1, "Ketu (true)": 7}
    
    for p in occupants:
        pt_name = p["Point"]
        if exalt_map.get(pt_name) == rashi_idx:
            score += 50
            
    return score

def get_stronger_sign(rashi_a, rashi_b, points):
    """
    Compare two signs and return the stronger one (index).
    Rule 1: More planets.
    Rule 2: If equal, (simplified) return rashi_a (needs full Jaimini logic, but this is a starter).
    """
    score_a = get_sign_strength_score(rashi_a, points)
    score_b = get_sign_strength_score(rashi_b, points)
    
    if score_a > score_b:
        return rashi_a
    elif score_b > score_a:
        return rashi_b
    else:
        # Tie-breaking (simplified: Dual > Fixed > Movable is NOT for strength, that's for other things)
        # Proper tie-break usually checks Lord's strength. 
        # For now, default to A if really tied.
        return rashi_a

# ---------------------------------
# Sthir Dasa
# ---------------------------------
# Movable (Char): 7 years
# Fixed (Sthir): 8 years
# Dual (Dvisva): 9 years
# Start: Brahma Grah Ashrit Rashi
# Order: Onwards if odd, Reverse if even

def get_brahma_graha(points, asc_rashi_idx):
    """
    Simplified Brahma Graha finding:
    Lords of 6, 8, 12 from Lagna.
    Find strongest among them.
    Must be in Lagna or 7th? Or placed in odd sign within 6th bhava?
    
    Given complexity and "Brahma" variations, we will try a standard approach:
    1. Identify Lords of 6, 8, 12 from Lagna.
    2. Check their strengths (using Sign strength of their placement).
    3. Return the planet name.
    """
    # Lords mapping (0=Mars, 1=Venus, etc.)
    sign_lords = {0:"Mars",1:"Venus",2:"Mercury",3:"Moon",4:"Sun",5:"Mercury",6:"Venus",7:"Mars",8:"Jupiter",9:"Saturn",10:"Saturn",11:"Jupiter"}
    
    lord_6 = sign_lords[(asc_rashi_idx + 5) % 12]
    lord_8 = sign_lords[(asc_rashi_idx + 7) % 12]
    lord_12 = sign_lords[(asc_rashi_idx + 11) % 12]
    
    candidates = list(set([lord_6, lord_8, lord_12]))
    
    # Compare strength (by placement sign strength)
    best_graha = candidates[0]
    best_score = -1
    
    for graha in candidates:
        r_idx = get_planet_rashi(graha, points)
        # Score of the sign he is in
        sc = get_sign_strength_score(r_idx, points)
        if sc > best_score:
            best_score = sc
            best_graha = graha
            
    return best_graha, get_planet_rashi(best_graha, points)

def build_sthir_dasa(points, local_start, cycles=1):
    """
    Sthir Dasa (7, 8, 9 years for Movable, Fixed, Dual).
    Starts from Brahma Graha's sign.
    """
    # Need Ascendant for Brahma calculation
    asc_entry = next((p for p in points if "Ascendant" in p.get("Point", "")), None)
    if not asc_entry:
         # Fallback
         asc_rashi_idx = 0
    else:
        asc_rashi_idx = asc_entry["Rashi_Idx"]
        
    brahma_graha, start_rashi = get_brahma_graha(points, asc_rashi_idx)
    
    # Check if start rashi is odd or even for direction
    # Odd (Mesha 0, Mithuna 2...) -> Onwards
    # Even (Vrishabha 1, Karka 3...) -> Reverse
    is_odd = (start_rashi % 2 == 0) # 0 is Aries (Odd), 1 is Taurus (Even)
    
    direction = 1 if is_odd else -1
    
    rows = []
    cur = local_start
    
    # 12 signs
    for i in range(12 * cycles):
        rashi_idx = (start_rashi + (i * direction)) % 12
        rashi_name = RASHI_SA[rashi_idx]
        
        # Duration: Movable=7, Fixed=8, Dual=9
        # Movable: 0, 3, 6, 9
        # Fixed: 1, 4, 7, 10
        # Dual: 2, 5, 8, 11
        rem = rashi_idx % 3
        if rem == 0: duration = 7 # Movable (Aries etc)
        elif rem == 1: duration = 8 # Fixed (Taurus etc)
        else: duration = 9 # Dual (Gemini etc)
        
        end = cur + timedelta(days=duration * 365.25)
        
        rows.append({
            "Mahadasa": rashi_name,
            "Rashi_Idx": rashi_idx,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": float(duration)
        })
        cur = end
        
    return pd.DataFrame(rows)

# ---------------------------------
# Yogardha Dasa
# ---------------------------------
# Spans are half of (Char + Sthir).
# Char Dasa spans: Count from Sign to Lord (approx, or specific Char logic).
# Sthir spans: 7/8/9.
# Start: Lagn or Yuvati (7th), whichever is stronger.
# Order: Onwards if odd, Reverse if even.

def get_char_dasa_span(rashi_idx, points):
    """
    Basic Char Dasa span calculation:
    Count from Sign to its Lord.
    If Lord is in own sign -> 12 years.
    Forward/Reverse counting depends on sign.
    Rule:
    Aries (Odd, Fwd) -> Mars
    Taurus (Even, Fwd) -> Venus
    Gemini (Odd, Fwd) -> Mercury
    Cancer (Even, Rev) -> Moon
    Leo (Odd, Rev) -> Sun
    Virgo (Even, Rev) -> Mercury
    Libra (Odd, Fwd) -> Venus
    Scorpio (Even, Fwd) -> Mars (Ket?)
    Sag (Odd, Fwd) -> Jup
    Cap (Even, Rev) -> Sat
    Aq (Odd, Rev) -> Sat (Rah?)
    Pisces (Even, Rev) -> Jup
    
    (Simplified standard Char Dasa spans often used in Jaimini)
    """
    # Mapping for direction of counting to lord
    # 1 = Forward, -1 = Reverse
    # Ar(0, F), Ta(1, F), Ge(2, F), Cn(3, R), Le(4, R), Vi(5, R), Li(6, F), Sc(7, F), Sg(8, F), Cp(9, R), Aq(10, R), Pi(11, R)
    directions = [1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1]
    
    lord_map = {0:"Mars",1:"Venus",2:"Mercury",3:"Moon",4:"Sun",5:"Mercury",6:"Venus",7:"Mars",8:"Jupiter",9:"Saturn",10:"Saturn",11:"Jupiter"}
    lord_name = lord_map[rashi_idx]
    
    # Scorpio/Aquarius exceptions (Ketu/Rahu co-lords) - simplified to Mars/Saturn for now unless specified
    
    lord_rashi = get_planet_rashi(lord_name, points)
    
    if lord_rashi == rashi_idx:
        return 12
    
    step = directions[rashi_idx]
    
    # Count from Rashi to Lord
    count = 0
    curr = rashi_idx
    while True:
        curr = (curr + step) % 12
        count += 1
        if curr == lord_rashi:
            break
            
    # Span is count - 1? No, usually count.
    # Ex: Aries to Mars in Aries -> 12.
    # Aries to Mars in Taurus (2nd) -> 1? 
    # Standard: Count blocks. If result is 0, make it 12?
    # BPHS logic: "Count from sign to lord".
    return count 

def build_yogardha_dasa(points, local_start, cycles=1):
    """
    Yogardha Dasa.
    Start: Stronger of Lagna or 7th.
    Order: Onwards if odd, Reverse if even.
    Duration: (Char Span + Sthir Span) / 2
    """
    asc_entry = next((p for p in points if "Ascendant" in p.get("Point", "")), None)
    asc_idx = asc_entry["Rashi_Idx"] if asc_entry else 0
    seventh_idx = (asc_idx + 6) % 12
    
    start_rashi = get_stronger_sign(asc_idx, seventh_idx, points)
    
    is_odd = (start_rashi % 2 == 0)
    direction = 1 if is_odd else -1
    
    rows = []
    cur = local_start
    
    for i in range(12 * cycles):
        rashi_idx = (start_rashi + (i * direction)) % 12
        rashi_name = RASHI_SA[rashi_idx]
        
        # Char span
        char_span = get_char_dasa_span(rashi_idx, points)
        
        # Sthir span
        rem = rashi_idx % 3
        if rem == 0: sthir_span = 7
        elif rem == 1: sthir_span = 8
        else: sthir_span = 9
        
        # Average
        duration = (char_span + sthir_span) / 2.0
        
        end = cur + timedelta(days=duration * 365.25)
        rows.append({
            "Mahadasa": rashi_name,
            "Rashi_Idx": rashi_idx,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": duration
        })
        cur = end
        
    return pd.DataFrame(rows)


# ---------------------------------
# Utility: Jaimini Karakas
# ---------------------------------

def get_jaimini_karakas(points):
    """
    Determine Jaimini Karakas based on longitude (degree only, ignoring sign).
    Returns dict: {'AK': 'Sun', 'AmK': 'Moon', ...}
    Order: AK, AmK, BK, MK, PiK, PK, GK, DK (8 karakas scheme usually, or 7).
    Standard BPHS uses 7 Karakas (Sun to Sat), but sometimes 8 (incl Rahu).
    Let's use 7 Karakas by default as per most standard texts unless Rahu is very advanced.
    However, many Jaimini inputs expect 8. We will use 7 for simplicity and consistency with standard Parashara modes unless Rahu/Ketu logic is intricate.
    Actually, let's Stick to 7 Karakas (AK, AmK, BK, MK, PiK, PK, GK, DK is 8?? No.
    7 Karakas: AK, AmK, BK, MK, PiK, GK, DK. (PK merged? No).
    Let's just sort 7 planets: Sun, Moon, Mars, Merc, Jup, Ven, Sat.
    """
    # 7 Planets
    grahas = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    # Get longitudes modulo 30
    candidates = []
    for g in grahas:
        lon = get_planet_longitude(g, points)
        lon_in_sign = lon % 30.0
        candidates.append({"name": g, "deg": lon_in_sign})
        
    # Sort descending
    candidates.sort(key=lambda x: x["deg"], reverse=True)
    
    # Map to Karakas (7 scheme)
    # AK (Atma), AmK (Amatya), BK (Bhratri), MK (Matri), PK (Putra), GK (Gnati), DK (Dara)
    tags = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
    karakas = {}
    for i, tag in enumerate(tags):
        if i < len(candidates):
            karakas[tag] = candidates[i]["name"]
            
    return karakas

# ---------------------------------
# Kendradi Dasa
# ---------------------------------

def build_kendradi_dasa(points, local_start, variant="lagn", cycles=1):
    """
    Kendradi Dasa.
    variant="lagn": Lagn Kendradi. Starts from stronger of Lagna or 7th.
    variant="ak": Atmakaraka Kendradi. Starts from stronger of AK sign or 7th from AK.
    
    Dashas of Fixed Rashis in the Kendr etc. (1, 4, 7, 10).
    BUT text says: "Dashas of Fixed Rashis in the Kendr etc." -> This implies the dashas ARE the fixed signs?
    Or "Dashas OF RASHIS in Kendr". The text says "Dashas of Fixed Rashis in the Kendr".
    Actually standard Kendradi interpretation:
    - If start sign is Odd: Order is 1, 4, 7, 10, 2, 5, 8, 11, 3, 6, 9, 12 (Kendras, Panaparas, Apoklimas).
    - If start sign is Even: Order is Reverse? 
    Wait, "Dashas of Fixed Rashis in the Kendr etc." might mean "Sthir Dasha behavior"?
    Let's stick to the text: "In this system there are Dashas of Fixed Rashis in the Kendr etc. from Lagn..."
    "Dashas would be in the order of comparative strength of the Rashis."
    This suggests we take Kendras (1,4,7,10), find the strongest? Or iterate them?
    Standard Kendradi (Sangamagrama Madhava etc):
    Sequence of signs: Kendras from Start, then Panaparas from Start, then Apoklimas from Start.
    Order logic:
    If Start is Odd: 1, 4, 7, 10 (Direct).
    If Start is Even: 1, 10, 7, 4 (Reverse).
    Or is it based on odd/even of the *signs*?
    Text: "placed in an odd Rashi, the Kendr etc. are counted in the onward order."
    
    Duration: "same as in Char Dasha" (Count to lord).
    
    Let's implement the Sequence logic (Kendras -> Panaparas -> Apoklimas).
    """
    # 1. Determine Start Rashi
    if variant == "ak":
        karakas = get_jaimini_karakas(points)
        ak_name = karakas.get("AK", "Sun")
        start_node_1 = get_planet_rashi(ak_name, points)
    else:
        asc = next((p for p in points if "Ascendant" in p.get("Point","")), None)
        start_node_1 = asc["Rashi_Idx"] if asc else 0
        
    start_node_2 = (start_node_1 + 6) % 12
    
    start_rashi = get_stronger_sign(start_node_1, start_node_2, points)
    
    # 2. Determine Order
    # "If Lagn/Yuvati ... is placed in an odd Rashi, the Kendr etc. are counted in the onward order."
    is_odd = (start_rashi % 2 == 0) # 0=Aries(Odd)
    
    if is_odd:
        # Onward: 1, 4, 7, 10 from Start
        # Groups: Kendras (0, 3, 6, 9 offset), Panaparas (1, 4, 7, 10 offset), Apoklimas (2, 5, 8, 11 offset)
        offsets = [0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8, 11]
    else:
        # Reverse/Backward
        # Kendras reverse: 1, 10, 7, 4 -> offsets 0, 9, 6, 3
        # Panaparas reverse: 2, 11, 8, 5 -> offsets 1, 10, 7, 4
        # Apoklimas reverse: 3, 12, 9, 6 -> offsets 2, 11, 8, 5
        offsets = [0, 9, 6, 3, 1, 10, 7, 4, 2, 11, 8, 5]
        
    rows = []
    cur = local_start
    
    for i in range(12 * cycles):
        # offsets cycle every 12
        off = offsets[i % 12]
        rashi_idx = (start_rashi + off) % 12
        rashi_name = RASHI_SA[rashi_idx]
        
        # Duration: Char Dasha like (Count to Lord)
        # Note: BPHS says "same as Char Dasha", "arrive at by counting up to the Rashi of the Grah, which is stronger..."
        # Simplified: Use `get_char_dasa_span`
        years = get_char_dasa_span(rashi_idx, points)
        
        end = cur + timedelta(days=years * 365.25)
        rows.append({
            "Mahadasa": rashi_name,
            "Rashi_Idx": rashi_idx,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": float(years)
        })
        cur = end
        
    return pd.DataFrame(rows)

# ---------------------------------
# Karak Dasa
# ---------------------------------
# First Dasha: AK.
# Subsequent: Remaining 7 Karakas in order.
# Years: Count from Lagn to Karak.

def build_karak_dasa(points, local_start, cycles=1):
    karakas = get_jaimini_karakas(points)
    # Order: AK, AmK, BK, MK, PK, GK, DK
    k_order = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
    
    # BPHS says "remaining 7 Karakas". We have 7 total.
    # Maybe Rahu is 8th? "Atma Karak and subsequent... remaining 7". This implies 8 total.
    # If using 7 grahas, we only have 7 karakas.
    # Let's assume standard 7 karaka cycle for now.
    
    asc = next((p for p in points if "Ascendant" in p.get("Point","")), None)
    lagna_idx = asc["Rashi_Idx"] if asc else 0
    
    rows = []
    cur = local_start
    
    for _ in range(cycles):
        for k_tag in k_order:
            p_name = karakas.get(k_tag)
            if not p_name: continue
            
            p_rashi_idx = get_planet_rashi(p_name, points)
            
            # Years: Count from Lagn to Karak
            # Count is always forward? Text: "Counted from Lagn up to the Karak". Usually forward.
            count = (p_rashi_idx - lagna_idx + 12) % 12
            if count == 0: count = 12 # 12th house is 12 years? or 0dist is 12?
            # Actually distance logic: 1st house = 1 year?
            years = count if count > 0 else 12 # 0 distance (same sign) -> 12 years usually or 1?
            # "Equal to number of Rashi counted..." -> 1st to 1st is 1. 1st to 2nd is 2.
            # BPHS Verse 178.
            # Let's use 1 for same sign, 12 for 12th.
            if p_rashi_idx == lagna_idx: years = 1 # Or 12? Usually Distance = IndexDiff + 1
            else: years = (p_rashi_idx - lagna_idx + 12) % 12 + 1 # Wait, check simple math. 0 off -> 1. 1 off -> 2.
            # If p=Lagna, diff=0, +1 -> 1. Correct.
            
            end = cur + timedelta(days=years * 365.25)
            rows.append({
                "Mahadasa": p_name, # Dasa of the Planet (Karak)
                "Type": k_tag,
                "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
                "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
                "Duration (years)": float(years)
            })
            cur = end

    return pd.DataFrame(rows)

# ---------------------------------
# Manduk Dasa
# ---------------------------------
# Start: Stronger of Lagna or 7th.
# Order: Next 3rd Rashi (Jump 3).
# Direction: Odd -> Onward, Even -> Reverse.
# Years: Sthir Dasa years (7/8/9).

def build_manduk_dasa(points, local_start, cycles=1):
    asc = next((p for p in points if "Ascendant" in p.get("Point","")), None)
    asc_idx = asc["Rashi_Idx"] if asc else 0
    sev_idx = (asc_idx + 6) % 12
    
    start_rashi = get_stronger_sign(asc_idx, sev_idx, points)
    is_odd = (start_rashi % 2 == 0)
    direction = 1 if is_odd else -1
    
    # Jump 3 means: 1, 4, 7, 10... (Kendra pattern)
    # "Next 3rd Rashi". 1st -> 4th (add 3).
    
    rows = []
    cur = local_start
    
    curr_rashi = start_rashi
    
    for i in range(12 * cycles): # Manduk usually covers all signs? or just Kendras?
        # "Every Dasha is of the next 3rd Rashi". If we cover all 12, we need a specific sequence.
        # 1, 4, 7, 10, 2, 5, 8, 11, 3, 6, 9, 12 is the sequence if jumping 3.
        # This matches Manduk Gati (Frog Jump).
        
        rashi_name = RASHI_SA[curr_rashi]
        
        # Years: Sthir (7/8/9)
        rem = curr_rashi % 3
        if rem == 0: duration = 7
        elif rem == 1: duration = 8
        else: duration = 9
        
        end = cur + timedelta(days=duration * 365.25)
        rows.append({
            "Mahadasa": rashi_name,
            "Rashi_Idx": curr_rashi,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": float(duration)
        })
        cur = end
        
        # Jump 3
        curr_rashi = (curr_rashi + (3 * direction)) % 12
        
    return pd.DataFrame(rows)

# ---------------------------------
# Shula Dasa
# ---------------------------------
# Start: Stronger of 2nd or 8th.
# Order: Odd -> Onward, Even -> Backward.
# Years: Sthir (7/8/9).
# Used for death.

def build_shula_dasa(points, local_start, cycles=1):
    asc = next((p for p in points if "Ascendant" in p.get("Point","")), None)
    asc_idx = asc["Rashi_Idx"] if asc else 0
    
    h2 = (asc_idx + 1) % 12
    h8 = (asc_idx + 7) % 12
    
    start_rashi = get_stronger_sign(h2, h8, points)
    is_odd = (start_rashi % 2 == 0)
    direction = 1 if is_odd else -1
    
    rows = []
    cur = local_start
    
    for i in range(12 * cycles):
        rashi_idx = (start_rashi + (i * direction)) % 12
        rashi_name = RASHI_SA[rashi_idx]
        
        # Sthir years
        rem = rashi_idx % 3
        if rem == 0: duration = 7
        elif rem == 1: duration = 8
        else: duration = 9
        
        end = cur + timedelta(days=duration * 365.25)
        rows.append({
            "Mahadasa": rashi_name,
            "Rashi_Idx": rashi_idx,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": float(duration)
        })
        cur = end
        
    return pd.DataFrame(rows)

# ---------------------------------
# Trikon Dasa
# ---------------------------------
# Start: Strongest amongst Trikonas (1, 5, 9) from Lagna.
# Order: Odd -> Onward, Even -> Reverse.
# Years: Char Dasa years.

def build_trikon_dasa(points, local_start, cycles=1):
    asc = next((p for p in points if "Ascendant" in p.get("Point","")), None)
    asc_idx = asc["Rashi_Idx"] if asc else 0
    
    t1 = asc_idx
    t5 = (asc_idx + 4) % 12
    t9 = (asc_idx + 8) % 12
    
    # Strongest of 3
    s1 = get_sign_strength_score(t1, points)
    s5 = get_sign_strength_score(t5, points)
    s9 = get_sign_strength_score(t9, points)
    
    # Simple max
    if s1 >= s5 and s1 >= s9: start_rashi = t1
    elif s5 >= s1 and s5 >= s9: start_rashi = t5
    else: start_rashi = t9
    
    is_odd = (start_rashi % 2 == 0)
    direction = 1 if is_odd else -1
    
    rows = []
    cur = local_start
    
    for i in range(12 * cycles):
        rashi_idx = (start_rashi + (i * direction)) % 12
        rashi_name = RASHI_SA[rashi_idx]
        
        years = get_char_dasa_span(rashi_idx, points)
        
        end = cur + timedelta(days=years * 365.25)
        rows.append({
            "Mahadasa": rashi_name,
            "Rashi_Idx": rashi_idx,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": float(years)
        })
        cur = end
        
    return pd.DataFrame(rows)

# ---------------------------------
# Dirga Dasa (Drig Dasa)
# ---------------------------------
# Start: 9th House.
# 1. 9th Rashi
# 2. Rashis aspected by 9th.
# 3. 10th Rashi
# 4. Rashis aspected by 10th.
# 5. 11th Rashi
# 6. Rashis aspected by 11th.
# Aspects: Jaimini (Movable <-> Fixed, Dual <-> Dual).
# Order of aspected rashis:
#   Movable aspecting: Count backwards?
#   Fixed aspecting: Count onwards?
#   Dual: Odd->Onward, Even->Backward

def get_jaimini_aspects(rashi_idx):
    """
    Return list of signs aspected by `rashi_idx` (Jaimini).
    Movable (0, 3, 6, 9) aspects Fixed (1, 4, 7, 10) except adjacent.
    Fixed aspects Movable except adjacent.
    Dual (2, 5, 8, 11) aspects other Duals.
    """
    aspects = []
    # Rashi type
    # 0=M, 1=F, 2=D
    rtype = rashi_idx % 3
    
    if rtype == 0: # Movable
        # Aspects Fixed (1, 4, 7, 10)
        # Exclude adjacent: 
        # Aries (0) -> Aspects Leo(4), Sc(7), Aq(10). Excludes Tau(1).
        # Cancer (3) -> Aspects Sc(7), Aq(10), Tau(1). Excludes Leo(4).
        fixed = [1, 4, 7, 10]
        adjacent = (rashi_idx + 1) % 12
        aspects = [x for x in fixed if x != adjacent]
        
    elif rtype == 1: # Fixed
        # Aspects Movable (0, 3, 6, 9)
        # Exclude adjacent:
        # Taurus (1) -> Aspects Cn(3), Li(6), Cp(9). Excludes Ar(0 - previous adjacent).
        movable = [0, 3, 6, 9]
        adjacent = (rashi_idx - 1 + 12) % 12
        aspects = [x for x in movable if x != adjacent]
        
    else: # Dual
        # Aspects other Duals
        duals = [2, 5, 8, 11]
        aspects = [x for x in duals if x != rashi_idx]
        
    return aspects

def build_dirga_dasa(points, local_start, cycles=1):
    asc = next((p for p in points if "Ascendant" in p.get("Point","")), None)
    asc_idx = asc["Rashi_Idx"] if asc else 0
    
    h9 = (asc_idx + 8) % 12
    h10 = (asc_idx + 9) % 12
    h11 = (asc_idx + 10) % 12
    
    basis_signs = [h9, h10, h11]
    
    sequence = []
    
    for base in basis_signs:
        sequence.append(base)
        aspects = get_jaimini_aspects(base)
        
        # Ordering of aspected signs
        # Verse 187: "Movable ... backwards. Fixed ... onwards. Dual ... Odd->Onward, Even->Backward"
        # Wait, phrasing: "Rashi, receiving a Drishti from the Movable Rashi, is counted backwards"
        # So if Base is Movable, its aspected signs are enumerated in reverse order?
        # Or does it mean the logic of finding them?
        # Let's assume enumeration order.
        
        rtype = base % 3
        if rtype == 0: # Base is Movable
            # Counted backwards. Just sort aspects descending? Or counter-clockwise from Base?
            # Standard Drig Dasa usually orders aspected signs by proximity in direction?
            # Let's just sort descending for now to "count backwards" conceptually, or use specialized logic.
            # Usually: If Ar(0) aspects 4, 7, 10. Backwards from Ar(0)? 12, 11...
            # The signs are 4, 7, 10. Reverse of 4,7,10 is 10,7,4.
            aspects.sort(reverse=True)
            
        elif rtype == 1: # Base is Fixed
            # Onwards
            aspects.sort()
            
        else: # Dual
            # Odd -> Onwards, Even -> Backwards
            is_odd = (base % 2 == 0)
            if is_odd:
                aspects.sort()
            else:
                aspects.sort(reverse=True)
                
        sequence.extend(aspects)
        
    rows = []
    cur = local_start
    
    # Only 1 cycle makes sense here as it's a specific sequence of 3 groups x 4 signs = 12 total?
    # Yes, 1 base + 3 aspects = 4. 3 groups = 12 signs.
    
    for rashi_idx in sequence:
        rashi_name = RASHI_SA[rashi_idx]
        
        # Years: "Char Dasha" or "Sthir"? 
        # Verse 175-176 (Kendradi) mentions Char spans.
        # Verse 185-187 (Dirga) doesn't explicitly state years.
        # But commonly Drig Dasa uses Char Dasa years (Count to Lord).
        years = get_char_dasa_span(rashi_idx, points)
        
        end = cur + timedelta(days=years * 365.25)
        rows.append({
            "Mahadasa": rashi_name,
            "Rashi_Idx": rashi_idx,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": float(years)
        })
        cur = end
        
    return pd.DataFrame(rows)

# ---------------------------------
# Panch Swar Dasa
# ---------------------------------
# Name based.
# A, I, U, E, O.
# 12 years each.
# Sub periods: 5 swaras in same order.

def get_name_swara_index(name_str):
    """
    Determine the Swara index (0-4) from the name.
    A=0, I=1, U=2, E=3, O=4.
    Simple mapping from english vowels.
    """
    if not name_str: return 0
    name_norm = name_str.lower().strip()
    
    # Priority check for first vowel
    for char in name_norm:
        if char == 'a': return 0
        if char == 'i': return 1
        if char == 'u': return 2
        if char == 'e': return 3
        if char == 'o': return 4
        
    return 0 # Default to A

def build_panch_swar_dasa(points, local_start, name_str="", cycles=1):
    start_idx = get_name_swara_index(name_str)
    swaras = ["A", "I", "U", "E", "O"]
    num_swaras = 5
    year_per_swara = 12
    
    rows = []
    cur = local_start
    
    for i in range(num_swaras * cycles):
        s_idx = (start_idx + i) % num_swaras
        s_name = swaras[s_idx]
        
        end = cur + timedelta(days=year_per_swara * 365.25)
        rows.append({
            "Mahadasa": f"Swar {s_name}",
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": float(year_per_swara)
        })
        cur = end
        
    return pd.DataFrame(rows)
        
# ---------------------------------
# Kalachakra Dasa
# ---------------------------------

def get_kalachakra_sequences():
    """
    Returns a dictionary mapping (Nakshatra_Idx, Pada) -> [List of Rashi Indices].
    Nakshatras 0-26. Padas 1-4.
    """
    # Rashi Years
    # Ar(0)=7, Ta(1)=16, Ge(2)=9, Cn(3)=21, Le(4)=5, Vi(5)=9, Li(6)=16, Sc(7)=7, Sg(8)=10, Cp(9)=4, Aq(10)=4, Pi(11)=10
    
    # 1. Savya - Ashvini Group
    # Ashvini(0), Punarvasu(6), Hasta(12), Mula(18), P-Bhadra(24)
    # AND Kritika(2), Aslesha(8), Swati(14), U-Shadha(20), Revati(26)
    ashvini_group = [0, 6, 12, 18, 24, 2, 8, 14, 20, 26]
    
    # Savya - Bharani Group
    # Bharani(1), Pushya(7), Chitra(13), P-Shadha(19), U-Bhadra(25)
    bharani_group = [1, 7, 13, 19, 25]
    
    # Apsavya - Rohini Group
    # Rohini(3), Magha(9), Vishakha(15), Shravan(21)
    rohini_group = [3, 9, 15, 21]
    
    # Apsavya - Mrigashira Group
    # Mrigashira(4), Ardra(5), P-Phalguni(10), U-Phalguni(11), Anuradha(16), Jyeshtha(17), Dhanishtha(22), Shatabhisha(23)
    mrigashira_group = [4, 5, 10, 11, 16, 17, 22, 23]
    
    seq_map = {}
    
    # Ashvini Group Sequences (Savya)
    # Pad 1: Mesh, Vrishabh, Mithun, Kark, Simh, Kanya, Tula, Vrischik, Dhanu
    a1 = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    # Pad 2: Makar, Kumbh, Meen, Mesh, Vrishabh, Mithun, Kark, Simh, Kanya
    a2 = [9, 10, 11, 0, 1, 2, 3, 4, 5]
    # Pad 3: Vrishabh, Mesh, Meen, Kumbh, Makar, Dhanu, Mesh, Vrishabh, Mithun
    a3 = [1, 0, 11, 10, 9, 8, 0, 1, 2]
    # Pad 4: Kark, Simh, Kanya, Tula, Vrischik, Dhanu, Makar, Kumbh, Meen
    a4 = [3, 4, 5, 6, 7, 8, 9, 10, 11]
    
    for nk in ashvini_group:
        seq_map[(nk, 1)] = a1
        seq_map[(nk, 2)] = a2
        seq_map[(nk, 3)] = a3
        seq_map[(nk, 4)] = a4
        
    # Bharani Group Sequences (Savya)
    # Pad 1: Vrischik, Tula, Kanya, Kark, Simh, Mithun, Vrishabh, Mesh, Meen
    b1 = [7, 6, 5, 3, 4, 2, 1, 0, 11]
    # Pad 2: Kumbh, Makar, Dhanu, Mesh, Vrishabh, Mithun, Kark, Simh, Kanya
    b2 = [10, 9, 8, 0, 1, 2, 3, 4, 5]
    # Pad 3: Tula, Vrischik, Dhanu, Makar, Kumbh, Meen, Vrischik, Tula, Kanya
    b3 = [6, 7, 8, 9, 10, 11, 7, 6, 5]
    # Pad 4: Kark, Simh, Mithun, Vrishabh, Mesh, Meen, Kumbh, Makar, Dhanu
    # Note: Text "Kark, Simh, Mithun...". Sim(4) to Mith(2) is 'Manduki'? or just jump? It says Kanya to Kark, Simh to Mithun is Manduki.
    # Text at 99: "Movement from Simh to Mithun is Manduki".
    # Here: Kark(3) -> Simh(4) -> Mithun(2) -> Vrish(1) -> Mesh(0) -> Meen(11) -> Kumbh(10) -> Makar(9) -> Dhanu(8).
    b4 = [3, 4, 2, 1, 0, 11, 10, 9, 8]
    
    for nk in bharani_group:
        seq_map[(nk, 1)] = b1
        seq_map[(nk, 2)] = b2
        seq_map[(nk, 3)] = b3
        seq_map[(nk, 4)] = b4
        
    # Rohini Group Sequences (Apsavya - Count Jiva to Deha)
    # Pad 1: Dhanu, Makar, Kumbh, Meen, Mesh, Vrishabh, Mithun, Simh, Tula
    r1 = [8, 9, 10, 11, 0, 1, 2, 4, 6] # Note: Mithun(2) -> Simh(4) -> Tula(6)
    # Pad 2: Kanya, Tula, Vrischik, Meen, Kumbh, Makar, Dhanu, Vrischik, Vrischik (Text: Vrischik and Vrischik)
    # Wait, usually 9 items. Kanya, Tula, Vris, Meen, Kumb, Makar, Dhanu, Vris, Vris?
    # Maybe Typo? "Dhanu, Vrischik and Vrischik". Or Dhanu, Vrischik-Deha?
    # If we assume 9 items and last is Deha=Tula? No, Pad 2 Deha is Tula.
    # Text: "Lords... Kanya, Tula, Vrischik, Meen, Kumbh, Makar, Dhanu, Vrischik and Vrischik".
    # That is 9 items. Last two are Vrischik?
    # Another version (common): Kanya, Tula, Vrischik, Meen, Kumbh, Makar, Dhanu, Vrischik, Tula.
    # Let's check Tula Deha. Jiva Kanya. Jiva->Deha. Start Kanya. End Tula.
    # So last should be Tula (6).
    r2 = [5, 6, 7, 11, 10, 9, 8, 7, 6] 
    # Pad 3: Kanya, Simh, Kark, Mithun, Vrishabh, Mesh, Dhanu, Makar, Kumbh
    r3 = [5, 4, 3, 2, 1, 0, 8, 9, 10]
    # Pad 4: Meen, Mesh, Vrishabh, Mithun, Simh, Kark, Kanya, Tula, Vrischik
    r4 = [11, 0, 1, 2, 4, 3, 5, 6, 7]
    
    for nk in rohini_group:
        seq_map[(nk, 1)] = r1
        seq_map[(nk, 2)] = r2
        seq_map[(nk, 3)] = r3
        seq_map[(nk, 4)] = r4
        
    # Mrigashira Group Sequences (Apsavya)
    # Pad 1: Meen, Kumbh, Makar, Dhanu, Vrischik, Tula, Kanya, Simh, Kark
    m1 = [11, 10, 9, 8, 7, 6, 5, 4, 3]
    # Pad 2: Mithun, Vrishabh, Mesh, Dhanu, Makar, Kumbh, Meen, Mesh, Vrishabh
    m2 = [2, 1, 0, 8, 9, 10, 11, 0, 1]
    # Pad 3: Mithun, Simh, Kark, Kanya, Tula, Vrischik, Meen, Kumbh, Makar
    m3 = [2, 4, 3, 5, 6, 7, 11, 10, 9]
    # Pad 4: Dhanu, Vrischik, Tula, Kanya, Simh, Kark, Mithun, Vrishabh, Mesh
    m4 = [8, 7, 6, 5, 4, 3, 2, 1, 0]
    
    for nk in mrigashira_group:
        seq_map[(nk, 1)] = m1
        seq_map[(nk, 2)] = m2
        seq_map[(nk, 3)] = m3
        seq_map[(nk, 4)] = m4
        
    return seq_map

def build_kalachakra_dasa(points, local_start, cycles=1):
    """
    Kalachakra Dasa implementation.
    Calculation:
    1. Find Moon's Nakshatra and Pada.
    2. Determine Balance of Dasha at birth.
       - Unlike Vimshottari, Balance is calculated on the TOTAL years of the sequence?
       - Verse 91: "Multiply past Ghatikas... of the Pad... by existing Dasha years and divide by 15... deduct from total... balance."
       - Verse 93: "Past Kalas ... multiplied by years allotted to Dasha and divided by 200." (200 kalas = 1 Pada).
       - This implies the "Dasha" here is the *Full Cycle* of the Pada (e.g. 100, 85, etc)? Or the specific first sub-period?
       - Example in Verse 95: "Full Dasha years are 100... expired portion... 90 years 9 months... deducting total years from Dhanu to Mithun (77)... balance of Vrishabh is 13y 9m... deducting from 16... balance 2y 3m."
       - This confirms: We calculate expired years based on the WHOLE CYCLE (sum of all 9 rashis).
       - Then we traverse the sequence, subtracting elapsed years until we find the current running Rashi and its balance.
    """
    moon_entry = next((p for p in points if p["Point"] == "Moon"), None)
    if not moon_entry: return pd.DataFrame(), 0.0, 0.0
    
    moon_lon = moon_entry.get("Longitude (Dec)", 0)
    
    # Nakshatra info
    nak_span = 13 + (20/60.0) # 13.3333
    nak_idx = int(moon_lon / nak_span)
    nak_rem = moon_lon % nak_span
    
    # Pada (Quarter)
    pada_span = nak_span / 4.0 # 3.3333 deg = 200 arcmins
    pada_idx = int(nak_rem / pada_span) # 0, 1, 2, 3
    pada_num = pada_idx + 1
    
    # Fraction passed in Pada
    passed_in_pada = nak_rem % pada_span
    passed_fraction = passed_in_pada / pada_span
    
    # Get sequence
    seq_map = get_kalachakra_sequences()
    sequence = seq_map.get((nak_idx, pada_num), [])
    
    if not sequence:
        return pd.DataFrame(), 0.0, 0.0 # Should not happen if map coverage is complete
        
    # Rashi Years Map
    rashi_years = {
        0: 7, 1: 16, 2: 9, 3: 21, 4: 5, 5: 9, 6: 16, 7: 7, 8: 10, 9: 4, 10: 4, 11: 10
    }
    
    # Total Cycle Years
    total_years = sum(rashi_years[r] for r in sequence)
    
    # Expired Years
    # Savya: Based on *Elapsed* portion? 
    # Apsavya: Based on *Remaining* portion?
    # Text 94: "In Savya... calculations based on Deha (Start)... In Apsavya... on Jiva (End? No, Jiva is start for Apsavya sequence)."
    # The example for Apsavya (Mrigashira 4) used "Past Kalas" (Elapsed) to find Expired Dasa.
    # And Savya example (Kritika) also used "Past Kalas".
    # So for both, we use Elapsed Time in Pada to find Expired Time in Dasha.
    
    expired_years = passed_fraction * total_years
    
    # Find current running rashi
    # We subtract rashi years from expired_years until we hit the current one.
    
    remaining_in_cycle = total_years - expired_years
    # But strictly we need to pinpoint start in timeline.
    
    running_rashi_idx = 0
    balance_in_rashi = 0
    years_accum = 0
    
    for i, ridx in enumerate(sequence):
        dur = rashi_years[ridx]
        if expired_years < dur:
            running_rashi_idx = i
            balance_in_rashi = dur - expired_years
            break
        expired_years -= dur
        
    # Generate Rows
    rows = []
    cur = local_start
    
    # First (current) item
    first_r_idx = sequence[running_rashi_idx]
    first_dur = balance_in_rashi
    first_end = cur + timedelta(days=first_dur * 365.25)
    
    rows.append({
        "Mahadasa": RASHI_SA[first_r_idx],
        "Rashi_Idx": first_r_idx,
        "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
        "End (local)": first_end.strftime("%Y-%m-%d %H:%M:%S"),
        "Duration (years)": float(first_dur) # Balance
    })
    cur = first_end
    
    # Subsequent items
    # We continue the sequence from running_rashi_idx + 1
    # If cycles > 1, we loop the sequence.
    
    steps_needed = 9 * cycles # roughly 1 full cycle
    current_seq_idx = running_rashi_idx + 1
    
    for _ in range(steps_needed):
        seq_i = current_seq_idx % len(sequence)
        r_idx = sequence[seq_i]
        dur = rashi_years[r_idx]
        
        end = cur + timedelta(days=dur * 365.25)
        rows.append({
            "Mahadasa": RASHI_SA[r_idx],
            "Rashi_Idx": r_idx,
            "Start (local)": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End (local)": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (years)": float(dur)
        })
        cur = end
        current_seq_idx += 1
        
    df = pd.DataFrame(rows)
    remaining_ayu = max(0.0, total_years - expired_years)
    return df, float(total_years), float(remaining_ayu)

