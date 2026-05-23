# src/ci_core/vargas.py
from src.jyotisha.base.utils import norm360, lon_to_sign_idx
from src.jyotisha.base.constants import (
    RASHI_SA, HORA_NAMES, DREKKANA_NAMES, CHATURTHAMSA_NAMES, NAVAMSA_NAMES,
    SAPTAMSA_NAMES, DASAMSA_NAMES, DVADASAMSA_NAMES, SHODASAMSA_NAMES,
    VIMSAMSA_NAMES, SIDDHAMSA_NAMES, SAPTAVIMSAMSA_NAMES, TRIMSAMSA_NAMES_ODD, 
    TRIMSAMSA_NAMES_EVEN, KHAVEDAMSA_NAMES, AKSHAVEDAMSA_NAMES, 
    SHASHTIAMSA_NAMES, SHASHTIAMSA_BENEFIC, NAK_NAMES
)

# ---------------------------------
# Divisional Chart (Varga) Calculations
# ---------------------------------
def navamsa_for(lon):
    lon = norm360(lon); si = lon_to_sign_idx(lon); intra = lon - 30*si
    pada = int(intra // (30/9)) + 1
    movable = {0,3,6,9}; fixed = {1,4,7,10}; dual = {2,5,8,11}
    if si in movable: start = si
    elif si in fixed: start = (si + 8) % 12
    else:             start = (si + 4) % 12
    nsign = (start + (pada - 1)) % 12
    return nsign, pada

def drekkana_for(lon):
    """D-3: Drekkana - each sign divided into 3 parts of 10°"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    drek = int(intra // 10)  # 0, 1, or 2
    if drek == 0:
        return si
    elif drek == 1:
        return (si + 4) % 12
    else:
        return (si + 8) % 12

def chaturthamsa_for(lon):
    """D-4: Chaturthamsa - each sign divided into 4 parts of 7.5°"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 7.5)  # 0-3
    return (si + part * 3) % 12

def saptamsa_for(lon):
    """D-7: Saptamsa - each sign divided into 7 parts"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // (30/7))
    odd = (si % 2 == 0)
    if odd:
        return (si + part) % 12
    else:
        return (si + 6 + part) % 12

def dasamsa_for(lon):
    """D-10: Dasamsa - each sign divided into 10 parts of 3°"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 3)  # 0-9
    odd = (si % 2 == 0)
    if odd:
        return (si + part) % 12
    else:
        return (si + 8 + part) % 12

def dwadasamsa_for(lon):
    """D-12: Dwadasamsa - each sign divided into 12 parts of 2.5°"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 2.5)  # 0-11
    return (si + part) % 12

def shodasamsa_for(lon):
    """D-16: Shodasamsa - each sign divided into 16 parts"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // (30/16))
    movable = {0, 3, 6, 9}
    fixed = {1, 4, 7, 10}
    if si in movable:
        return (0 + part) % 12
    elif si in fixed:
        return (4 + part) % 12
    else:
        return (8 + part) % 12

def vimsamsa_for(lon):
    """D-20: Vimsamsa - each sign divided into 20 parts"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 1.5)
    movable = {0, 3, 6, 9}
    fixed = {1, 4, 7, 10}
    if si in movable:
        return (0 + part) % 12
    elif si in fixed:
        return (8 + part) % 12
    else:
        return (4 + part) % 12

def chaturvimsamsa_for(lon):
    """D-24: Chaturvimsamsa/Siddhamsa - each sign divided into 24 parts"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 1.25)
    odd = (si % 2 == 0)
    if odd:
        return (4 + part) % 12
    else:
        return (3 + part) % 12

def trimsamsa_for(lon):
    """D-30: Trimsamsa"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    odd = (si % 2 == 0)
    
    if odd:
        if intra < 5: return 0
        elif intra < 10: return 10
        elif intra < 18: return 8
        elif intra < 25: return 2
        else: return 1
    else:
        if intra < 5: return 1
        elif intra < 12: return 5
        elif intra < 20: return 11
        elif intra < 25: return 9
        else: return 7

def khavedamsa_for(lon):
    """D-40: Khavedamsa"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 0.75)
    odd = (si % 2 == 0)
    if odd:
        return (0 + part) % 12
    else:
        return (6 + part) % 12

def akshavedamsa_for(lon):
    """D-45: Akshavedamsa"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // (30/45))
    movable = {0, 3, 6, 9}
    fixed = {1, 4, 7, 10}
    if si in movable:
        return (0 + part) % 12
    elif si in fixed:
        return (4 + part) % 12
    else:
        return (8 + part) % 12

def shashtiamsa_for(lon):
    """D-60: Shashtiamsa"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    result = int((intra * 2) % 12)
    return result

def saptavimsamsa_for(lon):
    """D-27: Saptavimsamsa"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // (30/27))
    fire = {0, 4, 8}
    earth = {1, 5, 9}
    air = {2, 6, 10}
    if si in fire: start = 0
    elif si in earth: start = 3
    elif si in air: start = 6
    else: start = 9
    return (start + part) % 12

def get_all_vargas(lon):
    return {
        'D1': lon_to_sign_idx(lon),
        'D2': 4 if (lon_to_sign_idx(lon) % 2 == 0 and (lon % 30) < 15) or (lon_to_sign_idx(lon) % 2 == 1 and (lon % 30) >= 15) else 3,
        'D3': drekkana_for(lon),
        'D4': chaturthamsa_for(lon),
        'D7': saptamsa_for(lon),
        'D9': navamsa_for(lon)[0],
        'D10': dasamsa_for(lon),
        'D12': dwadasamsa_for(lon),
        'D16': shodasamsa_for(lon),
        'D20': vimsamsa_for(lon),
        'D24': chaturvimsamsa_for(lon),
        'D27': saptavimsamsa_for(lon),
        'D30': trimsamsa_for(lon),
        'D40': khavedamsa_for(lon),
        'D45': akshavedamsa_for(lon),
        'D60': shashtiamsa_for(lon),
    }

def get_varga_names(lon):
    """Get the classical names for each Varga (divisional chart) position."""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30 * si
    odd = (si % 2 == 0)

    d1_name = RASHI_SA[si]

    if odd: hora_idx = 0 if intra < 15 else 1
    else: hora_idx = 1 if intra < 15 else 0
    d2_name = HORA_NAMES[hora_idx]

    drek = int(intra // 10)
    d3_name = DREKKANA_NAMES[drek]

    part = int(intra // 7.5)
    d4_name = CHATURTHAMSA_NAMES[part] if part < 4 else CHATURTHAMSA_NAMES[3]

    part = int(intra // (30/7))
    d7_name = SAPTAMSA_NAMES[part] if part < 7 else SAPTAMSA_NAMES[6]

    movable = {0, 3, 6, 9}
    fixed = {1, 4, 7, 10}
    if si in movable: d9_name = NAVAMSA_NAMES[0]
    elif si in fixed: d9_name = NAVAMSA_NAMES[1]
    else: d9_name = NAVAMSA_NAMES[2]

    part = int(intra // 3)
    d10_name = DASAMSA_NAMES[part] if part < 10 else DASAMSA_NAMES[9]

    part = int(intra // 2.5)
    d12_name = DVADASAMSA_NAMES[part] if part < 12 else DVADASAMSA_NAMES[11]

    part = int(intra // (30/16))
    d16_name = SHODASAMSA_NAMES[part] if part < 16 else SHODASAMSA_NAMES[15]

    part = int(intra // 1.5)
    d20_name = VIMSAMSA_NAMES[part] if part < 20 else VIMSAMSA_NAMES[19]

    part = int(intra // 1.25)
    d24_name = SIDDHAMSA_NAMES[part] if part < 24 else SIDDHAMSA_NAMES[23]

    nak_span = 360.0 / 27.0
    nak_idx = int(lon // nak_span)
    d27_name = SAPTAVIMSAMSA_NAMES[nak_idx]

    if odd:
        if intra < 5: d30_name = TRIMSAMSA_NAMES_ODD[0]
        elif intra < 10: d30_name = TRIMSAMSA_NAMES_ODD[1]
        elif intra < 18: d30_name = TRIMSAMSA_NAMES_ODD[2]
        elif intra < 25: d30_name = TRIMSAMSA_NAMES_ODD[3]
        else: d30_name = TRIMSAMSA_NAMES_ODD[4]
    else:
        if intra < 5: d30_name = TRIMSAMSA_NAMES_EVEN[0]
        elif intra < 12: d30_name = TRIMSAMSA_NAMES_EVEN[1]
        elif intra < 20: d30_name = TRIMSAMSA_NAMES_EVEN[2]
        elif intra < 25: d30_name = TRIMSAMSA_NAMES_EVEN[3]
        else: d30_name = TRIMSAMSA_NAMES_EVEN[4]

    part = int(intra // 0.75)
    d40_name = KHAVEDAMSA_NAMES[part] if part < 40 else KHAVEDAMSA_NAMES[39]

    part = int(intra // (30/45))
    d45_name = AKSHAVEDAMSA_NAMES[part] if part < 45 else AKSHAVEDAMSA_NAMES[44]

    part = int(intra * 2)
    d60_name = SHASHTIAMSA_NAMES[part] if part < 60 else SHASHTIAMSA_NAMES[59]
    d60_benefic = (part + 1) in SHASHTIAMSA_BENEFIC

    return {
        'D1': d1_name, 'D2': d2_name, 'D3': d3_name, 'D4': d4_name, 'D7': d7_name,
        'D9': d9_name, 'D10': d10_name, 'D12': d12_name, 'D16': d16_name,
        'D20': d20_name, 'D24': d24_name, 'D27': d27_name, 'D30': d30_name,
        'D40': d40_name, 'D45': d45_name, 'D60': d60_name, 'D60_benefic': d60_benefic
    }

def get_nakshatra_details(lon):
    """Get nakshatra name, pada (1-4), and percentage left in nakshatra"""
    lon = norm360(lon)
    nak_span = 360.0 / 27.0
    pada_span = nak_span / 4.0

    nak_idx = int(lon // nak_span)
    intra_nak = lon - nak_idx * nak_span
    pada = int(intra_nak // pada_span) + 1

    pct_left = ((nak_span - intra_nak) / nak_span) * 100

    return {
        'nakshatra': NAK_NAMES[nak_idx],
        'pada': pada,
        'pct_left': round(pct_left, 2)
    }
