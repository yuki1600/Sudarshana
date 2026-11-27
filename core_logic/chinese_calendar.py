"""
chinese_calendar: the Chinese lunisolar date of a civil day, for Zi Wei Dou Shu (server/traditions.py).

Months run from new moon to new moon; the eleventh holds the winter solstice; a year of thirteen months (eleventh to
eleventh) repeats, as a leap month, its first month that holds no principal term (zhongqi, the Sun at a multiple of
30 degrees); every boundary is reckoned on the date in China (UTC+8). The Sun and the Moon are the app's own, under the
chosen ephemeris (NASA JPL's DE442). Source: H. Aslaksen, "The Mathematics of the Chinese Calendar" (2010), sections
3-4; docs/SOURCES.md section 19.
"""
from __future__ import annotations
import math
from dataclasses import replace
from typing import Dict, List

from . import ephemeris as E, time_search as TS

CHINA = 8.0 / 24.0      # China Standard Time, UTC+8


def _day(jd_ut: float) -> int:
    """The date in China of a moment, as a Julian day number."""
    return math.floor(jd_ut + CHINA + 0.5)


def _end(day: int) -> float:
    """The last moment (UT) of a China date."""
    return day + 0.5 - CHINA


def lunar_date(local_day: int, cfg: E.EphemerisConfig) -> Dict[str, int]:
    """The Chinese lunar date of the civil date ``local_day`` (a Julian day number): {year, month, leap (0/1), day}.
    ``year`` is the Gregorian year its new year fell in (its stem and branch give the lunar year's)."""
    trop = replace(cfg, ayanamsa="TROPICAL", siddhanta=0)
    sun = E.longitude_func("Sun", trop)

    def new_moon_by(day: int) -> int:       # the China date of the last new moon on or before ``day``
        return _day(TS.longitude_event(_end(day), 2, 0.0, 1, "diff", True, trop))

    def next_new_moon(day: int) -> int:     # the China date of the first new moon after ``day``
        return _day(TS.longitude_event(_end(day), 2, 0.0, 1, "diff", False, trop))

    solstice = _day(TS.longitude_event(_end(local_day), 1, 270.0, None, "diff", True, trop))
    following = _day(TS.longitude_event(_end(solstice) + 1.0, 1, 270.0, None, "diff", False, trop))
    first, last = new_moon_by(solstice), new_moon_by(following)
    starts: List[int] = [first]
    while starts[-1] < last:
        starts.append(next_new_moon(starts[-1]))
    leap_at = -1
    if len(starts) - 1 == 13:       # thirteen months: the first without a principal term is the leap one
        term = lambda day: math.floor(sun(day - 0.5 - CHINA) / 30.0)  # noqa: E731  the Sun's 30-degree part at the date's start
        leap_at = next((i for i in range(1, 13) if term(starts[i + 1]) == term(starts[i])), -1)
    k = new_moon_by(local_day)
    index = min(range(len(starts)), key=lambda i: abs(starts[i] - k))
    if index == len(starts) - 1:     # the next eleventh month already begun
        index, leap_at = 0, -1
    n = index - (1 if 0 < leap_at <= index else 0)
    month = (10 + n) % 12 + 1        # 0 is the eleventh month
    year_start = next(i for i in range(len(starts)) if (10 + i - (1 if 0 < leap_at <= i else 0)) % 12 + 1 == 1 and i != leap_at)
    year = E.jd_to_calendar(starts[year_start])[0] - (1 if index < year_start else 0)
    return {"year": year, "month": month, "leap": int(index == leap_at), "day": local_day - k + 1}
