
import sys
import os
from datetime import datetime
from dateutil import tz

# Add src to path
sys.path.append(os.getcwd())

from src.ci_mundane import find_solar_ingress, find_new_moon_in_sign

def test_calculations():
    print("Testing Mundane Calculations...")
    
    # Parameters
    year = 2025
    lat = 28.6139 # Delhi
    lon = 77.2090
    tzname = "Asia/Kolkata"
    ayanamsa = "Lahiri"
    
    # 1. Test Solar Ingress into Aries (Mesha)
    print("\n1. Testing Solar Ingress into Aries (0) - Sidereal")
    ingress_dt = find_solar_ingress(year, 0, lat, lon, tzname, ayanamsa, "sidereal")
    print(f"Result: {ingress_dt}")
    
    if ingress_dt:
        # Verify position
        import swisseph as swe
        from src.ci_core import init_ephe, get_ayanamsa_code, norm360
        
        swe.set_sid_mode(get_ayanamsa_code(ayanamsa), 0, 0)
        utc = ingress_dt.astimezone(tz.UTC)
        jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600, swe.GREG_CAL)
        
        # Result is already sidereal
        sun_sid = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]
        print(f"Sun Sidereal Longitude at result: {sun_sid}")
        
    # 2. Test New Moon in Pisces (11) - Sidereal
    print("\n2. Testing New Moon in Pisces (11) - Sidereal")
    nm_dt = find_new_moon_in_sign(year, 11, lat, lon, tzname, ayanamsa, "sidereal")
    print(f"Result: {nm_dt}")
    
    if nm_dt:
        # Verify position
        utc = nm_dt.astimezone(tz.UTC)
        jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600, swe.GREG_CAL)
        
        swe.set_sid_mode(get_ayanamsa_code(ayanamsa), 0, 0)
        sun_sid = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]
        moon_sid = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]
        
        print(f"Sun Sidereal Longitude: {sun_sid}")
        print(f"Moon Sidereal Longitude: {moon_sid}")
        print(f"Difference: {norm360(moon_sid - sun_sid)}")

if __name__ == "__main__":
    test_calculations()
