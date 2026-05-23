# src/ci_core/ashtakavarga.py

ASHTAKAVARGA_RULES = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Ascendant": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Ascendant": [3, 6, 10, 11],
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Ascendant": [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Ascendant": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Ascendant": [1, 3, 4, 6, 10, 11],
    },
    "Ascendant": {
        "Sun": [3, 4, 6, 10, 11, 12],
        "Moon": [3, 6, 10, 11, 12],
        "Mars": [1, 3, 6, 10, 11],
        "Mercury": [1, 2, 4, 6, 8, 10, 11],
        "Jupiter": [1, 2, 4, 5, 6, 7, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9],
        "Saturn": [1, 3, 4, 6, 10, 11],
        "Ascendant": [3, 6, 10, 11],
    },
}


def compute_ashtakavarga(points_df):
    """
    Compute Bhinnashtakavarga (individual planet contributions) and Sarvashtakavarga (totals).
    
    Returns dict with:
    - bav: {planet: [12 bindu values for each sign 0-11]}
    - sav: [12 total bindu values for each sign 0-11]
    """
    # Get sign indices for all relevant bodies
    sign_positions = {}
    
    for _, row in points_df.iterrows():
        point = row['Point']
        sign_idx = row['Rashi_Idx']
        
        # Map point names to our standard names
        if point == "Ascendant (1st House Cusp)":
            sign_positions["Ascendant"] = sign_idx
        elif point in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            sign_positions[point] = sign_idx
    
    # Initialize Bhinnashtakavarga for each planet
    bav = {planet: [0] * 12 for planet in ASHTAKAVARGA_RULES.keys()}
    
    # Calculate bindus for each planet
    for planet, rules in ASHTAKAVARGA_RULES.items():
        for ref_body, houses in rules.items():
            if ref_body not in sign_positions:
                continue
            ref_sign = sign_positions[ref_body]
            
            for house in houses:
                # House 1 = same sign as reference, house 2 = next sign, etc.
                target_sign = (ref_sign + house - 1) % 12
                bav[planet][target_sign] += 1
    
    # Calculate Sarvashtakavarga (sum of all BAVs)
    sav = [0] * 12
    for sign_idx in range(12):
        for planet in bav:
            sav[sign_idx] += bav[planet][sign_idx]
    
    return {
        "bav": bav,
        "sav": sav,
        "sign_positions": sign_positions
    }


def calculate_ashtakavarga_longevity(bav):
    """
    Calculate longevity based on Ashtakavarga rekhas.
    Mapping:
    0 rekhas = 2 days
    1 rekha  = 1.5 days
    2 rekhas = 1 day
    3 rekhas = 0.5 days
    4 rekhas = 7.5 days
    5 rekhas = 2 years
    6 rekhas = 4 years
    7 rekhas = 6 years
    8 rekhas = 8 years
    
    Longevity = (Sum of all spans) / 2
    """
    # Duration in days (using 365.25 for years)
    mapping = {
        0: 2.0,
        1: 1.5,
        2: 1.0,
        3: 0.5,
        4: 7.5,
        5: 2.0 * 365.25,
        6: 4.0 * 365.25,
        7: 6.0 * 365.25,
        8: 8.0 * 365.25
    }
    
    total_days = 0.0
    
    # Iterate through all Ashtakavargas (Lagna + 7 Grahas)
    # The bav dict contains keys for all planets in ASHTAKAVARGA_RULES
    for planet, rekhas in bav.items():
        for r_points in rekhas:
            # Ensure points are within 0-8 just in case, though they should be
            points = max(0, min(8, int(r_points)))
            if points in mapping:
                total_days += mapping[points]
            
    # "Half of the sum total of all will be the longevity"
    final_years = (total_days / 365.25) / 2.0
    
    return round(final_years, 2)
