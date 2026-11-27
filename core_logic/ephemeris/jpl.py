"""jpl: part of ephemeris. Settings > Ephemeris "XALEN": the grahas' positions from NASA JPL's DE442 kernel, read by
the XALEN Ephemeris engine (native/jpl_kernel: its SPK reader, IAU 2006 precession and IAU 2000B nutation) instead of
the Swiss Ephemeris (docs/SOURCES.md section 1).

``engine(cfg)`` is swisseph itself, or for ``cfg.ephemeris == "xalen"`` swisseph with ``calc_ut`` answered from the
kernel for the Sun, the Moon, the planets and the nodes under the same position flags (true or apparent, aberration,
deflection, nutation, topocentric, equatorial). The rest stays the Swiss Ephemeris': Delta-T (so a moment is the
same moment under either ephemeris), houses, ayanamsas and fixed stars, rise and set, eclipses, and every body at
dates outside the kernel's 1550-2650.

The Swiss Ephemeris reads the same DE442 through JPL's own binary file (``de442.eph``, SEFLG_JPLEPH; config.py),
which JPL publishes as ASCII only: ``asc2eph`` is JPL's converter (asc2eph.f) in Python.

``fetch_jpl_files()`` downloads the kernel and builds the binary file (start.sh and the Dockerfile call it).
"""
from __future__ import annotations
import hashlib
import os
import struct
import subprocess
import threading
from typing import Iterable, Iterator, List, Optional, Tuple
from .config import EphemerisConfig, EphemerisUnavailable, JPL_EPHE_PATH, JPL_FILE, _ephe_flag, _require_swe
try:
    import jpl_kernel
except ImportError:
    jpl_kernel = None

KERNEL_PATH = os.environ.get("SUDARSHANA_JPL_KERNEL") or os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "ephemeris", "jpl", "de442.bsp"))
KERNEL_URL = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de442.bsp"
# the file whose MD5 is NAIF's (aa_checksums.txt: 446656322267e7b819a26cb08a0d8718)
KERNEL_SHA256 = "8d5001fab315eeff222cc51f7cf7ffcdb43fb38fb9ac73ff09e09a5b361fd388"
_BODIES = range(12)   # SE_SUN .. SE_PLUTO, SE_MEAN_NODE, SE_TRUE_NODE
_EDGE = 1.0           # days kept off the kernel's ends: light-time (Pluto's ~5 hours) and the speed steps reach past the moment


class KernelSwe:
    """swisseph with ``calc_ut`` from the kernel (see the module's docstring); every other name is swisseph's."""

    def __init__(self, swe, span: Tuple[float, float]):
        self._swe, self._span = swe, span
        self._topo: Optional[Tuple[float, float, float]] = None
        self._flags = (swe.FLG_JPLEPH | swe.FLG_SWIEPH | swe.FLG_MOSEPH | swe.FLG_SPEED | swe.FLG_TRUEPOS | swe.FLG_NONUT
                       | swe.FLG_NOABERR | swe.FLG_NOGDEFL | swe.FLG_TOPOCTR | swe.FLG_EQUATORIAL | swe.FLG_SIDEREAL)

    def __getattr__(self, name):
        return getattr(self._swe, name)

    def set_topo(self, lon: float, lat: float, alt: float = 0.0) -> None:
        self._swe.set_topo(lon, lat, alt)
        self._topo = (lon, lat, alt)

    def calc_ut(self, jd_ut: float, body: int, flags: Optional[int] = None):
        s = self._swe
        if flags is None:
            flags = _ephe_flag(s, jd_ut) | s.FLG_SPEED
        tt = jd_ut + s.deltat_ex(jd_ut, _ephe_flag(s, jd_ut))   # the Swiss Ephemeris' Delta-T, a user-defined one too
        if body not in _BODIES or not self._span[0] + _EDGE <= tt <= self._span[1] - _EDGE:
            return s.calc_ut(jd_ut, body, flags)
        if flags & ~self._flags:
            raise ValueError("the JPL kernel does not answer position flags 0x%x" % (flags & ~self._flags))
        topo = None
        if flags & s.FLG_TOPOCTR:
            if self._topo is None:
                raise ValueError("topocentric positions need set_topo first")
            topo = self._topo
        apparent = not flags & s.FLG_TRUEPOS     # true positions: geometric, no light-time, deflection or aberration
        xx = jpl_kernel.calc(tt, jd_ut, body, apparent, apparent and not flags & s.FLG_NOGDEFL,
                             apparent and not flags & s.FLG_NOABERR, not flags & s.FLG_NONUT,
                             bool(flags & s.FLG_EQUATORIAL), bool(flags & s.FLG_SPEED), topo)
        if flags & s.FLG_SIDEREAL:
            # on the plane the sidereal mode names (the solar system's, for Jagannatha): the Swiss Ephemeris' own rotation
            # to it, carrying the kernel's difference from its place (the rotation is rigid, so to micro arc seconds)
            on = s.calc_ut(jd_ut, body, flags)[0]
            off = s.calc_ut(jd_ut, body, flags & ~s.FLG_SIDEREAL)[0]
            xx = ((on[0] + (xx[0] - off[0] + 180.0) % 360.0 - 180.0) % 360.0,) + tuple(
                a + b - c for a, b, c in zip(on[1:], xx[1:], off[1:]))
        return tuple(xx), flags


_ENGINE: Optional[KernelSwe] = None
_ENGINE_LOCK = threading.Lock()


def engine(cfg: EphemerisConfig):
    """The ephemeris the settings chose: swisseph, or ``KernelSwe`` for "xalen"."""
    s = _require_swe(cfg.ephe_path)
    if cfg.ephemeris != "xalen":
        return s
    global _ENGINE
    with _ENGINE_LOCK:
        if _ENGINE is None:
            if jpl_kernel is None:
                raise EphemerisUnavailable("the XALEN ephemeris needs its native module: run ./start.sh, which builds "
                                           "native/jpl_kernel (Rust, https://rustup.rs)")
            if not os.path.isfile(KERNEL_PATH):
                raise EphemerisUnavailable("the XALEN ephemeris needs NASA JPL's DE442 kernel: run ./start.sh, which "
                                           "downloads it to ephemeris/jpl/")
            start, end, _label = jpl_kernel.load(KERNEL_PATH)
            _ENGINE = KernelSwe(s, (start, end))
    return _ENGINE


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _curl(url: str, out: Optional[str] = None) -> subprocess.Popen:
    """curl fetching ``url`` (to ``out``, or as its stdout): curl takes the system's certificates, while Python's own
    store can lack the newer root NASA's servers chain to (Sectigo R46). Every file is checked by its SHA-256 after."""
    args = ["curl", "-sSfL", "--retry", "3", "--connect-timeout", "30", url] + (["-o", out] if out else [])
    return subprocess.Popen(args, stdout=None if out else subprocess.PIPE)


def fetch_kernel(path: str = KERNEL_PATH) -> None:
    """Download the kernel to ``path`` unless it is there, checking its SHA-256."""
    if os.path.isfile(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    part = path + ".part"
    if _curl(KERNEL_URL, part).wait() != 0 or _sha256(part) != KERNEL_SHA256:
        os.remove(part)
        raise RuntimeError("%s: the download's SHA-256 is not the kernel's" % KERNEL_URL)
    os.replace(part, path)


# ---------------------------------------------------------------------------
# JPL's binary ephemeris file, for the Swiss Ephemeris (SEFLG_JPLEPH)
# ---------------------------------------------------------------------------
ASCII_URL = "https://ssd.jpl.nasa.gov/ftp/eph/planets/ascii/de442/"
ASCII_FILES = ["header.442"] + ["ascp%05d.442" % y for y in range(1550, 2551, 100)]
# what asc2eph builds from them (the converter gives JPL's own binary of DE440 byte for byte from its ASCII)
JPL_FILE_SHA256 = "18e6a286d5d0a2dafae0a36ce5152d2d567a35d4e8c7c0a09f6309e936d2c9ea"
_OLDMAX = 400   # asc2eph.f: the constant names record 1 holds before the extra ones


def asc2eph(header: Iterable[str], data: Iterable[Iterable[str]], out: str) -> None:
    """JPL's asc2eph.f: the ASCII ephemeris (the lines of ``header``, then of each data file in order) to the binary
    direct-access file JPL distributes and the Swiss Ephemeris reads, little-endian as JPL's Linux files. Record 1:
    title, constant names, span, pointers; record 2: the constants; then one record of Chebyshev coefficients per span,
    the data files' overlapping records once."""
    lines: Iterator[str] = (line.rstrip("\r\n") for line in header)
    ksize = int(next(lines)[6:12])
    ncoeff = ksize // 2

    def group(n: int) -> None:      # asc2eph.f NXTGRP: the next non-blank line, and the blank one after it
        line = next(lines)
        while not line.strip():
            line = next(lines)
        if line[:12] != "GROUP   %d" % n:
            raise ValueError("JPL ephemeris header: %r where GROUP %d was expected" % (line, n))
        if n != 1070:
            next(lines)

    group(1010)
    title = b"".join(next(lines).ljust(84)[:84].encode("ascii") for _ in range(3))
    group(1030)
    next(lines)
    group(1040)
    n = int(next(lines)[:6])
    names: List[str] = []
    while len(names) < n:   # (10A8) into CHARACTER*6: each field's last six characters
        line = next(lines).ljust(80)
        names += [line[i + 2:i + 8] for i in range(0, 80, 8)]
    names = names[:n]
    group(1041)
    n = int(next(lines)[:6])
    values: List[float] = []
    while len(values) < n:
        values += [float(v.replace("D", "E")) for v in next(lines).split()]
    values = values[:n]
    const = dict(zip(names, values))
    group(1050)
    rows = [[int(line[i:i + 6].strip() or 0) for i in range(0, 90, 6)] for line in (next(lines).ljust(90) for _ in range(3))]
    group(1070)

    rec = ncoeff * 8
    first = last = span = None
    tmp = out + ".part"
    with open(tmp, "wb") as f:
        f.seek(2 * rec)
        for stream in data:
            it = iter(stream)
            for line in it:
                if not line.strip() or int(line[:6]) == 0:
                    continue
                nc = int(line[6:12])
                if nc != ncoeff:
                    raise ValueError("JPL ephemeris record %s: %d coefficients, the header says %d" % (line[:6], nc, ncoeff))
                db: List[str] = []
                for _ in range((nc + 2) // 3):
                    db += next(it).split()
                coeff = [float(v.replace("D", "E")) for v in db[:nc]]
                if last is not None and coeff[0] < last:
                    continue                                        # the previous file's last record again
                if last is not None and coeff[0] != last:
                    raise ValueError("JPL ephemeris: records do not abut at JD %s" % coeff[0])
                f.write(struct.pack("<%dd" % nc, *coeff))
                if first is None:
                    first, span = coeff[0], coeff[1] - coeff[0]
                last = coeff[1]
        cnam = (names + [" " * 6] * _OLDMAX)[:_OLDMAX]
        head = (title + "".join(cnam).encode("ascii") + struct.pack("<3di2d", first, last, span, len(names),
                                                                         const["AU    "], const["EMRAT "])
                + struct.pack("<36i", *[rows[i][j] for j in range(12) for i in range(3)])
                + struct.pack("<4i", int(const["DENUM "]), *[rows[i][12] for i in range(3)]))
        if len(names) > _OLDMAX:
            head += "".join(names[_OLDMAX:]).encode("ascii")
        head += struct.pack("<6i", *[rows[i][13] for i in range(3)], *[rows[i][14] for i in range(3)])
        cval = values if len(values) > _OLDMAX else (values + [0.0] * _OLDMAX)[:_OLDMAX]
        f.seek(0)
        f.write(head.ljust(rec, b"\0"))
        f.write(struct.pack("<%dd" % len(cval), *cval).ljust(rec, b"\0"))
    os.replace(tmp, out)


def fetch_jpl_file(path: str = os.path.join(JPL_EPHE_PATH, JPL_FILE)) -> None:
    """Build the Swiss Ephemeris' DE442 file at ``path`` from JPL's ASCII files unless it is there, checking its SHA-256."""
    if os.path.isfile(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def text(name):     # the file's lines, streamed: a curl that fails part way shows in the SHA-256
        proc = _curl(ASCII_URL + name)
        yield from (line.decode("ascii") for line in proc.stdout)
        if proc.wait() != 0:
            raise RuntimeError("could not download %s%s" % (ASCII_URL, name))

    asc2eph(text(ASCII_FILES[0]), (text(name) for name in ASCII_FILES[1:]), path + ".built")
    if _sha256(path + ".built") != JPL_FILE_SHA256:
        os.remove(path + ".built")
        raise RuntimeError("%s: the DE442 file built from JPL's ASCII files is not the expected one" % ASCII_URL)
    os.replace(path + ".built", path)


def fetch_jpl_files() -> None:
    """NASA JPL's DE442 for both ephemerides: the kernel (XALEN) and the binary file (the Swiss Ephemeris)."""
    fetch_kernel()
    fetch_jpl_file()

