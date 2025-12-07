# src/ci_core/astrocartography.py
import math
import swisseph as swe
from .constants import PLANETS, RASHI_SA
from .utils import norm360, lon_to_sign_idx

# Rāśi symbols for display
RASHI_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# Sanskrit rāśi names (IAST transliteration)
RASHI_NAMES_IAST = [
    "Meṣa", "Vṛṣabha", "Mithuna", "Karka", "Siṃha", "Kanyā",
    "Tulā", "Vṛścika", "Dhanu", "Makara", "Kumbha", "Mīna"
]

def split_line_at_antimeridian(coords, threshold=180):
    """Split line into segments when longitude jumps > threshold degrees."""
    if not coords or len(coords) < 2:
        return [coords] if coords else []
    
    segments = []
    current_segment = [coords[0]]
    
    for i in range(1, len(coords)):
        prev_lon = coords[i-1]["lon"]
        curr_lon = coords[i]["lon"]
        
        # Detect antimeridian crossing (jump > 180°)
        if abs(curr_lon - prev_lon) > threshold:
            # Save current segment and start new one
            if current_segment:
                segments.append(current_segment)
            current_segment = []
        
        current_segment.append(coords[i])
    
    if current_segment:
        segments.append(current_segment)
    
    return segments

def _find_longitude_for_ascendant(jd_ut, lat, target_asc_sid, ayan):
    """
    Find the geographical longitude where a specific sidereal longitude 
    becomes the Ascendant at a given latitude and time.
    """
    target_asc_trop = norm360(target_asc_sid + ayan)
    
    def get_asc_for_longitude(geo_lon):
        try:
            cusps_trop, ascmc_trop = swe.houses(jd_ut, float(lat), float(geo_lon), b'O')
            return ascmc_trop[0]
        except Exception:
            return None
    
    # Coarse search
    best_lon = None
    best_diff = 360.0
    
    for lon_int in range(-180, 181, 5):
        lon = float(lon_int)
        asc = get_asc_for_longitude(lon)
        if asc is None: continue
        diff = abs(norm360(asc - target_asc_trop))
        if diff > 180: diff = 360 - diff
        if diff < best_diff:
            best_diff = diff
            best_lon = lon
    
    if best_lon is None: return None
    
    # Refinement
    low = best_lon - 5
    high = best_lon + 5
    for _ in range(20):
        mid = (low + high) / 2
        asc_mid = get_asc_for_longitude(mid)
        if asc_mid is None: break
        
        diff_mid = norm360(asc_mid - target_asc_trop)
        if diff_mid > 180: diff_mid -= 360
        
        # We need to determine slope direction. Ascendant increases as longitude increases.
        # If asc_mid < target (diff negative), we need more longitude -> go right
        # However, due to 360 wrapping, simple logic is tricky.
        # Instead, assume monotonicity in small range.
        if diff_mid < 0:
            low = mid
        else:
            high = mid
            
    return (low + high) / 2

def compute_rashi_lines(jd_ut, ayanamsa_code, ephe_path="ephe", use_moseph=False, lat_step=2.0):
    if not use_moseph: swe.set_ephe_path(ephe_path)
    if ayanamsa_code is not None: swe.set_sid_mode(ayanamsa_code)
    
    ayan = swe.get_ayanamsa_ut(jd_ut) if ayanamsa_code is not None else 0.0
    ephflag = swe.FLG_MOSEPH if use_moseph else swe.FLG_SWIEPH
    flags = ephflag | swe.FLG_SPEED
    if ayanamsa_code is not None: flags |= swe.FLG_SIDEREAL
    
    planets = []
    
    for nm, code in PLANETS.items():
        vals = swe.calc_ut(jd_ut, code, flags)[0]
        lonv = norm360(vals[0])
        rashi_idx = lon_to_sign_idx(lonv)
        
        planet_asc_line = []
        for lat in range(-66, 67, int(lat_step)):
            lon = _find_longitude_for_ascendant(jd_ut, lat, lonv, ayan)
            if lon is not None:
                planet_asc_line.append({"lat": lat, "lon": round(lon, 2)})
        
        segments = split_line_at_antimeridian(planet_asc_line)
        planets.append({
            "name": nm, "longitude": round(lonv, 4),
            "rashi_idx": rashi_idx, "rashi_name": RASHI_SA[rashi_idx],
            "rashi_symbol": RASHI_SYMBOLS[rashi_idx], "retro": vals[3] < 0,
            "line": segments[0] if segments else [], "line_segments": segments
        })
    
    try: vals_true = swe.calc_ut(jd_ut, swe.TRUE_NODE, flags)[0]
    except Exception: vals_true = swe.nod_aps_ut(jd_ut, swe.MOON, flags, swe.NODBIT_OSCU)[0]
    rahu = norm360(vals_true[0]); ketu = norm360(rahu + 180)
    
    for nm, lonv in [("Rahu", rahu), ("Ketu", ketu)]:
        rashi_idx = lon_to_sign_idx(lonv)
        planet_asc_line = []
        for lat in range(-66, 67, int(lat_step)):
            lon = _find_longitude_for_ascendant(jd_ut, lat, lonv, ayan)
            if lon is not None: planet_asc_line.append({"lat": lat, "lon": round(lon, 2)})
        segments = split_line_at_antimeridian(planet_asc_line)
        planets.append({
            "name": nm, "longitude": round(lonv, 4),
            "rashi_idx": rashi_idx, "rashi_name": RASHI_SA[rashi_idx],
            "rashi_symbol": RASHI_SYMBOLS[rashi_idx], "retro": True,
            "line": segments[0] if segments else [], "line_segments": segments
        })
        
    rashi_lines = []
    for rashi_idx in range(12):
        cusp_longitude = rashi_idx * 30.0
        line_coords = []
        for lat in range(-66, 67, int(lat_step)):
            lon = _find_longitude_for_ascendant(jd_ut, lat, cusp_longitude, ayan)
            if lon is not None: line_coords.append({"lat": lat, "lon": round(lon, 2)})
        segments = split_line_at_antimeridian(line_coords)
        rashi_lines.append({
            "rashi_idx": rashi_idx, "rashi_name": RASHI_SA[rashi_idx],
            "rashi_symbol": RASHI_SYMBOLS[rashi_idx],
            "line": segments[0] if segments else [], "line_segments": segments
        })
        
    return {"rashi_lines": rashi_lines, "planets": planets}

def compute_lagna_grid(jd_ut, ayanamsa_code, ephe_path="ephe", use_moseph=False,
                       lat_step=5.0, lon_step=10.0):
    if not use_moseph: swe.set_ephe_path(ephe_path)
    if ayanamsa_code is not None: swe.set_sid_mode(ayanamsa_code)
    ayan = swe.get_ayanamsa_ut(jd_ut) if ayanamsa_code is not None else 0.0
    
    grid = []
    for lat in range(-85, 86, int(lat_step)):
        for lon in range(-180, 180, int(lon_step)):
            try:
                cusps_trop, ascmc_trop = swe.houses(jd_ut, float(lat), float(lon), b'O')
                asc_sid = norm360(ascmc_trop[0] - ayan)
                lagna_idx = lon_to_sign_idx(asc_sid)
                grid.append({
                    "lat": lat, "lon": lon,
                    "lagna_idx": lagna_idx, "lagna_name": RASHI_SA[lagna_idx],
                    "lagna_name_iast": RASHI_NAMES_IAST[lagna_idx], "lagna_symbol": RASHI_SYMBOLS[lagna_idx]
                })
            except Exception: pass
            
    # Compute planets for grid (simplified return, full planets returned by compute_rashi_lines)
    # Actually, the original function returned grid AND planets. I should keep that.
    ephflag = swe.FLG_MOSEPH if use_moseph else swe.FLG_SWIEPH
    flags = ephflag | swe.FLG_SPEED
    if ayanamsa_code is not None: flags |= swe.FLG_SIDEREAL
    
    planets = []
    for nm, code in PLANETS.items():
        vals = swe.calc_ut(jd_ut, code, flags)[0]
        lonv = norm360(vals[0])
        rashi_idx = lon_to_sign_idx(lonv)
        planets.append({
            "name": nm, "longitude": round(lonv, 4),
            "rashi_idx": rashi_idx, "rashi_name": RASHI_SA[rashi_idx],
            "rashi_name_iast": RASHI_NAMES_IAST[rashi_idx], "rashi_symbol": RASHI_SYMBOLS[rashi_idx],
            "retro": vals[3] < 0
        })
    try: vals_true = swe.calc_ut(jd_ut, swe.TRUE_NODE, flags)[0]
    except Exception: vals_true = swe.nod_aps_ut(jd_ut, swe.MOON, flags, swe.NODBIT_OSCU)[0]
    rahu = norm360(vals_true[0]); ketu = norm360(rahu + 180)
    for nm, lonv in [("Rahu", rahu), ("Ketu", ketu)]:
        rashi_idx = lon_to_sign_idx(lonv)
        planets.append({
            "name": nm, "longitude": round(lonv, 4),
            "rashi_idx": rashi_idx, "rashi_name": RASHI_SA[rashi_idx],
            "rashi_name_iast": RASHI_NAMES_IAST[rashi_idx], "rashi_symbol": RASHI_SYMBOLS[rashi_idx],
            "retro": True
        })
            
    return {"grid": grid, "planets": planets, "ayanamsa_value": round(ayan, 6)}

def compute_lagna_for_location(jd_ut, lat, lon, ayanamsa_code, ephe_path="ephe", use_moseph=False):
    if not use_moseph: swe.set_ephe_path(ephe_path)
    if ayanamsa_code is not None: swe.set_sid_mode(ayanamsa_code)
    ayan = swe.get_ayanamsa_ut(jd_ut) if ayanamsa_code is not None else 0.0
    try:
        cusps_trop, ascmc_trop = swe.houses(jd_ut, float(lat), float(lon), b'O')
        asc_sid = norm360(ascmc_trop[0] - ayan)
        lagna_idx = lon_to_sign_idx(asc_sid)
        return {
            "lagna_idx": lagna_idx, "lagna_name": RASHI_SA[lagna_idx],
            "lagna_name_iast": RASHI_NAMES_IAST[lagna_idx], "lagna_symbol": RASHI_SYMBOLS[lagna_idx],
            "asc_longitude": asc_sid
        }
    except Exception: return None
