"""events: part of dasa_systems (split from one module; see __init__.py)."""
import copy
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple
from .chart import JChart, NAK
from .rasi import brahma_planet
from .nakshatra import group_dasa, nakshatra_dasa

# ---------------------------------------------------------------- dasa utilities

def sub_periods(mds: List[Dict[str, Any]], to_date, path: Sequence[int],
                rule: Optional[Callable[[int], List[Tuple[Dict[str, Any], float]]]] = None) -> List[Dict[str, Any]]:
    """The periods one level below ``mds[path[0]]["antardasas"][path[1]]`` .. (``path`` = indices, mahadasa
    first). Every period below the antardasas is divided by its lord's table (BPHS 51.1-2): the
    antardasas of the (first non-empty) mahadasa of the same lord, in their proportions; ``rule(period)`` gives
    (period fields, fraction) pairs instead (``kalachakra_rule``, ``sudarsana_rule``)."""
    table = {}
    for md in mds:
        if md["years"] > 0.0:
            table.setdefault(md["lord"], md)

    def default(p):
        src = table[p["lord"]]
        return [(ad, ad["years"] / src["years"]) for ad in src["antardasas"]]

    def children(p):
        if "antardasas" in p:
            return p["antardasas"]
        a, out = p["t"], []
        for ad, w in (rule or default)(p):
            y = p["years"] * w
            out.append(dict(ad, start=to_date(a), end=to_date(a + y), years=y, t=a))
            a += y
        return out
    level = mds
    for i in path:
        level = children(level[i])
    return level


def locate_event(dasas: List[Dict[str, Any]], when: datetime, depth: int = 1) -> List[int]:
    """"Locate an event": the index of the period holding ``when`` at each of
    ``depth`` levels (mahadasa, antardasa ...), by start <= when <= end."""
    out, level = [], dasas
    for _ in range(depth):
        i = next((k for k, p in enumerate(level) if p["start"] <= when <= p["end"]), None)
        if i is None:
            break
        out.append(i)
        level = level[i].get("antardasas", [])
    return out


def years_in_span(span_days: float, to_date: Callable[[float], datetime], days_per_year: float = 365.24219) -> float:
    """The dasa years (of ``to_date``'s definition) that fill ``span_days`` from
    birth: y += (span - days(y)) / nominal length, at most 500 steps, to 1 s."""
    birth = to_date(0.0)
    y = 0.0
    for _ in range(500):
        days = (to_date(y) - birth).total_seconds() / 86400.0
        if abs(days - span_days) <= 1.0 / 86400.0:
            break
        y += (span_days - days) / days_per_year
    return y


def fitted_to_span(to_date: Callable[[float], datetime], span_days: float, total_years: float,
                   days_per_year: float = 365.24219) -> Callable[[float], datetime]:
    """Dasa span fitting for event charts (returns, the Solar Month chart): every period scaled so the whole dasa
    (``total_years``) fills ``span_days``, the span of the event chart (a convention; docs/SOURCES.md section 9.1).
    Build ``to_date`` from ``event_year_definition`` when the chart is a Tajaka or Tithi Pravesha return."""
    k = years_in_span(span_days, to_date, days_per_year) / total_years
    return lambda years: to_date(years * k)


def event_year_definition(definition: int, chart_kind: int, name: str = "",
                          special_year_tajaka: bool = True, special_year_tp: bool = True) -> int:
    """The year definition used while a dasa is fitted into an event span.
    SpecialYearForTajaka (default on) forces 3, true sidereal solar, for chart kind 1 and for kind 5 whose
    name contains "Sol". SpecialYearForTP forces 4, the 360-tithi year, for kind 2 and for kind 5 whose name
    contains "Lun" or "Moon". Other charts keep ``definition``."""
    if special_year_tajaka and chart_kind == 1:
        definition = 3
    if special_year_tp and chart_kind == 2:
        definition = 4
    if special_year_tajaka and chart_kind == 5 and "Sol" in name:
        definition = 3
    if special_year_tp and chart_kind == 5 and ("Lun" in name or "Moon" in name):
        definition = 4
    return definition


# The years each builder's dasa runs, which ``fitted_to_span`` fits into an event chart's span; 120
# unless listed; a few builders sum their first cycle (EVENT_CYCLE)
EVENT_YEARS = {"yogini": 36, "dwisaptati": 72, "shattrimsa": 36, "dwadasottari": 112, "chaturaseeti": 84,
               "sataabdika": 100, "shodasottari": 116, "panchottari": 105, "ashtottari": 108, "shashtihayani": 60,
               "saptarshi_dasa": 100, "tithi_ashtottari_dasa": 108, "tithi_yogini_dasa": 36,
               "karana_chaturaseeti_dasa": 84, "sudarsana_chakra_dasa": 12, "shoola_dasa": 108, "navamsa_dasa": 108,
               "varnada_dasa": 108, "niryaana_shoola_dasa": 96, "sthira_dasa": 96, "mandooka_d11_dasa": 96}
EVENT_CYCLE = {"trikona_dasa": 12, "chara_parasara_dasa": 12, "mandooka_knrao_dasa": 12, "kalachakra_dasa": 9}


def _builder_key(fn) -> str:
    """A builder's name, or the dasa name of a ``functools.partial`` of ``nakshatra_dasa`` / ``group_dasa``."""
    f = getattr(fn, "func", fn)
    return fn.args[0] if f in (nakshatra_dasa, group_dasa) else f.__name__


def event_years(fn, mds: List[Dict[str, Any]], **kw) -> float:
    """The ``total_years`` of ``fitted_to_span`` for builder ``fn`` (``mds`` its periods): Drigdasa 96 (24
    periods and 120 with ``parasara=False``), Karaka 12 per karaka."""
    k = _builder_key(fn)
    if k == "drig_dasa":
        return 96.0 if kw.get("parasara", True) else 120.0
    if k == "karaka_dasa":
        return 6.0 * len(mds)
    if k in EVENT_CYCLE:
        return sum(m["years"] for m in mds[:EVENT_CYCLE[k]])
    return float(EVENT_YEARS.get(k, 120))


# Tajaka charts (chart kind 1) with UseDasaSeedFromNatalInTajaka and ProgressDasaSeedInTajaka on (the default
# for every slot): the nakshatra dasas take the natal chart moved on by the years (``progress``); the rasi dasas
# take the Tajaka chart with the Muntha's sign in place of the lagna's, or a natal point's
# sign counted from the Muntha as the lagna's; Sudasa its natal Sree Lagna's balance; the others the Tajaka chart.
TAJAKA_NATAL = {"vimsottari_dasa", "yogini", "dwisaptati", "shattrimsa", "dwadasottari", "chaturaseeti", "sataabdika",
                "shodasottari", "panchottari", "ashtottari", "shashtihayani", "saptarshi_dasa", "tithi_ashtottari_dasa",
                "tithi_yogini_dasa", "yoga_vimsottari_dasa", "karana_chaturaseeti_dasa", "rasi_bhukta_vimsottari_dasa"}
TAJAKA_MUNTHA = {"narayana_dasa", "lagnamsaka_dasa", "drig_dasa", "lagna_kendradi_rasi_dasa", "trikona_dasa",
                 "chara_knrao_dasa", "chara_rangacharya_dasa", "yogardha_dasa", "paryaya_dasa", "shoola_dasa",
                 "niryaana_shoola_dasa", "mandooka_d11_dasa", "mandooka_knrao_dasa", "navamsa_dasa"}
TAJAKA_POINT = {"ak_kendradi_rasi_dasa": JChart.atmakaraka, "brahma_dasa": brahma_planet, "sthira_dasa": brahma_planet}


def event_dasa(fn, jc: JChart, to_date, natal: Optional[JChart] = None, **kw) -> List[Dict[str, Any]]:
    """Builder ``fn``'s dasa of an event chart ``jc`` (a Tithi Pravesha or other return; ``to_date`` the event
    chart's, ``fitted_to_span``): as for a birth chart, but Karana Chaturaseeti lists 8 periods (the view shows the
    first 8 of Yogini, Shattrimsa and Tithi Yogini, 12 of Chara) and Sudasa cuts its first period by the
    ``natal`` Sree Lagna."""
    k = _builder_key(fn)
    if k == "karana_chaturaseeti_dasa":
        kw.setdefault("event", True)
    if k == "sudasa" and natal is not None:
        kw.setdefault("sl_lon", natal.special["Sree_Lagna"])
    return fn(jc, to_date, **kw)


def tajaka_dasa(fn, natal: JChart, event: JChart, muntha_signs: Sequence[int], years: int, to_date,
                **kw) -> List[Dict[str, Any]]:
    """Builder ``fn``'s dasa in a Tajaka chart ``years`` after birth; ``muntha_signs`` the Muntha's sign in each
    varga (``tajika.muntha_position``), ``to_date`` the event chart's, fitted to its span (``fitted_to_span``)."""
    k = _builder_key(fn)
    if k in TAJAKA_NATAL:
        return event_dasa(fn, natal, to_date, progress=years, **kw)
    if k in TAJAKA_MUNTHA:
        moved = copy.copy(event)
        moved.signs = [[m] + list(v[1:]) for m, v in zip(muntha_signs, event.signs)]
        return fn(moved, to_date, **kw)
    if k in TAJAKA_POINT:
        seed = (natal.signs[0][TAJAKA_POINT[k](natal)] - natal.signs[0][0] + muntha_signs[0]) % 12
        return fn(event, to_date, seed=seed, **kw)
    return event_dasa(fn, event, to_date, natal, **kw)


def sum_of_longitudes(lords: Sequence[int], lons: Sequence[float]) -> float:
    """"Sum of longitudes of planets upto this level" (Nakshatra dasa popup): the lords of the chosen
    periods, mahadasa first; Sun .. Saturn add their longitude in the chart, Rahu and Ketu add 360 minus it."""
    total = 0.0
    for p in lords:
        total += lons[p] if p < 8 else 360.0 - lons[p]
    return total % 360.0


def without_sesham(mds: List[Dict[str, Any]], to_date) -> List[Dict[str, Any]]:
    """Dasas of a mundane chart with DasaSeshamInMundaneCharts off: the first period is
    not cut to its balance, so every period moves on by the part that had run."""
    if not mds:
        return mds
    shift = mds[0]["t"]

    def move(ps):
        for p in ps:
            if "t" in p:
                p["t"] -= shift
                p["start"], p["end"] = to_date(p["t"]), to_date(p["t"] + p["years"])
            move(p.get("antardasas", ()))
    move(mds)
    return mds


def nakshatra_progression_arc(mds: List[Dict[str, Any]], to_date, when: datetime, seed_lon: float, levels: int = 6,
                              rule=None) -> float:
    """"Nakshatra Dasa Progression" (with ``locate_event``): every body and lagna of the natal chart
    moves by this arc. The longitude the running period stands for: from the start of the seed's nakshatra, each level's
    period index in equal parts (a nakshatra for each mahadasa, a ninth of that for each antardasa ..), plus the elapsed
    fraction of the deepest period; the arc is that less the seed's longitude."""
    lon, step = (seed_lon // NAK) * NAK, NAK
    level, path = mds, []
    for depth in range(levels):
        i = next(k for k, p in enumerate(level) if p["start"] <= when <= p["end"])
        lon += i * step
        path.append(i)
        p = level[i]
        if depth == levels - 1:
            lon += (when - p["start"]).total_seconds() / (p["end"] - p["start"]).total_seconds() * step
            break
        step /= len(level) if depth else 9
        level = p["antardasas"] if depth == 0 else sub_periods(mds, to_date, path, rule)
    return (lon - seed_lon) % 360.0
