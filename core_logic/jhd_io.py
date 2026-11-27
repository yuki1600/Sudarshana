"""
core_logic/jhd_io.py
====================
Reader/writer for ``.jhd`` chart files.

The format is **versioned and variable-length** (the 18 sample charts in
``data/sample_charts`` come in 7-, 8-, 14-, 15-, 17- and 18-line variants) and
the file stores **no name** (the name is the file name).  Modern layouts are read as whitespace-separated
fields (three integers, seven decimals, two integers, two words, an integer, two decimals, an integer) with
defaults for the fields a shorter file lacks (``< 8`` read: altitude 425; ``< 11``: zones = line 5, no DST; ``< 14``: place
Unknown; ``< 15``: Gregorian; ``< 17``: 1013.25 hPa, 20 C; ``< 18``: line 18 = 0):

====  =======================================================================
line  meaning
====  =======================================================================
1-3   month, day, year
4     birth time, H.MM with seconds as /6000 (``7.200000`` = 7h20m, ``17.506667`` = 17h50m40s)
      — the same packing as lines 5-7 (all four decode alike)
5     time zone, H.MM, **east negative** (-5.30 = 5h30m east; -4.392667 = 4h39.2667m).
      This is the zone the chart is computed with.
6-7   longitude, latitude as D.MM (degrees.minutes), **east longitude negative**,
      north latitude positive (-81.08 = 81 deg 08' E)
8     altitude (m) in modern files; in the legacy "ephemeris" variant a fraction (unused)
9-10  modern: standard and DST zone (decimal hours, east negative) for DST re-evaluation
      (``core_logic.dst``).  Legacy: 8 sidereal longitudes (Sun..mean Rahu) + lagna
11    modern: DST flag (1 = the chart is in DST)
12    modern: country index into the atlas's country table (105 = India)
13-14 modern: city, country ('^' stands for a space)
15    modern: calendar, 1 = Gregorian, 0 = Julian
16-17 modern: pressure (hPa), temperature (C)
18    modern: an integer whose meaning is not established (0)
last  legacy only: 9-character 0/1 mask = retrograde flags, Sun..Saturn then Rahu, Ketu
      (nodes always 0).  Matches the ephemeris on all 5 legacy samples.
====  =======================================================================

Legacy files embed the longitudes computed when they were written; they are exposed as
``cached_longitudes`` and used as an oracle for the ephemeris layer.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

LEGACY_PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]
_MASK = re.compile(r"^[01]{9}$")


def decode_hm(value: str) -> float:
    """``H.MM`` (or ``D.MM``) text -> decimal hours/degrees.  Fraction digits are minutes/100."""
    v = float(value)
    sign = -1.0 if v < 0 or value.strip().startswith("-") else 1.0
    v = abs(v)
    whole = int(v)
    minutes = round((v - whole) * 100.0, 6)
    return sign * (whole + minutes / 60.0)


def encode_hm(value: float) -> float:
    """Inverse of :func:`decode_hm`."""
    sign = -1.0 if value < 0 else 1.0
    v = abs(value)
    whole = int(v)
    minutes = (v - whole) * 60.0
    if minutes >= 59.9999995:  # rounding guard
        whole, minutes = whole + 1, 0.0
    return sign * (whole + minutes / 100.0)


def parse_jhd_string(content: str) -> Dict[str, Any]:
    """Parse ``.jhd`` text of any known layout into a dict (see module docstring)."""
    lines = [ln.strip() for ln in content.replace("\r", "").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    if len(lines) < 7:
        raise ValueError(f"Invalid JHD format: need at least 7 lines, got {len(lines)}")
    try:
        month, day, year = int(float(lines[0])), int(float(lines[1])), int(float(lines[2]))
        time_tok = lines[3]
        raw_time = float(time_tok)
        raw_tz = float(lines[4])
        raw_lon = float(lines[5])
        raw_lat = float(lines[6])
    except ValueError as exc:
        raise ValueError(f"Error parsing JHD header: {exc}") from exc

    hour_local = decode_hm(time_tok)  # line 4 is decoded like lines 5-7
    tz_east = -decode_hm(lines[4])
    lon_east = -decode_hm(lines[5])
    lat = decode_hm(lines[6])

    out: Dict[str, Any] = {
        "year": year, "month": month, "day": day,
        "hour_local": hour_local, "tz_east_hours": tz_east,
        "longitude_east": lon_east, "latitude": lat,
        "altitude_m": 0.0, "city": "", "country": "", "country_index": None,
        "tz_standard_east": tz_east, "tz_dst_east": tz_east, "dst": False, "gregorian": True,
        "field18": 0, "atmosphere": None, "cached_longitudes": None, "legacy_flags": None,
        "layout": "basic",
        "raw_header": {"time": raw_time, "tz": raw_tz, "lon": raw_lon, "lat": raw_lat},
    }

    n = len(lines)
    legacy = n >= 18 and _MASK.match(lines[-1]) is not None
    if legacy:
        out["layout"] = "legacy_ephemeris"
        vals = [float(x) for x in lines[8:17]]
        out["cached_longitudes"] = dict(zip(LEGACY_PLANET_ORDER, vals[:8]))
        out["cached_lagna"] = vals[8]
        out["legacy_flags"] = lines[-1]
        out["legacy_fraction"] = float(lines[7])
    else:
        if n >= 8:
            out["altitude_m"] = float(lines[7])
            out["layout"] = "v8"
        if n >= 10:
            # lines 9/10: standard and DST zone, decimal hours, east negative
            out["tz_standard_east"], out["tz_dst_east"] = -float(lines[8]), -float(lines[9])
            out["layout"] = "v14"
        if n >= 11:
            out["dst"] = int(float(lines[10])) != 0
        if n >= 12:
            out["country_index"] = int(float(lines[11]))
        if n >= 14:
            out["city"], out["country"] = lines[12].replace("^", " "), lines[13].replace("^", " ")
        if n >= 15:
            out["layout"] = "v15"
            out["gregorian"] = int(float(lines[14])) != 0
        if n >= 17:
            out["layout"] = "v17"
            out["atmosphere"] = {"pressure": float(lines[15]), "temperature": float(lines[16])}
        if n >= 18:
            out["layout"] = "v18"
            out["field18"] = int(float(lines[17]))
    out["rating"] = out["country_index"]  # old name of line 12

    # --- backwards-compatible aliases -----------------------------------
    out["birth_time_hours"] = hour_local
    h = int(hour_local)
    m = int((hour_local - h) * 60.0)
    out["birth_time_hms"] = (h, m, round(((hour_local - h) * 60.0 - m) * 60.0, 2))
    out["timezone_offset"] = out["tz_east_hours"]
    out["longitude"] = lon_east
    out["name"] = ""
    out["format"] = f".jhd ({out['layout']})"
    return out


def parse_jhd_file(filepath: str) -> Dict[str, Any]:
    """Read and parse a ``.jhd`` file.  ``name`` is taken from the file name (no name is stored)."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"JHD file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
        res = parse_jhd_string(fh.read())
    res["filepath"] = filepath
    res["name"] = os.path.splitext(os.path.basename(filepath))[0]
    return res


def serialize_to_jhd(chart: Dict[str, Any], filepath: Optional[str] = None) -> str:
    """
    Write the modern 18-line layout.  Accepts the dict produced by :func:`parse_jhd_string`
    (``hour_local``, ``tz_east_hours``, ``longitude_east``, ``latitude`` ...).
    """
    atm = chart.get("atmosphere") or {}
    tz_east = float(chart["tz_east_hours"])
    lines: List[str] = [
        str(int(chart["month"])), str(int(chart["day"])), str(int(chart["year"])),
        f"{encode_hm(float(chart['hour_local'])):.6f}",
        f"{encode_hm(-tz_east):.6f}",
        f"{encode_hm(-float(chart['longitude_east'])):.6f}",
        f"{encode_hm(float(chart['latitude'])):.6f}",
        f"{float(chart.get('altitude_m', 0.0)):.6f}",
        f"{-float(chart.get('tz_standard_east', tz_east)):.6f}", f"{-float(chart.get('tz_dst_east', tz_east)):.6f}",
        "1" if chart.get("dst") else "0", str(int(chart.get("country_index") or chart.get("rating") or 0)),
        (chart.get("city") or "Unknown").replace(" ", "^"), (chart.get("country") or "Unknown").replace(" ", "^"),
        "1" if chart.get("gregorian", True) else "0",
        f"{float(atm.get('pressure', 1013.25)):.6f}",
        f"{float(atm.get('temperature', 20.0)):.6f}",
        str(int(chart.get("field18") or 0)),
    ]
    text = "\n".join(lines) + "\n"
    if filepath:
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(text)
    return text


def to_birth_data(chart: Dict[str, Any]):
    """Convert a parsed chart to :class:`core_logic.ephemeris.BirthData`."""
    from .ephemeris import BirthData
    atm = chart.get("atmosphere") or {}
    return BirthData(
        year=chart["year"], month=chart["month"], day=chart["day"],
        hour_local=chart["hour_local"], tz_east_hours=chart["tz_east_hours"],
        longitude_east=chart["longitude_east"], latitude=chart["latitude"],
        altitude_m=chart.get("altitude_m", 0.0),
        place=", ".join(p for p in (chart.get("city"), chart.get("country")) if p),
        gregorian=chart.get("gregorian", True),
        **({"pressure_hpa": atm["pressure"], "temperature_c": atm["temperature"]} if "pressure" in atm else {}),
    )
