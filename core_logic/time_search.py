"""
core_logic/time_search.py
==========================
Time searches (astronomy: when a longitude, a difference, a sum or a midpoint reaches a value), with step sizes
and tolerances that find moments to the second (docs/SOURCES.md section 12):

* ``longitude_event`` - the
  moment a body, or the difference / sum / midpoint of two bodies, reaches a target; steps of 1/12 day when the
  lagna is involved, 3 days for the Moon, 10 days otherwise (halved for midpoints; negative to search back) until
  the value wraps through the target, then refined (regula falsi) to 1.157e-5 day (lagna: 7.7e-7 day);
* ``sum_event`` - the sum of two longitudes (yoga end times, SS 2.65) through the same search;
* ``retrograde_station`` - next / previous change of retrograde state (Rahu by its speed), 20-day
  steps, bisection to 1 s;
* ``sign_window`` - entry and exit of a body in a sign (Ketu as Rahu's
  7th), bisection to 1 s;
* ``reaches_longitude`` - a body (or a pair) at a longitude (transit and return searches);
* ``cusps_by_reference`` - houses from another point (popup "reference
  longitude for finding houses"): the cusps at the moment, searching back from the chart time + 0.0035 day,
  when the lagna is at that point's longitude;
* the event spans that set the dasa span of an event chart (``dasa_systems.fitted_to_span``):
  ``retrograde_period``, ``event_period``, ``half_cycle_period``; ``varga_window`` the days since a body entered its part of a
  varga and until it leaves it;
* ``special_lagna`` / ``special_point`` - the user's two extra points (Settings);
* ``ecliptic_rise_set`` - ``semi_diameter`` (also the Panchanga's Sun and Moon rise and set): rising and setting
  by the ecliptic, the lagna reaching the body's longitude minus its apparent
  semi-diameter (plus 34' of refraction with SunriseDefinition 2).

Bodies are point indices: 0 Lagna, 1 Sun .. 9 Ketu.  Times are UT Julian days.
"""
from dataclasses import replace
from typing import Callable, Optional, Tuple

from . import ephemeris as E

NAMES = ("Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
SECOND = 1.1574074074074073e-05                  # one second, in days
LAGNA_TOL = 7.716049382716049e-07                # 0x3ea9e409340f4581


def body_longitude(p: int, cfg: Optional[E.EphemerisConfig] = None,
                   birth: Optional[E.BirthData] = None) -> Callable[[float], float]:
    """For one body: jd -> sidereal longitude (the lagna needs ``birth`` for the place)."""
    return E.longitude_func(NAMES[p], cfg, birth)


def _step(a: int, b: Optional[int], mid: bool, backward: bool) -> float:
    step = 1.0 / 12.0 if 0 in (a, b) else 3.0 if 2 in (a, b) else 10.0
    if mid:
        step *= 0.5
    return -step if backward else step


def _crossing(f: Callable[[float], float], jd: float, step: float, tol: float, stop: Optional[float] = None) -> float:
    """Step until f (in [0, 360)) wraps through 0 / 360 (below 120 <-> above 240), then narrow the bracket as
    it repeats until it is under ``tol``: the regula-falsi point x, a new bracket x + 1/1024 (then 1/16) of the
    way to each end when the wrap lies between them, else halve; the later end (the 1/1024 bracket closes within a
    few ms of the exact moment, as theirs does). A forward search with ``stop`` gives up past it and returns some
    moment later than ``stop``."""
    wrap = lambda u, v: (u > 240.0 and v < 120.0) or (u < 120.0 and v > 240.0)  # noqa: E731
    a, fa = jd, f(jd)
    for _ in range(100000):
        c, fc = a + step, f(a + step)
        if wrap(fa, fc):
            break
        a, fa = c, fc
        if stop is not None and a > stop:
            return a
    else:
        raise ValueError("no crossing found")     # e.g. a sign the lagna never reaches near a pole: the routes answer 422
    while abs(a - c) > tol and fa != fc:
        lo_x, hi_x, small, big = (a, c, fa, fc) if fa < fc else (c, a, fc, fa)
        # from lo_x, and 360 - big first: (small + 360) - big lost small's digits, and times a JD of ~2.4e6 that put x
        # seconds off, so every bracket failed into halving and the result came up to 1 s late (Vivekananda's angret)
        x = lo_x + (hi_x - lo_x) * small / (small + (360.0 - big))
        for k in (1024.0, 16.0):
            p, q = x + (a - x) / k, x + (c - x) / k
            fp = f(p)
            if not wrap(fa, fp):
                fq = f(q)
                if wrap(fp, fq):
                    a, fa, c, fc = p, fp, q, fq
                    break
        else:
            m = (a + c) * 0.5
            fm = f(m)
            if wrap(fm, fa):
                c, fc = m, fm
            else:
                a, fa = m, fm
    return max(a, c)


def longitude_event(jd: float, a: int, target: float, b: Optional[int] = None, mode: str = "diff",
                    backward: bool = False, cfg: Optional[E.EphemerisConfig] = None,
                    birth: Optional[E.BirthData] = None, stop: Optional[float] = None) -> float:
    """The first moment after (before) ``jd`` when lon(a) - target (``b``
    None), lon(a) - lon(b) - target ("diff"), lon(a) + lon(b) - target ("sum") or the midpoint of a and b minus
    the target ("mid") passes through 0. ``stop``: see ``_crossing``."""
    fa = body_longitude(a, cfg, birth)
    fb = body_longitude(b, cfg, birth) if b is not None else (lambda jd_: 0.0)
    if mode == "diff":
        f = lambda t: (fa(t) - fb(t) - target) % 360.0  # noqa: E731
    elif mode == "sum":
        f = lambda t: (fa(t) + fb(t) - target) % 360.0  # noqa: E731
    elif mode == "mid":
        f = lambda t: (((fa(t) - fb(t)) % 360.0) * 0.5 + fb(t) - target) % 360.0  # noqa: E731
    else:
        raise ValueError(mode)
    tol = LAGNA_TOL if 0 in (a, b) else SECOND
    return _crossing(f, jd, _step(a, b, mode == "mid", backward), tol, stop)


def sum_event(jd: float, a: int, b: int, target: float, backward: bool = False,
              cfg: Optional[E.EphemerisConfig] = None, birth: Optional[E.BirthData] = None) -> float:
    """The moment lon(a) + lon(b) reaches ``target`` (yoga end times: Sun + Moon)."""
    return longitude_event(jd, a, target, b, "sum", backward, cfg, birth)


def retrograde_station(jd: float, p: int, forward: bool = True,
                       cfg: Optional[E.EphemerisConfig] = None) -> Tuple[float, bool]:
    """The next (previous) change of retrograde state of body ``p`` after ``jd``, and the state after
    it (before it, searching back): 20-day steps, bisection to 1 s."""
    cfg = cfg or E.EphemerisConfig()
    retro = lambda t: E.planet_positions(t, cfg)[NAMES[p]]["speed"] < 0.0  # noqa: E731
    step = 20.0 if forward else -20.0
    lo, s0 = jd, retro(jd)
    hi = lo + step
    while retro(hi) == s0:
        lo, hi = hi, hi + step
    while abs(hi - lo) > SECOND:
        m = 0.5 * (lo + hi)
        if retro(m) == s0:
            lo = m
        else:
            hi = m
    return hi, not s0


def retrograde_period(jd: float, p: int, forward: bool = True,
                      cfg: Optional[E.EphemerisConfig] = None) -> Tuple[float, float]:
    """The next (previous) station of ``p`` (Ketu as Rahu) and the station after
    it; the chart moves to the first, the dasa spans the two."""
    p = 8 if p == 9 else p
    t1, _ = retrograde_station(jd, p, forward, cfg)
    return t1, retrograde_station(t1, p, True, cfg)[0]


def event_period(jd: float, a: int, target: float, b: Optional[int] = None, mode: str = "diff",
                 backward: bool = True, cfg: Optional[E.EphemerisConfig] = None,
                 birth: Optional[E.BirthData] = None) -> Tuple[float, float]:
    """The event (``longitude_event``) before (after) ``jd`` and its next recurrence, searched from
    0.0035 day after it."""
    t1 = longitude_event(jd, a, target, b, mode, backward, cfg, birth)
    return t1, longitude_event(t1 + 0.0035, a, target, b, mode, False, cfg, birth)


def half_cycle_period(jd: float, a: int, target: float, b: Optional[int] = None, mode: str = "diff",
                      backward: bool = True, cfg: Optional[E.EphemerisConfig] = None,
                      birth: Optional[E.BirthData] = None) -> Tuple[float, float]:
    """The nearer (in the search direction) of the events at ``target`` and ``target`` + 180, and
    the next event at the other one (e.g. new moon to full moon)."""
    opp = (target + 180.0) % 360.0
    ta = longitude_event(jd, a, target, b, mode, backward, cfg, birth)
    tb = longitude_event(jd, a, opp, b, mode, backward, cfg, birth)
    start, nxt = (tb, target) if (tb > ta if backward else tb < ta) else (ta, opp)
    return start, longitude_event(start + 0.0035, a, nxt, b, mode, False, cfg, birth)


def varga_window(jd: float, p: int, multiplier: int = 1, cfg: Optional[E.EphemerisConfig] = None,
                 birth: Optional[E.BirthData] = None) -> Tuple[float, float]:
    """(days since ``p`` entered its 30 / ``multiplier`` degree part, days until
    it leaves it): the later of the last moments at either end of the part, the earlier of the next (so a
    retrograde body is followed); Ketu as Rahu."""
    p = 8 if p == 9 else p
    span = 30.0 / multiplier
    lo = int(body_longitude(p, cfg, birth)(jd) * multiplier * 0.03333333333333333) * span
    ev = lambda lon, back: longitude_event(jd, p, lon % 360.0, None, "diff", back, cfg, birth)  # noqa: E731
    entry = max(ev(lo, True), ev(lo + span, True))
    exit_ = min(ev(lo + span, False), ev(lo, False))
    return jd - entry, exit_ - jd


def sign_window(jd: float, p: int, sign: Optional[int] = None, backward: bool = False,
                cfg: Optional[E.EphemerisConfig] = None, birth: Optional[E.BirthData] = None) -> Tuple[float, float]:
    """(entry, exit) of body ``p`` in ``sign`` (default: its sign at
    ``jd``), stepping 1/12 day (lagna), 3 (Moon) or 10 days from ``jd`` (back when ``backward``) to reach the
    sign, then bisection to 1 s for both ends."""
    f = body_longitude(p, cfg, birth)
    sg = lambda t: int(f(t) // 30.0) % 12  # noqa: E731
    if sign is None:
        sign = sg(jd)
    step = 1.0 / 12.0 if p == 0 else 3.0 if p == 2 else 10.0
    if backward:
        step = -step
    t = jd - SECOND
    while sg(t) != sign:
        t += step
    inside = t

    def edge(direction: float) -> float:
        out = inside + direction
        while sg(out) == sign:
            out += direction
        lo, hi = inside, out
        while abs(hi - lo) > SECOND:
            m = 0.5 * (lo + hi)
            if sg(m) == sign:
                lo = m
            else:
                hi = m
        return lo
    return edge(-abs(step)), edge(abs(step))


def reaches_longitude(jd: float, p: int, target: float, backward: bool = False, relative_to: Optional[int] = None,
                      sum_with: bool = False, cfg: Optional[E.EphemerisConfig] = None,
                      birth: Optional[E.BirthData] = None) -> float:
    """Body ``p`` at ``target`` (mode 1), or the difference (sum, mode
    2) of ``p`` and ``relative_to`` at it."""
    if relative_to is None:
        return longitude_event(jd, p, target, None, "diff", backward, cfg, birth)
    return longitude_event(jd, p, target, relative_to, "sum" if sum_with else "diff", backward, cfg, birth)


RADIUS_KM = (0.0, 695500.0, 1737.4, 3397.0, 2439.7, 71492.0, 6051.8, 60268.0)    # body radii, km (Sun .. Saturn)


def semi_diameter(p: int, dist_au: float, sunrise_definition: int = 0) -> float:
    """Apparent semi-diameter (deg): radius x 6.68e-9 AU/km / distance x 57.3; 0 for
    SunriseDefinition 0 and 3, + 0.5667 deg of refraction for 2."""
    if sunrise_definition in (0, 3) or p >= len(RADIUS_KM):
        return 0.0
    sd = RADIUS_KM[p] * 6.684578082767149e-09 / dist_au * 57.29577951308232
    return sd + 0.5666666666666667 if sunrise_definition == 2 else sd


def ecliptic_rise_set(jd: float, p: int, birth: E.BirthData, sunrise_definition: int = 0, backward: bool = False,
                      cfg: Optional[E.EphemerisConfig] = None) -> Tuple[float, float]:
    """(rise, set) of body ``p`` by the ecliptic: the lagna at lon(p) - sd, then at lon(p) + 180 + sd;
    sd from the body's distance at ``jd``."""
    cfg = cfg or E.EphemerisConfig()
    sd = semi_diameter(p, E.planet_positions(jd, cfg)[NAMES[p]]["dist"], sunrise_definition)
    rise = longitude_event(jd, 0, -sd, p, "diff", backward, cfg, birth)
    set_ = longitude_event(jd, 0, sd + 180.0, p, "diff", backward, cfg, birth)
    return rise, set_


def cusps_by_reference(birth: E.BirthData, ref_lon: float, system: str = "EQUAL",
                       cfg: Optional[E.EphemerisConfig] = None):
    """``ephemeris.house_cusps`` at the moment (back from birth + 0.0035 day)
    the lagna reaches ``ref_lon``."""
    jd = longitude_event(birth.jd_ut + 0.0035, 0, ref_lon, None, "diff", True, cfg, birth)
    return E.house_cusps(jd, birth.latitude, birth.longitude_east, system, cfg)


def special_lagna(birth: E.BirthData, planet: int = 1, speed: int = 5, nodes_reverse: bool = True,
                  sunrise_definition: int = 0, cfg: Optional[E.EphemerisConfig] = None) -> float:
    """The user's special lagna (a convention, docs/SOURCES.md section 5; INI SpecialLagnaPlanet /
    SpecialLagnaSpeedFactor / SpecialLagnaNodesReverse, defaults 1 / 5 / 1): ``planet``'s longitude
    at its last rise by the ecliptic, moving ``speed`` circles a day since (backwards for Rahu / Ketu)."""
    rise = ecliptic_rise_set(birth.jd_ut, planet, birth, sunrise_definition, True, cfg)[0]
    arc = (birth.jd_ut - rise) * speed * 360.0
    lon = body_longitude(planet, cfg, birth)(rise)
    return (lon - arc if nodes_reverse and planet in (8, 9) else lon + arc) % 360.0


def special_point(points, deg: float = 0.0, minutes: float = 0.0, seconds: float = 0.0, after: bool = True,
                  planet: Optional[int] = None, saham: Optional[float] = None, sign: Optional[int] = None,
                  midpoint: Optional[Tuple[int, int]] = None) -> float:
    """The user's special point (INI SpecialPointDeg/Min/Sec, SpecialPointBehindAfter, then the first
    of SpecialPointUsePlanet / UseSaham / UseRasi / UseMidPoint set): the offset (negated when behind) from the
    planet's longitude, a saham's, the start of a sign, or the midpoint of two points (``points`` by point
    index); with none of them, twice the offset.  Not reduced mod 360."""
    off = minutes * 0.016666666666666666 + seconds * 0.0002777777777777778 + deg
    if not after:
        off = -off
    if planet is not None:
        return points[planet] + off
    if saham is not None:
        return saham + off
    if sign is not None:
        return sign * 30.0 + off
    if midpoint is not None:
        a, b = points[midpoint[1]], points[midpoint[0]]
        return ((a - b) % 360.0 * 0.5 + b) % 360.0 + off
    return off + off


# ---------------------------------------------------------------- Mundane tab: calendar charts (SS 14: the measures of time)

def _tropical(cfg: Optional[E.EphemerisConfig]) -> E.EphemerisConfig:
    return replace(cfg or E.EphemerisConfig(), ayanamsa="TROPICAL")


def solar_year(jd: float, backward: bool = True, sign: int = 0, tropical: bool = False,
               cfg: Optional[E.EphemerisConfig] = None) -> float:
    """Solar New Year: the Sun's entry into ``sign`` (SolarYrSign), in tropical signs with
    ``tropical`` (SolarYrTrop), before (after) ``jd``."""
    return longitude_event(jd, 1, sign * 30.0, backward=backward, cfg=_tropical(cfg) if tropical else cfg)


def solar_month(jd: float, backward: bool = True, tropical: bool = False, cfg: Optional[E.EphemerisConfig] = None) -> float:
    """Solar New Month (SS 14.3): the Sun's last (next) entry into a sign."""
    c = _tropical(cfg) if tropical else cfg
    sign = int(E.planet_positions(jd, c)["Sun"]["lon"] // 30)
    return longitude_event(jd, 1, (sign if backward else sign + 1) * 30.0 % 360.0, backward=backward, cfg=c)


def lunar_year(jd: float, backward: bool = True, definition: int = 2, sign: int = 11,
               cfg: Optional[E.EphemerisConfig] = None) -> float:
    """Lunar New Year: ``definition`` LunarYrDef = 2 x month kind + tropical; kind
    0 Suklanta, 1 Amanta, 2 Solar. The Sun's entry into ``sign`` (LunarYrSign; before or after ``jd``), and for the
    lunar kinds the first Full or New Moon after it."""
    kind = definition // 2
    entry = longitude_event(jd, 1, sign * 30.0, backward=backward, cfg=_tropical(cfg) if definition & 1 else cfg)
    if kind == 2:
        return entry
    return longitude_event(entry, 2, 180.0 if kind == 0 else 0.0, 1, "diff", False, cfg)


def lunar_month(jd: float, backward: bool = True, definition: int = 2, cfg: Optional[E.EphemerisConfig] = None) -> float:
    """Lunar New Month (SS 14.12-13): the last (next) Full Moon (Suklanta), New Moon (Amanta), or the Sun's
    entry into a sign (Solar)."""
    kind = definition // 2
    if kind == 2:
        return solar_month(jd, backward, bool(definition & 1), cfg)
    return longitude_event(jd, 2, 180.0 if kind == 0 else 0.0, 1, "diff", backward, cfg)


def lunar_day(jd: float, backward: bool = True, cfg: Optional[E.EphemerisConfig] = None) -> float:
    """New Lunar Day (SS 2.66): the start (next start) of a tithi, Moon - Sun at a multiple of 12 degrees."""
    p = E.planet_positions(jd, cfg)
    i = int(((p["Moon"]["lon"] - p["Sun"]["lon"]) % 360.0) // 12.0)
    return longitude_event(jd, 2, (i if backward else i + 1) * 12.0 % 360.0, 1, "diff", backward, cfg)


def fortnight(jd: float, backward: bool = True, cfg: Optional[E.EphemerisConfig] = None) -> float:
    """Fortnight Chart: the nearer New or Full Moon in the search direction."""
    return half_cycle_period(jd, 2, 0.0, 1, "diff", backward, cfg)[0]
