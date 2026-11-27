"""
core_logic/workflows.py
=======================
Ephemeris-driven mode workflows: the engines in ``mundane``, ``tithi_pravesha`` and
``miscellany`` take longitude callbacks; this module feeds them ``ephemeris.longitude_func``
and adds the searches of the transit, Tajaka, mundane and rectification screens (the app's help:
"Transit calculations", "Tajaka calculations", "Tithi Pravesha", "Mundane calculations", "Impact of birthtime
error").  Sources: docs/SOURCES.md sections 12-14 and 17.

Requires pyswisseph, like ``ephemeris``.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from . import ephemeris as E
from .mundane import solve_longitude_crossing
from .natal_chart import RASI_NAMES_EN
from .utils import norm360

# Search step (days) small enough that no body can cross a target and come back within it,
# and a window covering a full synodic cycle including retrograde loops.
_STEP_DAYS = {"Moon": 0.25, "Sun": 1.0, "Mercury": 0.5, "Venus": 1.0, "Mars": 1.0,
              "Jupiter": 2.0, "Saturn": 2.0, "Rahu": 2.0, "Ketu": 2.0}
_WINDOW_DAYS = {"Moon": 30.0, "Sun": 370.0, "Mercury": 400.0, "Venus": 600.0, "Mars": 800.0,
                "Jupiter": 4500.0, "Saturn": 11000.0, "Rahu": 7000.0, "Ketu": 7000.0}
ARDRA_START = 5 * 360.0 / 27.0          # 6th nakshatra: starts at 6 deg 40' Gemini


def find_transit(body: str, target_lon: float, jd_start: float,
                 cfg: Optional[E.EphemerisConfig] = None, max_days: Optional[float] = None) -> Optional[float]:
    """First JD (UT) after ``jd_start`` when ``body`` reaches sidereal ``target_lon``
    (the transit search).  Retrograde crossings count."""
    return solve_longitude_crossing(E.longitude_func(body, cfg), target_lon, jd_start + _STEP_DAYS[body],
                                    step_days=_STEP_DAYS[body],
                                    max_days=max_days or _WINDOW_DAYS[body], tolerance_deg=1e-6)


def next_sign_change(body: str, jd_start: float, cfg: Optional[E.EphemerisConfig] = None) -> Dict[str, Any]:
    """When ``body`` next leaves its current sign, forwards or (retrograde) backwards."""
    sign = int(E.longitude_func(body, cfg)(jd_start) // 30)
    fwd = find_transit(body, ((sign + 1) % 12) * 30.0, jd_start, cfg)
    back = find_transit(body, sign * 30.0, jd_start, cfg)
    if back is None or (fwd is not None and fwd < back):
        jd, to = fwd, (sign + 1) % 12
    else:
        jd, to = back, (sign - 1) % 12
    return {"body": body, "jd_ut": jd, "from_sign": sign, "to_sign": to}


def lagna_sign_change(birth: E.BirthData, cfg: Optional[E.EphemerisConfig] = None,
                      backward: bool = False) -> Dict[str, Any]:
    """Birth-time rectification aid: the local time at which the lagna leaves (``backward``:
    entered) its current sign, i.e. how far the birth time can move without changing it."""
    f = E.longitude_func("Lagna", cfg, birth)
    jd0 = birth.jd_ut
    sign = int(f(jd0) // 30)
    target = sign * 30.0 if backward else ((sign + 1) % 12) * 30.0
    # the lagna circles once per sidereal day, so the previous crossing is within one day
    start = jd0 - 0.9972 if backward else jd0
    jd = solve_longitude_crossing(f, target, start + 0.002, step_days=0.002, max_days=1.0, tolerance_deg=1e-6)
    return {"jd_ut": jd, "hour_local": birth.hour_local + (jd - jd0) * 24.0,
            "minutes_from_birth": (jd - jd0) * 1440.0, "sign_index": sign}


def transit_calendar(natal: Dict[str, Any], jd_start: float, step_days: float = 1.0, rows: int = 30,
                     bodies: Optional[List[str]] = None, cfg: Optional[E.EphemerisConfig] = None) -> List[Dict[str, Any]]:
    """Transit calendar: every ``step_days`` the sign of each transiting body and
    its house from natal lagna and natal Moon (gochara, PD 26.1-8).  At most 100 rows."""
    bodies = bodies or ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    lagna_sign, moon_sign = natal["lagna_sign"], natal["planet_signs"]["Moon"]
    out = []
    for i in range(min(rows, 100)):
        jd = jd_start + i * step_days
        pos = E.planet_positions(jd, cfg)
        out.append({"jd_ut": jd, "bodies": {
            b: {"lon": pos[b]["lon"], "sign": RASI_NAMES_EN[pos[b]["sign_index"]],
                "house_from_lagna": (pos[b]["sign_index"] - lagna_sign) % 12 + 1,
                "house_from_moon": (pos[b]["sign_index"] - moon_sign) % 12 + 1,
                "retrograde": pos[b]["retrograde"]} for b in bodies}})
    return out


def solar_return(birth: E.BirthData, years: float, cfg: Optional[E.EphemerisConfig] = None) -> float:
    """Tajaka chart moment: the Sun back at its natal longitude plus ``years`` x 360 deg.
    Whole years give annual charts; 1/12 steps monthly charts, 1/144 the 60-hour charts, etc."""
    natal_sun = E.planet_positions(birth.jd_ut, cfg)["Sun"]["lon"]
    approx = birth.jd_ut + years * 365.256363
    return find_transit("Sun", natal_sun + years * 360.0, approx - 5.0, cfg, max_days=10.0)


def chart_at_jd(birth: E.BirthData, jd_ut: float, cfg: Optional[E.EphemerisConfig] = None,
                **kw) -> Dict[str, Any]:
    """build_chart for another moment at the birth place (Tajaka, TP, entry charts)."""
    y, m, d, h = E.jd_to_calendar(jd_ut + birth.tz_east_hours / 24.0, birth.gregorian)
    return E.build_chart(replace(birth, year=y, month=m, day=d, hour_local=h), cfg, **kw)


def entry_chart(birth: E.BirthData, period: Dict[str, Any], cfg: Optional[E.EphemerisConfig] = None,
                **kw) -> Dict[str, Any]:
    """"Entry chart of this period": the chart cast when a dasa period (an entry of any
    dasas timeline, local ISO dates) began."""
    start = datetime.fromisoformat(period["start"])
    jd = E.julian_day_ut(start.year, start.month, start.day,
                         start.hour + start.minute / 60 + start.second / 3600 - birth.tz_east_hours, birth.gregorian)
    return chart_at_jd(birth, jd, cfg, **kw)


def tithi_pravesha(birth: E.BirthData, years_after_birth: int,
                   cfg: Optional[E.EphemerisConfig] = None) -> Dict[str, Any]:
    """Tithi Pravesha chart moment of a year: the natal Moon-Sun angle recurring while the Sun
    is in its natal sign (search starts when the Sun enters that sign)."""
    from .tithi_pravesha import solve_tithi_pravesha_chart
    natal = E.planet_positions(birth.jd_ut, cfg)
    sun_sign_start = int(natal["Sun"]["lon"] // 30) * 30.0
    approx = find_transit("Sun", sun_sign_start, solar_return(birth, years_after_birth, cfg) - 40.0, cfg, 50.0)
    return solve_tithi_pravesha_chart(natal["Sun"]["lon"], natal["Moon"]["lon"],
                                      E.longitude_func("Sun", cfg), E.longitude_func("Moon", cfg), approx)


def ardra_pravesha(year: int, cfg: Optional[E.EphemerisConfig] = None) -> float:
    """Mundane: JD (UT) when the Sun enters Ardra nakshatra (6 deg 40' Gemini) in ``year``."""
    return find_transit("Sun", ARDRA_START, E.julian_day_ut(year, 1, 1, 0.0), cfg)


def angular_return(body1: str, body2: str, separation_deg: float, jd_start: float,
                   cfg: Optional[E.EphemerisConfig] = None, window_days: float = 40.0) -> Dict[str, Any]:
    """Angular return: when body2 - body1 next equals ``separation_deg`` (astronomy)."""
    from .miscellany import compute_angular_separation_return
    return compute_angular_separation_return(E.longitude_func(body1, cfg), E.longitude_func(body2, cfg),
                                             separation_deg, jd_start, window_days)


def match_charts(bride: Dict[str, Any], groom: Dict[str, Any]) -> Dict[str, Any]:
    """Horoscope matching from two build_chart results."""
    from .compatibility import evaluate_horoscope_matching

    def data(c):
        return {"moon_longitude": c["planet_longitudes"]["Moon"], "lagna_longitude": c["lagna_lon"],
                "planet_longitudes": c["planet_longitudes"]}
    return evaluate_horoscope_matching(data(bride), data(groom))


def prasna_lagna(kind: str, n: int, d150_unequal: bool = True) -> float:
    """The Prasna Lagna of number ``n`` (Prasna (Horary) tab): "108" the middle of navamsa n (the 108 navamsas,
    BPHS 6.12); "249" the start of KP sub n (KSK); "nadi" the middle of nadi n of 1800, 150 to a sign (DK's nadyamsas;
    D150Preference ``d150_unequal``: the unequal nadis, off: 0.2 degree each).  Choosing the lagna by a number the
    querent gives is a convention of these schools (docs/SOURCES.md section 14)."""
    if kind == "108":
        return ((n - 1) // 9) * 30.0 + ((n - 1) % 9 + 0.5) * 10.0 / 3.0
    if kind == "249":
        from .kp_astrology import KP_249_TABLE
        return KP_249_TABLE[n - 1]["start_deg"]
    from .varga_charts import D150_BOUNDS
    sign, i = (n - 1) // 150, (n - 1) % 150
    if d150_unequal:
        return sign * 30.0 + (D150_BOUNDS[i] + (D150_BOUNDS + (15120,))[i + 1]) / 1008.0     # the table holds each nadi's start; the last ends at 30 degrees
    return sign * 30.0 + i * 0.2 + 0.1


def nisheka_moment(birth: E.BirthData, chart: Dict[str, Any], cfg: Optional[E.EphemerisConfig] = None) -> float:
    """The Nisheka / Aadhana chart (Modes menu): JD UT of the conception chart, BPHS 4.25-30.  Days before birth =
    the whole degrees between Maandi and Saturn in their signs + the arc from the 1st to the 9th cusp + (when the lagna's
    lord is in the invisible half, within 180 deg ahead of the lagna) the Moon's degrees in its sign + 28.5 (BPHS's
    "signs, degrees" read as months of 30 days and days; the 28.5 a convention); taken /
    365 years of 360-day (savana, definition 1) years, and the chart runs for that many days (its dasas compressed
    to them)."""
    lons = chart["planet_longitudes"]
    days = nisheka_days(lons["Saturn"], chart["upagrahas"]["Mandi"], lons["Moon"], chart["lagna_lon"],
                        [lons[p] for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")])
    return birth.jd_ut - days * 360.0 / 365.0


def nisheka_days(saturn: float, mandi: float, moon: float, lagna: float, sun_to_saturn, cusp_arc: float = 240.0) -> float:
    """The day count of BPHS 4.25-30 (see ``nisheka_moment``); ``cusp_arc`` = 9th cusp - 1st cusp (240 for the
    default equal houses)."""
    from .sign_strength import SIGN_LORDS
    x = abs(int(mandi % 30.0 - saturn % 30.0)) + cusp_arc
    lord = SIGN_LORDS[int(lagna // 30)]
    if (sun_to_saturn[lord - 1] - lagna) % 360.0 < 180.0:
        x += moon % 30.0
    return x + 28.5


def lifecycle_moment(birth: E.BirthData, n: int, cfg: Optional[E.EphemerisConfig] = None, years: float = 144.0,
                     kind: str = "SOLAR") -> datetime:
    """Modes > next / previous lifecycle (a convention, no verse): the chart ``n`` lifecycles of ``years`` (LifeCycleYears)
    from birth; ``kind`` as ``ephemeris.dasa_year_mapper`` (LifeCycleYearDefinition, default the true sidereal year)."""
    return E.dasa_year_mapper(birth, cfg, kind)(n * years)


def _sign_spans(body: str, jd0: float, jd1: float, cfg: Optional[E.EphemerisConfig], birth: E.BirthData) -> List[tuple]:
    """(sign, start JD, end JD) of a slow body's stays in signs between two moments, retrograde re-entries included."""
    sign = lambda jd: int(E.planet_positions(jd, cfg, birth)[body]["lon"] // 30)  # noqa: E731
    spans, t, s, start = [], jd0, sign(jd0), jd0
    while t < jd1:
        t2 = min(t + 3.0, jd1)
        s2 = sign(t2)
        if s2 != s:
            a, b = t, t2
            while b - a > 1e-3:
                m = (a + b) / 2
                a, b = (m, b) if sign(m) == s else (a, m)
            spans.append((s, start, b))
            s, start = s2, b
        t = t2
    spans.append((s, start, jd1))
    return spans


def dasa_transit_correlation(birth: E.BirthData, jd0: float, jd1: float, ref_sign: int,
                             cfg: Optional[E.EphemerisConfig] = None) -> Dict[int, Dict[str, List[tuple]]]:
    """Dasa-Transit Correlation (dasa popup; a convention, no verse): for a chosen period, the spans of Jupiter, Saturn, Rahu
    and Ketu in each house (1 .. 12) from ``ref_sign``, the sign the period's lord occupies: {house: {planet: [(start JD,
    end JD)]}}, clipped to the period."""
    out = {h: {p: [] for p in ("Jupiter", "Saturn", "Rahu", "Ketu")} for h in range(1, 13)}
    for body in ("Jupiter", "Saturn", "Rahu", "Ketu"):
        for sign, a, b in _sign_spans(body, jd0, jd1, cfg, birth):
            out[(sign - ref_sign) % 12 + 1][body].append((a, b))
    return out
