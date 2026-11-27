"""The windows off the main tree: Aspect Table, Horoscope Matching, Vimsottari seed comparison, Dasa-Transit
Correlation, and the dasa commands that answer with a period or a message."""
from core_logic import compatibility as C, dashas as DS, ephemeris as E, dasa_systems as J, varga_charts as V, natal_chart as N, shadbala as SB, sign_strength as SS, workflows as W

from . import basics as B, dasas as D, settings as S
from .charts import CLASS_NAMES, _nine
from .houses import ORDINAL, _bhavas

LEVEL_ABBR = ("MD", "AD", "PD", "SD", "PAD", "DAD")
REFS = ["Lagna"] + B.PLANETS
NAK = 360.0 / 27.0


def aspect_table(b, ch, cfg, s, d, ref):
    """The Aspect Table (BPHS 26): the aspect of each of Sun .. Ketu on the others and on the 12 houses, in chart D-``d``. Virupas are cut to a whole number;
    a planet's name is coloured by its relation to the lord of its sign, a house's number by its relation to that house's lord."""
    opt = S.varga_options(s)
    lons = [V.varga_longitude(x, d, opt) for x in _nine(ch)]
    signs = [V.varga_sign(x, d, opt) for x in _nine(ch)]
    compound = SB.compound_relationships(signs[1:])
    retro = [False] + [bool(ch["retrograde"].get(p)) for p in B.PLANETS]
    if ref == 0 and d == 1:
        houses = [x[1 if s.house_cusp_in_middle else 0] for x in _bhavas(b, ch, cfg, s)]
    else:
        step = -30.0 if s.bhava_nodes_reversed and ref in (8, 9) else 30.0
        houses = [(lons[ref] + i * step) % 360.0 for i in range(12)]
    natures = E.chart_shadbala(b, ch, cfg)["natures"]     # the Grahas tab's natural benefics (insights: n.b7): Mo by paksha, Me by its company; the nodes malefic
    scale = s.aspect_full / 100.0
    value = lambda target, p: int(SB.aspect_value(target - lons[p], p, s.aspect_parasara) * scale)  # noqa: E731
    rows = []
    for p in range(1, 10):
        if p <= 7:     # BPHS's degrees: a moolatrikona sign is moolatrikona, exalted or own by the degree, never two (natal_chart.get_graha_dignity)
            marks = {"Exalted": ["exalted"], "Debilitated": ["debilitated"], "Moolatrikona": ["moolatrikona"]}.get(N.get_graha_dignity(B.PLANETS[p - 1], lons[p]), [])
        else:          # the nodes have no degrees in BPHS: by sign
            marks = [m for m, table in (("exalted", SS.EXALTATION), ("debilitated", SS.DEBILITATION), ("moolatrikona", SS.MOOLATRIKONA)) if table[p] == signs[p]]
        rel = compound[p - 1][SS.SIGN_LORDS[signs[p]] - 1]
        rows.append({"body": B.PLANET_ABBR[p - 1], "marks": marks, "relation": CLASS_NAMES[rel], "benefic": p <= 7 and natures[p - 1] > 0, "retro": bool(retro[p]),     # the nodes too, as in the charts: by their motion
                     "combust": N.is_combust(p, lons, retro, s.combustion_by_motion, s.combustion_classical),
                     "cells": [None if q == p or {p, q} == {8, 9} else value(lons[q], p) for q in range(1, 10)],     # nothing on itself, and Rahu and Ketu none on each other
                     "houses": [value(x, p) for x in houses],
                     "lord_class": [compound[p - 1][SS.SIGN_LORDS[int(x % 360.0 // 30)] - 1] for x in houses]})
    return {"title": "Rasi" if d == 1 else "D-%d" % d, "full": s.aspect_full, "reference": REFS[ref], "bodies": B.PLANET_ABBR, "houses": ORDINAL, "rows": rows, "names": CLASS_NAMES}


def matching(ch, bride, nak, pada):
    """View > Horoscope Matching Score: the native's Moon against a partner's nakshatra and pada, and the score against every pada beside it."""
    moon = ch["planet_longitudes"]["Moon"]
    me = int(moon / NAK), int(moon / (10.0 / 3.0)) % 4

    def score(n, p):        # the table's row is the bride's part
        return C.pada_match_points(*me, n, p, swap=True) if bride else C.pada_match_points(n, p, *me, swap=True)
    stars = B._tables()[0]["nakshatras"]
    rows = [{"nakshatra": stars[n], "pada": p + 1, "score": score(n, p), "level": C.pada_match_level(score(n, p))} for n in range(27) for p in range(4)]
    pick = rows[nak * 4 + pada]
    return {"native": "%s, pada %d" % (stars[me[0]], me[1] + 1), "partner": "Bride" if bride else "Bridegroom", "score": pick["score"], "level": pick["level"], "rows": rows,
            "native_nak": me[0], "native_pada": me[1]}


def matching_matrix():
    """All bride×groom pada combinations of the pada matching table."""
    return C.match_matrix()


def matching_detail(bride_nak, bride_pada, groom_nak, groom_pada):
    """Ashta Kuta breakdown for a selected boy/girl Moon pada pair."""
    return C.match_from_padas(bride_nak, bride_pada, groom_nak, groom_pada)


def matching_compare(bride_ch, groom_ch, bride_name="Bride", groom_name="Groom", bride_sb=None, groom_sb=None, bride_mars=None, groom_mars=None, aspect_parasara=True):
    """Full match + similarities/differences from two charts (with their shadbala, for the strength area, and Mars's bhavas for Kuja dosha)."""
    bride_ch = {**bride_ch, "name": bride_name}
    groom_ch = {**groom_ch, "name": groom_name}
    return C.compare_charts(bride_ch, groom_ch, bride_sb, groom_sb, bride_mars, groom_mars, aspect_parasara)


# the seed, and its NakshatraDasaStartPoint
SEED_ROWS = [("Janma nakshatra (Moonstar)", 0), ("Lagna nakshatra", 4), ("Sun's nakshatra", 8), ("Utpanna nakshatra (5th from Moonstar)", 1), ("Kshema nakshatra (4th from Moonstar)", 2),
             ("Aadhaana nakshatra (8th from Moonstar)", 3), ("Trisphuta (sookshma) nakshatra", 7), ("Mandi nakshatra", 5), ("Gulika nakshatra", 6)]


def seeds(ch, pada_houses):
    """Vimsottari seed comparison: the planets in quadrants from each candidate star."""
    moon, up = ch["planet_longitudes"]["Moon"], ch["upagrahas"]
    of = {0: moon, 4: ch["lagna_lon"], 8: ch["planet_longitudes"]["Sun"], 1: moon + 4 * NAK, 2: moon + 3 * NAK, 3: moon + 7 * NAK, 7: ch["sphutas"]["sookshma_trisphuta"], 5: up["Mandi"], 6: up["Gulika"]}
    hits = DS.compare_vimshottari_seeds({n: of[k] for n, k in SEED_ROWS}, {p: ch["planet_longitudes"][p] for p in B.PLANETS}, pada_houses)
    stars = B._tables()[0]["nakshatras"]
    return [{"seed": n, "index": k, "star": stars[int(of[k] % 360.0 / NAK)], "planets": hits[n], "count": len(hits[n])} for n, k in SEED_ROWS]


def period_at(d, jc, to_date, mds, path, kw):
    """The period ``path`` leads to, and the periods above it."""
    if not path:
        raise ValueError("choose a period first")
    trail, level = [], mds
    for k in range(len(path)):
        level = J.sub_periods(mds, to_date, path[:k], d.rule(jc, kw) if d.rule else None) if k else mds
        if not 0 <= path[k] < len(level):
            raise ValueError("no such period")
        trail.append(level[path[k]])
    return trail


def _lord_sign(d, jc, p):
    if d.label is D._planet or d.key == "karaka_dasa":
        return jc.signs[0][p["lord"]]
    return p.get("sign", p["lord"])


def dasa_transit(d, jc, to_date, mds, path, birth, cfg, kw):
    """Dasa-Transit Correlation: for the chosen period, when Jupiter, Saturn, Rahu and Ketu are in each house from its lord's sign. Dates in the chart's zone."""
    period = period_at(d, jc, to_date, mds, path, kw)[-1]
    ref = _lord_sign(d, jc, period)
    jd = lambda t: E.julian_day_ut(t.year, t.month, t.day, t.hour + t.minute / 60 + (t.second + t.microsecond / 1e6) / 3600 - birth.tz_east_hours, birth.gregorian)  # noqa: E731

    def day(x):
        y, m, dd, _ = E.jd_to_calendar(x + birth.tz_east_hours / 24.0, birth.gregorian)
        return "%04d-%02d-%02d" % (y, m, dd)
    found = W.dasa_transit_correlation(birth, jd(period["start"]), jd(period["end"]), ref, cfg)
    title = "%s %s" % (d.label(period), LEVEL_ABBR[len(path) - 1])
    rows = [{"house": "%s bhava from %s" % (ORDINAL[h - 1], B.SIGNS[ref]), "cells": {n: ["From %s to %s" % (day(a), day(b_)) for a, b_ in spans] for n, spans in found[h].items()}} for h in range(1, 13)]
    return {"title": title, "rows": rows}


def locate(d, jc, to_date, mds, when, depth, kw):
    """Locate an event: the path of the periods running at ``when``, down to level ``depth``, and their labels; none outside the dasa."""
    path, labels = [], []
    for _ in range(depth):
        try:
            level = D.level(d, jc, to_date, mds, path, False, kw)["periods"]
        except ValueError:      # no level this deep here: some of rasi-bhukta's antardasas
            break
        i = next((k for k, p in enumerate(level) if p["start"] <= when <= p["end"]), None)
        if i is None:
            break
        path.append(i)
        labels.append(level[i]["label"])
    return {"path": path, "labels": labels}


def sum_longitudes(d, jc, to_date, mds, path, kw):
    """"Sum of longitudes of planets upto this level"."""
    if d.label is not D._planet:
        return "Available only in dasas of grahas, such as Vimsottari dasa, Ashtottari dasa, Yogini dasa etc."
    x = J.sum_of_longitudes([p["lord"] for p in period_at(d, jc, to_date, mds, path, kw)], jc.lons) % 360.0
    secs = round(x % 30.0 * 3600, 2)
    return "Sum of longitudes of grahas upto selected level is %2d %s %02d' %05.2f\"." % (secs // 3600, B.SIGNS[int(x // 30)], secs % 3600 // 60, secs % 60)
