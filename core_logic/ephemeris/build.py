"""build: part of ephemeris (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Any, Dict, Optional
from .moments import BirthData
from .config import EphemerisConfig, _require_swe, _sss_chart, ayanamsa_value
from .houses import house_cusps
from .positions import planet_positions
from .points import special_points
from .sunrise import sunrise_sunset

# ---------------------------------------------------------------------------
# One-call chart: the connection between the ephemeris and the engines
# ---------------------------------------------------------------------------
def build_chart(
    birth: BirthData,
    cfg: Optional[EphemerisConfig] = None,
    house_system: str = "PORPHYRY",
    with_special_points: bool = True,
) -> Dict[str, Any]:
    """
    Compute everything the engines need from birth data.

    The returned dict uses exactly the shapes ``core_logic`` functions take:
      ``planet_longitudes``  Dict[str, float]  (Sun..Saturn, Rahu, Ketu)
      ``planet_signs``       Dict[str, int]    (0 = Aries)
      ``lagna_sign`` / ``lagna_lon``
      ``retrograde``         Dict[str, bool]
      ``sunrise_hours`` / ``sunset_hours`` / ``birth_time_hours``
      ``ayanamsa``           degrees at birth
      ``special_lagnas``     Hora/Ghati/Bhava/Vighati lagna, Pranapada, Sree lagna, Bhrigu
                             bindu, Indu lagna, Kunda (longitudes), Indu/Varnada lagna (sign index)
      ``varnada_lagnas``     V1..V12 longitudes; ``sphutas`` Prana..Pancha, Yogi/Avayogi sphutas
      ``upagrahas``          Dhuma..Upaketu and Kaala..Mandi longitudes
      ``is_night`` / ``vedic_weekday``  (0 = Sunday; changes at sunrise)
    Feed e.g. ``dashas.compute_vimshottari_tree(chart['planet_longitudes']['Moon'], dt)``,
    ``ashtakavarga.run_full_ashtakavarga_pipeline(chart['planet_signs'], chart['lagna_sign'])``.

    A chart for another moment (a transit, a return, a shifted birth time, another zone) is a new ``BirthData``
    built and passed here; the tropical zodiac is ``EphemerisConfig(ayanamsa="TROPICAL")``.  Sources of each part:
    docs/SOURCES.md section 1.
    """
    cfg = cfg or EphemerisConfig()
    jd = birth.jd_ut
    pos = planet_positions(jd, cfg, birth)
    houses = house_cusps(jd, birth.latitude, birth.longitude_east, house_system, cfg)
    sun = sunrise_sunset(birth, cfg)
    lagna_lon = houses["ascendant"]
    lons = {n: p["lon"] for n, p in pos.items()}
    chart = {
        "jd_ut": jd,
        "ayanamsa": _sss_chart(jd, cfg, birth.longitude_east, birth.latitude)["ayanamsa"] if cfg.siddhanta == 1
        else ayanamsa_value(jd, cfg, birth.longitude_east),
        "positions": pos,
        "planet_longitudes": lons,
        "planet_signs": {n: int(l // 30) for n, l in lons.items()},
        "retrograde": {n: p["retrograde"] for n, p in pos.items()},
        "lagna_lon": lagna_lon,
        "lagna_sign": int(lagna_lon // 30),
        "houses": houses,
        "sunrise_hours": sun["sunrise_hours"],
        "sunset_hours": sun["sunset_hours"],
        "birth_time_hours": birth.hour_local,
        "local_sidereal_time_hours": houses["armc"] / 15.0 if cfg.siddhanta == 1 else
        (_require_swe(cfg.ephe_path).sidtime(jd) + birth.longitude_east / 15.0) % 24.0,
        "config": cfg,
    }
    if with_special_points:
        chart.update(special_points(birth, chart, cfg))
    return chart
