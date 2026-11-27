"""The Timeline tab: one calendar year of the sky — the Barhaspatya samvatsara, every graha's signs, retrogressions,
gandanta passages, combustion, conjunctions and eclipses (the Moon only in the signs: anywhere else it would swamp the year)."""
from __future__ import annotations

import math

from core_logic import ephemeris as E
from core_logic.natal_chart import is_combust

from .basics import _tables
from .finance import _eclipses
from .settings import SIGNS

BODIES = ["Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]
POINTS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]    # is_combust's numbering, from 1
STATIONS = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]   # the nodes' wobble is no retrogression
HEAVY = {"Jupiter", "Saturn", "Rahu", "Ketu"}
SLOW = HEAVY | {"Mars", "Uranus", "Neptune", "Pluto"}
GANDANTA = 360.0 / 108.0      # the last navamsa of a water sign and the first of the fire sign after it
MINUTE = 1.0 / 1440.0

# Barhaspatya samvatsara: a 30° step of Surya Siddhanta's mean Jupiter, 364,220 revolutions in 1,577,917,828 days from Kali
# (Ujjain midnight). Offset 25 names VS 2080-2083 Nala, Pingala, Kalayukta, Siddharthi at Mesha Sankranti, as North India does.
KALI = 588465.5 - 75.77 / 360.0
JOVIAN_YEAR = 1577917828 / (364220 * 12)
OFFSET = 25


def _iso(jd: float, tz: float) -> str:
    y, m, d, h = E.jd_to_calendar(jd + tz / 24.0, True)
    mi = int(round(h * 60))
    return "%04d-%02d-%02dT%02d:%02d" % (y, m, d, mi // 60, mi % 60) if mi < 1440 else _iso(jd + MINUTE, tz)


def samvatsaras(jd0: float, jd1: float, tz: float) -> list[dict]:
    names = _tables()[0]["samvatsaras"]
    out, n = [], math.floor((jd0 - KALI) / JOVIAN_YEAR)
    while KALI + n * JOVIAN_YEAR < jd1:
        s = KALI + n * JOVIAN_YEAR
        out.append({"name": names[(n + OFFSET) % 60], "number": (n + OFFSET) % 60 + 1, "start": _iso(s, tz), "end": _iso(s + JOVIAN_YEAR, tz)})
        n += 1
    return out


def in_gandanta(lon: float) -> bool:
    x = lon % 120.0
    return x >= 120.0 - GANDANTA or x < GANDANTA


def year(birth, cfg, y: int, classical: bool = False) -> dict:
    tz = birth.tz_east_hours
    jd0 = E.julian_day_ut(y, 1, 1, 0.0, True) - tz / 24.0
    jd1 = E.julian_day_ut(y + 1, 1, 1, 0.0, True) - tz / 24.0
    cache: dict[float, dict] = {}

    def at(jd: float) -> dict:
        if jd not in cache:
            cache[jd] = E.planet_positions(jd, cfg, birth, include_outer=True)
        return cache[jd]

    def refine(lo: float, hi: float, state) -> float:
        """The moment in [lo, hi] where state(jd) flips, to the minute."""
        s0 = state(lo)
        while hi - lo > MINUTE / 2:
            m = 0.5 * (lo + hi)
            lo, hi = (m, hi) if state(m) == s0 else (lo, m)
        return hi

    days = [jd0 + i for i in range(int(math.ceil(jd1 - jd0)) + 1)]
    days[-1] = jd1
    nak = _tables()[0]["nakshatras"]
    where = lambda lon: {"sign": SIGNS[int(lon // 30) % 12], "deg": lon % 30.0, "nakshatra": nak[int(lon // (360.0 / 27)) % 27]}  # noqa: E731

    def spans(state, label) -> list[dict]:
        """Runs of days where state(jd) is truthy; from/to None when the run goes past the year's ends."""
        out, start, prev = [], (None if state(jd0) else False), jd0
        for d in days[1:]:
            now, was = bool(state(d)), bool(state(prev))
            if now != was:
                t = refine(prev, d, lambda j: bool(state(j)))
                if now:
                    start = t
                else:
                    out.append({**label(start if start is not None else jd0, t), "from": None if start is None else _iso(start, tz), "to": _iso(t, tz)})
                    start = False
            prev = d
        if start is not False:
            out.append({**label(start if start is not None else jd0, jd1), "from": None if start is None else _iso(start, tz), "to": None})
        return out

    def combust(j: float, b: str) -> bool:
        p = at(j)
        return is_combust(POINTS.index(b) + 1, [0.0] + [p[x]["lon"] for x in POINTS], [False] + [p[x]["speed"] < 0 for x in POINTS], classical=classical)

    signs, retro, gandanta, combustion = {}, {}, {}, {}
    for b in ["Moon"] + BODIES:     # the Moon's signs only, for its own list: on the strip and in the rest it would swamp the year
        lon = lambda j, b=b: at(j)[b]["lon"]  # noqa: E731
        # a sign is a run of the same sign index; the label gives which one
        # retrograde: the sign was entered moving backwards; the nodes too (the mean ones always, the true ones nearly always)
        rows, cur, start, back = [], int(lon(jd0) // 30), None, False
        for d0, d1 in zip(days, days[1:]):
            if int(lon(d1) // 30) != cur:
                t = refine(d0, d1, lambda j: int(lon(j) // 30))
                rows.append({"sign": SIGNS[cur], "from": None if start is None else _iso(start, tz), "to": _iso(t, tz), "retrograde": back})
                cur, start, back = int(lon(d1) // 30), t, (b in STATIONS or b in ("Rahu", "Ketu")) and at(t)[b]["speed"] < 0
        rows.append({"sign": SIGNS[cur], "from": None if start is None else _iso(start, tz), "to": None, "retrograde": back})
        signs[b] = rows
        if b == "Moon":
            continue
        if b in STATIONS:
            retro[b] = spans(lambda j, b=b: at(j)[b]["speed"] < 0,
                             lambda s, e, b=b: {"sign_from": where(at(s)[b]["lon"])["sign"], "sign_to": where(at(e)[b]["lon"])["sign"],
                                                "nak_from": where(at(s)[b]["lon"])["nakshatra"], "nak_to": where(at(e)[b]["lon"])["nakshatra"]})
        g = spans(lambda j, b=b: in_gandanta(at(j)[b]["lon"]), lambda s, e, b=b: {"where": "%s–%s" % (
            SIGNS[(int(((at(s)[b]["lon"] + GANDANTA) % 360) // 120) * 4 + 11) % 12], SIGNS[int(((at(s)[b]["lon"] + GANDANTA) % 360) // 120) * 4])})
        if g:
            gandanta[b] = g
        if b in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn"):     # the grahas shown combust (the Moon's monthly one would swamp the strip)
            c = spans(lambda j, b=b: combust(j, b), lambda s, e, b=b: {"sign_from": where(at(s)[b]["lon"])["sign"], "sign_to": where(at(e)[b]["lon"])["sign"]})
            if c:
                combustion[b] = c

    conj = []
    for i, a in enumerate(BODIES):
        for b in BODIES[i + 1:]:
            if {a, b} == {"Rahu", "Ketu"}:
                continue
            sep = lambda j, a=a, b=b: (at(j)[a]["lon"] - at(j)[b]["lon"] + 180.0) % 360.0 - 180.0  # noqa: E731
            for d0, d1 in zip(days, days[1:]):
                s0, s1 = sep(d0), sep(d1)
                if (s0 < 0) != (s1 < 0) and abs(s0 - s1) < 90:     # through 0°, not the ±180° wrap
                    t = refine(d0, d1, lambda j: sep(j) < 0)
                    lon = at(t)[a]["lon"]
                    conj.append({"at": _iso(t, tz), "bodies": [a, b], **where(lon), "gandanta": in_gandanta(lon),
                                 "major": bool({a, b} & HEAVY) or {a, b} <= SLOW})
    conj.sort(key=lambda c: c["at"])

    eclipses = []
    for e in _eclipses(birth, jd0, jd1):
        p = at(e["jd"])
        lon = p["Sun"]["lon"] if e["eclipse"] == "solar" else (p["Sun"]["lon"] + 180.0) % 360.0
        eclipses.append({"at": _iso(e["jd"], tz), "kind": e["eclipse"], "type": e["type"], **where(lon), "gandanta": in_gandanta(lon),
                         "node": "Rahu" if abs((lon - p["Rahu"]["lon"] + 180) % 360 - 180) < 90 else "Ketu"})

    eclipses.sort(key=lambda e: e["at"])
    return {"year": y, "samvatsaras": samvatsaras(jd0, jd1, tz), "signs": signs, "retrograde": retro, "gandanta": gandanta,
            "combustion": combustion, "conjunctions": conj, "eclipses": eclipses}
