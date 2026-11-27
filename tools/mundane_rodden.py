"""Cross-check the Rodden library's event charts (BTS/, read by databases/build_rodden_db.py) with the Research databases.

A Rodden chart is the same event as a Research record when both moments agree within 3 minutes (whatever the places),
or when the day agrees, the kind is the same and the places are within 500 km. Then Research takes Rodden's time where it
has none to the minute, or a reported one Rodden confirms; where both have a time and they disagree, Research keeps its
own and the disagreement is listed. A Rodden event Research lacks is added to it as a new record; one of no kind Research
has (TV shows, space flights, attacks, UFO sightings...) goes to Events, a database of its own. Only Research changes:
the Rodden library stays as it is.

Writes data/mundane/rodden_disasters.json, rodden_nations.json and rodden_events.json, which server/mundane_data.py lays
over the Research databases, and data/mundane/RODDEN.md, the cross-check.

Re-runnable after a change to BTS/ or data/mundane: .venv/bin/python -m tools.mundane_rodden
"""
from __future__ import annotations

import json
import math
import os
import re
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

import swisseph as swe

from server import mundane_data as M
from tools.mundane_ncei import iso_codes

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "databases"))
import build_rodden_db as R  # noqa: E402

SAME_MOMENT, SAME_DAY = 3 / 1440, 1.1   # days: one moment, and one day either side (an untimed record is cast at local noon)
NEAR = {"disasters": 500, "nations": 1000, "elections": 100}   # km, for a match on the day alone
# a Rodden chart's kind from its name, first hit wins; deliberate acts (attacks, shootings, wars, tests) are no disaster
NOT_EVENTS = re.compile(r"terror|shooting|bomb|massacre|attack|assassinat|murder|execution|suicide|electrocut|military|\bwar\b|nuclear|ufo|phenomena|"
                        r"space|celestial|twins|maiden|voyage|\bfirst\b|performance", re.I)
KINDS = [
    ("tsunami", r"tsunami(?!.*quake)"), ("earthquake", r"earthquake|quake|seism"), ("volcano", r"erupt|volcan|surtsey"),
    ("cyclone", r"hurricane|typhoon|cyclone"), ("tornado", r"tornado"), ("storm", r"storm|blizzard|derecho"),
    ("flood", r"flood|dam broke|dam failure|glacier burst"), ("avalanche", r"avalanche"), ("landslide", r"landslide|mudslide|rockslide|\bslide\b"),
    ("heatwave", r"heat ?wave"), ("meteor", r"meteor|asteroid|tunguska"),
    ("air crash", r"plane|flight|airlines|airways|airbus|boeing|lockheed|concorde|hindenburg|zeppelin|aircraft|airshow|helicopter|air france|\bjet\b"),
    ("rail accident", r"train|\brail|derail|amtrak|tgv"), ("explosion", r"explosion|blast"), ("shipwreck", r"sinking|sank|capsi[sz]|ferry|shipwreck"),
    ("wildfire", r"^nature.*\bfire\b|wildfire|bushfire|forest fire"), ("fire", r"\bfire\b|fireworks"),
    ("nation", r"^nation\b"), ("oath", r"^political.*inaugurat"),
]
PEOPLE = re.compile(r"(twins|triplets|quadruplets|quintuplets|sextuplets|septuplets|octuplets|conjoined)\b", re.I)
# Events: the event charts of no other kind, typed by their name (Rodden's own prefixes, mostly), else by their category keywords
EVENT_TYPES = [
    ("assassination", r"assassinat"), ("terror attack", r"terror|bomb|attack|massacre|hostage|hijack"), ("shooting", r"shooting"),
    ("nuclear test", r"nuclear"), ("military", r"^military|\bwar\b|battle|invasion"), ("UFO sighting", r"ufo"),
    ("space flight", r"^space|spacecraft|spaceship|launch|apollo|shuttle|\bsts-|satellite|rocket|on moon"), ("aviation", r"^aviation"),
    ("crime", r"robbery|heist|\btrial\b|kidnap|murder"),
    ("celestial", r"^celestial|^synodic|conjunction|eclipse|comet"), ("business", r"^business|shares|stock|company|website"),
    ("organization", r"^astrology|^social|association|society|\bclub\b|\bparty\b"), ("city", r"^cities"), ("sports event", r"^sports|olympic"),
    ("science", r"^science"), ("law", r"^law\b"), ("political", r"^political|sovereignty|referendum|treaty|independence|constitution"),
    ("phenomenon", r"^phenomena"), ("death", r"^mortality"), ("historic", r"^historic"), ("inauguration", r"inaugurat"),
]
CATEGORY_TYPES = [("TV show", "Release dates (TV series)"), ("TV show", "Foundings (TV series)"), ("space flight", "Space"),
                  ("terror attack", "Terrorist attacks"), ("business", "Business/Finance"), ("business", "Company Founding"),
                  ("sports event", "Sports contests"), ("military", "Military action"), ("political", "Political"),
                  ("historic", "Historic milestones"), ("organization", "Foundings")]
FAMILY = {"earthquake": {"earthquake", "tsunami"}, "tsunami": {"tsunami", "earthquake"}, "cyclone": {"cyclone", "storm", "winter storm"},
          "storm": {"storm", "winter storm", "cyclone"}, "fire": {"wildfire"}}
STATES = {"england": "GB", "scotland": "GB", "wales": "GB", "northern ireland": "GB", "russian federation": "RU", "south korea": "KR",
          "north korea": "KP", "taiwan": "TW", "iran": "IR", "syria": "SY", "vietnam": "VN", "laos": "LA", "bolivia": "BO", "venezuela": "VE",
          "tanzania": "TZ", "czech republic": "CZ", "east timor": "TL", "ivory coast": "CI", "burma": "MM", "macedonia": "MK"}


def kind_of(name: str, cats: list[str]) -> str | None:
    n = name.lower()
    if NOT_EVENTS.search(n):
        return None
    for k, pat in KINDS:
        if re.search(pat, n):
            return k
    t = " ".join(cats)
    return "other" if "Natural Disasters" in t else "accident" if re.match(r"(accident|disaster|mortality)", n) or "Accidents" in t else None


def event_type(name: str, cats: list[str]) -> str:
    n = name.lower().lstrip("\u200e")
    if n.startswith(("entertainment", "first performance")):
        return "TV show" if any("TV series" in c for c in cats) else "entertainment"
    for t, pat in EVENT_TYPES:
        if re.search(pat, n):
            return t
    return next((t for t, c in CATEGORY_TYPES if any(x.strip().startswith(c) for x in cats)), "other")


def km(a1: float, o1: float, a2: float, o2: float) -> float:
    p1, p2, dl = math.radians(a1), math.radians(a2), math.radians(o2 - o1)
    return 6371 * math.acos(max(-1.0, min(1.0, math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl))))


def ymd(y: int, m: int, d: int) -> str:
    return f"-{-y:04d}-{m:02d}-{d:02d}" if y < 0 else f"{y:04d}-{m:02d}-{d:02d}"


def hms(h: float) -> str:
    s = round(h * 3600)
    return f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}"


def utc(jd: float, gregorian: bool) -> tuple[str, str]:
    y, m, d, h = swe.revjul(jd, swe.GREG_CAL if gregorian else swe.JUL_CAL)
    return ymd(y, m, d), hms(h)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).strip("-")


def countries() -> dict[str, str]:
    """Country, state and province names to ISO codes: GeoNames' countries, then their first-level divisions."""
    out = {}
    db = ROOT / "databases" / "places.db"
    if db.exists():
        with sqlite3.connect(db) as c:
            for key, name in c.execute("select key, name from admin1"):
                out.setdefault(name.lower(), key.split(".")[0])
    return {**out, **iso_codes(), **STATES}


def rodden_events() -> list[dict]:
    """The library's event charts (as build_rodden_db keeps them: AA first, duplicate spellings dropped) that have a kind."""
    seen, out = set(), []
    for folder in R.FOLDERS:
        for dp, _, fs in os.walk(ROOT / "BTS" / folder):
            for f in sorted(fs):
                path = os.path.join(dp, f)
                try:
                    c = R.chart(path)
                except (ValueError, KeyError):
                    continue
                if c["dup"] in seen:
                    continue
                seen.add(c["dup"])
                with open(path, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
                main = R.fields(R.section(text, "MAIN BIRTH DATA"))
                if main.get("gender") != "N/A" or PEOPLE.match(c["name"]):   # people: twins and the like are births, not events
                    continue
                cats = R.section(text, "CATEGORY KEYWORDS").splitlines()
                k = kind_of(c["name"], cats) or "event"
                b = c["birth"]
                jd = swe.julday(b["year"], b["month"], b["day"], b["hour_local"] - b["tz_east_hours"], swe.GREG_CAL if b["gregorian"] else swe.JUL_CAL)
                bio = re.sub(r"^Link to Wikipedia biography\s*$", "", R.section(text, "BIOGRAPHY"), flags=re.M).strip()
                out.append({**c, "kind": k, "type": event_type(c["name"], cats) if k == "event" else None, "jd": jd, "bio": bio, "datasource": main.get("datasource", ""),
                            "url": "https://www.astro.com/astro-databank/" + quote(c["name"].replace(" ", "_"), safe=",:()'")})
    return out


def research() -> dict[str, list[tuple[dict, float]]]:
    """Every Research record before cleaning, without this tool's own files, with its moment (an untimed one at local noon).
    Finance is left out: tools/mundane_finance.py takes the library's first-trade charts itself, and a startup may have no date."""
    return {s: [(r, M.birth_of(r).jd_ut) for r in M.raw_dataset(s, rodden=False)] for s in M.SETS if s != "finance"}


def match(e: dict, recs: list[tuple[dict, float]], set_: str) -> tuple[dict, float, float] | None:
    near = [(r, jd, km(e["birth"]["latitude"], e["birth"]["longitude_east"], r["lat"], r["lon"])) for r, jd in recs if abs(jd - e["jd"]) <= SAME_DAY]
    moment = [x for x in near if x[0].get("time") and abs(x[1] - e["jd"]) <= SAME_MOMENT and x[2] <= 3000]
    if moment:   # nearest first: Pakistan and India became independent in the same minute
        return min(moment, key=lambda x: x[2])
    fam = FAMILY.get(e["kind"], {e["kind"]})
    day = [x for x in near if x[2] <= NEAR[set_] and (set_ != "disasters" or x[0].get("type") in fam)]
    return min(day, key=lambda x: (abs(x[1] - e["jd"]) if x[0].get("time") else 1, x[2])) if day else None


def name_of(e: dict) -> str:
    """"Nature:Earthquake:Leeward Islands 1974" -> "Earthquake Leeward Islands 1974"."""
    return re.sub(r"\s*:\s*", " ", re.sub(r"^[A-Za-z .]+:\s*", "", e["name"])).strip() or e["name"]


def new_record(e: dict, set_: str, iso: dict[str, str]) -> dict | None:
    b = e["birth"]
    place = b["place"]
    country = place.rsplit(", ", 1)[-1]
    code = iso.get(country.lower())
    if code == "US" and country.lower() != "united states":
        country = "United States"
    r = {"date": ymd(b["year"], b["month"], b["day"]), "time": hms(b["hour_local"]), "tz_east": b["tz_east_hours"], "gregorian": b["gregorian"],
         "time_confidence": "exact", "time_source": f"Rodden {e['rating']}: {e['datasource']}", "lat": b["latitude"], "lon": b["longitude_east"],
         "place": place, "country": country, **({"iso2": code} if code else {}), "source": e["url"], "rodden": [e["name"]]}
    if e["bio"]:
        r["notes"] = e["bio"] if len(e["bio"]) <= 400 else e["bio"][:400].rsplit(" ", 1)[0] + "…"
    if set_ == "nations":
        if not code:
            return None
        n = e["name"].lower()
        event = next((v for k, v in (("independ", "independence"), ("republic", "republic"), ("reunif", "union"), ("union", "union"),
                                     ("constitution", "constitution")) if k in n), "founding")
        paren = re.search(r"\(([^)]+)\)", e["name"])
        return {**r, "iso2": code, "chart_name": f"{paren.group(1) if paren else event.capitalize()} (Rodden)", "event": event, "primary": False}
    return {**r, "type": e["type"] if set_ == "events" else e["kind"], "name": name_of(e)}


def main() -> None:
    iso, recs, events = countries(), research(), rodden_events()
    out = {s: [] for s in ("disasters", "nations", "events")}
    ids, report, fills, matches = set(), defaultdict(list), defaultdict(list), []
    added: dict[tuple, dict] = {}
    for e in events:
        set_ = {"nation": "nations", "oath": "elections", "event": "events"}.get(e["kind"], "disasters")
        base = rid = "ro-" + slug(e["name"])
        n = 1
        while rid in ids:
            n += 1
            rid = f"{base}-{n}"
        ids.add(rid)
        m = match(e, recs[set_], set_) if set_ != "events" else None
        if not m:
            r = new_record(e, set_, iso) if set_ in ("disasters", "nations") else None
            if r is None:   # an oath Elections lacks, a nation of no known country, or an event of no other kind: Events
                set_, r = "events", new_record({**e, "type": e["type"] or {"oath": "inauguration"}.get(e["kind"], e["kind"])}, "events", iso)
            key = (set_, round(e["jd"] * 1440))
            if key in added:   # the same moment under another name: one record, both names
                added[key]["rodden"].append(e["name"])
            else:
                added[key] = {"id": rid, **r}
                out[set_].append(added[key])
            continue
        r, jd, dist = m
        delta = round((e["jd"] - jd) * 1440)
        exact = r.get("time_confidence") == "exact"
        outcome = ("agree" if abs(delta) <= 3 else "time differs") if r.get("time") and (exact or abs(delta) > 3) else "timed from Rodden"
        if outcome == "agree" and dist > 300:
            outcome = "place differs"
        entry = {"id": rid, "same_as": r["id"], "rodden": [e["name"]], "rating": e["rating"], "outcome": outcome,
                 "delta_min": delta if r.get("time") else None, "km": round(dist), "source": e["url"]}
        if outcome == "timed from Rodden":
            entry["date"], entry["time"] = utc(e["jd"], r.get("gregorian", True))
            entry.update(tz_east=0, gregorian=r.get("gregorian", True), time_source=f"Rodden {e['rating']}: {e['name']}")
            fills[r["id"]].append((entry, e["jd"]))
        if set_ in out:
            out[set_].append(entry)
        matches.append((entry, e, r, dist))
    for rid, fs in fills.items():   # two Rodden charts that give one event different times: neither is taken
        if max(j for _, j in fs) - min(j for _, j in fs) > SAME_MOMENT:
            for entry, _ in fs:
                for k in ("date", "time", "tz_east", "gregorian", "time_source"):
                    entry.pop(k)
                entry["outcome"] = "Rodden charts disagree"
    for entry, e, r, dist in matches:
        report[entry["outcome"]].append((e, r, round((e["jd"] - M.birth_of(r).jd_ut) * 1440), dist))
    about = {"disasters": "The Rodden library's AA- and A-rated disaster charts (Astro-Databank): those of an event the other files lack, and, with same_as, "
                          "those of an event they have, which lend it their time where it has none to the minute. Local time at tz_east; a lent time is UTC.",
             "nations": "The Rodden library's AA- and A-rated national charts (Astro-Databank), as rodden_disasters.json does for disasters.",
             "events": "The Rodden library's AA- and A-rated charts of events of no other database's kind (Astro-Databank): TV shows, space flights, "
                       "attacks, UFO sightings, foundings, celestial events and more; type is the kind. Local time at tz_east."}
    for s, records in out.items():
        with open(M.DIR / f"rodden_{s}.json", "w", encoding="utf-8") as f:
            json.dump({"_about": about[s], "records": records}, f, ensure_ascii=False, indent=1)
            f.write("\n")
    write_report(events, report, out)


def write_report(events: list[dict], report: dict, out: dict) -> None:
    def when(e):
        return "%s %s UTC" % utc(e["jd"], e["birth"]["gregorian"])

    def theirs(r):
        return f"{r['date']} {r.get('time') or '(no time)'}{'' if not r.get('time') else ' UTC' if not r.get('tz_east') else ' UTC%+g' % r['tz_east']}"

    kinds = Counter(e["type"] or e["kind"] for e in events)
    matched = sum(len(v) for v in report.values())
    new = [r for s in out.values() for r in s if not r.get("same_as")]
    lines = ["# Rodden library × Research databases", "",
             "The cross-check of tools/mundane_rodden.py: the Rodden library's event charts (AA and A rated, BTS/) against the Research databases",
             "(data/mundane). Matched: both moments within 3 minutes, or the same day, kind and place (500 km). Research takes Rodden's time where it",
             "has none to the minute; where both are timed and differ, Research keeps its own. Unmatched Rodden events are added to Research",
             "(rodden_disasters.json, rodden_nations.json), and those of no kind Research has to its Events database (rodden_events.json).",
             "Only Research changes: the Rodden library stays as it is.", "",
             f"Rodden event charts: {len(events):,} ({', '.join(f'{k} {v}' for k, v in kinds.most_common())}).", "",
             "| Outcome | Charts |", "|---|---:|",
             *[f"| {k} | {len(report[k]):,} |" for k in ("agree", "place differs", "time differs", "timed from Rodden", "Rodden charts disagree") if report[k]],
             f"| matched in all | {matched:,} |",
             f"| added to Research | {len(new):,} records ({sum(len(r['rodden']) for r in new):,} charts) |", "",
             "| Added to | Records |", "|---|---:|", *[f"| {k} | {sum(not r.get('same_as') for r in v):,} |" for k, v in out.items()], ""]
    for k, title in (("time differs", "Times that differ (Research keeps its own)"), ("place differs", "Places more than 300 km apart (same moment)"),
                     ("timed from Rodden", "Research records timed from Rodden")):
        if report[k]:
            lines += [f"## {title}", "", "| Rodden chart | Rodden | Research | Record | Minutes | km |", "|---|---|---|---|---:|---:|"]
            for e, r, d, dist in sorted(report[k], key=lambda x: x[0]["jd"]):
                lines.append(f"| {e['name'].replace('|', '/')} | {when(e)} | {theirs(r)} | {r['id']} {str(r.get('name') or r.get('chart_name') or r.get('place', '')).replace('|', '/')} | "
                             f"{d if r.get('time') else ''} | {round(dist)} |")
            lines.append("")
    lines += ["## Rodden events added to Research", "", "| Id | Type | Date | Time | Charts |", "|---|---|---|---|---|"]
    for r in sorted(new, key=lambda r: r["date"]):
        lines.append(f"| {r['id']} | {r.get('type') or r.get('event')} | {r['date']} | {r['time']} UTC{r['tz_east']:+g} | {'; '.join(r['rodden']).replace('|', '/')} |")
    (M.DIR / "RODDEN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    per_set = ", ".join(f"{k} {sum(not r.get('same_as') for r in v)}" for k, v in out.items())
    print(f"{len(events)} event charts: {matched} matched ({', '.join(f'{k} {len(v)}' for k, v in report.items())}), "
          f"{len(new)} added to Research ({per_set})")


if __name__ == "__main__":
    main()
