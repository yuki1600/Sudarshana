"""The Astrocartography tab: the sign and bhava bands and the graha lines of a moment, over the world map. Our own view, not a port."""
from core_logic import astrocartography as A, ephemeris as E, house_systems as H

from . import houses as HS
from .houses import ABBR, REFS


def _zones(key, ids, lons, f, cusps=()):
    curves = A.bands(lons, f)
    zones = [{key: i, "curve": c, "area": a} for i, c, a in zip(ids, curves, [*A.band_areas(lons, f, curves), None])]
    for zone, cusp in zip(zones, cusps):
        zone["cusp"] = A.lagna_curve(cusp, f)
    return zones


def _bhavas(birth, ch, cfg, s, of, t, f):
    """Which bhava, east of each curve, in system ``t`` (a Houses tab system, not necessarily the House system option); the curves are the bhavas' borders.
    Lagna: the natal bhava the relocated Lagna falls in. A graha: its bhava in the relocated chart, from the relocated Lagna.
    With the cusp in the middle of the bhava it has its own curve: where the Lagna is on the natal cusp, or the graha on the cusp of that house. Otherwise the border is the cusp."""
    cim = s.house_cusp_in_middle
    if of == "Lagna":
        bh = HS._bhavas(birth, ch, cfg, s.model_copy(update={"house_type": t}))
        return _zones("house", [*range(1, 13), 1], [b[0] for b in bh], f, [b[1] for b in bh] if cim else ())
    x = ch["planet_longitudes"][of]
    if t < 3:   # the houses go with the relocated Lagna alone, so each border is a Lagna curve
        borders, middles = A.crossings(lambda lagna: H.bhava_spans(lagna, t, [lagna + 30.0 * i for i in range(12)], cim), x)
        first = next(i for i, (_, h) in enumerate(borders) if h == 12)
        borders = borders[first:] + borders[:first]
        cusp = dict((h, lagna) for lagna, h in middles)
        return _zones("house", [*(h for _, h in borders), 12], [lagna for lagna, _ in borders], f, [cusp[h] for _, h in borders] if cim else ())
    letter, swe = E.HOUSE_SYSTEM_CODES[HS.SYSTEMS[t]].encode(), E._require_swe()

    def bhavas_at(armc, lat):
        c, a = swe.houses_armc(armc, lat, f.obliquity, letter)
        return H.bhava_spans((a[0] - f.ayanamsa) % 360.0, t, [(y - f.ayanamsa) % 360.0 for y in c[:12]], cim)
    borders, middles = A.armc_curves(bhavas_at, x, f)
    houses = range(12, 0, -1)      # east, the sky turns west: a graha goes back a house at a time
    if sorted(borders) != list(range(1, 13)) or len({len(c) for c in borders.values()}) != 1:
        raise ValueError("These bhavas could not be traced for this graha. Choose another system.")
    curves = A.ordered([borders[h] for h in houses])
    zones = [{"house": h, "curve": c, "area": [*c, *n[::-1]] if n else None} for h, c, n in zip([*houses, 12], curves, [*curves[1:], None])]
    if cim:
        for zone in zones[:12]:
            c, m = zone["curve"], middles[zone["house"]]
            mid = len(m) // 2
            shift = c[mid][0] + (m[mid][0] - c[mid][0]) % 360.0 - m[mid][0]
            zone["cusp"] = [[lon + shift, lat] for lon, lat in m]
    return zones


def astrocartography(birth, ch, cfg, s, bhava_of=None, bhava_system=None):
    f = A.frame(birth.jd_ut, cfg)
    lines = []
    for name in REFS[1:]:
        x = ch["planet_longitudes"][name]
        mc, ic = A.meridian_lon(x, f), A.meridian_lon(x + 180.0, f)
        lines += [{"body": ABBR[name], "angle": angle, "curve": curve} for angle, curve in (
            ("ASC", A.lagna_curve(x, f)), ("DSC", A.lagna_curve(x + 180.0, f)), ("MC", [[mc, -90], [mc, 90]]), ("IC", [[ic, -90], [ic, 90]]))]
    return {"poles": A.ecliptic_poles(f), "lines": lines, "signs": _zones("sign", [i % 12 for i in range(13)], [30.0 * i for i in range(12)], f),
            "bhavas": _bhavas(birth, ch, cfg, s, bhava_of, (3 if bhava_of == "Lagna" else 1) if bhava_system is None else bhava_system, f) if bhava_of else None}
