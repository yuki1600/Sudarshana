"""
Aspect grid and aspect score calculations.
"""

from __future__ import annotations

import colorsys
import pandas as pd
from src.jyotisha.base.utils import norm360, sign_dms_str, aspect_strength_pct


def aspect_score(src_lon: float, tgt_lon: float, src_graha: str, orb: float = 12.0) -> float:
    ang = norm360(tgt_lon - src_lon)

    def near(a: float) -> float:
        d = min(abs(norm360(ang - a)), 360 - abs(norm360(ang - a)))
        return max(0.0, 1.0 - d / orb)

    allowed = {0, 180}
    if src_graha == "Jupiter":
        allowed |= {120, 240}
    if src_graha == "Mars":
        allowed |= {90, 270}
    if src_graha == "Saturn":
        allowed |= {60, 300}
    return max(near(a) for a in allowed)


def pct_to_color(pct: float) -> str:
    pct_clamped = max(0.0, min(100.0, pct))
    hue = (pct_clamped / 100.0) * 120.0
    r, g, b = colorsys.hls_to_rgb(hue / 360.0, 0.5, 0.7)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


def compute_aspect_grid(numeric_lons: dict[str, float], cusps_sid: list[float]) -> pd.DataFrame:
    aspect_planets = [
        p for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu (true)", "Ketu (true)", "Uranus", "Neptune", "Pluto"]
        if p in numeric_lons
    ]
    aspect_rows = []
    targets = [{"Name": p, "Longitude": numeric_lons[p]} for p in aspect_planets] + [
        {"Name": f"House {i + 1}", "Longitude": c} for i, c in enumerate(cusps_sid)
    ]
    for tgt in targets:
        row = {"Target": tgt["Name"], "Longitude": sign_dms_str(tgt["Longitude"])}
        for src in aspect_planets:
            if tgt["Name"] == src:
                row[src] = None
                row[f"{src}_color"] = "#9aa3ad"
                continue
            pct = round(aspect_strength_pct(norm360(tgt["Longitude"] - numeric_lons[src]), src), 1)
            row[src] = pct
            row[f"{src}_color"] = pct_to_color(pct)
        aspect_rows.append(row)
    return pd.DataFrame(aspect_rows)
