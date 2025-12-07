# src/ci_core/mundane.py
import swisseph as swe
import pandas as pd
from datetime import datetime, timedelta
from dateutil import tz
from .utils import norm360, lon_to_sign_idx, sign_dms_str
from .constants import RASHI_SA, RASHI_EN, MAASA_MAP

from .vargas import get_nakshatra_details, navamsa_for, get_all_vargas
from .dates import jd_to_datetime
from .constants import PLANETS, get_ayanamsa_code
from .calculations import init_ephe
from datetime import timezone

# Need to import compute_chart_with_tzname from calculations (which we will create next)
# To avoid runtime circular import if generic imports are used, we can do local import inside functions if needed
# OR assume calculations.py is the base.

def get_sun_moon_positions(jd, ayanamsa_code=swe.SIDM_LAHIRI):
    """Helper for tithi calcs"""
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    sun_data = swe.calc_ut(jd, swe.SUN, FLAGS)[0]
    moon_data = swe.calc_ut(jd, swe.MOON, FLAGS)[0]
    
    return {
        "sun_lon": norm360(sun_data[0]),
        "moon_lon": norm360(moon_data[0]),
        "sun_speed": sun_data[3],
        "moon_speed": moon_data[3]
    }

def get_tithi_at_jd(jd, ayanamsa_code=swe.SIDM_LAHIRI):
    """Get tithi number (1-30) at given JD"""
    pos = get_sun_moon_positions(jd, ayanamsa_code)
    diff = norm360(pos["moon_lon"] - pos["sun_lon"])
    tithi_num = int(diff // 12) + 1  # 1 to 30
    tithi_progress = (diff % 12) / 12.0
    return tithi_num, tithi_progress

def find_new_moon(start_jd, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """Find the New Moon (Amavasya)"""
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    for _ in range(60):
        tithi, _ = get_tithi_at_jd(jd, ayanamsa_code)
        if tithi == 30: break
        jd += step
    for _ in range(20):
        pos = get_sun_moon_positions(jd, ayanamsa_code)
        diff = norm360(pos["moon_lon"] - pos["sun_lon"])
        if diff > 180: diff -= 360
        if abs(diff) < 0.0001: break
        rel = pos["moon_speed"] - pos["sun_speed"]
        jd += -diff / rel if rel != 0 else step * 0.1
    return jd

def find_full_moon(start_jd, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """Find the Full Moon (Purnima)"""
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    for _ in range(60):
        tithi, _ = get_tithi_at_jd(jd, ayanamsa_code)
        if tithi == 15: break
        jd += step
    for _ in range(20):
        pos = get_sun_moon_positions(jd, ayanamsa_code)
        diff = norm360(pos["moon_lon"] - pos["sun_lon"])
        target_diff = diff - 180
        if abs(target_diff) < 0.0001: break
        rel = pos["moon_speed"] - pos["sun_speed"]
        jd += -target_diff / rel if rel != 0 else step * 0.1
    return jd

def find_tithi_start(start_jd, target_tithi, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """Find when a specific tithi (1-30) begins."""
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    target_diff = (target_tithi - 1) * 12
    
    for _ in range(60):
        tithi, progress = get_tithi_at_jd(jd, ayanamsa_code)
        if tithi == target_tithi:
            pos = get_sun_moon_positions(jd, ayanamsa_code)
            relative_speed = pos["moon_speed"] - pos["sun_speed"]
            jd -= (progress * 12) / relative_speed
            break
        jd += step
    
    for _ in range(20):
        pos = get_sun_moon_positions(jd, ayanamsa_code)
        diff = norm360(pos["moon_lon"] - pos["sun_lon"])
        error = diff - target_diff
        if error > 180: error -= 360
        elif error < -180: error += 360
        if abs(error) < 0.0001: break
        relative_speed = pos["moon_speed"] - pos["sun_speed"]
        adjustment = -error / relative_speed if relative_speed != 0 else step * 0.1
        jd += adjustment
    return jd

def find_lunar_new_year(year, system="amanta", ayanamsa_code=swe.SIDM_LAHIRI):
    start_jd = swe.julday(year, 2, 15, 12.0, swe.GREG_CAL)
    for _ in range(5):
        nm_jd = find_new_moon(start_jd, "next", ayanamsa_code)
        pos = get_sun_moon_positions(nm_jd, ayanamsa_code)
        sun_sign = lon_to_sign_idx(pos["sun_lon"])
        if sun_sign == 11 or sun_sign == 0:
            return nm_jd
        start_jd = nm_jd + 1
    return start_jd

def find_lunar_month_start(start_jd, direction="next", system="amanta", ayanamsa_code=swe.SIDM_LAHIRI):
    if system == "amanta": return find_new_moon(start_jd, direction, ayanamsa_code)
    else: return find_full_moon(start_jd, direction, ayanamsa_code)

def find_solar_return(natal_sun_lon, year, lat, lon, tzname, ayanamsa_code=swe.SIDM_LAHIRI):
    start_jd = swe.julday(year, 1, 1, 12.0, swe.GREG_CAL)
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    jd = start_jd
    for _ in range(400):
        sun_lon = norm360(swe.calc_ut(jd, swe.SUN, FLAGS)[0][0])
        diff = norm360(sun_lon - natal_sun_lon)
        if diff < 1 or diff > 359: break
        jd += 1
    for _ in range(20):
        sun_data = swe.calc_ut(jd, swe.SUN, FLAGS)[0]
        sun_lon, sun_speed = norm360(sun_data[0]), sun_data[3]
        diff = sun_lon - natal_sun_lon
        if diff > 180: diff -= 360
        elif diff < -180: diff += 360
        if abs(diff) < 0.00001: break
        adjustment = -diff / sun_speed if sun_speed != 0 else 0.1
        jd += adjustment
    return jd

def find_tithi_pravesha(natal_sun_lon, natal_tithi, year, lat, lon, tzname, ayanamsa_code=swe.SIDM_LAHIRI):
    solar_return_jd = find_solar_return(natal_sun_lon, year, lat, lon, tzname, ayanamsa_code)
    best_jd = solar_return_jd
    best_diff = float('inf')
    for day_offset in range(-15, 16):
        test_jd = solar_return_jd + day_offset
        tithi, progress = get_tithi_at_jd(test_jd, ayanamsa_code)
        if tithi == natal_tithi:
            swe.set_sid_mode(ayanamsa_code)
            FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
            sun_lon = norm360(swe.calc_ut(test_jd, swe.SUN, FLAGS)[0][0])
            sun_diff = abs(norm360(sun_lon - natal_sun_lon))
            if sun_diff > 180: sun_diff = 360 - sun_diff
            if sun_diff < best_diff:
                best_diff = sun_diff
                best_jd = test_jd
    return best_jd, best_diff

def moon_nakshatra_idx(jd, ayanamsa_code=swe.SIDM_LAHIRI):
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    lon = norm360(swe.calc_ut(jd, swe.MOON, FLAGS)[0][0])
    return int(lon // (360.0 / 27.0))

def yoga_idx_at(jd, ayanamsa_code=swe.SIDM_LAHIRI):
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_lon = norm360(swe.calc_ut(jd, swe.SUN, FLAGS)[0][0])
    moon_lon = norm360(swe.calc_ut(jd, swe.MOON, FLAGS)[0][0])
    yoga_lon = norm360(sun_lon + moon_lon)
    return int(yoga_lon // (360.0 / 27.0))

def find_nakshatra_pravesha(natal_sun_lon, natal_nak_idx, year, lat, lon, tzname, ayanamsa_code=swe.SIDM_LAHIRI):
    anchor_jd = find_solar_return(natal_sun_lon, year, lat, lon, tzname, ayanamsa_code)
    best_jd = None; window_days = 30; step = 0.25; prev_idx = None
    jd = anchor_jd - window_days
    while jd <= anchor_jd + window_days:
        idx = moon_nakshatra_idx(jd, ayanamsa_code)
        if idx == natal_nak_idx and prev_idx is not None and prev_idx != idx:
            low, high = jd - step, jd
            for _ in range(25):
                mid = (low + high) / 2.0
                if moon_nakshatra_idx(mid, ayanamsa_code) == natal_nak_idx: high = mid
                else: low = mid
            best_jd = high; break
        prev_idx = idx; jd += step
    return best_jd if best_jd else anchor_jd

def find_yoga_pravesha(natal_sun_lon, natal_yoga_idx, year, lat, lon, tzname, ayanamsa_code=swe.SIDM_LAHIRI):
    anchor_jd = find_solar_return(natal_sun_lon, year, lat, lon, tzname, ayanamsa_code)
    best_jd = None; window_days = 30; step = 0.25; prev_idx = None
    jd = anchor_jd - window_days
    while jd <= anchor_jd + window_days:
        idx = yoga_idx_at(jd, ayanamsa_code)
        if idx == natal_yoga_idx and prev_idx is not None and prev_idx != idx:
            low, high = jd - step, jd
            for _ in range(25):
                mid = (low + high) / 2.0
                if yoga_idx_at(mid, ayanamsa_code) == natal_yoga_idx: high = mid
                else: low = mid
            best_jd = high; break
        prev_idx = idx; jd += step
    return best_jd if best_jd else anchor_jd

def get_mundane_chart(event_jd, lat, lon, tzname, ayanamsa="Lahiri", ephe_path="ephe"):
    from .calculations import compute_chart_with_tzname
    dt = jd_to_datetime(event_jd, tzname)
    return compute_chart_with_tzname(
        dt.year, dt.month, dt.day,
        dt.hour, dt.minute, dt.second,
        lat, lon, tzname,
        ephe_path=ephe_path,
        ayanamsa=ayanamsa
    )

def calculate_muntha(natal_asc_lon, birth_year, varsha_year):
    years_elapsed = varsha_year - birth_year
    muntha_lon = norm360(natal_asc_lon + (years_elapsed * 30.0))
    sign_idx = lon_to_sign_idx(muntha_lon)
    nak_det = get_nakshatra_details(muntha_lon)
    nsi, pada = navamsa_for(muntha_lon)
    all_vargas = get_all_vargas(muntha_lon)
    return {
        'longitude': muntha_lon,
        'longitude_dms': sign_dms_str(muntha_lon),
        'sign_idx': sign_idx,
        'sign_name': RASHI_SA[sign_idx],
        'sign_en': RASHI_EN[sign_idx],
        'nakshatra': nak_det['nakshatra'],
        'pada': nak_det['pada'],
        'navamsha_idx': nsi,
        'navamsha': RASHI_SA[nsi],
        'vargas': all_vargas
    }

def build_varsha_vimshottari(moon_lon, varsha_start_dt, duration_days=365.25):
    NAK_STEP = 360.0 / 27.0
    MD_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    MD_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
    TOTAL_YEARS = 120.0
    compression_ratio = duration_days / (TOTAL_YEARS * 365.25)
    
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    start_md_i = nak_index % 9
    start_md = MD_ORDER[start_md_i]
    start_md_left_years = MD_YEARS[start_md] * frac_left
    
    rows = []; cur = varsha_start_dt
    seq = [(start_md, start_md_left_years)]
    j = (start_md_i + 1) % 9; spent = start_md_left_years
    while spent < TOTAL_YEARS - 1e-9:
        lord = MD_ORDER[j]; y2 = MD_YEARS[lord]
        seq.append((lord, y2)); spent += y2; j = (j + 1) % 9
        
    for lord, years in seq:
        compressed_days = years * 365.25 * compression_ratio
        st = cur; en = st + timedelta(days=compressed_days)
        rows.append({
            "Mahadasa": lord,
            "Start": st.strftime("%Y-%m-%d %H:%M"),
            "End": en.strftime("%Y-%m-%d %H:%M"),
            "Duration (days)": round(compressed_days, 2),
            "Duration (original years)": round(years, 2)
        })
        cur = en
    return pd.DataFrame(rows)

def build_varsha_yogini(moon_lon, varsha_start_dt, duration_days=365.25):
    NAK_STEP = 360.0 / 27.0
    YOG_ORDER = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
    YOG_YEARS = {"Mangala": 1, "Pingala": 2, "Dhanya": 3, "Bhramari": 4, "Bhadrika": 5, "Ulka": 6, "Siddha": 7, "Sankata": 8}
    TOTAL_YEARS = 36.0
    N2Y = {0:"Bhramari", 1:"Bhadrika", 2:"Ulka", 3:"Siddha", 4:"Sankata", 5:"Mangala", 6:"Pingala", 7:"Dhanya", 8:"Bhramari", 9:"Bhadrika", 10:"Ulka", 11:"Siddha", 12:"Sankata", 13:"Mangala", 14:"Pingala", 15:"Dhanya", 16:"Bhramari", 17:"Bhadrika", 18:"Ulka", 19:"Siddha", 20:"Sankata", 21:"Mangala", 22:"Pingala", 23:"Dhanya", 24:"Bhramari", 25:"Bhadrika", 26:"Ulka"}
    compression_ratio = duration_days / (TOTAL_YEARS * 365.25)
    
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    start_yog = N2Y[nak_index]
    yog_i = YOG_ORDER.index(start_yog)
    
    rows = []; cur = varsha_start_dt
    y1 = YOG_YEARS[start_yog] * frac_left
    rows.append({
        "Yogini": YOG_ORDER[yog_i],
        "Start": cur.strftime("%Y-%m-%d %H:%M"),
        "End": (cur + timedelta(days=y1 * 365.25 * compression_ratio)).strftime("%Y-%m-%d %H:%M"),
        "Duration (days)": round(y1 * 365.25 * compression_ratio, 2),
        "Duration (original years)": round(y1, 2)
    })
    cur += timedelta(days=y1 * 365.25 * compression_ratio)
    yog_i = (yog_i + 1) % 8
    
    for _ in range(24):
        lord = YOG_ORDER[yog_i]; y2 = YOG_YEARS[lord]
        compressed_days = y2 * 365.25 * compression_ratio
        end = cur + timedelta(days=compressed_days)
        rows.append({
            "Yogini": lord,
            "Start": cur.strftime("%Y-%m-%d %H:%M"),
            "End": end.strftime("%Y-%m-%d %H:%M"),
            "Duration (days)": round(compressed_days, 2),
            "Duration (original years)": round(y2, 2)
        })
        cur = end; yog_i = (yog_i + 1) % 8
    return pd.DataFrame(rows)

# ---------------------------------------------------------
# New Additions for Mundane Events (from ci_mundane.py)
# ---------------------------------------------------------

def find_new_moon_in_sign(year: int, sign_index: int, lat: float, lon: float, tzname: str, 
                           ayanamsa: str = "Lahiri", year_type: str = "sidereal") -> datetime | None:
    """
    Find the exact datetime of Sun-Moon conjunction (New Moon) in a specific sign.
    """
    # Only set sidereal mode if year_type is sidereal
    sid_mode = get_ayanamsa_code(ayanamsa) if year_type == 'sidereal' else None
    # Assuming standard ephe path or passed in context, defaulting to "ephe" logic done in init_ephe usually
    # Using default init_ephe() call which handles path internally if possible or we pass None
    FLAGS = init_ephe(use_moseph=False, sidereal_mode=sid_mode)
    
    # Target sign range
    sign_start = sign_index * 30.0
    sign_end = (sign_index + 1) * 30.0
    
    # Search from Jan 1 to Dec 31
    start_date = datetime(year, 1, 1, tzinfo=tz.gettz(tzname))
    end_date = datetime(year, 12, 31, 23, 59, 59, tzinfo=tz.gettz(tzname))
    
    # Sample every 12 hours
    current = start_date
    step = timedelta(hours=12)
    
    prev_diff = None
    
    while current <= end_date:
        # Convert to JD UT
        utc = current.astimezone(timezone.utc)
        ut_hour = utc.hour + utc.minute/60 + utc.second/3600
        jd_ut = swe.julday(utc.year, utc.month, utc.day, ut_hour, swe.GREG_CAL)
        
        # Get Sun and Moon positions
        sun_lon = norm360(swe.calc_ut(jd_ut, swe.SUN, FLAGS)[0][0])
        moon_lon = norm360(swe.calc_ut(jd_ut, swe.MOON, FLAGS)[0][0])
        
        # Calculate angular difference
        diff = norm360(moon_lon - sun_lon)
        
        # Check for conjunction (diff near 0 or 360)
        if prev_diff is not None:
            # Detect zero crossing
            if (prev_diff > 350 and diff < 10) or (prev_diff > diff and diff < 10):
                # We crossed a New Moon! Now refine to exact time
                exact_time = refine_conjunction_time(current - step, current, 
                                                      swe.SUN, swe.MOON, FLAGS)
                
                # Check if both Sun and Moon are in the target sign at conjunction
                utc_exact = exact_time.astimezone(timezone.utc)
                ut_hour_exact = utc_exact.hour + utc_exact.minute/60 + utc_exact.second/3600
                jd_exact = swe.julday(utc_exact.year, utc_exact.month, utc_exact.day, ut_hour_exact, swe.GREG_CAL)
                
                sun_exact = norm360(swe.calc_ut(jd_exact, swe.SUN, FLAGS)[0][0])
                
                sun_sign = int(sun_exact // 30)
                
                if sun_sign == sign_index:
                    return exact_time
        
        prev_diff = diff
        current += step
    
    return None


def find_solar_ingress(year: int, sign_index: int, lat: float, lon: float, tzname: str,
                       ayanamsa: str = "Lahiri", year_type: str = "sidereal") -> datetime | None:
    """
    Find the exact datetime when Sun enters a specific sign (0° of that sign).
    """
    sid_mode = get_ayanamsa_code(ayanamsa) if year_type == 'sidereal' else None
    FLAGS = init_ephe(use_moseph=False, sidereal_mode=sid_mode)
    
    # Target longitude
    target_lon = sign_index * 30.0
    
    # Search from Jan 1 to Dec 31
    start_date = datetime(year, 1, 1, tzinfo=tz.gettz(tzname))
    end_date = datetime(year, 12, 31, 23, 59, 59, tzinfo=tz.gettz(tzname))
    
    # Sample every 6 hours
    current = start_date
    step = timedelta(hours=6)
    
    prev_lon = None
    
    while current <= end_date:
        # Convert to JD UT
        utc = current.astimezone(timezone.utc)
        ut_hour = utc.hour + utc.minute/60 + utc.second/3600
        jd_ut = swe.julday(utc.year, utc.month, utc.day, ut_hour, swe.GREG_CAL)
        
        # Get Sun position
        sun_lon = norm360(swe.calc_ut(jd_ut, swe.SUN, FLAGS)[0][0])
        
        # Check for crossing
        if prev_lon is not None:
            # Handle wraparound at 360/0
            if prev_lon > 350 and sun_lon < 10:
                prev_lon -= 360
            
            # Check if we crossed the target longitude
            if prev_lon < target_lon <= sun_lon or                (target_lon == 0 and prev_lon < 0 and sun_lon >= 0):
                # Refine to exact crossing time
                exact_time = refine_ingress_time(current - step, current, swe.SUN,
                                                  target_lon, FLAGS)
                return exact_time
        
        prev_lon = sun_lon
        current += step
    
    return None


def find_planetary_conjunction(planet1: str, planet2: str, year: int | None = None, lat: float = 0, lon: float = 0,
                                tzname: str = "UTC", ayanamsa: str = "Lahiri", 
                                aspect_type: str = 'conjunction', year_type: str = 'sidereal',
                                sign_index: int | None = None,
                                reference_date: datetime | None = None,
                                direction: str = "forward") -> datetime | None:
    """
    Find the exact datetime when two planets form a conjunction or opposition.
    """
    sid_mode = get_ayanamsa_code(ayanamsa) if year_type == 'sidereal' else None
    FLAGS = init_ephe(use_moseph=False, sidereal_mode=sid_mode)
    
    # Get planet codes
    p1_code = PLANETS.get(planet1)
    p2_code = PLANETS.get(planet2)
    
    if p1_code is None or p2_code is None:
        return None
    
    # Target aspect
    target_aspect = 0.0 if aspect_type == 'conjunction' else 180.0
    
    # Determine search range
    if reference_date:
        start_date = reference_date
        # Search range of 2 years should be sufficient for most aspects
        if direction == 'forward':
            end_date = start_date + timedelta(days=730)
            step = timedelta(hours=12)
        else:
            end_date = start_date - timedelta(days=730)
            step = timedelta(hours=-12)
    else:
        # Default to searching the specified year
        if year is None:
            year = datetime.now().year
        start_date = datetime(year, 1, 1, tzinfo=tz.gettz(tzname))
        end_date = datetime(year, 12, 31, 23, 59, 59, tzinfo=tz.gettz(tzname))
        step = timedelta(hours=12)
    
    current = start_date
    prev_diff = None
    
    # Loop condition helper
    def check_loop(curr, end, direct):
        if direct == 'forward':
            return curr <= end
        else:
            return curr >= end

    while check_loop(current, end_date, direction):
        # Convert to JD UT
        utc = current.astimezone(timezone.utc)
        ut_hour = utc.hour + utc.minute/60 + utc.second/3600
        jd_ut = swe.julday(utc.year, utc.month, utc.day, ut_hour, swe.GREG_CAL)
        
        # Get planet positions
        p1_lon = norm360(swe.calc_ut(jd_ut, p1_code, FLAGS)[0][0])
        p2_lon = norm360(swe.calc_ut(jd_ut, p2_code, FLAGS)[0][0])
        
        # Calculate angular difference
        diff = norm360(p2_lon - p1_lon)
        
        # Check for aspect
        if prev_diff is not None:
            aspect_found = False
            
            if aspect_type == 'conjunction':
                # Look for diff crossing 0
                if (prev_diff > 350 and diff < 10) or (prev_diff > diff and diff < 5):
                    aspect_found = True
            else:  # opposition
                # Look for diff crossing 180
                if abs(prev_diff - 180) > 10 and abs(diff - 180) < 10:
                    if prev_diff < 180 < diff or prev_diff > 180 > diff:
                        aspect_found = True
            
            if aspect_found:
                # Refine to exact time
                if direction == 'forward':
                    t_start, t_end = current - step, current
                else:
                    t_start, t_end = current, current - step
                    
                exact_time = refine_aspect_time(t_start, t_end, p1_code, p2_code,
                                                 target_aspect, FLAGS)
                
                # If sign_index is specified, check if event occurs in that sign
                if sign_index is not None:
                    utc_exact = exact_time.astimezone(timezone.utc)
                    ut_hour_exact = utc_exact.hour + utc_exact.minute/60 + utc_exact.second/3600
                    jd_exact = swe.julday(utc_exact.year, utc_exact.month, utc_exact.day, ut_hour_exact, swe.GREG_CAL)
                    
                    p1_exact = norm360(swe.calc_ut(jd_exact, p1_code, FLAGS)[0][0])
                    
                    p1_sign = int(p1_exact // 30)
                    
                    if p1_sign != sign_index:
                        # Event not in target sign, continue searching
                        prev_diff = diff
                        current += step
                        continue
                
                return exact_time
        
        prev_diff = diff
        current += step
    
    return None


# Helper functions for refining event times

def refine_conjunction_time(start: datetime, end: datetime, body1_code: int, body2_code: int,
                             flags: int) -> datetime:
    """Refine conjunction time using bisection method."""
    
    while (end - start).total_seconds() > 1:  # Refine to 1 second
        mid = start + (end - start) / 2
        
        # Get positions at mid
        utc = mid.astimezone(timezone.utc)
        ut_hour = utc.hour + utc.minute/60 + utc.second/3600
        jd_ut = swe.julday(utc.year, utc.month, utc.day, ut_hour, swe.GREG_CAL)
        
        b1_lon = norm360(swe.calc_ut(jd_ut, body1_code, flags)[0][0])
        b2_lon = norm360(swe.calc_ut(jd_ut, body2_code, flags)[0][0])
        
        diff = norm360(b2_lon - b1_lon)
        
        # Check which half contains the zero crossing
        if diff < 180:
            end = mid
        else:
            start = mid
    
    return start + (end - start) / 2


def refine_ingress_time(start: datetime, end: datetime, body_code: int, target_lon: float,
                         flags: int) -> datetime:
    """Refine ingress time using bisection method."""
    
    while (end - start).total_seconds() > 1:  # Refine to 1 second
        mid = start + (end - start) / 2
        
        # Get position at mid
        utc = mid.astimezone(timezone.utc)
        ut_hour = utc.hour + utc.minute/60 + utc.second/3600
        jd_ut = swe.julday(utc.year, utc.month, utc.day, ut_hour, swe.GREG_CAL)
        
        body_lon = norm360(swe.calc_ut(jd_ut, body_code, flags)[0][0])
        
        # Handle wraparound
        if target_lon == 0 and body_lon > 180:
            body_lon -= 360
        
        # Check which half contains the crossing
        if body_lon < target_lon:
            start = mid
        else:
            end = mid
    
    return start + (end - start) / 2


def refine_aspect_time(start: datetime, end: datetime, body1_code: int, body2_code: int,
                        target_aspect: float, flags: int) -> datetime:
    """Refine aspect time using bisection method."""
    
    while (end - start).total_seconds() > 1:  # Refine to 1 second
        mid = start + (end - start) / 2
        
        # Get positions at mid
        utc = mid.astimezone(timezone.utc)
        ut_hour = utc.hour + utc.minute/60 + utc.second/3600
        jd_ut = swe.julday(utc.year, utc.month, utc.day, ut_hour, swe.GREG_CAL)
        
        b1_lon = norm360(swe.calc_ut(jd_ut, body1_code, flags)[0][0])
        b2_lon = norm360(swe.calc_ut(jd_ut, body2_code, flags)[0][0])
        
        diff = norm360(b2_lon - b1_lon)
        
        # Check which half is closer to target aspect
        if abs(diff - target_aspect) > abs(diff - target_aspect - 180):
            diff -= 360 if diff > target_aspect else -360
        
        if diff < target_aspect:
            start = mid
        else:
            end = mid
    
    return start + (end - start) / 2

