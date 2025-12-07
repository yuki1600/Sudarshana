
# src/app.py
import csv, io, os, sqlite3, sys, zipfile, ssl, urllib.request, re, json
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import List, Optional

import sqlite3
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.ci_core import (
    compute_chart_with_tzname, get_ayanamsa_list, compute_ashtakavarga, 
    compute_transit_positions, get_ayanamsa_code, datetime_to_jd, jd_to_datetime,
    find_lunar_new_year, find_lunar_month_start, find_new_moon, find_full_moon,
    find_tithi_start, find_solar_return, find_tithi_pravesha,
    find_nakshatra_pravesha, find_yoga_pravesha, norm360,
    find_opposition, get_mundane_chart, get_tithi_at_jd, PLANETS,
    RASHI_SA, TITHI_NAMES_FULL, calculate_muntha, build_varsha_vimshottari,
    build_varsha_yogini, get_vimshottari_antardasha, get_vimshottari_pratyantardasha,
    get_yogini_antardasha, get_yogini_pratyantardasha, calculate_ashtakavarga_longevity,
    compute_lagna_grid, compute_lagna_for_location, compute_rashi_lines,
    find_new_moon_in_sign, find_solar_ingress, find_planetary_conjunction
)
import src.ci_match as ci_match
import src.dasa_systems as dasa_systems
import swisseph as swe

# ----- Absolute paths (robust no matter your working dir) -----
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "places.db"
EPHE_PATH = str(BASE_DIR / "ephe")
UI_DIR = BASE_DIR / "ui"
SWISS_MIN_YEAR = -12998
SWISS_MAX_YEAR = 16799

app = FastAPI(title="Celestial Intelligence API + UI")

# ----- Root route redirects to UI -----
@app.get("/")
def root():
    return RedirectResponse(url="/ui/")

# ----- DB helpers -----
def get_db():
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail=f"places DB not found at {DB_PATH}. Did you run: python -m scripts.build_places_db ?")
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    return con

# ----- Validation helpers -----
def ensure_year_in_range(year: int, label: str = "Year"):
    if year is None:
        return
    if year < SWISS_MIN_YEAR or year > SWISS_MAX_YEAR:
        raise HTTPException(
            status_code=400,
            detail=f"{label} must be between {SWISS_MIN_YEAR} and {SWISS_MAX_YEAR} (Swiss Ephemeris limit)."
        )

# ----- DateTime helpers -----
def format_datetime_for_js(dt):
    """
    Format datetime object to JavaScript-compatible ISO 8601 string.
    
    For historical dates, timezone offsets may include seconds (e.g., +05:53:28),
    which JavaScript Date constructor cannot parse. This function rounds the offset
    to minutes while preserving the correct wall clock time.
    
    Args:
        dt: datetime object with timezone info
        
    Returns:
        ISO 8601 formatted string with timezone offset in ±HH:MM format
    """
    if dt is None:
        return None
        
    # If it's a HistoricalDate (or has isoformat and no utcoffset support), use its isoformat
    if hasattr(dt, 'isoformat') and (not hasattr(dt, 'utcoffset') or dt.utcoffset() is None):
        return dt.isoformat()
    
    if not hasattr(dt, 'tzinfo') or dt.tzinfo is None:
        # No timezone info, return as-is with 'Z' suffix for UTC
        return dt.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    
    # Get the UTC offset in seconds
    offset = dt.utcoffset()
    if offset is None:
        return dt.isoformat() # Fallback
        
    offset_seconds = offset.total_seconds()
    
    # Round to nearest minute (to avoid seconds in offset)
    offset_minutes = round(offset_seconds / 60)
    offset_hours = int(offset_minutes // 60)
    offset_mins = int(abs(offset_minutes) % 60)
    
    # Format: YYYY-MM-DDTHH:MM:SS±HH:MM
    time_str = dt.strftime('%Y-%m-%dT%H:%M:%S')
    offset_str = f"{'+' if offset_minutes >= 0 else '-'}{abs(offset_hours):02d}:{offset_mins:02d}"
    
    return f"{time_str}{offset_str}"


# ----- Models -----
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

# ----- Endpoints: countries / places -----
@app.get("/countries", response_model=List[Country])
def list_countries():
    con = get_db()
    try:
        rows = con.execute("SELECT iso2, name FROM countries ORDER BY name").fetchall()
    except sqlite3.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"countries table missing: {e}")
    finally:
        con.close()
    return [Country(iso2=r["iso2"], name=r["name"]) for r in rows]

@app.get("/places", response_model=List[Place])
def search_places(
    country: str = Query(..., min_length=2, max_length=2, description="ISO2 country code, e.g. IN"),
    q: str = Query("", description="typeahead query (name/alternatenames)"),
    limit: int = Query(20, ge=1, le=100),
):
    con = get_db()
    cur = con.cursor()
    try:
        if q.strip():
            # Try FTS first
            try:
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
            except sqlite3.OperationalError:
                # FTS not available or table missing -> LIKE fallback
                like = f"%{q.strip()}%"
                sql = """
                SELECT p.geonameid, p.name, p.asciiname, p.alternatenames,
                       p.lat, p.lon, p.country_iso2, p.admin1_code, p.population,
                       c.name as country_name, a.name as admin1_name, p.timezone
                FROM places p
                LEFT JOIN countries c ON c.iso2 = p.country_iso2
                LEFT JOIN admin1 a ON a.key = p.country_iso2 || '.' || p.admin1_code
                WHERE p.country_iso2 = ?
                  AND (p.name LIKE ? OR p.asciiname LIKE ? OR p.alternatenames LIKE ?)
                ORDER BY p.population DESC NULLS LAST
                LIMIT ?;
                """
                rows = cur.execute(sql, (country.upper(), like, like, like, limit)).fetchall()
        else:
            # No query -> top cities by population
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
    except sqlite3.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"places query failed: {e}")
    finally:
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

# ----- Endpoint: ayanamsa list -----
@app.get("/ayanamsas")
def list_ayanamsas():
    """Return list of available ayanamsa options"""
    return {"ayanamsas": get_ayanamsa_list()}

# ----- Endpoint: chart -----
@app.get("/chart")
def chart(
    date: str = Query(..., description="YYYY-MM-DD"),
    time: str = Query(..., description="HH:MM or HH:MM:SS (local time at place)"),
    lat: float = Query(...),
    lon: float = Query(...),
    tz: str = Query(..., description="IANA tz, e.g. Asia/Kolkata"),
    house_sys: str = Query("O", description="house system code; 'O' = Sripati/Porphyry"),
    moseph: bool = Query(False, description="use Moshier instead of Swiss (not recommended)"),
    ayanamsa: str = Query("Lahiri", description="Ayanamsa system to use"),
    name: str = Query(None, description="Name of person (for Panch Swar Dasa)"),
):
    try:
        if len(time.split(":")) == 2:
            time_s = time + ":00"
        else:
            time_s = time
            
        try:
            dt = datetime.strptime(f"{date} {time_s}", "%Y-%m-%d %H:%M:%S")
            y, m, d = dt.year, dt.month, dt.day
            hh, mm, ss = dt.hour, dt.minute, dt.second
        except ValueError:
            # Fallback for extreme dates (BCE or >9999)
            # Regex for YYYY-MM-DD or -YYYYYY-MM-DD
            # Match date part: optional sign, digits, dash, month, dash, day
            date_match = re.match(r"^([+-]?\d+)-(\d{1,2})-(\d{1,2})$", date)
            if not date_match:
                raise ValueError("Invalid date format")
                
            y = int(date_match.group(1))
            m = int(date_match.group(2))
            d = int(date_match.group(3))
            
            # Match time part
            time_match = re.match(r"^(\d{1,2}):(\d{1,2}):(\d{1,2})$", time_s)
            if not time_match:
                raise ValueError("Invalid time format")
                
            hh = int(time_match.group(1))
            mm = int(time_match.group(2))
            ss = int(time_match.group(3))

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bad date/time: {e}")

    ensure_year_in_range(y, "Date year")

    try:
        res = compute_chart_with_tzname(
            y, m, d, hh, mm, ss,
            lat, lon, tz,
            ephe_path=EPHE_PATH, use_moseph=moseph, house_sys=house_sys.encode("ascii"),
            ayanamsa=ayanamsa, name=name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart error: {e}")

    def dfrec(df):
        # Use to_json->loads so NaN/NaT become null (JSON-compliant)
        return json.loads(df.to_json(orient="records"))
    
    # Compute Ashtakavarga
    ashtakavarga = compute_ashtakavarga(res["points"])
    # Calculate Ashtakavarga Longevity (years)
    ashtakavarga_longevity = calculate_ashtakavarga_longevity(ashtakavarga["bav"])
    
    payload = {
        "tzname": res["tzname"],
        "local_dt": format_datetime_for_js(res["local_dt"]),
        "utc_dt": format_datetime_for_js(res["utc_dt"]),
        "ayanamsa_name": res.get("ayanamsa_name", "Lahiri"),
        "ayanamsa_value": res.get("ayanamsa_value", 0),
        "points": dfrec(res["points"]),
        "houses": dfrec(res["houses"]),
        "vimshottari_md": dfrec(res["vimshottari_md"]),
        "yogini": dfrec(res["yogini"]),
        "varnada_dasa": dfrec(res.get("varnada_dasa", [])),
        # Additional Dasa Systems
        "ashtottari": dfrec(res.get("ashtottari", [])),
        "shodshottari": dfrec(res.get("shodshottari", [])),
        "dwadashottari": dfrec(res.get("dwadashottari", [])),
        "panchottari": dfrec(res.get("panchottari", [])),
        "shatabdik": dfrec(res.get("shatabdik", [])),
        "chaturashiti_sama": dfrec(res.get("chaturashiti_sama", [])),
        "dwisaptati_sama": dfrec(res.get("dwisaptati_sama", [])),
        "shastihayani": dfrec(res.get("shastihayani", [])),
        "shattrimshat_sama": dfrec(res.get("shattrimshat_sama", [])),
        "chakra": dfrec(res.get("chakra", [])),
        "sthir": dfrec(res.get("sthir", [])),
        "yogardha": dfrec(res.get("yogardha", [])),
        "kendradi_lagn": dfrec(res.get("kendradi_lagn", [])),
        "kendradi_ak": dfrec(res.get("kendradi_ak", [])),
        "karak": dfrec(res.get("karak", [])),
        "manduk": dfrec(res.get("manduk", [])),
        "shula": dfrec(res.get("shula", [])),
        "trikon": dfrec(res.get("trikon", [])),
        "dirga": dfrec(res.get("dirga", [])),
        "panch_swar": dfrec(res.get("panch_swar", [])),
        "kalachakra": dfrec(res.get("kalachakra", [])),
        "kalachakra_ayurdaya": res.get("kalachakra_ayurdaya", 0.0),
        "kalachakra_remaining": res.get("kalachakra_remaining", 0.0),
        "shadbala": dfrec(res["shadbala"]),
        "shadbala_sthana": dfrec(res.get("shadbala_sthana", [])),
        "shadbala_kala": dfrec(res.get("shadbala_kala", [])),
        "ishta_kashta": dfrec(res.get("ishta_kashta", [])),
        "bhava_bala": dfrec(res.get("bhava_bala", [])),
        "aspect_grid": dfrec(res.get("aspect_grid", [])),
        "pushkara_table": dfrec(res.get("pushkara_table", [])),
        "panchanga": dfrec(res["panchanga"]),
        "vargas": res.get("vargas", {}),
        "ashtakavarga": {
            "bav": ashtakavarga["bav"],
            "sav": ashtakavarga["sav"],
            "longevity": ashtakavarga_longevity,
        },
    }
    return JSONResponse(content=jsonable_encoder(payload))


# ----- Endpoint: Transit positions -----
@app.get("/transit")
def transit(
    lat: float = Query(..., description="Latitude of location"),
    lon: float = Query(..., description="Longitude of location"),
    tz: str = Query(..., description="IANA timezone, e.g. Asia/Kolkata"),
    transit_date: str = Query(None, description="Transit date YYYY-MM-DD (defaults to today)"),
    transit_time: str = Query(None, description="Transit time HH:MM:SS (defaults to now)"),
    ayanamsa: str = Query("Lahiri", description="Ayanamsa system to use"),
):
    """Get current (or specified) transit planetary positions"""
    from datetime import datetime as dt_module
    from dateutil import tz as tz_module
    
    try:
        local_zone = tz_module.gettz(tz)
        
        if transit_date and transit_time:
            if len(transit_time.split(":")) == 2:
                transit_time += ":00"
            transit_dt = dt_module.strptime(f"{transit_date} {transit_time}", "%Y-%m-%d %H:%M:%S")
            transit_dt = transit_dt.replace(tzinfo=local_zone)
        elif transit_date:
            # Date given but no time - use noon
            transit_dt = dt_module.strptime(f"{transit_date} 12:00:00", "%Y-%m-%d %H:%M:%S")
            transit_dt = transit_dt.replace(tzinfo=local_zone)
        else:
            # Use current time in the given timezone
            transit_dt = dt_module.now(local_zone)
        
        res = compute_transit_positions(
            transit_dt, lat, lon, tz,
            ephe_path=EPHE_PATH,
            ayanamsa=ayanamsa
        )
        
        def dfrec(df): return json.loads(df.to_json(orient="records"))
        
        return JSONResponse(content=jsonable_encoder({
            "transit_dt": res["transit_dt"],
            "ayanamsa_value": res["ayanamsa_value"],
            "points": dfrec(res["points"]),
        }))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transit calculation error: {e}")


# ----- Mundane Astrology Endpoints -----

@app.get("/mundane/lunar-new-year")
def lunar_new_year(
    year: int = Query(..., description="Year to find lunar new year for"),
    lat: float = Query(...),
    lon: float = Query(...),
    tz: str = Query(...),
    system: str = Query("amanta", description="Lunar calendar system: amanta or purnimant"),
    ayanamsa: str = Query("Lahiri"),
):
    """Find Lunar New Year (Chaitra Shukla Pratipada) and generate chart"""
    try:
        ensure_year_in_range(year, "Year")
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        event_jd = find_lunar_new_year(year, system, ayanamsa_code)
        event_dt = jd_to_datetime(event_jd, tz)
        
        # Generate chart for this moment
        chart = get_mundane_chart(event_jd, lat, lon, tz, ayanamsa, EPHE_PATH)
        
        def dfrec(df): return json.loads(df.to_json(orient="records"))
        ashtakavarga = compute_ashtakavarga(chart["points"])
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": "lunar_new_year",
            "event_dt": format_datetime_for_js(event_dt),
            "year": year,
            "system": system,
            "chart": {
                "tzname": chart["tzname"],
                "local_dt": format_datetime_for_js(chart["local_dt"]),
                "ayanamsa_name": chart.get("ayanamsa_name", ayanamsa),
                "ayanamsa_value": chart.get("ayanamsa_value", 0),
                "points": dfrec(chart["points"]),
                "houses": dfrec(chart["houses"]),
                "panchanga": dfrec(chart["panchanga"]),
                "shadbala": dfrec(chart.get("shadbala", [])),
                "shadbala_sthana": dfrec(chart.get("shadbala_sthana", [])),
                "shadbala_kala": dfrec(chart.get("shadbala_kala", [])),
                "ishta_kashta": dfrec(chart.get("ishta_kashta", [])),
                "ashtakavarga": {"bav": ashtakavarga["bav"], "sav": ashtakavarga["sav"]},
            }
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lunar new year error: {e}")


@app.get("/mundane/lunar-month")
def lunar_month(
    date: str = Query(..., description="Reference date YYYY-MM-DD"),
    lat: float = Query(...),
    lon: float = Query(...),
    tz: str = Query(...),
    direction: str = Query("next", description="Direction: previous or next"),
    system: str = Query("amanta"),
    ayanamsa: str = Query("Lahiri"),
):
    """Find start of lunar month (new moon for Amanta, full moon for Purnimant)"""
    try:
        from dateutil import tz as tz_module
        ref_dt = datetime.strptime(date, "%Y-%m-%d").replace(
            hour=12, tzinfo=tz_module.gettz(tz)
        )
        start_jd = datetime_to_jd(ref_dt)
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        
        event_jd = find_lunar_month_start(start_jd, direction, system, ayanamsa_code)
        event_dt = jd_to_datetime(event_jd, tz)
        
        chart = get_mundane_chart(event_jd, lat, lon, tz, ayanamsa, EPHE_PATH)
        def dfrec(df): return json.loads(df.to_json(orient="records"))
        ashtakavarga = compute_ashtakavarga(chart["points"])
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": "lunar_month_start",
            "event_dt": format_datetime_for_js(event_dt),
            "direction": direction,
            "system": system,
            "chart": {
                "tzname": chart["tzname"],
                "local_dt": format_datetime_for_js(chart["local_dt"]),
                "points": dfrec(chart["points"]),
                "houses": dfrec(chart["houses"]),
                "panchanga": dfrec(chart["panchanga"]),
                "shadbala": dfrec(chart.get("shadbala", [])),
                "shadbala_sthana": dfrec(chart.get("shadbala_sthana", [])),
                "shadbala_kala": dfrec(chart.get("shadbala_kala", [])),
                "ishta_kashta": dfrec(chart.get("ishta_kashta", [])),
                "ashtakavarga": {"bav": ashtakavarga["bav"], "sav": ashtakavarga["sav"]},
            }
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lunar month error: {e}")


@app.get("/mundane/new-moon")
def new_moon(
    date: str = Query(...),
    lat: float = Query(...),
    lon: float = Query(...),
    tz: str = Query(...),
    direction: str = Query("next"),
    ayanamsa: str = Query("Lahiri"),
):
    """Find new moon (Amavasya)"""
    try:
        from dateutil import tz as tz_module
        ref_dt = datetime.strptime(date, "%Y-%m-%d").replace(
            hour=12, tzinfo=tz_module.gettz(tz)
        )
        start_jd = datetime_to_jd(ref_dt)
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        
        event_jd = find_new_moon(start_jd, direction, ayanamsa_code)
        event_dt = jd_to_datetime(event_jd, tz)
        
        chart = get_mundane_chart(event_jd, lat, lon, tz, ayanamsa, EPHE_PATH)
        def dfrec(df): return json.loads(df.to_json(orient="records"))
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": "new_moon",
            "event_dt": format_datetime_for_js(event_dt),
            "direction": direction,
            "chart": {
                "tzname": chart["tzname"],
                "local_dt": format_datetime_for_js(chart["local_dt"]),
                "points": dfrec(chart["points"]),
                "houses": dfrec(chart["houses"]),
                "panchanga": dfrec(chart["panchanga"]),
                "shadbala": dfrec(chart.get("shadbala", [])),
                "shadbala_sthana": dfrec(chart.get("shadbala_sthana", [])),
                "shadbala_kala": dfrec(chart.get("shadbala_kala", [])),
                "ishta_kashta": dfrec(chart.get("ishta_kashta", [])),
            }
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"New moon error: {e}")


@app.get("/mundane/full-moon")
def full_moon(
    date: str = Query(...),
    lat: float = Query(...),
    lon: float = Query(...),
    tz: str = Query(...),
    direction: str = Query("next"),
    ayanamsa: str = Query("Lahiri"),
):
    """Find full moon (Purnima)"""
    try:
        from dateutil import tz as tz_module
        ref_dt = datetime.strptime(date, "%Y-%m-%d").replace(
            hour=12, tzinfo=tz_module.gettz(tz)
        )
        start_jd = datetime_to_jd(ref_dt)
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        
        event_jd = find_full_moon(start_jd, direction, ayanamsa_code)
        event_dt = jd_to_datetime(event_jd, tz)
        
        chart = get_mundane_chart(event_jd, lat, lon, tz, ayanamsa, EPHE_PATH)
        def dfrec(df): return json.loads(df.to_json(orient="records"))
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": "full_moon",
            "event_dt": format_datetime_for_js(event_dt),
            "direction": direction,
            "chart": {
                "tzname": chart["tzname"],
                "local_dt": format_datetime_for_js(chart["local_dt"]),
                "points": dfrec(chart["points"]),
                "houses": dfrec(chart["houses"]),
                "panchanga": dfrec(chart["panchanga"]),
                "shadbala": dfrec(chart.get("shadbala", [])),
                "shadbala_sthana": dfrec(chart.get("shadbala_sthana", [])),
                "shadbala_kala": dfrec(chart.get("shadbala_kala", [])),
                "ishta_kashta": dfrec(chart.get("ishta_kashta", [])),
            }
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full moon error: {e}")


@app.get("/mundane/tithi")
def tithi_chart(
    date: str = Query(...),
    target_tithi: int = Query(..., ge=1, le=30, description="Tithi number 1-30"),
    lat: float = Query(...),
    lon: float = Query(...),
    tz: str = Query(...),
    direction: str = Query("next"),
    ayanamsa: str = Query("Lahiri"),
):
    """Find when a specific tithi begins"""
    try:
        from dateutil import tz as tz_module
        ref_dt = datetime.strptime(date, "%Y-%m-%d").replace(
            hour=12, tzinfo=tz_module.gettz(tz)
        )
        start_jd = datetime_to_jd(ref_dt)
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        
        event_jd = find_tithi_start(start_jd, target_tithi, direction, ayanamsa_code)
        event_dt = jd_to_datetime(event_jd, tz)
        
        tithi_name = TITHI_NAMES_FULL[target_tithi - 1] if target_tithi <= 30 else f"Tithi {target_tithi}"
        
        chart = get_mundane_chart(event_jd, lat, lon, tz, ayanamsa, EPHE_PATH)
        def dfrec(df): return json.loads(df.to_json(orient="records"))
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": "tithi_start",
            "tithi_num": target_tithi,
            "tithi_name": tithi_name,
            "event_dt": format_datetime_for_js(event_dt),
            "direction": direction,
            "chart": {
                "tzname": chart["tzname"],
                "local_dt": format_datetime_for_js(chart["local_dt"]),
                "points": dfrec(chart["points"]),
                "houses": dfrec(chart["houses"]),
                "panchanga": dfrec(chart["panchanga"]),
                "shadbala": dfrec(chart.get("shadbala", [])),
                "shadbala_sthana": dfrec(chart.get("shadbala_sthana", [])),
                "shadbala_kala": dfrec(chart.get("shadbala_kala", [])),
                "ishta_kashta": dfrec(chart.get("ishta_kashta", [])),
            }
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tithi error: {e}")


@app.get("/mundane/solar-return")
def solar_return(
    natal_sun_lon: float = Query(..., description="Natal Sun longitude in degrees"),
    natal_asc_lon: float = Query(None, description="Natal Ascendant longitude (for Muntha calculation)"),
    birth_year: int = Query(None, description="Birth year (for Muntha calculation)"),
    year: int = Query(..., description="Year for solar return"),
    lat: float = Query(...),
    lon: float = Query(...),
    tz: str = Query(...),
    ayanamsa: str = Query("Lahiri"),
):
    """Find Tajika (Solar Return) chart - when Sun returns to natal position"""
    try:
        ensure_year_in_range(year, "Year")
        if birth_year is not None:
            ensure_year_in_range(birth_year, "Birth year")
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        event_jd = find_solar_return(natal_sun_lon, year, lat, lon, tz, ayanamsa_code)
        event_dt = jd_to_datetime(event_jd, tz)
        
        chart = get_mundane_chart(event_jd, lat, lon, tz, ayanamsa, EPHE_PATH)
        def dfrec(df): return json.loads(df.to_json(orient="records"))
        ashtakavarga = compute_ashtakavarga(chart["points"])
        
        # Calculate Muntha if natal ascendant and birth year are provided
        muntha = None
        if natal_asc_lon is not None and birth_year is not None:
            muntha = calculate_muntha(natal_asc_lon, birth_year, year)
        
        # Get Moon's longitude for compressed dasha calculation
        moon_point = None
        for p in chart["points"].to_dict(orient="records"):
            if p.get("Point") == "Moon":
                moon_point = p
                break
        
        # Calculate compressed Vimshottari and Yogini dashas for the year
        moon_lon = moon_point["Longitude (Dec)"] if moon_point else 0
        varsha_vim = build_varsha_vimshottari(moon_lon, event_dt)
        varsha_yog = build_varsha_yogini(moon_lon, event_dt)
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": "solar_return",
            "event_dt": format_datetime_for_js(event_dt),
            "year": year,
            "natal_sun_lon": natal_sun_lon,
            "muntha": muntha,
            "chart": {
                "tzname": chart["tzname"],
                "local_dt": format_datetime_for_js(chart["local_dt"]),
                "ayanamsa_name": chart.get("ayanamsa_name", ayanamsa),
                "ayanamsa_value": chart.get("ayanamsa_value", 0),
                "points": dfrec(chart["points"]),
                "houses": dfrec(chart["houses"]),
                "panchanga": dfrec(chart["panchanga"]),
            "vimshottari_md": dfrec(chart["vimshottari_md"]),
            "varsha_vimshottari": dfrec(varsha_vim),
            "varsha_yogini": dfrec(varsha_yog),
            "shadbala": dfrec(chart["shadbala"]),
            "shadbala_sthana": dfrec(chart.get("shadbala_sthana", [])),
            "shadbala_kala": dfrec(chart.get("shadbala_kala", [])),
            "ishta_kashta": dfrec(chart.get("ishta_kashta", [])),
                "bhava_bala": dfrec(chart.get("bhava_bala", [])),
                "ashtakavarga": {"bav": ashtakavarga["bav"], "sav": ashtakavarga["sav"]},
        }
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Solar return error: {e}")


@app.get("/mundane/tithi-pravesha")
def tithi_pravesha(
    natal_sun_lon: float = Query(..., description="Natal Sun longitude"),
    natal_tithi: int = Query(..., ge=1, le=30, description="Natal tithi number"),
    natal_asc_lon: float = Query(None, description="Natal Ascendant longitude (for Muntha calculation)"),
    birth_year: int = Query(None, description="Birth year (for Muntha calculation)"),
    year: int = Query(...),
    lat: float = Query(...),
    lon: float = Query(...),
    tz: str = Query(...),
    ayanamsa: str = Query("Lahiri"),
):
    """Find Tithi Pravesha - when Sun returns to natal position AND tithi matches"""
    try:
        ensure_year_in_range(year, "Year")
        if birth_year is not None:
            ensure_year_in_range(birth_year, "Birth year")
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        event_jd, sun_diff = find_tithi_pravesha(
            natal_sun_lon, natal_tithi, year, lat, lon, tz, ayanamsa_code
        )
        event_dt = jd_to_datetime(event_jd, tz)
        
        chart = get_mundane_chart(event_jd, lat, lon, tz, ayanamsa, EPHE_PATH)
        def dfrec(df): return json.loads(df.to_json(orient="records"))
        ashtakavarga = compute_ashtakavarga(chart["points"])
        
        # Calculate Muntha if natal ascendant and birth year are provided
        muntha = None
        if natal_asc_lon is not None and birth_year is not None:
            muntha = calculate_muntha(natal_asc_lon, birth_year, year)
        
        # Get Moon's longitude for compressed dasha calculation
        moon_point = None
        for p in chart["points"].to_dict(orient="records"):
            if p.get("Point") == "Moon":
                moon_point = p
                break
        
        # Calculate compressed Vimshottari and Yogini dashas for the year
        moon_lon = moon_point["Longitude (Dec)"] if moon_point else 0
        varsha_vim = build_varsha_vimshottari(moon_lon, event_dt)
        varsha_yog = build_varsha_yogini(moon_lon, event_dt)
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": "tithi_pravesha",
            "event_dt": format_datetime_for_js(event_dt),
            "year": year,
            "natal_sun_lon": natal_sun_lon,
            "natal_tithi": natal_tithi,
            "tithi_name": TITHI_NAMES_FULL[natal_tithi - 1],
            "sun_position_diff": round(sun_diff, 4),
            "muntha": muntha,
            "chart": {
                "tzname": chart["tzname"],
                "local_dt": format_datetime_for_js(chart["local_dt"]),
                "points": dfrec(chart["points"]),
                "houses": dfrec(chart["houses"]),
                "panchanga": dfrec(chart["panchanga"]),
                "vimshottari_md": dfrec(chart["vimshottari_md"]),
                "varsha_vimshottari": dfrec(varsha_vim),
                "varsha_yogini": dfrec(varsha_yog),
                "shadbala": dfrec(chart.get("shadbala", [])),
                "shadbala_sthana": dfrec(chart.get("shadbala_sthana", [])),
                "shadbala_kala": dfrec(chart.get("shadbala_kala", [])),
                "ishta_kashta": dfrec(chart.get("ishta_kashta", [])),
                "ashtakavarga": {"bav": ashtakavarga["bav"], "sav": ashtakavarga["sav"]},
            }
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tithi pravesha error: {e}")


@app.get("/mundane/nakshatra-pravesha")
def nakshatra_pravesha(
    natal_sun_lon: float = Query(..., description="Natal Sun longitude"),
    natal_moon_lon: float = Query(..., description="Natal Moon longitude"),
    natal_asc_lon: float = Query(None, description="Natal Ascendant longitude (for Muntha calculation)"),
    birth_year: int = Query(None, description="Birth year (for Muntha calculation)"),
    year: int = Query(...),
    lat: float = Query(...),
    lon: float = Query(...),
    tz: str = Query(...),
    ayanamsa: str = Query("Lahiri"),
):
    """Find Nakshatra Pravesha (Moon returning to natal Nakshatra near solar return)."""
    try:
        ensure_year_in_range(year, "Year")
        if birth_year is not None:
            ensure_year_in_range(birth_year, "Birth year")
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        natal_nak_idx = int(norm360(natal_moon_lon) // (360.0 / 27.0))
        event_jd = find_nakshatra_pravesha(natal_sun_lon, natal_nak_idx, year, lat, lon, tz, ayanamsa_code)
        event_dt = jd_to_datetime(event_jd, tz)

        chart = get_mundane_chart(event_jd, lat, lon, tz, ayanamsa, EPHE_PATH)
        def dfrec(df): return json.loads(df.to_json(orient="records"))
        ashtakavarga = compute_ashtakavarga(chart["points"])

        muntha = None
        if natal_asc_lon is not None and birth_year is not None:
            muntha = calculate_muntha(natal_asc_lon, birth_year, year)

        moon_point = None
        for p in chart["points"].to_dict(orient="records"):
            if p.get("Point") == "Moon":
                moon_point = p
                break
        moon_lon = moon_point["Longitude (Dec)"] if moon_point else 0
        varsha_vim = build_varsha_vimshottari(moon_lon, event_dt)
        varsha_yog = build_varsha_yogini(moon_lon, event_dt)

        return JSONResponse(content=jsonable_encoder({
            "event_type": "nakshatra_pravesha",
            "event_dt": format_datetime_for_js(event_dt),
            "year": year,
            "natal_sun_lon": natal_sun_lon,
            "natal_moon_lon": natal_moon_lon,
            "nakshatra_name": NAK_NAMES[natal_nak_idx],
            "muntha": muntha,
            "chart": {
                "tzname": chart["tzname"],
                "local_dt": format_datetime_for_js(chart["local_dt"]),
                "points": dfrec(chart["points"]),
                "houses": dfrec(chart["houses"]),
                "panchanga": dfrec(chart["panchanga"]),
                "vimshottari_md": dfrec(chart["vimshottari_md"]),
                "varsha_vimshottari": dfrec(varsha_vim),
                "varsha_yogini": dfrec(varsha_yog),
                "shadbala": dfrec(chart.get("shadbala", [])),
                "shadbala_sthana": dfrec(chart.get("shadbala_sthana", [])),
                "shadbala_kala": dfrec(chart.get("shadbala_kala", [])),
                "ishta_kashta": dfrec(chart.get("ishta_kashta", [])),
                "ashtakavarga": {"bav": ashtakavarga["bav"], "sav": ashtakavarga["sav"]},
            }
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nakshatra pravesha error: {e}")


@app.get("/match")
def match_charts(
    b_date: str = Query(None, description="Boy Date YYYY-MM-DD"),
    b_time: str = Query(None, description="Boy Time HH:MM"),
    b_lat: float = Query(None),
    b_lon: float = Query(None),
    b_tz: str = Query(None),
    b_nak: int = Query(None, description="Boy Nakshatra (1-27)"),
    b_pada: int = Query(None, description="Boy Pada (1-4)"),
    g_date: str = Query(None, description="Girl Date YYYY-MM-DD"),
    g_time: str = Query(None, description="Girl Time HH:MM"),
    g_lat: float = Query(None),
    g_lon: float = Query(None),
    g_tz: str = Query(None),
    g_nak: int = Query(None, description="Girl Nakshatra (1-27)"),
    g_pada: int = Query(None, description="Girl Pada (1-4)"),
    ayanamsa: str = Query("Lahiri"),
):
    """Calculate Marriage Compatibility (Das Kuta)"""
    try:
        def get_moon_from_input(date_str, time_str, lat, lon, tz_str, nak, pada, ayanamsa_name):
            # If Nakshatra/Pada provided, synthesize longitude
            if nak is not None and pada is not None:
                # 1 Nakshatra = 360/27 = 13.3333 deg
                # 1 Pada = 3.3333 deg
                # Start of Nakshatra
                nak_start = (nak - 1) * (360.0 / 27.0)
                # Start of Pada
                pada_start = nak_start + (pada - 1) * (360.0 / 27.0 / 4.0)
                # Center of Pada
                center = pada_start + (360.0 / 27.0 / 8.0)
                return center
            
            # Else compute from birth details
            if not date_str or not time_str:
                raise ValueError("Either Nakshatra/Pada OR full Birth Details must be provided.")
                
            if len(time_str.split(":")) == 2: time_str += ":00"
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            
            chart_res = compute_chart_with_tzname(
                dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
                lat, lon, tz_str, ayanamsa=ayanamsa_name
            )
            for p in chart_res["points"].to_dict(orient="records"):
                if p["Point"] == "Moon":
                    return p["Longitude (Dec)"]
            return 0.0

        b_moon = get_moon_from_input(b_date, b_time, b_lat, b_lon, b_tz, b_nak, b_pada, ayanamsa)
        g_moon = get_moon_from_input(g_date, g_time, g_lat, g_lon, g_tz, g_nak, g_pada, ayanamsa)

        # 5. Calculate Match
        result = ci_match.calculate_match(b_moon, g_moon)
        
        return JSONResponse(content=jsonable_encoder(result))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching error: {e}")


@app.get("/mundane/yoga-pravesha")
def yoga_pravesha(
    natal_sun_lon: float = Query(..., description="Natal Sun longitude"),
    natal_moon_lon: float = Query(..., description="Natal Moon longitude"),
    natal_asc_lon: float = Query(None, description="Natal Ascendant longitude (for Muntha calculation)"),
    birth_year: int = Query(None, description="Birth year (for Muntha calculation)"),
    year: int = Query(...),
    lat: float = Query(...),
    lon: float = Query(...),
    tz: str = Query(...),
    ayanamsa: str = Query("Lahiri"),
):
    """Find Yoga Pravesha (Sun+Moon yoga returning to natal yoga near solar return)."""
    try:
        ensure_year_in_range(year, "Year")
        if birth_year is not None:
            ensure_year_in_range(birth_year, "Birth year")
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        natal_yoga_idx = int(norm360(natal_sun_lon + natal_moon_lon) // (360.0 / 27.0))
        event_jd = find_yoga_pravesha(natal_sun_lon, natal_yoga_idx, year, lat, lon, tz, ayanamsa_code)
        event_dt = jd_to_datetime(event_jd, tz)

        chart = get_mundane_chart(event_jd, lat, lon, tz, ayanamsa, EPHE_PATH)
        def dfrec(df): return json.loads(df.to_json(orient="records"))
        ashtakavarga = compute_ashtakavarga(chart["points"])

        muntha = None
        if natal_asc_lon is not None and birth_year is not None:
            muntha = calculate_muntha(natal_asc_lon, birth_year, year)

        moon_point = None
        for p in chart["points"].to_dict(orient="records"):
            if p.get("Point") == "Moon":
                moon_point = p
                break
        moon_lon = moon_point["Longitude (Dec)"] if moon_point else 0
        varsha_vim = build_varsha_vimshottari(moon_lon, event_dt)
        varsha_yog = build_varsha_yogini(moon_lon, event_dt)

        return JSONResponse(content=jsonable_encoder({
            "event_type": "yoga_pravesha",
            "event_dt": format_datetime_for_js(event_dt),
            "year": year,
            "natal_sun_lon": natal_sun_lon,
            "natal_yoga_idx": natal_yoga_idx,
            "muntha": muntha,
            "chart": {
                "tzname": chart["tzname"],
                "local_dt": format_datetime_for_js(chart["local_dt"]),
                "points": dfrec(chart["points"]),
                "houses": dfrec(chart["houses"]),
                "panchanga": dfrec(chart["panchanga"]),
                "vimshottari_md": dfrec(chart["vimshottari_md"]),
                "varsha_vimshottari": dfrec(varsha_vim),
                "varsha_yogini": dfrec(varsha_yog),
                "shadbala": dfrec(chart.get("shadbala", [])),
                "shadbala_sthana": dfrec(chart.get("shadbala_sthana", [])),
                "shadbala_kala": dfrec(chart.get("shadbala_kala", [])),
                "ishta_kashta": dfrec(chart.get("ishta_kashta", [])),
                "ashtakavarga": {"bav": ashtakavarga["bav"], "sav": ashtakavarga["sav"]},
            }
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yoga pravesha error: {e}")


@app.get("/mundane/planet-sign-change")
def planet_sign_change(
    planet: str = Query(..., description="Planet name: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn"),
    date: str = Query(...),
    tz: str = Query(...),
    direction: str = Query("next"),
    target_sign: int = Query(None, ge=0, le=11, description="Target sign index 0-11 (optional)"),
    ayanamsa: str = Query("Lahiri"),
):
    """Find when a planet changes sign (or enters a specific sign)"""
    try:
        from dateutil import tz as tz_module
        from datetime import timedelta
        
        if planet not in PLANETS:
            raise HTTPException(status_code=400, detail=f"Invalid planet: {planet}")
        
        planet_code = PLANETS[planet]
        ref_dt = datetime.strptime(date, "%Y-%m-%d").replace(
            hour=12, tzinfo=tz_module.gettz(tz)
        )
        
        # When searching for "next", add a small offset to ensure we start from after the reference time
        # This prevents finding the same event again when the reference date is the date of a previous result
        if direction == "next":
            ref_dt = ref_dt + timedelta(hours=1)  # Add 1 hour to start searching from after noon
        
        start_jd = datetime_to_jd(ref_dt)
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        
        event_jd, new_sign = find_planet_sign_change(
            planet_code, start_jd, target_sign, direction, ayanamsa_code
        )
        event_dt = jd_to_datetime(event_jd, tz)
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": "planet_sign_change",
            "planet": planet,
            "new_sign_idx": new_sign,
            "new_sign_name": RASHI_SA[new_sign],
            "event_dt": format_datetime_for_js(event_dt),
            "direction": direction,
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planet sign change error: {e}")


@app.get("/mundane/planet-stationary")
def planet_stationary(
    planet: str = Query(...),
    date: str = Query(...),
    tz: str = Query(...),
    direction: str = Query("next"),
    station_type: str = Query("retrograde", description="Station type: retrograde or direct"),
):
    """Find when a planet becomes stationary (before retrograde or direct)"""
    try:
        from dateutil import tz as tz_module
        
        if planet not in PLANETS:
            raise HTTPException(status_code=400, detail=f"Invalid planet: {planet}")
        
        planet_code = PLANETS[planet]
        ref_dt = datetime.strptime(date, "%Y-%m-%d").replace(
            hour=12, tzinfo=tz_module.gettz(tz)
        )
        start_jd = datetime_to_jd(ref_dt)
        
        event_jd = find_planet_stationary(planet_code, start_jd, direction, station_type)
        event_dt = jd_to_datetime(event_jd, tz)
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": "planet_stationary",
            "planet": planet,
            "station_type": station_type,
            "event_dt": format_datetime_for_js(event_dt),
            "direction": direction,
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planet stationary error: {e}")


@app.get("/mundane/conjunction")
def conjunction(
    planet1: str = Query(...),
    planet2: str = Query(...),
    date: str = Query(...),
    tz: str = Query(...),
    direction: str = Query("next"),
    ayanamsa: str = Query("Lahiri"),
):
    """Find conjunction of two planets"""
    try:
        from dateutil import tz as tz_module
        
        if planet1 not in PLANETS or planet2 not in PLANETS:
            raise HTTPException(status_code=400, detail="Invalid planet name")
        
        planet1_code = PLANETS[planet1]
        planet2_code = PLANETS[planet2]
        ref_dt = datetime.strptime(date, "%Y-%m-%d").replace(
            hour=12, tzinfo=tz_module.gettz(tz)
        )
        start_jd = datetime_to_jd(ref_dt)
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        
        event_jd = find_conjunction(planet1_code, planet2_code, start_jd, direction, ayanamsa_code)
        event_dt = jd_to_datetime(event_jd, tz)
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": "conjunction",
            "planet1": planet1,
            "planet2": planet2,
            "event_dt": format_datetime_for_js(event_dt),
            "direction": direction,
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conjunction error: {e}")


@app.get("/mundane/opposition")
def opposition(
    planet1: str = Query(...),
    planet2: str = Query(...),
    date: str = Query(...),
    tz: str = Query(...),
    direction: str = Query("next"),
    ayanamsa: str = Query("Lahiri"),
):
    """Find opposition of two planets"""
    try:
        from dateutil import tz as tz_module
        
        if planet1 not in PLANETS or planet2 not in PLANETS:
            raise HTTPException(status_code=400, detail="Invalid planet name")
        
        planet1_code = PLANETS[planet1]
        planet2_code = PLANETS[planet2]
        ref_dt = datetime.strptime(date, "%Y-%m-%d").replace(
            hour=12, tzinfo=tz_module.gettz(tz)
        )
        start_jd = datetime_to_jd(ref_dt)
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        
        event_jd = find_opposition(planet1_code, planet2_code, start_jd, direction, ayanamsa_code)
        event_dt = jd_to_datetime(event_jd, tz)
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": "opposition",
            "planet1": planet1,
            "planet2": planet2,
            "event_dt": format_datetime_for_js(event_dt),
            "direction": direction,
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Opposition error: {e}")


# ----- Dasha Sub-period Endpoints -----

@app.get("/dasha/antardasha")
def api_get_antardasha(
    md_lord: str = Query(..., description="Mahadasha lord (e.g., Saturn)"),
    md_start: str = Query(..., description="Mahadasha start datetime (YYYY-MM-DD HH:MM:SS)"),
    md_duration_years: float = Query(..., description="Mahadasha duration in years")
):
    """Get all Antardasha periods within a Mahadasha."""
    try:
        result = get_vimshottari_antardasha(md_lord, md_start, md_duration_years)
        return JSONResponse(content=jsonable_encoder({"antardasha": result}))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Antardasha error: {e}")


@app.get("/dasha/pratyantardasha")
def api_get_pratyantardasha(
    md_lord: str = Query(..., description="Mahadasha lord"),
    ad_lord: str = Query(..., description="Antardasha lord"),
    ad_start: str = Query(..., description="Antardasha start datetime (YYYY-MM-DD HH:MM:SS)"),
    ad_duration_days: float = Query(..., description="Antardasha duration in days")
):
    """Get all Pratyantardasha periods within an Antardasha."""
    try:
        result = get_vimshottari_pratyantardasha(md_lord, ad_lord, ad_start, ad_duration_days)
        return JSONResponse(content=jsonable_encoder({"pratyantardasha": result}))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pratyantardasha error: {e}")


@app.get("/dasha/yogini/antardasha")
def api_get_yogini_antardasha(
    md_lord: str = Query(..., description="Yogini Mahadasha lord (e.g., Sankata)"),
    md_start: str = Query(..., description="Mahadasha start datetime (YYYY-MM-DD HH:MM:SS)"),
    md_duration_years: float = Query(..., description="Mahadasha duration in years")
):
    """Get all Antardasha periods within a Yogini Mahadasha."""
    try:
        result = get_yogini_antardasha(md_lord, md_start, md_duration_years)
        return JSONResponse(content=jsonable_encoder({"antardasha": result}))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yogini Antardasha error: {e}")


@app.get("/dasha/yogini/pratyantardasha")
def api_get_yogini_pratyantardasha(
    md_lord: str = Query(..., description="Yogini Mahadasha lord"),
    ad_lord: str = Query(..., description="Yogini Antardasha lord"),
    ad_start: str = Query(..., description="Antardasha start datetime (YYYY-MM-DD HH:MM:SS)"),
    ad_duration_days: float = Query(..., description="Antardasha duration in days")
):
    """Get all Pratyantardasha periods within a Yogini Antardasha."""
    try:
        result = get_yogini_pratyantardasha(md_lord, ad_lord, ad_start, ad_duration_days)
        return JSONResponse(content=jsonable_encoder({"pratyantardasha": result}))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yogini Pratyantardasha error: {e}")


@app.get("/dasha/generic/sub")
def api_get_generic_sub_period(
    system: str = Query(..., description="Dasa system name (e.g. ashtottari, chakra)"),
    lord: str = Query(..., description="Parent lord name"),
    start: str = Query(..., description="Parent start datetime (YYYY-MM-DD HH:MM:SS)"),
    duration_years: float = Query(..., description="Parent duration in years")
):
    """Get sub-periods (Antardasha/Pratyantardasha) for any Dasa system."""
    try:
        result = dasa_systems.calculate_generic_sub_periods(system, lord, start, duration_years)
        return JSONResponse(content=jsonable_encoder({"periods": result}))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Generic sub-period error: {e}")


# ----- Unified Mundane Chart Endpoint -----

@app.get("/api/mundane/chart")
def mundane_chart(
    # Location and time
    lat: float = Query(...),
    lon: float = Query(...),
    tz: str = Query(..., description="IANA timezone, e.g. Asia/Kolkata"),
    
    # Reference date for searching
    year: int = Query(..., description="Year to search for event"),
    
    # Mundane type
    mundane_type: str = Query(..., description="lunar|solar|conjunction|transit|stationary"),
    
    # Year type selection
    year_type: str = Query("sidereal", description="sidereal|tropical - affects zodiac system"),
    
    # Optional parameters based on type
    sign_index: Optional[int] = Query(None, ge=0, le=11, description="Sign index 0-11 for lunar/solar/conjunction"),
    
    planet1: Optional[str] = Query(None, description="First planet for conjunction"),
    planet2: Optional[str] = Query(None, description="Second planet for conjunction"),
    aspect: Optional[str] = Query(None, description="conjunction|opposition"),
    planet: Optional[str] = Query(None, description="Planet for transit/stationary"),
    target_sign: Optional[int] = Query(None, ge=0, le=11, description="Target sign index for transit"),
    stationary_type: Optional[str] = Query(None, description="retrograde|direct"),
    
    # Astro settings
    ayanamsa: str = Query("Lahiri"),
    house_sys: str = Query("O", description="house system code; 'O' = Sripati/Porphyry"),
    moseph: bool = Query(False)
):
    """
    Compute mundane chart event datetime and return full chart.
    
    This endpoint finds astronomical events (New Moon in sign, solar ingress, etc.)
    and generates a complete natal chart for that moment.
    """
    try:
        ensure_year_in_range(year, "Year")
        event_dt = None
        event_description = ""
        event_type_name = ""
        
        # Compute event based on mundane_type
        if mundane_type == "lunar":
            if sign_index is None:
                raise HTTPException(status_code=400, detail="sign_index required for lunar chart")
            
            event_dt = find_new_moon_in_sign(year, sign_index, lat, lon, tz, ayanamsa, year_type)
            if event_dt is None:
                raise HTTPException(status_code=404, detail=f"No New Moon found in {RASHI_SA[sign_index]} for year {year}")
            
            event_type_name = "Lunar Chart (New Moon)"
            event_description = f"New Moon in {RASHI_SA[sign_index]} ({'Sidereal' if year_type == 'sidereal' else 'Tropical'})"
            
        elif mundane_type == "solar":
            if sign_index is None:
                raise HTTPException(status_code=400, detail="sign_index required for solar chart")
            
            event_dt = find_solar_ingress(year, sign_index, lat, lon, tz, ayanamsa, year_type)
            if event_dt is None:
                raise HTTPException(status_code=404, detail=f"Solar ingress into {RASHI_SA[sign_index]} not found for year {year}")
            
            event_type_name = "Solar Chart (Ingress)"
            event_description = f"Sun enters {RASHI_SA[sign_index]} ({'Sidereal' if year_type == 'sidereal' else 'Tropical'})"
            
        elif mundane_type == "conjunction":
            if not planet1 or not planet2 or aspect is None:
                raise HTTPException(status_code=400, detail="planet1, planet2, and aspect required for conjunction")
            
            event_dt = find_planetary_conjunction(
                planet1, planet2, year, lat, lon, tz, ayanamsa, aspect, year_type, sign_index
            )
            if event_dt is None:
                msg = f"{planet1}-{planet2} {aspect} not found in year {year}"
                if sign_index is not None:
                    msg += f" in {RASHI_SA[sign_index]}"
                raise HTTPException(status_code=404, detail=msg)
            
            aspect_name = "Conjunction" if aspect == "conjunction" else "Opposition"
            event_type_name = f"{aspect_name} Chart"
            event_description = f"{planet1}-{planet2} {aspect_name}"
            if sign_index is not None:
                event_description += f" in {RASHI_SA[sign_index]}"
            event_description += f" ({'Sidereal' if year_type == 'sidereal' else 'Tropical'})"
            
        elif mundane_type == "transit":
            # TODO: Implement transit ingress finder
            raise HTTPException(status_code=501, detail="Transit ingress not yet implemented")
            
        elif mundane_type == "stationary":
            # TODO: Implement stationary finder
            raise HTTPException(status_code=501, detail="Stationary/retrogression not yet implemented")
        
        else:
            raise HTTPException(status_code=400, detail=f"Invalid mundane_type: {mundane_type}")
        
        # Now compute the full chart for this event datetime
        y, m, d = event_dt.year, event_dt.month, event_dt.day
        hh, mm, ss = event_dt.hour, event_dt.minute, event_dt.second
        
        # For tropical year type, don't use ayanamsa (use tropical coordinates)
        # For sidereal year type, use the specified ayanamsa
        chart_ayanamsa = None if year_type == 'tropical' else ayanamsa
        
        res = compute_chart_with_tzname(
            y, m, d, hh, mm, ss,
            lat, lon, tz,
            ephe_path=EPHE_PATH, use_moseph=moseph, house_sys=house_sys.encode("ascii"),
            ayanamsa=chart_ayanamsa
        )
        
        def dfrec(df): return json.loads(df.to_json(orient="records"))
        
        # Compute Ashtakavarga
        ashtakavarga = compute_ashtakavarga(res["points"])
        
        chart_data = {
            "tzname": res["tzname"],
            "local_dt": format_datetime_for_js(res["local_dt"]),
            "utc_dt": format_datetime_for_js(res["utc_dt"]),
            "ayanamsa_name": res.get("ayanamsa_name", "Tropical" if year_type == 'tropical' else ayanamsa),
            "ayanamsa_value": res.get("ayanamsa_value", 0),
            "points": dfrec(res["points"]),
            "houses": dfrec(res["houses"]),
            "vimshottari_md": dfrec(res["vimshottari_md"]),
            "yogini": dfrec(res["yogini"]),
            "shadbala": dfrec(res["shadbala"]),
            "shadbala_sthana": dfrec(res.get("shadbala_sthana", [])),
            "shadbala_kala": dfrec(res.get("shadbala_kala", [])),
            "ishta_kashta": dfrec(res.get("ishta_kashta", [])),
            "panchanga": dfrec(res["panchanga"]),
            "vargas": res.get("vargas", {}),
            "ashtakavarga": {
                "bav": ashtakavarga["bav"],
                "sav": ashtakavarga["sav"],
            },
        }
        
        return JSONResponse(content=jsonable_encoder({
            "event_type": event_type_name,
            "event_datetime": format_datetime_for_js(event_dt),
            "event_description": event_description,
            "year_type": year_type,
            "chart": chart_data
        }))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mundane chart error: {e}")


# ----- Astrocartography Endpoints -----

@app.get("/astrocartography/lagna-grid")
def lagna_grid(
    date: str = Query(..., description="Date YYYY-MM-DD"),
    time: str = Query(..., description="Time HH:MM or HH:MM:SS (UTC or local)"),
    tz: str = Query("UTC", description="IANA timezone for the time"),
    ayanamsa: str = Query("Lahiri", description="Ayanamsa system"),
    lat_step: float = Query(5.0, ge=2.0, le=15.0, description="Latitude step (degrees)"),
    lon_step: float = Query(10.0, ge=5.0, le=30.0, description="Longitude step (degrees)"),
):
    """
    Get Lagna (ascendant) sign for a grid of world locations at a given datetime.
    Used for Astrocartography map visualization.
    """
    try:
        from dateutil import tz as tz_module
        
        # Parse date and time
        if len(time.split(":")) == 2:
            time_s = time + ":00"
        else:
            time_s = time
        
        local_zone = tz_module.gettz(tz)
        dt_local = datetime.strptime(f"{date} {time_s}", "%Y-%m-%d %H:%M:%S")
        dt_local = dt_local.replace(tzinfo=local_zone)
        dt_utc = dt_local.astimezone(tz_module.UTC)
        
        # Calculate Julian Day
        ut_hour = dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
        jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut_hour, swe.GREG_CAL)
        
        # Get ayanamsa code
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        
        # Compute grid
        result = compute_lagna_grid(
            jd_ut, ayanamsa_code,
            ephe_path=EPHE_PATH,
            lat_step=lat_step,
            lon_step=lon_step
        )
        
        return JSONResponse(content=jsonable_encoder({
            "datetime": dt_local.isoformat(),
            "datetime_utc": dt_utc.isoformat(),
            "ayanamsa_name": ayanamsa,
            "ayanamsa_value": result["ayanamsa_value"],
            "grid": result["grid"],
            "planets": result["planets"],
            "grid_count": len(result["grid"])
        }))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lagna grid error: {e}")


@app.get("/astrocartography/lagna-location")
def lagna_location(
    date: str = Query(..., description="Date YYYY-MM-DD"),
    time: str = Query(..., description="Time HH:MM or HH:MM:SS"),
    tz: str = Query("UTC", description="IANA timezone for the time"),
    lat: float = Query(..., description="Latitude of location"),
    lon: float = Query(..., description="Longitude of location"),
    ayanamsa: str = Query("Lahiri", description="Ayanamsa system"),
):
    """
    Get Lagna (ascendant) for a specific location at a given datetime.
    Used for click-on-map feature in Astrocartography.
    """
    try:
        from dateutil import tz as tz_module
        
        # Parse date and time
        if len(time.split(":")) == 2:
            time_s = time + ":00"
        else:
            time_s = time
        
        local_zone = tz_module.gettz(tz)
        dt_local = datetime.strptime(f"{date} {time_s}", "%Y-%m-%d %H:%M:%S")
        dt_local = dt_local.replace(tzinfo=local_zone)
        dt_utc = dt_local.astimezone(tz_module.UTC)
        
        # Calculate Julian Day
        ut_hour = dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
        jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut_hour, swe.GREG_CAL)
        
        # Get ayanamsa code
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        
        # Compute lagna for this location
        result = compute_lagna_for_location(
            jd_ut, lat, lon, ayanamsa_code,
            ephe_path=EPHE_PATH
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return JSONResponse(content=jsonable_encoder({
            "lat": lat,
            "lon": lon,
            "datetime": dt_local.isoformat(),
            "ayanamsa_name": ayanamsa,
            **result
        }))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lagna location error: {e}")


@app.get("/astrocartography/rashi-lines")
def rashi_lines(
    date: str = Query(..., description="Date YYYY-MM-DD"),
    time: str = Query(..., description="Time HH:MM or HH:MM:SS (UTC or local)"),
    tz: str = Query("UTC", description="IANA timezone for the time"),
    ayanamsa: str = Query("Lahiri", description="Ayanamsa system"),
    lat_step: float = Query(2.0, ge=1.0, le=10.0, description="Latitude step for line resolution"),
):
    """
    Get the curved astrocartography lines showing where each rāśi rises (Ascendant)
    and where each planet is on the Ascendant at different latitudes.
    This creates the classic curved line visualization.
    """
    try:
        from dateutil import tz as tz_module
        
        # Parse date and time
        if len(time.split(":")) == 2:
            time_s = time + ":00"
        else:
            time_s = time
        
        local_zone = tz_module.gettz(tz)
        dt_local = datetime.strptime(f"{date} {time_s}", "%Y-%m-%d %H:%M:%S")
        dt_local = dt_local.replace(tzinfo=local_zone)
        dt_utc = dt_local.astimezone(tz_module.UTC)
        
        # Calculate Julian Day
        ut_hour = dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
        jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut_hour, swe.GREG_CAL)
        
        # Get ayanamsa code
        ayanamsa_code = get_ayanamsa_code(ayanamsa)
        
        # Compute rashi lines
        result = compute_rashi_lines(
            jd_ut, ayanamsa_code,
            ephe_path=EPHE_PATH,
            lat_step=lat_step
        )
        
        return JSONResponse(content=jsonable_encoder({
            "datetime": dt_local.isoformat(),
            "datetime_utc": dt_utc.isoformat(),
            "ayanamsa_name": ayanamsa,
            "ayanamsa_value": result["ayanamsa_value"],
            "rashi_lines": result["rashi_lines"],
            "planets": result["planets"]
        }))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rashi lines error: {e}")


# ----- Serve the minimal UI under /ui -----
if not UI_DIR.exists():
    UI_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/ui", StaticFiles(directory=str(UI_DIR), html=True), name="ui")
