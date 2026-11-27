"""Pull NOAA NCEI's significant earthquake, tsunami and volcanic eruption catalogues into data/mundane/.

Re-runnable: python tools/mundane_ncei.py. Records without at least a year, month and day are dropped (nothing to cast);
NCEI times are UTC, so a record's moment is stored at tz_east 0 with the event's own latitude and longitude.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import urllib.request
from pathlib import Path

API = "https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/"
OUT = Path(__file__).resolve().parents[1] / "data" / "mundane"
WEB = "https://www.ngdc.noaa.gov/hazel/view/hazards/"
# NCEI's tsunami cause codes (https://www.ngdc.noaa.gov/hazel/view/about)
CAUSE = {0: "unknown", 1: "earthquake", 2: "questionable earthquake", 3: "earthquake and landslide", 4: "volcano and earthquake",
         5: "volcano, earthquake and landslide", 6: "volcano", 7: "volcano and landslide", 8: "landslide", 9: "meteorological",
         10: "explosion", 11: "astronomical tide"}


# NCEI's country names that are not the GeoNames country name
ALIAS = {"usa": "US", "usa territory": "US", "myanmar (burma)": "MM", "uk": "GB", "uk territory": "GB", "azores (portugal)": "PT",
         "kermadec islands (new zealand)": "NZ", "kermadec islands": "NZ", "martinique (french territory)": "MQ", "bosnia-herzegovina": "BA",
         "micronesia, fed. states of": "FM", "congo": "CG", "netherlands": "NL", "holland": "NL", "guadeloupe (french territory)": "GP", "congo, drc": "CD",
         "st. vincent & the grenadines": "VC", "cape verde": "CV", "solomon is.": "SB", "wallis and futuna (french territory)": "WF", "canary islands": "ES",
         "cote d'ivoire": "CI", "czech republic": "CZ", "naoero": "NR", "st. kitts & nevis": "KN", "trinidad": "TT"}


def country_table() -> list[tuple[str, str]]:
    db = Path(__file__).resolve().parents[1] / "databases" / "places.db"
    if not db.exists():
        return []
    with sqlite3.connect(db) as c:
        return list(c.execute("select iso2, name from countries"))


def iso_codes() -> dict[str, str]:
    return {**{n.lower(): code for code, n in country_table()}, **ALIAS}


def fetch(path: str) -> list[dict]:
    items, page = [], 1
    while True:
        with urllib.request.urlopen(f"{API}{path}?itemsPerPage=200&page={page}", timeout=120) as r:
            body = json.load(r)
        items += body["items"]
        if page >= body["totalPages"]:
            return items
        page += 1


def moment(x: dict) -> dict | None:
    y, m, d = x.get("year"), x.get("month"), x.get("day")
    if y is None or m is None or d is None:
        return None
    h, mi, s = x.get("hour"), x.get("minute"), x.get("second")
    time = None
    if h is not None:
        time = f"{h:02d}:{mi or 0:02d}" + (f":{min(int(s), 59):02d}" if s is not None else "")
    lat, lon = x.get("latitude"), x.get("longitude")
    if lat is None or lon is None:
        return None
    return {"date": f"{y:04d}-{m:02d}-{d:02d}" if y >= 0 else f"{y:05d}-{m:02d}-{d:02d}",
            # a day without a time is cast at local noon, so its zone is the place's mean time
            "time": time, "tz_east": 0 if time else round(lon / 15, 2), "gregorian": (y, m, d) >= (1582, 10, 15),
            # instrumental times to the second from 1900; before that a reported hour is a contemporary account
            "time_confidence": "date" if time is None else ("exact" if y >= 1900 and s is not None else ("reported" if mi is not None else "approx")),
            "lat": lat, "lon": lon}


def place(x: dict) -> tuple[str, str]:
    loc = (x.get("locationName") or x.get("location") or "").strip()
    country = (x.get("country") or "").strip().title()
    if ":" in loc:
        loc = loc.split(":", 1)[1].strip()
    return " ".join(loc.title().split()), country


def build(kind: str, path: str, extra) -> list[dict]:
    out, iso, proper = [], iso_codes(), dict(country_table())
    for x in fetch(path):
        m = moment(x)
        if m is None:
            continue
        p, country = place(x)
        code = iso.get(country.lower())
        rec = {"id": f"{kind[:2]}{x['id']}", "type": kind, **m, "place": p, "country": proper.get(code, country), "iso2": code,   # "Usa" -> "United States"
               "deaths": x.get("deathsTotal", x.get("deaths")), "damage_musd": x.get("damageMillionsDollarsTotal", x.get("damageMillionsDollars")),
               "ncei_id": x["id"], **extra(x),
               "source": f"{WEB}{kind}/event-more-info/{x['id']}"}
        out.append({k: v for k, v in rec.items() if v is not None})
    return sorted(out, key=lambda r: (int(r["date"][:-6]), r["date"][-5:], r.get("time") or ""))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sets = {
        "earthquakes": build("earthquake", "earthquakes", lambda x: {
            "magnitude": x.get("eqMagnitude", x.get("eqMagMw", x.get("eqMagMs"))), "intensity": x.get("intensity"), "depth_km": x.get("eqDepth"),
            "tsunami": bool(x.get("tsunamiEventId")) or None}),
        "tsunamis": build("tsunami", "tsunamis/events", lambda x: {
            "magnitude": x.get("maxWaterHeight"), "eq_magnitude": x.get("eqMagnitude"),
            "cause": CAUSE.get(x.get("causeCode")), "validity": x.get("eventValidity")}),
        "volcanoes": build("volcano", "volcanoes", lambda x: {
            "name": x.get("name"), "magnitude": x.get("vei"), "elevation_m": x.get("elevation"), "morphology": x.get("morphology")}),
    }
    about = {
        "earthquakes": "NOAA NCEI Global Significant Earthquake Database (doi:10.7289/V5TD9V7K): events with deaths, $1M+ damage, magnitude 7.5+, intensity X+ or a tsunami. magnitude: NCEI's preferred magnitude. Times UTC.",
        "tsunamis": "NOAA NCEI Global Historical Tsunami Database (doi:10.7289/V5PN93H7). magnitude: maximum water height in metres. validity: 4 definite .. -1 erroneous entry. Times UTC.",
        "volcanoes": "NOAA NCEI Significant Volcanic Eruptions Database (doi:10.7289/V5JW8BSH): eruptions with deaths, $1M+ damage, VEI 6+, or a tsunami or earthquake. magnitude: VEI. Times UTC.",
    }
    for name, recs in sets.items():
        about[name] += " Dates before 1582-10-15 are taken as Julian (as historical catalogues record them); a day without a time is cast at local noon, tz_east being the place's mean time."
        (OUT / f"{name}.json").write_text(json.dumps({"_about": about[name], "records": recs}, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(name, len(recs), file=sys.stderr)


if __name__ == "__main__":
    main()
