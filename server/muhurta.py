"""The Muhurta tab: a civil day's panchang and daily muhurtas (sunrise to next sunrise), as Drikpanchang lists them, and
the search for good times for an event over a month (Panchang Shuddhi, data/muhurta_rules.json)."""
from __future__ import annotations

import calendar
import dataclasses
import json
import os
from typing import Optional

from core_logic import ephemeris as E, daily_panchanga as JP, time_search as JS, miscellany as CM, panchanga as P

from . import calendars as CAL
from .basics import SIGNS

NAK = 360.0 / 27.0
MINUTE = 1.0 / 1440.0
WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
HORA_LORDS = {1: "Sun", 2: "Moon", 3: "Mars", 4: "Mercury", 5: "Jupiter", 6: "Venus", 7: "Saturn"}
HORA_GOOD = {"Jupiter", "Venus", "Mercury", "Moon"}      # Shubha Hora
NIGHT_CHOGHADIYA = {
    0: ["Shubha", "Amrita", "Chara", "Roga", "Kala", "Labha", "Udvega"],
    1: ["Chara", "Roga", "Kala", "Labha", "Udvega", "Shubha", "Amrita"],
    2: ["Kala", "Labha", "Udvega", "Shubha", "Amrita", "Chara", "Roga"],
    3: ["Udvega", "Shubha", "Amrita", "Chara", "Roga", "Kala", "Labha"],
    4: ["Amrita", "Chara", "Roga", "Kala", "Labha", "Udvega", "Shubha"],
    5: ["Roga", "Kala", "Labha", "Udvega", "Shubha", "Amrita", "Chara"],
    6: ["Labha", "Udvega", "Shubha", "Amrita", "Chara", "Roga", "Kala"],
}
# Auspicious yogas: the nakshatras that make them on each weekday (0 = Sunday); nakshatra 0 = Ashwini
SARVARTHA_SIDDHI = {0: {0, 7, 11, 12, 18, 20, 25}, 1: {3, 4, 7, 16, 21}, 2: {0, 2, 8, 25}, 3: {2, 3, 4, 12, 16},
                    4: {0, 6, 7, 16, 26}, 5: {0, 6, 16, 21, 26}, 6: {3, 14, 21}}
AMRIT_SIDDHI = {0: 12, 1: 4, 2: 0, 3: 16, 4: 7, 5: 26, 6: 21}
RAVI_YOGA_COUNTS = {4, 6, 9, 10, 13, 20}          # the Moon's nakshatra counted from the Sun's (the Sun's is 1)
GANDA_MOOLA = {0, 8, 9, 17, 18, 26}
PANCHAKA_SIGNS = {10, 11}                          # the Moon in Kumbha or Meena
# the spans every event avoids; Ganda Moola and Panchak only lower a score, or are cut where a rule asks
HARD_AVOID = {"Rahu Kalam", "Yamaganda", "Gulika Kalam", "Dur Muhurta", "Varjyam", "Bhadra (Vishti)"}
BAD_YOGAS = {16, 26}                               # Vyatipata and Vaidhriti
TARAS = ["Janma", "Sampat", "Vipat", "Kshema", "Pratyak", "Sadhana", "Naidhana", "Mitra", "Parama Mitra"]
BAD_TARAS = {2, 4, 6}
GOOD_CHANDRA = {1, 3, 6, 7, 10, 11}               # houses of the transit Moon from the natal Moon
LAGNA_TYPES = ["movable", "fixed", "dual"]         # sign % 3
ASTA_ORB = {"Venus": (6, 10.0), "Jupiter": (5, 11.0)}   # body number, degrees from the Sun
MIN_WINDOW = 5 * MINUTE                            # Drikpanchang drops muhurtas shorter than 5 minutes
RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "muhurta_rules.json")


def _iso(jd: float, tz: float) -> str:
    y, m, d, h = E.jd_to_calendar(jd + tz / 24.0, True)
    s = int(round(h * 3600))
    if s >= 86400:                                  # rounding up to midnight: the next day, as a clock would read it
        s -= 86400
        y, m, d, _ = E.jd_to_calendar(jd + tz / 24.0 + 1.0, True)
    return "%04d-%02d-%02dT%02d:%02d:%02d" % (y, m, d, s // 3600, s % 3600 // 60, s % 60)


def segments(first: int, ends: list, count: int, start: float) -> list:
    """[(index, from, to)] across a day from the (index, end) pairs ``civil_day_panchanga`` gives; the last runs on
    past the day, so its ``to`` is None."""
    out, t, nxt = [], start, first
    for idx, end in ends:
        out.append((idx, t, end))
        t, nxt = end, (idx + 1) % count
    out.append((nxt, t, None))
    return out


def intersect(a: list, b: list) -> list:
    """The overlaps of two lists of (start, end) ranges."""
    out = []
    for s1, e1 in a:
        for s2, e2 in b:
            s, e = max(s1, s2), min(e1, e2)
            if s < e:
                out.append((s, e))
    return sorted(out)


def subtract(a: list, cuts: list) -> list:
    """The ranges of ``a`` with every range of ``cuts`` taken out."""
    out = list(a)
    for cs, ce in cuts:
        nxt = []
        for s, e in out:
            if ce <= s or cs >= e:
                nxt.append((s, e))
                continue
            if s < cs:
                nxt.append((s, cs))
            if ce < e:
                nxt.append((ce, e))
        out = nxt
    return sorted(out)


def _slots(start: float, stop: float, names: list, n: int = 8) -> list:
    step = (stop - start) / n
    return [(names[i % len(names)], start + i * step, start + (i + 1) * step) for i in range(n)]


def _lagna_table(place: E.BirthData, cfg, start: float, stop: float) -> list:
    """[(sign, from, to)] of the rising sign through [start, stop]: a 5-minute scan, each change narrowed by bisection."""
    sign = lambda t: int(E.lagna_at(t, place, cfg) // 30) % 12  # noqa: E731
    rows, t, cur, since = [], start, sign(start), start
    while t < stop:
        n = min(t + 5 * MINUTE, stop)
        s = sign(n)
        if s != cur:
            lo, hi = t, n
            for _ in range(14):
                mid = (lo + hi) / 2.0
                lo, hi = (mid, hi) if sign(mid) == cur else (lo, mid)
            rows.append((cur, since, hi))
            since, cur = hi, s
        t = n
    rows.append((cur, since, stop))
    return rows


def karana_name(i: int) -> str:
    return P.compute_karana(0.0, i * 6.0 + 0.1)["karana_name"]


def tithi_name(i: int) -> str:
    return "%s %s" % ("Shukla" if i < 15 else "Krishna", P.TITHI_NAMES[i])


def _raw(place: E.BirthData, cfg) -> dict:
    """The day at ``place`` (its date) as Julian days: the panchang limbs, the spans to avoid and to prefer, and the
    slots of each daily muhurta system."""
    d = JP.civil_day_panchanga(place, place.year, place.month, place.day, cfg)
    rise, set_, start, wd = d["sunrise"], d["sunset"], d["start"], d["weekday"]
    stop = d["horas"][-1][2]                         # the next sunrise
    limb = lambda k, n: segments(d[k], d[k + "_ends"], n, start)  # noqa: E731
    tithis, naks, yogas, karanas, moon_signs = limb("tithi", 30), limb("nakshatra", 27), limb("yoga", 27), limb("karana", 60), limb("moon_sign", 12)
    upto = lambda rows: [(i, a, b if b is not None else stop) for i, a, b in rows]  # noqa: E731
    spans = lambda rows, pick, name: [(name, a, b) for i, a, b in upto(rows) if pick(i)]  # noqa: E731
    sun_nak = int(JS.body_longitude(1, cfg, place)(start) // NAK)

    muhurta = (set_ - rise) / 15.0
    auspicious = ([("Abhijit Muhurta", rise + 7 * muhurta, rise + 8 * muhurta)] if wd != 3 else [])
    auspicious += [("Brahma Muhurta", rise - 96 * MINUTE, rise - 48 * MINUTE)]
    auspicious += spans(naks, lambda i: i in SARVARTHA_SIDDHI[wd], "Sarvartha Siddhi")
    auspicious += spans(naks, lambda i: i == AMRIT_SIDDHI[wd], "Amrit Siddhi")
    auspicious += spans(naks, lambda i: wd == 0 and i == 7, "Ravi Pushya")
    auspicious += spans(naks, lambda i: wd == 4 and i == 7, "Guru Pushya")
    auspicious += spans(naks, lambda i: (i - sun_nak) % 27 + 1 in RAVI_YOGA_COUNTS, "Ravi Yoga")
    avoid = [("Rahu Kalam", *d["rahu_kala"]), ("Yamaganda", *d["yamaganda"]), ("Gulika Kalam", *d["gulika_kala"])]
    avoid += [("Dur Muhurta", a, b) for a, b in d["durmuhurta"]] + [("Varjyam", a, b) for a, b in d["varjya"]]
    avoid += spans(karanas, lambda i: karana_name(i).startswith("Vishti"), "Bhadra (Vishti)")
    avoid += spans(naks, lambda i: i in GANDA_MOOLA, "Ganda Moola")
    avoid += spans(moon_signs, lambda i: i in PANCHAKA_SIGNS, "Panchak")
    return {
        "d": d, "rise": rise, "set": set_, "start": start, "stop": stop, "wd": wd,
        "tithis": tithis, "naks": naks, "yogas": yogas, "karanas": karanas, "moon_signs": moon_signs, "upto": upto,
        "auspicious": auspicious, "avoid": avoid,
        "cho_day": _slots(rise, set_, CM.CHOGHADIYA_ORDER_DAY[wd]), "cho_night": _slots(set_, stop, NIGHT_CHOGHADIYA[wd]),
        "gowri": _slots(rise, set_, P.GOWRI_DAY_ORDER[wd]) + _slots(set_, stop, P.GOWRI_NIGHT_ORDER[wd]),
        "horas": [(HORA_LORDS[lord], a, b) for lord, a, b in d["horas"]],
        "month": CAL.lunar_month(rise, d["tithi"], cfg, place.year, place.month),
    }


def day(place: E.BirthData, cfg, lunar: str = "purnimanta") -> dict:
    """The panchang and daily muhurtas of the civil day at ``place`` (its date; the clock time is not used)."""
    r = _raw(place, cfg)
    tz = place.tz_east_hours
    iso = lambda jd: _iso(jd, tz) if jd is not None else None  # noqa: E731
    span = lambda name, a, b, good=None: {"name": name, "start": iso(a), "end": iso(b), "good": good}  # noqa: E731
    limbs = lambda rows, name, good=lambda i: None: [span(name(i), a, b, good(i)) for i, a, b in rows]  # noqa: E731
    cho = lambda rows: [span(n, a, b, CM.CHOGHADIYA_QUALITY[n][1]) for n, a, b in rows]  # noqa: E731
    month = {k: v for k, v in r["month"].items() if not k.endswith("_jd")}
    d = r["d"]
    return {
        "date": "%04d-%02d-%02d" % (place.year, place.month, place.day),
        "weekday": WEEKDAYS[r["wd"]],
        "sunrise": iso(r["rise"]), "sunset": iso(r["set"]), "next_sunrise": iso(r["stop"]),
        "moonrise": iso(d["moonrise"]) if d["moonrise"] else None, "moonset": iso(d["moonset"]) if d["moonset"] else None,
        "month": {**month, "name": month[lunar]},
        "tithi": limbs(r["tithis"], tithi_name),
        "nakshatra": limbs(r["naks"], lambda i: P.NAKSHATRA_NAMES[i]),
        "yoga": limbs(r["yogas"], lambda i: P.NITYA_YOGA_NAMES[i][0], lambda i: P.NITYA_YOGA_NAMES[i][1]),
        "karana": limbs(r["karanas"], karana_name, lambda i: not karana_name(i).startswith("Vishti")),
        "moon_sign": limbs(r["moon_signs"], lambda i: SIGN_NAMES[i]),
        "avoid": [span(n, a, b, False) for n, a, b in r["avoid"]],
        "auspicious": [span(n, a, b, True) for n, a, b in r["auspicious"]],
        "choghadiya": {"day": cho(r["cho_day"]), "night": cho(r["cho_night"])},
        "hora": [span(n, a, b, n in HORA_GOOD) for n, a, b in r["horas"]],
        "gowri": [span(n, a, b, P.GOWRI_QUALITIES[n][1]) for n, a, b in r["gowri"]],
        "lagna": [span(SIGN_NAMES[i], a, b) for i, a, b in _lagna_table(place, cfg, r["rise"], r["stop"])],
    }


# ---------------------------------------------------------------------------
# Find a muhurta
# ---------------------------------------------------------------------------

def rules() -> dict:
    with open(RULES_PATH, encoding="utf-8") as f:
        return {e["id"]: e for e in json.load(f)["events"]}


def events() -> list:
    return [{"id": e["id"], "name": e["name"], "group": e["group"]} for e in rules().values()]


def tithi_allowed(rule: dict, i: int) -> bool:
    """Tithi ``i`` (0..29) by the rule's numbers within a paksha; Amavasya never, Purnima where the rule says."""
    n = i % 15 + 1
    if n == 15:
        return i == 14 and rule.get("purnima", False)
    return n in rule["tithis"]


def tara(natal_nak: int, nak: int) -> int:
    """Tarabala: 0 Janma .. 8 Parama Mitra, the transit nakshatra counted from the birth nakshatra."""
    return (nak - natal_nak) % 27 % 9


def chandra_house(natal_sign: int, sign: int) -> int:
    """Chandrabala: the house of the transit Moon from the natal Moon (1..12); 8 is Chandrashtama."""
    return (sign - natal_sign) % 12 + 1


def _at(rows: list, t: float) -> Optional[int]:
    return next((i for i, a, b in rows if a <= t < b), None)


def _combust(cfg, jd: float, planet: str) -> bool:
    body, orb = ASTA_ORB[planet]
    sun, p = JS.body_longitude(1, cfg)(jd), JS.body_longitude(body, cfg)(jd)
    return abs((p - sun + 180.0) % 360.0 - 180.0) < orb


def judge(place: E.BirthData, cfg, rule: dict, natal_moon: Optional[float] = None) -> dict:
    """One day for one event: a rejection reason (Drikpanchang's wording where it has one) or the windows, best first."""
    r = _raw(place, cfg)
    tz, name, wd, month = place.tz_east_hours, rule["name"], r["wd"], r["month"]
    iso = lambda jd: _iso(jd, tz)  # noqa: E731
    upto = r["upto"]
    tithis, naks, yogas, signs = upto(r["tithis"]), upto(r["naks"]), upto(r["yogas"]), upto(r["moon_signs"])
    out = {"date": "%04d-%02d-%02d" % (place.year, place.month, place.day), "weekday": WEEKDAYS[r["wd"]],
           "tithi": tithi_name(r["d"]["tithi"]), "nakshatra": P.NAKSHATRA_NAMES[r["d"]["nakshatra"]],
           "month": {k: month[k] for k in ("amanta", "purnimanta", "saura", "adhika", "kshaya")}, "windows": [], "reason": None, "short": None, "best": None}

    def no(reason, short):
        return {**out, "reason": reason, "short": short}

    if WEEKDAYS[wd] in rule["weekdays_avoid"]:
        return no("Prohibited weekday for %s" % name, "Weekday")
    if month["adhika"]:
        return no("Adhika (leap) month", "Adhika month")
    if month["kshaya"]:
        return no("Kshaya month: %s is lost from this year" % month["kshaya"], "Kshaya month")
    if month["amanta"] in rule["months_avoid"]:
        return no("%s is not an auspicious month for %s" % (month["amanta"], name), "Month closed")
    sun_sign = int(JS.body_longitude(1, cfg)(r["rise"]) // 30)
    if rule.get("kharmas") and sun_sign in (8, 11):
        return no("Kharmas: the Sun is in %s" % SIGN_NAMES[sun_sign], "Kharmas")
    for planet in rule.get("asta", []):
        if _combust(cfg, r["rise"], planet):
            return no("%s is combust (%s Tara Asta)" % (planet, "Shukra" if planet == "Venus" else "Guru"), "%s combust" % planet)

    natal_nak = int(natal_moon // NAK) if natal_moon is not None else None
    natal_sign = int(natal_moon // 30) if natal_moon is not None else None
    good_naks = set(range(27)) if rule["nakshatras"] == "any" else {P.NAKSHATRA_NAMES.index(n) for n in rule["nakshatras"]}
    ok_t = [(a, b) for i, a, b in tithis if tithi_allowed(rule, i)]
    ok_n = [(a, b) for i, a, b in naks if i in good_naks]
    if not ok_t:
        return no("Prohibited tithi for %s" % name, "Tithi")
    if not ok_n:
        return no("Auspicious nakshatra not available", "Nakshatra")
    span = [(r["rise"], r["stop"] if rule.get("night") else r["set"])]
    base = intersect(intersect(ok_t, ok_n), span)
    if not base:
        return no("Prohibited tithi is corrupting auspicious nakshatra", "Tithi")
    cuts = [(a, b) for n, a, b in r["avoid"] if n in HARD_AVOID or (n == "Panchak" and rule.get("panchak"))]
    cuts += [(a, b) for i, a, b in yogas if i in BAD_YOGAS]
    free = subtract(base, cuts)
    if natal_sign is not None:
        ashtama = [(a, b) for i, a, b in signs if chandra_house(natal_sign, i) == 8]
        if free and not subtract(free, ashtama):
            return no("Chandrashtama: the Moon is 8th from the birth Moon", "Chandrashtama")
        free = subtract(free, ashtama)
    lagnas = _lagna_table(place, cfg, r["rise"], r["stop"])
    pieces = [(s, a, b) for s, ls, le in lagnas for a, b in intersect(free, [(ls, le)]) if b - a >= MIN_WINDOW]
    if not pieces:
        return no("Available auspicious time is too short for %s" % name, "Too short")

    by_name = lambda rows, a, b: {n for n, s, e in rows if s < b and a < e}  # noqa: E731
    windows = []
    for s, a, b in pieces:
        mid = (a + b) / 2.0
        t, n, y = _at(tithis, mid), _at(naks, mid), _at(yogas, mid)
        score, why = 60, [{"label": "%s nakshatra" % P.NAKSHATRA_NAMES[n], "good": True}, {"label": tithi_name(t), "good": True}]

        def add(points, label, good):
            nonlocal score
            score += points
            why.append({"label": label, "good": good})
        if LAGNA_TYPES[s % 3] in rule["lagna"]:
            add(10, "%s lagna (%s)" % (SIGN_NAMES[s], LAGNA_TYPES[s % 3]), True)
        if rule.get("shukla_bonus") and t < 15:
            add(6, "Waxing Moon", True)
        elif t >= 25:
            add(-6, "Late waning Moon", False)
        if P.NITYA_YOGA_NAMES[y][1]:
            add(4, "%s yoga" % P.NITYA_YOGA_NAMES[y][0], True)
        else:
            add(-8, "%s yoga" % P.NITYA_YOGA_NAMES[y][0], False)
        for good in sorted(by_name(r["auspicious"], a, b) - {"Brahma Muhurta"}):
            add(10 if good == "Abhijit Muhurta" else 6, good, True)
        cho = next((c for c, cs, ce in r["cho_day"] + r["cho_night"] if cs <= mid < ce), None)
        if cho:
            add(4 if CM.CHOGHADIYA_QUALITY[cho][1] else -4, "%s choghadiya" % cho, CM.CHOGHADIYA_QUALITY[cho][1])
        for bad in sorted(by_name(r["avoid"], a, b) - HARD_AVOID - ({"Panchak"} if rule.get("panchak") else set())):
            add(-6, bad, False)
        if natal_nak is not None:
            k = tara(natal_nak, n)
            add(-15 if k in BAD_TARAS else 8, "Tarabala: %s" % TARAS[k], k not in BAD_TARAS)
            h = chandra_house(natal_sign, _at(signs, mid))
            add(8 if h in GOOD_CHANDRA else -6, "Chandrabala: Moon %s from the birth Moon" % _ordinal(h), h in GOOD_CHANDRA)
        windows.append({"start": iso(a), "end": iso(b), "score": max(0, min(100, score)), "lagna": SIGN_NAMES[s],
                        "nakshatra": P.NAKSHATRA_NAMES[n], "tithi": tithi_name(t), "reasons": why})
    windows.sort(key=lambda w: -w["score"])
    return {**out, "windows": windows[:6], "best": windows[0]["score"]}


def _ordinal(n: int) -> str:
    return "%d%s" % (n, "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))


def find(place: E.BirthData, cfg, event: str, natal_moon: Optional[float] = None) -> dict:
    """Every day of the month of ``place``'s date judged for ``event``.
    shortcut: the place's zone is held for the whole month, so a daylight-saving change mid-month shifts later days by
    an hour; upgrade by asking the zone per day."""
    rule = rules().get(event)
    if rule is None:
        raise ValueError("No such event: %s" % event)
    n = calendar.monthrange(place.year, place.month)[1]
    days = [judge(dataclasses.replace(place, day=k), cfg, rule, natal_moon) for k in range(1, n + 1)]
    return {"event": {"id": rule["id"], "name": rule["name"]}, "personal": natal_moon is not None,
            "good_days": sum(1 for x in days if x["windows"]), "days": days}
