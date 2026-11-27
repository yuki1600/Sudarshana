"""dasa_routes: part of app (split from one module; see __init__.py)."""
from typing import Optional
from fastapi import HTTPException
from pydantic import Field
from .. import dasas, modes, service
from .chart_routes import ChartReq
from .mode_routes import MomentIn
from .main import app

class DasaReq(ChartReq):
    key: str = "vimsottari_dasa"
    path: list[int] = []     # indices from the mahadasa down: the period whose divisions are wanted
    event: Optional[service.EventIn] = None    # ``birth`` is a derived chart with this span ..
    natal: Optional[service.BirthIn] = None    # .. of this natal chart
    shift_minutes: float = 0.0


@app.get("/api/dasas")
def dasa_list():
    return dasas.listing()


@app.post("/api/dasa")
def dasa(req: DasaReq):
    return _on_dasa(service.dasa, req, req.path, req.shift_minutes, keyword=True)


@app.post("/api/dasa/best")
def best_dasa(req: ChartReq):
    return service.best_dasa(req.birth, req.settings)


def _on_dasa(fn, req, *a, keyword=False):
    try:
        if keyword:
            return fn(req.birth, req.settings, req.key, a[0], req.event, req.natal, a[1])
        return fn(req.birth, req.settings, req.key, req.event, req.natal, *a)
    except KeyError:
        raise HTTPException(404, "no such dasa: %s" % req.key)
    except (ValueError, IndexError) as e:
        raise HTTPException(422, str(e))


@app.post("/api/dasa/transit_correlation")
def dasa_transit(req: DasaReq):
    return _on_dasa(service.dasa_transit, req, req.path)


@app.post("/api/dasa/sum_of_longitudes")
def sum_of_longitudes(req: DasaReq):
    return _on_dasa(service.sum_longitudes, req, req.path)


@app.post("/api/dasa/entry_chart")
def entry_chart(req: DasaReq):
    return _on_dasa(service.entry_chart, req, req.path)


class LocateReq(DasaReq):
    when: MomentIn
    depth: int = Field(2, ge=1, le=6)


@app.post("/api/dasa/locate")
def locate_event(req: LocateReq):
    b = req.when.on(req.birth).data()
    # the event's moment, on the clock of the dasa's dates
    when = modes._when(modes._local(req.birth.data(), b.jd_ut))
    return _on_dasa(service.locate_event, req, when, req.depth)
