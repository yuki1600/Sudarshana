"""file_routes: part of app (split from one module; see __init__.py)."""
import gzip
import json
import os
from datetime import datetime, timezone
import swisseph as swe
from typing import Literal, Optional
from fastapi import HTTPException, Path, Request, Response
from pydantic import BaseModel, Field
from core_logic import ephemeris as E, jhd_io
from .. import ini, lore, mundane_data, places, remedies, rodden, service, settings
from ..jsonenc import to_jsonable
from .chart_routes import ChartReq, JhdReq
from .main import app

@app.get("/api/countries")
def list_countries():
    return places.countries()


@app.get("/api/states")
def list_states(country: str):
    return places.states(country)


@app.get("/api/places")
def search_places(q: str, limit: int = 20, country: str | None = None, state: str | None = None):
    return places.search(q, max(1, min(limit, 100)), country, state)   # the typeahead asks for 20; no one gets the whole atlas


VS_FORMAT = "sudarshana-chart"   # the "format" key of a .vs file (.s before 2026-11-26): Sudarshana's own chart file, JSON


@app.post("/api/jhd/parse")
def parse_jhd(req: JhdReq):
    """A chart file, either kind: a .vs file (JSON, or an older .s) or a .jhd (lines of text)."""
    if req.content.lstrip().startswith("{"):
        try:
            d = json.loads(req.content)
            if d.get("format") != VS_FORMAT:
                raise ValueError("no \"format\": \"%s\"" % VS_FORMAT)
            b = service.BirthIn.model_validate(d["birth"])
            meta = d.get("meta") or {}
            if not isinstance(meta, dict):
                raise ValueError("meta is not an object")
        except (ValueError, KeyError, TypeError, AttributeError) as e:   # pydantic's ValidationError is a ValueError
            raise HTTPException(422, "not a readable .vs file: %s" % e)
        return {"birth": to_jsonable(b.data()), "parsed": {**meta, "name": str(d.get("name") or ""), "notes": str(d.get("notes") or "")}}
    try:
        parsed = jhd_io.parse_jhd_string(req.content)
    except (ValueError, KeyError, IndexError) as e:
        raise HTTPException(422, "not a readable .jhd file: %s" % e)
    b = jhd_io.to_birth_data(parsed)
    return {"birth": to_jsonable(b), "parsed": {**to_jsonable(parsed), "gender": parsed["field18"]}}


class ZoneReq(BaseModel):
    place: dict            # a row of /api/places
    year: int
    month: int
    day: int
    hour: float            # local standard time


@app.post("/api/zone")
def zone(req: ZoneReq):
    """Zone (east positive) and DST flag for a place on a local date.

    GeoNames hits carry an IANA ``timezone`` (historical transitions via the tz database).
    """
    try:
        tz, is_dst = places.zone_at(req.place, req.year, req.month, req.day, req.hour)
    except (TypeError, KeyError, ValueError) as e:
        raise HTTPException(422, "not a place: %s" % e)
    return {"tz_east_hours": tz, "dst": is_dst}


class IniReq(BaseModel):
    content: str


@app.post("/api/ini/parse")
def ini_parse(req: IniReq):
    """Import preferences: the options a preferences .ini sets, as the Settings screen keeps them."""
    return ini.parse(req.content)


class IniExportReq(BaseModel):
    settings: Optional[service.SettingsIn] = None


@app.post("/api/ini/export")
def ini_export(req: IniExportReq):
    return {"content": ini.write(req.settings or service.SettingsIn())}


class ExportReq(BaseModel):
    birth: service.BirthIn
    city: str = ""
    country: str = ""
    dst: bool = False
    tz_standard_east: Optional[float] = None
    tz_dst_east: Optional[float] = None
    gender: int = Field(0, ge=0, le=2)      # line 18 of a .jhd file: Unknown, Male, Female
    format: Literal["jhd", "vs", "s"] = "jhd"   # "s": the .vs format's name before 2026-11-26
    name: str = ""                          # .vs only, with state and notes: a .jhd has no line for them
    state: str = ""
    notes: str = ""


@app.post("/api/jhd/export")
def export_jhd(req: ExportReq):
    b = req.birth
    if req.format in ("vs", "s"):
        tz = b.tz_east_hours
        return {"content": json.dumps({
            "format": VS_FORMAT, "version": 1, "app": "Sudarshana",
            "saved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "name": req.name,
            "birth": b.model_dump(exclude={"adjust"}),
            "meta": {"city": req.city, "state": req.state, "country": req.country, "dst": req.dst,
                     "tz_standard_east": tz if req.tz_standard_east is None else req.tz_standard_east,
                     "tz_dst_east": tz if req.tz_dst_east is None else req.tz_dst_east, "gender": req.gender},
            "notes": req.notes,
        }, indent=2, ensure_ascii=False) + "\n"}
    chart = {**b.model_dump(exclude={"adjust"}), "city": req.city, "country": req.country, "dst": req.dst,
             "tz_standard_east": req.tz_standard_east if req.tz_standard_east is not None else b.tz_east_hours,
             "tz_dst_east": req.tz_dst_east if req.tz_dst_east is not None else b.tz_east_hours,
             "atmosphere": {"pressure": b.pressure_hpa, "temperature": b.temperature_c}, "field18": req.gender}
    return {"content": jhd_io.serialize_to_jhd(chart)}



@app.get("/api/remedies/topics")
def remedies_topics():
    """Primary (Śrī Vaiṣṇava) and Secondary (BPHS) remedy catalogues."""
    return remedies.topics()


@app.post("/api/remedies/chart")
def remedies_chart(req: ChartReq):
    """Birth-condition flags for BPHS Ch. 85–96 filtering."""
    return remedies.chart_flags(req.birth, req.settings)


def _gzipped(body: bytes, request: Request) -> Response:
    """JSON kept gzipped: sent as it is to a client that takes gzip (every browser; the middleware leaves it be), unpacked for one that doesn't."""
    if "gzip" in request.headers.get("accept-encoding", ""):
        return Response(body, media_type="application/json", headers={"Content-Encoding": "gzip", "Vary": "Accept-Encoding"})
    return Response(gzip.decompress(body), media_type="application/json")


@app.get("/api/mundane/data/{name}")
def mundane_dataset(name: str, request: Request):
    """One of the Research tab's databases, sent when its tab is first opened."""
    if name not in mundane_data.SETS:
        raise HTTPException(404, "no such mundane database")
    return _gzipped(mundane_data.payload(name), request)


@app.get("/api/mundane/summary")
def mundane_summary():
    """The Research Overview's cards: each database's size, span, top kinds and countries and notable records, without the records."""
    return mundane_data.summary()


class PatternsReq(BaseModel):
    ids: list[str] = Field(max_length=20000)
    settings: Optional[service.SettingsIn] = None


@app.post("/api/mundane/patterns")
def mundane_patterns(req: PatternsReq):
    """The chosen events' signs, nakshatras, tithis, weekdays, houses and eclipse distances, and a control sample over the same years."""
    return mundane_data.patterns(req.ids, req.settings)


@app.get("/api/calculations/topics")
def calculations_topics():
    """Structured calculation explainers for the Calculations tab."""
    return remedies.calculation_topics()


@app.get("/api/colors")
def colors():
    """Preferences > Colors to be used: the 125 colours and their groups."""
    with open(os.path.join(os.path.dirname(__file__), "..", "..", "data", "colours.json"), encoding="utf-8") as f:
        data = json.load(f)
    return {"groups": data["groups"], "colours": data["colours"]}


@app.get("/api/lore/nakshatra/{n}")
def lore_nakshatra(n: int = Path(ge=1, le=27)):
    """A nakshatra's pop-up: what Dr. Pai's Cosmic Insights says of it (data/lore/nakshatras.json), and its padas."""
    return lore.nakshatra(n)


@app.get("/api/lore/graha/{ab}")
def lore_graha(ab: Literal["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"]):
    """A graha's pop-up: what the classics say of it (data/lore/grahas.json), its relations and the BPHS slokas on it."""
    return lore.graha(ab)


@app.get("/api/lore/rashi/{n}")
def lore_rashi(n: int = Path(ge=1, le=12)):
    """A rashi's pop-up: what the classics say of it (data/lore/rashis.json), its nakshatras and the grahas' dignities in it."""
    return lore.rashi(n)


@app.get("/api/lore/bhava/{n}")
def lore_bhava(n: int = Path(ge=1, le=12)):
    """A bhava's pop-up, read for no chart: what the classics say of it (data/lore/bhavas.json) and BPHS on it and its lord."""
    return lore.bhava(n)



SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_charts")


@app.get("/api/sky")
def sky():
    """The nine grahas at this moment, for the sign-in page; public, since the sky is no one's data.
    The app's own defaults (Pushya-paksha ayanamsa), so the sign-in chart agrees with a new chart made now."""
    n = datetime.now(timezone.utc)
    jd = swe.julday(n.year, n.month, n.day, n.hour + n.minute / 60 + n.second / 3600)
    cfg = settings.config(settings.SettingsIn(ayanamsa="PUSHYA_PAKSHA", house_type=3))
    return {k: {"lon": p["lon"], "retrograde": p["retrograde"]} for k, p in E.planet_positions(jd, cfg).items()}


@app.get("/api/samples")
def samples():
    if not os.path.isdir(SAMPLES):
        return []
    return sorted(f[:-4] for f in os.listdir(SAMPLES) if f.endswith(".jhd"))


@app.get("/api/samples/{name}")
def sample(name: str):
    if name not in samples():  # only names from the listing: no path traversal
        raise HTTPException(404, "no such sample chart")
    with open(os.path.join(SAMPLES, name + ".jhd"), encoding="utf-8", errors="ignore") as f:
        return {"name": name, "content": f.read()}


@app.get("/api/rodden")
def rodden_charts(request: Request):
    """Open chart's Rodden list: every AA- and A-rated library chart, [id, name, rating, year, month, day, hour, place]."""
    return _gzipped(rodden.listing(), request)


@app.get("/api/rodden/{id}")
def rodden_chart(id: int = Path(ge=0, lt=2 ** 63)):     # past SQLite's integers: a 422, not an OverflowError
    c = rodden.chart(id)
    if not c:
        raise HTTPException(404, "no such Rodden chart")
    return c
