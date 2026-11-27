"""One chart object over the engines: {birth, settings} -> chart dict (TODO section 2, "Chart API")."""
import dataclasses
import functools
import json
from datetime import datetime, timedelta
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from core_logic import shadbala as SBE
from core_logic import compatibility as C, conditional_dasas as CD, ephemeris as E, natal_chart as N, sign_strength as SS, varga_charts as V

from . import astrocarto as AC, basics as B, lore as LO, chakras as CK, charts as CH, dasas as D, festivals as FE, finance as FN, houses as HS, insights as IN, jamakkol as JM, longevity as LG, miscellany as MI, modes as M, muhurta as MU, report as RP, settings as SET, strengths as ST, tables as TB, timeline as TL, transits as TR, windows as W
from .jsonenc import to_jsonable

SettingsIn = SET.SettingsIn


class AdjustIn(BaseModel):
    """Moves a chart's bodies, for the charts that are not a moment; see basics.adjusted. A mode's birth carries it, so every view shows it."""
    base: Optional[dict] = None       # birth data of the chart whose longitudes this one takes
    arc: float = 0.0
    lons: dict[str, float] = {}
    lagna: Optional[float] = None
    prasna_lagna: Optional[float] = None
    muntha: Optional[float] = None           # a Tajaka chart's Muntha, and its sign in each varga (varga_charts.DIVISIONS order)
    muntha_signs: Optional[list[int]] = None


class BirthIn(BaseModel):
    year: int                  # astronomical: 0 is 1 BCE
    month: int = Field(ge=1, le=12)
    day: int
    hour_local: float          # decimal hours, local (zone) time
    tz_east_hours: float       # east positive
    longitude_east: float
    latitude: float = Field(ge=-90.0, le=90.0)
    altitude_m: float = 0.0
    gregorian: bool = True
    place: str = ""
    pressure_hpa: float = 1013.25
    temperature_c: float = 20.0
    adjust: Optional[AdjustIn] = None

    @model_validator(mode="after")
    def _real_day(self):
        # a day the month doesn't have (30 February) was cast silently as a later date
        leap = self.year % 4 == 0 and (not self.gregorian or self.year % 100 != 0 or self.year % 400 == 0)
        if not 1 <= self.day <= (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[self.month - 1]:
            raise ValueError("no day %d in month %d of %d" % (self.day, self.month, self.year))
        return self

    def data(self) -> E.BirthData:
        return E.BirthData(**self.model_dump(exclude={"adjust"}))


@functools.lru_cache(maxsize=256)
def _raw(birth_json: str, settings_json: str):
    b = BirthIn.model_validate_json(birth_json)
    birth = b.data()
    s = SettingsIn.model_validate_json(settings_json)
    cfg = SET.config(s)
    ch = E.build_chart(birth, cfg, "PORPHYRY")
    ch["outer"] = {n: x["lon"] for n, x in E.planet_positions(birth.jd_ut, cfg, birth, include_outer=True).items() if n in CH.OPTIONAL["outer"]}    # the Surya Siddhanta has none
    ch["nakshatra_correction"] = -E.ayanamsa_value(birth.jd_ut, dataclasses.replace(cfg, ayanamsa="CUSTOM_STAR", custom_star=",alVir", custom_star_longitude=180.0, custom_star_fixed_plane=False)) if s.sidereal_nakshatras_in_tropical and s.ayanamsa == "TROPICAL" else 0.0
    if cfg.topocentric or cfg.apparent_refraction:
        # shortcut: only the chart's positions use the place; the engines' searches (panchanga, dasa years, events) call planet_positions without one, so they stay geocentric and unrefracted
        cfg = dataclasses.replace(cfg, topocentric=False, apparent_refraction=False)
    if b.adjust:
        base = _raw(json.dumps(b.adjust.base), settings_json)[2] if b.adjust.base else None
        ch = B.adjusted(ch, b.adjust, base)
    return birth, cfg, ch, s


class EventIn(BaseModel):
    """How the dasas of a derived chart fit into its span; a mode's ``event``, sent back unchanged."""
    kind: Literal[1, 2, 5]
    name: str = ""
    span_days: float = Field(gt=0)
    counts: list[int] = []    # Tajaka: the years, months .. after birth


def _key(birth: BirthIn, settings: Optional[SettingsIn]):
    # the cache key is the request itself, so scrubbing back to an earlier time is free
    s = settings or SettingsIn()
    SET.apply_process_wide(s)
    return birth.model_dump_json(), s.model_dump_json()


def build_chart(birth: BirthIn, settings: Optional[SettingsIn] = None) -> dict:
    return to_jsonable(_raw(*_key(birth, settings))[2])


def basics(birth: BirthIn, settings: Optional[SettingsIn] = None, name: str = "") -> dict:
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(B.basics(b, ch, cfg, s, name))


def _typed(s, key):
    """What the dasa's Options dialog typed over the strengths; its Ayur Narayana uses Rahu Ta / Sc, Ketu Le / Aq (apply_process_wide puts them back on the next request)."""
    per = s.per_dasa.get(key, {})
    if per.get("option") == 3:
        SS.EXALTATION[8], SS.EXALTATION[9], SS.DEBILITATION[8], SS.DEBILITATION[9] = 1, 4, 7, 10
    return SS.typed_strengths(per.get("typed"))


@functools.lru_cache(maxsize=128)
def _dasa(birth_json: str, settings_json: str, key: str):
    """The mahadasas of one dasa for one chart; dating them is the slow part (a Sun search per boundary)."""
    birth, cfg, ch, s = _raw(birth_json, settings_json)
    jc = SET.jchart(ch, E.day_lords(birth, cfg, **SET.day_kw(s)), s)
    to_date = SET.year_mapper(birth, cfg, s)
    kw = D.options(key, s)
    with _typed(s, key):
        return jc, to_date, D.BY_KEY[key].build(jc, to_date, **kw), kw, s.year_definition


@functools.lru_cache(maxsize=128)
def _event_dasa(birth_json: str, settings_json: str, natal_json: str, event_json: str, key: str):
    birth, cfg, ch, s = _raw(birth_json, settings_json)
    natal_birth, _, natal_ch, _ = _raw(natal_json, settings_json)
    jc = SET.jchart(ch, E.day_lords(birth, cfg, **SET.day_kw(s)), s)
    natal = SET.jchart(natal_ch, E.day_lords(natal_birth, cfg, **SET.day_kw(s)), s)
    with _typed(s, key):
        to_date, mds, definition, kw = M.fit_dasa(D.BY_KEY[key], jc, natal, birth, cfg, s, EventIn.model_validate_json(event_json))
    return jc, to_date, mds, kw, definition


def _dasa_any(birth, settings, key, event, natal):
    if key not in D.BY_KEY:
        raise KeyError(key)
    if event is None:
        return _dasa(*_key(birth, settings), key)
    keys = _key(birth, settings)
    return _event_dasa(*keys, _key(natal or birth, settings)[0], event.model_dump_json(), key)


def dasa(birth: BirthIn, settings: Optional[SettingsIn], key: str, path: list,
         event: Optional[EventIn] = None, natal: Optional[BirthIn] = None, shift_minutes: float = 0.0) -> dict:
    """The natal dasa of ``birth``, or with ``event`` and ``natal`` the dasa of the derived chart ``birth``. ``shift_minutes``: Shift dasa dates."""
    jc, to_date, mds, kw, definition = _dasa_any(birth, settings, key, event, natal)
    tajaka = event is not None and event.kind == M.TAJAKA
    with _typed(settings or SettingsIn(), key):
        lv = D.level(D.BY_KEY[key], jc, to_date, mds, path, tajaka, kw)
    if shift_minutes:
        shift = timedelta(minutes=shift_minutes)
        lv["periods"] = [{**p, "start": p["start"] + shift, "end": p["end"] + shift} for p in lv["periods"]]
    return {**to_jsonable(lv), "years": SET.YEARS[definition]}


def longevity(birth: BirthIn, settings: Optional[SettingsIn] = None) -> list:
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(LG.sections(b, ch, cfg, s, lambda key: _dasa_any(birth, settings, key, None, None)))


def best_dasa(birth, settings):
    """The nakshatra dasa that suits the chart best (core_logic/conditional_dasas.py)."""
    b, cfg, ch, s = _raw(*_key(birth, settings))
    jc = SET.jchart(ch, E.day_lords(b, cfg, **SET.day_kw(s)), s)
    sb = E.chart_shadbala(b, ch, cfg)["planets"]
    return to_jsonable(CD.best_dasa(jc, [False] + [bool(ch["retrograde"].get(p)) for p in B.PLANETS], s.combustion_by_motion,
                                    [0.0] + [sb[p]["percent"] for p in B.PLANETS[:7]], s.combustion_classical))


def _on_dasa(fn, birth, settings, key, event, natal, *a):
    jc, to_date, mds, kw, _ = _dasa_any(birth, settings, key, event, natal)
    with _typed(settings or SettingsIn(), key):
        return to_jsonable(fn(D.BY_KEY[key], jc, to_date, mds, *a, kw))


def locate_event(birth, settings, key, event, natal, when: datetime, depth):
    return _on_dasa(W.locate, birth, settings, key, event, natal, when, depth)


def sum_longitudes(birth, settings, key, event, natal, path):
    return {"text": _on_dasa(W.sum_longitudes, birth, settings, key, event, natal, path)}


def dasa_transit(birth, settings, key, event, natal, path):
    b, cfg, _, _ = _raw(*_key(birth, settings))
    jc, to_date, mds, kw, _ = _dasa_any(birth, settings, key, event, natal)
    with _typed(settings or SettingsIn(), key):
        return to_jsonable(W.dasa_transit(D.BY_KEY[key], jc, to_date, mds, path, b, cfg, kw))


def entry_chart(birth, settings, key, event, natal, path):
    """Entry chart of this period: the chart at its start, its dasas fitted into the period."""
    b, _, _, _ = _raw(*_key(birth, settings))
    jc, to_date, mds, kw, _ = _dasa_any(birth, settings, key, event, natal)
    d = D.BY_KEY[key]
    with _typed(settings or SettingsIn(), key):
        trail = W.period_at(d, jc, to_date, mds, path, kw)
    p = trail[-1]
    return to_jsonable(M.entry_chart(b, p["start"], p["end"], "Entry %s %s" % (d.label(p), W.LEVEL_ABBR[len(path) - 1])))


def aspect_table(birth, settings, d, ref):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(W.aspect_table(b, ch, cfg, s, d, ref))


def matching(birth, settings, bride, nak, pada):
    _, _, ch, _ = _raw(*_key(birth, settings))
    return to_jsonable(W.matching(ch, bride, nak, pada))


def matching_matrix():
    return to_jsonable(W.matching_matrix())


def matching_detail(bride_nak, bride_pada, groom_nak, groom_pada):
    return to_jsonable(W.matching_detail(bride_nak, bride_pada, groom_nak, groom_pada))


def matching_compare(bride, groom, settings, bride_name="Bride", groom_name="Groom"):
    bb, bcfg, bch, bs = _raw(*_key(bride, settings))
    gb, gcfg, gch, gs = _raw(*_key(groom, settings))
    bsb, gsb = E.chart_shadbala(bb, bch, bcfg), E.chart_shadbala(gb, gch, gcfg)
    out = W.matching_compare(bch, gch, bride_name, groom_name, bsb, gsb,
                             HS.mars_bhavas(bb, bch, bcfg, bs), HS.mars_bhavas(gb, gch, gcfg, gs), bs.aspect_parasara)
    out["grid"]["karakas"] = [b["karakas"]["bphs"] for b in LO._load("bhavas.json")["bhavas"]]     # each bhava's karaka (BPHS 32.31-34), as Lore gives it
    for who, (b, cfg, ch, s) in (("girl", (bb, bcfg, bch, bs)), ("boy", (gb, gcfg, gch, gs))):     # the Strength area's avasthas, vimsopaka and vaiseshikamsa, as the Strengths tab gives them
        av, vim = TB._avasthas(b, ch, cfg, s), {r["name"]: r for r in ST.vimsopaka_of(ch, s)}
        vai = ST.vaiseshikamsa_of(ch, s, E.day_lords(b, cfg, **SET.day_kw(s)))
        names = B._tables()[0]
        amsa = lambda n, table: names[table][n - 2].strip().split("-", 1)[-1] if n >= 2 else ""  # noqa: E731
        bh = HS._bhavas(b, ch, cfg, s, 0)      # each bhava's cusp in the chosen house system: its middle, or its start
        ak = ST.ashtakavarga_of(ch, s)
        sav = [x + l for x, l in zip(ak["sav"], ak["bav"][0])]     # each sign's SAV with the lagna's own row added (8 rows), Aries first
        lajj = {r["name"]: r["avasthas"]["Lajjitadi"] for r in IN.graha_insights(b, ch, cfg, s, 1)}     # as the Strengths tab's Lajjitadi
        for h, row in zip(bh, out["grid"][who]["houses"]):
            row["cusp"] = round(h[1 if s.house_cusp_in_middle else 0] % 360.0, 4)
            row["sav"] = sav[(ch["lagna_sign"] + row["house"] - 1) % 12]
        for p, x in out["grid"][who]["planets"].items():
            if p in vim:
                x.update(age=av[p]["age_name"], alertness=av[p]["parashara_alertness_name"], mood=av[p]["parashara_mood_names"], vimsopaka=vim[p]["shodasa"],
                         activity=av[p]["activity_name"], lajjitadi=lajj.get(p, ""),
                         vaiseshikamsa={"dasa": amsa(vai[p]["dasa"], "vaiseshikamsa_dasa"), "shodasa": amsa(vai[p]["shodasa"], "vaiseshikamsa_shodasa"),
                                        "dasa_n": vai[p]["dasa"], "shodasa_n": vai[p]["shodasa"]})
    # each partner's grahas on the other's grahas and bhava cusps (BPHS 26), as the Aspects tab's table: the aspecting graha's own
    # marks and relation from its chart, the values on the other's longitudes and cusps, a bhava's colour the aspecting graha's
    # relation to the lord of that bhava's sign
    def cross(b, cfg, ch, s, dst, who):
        t = W.aspect_table(b, ch, cfg, s, 1, 0)
        signs = [ch["planet_signs"][p] for p in B.PLANETS]
        compound, scale = SBE.compound_relationships(signs), s.aspect_full / 100.0
        on, cusps = [dst["planet_longitudes"][p] for p in B.PLANETS], [h["cusp"] for h in out["grid"][who]["houses"]]
        for i, r in enumerate(t["rows"]):
            val = lambda x: int(SBE.aspect_value(x - ch["planet_longitudes"][B.PLANETS[i]], i + 1, s.aspect_parasara) * scale)  # noqa: E731
            r.update(cells=[val(x) for x in on], houses=[val(x) for x in cusps],
                     lord_class=[compound[i][SS.SIGN_LORDS[int(x % 360.0 // 30)] - 1] for x in cusps])
        return t
    out["cross"] = {"girl": cross(bb, bcfg, bch, bs, gch, "boy"), "boy": cross(gb, gcfg, gch, gs, bch, "girl")}     # "girl": her grahas on him
    girl, boy = (_match_side(birth, settings, sb, out["grid"][who]["kuja"]) for birth, sb, who in ((bride, bsb, "girl"), (groom, gsb, "boy")))
    out["factors"] = C.match_factors(girl, boy, out["match"])
    out["dasas"] = {"girl": C.marriage_dasas(girl, "girl"), "boy": C.marriage_dasas(boy, "boy")}
    return to_jsonable(out)


def _match_side(birth, settings, sb, kuja):
    """One partner's chart as the matching's factors read it (core_logic/compatibility/factors.py), in the user's varga
    options and chara karaka scheme; every Vimsottari mahadasa with its antardasas."""
    b, cfg, ch, s = _raw(*_key(birth, settings))
    opt = SET.varga_options(s)
    lons = {p: ch["planet_longitudes"][p] for p in B.PLANETS}
    nine = [ch["lagna_lon"]] + [lons[p] for p in B.PLANETS]
    signs = [int(x // 30) for x in nine]
    vs = lambda d: {n: V.varga_sign(x, d, opt) for n, x in zip(["Lagna"] + B.PLANETS, nine)}  # noqa: E731
    slots = dict(zip(B.KARAKA_SLOTS, N.chara_karaka_slots(nine, signs, s.chara_karakas)))
    ul = SS.bhava_arudhas(signs, nine, s.arudha_exceptions_bhava, s.arudha_nodes)[11]
    key = "vimsottari_dasa"
    jc, to_date, mds, kw, _ = _dasa(*_key(birth, settings), key)
    full = lambda short: next(p for p in B.PLANETS if p.startswith(short[:3]))     # "Jup" -> "Jupiter"  # noqa: E731
    label = lambda m: full(D.BY_KEY[key].label(m))  # noqa: E731
    periods = [(label(m), m["start"], m["end"], [(full(a["label"]), a["start"], a["end"]) for a in D.level(D.BY_KEY[key], jc, to_date, mds, [i], False, kw)["periods"]])
               for i, m in enumerate(mds)]
    return {"lons": lons, "lagna_lon": ch["lagna_lon"], "sb": sb, "d9": vs(9), "d7": vs(7), "ul": ul,
            "dk": (["Lagna"] + B.PLANETS)[slots["DK"]], "kuja": kuja, "periods": periods, "now": datetime.now()}


def seeds(birth, settings, pada_houses):
    _, _, ch, _ = _raw(*_key(birth, settings))
    return to_jsonable(W.seeds(ch, pada_houses))


def report(birth, settings, name, title, complete, place=""):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return {"text": (RP.complete if complete else RP.basic)(b, ch, cfg, s, name, title, place)}


def _view(fn, birth: BirthIn, settings: Optional[SettingsIn]) -> dict:
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(fn(b, ch, cfg, s))


def strengths(birth, settings=None):
    return _view(ST.strengths, birth, settings)


def graha_insights(birth, settings=None, d=1):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(IN.graha_insights(b, ch, cfg, s, d))


def houses(birth, settings=None, ref=0):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(HS.houses(b, ch, cfg, s, ref))


def bhava_reading(birth, settings=None, house=1, ref=0):
    """A bhava's pop-up for this chart (lore.bhava_reading), in the user's own settings."""
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(LO.bhava_reading(b, ch, cfg, s, house, ref))


def kp(birth, settings=None, ref=0):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(HS.kp(b, ch, cfg, s, ref))


def timezone(birth, zone):
    """Change timezone: the same moment on another clock."""
    b = birth.data()
    moved = M._local(dataclasses.replace(b, tz_east_hours=zone), b.jd_ut)
    return to_jsonable({"birth": dataclasses.asdict(moved), "start": M._when(moved)})


def tajaka(birth: BirthIn, settings: Optional[SettingsIn], **period) -> dict:
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(M.tajaka(b, cfg, ch, s, **period))


def _mode(fn, birth: BirthIn, settings: Optional[SettingsIn], *a, **kw) -> dict:
    b, cfg, _, _ = _raw(*_key(birth, settings))
    return to_jsonable(fn(b, cfg, *a, **kw))


def _mode_s(fn, birth: BirthIn, settings: Optional[SettingsIn], *a, **kw) -> dict:
    b, cfg, _, s = _raw(*_key(birth, settings))
    return to_jsonable(fn(b, cfg, s, *a, **kw))


def tithi_pravesha(birth, settings, year, month=0, day=0):
    return _mode_s(M.tithi_pravesha, birth, settings, year, month, day)


def tithi_pravesha_months(birth, settings, year):
    return _mode_s(M.tithi_pravesha_months, birth, settings, year)


def pravesha(birth, settings, when: BirthIn, kind, period, before=False):
    return _mode(M.pravesha, birth, settings, when.data().jd_ut, kind, period, before)


def angular_return(birth, settings, when: BirthIn, a, b, backward):
    return _mode(M.angular_return, birth, settings, when.data().jd_ut, a, b, backward)


def _with_chart(fn, birth, settings, *a):
    b, cfg, ch, _ = _raw(*_key(birth, settings))
    return to_jsonable(fn(b, cfg, ch, *a))


def step(birth, seconds, months=0):
    b = birth.data()
    moved = M.add_months(b, months) if months else M._local(b, b.jd_ut + seconds / 86400.0)
    return to_jsonable({"birth": dataclasses.asdict(moved), "start": M._when(moved)})


def table(birth, settings, view, varga=1, options=None):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    if view == "aspects" and options:
        natal = options.get("natal")
        natal_ch = _raw(*_key(BirthIn.model_validate(natal), settings))[2] if natal else None
        return to_jsonable(TB.aspect_evaluation(b, ch, cfg, s, natal_ch, **{k: v for k, v in options.items() if k != "natal"}))
    if view in TB.VARGA_VIEWS:
        return to_jsonable(TB.VIEWS[view](b, ch, cfg, s, varga))
    return to_jsonable(TB.VIEWS[view](b, ch, cfg, s))


def key_info(birth, settings, name, d):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(B.points_table(ch, s, d, B.user_points(b, ch, cfg, s), B.extra_points(ch, s, d, b, cfg)))


def ashtakavarga(birth, settings, d, lagna):
    _, _, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(ST.ashtakavarga_view(ch, s, d, lagna))


def pinda_transits(birth, settings, star, sign):
    """Jupiter's and Saturn's last visits to a nakshatra and rasi from the sodhya pindas, with the MD-ADs then."""
    b, cfg, _, _ = _raw(*_key(birth, settings))
    jc, to_date, mds, kw, _ = _dasa_any(birth, settings, "vimsottari_dasa", None, None)
    vim = D.BY_KEY["vimsottari_dasa"]
    with _typed(settings or SettingsIn(), "vimsottari_dasa"):
        rule = vim.rule(jc, kw) if vim.rule else None
    pds = functools.lru_cache(None)(lambda i, k: D.J.sub_periods(mds, to_date, [i, k], rule))
    now, last = datetime.utcnow(), mds[-1]["end"]     # the dasas run ~120 years: past them there is no MD-AD to name
    end = min(E.julian_day_ut(now.year, now.month, now.day, now.hour + now.minute / 60.0, True),
              E.julian_day_ut(last.year, last.month, last.day, last.hour + last.minute / 60.0 - b.tz_east_hours, b.gregorian))
    return ST.pinda_transits(b, cfg, mds, pds, star, sign, end)


def yogas(birth, settings, group, d, bhava=False):
    """``bhava``: house placements and house lords of the D-1 by the lagna's houses in the chosen house system."""
    b, cfg, ch, s = _raw(*_key(birth, settings))
    bh = HS._bhavas(b, ch, cfg, s, 0) if bhava and d == 1 else None
    return to_jsonable(ST.yogas_of(ch, group, d, bh, s.house_cusp_in_middle))


def bars(birth, settings, kind, d):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(ST.bar_group(b, ch, cfg, s, kind, d))


def _with_houses(b, ch, cfg, s, spec):
    """``ch`` with the houses the bhava chart needs (the cached chart is shared, so a copy)."""
    return {**ch, "bhavas": HS._bhavas(b, ch, cfg, s, s.bhava_ref)} if CH.needs_houses(s, spec) else ch


def panel(birth, settings, spec, view, optional, natal=None):
    """``natal``: for a transit's bhava chart, its grahas are placed in the natal chart's houses (its cusps and reference), not the transit's own."""
    b, cfg, ch, s = _raw(*_key(birth, settings))
    ch = _with_houses(b, ch, cfg, s, spec)
    sign = None
    if natal is not None and spec.kind == "bhava":
        nb, ncfg, nch, _ = _raw(*_key(natal, settings))
        sign = CH.sign_of(_with_houses(nb, nch, ncfg, s, spec), s, spec)
    user_points = B.user_points(b, ch, cfg, s)
    karakas = None
    if view == "chara_karaka":
        nine = [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in B.PLANETS]
        slots = N.chara_karaka_slots(nine, [int(x // 30) for x in nine], s.chara_karakas)
        karakas = {B.PLANET_ABBR[i - 1]: k for k, i in zip(B.KARAKA_SLOTS, slots) if i}
    return to_jsonable(CH.panel(ch, s, spec, view, optional, karakas, user_points, sign=sign))


def jamakkol(birth, settings, kind="rasi"):
    """``kind`` "bhava": the houses from the lagna (the house type set, whatever the bhava chart's reference), not from Udayam."""
    if kind == "rasi":
        b, cfg, ch, _ = _raw(*_key(birth, settings))
        return to_jsonable(JM.chart(b, cfg, ch))
    settings = (settings or SettingsIn()).model_copy(update={"bhava_ref": 0})
    b, cfg, ch, s = _raw(*_key(birth, settings))
    spec = CH.ChartSpec(kind="bhava", d=1)
    return to_jsonable(JM.chart(b, cfg, ch, CH.sign_of(_with_houses(b, ch, cfg, s, spec), s, spec)))


def chart_ask(birth, settings, spec, question, kind, planet, rasi):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    ch = _with_houses(b, ch, cfg, s, spec)
    if question == "highlight":
        return {"signs": CH.highlight(ch, s, spec, kind, planet, rasi)}
    if question == "relationships":
        return {"classes": CH.relationships(ch, s, spec, kind, planet), "names": CH.CLASS_NAMES}
    if question == "when":
        return {"text": CH.when_changes(b, ch, s, cfg, spec, planet or 0)}
    if question == "marana":
        return {"text": CH.marana(ch, s, spec)}
    if question == "pachakadi":
        return {"text": CH.pachakadi(ch, s, spec, planet, rasi)}
    p = CH.panel(ch, s, spec, retro_all=True)
    return {"text": CH.text_chart(p, kind or "south")}


def move_lagna(birth, settings, forward):
    b, cfg, _, _ = _raw(*_key(birth, settings))
    moved = M._local(b, CH.move_lagna(b, cfg, forward))
    return to_jsonable({"birth": dataclasses.asdict(moved), "start": M._when(moved)})


def nisheka(birth, settings):
    return _with_chart(M.nisheka, birth, settings)


def lifecycle(birth, settings, n):
    return _mode_s(M.lifecycle, birth, settings, n)


def special_search(birth, settings, when: BirthIn, *a):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(M.special_search(b, cfg, ch, when.data().jd_ut, *a, s=s))


def progression(birth, settings, kind, when: BirthIn, division=1, dasa="vimsottari_dasa", seed=2):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(M.progression(b, cfg, ch, kind, when.data(), division, dasa, seed, s))


def prasna(birth, kind, n, replace, years=0.0, days=0.0):
    return to_jsonable(M.prasna(birth.data(), kind, n, replace, years, days))


def correlation(natal: BirthIn, birth: BirthIn, settings, threshold, rule=0, orb=1.0, division=1):
    tb, cfg, ch, _ = _raw(*_key(birth, settings))
    natal_ch = _raw(*_key(natal, settings))[2]
    if rule:
        return to_jsonable(TR.correlation_by_orb(natal_ch, ch, tb, cfg, rule, orb, division))
    return to_jsonable(TR.correlation(natal_ch, ch, tb, cfg, threshold))


def calendar(natal: BirthIn, birth: BirthIn, settings, step, count, items, natal_varga=1, transit_varga=1, offset=0):
    tb, cfg, _, s = _raw(*_key(birth, settings))
    return to_jsonable(TR.calendar(_raw(*_key(natal, settings))[2], tb, cfg, s, step, count, items, natal_varga, transit_varga, offset))


def chakras(natal: BirthIn, birth: BirthIn, settings, options=None):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    nb, _, nch, _ = _raw(*_key(natal, settings))
    return to_jsonable(CK.wheels(nch, ch, b, cfg, s, options, natal_b=nb))


def chakra_special_point(birth, settings, kind, value, division, point, star):
    _, _, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(CK.special_point(ch, s, kind, value, division, point, star))


def amsa(birth, settings, division):
    _, _, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(B.amsa_rulers(ch, division, s))


def mundane(birth, settings, **options):
    return _mode_s(M.mundane, birth, settings, **options)


def transit(natal: BirthIn, birth: BirthIn, settings: Optional[SettingsIn], reference=0, natal_varga=1, transit_varga=1) -> dict:
    tb, cfg, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(TR.views(_raw(*_key(natal, settings))[2], tb, ch, cfg, s, reference, natal_varga, transit_varga))


def transit_domains(natal: BirthIn, birth: BirthIn, settings: Optional[SettingsIn]) -> list:
    _, _, ch, s = _raw(*_key(birth, settings))
    return TR.domains(_raw(*_key(natal, settings)), ch, s)


@functools.lru_cache(maxsize=64)
def _domain(natal_json: str, birth_json: str, settings_json: str, d: int):
    tb, cfg, ch, s = _raw(birth_json, settings_json)
    return to_jsonable(TR.domain_timeline(_raw(natal_json, settings_json), ch, tb, cfg, s, d))


def transit_domain(natal: BirthIn, birth: BirthIn, settings: Optional[SettingsIn], d: int) -> dict:
    b, s = _key(birth, settings)
    return _domain(natal.model_dump_json(), b, s, d)


@functools.lru_cache(maxsize=64)
def _domain_ahead(natal_json: str, birth_json: str, settings_json: str, d: int, years: int):
    tb, cfg, _, s = _raw(birth_json, settings_json)
    return to_jsonable(TR.domain_ahead(_raw(natal_json, settings_json), tb, cfg, s, d, years))


def transit_ahead(natal: BirthIn, birth: BirthIn, settings: Optional[SettingsIn], d: int, years: int) -> dict:
    """The Transit Calendar's "Coming up" (TR.domain_ahead) from the transit moment ``birth``."""
    b, s = _key(birth, settings)
    return _domain_ahead(natal.model_dump_json(), b, s, d, years)


@functools.lru_cache(maxsize=256)
def _panchanga(birth_json: str, settings_json: str, offset: int, days: int):
    birth, cfg, _, _ = _raw(birth_json, settings_json)
    return to_jsonable(MI.panchanga(birth, cfg, offset, days))


def panchanga(birth, settings, offset, days):
    return _panchanga(*_key(birth, settings), offset, days)


@functools.lru_cache(maxsize=256)
def _muhurta_day(birth_json: str, settings_json: str, lunar: str):
    birth, cfg, _, _ = _raw(birth_json, settings_json)
    return to_jsonable(MU.day(birth, cfg, lunar))


def muhurta_day(birth, settings, lunar):
    """The panchang and daily muhurtas of the date and place in ``birth`` (its clock time is not used)."""
    return _muhurta_day(*_key(birth, settings), lunar)


@functools.lru_cache(maxsize=64)
def _muhurta_find(birth_json: str, settings_json: str, event: str, natal_json: Optional[str]):
    birth, cfg, _, _ = _raw(birth_json, settings_json)
    moon = _raw(natal_json, settings_json)[2]["positions"]["Moon"]["lon"] if natal_json else None
    return to_jsonable(MU.find(birth, cfg, event, moon))


def muhurta_find(birth, settings, event, natal=None):
    """Every day of the month of ``birth``'s date judged for ``event``; with ``natal``, for that person too."""
    b, s = _key(birth, settings)
    return _muhurta_find(b, s, event, natal.model_dump_json() if natal else None)


@functools.lru_cache(maxsize=16)
def _festivals(birth_json: str, settings_json: str):
    birth, cfg, _, _ = _raw(birth_json, settings_json)
    return to_jsonable(FE.year(birth, cfg, birth.year))


def festivals(birth, settings, calendar):
    """The observances of ``birth``'s Gregorian year at its place in one regional calendar, with the other calendars' dates."""
    b, s = _key(birth.model_copy(update={"month": 1, "day": 1, "hour_local": 12.0}), settings)
    all_ = _festivals(b, s)
    return {"year": birth.year, "calendar": calendar, "items": FE.view(all_, calendar), "days": all_["days"][calendar]}


def laghu_parasari(birth, settings, mode, added, span_days, division=1, count_signs=True, one_cycle=False):
    b, cfg, ch, _ = _raw(*_key(birth, settings))
    return to_jsonable(MI.laghu_parasari(b, ch, cfg, mode, added, span_days, division, count_signs, one_cycle))


def panchanga_text(birth, settings, kind, year, month, day, days):
    b, cfg, ch, _ = _raw(*_key(birth, settings))
    return {"text": MI.monthly_text(b, ch, cfg, kind, year, month, day, days)}


def vargas(birth, settings=None, divisions=None):
    _, _, ch, s = _raw(*_key(birth, settings))
    return to_jsonable(B.many_vargas(ch, s, divisions))


def astrocartography(birth, settings=None, bhava_of=None, bhava_system=None):
    b, cfg, ch, s = _raw(*_key(birth, settings))
    if birth.adjust and birth.adjust.model_dump(exclude_defaults=True, exclude={"muntha", "muntha_signs"}):   # a Tajaka chart's Muntha moves nothing
        raise ValueError("This chart's bodies are moved by rule, so it has no map. Go back to the natal chart.")
    if s.siddhanta or s.topocentric or s.apparent_refraction:
        raise ValueError("The map needs Drik Siddhanta, geocentric, unrefracted positions, because the others change with the place.")
    return to_jsonable(AC.astrocartography(b, ch, cfg, s, bhava_of, bhava_system))


def finance_ohlc(symbol: str, range_: str = "1y", interval: str = "1d", exchange: Optional[str] = None,
                 end_ms: Optional[int] = None, buffer: int = 1):
    return to_jsonable(FN.ohlc(symbol, range_, interval, exchange, end_ms, buffer))


def finance_search(q: str, limit: int = 8):
    return to_jsonable(FN.search_symbols(q, limit))


def finance_events(birth, settings, start_ms: int, end_ms: int, kinds: Optional[list] = None):
    b, cfg, _, _ = _raw(*_key(birth, settings))
    return to_jsonable(FN.events(b, cfg, start_ms, end_ms, kinds))


@functools.lru_cache(maxsize=32)
def _timeline(birth_json: str, settings_json: str, year: int):
    b, cfg, _, s = _raw(birth_json, settings_json)
    return to_jsonable(TL.year(b, cfg, year, s.combustion_classical))


def timeline(birth, settings, year: int):
    """The Timeline tab's year of the sky; the same chart zone and settings give the same year, so it is kept."""
    return _timeline(*_key(birth, settings), year)
