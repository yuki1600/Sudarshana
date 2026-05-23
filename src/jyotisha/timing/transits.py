# src/ci_core/transits.py
from datetime import datetime, timezone
from dateutil import tz
import swisseph as swe
import pandas as pd
from src.jyotisha.base.constants import PLANETS
from src.jyotisha.base.utils import norm360, lon_to_sign_idx, sign_dms_str, rashi_name
from src.jyotisha.identity.vargas import get_all_vargas, get_nakshatra_details, navamsa_for


def init_ephe_wrapper(ephe_path="ephe", use_moseph=False, sidereal_mode=swe.SIDM_LAHIRI):
    """
    Wrapper for initializing swisseph similar to ci_core.init_ephe,
    but duplicated here to avoid circular import if calculations calls transits (unlikely but safe).
    Alternatively, we can just use set_ephe_path directly.
    """
    if not use_moseph:
        swe.set_ephe_path(ephe_path)
    if sidereal_mode is not None:
        swe.set_sid_mode(sidereal_mode)
    ephflag = swe.FLG_MOSEPH if use_moseph else swe.FLG_SWIEPH
    flags = ephflag | swe.FLG_SPEED
    if sidereal_mode is not None:
        flags |= swe.FLG_SIDEREAL
    return flags


def find_planet_sign_change(planet_code, start_jd, target_sign=None, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """Find when a planet enters a new sign (or a specific sign)."""
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    
    # Get starting sign
    start_lon = norm360(swe.calc_ut(jd, planet_code, FLAGS)[0][0])
    start_sign = lon_to_sign_idx(start_lon)
    
    # For "next" direction, ensure we start searching from slightly after start_jd
    if direction == "next":
        jd = start_jd + 0.01  # Add ~14 minutes
        start_lon = norm360(swe.calc_ut(jd, planet_code, FLAGS)[0][0])
        start_sign = lon_to_sign_idx(start_lon)
    
    # Search for sign change
    for _ in range(1000):  # Max ~3 years search
        jd += step
        lon = norm360(swe.calc_ut(jd, planet_code, FLAGS)[0][0])
        current_sign = lon_to_sign_idx(lon)
        
        if target_sign is not None:
            if current_sign == target_sign:
                break
        else:
            if current_sign != start_sign:
                break
        
        start_sign = current_sign
    
    # Refine to exact moment of sign entry
    target_entry = (current_sign * 30) if direction == "next" else ((current_sign + 1) * 30) % 360
    
    for _ in range(20):
        data = swe.calc_ut(jd, planet_code, FLAGS)[0]
        lon = norm360(data[0])
        speed = data[3]
        
        diff = lon - target_entry
        if diff > 180: diff -= 360
        elif diff < -180: diff += 360
        
        if abs(diff) < 0.00001:
            break
        
        adjustment = -diff / speed if speed != 0 else step * 0.1
        jd += adjustment
    
    return jd, current_sign


def find_planet_stationary(planet_code, start_jd, direction="next", station_type="retrograde"):
    """
    Find when a planet becomes stationary (speed = 0).
    station_type: "retrograde" (before retrograde) or "direct" (before direct)
    """
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    
    start_speed = swe.calc_ut(jd, planet_code, FLAGS)[0][3]
    
    for _ in range(1000):
        jd += step
        speed = swe.calc_ut(jd, planet_code, FLAGS)[0][3]
        if station_type == "retrograde":
            if start_speed > 0 and speed < 0: break
        else:  # direct
            if start_speed < 0 and speed > 0: break
        start_speed = speed
    
    # Refine
    jd -= step
    for _ in range(20):
        data = swe.calc_ut(jd, planet_code, FLAGS)[0]
        speed = data[3]
        if abs(speed) < 0.00001: break
        
        jd2 = jd + 0.01
        speed2 = swe.calc_ut(jd2, planet_code, FLAGS)[0][3]
        accel = (speed2 - speed) / 0.01
        
        if abs(accel) > 0.00001:
            adjustment = -speed / accel
            jd += adjustment
        else:
            jd += step * 0.1
    
    return jd


def find_conjunction(planet1_code, planet2_code, start_jd, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """Find when two planets conjoin (same longitude)."""
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    prev_diff = None
    
    for _ in range(1000):
        lon1 = norm360(swe.calc_ut(jd, planet1_code, FLAGS)[0][0])
        lon2 = norm360(swe.calc_ut(jd, planet2_code, FLAGS)[0][0])
        diff = norm360(lon1 - lon2)
        if diff > 180: diff -= 360
        
        if prev_diff is not None:
            if (prev_diff > 0 and diff <= 0) or (prev_diff < 0 and diff >= 0): break
        prev_diff = diff
        jd += step
    
    # Refine
    for _ in range(20):
        data1 = swe.calc_ut(jd, planet1_code, FLAGS)[0]
        data2 = swe.calc_ut(jd, planet2_code, FLAGS)[0]
        lon1, speed1 = norm360(data1[0]), data1[3]
        lon2, speed2 = norm360(data2[0]), data2[3]
        
        diff = lon1 - lon2
        if diff > 180: diff -= 360
        elif diff < -180: diff += 360
        
        if abs(diff) < 0.00001: break
        
        relative_speed = speed1 - speed2
        adjustment = -diff / relative_speed if abs(relative_speed) > 0.00001 else step * 0.1
        jd += adjustment
    
    return jd


def find_opposition(planet1_code, planet2_code, start_jd, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """Find when two planets are in opposition (180 degrees apart)."""
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    prev_diff = None
    
    for _ in range(1000):
        lon1 = norm360(swe.calc_ut(jd, planet1_code, FLAGS)[0][0])
        lon2 = norm360(swe.calc_ut(jd, planet2_code, FLAGS)[0][0])
        diff = norm360(lon1 - lon2) - 180
        if diff > 180: diff -= 360
        elif diff < -180: diff += 360
        
        if prev_diff is not None:
            if (prev_diff > 0 and diff <= 0) or (prev_diff < 0 and diff >= 0): break
        prev_diff = diff
        jd += step
    
    # Refine
    for _ in range(20):
        data1 = swe.calc_ut(jd, planet1_code, FLAGS)[0]
        data2 = swe.calc_ut(jd, planet2_code, FLAGS)[0]
        lon1, speed1 = norm360(data1[0]), data1[3]
        lon2, speed2 = norm360(data2[0]), data2[3]
        
        diff = norm360(lon1 - lon2) - 180
        if diff > 180: diff -= 360
        elif diff < -180: diff += 360
        
        if abs(diff) < 0.00001: break
        
        relative_speed = speed1 - speed2
        adjustment = -diff / relative_speed if abs(relative_speed) > 0.00001 else step * 0.1
        jd += adjustment
    
    return jd


def compute_transit_positions(transit_dt, lat, lon, tzname, ephe_path="ephe", use_moseph=False, ayanamsa="Lahiri"):
    from .constants import AYANAMSA_OPTIONS
    ayanamsa_code = AYANAMSA_OPTIONS.get(ayanamsa, swe.SIDM_LAHIRI)
    FLAGS = init_ephe_wrapper(ephe_path, use_moseph, sidereal_mode=ayanamsa_code)
    
    local_zone = tz.gettz(tzname)
    if isinstance(transit_dt, str):
        transit_dt = datetime.fromisoformat(transit_dt.replace('Z', '+00:00'))
    
    if transit_dt.tzinfo is None:
        transit_dt = transit_dt.replace(tzinfo=local_zone)
    
    dt_utc = transit_dt.astimezone(timezone.utc)
    ut_hour = dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut_hour, swe.GREG_CAL)
    
    cusps_trop, ascmc_trop = swe.houses(jd_ut, lat, lon, b'O')
    ayan = swe.get_ayanamsa_ut(jd_ut)
    asc_sid = norm360(ascmc_trop[0] - ayan)
    
    rows = []
    
    # Add transit Ascendant
    all_vargas = get_all_vargas(asc_sid)
    nak_det = get_nakshatra_details(asc_sid)
    nsi, pada = navamsa_for(asc_sid)
    rows.append({
        "Point": "Ascendant (Transit)",
        "Longitude (Sign DMS)": sign_dms_str(asc_sid),
        "Longitude (Dec)": round(asc_sid, 4),
        "Rashi": rashi_name(asc_sid),
        "Rashi_Idx": lon_to_sign_idx(asc_sid),
        "Nakshatra": nak_det['nakshatra'],
        "Pada": nak_det['pada'],
        "Navamsha_Idx": nsi,
        "D3_Idx": all_vargas['D3'],
        "D10_Idx": all_vargas['D10'],
        "Retro": False
    })
    
    for nm, code in PLANETS.items():
        vals = swe.calc_ut(jd_ut, code, FLAGS)[0]
        lonv, spd = norm360(vals[0]), vals[3]
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        nsi, pada = navamsa_for(lonv)
        is_retro = spd < 0
        
        rows.append({
            "Point": nm,
            "Longitude (Sign DMS)": sign_dms_str(lonv),
            "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv),
            "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Navamsha_Idx": nsi,
            "D3_Idx": all_vargas['D3'],
            "D10_Idx": all_vargas['D10'],
            "Retro": is_retro
        })
    
    try:
        vals_true = swe.calc_ut(jd_ut, swe.TRUE_NODE, FLAGS)[0]
    except Exception:
        vals_true = swe.nod_aps_ut(jd_ut, swe.MOON, FLAGS, swe.NODBIT_OSCU)[0]
    
    rahu = norm360(vals_true[0])
    ketu = norm360(rahu + 180)
    
    for nm, lonv in [("Rahu (true)", rahu), ("Ketu (true)", ketu)]:
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        nsi, pada = navamsa_for(lonv)
        rows.append({
            "Point": nm,
            "Longitude (Sign DMS)": sign_dms_str(lonv),
            "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv),
            "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Navamsha_Idx": nsi,
            "D3_Idx": all_vargas['D3'],
            "D10_Idx": all_vargas['D10'],
            "Retro": True
        })
    
    return {
        "transit_dt": transit_dt.isoformat(),
        "ayanamsa_value": round(ayan, 6),
        "points": pd.DataFrame(rows)
    }
