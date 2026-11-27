"""Build ``databases/rodden.db``, the Open chart dialog's Rodden library, from the Rodden AA and A text files in ``BTS/``.

Each file holds one chart: birth data, biography, relationships, events, source notes and category keywords. The library
keeps each as a .vs chart file, and as the Predictions tab's facts: what fits its questions (gender, parents' deaths,
marriage, illness, retirement) goes there, every dated event goes to Other events, and the rest (biography,
relationships, sources, keywords) goes to Notes.

    .venv/bin/python databases/build_rodden_db.py [BTS folder]

Checks every chart's parsed birth moment against the tropical Ascendant its file states, and prints how many disagree.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

import swisseph as swe

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "rodden.db"
FOLDERS = ("rodden_AA", "rodden_A")   # AA first: a chart in both keeps its better rating
MONTHS = {m: i for i, m in enumerate(("january", "february", "march", "april", "may", "june", "july", "august", "september",
                                       "october", "november", "december"), 1)}
SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
BORN = re.compile(r"(\d{1,2}) ([A-Za-z]+) (\d{1,4})(?: (?:BC|CE))?(?: \((-?\d+)\))?\s*(Jul\.Cal\.)?.*?\bat (\d{1,2}):(\d{2})(?::(\d{2}))?")


def section(text: str, name: str) -> str:
    m = re.search(r"^START %s\s*$(.*?)^END %s\s*$" % (name, name), text, re.M | re.S)
    return m.group(1).strip() if m else ""


def fields(block: str) -> dict[str, str]:
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"^(\w+):[ \t]*(.*)$", block, re.M)}


def coord(s: str) -> float:
    """``40n02``, ``75w05``, ``13s3956``, ``1e0``: degrees, arc minutes and maybe seconds; south and west negative."""
    m = re.fullmatch(r"(\d+)([nsew])(\d{1,2})(\d{2})?", s.strip())
    if not m:
        raise ValueError("coordinate %r" % s)
    v = int(m.group(1)) + int(m.group(3)) / 60 + int(m.group(4) or 0) / 3600
    return -v if m.group(2) in "sw" else v


def zone(tz: str) -> tuple[float, bool]:
    """Hours east and whether it is daylight or war time. ``h5e30``: 5h30m east; ``m2e2015``: the mean time of the
    meridian 2°20'15" east, a fifteenth of it in hours."""
    m = re.search(r"\b([hm])(\d+)([ew])(\d*)", tz)
    if not m:
        raise ValueError("time zone %r" % tz)
    rest = m.group(4)
    v = int(m.group(2)) + int(rest[:2] or 0) / 60 + int(rest[2:4] or 0) / 3600
    if m.group(1) == "m":
        v /= 15
    return (-v if m.group(3) == "w" else v) + 0.0, bool(re.search(r"daylight|war time", tz))   # + 0.0: "h0w" is no -0


def born(s: str) -> tuple[int, int, int, float, bool]:
    m = BORN.match(s)
    if not m or m.group(2).lower() not in MONTHS:
        raise ValueError("birth date %r" % s)
    year = int(m.group(4)) if m.group(4) else int(m.group(3))   # "1099 BC (-1098)": the astronomical year
    hour = int(m.group(6)) + int(m.group(7)) / 60 + int(m.group(8) or 0) / 3600
    return year, MONTHS[m.group(2).lower()], int(m.group(1)), hour, not m.group(5)


def event(line: str) -> dict | None:
    """``Work : New Career  14 March 1954   (Baseball debut)     chart Placidus Equal_H.`` as a Predictions event."""
    parts = [p for p in re.split(r"\s{2,}", line.strip()) if p and not p.startswith("chart ")]
    if len(parts) < 2:
        return None
    kind, when = parts[0], parts[1]
    y = re.search(r"(-?\d{1,4})\s*$", when)
    if not y:
        return None
    note = " ".join(p.strip("()") for p in parts[2:])
    return {"year": int(y.group(1)), "approx": False, "kind": re.sub(r"\s*:\s*", ": ", kind),
            "note": " · ".join(x for x in (when if not re.fullmatch(r"-?\d{1,4}", when) else "", note) if x)}


def facts(main: dict, text: str, notes: str) -> dict:
    events = [e for e in map(event, section(text, "EVENTS").splitlines()) if e]
    for i, e in enumerate(events):
        e["id"] = "r%d" % i
    events.sort(key=lambda e: e["year"])
    a: dict = {}
    if main.get("gender") in ("M", "F"):
        a["gender"] = "Male" if main["gender"] == "M" else "Female"
    first = lambda *kinds: next((e for e in events if e["kind"] in kinds), None)  # noqa: E731
    for who in ("Father", "Mother"):
        if e := first("Death of " + who):
            a[who.lower()], a[who.lower() + ".year"] = "Passed", e["year"]
    marriages = [e for e in events if e["kind"] == "Relationship: Marriage"]
    endings = [e for e in events if e["kind"] in ("Relationship: Divorce dates", "Death of Mate")]
    if marriages or endings:
        last = endings[-1] if endings and (not marriages or endings[-1]["year"] >= marriages[-1]["year"]) else None
        a["marriage"] = "Remarried" if len(marriages) > 1 else ("Widowed" if last["kind"] == "Death of Mate" else "Divorced") if last else "Married"
        if marriages:
            a["marriage.year"] = marriages[0]["year"]
    if e := first("Health: Medical diagnosis", "Health: Medical procedure", "Health: Acute illness", "Health: Chronic illness"):
        a["illness"], a["illness.year"] = "Yes", e["year"]
    if first("Work: Retired"):
        a["career"] = "Retired"
        if e := first("Work: New Career", "Work: New Job"):
            a["career.year"] = e["year"]
    return {"answers": a, "events": events, "notes": notes}


def notes_of(main: dict, text: str) -> str:
    """What no question or event holds: the biography, relationships, other birth data, sources and keywords."""
    head = [f"Birth name: {main['birthname']}" if main.get("birthname") else "",
            "Rodden rating %s · %s · collected by %s" % (main.get("rodden_rating", ""), main.get("datasource", ""), main.get("collector", "")),
            re.sub(r"\s+", " ", f"Born {main.get('born_on', '').split('  (=')[0]}, {main.get('place', '')}, {main.get('timezone', '')}")]
    bio = re.sub(r"^Link to Wikipedia biography\s*$", "", section(text, "BIOGRAPHY"), flags=re.M).strip()
    alt = re.sub(r"^(astrodata|sun|moon|asc):.*$\n?", "", section(text, "ALT BIRTH DATA"), flags=re.M).strip()
    seen, keys = set(), []
    for k in section(text, "CATEGORY KEYWORDS").splitlines():   # the lines that say something: "Kids more than 3 (Six)"
        k = k.strip()
        if "(" in k and "births" not in k and k not in seen:
            seen.add(k)
            keys.append(k)
    parts = [("", "\n".join(h for h in head if h)), ("Biography", bio), ("Relationships", section(text, "RELATIONSHIPS")),
             ("Other birth data", alt), ("Source notes", section(text, "SOURCE NOTES")), ("Keywords", "\n".join(keys))]
    return "\n\n".join(f"{t}\n{b}" if t else b for t, b in parts if b.strip())


def chart(path: str) -> dict:
    with open(path, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    main = fields(section(text, "MAIN BIRTH DATA"))
    name = main.get("name", "").strip()
    if not name or "born_on" not in main:
        raise ValueError("no name or birth date")
    year, month, day, hour, gregorian = born(main["born_on"])
    place, lat, lon = [p.strip() for p in main["place"].rsplit(",", 2)]
    tz, dst = zone(main["timezone"])
    city, _, country = place.partition(", ")
    gender = {"M": 1, "F": 2}.get(main.get("gender", ""), 0)
    birth = {"year": year, "month": month, "day": day, "hour_local": round(hour, 6), "tz_east_hours": round(tz, 6),
             "longitude_east": round(coord(lon), 6), "latitude": round(coord(lat), 6), "altitude_m": 0.0,
             "gregorian": gregorian, "place": place, "pressure_hpa": 1013.25, "temperature_c": 20.0}
    s = {"format": "sudarshana-chart", "version": 1, "app": "Sudarshana", "name": name, "birth": birth,
         "meta": {"city": city, "state": "", "country": country, "dst": dst, "tz_standard_east": round(tz - dst, 6),
                  "tz_dst_east": round(tz, 6), "gender": gender}, "notes": ""}
    return {"name": name, "rating": main.get("rodden_rating", ""), "birth": birth, "place": place, "s": s, "asc": main.get("asc", ""),
            "dup": (unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().casefold(), main["born_on"], main["place"]),
            "facts": facts(main, text, notes_of(main, text))}


def asc_off(c: dict) -> float | None:
    """Degrees between the Ascendant of the parsed moment and the one the file states (tropical), or None when it states none."""
    m = re.match(r"(\w+) (\d+)°(\d+)", c["asc"])
    if not m or m.group(1) not in SIGNS:
        return None
    b = c["birth"]
    jd = swe.julday(b["year"], b["month"], b["day"], b["hour_local"] - b["tz_east_hours"], swe.GREG_CAL if b["gregorian"] else swe.JUL_CAL)
    got = swe.houses(jd, b["latitude"], b["longitude_east"], b"E")[1][0]   # equal houses: the Ascendant is the same, and they exist at any latitude
    want = SIGNS.index(m.group(1)) * 30 + int(m.group(2)) + int(m.group(3)) / 60
    return abs((got - want + 180) % 360 - 180)


def main(src: str) -> None:
    rows, seen, skipped, off = [], set(), [], []
    for folder in FOLDERS:
        for dp, _, fs in os.walk(os.path.join(src, folder)):
            for f in sorted(fs):
                if not f.endswith(".txt"):
                    continue
                try:
                    c = chart(os.path.join(dp, f))
                except (ValueError, KeyError) as e:
                    skipped.append(f"{folder}/{f}: {e}")
                    continue
                if c["dup"] in seen:
                    continue
                seen.add(c["dup"])
                if (d := asc_off(c)) is not None and d > 1:
                    off.append(f"{c['name']}: {d:.1f}°")
                rows.append(c)
    rows.sort(key=lambda c: c["name"].casefold())
    tmp = DB_PATH.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    db = sqlite3.connect(tmp)
    db.executescript("""CREATE TABLE charts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, rating TEXT NOT NULL, year INTEGER, month INTEGER,
        day INTEGER, hour REAL, place TEXT, key TEXT NOT NULL, content TEXT NOT NULL, facts TEXT NOT NULL);
        CREATE INDEX charts_key ON charts (key);""")
    for i, c in enumerate(rows, 1):
        b = c["birth"]
        key = "%s|%d-%02d-%02d" % (c["name"], b["year"], b["month"], b["day"])   # web/src/lifeFacts.ts chartKey
        db.execute("INSERT INTO charts VALUES (?,?,?,?,?,?,?,?,?,?,?)", (i, c["name"], c["rating"], b["year"], b["month"], b["day"],
                   b["hour_local"], c["place"], key, json.dumps(c["s"], ensure_ascii=False), json.dumps(c["facts"], ensure_ascii=False)))
    db.commit()
    db.execute("VACUUM")
    db.close()
    os.replace(tmp, DB_PATH)
    print(f"{len(rows)} charts into {DB_PATH} ({DB_PATH.stat().st_size / 1e6:.0f} MB); {len(skipped)} files skipped, "
          f"{len(off)} with the Ascendant more than 1° from the file's")
    for s in skipped + off[:40]:
        print("  ", s)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(BASE.parent / "BTS"))
