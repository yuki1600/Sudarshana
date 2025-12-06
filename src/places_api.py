# src/places_api.py
import sqlite3
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional

DB_PATH = "data/places.db"
app = FastAPI(title="CI Places API")

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

class Country(BaseModel):
    iso2: str
    name: str

class Place(BaseModel):
    geonameid: int
    name: str
    admin1: Optional[str]
    country_iso2: str
    country_name: str
    lat: float
    lon: float
    timezone: str

@app.get("/countries", response_model=List[Country])
def list_countries():
    con = get_db()
    rows = con.execute("SELECT iso2, name FROM countries ORDER BY name").fetchall()
    con.close()
    return [Country(iso2=r["iso2"], name=r["name"]) for r in rows]

@app.get("/places", response_model=List[Place])
def search_places(
    country: str = Query(..., min_length=2, max_length=2, description="ISO2 code, e.g. IN"),
    q: str = Query("", min_length=0, description="typeahead query"),
    limit: int = Query(20, ge=1, le=100)
):
    con = get_db()
    cur = con.cursor()

    if q.strip():
        # Full-text search (FTS5). If empty query, we’ll show popular cities below.
        fts_query = f'"{q.strip()}"'
        sql = """
        SELECT p.geonameid, p.name, p.asciiname, p.alternatenames,
               p.lat, p.lon, p.country_iso2, p.admin1_code, p.population,
               c.name as country_name, a.name as admin1_name, p.timezone
        FROM places_fts f
        JOIN places p ON p.geonameid = f.rowid
        LEFT JOIN countries c ON c.iso2 = p.country_iso2
        LEFT JOIN admin1 a ON a.key = p.country_iso2 || '.' || p.admin1_code
        WHERE p.country_iso2 = ?
          AND f MATCH ?
        ORDER BY p.population DESC NULLS LAST
        LIMIT ?;
        """
        rows = cur.execute(sql, (country.upper(), fts_query, limit)).fetchall()
    else:
        # No query: return top cities by population for that country
        sql = """
        SELECT p.geonameid, p.name, p.asciiname, p.alternatenames,
               p.lat, p.lon, p.country_iso2, p.admin1_code, p.population,
               c.name as country_name, a.name as admin1_name, p.timezone
        FROM places p
        LEFT JOIN countries c ON c.iso2 = p.country_iso2
        LEFT JOIN admin1 a ON a.key = p.country_iso2 || '.' || p.admin1_code
        WHERE p.country_iso2 = ?
        ORDER BY p.population DESC NULLS LAST
        LIMIT ?;
        """
        rows = cur.execute(sql, (country.upper(), limit)).fetchall()

    con.close()

    return [
        Place(
            geonameid=r["geonameid"],
            name=r["name"],
            admin1=r["admin1_name"],
            country_iso2=r["country_iso2"],
            country_name=r["country_name"],
            lat=float(r["lat"]),
            lon=float(r["lon"]),
            timezone=r["timezone"] or "UTC",
        )
        for r in rows
    ]
