"""tradition_routes: part of app (split from one module; see __init__.py). The Traditions tab (server/traditions.py)."""
from typing import Literal
from pydantic import Field
from .. import traditions as TD
from .chart_routes import ChartReq, _found
from .main import app


class TraditionReq(ChartReq):
    part: Literal[TD.PARTS]
    house_system: str = Field("placidus", max_length=20)      # Western: one of TD.HOUSE_SYSTEMS
    male: bool = True                                          # Chinese and Korean luck periods, Ba Zhai
    person: str = Field("", max_length=120)                    # numerology: the name to read
    chaldean: bool = False                                     # numerology: Chaldean rather than Pythagorean values


@app.post("/api/traditions")
def traditions(req: TraditionReq):
    """Traditions > one sub tab's calculations for the chart (``part``)."""
    return _found(TD.compute, req.part, req.birth, req.settings, req.house_system, req.male, req.person, req.chaldean)
