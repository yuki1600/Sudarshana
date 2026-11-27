"""Place typeahead: GeoNames ``databases/places.db`` (start.sh builds it when it is missing).

GeoNames data is free under CC-BY 4.0 (build with ``python databases/build_places_db.py``).
Search hits are dicts of a place's name, country, coordinates, zone offsets and IANA zone, plus its ``admin1_*`` state fields.
"""
from __future__ import annotations

import functools
import os
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_ROOT = os.path.join(os.path.dirname(__file__), "..")
_DB = os.path.join(_ROOT, "databases", "places.db")


def _db_path() -> str | None:
    return _DB if os.path.isfile(_DB) else None


@functools.lru_cache(maxsize=256)
def _tz_offsets(name: str) -> tuple[float, float]:
    """(standard, DST) hours east-positive from an IANA zone name."""
    try:
        tz = ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return 0.0, 0.0
    jan = datetime(2024, 1, 15, tzinfo=tz).utcoffset()
    jul = datetime(2024, 7, 15, tzinfo=tz).utcoffset()
    if jan is None or jul is None:
        return 0.0, 0.0
    a, b = jan.total_seconds() / 3600.0, jul.total_seconds() / 3600.0
    return min(a, b), max(a, b)


def _place_dict(name: str, lat: float, lon: float, country: str, timezone: str | None,
                admin1_code: str = "", admin1_name: str = "", altitude: float | None = None) -> dict:
    std, dst_off = _tz_offsets(timezone) if timezone else (0.0, 0.0)
    return {
        "country_code": country or "",
        "name": name,
        "latitude": lat,
        "longitude": lon,
        "tz_standard": std,
        "tz_dst": dst_off,
        "a": 0,
        "b": 0,
        "admin1_code": admin1_code or "",
        "admin1_name": admin1_name or "",
        "timezone": timezone or "",  # IANA name; /api/zone uses this for historical DST
        "altitude": altitude,        # metres above sea level (GeoNames); None when unknown
    }


def zone_at(place: dict, year: int, month: int, day: int, hour: float) -> tuple[float, bool]:
    """Effective east-positive zone and DST flag on a local civil date.

    Uses the IANA zone (GeoNames) so transitions follow the tz database across years; a place with
    only hour offsets keeps its standard zone.
    """
    iana = (place.get("timezone") or "").strip()
    if iana:
        try:
            tz = ZoneInfo(iana)
        except ZoneInfoNotFoundError:
            tz = None
        if tz is not None:
            h = int(hour)
            m = int(round((hour - h) * 60)) % 60
            # fold=0: the first occurrence if the local time is ambiguous (fall-back hour)
            when = datetime(year, month, day, h, m, tzinfo=tz)
            off = when.utcoffset()
            if off is None:
                return 0.0, False
            delta = when.dst()
            return off.total_seconds() / 3600.0, bool(delta and delta.total_seconds())

    return float(place["tz_standard"]), False


@functools.lru_cache(maxsize=1)
def _connect() -> sqlite3.Connection | None:
    path = _db_path()
    if not path:
        return None
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


@functools.lru_cache(maxsize=1)
def _elevation_sql(con: sqlite3.Connection) -> str:
    """A places.db built before the elevation column still searches: its places have no altitude."""
    return "p.elevation" if any(c["name"] == "elevation" for c in con.execute("PRAGMA table_info(places)")) else "NULL"


def countries() -> list[dict[str, str]]:
    """ISO countries present in the GeoNames DB (none before it is built)."""
    con = _connect()
    if con is not None:
        rows = con.execute(
            """
            SELECT c.iso2 AS code, c.name
            FROM countries AS c
            WHERE EXISTS (SELECT 1 FROM places p WHERE p.country_iso2 = c.iso2)
            ORDER BY c.name COLLATE NOCASE
            """
        ).fetchall()
        if rows:
            return [{"code": r["code"], "name": r["name"]} for r in rows]
    return []


def states(country: str) -> list[dict[str, str]]:
    """Admin1 (state/province) rows for a country, from GeoNames."""
    cc = (country or "").strip().upper()
    if not cc:
        return []
    con = _connect()
    if con is None:
        return []
    rows = con.execute(
        """
        SELECT a.key, a.name, substr(a.key, length(?) + 2) AS code
        FROM admin1 AS a
        WHERE a.key LIKE ? || '.%'
          AND EXISTS (
            SELECT 1 FROM places p
            WHERE p.country_iso2 = ? AND p.admin1_code = substr(a.key, length(?) + 2)
          )
        ORDER BY a.name COLLATE NOCASE
        """,
        (cc, cc, cc, cc),
    ).fetchall()
    return [{"code": r["code"], "name": r["name"]} for r in rows if r["code"]]


def _search_geonames(prefix: str, limit: int, country: str | None, state: str | None) -> list[dict]:
    """Search all places by name; country/state only boost matching rows to the top."""
    con = _connect()
    if con is None:
        return []
    p = prefix.strip()
    if len(p) < 2:
        return []
    like = p + "%"
    word = "% " + p + "%"
    alt = "%," + p + "%"
    alt_start = p + "%"
    cc = (country or "").strip().upper()
    st = (state or "").strip()
    # prefer: 0 = country+state, 1 = country, 2 = everywhere else
    prefer_sql = "2"
    prefer_args: list = []
    if cc and st:
        prefer_sql = """CASE
                 WHEN p.country_iso2 = ? AND p.admin1_code = ? THEN 0
                 WHEN p.country_iso2 = ? THEN 1
                 ELSE 2 END"""
        prefer_args = [cc, st, cc]
    elif cc:
        prefer_sql = "CASE WHEN p.country_iso2 = ? THEN 0 ELSE 1 END"
        prefer_args = [cc]

    rows = con.execute(
        f"""
        SELECT p.name, p.lat, p.lon, p.country_iso2, p.timezone, p.population, {_elevation_sql(con)} AS elevation,
               p.admin1_code, COALESCE(a.name, '') AS admin1_name,
               {prefer_sql} AS prefer,
               CASE
                 WHEN p.name LIKE ? COLLATE NOCASE OR p.asciiname LIKE ? COLLATE NOCASE THEN 0
                 WHEN p.name LIKE ? COLLATE NOCASE OR p.asciiname LIKE ? COLLATE NOCASE THEN 1
                 ELSE 2
               END AS rank
        FROM places AS p
        LEFT JOIN admin1 AS a ON a.key = p.country_iso2 || '.' || p.admin1_code
        WHERE p.name LIKE ? COLLATE NOCASE OR p.asciiname LIKE ? COLLATE NOCASE
           OR p.name LIKE ? COLLATE NOCASE OR p.asciiname LIKE ? COLLATE NOCASE
           OR p.alternatenames LIKE ? COLLATE NOCASE OR p.alternatenames LIKE ? COLLATE NOCASE
        ORDER BY prefer, rank, p.population DESC, p.name COLLATE NOCASE
        LIMIT ?
        """,
        [*prefer_args, like, like, word, word, like, like, word, word, alt_start, alt, limit],
    ).fetchall()
    return [
        _place_dict(r["name"], r["lat"], r["lon"], r["country_iso2"], r["timezone"],
                    r["admin1_code"] or "", r["admin1_name"] or "", r["elevation"])
        for r in rows
    ]



def search(prefix: str, limit: int = 20, country: str | None = None, state: str | None = None) -> list[dict]:
    p = prefix.strip()
    if not p:
        return []
    return _search_geonames(p, limit, country, state)
