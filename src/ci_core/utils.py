# src/ci_core/utils.py
from .constants import RASHI_SA

def norm360(val):
    v = val % 360.0
    if v < 0: v += 360.0
    return v

def lon_to_sign_idx(lon):
    return int(norm360(lon) // 30)

def get_rashi_idx(lon):
    return lon_to_sign_idx(lon)

def get_nakshatra_idx(lon):
    return int(norm360(lon) // (360.0 / 27.0))

def get_pada(lon):
    nak_len = 360.0 / 27.0
    intra_nak = norm360(lon) % nak_len
    pada_len = nak_len / 4.0
    return int(intra_nak // pada_len) + 1

def dms_tuple(x):
    x = float(abs(x))
    d = int(x)
    m_float = (x - d) * 60.0
    m = int(m_float)
    s = round((m_float - m) * 60.0)
    if s == 60: s = 0; m += 1
    if m == 60: m = 0; d += 1
    return d, m, s

def dms_str(val):
    d, m, s = dms_tuple(val)
    return f"{d}°{m:02d}'{s:02d}\""

def sign_dms_str(lon):
    val = norm360(lon)
    sign = int(val // 30)
    rem = val - (sign * 30)
    d, m, s = dms_tuple(rem)
    return f"{RASHI_SA[sign]} {d}°{m:02d}'{s:02d}\""

def rashi_name(lon):
    return RASHI_SA[lon_to_sign_idx(lon)]

def ordinal(n):
    return f"{n}{'tsnrhtdd'[(n//10%10!=1)*(n%10<4)*n%10::4]}"

def aspect_strength_pct(angle_deg: float, planet: str | None = None) -> float:
    """
    Piecewise-linear aspect strength in percentage based on anchor angles.
    """
    ang = norm360(angle_deg)
    base = {
        0.0: 0.0, 30.0: 0.0, 60.0: 25.0, 90.0: 75.0, 120.0: 50.0,
        150.0: 0.0, 180.0: 100.0, 210.0: 75.0, 240.0: 50.0, 270.0: 25.0,
        300.0: 0.0, 330.0: 0.0, 360.0: 0.0,
    }
    planet_full = {
        "Mars": [90.0, 270.0],
        "Jupiter": [120.0, 240.0],
        "Saturn": [60.0, 300.0],
    }
    anchors = base.copy()
    if planet:
        for p, angles in planet_full.items():
            if planet == p:
                for a in angles:
                    anchors[a] = 100.0
    
    pts = sorted(anchors.items())
    for (a1, v1), (a2, v2) in zip(pts, pts[1:]):
        if a1 <= ang <= a2:
            if a2 == a1: return v1
            t = (ang - a1) / (a2 - a1)
            return v1 + t * (v2 - v1)
    return 0.0

def sign_distance(start, end, step):
    if step == 0: return 0
    count = 0
    curr = start
    while curr != end:
        curr = (curr + step) % 12
        count += 1
    return count if count > 0 else 12
