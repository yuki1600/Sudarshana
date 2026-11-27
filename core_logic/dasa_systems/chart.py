"""chart: part of dasa_systems (split from one module; see __init__.py)."""
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Sequence
from .. import natal_chart as N

PLANET_ABBR = ["Lag", "Sun", "Moon", "Mars", "Merc", "Jup", "Ven", "Sat", "Rah", "Ket"]
SIGN_ABBR = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]
NAK = 360.0 / 27.0

# the varga order of the chart tables (Key Info's 23 charts)
VARGAS = (("D1", N.compute_varga_d1), ("D9", N.compute_varga_d9), ("D2", lambda x: N.compute_varga_d2(x, "us")),
          ("D3", N.compute_varga_d3), ("D4", N.compute_varga_d4), ("D5", N.compute_varga_d5),
          ("D6", N.compute_varga_d6), ("D7", N.compute_varga_d7), ("D8", N.compute_varga_d8),
          ("D10", N.compute_varga_d10), ("D11", N.compute_varga_d11), ("D12", N.compute_varga_d12),
          ("D16", N.compute_varga_d16), ("D20", N.compute_varga_d20), ("D24", N.compute_varga_d24),
          ("D27", N.compute_varga_d27), ("D30", N.compute_varga_d30), ("D40", N.compute_varga_d40),
          ("D45", N.compute_varga_d45), ("D60", N.compute_varga_d60), ("D81", N.compute_varga_d81),
          ("D108", N.compute_varga_d108), ("D144", N.compute_varga_d144))
VARGA_NUMBER = [int(v[1:]) for v, _ in VARGAS]

# 28-nakshatra scheme with Abhijit for the group dasas (starts and spans): Abhijit from 276 deg 40' (the last quarter of
# Uttarashadha) to 280 deg 53' 40" (about the first fifteenth of Sravana; docs/SOURCES.md section 2)
NAK28_START = [0.0, 13.333333, 26.666667, 40.0, 53.333333, 66.666667, 80.0, 93.333333, 106.666667, 120.0,
               133.333333, 146.666667, 160.0, 173.333333, 186.666667, 200.0, 213.333333, 226.666667, 240.0,
               253.333333, 266.666667, 276.666667, 280.894444, 293.333333, 306.666667, 320.0, 333.333333,
               346.666667]


class JChart:
    """The parts of the chart object the dasa builders read, from an ``ephemeris.build_chart`` result:
    ``lons[p]`` rasi longitudes of points 0 Lagna .. 9 Ketu and ``signs[v][p]`` their signs in varga ``v``."""

    POINTS = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    POINT_KEYS = {17: ("special", "Pranapada"), 19: ("special", "Indu_Lagna"), 20: ("special", "Bhrigu_Bindu"),
                  31: ("upagrahas", "Mandi"), 32: ("upagrahas", "Gulika"), 36: ("sphutas", "sookshma_trisphuta")}

    def __init__(self, chart: Dict[str, Any], day: Optional[Dict[str, Any]] = None,
                 user_points: Optional[Dict[int, float]] = None):
        """``day``: ``ephemeris.day_lords(birth)`` (ghatis since sunrise, day / night length) for the dasas
        timed by the birth moment (Kaala, Chakra)."""
        pl = chart["planet_longitudes"]
        self.lons = [chart["lagna_lon"]] + [pl[p] for p in self.POINTS[1:]]
        self.signs = [[f(x) for x in self.lons] for _, f in VARGAS]
        self.special = chart.get("special_lagnas", {})
        self.upagrahas = chart.get("upagrahas", {})
        self.sphutas = chart.get("sphutas", {})
        self.user_points = user_points or {}
        self.day = day
        self.correction = 0.0       # the sidereal nakshatras of a tropical chart (dasa_seed)
        hl = self.special.get("Hora_Lagna")
        self.hora_lagna_sign = int(hl // 30) if hl is not None else None
        vl = chart.get("varnada_lagnas")
        self.varnada_sign = int(vl[0] // 30) if vl else None

    def moon(self) -> float:
        return self.lons[2]

    def point(self, p: int) -> float:
        """The rasi longitude of point ``p`` (0 .. 9, and the dasa seeds: 17 Pranapada, 19 Indu Lagna, 20
        Bhrigu Bindu, 31 Maandi, 32 Gulika, 36 Sookshma TriSphuta; 103, 104 the user's special lagna and point,
        from ``jc.user_points``)."""
        if p < 10:
            return self.lons[p]
        if p in (103, 104):
            return self.user_points.get(p, 0.0)     # as captured: without a point set, 0 degrees (Ketu's dasa, whole)
        source, key = self.POINT_KEYS[p]
        return getattr(self, source)[key]

    def atmakaraka(self) -> int:
        """The atmakaraka: the graha furthest in its sign (8 karakas: Rahu counted from the end of its sign; BPHS 32.3-8)."""
        deg = [x % 30.0 for x in self.lons[:9]]
        deg[8] = 30.0 - deg[8]
        return max(range(1, 9), key=lambda p: deg[p])


def _md(lord, start, end, years, t=None):
    """A period; ``t`` is its start in dasa years from birth (what ``sub_periods`` dates the lower levels from)."""
    return {"lord": lord, "start": start, "end": end, "years": years, "t": t}


def periods(to_date: Callable[[float], datetime], lords: Sequence[int], years: Sequence[float],
            start: float = 0.0, sub: Optional[Callable[[int, int], Sequence[int]]] = None,
            sub_years: Optional[Sequence[float]] = None, total: Optional[float] = None) -> List[Dict[str, Any]]:
    """Mahadasas from ``start`` (dasa years from birth) with their antardasas.
    ``sub(i, lord)`` lists the antardasa lords of mahadasa ``i``; they share it equally unless ``sub_years``
    (years by lord) is given, then in proportion to ``sub_years[lord] / total``."""
    out, t = [], start
    if hasattr(to_date, "rebased"):   # the Moon year (ephemeris.dasa_year_mapper) counts from the dasa's start
        to_date = to_date.rebased(start)
    for i, (lord, y) in enumerate(zip(lords, years)):
        md = _md(lord, to_date(t), to_date(t + y), y, t)
        if sub is not None:
            ads, a = [], t
            subs = list(sub(i, lord))
            for s in subs:
                ay = y * sub_years[s] / total if sub_years is not None else y / len(subs)
                ads.append(_md(s, to_date(a), to_date(a + ay), ay, a))
                a += ay
            md["antardasas"] = ads
        out.append(md)
        t += y
    return out
