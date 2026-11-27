"""compare: part of compatibility (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Dict, Tuple, Optional, Any
from ..utils import norm360
from ..natal_chart import NAKSHATRA_NAMES, RASI_LORDS, EXALTATION, DEBILITATION, get_graha_dignity
from ..aspects_friendships import get_natural_relationship
from .tables import _ordinal
from .matching import evaluate_horoscope_matching
from .kuja import evaluate_kuja_dosha
from .pada_points import pada_match_level, pada_match_points

def _house(sign: int, from_sign: int) -> int:
    return (sign - from_sign) % 12 + 1


def _sign(lon: float) -> int:
    return int(norm360(lon) // 30.0)


_BODIES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
_SEVEN = _BODIES[:7]
_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
# the twelve bhavas and what each says about the marriage (BPHS 11, each bhava's significations); 2, 4, 5, 7, 8 and 12 the marriage bhavas
_BHAVAS = {1: "self", 2: "family", 3: "courage", 4: "home", 5: "children", 6: "disputes", 7: "spouse", 8: "longevity",
           9: "fortune", 10: "career", 11: "gains", 12: "bed comforts"}
_MARRIAGE_HOUSES = {h: _BHAVAS[h] for h in (2, 4, 5, 7, 8, 12)}
_BHAVA_NEED = 7.0     # rupas a bhava's strength is measured against
_SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def _apart(a: int, b: int) -> str:
    """How two signs sit from each other, as the pair of house counts: "1/7", "6/8", "2/12"..."""
    h = _house(b, a)
    o = _house(a, b)
    return "%d/%d" % (min(h, o), max(h, o))


def _place_class(h: int) -> str:
    return "dusthana" if h in (6, 8, 12) else "kendra/trikona" if h in (1, 4, 5, 7, 9, 10) else "neutral"


def _sign_dignity(p: str, sign: int) -> str:
    """Dignity by sign alone (for a varga, where the degrees inside the sign mean nothing)."""
    if p in EXALTATION and EXALTATION[p][0] == sign:
        return "Exalted"
    if p in DEBILITATION and DEBILITATION[p][0] == sign:
        return "Debilitated"
    return "Own Sign" if RASI_LORDS[sign] == p else ""


def _who(items: Dict[str, Any]) -> str:
    return ", ".join(items) or "none"


def compare_charts(bride: Dict[str, Any], groom: Dict[str, Any],
                   bride_strength: Optional[Dict[str, Any]] = None, groom_strength: Optional[Dict[str, Any]] = None,
                   bride_mars: Optional[Dict[str, int]] = None, groom_mars: Optional[Dict[str, int]] = None,
                   aspect_parasara: bool = True) -> Dict[str, Any]:
    """Similarities and differences between two charts for marriage matching, by area: rasi (D-1), navamsa (D-9),
    the twelve bhavas, and graha strength (shadbala, when the caller passes each chart's chart_shadbala).
    ``bride_mars`` / ``groom_mars``: Mars's bhava from Lagna, Moon and Venus by the cusps, for Kuja dosha (else by sign);
    ``aspect_parasara`` the curves for Jupiter's aspect on Mars there.

    The rules, one per line of the area's key points ("same" = alike or agreeable, "diff" = differ or hard):
    - lagnas, D-9 lagnas: hard 6/8 or 2/12 from each other; Moon signs: hard 6/8, 2/12 or 5/9 (Bhakoota)
    - each graha (D-1 and D-9): alike in the same bhava from its own lagna; the same sign is noted as alike
    - lagna lords: alike unless either is the other's natural enemy; 3/11 apart, noted as agreeable
    - one's Lagna, Moon or Venus in the other's 7th: agreeable; none: differ
    - spouse karakas (boy's Venus, girl's Jupiter): agreeable when neither is in a dusthana (D-1) or debilitated (D-9)
    - Kuja dosha: alike when both or neither have it uncancelled
    - D-9 lagna lord and 7th lord, each bhava's lord: alike when both sit in the same kind of bhava
      (kendra/trikona, dusthana, neither); a bhava's occupants: alike when both hold grahas or both are empty,
      and both have a malefic or neither; its Bhava Bala: alike when both reach 7 rupas or neither does
    - shadbala: alike when both reach the graha's required rupas or neither does; dignity: alike when the same"""
    from ..varga_charts import d9

    b_lons = bride["planet_longitudes"]
    g_lons = groom["planet_longitudes"]
    b_lag = bride["lagna_lon"]
    g_lag = groom["lagna_lon"]
    b_ls, g_ls = _sign(b_lag), _sign(g_lag)
    bodies = [p for p in _BODIES if p in b_lons and p in g_lons]
    areas = {k: {"same": [], "diff": []} for k in ("rasi", "navamsa", "houses", "strength")}
    notes = []

    def relation(area: str, what: str, a: int, b: int, hard: Tuple[str, ...]):
        pair = _apart(a, b)
        text = f"{what}: {_SIGN_NAMES[a]} / {_SIGN_NAMES[b]}, {pair} from each other"
        areas[area]["diff" if pair in hard else "same"].append(text + (" (hard)" if pair in hard else ""))

    # --- Rasi (D-1)
    rasi = areas["rasi"]
    relation("rasi", "Lagnas", b_ls, g_ls, ("6/8", "2/12"))
    relation("rasi", "Moon signs", _sign(b_lons["Moon"]), _sign(g_lons["Moon"]), ("6/8", "2/12", "5/9"))   # 5/9 Moons: Bhakoota dosha
    for p in bodies:
        bh, gh = _house(_sign(b_lons[p]), b_ls), _house(_sign(g_lons[p]), g_ls)
        line = f"Both {p} in the {_ordinal(bh)} bhava" if bh == gh else f"{p}: girl {_ordinal(bh)} / boy {_ordinal(gh)} bhava"
        rasi["same" if bh == gh else "diff"].append(line)
        if _sign(b_lons[p]) == _sign(g_lons[p]) and p != "Moon":
            rasi["same"].append(f"Both {p} in {_SIGN_NAMES[_sign(b_lons[p])]}")
    b_ll, g_ll = RASI_LORDS[b_ls], RASI_LORDS[g_ls]
    if b_ll == g_ll:
        rasi["same"].append(f"Same lagna lord ({b_ll})")
    else:
        r1, r2 = get_natural_relationship(b_ll, g_ll), get_natural_relationship(g_ll, b_ll)
        line = f"Lagna lords {b_ll} (girl) and {g_ll} (boy): {r1.lower()} / {r2.lower()}"
        rasi["same" if "Enemy" not in (r1, r2) else "diff"].append(line)
        if b_ll in b_lons and g_ll in g_lons:   # the lagna lords 3-11 from each other, by their signs
            if _apart(_sign(b_lons[b_ll]), _sign(g_lons[g_ll])) == "3/11":
                rasi["same"].append("Lagna lords sit 3/11 from each other")
    # one's lagna, Moon or Venus in the other's 7th house
    overlay = []
    for who, other, lons, lag, o_ls in (("Girl", "boy", b_lons, b_lag, g_ls), ("Boy", "girl", g_lons, g_lag, b_ls)):
        for name, lon in (("Lagna", lag), ("Moon", lons["Moon"]), ("Venus", lons.get("Venus"))):
            if lon is not None and _house(_sign(lon), o_ls) == 7:
                overlay.append(f"{who}'s {name} falls in the {other}'s 7th bhava")
    rasi["same"].extend(overlay)
    if not overlay:
        rasi["diff"].append("Neither's Lagna, Moon or Venus falls in the other's 7th bhava")
    # the spouse karakas: the boy's Venus, the girl's Jupiter
    kv, kj = _house(_sign(g_lons["Venus"]), g_ls), _house(_sign(b_lons["Jupiter"]), b_ls)
    cv, cj = _place_class(kv), _place_class(kj)
    line = f"Spouse karakas: boy's Venus in {_ordinal(kv)} ({cv}), girl's Jupiter in {_ordinal(kj)} ({cj})"
    rasi["diff" if "dusthana" in (cv, cj) else "same"].append(line)
    # Mangala (Kuja) dosha from Lagna, Moon, Venus
    b_kuja = evaluate_kuja_dosha(b_lons, b_lag, bride_mars, aspect_parasara)
    g_kuja = evaluate_kuja_dosha(g_lons, g_lag, groom_mars, aspect_parasara)

    def mars(k):
        """"Mars 7th bhava from Venus, 8th from Lagna", "none", or that with "(cancelled)" """
        r = [f"{_ordinal(k['houses'][x])} bhava from {x}" if i == 0 else f"{_ordinal(k['houses'][x])} from {x}"
             for i, x in enumerate(x for x in ("Venus", "Moon", "Lagna") if f"{x} (Bhava {k['houses'][x]})" in k["affliction_sources"])]
        return ("Mars " + ", ".join(r) + (" (cancelled)" if k["is_cancelled"] else "")) if r else "none"
    b_act, g_act = (k["has_kuja_dosha"] and not k["is_cancelled"] for k in (b_kuja, g_kuja))
    if b_act and g_act:
        rasi["same"].append(f"Mangala dosha in both: girl {mars(b_kuja)} / boy {mars(g_kuja)}")
    elif b_act or g_act:
        rasi["diff"].append(f"Mangala dosha in one: girl {mars(b_kuja)} / boy {mars(g_kuja)}")
    elif b_kuja["has_kuja_dosha"] or g_kuja["has_kuja_dosha"]:
        rasi["same"].append(f"No Mangala dosha left in either: girl {mars(b_kuja)} / boy {mars(g_kuja)}")
    else:
        rasi["same"].append("Neither has Mangala dosha")
    notes.append({"kind": "kuja", "bride": b_kuja, "groom": g_kuja})
    notes.append({"kind": "moon_separation", "houses": _house(_sign(g_lons["Moon"]), _sign(b_lons["Moon"]))})

    # --- Navamsa (D-9)
    nav = areas["navamsa"]
    b_d9, g_d9 = d9(b_lag), d9(g_lag)
    relation("navamsa", "Navamsa lagnas", b_d9, g_d9, ("6/8", "2/12"))
    for p in bodies:
        bh, gh = _house(d9(b_lons[p]), b_d9), _house(d9(g_lons[p]), g_d9)
        line = f"Both {p} in the {_ordinal(bh)} bhava" if bh == gh else f"{p}: girl {_ordinal(bh)} / boy {_ordinal(gh)} bhava"
        nav["same" if bh == gh else "diff"].append(line)
    for what, lord_house in (("lagna lord", 1), ("7th lord", 7)):
        bl, gl = RASI_LORDS[(b_d9 + lord_house - 1) % 12], RASI_LORDS[(g_d9 + lord_house - 1) % 12]
        bh, gh = _house(d9(b_lons[bl]), b_d9), _house(d9(g_lons[gl]), g_d9)
        bc, gc = _place_class(bh), _place_class(gh)
        line = f"D-9 {what}: girl {bl} in {_ordinal(bh)}, boy {gl} in {_ordinal(gh)}"
        nav["same" if bc == gc else "diff"].append(line + (f" (both {bc})" if bc == gc else f" ({bc} / {gc})"))
    bv = [p for p in bodies if d9(b_lons[p]) == _sign(b_lons[p])]
    gv = [p for p in bodies if d9(g_lons[p]) == _sign(g_lons[p])]
    if set(bv) & set(gv):
        nav["same"].append("Both vargottama: " + ", ".join(p for p in bv if p in gv))
    if set(bv) ^ set(gv):
        nav["diff"].append("Vargottama only in one: girl %s / boy %s" % (_who([p for p in bv if p not in gv]), _who([p for p in gv if p not in bv])))
    dv, dj = _sign_dignity("Venus", d9(g_lons["Venus"])), _sign_dignity("Jupiter", d9(b_lons["Jupiter"]))
    line = f"Spouse karakas: boy's Venus {dv.lower() or 'in an ordinary sign'}, girl's Jupiter {dj.lower() or 'in an ordinary sign'}"
    nav["diff" if "Debilitated" in (dv, dj) else "same"].append(line)

    # --- The twelve bhavas (from each lagna)
    hs = areas["houses"]
    rank = lambda st, h: 1 + sorted((x["rupas"] for x in st["bhavas"]), reverse=True).index(st["bhavas"][h - 1]["rupas"])  # noqa: E731
    for h, about in _BHAVAS.items():
        tag = f"{_ordinal(h)} ({about})"
        bl, gl = RASI_LORDS[(b_ls + h - 1) % 12], RASI_LORDS[(g_ls + h - 1) % 12]
        bh, gh = _house(_sign(b_lons[bl]), b_ls), _house(_sign(g_lons[gl]), g_ls)
        bc, gc = _place_class(bh), _place_class(gh)
        line = f"{tag} lord: girl {bl} in {_ordinal(bh)}, boy {gl} in {_ordinal(gh)}"
        hs["same" if bc == gc else "diff"].append(line + (f" (both {bc})" if bc == gc else f" ({bc} / {gc})"))
        bo = [p for p in bodies if _house(_sign(b_lons[p]), b_ls) == h]
        go = [p for p in bodies if _house(_sign(g_lons[p]), g_ls) == h]
        if bo or go:
            bm, gm = any(p in _MALEFICS for p in bo), any(p in _MALEFICS for p in go)
            hs["same" if bm == gm and bool(bo) == bool(go) else "diff"].append(f"{tag} holds: girl {_who(bo)} / boy {_who(go)}")
        if bride_strength and groom_strength:      # Bhava Bala against its 7 rupas
            br_, gr_ = (st_["bhavas"][h - 1]["rupas"] for st_ in (bride_strength, groom_strength))
            strong = lambda r: "strong" if r >= _BHAVA_NEED else "weak"  # noqa: E731
            both = strong(br_) == strong(gr_)
            hs["same" if both else "diff"].append(
                f"{tag} bala: girl {br_ / _BHAVA_NEED:.0%}, boy {gr_ / _BHAVA_NEED:.0%} of 7 rupas" + (f" (both {strong(br_)})" if both else ""))

    # --- Graha strength: shadbala against its required rupas, and dignity in the rasi and navamsa
    st = areas["strength"]
    if bride_strength and groom_strength:
        from ..shadbala import _REQUIRED_RUPAS
        for i, p in enumerate(_SEVEN):
            br_, gr_ = bride_strength["planets"][p]["rupas"], groom_strength["planets"][p]["rupas"]
            bs, gs = br_ >= _REQUIRED_RUPAS[i], gr_ >= _REQUIRED_RUPAS[i]
            nums = f"{br_:.1f} / {gr_:.1f} rupas, needs {_REQUIRED_RUPAS[i]:g}"
            if bs == gs:
                st["same"].append(f"{p} {'strong' if bs else 'weak'} in both ({nums})")
            else:
                st["diff"].append(f"{p}: girl {'strong' if bs else 'weak'}, boy {'strong' if gs else 'weak'} ({nums})")
    for p in bodies:
        for chart, b_dig, g_dig in (("rasi", get_graha_dignity(p, b_lons[p]), get_graha_dignity(p, g_lons[p])),
                                    ("navamsa", _sign_dignity(p, d9(b_lons[p])), _sign_dignity(p, d9(g_lons[p])))):
            b_dig, g_dig = ("" if d in ("General Sign", "Neutral") else d for d in (b_dig, g_dig))
            if not (b_dig or g_dig):
                continue
            if b_dig == g_dig:
                st["same"].append(f"{p} {b_dig.lower()} in both {chart} charts")
            else:
                st["diff"].append(f"{p} in {chart}: girl {b_dig.lower() or 'ordinary'} / boy {g_dig.lower() or 'ordinary'}")

    from ..shadbala import _REQUIRED_RUPAS
    from ..laghu_parasari import evaluate_functional_nature_for_lagna

    def side(lons, lag, sb):
        """One chart's places for the grids: each graha's sign and house in the rasi and navamsa, its dignity, rupas and
        functional nature as a lord (from the lagna and from the navamsa lagna); the twelve bhavas."""
        ls, l9 = _sign(lag), d9(lag)
        fn, fn9 = evaluate_functional_nature_for_lagna(ls), evaluate_functional_nature_for_lagna(l9)
        plain = lambda d: "" if d in ("General Sign", "Neutral") else d  # noqa: E731
        planets = {p: {"lon": round(norm360(lons[p]), 4), "sign": _sign(lons[p]), "house": _house(_sign(lons[p]), ls), "d9_sign": d9(lons[p]), "d9_house": _house(d9(lons[p]), l9),
                       "dignity": plain(get_graha_dignity(p, lons[p])), "d9_dignity": _sign_dignity(p, d9(lons[p])),
                       "rupas": sb["planets"][p]["rupas"] if sb and p in _SEVEN else None,
                       "nature": fn[p]["classification"] if p in fn else None, "d9_nature": fn9[p]["classification"] if p in fn9 else None} for p in bodies}
        houses = [{"house": h, "lord": RASI_LORDS[(ls + h - 1) % 12], "lord_house": _house(_sign(lons[RASI_LORDS[(ls + h - 1) % 12]]), ls),
                   "holds": [p for p in bodies if planets[p]["house"] == h], "rank": rank(sb, h) if sb else None,
                   "rupas": round(sb["bhavas"][h - 1]["rupas"], 2) if sb else None} for h in _BHAVAS]
        return {"lagna": ls, "lagna_lon": round(norm360(lag), 4), "d9_lagna": l9, "planets": planets, "houses": houses}
    grid = {"bodies": bodies, "girl": {**side(b_lons, b_lag, bride_strength), "kuja": b_kuja}, "boy": {**side(g_lons, g_lag, groom_strength), "kuja": g_kuja},
            "need": dict(zip(_SEVEN, _REQUIRED_RUPAS)), "about": list(_BHAVAS.values())}
    for a in areas.values():     # every line, so the area card's "n alike · m differ" is what the key points list
        a["key"] = [{"text": t, "same": same} for same, lst in ((True, a["same"]), (False, a["diff"])) for t in lst]
        a["key"].sort(key=lambda x: "Mangala dosha" not in x["text"])     # Mangala (Kuja) dosha leads the key points

    match = evaluate_horoscope_matching(
        {"moon_longitude": b_lons["Moon"], "lagna_longitude": b_lag, "planet_longitudes": b_lons, "mars_bhavas": bride_mars, "aspect_parasara": aspect_parasara,
         "name": bride.get("name", "Bride")},
        {"moon_longitude": g_lons["Moon"], "lagna_longitude": g_lag, "planet_longitudes": g_lons, "mars_bhavas": groom_mars, "aspect_parasara": aspect_parasara,
         "name": groom.get("name", "Groom")},
    )
    bn = int(norm360(b_lons["Moon"]) // (360.0 / 27.0))
    bp = int(norm360(b_lons["Moon"]) // (10.0 / 3.0)) % 4
    gn = int(norm360(g_lons["Moon"]) // (360.0 / 27.0))
    gp = int(norm360(g_lons["Moon"]) // (10.0 / 3.0)) % 4
    match["pada_score"] = pada_match_points(bn, bp, gn, gp)
    match["pada_level"] = pada_match_level(match["pada_score"])
    match["bride_nak"] = bn
    match["bride_pada"] = bp
    match["groom_nak"] = gn
    match["groom_pada"] = gp

    return {
        "match": match,
        "areas": areas,
        "grid": grid,
        "similarities": [x for a in areas.values() for x in a["same"]],
        "differences": [x for a in areas.values() for x in a["diff"]],
        "notes": notes,
        "bride_moon": {"nakshatra": bn, "pada": bp + 1, "name": NAKSHATRA_NAMES[bn]},
        "groom_moon": {"nakshatra": gn, "pada": gp + 1, "name": NAKSHATRA_NAMES[gn]},
    }
