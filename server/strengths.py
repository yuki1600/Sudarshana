"""The Strengths screen: ashtakavarga, shadbala, vimsopaka and yogas."""
from datetime import datetime, timedelta

from core_logic import ashtakavarga, avasthas as AV, ephemeris as E, dasa_systems as J, time_search as JS, varga_charts as V, yoga_engine, shadbala as SB, tajika as T

from . import settings as S

from . import basics as B
from .basics import PLANETS
from . import houses as HS
from core_logic import house_systems as H

SEVEN = PLANETS[:7]


def ashtakavarga_of(ch, s):
    signs = [ch["lagna_sign"]] + [ch["planet_signs"][p] for p in SEVEN]
    r = ashtakavarga.ashtakavarga_tables(signs, **S.ashtakavarga_kw(s))
    return {"signs": signs, "bav": r["bav"], "reduced": r["reduced"], "pindas": r["pindas"], "sav": r["sav"]}


def _varga_signs(ch, s):
    """Sun .. Ketu in the vargas of the strengths, in the chosen schemes."""
    lons = [ch["planet_longitudes"][p] for p in PLANETS]
    opt = S.varga_options(s)
    return {v: [V.varga_sign(x, int(v[1:]), opt) for x in lons] for v, _ in J.VARGAS if v in SB.VARGA_ORDER}


def vimsopaka_of(ch, s):
    vim = SB.vimsopaka_balas(_varga_signs(ch, s), s.vimsopaka_from_rasi)
    return [{"name": p, **{k: vim[p][k] for k in ("dasa", "shodasa", "sapta", "shad")}} for p in PLANETS]


def vargas_used(group):
    """The note under a vimsopaka bar graph: the vargas of that scheme, in D-number order."""
    idx = next(i for g, i, _ in SB._VIMSOPAKA_GROUPS if g == group)
    return ", ".join(sorted((SB.VARGA_ORDER[i] for i in idx), key=lambda v: int(v[1:])))


def shadbala_of(birth, ch, cfg):
    sb = E.chart_shadbala(birth, ch, cfg)
    keys = ("sthana", "kala", "dig", "cheshta", "naisargika", "drig", "total", "rupas", "percent", "ishta", "kashta")
    return {"planets": [{"name": p, **{k: sb["planets"][p][k] for k in keys}, "required": SB._REQUIRED_RUPAS[i]} for i, p in enumerate(SEVEN)],
            "bhavas": [{"house": i + 1, **b} for i, b in enumerate(sb["bhavas"])]}


def yogas_of(ch, group=0, d=1, bhavas=None, cusp_in_middle=True):
    """``bhavas``: the D-1's houses, for house placements and lords by longitude (else houses are signs)."""
    return [{k: r[k] for k in ("type", "name", "varga", "givers_text", "result", "definition", "basis", "places")}
            for r in yoga_engine.chart_yogas(ch, group, V.DIVISIONS.index(d), bhavas, cusp_in_middle)]


def yoga_list():
    """"Just show a list of supported yogas"."""
    return [{"index": i + 1, "type": yoga_engine.GROUPS[g + 1], "name": n, "definition": d, "result": r,
             "basis": yoga_engine.BASIS_NAMES[yoga_engine.BASIS[g][i]]} for g, cat in enumerate(yoga_engine.CATALOGUE) for i, (n, d, r) in enumerate(cat)]


def ashtakavarga_view(ch, s, d=1, lagna=None):
    """The Ashtakavarga view of D-``d``, with ``lagna`` as the lagna when it is recomputed from another sign: BAV and SAV, the reduced rows, the prastara of each row, the pindas and the signs and stars they give."""
    opt = S.varga_options(s)
    signs = [V.varga_sign(ch["lagna_lon"], d, opt)] + [V.varga_sign(ch["planet_longitudes"][p], d, opt) for p in SEVEN]
    if lagna is not None:
        signs[0] = lagna
    kw = S.ashtakavarga_kw(s)
    r = ashtakavarga.ashtakavarga_tables(signs, **kw)
    # "By multiplying the sodhya pinda of a planet and the score in its ashtakavarga in a rasi, we get a number. By dividing it with 27 and 12, we get a nakshatra or rasi"
    stars = B._tables()[0]["nakshatras"]
    points = [[{"rasi": B.SIGNS[(p[0] * n - 1) % 12], "nakshatra": stars[(p[0] * n - 1) % 27], "star": (p[0] * n - 1) % 27, "sign": (p[0] * n - 1) % 12} for n in r["bav"][i]] for i, p in enumerate(r["pindas"])]
    return {"signs": signs, "bav": r["bav"], "reduced": r["reduced"], "pindas": r["pindas"], "sav": r["sav"], "pav": ashtakavarga.prastara_tables(signs, kw["parasara"], kw["definition"]), "pinda_points": points}


def bar_group(birth, ch, cfg, s, kind, d=1):
    """The other sets of bar graphs. Same data as the lists."""
    panel = lambda title, labels, values, digits=1: {"title": title, "labels": labels, "values": values, "digits": digits}  # noqa: E731
    nine, seven = ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"], ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa"]
    sb = E.chart_shadbala(birth, ch, cfg)
    if kind == "bhava":
        return [panel("Bhava Bala", [str(i + 1) for i in range(12)], [b["total"] for b in sb["bhavas"]])]
    if kind == "breakup":
        keys = (("sthana", "Sthana Bala"), ("kala", "Kaala Bala"), ("dig", "Dig Bala"), ("cheshta", "Cheshta Bala"), ("naisargika", "Naisargika Bala"), ("drig", "Drik Bala"))
        return [panel(t, seven, [sb["planets"][p][k] for p in SEVEN]) for k, t in keys]
    if kind == "vimsopaka":
        rows = vimsopaka_of(ch, s)
        return [{**panel("Vimsopaka Bala (%s)" % t, nine, [r[k] for r in rows]), "note": vargas_used(k)} for k, t in (("shodasa", "Shodasa"), ("dasa", "Dasa"), ("sapta", "Sapta"), ("shad", "Shad"))]
    if kind == "vaiseshikamsa":
        vai = vaiseshikamsa_of(ch, s, E.day_lords(birth, cfg, **S.day_kw(s)))
        return [panel("Vaiseshikamsa (%s)" % t, nine, [vai[p][k] for p in PLANETS], 0) for k, t in (("dasa", "Dasa"), ("shodasa", "Shodasa"), ("sapta", "Sapta"), ("shad", "Shad"))]
    if kind == "rashmis":
        ra = SB.rashmis_ishta_kashta(sb["planets"])
        return [panel(t, seven, [ra[p][k] for p in SEVEN], 2) for k, t in (("uchcha_rashmi", "Uchcha Rashmi"), ("cheshta_rashmi", "Cheshta Rashmi"), ("subha", "Subha Rashmi"), ("asubha", "Asubha Rashmi"), ("ishta", "Ishta Phala (Parasara)"), ("kashta", "Kashta Phala (Parasara)"))]
    av = ashtakavarga_view(ch, s, d)
    shadbala, vim = shadbala_of(birth, ch, cfg), vimsopaka_of(ch, s)
    return bars_of(birth, ch, cfg, s, av, shadbala, vim, d)


def bars_of(birth, ch, cfg, s, av, shadbala, vimsopaka, d=1):
    """Strengths > Bar graphs: the panels of the screen, each {title, labels, values}. Same data as the lists."""
    jc = S.jchart(ch, None, s)
    sb = E.chart_shadbala(birth, ch, cfg)
    day = E.day_lords(birth, cfg, **S.day_kw(s))
    tb = T.tajaka_balas(jc.signs, jc.lons, [sb["planets"][p]["uchcha"] for p in SEVEN], day["is_day"])
    vai = vaiseshikamsa_of(ch, s, day)
    nine, seven = ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"], ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa"]
    panel = lambda title, labels, values, digits=0: {"title": title, "labels": labels, "values": values, "digits": digits}  # noqa: E731
    return [
        {**panel("Vimsopaka Bala (Shodasa)", nine, [r["shodasa"] for r in vimsopaka], 1), "note": vargas_used("shodasa")},     # all 16 vargas
        panel("Shadbala (% bala)", seven, [r["percent"] for r in shadbala["planets"]]),
        panel("Ishta Phala", seven, [r["ishta"] for r in shadbala["planets"]], 1),
        panel("Pancha Vargeeya Bala", seven, [tb[p]["pancha_vargeeya"] for p in SEVEN], 1),
        panel("Dwadasa Vargeeya Bala", seven, [tb[p]["dwadasa_vargeeya"] for p in SEVEN]),
        panel("Harsha Bala", seven, [tb[p]["harsha"] for p in SEVEN]),
        panel("Vaiseshikamsa (Dasa)", nine, [vai[p]["dasa"] for p in PLANETS]),
        panel("Ashtakavarga Bala (D-%d)" % d, ["As"] + seven, [av["bav"][i][s] for i, s in enumerate(av["signs"])]),
    ]


def _motion(a, b):
    """Degrees moved from longitude a to b, the short way round (negative: retrograde)."""
    return (b - a + 180.0) % 360.0 - 180.0


def _samples(lon, jd0, jd1, step):
    """Times and longitudes every ``step`` days, and every half day across each station (where the motion turns), so
    that a retrograde dip out of a sign or star and back in near a station is not stepped over."""
    ts = [jd0 + i * step for i in range(int((jd1 - jd0) // step) + 1)] + [jd1]
    xs = [lon(t) for t in ts]
    turns = {k for k in range(1, len(ts) - 1) if _motion(xs[k - 1], xs[k]) * _motion(xs[k], xs[k + 1]) <= 0}     # 0: no net motion over a step, turned within it
    out_t, out_x = [ts[0]], [xs[0]]
    for k in range(1, len(ts)):
        if k in turns or k - 1 in turns:
            t = ts[k - 1] + 0.5
            while t < ts[k]:
                out_t.append(t)
                out_x.append(lon(t))
                t += 0.5
        out_t.append(ts[k])
        out_x.append(xs[k])
    return out_t, out_x


def _visits(lon, inside, ts, xs, gap=730.0):
    """The stays of a body in a part of the zodiac (``inside(longitude)``) over the samples ``ts``/``xs``: each visit a
    list of its passes [entry, exit], every edge bisected to the hour. Retrogression can take the body out and back in
    again (several passes); passes less than ``gap`` days apart are one visit. An entry at ts[0] means it was already
    there; an exit of None, still there at the end."""
    def edge(a, b, ia):     # inside at a is ia, at b it is not
        while b - a > 1 / 24:
            m = (a + b) / 2
            a, b = (m, b) if inside(lon(m)) == ia else (a, m)
        return b
    passes, was = [], inside(xs[0])
    start = ts[0] if was else None
    for k in range(1, len(ts)):
        now = inside(xs[k])
        if now != was:
            e = edge(ts[k - 1], ts[k], was)
            if now:
                start = e
            else:
                passes.append([start, e])
            was = now
    if was:
        passes.append([start, None])
    visits = []
    for p in passes:
        if visits and p[0] - visits[-1][-1][1] < gap:
            visits[-1].append(p)
        else:
            visits.append([p])
    return visits


def pinda_transits(birth, cfg, mds, pds, star, sign, now_jd, count=3):
    """Jupiter's and Saturn's last ``count`` visits, since birth, to the nakshatra ``star`` and the rasi ``sign`` (from
    the sodhya pindas: "transit of Jupiter/Saturn in it is good/bad"): each visit's span and the vimsottari MD-ADs it
    fell in, then every entry and exit in it (retrograde ones marked) with the MD-AD-PD then. ``pds(i, k)``: the
    pratyantardasas of antardasa k of mahadasa i."""
    two = ["", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"]

    def local(jd):      # the dasas' dates are local clock times
        y, mo, d, h = E.jd_to_calendar(jd + birth.tz_east_hours / 24.0, birth.gregorian)
        return datetime(y, mo, d) + timedelta(hours=h)

    def text(jd):
        return None if jd is None else local(jd).strftime("%Y-%m-%d")

    def dasa_at(jd):
        t = local(jd)
        for i, m in enumerate(mds):
            if m["start"] <= t < m["end"]:
                for k, ad in enumerate(m["antardasas"]):
                    if ad["start"] <= t < ad["end"]:
                        pd = next((p for p in pds(i, k) if p["start"] <= t < p["end"]), None)
                        return "-".join(two[x["lord"]] for x in (m, ad, pd) if x)
        return None

    def visit(lon, v):
        a, b = v[0][0], v[-1][1]
        ta, tb = local(a), local(b if b is not None else now_jd)
        running = [f"{two[m['lord']]}-{two[ad['lord']]}" for m in mds for ad in m["antardasas"] if ad["start"] <= tb and ad["end"] >= ta]
        retro = lambda jd: jd is not None and _motion(lon(jd - 0.5), lon(jd + 0.5)) < 0  # noqa: E731
        born_in = a <= birth.jd_ut
        return {"start": text(a), "end": text(b), "dasas": running, "born_in": born_in,
                "passes": [{"in": text(i), "in_r": not (born_in and n == 0) and retro(i), "in_dasa": dasa_at(i),
                            "out": text(o), "out_r": retro(o), "out_dasa": None if o is None else dasa_at(o)} for n, (i, o) in enumerate(v)]}

    part = 360.0 / 27.0
    out = {}
    for name, p, step in (("jupiter", 5, 5.0), ("saturn", 7, 10.0)):
        lon = JS.body_longitude(p, cfg, birth)
        ts, xs = _samples(lon, birth.jd_ut, now_jd, step)
        out[name] = {k: [visit(lon, v) for v in _visits(lon, f, ts, xs)[-count:]][::-1]
                     for k, f in (("star", lambda x: int(x // part) == star), ("sign", lambda x: int(x // 30.0) == sign))}
    return out


def vaiseshikamsa_of(ch, s, day):
    opt = S.varga_options(s)
    lagna = [V.varga_sign(ch["lagna_lon"], int(v[1:]), opt) for v in SB.VARGA_ORDER]
    return SB.vaiseshikamsa_counts(_varga_signs(ch, s), S.amsa_bala(s, ch, lagna, day["janma_ghatis"]))


def cusp_bala_of(birth, ch, cfg, s):
    """Each graha's strength by its place in its house: 100% on the cusp (the house's middle), falling linearly to 0 at either edge."""
    bh = HS._bhavas(birth, ch, cfg, s)
    out = []
    for p in PLANETS:
        lon = ch["planet_longitudes"][p]
        i = H.house_of(lon, bh)
        start, mid, end = bh[i]
        off = (lon - mid + 180.0) % 360.0 - 180.0      # degrees past the cusp, negative before it
        half = (mid - start) % 360.0 if off < 0 else (end - mid) % 360.0
        out.append({"name": p, "house": i + 1, "lon": lon, "cusp": mid, "from_cusp": off, "percent": max(0.0, 100.0 * (1 - abs(off) / half)) if half else 100.0})
    return out


def strengths(birth, ch, cfg, s):
    av, shadbala, vimsopaka = ashtakavarga_of(ch, s), shadbala_of(birth, ch, cfg), vimsopaka_of(ch, s)
    return {"av": av, "shadbala": shadbala, "cusp_bala": cusp_bala_of(birth, ch, cfg, s), "vimsopaka": vimsopaka, "yogas": yogas_of(ch), "bars": bars_of(birth, ch, cfg, s, av, shadbala, vimsopaka)}
