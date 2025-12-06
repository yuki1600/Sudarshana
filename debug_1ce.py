import sys
from datetime import datetime
from src.ci_core import compute_chart

print("Debugging 1 CE chart calculation...")
try:
    # 1 CE parameters
    y, m, d = 1, 1, 1
    hh, mm, ss = 12, 0, 0
    lat, lon = 12.2979, 76.6393
    tz = "Asia/Kolkata"
    ayanamsa = "Lahiri"
    
    res = compute_chart(y, m, d, hh, mm, ss, lat, lon, tzname_override=tz, ayanamsa=ayanamsa)
    print("Success!")
    print(res.keys())
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
