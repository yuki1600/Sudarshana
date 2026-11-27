"""
core_logic/daily_panchanga.py
=============================
The Panchanga tab: the panchanga of one day, and the "Copy monthly panchanga" text (one day per date, from
local noon).  Sources: docs/SOURCES.md section 8 (the elements SS 2.64-69).

* the day runs from sunrise (+ 0.01 hour) for one day; each element's end times inside it are found with the
  search family (``time_search``): the tithi (Moon - Sun reaching the next 12 deg), nakshatra (Moon, 13 deg 20'),
  yoga (Moon + Sun, 13 deg 20'), karana (Moon - Sun, 6 deg; up to three) and the Moon's sign; after an end the
  next one is searched from 0.1 day later;
* Rahu kala, Gulika kala and Yamaganda: an eighth of the daytime (the default) by the weekday tables of
  ``panchanga`` (Kalaprakasika ch. 33; Gulika one part later when its option is cleared);
* varjya (``panchanga.tyajya_time``) of the nakshatra running at the day's start and of the next, kept when it
  overlaps the day, and the durmuhurtas (``panchanga.DURMUHURTA_PARTS``);
* moonrise / moonset by the ecliptic (the Moon's semi-diameter, ``time_search.ecliptic_rise_set``);
* the single-day view's 24 horas (sunrise to sunrise / 24, lords (weekday - 2 i) mod 7 + 1: BPHS 27.13,
  Kalaprakasika ch. 33) and the 16 parts of day and night (eighths of each, BPHS 3.66-69; lords
  (weekday + 5 i) mod 7 by day, (weekday + 4 i - 28) mod 7 by night).

Times are UT Julian days.
"""
from typing import Any, Dict, List, Optional, Tuple

from . import ephemeris as E, time_search as S, panchanga as P

NAK = 13.333333333333334       # a nakshatra, 13 deg 20' (SS 2.64)
STEP_AFTER_END = 0.1           # days after an element's end to search for the next


def _ends(start: float, value, target_of, find, limit: int) -> List[Tuple[int, float]]:
    """(index, end) of each element ending in [start, start + 1): ``value(t)`` is the element's index at ``t``,
    ``target_of(i)`` the longitude where element ``i`` ends, ``find(t, target)`` the search."""
    out, t = [], start
    for _ in range(limit):
        i = value(t)
        end = find(t, target_of(i))
        if not start <= end < start + 1.0:
            break
        out.append((i, end))
        t = end + STEP_AFTER_END
    return out


def civil_day_panchanga(birth: E.BirthData, year: int, month: int, day: int,
                        cfg: Optional[E.EphemerisConfig] = None) -> Dict[str, Any]:
    """The panchanga of a civil day at the place of ``birth`` as the Panchanga tab computes it."""
    cfg = cfg or E.EphemerisConfig()
    place = E.BirthData(year, month, day, 12.0, birth.tz_east_hours, birth.longitude_east, birth.latitude,
                        birth.altitude_m, birth.gregorian, birth.place, birth.pressure_hpa, birth.temperature_c)
    sun = E.sunrise_sunset(place, cfg)
    start = sun["sunrise_jd"] + 0.01 / 24.0
    lon = lambda p: S.body_longitude(p, cfg, place)  # noqa: E731
    moon, sunl = lon(2), lon(1)
    elong = lambda t: (moon(t) - sunl(t)) % 360.0  # noqa: E731
    diff_event = lambda t, target: S.longitude_event(t, 2, target % 360.0, 1, "diff", cfg=cfg, birth=place)  # noqa
    tithis = _ends(start, lambda t: int(elong(t) / 12.0), lambda i: (i + 1) * 12.0, diff_event, 2)
    naks = _ends(start, lambda t: int(moon(t) / NAK), lambda i: (i + 1) * NAK,
                 lambda t, x: S.longitude_event(t, 2, x % 360.0, cfg=cfg, birth=place), 2)
    yogas = _ends(start, lambda t: int(((moon(t) + sunl(t)) % 360.0) / NAK), lambda i: (i + 1) * NAK,
                  lambda t, x: S.sum_event(t, 2, 1, x % 360.0, cfg=cfg, birth=place), 2)
    karanas = _ends(start, lambda t: int(elong(t) / 6.0), lambda i: (i + 1) * 6.0, diff_event, 3)
    moon_sign = _ends(start, lambda t: int(moon(t) / 30.0), lambda i: (i + 1) * 30.0,
                      lambda t, x: S.longitude_event(t, 2, x % 360.0, cfg=cfg, birth=place), 1)
    weekday = (int(start + 0.5 + birth.tz_east_hours / 24.0) + 1) % 7          # 0 = Sunday
    rise, set_ = sun["sunrise_jd"], sun["sunset_jd"]
    eighth = (set_ - rise) * 0.125

    def part(k: int) -> Tuple[float, float]:
        return rise + (k - 1) * eighth, rise + k * eighth
    # varjya of the nakshatra at the day's start and of the next one
    varjya, t = [], start
    nak_start = S.longitude_event(start, 2, int(moon(start) / NAK) * NAK, backward=True, cfg=cfg, birth=place)
    for _ in range(2):
        n = int(moon(t) / NAK)
        nak_end = S.longitude_event(t, 2, ((n + 1) * NAK) % 360.0, cfg=cfg, birth=place)
        a, b = P.tyajya_time(n, nak_start, nak_end)
        if start <= b and a <= start + 1.0:
            varjya.append((a, b))
        nak_start, t = nak_end, nak_end + STEP_AFTER_END
    muhurta = (set_ - rise) / 15.0
    dur = [(rise + (k - 1) * muhurta, rise + k * muhurta) for k in P.DURMUHURTA_PARTS[weekday]]
    moonrise, moonset = S.ecliptic_rise_set(start, 2, place, cfg.sunrise_definition, cfg=cfg)
    nxt = E.sunrise_sunset(E._shifted_day(place, 1), cfg)["sunrise_jd"]
    hora = (nxt - rise) / 24.0
    horas = [((weekday - 2 * i + 49) % 7 + 1, rise + i * hora, rise + (i + 1) * hora) for i in range(24)]
    night8 = (nxt - set_) * 0.125
    parts = [((weekday + 5 * i) % 7, rise + i * eighth, rise + (i + 1) * eighth) for i in range(8)] + [
        ((weekday + 4 * i - 28) % 7, set_ + (i - 8) * night8, set_ + (i - 7) * night8) for i in range(8, 16)]
    return {"start": start, "weekday": weekday, "sunrise": rise, "sunset": set_,
            "tithi": int(elong(start) / 12.0), "tithi_ends": tithis,
            "nakshatra": int(moon(start) / NAK), "nakshatra_ends": naks,
            "yoga": int(((moon(start) + sunl(start)) % 360.0) / NAK), "yoga_ends": yogas,
            "karana": int(elong(start) / 6.0), "karana_ends": karanas,
            "moon_sign": int(moon(start) / 30.0), "moon_sign_ends": moon_sign,
            "rahu_kala": part(P.RAHU_KALAM_PARTS[weekday]), "gulika_kala": part(P.GULIKA_KALAM_PARTS[weekday]),
            "yamaganda": part(P.YAMA_GHANTAM_PARTS[weekday]), "varjya": varjya, "durmuhurta": dur,
            "moonrise": moonrise, "moonset": moonset, "horas": horas, "day_parts": parts}
