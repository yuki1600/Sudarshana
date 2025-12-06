# src/main.py
from __future__ import annotations
import argparse, sqlite3, sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Import core both ways (module or script execution)
try:
    from src.ci_core import compute_chart_with_tzname
except ImportError:
    from ci_core import compute_chart_with_tzname

# ---------- Paths (robust no matter where you launch from)
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "places.db"
DEFAULT_EPHE = BASE_DIR / "ephe"

# ---------- DB helpers
def db():
    if not DB_PATH.exists():
        sys.exit(f"[ERR] places DB not found at {DB_PATH}\nRun: python -m scripts.build_places_db")
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    return con

# ---------- Country search (partial / interactive)
def search_countries(query: str | None, limit: int = 30) -> list[tuple[str, str]]:
    """Return [(iso2, name), ...] matching query in iso2 or name (LIKE), or top alphabetic if query empty."""
    con = db()
    cur = con.cursor()
    if query and query.strip():
        q = query.strip()
        like = f"%{q}%"
        rows = cur.execute(
            """
            SELECT iso2, name
            FROM countries
            WHERE UPPER(iso2) LIKE UPPER(?) OR name LIKE ?
            ORDER BY name
            LIMIT ?
            """,
            (like, like, limit),
        ).fetchall()
    else:
        rows = cur.execute(
            "SELECT iso2, name FROM countries ORDER BY name LIMIT ?",
            (limit,),
        ).fetchall()
    con.close()
    return [(r["iso2"], r["name"]) for r in rows]

def resolve_country_initial(pref: str | None) -> tuple[str, str] | None:
    """Fast path: if pref is exact ISO2 or yields exactly one match, return it, else None."""
    if not pref:
        return None
    con = db()
    s = pref.strip()
    # exact ISO2
    if len(s) == 2:
        r = con.execute("SELECT iso2, name FROM countries WHERE UPPER(iso2)=UPPER(?)", (s,)).fetchone()
        con.close()
        if r:
            return (r["iso2"], r["name"])
        return None
    con.close()
    # partial: get matches; if unique, accept
    matches = search_countries(s, limit=5)
    if len(matches) == 1:
        return matches[0]
    return None

def prompt_country_interactive(pref: str | None) -> tuple[str, str]:
    """
    Interactive country picker:
      - Start with `pref` (if any) as the first search
      - Show a numbered list
      - Let user type a number to select, or new text to refine
      - Enter with empty input lists a fresh top set
    """
    # Try fast resolution
    resolved = resolve_country_initial(pref)
    if resolved:
        return resolved

    query = pref or ""
    while True:
        rows = search_countries(query, limit=30)
        if rows:
            print("\nCountry matches:")
            for i, (iso2, name) in enumerate(rows, 1):
                print(f"{i:2d}. {name}  ({iso2})")
            s = input("Select number, or type to search again (Enter to list all): ").strip()
            if s.isdigit():
                k = int(s)
                if 1 <= k <= len(rows):
                    return rows[k - 1]
                print("Out of range.")
                continue
            # Text search (can be empty to show top list)
            query = s
        else:
            print("No matches. Try a different text.")
            query = input("Country search: ").strip()

# ---------- City search (same as before; uses FTS/LIKE)
def search_places(country_iso2: str, q: str, limit=20):
    con = db()
    cur = con.cursor()
    q = (q or "").strip()
    if q:
        try:
            # FTS path
            fts_query = f'"{q}"'
            sql = """
            SELECT p.geonameid, p.name,
                   a.name AS admin1_name, p.country_iso2,
                   c.name AS country_name, p.lat, p.lon, p.timezone, p.population
            FROM places_fts f
            JOIN places p ON p.geonameid = f.rowid
            LEFT JOIN admin1 a ON a.key = p.country_iso2 || '.' || p.admin1_code
            LEFT JOIN countries c ON c.iso2 = p.country_iso2
            WHERE p.country_iso2 = ? AND f MATCH ?
            ORDER BY p.population DESC NULLS LAST
            LIMIT ?;
            """
            rows = cur.execute(sql, (country_iso2.upper(), fts_query, limit)).fetchall()
        except sqlite3.OperationalError:
            # LIKE fallback
            like = f"%{q}%"
            sql = """
            SELECT p.geonameid, p.name,
                   a.name AS admin1_name, p.country_iso2,
                   c.name AS country_name, p.lat, p.lon, p.timezone, p.population
            FROM places p
            LEFT JOIN admin1 a ON a.key = p.country_iso2 || '.' || p.admin1_code
            LEFT JOIN countries c ON c.iso2 = p.country_iso2
            WHERE p.country_iso2 = ? AND (p.name LIKE ? OR p.asciiname LIKE ? OR p.alternatenames LIKE ?)
            ORDER BY p.population DESC NULLS LAST
            LIMIT ?;
            """
            rows = cur.execute(sql, (country_iso2.upper(), like, like, like, limit)).fetchall()
    else:
        # top cities by population
        rows = cur.execute("""
            SELECT p.geonameid, p.name,
                   a.name AS admin1_name, p.country_iso2,
                   c.name AS country_name, p.lat, p.lon, p.timezone, p.population
            FROM places p
            LEFT JOIN admin1 a ON a.key = p.country_iso2 || '.' || p.admin1_code
            LEFT JOIN countries c ON c.iso2 = p.country_iso2
            WHERE p.country_iso2 = ?
            ORDER BY p.population DESC NULLS LAST
            LIMIT ?;
        """, (country_iso2.upper(), limit)).fetchall()
    con.close()
    out = []
    for r in rows:
        out.append(dict(
            geonameid=r["geonameid"],
            name=r["name"],
            admin1=r["admin1_name"],
            country_iso2=r["country_iso2"],
            country_name=r["country_name"],
            lat=float(r["lat"]), lon=float(r["lon"]),
            timezone=r["timezone"] or "UTC",
            population=r["population"] or 0,
        ))
    return out

def prompt_city(country_iso2: str, pref: str | None):
    print(f"\n[Country: {country_iso2}] Type part of city/town (Enter to list top):")
    query = pref or input("City query: ").strip()
    while True:
        results = search_places(country_iso2, query, limit=20)
        if not results:
            print("No matches. Try different text.")
            query = input("City query: ").strip()
            continue
        print("\nMatches:")
        for i, p in enumerate(results, 1):
            adm = f", {p['admin1']}" if p['admin1'] else ""
            print(f"{i:2d}. {p['name']}{adm} — {p['country_iso2']}  "
                  f"[lat {p['lat']:.4f}, lon {p['lon']:.4f}, tz {p['timezone']}]")
        s = input("Select number (or type to search again): ").strip()
        if s.isdigit():
            k = int(s)
            if 1 <= k <= len(results):
                return results[k-1]
            else:
                print("Out of range.")
        else:
            query = s  # new search text

# ---------- Date & time parsing (supports seconds)
def parse_date(dstr: str | None) -> str:
    while True:
        s = dstr or input("Date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return s
        except ValueError:
            print("Bad date; try again.")
            dstr = None

def parse_time(tstr: str | None) -> str:
    while True:
        s = tstr or input("Time (HH:MM[:SS]): ").strip()
        parts = s.split(":")
        if len(parts) in (2,3):
            try:
                hh = int(parts[0]); mm = int(parts[1]); ss = int(parts[2]) if len(parts)==3 else 0
                if 0<=hh<24 and 0<=mm<60 and 0<=ss<60:
                    return f"{hh:02d}:{mm:02d}:{ss:02d}"
            except Exception:
                pass
        print("Bad time; try again (e.g., 09:45 or 09:45:30).")
        tstr=None

# ---------- Main flow
def run_cli(args):
    # 1) Country (interactive partial search)
    country_iso2, country_name = prompt_country_interactive(args.country)

    # 2) City search & pick
    place = prompt_city(country_iso2, args.city)
    lat, lon, tzname = place["lat"], place["lon"], place["timezone"]
    city_label = f"{place['name']}{', ' + place['admin1'] if place['admin1'] else ''}, {country_iso2}"

    # 3) Date & Time (with seconds)
    date_s = parse_date(args.date)
    time_s = parse_time(args.time)

    y, m, d = map(int, date_s.split("-"))
    hh, mm, ss = map(int, time_s.split(":"))

    # 4) Compute chart
    ephe_path = str(args.ephe)
    res = compute_chart_with_tzname(
        y, m, d, hh, mm, ss,
        lat, lon, tzname,
        ephe_path=ephe_path,
        use_moseph=args.moseph,
        house_sys=args.house_sys.encode("ascii")
    )

    # 5) Output
    print("\n=== SUMMARY ===")
    print(f"Country: {country_name} ({country_iso2})")
    print(f"Place:   {city_label}")
    print(f"Coords:  lat {lat:.6f}, lon {lon:.6f}")
    print(f"TZ:      {tzname}")
    print(f"Local:   {res['local_dt']}")
    print(f"UTC:     {res['utc_dt']}")

    pd.set_option("display.max_colwidth", 80)

    print("\n=== PAÑCĀṄGA ===")
    print(res["panchanga"].to_string(index=False))

    print("\n=== POINTS & PLANETS ===")
    print(res["points"].to_string(index=False))

    print("\n=== HOUSES (Śrīpati/Porphyry) ===")
    print(res["houses"].to_string(index=False))

    print("\n=== VIMŚOTTARĪ (Mahādaśā) ===")
    print(res["vimshottari_md"].head(12).to_string(index=False))

    print("\n=== YOGINĪ (major) ===")
    print(res["yogini"].to_string(index=False))

    print("\n=== ŚAḌBALA (Virūpa/Rūpa + Rank) ===")
    print(res["shadbala"].to_string(index=False))

def main():
    ap = argparse.ArgumentParser(description="Celestial Intelligence — Terminal UI with local places DB")
    ap.add_argument("--country", help="Country query (ISO2 or part of name/code), e.g. 'IN' or 'Ind' or 'India'")
    ap.add_argument("--city",    help="Initial city search text")
    ap.add_argument("--date",    help="YYYY-MM-DD")
    ap.add_argument("--time",    help="HH:MM or HH:MM:SS (local time)")
    ap.add_argument("--ephe",    default=str(DEFAULT_EPHE), help="Ephemeris folder path")
    ap.add_argument("--house_sys", default="O", help="House system code, 'O'=Sripati/Porphyry")
    ap.add_argument("--moseph", action="store_true", help="Use Moshier instead of Swiss (not recommended)")
    args = ap.parse_args()
    run_cli(args)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
