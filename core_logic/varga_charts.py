"""
core_logic/varga_charts.py
==========================
Divisional charts with every scheme of Settings > Divisional charts: D-2 .. D-144, the custom D-n, D-n of D-m,
the varga longitudes, the bhava chart and the D-150 nadiamsa.  Sources of each scheme: docs/SOURCES.md section 3
(BPHS 6.5-41 for the Parasari divisions, PVR 6.2 for D-5, D-6, D-8, D-11, the named modern variants as marked
there, Deva Keralam for D-150).

Parts are counted by truncating toward zero with fixed float constants, so that a point
on a boundary falls where they put it.  ``VargaOptions()`` holds the defaults (data/default_settings.ini); a scheme
number is its place in the option's list (see ``SCHEMES``).  ``natal_chart.compute_varga_dN`` keep the default
schemes; this module has every scheme.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

# the varga order of the chart tables (Key Info's 23 charts) and the multipliers of the varga indices
DIVISIONS = (1, 9, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 81, 108, 144)
MULTIPLIER = (1, 9, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 81, 108, 144, 90, 150, 2, 30, 1, 9)

# menu labels in scheme order (= the value of the scheme's global); [default] marked in VargaOptions
SCHEMES = {
    2: ("Traditional Parasara hora (only Cn & Le)", "Jagannatha hora (1st/7th, day/night)",
        "Parivritti-dwaya (bicyclical) hora", "Samasaptaka hora (rasi and 7th)", "Mandooka hora (rasi and 3rd)",
        "Kashinatha hora (ownership, day/night)", "Parasara hora with parivritti & even sign reversal (Uma-Shambhu)",
        "Labha Mandooka hora (rasi and 11th)", "Raman hora (1st/11th, day/night)", "Raman hora (SJC modified)",
        "Niranjan hora (3rd/8th, 2nd/7th, day/night)", "Niranjan hora (SJC modified)"),
    3: ("Traditional Parasara drekkana", "Parivritti-traya drekkana", "Somanatha drekkana", "Jagannatha drekkana",
        "Parasara drekkana with parivritti & even sign reversal (Uma-Shambhu)"),
    4: ("Traditional Parasara chaturthamsa", "Parivritti chaturthamsa (cyclical, H-4)"),
    5: ("Standard panchamsa", "Parivritti panchamsa (cyclical, H-5)"),
    7: ("Traditional Parasara saptamsa", "Parasara saptamsa with even sign reversal (start from 7th, go reverse)",
        "Parasara saptamsa with even sign reversal (go reverse, end in 7th)"),
    8: ("Continuous/regular ashtamsa", "Dr. Raman's ashtamsa (tattva based)"),
    9: ("Parasara's navamsa", "Kalachakra navamsa", "Rangacharya's Krishna mishra navamsa (non-uniform)",
        "Parasara navamsa with even sign reversal (uniform Krishna Mishra)"),
    10: ("Traditional Parasara dasamsa", "Parivritti dasamsa (Ojha)",
         "Parasara dasamsa with even sign reversal (start from 9th, go reverse)",
         "Parasara dasamsa with even sign reversal (go reverse, end in 9th)",
         "Parasara dasamsa with even sign reversal (start from reverse 9th, go reverse)"),
    11: ("Rudramsa (regular, Pt. Rath)", "Ekadasamsa (anti-zodiacal, Dr. Raman)"),
    12: ("Traditional Parasara dwadasamsa", "Parasara dwadasamsa with even sign reversal"),
    16: ("Traditional Parasara shodasamsa", "Parasara shodasamsa with even sign reversal"),
    20: ("Traditional Parasara vimsamsa", "Parasara vimsamsa with even sign reversal"),
    24: ("Parasara siddhamsa with even sign reversal (odd Le->Cn, even Cn->Le)",
         "Traditional Parasara siddhamsa (odd Le->Cn, even Cn->Ge)",
         "Parasara siddhamsa with even sign double reversal (odd Le->Cn, even Le->Cn)"),
    27: ("Traditional Parasara nakshatramsa", "Parasara nakshatramsa with even sign reversal"),
    30: ("Parasara trimsamsa", "Parivritti (cyclical) trimsamsa", "Shashtyamsa like trimsamsa"),
    60: ("Traditional Parasara shashtyamsa (from sign)", "Parasara shashtyamsa with even sign reversal (from sign)",
         "Parasara shashtyamsa with even sign reversal (from Aries)", "Parasara shashtyamsa (from Aries)"),
    81: ("Parasara's nava-navamsa", "Kalachakra nava-navamsa"),
    108: ("From the sign", "From the navamsa sign"),
    150: ("Equal parts", "Unequal parts"),
}


@dataclass
class VargaOptions:
    """Scheme of each division (the INI ``D<n>Preference`` / ``HoraPreference`` keys; D-81 is menu only) and the
    switches of ``varga_longitude``.  Defaults are data/default_settings.ini's."""
    d2: int = 6  # HoraPreference: Uma-Shambhu
    d3: int = 0
    d4: int = 0
    d5: int = 0
    d7: int = 0
    d8: int = 0
    d9: int = 0
    d10: int = 0
    d11: int = 0
    d12: int = 0
    d16: int = 0
    d20: int = 0
    d24: int = 1
    d27: int = 0
    d30: int = 0
    d60: int = 0
    d81: int = 0  # (not saved in the ini)
    d108: int = 1  # D108Preference
    d150: int = 1  # D150Preference
    ardha_nadi_ruler: int = 1  # ArdhaNadiRulerDefinition
    mirror_reversed_longitudes: bool = True  # varga longitudes mirrored in even signs (reversal schemes)
    equal_d30_longitudes: bool = True  # no unequal Parasara D-30 longitude (d30_unequal_longitude)


DEFAULT = VargaOptions()


def _t(x: float) -> int:
    """Truncation toward zero (how the parts are counted)."""
    return int(x)


def _sd(lon: float) -> Tuple[int, float]:
    """Sign (point record +0xe8, trunc(lon / 30)) and degrees in it."""
    s = int(lon / 30.0)
    return s, lon - s * 30.0


_KALACHAKRA = (7, 6, 5, 3, 4, 2, 1, 0, 11, 10, 9, 8)
_START_9 = (0, 8, 4)
_DIR = (1, -1)


def d9(lon: float, mode: int = 0) -> int:
    base = _t(lon * 0.3) % 12
    if mode == 1:
        return _KALACHAKRA[base] if _t(lon * 0.025) & 1 else base
    if mode in (2, 3):
        q = _t(lon * 0.03333333333333333) % 12
        if mode == 2:
            k = _t((lon - q * 30.0) * -0.3)
            return ((_START_9[q % 3] + q) % 12 - k * _DIR[q % 2] + 108) % 12
        part = _t((lon - q * 30.0) * 0.3)
        i = (_START_9[q % 3] + q) % 12
        if _DIR[q % 2] == -1:
            i = (i + 8) % 12
        return (_DIR[q % 2] * part + 108 + i) % 12
    return base


_HORA_JAGANNATHA = (0, 1, 2, 3, 10, 11, 0, 1, 2, 3, 10, 11, 6, 7, 8, 9, 4, 5, 6, 7, 8, 9, 4, 5)
_HORA_OWNER = (0, 1, 2, 3, 3, 2, 1, 0, 8, 9, 9, 8, 7, 6, 5, 4, 4, 5, 6, 7, 11, 10, 10, 11)   # the hora by ownership


def _hora_owner(sign: int, flag: bool, plain: bool) -> int:
    v = _HORA_OWNER[sign + flag * 12]
    if not plain and sign in (3, 4):         # Cancer and Leo give their own sign
        return sign
    return v


def _cn_le(lon: float) -> int:
    return 3 if _t((lon * 0.06666666666666667 + 1.0) * 0.5) & 1 else 4


def d2(lon: float, mode: int = 6) -> int:
    s, deg = _sd(lon)
    half = _t(lon * 0.06666666666666667) & 1
    second = deg >= 15.0
    if mode == 0:
        return _cn_le(lon)
    if mode == 1:
        return _HORA_JAGANNATHA[s + (_cn_le(lon) - 3) * 12]
    if mode == 2:
        return _t(lon * 0.06666666666666667) % 12
    if mode in (3, 4, 7):
        return (s + {3: 6, 4: 2, 7: 10}[mode] * half) % 12
    if mode == 5:
        return _hora_owner(s % 12, (s & 1) == second, True)
    if mode == 6:
        q = _t(lon * 0.03333333333333333)
        x = q * 30.0 + (30.0 - (lon - q * 30.0)) if q & 1 else lon
        return _t(x * 0.06666666666666667) % 12
    flag = (s & 1) == second
    if mode in (8, 9):
        return _hora_owner((s + 10) % 12 if second else s, flag, mode == 9)
    if mode in (10, 11):
        b = (s + 11) % 12 if s & 1 else s
        return _hora_owner((b + (7 if second else 2)) % 12, flag, mode == 11)
    raise ValueError(mode)


_D3_US = (0, 1, 2, 5, 4, 3, 6, 7, 8, 11, 10, 9)


def d3(lon: float, mode: int = 0) -> int:
    s, deg = _sd(lon)
    k = _t(deg * -0.1)
    if mode == 0:
        return (s + (1200 - k) * 4) % 12
    if mode == 1:
        return _t(lon * 0.1) % 12
    if mode == 2:                                   # Somanatha
        v = (s // 2 + 400) * 3 - k
        return v % 12 if s % 2 == 0 else 11 - v % 12
    if mode == 3:                                   # Jagannatha: from the movable sign of the element
        return ((s & 3) * 9 % 12 + (1200 - k) * 4) % 12
    if mode == 4:
        return _D3_US[_t(lon * 0.1) % 12]
    raise ValueError(mode)


def d4(lon: float, mode: int = 0) -> int:
    s, deg = _sd(lon)
    if mode == 1:
        return _t(lon * 0.13333333333333333) % 12
    return (s + (0, 3, 6, 9)[min(_t(deg * 0.13333333333333333), 3)]) % 12


_UNEQUAL_ODD = {3: 0, 7: 10, 5: 8, 4: 2, 6: 6}
_UNEQUAL_EVEN = {3: 7, 7: 9, 5: 11, 4: 5, 6: 1}


def _unequal(s: int, deg: float, bounds: Sequence[float]) -> int:
    """D-5 / D-30 parts: odd signs Ar Aq Sg Ge Li, even signs (degrees counted from the end) Sc Cp Pi Vi Ta."""
    x = 30.0 - deg if s & 1 else deg
    if x < bounds[0]:
        i = 3
    elif x <= bounds[1]:
        i = 7
    elif x <= bounds[2]:
        i = 5
    elif x <= bounds[3]:
        i = 4
    else:
        i = 6
    return (_UNEQUAL_EVEN if s & 1 else _UNEQUAL_ODD)[i]


def d5(lon: float, mode: int = 0) -> int:
    if mode == 1:
        return _t(lon * 0.16666666666666666) % 12
    s, deg = _sd(lon)
    return _unequal(s, deg, (6.0, 12.0, 18.0, 24.0))


def d6(lon: float) -> int:
    return _t(lon * 0.2) % 12


def d7(lon: float, mode: int = 0) -> int:
    s, deg = _sd(lon)
    part = _t(deg * 0.23333333333333334)
    if mode == 1:
        return (_DIR[s & 1] * part + (0, 6)[s & 1] + s + 12) % 12
    if mode == 2:
        return (_DIR[s & 1] * part + s + 12) % 12
    return _t(lon * 0.23333333333333334) % 12


def d8(lon: float, mode: int = 0) -> int:
    if mode == 1:
        s, deg = _sd(lon)
        return ((0, 4, 8)[s % 3] - _t(deg * -0.26666666666666666)) % 12
    return _t(lon * 0.26666666666666666) % 12


def d10(lon: float, mode: int = 0) -> int:
    if mode == 1:
        return _t(lon * 0.3333333333333333) % 12
    s, deg = _sd(lon)
    part = _t(deg * 0.3333333333333333)
    if s & 1 == 0:
        return (s + part) % 12
    return (s + {0: part + 8, 2: 20 - part, 3: 17 - part, 4: 16 - part}[mode]) % 12


def d11(lon: float, mode: int = 0) -> int:
    s, deg = _sd(lon)
    part = _t(deg * 0.36666666666666664)
    return (s - part + 11) % 12 if mode == 1 else (part - s + 24) % 12


def _from_start(lon: float, scale: float, n: int, starts: Sequence[int], reverse: bool) -> int:
    s, deg = _sd(lon)
    part = _t(deg * scale)
    if reverse and s & 1:
        part = n - 1 - part
    return (starts[s % len(starts)] + part) % 12


def d12(lon: float, mode: int = 0) -> int:
    s, deg = _sd(lon)
    part = _t(deg * 0.4)
    if mode == 1 and s & 1:
        part = 11 - part
    return (s + part) % 12


def d16(lon: float, mode: int = 0) -> int:
    return _from_start(lon, 0.5333333333333333, 16, (0, 4, 8), mode == 1)


def d20(lon: float, mode: int = 0) -> int:
    return _from_start(lon, 0.6666666666666666, 20, (0, 8, 4), mode == 1)


def d24(lon: float, mode: int = 1) -> int:
    s, deg = _sd(lon)
    part = _t(deg * 0.8)
    if mode == 1:
        return ((4, 3)[s & 1] + part + 24) % 12
    if mode == 2:
        return (part + 28) % 12
    return ((4, 3)[s & 1] + _DIR[s & 1] * part + 24) % 12


def d27(lon: float, mode: int = 0) -> int:
    return _from_start(lon, 0.9, 27, (0, 3, 6, 9), mode == 1)


def d30(lon: float, mode: int = 0) -> int:
    if mode == 1:
        return _t(lon) % 12
    s, deg = _sd(lon)
    if mode == 2:
        return (s + _t(deg)) % 12
    return _unequal(s, deg, (5.0, 10.0, 18.0, 25.0))


def d40(lon: float) -> int:
    s, deg = _sd(lon)
    return ((0, 6)[s & 1] - _t(deg * -1.3333333333333333)) % 12


def d45(lon: float) -> int:
    s, deg = _sd(lon)
    return ((0, 4, 8)[s % 3] - _t(deg * -1.5)) % 12


def d60(lon: float, mode: int = 0) -> int:
    s, deg = _sd(lon)
    part = _t(deg + deg)
    if mode in (1, 2) and s & 1:
        part = 59 - part
    return (part if mode in (2, 3) else part + s) % 12


def d81(lon: float, mode: int = 0) -> int:
    n9 = _t(lon * 0.3)
    s9 = n9 % 12
    f = (lon - n9 * 3.333333333333333) * 9.0
    if mode == 1 and _t(lon * 0.025) & 1:
        f = 30.0 - f
        s9 = _KALACHAKRA[s9]
    x = s9 * 30.0 + f
    s81 = _t(x * 0.3) % 12
    if mode == 1 and _t(x * 0.025) & 1:
        s81 = _KALACHAKRA[s81]
    return s81


def d108(lon: float, mode: int = 1, d9_sign: Optional[int] = None) -> int:
    s, deg = _sd(lon)
    base = (d9(lon) if d9_sign is None else d9_sign) if mode == 1 else s
    return (base - _t(deg * -3.6)) % 12


def d144(lon: float, d12_sign: Optional[int] = None) -> int:
    s, deg = _sd(lon)
    return ((d12(lon) if d12_sign is None else d12_sign) - _t(deg * -4.8)) % 12


def varga_sign(lon: float, division: int, opt: VargaOptions = DEFAULT) -> int:
    """Sign of a rasi longitude in one division with the schemes of ``opt``."""
    if division == 1:
        return _sd(lon)[0]
    if division == 108:
        return d108(lon, opt.d108, d9(lon, opt.d9))
    if division == 144:
        return d144(lon, d12(lon, opt.d12))
    if division in (6, 40, 45):
        return {6: d6, 40: d40, 45: d45}[division](lon)
    fn = {2: d2, 3: d3, 4: d4, 5: d5, 7: d7, 8: d8, 9: d9, 10: d10, 11: d11, 12: d12, 16: d16, 20: d20, 24: d24,
          27: d27, 30: d30, 60: d60, 81: d81}[division]
    return fn(lon, getattr(opt, "d%d" % division))


def varga_signs(lon: float, opt: VargaOptions = DEFAULT) -> Dict[int, int]:
    """Signs in all 23 divisions (in ``DIVISIONS`` order)."""
    return {d: varga_sign(lon, d, opt) for d in DIVISIONS}


# ---------------------------------------------------------------- custom, D-m x n, varga longitudes

_CUSTOM_PERIOD = (1, 2, 2, 2, 2, 2, 3, 3, 4, 4)
_CUSTOM_START = ((0, 0, 0, 0), (0, 6, 0, 0), (0, 8, 0, 0), (0, 4, 0, 0), (0, 10, 0, 0), (0, 2, 0, 0),
                 (0, 4, 8, 0), (0, 8, 4, 0), (0, 3, 6, 9), (0, 9, 6, 3))


def custom_varga(lon: float, n: int, cyclic: bool = False, from_sign: bool = False, reverse_even: bool = False,
                 start: int = 0) -> int:
    """Custom D-n (the user's own division): ``n`` parts per sign, cyclic or counted from Aries / the sign plus the
    start table ``start`` (0 the base,
    1 1st/7th, 2 1st/9th, 3 1st/5th, 4 1st/11th, 5 1st/3rd by odd / even sign, 6 1st/5th/9th, 7 1st/9th/5th
    by modality, 8 1st/4th/7th/10th, 9 1st/10th/7th/4th by element), parts counted from the end in even signs
    (``reverse_even``)."""
    if cyclic:
        return _t(n * lon * 0.03333333333333333) % 12
    s, _ = _sd(lon)
    part = _t((lon - s * 30.0) * n * 0.03333333333333333)
    if reverse_even and s & 1:
        part = n - part - 1
    return (part + _CUSTOM_START[start][s % _CUSTOM_PERIOD[start]] + (s if from_sign else 0)) % 12


def _reversing(division: int, opt: VargaOptions) -> bool:
    """Whether the chosen scheme counts even signs backwards."""
    m = {9: opt.d9 in (2, 3), 2: opt.d2 == 6, 3: opt.d3 in (2, 4), 10: opt.d10 in (2, 3, 4), 24: opt.d24 == 0,
         7: opt.d7 in (1, 2), 16: opt.d16 == 1, 12: opt.d12 == 1, 20: opt.d20 == 1, 27: opt.d27 == 1,
         60: opt.d60 in (1, 2), 11: opt.d11 == 1}
    return m.get(division, False)


def d30_unequal_longitude(deg: float, even_sign: bool) -> float:
    """Degrees in a sign mapped onto 0..30 of its unequal trimsamsa part (BPHS 6.27-28's 5, 5, 8, 7, 5 degrees)."""
    x = 30.0 - deg if even_sign else deg
    if x < 5.0:
        w = 5.0
    elif x < 10.0:
        x, w = x - 5.0, 5.0
    elif x < 18.0:
        x, w = x - 10.0, 8.0
    elif x < 25.0:
        x, w = x - 18.0, 7.0
    else:
        x, w = x - 25.0, 5.0
    if even_sign:
        x = w - x
    return x * 30.0 / w


def varga_longitude(lon: float, division: int, opt: VargaOptions = DEFAULT) -> float:
    """Longitude of a point in a divisional chart (a convention, docs/SOURCES.md section 3): the varga sign plus the
    degrees of ``lon x n`` in their sign (mirrored in even rasi signs for the reversing schemes)."""
    s, deg = _sd(lon)
    x = MULTIPLIER[DIVISIONS.index(division)] * lon
    if not opt.equal_d30_longitudes and division == 30:
        x = d30_unequal_longitude(deg, bool(s & 1))
    if opt.mirror_reversed_longitudes and s & 1 and _reversing(division, opt):
        q = _t(x * 0.03333333333333333)
        x = q * 30.0 + (30.0 - (x - q * 30.0))
    return varga_sign(lon, division, opt) * 30.0 + x % 30.0


def sub_varga(lon: float, m: int, n: int, opt: VargaOptions = DEFAULT) -> int:
    """D-n of D-m: division ``n`` applied to the longitude in the D-m chart."""
    x = varga_longitude(lon, m, opt)
    return int(x / 30.0) if n == 1 else varga_sign(x, n, opt)


# ---------------------------------------------------------------- D-150 nadiamsa

# unequal nadiamsa starts in 1/504 degree, (Deva Keralam's Table 1 gives
# unequal spans; these were not checked against it, docs/SOURCES.md section 3)
D150_BOUNDS = (
    0, 252, 336, 378, 504, 560, 630, 672, 756, 945, 1008, 1120, 1134, 1260, 1344, 1512, 1680, 1764, 1890, 2016,
    2160, 2240, 2268, 2352, 2520, 2646, 2688, 2772, 2800, 2835, 3024, 3150, 3276, 3360, 3402, 3528, 3696, 3780,
    3920, 4032, 4158, 4284, 4320, 4368, 4410, 4480, 4536, 4704, 4725, 4788, 4914, 5040, 5292, 5376, 5544, 5600,
    5670, 5712, 5796, 6048, 6160, 6300, 6384, 6426, 6480, 6552, 6615, 6720, 6804, 6930, 7056, 7182, 7280, 7308,
    7392, 7560, 7728, 7812, 7840, 7938, 8064, 8190, 8316, 8400, 8505, 8568, 8640, 8694, 8736, 8820, 8960, 9072,
    9324, 9408, 9450, 9520, 9576, 9744, 9828, 10080, 10206, 10332, 10395, 10416, 10584, 10640, 10710, 10752, 10800,
    10836, 10962, 11088, 11200, 11340, 11424, 11592, 11718, 11760, 11844, 11970, 12096, 12285, 12320, 12348, 12432,
    12474, 12600, 12768, 12852, 12880, 12960, 13104, 13230, 13356, 13440, 13608, 13776, 13860, 13986, 14000, 14112,
    14175, 14364, 14448, 14490, 14560, 14616, 14742, 14784, 14868)


def d150(lon: float, opt: VargaOptions = DEFAULT) -> Tuple[int, int, int]:
    """(nadiamsa part 0..149, half-part 0..299, nadi index 0..8) of a longitude (Deva Keralam: forward in movable,
    backward in fixed signs)."""
    s, deg = _sd(lon)
    if opt.d150 == 0:
        part = _t(deg * 5.0)
        half = part * 2 + (deg - part * 0.2 >= 0.1)
    else:
        # the table has 150 entries: past 29.5 deg the word after it is read (some large value), which
        # leaves part 149 and its first half
        c = next((i for i in range(1, 150) if deg < D150_BOUNDS[i] * 0.001984126984126984), 150)
        part = c - 1
        if c == 150:
            half = 298
        else:
            lo = D150_BOUNDS[c - 1] * 0.001984126984126984
            half = part * 2 + ((D150_BOUNDS[c] - D150_BOUNDS[c - 1]) * 0.001984126984126984 * 0.5 <= deg - lo)
    return part, half, _nadi_index(s, half, opt.ardha_nadi_ruler)


def _nadi_index(sign: int, half: int, mode: int) -> int:
    if mode == 0:
        return ((0, 3, 6)[sign % 3] + half) % 9
    if mode == 1:
        return ((0, 6, 3)[sign % 3] + half) % 9
    if sign % 3 == 1:
        return (299 - half) % 9
    if sign % 3 == 2:
        return (half - 150) % 9 if half > 149 else (half + 150) % 9
    return half % 9


# ---------------------------------------------------------------- bhava chart (varga slot 28)

def bhava_chart_sign(point_lon_in_varga: float, ref_lon_in_varga: float, ref_is_node: bool = False,
                     lagna_in_middle: bool = True, nodes_reversed: bool = True) -> int:
    """Bhava (chalit) sign of a point in a varga chart: its varga sign moved by one when it is on the other side of
    the reference point's degree (BhavaChartRef, default 2 = the Moon; HouseCuspsInMiddle the lagna in the middle
    of the house, and bhavas from Rahu / Ketu backwards, both on by default).  Longitudes are ``varga_longitude``
    values."""
    s = int(point_lon_in_varga / 30.0) % 12
    deg, ref = point_lon_in_varga % 30.0, ref_lon_in_varga % 30.0
    if lagna_in_middle:
        if ref < 15.0:
            return (s + 1) % 12 if ref + 15.0 <= deg else s
        return (s + 11) % 12 if ref - 15.0 > deg else s
    if nodes_reversed and ref_is_node:
        return (s + 1) % 12 if deg > ref else s
    return (s + 11) % 12 if deg < ref else s


# amsa rulers: the deities of each division's parts (BPHS 6.7-41; the D-150 names of Deva Keralam), per varga
# index, with their counts; D-20 even signs use the second table (BPHS 6.17-21)
AMSA_COUNT = (1, 3, 2, 3, 4, 1, 1, 7, 1, 10, 1, 4, 4, 20, 12, 27, 5, 12, 3, 60, 81, 108, 144, 1, 1, 150)
AMSA_NAMES = {
    1: (
        'Deva', 'Manushya', 'Raakshasa',),
    3: (
        'Naarada', 'Agastya', 'Durvaasa',),
    4: (
        'Sanaka', 'Sananda', 'Kumaara', 'Sanaatana',),
    7: (
        'Kshaara', 'Ksheera', 'Dadhi', 'Ghrita', 'Ikshu Rasa', 'Madya', 'Suddha Jala',),
    9: (
        'Indra', 'Agni', 'Yama', 'Nirriti', 'Varuna', 'Vaayu', 'Kubera', 'Isaana', 'Brahma', 'Ananta',),
    11: (
        'Ganesa', 'Aswini Kumaras', 'Yama', 'Ahi (Sarpa)',),
    12: (
        'Brahma', 'Vishnu', 'Shiva', 'Surya',),
    13: (
        'Kaali', 'Gouri', 'Jayaa', 'Lakshmi', 'Vijayaa', 'Vimalaa', 'Sati', 'Taaraa', 'Jwaalaa-mukhi', 'Swethaa',
        'Lalitaa', 'Bagala-mukhi', 'Pratyangiraa', 'Sachi', 'Roudri', 'Bhavaani', 'Varadaa', 'Jayaa', 'Tripuraa',
        'Sumukhi',),
    14: (
        'Skanda', 'Parasu Raama', 'Anala', 'Viswa-karmaa', 'Bhaga', 'Mitra', 'Maya', 'Antaka', 'Vrisha-dhwaja',
        'Govinda', 'Madana', 'Bheema',),
    15: (
        'Aswini Kumaara', 'Yama', 'Agni', 'Brahma', 'Chandra', 'Shiva', 'Aditi', 'Guru', 'Ahi (Sarpa - Rahu)',
        'Pitris', 'Bhaga', 'Aryamaan', 'Surya', 'Tvashta', 'Vaayu', 'Shakragni', 'Mitra', 'Indra', 'Nirriti',
        'Varuna', 'Viswadeva', 'Govinda', 'Vasu', 'Varuna', 'Ajapada', 'Ahirbudhanya', 'Pooshan',),
    16: (
        'Agni', 'Vaayu', 'Indra', 'Kubera', 'Varuna',),
    17: (
        'Vishnu', 'Chandra', 'Marichi', 'Tvashtaa', 'Brahma', 'Shiva', 'Surya', 'Yama', 'Yaksha', 'Gandharva',
        'Kaala', 'Varuna',),
    18: (
        'Brahma', 'Shiva', 'Vishnu',),
    19: (
        'Ghora', 'Raakshasa', 'Deva', 'Kubera', 'Yaksha', 'Kinnara', 'Bhrashta', 'Kulaghna', 'Garala', 'Vahni',
        'Maayaa', 'Pureeshaka', 'Apaampati', 'Marutvaan', 'Kaala', 'Sarpa', 'Amrita', 'Indu', 'Mridu', 'Komala',
        'Heramba', 'Brahma', 'Vishnu', 'Maheswara', 'Deva', 'Aardra', 'Kali-naasa', 'Kshiteesa', 'Kamalaakara',
        'Gulika', 'Mrityu', 'Kaala', 'Daavaagni', 'Ghora', 'Yama', 'Kantaka', 'Sudhaa', 'Amrita', 'Poorna Chandra',
        'Visha-dagdha', 'Kula-naasa', 'Vamsa-kshaya', 'Utpaata', 'Kaala', 'Saumya', 'Komala', 'Seetala',
        'Karala-danshtra', 'Chandra-mukhi', 'Praveena', 'Kaala Paavaka', 'Dandaayudha', 'Nirmala', 'Saumya',
        'Kroora', 'Ati-seetaka', 'Amrita', 'Payodhi', 'Bhramana', 'Chandra-rekha',),
    2: (
        'Devas  -  Sun', 'Pitris  -  Moon',),
}

# D-60: the shashtyamsas BPHS (6.33-41) calls cruel, by their number 1 .. 60 (in an even sign the count runs back, as amsa_ruler does); the rest are benefic
D60_MALEFIC = frozenset((1, 2, 7, 8, 9, 10, 11, 12, 15, 16, 30, 31, 32, 33, 34, 35, 36, 40, 41, 42, 43, 44, 48, 51, 52, 55, 59))
D60_MEANINGS = (
    'terrible', 'demon', 'divine', 'lord of wealth', 'nature spirit', 'celestial musician', 'fallen', 'destroyer of the family', 'poison', 'fire',
    'illusion', 'filth', 'lord of the waters', 'lord of the winds', 'time, death', 'serpent', 'nectar', 'the moon', 'gentle', 'tender',
    'Ganesha', 'the creator', 'the preserver', 'the great lord', 'divine', 'moist', 'destroyer of strife', 'lord of the earth', 'lotus pond', 'poison',
    'death', 'time, death', 'forest fire', 'terrible', 'lord of death', 'thorn', 'nectar', 'nectar', 'full moon', 'burnt by poison',
    'ruin of the family', 'end of the line', 'calamity', 'time, death', 'gentle', 'tender', 'cool', 'fearsome fangs', 'moon-faced', 'skilful',
    'fire of destruction', 'armed with a rod', 'pure', 'gentle', 'cruel', 'very cool', 'nectar', 'ocean', 'wandering', 'crescent moon',
)
assert len(D60_MEANINGS) == len(AMSA_NAMES[19]) == 60

# Every other varga's amsa rulers: how kind each is (good, middling, bad: the Amsas tab's green, yellow, red; none where the texts make no such
# distinction) and what the name means, by the varga's index. Trimurti: Vishnu sattvic, Brahma rajasic, Shiva tamasic; D-30 by its planets;
# D-20 the goddesses' gentle (saumya) and fierce (ugra) forms.
_G, _M, _B = "good", "middling", "bad"
AMSA_NATURE = {
    1: {"Deva": (_G, "divine"), "Manushya": (_M, "human"), "Raakshasa": (_B, "demonic")},
    2: {"Devas  -  Sun": (None, "the gods: the Sun's hora"), "Pitris  -  Moon": (None, "the ancestors: the Moon's hora")},
    3: {"Naarada": (_G, "the gods' sage and messenger"), "Agastya": (_M, "the sage of the south"), "Durvaasa": (_B, "the sage of wrath")},
    4: {"Sanaka": (None, "the ancient one"), "Sananda": (None, "the joyful one"), "Kumaara": (None, "the youth"), "Sanaatana": (None, "the eternal one")},
    7: {"Kshaara": (_B, "salt water"), "Ksheera": (_G, "milk"), "Dadhi": (_G, "curd"), "Ghrita": (_G, "ghee"), "Ikshu Rasa": (_G, "sugarcane juice"),
        "Madya": (_B, "liquor"), "Suddha Jala": (_G, "pure water")},
    9: {"Indra": (_G, "king of the gods, the east"), "Agni": (_M, "fire, the south-east"), "Yama": (_B, "death, the south"), "Nirriti": (_B, "misfortune, the south-west"),
        "Varuna": (_G, "the waters, the west"), "Vaayu": (_M, "the wind, the north-west"), "Kubera": (_G, "wealth, the north"), "Isaana": (_G, "Shiva, the north-east"),
        "Brahma": (_G, "the creator, the zenith"), "Ananta": (_G, "the endless serpent, the nadir")},
    11: {"Ganesa": (_G, "remover of obstacles"), "Aswini Kumaras": (_G, "the divine healers"), "Yama": (_B, "death"), "Ahi (Sarpa)": (_B, "the serpent")},
    12: {"Brahma": (_M, "the creator"), "Vishnu": (_G, "the preserver"), "Shiva": (_B, "the destroyer"), "Surya": (_M, "the sun")},
    13: {"Kaali": (_B, "the dark one"), "Gouri": (_G, "the fair one"), "Jayaa": (_G, "victory"), "Lakshmi": (_G, "fortune"), "Vijayaa": (_G, "triumph"),
         "Vimalaa": (_G, "the pure one"), "Sati": (_G, "the faithful one"), "Taaraa": (_M, "the saviour"), "Jwaalaa-mukhi": (_B, "the flame-faced"),
         "Swethaa": (_G, "the white one"), "Lalitaa": (_G, "the playful one"), "Bagala-mukhi": (_B, "the one who paralyses"), "Pratyangiraa": (_B, "the lion-faced avenger"),
         "Sachi": (_G, "Indra's queen"), "Roudri": (_B, "the terrible one"), "Bhavaani": (_G, "giver of life"), "Varadaa": (_G, "the giver of boons"),
         "Tripuraa": (_M, "of the three cities"), "Sumukhi": (_G, "the fair-faced"),
         "Dayaa": (_G, "compassion"), "Medhaa": (_G, "intellect"), "Chinna-seershaa": (_B, "the self-beheaded"), "Pisaachini": (_B, "the she-ghoul"),
         "Dhoomavati": (_B, "the smoky widow"), "Maatangi": (_M, "the outcaste's goddess"), "Baalaa": (_G, "the maiden"), "Bhadraa": (_G, "the auspicious one"),
         "Arunaa": (_G, "the dawn"), "Analaa": (_M, "the fiery one"), "Pingalaa": (_M, "the tawny one"), "Chuchchukaa": (_B, "the emaciated one"),
         "Ghoraa": (_B, "the terrible one"), "Vaaraahi": (_M, "the boar-faced"), "Vaishnavi": (_G, "Vishnu's power"), "Sitaa": (_G, "the furrow, Rama's queen"),
         "Bhuvaneswari": (_G, "queen of the worlds"), "Bhairavi": (_B, "the fearsome one"), "Mangalaa": (_G, "the auspicious one"), "Aparaajitaa": (_G, "the unconquered")},
    14: {"Skanda": (_G, "the war god"), "Parasu Raama": (_M, "Rama with the axe"), "Anala": (_M, "fire"), "Viswa-karmaa": (_G, "the divine architect"),
         "Bhaga": (_G, "fortune"), "Mitra": (_G, "friendship"), "Maya": (_M, "the demons' architect"), "Antaka": (_B, "the ender, death"),
         "Vrisha-dhwaja": (_G, "Shiva of the bull banner"), "Govinda": (_G, "Krishna"), "Madana": (_G, "the god of love"), "Bheema": (_B, "the fearsome")},
    15: {"Aswini Kumaara": (_G, "the divine healers"), "Yama": (_B, "death"), "Agni": (_M, "fire"), "Brahma": (_G, "the creator"), "Chandra": (_G, "the moon"),
         "Shiva": (_M, "Rudra, the storm"), "Aditi": (_G, "mother of the gods"), "Guru": (_G, "Brihaspati, the gods' teacher"), "Ahi (Sarpa - Rahu)": (_B, "the serpent"),
         "Pitris": (_G, "the ancestors"), "Bhaga": (_G, "fortune"), "Aryamaan": (_G, "patronage"), "Surya": (_G, "the sun"), "Tvashta": (_G, "the divine craftsman"),
         "Vaayu": (_M, "the wind"), "Shakragni": (_G, "Indra and Agni"), "Mitra": (_G, "friendship"), "Indra": (_G, "king of the gods"), "Nirriti": (_B, "misfortune"),
         "Varuna": (_G, "the waters"), "Viswadeva": (_G, "all the gods"), "Govinda": (_G, "Vishnu"), "Vasu": (_G, "the bright gods"), "Ajapada": (_M, "the one-footed goat"),
         "Ahirbudhanya": (_M, "the serpent of the deep"), "Pooshan": (_G, "the nourisher")},
    16: {"Agni": (_B, "fire: Mars"), "Vaayu": (_B, "wind: Saturn"), "Indra": (_G, "king of the gods: Jupiter"), "Kubera": (_G, "wealth: Mercury"), "Varuna": (_G, "the waters: Venus")},
    17: {"Vishnu": (_G, "the preserver"), "Chandra": (_G, "the moon"), "Marichi": (_G, "the sage of light"), "Tvashtaa": (_G, "the divine craftsman"),
         "Brahma": (_M, "the creator"), "Shiva": (_B, "the destroyer"), "Surya": (_M, "the sun"), "Yama": (_B, "death"), "Yaksha": (_M, "nature spirit"),
         "Gandharva": (_G, "celestial musician"), "Kaala": (_B, "time, death"), "Varuna": (_G, "the waters")},
    18: {"Brahma": (_M, "the creator"), "Shiva": (_B, "the destroyer"), "Vishnu": (_G, "the preserver")},
}
AMSA_D20_EVEN = (
     'Dayaa', 'Medhaa', 'Chinna-seershaa', 'Pisaachini', 'Dhoomavati', 'Maatangi', 'Baalaa', 'Bhadraa', 'Arunaa',
     'Analaa', 'Pingalaa', 'Chuchchukaa', 'Ghoraa', 'Vaaraahi', 'Vaishnavi', 'Sitaa', 'Bhuvaneswari', 'Bhairavi',
     'Mangalaa', 'Aparaajitaa')
# D-150 names: D150NamePreference 1 / otherwise (default 0)
AMSA_D150 = ((
         'Vasudha', 'Vaishnavi', 'Braahmi', 'Kaalakoota', 'Sankari', 'Sadaakari', 'Samaa', 'Saumya', 'Suraa',
         'Maayaa', 'Manohara', 'Maadhavi', 'Manjuswana', 'Ghora', 'Kumbhini', 'Kutila', 'Prabhaa', 'Paraa',
         'Payaswini', 'Maalaa', 'Jagati', 'Jarjhari', 'Dhruva', 'Musala', 'Mudgara', 'Paasaa', 'Chambaka',
         'Daamini', 'Mahi', 'Kalusha', 'Kamala', 'Kaantaa', 'Kaalaa', 'Karikara', 'Kshamaa', 'Durdharaa',
         'Durbhagaa', 'Viswa', 'Visirna', 'Vikata Viswala', 'Aavilaa', 'Vidruma', 'Sukhada', 'Snigdha', 'Sodara',
         'Surasundari', 'Amritapraasini', 'Karaalaa', 'Kaamadrik', 'Kara Veerani', 'Gahwaraa', 'Kundini', 'Kundini',
         'Roudra/Kaanthaa', 'Vishaa', 'Vishanaasini', 'Nirmada', 'Seetala', 'Nimnaa', 'Preeta', 'Priyavaasini',
         'Maanaghna', 'Durbhaga', 'Chitra', 'Chitrini', 'Chiranjeevani', 'Viroopa/Bhoopa', 'Gadaaharaa', 'Naalaa',
         'Nalini', 'Nirmalaa', 'Nadee', 'Sadamritamsukala', 'Chapalaa', 'Saankuraa', 'Trailokya Mohanakari',
         'Mahaamaayaa', 'Suseetalaa', 'Sumataa/Subhagaa', 'Suprabhaa', 'Sobhaa', 'Sobhana', 'Sivadaa', 'Sivaa',
         'Balaa', 'Jwaalaa', 'Gadaa', 'Gaadaa', 'Nootana', 'Sumanoharaa', 'Somavalli', 'Somalataa', 'Mangala',
         'Mudrikaa', 'Sootaa', 'Mokshapavarga', 'Valaya', 'Navaneetaa', 'Nisaakari', 'Nivriti', 'Nigadaa',
         'Saaraa/Saura', 'Sangeeta', 'Sumathaa', 'Viswambharaa', 'Kumaari', 'Kokilaa', 'Kunjarakriti', 'Aindiraa',
         'Swaahaa', 'Swaraa', 'Vahni', 'Peethi', 'Rakshajala', 'Plava', 'Madiraa', 'Maitri', 'Haarini', 'Harini',
         'Marut', 'Dhananjaya', 'Dhanakari', 'Dhanadaa', 'Mrichchaya', 'Ambujaa', 'Isaani', 'Thoolini', 'Roudri',
         'Sivaa', 'Sivakari', 'Kalaa', 'Kunda', 'Mukunda', 'Bharata', 'Pasitha', 'Kandini', 'Smaraa', 'Kunthala',
         'Kokila', 'Paapa', 'Kaamini', 'Kalasodbhava', 'Viraprasoo', 'Sankara', 'Satayajnaa', 'Sadaavari',
         'Brahvi/Virahapa', 'Paatalini', 'Pankajaa', 'Parameswari'),
             (
         'Vasudha', 'Vaishnavi', 'Braahmi', 'Kaalakoota', 'Sankari', 'Sudhakarasama', 'Saumya', 'Suraa', 'Maayaa',
         'Manohara', 'Maadhavi', 'Manjuswana', 'Ghora', 'Kumbhini', 'Kutila', 'Prabhaa', 'Paraa', 'Payaswini',
         'Maalaa', 'Jagati', 'Jarjhari', 'Dhruva', 'Musala', 'Mudgala', 'Paasaa', 'Chambaka', 'Daamini', 'Mahi',
         'Kalusha', 'Kamala', 'Kaantaa', 'Kaalaa', 'Karikara', 'Kshamaa', 'Durdharaa', 'Durbhagaa', 'Viswa',
         'Visirna', 'Vihwala', 'Anilaa', 'Bheema', 'Sukhaprada', 'Snigdha', 'Sodara', 'Surasundari',
         'Amritapraasini', 'Kaalaa/Karaalaa', 'Kaamadrikkara Veerini', 'Gahwaraa', 'Kundini', 'Kaanthaa',
         'Vishaakhya (Visha)', 'Vishanaasini', 'Nirmada', 'Seetala', 'Nimnaa', 'Preeta', 'Priyavivardhini',
         'Manaadha (Maanaghna)', 'Durbhaga', 'Chitra', 'Vichitra', 'Chiranjeevini', 'Bhoopa', 'Gadaaharaa',
         'Naalaa', 'Gaalavee', 'Nirmalaa', 'Nadee', 'Sudhaa', 'Mritamsuga', 'Kaali', 'Kaalikaa', 'Kalushaankuraa',
         'Trailokya Mohanakari', 'Mahaamaayaa', 'Suseetalaa', 'Sukhadaa', 'Suprabhaa', 'Sobhaa', 'Sobhana',
         'Sivadaa', 'Sivaa', 'Balaa', 'Jwaalaa', 'Gadaa', 'Gaadaa', 'Sootana (Nootana)', 'Sumanoharaa', 'Somavalli',
         'Somalataa', 'Mangala', 'Mudrikaa', 'Sudhaa', 'Melaa', 'Apavargaa', 'Pasyathaa', 'Navaneetaa',
         'Nisaachari', 'Nivriti', 'Nirgatha', 'Saaraa', 'Saamagaa', 'Saamadaa', 'Samaa', 'Viswambharaa', 'Kumaari',
         'Kokilaa', 'Kunjarakriti', 'Indra', 'Swaahaa', 'Swadhaa', 'Vahni', 'Peetha', 'Yakshi', 'Achalaprabhaa',
         'Saarini', 'Madhuraa', 'Maitri', 'Harini', 'Haarini', 'Marutaa', 'Dhananjaya', 'Dhanakari', 'Dhanadaa',
         'Kachchapaa', 'Ambujaa', 'Isaani', 'Soolini', 'Roudri', 'Sivaasivakari', 'Kalaa', 'Kunda', 'Mukunda',
         'Bharata', 'Kadali', 'Smaraa', 'Basita', 'Kodala', 'Kokilamsa', 'Kaamini', 'Kalasodbhava', 'Viraprasoo',
         'Sangaraa', 'Satayajnaa', 'Sataavari', 'Sragvi', 'Paatalini', 'Naagapankaja', 'Parameswari'))


def amsa_ruler(lon: float, varga: int, opt: VargaOptions = DEFAULT, d150_names: int = 0) -> Tuple[int, int, str]:
    """(part, ruler index, ruler) of a longitude in the varga with the varga index
    ``varga`` (1 D-9, 2 D-2 .. 19 D-60, 25 D-150).  The view prints part + 1 and index + 1."""
    s, deg = _sd(lon)
    part = _t(MULTIPLIER[varga] * deg * 0.03333333333333333)
    if varga == 16:                                  # D-30 by the unequal parts
        bounds = (25.0, 20.0, 12.0, 5.0) if s & 1 else (25.0, 18.0, 10.0, 5.0)
        k = next((i for i, b in enumerate(bounds) if deg >= b), 4)
        idx = k if s & 1 else 4 - k
    elif varga == 25:
        part = d150(lon, opt)[0] % 150
        idx = part if s % 3 == 0 else 149 - part if s % 3 == 1 else (part + 75 if part < 75 else part - 75)
    else:
        idx = part
        if varga not in (1, 3, 4, 11, 13, 15, 17) and s & 1:
            idx = MULTIPLIER[varga] - part - 1
        if varga in (1, 3, 18):
            idx += s % 3
    idx %= AMSA_COUNT[varga]
    names = (AMSA_D150[0 if d150_names == 1 else 1] if varga == 25 else
             AMSA_D20_EVEN if varga == 13 and s & 1 else AMSA_NAMES.get(varga, ("",) * AMSA_COUNT[varga]))
    return part, idx, names[idx]
