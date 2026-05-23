"""
Arudha Padas and Upapada calculations.
"""

from __future__ import annotations

from typing import Any

from src.jyotisha.base.constants import SIGN_LORD, RASHI_SA
from src.jyotisha.base.utils import lon_to_sign_idx, sign_dms_str, rashi_name
from src.jyotisha.identity.vargas import navamsa_for, get_all_vargas, get_varga_names, get_nakshatra_details


def arudha_sign_for_house(house_sign_idx: int, lord_sign_idx: int | None) -> int | None:
    if lord_sign_idx is None:
        return None
    offset = (lord_sign_idx - house_sign_idx + 12) % 12
    if offset == 3:
        return lord_sign_idx
    pada_idx = (lord_sign_idx + offset) % 12
    if offset == 0:
        return (house_sign_idx + 9) % 12
    if offset == 6:
        return (house_sign_idx + 3) % 12
    if pada_idx == house_sign_idx:
        return (house_sign_idx + 9) % 12
    if pada_idx == (house_sign_idx + 6) % 12:
        return (house_sign_idx + 3) % 12
    return pada_idx


def compute_arudha_padas(asc_sign_idx: int, numeric_lons: dict[str, float]) -> list[dict[str, Any]]:
    arudha_results = []
    for offset in range(12):
        house_num = offset + 1
        house_sign_idx = (asc_sign_idx + offset) % 12
        lord = SIGN_LORD.get(house_sign_idx)
        lord_lon = numeric_lons.get(lord, None)
        lord_sign_idx = lon_to_sign_idx(lord_lon) if lord_lon is not None else None
        pada_sign_idx = arudha_sign_for_house(house_sign_idx, lord_sign_idx)
        if pada_sign_idx is None:
            continue
        pada_lon = pada_sign_idx * 30.0
        nsi, _ = navamsa_for(pada_lon)
        nak_det = get_nakshatra_details(pada_lon)
        all_vargas = get_all_vargas(pada_lon)
        varga_names = get_varga_names(pada_lon)
        is_ul = house_num == 12
        point_name = "Arudha Lagna" if house_num == 1 else ("Upapada Lagna" if is_ul else f"Arudha H{house_num}")

        row_data = {
            "Point": point_name,
            "Longitude (Sign DMS)": sign_dms_str(pada_lon),
            "Longitude (Dec)": round(pada_lon, 4),
            "Rashi": rashi_name(pada_lon),
            "Rashi_Idx": pada_sign_idx,
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi],
            "Navamsha_Idx": nsi,
            "D2": all_vargas['D2'], "D3": all_vargas['D3'], "D4": all_vargas['D4'],
            "D7": all_vargas['D7'], "D10": all_vargas['D10'], "D12": all_vargas['D12'],
            "D16": all_vargas['D16'], "D20": all_vargas['D20'], "D24": all_vargas['D24'],
            "D27": all_vargas['D27'], "D30": all_vargas['D30'], "D40": all_vargas['D40'],
            "D45": all_vargas['D45'], "D60": all_vargas['D60'],
            "Varga_Names": varga_names,
            "Latitude (DMS)": "—",
            "Speed (DMS/day)": "—",
            "Retro": False,
            "IsArudha": True,
            "House": house_num,
        }

        arudha_results.append({
            "point_name": point_name,
            "pada_lon": pada_lon,
            "all_vargas": all_vargas,
            "row_data": row_data
        })
    return arudha_results


# ---------------------------------------------------------------------------
# Argala (Ch. 31) — Intervention analysis
# ---------------------------------------------------------------------------

_ARGALA_POSITIVE = [2, 4, 11]   # house offsets that form Argala on reference
_ARGALA_VIRODHA  = [12, 10, 3]  # house offsets that obstruct Argala

_REF_POINTS = [
    "Ascendant (1st House Cusp)", "Sun", "Moon", "Mars",
    "Mercury", "Jupiter", "Venus", "Saturn",
    "Rahu (true)", "Ketu (true)",
]


def compute_argala(
    asc_sign_idx: int,
    numeric_lons: dict[str, float],
) -> list[dict]:
    """
    Compute Argala (intervention) for each reference point.

    For each reference sign R:
      Positive Argala: planets in 2nd, 4th, 11th from R
      Virodha Argala : planets in 12th, 10th, 3rd from R (neutralise positive)
      Net Argala     : positive not fully obstructed

    Returns list of dicts per reference point.
    """
    from src.jyotisha.base.constants import RASHI_SA
    rows = []

    ref_lons: list[tuple[str, float]] = [
        (name, lon)
        for name in _REF_POINTS
        if (lon := numeric_lons.get(name)) is not None
    ]

    # Build sign → planets map
    sign_planets: dict[int, list[str]] = {i: [] for i in range(12)}
    _all_pl = ["Sun", "Moon", "Mars", "Mercury", "Jupiter",
               "Venus", "Saturn", "Rahu (true)", "Ketu (true)"]
    for p in _all_pl:
        if p in numeric_lons:
            si = lon_to_sign_idx(numeric_lons[p])
            sign_planets[si].append(p)

    for ref_name, ref_lon in ref_lons:
        ref_si = lon_to_sign_idx(ref_lon)
        pos_argala: dict[int, list[str]] = {}
        vir_argala: dict[int, list[str]] = {}

        for offset in _ARGALA_POSITIVE:
            target = (ref_si + offset - 1) % 12
            pl_there = [p for p in sign_planets[target] if p not in (ref_name,)]
            if pl_there:
                pos_argala[offset] = pl_there

        for offset in _ARGALA_VIRODHA:
            target = (ref_si + offset - 1) % 12
            pl_there = [p for p in sign_planets[target] if p not in (ref_name,)]
            if pl_there:
                vir_argala[offset] = pl_there

        # Net: positive argala exists in positions not fully obstructed
        net_active: list[str] = []
        obstruction_pairs = [(2, 12), (4, 10), (11, 3)]
        for pos_off, vir_off in obstruction_pairs:
            pos_pl = pos_argala.get(pos_off, [])
            vir_pl = vir_argala.get(vir_off, [])
            if pos_pl:
                if len(pos_pl) > len(vir_pl):
                    net_active += pos_pl
                elif not vir_pl:
                    net_active += pos_pl

        rows.append({
            "Reference": ref_name,
            "Positive Argala (2nd)": ", ".join(pos_argala.get(2, [])) or "—",
            "Positive Argala (4th)": ", ".join(pos_argala.get(4, [])) or "—",
            "Positive Argala (11th)": ", ".join(pos_argala.get(11, [])) or "—",
            "Virodha (12th)": ", ".join(vir_argala.get(12, [])) or "—",
            "Virodha (10th)": ", ".join(vir_argala.get(10, [])) or "—",
            "Virodha (3rd)": ", ".join(vir_argala.get(3, [])) or "—",
            "Net Argala Active": ", ".join(net_active) if net_active else "—",
        })

    return rows
