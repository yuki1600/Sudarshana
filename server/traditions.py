"""The Traditions tab (web/src/Traditions.tsx): what the XALEN Ephemeris engine offers beyond Jyotish, through
native/traditions. The positions are the app's own, under the chosen ephemeris (NASA JPL's DE442) and the user's
position settings; XALEN's crates do the techniques. docs/SOURCES.md section 19 names each one's source.

Western: tropical places, houses (XALEN's 15 systems), aspects, patterns, dignities, the 97 lots, Sabian symbols,
midpoints and the 90-degree dial, declinations, antiscia, harmonics, fixed stars, the Uranian points, Hellenistic time
lords, secondary progressions, solar arc, and the solar and lunar returns (by the app's own root finder).
Chinese: BaZi, Zi Wei Dou Shu (on the lunar date, core_logic/chinese_calendar.py), Flying Stars, Ba Zhai, Qi Men Dun Jia.
World: Korean Saju, Nine Star Ki, Mahabote, the Tibetan year, the Mayan and Aztec calendars, the Egyptian decans, the
Celtic tree, the Persian Jarbakhtar. Then I Ching, numerology and Lal Kitab.
"""
from __future__ import annotations
import functools
import json
import math
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core_logic import ephemeris as E, time_search as TS
from core_logic.chinese_calendar import lunar_date
from . import service

try:
    import traditions as T
except ImportError:
    T = None

HOUSE_SYSTEMS = list(T.HOUSE_SYSTEMS) if T else []
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
WESTERN = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
CLASSICAL = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
YEAR = 365.2422


def _need() -> None:
    if T is None:
        raise E.EphemerisUnavailable("the Traditions tab needs its native module: run ./start.sh, which builds native/traditions "
                                     "(Rust, https://rustup.rs)")


def _local(b: E.BirthData) -> float:
    """The birth's local civil moment as a Julian day (the day pillar, the Mayan and Aztec days turn at local midnight)."""
    return b.jd_ut + b.tz_east_hours / 24.0


def _date(jd_ut: float, tz: float) -> str:
    y, m, d, h = E.jd_to_calendar(jd_ut + tz / 24.0)
    hh = int(h)
    return "%04d-%02d-%02dT%02d:%02d" % (y, m, d, hh, int((h - hh) * 60))


def _now_jd() -> float:
    n = datetime.now(timezone.utc)
    return E.julian_day_ut(n.year, n.month, n.day, n.hour + n.minute / 60.0 + n.second / 3600.0)


def _tropical(cfg: E.EphemerisConfig) -> E.EphemerisConfig:
    return replace(cfg, ayanamsa="TROPICAL", ayanamsa_offset_deg=0.0, siddhanta=0)


def _obliquity(jd_ut: float) -> float:
    s = E._require_swe()
    with E._SWE_LOCK:
        return s.calc_ut(jd_ut, s.ECL_NUT)[0][0]


def _declination(lon: float, lat: float, eps: float) -> float:
    l, b, e = math.radians(lon), math.radians(lat), math.radians(eps)
    return math.degrees(math.asin(math.sin(b) * math.cos(e) + math.cos(b) * math.sin(e) * math.sin(l)))


def _house_of(lon: float, cusps: List[float]) -> int:
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if (lon - a) % 360.0 < (b - a) % 360.0:
            return i + 1
    return 12


def _places(jd_ut: float, cfg: E.EphemerisConfig, b: E.BirthData) -> Dict[str, Dict[str, float]]:
    """The tropical places of the ten planets, the node (North Node), Chiron and Lilith."""
    pos = E.planet_positions(jd_ut, _tropical(cfg), b, include_outer=True)
    out = {n: {"lon": pos[n]["lon"], "lat": pos[n]["lat"], "speed": pos[n]["speed"]} for n in WESTERN}
    out["North Node"] = {"lon": pos["Rahu"]["lon"], "lat": 0.0, "speed": pos["Rahu"]["speed"]}
    s = E._require_swe()
    tt = jd_ut + s.deltat_ex(jd_ut, E._ephe_flag(s, jd_ut))
    extra = json.loads(T.extra_bodies(tt))
    later = json.loads(T.extra_bodies(tt + 1.0))
    for name in ("Chiron", "Lilith"):
        if extra[name] is not None:
            out[name] = {"lon": extra[name], "lat": 0.0, "speed": ((later[name] - extra[name] + 180.0) % 360.0) - 180.0}
    return out


def western(b: E.BirthData, cfg: E.EphemerisConfig, system: str = "placidus") -> Dict[str, Any]:
    _need()
    jd, now = b.jd_ut, _now_jd()
    eps = _obliquity(jd)
    h = json.loads(T.houses(jd, b.latitude, b.longitude_east, eps, system))
    places = _places(jd, cfg, b)
    age = max(0, int((now - jd) // YEAR))
    w = json.loads(T.western(json.dumps({
        "bodies": [{"name": n, **p} for n, p in places.items()], "asc": h["ascendant"], "mc": h["mc"], "obliquity": eps,
        "birth_jd": jd, "now_jd": now, "age": age})))
    bodies = [{"name": n, "lon": p["lon"], "speed": p["speed"], "retrograde": p["speed"] < 0, "house": _house_of(p["lon"], h["cusps"]),
               "declination": _declination(p["lon"], p["lat"], eps)} for n, p in places.items()]
    # secondary progressions to now, and the solar arc they give
    pjd = T.progressed_jd(jd, now)
    prog = _places(pjd, cfg, b)
    arc = json.loads(T.solar_arc(places["Sun"]["lon"], prog["Sun"]["lon"],
                                 json.dumps([[n, p["lon"]] for n, p in places.items()] + [["Asc", h["ascendant"]], ["MC", h["mc"]]])))
    # this year's solar return and the next lunar return, by the app's own root finder on DE442 (tropical)
    trop = _tropical(cfg)
    y = E.jd_to_calendar(now)[0]
    solar = TS.longitude_event(E.julian_day_ut(y, b.month, max(1, min(b.day, 28)), 0.0) - 5.0, 1, places["Sun"]["lon"], None, "diff", False, trop)
    lunar = TS.longitude_event(now, 2, places["Moon"]["lon"], None, "diff", False, trop)
    tz = b.tz_east_hours
    dated = lambda rows: [{**r, "start": _date(r["start_jd"], tz), "end": _date(r["end_jd"], tz)} for r in rows]  # noqa: E731
    hel = w["hellenistic"]
    for k in ("zr_spirit", "zr_fortune"):     # the major periods, and the sub periods of the one running now
        now_l1 = next((p for p in hel[k] if p["level"] == 1 and p["start_jd"] <= now < p["end_jd"]), None)
        hel[k] = dated([p for p in hel[k] if p["level"] == 1 or (now_l1 and now_l1["start_jd"] <= p["start_jd"] < now_l1["end_jd"])])
    hel["firdaria"] = dated(hel["firdaria"])
    w.pop("sabian", None)     # XALEN ships the Sabian symbols' degrees without their text
    w["cosmobiology"].pop("midpoints", None)     # the pictures are what the page shows; every midpoint is in "midpoints"
    hel["decennials"] = [{**d, "start": _date(d["start_jd"], tz), "end": _date(d["end_jd"], tz), "sub_periods": dated(d["sub_periods"])}
                         for d in hel["decennials"]]
    return {"system": system, "systems": HOUSE_SYSTEMS, "houses": h, "bodies": bodies, "age": age, "obliquity": eps, **w,
            "progressed": {"moment": _date(pjd, tz), "bodies": [{"name": n, "lon": p["lon"], "retrograde": p["speed"] < 0} for n, p in prog.items()]},
            "solar_arc": arc, "returns": {"solar": _date(solar, tz), "lunar": _date(lunar, tz)}}


def _solar_month(b: E.BirthData, cfg: E.EphemerisConfig) -> tuple:
    """The BaZi solar year and month (1 = the Yin month from Li Chun, the apparent Sun at 315 degrees) of the birth."""
    sun = E.planet_positions(b.jd_ut, replace(_tropical(cfg), true_positions=False, no_nutation=False, topocentric=False), b)["Sun"]["lon"]
    month = int(((sun - 315.0) % 360.0) // 30.0) + 1
    year = b.year - (1 if b.month <= 2 and month >= 11 else 0)
    return year, month, sun


def chinese(b: E.BirthData, cfg: E.EphemerisConfig, male: bool) -> Dict[str, Any]:
    _need()
    year, month, _sun = _solar_month(b, cfg)
    local = _local(b)
    ld = lunar_date(math.floor(local + 0.5), cfg)
    hour = b.hour_local % 24.0
    out = json.loads(T.chinese(year, month, local, hour, ld["year"], ld["month"], ld["day"], male, b.year, b.month, b.day))
    out["lunar_date"] = ld
    out["solar_month"] = month
    return out


def _sidereal_houses(b: E.BirthData, cfg: E.EphemerisConfig) -> Dict[str, int]:
    """Each graha's house counted from the lagna's sign (Lal Kitab's chart, the lagna always the first house)."""
    pos = E.planet_positions(b.jd_ut, cfg, b)
    lagna = int(E.lagna_at(b.jd_ut, b, cfg) // 30)
    return {n: (int(pos[n]["lon"] // 30) - lagna) % 12 + 1 for n in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")}


def world(b: E.BirthData, cfg: E.EphemerisConfig, male: bool) -> Dict[str, Any]:
    _need()
    w = western(b, cfg)
    sun = next(x["lon"] for x in w["bodies"] if x["name"] == "Sun")
    almuten = max(w["dignities"], key=lambda d: d["score"])["body"]
    birth_year = b.year + (b.jd_ut - E.julian_day_ut(b.year, 1, 1, 0.0)) / YEAR
    local = _local(b)
    out = json.loads(T.world(b.year, b.month, b.day, int(b.hour_local % 24), local, male, sun, w["houses"]["ascendant"], birth_year, almuten))
    out["sun"], out["asc"] = sun, w["houses"]["ascendant"]
    return out


def iching(b: E.BirthData) -> Dict[str, Any]:
    _need()
    return json.loads(T.iching(b.year, b.month, b.day, int(b.hour_local % 24)))


def numerology(b: E.BirthData, name: str, chaldean: bool) -> Dict[str, Any]:
    _need()
    year = E.jd_to_calendar(_now_jd())[0]
    out = json.loads(T.numerology(name, b.year, b.month, b.day, chaldean, year))
    out["name"], out["system"], out["year"] = name, "chaldean" if chaldean else "pythagorean", year
    return out


def lalkitab(b: E.BirthData, cfg: E.EphemerisConfig) -> Dict[str, Any]:
    _need()
    age = max(0, int((_now_jd() - b.jd_ut) // YEAR))
    houses = _sidereal_houses(b, cfg)
    out = json.loads(T.lalkitab(json.dumps(houses), age + 1))
    out["age"] = age
    return out


PARTS = ("western", "chinese", "world", "iching", "numerology", "lalkitab")


@functools.lru_cache(maxsize=64)
def _part(part: str, birth_json: str, settings_json: str, system: str, male: bool, person: str, chaldean: bool) -> Dict[str, Any]:
    b, cfg, _ch, _s = service._raw(birth_json, settings_json)
    if part == "western":
        if system not in HOUSE_SYSTEMS:
            raise ValueError("unknown house system %r" % system)
        return western(b, cfg, system)
    if part == "chinese":
        return chinese(b, cfg, male)
    if part == "world":
        return world(b, cfg, male)
    if part == "iching":
        return iching(b)
    if part == "numerology":
        return numerology(b, person, chaldean)
    return lalkitab(b, cfg)


def compute(part: str, birth, settings, system: str = "placidus", male: bool = True, person: str = "", chaldean: bool = False) -> Dict[str, Any]:
    """One sub tab's data for the request's chart and settings (cached by the request, as service's views are)."""
    _need()
    return _part(part, *service._key(birth, settings), system, male, person, chaldean)


def available() -> Optional[str]:
    """None when the tab can calculate; else what is missing."""
    return None if T else "native/traditions is not built (./start.sh builds it with Rust)"
