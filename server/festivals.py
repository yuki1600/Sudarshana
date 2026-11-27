"""Festivals and observances of a Gregorian year at a place, per regional calendar (data/festivals.json).

Lunar festivals take the tithi that covers a part of the day (Dharmasindhu's kalas: sunrise, Arunodaya, Purvahna,
Madhyahna, Aparahna, Pradosha, Nishitha, moonrise); solar ones the Sun's sign by the region's rule for the day a
solar month begins, and the Moon's nakshatra. Ekadasis follow the Smarta rule (the tithi at sunrise) or the Vaishnava
one (at Arunodaya, so a Dashami touching it moves the fast on), with the parana after Hari Vasara. Also the Pitru
Paksha shraddhas, the Sankrantis and the eclipses seen from the place."""
from __future__ import annotations

import bisect
import dataclasses
import datetime as DT
import functools
import json
import os
from typing import Optional

from core_logic import ephemeris as E, time_search as JS, panchanga as P
from core_logic.natal_chart import RASI_NAMES_SA

from .calendars import LUNAR_MONTHS
from .muhurta import _iso

PATH = os.path.join(os.path.dirname(__file__), "..", "data", "festivals.json")
MIN = 1.0 / 1440.0
ARUNODAYA = 96 * MIN                     # 4 ghatis before sunrise
GHATI = 24 * MIN
INSTANTS = {"sunrise", "arunodaya", "moonrise"}
KALA_NAME = {"sunrise": "Sunrise", "arunodaya": "Arunodaya", "moonrise": "Moonrise", "dawn": "Arunodaya", "purvahna": "Purvahna",
             "madhyahna": "Madhyahna", "aparahna": "Aparahna", "pradosha": "Pradosha", "nishitha": "Nishitha"}
KALA_TEXT = {"sunrise": "at sunrise", "arunodaya": "at Arunodaya, 96 minutes (4 ghatis) before sunrise", "moonrise": "at moonrise",
             "dawn": "in Arunodaya, the 96 minutes before sunrise", "purvahna": "in Purvahna, the first half of the day",
             "madhyahna": "at Madhyahna, the middle fifth of the day", "aparahna": "in Aparahna, the fourth fifth of the day",
             "pradosha": "at Pradosha, the first fifth of the night", "nishitha": "at Nishitha, the middle (8th of 15) muhurta of the night"}
PREFER_TEXT = {"first": "; on two days, the first", "second": "; on two days, the second", "more": "; on two days, the one it covers longer"}
SANKRANTI_TEXT = {"sunrise": "on the day (sunrise to sunrise) of the Sun's entry", "sunset": "on the day of the Sun's entry if it is before sunset, else the next day",
                  "aparahna": "on the day of the Sun's entry if it is in the first three fifths of the daytime, else the next day",
                  "midnight": "the day after the Sun's entry, or two days after if it falls past midnight"}
OFFSET_TEXT = {-1: "The day before: ", 1: "The day after: ", 2: "Two days after: "}
EKADASI = {"smarta": ("sunrise", "first", "before"), "vaishnava": ("arunodaya", "second", "after")}
EKADASI_TEXT = {"smarta": "Smarta rule: the Ekadasi at sunrise; when it holds two sunrises, the first",
                "vaishnava": "Vaishnava rule: the Ekadasi at Arunodaya, 96 minutes before sunrise, so a Dashami touching Arunodaya moves the fast to the next day; when it holds two Arunodayas, the second"}
EKADASI_NOTE = {
    "smarta": "Ekadasi is the 11th tithi of a paksha: the stretch while the Moon moves from 120 to 132 degrees ahead of the Sun (300 to 312 in "
              "Krishna paksha). A tithi keeps its own clock, about 19 to 26 hours, so it starts and ends at any hour and is the same moment "
              "everywhere; only the day it is kept depends on the place's sunrise. The tithi in force at sunrise names the whole day, so the fast "
              "is kept on the day whose sunrise falls in the Ekadasi. A long one that holds two sunrises is kept on the first; a short one that "
              "begins after one sunrise and ends before the next (a kshaya tithi) is kept on the day it begins. The fast is broken (parana) the "
              "next morning in the Dwadashi, once Hari Vasara, its first quarter, is over.",
    "vaishnava": "Ekadasi is the 11th tithi of a paksha: the stretch while the Moon moves from 120 to 132 degrees ahead of the Sun (300 to 312 in "
                 "Krishna paksha). A tithi keeps its own clock, about 19 to 26 hours, so it starts and ends at any hour. Vaishnavas keep only a pure "
                 "Ekadasi: Dashami must be over by Arunodaya, the dawn 96 minutes (4 ghatis) before sunrise. If Dashami still runs at Arunodaya "
                 "the Ekadasi is touched (viddha) and the fast moves to the next day; one that holds two Arunodayas is kept on the second. The "
                 "fast is broken (parana) the next morning in the Dwadashi, once Hari Vasara, its first quarter, is over."}
PITRU = ["Purnima Shraddha"] + ["%s Shraddha" % n for n in ("Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami",
                                                            "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi")] + ["Mahalaya Amavasya"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]   # date.weekday()
GROUPS = ["Festivals", "Ekadasi", "Jayanti", "Pitru Paksha", "Vratas", "Sankranti", "Grahana"]


@functools.lru_cache(maxsize=1)
def data() -> dict:
    with open(PATH, encoding="utf-8") as f:
        return json.load(f)


def calendars() -> list:
    return [{k: c[k] for k in ("id", "name", "places", "about", "months")} for c in data()["calendars"]]


def tithi_text(k: int) -> str:
    """0..29 as a tithi's name with its paksha (Purnima and Amavasya need none)."""
    return P.TITHI_NAMES[k] if k in (14, 29) else "%s %s" % ("Shukla" if k < 15 else "Krishna", P.TITHI_NAMES[k])


def _bisect(f, lo: float, hi: float, n: int = 36) -> float:
    """The moment in [lo, hi] where f turns true (f(lo) false, f(hi) true)."""
    for _ in range(n):
        mid = (lo + hi) / 2.0
        lo, hi = (lo, mid) if f(mid) else (mid, hi)
    return hi


class Sky:
    """The year (with margins either side) at one place: sunrises, new moons, tithis, sankrantis and nakshatras."""

    def __init__(self, place: E.BirthData, cfg, year: int):
        self.place, self.cfg, self.year = place, cfg, year
        self.sun, self.moon = JS.body_longitude(1, cfg), JS.body_longitude(2, cfg)
        first = DT.date(year - 1, 11, 1)
        self.dates = [first + DT.timedelta(i) for i in range((DT.date(year + 1, 3, 1) - first).days)]
        rs = [E.sunrise_sunset(dataclasses.replace(place, year=d.year, month=d.month, day=d.day), cfg) for d in self.dates]
        self.rise, self.set = [r["sunrise_jd"] for r in rs], [r["sunset_jd"] for r in rs]
        self._moonrise: dict = {}
        self._tithis: dict = {}
        swe = E.engine(cfg)
        # the Moon less the Sun needs no ayanamsa: two direct calls, not the whole sidereal table
        elong = lambda t: (swe.calc_ut(t, swe.MOON, E._ephe_flag(swe, t))[0][0] - swe.calc_ut(t, swe.SUN, E._ephe_flag(swe, t))[0][0]) % 360.0  # noqa: E731
        self.elong = elong
        # new moons, then the lunations between them: Amanta month by the Sun's sign at the two ends, Adhika with no Sankranti
        t, prev, nms = self.rise[0], elong(self.rise[0]), []
        while t < self.rise[-1]:
            cur = elong(t + 1.0)
            if prev > 300.0 and cur < 60.0:
                nms.append(_bisect(lambda x: elong(x) < 180.0, t, t + 1.0))
            t, prev = t + 1.0, cur
        sign = lambda x: int(self.sun(x) // 30) % 12  # noqa: E731
        self.lunations = [(a, b, (sign(a) + 1) % 12, sign(a) == sign(b)) for a, b in zip(nms, nms[1:])]
        # the Sun's entries into the signs
        self.sankrantis, t, s = [], self.rise[0], sign(self.rise[0])
        while t < self.rise[-1]:
            s2 = sign(t + 1.0)
            if s2 != s:
                self.sankrantis.append((s2, _bisect(lambda x: sign(x) == s2, t, t + 1.0)))
            t, s = t + 1.0, s2
        # the Moon's nakshatras as (index, start, end)
        nak = lambda x: int(self.moon(x) // (360.0 / 27.0)) % 27  # noqa: E731
        t, k, since, self.naks = self.rise[0], nak(self.rise[0]), None, []
        while t < self.rise[-1]:
            k2 = nak(t + 0.25)
            if k2 != k:
                edge = _bisect(lambda x: nak(x) == k2, t, t + 0.25)
                if since is not None:
                    self.naks.append((k, since, edge))
                since = edge
            t, k = t + 0.25, k2
        self._starts: dict = {}

    # -- days ---------------------------------------------------------------
    def day_of(self, jd: float) -> int:
        """The index of the day (sunrise to sunrise) holding ``jd``."""
        return max(bisect.bisect_right(self.rise, jd) - 1, 0)

    def moonrise(self, i: int) -> Optional[float]:
        """The first moonrise after midday of day ``i``."""
        if i not in self._moonrise:
            s = E._require_swe(self.cfg.ephe_path)
            p = self.place
            with E._SWE_LOCK:
                ret, tret = s.rise_trans((self.rise[i] + self.set[i]) / 2.0, s.MOON, s.CALC_RISE, (p.longitude_east, p.latitude, p.altitude_m), p.pressure_hpa, p.temperature_c,
                                         E._ephe_flag(s, self.rise[i]))
            self._moonrise[i] = tret[0] if ret == 0 else None
        return self._moonrise[i]

    def kala(self, i: int, k: str):
        """The (from, to) of part ``k`` of day ``i``; an instant has from == to."""
        r, s, r2 = self.rise[i], self.set[i], self.rise[i + 1]
        d, n = s - r, r2 - s
        if k == "moonrise":
            m = self.moonrise(i)
            return (m, m)
        return {"sunrise": (r, r), "arunodaya": (r - ARUNODAYA, r - ARUNODAYA), "dawn": (r - ARUNODAYA, r),
                "purvahna": (r, r + d / 2), "madhyahna": (r + 0.4 * d, r + 0.6 * d), "aparahna": (r + 0.6 * d, r + 0.8 * d),
                "pradosha": (s, s + n / 5), "nishitha": (s + 7 * n / 15, s + 8 * n / 15)}[k]

    def pick(self, ts: float, te: float, kala: str, prefer: str = "more", fallback: str = "before") -> int:
        """The day on which a span (a tithi or nakshatra) covers ``kala``. On two days: ``prefer``; a cover of under a
        ghati yields to a longer one. On neither: the day it begins in, or with ``after`` the next day whose kala
        follows its start."""
        lo, hi = max(self.day_of(ts) - 1, 0), min(self.day_of(te) + 1, len(self.rise) - 2)
        cands = []
        for i in range(lo, hi + 1):
            a, b = self.kala(i, kala)
            if a is None:
                continue
            cover = (1.0 if ts <= a < te else 0.0) if kala in INSTANTS else min(b, te) - max(a, ts)
            if cover > 0:
                cands.append((cover, i))
        if len(cands) > 1 and kala not in INSTANTS and any(c >= GHATI for c, _ in cands):
            cands = [c for c in cands if c[0] >= GHATI]
        if not cands:
            if fallback == "after":     # none (no moonrise for days near the poles): the day it begins in
                return next((i for i in range(lo, min(hi + 2, len(self.rise) - 1)) if (self.kala(i, kala)[0] or 0) > ts), self.day_of(ts))
            return self.day_of(ts)
        if prefer == "first":
            return cands[0][1]
        if prefer == "second":
            return cands[-1][1]
        return max(cands, key=lambda c: (c[0], -c[1]))[1]

    def tithi(self, lunation, k: int):
        """(start, end) of tithi ``k`` (0..29) in a lunation."""
        a, b = lunation[0], lunation[1]
        f = lambda g: _bisect(lambda x: self.elong(x) >= g, a, b)  # noqa: E731
        if (a, k) not in self._tithis:
            self._tithis[(a, k)] = (a if k == 0 else f(12.0 * k)), (b if k == 29 else f(12.0 * (k + 1)))
        return self._tithis[(a, k)]

    def month_starts(self, rule: str) -> list:
        """[(sign, first day)] of the solar months by a region's rule."""
        if rule not in self._starts:
            out = []
            for sign, t in self.sankrantis:
                i = self.day_of(t)
                r, s, r2 = self.rise[i], self.set[i], self.rise[i + 1]
                if rule == "sunrise":
                    pass
                elif rule == "sunset":
                    i += t >= s
                elif rule == "aparahna":
                    i += t >= r + 0.6 * (s - r)
                else:                                   # midnight: the middle of the night
                    i += 1 if t < (s + r2) / 2 else 2
                out.append((sign, i))
            self._starts[rule] = out
        return self._starts[rule]

    def solar(self, rule: str, i: int):
        """(sign, first day) of the solar month day ``i`` is in."""
        starts = self.month_starts(rule)
        j = bisect.bisect_right([d for _, d in starts], i) - 1
        return starts[j] if j >= 0 else (None, None)

    def masa(self, i: int, cal: dict) -> dict:
        """The month of day ``i`` (at its sunrise) as ``cal`` names it: Purnimanta, Amanta or the Sun's sign."""
        if cal["months"] == "solar":
            return {"masa": RASI_NAMES_SA[self.solar(cal["sankranti"], i)[0]]}
        r = self.rise[i]
        _, _, m, adhika = next(lun for lun in self.lunations if lun[0] <= r < lun[1])
        return {"masa": _month_name(cal, m, int(self.elong(r) // 12)), **({"adhika": True} if adhika else {})}

    def iso(self, jd: float) -> str:
        return _iso(jd, self.place.tz_east_hours)


def _sign(name: str) -> int:
    return RASI_NAMES_SA.index(name)


def _solar_name(cal: dict, sign: int) -> str:
    return "%s (%s)" % (cal["solar_names"][sign], RASI_NAMES_SA[sign]) if cal.get("solar_names") else "the solar month %s" % RASI_NAMES_SA[sign]


def _month_name(cal: dict, m: int, k: int) -> str:
    """Amanta month ``m`` as the calendar names it for tithi ``k``: Purnimanta moves the dark half to the next month."""
    return LUNAR_MONTHS[(m + 1) % 12] if cal["months"] == "purnimanta" and k >= 15 else LUNAR_MONTHS[m]


def criteria(rule: dict, cal: dict) -> str:
    """The rule in words, with the calendar's month names."""
    if "before" in rule:
        inner = criteria(rule["before"], cal)
        return "The %s before %s" % (rule["weekday"], inner[0].lower() + inner[1:])
    kala = rule.get("kala", "sunrise")
    pre = OFFSET_TEXT.get(rule.get("offset", 0), "")
    if "sankranti" in rule:
        sign = _sign(rule["sankranti"])
        text = "The Sun enters %s, %s" % (RASI_NAMES_SA[sign], SANKRANTI_TEXT[rule.get("by", cal["sankranti"])])
        if cal.get("solar_names"):
            text = "%s 1: %s" % (cal["solar_names"][sign], text[0].lower() + text[1:])
    elif "day" in rule:
        text = "Day %d of %s" % (rule["day"], _solar_name(cal, _sign(rule["sun"])))
    elif "nak" in rule:
        text = "%s nakshatra %s in %s; if it comes twice, the second" % (rule["nak"], KALA_TEXT[kala], _solar_name(cal, _sign(rule["sun"])))
    else:
        ks = rule["tithi"] if isinstance(rule["tithi"], list) else [rule["tithi"]]
        names = " and ".join(tithi_text(k - 1) for k in ks)
        how = ". " + EKADASI_TEXT[cal["ekadasi"]] if kala == "ekadasi" else ", " + KALA_TEXT[kala] + PREFER_TEXT[rule.get("prefer", "more")]
        if "month" in rule:
            text = "%s %s%s" % (_month_name(cal, LUNAR_MONTHS.index(rule["month"]), ks[0] - 1), names, how)
        elif "sun" in rule:
            text = "%s in %s%s" % (names, _solar_name(cal, _sign(rule["sun"])), how)
        else:
            text = "%s of every month%s" % (names, how)
    return pre + (text[0].lower() + text[1:] if pre else text)


def _days(sky: Sky, rule: dict, cal: dict) -> list:
    """[(day, span, at)] for one rule in one calendar: span = (label, from, to) of what decided it, at = (label, from, to)."""
    off = rule.get("offset", 0)
    shift = lambda rows: [(i + off, *rest) for i, *rest in rows]  # noqa: E731
    if "before" in rule:
        wd = WEEKDAYS.index(rule["weekday"])
        return [(i - ((sky.dates[i].weekday() - wd) % 7 or 7), span, None) for i, span, *_ in _days(sky, rule["before"], cal)]
    if "sankranti" in rule:
        sign = _sign(rule["sankranti"])
        return shift([(i, None, ("Sun enters %s" % RASI_NAMES_SA[s], t_, t_)) for (s, i), (_, t_) in zip(sky.month_starts(rule.get("by", cal["sankranti"])), sky.sankrantis) if s == sign])
    if "day" in rule:
        sign = _sign(rule["sun"])
        return shift([(i + rule["day"] - 1, None, None) for s, i in sky.month_starts(cal["sankranti"]) if s == sign])
    kala, prefer, fallback = rule.get("kala", "sunrise"), rule.get("prefer", "more"), rule.get("fallback", "before")
    if kala == "ekadasi":
        kala, prefer, fallback = EKADASI[cal["ekadasi"]]
    at = lambda i: (KALA_NAME[kala], *sky.kala(i, kala)) if sky.kala(i, kala)[0] is not None else None  # noqa: E731
    if "nak" in rule:
        n, sign = P.NAKSHATRA_NAMES.index(rule["nak"]), _sign(rule["sun"])
        best = {}
        for k, a, b in sky.naks:
            if k == n:
                i = sky.pick(a, b, kala, "first")
                s, start = sky.solar(cal["sankranti"], i)
                if s == sign:
                    best[start] = (i, (rule["nak"], a, b), at(i))     # a second occurrence in the month replaces the first
        return shift(list(best.values()))
    out, seen = [], set()
    for lun in sky.lunations:
        if "month" in rule and (lun[3] or LUNAR_MONTHS[lun[2]] != rule["month"]):
            continue
        for k in (rule["tithi"] if isinstance(rule["tithi"], list) else [rule["tithi"]]):
            ts, te = sky.tithi(lun, k - 1)
            i = sky.pick(ts, te, kala, prefer, fallback)
            if "udaya_ghatis" in rule:      # Dharmasindhu: a tithi that outlasts a sunrise by n ghatis is kept that day
                i = next((j for j in (i + 1, i) if ts <= sky.rise[j] <= te - rule["udaya_ghatis"] * GHATI), i)
            if "sun" in rule:
                s, start = sky.solar(cal["sankranti"], i)
                if s != _sign(rule["sun"]) or start in seen:
                    continue
                seen.add(start)
            out.append((i, (tithi_text(k - 1), ts, te), at(i), {"parana": _parana(sky, lun, k - 1, i)} if rule.get("kala") == "ekadasi" else {}))
    return shift(out)


def _parana(sky: Sky, lun, k: int, i: int) -> dict:
    """The time to break an Ekadasi fast kept on day ``i``: the next morning after Hari Vasara (the first quarter of
    the Dwadashi), within the Dwadashi and the first fifth of the day; failing that after Madhyahna.
    shortcut: Drikpanchang's finer cases (a Dwadashi ending before sunrise, Mahadwadashis) are not modelled."""
    p = i + 1
    r, s = sky.rise[p], sky.set[p]
    ds, de = sky.tithi(lun, k + 1)
    a = max(r, ds + (de - ds) / 4) if de > r else r
    pratah = r + (s - r) / 5
    if a < pratah:
        b = min(de, pratah) if de > a else pratah
    else:
        a = max(a, r + 0.6 * (s - r))
        b = min(de, s) if de > a else s
    return {"from": sky.iso(a), "to": sky.iso(b), "hari_vasara_end": sky.iso(ds + (de - ds) / 4)}


def _entry(sky: Sky, i: int, span, at, extra: Optional[dict] = None) -> dict:
    out = {"date": sky.dates[i].isoformat(), **(extra or {})}
    if span:
        out["span"] = {"label": span[0], "from": sky.iso(span[1]), "to": sky.iso(span[2])}
    if at:
        out["at"] = {"label": at[0], "from": sky.iso(at[1]), "to": sky.iso(at[2])}
    return out


def _calendar(sky: Sky, cal: dict) -> list:
    """Every observance of ``cal`` in the year: [{id, key, name, group, criteria, note, dates}]."""
    D, cid, items = data(), cal["id"], []
    for f in D["festivals"]:
        if cid not in f["in"]:
            continue
        items.append({"id": f["id"], "key": f.get("key", f["id"]), "name": f.get("names", {}).get(cid, f["name"]), "group": f["group"],
                      "criteria": criteria(f["rule"], cal), "note": f.get("note"),
                      "dates": [_entry(sky, *row) for row in _days(sky, f["rule"], cal)]})
    # a Sankranti that a festival already stands for is not listed again
    taken = {d["date"] for f, x in zip([f for f in D["festivals"] if cid in f["in"]], items) if "sankranti" in f["rule"] and not f["rule"].get("offset") for d in x["dates"]}
    # the Ekadasis, by name; an Adhika month's are Padmini and Parama
    kala, prefer, fallback = EKADASI[cal["ekadasi"]]
    eka: dict = {}
    for lun in sky.lunations:
        for p, k in ((0, 10), (1, 25)):
            name = "%s Ekadasi" % D["ekadasi_names"]["adhika" if lun[3] else LUNAR_MONTHS[lun[2]]][p]
            ts, te = sky.tithi(lun, k)
            i = sky.pick(ts, te, kala, prefer, fallback)
            month = "Adhika %s" % LUNAR_MONTHS[lun[2]] if lun[3] else _month_name(cal, lun[2], k)
            row = eka.setdefault(name, {"id": "ekadasi-" + name.split()[0].lower(), "key": "ekadasi-" + name.split()[0].lower(), "name": name, "group": "Ekadasi",
                                        "criteria": "%s %s. %s" % (month, tithi_text(k), EKADASI_TEXT[cal["ekadasi"]]), "note": EKADASI_NOTE[cal["ekadasi"]], "dates": []})
            row["dates"].append(_entry(sky, i, (tithi_text(k), ts, te), (KALA_NAME[kala], *sky.kala(i, kala)), {"parana": _parana(sky, lun, k, i)}))
    items += eka.values()
    # Pitru Paksha: the shraddha of each tithi in the Aparahna, Bhadrapada Purnima to the Amavasya (Amanta)
    for lun in sky.lunations:
        if LUNAR_MONTHS[lun[2]] == "Bhadrapada" and not lun[3]:
            for n, k in enumerate(range(14, 30)):
                ts, te = sky.tithi(lun, k)
                i = sky.pick(ts, te, "aparahna")
                items.append({"id": "pitru-%d" % n, "key": "pitru-%d" % n, "name": "Sarva Pitru Amavasya" if k == 29 and cid == "north" else PITRU[n], "group": "Pitru Paksha",
                              "criteria": "%s %s, %s" % (_month_name(cal, lun[2], k), tithi_text(k), KALA_TEXT["aparahna"]),
                              "note": "Shraddha for those who passed away on this tithi." if k < 29 else "Shraddha for all ancestors, and for those whose tithi is not known.",
                              "dates": [_entry(sky, i, (tithi_text(k), ts, te), ("Aparahna", *sky.kala(i, "aparahna")))]})
    # the Sankrantis
    starts = sky.month_starts(cal["sankranti"])
    for (sign, i), (_, t) in zip(starts, sky.sankrantis):
        if sky.dates[i].isoformat() in taken:
            continue
        name = "%s begins" % cal["solar_names"][sign] if cal.get("solar_names") else "%s Sankranti" % RASI_NAMES_SA[sign]
        items.append({"id": "sankranti-%d" % sign, "key": "sankranti-%d" % sign, "name": name, "group": "Sankranti",
                      "criteria": "The Sun enters %s, %s" % (RASI_NAMES_SA[sign], SANKRANTI_TEXT[cal["sankranti"]]), "note": None,
                      "dates": [_entry(sky, i, None, ("Sun enters %s" % RASI_NAMES_SA[sign], t, t))]})
    items += _eclipses(sky)
    # merge rows of one id (a festival or Sankranti twice in the margins), keep the year's dates, drop the empty
    merged: dict = {}
    for x in items:
        row = merged.setdefault(x["id"], {**x, "dates": []})
        row["dates"] += [d for d in x["dates"] if d["date"].startswith(str(sky.year))]
    out = [x for x in merged.values() if x["dates"]]
    index = {d.isoformat(): i for i, d in enumerate(sky.dates)}
    for x in out:
        x["dates"].sort(key=lambda d: d["date"])
        for d in x["dates"]:
            d.update(sky.masa(index[d["date"]], cal))
    out.sort(key=lambda x: (GROUPS.index(x["group"]), x["dates"][0]["date"]))
    return out


def _eclipses(sky: Sky) -> list:
    """The solar and lunar eclipses of the year seen from the place."""
    out = []
    for kind in ("solar", "lunar"):
        t = sky.rise[0]
        while True:
            try:
                e = E.next_eclipse(t, kind, sky.place, cfg=sky.cfg)
            except Exception:   # noqa: BLE001 -- no eclipse found: the list simply has none
                break
            if e["max_jd"] > sky.rise[-2]:
                break
            i = sky.dates.index(DT.date.fromisoformat(sky.iso(e["max_jd"])[:10]))
            name = "%s %s eclipse" % (e["type"].capitalize(), kind)
            out.append({"id": "eclipse-%s-%s" % (kind, sky.iso(e["max_jd"])[:10]), "key": "eclipse-%s-%s" % (kind, sky.iso(e["max_jd"])[:10]),
                        "name": "%s (%s Grahana)" % (name, "Surya" if kind == "solar" else "Chandra"), "group": "Grahana",
                        "criteria": "The %s eclipse seen from this place, from first contact to last." % kind,
                        "note": "The Sutak (vedha) begins %s before the eclipse." % ("12 hours" if kind == "solar" else "9 hours"),
                        "dates": [_entry(sky, i, None, ("Eclipse", e["begin_jd"], e["end_jd"]))]})
            t = e["max_jd"] + 20.0
    return out


def year(place: E.BirthData, cfg, year_: int) -> dict:
    """Every calendar's observances of the Gregorian year at ``place``: {items: {calendar id: [items]}, days: {calendar id: {date: day}}}.
    shortcut: the place's zone is held for the year, so daylight saving moves times by an hour in part of it; dates are
    almost never affected. Kshaya months are not detected, so a festival of a lost month is missing that year."""
    sky = Sky(place, cfg, year_)
    year_days = [i for i, d in enumerate(sky.dates) if d.year == year_]
    tithis = {i: tithi_text(int(sky.elong(sky.rise[i]) // 12)) for i in year_days}
    cals = data()["calendars"]
    return {"items": {c["id"]: _calendar(sky, c) for c in cals},
            # each day's tithi at sunrise and month as the calendar names it, for any date the tab shows
            "days": {c["id"]: {sky.dates[i].isoformat(): {"tithi": tithis[i], **sky.masa(i, c)} for i in year_days} for c in cals}}


def view(all_: dict, cid: str) -> list:
    """One calendar's items, each with the same festival's dates in the other calendars (``elsewhere``)."""
    names = {c["id"]: c["name"] for c in data()["calendars"]}
    by_key: dict = {}
    for c, items in all_["items"].items():
        for x in items:
            by_key.setdefault(x["key"], []).append((c, x))
    return [{**x, "elsewhere": [{"calendar": names[c], "name": y["name"], "dates": [d["date"] for d in y["dates"]]}
                                for c, y in by_key[x["key"]] if c != cid]} for x in all_["items"].get(cid, [])]
