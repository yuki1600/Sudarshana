"""day: part of ephemeris (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Any, Dict, Optional
from ..utils import norm360
from .moments import BirthData
from .config import EphemerisConfig, _require_swe
from .sunrise import _local_jd, _shifted_day, day_night_span, sunrise_sunset
from .positions import planet_positions

# The Kaala lords (docs/SOURCES.md section 1.3); planets 1 = Sun .. 7 = Saturn, 8 = Rahu. Day and night each in 8 parts
# (BPHS 3.66-69), the lords in the Tamil jama order, the order that puts Rahu's part on each weekday's Rahu kala;
# the day's parts start from the weekday lord, the night's from the 5th in the order (as BPHS 3.66-69 starts the night
# from a 5th lord)
_KAALA_ORDER = [1, 3, 5, 4, 6, 7, 2, 8]            # Sun Mars Jupiter Mercury Venus Saturn Moon Rahu
_KAALA_START_DAY = [_KAALA_ORDER.index(weekday + 1) for weekday in range(7)]    # by weekday, 0 = Sunday: its lord
_KAALA_START_NIGHT = [(k + 4) % 8 for k in _KAALA_START_DAY]                      # the 5th from it
# by hora lord: the first 5-minute sign of a day / night hora (a display convention; docs/SOURCES.md section 1.3)
_HORA_SIGN_NIGHT = [0, 3, 3, 0, 2, 8, 1, 9]
_HORA_SIGN_DAY = [0, 4, 4, 7, 5, 11, 6, 10]


def day_lords(birth: BirthData, cfg: Optional[EphemerisConfig] = None, kaala_day_night_separate: bool = True,
              weekday_definition: int = 0, mahakala_definition: int = 1) -> Dict[str, Any]:
    """
    Vedic weekday, hora lord, its 5-minute sign and the Kaala lord under three day definitions: "sunrise" (sunrise
    to sunrise, BPHS 27.13), "lmt" (6 am to 6 am local mean time), "clock" (6 am to 6 am zone time). A hora is 1/24
    of the full day, its lord the 6th weekday lord from the previous one (BPHS 27.13, SS 12.78-79); Kaala parts are
    eighths of the day and of the night (``kaala_day_night_separate``, INI KaalaInDayNightSeparate=1) or
    sixteenths of the full day. ``weekday_definition`` (INI WeekdayDefinition, 0 = sunrise, else lmt) picks the
    reported set, ``mahakala_definition`` (INI WeekdayDefinitionKaala, 2 = clock, else lmt) the "Mahakala" hora.
    Lords are 1 = Sun .. 7 = Saturn, 8 = Rahu; signs 0 = Aries. ``janma_ghatis`` = ghatis since sunrise.
    """
    cfg = cfg or EphemerisConfig()
    s = _require_swe(cfg.ephe_path)
    t = birth.jd_ut
    span = day_night_span(birth, cfg)
    k = -1 if span["vedic_sunrise_hours"] < 0 else 0
    sun0, sun1 = sunrise_sunset(_shifted_day(birth, k), cfg), sunrise_sunset(_shifted_day(birth, k + 1), cfg)
    bounds = {"sunrise": (sun0["sunrise_jd"], sun0["sunset_jd"], sun1["sunrise_jd"])}
    for key, hour in (("lmt", 6.0 - birth.longitude_east / 15.0 + birth.tz_east_hours), ("clock", 6.0)):
        start = _local_jd(birth, hour) - (1.0 if birth.hour_local < hour else 0.0)
        bounds[key] = (start, start + 0.5, start + 1.0)
    civil = (s.day_of_week(_local_jd(birth, 12.0)) + 1) % 7      # swe: Monday = 0
    is_day_a = bounds["sunrise"][1] > t
    out = {}
    for key, (start, mid, end) in bounds.items():
        is_day = mid > t
        weekday = (civil - 1) % 7 if (birth.hour_local < 12.0 and not is_day) else civil
        x = (t - start) * 24.0 / (end - start)
        hora = int(x)
        if hora >= 24:
            hora, weekday = hora - 24, (weekday + 1) % 7
        hora_lord = (hora * 5 + weekday) % 7 + 1
        sign = ((_HORA_SIGN_DAY if is_day else _HORA_SIGN_NIGHT)[hora_lord] + int((x - hora) * 12.0)) % 12
        out[key] = {"weekday": weekday, "is_day": is_day, "hora": hora, "hora_lord": hora_lord,
                    "hora_5min_sign": sign}
    for key, (start, mid, end) in bounds.items():
        if kaala_day_night_separate:
            # day or night is taken from the sunrise definition for all three (and in daytime the clock
            # definition takes the sunrise definition's part)
            src = "sunrise" if (key == "clock" and is_day_a) else key
            s0, m0, e0 = bounds[src]
            part = int((t - s0) * 8 / (m0 - s0)) if is_day_a else 8 + int((t - m0) * 8 / (e0 - m0))
        else:
            part = int((t - start) * 16 / (end - start))
        table = _KAALA_START_DAY if part < 8 else _KAALA_START_NIGHT
        out[key]["kaala_lord"] = _KAALA_ORDER[(table[out[key]["weekday"]] + part) % 8]
    main = out["sunrise" if weekday_definition == 0 else "lmt"]
    maha = out["clock" if mahakala_definition == 2 else "lmt"]
    rise, sset, nxt = bounds["sunrise"]
    # the day count of the strength tables: local civil day number - 2038, one less before sunrise
    day_count = int(_local_jd(birth, 12.0) + 0.5) - 2038 - (1 if (birth.hour_local < 12.0 and not is_day_a) else 0)
    return {"definitions": out, "weekday": main["weekday"], "hora_lord": main["hora_lord"],
            "day_count": day_count, "is_day": is_day_a, "day_ghatis": (sset - rise) * 60.0,
            "night_ghatis": (nxt - sset) * 60.0,
            "hora_5min_sign": main["hora_5min_sign"], "kaala_lord": main["kaala_lord"],
            "mahakala_hora_lord": maha["hora_lord"], "mahakala_hora_5min_sign": maha["hora_5min_sign"],
            # the "Kaala Lord: x (Mahakala: y)" text gives the clock definition's lord always
            "mahakala_kaala_lord": out["clock"]["kaala_lord"],
            "janma_ghatis": (t - bounds["sunrise"][0]) * 60.0}


# Panchanga lords (docs/SOURCES.md section 8); lords are point indices 1 = Sun .. 8 = Rahu, 9 = Ketu;
# month 0 = Vaisakha .. 11 = Chaitra
_TITHI_LORDS = [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 8]
_NAKSHATRA_LORDS = [9, 6, 1, 2, 3, 8, 5, 7, 4]
_YOGA_LORDS = [7, 4, 9, 6, 1, 2, 3, 8, 5]
_SIGN_LORDS = [3, 6, 4, 2, 1, 4, 6, 3, 5, 7, 7, 5]


def _karana_index(k: int) -> int:
    """Karana (0 Bava .. 6 Vishti, 7 Sakuna, 8 Chatushpada, 9 Naga, 10 Kimstughna) of the k-th half tithi."""
    if k == 0:
        return 10
    return 7 + (k - 57) if k >= 57 else (k - 1) % 7


def _new_moon(jd: float, cfg: EphemerisConfig, direction: int) -> float:
    """The new moon before (direction -1) or after (+1) ``jd``."""
    def elong(t):
        p = planet_positions(t, cfg)
        return norm360(p["Moon"]["lon"] - p["Sun"]["lon"])
    e = elong(jd)
    t = jd - e / 12.19 if direction < 0 else jd + (360.0 - e) / 12.19
    for _ in range(20):
        d = ((elong(t) + 180.0) % 360.0) - 180.0
        if abs(d) < 1e-7:
            break
        t -= d / 12.19
    return t


def panchanga(birth: BirthData, chart: Dict[str, Any], cfg: Optional[EphemerisConfig] = None) -> Dict[str, Any]:
    """
    The panchanga of a chart as Key Info shows it (SS 2.64-69; the default amanta lunar year, INI LunarYrDef=2):
    tithi 0..29, nakshatra 0..26, yoga 0..26, karana 0..10 with their lords (point
    indices) and the fraction left; lunar month 0 = Vaisakha (Sun's sign at the new moon before birth), "adhika"
    2 when the next new moon is in the same sign, 1 ("nija") when the previous one is; samvatsara 0..59.
    """
    cfg = cfg or EphemerisConfig()
    sun, moon = chart["planet_longitudes"]["Sun"], chart["planet_longitudes"]["Moon"]
    elong = norm360(moon - sun)
    tithi = int(elong / 12.0)
    tithi_left = (12.0 * (tithi + 1) - elong) / 12.0
    nak = int(moon * 0.075)
    yoga_x = norm360(sun + moon) * 0.075
    karana = _karana_index(int(elong / 6.0))
    karana_left = tithi_left * 2.0
    if karana_left > 1.0:
        karana_left -= 1.0
    if karana < 7:
        karana_lord = karana + 1
    else:
        karana_lord = _SIGN_LORDS[(karana * 3 + 123 + chart["lagna_sign"]) % 12]
    nm = _new_moon(birth.jd_ut, cfg, -1)
    sign = lambda t, body: int(planet_positions(t, cfg)[body]["lon"] // 30)  # noqa: E731
    month, moon_sign = sign(nm, "Sun"), sign(nm, "Moon")
    adhika = 0
    if sign(_new_moon(nm + 0.0035, cfg, +1), "Moon") == moon_sign:
        adhika = 2
    elif sign(_new_moon(nm - 0.007, cfg, -1), "Moon") == moon_sign:
        adhika = 1
    year = birth.year - (1 if birth.month < 6 and 6 <= month <= 10 else 0)
    return {"tithi": tithi, "tithi_lord": _TITHI_LORDS[tithi], "tithi_left": tithi_left,
            "nakshatra": nak, "nakshatra_lord": _NAKSHATRA_LORDS[nak % 9], "nakshatra_left": 1.0 - (moon * 0.075 - nak),
            "yoga": int(yoga_x), "yoga_lord": _YOGA_LORDS[int(yoga_x) % 9], "yoga_left": 1.0 - (yoga_x - int(yoga_x)),
            "karana": karana, "karana_lord": karana_lord, "karana_left": karana_left,
            "lunar_month": month, "adhika": adhika, "samvatsara": (year + 14333) % 60}
