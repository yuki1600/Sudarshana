# scripts/build_places_db.py
from __future__ import annotations
import csv, io, os, sqlite3, sys, zipfile, ssl, urllib.request
from pathlib import Path
from typing import Iterable, Optional

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "places.db"

GEONAMES = "https://download.geonames.org/export/dump"
FILES = {
    "allcountries": ("allCountries.zip", f"{GEONAMES}/allCountries.zip"),
    "countryInfo":  ("countryInfo.txt",  f"{GEONAMES}/countryInfo.txt"),
    "admin1":       ("admin1CodesASCII.txt", f"{GEONAMES}/admin1CodesASCII.txt"),
    "timeZones":    ("timeZones.txt",   f"{GEONAMES}/timeZones.txt"),
}

# ---------------------------
# Utilities
# ---------------------------
def log(msg: str): print(msg, file=sys.stdout, flush=True)

def dl(url: str, dest: Path):
    import ssl
    dest.parent.mkdir(parents=True, exist_ok=True)
    log(f"→ Downloading {url} → {dest}")
    ctx = None
    try:
        # Prefer certifi if available
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            ctx = ssl.create_default_context()
        with urllib.request.urlopen(url, context=ctx) as r, open(dest, "wb") as f:
            f.write(r.read())
    except Exception as e:
        log(f"[!] Python download failed ({e}). Use curl as fallback:")
        log(f"    curl -L '{url}' -o '{dest}'")
        raise


def ensure_files():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for key, (fn, url) in FILES.items():
        p = RAW_DIR / fn
        if not p.exists():
            dl(url, p)
        else:
            log(f"✓ Found {p.name}")

# ---------------------------
# SQLite helpers
# ---------------------------
def connect_db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        log(f"→ Removing old DB {DB_PATH}")
        DB_PATH.unlink()
    con = sqlite3.connect(str(DB_PATH))
    con.execute("PRAGMA journal_mode=MEMORY;")
    con.execute("PRAGMA synchronous=OFF;")
    con.execute("PRAGMA temp_store=MEMORY;")
    con.execute("PRAGMA mmap_size=30000000000;")  # best-effort, ignored if unsupported
    return con

def finalize_db(con: sqlite3.Connection):
    con.execute("PRAGMA optimize;")
    try:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")
    except sqlite3.OperationalError:
        pass
    con.commit()
    con.close()
    log(f"✓ Built {DB_PATH} (size ≈ {DB_PATH.stat().st_size/1_000_000:.1f} MB)")

# ---------------------------
# Schema
# ---------------------------
SCHEMA_SQL = """
CREATE TABLE countries (
  iso2 TEXT PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE admin1 (
  key TEXT PRIMARY KEY,        -- e.g. 'IN.KA'
  name TEXT NOT NULL
);

CREATE TABLE places (
  geonameid INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  asciiname TEXT,
  alternatenames TEXT,
  lat REAL NOT NULL,
  lon REAL NOT NULL,
  country_iso2 TEXT NOT NULL,
  admin1_code TEXT,
  population INTEGER,
  timezone TEXT,
  fclass TEXT,
  fcode TEXT,
  FOREIGN KEY(country_iso2) REFERENCES countries(iso2)
);

-- FTS5 external-content index for fast typeahead
CREATE VIRTUAL TABLE places_fts USING fts5(
  name, asciiname, alternatenames,
  content='places', content_rowid='geonameid', tokenize='unicode61'
);

-- Helpful indexes
CREATE INDEX idx_places_country ON places(country_iso2);
CREATE INDEX idx_places_country_pop ON places(country_iso2, population DESC);
CREATE INDEX idx_places_admin1 ON places(country_iso2, admin1_code);
CREATE INDEX idx_places_tz ON places(timezone);
"""

def create_schema(con: sqlite3.Connection):
    con.executescript(SCHEMA_SQL)
    con.commit()

# ---------------------------
# Load reference tables
# ---------------------------
def load_countries(con: sqlite3.Connection, path: Path):
    log("→ Loading countries")
    cur = con.cursor()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line or line.startswith("#"): 
                continue
            parts = line.strip().split("\t")
            if len(parts) < 5: 
                continue
            iso2 = parts[0].strip()
            name = parts[4].strip()
            if iso2 and name:
                cur.execute("INSERT OR IGNORE INTO countries (iso2, name) VALUES (?,?)", (iso2, name))
    con.commit()
    log("  ✓ countries loaded")

def load_admin1(con: sqlite3.Connection, path: Path):
    log("→ Loading admin1 (states/provinces)")
    cur = con.cursor()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): 
                continue
            parts = line.strip().split("\t")
            if len(parts) < 2: 
                continue
            key = parts[0]        # e.g., 'IN.KA'
            name = parts[1]
            cur.execute("INSERT OR IGNORE INTO admin1 (key, name) VALUES (?,?)", (key, name))
    con.commit()
    log("  ✓ admin1 loaded")

# ---------------------------
# Stream & load allCountries
# ---------------------------
ALLCOLUMNS = [
    "geonameid","name","asciiname","alternatenames","latitude","longitude","feature_class","feature_code",
    "country_code","cc2","admin1_code","admin2_code","admin3_code","admin4_code","population",
    "elevation","dem","timezone","modification_date"
]

def is_valid_place(row: list[str], feature_class: str) -> bool:
    # row columns by index per GeoNames spec
    fclass = row[6]
    tz = row[17]
    if not tz:
        return False
    if feature_class == "P":    # populated places only
        return fclass == "P"
    elif feature_class == "ALL":
        return True
    else:
        # default same as P
        return fclass == "P"

def iter_allCountries_zip(zip_path: Path) -> Iterable[list[str]]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        # allCountries.txt inside zip
        with zf.open("allCountries.txt", "r") as f:
            for raw in f:
                line = raw.decode("utf-8").rstrip("\n")
                if not line: 
                    continue
                yield line.split("\t")

def load_places(con: sqlite3.Connection, allcountries_zip: Path, feature_class: str):
    log(f"→ Loading places from {allcountries_zip.name} (feature_class={feature_class})")
    cur = con.cursor()
    batch = []
    total = 0
    for row in iter_allCountries_zip(allcountries_zip):
        if len(row) < 19:
            continue
        if not is_valid_place(row, feature_class):
            continue
        try:
            geonameid = int(row[0])
            name = row[1]
            asciiname = row[2]
            alternatenames = row[3]  # large; OK for FTS
            lat = float(row[4]); lon = float(row[5])
            fclass = row[6]; fcode = row[7]
            country = row[8]
            admin1 = row[10]
            pop = int(row[14]) if row[14] else None
            tz = row[17]
        except Exception:
            continue

        batch.append((geonameid, name, asciiname, alternatenames, lat, lon, country, admin1, pop, tz, fclass, fcode))

        if len(batch) >= 5000:
            cur.executemany("""
                INSERT OR REPLACE INTO places
                (geonameid, name, asciiname, alternatenames, lat, lon, country_iso2, admin1_code,
                 population, timezone, fclass, fcode)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, batch)
            total += len(batch)
            batch.clear()
            if total % 100000 == 0:
                log(f"  … {total:,} rows")

    if batch:
        cur.executemany("""
            INSERT OR REPLACE INTO places
            (geonameid, name, asciiname, alternatenames, lat, lon, country_iso2, admin1_code,
             population, timezone, fclass, fcode)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, batch)
        total += len(batch)
        batch.clear()

    con.commit()
    log(f"  ✓ places loaded: {total:,}")

def build_fts(con: sqlite3.Connection):
    log("→ Building FTS index (places_fts)")
    cur = con.cursor()
    cur.execute("""
        INSERT INTO places_fts(rowid, name, asciiname, alternatenames)
        SELECT geonameid, name, asciiname, alternatenames FROM places
    """)
    con.commit()
    # compact FTS
    try:
        cur.execute("INSERT INTO places_fts(places_fts) VALUES('optimize');")
        con.commit()
    except sqlite3.OperationalError:
        pass
    log("  ✓ FTS built")

# ---------------------------
# Main
# ---------------------------
def main():
    import argparse
    ap = argparse.ArgumentParser(description="Build places.db from GeoNames allCountries")
    ap.add_argument("--feature-class", choices=["P","ALL"], default="P",
                    help="P = populated places only (recommended). ALL = all feature classes (huge).")
    args = ap.parse_args()

    ensure_files()

    con = connect_db()
    try:
        create_schema(con)
        load_countries(con, RAW_DIR / FILES["countryInfo"][0])
        load_admin1(con,    RAW_DIR / FILES["admin1"][0])
        load_places(con,    RAW_DIR / FILES["allcountries"][0], feature_class=args.feature_class)
        build_fts(con)
    finally:
        finalize_db(con)

    log("✓ Done. You can now run your API/UI on this larger DB.")
    log("   uvicorn src.app:app --reload")

if __name__ == "__main__":
    main()
