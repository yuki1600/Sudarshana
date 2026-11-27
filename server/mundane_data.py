"""The Mundane tab's databases (data/mundane) and the astrological factors of a selection of their events, with a control sample."""
from __future__ import annotations

import functools
import gzip
import json
import random
from collections import Counter
from datetime import date
from pathlib import Path

from core_logic import ephemeris as E

from . import settings as SET

DIR = Path(__file__).resolve().parent.parent / "data" / "mundane"
# each set's files; events has none of its own: all of it is the Rodden library's (rodden_events.json, laid over every set by raw_dataset)
SETS = {"disasters": ("earthquakes", "tsunamis", "volcanoes", "disasters"), "nations": ("nations",), "elections": ("elections", "oaths"), "sports": ("sports",),
        "events": (), "finance": ("finance",)}
BODIES = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
TIMED = ("exact", "reported", "approx")   # a time good enough for the Lagna and houses
MAX_EVENTS = 5000
CONTROL = 1000


def _file(name: str) -> dict:
    """A data file, read each time: the parsed records are not kept (Finance's would hold over 100 MB); payload() and summary() are."""
    path = DIR / f"{name}.json"
    if not path.exists():
        return {"_about": "", "records": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _year(r: dict) -> int:
    return -int(r["date"][1:].split("-")[0]) if r["date"].startswith("-") else int(r["date"].split("-")[0])


def dropped(r: dict, quake_moments: frozenset = frozenset()) -> str | None:
    """Why a record is left out of the databases, or None to keep it: only events whose time is recorded exactly, with their date and place, stay."""
    if r["id"].startswith("fi-"):
        return None   # a company stays whatever is known of it: a listing timed at the opening bell, a founding day, or no date (a startup)
    if not r.get("time"):
        return "no oath time" if r["id"].startswith("el-") else "no time"
    if r.get("time_confidence") != "exact" and not (r["id"].startswith("el-") and r.get("time_confidence") in TIMED):   # an oath's scheduled/reported ceremony time is kept
        return "time not exact"   # reported, announced or approximate: only a time recorded to the minute is kept
    if not r.get("place"):
        return "no place"
    if r.get("gregorian") is False:
        return "julian date"
    if (r["id"][:2] in ("ea", "ts") or (r["id"].startswith("ro-") and r.get("type") in ("earthquake", "tsunami"))) and _year(r) < 1900:
        return "before 1900"   # pre-instrumental: NCEI's times are reconstructed from accounts
    if r["id"].startswith("ts") and r.get("validity", 4) < 3:
        return "doubtful tsunami"
    if r["id"].startswith("ts") and (r["date"], r["time"][:5]) in quake_moments:
        return "same as an earthquake"
    if r["id"].startswith("el-") and not r.get("oath_known"):
        return "no oath time"
    return None


def _files(name: str) -> dict[str, dict]:
    """A set's data files and its Rodden file, each read once."""
    return {f: _file(f) for f in (*SETS[name], f"rodden_{name}")}


def raw_dataset(name: str, rodden: bool = True, files: dict[str, dict] | None = None) -> list[dict]:
    """A set's records before cleaning. A curated record that is the same event as an NCEI one (same_as) lends it its name and article.
    With ``rodden``, the Rodden library's charts (rodden_<set>.json, tools/mundane_rodden.py) are laid over them: one of an event
    the set has lends it its time where it has none to the minute; one of an event it lacks joins it."""
    files = files or _files(name)
    records = [r for f in SETS[name] for r in files[f]["records"]]
    same = {r["same_as"]: r for r in records if r.get("same_as")}
    if same:
        records = [{**r, "name": same[r["id"]]["name"], "article": same[r["id"]]["source"], "landmark": True} if r["id"] in same else r
                   for r in records if not r.get("same_as")]
    if rodden:
        ro = files[f"rodden_{name}"]["records"]
        lend = {r["same_as"]: r for r in ro if r.get("same_as") and r.get("time")}
        records = [{**r, **{k: lend[r["id"]][k] for k in ("date", "time", "tz_east", "gregorian", "time_source")}, "time_confidence": "exact",
                    "rodden_source": lend[r["id"]]["source"]} if r["id"] in lend and r.get("time_confidence") != "exact" else r
                   for r in records] + [r for r in ro if not r.get("same_as")]
    return records


def quake_moments(records: list[dict]) -> frozenset:
    return frozenset((r["date"], r["time"][:5]) for r in records if r["id"].startswith("ea") and r.get("time"))


def dataset(name: str) -> dict:
    """One of the sets, cleaned: its files' notes, the records kept and how many were left out for each reason. Built afresh each
    call; what the web is sent is kept by payload() and summary()."""
    files = _files(name)
    raw = raw_dataset(name, files=files)
    moments = quake_moments(raw)
    records, removed = [], {}
    for r in raw:
        why = dropped(r, moments)
        if why:
            removed[why] = removed.get(why, 0) + 1
        else:
            records.append(r)
    if name == "nations":   # a country whose primary chart was untimed: its earliest timed alternate becomes primary
        has = {r["iso2"] for r in records if r["primary"]}
        for r in sorted(records, key=_year):
            if r["iso2"] not in has:
                records[records.index(r)] = {**r, "primary": True}
                has.add(r["iso2"])
    return {"name": name, "about": {f: d["_about"] for f, d in files.items() if d["_about"]}, "records": records, "removed": removed}


@functools.cache
def payload(name: str) -> bytes:
    """A set as its Research tab is sent it, gzipped: made the first time the tab is opened, then kept (2 MB at most) in place
    of its parsed records."""
    return gzip.compress(json.dumps(dataset(name), ensure_ascii=False, separators=(",", ":")).encode(), 6)


KIND = {"disasters": "type", "events": "type", "sports": "sport", "elections": "office", "nations": "event", "finance": "sector"}


def _when(r: dict) -> tuple:
    """The web's date order: year (BCE negative), month, day, then the hour, an untimed day at noon."""
    y, m, d = r["date"].lstrip("-").split("-")[:3]
    return (-int(y) if r["date"].startswith("-") else int(y), int(m), int(d), int(r["time"][:2]) if r.get("time") else 12)


def _top(values) -> list[list]:
    """[value, count], most first, then a to z, an empty value as '—': the web's countBy."""
    return sorted(([k, n] for k, n in Counter(v or "—" for v in values).items()), key=lambda kn: (-kn[1], kn[0]))


@functools.cache
def summary() -> dict:
    """Each set's Overview card without its records: its size, span and country count, its five top kinds and countries, and five
    notable records (the deadliest disasters, the most valuable companies, else the latest), whole so that they open."""
    out = {}
    for name in SETS:
        recs = dataset(name)["records"]
        dated = sorted((r for r in recs if r.get("date")), key=_when)
        worth = lambda r: r.get("market_cap") or r.get("valuation") or 0
        notable = (sorted((r for r in recs if isinstance(r.get("deaths"), (int, float)) and r["deaths"]), key=lambda r: -r["deaths"]) if name == "disasters"
                   else sorted((r for r in recs if worth(r)), key=lambda r: -worth(r)) if name == "finance" else dated[::-1])[:5]
        countries = _top(r["country"] for r in recs if r.get("country"))
        out[name] = {"count": len(recs), "countries": len(countries), "top_countries": countries[:5], "kinds": _top(str(r.get(KIND[name]) or "") for r in recs)[:5],
                     "first": dated[0]["date"] if dated else None, "last": dated[-1]["date"] if dated else None, "notable": notable,
                     "status": dict(Counter(r["status"] for r in recs)) if name == "finance" else None}
    return out


@functools.lru_cache(maxsize=1)
def _index() -> dict[str, dict]:
    return {r["id"]: r for name in SETS for r in dataset(name)["records"] if r.get("date")}   # a company without a date has no chart


def birth_of(r: dict) -> E.BirthData:
    """A record's moment as birth data; a record without a time is its local noon."""
    y, m, d = (int(x) for x in r["date"].lstrip("-").split("-"))
    if r["date"].startswith("-"):
        y = -y
    hh = 12.0
    if r.get("time"):
        parts = [float(x) for x in r["time"].split(":")]
        hh = parts[0] + parts[1] / 60 + (parts[2] if len(parts) > 2 else 0) / 3600
    return E.BirthData(y, m, d, hh, float(r["tz_east"]), float(r["lon"]), float(r["lat"]), gregorian=bool(r.get("gregorian", True)), place=r.get("place", ""))


@functools.lru_cache(maxsize=64)
def _eclipses(century: int) -> tuple:
    """(max_jd, kind) of every solar and lunar eclipse in a century."""
    jd0, jd1 = E.julian_day_ut(century * 100, 1, 1, 0, century * 100 >= 1583), E.julian_day_ut(century * 100 + 100, 1, 1, 0, century * 100 + 100 >= 1583)
    out = []
    for kind in ("solar", "lunar"):
        j = jd0
        while True:
            e = E.next_eclipse(j, kind)
            if e["max_jd"] > jd1:
                break
            out.append((e["max_jd"], kind))
            j = e["max_jd"] + 1
    return tuple(sorted(out))


def _nearest_eclipse(jd: float, kind: str) -> float | None:
    """Signed days from the nearest eclipse of this kind (negative: the eclipse comes after)."""
    c = int((jd - 1721425.5) // 36524.25)   # the century of the moment, near enough at the edges
    best = None
    for cc in (c - 1, c, c + 1):
        for ejd, k in _eclipses(cc):
            if k == kind and (best is None or abs(jd - ejd) < abs(best)):
                best = jd - ejd
    return round(best, 2) if best is not None else None


def _factors(jd: float, b: E.BirthData, cfg, timed: bool, moon_ok: bool, eclipses: bool) -> dict:
    pos = E.planet_positions(jd, cfg, b)
    lagna = E.lagna_at(jd, b, cfg) if timed else None
    rows = {}
    for n in BODIES:
        if n == "Moon" and not moon_ok:
            continue
        lon = pos[n]["lon"]
        rows[n] = [int(lon // 30), int(lon * 3 // 40), 1 if pos[n]["retrograde"] and n not in ("Rahu", "Ketu") else 0,
                   (int(lon // 30) - int(lagna // 30)) % 12 + 1 if lagna is not None else None]
    out = {"p": rows, "lagna": int(lagna // 30) if lagna is not None else None, "weekday": int(jd + b.tz_east_hours / 24 + 1.5) % 7}   # 0 = Sunday: the local civil day
    if moon_ok:
        el = (pos["Moon"]["lon"] - pos["Sun"]["lon"]) % 360
        out["tithi"] = int(el // 12) + 1
        out["phase"] = round(el, 1)
    if eclipses:
        out["solar"] = _nearest_eclipse(jd, "solar")
        out["lunar"] = _nearest_eclipse(jd, "lunar")
    return out


@functools.lru_cache(maxsize=20000)
def _event_factors(rid: str, settings_json: str) -> dict:
    r = _index()[rid]
    cfg = SET.config(SET.SettingsIn.model_validate_json(settings_json))
    b = birth_of(r)
    conf = r.get("time_confidence", "date")
    year = b.year
    return {"id": rid, "jd": round(b.jd_ut, 4), "year": year, "timed": conf in TIMED,
            **_factors(b.jd_ut, b, cfg, conf in TIMED, conf != "month", -2000 <= year <= 2200)}


def patterns(ids: list[str], settings) -> dict:
    """The factors of the chosen events and of a control sample: random moments over the same years, at the events' own places."""
    index = _index()
    known = [i for i in dict.fromkeys(ids) if i in index]
    capped = len(known) > MAX_EVENTS
    known = known[:MAX_EVENTS]
    s = settings or SET.SettingsIn()
    key = s.model_dump_json()
    events = [_event_factors(i, key) for i in known]
    control = []
    if events:
        cfg = SET.config(s)
        lo, hi = min(e["jd"] for e in events), max(e["jd"] for e in events)
        if hi - lo < 365.25:   # one season is no baseline for the slow planets: widen to a year either side
            lo, hi = lo - 365.25, hi + 365.25
        rng = random.Random(f"{len(events)}:{lo:.3f}:{hi:.3f}")
        recs = [index[i] for i in known]
        timed_share = sum(e["timed"] for e in events) / len(events)
        for _ in range(CONTROL):
            jd = rng.uniform(lo, hi)
            r = rng.choice(recs)
            b = E.BirthData(2000, 1, 1, 12.0, 0.0, float(r["lon"]), float(r["lat"]))
            timed = rng.random() < timed_share
            control.append({"jd": round(jd, 4), "timed": timed, **_factors(jd, b, cfg, timed, True, True)})
    return {"events": events, "control": control, "capped": capped, "unknown": len({i for i in ids if i not in index})}


def sanity(name: str, r: dict) -> list[str]:
    """What is wrong with a record, for the tests: required fields, ranges and a real date."""
    if name == "finance" and not r.get("date"):   # a company with no listing or founding day: listed, without a chart
        bad = [k for k in ("id", "name", "status", "source") if not r.get(k)]
        return [f"missing {bad}"] if bad else []
    bad = [k for k in ("id", "date", "tz_east", "lat", "lon", "time_confidence", "source") if r.get(k) in (None, "")]
    if bad:
        return [f"missing {bad}"]
    errs = []
    if not -90 <= r["lat"] <= 90 or not -180 <= r["lon"] <= 180:
        errs.append("lat/lon out of range")
    if not -14 <= r["tz_east"] <= 14:
        errs.append("tz out of range")
    if r["time_confidence"] not in ("exact", "reported", "approx", "date", "month"):
        errs.append("bad time_confidence")
    y, m, d = (int(x) for x in r["date"].lstrip("-").split("-"))
    if r.get("gregorian", True) and not r["date"].startswith("-"):
        try:
            date(y, m, d)
        except ValueError:
            errs.append("not a date")
    elif not (1 <= m <= 12 and 1 <= d <= 31):
        errs.append("not a date")
    if r.get("time") and not all(x.isdigit() for x in r["time"].split(":")):
        errs.append("bad time")
    return errs
