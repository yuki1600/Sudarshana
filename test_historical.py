#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/ashokraj/Documents/Celestial Intelligence')
from src.ci_core import compute_chart_with_tzname

try:
    result = compute_chart_with_tzname(
        -1999, 1, 15, 12, 0, 0,
        28.62137, 77.2148, "Asia/Kolkata",
        ephe_path="./ephe", use_moseph=False, house_sys=b"P",
        ayanamsa="Lahiri"
    )
    print("SUCCESS!")
    print(f"Local DT: {result['local_dt']}")
    print(f"UTC DT: {result['utc_dt']}")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
