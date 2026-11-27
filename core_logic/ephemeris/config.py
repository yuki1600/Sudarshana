"""config: part of ephemeris (split from one module; see __init__.py)."""
from __future__ import annotations
import os
import struct
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from .. import surya_siddhanta
from ..deltat import deltat_se202
from ..utils import norm360
try:
    import swisseph as swe
except ImportError:
    swe = None

class EphemerisUnavailable(RuntimeError):
    """Raised when pyswisseph is not installed."""


DEFAULT_EPHE_PATH = os.environ.get("SUDARSHANA_EPHE_PATH") or os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "ephemeris", "data")
)
# NASA JPL's DE442 (1550-2650) as JPL's binary file, which the Swiss Ephemeris reads itself (SEFLG_JPLEPH) when it is
# there; jpl.py builds it from JPL's ASCII files. Outside its span the .se1 files answer
JPL_EPHE_PATH = os.environ.get("SUDARSHANA_JPL_PATH") or os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "ephemeris", "jpl"))
JPL_FILE = "de442.eph"

# Swiss Ephemeris state (ephe path, sidereal mode, topocentric place) is per thread in builds with
# thread-local storage (Linux wheels) and process-wide otherwise (macOS).  So the ephe path is
# remembered per thread (a new thread would otherwise silently fall back to the Moshier model),
# and every public function that sets state holds this lock for the process-wide builds.
_thread_state = threading.local()
_SWE_LOCK = threading.RLock()


def _require_swe(ephe_path: Optional[str] = None):
    if swe is None:
        raise EphemerisUnavailable("pyswisseph is required: pip install -r requirements.txt")
    path = ephe_path or DEFAULT_EPHE_PATH
    if getattr(_thread_state, "path", None) != path:
        swe.set_ephe_path(path + os.pathsep + JPL_EPHE_PATH)
        if _jpl_span():
            swe.set_jpl_file(JPL_FILE)
        # the Moon's tidal acceleration, which Delta-T before 1955 rests on: DE440, DE441 and DE442 share -25.936"/cy^2.
        # Left automatic, Swiss Ephemeris 2.10 takes it from the last file it read and knows DE442 by no number (-25.80):
        # Delta-T in 1500 would move 2.6 s with the call before. A user-defined Delta-T (swisseph_202) is not touched
        swe.set_tid_acc(swe.TIDAL_DE441)
        _thread_state.path = path
    return swe


_JPL_SPAN: List[Optional[Tuple[float, float]]] = []


def _jpl_span() -> Optional[Tuple[float, float]]:
    """The first and last Julian day (TDB) of JPL's DE442 file (its record 1), or None when the file is not there."""
    if not _JPL_SPAN:
        try:
            with open(os.path.join(JPL_EPHE_PATH, JPL_FILE), "rb") as f:
                f.seek(2652)    # after the title (252 bytes) and the 400 constant names (6 each): start, end, span
                start, end = struct.unpack("<2d", f.read(16))
            _JPL_SPAN.append((start, end))
        except OSError:
            _JPL_SPAN.append(None)
    return _JPL_SPAN[0]


def _ephe_flag(s, jd: float) -> int:
    """The Swiss Ephemeris' data at ``jd``: JPL's DE442 file (SEFLG_JPLEPH) inside its span, kept a day off its ends for
    light-time and speeds; the .se1 files (SEFLG_SWIEPH) outside it, where JPLEPH would fall back to the Moshier model."""
    span = _jpl_span()
    return s.FLG_JPLEPH if span and span[0] + 1.0 <= jd <= span[1] - 1.0 else s.FLG_SWIEPH


@contextmanager
def _delta_t(s, jd_ut: float, cfg: "EphemerisConfig"):
    """Use Swiss Ephemeris 2.02's Delta-T (core_logic.deltat) for computations at ``jd_ut``; restores the library
    model after."""
    dt = deltat_se202(jd_ut) if cfg.swisseph_202 else None
    if dt is None:
        yield
        return
    s.set_delta_t_userdef(dt)
    try:
        yield
    finally:
        s.set_delta_t_userdef(s.DELTAT_AUTOMATIC)


# ---------------------------------------------------------------------------
# Ayanamsa: the 22 choices of Settings > Ayanamsa, in their menu order (docs/SOURCES.md section 1.1)
# ---------------------------------------------------------------------------
# kind: "swe"  -> Swiss Ephemeris sidereal mode (const name)
#       "star" -> ayanamsa = tropical longitude of star - target: the junction star (Surya Siddhanta ch. 8) held at
#                 the middle of its nakshatra; "star_se202" is the star as Swiss Ephemeris 2.02's fixstars.cat gives
#                 it (in ephemeris/data/sefstars.txt as SE2Spica / SE2Aldebaran / ,se2deCnc / SE2Shaula), used with
#                 EphemerisConfig.swisseph_202
#       "tropical" / "custom" / "unsupported"
AYANAMSAS: List[Dict[str, Any]] = [
    {"key": "TRUE_LAHIRI", "label": "True Lahiri/Chitrapaksha (Spica in the middle of Chitra always)",
     "kind": "star", "star": "Spica", "star_se202": "SE2Spica", "target": 180.0},
    {"key": "LAHIRI", "label": "Traditional Lahiri", "kind": "swe", "const": "SIDM_LAHIRI"},
    {"key": "PUSHYA_PAKSHA", "label": "Pushya-paksha ayanamsa", "kind": "star",
     "star": ",deCnc", "star_se202": ",se2deCnc", "target": 106.0},
    {"key": "RAMAN", "label": "Raman", "kind": "swe", "const": "SIDM_RAMAN"},
    {"key": "KP", "label": "Krishnamoorthy (KP)", "kind": "swe", "const": "SIDM_KRISHNAMURTI"},
    {"key": "CUSTOM_STAR", "label": "Fixed star based CUSTOM ayanamsa", "kind": "custom"},
    # Jagannatha: Spica at 180 measured on the solar system's rotation plane: swe sidereal mode 0x200
    # (SE_SIDBIT_SSY_PLANE, Swiss Ephemeris doc 2.8.12), planets and Spica with SEFLG_SIDEREAL, then planet - Spica + 180
    {"key": "JAGANNATHA", "label": "Jagannatha (Spica in the middle of Chitra always, fixed solar rotation plane)",
     "kind": "star_plane", "star": "Spica", "star_se202": "SE2Spica", "target": 180.0},
    {"key": "ROHINI_PAKSHA", "label": "Rohini-paksha ayanamsa (Aldebaran in the middle of Rohini always)",
     "kind": "star", "star": "Aldebaran", "star_se202": "SE2Aldebaran", "target": 46.0 + 40.0 / 60.0},
    # SSS: the Surya Siddhanta's libration of the equinox (3.9-10) at the place's local true time (surya_siddhanta.ayanamsa)
    {"key": "SSS", "label": "Sri Surya Siddhanta", "kind": "sss"},
    # Deva-datta: Lahiri less 0d22'37" (no published definition found; docs/SOURCES.md section 1.1)
    {"key": "DEVA_DATTA", "label": "Deva-datta", "kind": "swe", "const": "SIDM_LAHIRI", "delta": -0.37694444444444447},
    {"key": "USHA_SHASHI", "label": "Usha-Shashi", "kind": "swe", "const": "SIDM_USHASHASHI"},
    {"key": "YUKTESHWAR", "label": "Yukteshwar", "kind": "swe", "const": "SIDM_YUKTESHWAR"},
    {"key": "JN_BHASIN", "label": "JN Bhasin", "kind": "swe", "const": "SIDM_JN_BHASIN"},
    # Chandra Hari: Shaula (lambda Scorpii) at 240 deg, the start of Mula (Swiss Ephemeris "True Mula"); a star
    # ayanamsa on the true equinox (see _computed)
    {"key": "CHANDRA_HARI", "label": "Chandra Hari", "kind": "star", "star": "Shaula", "star_se202": "SE2Shaula",
     "target": 240.0},
    {"key": "FAGAN", "label": "Fagan", "kind": "swe", "const": "SIDM_FAGAN_BRADLEY"},
    {"key": "DELUCE", "label": "Deluce", "kind": "swe", "const": "SIDM_DELUCE"},
    {"key": "DJWHAL_KHUL", "label": "Djwhal Khul", "kind": "swe", "const": "SIDM_DJWHAL_KHUL"},
    {"key": "ALDEBARAN_15TA", "label": "Aldebaran at 15Ta0", "kind": "swe", "const": "SIDM_ALDEBARAN_15TAU"},
    {"key": "GALCENT_0SG", "label": "Galaxy center at 0Sg0", "kind": "swe", "const": "SIDM_GALCENT_0SAG"},
    {"key": "HIPPARCHOS", "label": "Hipparchos", "kind": "swe", "const": "SIDM_HIPPARCHOS"},
    {"key": "SASSANIAN", "label": "Sassanian", "kind": "swe", "const": "SIDM_SASSANIAN"},
    {"key": "TROPICAL", "label": "Tropical (sayana)", "kind": "tropical"},
]
_AYANAMSA_BY_KEY = {a["key"]: a for a in AYANAMSAS}

# Swiss Ephemeris 2.02.01's ayanamsa table (the ayanamsa[] array of its sweph.c: (t0, ayanamsa at t0) by
# SE_SIDM_*). Later versions changed some entries and correct t0 for their precession model (Lahiri +0.14", Raman /
# KP -0.83" in 1863-1947); SE_SIDM_USER with these reproduces the 2.02 values to 0.005"; used with swisseph_202
_SE202_AYANAMSAS = [
    (2433282.5, 24.042044444), (2435553.5, 23.245522556), (2415020.0, 26.41305), (2415020.0, 21.01443999999998),
    (2415020.0, 18.66095999999999), (2415020.0, 22.363888999999972), (2415020.0, 26.963097600000026),
    (2415020.0, 21.082222), (2415020.0, 21.365556000000026), (1684532.5, -3.36667), (1684532.5, -4.76667),
    (1684532.5, -5.61667), (1684532.5, -4.56667), (1673941.0, -5.079167), (1684532.5, -4.44088389),
    (1674484.0, -9.33333), (1927135.8747793, 0.0), (1746447.518, 0.0), (2451545.0, 0.0), (2415020.0, 0.0),
    (2433282.42345905, 0.0), (1903396.8128654, 0.0), (1903396.8128654, -0.21463395), (1903396.7895321, 0.0),
    (1903396.7895321, -0.23763238), (1903396.8128654, -0.79167046), (1903396.8128654, 2.11070444)]


def _set_swe_sid_mode(s, mode: int, cfg: "EphemerisConfig") -> None:
    """swe_set_sid_mode(mode), or SE 2.02's definition of it with ``swisseph_202``."""
    if cfg.swisseph_202 and 0 <= mode < len(_SE202_AYANAMSAS):
        s.set_sid_mode(s.SIDM_USER, *_SE202_AYANAMSAS[mode])
    else:
        s.set_sid_mode(mode, 0, 0)

# House systems of Settings > Bhavas -> Swiss Ephemeris letters (None = handled here)
HOUSE_SYSTEM_CODES: Dict[str, Optional[str]] = {
    "RASI": "W",              # each rasi is a house (whole sign)
    "EQUAL": "E",             # equal houses (30 deg each) from the ascendant
    "EQUAL_PADA": None,       # equal houses based on nakshatra padas (9 padas each)
    "PORPHYRY": "O",          # Sripati
    "PLACIDUS": "P",
    "KOCH": "K",
    "REGIOMONTANUS": "R",
    "CAMPANUS": "C",
    "AXIAL_ROTATION": "X",
    "POLICH_PAGE": "T",
    "ALCABITUS": "B",
}

PLANET_IDS = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4,
    "Jupiter": 5, "Saturn": 6, "Uranus": 7, "Neptune": 8, "Pluto": 9,
}
CLASSICAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
              "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


@dataclass
class EphemerisConfig:
    """User-tunable calculation options (Settings > Model and ayanamsa, Grahas, Sunrise, Upagrahas)."""
    ayanamsa: str = "TRUE_LAHIRI"          # key of AYANAMSAS
    ayanamsa_offset_deg: float = 0.0       # the "add this correction" amount
    custom_star: Optional[str] = None      # for CUSTOM_STAR (ini CustomStarCode, e.g. ",alVir")
    custom_star_longitude: float = 180.0   # sidereal longitude the custom star is fixed at (CustomStarLongitude)
    custom_star_fixed_plane: bool = False  # FixedPlaneInCustomStarAyanamsa: measured on the invariable plane
    nodes: str = "mean"                    # "mean" | "true"
    topocentric: bool = False              # geocentric by default
    true_positions: bool = True            # SEFLG_TRUEPOS; ini TruePositions=1
    apparent_refraction: bool = False      # swe_refrac when TruePositions is off; ini ApparentRefraction=0
    no_aberration: bool = False            # switch off annual aberration
    no_gravitational_deflection: bool = False   # switch off light deflection
    no_nutation: bool = False              # mean equinox of date
    sunrise_definition: int = 0            # 0..3 (sunrise_sunset); ini SunriseDefinition=0
    # The kalavelas (BPHS 3.66-70): UpagrahaRiseMethod of Kaala, Mrityu, Artha Prahara, Yama Ghantaka, Maandi, Gulika
    # (0 beginning, 1 middle, 2 end of the part), Mandi- / GulikaInSaturnPortion (off: the lord-less 8th part),
    # UpagrahaDayDefinition (non-zero: 6 am / 6 pm local mean time)
    upagraha_rise: Tuple[int, int, int, int, int, int] = (1, 1, 1, 1, 1, 0)
    mandi_in_saturn_portion: bool = True
    gulika_in_saturn_portion: bool = True
    upagraha_day_definition: int = 0
    vyatipata_method: int = 0              # VyatipataMethod: 0 = 360 - Dhuma (BPHS 3.61-64), 1 = Dhuma + 53 deg 20'
    # ContinuousSpecialLagnas: hora, ghati, bhava, vighati lagnas run from the Sun at birth, not the Sun at sunrise
    # (BPHS 5.2-8 counts from the Sun at sunrise)
    continuous_special_lagnas: bool = False
    ephe_path: Optional[str] = None
    # reproduce Swiss Ephemeris 2.02's conventions (its Delta-T, star catalogue, ayanamsa table and rise_trans flags), the
    # version, Swiss Ephemeris 2.02.01's; False uses the current library's. The data is JPL's DE442 either way
    swisseph_202: bool = False
    # planetary model (INI Siddhanta): 0 drik (Swiss Ephemeris), 1 Sri Surya Siddhanta (surya_siddhanta: planets, lagna,
    # houses and sunrise from the SSS; the chosen ayanamsa is kept)
    siddhanta: int = 0
    # the engine of the drik model: "swiss" (the Swiss Ephemeris on JPL's DE442 file) or "xalen" (the XALEN Ephemeris
    # engine on JPL's DE442 kernel; jpl.py)
    ephemeris: str = "swiss"


def _computed(spec: Dict[str, Any]) -> bool:
    """The ayanamsas computed on the true equinox of date (tropical, Chandra Hari, SSS): the others are reduced
    by a mean-equinox ayanamsa and so take mean-equinox (SEFLG_NONUT) positions."""
    return spec["kind"] in ("tropical", "sss") or spec["key"] == "CHANDRA_HARI"


def _ayanamsa_spec(cfg: EphemerisConfig) -> Dict[str, Any]:
    spec = _AYANAMSA_BY_KEY.get(cfg.ayanamsa)
    if spec is None:
        raise ValueError(f"unknown ayanamsa {cfg.ayanamsa!r}; choose from {[a['key'] for a in AYANAMSAS]}")
    if spec["kind"] == "unsupported":
        raise NotImplementedError(
            f"{spec['label']}: this ayanamsa has no definition here")
    if spec["kind"] == "custom":   # a star ayanamsa (or a fixed-plane one, as Jagannatha) of the user's star
        if not cfg.custom_star:
            raise ValueError("CUSTOM_STAR requires cfg.custom_star")
        return dict(spec, kind="star_plane" if cfg.custom_star_fixed_plane else "star", star=cfg.custom_star,
                    star_se202=cfg.custom_star, target=cfg.custom_star_longitude)
    return spec


def ayanamsa_value(jd_ut: float, cfg: Optional[EphemerisConfig] = None,
                   longitude_east: Optional[float] = None) -> float:
    """Ayanamsa in degrees at ``jd_ut`` for the configured choice (includes the user offset).  The SSS ayanamsa
    depends on the place's local time (``longitude_east``, Ujjain when not given)."""
    cfg = cfg or EphemerisConfig()
    with _SWE_LOCK:
        return _ayanamsa_value(jd_ut, cfg, longitude_east)


def _ayanamsa_value(jd_ut: float, cfg: EphemerisConfig, longitude_east: Optional[float] = None) -> float:
    s = _require_swe(cfg.ephe_path)
    spec = _ayanamsa_spec(cfg)
    kind = spec["kind"]
    if kind == "sss":
        lon = surya_siddhanta.UJJAIN if longitude_east is None else longitude_east
        return surya_siddhanta.ayanamsa(jd_ut, lon, cfg.ayanamsa_offset_deg)
    if kind == "tropical":
        base = 0.0
    elif kind == "star_plane":
        # swe_get_ayanamsa in mode 0x200 less (target - the star's sidereal longitude on that plane)
        s.set_sid_mode(_SSY_PLANE, 0, 0)
        base = s.get_ayanamsa(jd_ut) - _plane_shift(s, jd_ut, cfg, spec)
    elif kind == "swe":
        _set_swe_sid_mode(s, getattr(s, spec["const"]), cfg)
        # with swisseph_202, the Swiss Ephemeris 2.02 convention: swe_get_ayanamsa (the ET function) given the UT
        base = (s.get_ayanamsa(jd_ut) if cfg.swisseph_202 else s.get_ayanamsa_ut(jd_ut)) + spec.get("delta", 0.0)
    else:  # star based (also CUSTOM_STAR)
        star, target = spec["star_se202" if cfg.swisseph_202 else "star"], spec["target"]
        # the star takes the planet flags and is mean (no nutation), like the mean-equinox ayanamsa it stands for;
        # not for the true-equinox ayanamsas
        # (_computed: Chandra Hari), which are measured on the true equinox, like their planets
        star_flags = _calc_flags(cfg, jd_ut) & ~s.FLG_TOPOCTR
        if not _computed(spec):
            star_flags |= s.FLG_NONUT
        with _delta_t(s, jd_ut, cfg):
            trop = s.fixstar_ut(star, jd_ut, star_flags)[0][0]
        base = norm360(trop - target)
    return base + cfg.ayanamsa_offset_deg


_SSY_PLANE = 0x200   # SE_SIDM_FAGAN_BRADLEY | SE_SIDBIT_SSY_PLANE: positions on the solar system rotation plane


def _plane_shift(s, jd_ut: float, cfg: EphemerisConfig, spec: Dict[str, Any]) -> float:
    """target - the star's longitude on the invariable plane (SEFLG_SIDEREAL in mode 0x200): what the
    star_plane ayanamsa adds to the sidereal planets."""
    s.set_sid_mode(_SSY_PLANE, 0, 0)
    star = spec["star_se202" if cfg.swisseph_202 else "star"]
    with _delta_t(s, jd_ut, cfg):
        return spec["target"] - s.fixstar_ut(star, jd_ut, (_calc_flags(cfg, jd_ut) & ~s.FLG_TOPOCTR) | s.FLG_SIDEREAL)[0][0]


def _ayanamsa_first(jd_ut: float, cfg: EphemerisConfig) -> float:
    """The base ayanamsa before the star correction: swe_get_ayanamsa (the ET function, given the UT) in the Swiss
    mode of the choice (Lahiri for the star ayanamsas, 0x200 for Jagannatha); 0 (plus the offset) for the
    true-equinox ones.  The SSS model's equation of time uses it."""
    s = _require_swe(cfg.ephe_path)
    spec = _ayanamsa_spec(cfg)
    if spec["kind"] in ("tropical", "sss") or spec["key"] == "CHANDRA_HARI":
        return cfg.ayanamsa_offset_deg
    mode = getattr(s, spec["const"]) if spec["kind"] == "swe" else _SSY_PLANE if spec["kind"] == "star_plane" \
        else s.SIDM_LAHIRI
    _set_swe_sid_mode(s, mode, cfg)
    return s.get_ayanamsa(jd_ut) + spec.get("delta", 0.0) + cfg.ayanamsa_offset_deg


_SSS_CACHE: Dict[Tuple, Dict[str, Any]] = {}


def _sss_chart(jd_ut: float, cfg: EphemerisConfig, longitude_east: Optional[float],
               latitude: Optional[float]) -> Dict[str, Any]:
    """surya_siddhanta.chart for ``cfg`` (Ujjain on the equator when no place is given); the last few are kept since
    the bodies, the lagna and the ayanamsa are asked for one at a time."""
    lon = surya_siddhanta.UJJAIN if longitude_east is None else longitude_east
    lat = 0.0 if latitude is None else latitude
    key = (jd_ut, lon, lat, cfg.ayanamsa, cfg.ayanamsa_offset_deg, cfg.custom_star, cfg.custom_star_longitude,
           cfg.custom_star_fixed_plane, cfg.swisseph_202)
    if key not in _SSS_CACHE:
        if _ayanamsa_spec(cfg)["kind"] == "sss":
            res = surya_siddhanta.chart(jd_ut, lon, lat, None, cfg.ayanamsa_offset_deg)
        else:
            res = surya_siddhanta.chart(jd_ut, lon, lat, _ayanamsa_value(jd_ut, cfg),
                                  ayanamsa_first=_ayanamsa_first(jd_ut, cfg))
        if len(_SSS_CACHE) > 64:
            _SSS_CACHE.clear()
        _SSS_CACHE[key] = res
    return _SSS_CACHE[key]




def _calc_flags(cfg: EphemerisConfig, jd_ut: float):
    s = _require_swe(cfg.ephe_path)
    f = _ephe_flag(s, jd_ut) | s.FLG_SPEED
    if cfg.true_positions:
        f |= s.FLG_TRUEPOS
    if cfg.topocentric:
        f |= s.FLG_TOPOCTR
    if cfg.no_aberration:
        f |= s.FLG_NOABERR
    if cfg.no_gravitational_deflection:
        f |= s.FLG_NOGDEFL
    if cfg.no_nutation:
        f |= s.FLG_NONUT
    return f
