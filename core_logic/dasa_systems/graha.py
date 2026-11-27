"""graha: part of dasa_systems (split from one module; see __init__.py)."""
from typing import Any, Dict, List, Sequence
from .. import sign_strength as S
from .chart import JChart, NAK, _md, periods
from .rasi import KENDRA_ORDER, _direction, _forward_from, _kendradi
from .nakshatra import VIMSOTTARI

VIM_YEARS = [0, 6, 10, 7, 17, 16, 20, 19, 18, 7]                      # by point (Moola dasa)
MOOLATRIKONA_DASA = [12, 4, 1, 0, 5, 8, 6, 10, 10, 7]                 # moolatrikona signs by point (BPHS 3.51-54, 47.34-39)


def _moola_years(p: int, sg, no_correction: bool = False) -> int:
    """Moola dasa years (Sanjay Rath's): Vimsottari years less the signs from the planet to its moolatrikona (own 12, +1 exalted,
    -1 debilitated); a negative result taken positive, 0 as the full years. ``no_correction``
    (MoolaDasaNoCorrectionInMoolaTrikona): a planet in its moolatrikona keeps the full years."""
    s, mt = sg[p], MOOLATRIKONA_DASA[p]
    if mt == s and no_correction:
        return VIM_YEARS[p]
    n = 12 if mt == s else (mt - s) % 12
    if mt != s:
        if S.EXALTATION[p] == s and n < 12:
            n += 1
        elif S.DEBILITATION[p] == s and n > 0:
            n -= 1
    r = VIM_YEARS[p] - n
    return -r if r < 0 else r or VIM_YEARS[p]


def moola_dasa(jc: JChart, to_date, use_lagna: bool = True, use_moon: bool = True, use_sun: bool = True,
               no_correction: bool = False) -> List[Dict[str, Any]]:
    """Moola dasa (BJ 8.1-2): from the strongest (most grahas, the lagna counting one more; rule B) of the lagna,
    Moon and Sun signs, its kendras, panaparas, apoklimas (backwards from an even sign), each group by strength
    (rule B), the grahas in each sign by dignity; first cycle ``_moola_years``, second the rest of the
    Vimsottari years; antardasas from the lord in that order, in proportion to the first cycle. Options:
    ``use_lagna`` / ``use_moon`` / ``use_sun`` (LagnaUsedInMoolaDasa ..; off: its count is 0, the lagna stays the
    fallback), ``no_correction`` as ``_moola_years``."""
    sg, lons = jc.signs[0], jc.lons
    cands = [(sg[0], sg[1:10].count(sg[0]) + 1 if use_lagna else 0), (sg[2], sg[1:10].count(sg[2]) if use_moon else 0),
             (sg[1], sg[1:10].count(sg[1]) if use_sun else 0)]
    top = max(c for _, c in cands)
    seed = S.sort_signs([s for s, c in cands if c == top], sg, lons, "B")[0]
    d = -1 if seed % 2 else 1
    signs = [(seed + k * d) % 12 for k in KENDRA_ORDER]
    signs = sum((S.sort_signs(signs[g:g + 4], sg, lons, "B") for g in (0, 4, 8)), [])
    order = sum((S.planets_in_sign(s, sg, lons) for s in signs), [])
    first = [float(_moola_years(p, sg, no_correction)) for p in order]
    by = [0.0] * 10
    for p, y in zip(order, first):
        by[p] = y
    return periods(to_date, order * 2, first + [VIM_YEARS[p] - y for p, y in zip(order, first)], 0.0,
                   lambda i, p: [order[(i + j) % 9] for j in range(9)], by, sum(first))




def _graha_order(signs_: Sequence[int], sg, lons) -> List[int]:
    """Kendras, panaparas, apoklimas each sorted by rule B, then the grahas in each sign by dignity."""
    groups = sum((S.sort_signs(signs_[g:g + 4], sg, lons, "B") for g in (0, 4, 8)), [])
    return sum((S.planets_in_sign(s, sg, lons) for s in groups), [])


OWN_SIGNS = [(0, 0), (4, 4), (3, 3), (0, 7), (2, 5), (8, 11), (1, 6), (9, 10), (10, 10), (7, 7)]   # own signs by point


def _ak_graha_years(p: int, sg) -> int:
    """The larger of the sign counts from the planet to its two own signs (as Narayana dasa counts them)."""
    return max(_count_to(own, sg[p], p) for own in OWN_SIGNS[p])


def _count_to(own: int, sign: int, p: int) -> int:
    n = (own - sign if (sign // 3) % 2 == 0 else sign - own) % 12 or 12
    if S.EXALTATION[p] == sign and n < 12:
        n += 1
    if S.DEBILITATION[p] == sign and n > 0:
        n -= 1
    return n


def ak_kendradi_graha_dasa(jc: JChart, to_date, varga: int = 0) -> List[Dict[str, Any]]:
    """AK Kendradi Graha dasa: the grahas (Ketu left out) from the atmakaraka's sign by kendras,
    panaparas, apoklimas (direction by its parity and Saturn / Ketu); years ``_ak_graha_years``; the antardasas of
    every period run through the same 8 grahas from the first, in proportion."""
    sg, lons = jc.signs[varga], jc.lons
    seed = sg[jc.atmakaraka()]
    d = _direction(seed, -1 if seed % 2 else 1, S.direction_override(seed, sg, lons))
    order = [p for p in _graha_order(_kendradi(seed, d == 1), sg, lons) if p != 9][:8]
    ys = [float(_ak_graha_years(p, sg)) for p in order]
    by = [0.0] * 10
    for p, y in zip(order, ys):
        by[p] = y
    return periods(to_date, order, ys, 0.0, lambda i, p: order, by, sum(ys))


NAISARGIKA = ([2, 3, 4, 6, 5, 1, 7, 0], [1, 2, 9, 20, 18, 20, 50, 12])


def naisargika_dasa(jc: JChart, to_date, no_ad_for_md_lord: bool = True, third_tenth_no_ad: bool = False,
                    others_no_ad: bool = False) -> List[Dict[str, Any]]:
    """Naisargika dasa (BPHS 43.16-17; BJ 8.3): Moon 1, Mars 2, Mercury 9, Venus 20, Jupiter 18, Sun 20, Saturn 50, lagna 12
    years; antardasas the Sun .. Saturn by kendras from the mahadasa lord's sign (rule B, dignity) weighted
    1/2 conjunct, 1/4 in the 4th / 8th, 1/3 in the 5th / 9th, 1/7 in the 7th, 1 elsewhere. INI
    NaisargikaDasaNoADForMDLord (default on: the lord itself has none, else weight 1), NaisargikaDasa3rd10thNoAD
    and NaisargikaDasaOthersNoAD (none for grahas in the 3rd / 10th, or in the 2nd / 6th / 11th / 12th)."""
    sg, lons = jc.signs[0], jc.lons
    lords, years = NAISARGIKA
    out = periods(to_date, lords, [float(y) for y in years], 0.0)
    t = 0.0
    for md in out:
        p = md["lord"]
        weights = []
        for q in _graha_order(_kendradi(sg[p], True), sg, lons):
            if not 1 <= q <= 7:
                continue
            h = (sg[q] - sg[p]) % 12
            if h == 0 and q == p:
                if no_ad_for_md_lord:
                    continue
                w = 1.0
            elif h == 0:
                w = 0.5
            elif h in (2, 9):
                if third_tenth_no_ad:
                    continue
                w = 1.0
            else:
                w = {3: 0.25, 7: 0.25, 4: 1 / 3, 8: 1 / 3, 6: 1 / 7}.get(h)
                if w is None:
                    if others_no_ad:
                        continue
                    w = 1.0
            weights.append((q, w))
        tot, a = sum(w for _, w in weights), t
        md["antardasas"] = []
        for q, w in weights:
            ay = md["years"] * w / tot
            md["antardasas"].append(_md(q, to_date(a), to_date(a + ay), ay, a))
            a += ay
        t += md["years"]
    return out


def sudarsana_chakra_dasa(jc: JChart, to_date, varga: int = 0, ad_from_lord: bool = True) -> List[Dict[str, Any]]:
    """Sudarsana Chakra dasa (BPHS 74; PVR ch. 31) of varga index ``varga`` (SCDasaVarga): a year for each sign from the
    lagna, with the Moon's and Sun's signs alongside; antardasas forward from the sign of the sign's lord
    (``ad_from_lord``, SudarsanaChakraDasaAD=1) or, off, each column forward from its own sign."""
    sg = jc.signs[varga]
    start = (lambda s: sg[S.SIGN_LORDS[s]]) if ad_from_lord else (lambda s: s)
    out = periods(to_date, [(sg[0] + i) % 12 for i in range(12)], [1.0] * 12, 0.0, _forward_from(start))
    for i, md in enumerate(out):
        md["moon"], md["sun"] = (sg[2] + i) % 12, (sg[1] + i) % 12
        for j, ad in enumerate(md["antardasas"]):
            if ad_from_lord:                                # each forward from the sign of its sign's lord
                ad["moon"], ad["sun"] = ((sg[S.SIGN_LORDS[md[k]]] + j) % 12 for k in ("moon", "sun"))
            else:                                           # each forward from its own sign
                ad["moon"], ad["sun"] = (md["moon"] + j) % 12, (md["sun"] + j) % 12
    return out


def buddhi_gati_dasa(jc: JChart, to_date, varga: int = 0) -> List[Dict[str, Any]]:
    """Buddhi gati dasa (Agni purana): the grahas by house from the 4th onwards (4th .. 3rd), further in
    the sign first; the first three again make 12; years = signs back from the lagna plus the period's index
    (12 for 0), second cycle 12 - years; antardasas 1/12 each, the first three then the nine, from the lord's first
    place there."""
    sg = jc.signs[varga]
    val = {p: jc.lons[p] % 30.0 + (12 - ((sg[p] - sg[0]) % 12 + 9) % 12) * 100.0 for p in range(1, 10)}
    order: List[int] = []
    for p in range(1, 10):
        k = 0
        while k < len(order) and not val[order[k]] < val[p]:
            k += 1
        order.insert(k, p)
    ads = order[:3] + order
    order += order[:3]
    ys = [float((sg[0] - sg[p] + i) % 12 or 12) for i, p in enumerate(order)]
    return periods(to_date, order * 2, ys + [12 - y for y in ys], 0.0,
                   lambda i, p: [ads[(j + ads.index(p)) % 12] for j in range(12)])


KARAKA_ABBR = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]


def karakas(jc: JChart) -> List[int]:
    """The 8 chara karakas (AK .. DK) by degree in the sign, Rahu counted from the end (BPHS 32.3-17)."""
    deg = [x % 30.0 for x in jc.lons[:9]]
    deg[8] = 30.0 - deg[8]
    return sorted(range(1, 9), key=lambda p: -deg[p])


def karaka_dasa(jc: JChart, to_date) -> List[Dict[str, Any]]:
    """Karaka dasa (BPHS 46.178): AK .. DK, years = signs from the lagna (12 for 0), second cycle 12 - years;
    antardasas from the next karaka, in proportion to that cycle's years."""
    sg, ks = jc.signs[0], karakas(jc)
    n = len(ks)
    ys = [float((sg[p] - sg[0]) % 12 or 12) for p in ks]
    second = [12 - y for y in ys]
    out = periods(to_date, ks * 2, ys + second, 0.0)
    t = 0.0
    for i, md in enumerate(out):
        md["karaka"] = i % n
        cyc, tot = (ys, sum(ys)) if i < n else (second, sum(second))
        a, md["antardasas"] = t, []
        for j in range(1, n + 1):
            k = (i + j) % n
            ay = md["years"] * cyc[k] / tot
            md["antardasas"].append(dict(_md(ks[k], to_date(a), to_date(a + ay), ay, a), karaka=k))
            a += ay
        t += md["years"]
    return out


def tara_dasa(jc: JChart, to_date, parasara: bool = False, direction_from_star: bool = False,
              use_sesham: bool = True, sesham_rev_apasavya: bool = False) -> List[Dict[str, Any]]:
    """Tara dasa as Pt. Sanjay Rath teaches it (TaraDasaParasara=0; ``parasara`` for BPHS 46.207-209): the grahas by kendras from the lagna (direction by its parity and
    Saturn / Ketu), each group by rule B and by dignity in the sign; Vimsottari years; balance of the Moon's
    nakshatra, or the lagna's when the Moon is in the lagna sign (TaraDasaUseSesham=1); antardasas from
    the lord in that order, in proportion.  Options: ``direction_from_star`` (TaraDasaDirectionFromStar) the
    direction by the parity of nakshatra // 3 of the strongest graha in the lagna (the Moon if it is empty);
    ``use_sesham`` False starts at birth; ``sesham_rev_apasavya`` reverses the balance when that nakshatra // 3 is
    odd; ``parasara`` (TaraDasaParasara=1) the Vimsottari order from the strongest graha of the kendras sorted by
    rule B, with the Moon's balance."""
    sg, lons = jc.signs[0], jc.lons
    lag = sg[0]
    if parasara:
        # the builder writes the kendras' grahas over the Moon's nakshatra lord before it looks that lord up
        first = next(iter(sum((S.planets_in_sign(k, sg, lons) for k in
                               S.sort_signs(_kendradi(lag, True)[:4], sg, lons, "B")), [])), None)
        lords, _ = VIMSOTTARI
        k = lords.index(first if first is not None else lords[int(lons[2] / NAK) % 9])
        order = [lords[(k + i) % 9] for i in range(9)]
        point = 2
    else:
        if direction_from_star:
            p = next(iter(S.planets_in_sign(lag, sg, lons)), 2)
            d = -1 if (int(lons[p] / NAK) // 3) % 2 else 1
        else:
            d = _direction(lag, -1 if lag % 2 else 1, S.direction_override(lag, sg, lons))
        order = _graha_order(_kendradi(lag, d == 1), sg, lons)
        # the seed is meant to be the strongest of the Moon and Sun signs, but the builder compares the Moon's
        # count + 1 with 0 (the Sun's count is overwritten), so it is always the Moon's sign: the lagna's nakshatra
        # if they share it
        point = 0 if sg[2] == sg[0] else 2
    nak = int(lons[point] / NAK)
    bal = 1 - (lons[point] % NAK) / NAK
    if sesham_rev_apasavya and not parasara and (nak // 3) % 2:
        bal = 1 - bal
    ys = [float(VIM_YEARS[p]) for p in order]
    by = [0.0] * 10
    for p, y in zip(order, ys):
        by[p] = y
    start = -(1 - bal) * ys[0] if use_sesham or parasara else 0.0
    return periods(to_date, order, ys, start, lambda i, p: [order[(i + j) % 9] for j in range(9)], by, sum(ys))
