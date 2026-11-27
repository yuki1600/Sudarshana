"""points: part of ephemeris (split from one module; see __init__.py)."""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, Tuple
from ..utils import norm360
from .moments import BirthData, jd_to_calendar
from .config import EphemerisConfig, _SWE_LOCK, _ephe_flag, _require_swe
from .sunrise import _local_jd, day_night_span, lagna_at
from .day import day_lords
from .positions import planet_positions

def chart_shadbala(birth: BirthData, chart: Dict[str, Any], cfg: Optional[EphemerisConfig] = None) -> Dict[str, Any]:
    """Shadbala and Bhava Bala of a chart (BPHS 27; shadbala.shadbala_and_bhava_bala with its day timings and vargas)."""
    from .. import natal_chart as N, shadbala as SB
    lons = chart["planet_longitudes"]
    names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    vf = {"D1": N.compute_varga_d1, "D2": lambda x: N.compute_varga_d2(x, "us"), "D3": N.compute_varga_d3,
          "D7": N.compute_varga_d7, "D9": N.compute_varga_d9, "D12": N.compute_varga_d12, "D30": N.compute_varga_d30}
    signs = {v: [f(lons[n]) for n in names] for v, f in vf.items()}
    d = day_lords(birth, cfg)
    return SB.shadbala_and_bhava_bala(lons, chart["lagna_lon"], signs, d["is_day"], d["janma_ghatis"], d["day_ghatis"],
                             d["night_ghatis"], d["day_count"], birth.year, birth.month, birth.day,
                             birth.hour_local, birth.longitude_east)


def kalavela_longitudes(birth: BirthData, cfg: Optional[EphemerisConfig] = None,
                        points: Optional[Dict[str, str]] = None, lmt_6am: bool = False) -> Dict[str, Dict[str, float]]:
    """
    Kaala, Mrityu, Artha Prahara, Yama Ghantaka, Gulika and Maandi: the lagna rising at the
    moment given by special_lagnas_upagrahas.kalavela_offset_fraction (BPHS 3.66-70).
    ``points`` overrides the part point per body ("beginning" | "middle" | "end").
    """
    from ..special_lagnas_upagrahas import KALAVELA_LORDS, kalavela_offset_fraction
    cfg = cfg or EphemerisConfig()
    span = day_night_span(birth, cfg, lmt_6am or bool(cfg.upagraha_day_definition))
    if cfg.upagraha_day_definition and not lmt_6am:   # the weekday stays the one that began at sunrise
        span["weekday"] = day_night_span(birth, cfg)["weekday"]
    rise = dict(zip(("Kaala", "Mrityu", "Artha_Prahara", "Yama_Ghantaka", "Mandi", "Gulika"),
                    (("beginning", "middle", "end")[m] for m in cfg.upagraha_rise)))
    eighth = {"Mandi": not cfg.mandi_in_saturn_portion, "Gulika": not cfg.gulika_in_saturn_portion}
    out = {}
    for body in KALAVELA_LORDS:
        frac = kalavela_offset_fraction(span["weekday"], span["is_night"], body,
                                        (points or {}).get(body, rise[body]), eighth.get(body, False))
        hour = span["start_hours"] + frac * (span["end_hours"] - span["start_hours"])
        jd = _local_jd(birth, hour)
        out[body] = {"longitude": lagna_at(jd, birth, cfg), "rising_hour": hour, "jd_ut": jd}
    return out


def special_points(birth: BirthData, chart: Dict[str, Any], cfg: Optional[EphemerisConfig] = None) -> Dict[str, Any]:
    """Special lagnas and upagrahas of a chart (``chart`` = positions from build_chart)."""
    from .. import natal_chart as N, special_lagnas_upagrahas as U, miscellany as M
    lons, lagna = chart["planet_longitudes"], chart["lagna_lon"]
    span = day_night_span(birth, cfg)
    rise = span["vedic_sunrise_hours"]
    cfg_ = cfg or EphemerisConfig()
    sun_at_rise = lons["Sun"] if cfg_.continuous_special_lagnas else planet_positions(_local_jd(birth, rise), cfg, birth)["Sun"]["lon"]
    t = birth.hour_local
    hora = N.compute_hora_lagna(rise, t, sun_at_rise)
    indu_sign, _, _ = U.compute_indu_lagna(lagna, lons["Moon"])
    varnada_sign, _ = U.compute_varnada_lagna(lagna, hora)
    kal = kalavela_longitudes(birth, cfg)
    sph = M.compute_prashna_sphutas(lagna, lons["Moon"], lons["Sun"], kal["Gulika"]["longitude"], lons["Rahu"],
                                    lons["Mars"], lons["Venus"], lons["Jupiter"])
    return {
        "sphutas": {k: v["longitude"] for k, v in sph.items() if isinstance(v, dict)},
        "varnada_lagnas": U.compute_varnada_lagnas(lagna, hora),
        "special_lagnas": {
            "Indu_Lagna": U.compute_indu_lagna_longitude(lagna, lons["Moon"]),
            "Kunda": U.compute_kunda(lagna)[0],
            "Hora_Lagna": hora,
            "Ghati_Lagna": N.compute_ghati_lagna(rise, t, sun_at_rise),
            "Bhava_Lagna": N.compute_bhava_lagna(rise, t, sun_at_rise),
            "Vighati_Lagna": U.compute_vighati_lagna(sun_at_rise, rise, t),
            "Pranapada": U.compute_pranapada_lagna(lons["Sun"], rise, t),
            "Sree_Lagna": U.compute_sree_lagna(lagna, lons["Moon"]),
            "Bhrigu_Bindu": U.compute_bhrigu_bindu(lons["Moon"], lons["Rahu"]),
            "Indu_Lagna_sign": indu_sign,
            "Varnada_Lagna_sign": varnada_sign,
        },
        "upagrahas": {
            **{k: v["longitude"] for k, v in U.compute_aprakash_grahas(lons["Sun"], cfg_.vyatipata_method).items()},
            **{k: v["longitude"] for k, v in kal.items()},
        },
        "is_night": span["is_night"],
        "vedic_weekday": span["weekday"],
    }


# Vimsottari seeds (Settings > Nakshatra dasas > Seed) that a chart provides (key -> (source, nakshatra offset key))
VIMSOTTARI_SEEDS = ["MOON", "UTPANNA", "KSHEMA", "ADHANA", "LAGNA", "MANDI", "GULIKA", "TRISPHUTA",
                    "BHRIGU_BINDU", "PRANAPADA", "SUN", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN",
                    "RAHU", "KETU"]


def vimsottari_seed_longitude(chart: Dict[str, Any], seed: str) -> Tuple[float, str]:
    """(longitude, seed_type) to pass to dashas.compute_vimshottari_tree for a named seed.

    Trisphuta = Lagna + Moon + Gulika.  Needs the ``special_lagnas``/``upagrahas`` keys of
    build_chart for Mandi, Gulika, Trisphuta, Bhrigu Bindu and Pranapada."""
    seed = seed.upper()
    lons = chart["planet_longitudes"]
    if seed in ("MOON", "UTPANNA", "KSHEMA", "ADHANA"):
        return lons["Moon"], seed
    if seed == "LAGNA":
        return chart["lagna_lon"], "LAGNA"
    if seed in ("MANDI", "GULIKA"):
        return chart["upagrahas"][seed.title()], "MOON"
    if seed == "TRISPHUTA":
        return norm360(chart["lagna_lon"] + lons["Moon"] + chart["upagrahas"]["Gulika"]), "MOON"
    if seed in ("BHRIGU_BINDU", "PRANAPADA"):
        return chart["special_lagnas"][seed.title() if seed == "PRANAPADA" else "Bhrigu_Bindu"], "MOON"
    if seed.title() in lons:
        return lons[seed.title()], "MOON"
    raise ValueError(f"unknown seed {seed!r}; choose from {VIMSOTTARI_SEEDS}")


def dasa_year_mapper(birth: BirthData, cfg: Optional[EphemerisConfig] = None,
                     kind: str = "SOLAR") -> Callable[[float], datetime]:
    """
    Nonlinear dasa years (the year definitions PVR 16.2 discusses; the measures of time of SS 14.1-19): years
    since birth -> local datetime.
      SOLAR  the Sun's longitude is the clock (one year = Sun moves 360 deg; "true" solar year,
             sidereal unless cfg.ayanamsa is TROPICAL)
      TITHI  360 tithis per year (Moon - Sun elongation moves 4320 deg per year), searched back from
             birth + 354.36708 days x years + 15 days
      MOON   definition 5 (no menu entry): 360 lunar stars a year, the Moon back at its natal longitude
             (+ 360 deg x years), the last such moment before birth + 327.84 days x years + 15 days (the
             first after birth + 327.84 x years - 15 days for years <= 0); its ``rebased(start)`` counts from
             the dasa's start instead (the dasa builders call it)
    Pass the result as ``to_date`` to dashas.compute_vimshottari_tree.
    The dasa year definitions of Settings > Dasa years (fixed-length years: birth JD + years x days):
    0 mean tropical -> days_per_year=365.24219,
    1 savana (360 days), 2 user days, 3 true sidereal solar -> SOLAR (the default),
    4 tithis -> TITHI, 5 Moon -> MOON, 6 mean sidereal -> SIDEREAL_SOLAR, 7 true tropical solar -> SOLAR with
    ayanamsa TROPICAL.
    """
    cfg = cfg or EphemerisConfig()
    jd0 = birth.jd_ut
    kind = kind.upper()
    if kind == "SOLAR":
        f, per_year, speed = (lambda jd: planet_positions(jd, cfg)["Sun"]["lon"]), 360.0, 360.0 / 365.256363
    elif kind == "TITHI":
        def f(jd):
            p = planet_positions(jd, cfg)
            return norm360(p["Moon"]["lon"] - p["Sun"]["lon"])
        per_year, speed = 4320.0, 4320.0 / 354.367
    elif kind == "MOON":
        f = lambda jd: planet_positions(jd, cfg)["Moon"]["lon"]  # noqa: E731
        start, speed = f(jd0), 360.0 / 27.321661

        def advance(jd_a: float, lon_a: float, years: float) -> float:
            target, back = lon_a + years * 360.0, years > 0.0
            jd = jd_a + years * 327.84 + (15.0 if back else -15.0)
            jd += -((f(jd) - target) % 360.0) / speed if back else ((target - f(jd)) % 360.0) / speed
            for _ in range(30):
                err = (target - f(jd) + 180.0) % 360.0 - 180.0
                jd += err / speed
                if abs(err) < 1e-7:
                    break
            return jd

        def local(jd: float) -> datetime:
            y, m, d, h = jd_to_calendar(jd + birth.tz_east_hours / 24.0, birth.gregorian)
            return datetime(y, m, d) + timedelta(hours=h)

        def to_date_moon(years: float) -> datetime:
            return local(advance(jd0, start, years))

        def rebased(first: float) -> Callable[[float], datetime]:
            # every period is advanced from the dasa's start, and the 327.84-day
            # guess from there can land on another Moon cycle than the one from birth
            jd_s = advance(jd0, start, first)
            return lambda years: local(advance(jd_s, start + first * 360.0, years - first))
        to_date_moon.rebased = rebased
        return to_date_moon
    else:
        raise ValueError("kind must be SOLAR, TITHI or MOON")
    start = f(jd0)

    def to_date(years: float) -> datetime:
        target = start + years * per_year
        jd = jd0 + years * per_year / speed
        for _ in range(30):
            err = (target - f(jd) + 180.0) % 360.0 - 180.0
            jd += err / speed
            if abs(err) < 1e-7:
                break
        y, m, d, h = jd_to_calendar(jd + birth.tz_east_hours / 24.0, birth.gregorian)
        return datetime(y, m, d) + timedelta(hours=h)
    return to_date


def next_eclipse(jd_ut: float, kind: str = "solar", birth: Optional[BirthData] = None,
                 backward: bool = False, cfg: Optional[EphemerisConfig] = None) -> Dict[str, Any]:
    """
    Next (or previous) solar/lunar eclipse after ``jd_ut`` via swe_sol_eclipse_when_glob/_loc
    and swe_lun_eclipse_when/_loc (Swiss Ephemeris doc 5.2).  With ``birth`` the search is
    for an eclipse visible at that place.  Returns max/begin/end JDs (UT) and the type.
    """
    cfg = cfg or EphemerisConfig()
    with _SWE_LOCK:
        s = _require_swe(cfg.ephe_path)
        geo = (birth.longitude_east, birth.latitude, birth.altitude_m) if birth else None
        if kind == "solar":
            if geo:
                ret, tret, _ = s.sol_eclipse_when_loc(jd_ut, geo, _ephe_flag(s, jd_ut), backward)
                begin, end = tret[1], tret[4]
            else:
                ret, tret = s.sol_eclipse_when_glob(jd_ut, _ephe_flag(s, jd_ut), 0, backward)
                begin, end = tret[2], tret[3]
        elif kind == "lunar":
            if geo:
                ret, tret, _ = s.lun_eclipse_when_loc(jd_ut, geo, _ephe_flag(s, jd_ut), backward)
            else:
                ret, tret = s.lun_eclipse_when(jd_ut, _ephe_flag(s, jd_ut), 0, backward)
            begin, end = tret[6], tret[7]          # penumbral phase
        else:
            raise ValueError("kind must be 'solar' or 'lunar'")
        types = [(s.ECL_TOTAL, "total"), (s.ECL_ANNULAR, "annular"), (s.ECL_PARTIAL, "partial"),
                 (s.ECL_PENUMBRAL, "penumbral")]
    pos = planet_positions(tret[0], cfg)
    return {"kind": kind, "type": next((n for bit, n in types if ret & bit), "unknown"),
            "max_jd": tret[0], "begin_jd": begin, "end_jd": end,
            "sun_lon": pos["Sun"]["lon"], "moon_lon": pos["Moon"]["lon"], "rahu_lon": pos["Rahu"]["lon"]}


def zone_offset_hours(tz_name: str, year: int, month: int, day: int, hour_local: float) -> float:
    """East-positive UT offset (DST included) of an IANA zone at a local wall-clock time, for
    BirthData.tz_east_hours.  Uses the system tz database (``zoneinfo``)."""
    from zoneinfo import ZoneInfo
    local = datetime(year, month, day) + timedelta(hours=hour_local)
    return local.replace(tzinfo=ZoneInfo(tz_name)).utcoffset().total_seconds() / 3600.0


def lmt_offset_hours(longitude_east: float) -> float:
    """Local mean time offset from UT (east positive): 4 minutes per degree."""
    return longitude_east / 15.0
