"""nakshatra: part of dasa_systems (split from one module; see __init__.py)."""
from typing import Any, Dict, List, Tuple
from .. import sign_strength as S
from .chart import JChart, NAK, NAK28_START, periods

# ---------------------------------------------------------------- nakshatra dasas (slots 0 .. 12, 69 .. 72)

# slot: (name, lords, years, nakshatra -> start index, mahadasas) from the builders' stack tables
NAKSHATRA_DASAS = {
    "yogini": ([3, 4, 7, 6, 8, 2, 1, 5], [4, 5, 6, 7, 8, 1, 2, 3], lambda k: k, 24),             # BPHS 46.195-199
    "dwisaptati": ([1, 2, 3, 4, 5, 6, 7, 8], [9] * 8, lambda k: (k + 9) % 27, 8),               # BPHS 46.37-39
    "shattrimsa": ([2, 1, 5, 3, 4, 7, 6, 8], [1, 2, 3, 4, 5, 6, 7, 8], lambda k: (k + 6) % 27, 24),  # BPHS 46.42-43
    "dwadasottari": ([1, 5, 9, 4, 8, 3, 7, 2], [7, 9, 11, 13, 15, 17, 19, 21], lambda k: (53 - k) % 27, 8),  # BPHS 46.27-28
    "chaturaseeti": ([1, 2, 3, 4, 5, 6, 7], [12] * 7, lambda k: (k + 13) % 27, 7),               # BPHS 46.35-36
    "sataabdika": ([1, 2, 6, 4, 5, 3, 7], [5, 5, 10, 10, 20, 20, 30], lambda k: (k + 1) % 27, 7),  # BPHS 46.31-34
    "shodasottari": ([1, 3, 5, 7, 9, 2, 4, 6], [11, 12, 13, 14, 15, 16, 17, 18], lambda k: (k + 20) % 27, 8),  # BPHS 46.23-26
    "panchottari": ([1, 4, 7, 3, 6, 2, 5], [12, 13, 14, 15, 16, 17, 18], lambda k: (k + 11) % 27, 7),  # BPHS 46.29-30
}
# Ashtottari (BPHS 46.17-22) and Shashtihayani (BPHS 46.40-41): groups of the 28 nakshatras, balance over the group
GROUP_DASAS = {
    "ashtottari": ([1, 2, 3, 4, 7, 5, 8, 6], [4, 3, 4, 3, 4, 3, 4, 3], [6, 15, 8, 17, 10, 19, 12, 21], 5),
    "shashtihayani": ([5, 1, 3, 2, 4, 6, 7, 8], [3, 4, 3, 4, 3, 4, 3, 4], [10, 10, 10, 6, 6, 6, 6, 6], 0),
}
VIMSOTTARI = ([9, 6, 1, 2, 3, 8, 5, 7, 4], [7, 20, 6, 10, 7, 18, 16, 19, 17])   # Ketu .. Mercury (BPHS 46.12-16)


def _cycle(lords, years, k, n, reverse=False):
    m, d = len(lords), -1 if reverse else 1
    return [lords[(k + d * i) % m] for i in range(n)], [years[(k + d * i) % m] for i in range(n)]


def nak_ad_position(i: int, j: int, n: int, method: int = 0, reverse: bool = False) -> int:
    """The position of the ``j``-th antardasa lord of a mahadasa at position ``i`` of
    the ``n`` lords. ``method`` NaksDasaADMethodPreference: 0 i + j (from the lord on), 1 i - j, 2 i + 1 + j,
    3 i + 1 - j, 4 i - 1 + j, 5 i - 1 - j; AntiZodiacalDasa negates ``j``. Method 0 is BPHS 51.2's order."""
    j = -j if reverse else j
    return (i + (j, -j, 1 + j, 1 - j, -1 + j, -1 - j)[method]) % n


def _forward_subs(lords, method=0, reverse=False):
    """The antardasa lords of a nakshatra dasa (default: from the mahadasa lord onwards)."""
    n = len(lords)
    return lambda i, lord: [lords[nak_ad_position(lords.index(lord), j, n, method, reverse)] for j in range(n)]


def _by_lord(lords, years):
    t = [0.0] * 10
    for p, y in zip(lords, years):
        t[p] = y
    return t, float(sum(years))


# Nakshatra dasa seeds (Settings > Nakshatra dasas > Seed; BPHS 46.16, PVR 16.4):
# point indices; seeds 1 / 2 / 3 are the Moon's 5th, 4th and 8th nakshatras (Utpanna, Kshema, Adhana).
DASA_SEEDS = [2, 2, 2, 2, 0, 31, 32, 36, 1, 3, 4, 5, 6, 7, 8, 9, 20, 19, 17, 103, 104]
SEED_SHIFT = {1: (4, 53.333333333333336), 2: (3, 40.0), 3: (7, 93.33333333333334)}


def dasa_seed(seed: int, lon: float, nak: int, correction: float = 0.0) -> Tuple[int, float, float]:
    """For one seed: (nakshatra, fraction left, longitude) of the seed's point (rasi longitude ``lon``, chart
    nakshatra ``nak``) with the dasa ayanamsa correction (the sidereal nakshatras of a tropical chart; 0 unless
    that option is set) added; the fraction left is taken before the Utpanna / Kshema / Adhana shift, and from
    the chart's own nakshatra."""
    x = (lon + correction) % 360.0
    left = 1.0 - (x * 0.07500000000000001 - nak)
    if seed in SEED_SHIFT:
        k, arc = SEED_SHIFT[seed]
        return (nak + k) % 27, left, (x + arc) % 360.0
    return nak, left, x


def _seed(jc: JChart, seed: int) -> Tuple[int, float, float]:
    """(nakshatra, fraction left, longitude) of start point ``seed`` (NakshatraDasaStartPoint)."""
    lon = jc.point(DASA_SEEDS[seed])
    return dasa_seed(seed, lon, int(((lon + jc.correction) % 360.0) / NAK), jc.correction)


def _conditional(to_date, lords, years, k, n, balance, reverse=False, ad_method=0, tribhagi=False):
    """Mahadasas from lord position ``k`` (backwards when ``reverse``, AntiZodiacalDasa, with the balance
    1 - ``balance``), the first one cut to the balance; antardasas by ``nak_ad_position``.  ``tribhagi`` (popup
    "Use Tribhagi variation"; not for Yogini, Shattrimsa, Kalachakra): the cycle three
    times at a third of the years."""
    ls, ys = _cycle(lords, years, k, n, reverse)
    if tribhagi:
        ls, ys = ls * 3, [y / 3.0 for y in ys] * 3
    by, tot = _by_lord(lords, years)
    if reverse:
        balance = 1.0 - balance
    return periods(to_date, ls, ys, -(1 - balance) * ys[0], _forward_subs(lords, ad_method, reverse), by, tot)


def nakshatra_dasa(name: str, jc: JChart, to_date, shift: int = 0, reverse: bool = False,
                   ad_method: int = 0, seed: int = 0, tribhagi: bool = False, progress: int = 0) -> List[Dict[str, Any]]:
    """The simple conditional nakshatra dasas (Moon's nakshatra; balance = fraction of it still to run).
    Per-slot options: ``shift`` NakshatraDasaShift (the start ``shift`` lords back in the cycle), ``reverse``
    AntiZodiacalDasa, ``ad_method`` NaksDasaADMethodPreference, ``seed`` NakshatraDasaStartPoint.
    ``progress``: a Tajaka chart's years since birth added to the natal seed's nakshatra (``tajaka_dasa``)."""
    lords, years, idx, n = NAKSHATRA_DASAS[name]
    nak, left, _ = _seed(jc, seed)
    nak = (nak + progress) % 27
    if tribhagi and name in ("yogini", "shattrimsa"):
        tribhagi = False
    return _conditional(to_date, lords, years, (idx(nak) - shift) % 27, n, left, reverse, ad_method, tribhagi)


def vimsottari_dasa(jc: JChart, to_date, shift: int = 0, reverse: bool = False,
                    ad_method: int = 0, seed: int = 0, tribhagi: bool = False, progress: int = 0) -> List[Dict[str, Any]]:
    """Vimsottari (BPHS 46.12-16) through the same path as the other nakshatra dasas, with the per-slot options
    (``dashas.compute_vimshottari_tree`` is the general API); with ``tribhagi`` each mahadasa also carries its
    nakshatra (``nak``, from the seed's on).  The natal chart with ``progress`` in a
    Tajaka chart is Mudda dasa."""
    lords, years = VIMSOTTARI
    nak, left, _ = _seed(jc, seed)
    nak = (nak + progress) % 27
    out = _conditional(to_date, lords, years, (nak - shift) % 9, 9, left, reverse, ad_method, tribhagi)
    if tribhagi:
        for i, md in enumerate(out):
            md["nak"] = (nak + (-i if reverse else i)) % 27
    return out


# The values taken past the 28 starts of NAK28_START when a group's index runs off their end:
# the 28 spans, then the Pushkara degrees (JP 1.58 and C. S. Patel's), kept for ``past_table``
PAST_TABLE_STARTS = [40.0 / 3.0] * 20 + [10.0, 4.227777777777778, 12.43888888888889] + [40.0 / 3.0] * 5 + [
    21.0, 14.0, 18.0, 8.0, 19.0, 9.0, 24.0, 11.0, 23.0, 14.0, 19.0, 9.0, 21.0, 14.0, 24.0, 7.0, 21.0, 14.0, 24.0, 7.0,
    21.0, 14.0, 24.0, 7.0]


def group_dasa(name: str, jc: JChart, to_date, shift: int = 0, ad_method: int = 0,
               seed: int = 0, tribhagi: bool = False, progress: int = 0, past_table: bool = False) -> List[Dict[str, Any]]:
    """Ashtottari / Shashtihayani: the Moon's group of nakshatras (28, with Abhijit); ``shift`` NakshatraDasaShift
    moves the Moon ``shift`` nakshatras back, ``ad_method`` as ``nak_ad_position``, ``seed`` the start point's
    longitude instead of the Moon's (AntiZodiacalDasa does not apply); ``progress`` (Tajaka) moves the first
    group's first nakshatra on (BPHS 46.17-22).  ``past_table``: without wrapping that nakshatra's index
    and takes the first group's start from past its table (``PAST_TABLE_STARTS``, progress up to 79 - first)."""
    lords, groups, years, first = GROUP_DASAS[name]
    moon, s = (_seed(jc, seed)[2] - shift * NAK) % 360.0, first + progress
    off = PAST_TABLE_STARTS[s - 28] - NAK28_START[s % 28] if past_table and s >= 28 else 0.0
    ends = NAK28_START[1:] + [360.0]
    for g in range(8):
        lo, hi = NAK28_START[s % 28] + off, ends[(s + groups[g] - 1) % 28] + off
        span = (hi - lo) % 360.0
        if (moon - lo) % 360.0 < span:  # the Moon on the group's arc
            return _conditional(to_date, lords, years, g, 8, 1 - ((moon - lo) % 360.0) / span, ad_method=ad_method,
                                tribhagi=tribhagi)
        s += groups[g]
    raise AssertionError("nakshatra groups cover the zodiac")


def saptarshi_dasa(jc: JChart, to_date, progress: int = 0) -> List[Dict[str, Any]]:
    """Saptarshi nakshatra dasa: 27 nakshatras backwards from the lagna's (+ ``progress``), 10 years
    each, from birth; antardasas the 10 nakshatras backwards from the period's, a year each."""
    k = int(jc.lons[0] / NAK) + progress
    ls = [(k - i) % 27 for i in range(27)]
    return periods(to_date, ls, [10.0] * 27, 0.0, lambda i, lord: [(lord - j) % 27 for j in range(10)])


def _elongation(jc: JChart) -> float:
    return (jc.lons[2] - jc.lons[1]) % 360.0


# tithi -> lord: Sun .. Rahu from each paksha's start, Saturn on the 15th and Rahu on the 30th (a convention,
# docs/SOURCES.md section 8)
TITHI_LORD = [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 8]
YOGA_LORD = [7, 4, 9, 6, 1, 2, 3, 8, 5]           # yoga % 9: the Vimsottari lord of the nakshatra 7 on (Vishkambha: Pushya's)


def _progressed_lord(lord: int, progress: int, n: int) -> int:
    """A Tajaka chart's start lord: the natal lord's point number moved on by
    the years, among points 1 .. ``n``."""
    return (lord + progress - 1) % n + 1


def tithi_ashtottari_dasa(jc: JChart, to_date, progress: int = 0) -> List[Dict[str, Any]]:
    """Tithi Ashtottari: Ashtottari lords from the janma tithi's lord, balance of the tithi
    (the tithi of the plain Moon - Sun angle); antardasas from the lord after the
    mahadasa lord."""
    lords, years = [6, 1, 2, 3, 4, 7, 5, 8], [21, 6, 15, 8, 17, 10, 19, 12]
    e = _elongation(jc)
    t = int(e / 12.0)
    k = lords.index(_progressed_lord(TITHI_LORD[t], progress, 8))
    ls, ys = _cycle(lords, years, k, 9)
    by, tot = _by_lord(lords, years)
    sub = lambda i, lord: [lords[(lords.index(lord) + 1 + j) % 8] for j in range(8)]
    return periods(to_date, ls, ys, -(1 - (12.0 * (t + 1) - e) / 12.0) * ys[0], sub, by, tot)


def tithi_yogini_dasa(jc: JChart, to_date, progress: int = 0) -> List[Dict[str, Any]]:
    """Tithi Yogini: Yogini lords from the janma tithi's lord, balance of the tithi."""
    lords, years = [3, 4, 7, 6, 8, 2, 1, 5], [4, 5, 6, 7, 8, 1, 2, 3]
    e = _elongation(jc)
    t = int(e / 12.0)
    return _conditional(to_date, lords, years, lords.index(_progressed_lord(TITHI_LORD[t], progress, 8)), 24,
                        (12.0 * (t + 1) - e) / 12.0)


def yoga_vimsottari_dasa(jc: JChart, to_date, progress: int = 0) -> List[Dict[str, Any]]:
    """Yoga Vimsottari: Vimsottari from the lord of the yoga (Sun + Moon), balance of the yoga."""
    lords, years = VIMSOTTARI
    y = (jc.lons[1] + jc.lons[2]) % 360.0 / NAK
    return _conditional(to_date, lords, years, lords.index(_progressed_lord(YOGA_LORD[int(y) % 9], progress, 9)),
                        10, 1 - (y - int(y)))


def karana_chaturaseeti_dasa(jc: JChart, to_date, progress: int = 0, event: bool = False) -> List[Dict[str, Any]]:
    """Karana Chaturaseeti sama: Sun .. Saturn, 12 years each, from the karana's lord (Bava Sun ..
    Vishti Saturn; Shakuni, Chatushpada, Naga, Kimstughna: lords of the 1st, 4th, 7th, 10th from the lagna,
    the lords of those kendras) moved on by ``progress``; balance of the karana.  An event chart (``event``) lists
    8 periods, the first lord again."""
    e = _elongation(jc)
    k = int(e / 6.0)
    kind = 10 if k == 0 else 7 + (k - 57) if k >= 57 else (k - 1) % 7     # Bava 0 .. Kimstughna 10 (SS 2.67-69)
    lord = kind + 1 if kind < 7 else S.SIGN_LORDS[(jc.signs[0][0] + kind * 3 + 123) % 12]
    return _conditional(to_date, [1, 2, 3, 4, 5, 6, 7], [12] * 7, lord - 1 + progress, 8 if event else 7,
                        1 - (e / 6.0 - k))
