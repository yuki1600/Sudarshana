"""view_routes: part of app (split from one module; see __init__.py)."""
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator
from .. import charts, chakras as chakra_views, service, settings, strengths as strength_views, tables
from .chart_routes import ChartReq, _found
from .main import app

class ChakraOptions(BaseModel):
    show: list[Literal["planets", "yogini", "trisphuta", "upagrahas", "lagnas", "sahams"]] = ["planets"]
    planet_varga: Literal[tuple(charts.V.DIVISIONS)] = 1
    base_point: Optional[int] = Field(None, ge=0, le=12)
    base_division: Literal[tuple(charts.V.DIVISIONS)] = 1
    base_star: Optional[int] = Field(None, ge=0, le=27)
    chart_kind: Optional[int] = None


class ChakrasReq(ChartReq):
    natal: service.BirthIn
    options: ChakraOptions = ChakraOptions()


@app.post("/api/chakras")
def chakras(req: ChakrasReq):
    return service.chakras(req.natal, req.birth, req.settings, req.options.model_dump())


class SpecialPointReq(ChartReq):
    kind: Literal["tara", "special_nakshatra", "tithi", "house", "planet"]
    value: int = Field(0, ge=0, le=35)
    division: Literal[tuple(charts.V.DIVISIONS)] = 1
    point: Literal[tuple(chakra_views.HOUSE_POINTS)] = "Moon"
    star: Optional[str] = None


@app.post("/api/chakras/special_point")
def chakra_special_point(req: SpecialPointReq):
    return service.chakra_special_point(req.birth, req.settings, req.kind, req.value, req.division, req.point, req.star)


class AmsaReq(ChartReq):
    division: Literal[9, 2, 3, 4, 7, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60, 150] = 9


@app.post("/api/amsa")
def amsa(req: AmsaReq):
    return service.amsa(req.birth, req.settings, req.division)


class TableReq(ChartReq):
    view: Literal[tuple(tables.VIEWS)]
    varga: Literal[tuple(charts.V.DIVISIONS)] = 1           # avasthas
    options: Optional[dict] = None                          # the aspect evaluation's options

    @field_validator("options")
    @classmethod
    def _known(cls, v):
        allowed = {"aspecting_varga", "aspected_varga", "aspecting_natal", "aspected_natal", "natal"}
        if v and not set(v) <= allowed:
            raise ValueError("unknown options: %s" % sorted(set(v) - allowed))
        return v


@app.post("/api/table")
def table(req: TableReq):
    return service.table(req.birth, req.settings, req.view, req.varga, req.options)


class KeyInfoReq(ChartReq):
    division: Literal[tuple(charts.V.DIVISIONS)] = 1         # the chart for longitudes


@app.post("/api/key_info")
def key_info(req: KeyInfoReq):
    return service.key_info(req.birth, req.settings, req.name, req.division)


class AshtakavargaReq(ChartReq):
    division: Literal[tuple(charts.V.DIVISIONS)] = 1
    lagna: Optional[int] = Field(None, ge=0, le=11)           # recompute from another sign


class PindaTransitsReq(ChartReq):
    star: int = Field(ge=0, le=26)
    sign: int = Field(ge=0, le=11)


@app.post("/api/pinda-transits")
def pinda_transits(req: PindaTransitsReq):
    return _found(service.pinda_transits, req.birth, req.settings, req.star, req.sign)     # a BCE year: 422


@app.post("/api/ashtakavarga")
def ashtakavarga(req: AshtakavargaReq):
    return service.ashtakavarga(req.birth, req.settings, req.division, req.lagna)


class YogasReq(ChartReq):
    group: int = Field(0, ge=0, le=10)
    division: Literal[tuple(charts.V.DIVISIONS)] = 1
    bhava: bool = False


@app.post("/api/yogas")
def yogas(req: YogasReq):
    return service.yogas(req.birth, req.settings, req.group, req.division, req.bhava)


@app.get("/api/yogas/list")
def yoga_list():
    return strength_views.yoga_list()


class BarsReq(ChartReq):
    kind: Literal["graha", "bhava", "breakup", "vimsopaka", "vaiseshikamsa", "rashmis"] = "graha"
    division: Literal[tuple(charts.V.DIVISIONS)] = 1


@app.post("/api/bars")
def bars(req: BarsReq):
    return service.bars(req.birth, req.settings, req.kind, req.division)


class AspectTableReq(ChartReq):
    division: Literal[tuple(charts.V.DIVISIONS)] = 1
    ref: int = Field(0, ge=0, le=9)


@app.post("/api/aspect_table")
def aspect_table(req: AspectTableReq):
    return service.aspect_table(req.birth, req.settings, req.division, req.ref)


class MatchingReq(ChartReq):
    bride: bool = True           # is the partner the bride? (combo 1005)
    nakshatra: int = Field(0, ge=0, le=26)
    pada: int = Field(0, ge=0, le=3)


@app.post("/api/matching")
def matching(req: MatchingReq):
    return service.matching(req.birth, req.settings, req.bride, req.nakshatra, req.pada)


@app.get("/api/matching/matrix")
def matching_matrix():
    return service.matching_matrix()


class MatchingDetailReq(BaseModel):
    bride_nakshatra: int = Field(0, ge=0, le=26)
    bride_pada: int = Field(0, ge=0, le=3)
    groom_nakshatra: int = Field(0, ge=0, le=26)
    groom_pada: int = Field(0, ge=0, le=3)


@app.post("/api/matching/detail")
def matching_detail(req: MatchingDetailReq):
    return service.matching_detail(req.bride_nakshatra, req.bride_pada, req.groom_nakshatra, req.groom_pada)


class MatchingCompareReq(BaseModel):
    bride: service.BirthIn
    groom: service.BirthIn
    settings: Optional[service.SettingsIn] = None
    bride_name: str = "Bride"
    groom_name: str = "Groom"


@app.post("/api/matching/compare")
def matching_compare(req: MatchingCompareReq):
    return service.matching_compare(req.bride, req.groom, req.settings, req.bride_name, req.groom_name)


class SeedsReq(ChartReq):
    pada_houses: bool = False    # "Pada and 4 padas on either side form the first house"


@app.post("/api/seeds")
def seeds(req: SeedsReq):
    return service.seeds(req.birth, req.settings, req.pada_houses)


class ReportReq(ChartReq):
    title: str = "Natal Chart"
    complete: bool = False
    place: str = ""         # "Delhi, India", the line under the co-ordinates


@app.post("/api/report")
def report(req: ReportReq):
    return _found(service.report, req.birth, req.settings, req.name or "Chart", req.title, req.complete, req.place)


@app.get("/api/tables")
def tables_listing():
    return tables.listing()


@app.get("/api/settings/schema")
def settings_schema():
    return settings.schema()
