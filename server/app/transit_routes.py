"""transit_routes: part of app (split from one module; see __init__.py)."""
from typing import Literal, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field
from .. import charts, service, transits as TR
from ..houses import REFS
from .chart_routes import ChartReq, _found
from .main import app

class TransitReq(ChartReq):
    natal: service.BirthIn
    reference: int = Field(0, ge=0, le=2)        # Moon, lagna, arudha lagna
    natal_varga: Literal[tuple(charts.V.DIVISIONS)] = 1
    transit_varga: Literal[tuple(charts.V.DIVISIONS)] = 1


@app.post("/api/transit")
def transit(req: TransitReq):
    return service.transit(req.natal, req.birth, req.settings, req.reference, req.natal_varga, req.transit_varga)


@app.post("/api/transit/domains")
def transit_domains(req: TransitReq):
    return service.transit_domains(req.natal, req.birth, req.settings)


class DomainReq(TransitReq):
    division: Literal[tuple(TR.DOMAINS)] = 1


@app.post("/api/transit/domain")
def transit_domain(req: DomainReq):
    return service.transit_domain(req.natal, req.birth, req.settings, req.division)


class AheadReq(DomainReq):
    years: Literal[TR.AHEAD_YEARS] = 2


@app.post("/api/transit/ahead")
def transit_ahead(req: AheadReq):
    return service.transit_ahead(req.natal, req.birth, req.settings, req.division, req.years)


class PanchangaReq(ChartReq):
    offset: int = Field(0, ge=-36500, le=36500)
    days: int = Field(7, ge=1, le=31)


@app.post("/api/panchanga")
def panchanga(req: PanchangaReq):
    return _found(service.panchanga, req.birth, req.settings, req.offset, req.days)


class MuhurtaDayReq(ChartReq):
    lunar: Literal["purnimanta", "amanta", "saura"] = "purnimanta"


@app.post("/api/muhurta/day")
def muhurta_day(req: MuhurtaDayReq):
    return _found(service.muhurta_day, req.birth, req.settings, req.lunar)


class MuhurtaFindReq(ChartReq):
    event: str
    natal: Optional[service.BirthIn] = None      # judge for this person too: tarabala, chandrabala


@app.get("/api/muhurta/events")
def muhurta_events():
    return service.MU.events()


@app.post("/api/muhurta/find")
def muhurta_find(req: MuhurtaFindReq):
    return _found(service.muhurta_find, req.birth, req.settings, req.event, req.natal)


class FestivalsReq(ChartReq):
    calendar: str = "north"


@app.get("/api/festivals/calendars")
def festival_calendars():
    return service.FE.calendars()


@app.post("/api/festivals")
def festivals(req: FestivalsReq):
    if req.calendar not in {c["id"] for c in service.FE.calendars()}:
        raise HTTPException(422, "No such calendar: %s" % req.calendar)
    return _found(service.festivals, req.birth, req.settings, req.calendar)


class PanchangaTextReq(ChartReq):
    kind: Literal["panchanga", "dp", "ephemeris", "movements"]
    year: int
    month: int = Field(ge=1, le=12)
    day: int = Field(1, ge=1, le=31)
    days: int = Field(31, ge=1, le=366)


@app.post("/api/panchanga/text")
def panchanga_text(req: PanchangaTextReq):
    return _found(service.panchanga_text, req.birth, req.settings, req.kind, req.year, req.month, req.day, req.days)


class LaghuReq(ChartReq):
    mode: int = Field(1, ge=0, le=5)
    added: Optional[Literal["Lagna", "Bhava Lagna", "Hora Lagna", "Ghati Lagna", "Vighati Lagna", "Pranapada Lagna", "Sree Lagna", "Indu Lagna"]] = "Lagna"
    span_days: Optional[float] = Field(None, gt=0)   # a derived chart: the span its ages fit into
    division: Literal[tuple(charts.V.DIVISIONS)] = 1
    count_signs: bool = True                          # "Count signs in divisions", or find longitudes
    one_cycle: bool = False


@app.post("/api/laghu_parasari")
def laghu_parasari(req: LaghuReq):
    return _found(service.laghu_parasari, req.birth, req.settings, req.mode, req.added, req.span_days, req.division, req.count_signs, req.one_cycle)


class VargasReq(ChartReq):
    divisions: Optional[list[Literal[1, 9, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 81, 108, 144]]] = None


@app.post("/api/vargas")
def vargas(req: VargasReq):
    return service.vargas(req.birth, req.settings, req.divisions)


class AstroReq(ChartReq):
    bhava_of: Optional[Literal[tuple(REFS)]] = None
    bhava_system: Optional[int] = Field(None, ge=0, le=10)    # a Houses tab system; none: Sripati for the Lagna, equal for a graha


@app.post("/api/astrocartography")
def astrocartography(req: AstroReq):
    return _found(service.astrocartography, req.birth, req.settings, req.bhava_of, req.bhava_system)


class FinanceOhlcReq(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=40)
    range: str = "1y"
    interval: str = "1d"
    exchange: Optional[str] = Field(None, max_length=32)
    end_ms: Optional[int] = None  # buffer ends here (default: now); UI pans a shorter window inside it
    buffer: int = Field(1, ge=1, le=10)  # fetch this many range-lengths so sliding stays local


@app.post("/api/finance/ohlc")
def finance_ohlc(req: FinanceOhlcReq):
    return _found(service.finance_ohlc, req.symbol, req.range, req.interval, req.exchange, req.end_ms, req.buffer)


@app.get("/api/finance/search")
def finance_search(q: str = "", limit: int = 8):
    return _found(service.finance_search, q, limit)


class FinanceEventsReq(ChartReq):
    start_ms: int
    end_ms: int
    kinds: Optional[list[Literal["ingress", "conjunction", "opposition", "station", "eclipse", "combustion"]]] = None


@app.post("/api/finance/events")
def finance_events(req: FinanceEventsReq):
    return _found(service.finance_events, req.birth, req.settings, req.start_ms, req.end_ms, req.kinds)


class TimelineReq(ChartReq):
    year: int = Field(ge=1800, le=2400)


@app.post("/api/timeline")
def timeline(req: TimelineReq):
    return _found(service.timeline, req.birth, req.settings, req.year)


class PanelReq(ChartReq):
    spec: charts.ChartSpec = charts.ChartSpec()
    view: Literal[charts.VIEWS] = "standard"
    optional: Optional[dict[str, bool]] = None
    natal: Optional[service.BirthIn] = None     # a transit's bhava chart: placed in these natal houses


@app.post("/api/panel")
def panel(req: PanelReq):
    return _found(service.panel, req.birth, req.settings, req.spec, req.view, req.optional, req.natal)


class JamakkolReq(ChartReq):
    kind: Literal["rasi", "bhava"] = "rasi"


@app.post("/api/jamakkol")
def jamakkol(req: JamakkolReq):
    """Transits > Jamakkol: ``birth`` is the moment and place of the question; ``kind`` the rasi chart or the bhavas from the lagna."""
    return _found(service.jamakkol, req.birth, req.settings, req.kind)


class AskReq(ChartReq):
    spec: charts.ChartSpec = charts.ChartSpec()
    question: Literal["highlight", "relationships", "when", "marana", "pachakadi", "text"]
    kind: Optional[Literal["argala", "virodhargala", "rasi_drishti_of_rasi", "graha_drishti", "rasi_drishti", "owned", "moolatrikona", "exalted", "debilitated",
                           "permanent", "temporary", "compound", "south", "north", "east", "all"]] = None
    planet: Optional[int] = Field(None, ge=0, le=9)
    rasi: Optional[int] = Field(None, ge=0, le=11)


@app.post("/api/chart/ask")
def chart_ask(req: AskReq):
    return _found(service.chart_ask, req.birth, req.settings, req.spec, req.question, req.kind, req.planet, req.rasi)


class MoveLagnaReq(ChartReq):
    forward: bool


@app.post("/api/chart/move_lagna")
def move_lagna(req: MoveLagnaReq):
    return _found(service.move_lagna, req.birth, req.settings, req.forward)
