"""positions: part of ephemeris (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Any, Dict, Optional
from ..utils import norm360
from .moments import BirthData
from .config import CLASSICAL_PLANETS, EphemerisConfig, PLANET_IDS, _SSY_PLANE, _SWE_LOCK, _ayanamsa_spec, _calc_flags, _delta_t, _computed, _plane_shift, _sss_chart, ayanamsa_value
from .jpl import engine

# ---------------------------------------------------------------------------
# Planet positions
# ---------------------------------------------------------------------------


def _apparent_ecliptic(s, jd_ut: float, lon: float, lat: float, dist: float, birth: BirthData):
    """Refraction for apparent positions (ApparentRefraction on, TruePositions off): ecliptic to horizon, swe_refrac
    (true altitude to apparent), back to the ecliptic (Swiss Ephemeris swe_azalt / swe_refrac)."""
    geo = (birth.longitude_east, birth.latitude, birth.altitude_m)
    az, true_alt, _app = s.azalt(jd_ut, s.ECL2HOR, geo, birth.pressure_hpa, birth.temperature_c, (lon, lat, dist))
    alt = s.refrac(true_alt, birth.pressure_hpa, birth.temperature_c, s.TRUE_TO_APP)
    return s.azalt_rev(jd_ut, s.HOR2ECL, geo, az, alt)


def planet_positions(
    jd_ut: float,
    cfg: Optional[EphemerisConfig] = None,
    birth: Optional[BirthData] = None,
    include_outer: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """
    Sidereal positions of the 7 grahas + Rahu/Ketu (+ Uranus/Neptune/Pluto when asked).

    Returns {name: {lon, lat, speed, retrograde, sign_index, deg_in_sign, dist (AU)}}.
    Sidereal longitude = tropical longitude - ayanamsa(jd).
    """
    cfg = cfg or EphemerisConfig()
    with _SWE_LOCK:
        return _planet_positions(jd_ut, cfg, birth, include_outer)


def _planet_positions(jd_ut, cfg, birth, include_outer):
    if cfg.siddhanta == 1:
        return _sss_positions(jd_ut, cfg, birth)
    s = engine(cfg)   # swisseph, or its calc_ut from the JPL kernel (Settings > Ephemeris)
    if cfg.topocentric:
        if birth is None:
            raise ValueError("topocentric positions need birth (lon/lat/altitude)")
        s.set_topo(birth.longitude_east, birth.latitude, birth.altitude_m)
    flags = _calc_flags(cfg, jd_ut)
    spec = _ayanamsa_spec(cfg)
    if not _computed(spec):
        # sidereal mode: mean equinox, like the ayanamsa it is reduced by; the true-equinox ayanamsas
        # (_computed: Chandra Hari, SSS) take true-equinox positions
        flags |= s.FLG_NONUT
    lon_east = birth.longitude_east if birth is not None else None
    if spec["kind"] == "star_plane":   # sidereal positions on the invariable plane, shifted by the star
        ay = -_plane_shift(s, jd_ut, cfg, spec)
        ay_rate = _plane_shift(s, jd_ut - 0.5, cfg, spec) - _plane_shift(s, jd_ut + 0.5, cfg, spec)
        s.set_sid_mode(_SSY_PLANE, 0, 0)
        flags = (flags & ~s.FLG_NONUT) | s.FLG_SIDEREAL
    else:
        ay = ayanamsa_value(jd_ut, cfg, lon_east)
        ay_rate = ayanamsa_value(jd_ut + 0.5, cfg, lon_east) - ayanamsa_value(jd_ut - 0.5, cfg, lon_east)  # deg/day

    def pack(lon_trop: float, lat: float, speed_trop: float, dist: float = 0.0, lat_speed: float = 0.0, dist_speed: float = 0.0) -> Dict[str, Any]:
        lon = norm360(lon_trop - ay)
        speed = speed_trop - ay_rate
        return {
            "lon": lon, "lat": lat, "speed": speed, "retrograde": speed < 0,
            "sign_index": int(lon // 30), "deg_in_sign": lon % 30.0, "dist": dist, "lat_speed": lat_speed, "dist_speed": dist_speed,
        }

    out: Dict[str, Dict[str, Any]] = {}
    names = list(CLASSICAL_PLANETS) + (["Uranus", "Neptune", "Pluto"] if include_outer else [])
    node_id = s.MEAN_NODE if cfg.nodes == "mean" else s.TRUE_NODE
    with _delta_t(s, jd_ut, cfg):
        raw = {name: s.calc_ut(jd_ut, PLANET_IDS[name], flags)[0] for name in names}
        xx = s.calc_ut(jd_ut, node_id, flags)[0]
    if cfg.apparent_refraction and not cfg.true_positions and spec["kind"] != "star_plane":
        if birth is None:
            raise ValueError("ApparentRefraction needs the birth place")

        def refr(row):
            # the sidereal longitude goes to swe_azalt as if it were the ecliptic of date
            lon, lat = _apparent_ecliptic(s, jd_ut, row[0] - ay, row[1], row[2], birth)
            return (lon + ay, lat, row[2], row[3], row[4], row[5])

        raw = {name: refr(row) for name, row in raw.items()}
        xx = refr(xx)
    for name in names:
        out[name] = pack(raw[name][0], raw[name][1], raw[name][3], raw[name][2], raw[name][4], raw[name][5])
    rahu = pack(xx[0], xx[1], xx[3], xx[2], xx[4], xx[5])
    out["Rahu"] = rahu
    ketu = pack(xx[0] + 180.0, -xx[1], xx[3], xx[2], -xx[4], xx[5])
    out["Ketu"] = ketu
    return out


def _sss_positions(jd_ut, cfg, birth):
    """SSS mode: longitudes from surya_siddhanta (no latitude / distance); speed by a one-day difference, the retrograde
    flag is the model's own (sighra anomaly range, SS 2.51-55; never for the nodes)."""
    lon_east = birth.longitude_east if birth is not None else None
    lat = birth.latitude if birth is not None else None
    now = _sss_chart(jd_ut, cfg, lon_east, lat)["positions"]
    nxt = _sss_chart(jd_ut + 0.5, cfg, lon_east, lat)["positions"]
    prv = _sss_chart(jd_ut - 0.5, cfg, lon_east, lat)["positions"]
    out = {}
    for name, (lon, retro) in now.items():
        speed = (nxt[name][0] - prv[name][0] + 180.0) % 360.0 - 180.0
        out[name] = {"lon": lon, "lat": 0.0, "speed": speed, "retrograde": retro, "sign_index": int(lon // 30),
                     "deg_in_sign": lon % 30.0, "dist": 0.0, "lat_speed": 0.0, "dist_speed": 0.0}
    return out
