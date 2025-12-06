# src/ci_mundane.py
# Mundane Astrology Event Finders

from datetime import datetime, timedelta, timezone
from dateutil import tz
import swisseph as swe
from src.ci_core import (
    norm360, get_ayanamsa_code, init_ephe, PLANETS
)

# Use EPHE_PATH from ci_core if available
try:
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent
    EPHE_PATH = str(BASE_DIR / "ephe")
except:
    EPHE_PATH = "ephe"

# Mundane Astrology Event Finders
# ================================

def find_new_moon_in_sign(year: int, sign_index: int, lat: float, lon: float, tzname: str, 
                           ayanamsa: str = "Lahiri", year_type: str = "sidereal") -> datetime | None:
    """
    Find the exact datetime of Sun-Moon conjunction (New Moon) in a specific sign.
    
    Args:
        year: Year to search in
        sign_index: 0-11 (Aries=0, Taurus=1, ..., Pisces=11)
        lat, lon: Location coordinates
        tzname: Timezone name (e.g., 'Asia/Kolkata')
        ayanamsa: Ayanamsa system to use
        year_type: 'sidereal' or 'tropical'
    
    Returns:
        datetime object (in local timezone) of the New Moon event, or None if not found
    """
    
    # Initialize ephemeris
    # Only set sidereal mode if year_type is sidereal
    sid_mode = get_ayanamsa_code(ayanamsa) if year_type == 'sidereal' else None
    FLAGS = init_ephe(ephe_path=EPHE_PATH if 'EPHE_PATH' in globals() else "ephe", 
                      use_moseph=False, sidereal_mode=sid_mode)
    
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
        # FLAGS already handles sidereal/tropical based on initialization
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
    
    Args:
        year: Year to search in
        sign_index: 0-11 (Aries=0, Taurus=1, ..., Pisces=11)
        lat, lon: Location coordinates
        tzname: Timezone name
        ayanamsa: Ayanamsa system to use
        year_type: 'sidereal' or 'tropical'
    
    Returns:
        datetime object (in local timezone) of the ingress, or None if not found
    """
    
    # Initialize ephemeris
    sid_mode = get_ayanamsa_code(ayanamsa) if year_type == 'sidereal' else None
    FLAGS = init_ephe(ephe_path=EPHE_PATH if 'EPHE_PATH' in globals() else "ephe",
                      use_moseph=False, sidereal_mode=sid_mode)
    
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
            if prev_lon < target_lon <= sun_lon or \
               (target_lon == 0 and prev_lon < 0 and sun_lon >= 0):
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
    
    Args:
        planet1, planet2: Planet names
        year: Year to search in (ignored if reference_date is provided)
        lat, lon: Location coordinates
        tzname: Timezone name
        ayanamsa: Ayanamsa system
        aspect_type: 'conjunction' (0°) or 'opposition' (180°)
        year_type: 'sidereal' or 'tropical' 
        sign_index: Optional - if provided, only return event if it occurs in this sign
        reference_date: Optional - start search from this date
        direction: 'forward' (next event) or 'backward' (previous event)
    
    Returns:
        datetime object or None
    """
    
    # Initialize ephemeris
    sid_mode = get_ayanamsa_code(ayanamsa) if year_type == 'sidereal' else None
    FLAGS = init_ephe(ephe_path=EPHE_PATH if 'EPHE_PATH' in globals() else "ephe",
                      use_moseph=False, sidereal_mode=sid_mode)
    
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
