"""chart_routes: part of app (split from one module; see __init__.py)."""
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field
from .. import service
from .main import app

class ChartReq(BaseModel):
    birth: service.BirthIn
    settings: Optional[service.SettingsIn] = None
    name: str = ""


class JhdReq(BaseModel):
    content: str


@app.post("/api/chart")
def chart(req: ChartReq):
    return service.build_chart(req.birth, req.settings)


@app.post("/api/basics")
def basics(req: ChartReq):
    return service.basics(req.birth, req.settings, req.name)


@app.post("/api/strengths")
def strengths(req: ChartReq):
    return service.strengths(req.birth, req.settings)


class GrahaInsightsReq(ChartReq):
    division: int = Field(1, ge=1, le=144)     # the varga whose signs the facts are read in (Starlight's top left chart)


@app.post("/api/graha_insights")
def graha_insights(req: GrahaInsightsReq):
    return service.graha_insights(req.birth, req.settings, req.division)


@app.post("/api/longevity")
def longevity(req: ChartReq):
    return _found(service.longevity, req.birth, req.settings)


class HousesReq(ChartReq):
    ref: int = Field(0, ge=0, le=9)      # the reference for the houses


@app.post("/api/houses")
def houses(req: HousesReq):
    return service.houses(req.birth, req.settings, req.ref)


class BhavaReadingReq(HousesReq):
    house: int = Field(1, ge=1, le=12)


@app.post("/api/lore/bhava_reading")
def lore_bhava_reading(req: BhavaReadingReq):
    """A bhava read for the chart: its rashi, lord, cusp and the cusp's nakshatra, the grahas in and aspecting it, its strength and
    BPHS 11's tests, and the classics' readings of each (server/lore.py bhava_reading); ``ref`` counts the bhavas from a graha."""
    return service.bhava_reading(req.birth, req.settings, req.house, req.ref)


@app.post("/api/kp")
def kp(req: HousesReq):
    return service.kp(req.birth, req.settings, req.ref)




def _found(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except (ValueError, OverflowError) as e:   # a search or a date out of range: the form says so
        raise HTTPException(422, str(e))
