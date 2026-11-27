"""moments: part of ephemeris (split from one module; see __init__.py)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from .config import _require_swe, _thread_state

# ---------------------------------------------------------------------------
# Time
# ---------------------------------------------------------------------------
def julian_day_ut(year: int, month: int, day: int, hour_ut: float, gregorian: bool = True) -> float:
    s = _require_swe(getattr(_thread_state, "path", None))  # no ephemeris data needed: keep the open files
    return s.julday(year, month, day, hour_ut, s.GREG_CAL if gregorian else s.JUL_CAL)


def jd_to_calendar(jd_ut: float, gregorian: bool = True) -> Tuple[int, int, int, float]:
    s = _require_swe(getattr(_thread_state, "path", None))
    return s.revjul(jd_ut, s.GREG_CAL if gregorian else s.JUL_CAL)


@dataclass
class BirthData:
    """Birth data in modern conventions: east longitude / east-positive timezone."""
    year: int
    month: int
    day: int
    hour_local: float                 # decimal hours in local (zone) time, may exceed 24 after DST
    tz_east_hours: float              # offset from UT, east positive (IST = +5.5)
    longitude_east: float
    latitude: float
    altitude_m: float = 0.0
    gregorian: bool = True
    place: str = ""
    pressure_hpa: float = 1013.25     # used for sunrise/sunset refraction (.jhd lines 16-17)
    temperature_c: float = 20.0      # the default atmosphere (SunriseDefinition 2 / 3)

    @property
    def jd_ut(self) -> float:
        return julian_day_ut(self.year, self.month, self.day, self.hour_local - self.tz_east_hours, self.gregorian)
