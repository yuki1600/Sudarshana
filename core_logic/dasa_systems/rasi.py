"""rasi: part of dasa_systems (split from one module; see __init__.py)."""
from typing import Any, Dict, List, Optional
from .. import sign_strength as S
from ..utils import norm360
from .chart import JChart, NAK, VARGA_NUMBER, _md, periods
from .nakshatra import VIMSOTTARI, _cycle

# ---------------------------------------------------------------- rasi dasas

NARAYANA_STEPS = ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],        # movable: every sign
                  [0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7],        # fixed: every 6th
                  [0, 4, 8, 9, 1, 5, 6, 10, 2, 3, 7, 11])        # dual: kendras, then trines of them


def _direction(sign: int, odd_forward: int, override: int) -> int:
    """Rasi dasa direction from a sign's parity (+1 / -1), forced forward (1) or reversed (2) by Saturn / Ketu."""
    if override == 1:
        return 1
    return -odd_forward if override == 2 else odd_forward


def narayana_dasa(jc: JChart, to_date, varga: int = 0, option: int = 0) -> List[Dict[str, Any]]:
    """Narayana dasa (PVR ch. 18) of varga index ``varga``: from the stronger of the lagna (in a varga: the varga
    sign of the lord of that varga's own house counted from the rasi lagna) and its 7th; order by
    the sign's modality, direction by
    (sign + 8) // 3 parity; years = signs to the lord (``sign_strength._sign_count``), second cycle 12 - years;
    antardasas from the sign of the lord of the stronger of the sign / its 7th, 1/12 each.
    ``option`` (the Narayana dasa options): 1 no "stronger of the sign and its 7th" for the seed or the
    antardasas, years by ``_narayana_years_alt`` (lord in the 7th: 10); 2 10 years each, one
    cycle of 12."""
    sg, lons = jc.signs[varga], jc.lons
    seed = sg[0]
    if varga:
        seed = sg[S.dasa_sign_lord((VARGA_NUMBER[varga] + 11 + jc.signs[0][0]) % 12, sg)]
    if option == 0:
        return _narayana_like(to_date, sg, lons, _narayana_order(S.stronger_of_7th(seed, sg, lons), sg, lons))
    if option == 2:
        ls = _narayana_order(S.stronger_of_7th(seed, sg, lons), sg, lons)
        return periods(to_date, ls, [10.0] * 12, 0.0, _from_lord_of_stronger(sg, lons))
    ls = _narayana_order(seed, sg, lons)
    ys = [float(_narayana_years_alt(s, sg)) for s in ls]
    return periods(to_date, ls * 2, ys + [12 - y for y in ys], 0.0, _from_lord_of_stronger(sg, lons, False))


def _narayana_years_alt(sign: int, sg) -> int:
    """Narayana option 1: signs from the lord's sign to the dasa sign (forward when the lord's sign
    is in Ar..Ge / Li..Sg), 10 when the lord is in the 7th, +1 exalted / -1 debilitated."""
    lord = S.dasa_sign_lord(sign, sg)
    ls = sg[lord]
    n = ((sign - ls) if (ls // 3) % 2 == 0 else (ls - sign)) % 12 or 12
    if (ls + 6) % 12 == sign:
        n = 10
    if S.EXALTATION[lord] == ls and n < 12:
        n += 1
    if S.DEBILITATION[lord] == ls and n > 0:
        n -= 1
    return n


def sudasa(jc: JChart, to_date, ad_option: int = 4, sl_lon: Optional[float] = None) -> List[Dict[str, Any]]:
    """Sudasa (PVR ch. 20): from the strongest kendra of the Sree Lagna's sign, then the strongest panapara and
    apoklima (rule A), direction by the SL sign's parity; Narayana years, the first one cut to the part of the
    SL's sign still to run; antardasas 1/12 each. ``ad_option`` SudasaADOption: the antardasas
    start from 0 the sign of the lord of the stronger of the sign and its 7th, 1 / 2 the sign itself, 3 / 4
    (default) that stronger sign; 1 and 3 go by kendras (0 3 6 9 1 4 ..), the others sign by sign; direction by
    the start's parity, Saturn / Ketu of the sign compared.  ``sl_lon``: the Sree Lagna whose part left cuts the
    first period; it is the natal chart's, so in a Tajaka chart it is the natal one."""
    sg, lons = jc.signs[0], jc.lons
    sl = int(jc.special["Sree_Lagna"] / 30.0) % 12
    sl_lon = jc.special["Sree_Lagna"] if sl_lon is None else sl_lon
    d = _direction(sl, -1 if sl % 2 else 1, S.direction_override(sl, sg, lons))
    ls = []
    base = sl
    for g in range(3):
        best = base
        for k in (3, 6, 9):
            best = S.stronger_sign(best, (base + k) % 12, sg, lons)
        ls += [(best + k * d) % 12 for k in (0, 3, 6, 9)]
        base = best + 1          # not wrapped: after Pisces the comparison takes a "sign 12" (no grahas, lord 0)
    ys = [float(S._sign_count(sg[S.dasa_sign_lord(s, sg)], s, S.dasa_sign_lord(s, sg))) for s in ls]
    ys[0] *= 1 - (sl_lon % 30.0) / 30.0

    def sub(i, sign):
        ref = sign if ad_option in (1, 2) else S.stronger_of_7th(sign, sg, lons)
        start = sg[S.dasa_sign_lord(ref, sg)] if ad_option == 0 else ref
        dd = _direction(ref, -1 if start % 2 else 1, S.direction_override(ref, sg, lons))
        steps = KENDRA_ORDER if ad_option in (1, 3) else range(12)
        return [(start + k * dd) % 12 for k in steps]
    return periods(to_date, ls * 2, ys + [12 - y for y in ys], 0.0, sub)


def _from_lord_of_stronger(sg, lons, stronger: bool = True):
    """Narayana-type antardasas (also Niryaana shoola, Sthira, Mandooka, Yogardha ...): 12 signs from the sign of the
    lord of the stronger of the mahadasa sign and its 7th (the sign itself when not ``stronger``), direction by
    that sign's parity and Saturn / Ketu."""
    def sub(i, sign):
        s7 = S.stronger_of_7th(sign, sg, lons) if stronger else sign
        start = sg[S.dasa_sign_lord(s7, sg)]
        dd = _direction(s7, -1 if start % 2 else 1, S.direction_override(s7, sg, lons))
        return [(start + j * dd) % 12 for j in range(12)]
    return sub


def _forward_from(f):
    return lambda i, sign: [(f(sign) + j) % 12 for j in range(12)]


def shoola_dasa(jc: JChart, to_date, ad_start: int = 1) -> List[Dict[str, Any]]:
    """Shoola dasa (BPHS 46.181-182; PVR ch. 23): 9 years each, forward from the stronger of the lagna and its 7th; antardasas
    forward from (ShoolaDasaAntardasaStart) 0 the sign, 1 (default) the stronger of the sign and its
    7th, 2 the sign of that stronger sign's lord."""
    sg, lons = jc.signs[0], jc.lons
    seed = S.stronger_of_7th(sg[0], sg, lons)
    ls = [(seed + i) % 12 for i in range(12)]

    def start(s):
        if ad_start == 0:
            return s
        s7 = S.stronger_of_7th(s, sg, lons)
        return sg[S.dasa_sign_lord(s7, sg)] if ad_start == 2 else s7
    return periods(to_date, ls, [9.0] * 12, 0.0, _forward_from(start))


NAVAMSA_EVEN = [7, 6, 5, 10, 9, 2, 1, 0, 11, 4, 3, 8]      # Navamsa dasa: even signs start elsewhere


def navamsa_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Navamsa dasa (JUS 2.3): 9 years each, forward from the stronger of the lagna and its 7th (an even sign
    mapped by the table at the builder's stack); antardasas the same way from each sign."""
    sg, lons = jc.signs[0], jc.lons

    def start(s):
        s = S.stronger_of_7th(s, sg, lons)
        return NAVAMSA_EVEN[s] if s % 2 else s
    seed = start(sg[0])
    ls = [(seed + i) % 12 for i in range(12)]
    return periods(to_date, ls, [9.0] * 12, 0.0, _forward_from(start))


def niryaana_shoola_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Niryaana shoola dasa (JUS 2.2-2.3; PVR ch. 22): from the stronger of the 2nd and 8th, direction by its parity and
    Saturn / Ketu; movable 7, fixed 8, dual 9 years."""
    sg, lons = jc.signs[0], jc.lons
    seed = S.stronger_of_7th((sg[0] + 7) % 12, sg, lons)
    d = _direction(seed, -1 if seed % 2 else 1, S.direction_override(seed, sg, lons))
    ls = [(seed + i * d) % 12 for i in range(12)]
    return periods(to_date, ls, [7.0 + s % 3 for s in ls], 0.0, _from_lord_of_stronger(sg, lons))


def brahma_planet(jc: JChart) -> int:
    """Brahma (BPHS 46.170-173; JUS 2.1): the lord of the 8th from the atmakaraka if it is there; otherwise
    the strongest of the lords of the 6th, 8th, 12th from
    the stronger of the lagna and the 7th that sit in odd signs in its 7th .. 12th; failing that from the other
    sign, then those in odd signs, then all three; Saturn / Rahu / Ketu become Mars / Mercury / Jupiter."""
    sg, lons = jc.signs[0], jc.lons
    # first the 8th from the atmakaraka (the 6th if a node is in either): its lord in that sign is Brahma
    ak = sg[jc.atmakaraka()]
    h = (ak + 7) % 12
    if h in (sg[8], sg[9]) or ak in (sg[8], sg[9]):
        h = (ak + 5) % 12
    lord = S.sign_lord(h, sg, lons)
    if sg[lord] == h:
        return lord
    lag, sev = sg[0], (sg[0] + 6) % 12
    a = S.stronger_sign(lag, sev, sg, lons)
    b = sev if a == lag else lag
    lords = lambda base: [S.sign_lord((base + k) % 12, sg, lons) for k in (5, 7, 11)]
    tests = [(a, True), (b, True), (a, False), (b, False)]
    cands = []
    for base, house in tests:
        cands = [p for p in lords(base) if sg[p] % 2 == 0 and (not house or (sg[p] - base) % 12 > 5)]
        if cands:
            break
    if not cands:
        cands = lords(a)
    best = cands[0]
    for p in cands[1:]:
        best = S.stronger_by_dignity(best, p, sg, lons)
    best = {7: 3, 8: 4, 9: 5}.get(best, best)
    return best if 1 <= best <= 6 else 1


def brahma_dasa(jc: JChart, to_date, seed: Optional[int] = None) -> List[Dict[str, Any]]:
    """Brahma dasa (BPHS 46.170-173; JUS 2.1): forward from Brahma's sign (or ``seed``, ``tajaka_dasa``) (+6 if it is an even
    sign); years = signs to the lord of the 6th (odd sign) / 8th (even sign), second cycle
    12 - years; antardasas forward from the sign of the mahadasa sign's lord."""
    sg, lons = jc.signs[0], jc.lons
    seed = sg[brahma_planet(jc)] if seed is None else seed
    if seed % 2:
        seed = (seed + 6) % 12
    ls = [(seed + i) % 12 for i in range(12)]
    ys = []
    for s in ls:
        lord = S.sign_lord((s + (5 if s % 2 == 0 else 7)) % 12, sg, lons)
        ls_ = sg[lord]
        n = (ls_ - s if s % 2 == 0 else s - ls_) % 12
        if S.EXALTATION[lord] == ls_ and n < 12:
            n += 1
        if S.DEBILITATION[lord] == ls_ and n > 0:
            n -= 1
        ys.append(float(n))
    return periods(to_date, ls * 2, ys + [12 - y for y in ys], 0.0,
                   _forward_from(lambda s: sg[S.dasa_sign_lord(s, sg)]))


def sthira_dasa(jc: JChart, to_date, seed: Optional[int] = None) -> List[Dict[str, Any]]:
    """Sthira dasa (BPHS 46.168-169; JUS 2.3): from Brahma's sign (or ``seed``), direction by its parity and Saturn / Ketu;
    movable 7, fixed 8, dual 9 years."""
    sg, lons = jc.signs[0], jc.lons
    seed = sg[brahma_planet(jc)] if seed is None else seed
    d = _direction(seed, -1 if seed % 2 else 1, S.direction_override(seed, sg, lons))
    ls = [(seed + i * d) % 12 for i in range(12)]
    return periods(to_date, ls, [7.0 + s % 3 for s in ls], 0.0, _from_lord_of_stronger(sg, lons))


def mandooka_d11_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Mandooka dasa of D-11 (Rath): from the 11th of the D-11 lagna, every other sign (frog's jump),
    then the signs skipped; direction by parity and Saturn / Ketu in D-11; movable 7, fixed 8, dual 9 years."""
    sg, lons = jc.signs[10], jc.lons
    seed = (sg[0] + 10) % 12
    d = _direction(seed, -1 if seed % 2 else 1, S.direction_override(seed, sg, lons))
    ls = [(seed + 2 * i * d) % 12 for i in range(6)] + [(seed + d + 2 * i * d) % 12 for i in range(6)]
    return periods(to_date, ls, [7.0 + s % 3 for s in ls], 0.0, _from_lord_of_stronger(sg, lons))


KENDRA_ORDER = [0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8, 11]


def mandooka_knrao_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Mandooka dasa (K.N. Rao): from the lagna (its 7th if even), kendras, panaparas, apoklimas in the
    direction of its parity; years = signs to the natural lord (own 12, 7th 10)."""
    sg = jc.signs[0]
    seed = sg[0] if sg[0] % 2 == 0 else (sg[0] + 6) % 12
    d = -1 if seed % 2 else 1
    ls = [(k * d + seed) % 12 for k in KENDRA_ORDER]
    ys = []
    for s in ls:
        n = (sg[S.SIGN_LORDS[s]] - s if s % 2 == 0 else s - sg[S.SIGN_LORDS[s]]) % 12 + 1
        ys.append(12.0 if n == 1 else 10.0 if n == 7 else float(n))
    return periods(to_date, ls, ys, 0.0, lambda i, sign: [(k * d + sign) % 12 for k in KENDRA_ORDER])


def varnada_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Varnada dasa (BPHS 5.10-24): from the stronger of the lagna and the hora lagna, direction by its parity;
    years = signs from the Varnada lagna (0 .. 11), second cycle 12 - years; antardasas from the sign itself."""
    sg, lons = jc.signs[0], jc.lons
    seed = S.stronger_sign(sg[0], jc.hora_lagna_sign, sg, lons)
    d = -1 if seed % 2 else 1
    ls = [(seed + i * d) % 12 for i in range(12)]
    ys = [float((s - jc.varnada_sign) % 12) for s in ls]
    return periods(to_date, ls * 2, ys + [12 - y for y in ys], 0.0,
                   lambda i, s: [(s + j * (-1 if s % 2 else 1)) % 12 for j in range(12)])


def patyayini_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Patyayini dasa (PVR 30.2): lagna and Sun .. Saturn by their degrees in the sign (ascending); each runs the
    difference to the previous one, scaled so that the largest degree is 120 years; antardasas from the
    mahadasa lord in that order, in proportion."""
    deg = [x % 30.0 for x in jc.lons[:8]]
    order = sorted(range(8), key=lambda p: deg[p])
    inc = [deg[order[0]]] + [deg[order[i]] - deg[order[i - 1]] for i in range(1, 8)]
    ys = [x * 120.0 / sum(inc) for x in inc]
    by = [0.0] * 10
    for p, y in zip(order, ys):
        by[p] = y
    return periods(to_date, order + order[:1], ys + ys[:1], 0.0,
                   lambda i, p: [order[(i + j) % 8] for j in range(8)], by, sum(ys))


def _kaala_unit(day: Dict[str, Any]) -> float:
    """Kaala dasa (BPHS 46.44-49): the years of Sun's period (Moon 2x, .. Ketu 9x) from the part of the day / night /
    twilight (a sixth of day or night on either side of sunrise and sunset) passed at birth."""
    g, dl, nl = day["janma_ghatis"], day["day_ghatis"], day["night_ghatis"]
    a = g - dl
    if g < dl / 6:
        x = (nl + dl) * (nl / 6 + g)
    elif g < dl * 5 / 6:
        x = (g - dl / 6) * dl
    elif g < nl / 6 + dl:
        x = (nl + dl) * (g - dl * 5 / 6)
    elif a < nl * 5 / 6:
        x = (a - nl / 6) * nl
    else:
        x = (nl + dl) * (a - nl * 5 / 6)
    return x / 225.0


def kaala_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Kaala dasa: Sun .. Ketu with n times the unit, then again with n times (8/3 - unit) (120 years in all);
    antardasas Sun .. Ketu twice in proportion to the 18 mahadasa lengths."""
    u = _kaala_unit(jc.day)
    ys = [n * u for n in range(1, 10)] + [n * (8.0 / 3.0 - u) for n in range(1, 10)]
    lords = list(range(1, 10)) * 2
    out = periods(to_date, lords, ys, 0.0)
    t = 0.0
    for md in out:
        a = t
        md["antardasas"] = []
        for lord, y in zip(lords, ys):
            ay = md["years"] * y / 120.0
            md["antardasas"].append(_md(lord, to_date(a), to_date(a + ay), ay, a))
            a += ay
        t += md["years"]
    return out


def chakra_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Chakra dasa (BPHS 46.50-51): 10 years each, forward from the sign of the lagna lord (day birth), the lagna
    (night) or the 2nd (twilight); antardasas forward the same way from each sign."""
    sg, day = jc.signs[0], jc.day
    g, dl, nl = day["janma_ghatis"], day["day_ghatis"], day["night_ghatis"]
    kind = 2
    if dl / 6 <= g:
        if g < dl * 5 / 6:
            kind = 0
        elif nl / 6 + dl <= g and g - dl < nl * 5 / 6:
            kind = 1
    start = [lambda s: sg[S.SIGN_LORDS[s]], lambda s: s, lambda s: (s + 1) % 12][kind]
    seed = start(sg[0])
    return periods(to_date, [(seed + i) % 12 for i in range(12)], [10.0] * 12, 0.0, _forward_from(start))


def rasi_bhukta_vimsottari_dasa(jc: JChart, to_date, progress: int = 0) -> List[Dict[str, Any]]:
    """Rasi-Bhukta Vimsottari: Vimsottari mahadasas; antardasas the 12 signs from the lord's sign, 1/12
    each."""
    lords, years = VIMSOTTARI
    moon = jc.moon()
    k = (int(moon / NAK) + progress) % 9
    ls, ys = _cycle(lords, years, k, 9)
    sg = jc.signs[0]
    return periods(to_date, ls, ys, -(moon % NAK) / NAK * ys[0], lambda i, p: [(sg[p] + j) % 12 for j in range(12)])


def _kendradi(seed: int, forward: bool) -> List[int]:
    return [(seed + k if forward else seed - k) % 12 for k in KENDRA_ORDER]




# antardasa steps by the mahadasa sign's modality (Drig, Trikona, Chara (Parasara))
AD_STEPS = ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7],
            [0, 3, 6, 9, 4, 7, 10, 1, 8, 11, 2, 5])


def _steps_sub(sg, lons, base=None):
    """Antardasas from ``base(sign)`` (default: the stronger of the sign and its 7th) by the sign's modality steps,
    backwards for an even sign."""
    base = base or (lambda s: S.stronger_of_7th(s, sg, lons))
    return lambda i, s: [(k * (-1 if s % 2 else 1) + base(s)) % 12 for k in AD_STEPS[s % 3]]


def _narayana_years(ls, sg) -> List[float]:
    return [float(S._sign_count(sg[S.dasa_sign_lord(s, sg)], s, S.dasa_sign_lord(s, sg))) for s in ls]


def _narayana_like(to_date, sg, lons, ls):
    """Narayana years (``sign_strength._sign_count``), second cycle 12 - years, and antardasas for the mahadasa signs ``ls``."""
    ys = _narayana_years(ls, sg)
    return periods(to_date, ls * 2, ys + [12 - y for y in ys], 0.0, _from_lord_of_stronger(sg, lons))


def _narayana_order(seed, sg, lons):
    start = S.typed_start()
    seed = seed if start is None else start
    flag = S.direction_override(seed, sg, lons)
    d = _direction(seed, -1 if ((seed + 8) // 3) % 2 else 1, flag)
    steps = NARAYANA_STEPS[0 if flag == 1 else seed % 3]
    return [(steps[i] * d + seed) % 12 for i in range(12)]


def lagnamsaka_dasa(jc: JChart, to_date, varga: int = 1) -> List[Dict[str, Any]]:
    """Lagnamsaka dasa (LagnamsakaDasaChart=1): Narayana dasa of the rasi chart from the stronger (rasi
    table) of the D-9 lagna's sign and its 7th."""
    sg, lons = jc.signs[0], jc.lons
    seed = S.stronger_of_7th(jc.signs[varga][0], sg, lons)
    return _narayana_like(to_date, sg, lons, _narayana_order(seed, sg, lons))


def padanaathaamsa_dasa(jc: JChart, to_date, varga: int = 1) -> List[Dict[str, Any]]:
    """Padanaathaamsa dasa (PadanathamsaDasaChart=1): Narayana dasa of D-9 from the stronger of the D-9
    sign of the natural lord of the arudha lagna's sign (point 59) and its 7th."""
    sg, lons = jc.signs[varga], jc.lons
    al = S.bhava_arudhas(jc.signs[0], jc.lons)[0]
    seed = S.stronger_of_7th(sg[S.SIGN_LORDS[al]], sg, lons)
    return _narayana_like(to_date, sg, lons, _narayana_order(seed, sg, lons))


def lagna_kendradi_rasi_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Lagna Kendradi Rasi dasa (BPHS 46.175-177; PVR ch. 19): kendras, panaparas, apoklimas from the stronger of the lagna and its
    7th (direction by its parity and Saturn / Ketu); Narayana years and antardasas."""
    sg, lons = jc.signs[0], jc.lons
    seed = S.stronger_of_7th(sg[0], sg, lons)
    d = _direction(seed, -1 if seed % 2 else 1, S.direction_override(seed, sg, lons))
    return _narayana_like(to_date, sg, lons, [(k * d + seed) % 12 for k in KENDRA_ORDER])


def ak_kendradi_rasi_dasa(jc: JChart, to_date, seed: Optional[int] = None) -> List[Dict[str, Any]]:
    """AK Kendradi Rasi dasa: kendras, panaparas, apoklimas forward from the stronger of the
    atmakaraka's sign (or ``seed``) and its 7th, each group by rule B; Narayana years and antardasas."""
    sg, lons = jc.signs[0], jc.lons
    seed = S.stronger_of_7th(sg[jc.atmakaraka()] if seed is None else seed, sg, lons)
    ls = _kendradi(seed, True)
    ls = sum((S.sort_signs(ls[g:g + 4], sg, lons, "B") for g in (0, 4, 8)), [])
    return _narayana_like(to_date, sg, lons, ls)


def trikona_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Trikona dasa (BPHS 46.183-184; JUS 2.4): from the strongest of the lagna and its trines (rule A), every sign in the
    direction of its parity; Narayana years; antardasas by modality steps from the stronger of the sign and
    its 7th."""
    sg, lons = jc.signs[0], jc.lons
    seed = S.stronger_sign(S.stronger_sign(sg[0], (sg[0] + 4) % 12, sg, lons), (sg[0] + 8) % 12, sg, lons)
    d = -1 if seed % 2 else 1
    ls = [(seed + i * d) % 12 for i in range(12)]
    return periods(to_date, ls, _narayana_years(ls, sg), 0.0, _steps_sub(sg, lons))


def yogardha_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Yogardha dasa (BPHS 46.174; JUS 2.4): every sign from the stronger of the lagna and its 7th (direction by parity and
    Saturn / Ketu); years the mean of the Narayana (chara) and 7 / 8 / 9 (sthira) years; Narayana
    antardasas."""
    sg, lons = jc.signs[0], jc.lons
    seed = S.stronger_of_7th(sg[0], sg, lons)
    d = _direction(seed, -1 if seed % 2 else 1, S.direction_override(seed, sg, lons))
    ls = [(seed + i * d) % 12 for i in range(12)]
    ys = [(y + 7 + s % 3) * 0.5 for s, y in zip(ls, _narayana_years(ls, sg))]
    return periods(to_date, ls * 2, ys + [12 - y for y in ys], 0.0, _from_lord_of_stronger(sg, lons))


PARYAYA_STEPS = {0: (3, [0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8, 11]),    # movable lagna: Ubhaya
                 1: (6, [0, 6, 1, 7, 2, 8, 3, 9, 4, 10, 5, 11]),    # fixed: Sthira
                 2: (4, [0, 4, 8, 1, 5, 9, 2, 6, 10, 3, 7, 11])}    # dual: Chara


def paryaya_dasa(jc: JChart, to_date, varga: int = 6) -> List[Dict[str, Any]]:
    """Paryaaya dasas (ParyaayaDasaChart=6): from the house of the varga's own number in that varga (the
    6th in D-6), by its modality: the strongest of it and its kendras / its 7th / its trines (rule A), then the
    steps of that type in the direction of (sign // 3) parity and Saturn / Ketu; Narayana years and
    antardasas in the varga."""
    sg, lons = jc.signs[varga], jc.lons
    seed = (VARGA_NUMBER[varga] + 11 + sg[0]) % 12
    gap, steps = PARYAYA_STEPS[seed % 3]
    best = seed
    for k in range(gap, 12, gap):
        best = S.stronger_sign(best, (seed + k) % 12, sg, lons)
    d = _direction(best, -1 if (best // 3) % 2 else 1, S.direction_override(best, sg, lons))
    return _narayana_like(to_date, sg, lons, [(k * d + best) % 12 for k in steps])


def _co_lord(a: int, b: int, sg, lons, kind: str) -> int:
    """The other two co-lord rules (PVR 15.5.1 in two orders): "C" (own sign, more grahas, further in the sign) and
    "D" (own sign, more grahas, movable over fixed over dual, then the sign count to the co-lord; BPHS 46.158-166's
    order for the Chara dasa's Scorpio and Aquarius)."""
    own_a, own_b = S._PAIR_SIGN[a], S._PAIR_SIGN[b]
    sa, sb = sg[a], sg[b]
    if sa == own_a:
        if sb != own_b:
            return b
    elif sb == own_b:
        return a
    na, nb = sg[1:10].count(sa), sg[1:10].count(sb)
    if kind == "C":
        if na != nb:
            return a if na > nb else b
        return b if lons[a] % 30.0 < lons[b] % 30.0 else a
    if na != nb:
        return a if na > nb else b
    if sa % 3 != sb % 3:
        return a if sa % 3 < sb % 3 else b
    return a if S._sign_count(sb, own_b, b) <= S._sign_count(sa, own_a, a) else b


def _lord(sign: int, sg, lons, kind: str) -> int:
    if sign == 10:
        return _co_lord(7, 8, sg, lons, kind)
    if sign == 7:
        return _co_lord(3, 9, sg, lons, kind)
    return S.SIGN_LORDS[sign]


def chara_parasara_dasa(jc: JChart, to_date, seed_point: int = 0, fractional: bool = False,
                        exaltation_exception: bool = True) -> List[Dict[str, Any]]:
    """Chara dasa (Parasara, BPHS 46.158-167): every sign from the lagna in the direction of (sign + 8) // 3 parity;
    years = signs to the lord (co-lord rule "D"), +1 exalted / -1 debilitated (CharaDasaExaltationException, on;
    BPHS 46.166), second cycle 12 - years; antardasas by modality steps from the stronger of the sign and its 7th.
    Options (not saved in the ini): ``seed_point`` (0 lagna, 1 Sun, 2 Moon) the dasa starts from;
    ``fractional`` years = the arc from the seed's degrees placed in the dasa sign to
    the lord, / 30, counted forward for Ar Ta Ge / Li Sc Sg and backward otherwise (0 -> 12)."""
    sg, lons = jc.signs[0], jc.lons
    seed = sg[seed_point]
    d = -1 if ((seed + 8) // 3) % 2 else 1
    ls = [(seed + i * d) % 12 for i in range(12)]
    ys = []
    for s in ls:
        lord = _lord(s, sg, lons, "D")
        if not fractional:
            n = S._sign_count(sg[lord], s, lord)
            if not exaltation_exception:                    # CharaDasaExaltationException=0: no +1 / -1
                n = (sg[lord] - s if (s // 3) % 2 == 0 else s - sg[lord]) % 12 or 12
            ys.append(float(n))
            continue
        x = s * 30.0 + lons[seed_point] % 30.0
        y = norm360(lons[lord] - x if (s // 3) % 2 == 0 else x - lons[lord]) / 30.0
        ys.append(y if y != 0.0 else 12.0)
    return periods(to_date, ls * 2, ys + [12 - y for y in ys], 0.0, _steps_sub(sg, lons))


def chara_knrao_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Chara dasa (K.N. Rao): every sign from the lagna in the direction of (sign + 8) // 3 parity;
    years = signs to the lord (co-lord rule "C"; no exaltation rule); antardasas from the next
    sign in the mahadasa sign's own direction."""
    sg, lons = jc.signs[0], jc.lons
    seed = sg[0]
    d = -1 if ((seed + 8) // 3) % 2 else 1
    ls = [(seed + i * d) % 12 for i in range(12)]
    ys = []
    for s in ls:
        ls_ = sg[_lord(s, sg, lons, "C")]
        ys.append(float((ls_ - s if (s // 3) % 2 == 0 else s - ls_) % 12 or 12))

    def sub(i, s):
        dd = -1 if ((s + 8) // 3) % 2 else 1
        return [(s + dd * (j + 1)) % 12 for j in range(12)]
    return periods(to_date, ls, ys, 0.0, sub)


RANGACHARYA_STEPS = ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7],
                     [0, 4, 8, 1, 5, 9, 2, 6, 10, 3, 7, 11])


def chara_rangacharya_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Iranganti Rangacharya Chara dasa: from the lagna by its modality's steps, backwards for an even
    sign; years (signs from the natural lord's sign, counted by that sign's parity, plus one;
    12 if the lord is in the sign), second cycle 12 - years; antardasas the same steps from the sign."""
    sg = jc.signs[0]
    seed = sg[0]
    d = -1 if seed % 2 else 1
    ls = [(k * d + seed) % 12 for k in RANGACHARYA_STEPS[seed % 3]]
    ys = []
    for s in ls:
        ls_ = sg[S.SIGN_LORDS[s]]
        ys.append(12.0 if ls_ == s else float(((s - ls_ if ls_ % 2 == 0 else ls_ - s) % 12 or 12) + 1))
    return periods(to_date, ls * 2, ys + [12 - y for y in ys], 0.0,
                   lambda i, s: [(k * (-1 if s % 2 else 1) + s) % 12 for k in RANGACHARYA_STEPS[s % 3]])


def drig_dasa(jc: JChart, to_date, parasara: bool = True) -> List[Dict[str, Any]]:
    """Drigdasa (BPHS 46.185-187; PVR ch. 21, DrigdasaOfParasara=1): the 9th, 10th and 11th, each followed by the signs it aspects
    (counted backwards from a movable, forwards from a fixed, by parity from a dual sign);
    movable 7, fixed 8, dual 9 years; antardasas by modality steps from the stronger of the sign and its
    7th."""
    sg, lons = jc.signs[0], jc.lons

    def aspects(start):
        m = start % 3
        step = -1 if m == 0 else (1 if parasara else -1) if m == 1 else (-1 if start % 2 else 1)
        out, s = [start], start
        for _ in range(11):
            s = (s + step) % 12
            if s != start and S.rasi_drishti(s, start):
                out.append(s)
        return out
    if parasara:
        ls = sum((aspects((sg[0] + k) % 12) for k in (8, 9, 10)), [])
        return periods(to_date, ls, [7.0 + s % 3 for s in ls], 0.0, _steps_sub(sg, lons))
    # DrigdasaOfParasara=0: from the 9th, 8th, 7th of a dual lagna, a fixed sign's aspects backwards too; years = signs to the lord (co-lord rule D,
    # sign_strength._sign_count), second cycle 12 - years (24 periods, 120 years); Narayana antardasas
    ls = sum((aspects((sg[0] + k) % 12) for k in ((8, 7, 6) if sg[0] % 3 == 2 else (8, 9, 10))), [])
    ys = []
    for s in ls:
        lord = _lord(s, sg, lons, "D")
        ys.append(float(S._sign_count(sg[lord], s, lord)))
    return periods(to_date, ls * 2, ys + [12 - y for y in ys], 0.0, _from_lord_of_stronger(sg, lons))


# Kalachakra (BPHS 46.52-95): years by sign, the 216-entry sign table (savya 0..107, apasavya 108..215, rows of 9
