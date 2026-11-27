"""
core_logic/ephemeris/
=====================
Swiss Ephemeris binding: turns birth data into the longitudes, houses and
sunrise/sunset that every other ``core_logic`` module consumes.

Sources (docs/SOURCES.md section 1):
- Positions, houses, rise and set, eclipses and Delta-T come from the Swiss Ephemeris
  (Astrodienst), as its documentation describes them, on NASA JPL's DE442 file in
  ``<repo>/ephemeris/jpl`` for 1550-2650 and its DE441 files in ``<repo>/ephemeris/data``
  outside (config.py ``_ephe_flag``); Settings > Ephemeris "XALEN" takes the grahas from
  the XALEN Ephemeris engine on the same DE442 (jpl.py). BPHS 3.8-9 asks for the grahas'
  positions as computed to agree with observation (drik ganita).
- Ayanamsas: the Swiss Ephemeris sidereal modes (Fagan=0, Deluce=2, Raman=3,
  Usha-Shashi=4, KP=5, Djwhal Khul=6, Yukteshwar=7, JN Bhasin=8, Aldebaran 15Ta=14,
  Hipparchos=15, Sassanian=16, Galactic centre 0Sg=17), and the star ayanamsas, a
  junction star (Surya Siddhanta ch. 8) held at the middle of its nakshatra: Spica
  180 deg, Aldebaran 46 deg 40 min, delta Cancri 106 deg, Shaula 240 deg.
- Birth-data semantics (east longitude, timezone) follow the .jhd conventions
  documented in ``jhd_io``.

Validation: ``tests/test_ephemeris_oracle.py`` compares this module with the planetary
longitudes and ascendant stored inside five sample ``.jhd`` files (agreement within
0.03 degree).

Requires ``pyswisseph`` (see requirements.txt).  Without it every function here raises
``EphemerisUnavailable``; the rest of ``core_logic`` stays importable.
"""
# The module was split into these parts; every name is re-exported from the part holding its final binding.
from __future__ import annotations
import math
import os
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple
from .. import surya_siddhanta
from ..deltat import deltat_se202
from ..utils import norm360
try:
    import swisseph as swe
except ImportError:
    swe = None
from .config import (  # noqa: F401
    AYANAMSAS,
    CLASSICAL_PLANETS,
    DEFAULT_EPHE_PATH,
    EphemerisConfig,
    EphemerisUnavailable,
    HOUSE_SYSTEM_CODES,
    PLANET_IDS,
    SIGN_NAMES,
    _AYANAMSA_BY_KEY,
    _SE202_AYANAMSAS,
    _SSS_CACHE,
    _SSY_PLANE,
    _SWE_LOCK,
    _ayanamsa_first,
    _ayanamsa_spec,
    _ayanamsa_value,
    _calc_flags,
    _delta_t,
    _ephe_flag,
    _jpl_span,
    JPL_EPHE_PATH,
    JPL_FILE,
    _computed,
    _plane_shift,
    _require_swe,
    _set_swe_sid_mode,
    _sss_chart,
    _thread_state,
    ayanamsa_value,
)
from .jpl import (  # noqa: F401
    KERNEL_PATH,
    KernelSwe,
    engine,
    asc2eph,
    fetch_jpl_file,
    fetch_jpl_files,
    fetch_kernel,
)
from .moments import (  # noqa: F401
    BirthData,
    jd_to_calendar,
    julian_day_ut,
)
from .positions import (  # noqa: F401
    _apparent_ecliptic,
    _planet_positions,
    _sss_positions,
    planet_positions,
)
from .houses import (  # noqa: F401
    house_cusps,
)
from .sunrise import (  # noqa: F401
    _SSS_DEPRESSION,
    _local_jd,
    _polar_day_edge,
    _shifted_day,
    _sss_sunrise_sunset,
    _sun_altitude_flags_step,
    day_night_span,
    lagna_at,
    longitude_func,
    sunrise_sunset,
)
from .day import (  # noqa: F401
    _HORA_SIGN_DAY,
    _HORA_SIGN_NIGHT,
    _KAALA_ORDER,
    _KAALA_START_DAY,
    _KAALA_START_NIGHT,
    _NAKSHATRA_LORDS,
    _SIGN_LORDS,
    _TITHI_LORDS,
    _YOGA_LORDS,
    _karana_index,
    _new_moon,
    day_lords,
    panchanga,
)
from .points import (  # noqa: F401
    VIMSOTTARI_SEEDS,
    dasa_year_mapper,
    chart_shadbala,
    kalavela_longitudes,
    lmt_offset_hours,
    next_eclipse,
    special_points,
    vimsottari_seed_longitude,
    zone_offset_hours,
)
from .build import (  # noqa: F401
    build_chart,
)
