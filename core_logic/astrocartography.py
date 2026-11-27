"""
core_logic/astrocartography.py
==============================
Where a sidereal longitude sits on the angles across the Earth at one moment.  Sudarshana's own feature.

Zodiacal: a point's ecliptic latitude is ignored, as the charts ignore it, so on a curve from ``lagna_curve`` the
relocated chart's Lagna is exactly that longitude.  A true horizon crossing of the Moon can lie a degree of longitude away.
"""
import math
from typing import List, NamedTuple, Optional, Sequence

from . import ephemeris as E

Curve = List[List[float]]    # [longitude east, latitude] from south to north; east of 180 is not wrapped, the map repeats it


class Frame(NamedTuple):
    ayanamsa: float
    obliquity: float         # true, degrees
    greenwich_armc: float    # degrees


def frame(jd_ut: float, cfg: Optional[E.EphemerisConfig] = None) -> Frame:
    s = E._require_swe()
    with E._SWE_LOCK:
        obliquity = s.calc_ut(jd_ut, s.ECL_NUT)[0][0]
    return Frame(E.ayanamsa_value(jd_ut, cfg), obliquity, E.house_cusps(jd_ut, 0.0, 0.0, "RASI", cfg)["armc"])


def _equatorial(sid_lon: float, f: Frame):
    """Right ascension in degrees, declination in radians."""
    lon, eps = math.radians(sid_lon + f.ayanamsa), math.radians(f.obliquity)
    return math.degrees(math.atan2(math.sin(lon) * math.cos(eps), math.cos(lon))), math.asin(math.sin(eps) * math.sin(lon))


def _wrap(lon: float) -> float:
    return (lon + 180.0) % 360.0 - 180.0


def meridian_lon(sid_lon: float, f: Frame) -> float:
    """The longitude where ``sid_lon`` is on the MC; the IC is the same at ``sid_lon + 180``."""
    return _wrap(_equatorial(sid_lon, f)[0] - f.greenwich_armc)


def ecliptic_poles(f: Frame) -> List[List[float]]:
    """The places with the north and the south ecliptic pole overhead: there the ecliptic is the horizon, so every Lagna curve's circle passes through them."""
    return [[_wrap(270.0 - f.greenwich_armc), 90.0 - f.obliquity], [_wrap(90.0 - f.greenwich_armc), f.obliquity - 90.0]]


def lagna_curve(sid_lon: float, f: Frame, step: int = 2) -> Curve:
    """Where the Lagna is ``sid_lon``, the rising half of its horizon circle, a row every ``step`` degrees along it; the 7th is the same at ``sid_lon + 180``.
    It ends where the point only grazes the horizon, at latitude 90 - |declination|, and the setting half goes on from there."""
    ra, dec = _equatorial(sid_lon, f)
    equator = _wrap(ra - f.greenwich_armc - 90.0)    # that row stays inside the map
    curve = []
    for t in range(-90, 91, step):
        a = math.radians(t)
        hour_angle = math.degrees(math.atan2(-math.cos(a), -math.sin(a) * math.sin(dec)))    # -180 to 0: east of the meridian, so rising
        curve.append([equator + 90.0 + hour_angle, math.degrees(math.asin(math.sin(a) * math.cos(dec)))])
    return curve


def bands(sid_lons: Sequence[float], f: Frame, step: int = 2) -> List[Curve]:
    """The Lagna curves of ascending longitudes, each east of the one before at the equator, closed by the first again at +360: band i lies between curves i and i + 1."""
    out: List[Curve] = []
    for sid_lon in [*sid_lons, sid_lons[0]]:
        c = lagna_curve(sid_lon, f, step)
        if out:
            mid = len(c) // 2
            shift = out[-1][mid][0] + (c[mid][0] - out[-1][mid][0]) % 360.0 - c[mid][0]
            c = [[lon + shift, lat] for lon, lat in c]
        out.append(c)
    return out


def band_areas(sid_lons: Sequence[float], f: Frame, curves: List[Curve]) -> List[Curve]:
    """Each band's outline: its two curves, joined along the ends of the curves between them.  Curves cross at the ecliptic poles, so near a pole a band is a bow tie:
    past the crossing it holds what the opposite band would, as the Lagna flips there.  ``curves`` are those of ``bands``."""
    out = []
    for i, sid_lon in enumerate(sid_lons):
        span = (sid_lons[(i + 1) % len(sid_lons)] - sid_lon) % 360.0
        n = math.ceil(span / 3.0)
        rows = bands([sid_lon + span * k / n for k in range(n + 1)], f, 90)[:-1]    # south end, equator, north end
        shift = curves[i][0][0] - rows[0][0][0]
        south, north = ([[r[j][0] + shift, r[j][1]] for r in rows[1:-1]] for j in (0, 2))
        out.append([*curves[i], *north, *curves[i + 1][::-1], *south[::-1]])
    return out


def crossings(bhavas_at, lon: float, step: float = 2.0, iters: int = 30):
    """As ``x`` goes once round from 0, where ``lon`` enters another bhava, as (x, that bhava from 1), and where it is on a bhava's middle, as (x, that bhava).
    ``bhavas_at(x)`` gives the (start, middle, end) of the 12; ``lon`` must stay in each bhava for more than ``step``."""
    from .house_systems import house_of

    def at(x):
        bh = bhavas_at(x % 360.0)
        h = house_of(lon, bh)
        return h, _wrap(lon - bh[h][1]) >= 0.0

    def edge(lo, hi, same):     # bisected from the low end: the first x that is like ``hi``
        for _ in range(iters):
            mid = lo + (hi - lo) * 0.5
            lo, hi = (lo, mid) if same(at(mid)) else (mid, hi)
        return hi % 360.0

    borders, middles = [], []
    x, s = 0.0, at(0.0)
    while x < 360.0:
        y = x + step
        t = at(y)
        if t[0] != s[0]:
            borders.append((edge(x, y, lambda u: u[0] == t[0]), t[0] + 1))
        elif t[1] != s[1]:
            middles.append((edge(x, y, lambda u: u[1] == t[1]), t[0] + 1))
        x, s = y, t
    return borders, middles


def armc_curves(bhavas_at, lon: float, f: Frame, lats=range(-64, 65, 2)):
    """Where ``lon`` enters each bhava, and where it is on each bhava's middle, when the houses depend on the latitude and not on the Lagna alone (a quadrant system):
    {bhava: curve} each, south to north, a row every latitude of ``lats``, short of the polar circles where those houses fail. ``bhavas_at(armc, lat)`` gives the 12."""
    borders, middles = {}, {}
    for lat in lats:
        b, m = crossings(lambda a: bhavas_at(a, lat), lon)
        for found, out in ((b, borders), (m, middles)):
            for armc, h in found:
                x = armc - f.greenwich_armc
                row = out.setdefault(h, [])
                row.append([row[-1][0] + _wrap(x - row[-1][0]) if row else _wrap(x), float(lat)])
    return borders, middles


def ordered(curves: List[Curve]) -> List[Curve]:
    """Curves each moved by whole turns to lie east of the one before at the middle row, closed by the first again a turn on, as ``bands`` gives them."""
    out: List[Curve] = []
    for c in curves:
        if out:
            mid = len(c) // 2
            shift = out[-1][mid][0] + (c[mid][0] - out[-1][mid][0]) % 360.0 - c[mid][0]
            c = [[x + shift, lat] for x, lat in c]
        out.append(c)
    return [*out, [[x + 360.0, lat] for x, lat in out[0]]]
