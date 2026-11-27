"""mode_routes: part of app (split from one module; see __init__.py)."""
from datetime import date
from typing import Literal
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator
from core_logic import sahams_library as SL
from .. import charts, dasas, modes, service
from .chart_routes import ChartReq, _found
from .main import app

class TajakaReq(ChartReq):
    year: int
    sunrise: bool = False                # Find Tajaka Sunrise Chart
    month: int = Field(0, ge=0, le=12)       # calendar month, 0 = none
    d25: int = Field(0, ge=0, le=12)         # the finer periods, each needs the one above
    h5: int = Field(0, ge=0, le=12)
    m25: int = Field(0, ge=0, le=12)
    m2: int = Field(0, ge=0, le=12)


@app.post("/api/modes/tajaka")
def mode_tajaka(req: TajakaReq):
    try:
        return service.tajaka(req.birth, req.settings, **req.model_dump(include={"year", "month", "d25", "h5", "m25", "m2", "sunrise"}))
    except (ValueError, OverflowError) as e:
        raise HTTPException(422, str(e))


class MomentIn(BaseModel):
    """A date and time typed into a mode's form."""
    year: int
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    hour_local: float = Field(ge=0, lt=24)
    tz_east_hours: float = Field(ge=-14, le=14)

    def on(self, birth: service.BirthIn) -> service.BirthIn:
        """The birth data at this moment (same place), rejecting a date the calendar does not have."""
        if birth.gregorian:
            try:
                date(self.year, self.month, self.day)
            except ValueError as e:
                raise HTTPException(422, "not a date: %s" % e)
        return birth.model_copy(update=self.model_dump())




class TithiPraveshaReq(ChartReq):
    year: int
    month: int = Field(0, ge=0, le=13)   # combo 1003 offers 1st .. 14th; a Tithi Pravesha year holds 12 or 13 lunar months
    day: int = Field(0, ge=0, le=30)     # "Daily chart: Enter 1-30"


@app.post("/api/modes/tithi_pravesha")
def mode_tithi_pravesha(req: TithiPraveshaReq):
    return _found(service.tithi_pravesha, req.birth, req.settings, req.year, req.month, req.day)


@app.post("/api/modes/tithi_pravesha/months")
def mode_tithi_pravesha_months(req: TithiPraveshaReq):
    return _found(service.tithi_pravesha_months, req.birth, req.settings, req.year)


class PraveshaReq(ChartReq):
    when: MomentIn
    kind: Literal["tithi", "nakshatra", "yoga"] = "tithi"
    period: Literal["annual", "monthly", "fortnightly", "daily"] = "annual"
    before: bool = False


@app.post("/api/modes/pravesha")
def mode_pravesha(req: PraveshaReq):
    return _found(service.pravesha, req.birth, req.settings, req.when.on(req.birth), req.kind, req.period, req.before)


class AngularReq(ChartReq):
    when: MomentIn
    a: int = Field(1, ge=1, le=9)
    b: int = Field(2, ge=1, le=9)
    backward: bool = False


@app.post("/api/modes/angular_return")
def mode_angular_return(req: AngularReq):
    return _found(service.angular_return, req.birth, req.settings, req.when.on(req.birth), req.a, req.b, req.backward)


class MundaneReq(ChartReq):
    kind: Literal["solar_year", "solar_month", "lunar_year", "lunar_month", "lunar_day", "fortnight", "ardra", "eclipse",
                  "planet_transit", "conjunction", "stationary", "swearing_in"]
    backward: bool = True
    in_mode: bool = False      # ``birth`` is already a derived chart: move on from it
    body: int = Field(1, ge=0, le=9)
    other: int = Field(7, ge=0, le=9)
    angle: float = Field(0.0, ge=0, lt=360)
    division: Literal[tuple(modes.DIVISIONS)] = "Rasi"
    eclipse: Literal["lunar", "solar", "local"] = "lunar"
    at_max: bool = False
    years: float = Field(1.0, ge=0)       # swearing_in: the period of effect
    days: float = Field(0.0, ge=0)


@app.post("/api/modes/mundane")
def mode_mundane(req: MundaneReq):
    return _found(service.mundane, req.birth, req.settings, **req.model_dump(exclude={"birth", "settings", "name"}))


class StepReq(ChartReq):
    seconds: float = 0.0
    months: int = 0


@app.post("/api/step")
def step(req: StepReq):
    """The same chart so many seconds (or calendar months) on, in its zone: the stepping buttons (33298-33301, 33369-33372)."""
    return _found(service.step, req.birth, req.seconds, req.months)


class ZoneChangeReq(BaseModel):
    birth: service.BirthIn
    zone: float = Field(ge=-14, le=14)


@app.post("/api/timezone")
def change_timezone(req: ZoneChangeReq):
    return _found(service.timezone, req.birth, req.zone)


class TransitModeReq(ChartReq):
    when: MomentIn


@app.post("/api/modes/transit")
def mode_transit(req: TransitModeReq):
    b = req.when.on(req.birth)
    return {"title": "Transit", "natal_dasas": True, "start": modes._when(b.data()), "birth": b.model_dump()}


class ProgressionReq(ChartReq):
    kind: Literal["solar", "nakshatra", "sudarsana", "bhrigu"]
    when: MomentIn      # the form has no zone: its zone is the chart's
    division: Literal[1, 9, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 108] = 1
    dasa: Literal[tuple(dasas.NAK_FAMILY)] = "vimsottari_dasa"
    seed: int = Field(2, ge=0, le=9)      # combo 1013: Lagna .. Ketu


@app.post("/api/modes/progression")
def mode_progression(req: ProgressionReq):
    when = req.when.on(req.birth).model_copy(update={"tz_east_hours": req.birth.tz_east_hours})
    return _found(service.progression, req.birth, req.settings, req.kind, when, req.division, req.dasa, req.seed)


class PrasnaReq(ChartReq):
    kind: Literal["108", "249", "nadi"]
    n: int
    replace: bool = False
    years: float = Field(0.0, ge=0)       # group "Dasa Compression"
    days: float = Field(0.0, ge=0)


@app.post("/api/modes/prasna")
def mode_prasna(req: PrasnaReq):
    return _found(service.prasna, req.birth, req.kind, req.n, req.replace, req.years, req.days)


@app.post("/api/modes/nisheka")
def mode_nisheka(req: ChartReq):
    return _found(service.nisheka, req.birth, req.settings)


class LifecycleReq(ChartReq):
    n: Literal[-1, 1] = 1


@app.post("/api/modes/lifecycle")
def mode_lifecycle(req: LifecycleReq):
    return _found(service.lifecycle, req.birth, req.settings, req.n)


class SearchReq(ChartReq):
    when: MomentIn
    body: int = Field(5, ge=0, le=9)
    offset: float = Field(0.0, ge=0, lt=360)   # degrees
    ahead: bool = False
    target: Literal["planet", "saham", "sign"] = "saham"
    value: int = Field(0, ge=0)                # the planet (0 lagna), saham or sign
    backward: bool = True
    division: Literal[tuple(charts.V.DIVISIONS)] = 1

    @field_validator("value")
    @classmethod
    def _value_in_range(cls, v, info):
        top = {"planet": 9, "saham": len(SL.SAHAMA_NAMES) - 1, "sign": 11}[info.data.get("target", "saham")]
        if v > top:
            raise ValueError("value must be 0 to %d" % top)
        return v


@app.post("/api/modes/special_search")
def mode_special_search(req: SearchReq):
    return _found(service.special_search, req.birth, req.settings, req.when.on(req.birth), req.body, req.offset, req.ahead, req.target,
                  req.value, req.backward, req.division)


@app.get("/api/sahams")
def sahams():
    # in the order of saham_longitudes' results
    return SL.SAHAMA_NAMES[::-1]


class CorrelationReq(ChartReq):
    natal: service.BirthIn
    threshold: float = Field(80.0, ge=0, le=100)
    rule: Literal[0, 1, 2, 3] = 0                 # Parasara, aspects by orb, quadrants, trines and 7th
    orb: float = Field(1.0, gt=0, le=30)
    division: Literal[tuple(charts.V.DIVISIONS)] = 1


@app.post("/api/transit/correlation")
def transit_correlation(req: CorrelationReq):
    return service.correlation(req.natal, req.birth, req.settings, req.threshold, req.rule, req.orb, req.division)


class CalendarReq(ChartReq):
    natal: service.BirthIn
    step: float = Field(1.0, gt=0, le=366)
    count: int = Field(15, ge=1, le=100)
    items: list[Literal["moon", "lagna", "tara", "murthi", "av", "kakshya"]] = ["moon", "lagna", "tara", "murthi", "av", "kakshya"]
    natal_varga: Literal[tuple(charts.V.DIVISIONS)] = 1
    transit_varga: Literal[tuple(charts.V.DIVISIONS)] = 1
    offset: int = Field(0, ge=0, le=4000)       # rows to skip: Starlight's Day by day, a page at a time over up to 10 years


@app.post("/api/transit/calendar")
def transit_calendar(req: CalendarReq):
    return _found(service.calendar, req.natal, req.birth, req.settings, req.step, req.count, req.items, req.natal_varga, req.transit_varga, req.offset)
