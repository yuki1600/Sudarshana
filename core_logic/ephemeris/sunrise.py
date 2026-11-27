"""sunrise: part of ephemeris (split from one module; see __init__.py)."""
from __future__ import annotations
from dataclasses import replace
from typing import Any, Callable, Dict, Optional
from .moments import BirthData, jd_to_calendar, julian_day_ut
from .config import _SWE_LOCK, EphemerisConfig, _calc_flags, _delta_t, _ephe_flag, _require_swe
from .houses import house_cusps
from .jpl import engine
from .positions import planet_positions

# ---------------------------------------------------------------------------
# Sunrise / sunset
# ---------------------------------------------------------------------------
def sunrise_sunset(birth: BirthData, cfg: Optional[EphemerisConfig] = None) -> Dict[str, float]:
    """
    Sunrise/sunset of the local civil day, as decimal local hours (the inputs several
    modules take: ``sunrise_hours``, ``sunset_hours``).

    ``cfg.sunrise_definition`` (Settings > Sunrise is when):
      0 centre of disc, true horizon   1 tip of disc, true horizon
      2 tip of disc, apparent horizon  3 centre of disc, apparent horizon
    0 is the Surya Siddhanta's sunrise (SS 2.60-63: the Sun's centre on the horizon, no refraction).

    Swiss mode also returns the next upper meridian transit (local noon, swe_rise_trans flag 4) and lower
    one (flag 8) after local midnight. The SSS model computes sunrise and sunset only.
    """
    cfg = cfg or EphemerisConfig()
    if cfg.siddhanta == 1:
        return _sss_sunrise_sunset(birth, cfg)
    s = engine(cfg)     # swe_rise_trans is the Swiss Ephemeris' either way; the Sun's place it checks is the chosen ephemeris'
    with _SWE_LOCK:     # Delta-T and set_topo are process-wide on macOS: planet_positions holds the same lock
        d = cfg.sunrise_definition
        bits = 0
        if d in (0, 3):
            bits |= s.BIT_DISC_CENTER
        if d in (0, 1):
            bits |= s.BIT_NO_REFRACTION
        local_midnight_ut = julian_day_ut(birth.year, birth.month, birth.day, 0.0 - birth.tz_east_hours, birth.gregorian)
        geo = (birth.longitude_east, birth.latitude, birth.altitude_m)
        res = {}
        for label, rs in (("sunrise", s.CALC_RISE), ("sunset", s.CALC_SET),
                          ("upper_transit", s.CALC_MTRANSIT), ("lower_transit", s.CALC_ITRANSIT)):
            start = res.get("sunrise_jd", local_midnight_ut)   # set and transits are searched from the sunrise
            with _delta_t(s, start, cfg):
                ret, tret = s.rise_trans(start, s.SUN, rs | bits, geo, birth.pressure_hpa, birth.temperature_c,
                                         _ephe_flag(s, start))
                if ret != 0:
                    # the texts assume the Sun rises and sets, so this is our own rule (docs/SOURCES.md section 1.3):
                    # under the midnight Sun the day runs from lower transit to lower transit; in the polar night it
                    # has no length, at the upper transit
                    jd = _polar_day_edge(s, start, geo, label, cfg)
                    res[label + "_jd"] = jd
                    res[label + "_hours"] = (jd - local_midnight_ut) * 24.0
                    continue
                jd = _sun_altitude_flags_step(s, tret[0], geo, cfg)
            res[label + "_jd"] = jd
            res[label + "_hours"] = (jd - local_midnight_ut) * 24.0
        return {"sunrise_hours": res["sunrise_hours"], "sunset_hours": res["sunset_hours"],
                "sunrise_jd": res["sunrise_jd"], "sunset_jd": res["sunset_jd"],
                "upper_transit_hours": res["upper_transit_hours"], "lower_transit_hours": res["lower_transit_hours"],
                "upper_transit_jd": res["upper_transit_jd"], "lower_transit_jd": res["lower_transit_jd"]}


# SSS mode: the horizon depression by SunriseDefinition (semi-diameter, and refraction for the apparent horizon)
_SSS_DEPRESSION = {0: 0.0, 1: 0.2680986783777464, 2: 0.834765345044413, 3: 0.0}


def _polar_day_edge(s, start: float, geo, label: str, cfg: EphemerisConfig) -> float:
    """Sunrise or sunset where the Sun does not cross the horizon (see ``sunrise_sunset``)."""
    noon = s.rise_trans(start, s.SUN, s.CALC_MTRANSIT, geo, 0.0, 0.0, _ephe_flag(s, start))[1][0]
    lon, lat, dist = s.calc_ut(noon, s.SUN, _ephe_flag(s, noon))[0][:3]
    midnight_sun = s.azalt(noon, s.ECL2HOR, geo, 0.0, 0.0, (lon, lat, dist))[1] > 0.0
    if not midnight_sun:
        return start if label == "sunset" else noon     # the sunset search starts from the sunrise found
    low = s.rise_trans(start - 1.0, s.SUN, s.CALC_ITRANSIT, geo, 0.0, 0.0, _ephe_flag(s, start))[1][0]
    return low if label == "sunrise" else low + 1.0


def _sss_sunrise_sunset(birth: BirthData, cfg: EphemerisConfig) -> Dict[str, float]:
    """SSS mode: no swe_rise_trans; the moment the SSS lagna reaches the Sun's longitude less the depression (the
    Sun on the horizon, SS 3.46-49), searched back from the end of the civil day (the contract of
    ``sunrise_sunset``), then forward to the lagna at Sun + 180 + depression (sunset)."""
    from .. import time_search
    dep = _SSS_DEPRESSION.get(cfg.sunrise_definition, 0.834765345044413)
    local_midnight_ut = julian_day_ut(birth.year, birth.month, birth.day, 0.0 - birth.tz_east_hours, birth.gregorian)
    rise = time_search.longitude_event(local_midnight_ut + 1.0, 0, -dep, 1, "diff", True, cfg, birth)
    sset = time_search.longitude_event(rise, 0, 180.0 + dep, 1, "diff", False, cfg, birth)
    return {"sunrise_hours": (rise - local_midnight_ut) * 24.0, "sunset_hours": (sset - local_midnight_ut) * 24.0,
            "sunrise_jd": rise, "sunset_jd": sset}


def _sun_altitude_flags_step(s, jd: float, geo, cfg: EphemerisConfig) -> float:
    """With swisseph_202: the position flags (TRUEPOS ...) reach swe_rise_trans, which Swiss Ephemeris 2.02 honours
    and 2.10 ignores (apparent Sun, ~1.5 s earlier at sunrise). Move the event to where the Sun computed with the
    configured flags has the altitude the apparent Sun had."""
    eph = _ephe_flag(s, jd)
    flags = (_calc_flags(cfg, jd) & ~s.FLG_SPEED) | s.FLG_EQUATORIAL | s.FLG_TOPOCTR
    if not cfg.swisseph_202 or flags == eph | s.FLG_EQUATORIAL | s.FLG_TOPOCTR:
        return jd  # apparent positions: rise_trans already used them
    s.set_topo(*geo)

    def alt(t, f):
        xx = s.calc_ut(t, s.SUN, f)[0]
        return s.azalt(t, s.EQU2HOR, geo, 0, 0, (xx[0], xx[1], xx[2]))[1]

    target = alt(jd, eph | s.FLG_EQUATORIAL | s.FLG_TOPOCTR)
    dt = 1.0 / 86400.0
    for _ in range(2):
        a = alt(jd, flags)
        rate = (alt(jd + dt, flags) - a) / dt
        jd -= (a - target) / rate
    return jd


def lagna_at(jd_ut: float, birth: BirthData, cfg: Optional[EphemerisConfig] = None) -> float:
    """Sidereal ascendant at ``jd_ut`` for the birth place."""
    return house_cusps(jd_ut, birth.latitude, birth.longitude_east, "RASI", cfg)["ascendant"]


def longitude_func(body: str, cfg: Optional[EphemerisConfig] = None,
                   birth: Optional[BirthData] = None) -> Callable[[float], float]:
    """jd_ut -> sidereal longitude of ``body`` (a graha, Rahu/Ketu, or "Lagna" with ``birth``).

    This is the ``*_lon_func`` callback the root solvers in mundane, tithi_pravesha and
    miscellany expect."""
    cfg = cfg or EphemerisConfig()
    if body == "Lagna":
        if birth is None:
            raise ValueError("the lagna needs a place (birth)")
        return lambda jd: lagna_at(jd, birth, cfg)
    return lambda jd: planet_positions(jd, cfg, birth)[body]["lon"]


def _local_jd(birth: BirthData, hour_local: float) -> float:
    return julian_day_ut(birth.year, birth.month, birth.day, hour_local - birth.tz_east_hours, birth.gregorian)


def _shifted_day(birth: BirthData, days: int) -> BirthData:
    y, m, d, _ = jd_to_calendar(_local_jd(birth, 12.0) + days, birth.gregorian)
    return replace(birth, year=y, month=m, day=d)


def day_night_span(birth: BirthData, cfg: Optional[EphemerisConfig] = None,
                   lmt_6am: bool = False) -> Dict[str, Any]:
    """
    The day (sunrise..sunset) or night (sunset..next sunrise) containing the birth moment, in
    local hours of the birth date (a night that began the evening before starts below 0).
    ``weekday`` is the Vedic weekday (it changes at sunrise), 0 = Sunday.
    ``lmt_6am``: use 6 am / 6 pm local mean time instead of sunrise/sunset (UpagrahaDayDefinition).
    """
    if lmt_6am:
        lmt_minus_zone = birth.longitude_east / 15.0 - birth.tz_east_hours

        def rise_set(k):
            return 6.0 - lmt_minus_zone + 24.0 * k, 18.0 - lmt_minus_zone + 24.0 * k
    else:
        def rise_set(k):
            sun = sunrise_sunset(_shifted_day(birth, k), cfg)
            return sun["sunrise_hours"] + 24.0 * k, sun["sunset_hours"] + 24.0 * k
    s = _require_swe((cfg or EphemerisConfig()).ephe_path)
    civil_weekday = (s.day_of_week(_local_jd(birth, 12.0)) + 1) % 7      # swe: Monday = 0
    t = birth.hour_local
    rise0, set0 = rise_set(0)
    if t < rise0:
        start, end, night, weekday = rise_set(-1)[1], rise0, True, (civil_weekday - 1) % 7
        sunrise = rise_set(-1)[0]
    elif t < set0:
        start, end, night, weekday, sunrise = rise0, set0, False, civil_weekday, rise0
    else:
        start, end, night, weekday, sunrise = set0, rise_set(1)[0], True, civil_weekday, rise0
    return {"start_hours": start, "end_hours": end, "is_night": night, "weekday": weekday,
            "vedic_sunrise_hours": sunrise}
