"""
Shadbala (six-fold strength), Bhava Bala, and Ishta/Kashta calculations.
"""

from __future__ import annotations

import swisseph as swe
import pandas as pd
from datetime import datetime, timedelta
from typing import Any

from src.jyotisha.base.constants import (
    DEBIL, EXALT, MOOLATR, PERM_FRIENDS, PERM_ENEMIES, NAISARGIKA,
    SIGN_INDEX, SIGN_LORD, MIN_SHADBALA_RUPA, MAX_SHADBALA_RUPA,
    BENEFICS, MALEFICS, RASHI_SA, RASHI_ABR, PLANETS, GRAHAS_FOR_HOUSE
)
from src.jyotisha.base.utils import norm360, lon_to_sign_idx, sign_dms_str, dms_str, rashi_name
from src.jyotisha.identity.vargas import navamsa_for
from src.jyotisha.relational.aspects import aspect_score


def lon_deg(sign_name: str, deg: float) -> float:
    return SIGN_INDEX[sign_name] * 30.0 + deg


def relation_to_lord(graha: str, lord: str) -> str:
    if lord in PERM_FRIENDS[graha] and graha in PERM_FRIENDS.get(lord, set()):
        return "great_friend"
    if lord in PERM_ENEMIES[graha] and graha in PERM_ENEMIES.get(lord, set()):
        return "great_enemy"
    if lord in PERM_FRIENDS[graha] or graha in PERM_FRIENDS.get(lord, set()):
        return "friend"
    if lord in PERM_ENEMIES[graha] or graha in PERM_ENEMIES.get(lord, set()):
        return "enemy"
    return "neutral"


def in_moolatrikona(graha: str, lon_: float) -> bool:
    if graha not in MOOLATR:
        return False
    s, a, b = MOOLATR[graha]
    si = SIGN_INDEX[s]
    deg = norm360(lon_) - si * 30.0
    if deg < 0:
        deg += 360
    return 0 <= deg < 30 and (a <= deg <= b)


def uccha_bala(lon_: float, graha: str) -> float:
    if graha not in DEBIL:
        return 0.0
    deb_sign, deb_deg = DEBIL[graha]
    deb = lon_deg(deb_sign, deb_deg)
    dist = min(abs(norm360(lon_ - deb)), 360 - abs(norm360(lon_ - deb)))
    dist = dist if dist <= 180.0 else 360.0 - dist
    return max(0.0, dist / 3.0)


MALE = {"Sun", "Mars", "Jupiter", "Saturn"}
FEMALE = {"Moon", "Venus"}


def oja_yugma_bala(lon_: float, graha: str) -> float:
    sidx = lon_to_sign_idx(lon_)
    even = (sidx % 2 == 1)
    sig_gain = 15.0 if ((graha in FEMALE and even) or (graha not in FEMALE and not even)) else 0.0
    nsign, _ = navamsa_for(lon_)
    neven = (nsign % 2 == 1)
    nav_gain = 15.0 if ((graha in FEMALE and neven) or (graha not in FEMALE and not neven)) else 0.0
    if graha == "Mercury":
        return 15.0
    return sig_gain + nav_gain


def kendradi_bala(lon_: float, starts: list[float], ends: list[float]) -> float:
    def _contains(start: float, end: float, x: float) -> bool:
        start = norm360(start)
        end = norm360(end)
        x = norm360(x)
        return (start <= end and start <= x < end) or (start > end and (x >= start or x < end))

    h = 12
    for i in range(12):
        if _contains(starts[i], ends[i], lon_):
            h = i + 1
            break
    return 60.0 if h in (1, 4, 7, 10) else (30.0 if h in (2, 5, 8, 11) else 15.0)


def drekkana_bala(lon_: float, graha: str) -> float:
    intra = lon_ - 30 * lon_to_sign_idx(lon_)
    drek = int(intra // 10) + 1
    if graha in MALE:
        return 15.0 if drek == 1 else 0.0
    if graha in FEMALE:
        return 15.0 if drek == 2 else 0.0
    return 15.0 if drek == 3 else 0.0


SV_WEIGHTS = {
    "moolatrikona": 45.0,
    "own": 30.0,
    "great_friend": 20.0,
    "friend": 15.0,
    "neutral": 10.0,
    "enemy": 4.0,
    "great_enemy": 2.0
}


def varga_sign_D1(lon_: float) -> int:
    return lon_to_sign_idx(lon_)


def varga_sign_D2(lon_: float) -> int:
    si = lon_to_sign_idx(lon_)
    intra = lon_ - 30 * si
    odd = (si % 2 == 0)
    return 4 if (odd and intra < 15) or ((not odd) and intra >= 15) else 3


def varga_sign_D3(lon_: float) -> int:
    si = lon_to_sign_idx(lon_)
    intra = lon_ - 30 * si
    return (si + int(intra // 10)) % 12


def varga_sign_D7(lon_: float) -> int:
    si = lon_to_sign_idx(lon_)
    intra = lon_ - 30 * si
    start = si if (si % 2 == 0) else (si + 6) % 12
    return (start + int(intra // (30 / 7))) % 12


def varga_sign_D9(lon_: float) -> int:
    return navamsa_for(lon_)[0]


def varga_sign_D12(lon_: float) -> int:
    si = lon_to_sign_idx(lon_)
    intra = lon_ - 30 * si
    return (si + int(intra // (30 / 12))) % 12


def varga_sign_D30(lon_: float) -> int:
    si = lon_to_sign_idx(lon_)
    intra = lon_ - 30 * si
    odd = (si % 2 == 0)
    if odd:
        lord = "Mars" if intra < 5 else ("Saturn" if intra < 10 else ("Jupiter" if intra < 18 else ("Mercury" if intra < 25 else "Venus")))
    else:
        lord = "Venus" if intra < 5 else ("Mercury" if intra < 12 else ("Jupiter" if intra < 20 else ("Saturn" if intra < 25 else "Mars")))
    lord_to_sign = {"Sun": 4, "Moon": 3, "Mars": 0, "Mercury": 2, "Jupiter": 8, "Venus": 1, "Saturn": 10}
    return lord_to_sign[lord]


def saptavargaja_bala(lon_: float, graha: str) -> float:
    v_funcs = [varga_sign_D1, varga_sign_D2, varga_sign_D3, varga_sign_D7, varga_sign_D9, varga_sign_D12, varga_sign_D30]
    total = 0.0
    for vf in v_funcs:
        vs = vf(lon_)
        lord = SIGN_LORD[vs]
        if graha in EXALT and SIGN_INDEX[EXALT[graha][0]] == vs:
            total += SV_WEIGHTS["own"] + 15.0
            continue
        if graha in DEBIL and SIGN_INDEX[DEBIL[graha][0]] == vs:
            total += SV_WEIGHTS["enemy"] / 2
            continue
        if in_moolatrikona(graha, vs * 30.0 + 1e-6):
            total += SV_WEIGHTS["moolatrikona"]
            continue
        total += SV_WEIGHTS["own"] if lord == graha else SV_WEIGHTS[relation_to_lord(graha, lord)]
    return min(total, 225.0)


def dig_bala(lon_: float, graha: str, asc_sid: float) -> float:
    if graha in {"Sun", "Mars"}:
        ref = norm360(asc_sid - 90.0)
    elif graha in {"Jupiter", "Mercury"}:
        ref = norm360(asc_sid + 180.0)
    elif graha in {"Venus", "Moon"}:
        ref = norm360(asc_sid + 90.0)
    else:
        ref = asc_sid
    delta = min(abs(norm360(lon_ - ref)), 360 - abs(norm360(lon_ - ref)))
    return max(0.0, delta / 3.0 if delta <= 180 else (360 - delta) / 3.0)


def nathonnatha_bala(graha: str, speed: float, local_dt: datetime) -> float:
    try:
        ghatis = ((local_dt.hour * 60 + local_dt.minute + local_dt.second / 60.0) / 60.0) * 2.5
        ghatis = max(0.0, min(30.0, ghatis))
        nata = 30.0 - ghatis
    except Exception:
        ghatis = 15.0
        nata = 15.0
    if graha == "Mercury":
        return 60.0
    if speed < 0:
        return 60.0
    natha_bala = max(0.0, min(60.0, 2.0 * nata))
    if graha in {"Moon", "Mars", "Saturn"}:
        return natha_bala
    if graha in {"Sun", "Jupiter", "Venus"}:
        return max(0.0, 60.0 - natha_bala)
    return natha_bala


def paksha_bala(graha: str, moon_lon: float, sun_lon: float) -> float:
    elong = norm360(moon_lon - sun_lon)
    diff = elong if elong <= 180 else 360 - elong
    virupa = diff / 3.0
    if graha in {"Jupiter", "Venus", "Mercury", "Moon"}:
        return virupa
    elif graha in {"Sun", "Mars", "Saturn"}:
        return max(0.0, 60.0 - virupa)
    else:
        return 30.0


def tribhaga_bala(graha: str, local_dt: datetime, sunrise_local: datetime, sunrise_prev_local: datetime, sunrise_next_local: datetime) -> float:
    try:
        if sunrise_local <= local_dt < sunrise_next_local:
            seg = (local_dt - sunrise_local).total_seconds() / (sunrise_next_local - sunrise_local).total_seconds()
            day = True
        else:
            seg = (local_dt - sunrise_prev_local).total_seconds() / (sunrise_local - sunrise_prev_local).total_seconds()
            day = False
    except Exception:
        return 0.0
    if graha == "Jupiter":
        return 60.0
    if day:
        if seg < 1 / 3:
            return 60.0 if graha == "Mercury" else 0.0
        if seg < 2 / 3:
            return 60.0 if graha == "Sun" else 0.0
        return 60.0 if graha == "Saturn" else 0.0
    else:
        if seg < 1 / 3:
            return 60.0 if graha == "Moon" else 0.0
        if seg < 2 / 3:
            return 60.0 if graha == "Venus" else 0.0
        return 60.0 if graha == "Mars" else 0.0


def abda_bala(graha: str, sunrise_local: datetime) -> float:
    varsha_lord = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"][sunrise_local.weekday()]
    return 15.0 if graha == varsha_lord else 0.0


def maasa_bala(graha: str, sun_lon: float) -> float:
    sun_sign = lon_to_sign_idx(sun_lon)
    lord = SIGN_LORD[sun_sign]
    return 30.0 if graha == lord else 0.0


def vara_bala(graha: str, sunrise_local: datetime) -> float:
    day_lord = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"][sunrise_local.weekday()]
    return 45.0 if graha == day_lord else 0.0


def hora_bala(graha: str, hora_lord: str) -> float:
    return 60.0 if graha == hora_lord else 0.0


KHANDA_RASI = {"movable": 45.0, "fixed": 33.0, "dual": 12.0}


def ayana_bala(graha: str, numeric_lons: dict[str, float], ayan: float) -> float:
    if graha == "Mercury":
        return 60.0
    try:
        lon_sid = numeric_lons[graha]
        lon_trop = norm360(lon_sid + ayan)
        lon_mod = lon_trop % 180.0
        bhuja = lon_mod if lon_mod <= 90.0 else 180.0 - lon_mod
        bhuja_rasi_idx = int(lon_trop // 30) % 12
        if bhuja_rasi_idx in {0, 3, 6, 9}:
            base = KHANDA_RASI["movable"]
            other = [KHANDA_RASI["fixed"], KHANDA_RASI["dual"]]
        elif bhuja_rasi_idx in {1, 4, 7, 10}:
            base = KHANDA_RASI["fixed"]
            other = [KHANDA_RASI["movable"], KHANDA_RASI["dual"]]
        else:
            base = KHANDA_RASI["dual"]
            other = [KHANDA_RASI["movable"], KHANDA_RASI["fixed"]]
        add_deg = (bhuja % 30.0) * max(other) / 30.0
        total = base + add_deg
        if graha in {"Moon", "Saturn"} and bhuja_rasi_idx in {6, 7, 8, 9, 10, 11}:
            total += 90.0
        if graha in {"Sun", "Mars", "Venus", "Jupiter"} and bhuja_rasi_idx in {0, 1, 2, 3, 4, 5}:
            total += 90.0
        return max(0.0, total / 3.0)
    except Exception:
        return 0.0


def yuddha_bala(graha: str, numeric_lons: dict[str, float]) -> float:
    contenders = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    my = numeric_lons[graha]
    sc = 0.0
    if graha in contenders:
        for o in contenders:
            if o == graha:
                continue
            if min(abs(my - numeric_lons[o]), 360 - abs(my - numeric_lons[o])) < 1.0:
                sc += 15.0
    return sc


def cheshta_bala(graha: str, jd_ut: float, FLAGS: int, numeric_lons: dict[str, float]) -> float:
    spd = swe.calc_ut(jd_ut, getattr(swe, graha.upper()), FLAGS)[0][3]
    try:
        spd_prev = swe.calc_ut(jd_ut - 1, getattr(swe, graha.upper()), FLAGS)[0][3]
    except Exception:
        spd_prev = spd
    if graha in {"Sun", "Moon"}:
        return paksha_bala(graha, numeric_lons["Moon"], numeric_lons["Sun"])
    if graha not in {"Mars", "Mercury", "Jupiter", "Venus", "Saturn"}:
        return 0.0
    mean_speeds = {"Mars": 0.524, "Mercury": 1.2, "Jupiter": 0.0831, "Venus": 1.2, "Saturn": 0.0335}
    mean = mean_speeds.get(graha, abs(spd) if abs(spd) > 0 else 1.0)
    ratio = abs(spd) / mean if mean else 0.0
    sun_lon = numeric_lons["Sun"]
    glon = numeric_lons[graha]
    seeghra = min(abs(norm360(glon - sun_lon)), 360 - abs(norm360(glon - sun_lon)))
    manda_kendra = abs(ratio - 1.0)
    if spd < 0:
        return 60.0
    if spd >= 0 and spd_prev < 0:
        return 30.0
    if ratio < 0.05:
        return 15.0
    is_inner = graha in {"Mercury", "Venus"}
    if not is_inner and 150 <= seeghra <= 210 and ratio >= 1.0:
        return 45.0
    if is_inner and seeghra <= 30 and ratio >= 1.0:
        return 45.0
    if ratio < 0.6 or manda_kendra > 0.5:
        return 30.0
    if ratio < 0.9:
        return 15.0
    if ratio < 1.1:
        return 7.5
    if ratio < 1.4:
        return 45.0
    return 30.0


def dignity_factor(planet: str, lon_planet: float) -> float:
    if planet in EXALT and lon_to_sign_idx(lon_planet) == SIGN_INDEX[EXALT[planet][0]]:
        return 1.15
    if planet in DEBIL and lon_to_sign_idx(lon_planet) == SIGN_INDEX[DEBIL[planet][0]]:
        return 0.85
    lord = SIGN_LORD[lon_to_sign_idx(lon_planet)]
    rel = relation_to_lord(planet, lord)
    if rel == "moolatrikona" or in_moolatrikona(planet, lon_planet):
        return 1.1
    if rel == "great_friend":
        return 1.08
    if rel == "friend":
        return 1.05
    if rel in {"neutral", "enemy", "great_enemy"}:
        return 1.0
    return 1.0


def drig_bala(graha: str, lon_: float, all_lons: dict[str, float]) -> float:
    aspect_map = {"Jupiter": [120, 180, 240], "Mars": [90, 180, 270], "Saturn": [60, 180, 300]}
    pinda_base = {"Sun": 30.0, "Moon": 60.0, "Mars": 45.0, "Mercury": 60.0, "Jupiter": 60.0, "Venus": 60.0, "Saturn": 45.0}
    total = 0.0
    for other, olon in all_lons.items():
        if other not in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"] or other == graha:
            continue
        angles = aspect_map.get(other, [180])
        s = max(0.0, max(1.0 - min(abs(norm360(lon_ - olon - a)), 360 - abs(norm360(lon_ - olon - a))) / 12.0 for a in angles))
        if s <= 0:
            continue
        pinda = pinda_base.get(other, 60.0) * s * dignity_factor(other, olon)
        if other in BENEFICS:
            total += pinda / 4.0
        if other in MALEFICS:
            total -= pinda / 4.0
        if other in {"Jupiter", "Mercury"}:
            total += pinda
    return max(-240.0, min(240.0, total))


def war_victor(p1: str, p2: str, jd_ut: float, FLAGS: int, base_totals: dict[str, float]) -> str:
    try:
        mag1 = swe.pheno_ut(jd_ut, getattr(swe, p1.upper()))[3]
        mag2 = swe.pheno_ut(jd_ut, getattr(swe, p2.upper()))[3]
        if mag1 < mag2:
            return p1
        if mag2 < mag1:
            return p2
    except Exception:
        pass
    return p1 if base_totals.get(p1, 0) >= base_totals.get(p2, 0) else p2


def compute_shadbala(
    local_dt: datetime,
    sunrise_local: datetime,
    sunrise_prev_local: datetime,
    sunrise_next_local: datetime,
    jd_ut: float,
    FLAGS: int,
    numeric_lons: dict[str, float],
    ayan: float,
    starts: list[float],
    ends: list[float],
    hora_lord: str,
    asc_sid: float
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, float]]:
    sb_rows = []
    sb_sthana = []
    sb_kala = []
    base_totals = {}

    for g in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        glon = numeric_lons[g]
        uc = float(uccha_bala(glon, g))
        sv = float(saptavargaja_bala(glon, g))
        oy = float(oja_yugma_bala(glon, g))
        ken = float(kendradi_bala(glon, starts, ends))
        dre = float(drekkana_bala(glon, g))
        sth = uc + sv + oy + ken + dre
        sb_sthana.append({
            "Planet": g,
            "Uccha": round(uc, 2),
            "Saptavargaja": round(sv, 2),
            "Oja/Yugma": round(oy, 2),
            "Kendradi": round(ken, 2),
            "Drekkana": round(dre, 2),
            "Total (Virupa)": round(sth, 2),
            "Total (Rupa)": round(sth / 60.0, 3)
        })

        nai = float(NAISARGIKA[g])
        dig = float(dig_bala(glon, g, asc_sid))
        natha = float(nathonnatha_bala(g, swe.calc_ut(jd_ut, getattr(swe, g.upper()), FLAGS)[0][3], local_dt))
        pak = float(paksha_bala(g, numeric_lons["Moon"], numeric_lons["Sun"]))
        tri = float(tribhaga_bala(g, local_dt, sunrise_local, sunrise_prev_local, sunrise_next_local))
        abd = float(abda_bala(g, sunrise_local))
        maa = float(maasa_bala(g, numeric_lons["Sun"]))
        var = float(vara_bala(g, sunrise_local))
        hor = float(hora_bala(g, hora_lord))
        aya = float(ayana_bala(g, numeric_lons, ayan))
        yud = float(yuddha_bala(g, numeric_lons))
        kal = natha + pak + tri + abd + maa + var + hor + aya + yud
        sb_kala.append({
            "Planet": g,
            "Nathonnatha/Cheshta": round(natha, 2),
            "Paksha": round(pak, 2),
            "Tribhaga": round(tri, 2),
            "Abda": round(abd, 2),
            "Maasa": round(maa, 2),
            "Vara": round(var, 2),
            "Hora": round(hor, 2),
            "Ayana": round(aya, 2),
            "Yuddha": round(yud, 2),
            "Total (Virupa)": round(kal, 2),
            "Total (Rupa)": round(kal / 60.0, 3)
        })

        che = float(cheshta_bala(g, jd_ut, FLAGS, numeric_lons))
        dri = float(drig_bala(g, glon, numeric_lons))
        total_v = sth + dig + kal + che + nai + dri
        base_totals[g] = total_v
        total_r = total_v / 60.0
        total_pct = max(0.0, min(100.0, (total_r / MAX_SHADBALA_RUPA.get(g, total_r)) * 100.0 if g in MAX_SHADBALA_RUPA else (total_r / 6.0) * 100.0))
        sb_rows.append({
            "Planet": g,
            "Sthana": round(sth, 2),
            "Dig": round(dig, 2),
            "Kala": round(kal, 2),
            "Cheshta": round(che, 2),
            "Naisargika": round(nai, 2),
            "Drig": round(dri, 2),
            "Total (Virupa)": round(total_v, 2),
            "Total (Rupa)": round(total_r, 3),
            "Total (%)": round(total_pct, 1),
            "Min Req (Rupa)": MIN_SHADBALA_RUPA[g],
            "Meets Min?": "Yes" if total_r >= MIN_SHADBALA_RUPA[g] else "No"
        })

    contenders = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    war_adjust = {g: 0.0 for g in contenders}
    for i, p1 in enumerate(contenders):
        for p2 in contenders[i + 1:]:
            dist = min(abs(numeric_lons[p1] - numeric_lons[p2]), 360 - abs(numeric_lons[p1] - numeric_lons[p2]))
            if dist < 1.0:
                victor = war_victor(p1, p2, jd_ut, FLAGS, base_totals)
                loser = p2 if victor == p1 else p1
                diff = abs(base_totals.get(p1, 0) - base_totals.get(p2, 0))
                war_adjust[victor] += diff
                war_adjust[loser] -= diff

    if any(abs(v) > 0 for v in war_adjust.values()):
        for row in sb_rows:
            p = row["Planet"]
            if p in war_adjust:
                row["Total (Virupa)"] = round(row["Total (Virupa)"] + war_adjust[p], 2)
                row["Total (Rupa)"] = round(row["Total (Virupa)"] / 60.0, 3)
                row["Meets Min?"] = "Yes" if row["Total (Rupa)"] >= MIN_SHADBALA_RUPA[p] else "No"

    shadbala_df = pd.DataFrame(sb_rows)
    ranks = shadbala_df.set_index("Planet")["Total (Rupa)"].rank(method="dense", ascending=False).astype(int).to_dict()
    NATURAL_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    shadbala_df = shadbala_df.set_index("Planet").loc[NATURAL_ORDER].reset_index()
    shadbala_df["Rank"] = shadbala_df["Planet"].map(ranks)

    planet_total_rupa = {r["Planet"]: r["Total (Rupa)"] for r in sb_rows}

    return shadbala_df, pd.DataFrame(sb_sthana), pd.DataFrame(sb_kala), planet_total_rupa


def bhava_ref(cusp_lon: float, asc_sid: float) -> float:
    desc = norm360(asc_sid + 180.0)
    nadir = norm360(asc_sid - 90.0)
    midh = norm360(asc_sid + 90.0)
    si = lon_to_sign_idx(cusp_lon)
    intra = cusp_lon - si * 30.0
    if si in {2, 5, 6, 10} or (si == 8 and intra < 15.0):
        return desc
    if si in {0, 1, 4} or (si == 9 and intra < 15.0) or (si == 8 and intra >= 15.0):
        return nadir
    if si in {3, 7}:
        return asc_sid
    if (si == 9 and intra >= 15.0) or si == 11:
        return midh
    return asc_sid


def compute_bhava_bala(
    local_dt: datetime,
    sunrise_local: datetime,
    sunset_local: datetime,
    cusps_sid: list[float],
    numeric_lons: dict[str, float],
    starts: list[float],
    ends: list[float],
    house_occ: dict[int, list[str]],
    planet_total_rupa: dict[str, float],
    asc_sid: float
) -> pd.DataFrame:
    sb_bhava = []
    BENEFICS_SET = {"Jupiter", "Venus", "Mercury", "Moon"}
    MALEFICS_SET = {"Saturn", "Mars", "Sun"}

    for i in range(12):
        cusp_sign_idx = lon_to_sign_idx(cusps_sid[i])
        ref = bhava_ref(cusps_sid[i], asc_sid)
        diff = abs(norm360(cusps_sid[i] - ref))
        diff = 360 - diff if diff > 180 else diff
        virupa = diff / 3.0
        for p, lonp in numeric_lons.items():
            if p not in {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}:
                continue
            s = aspect_score(lonp, cusps_sid[i], p, orb=12.0)
            if s <= 0:
                continue
            pinda = 60.0 * s
            if p in BENEFICS_SET:
                virupa += pinda / 4.0
            if p in MALEFICS_SET:
                virupa -= pinda / 4.0
            if p in {"Jupiter", "Mercury"}:
                virupa += pinda
        lord = SIGN_LORD[cusp_sign_idx]
        virupa += planet_total_rupa.get(lord, 0.0) * 60.0 * 0.25
        occs = house_occ[i + 1]
        if any(o in occs for o in ["Jupiter", "Mercury"]):
            virupa += 60.0
        if any(o in occs for o in ["Saturn", "Mars", "Sun"]):
            virupa -= 60.0
        is_day = False
        try:
            is_day = sunrise_local <= local_dt < sunset_local
        except Exception:
            pass
        seershodaya = cusp_sign_idx in {2, 4, 5, 6, 10}
        prishtodaya = cusp_sign_idx in {0, 1, 3, 7, 9}
        if is_day and seershodaya:
            virupa += 15.0
        elif (not is_day) and prishtodaya:
            virupa += 15.0
        virupa = max(0.0, virupa)
        bhava_rupa = virupa / 60.0
        sb_bhava.append({
            "Bhava": i + 1,
            "Cusp": sign_dms_str(cusps_sid[i]),
            "Bhava Bala (Rupa)": round(bhava_rupa, 3),
            "Strength (%)": round(bhava_rupa * 100.0, 1),
            "Lord": lord,
            "Lord Shadbala (Rupa)": round(planet_total_rupa.get(lord, 0.0), 3),
            "Occupants": ", ".join(occs)
        })

    if sb_bhava:
        ranks_bh = {row["Bhava"]: rank for rank, row in enumerate(sorted(sb_bhava, key=lambda r: r["Bhava Bala (Rupa)"], reverse=True), start=1)}
        for row in sb_bhava:
            row["Rank"] = ranks_bh[row["Bhava"]]

    return pd.DataFrame(sb_bhava)


def rasmi_from_kendra(angle_deg: float) -> float:
    ang = norm360(angle_deg)
    ang = 360.0 - ang if ang > 180 else ang
    signs = int(ang // 30.0)
    deg = ang - signs * 30.0
    signs += 1
    deg *= 2.0
    signs += int(deg // 30.0)
    deg = deg % 30.0
    return signs + deg / 30.0


def uchcha_rasmi_val(planet: str, lon: float) -> float:
    if planet not in DEBIL:
        return 0.0
    deb_sign, deb_deg = DEBIL[planet]
    deb_lon = lon_deg(deb_sign, deb_deg)
    return rasmi_from_kendra(lon - deb_lon)


def chesta_rasmi_val(planet: str, lon: float, sun_lon: float) -> float:
    if planet == "Sun":
        return 90.0
    return rasmi_from_kendra(lon - sun_lon)


def compute_ishta_kashta(numeric_lons: dict[str, float]) -> pd.DataFrame:
    ishta_rows = []
    NATURAL_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for g in NATURAL_ORDER:
        u_rasmi = uchcha_rasmi_val(g, numeric_lons[g])
        c_rasmi = chesta_rasmi_val(g, numeric_lons[g], numeric_lons["Sun"])
        subha = max(0.0, min(8.0, (u_rasmi + c_rasmi) / 2.0))
        asubha = max(0.0, 8.0 - subha)
        ishta = max(0.0, min(60.0, ((u_rasmi - 1.0) * 10.0 + (c_rasmi - 1.0) * 10.0) / 2.0))
        kashta = max(0.0, 60.0 - ishta)
        ishta_rows.append({
            "Planet": g,
            "Uchcha Rasmi": round(u_rasmi, 3),
            "Cheshta Rasmi": round(c_rasmi, 3),
            "Subha Rasmi": round(subha, 3),
            "Asubha Rasmi": round(asubha, 3),
            "Ishta Phala": round(ishta, 2),
            "Kashta Phala": round(kashta, 2)
        })
    return pd.DataFrame(ishta_rows)
