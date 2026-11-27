"""Build ``databases/places.db`` from free GeoNames dumps (CC-BY 4.0).

Default source is ``cities15000.zip`` (populated places with population ≥ 15 000) —
small enough to download in seconds, large enough for birth-place typeahead.
Pass ``--source allCountries`` for the full gazetteer (~1 GB DB).
"""
from __future__ import annotations

import argparse
import sqlite3
import zipfile
from pathlib import Path
from typing import Iterable
from urllib.request import urlopen

BASE = Path(__file__).resolve().parent
RAW_DIR = BASE / "raw"
DB_PATH = BASE / "places.db"
GEONAMES = "https://download.geonames.org/export/dump"

SOURCES = {
    "cities15000": ("cities15000.zip", f"{GEONAMES}/cities15000.zip", "cities15000.txt"),
    "cities5000": ("cities5000.zip", f"{GEONAMES}/cities5000.zip", "cities5000.txt"),
    "allCountries": ("allCountries.zip", f"{GEONAMES}/allCountries.zip", "allCountries.txt"),
}
REFS = {
    "countryInfo": ("countryInfo.txt", f"{GEONAMES}/countryInfo.txt"),
    "admin1": ("admin1CodesASCII.txt", f"{GEONAMES}/admin1CodesASCII.txt"),
}


def log(msg: str) -> None:
    print(msg, flush=True)


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    log(f"→ Downloading {url}")
    with urlopen(url, timeout=120) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    log(f"  ✓ {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")


def ensure(path: Path, url: str) -> Path:
    if not path.exists():
        download(url, path)
    else:
        log(f"✓ Found {path.name}")
    return path


SCHEMA = """
CREATE TABLE countries (
  iso2 TEXT PRIMARY KEY,
  name TEXT NOT NULL
);
CREATE TABLE admin1 (
  key TEXT PRIMARY KEY,
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
  elevation INTEGER      -- metres: GeoNames' elevation, else its DEM (SRTM / GTOPO30); NULL when neither
);
CREATE VIRTUAL TABLE places_fts USING fts5(
  name, asciiname, alternatenames,
  content='places', content_rowid='geonameid', tokenize='unicode61'
);
CREATE INDEX idx_places_country_pop ON places(country_iso2, population DESC);
CREATE INDEX idx_places_tz ON places(timezone);
"""


def load_countries(con: sqlite3.Connection, path: Path) -> None:
    log("→ Loading countries")
    cur = con.cursor()
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 5 and parts[0] and parts[4]:
                cur.execute("INSERT OR IGNORE INTO countries VALUES (?,?)", (parts[0], parts[4]))
    con.commit()


def load_admin1(con: sqlite3.Connection, path: Path) -> None:
    log("→ Loading admin1")
    cur = con.cursor()
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2 and parts[0]:
                cur.execute("INSERT OR IGNORE INTO admin1 VALUES (?,?)", (parts[0], parts[1]))
    con.commit()


def iter_dump(zip_path: Path, member: str) -> Iterable[list[str]]:
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(member) as f:
            for raw in f:
                line = raw.decode("utf-8").rstrip("\n")
                if line:
                    yield line.split("\t")


def load_places(con: sqlite3.Connection, zip_path: Path, member: str) -> None:
    log(f"→ Loading places from {zip_path.name}")
    cur = con.cursor()
    batch, total = [], 0
    for row in iter_dump(zip_path, member):
        if len(row) < 19 or row[6] != "P" or not row[17]:
            continue
        elev = row[15] or (row[16] if row[16] != "-9999" else "")      # -9999: the DEM has no value (sea)
        try:
            batch.append((
                int(row[0]), row[1], row[2], row[3],
                float(row[4]), float(row[5]), row[8], row[10],
                int(row[14] or 0), row[17], row[6], row[7], int(elev) if elev else None,
            ))
        except ValueError:
            continue
        if len(batch) >= 5000:
            cur.executemany(
                "INSERT OR REPLACE INTO places VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", batch
            )
            total += len(batch)
            batch.clear()
            if total % 50000 == 0:
                log(f"  … {total:,}")
    if batch:
        cur.executemany("INSERT OR REPLACE INTO places VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", batch)
        total += len(batch)
    con.commit()
    log(f"  ✓ {total:,} places")


def build_fts(con: sqlite3.Connection) -> None:
    log("→ Building FTS index")
    con.execute(
        "INSERT INTO places_fts(rowid, name, asciiname, alternatenames) "
        "SELECT geonameid, name, asciiname, alternatenames FROM places"
    )
    try:
        con.execute("INSERT INTO places_fts(places_fts) VALUES('optimize')")
    except sqlite3.OperationalError:
        pass
    con.commit()
    log("  ✓ FTS ready")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", choices=sorted(SOURCES), default="cities15000",
                    help="GeoNames dump to import (default: cities15000)")
    args = ap.parse_args()

    zip_name, zip_url, member = SOURCES[args.source]
    ensure(RAW_DIR / REFS["countryInfo"][0], REFS["countryInfo"][1])
    ensure(RAW_DIR / REFS["admin1"][0], REFS["admin1"][1])
    ensure(RAW_DIR / zip_name, zip_url)

    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=MEMORY")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("PRAGMA temp_store=MEMORY")
    try:
        con.executescript(SCHEMA)
        load_countries(con, RAW_DIR / REFS["countryInfo"][0])
        load_admin1(con, RAW_DIR / REFS["admin1"][0])
        load_places(con, RAW_DIR / zip_name, member)
        build_fts(con)
    finally:
        con.execute("PRAGMA optimize")
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        con.commit()
        con.close()
    log(f"✓ Built {DB_PATH} ({DB_PATH.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
