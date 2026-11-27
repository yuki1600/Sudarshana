"""
core_logic/ayurdaya.py
======================
Longevity by the texts: BPHS Ch. 9, 10, 43, 44, 70 and 71, cited below as chapter.verse.

Each rule is worked from its
verse and checked in tests/test_ayurdaya.py. Points are indexed as in sign_strength: 0 Lagna, 1 Sun .. 7 Saturn,
8 Rahu, 9 Ketu.
"""
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from . import varga_charts as V
from . import natal_chart as N
from . import sign_strength as S
from .key_info import NAK, TARA_LORDS
from .yoga_engine import graha_drishti
from .shadbala import NATURAL_RELATIONS_9
from .tajika import DEEPTAMSA

PINDA_YEARS = (19, 25, 15, 12, 15, 21, 20)              # 43.4-8, Sun .. Saturn
NISARGA_YEARS = (20, 1, 2, 9, 18, 20, 50)               # 43.16-17, Sun .. Saturn
DEEP_EXALTATION = (10.0, 33.0, 298.0, 165.0, 95.0, 357.0, 200.0)
VISIBLE_HALF = {12: 1.0, 11: 1 / 2, 10: 1 / 3, 9: 1 / 4, 8: 1 / 5, 7: 1 / 6}     # 43.10-11, what a malefic loses
FRIEND, NEUTRAL, ENEMY = 2, 3, 4                        # NATURAL_RELATIONS_9's codes
KENDRA, KONA, DUSTHANA, APOKLIMA, UPACHAYA = (1, 4, 7, 10), (1, 5, 9), (6, 8, 12), (3, 6, 9, 12), (3, 6, 11)
GOPURA, SIMHASANA, PARAVATA, DEVALOKA = 4, 5, 6, 7      # Vaiseshikamsa counts in the dasa varga

VERY_SHORT, SHORT, MEDIUM, LONG, EXTREME = "Very short", "Short (Alpayu)", "Medium (Madhyayu)", "Long (Purnayu)", "Extremely long"
CLASSES = (VERY_SHORT, SHORT, MEDIUM, LONG, EXTREME)    # 43.49-50: the steps a class rises or falls by
# 43.41-44 by the pairs that agree. One edition of BPHS prints 91 for one pair; the series and the Jaimini tables have 96.
SPAN_YEARS = {LONG: {3: 120, 2: 108, 1: 96}, MEDIUM: {3: 80, 2: 72, 1: 64}, SHORT: {3: 32, 2: 36, 1: 40}}
# Where the rectified span stops, as a share of the class's years: the Jaimini compartments (120 to 80, 80 to 40, 32 to 0), not in BPHS
FLOOR_SHARE = {LONG: 2 / 3, MEDIUM: 1 / 2, SHORT: 0.0, VERY_SHORT: 0.0, EXTREME: 100 / 120}
# the outer classes, when they get years: Yogarishta's 20 (43.53) and the Kali yuga's full span (the help's paramaayush), whatever the agreement
OUTER_YEARS = {VERY_SHORT: 20, EXTREME: 120}
PAIR_CLASS = {(0, 0): LONG, (1, 2): LONG, (0, 1): MEDIUM, (2, 2): MEDIUM, (0, 2): SHORT, (1, 1): SHORT}     # 43.33-40; 0 movable, 1 fixed, 2 dual
LAGNA_REQUIRED_RUPAS = 7.0                              # a house's minimum Bhava Bala, as the Strengths view reads it
# Tajika deeptamsas of points 1 .. 9; the nodes have none in the text, so 8 degrees (tajika.is_within_tajika_orb's fallback)
ORBS = (None,) + tuple(DEEPTAMSA[p] for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")) + (8.0, 8.0)
REKHA_YEARS = tuple(d / 360.0 for d in (2.0, 1.5, 1.0, 0.5, 7.5)) + (2.0, 4.0, 6.0, 8.0)                    # 71.1-4, for 0 .. 8 rekhas


@dataclass
class Natal:
    """What the methods read of a birth chart."""
    lons: Sequence[float]
    hora_lagna: float
    retro: Sequence[bool] = (False,) * 10
    bala: Sequence[float] = (0.0,) * 10         # Shadbala of points 1 .. 7, shown only: strengths are compared by ``percent``
    percent: Sequence[float] = (0.0,) * 10      # the same, against the rupas required
    lagna_bala: float = 0.0                     # Bhava Bala of the 1st house
    natures: Optional[Sequence[int]] = None     # Sun .. Saturn as chart_shadbala gives them: 1 benefic, -1 malefic
    amsa: Sequence[int] = (0,) * 10             # Vaiseshikamsa count in the dasa varga
    is_day: bool = True
    twilight: bool = False                      # 9.14
    moon_hora: bool = False
    by_motion: bool = True                      # the Combustion view's rule (is_combust_by_orbs)
    classical: bool = False                     # the classical orbs instead (natal_chart.is_combust)
    bhavas: Optional[Sequence[int]] = None      # each point's bhava (1-12) in the chosen house system; None: the rasi from the lagna
    orbs: bool = False                          # yuti and drishti within the smaller deeptamsa, drishti on a bhava at its cusp; not by rasi
    cusps: Optional[Sequence[float]] = None     # the bhavas' cusps (1st .. 12th) in the chosen house system, where drishti on a bhava lands
    saturn_rule: int = 0                        # 43.47 "when Saturn causes the yoga": 0 as the lagna or 8th lord only, 1 any contributor (his Saturn-Moon seat too), 2 never
    jupiter_rule: bool = True                   # 43.48
    outer_years: bool = False                   # Very short and Extremely long get OUTER_YEARS

    def __post_init__(self):
        self.s = [int((x % 360.0) // 30.0) for x in self.lons]
        self.waxing = (self.lons[2] - self.lons[1]) % 360.0 < 180.0
        if self.natures is None:
            self.natures = (-1, 1 if self.waxing else -1, -1, 1, 1, 1, -1)
        self.b7 = [p for p in range(1, 8) if self.natures[p - 1] > 0]
        # the nodes face each other, so "the malefics in the 3rd, 6th, 11th" can only mean the seven planets
        self.m7 = [p for p in range(1, 8) if self.natures[p - 1] < 0]
        self.malefics = self.m7 + [8, 9]

    def house(self, p: int) -> int:
        return (self.s[p] - self.s[0]) % 12 + 1

    def bhava(self, p: int) -> int:
        return self.bhavas[p] if self.bhavas else self.house(p)

    def house_sign(self, h: int) -> int:
        return (self.s[0] + h - 1) % 12

    def lord(self, h: int) -> int:
        return S.sign_lord(self.house_sign(h), self.s, self.lons)

    def occupants(self, h: int) -> List[int]:
        return [p for p in range(1, 10) if self.house(p) == h]

    def benefic(self, p: int) -> bool:
        return p in self.b7

    def has_malefic(self, h: int) -> bool:
        return any(self.house(p) == h for p in self.malefics)

    def has_benefic(self, h: int) -> bool:
        return any(self.house(p) == h for p in self.b7)

    def aspects(self, p: int, sign: int) -> bool:
        return graha_drishti(p, self.s[p], sign)

    def _orb(self, q: int, p: int) -> float:
        """Two grahas touch only where both reach: the smaller of their deeptamsas."""
        return min(ORBS[q], ORBS[p])

    def _within(self, q: int, lon: float, orb: float) -> bool:
        d = (lon - self.lons[q]) % 360.0
        return any(abs((d - 30.0 * k + 180.0) % 360.0 - 180.0) <= orb for k in range(1, 12) if graha_drishti(q, 0, k))

    def joins(self, q: int, p: int) -> bool:
        """Yuti of grahas q and p: the same rasi, or with ``orbs`` within their orb, across a sign's edge too."""
        if not self.orbs:
            return self.s[q] == self.s[p]
        return abs((self.lons[p] - self.lons[q] + 180.0) % 360.0 - 180.0) <= self._orb(q, p)

    def sees(self, q: int, p: int) -> bool:
        """q's graha drishti on graha p: on p's rasi, or with ``orbs`` within their orb of the aspect's exact angle."""
        if not self.orbs:
            return self.aspects(q, self.s[p])
        return self._within(q, self.lons[p], self._orb(q, p))

    def sees_house(self, q: int, h: int) -> bool:
        """q's graha drishti on bhava h (1 the lagna): on its rasi, or with ``orbs`` within q's deeptamsa of the bhava's cusp."""
        if not (self.orbs and self.cusps):
            return self.aspects(q, self.house_sign(h))
        return self._within(q, self.cusps[h - 1], ORBS[q])

    def aspected_by(self, p: int, group: Sequence[int]) -> bool:
        return any(q != p and self.sees(q, p) for q in group)

    def touched_by(self, p: int, group: Sequence[int]) -> bool:
        """Yuti with, or a drishti from, one of ``group``."""
        return any(q != p and (self.joins(q, p) or self.sees(q, p)) for q in group)

    def all_in(self, group: Sequence[int], houses: Sequence[int]) -> bool:
        return bool(group) and all(self.house(p) in houses for p in group)

    def hemmed(self, sign: int) -> bool:
        return all(any(self.s[p] == (sign + d) % 12 for p in self.malefics) for d in (1, -1))

    def combust(self, p: int) -> bool:
        if p == 2:      # is_combust_by_orbs covers Mars .. Saturn; 12 degrees is the Moon's classical orb
            return min((self.lons[2] - self.lons[1]) % 360.0, (self.lons[1] - self.lons[2]) % 360.0) <= 12.0
        return N.is_combust(p, self.lons, self.retro, self.by_motion, self.classical)

    def exalted(self, p: int) -> bool:
        return S.EXALTATION[p] == self.s[p]

    def own(self, p: int) -> bool:
        return S.owns_sign(p, self.s[p])

    def strong(self, p: int) -> bool:
        return self.percent[p] >= 100.0

    def in_enemy_sign(self, p: int) -> bool:
        return NATURAL_RELATIONS_9[p - 1][S.SIGN_LORDS[self.s[p]] - 1] == ENEMY

    def dignified(self, p: int) -> bool:
        return self.exalted(p) or self.own(p) or NATURAL_RELATIONS_9[p - 1][S.SIGN_LORDS[self.s[p]] - 1] == FRIEND

    def bare(self, p: int) -> bool:
        """43.78: bereft of dignity and of strength."""
        return not (self.exalted(p) or self.own(p) or S.MOOLATRIKONA[p] == self.s[p] or self.strong(p))

    def afflicted(self, p: int) -> bool:
        """43.74: combust, or yuti with or aspected by a malefic."""
        return self.combust(p) or self.touched_by(p, self.malefics)

    def gandanta(self) -> bool:
        """The Moon in the star's quarter on either side of a water-fire junction."""
        return not 10.0 / 3.0 <= self.lons[2] % 120.0 < 120.0 - 10.0 / 3.0


def arc_years(p: int, lon: float, full: Sequence[int] = PINDA_YEARS) -> float:
    """43.4-8: the full years at deep exaltation, half at deep debilitation, by the rule of three between."""
    arc = (DEEP_EXALTATION[p - 1] - lon) % 360.0
    return full[p - 1] * (360.0 - arc if arc < 180.0 else arc) / 360.0


def navamsa_years(lon: float) -> float:
    """43.18-19: a year for each navamsa from Aries, multiples of 12 expunged."""
    return (lon % 360.0) * 108.0 / 360.0 % 12.0


def _reductions(n: Natal, p: int, years: float) -> dict:
    """43.9-11, 43.22: the visible half (only the strongest in a house loses), then the halving or the third."""
    visible = VISIBLE_HALF.get(n.house(p), 0.0)
    if visible and max((q for q in range(1, 8) if n.s[q] == n.s[p]), key=lambda q: n.percent[q]) != p:
        visible = 0.0
    if p == 2 or n.benefic(p):      # 43.11: a waning Moon counts as a benefic here
        visible /= 2.0
    combust = n.combust(p) and p not in (6, 7)
    enemy = n.in_enemy_sign(p) and not n.retro[p]
    return {"visible": visible, "combust": combust, "enemy": enemy,
            "after": years * (1.0 - visible) * (0.5 if combust else 2.0 / 3.0 if enemy else 1.0)}


def _lagna_cut(n: Natal, p: int, years: float) -> float:
    """43.12-13: a malefic in the lagna loses its years x the lagna's minutes / 21600, half of it with a benefic's drishti on the lagna."""
    if n.s[p] != n.s[0] or p not in n.m7:
        return 0.0
    cut = years * (n.lons[0] % 360.0) * 60.0 / 21600.0
    return cut / 2.0 if any(n.sees_house(q, 1) for q in n.b7) else cut


def lagna_years(n: Natal) -> tuple:
    """43.14-15: (years, basis). The rasis gained from Aries, or the navamsas if the lord of the lagna's navamsa is the stronger lord."""
    if n.percent[S.SIGN_LORDS[V.d9(n.lons[0])]] > n.percent[S.SIGN_LORDS[n.s[0]]]:
        return navamsa_years(n.lons[0]), "navamsas"
    return (n.lons[0] % 360.0) / 30.0, "rasis"


def _arc_span(n: Natal, full: Sequence[int]) -> dict:
    """Pindayu or, with ``full`` its years, Nisargayu. BPHS gives Nisargayu only the years: later texts work it the same way."""
    rows = []
    for p in range(1, 8):
        gross = arc_years(p, n.lons[p], full)
        r = _reductions(n, p, gross)
        cut = _lagna_cut(n, p, r["after"])
        rows.append({"point": p, "full": full[p - 1], "gross": gross, **r, "lagna_cut": cut, "net": r["after"] - cut})
    years, basis = lagna_years(n)
    return {"rows": rows, "lagna": years, "lagna_basis": basis, "total": sum(r["net"] for r in rows) + years}


def amsayu(n: Natal) -> dict:
    """43.18-22: navamsa years with the same reductions; trebled in exaltation or an own sign, else doubled in an own navamsa or drekkana."""
    rows = []
    for p in range(1, 8):
        gross = navamsa_years(n.lons[p])
        factor = 3 if n.exalted(p) or n.own(p) else 2 if S.owns_sign(p, V.d9(n.lons[p])) or S.owns_sign(p, V.d3(n.lons[p])) else 1
        r = _reductions(n, p, gross * factor)
        rows.append({"point": p, "gross": gross, "factor": factor, **r, "net": r["after"]})
    years = navamsa_years(n.lons[0])
    return {"rows": rows, "lagna": years, "total": sum(r["net"] for r in rows) + years}


def class_of_years(years: float) -> str:
    """44.10-14: short before 32, medium to 64, long to 100, supreme beyond."""
    return SHORT if years < 32.0 else MEDIUM if years < 64.0 else LONG if years <= 100.0 else EXTREME


def spans(n: Natal) -> dict:
    """The three spans and 43.30-32: the strongest of Lagna, Sun and Moon picks Amsayu, Pindayu or Nisargayu; equals are averaged.
    Strongest against each one's minimum: the Lagna's Bhava Bala over 7 rupas, the Sun's and Moon's Shadbala over their required rupas."""
    out = {"pinda": _arc_span(n, PINDA_YEARS), "amsa": amsayu(n), "nisarga": _arc_span(n, NISARGA_YEARS)}
    strength = {"amsa": n.lagna_bala, "pinda": n.bala[1], "nisarga": n.bala[2]}
    percent = {"amsa": n.lagna_bala / 60.0 * 100.0 / LAGNA_REQUIRED_RUPAS, "pinda": n.percent[1], "nisarga": n.percent[2]}
    best = max(round(v, 2) for v in percent.values())
    chosen = [k for k, v in percent.items() if round(v, 2) == best]
    return {**out, "strength": strength, "percent": percent, "chosen": chosen, "years": sum(out[k]["total"] for k in chosen) / len(chosen)}


def pair_class(a: int, b: int) -> str:
    return PAIR_CLASS[tuple(sorted((a % 3, b % 3)))]


def _degrees(n: Natal, p: Optional[int]) -> float:
    if p is None:
        return n.hora_lagna % 30.0
    return 30.0 - n.lons[p] % 30.0 if p in (8, 9) else n.lons[p] % 30.0


def three_pairs(n: Natal) -> dict:
    """43.33-50: each pair's class, the class of two or three in agreement (if all differ the Moon-Saturn pair with the Moon in the 1st or
    7th, else Lagna-Hora Lagna), Saturn's and Jupiter's change of class, and the span by how many agree."""
    groups = ((("Lagna lord", n.lord(1)), ("8th lord", n.lord(8))), (("Saturn", 7), ("Moon", 2)), (("Lagna", 0), ("Hora Lagna", None)))
    sign = lambda p: int((n.hora_lagna % 360.0) // 30.0) if p is None else n.s[p]  # noqa: E731
    classes = [pair_class(sign(a[1]), sign(b[1])) for a, b in groups]
    base, votes = Counter(classes).most_common(1)[0]
    decided = "%d of 3 pairs agree" % votes
    if votes == 1:
        by_moon = n.house(2) in (1, 7)
        base = classes[1 if by_moon else 2]
        decided = "The pairs all differ: Saturn and Moon decide, the Moon being in the 1st or 7th" if by_moon else "The pairs all differ: Lagna and Hora Lagna decide"
    bodies = [b for g, c in zip(groups, classes) if c == base for b in g]
    average = sum(_degrees(n, p) for _, p in bodies) / len(bodies)

    falls, saturn = False, "Not a contributor: no change"
    if n.saturn_rule == 2:
        saturn = "Not applied (Settings: Longevity)"
    elif any(p == 7 and (n.saturn_rule == 1 or label in ("Lagna lord", "8th lord")) for label, p in bodies):
        only_malefic = n.touched_by(7, n.malefics) and not n.touched_by(7, n.b7)
        falls = not (n.own(7) or n.exalted(7) or only_malefic)
        saturn = "Contributor: the class falls" if falls else "Contributor, but own or exalted or influenced only by malefics: no change"
    rises = n.jupiter_rule and n.house(5) in (1, 7) and n.touched_by(5, n.b7) and not n.touched_by(5, n.malefics)
    jupiter = "In the 1st or 7th, influenced only by benefics: the class rises" if rises else "No change" if n.jupiter_rule else "Not applied (Settings: Longevity)"

    final = CLASSES[CLASSES.index(base) + int(rises) - int(falls)]
    years = SPAN_YEARS[final][votes] if final in SPAN_YEARS else OUTER_YEARS[final] if n.outer_years else None
    share = FLOOR_SHARE.get(final, 0.0)
    return {"groups": groups, "signs": [(sign(a[1]), sign(b[1])) for a, b in groups], "classes": classes, "votes": votes, "decided": decided, "base": base,
            "contributors": [label for label, _ in bodies], "average": average, "saturn": saturn, "jupiter": jupiter, "falls": falls, "rises": rises,
            "class": final, "years": years, "floor": years * share if years else None,
            "rectified": years * (share + (1.0 - share) * (1.0 - average / 30.0)) if years else None,
            "literal": years * (1.0 - average / 30.0) if years else None}


def placement(n: Natal) -> dict:
    """43.71-72: the stronger of the lagna's and the 8th's lords in a kendra, panaphara or apoklima bhava gives long, medium or short life."""
    lagna_lord, eighth_lord = n.lord(1), n.lord(8)
    a, b = n.percent[lagna_lord], n.percent[eighth_lord]
    # Shadbala against the required, as 43.14-15 judges the lords; the nodes have none, so with a node, or a tie, the dignity rule
    p = S.stronger_by_dignity(lagna_lord, eighth_lord, n.s, n.lons) if a == b or {lagna_lord, eighth_lord} & {8, 9} else lagna_lord if a > b else eighth_lord
    kind = (n.bhava(p) - 1) % 3
    return {"lagna_lord": lagna_lord, "eighth_lord": eighth_lord, "stronger": p, "house": n.bhava(p),
            "kind": ("Kendra", "Panaphara", "Apoklima")[kind], "class": (LONG, MEDIUM, SHORT)[kind]}


def sun_relation(n: Natal) -> dict:
    """43.72-73: the lagna's lord a friend, neutral or enemy of the Sun gives long, medium or short life. The Sun itself as lord has no such reading."""
    lord = n.lord(1)
    r = NATURAL_RELATIONS_9[lord - 1][0]
    return {"lord": lord, "relation": {0: "Own", FRIEND: "Friend", NEUTRAL: "Neutral", ENEMY: "Enemy"}[r], "class": {FRIEND: LONG, NEUTRAL: MEDIUM, ENEMY: SHORT}.get(r)}


def marakas(n: Natal) -> Dict[int, List[str]]:
    """Ch. 44 and the help's "Marakas": the killers, each with its reasons."""
    why: Dict[int, List[str]] = {}
    add = lambda p, text: why.setdefault(p, []).append(text)  # noqa: E731
    for h, name in ((2, "2nd"), (7, "7th")):
        lord = n.lord(h)
        add(lord, "Lord of the %s (44.3)" % name)
        for p in n.malefics:
            if n.house(p) == h:
                add(p, "Malefic in the %s (44.3)" % name)
            if p != lord and n.joins(p, lord):
                add(p, "Malefic with the %s lord (44.3)" % name)
            if n.house(p) != h and n.sees_house(p, h):
                add(p, "Malefic aspecting the %s (help)" % name)
            if p != lord and not n.joins(p, lord) and n.sees(p, lord):
                add(p, "Malefic aspecting the %s lord (help)" % name)
    lord12 = n.lord(12)
    for p in n.b7:
        if p != lord12 and n.joins(p, lord12):
            add(p, "Benefic with the 12th lord (44.6)")
    add(n.lord(8), "Lord of the 8th (44.6)")
    add(n.lord(6), "Lord of the 6th (44.15-21)")
    # 44.6-7: the dasha of an exclusive malefic may also kill, read functionally: every house it owns is a 3rd, 6th, 8th, 11th or 12th
    for p in range(1, 10):
        owned = [h for h in range(1, 13) if S.owns_sign(p, n.house_sign(h))]
        if owned and all(h in (3, 6, 8, 11, 12) for h in owned):
            add(p, "Exclusive malefic (44.6-7)")
    if 7 not in why and any(n.joins(7, p) or n.sees(7, p) for p in why):
        add(7, "Saturn related to a maraka (44.9)")
    # 44.22-24: Rahu and Ketu as marakas
    maraka_lords = (n.lord(2), n.lord(7))
    for p in (8, 9):
        h = n.house(p)
        if h in (1, 7, 8, 12):
            add(p, "Node in the %s (44.22-24)" % {1: "1st", 7: "7th", 8: "8th", 12: "12th"}[h])
        for lord in maraka_lords:
            if (n.s[p] - n.s[lord]) % 12 == 6:
                add(p, "Node in the 7th from a maraka lord (44.22-24)")
            if p != lord and n.joins(p, lord):
                add(p, "Node with a maraka lord (44.22-24)")
    if n.s[0] in (7, 9):    # Scorpio or Capricorn lagna
        add(8, "Rahu for Scorpio or Capricorn lagna (44.22-24)")
    # Rahu in the 6th, 8th or 12th gives difficulties, not death (44.22-24): not a maraka for that
    return why


# the killers by 44.3, 44.9, 44.22-24 and the help; the rest (8th, 6th lords, 44.6-7) can also kill
PRIME_VERSES = ("(44.3)", "(help)", "(44.9)", "(44.22-24)")


def prime(reasons: Sequence[str]) -> bool:
    return any(r.endswith(PRIME_VERSES) for r in reasons)


# 44.25-31: manner from who occupies or aspects the 3rd; 44.35-36 from who occupies the 8th
_DEATH_3RD = {
    1: "King or legal punishment (a strong Sun in the 3rd)",
    2: "Tuberculosis (Moon in the 3rd)",
    3: "Wounds, weapons, fire or thirst (Mars in the 3rd)",
    4: "Fever (Mercury in/aspecting the 3rd)",
    5: "Swelling or tumours (Jupiter in/aspecting the 3rd)",
    6: "Urinary disease (Venus in/aspecting the 3rd)",
}
_DEATH_8TH = {
    1: "Fire (Sun in the 8th)", 2: "Water (Moon in the 8th)", 3: "Weapons (Mars in the 8th)",
    4: "Fever (Mercury in the 8th)", 5: "Disease (Jupiter in the 8th)", 6: "Hunger (Venus in the 8th)",
    7: "Thirst (Saturn in the 8th)",
}


def death_circumstances(n: Natal) -> dict:
    """44.25-39: manner and place of death from the 3rd and the 8th; classical study only."""
    manners = []
    for p, text in _DEATH_3RD.items():
        # 44.25-31: the Sun (with strength), Moon and Mars by occupying the 3rd; Mercury, Jupiter and Venus by occupying or aspecting it
        if n.house(p) == 3 and (p != 1 or n.strong(1)) or p >= 4 and n.sees_house(p, 3):
            manners.append(text)
    if (n.house(7) == 3 or n.sees_house(7, 3)) and (n.house(8) == 3 or n.sees_house(8, 3)):
        manners.append("Poison, water, fire, fall or confinement (Saturn and Rahu on the 3rd)")
    if len([p for p in range(1, 10) if n.house(p) == 3 or n.sees_house(p, 3)]) >= 3:
        manners.append("Many diseases (many grahas on the 3rd)")
    for p in n.occupants(8):
        if p in _DEATH_8TH:
            manners.append(_DEATH_8TH[p])
    place = ("Foreign place (movable 3rd)", "Own home (fixed 3rd)", "On the way (dual 3rd)")[n.house_sign(3) % 3]
    if n.has_benefic(3) and not n.has_malefic(3):
        shrine = "Auspicious place / shrine (benefic in the 3rd)"
    elif n.has_malefic(3) and not n.has_benefic(3):
        shrine = "Sinful place (malefic in the 3rd)"
    elif n.has_benefic(3) and n.has_malefic(3):
        shrine = "Mixed place (mixed 3rd)"
    else:
        shrine = "No reading from the 3rd's occupants"
    with_lord9 = lambda group: any(q != n.lord(9) and n.joins(q, n.lord(9)) for q in group)  # noqa: E731  44.37: yuti, not drishti
    if (n.has_benefic(8) or any(n.sees_house(p, 8) for p in n.b7)) and with_lord9(n.b7):
        eighth_place = "Shrine (benefic on the 8th, 9th lord with a benefic)"
    elif (n.has_malefic(8) or any(n.sees_house(p, 8) for p in n.malefics)) and with_lord9(n.malefics):
        eighth_place = "Other than a shrine (malefic on the 8th, 9th lord with a malefic)"
    else:
        eighth_place = "No clear shrine reading from the 8th"
    # 44.33: Jupiter or Venus in the 3rd, conscious; other grahas there, unconscious; an empty 3rd says nothing
    conscious = ("Consciousness at death (Jupiter or Venus in the 3rd)" if any(n.house(p) == 3 for p in (5, 6))
                 else "Unconsciousness before death (other grahas in the 3rd)" if n.occupants(3)
                 else "No reading: the 3rd is empty")
    return {"manners": manners or ["No specific manner from the 3rd or 8th occupants"],
            "place": place, "shrine_3rd": shrine, "shrine_8th": eighth_place, "consciousness": conscious}


def maraka_stars(moon: float) -> List[dict]:
    """44.15-21: the stars counted from the birth star whose lords may kill; the first three by the class of life."""
    star = int((moon % 360.0) // NAK)
    return [{"name": name, "star": (star + k - 1) % 27, "count": k, "lord": TARA_LORDS[(star + k - 1) % 9], "for": who}
            for name, k, who in (("Vipat", 3, SHORT), ("Pratyak", 5, MEDIUM), ("Vadh", 7, LONG), ("23rd star", 23, "Any"))]


def ashtakavarga_years(bav: Sequence[Sequence[int]]) -> dict:
    """71.1-4: each sign's span by its rekhas, in the ashtakavargas of the lagna and the seven planets; the longevity is half the sum."""
    rows = [sum(REKHA_YEARS[r] for r in row) for row in bav]
    return {"rows": rows, "sum": sum(rows), "years": sum(rows) / 2.0}


def saturn_ashtakavarga(saturn_bav: Sequence[int], pinda: int, lagna_sign: int, saturn_sign: int) -> dict:
    """70.37-42 on Saturn's ashtakavarga. The years of distress: the rekhas from the lagna to Saturn, from Saturn to the lagna (both end signs
    counted) and their total. The transits of Saturn: yoga pinda x the rekhas of the 8th from Saturn, the remainder by 27 a star, by 12 a sign."""
    count = lambda a, b: sum(saturn_bav[(a + i) % 12] for i in range((b - a) % 12 + 1))  # noqa: E731
    first, second = count(lagna_sign, saturn_sign), count(saturn_sign, lagna_sign)
    rekhas = saturn_bav[(saturn_sign + 7) % 12]
    product = pinda * rekhas
    return {"lagna_to_saturn": first, "saturn_to_lagna": second, "total": first + second, "rekhas": rekhas, "product": product,
            "stars": [(product - 1 + k) % 27 for k in (0, 9, 18)] if product else [], "signs": [(product - 1 + k) % 12 for k in (0, 4, 8)] if product else []}


def _lagna_lord_with(n: Natal, group: Sequence[int]) -> bool:
    return any(q != n.lord(1) and n.joins(q, n.lord(1)) for q in group)


def _hurt(n: Natal, p: int) -> bool:
    """43.74 read as 43.75-77 are: afflicted (43.74), and no benefic with or aspecting it."""
    return n.afflicted(p) and not n.touched_by(p, n.b7)


def _short_kendra(n: Natal) -> bool:
    bad = [p for p in n.malefics if n.house(p) in KENDRA]
    return bool(bad) and not any(n.touched_by(p, n.b7) for p in bad) and not n.strong(n.lord(1))


def _clean(n: Natal, h: int) -> bool:
    return not n.has_benefic(h) and not any(n.sees_house(p, h) for p in n.b7)


# (verse, what it gives, the condition, the test), all in the rasi chart. "All the malefics" means the seven planets (see Natal).
LONG_LIFE = [
    ("43.55", "Limitless life", "Cancer lagna holding Jupiter and the Moon, Venus and Mercury in kendras, the rest in the 3rd, 6th, 11th",
     lambda n: n.s[0] == 3 and n.house(5) == n.house(2) == 1 and n.house(6) in KENDRA and n.house(4) in KENDRA and n.all_in((1, 3, 7), UPACHAYA)),
    ("43.56", "Super-natural life", "All benefics in kendras or konas, all malefics in the 3rd, 6th, 11th, and a benefic's sign in the 8th",
     lambda n: n.all_in(n.b7, KENDRA + KONA) and n.all_in(n.m7, UPACHAYA) and n.benefic(S.SIGN_LORDS[n.house_sign(8)])),
    ("43.57", "To the end of the Yuga", "Cancer lagna, Jupiter in a kendra in Gopuramsa, Venus in a kona in Paravatamsa",
     lambda n: n.s[0] == 3 and n.house(5) in KENDRA and n.amsa[5] == GOPURA and n.house(6) in KONA and n.amsa[6] == PARAVATA),
    ("43.58", "A sage's span", "Jupiter in the lagna in Simhasanamsa, Saturn in Devalokamsa, Mars in Paravatamsa",
     lambda n: n.house(5) == 1 and n.amsa[5] == SIMHASANA and n.amsa[7] == DEVALOKA and n.amsa[3] == PARAVATA),
    ("43.60", "Full span", "A benefic in a kendra, and the lagna lord with or aspected by a benefic",
     lambda n: any(n.house(p) in KENDRA for p in n.b7) and n.touched_by(n.lord(1), n.b7)),
    ("43.61", "Full span", "The lagna lord in a kendra, with or aspected by both Jupiter and Venus",
     lambda n: n.house(n.lord(1)) in KENDRA and n.touched_by(n.lord(1), (5,)) and n.touched_by(n.lord(1), (6,))),
    ("43.62", "Full span", "Three grahas exalted, among them the lagna and 8th lords, and no malefic in the 8th",
     lambda n: sum(n.exalted(p) for p in range(1, 10)) >= 3 and n.exalted(n.lord(1)) and n.exalted(n.lord(8)) and not n.has_malefic(8)),
    ("43.63", "Long life", "Three grahas in the 8th, exalted or in own or friendly signs, and a strong lagna lord",
     lambda n: len(n.occupants(8)) >= 3 and all(n.dignified(p) for p in n.occupants(8)) and n.strong(n.lord(1))),
    ("43.64", "Long life", "Saturn or the lagna lord with an exalted graha",
     lambda n: any(q != p and n.exalted(q) and n.joins(q, p) for p in (7, n.lord(1)) for q in range(1, 10))),
    ("43.65", "Long life", "All malefics in the 3rd, 6th, 11th and all benefics in kendras",
     lambda n: n.all_in(n.m7, UPACHAYA) and n.all_in(n.b7, KENDRA)),
    ("43.66", "Full span", "Benefics in the 6th, 7th and 8th, and all malefics in the 3rd and 11th",
     lambda n: all(n.has_benefic(h) for h in (6, 7, 8)) and n.all_in(n.m7, (3, 11))),
    ("43.67", "Full span", "The 8th lord a friend of the Sun, all malefics in the 6th and 12th, the lagna lord in a kendra",
     lambda n: NATURAL_RELATIONS_9[n.lord(8) - 1][0] == FRIEND and n.all_in(n.m7, (6, 12)) and n.house(n.lord(1)) in KENDRA),
    ("43.68", "Long life", "A malefic in the 8th and the 10th lord exalted",
     lambda n: n.has_malefic(8) and n.exalted(n.lord(10))),
    ("43.69", "Long life", "A dual lagna, with its lord in a kendra, in a kona or exalted",
     lambda n: n.s[0] % 3 == 2 and (n.house(n.lord(1)) in KENDRA + KONA or n.exalted(n.lord(1)))),
    ("43.70", "Long life", "A dual lagna, and two malefics in kendras from a strong lagna lord",
     lambda n: n.s[0] % 3 == 2 and n.strong(n.lord(1)) and sum(p != n.lord(1) and (n.s[p] - n.s[n.lord(1)]) % 3 == 0 for p in n.malefics) >= 2),
]
SHORT_LIFE = [
    ("43.74", "Short life", "Mars and the 3rd lord, or the 8th lord and Saturn, all combust or with or aspected by malefics, no benefic with or aspecting them",
     lambda n: all(_hurt(n, p) for p in (3, n.lord(3))) or all(_hurt(n, p) for p in (n.lord(8), 7))),
    ("43.75", "Short life", "The lagna lord in the 6th, 8th or 12th with a malefic, no benefic on it",
     lambda n: n.house(n.lord(1)) in DUSTHANA and _lagna_lord_with(n, n.malefics) and not n.touched_by(n.lord(1), n.b7)),
    ("43.76", "Short life", "Malefics in kendras with no benefic on them, and the lagna lord not strong", _short_kendra),
    ("43.77", "Short life", "Malefics in the 12th and 2nd, no benefic in or aspecting them",
     lambda n: n.has_malefic(12) and n.has_malefic(2) and _clean(n, 12) and _clean(n, 2)),
    ("43.78", "Short life", "The lagna and 8th lords without dignity or bala, and no benefic helping them",
     lambda n: n.bare(n.lord(1)) and n.bare(n.lord(8)) and not n.touched_by(n.lord(1), n.b7) and not n.touched_by(n.lord(8), n.b7)),
    ("43.78", "Medium life", "The lagna and 8th lords without dignity or bala, but a benefic helps them",
     lambda n: n.bare(n.lord(1)) and n.bare(n.lord(8)) and (n.touched_by(n.lord(1), n.b7) or n.touched_by(n.lord(8), n.b7))),
]
BALARISHTA = [
    ("9.3", "Early end", "The Moon in the 6th, 8th or 12th aspected by a malefic, no benefic aspect",
     lambda n: n.house(2) in DUSTHANA and n.aspected_by(2, n.malefics) and not n.aspected_by(2, n.b7)),
    ("9.3", "May live to 8", "The Moon in the 6th, 8th or 12th aspected by a malefic and by a benefic",
     lambda n: n.house(2) in DUSTHANA and n.aspected_by(2, n.malefics) and n.aspected_by(2, n.b7)),
    ("9.4", "Within a month", "A retrograde benefic in the 6th, 8th or 12th aspected by a malefic, no benefic in the lagna",
     lambda n: any(n.retro[p] and n.house(p) in DUSTHANA and n.aspected_by(p, n.malefics) for p in n.b7) and not n.has_benefic(1)),
    ("9.6", "Very early", "Mars in the 1st or 8th, with Saturn or the Sun or aspected by a malefic, no benefic aspect",
     lambda n: n.house(3) in (1, 8) and (n.joins(7, 3) or n.joins(1, 3) or n.aspected_by(3, n.malefics)) and not n.aspected_by(3, n.b7)),
    ("9.7", "A fortnight", "Saturn and Mars aspect the lagna, the Sun and Moon with Rahu",
     lambda n: n.sees_house(7, 1) and n.sees_house(3, 1) and n.joins(1, 8) and n.joins(2, 8) and n.joins(1, 2)),
    ("9.8", "Very early, with the mother", "Saturn in the 10th, the Moon in the 6th, Mars in the 7th",
     lambda n: (n.house(7), n.house(2), n.house(3)) == (10, 6, 7)),
    ("9.9", "Very early", "Saturn in the 1st, the Moon in the 8th, Jupiter in the 3rd",
     lambda n: (n.house(7), n.house(2), n.house(5)) == (1, 8, 3)),
    ("9.10", "A month", "The Sun in the 9th, Mars in the 7th, Jupiter and Venus in the 11th",
     lambda n: (n.house(1), n.house(3), n.house(5), n.house(6)) == (9, 7, 11, 11)),
    ("9.11", "Short life", "A graha in the 12th, not aspected by the Sun, Moon, Venus or Rahu",
     lambda n: bool(n.occupants(12)) and not any(n.sees_house(p, 12) for p in (1, 2, 6, 8))),
    ("9.12", "Early end", "The Moon with a malefic in the 1st, 7th or 8th, no benefic on the Moon",
     lambda n: n.house(2) in (1, 7, 8) and any(p != 2 and n.joins(p, 2) for p in n.malefics) and not n.touched_by(2, n.b7)),
    ("9.13", "Early death", "Birth at twilight, in a Moon hora or in gandanta, with the Moon and all malefics in kendras",
     lambda n: (n.twilight or n.moon_hora or n.gandanta()) and n.house(2) in KENDRA and n.all_in(n.m7, KENDRA)),
    ("9.15", "Early death", "Scorpio lagna, all malefics in the eastern half and all benefics in the western",
     lambda n: n.s[0] == 7 and n.all_in(n.m7, (10, 11, 12, 1, 2, 3)) and n.all_in(n.b7, (4, 5, 6, 7, 8, 9))),
    ("9.16", "Early death", "Malefics in the 12th and 6th, or the 8th and 2nd, and the lagna hemmed between malefics",
     lambda n: n.hemmed(n.s[0]) and ((n.has_malefic(12) and n.has_malefic(6)) or (n.has_malefic(8) and n.has_malefic(2)))),
    ("9.17", "Premature death", "Malefics in the 1st and 7th, the Moon with a malefic, no benefic on the Moon",
     lambda n: n.has_malefic(1) and n.has_malefic(7) and any(p != 2 and n.joins(p, 2) for p in n.malefics) and not n.touched_by(2, n.b7)),
    ("9.18", "Early death", "A waning Moon in the lagna, malefics in the 8th and a kendra",
     lambda n: not n.waxing and n.house(2) == 1 and n.has_malefic(8) and any(p != 2 and n.house(p) in KENDRA for p in n.malefics)),
    ("9.19", "Premature death", "The Moon in the 1st, 7th, 8th or 12th, hemmed between malefics",
     lambda n: n.house(2) in (1, 7, 8, 12) and n.hemmed(n.s[2])),
    ("9.20", "Very early, with the mother", "The Moon in the lagna hemmed between malefics, a malefic in the 7th or 8th",
     lambda n: n.house(2) == 1 and n.hemmed(n.s[2]) and (n.has_malefic(7) or n.has_malefic(8))),
    ("9.21", "Very early", "Saturn in the 12th, the Sun in the 9th, Mars in the 8th, no benefic aspect",
     lambda n: (n.house(7), n.house(1), n.house(3)) == (12, 9, 8) and not any(n.aspected_by(p, n.b7) for p in (7, 1, 3))),
    ("9.22", "Early death", "A waning Moon in the lagna, a malefic in the 7th or in the rising drekkana",
     lambda n: not n.waxing and n.house(2) == 1 and (n.has_malefic(7) or any(p != 2 and n.s[p] == n.s[0] and n.lons[p] % 30.0 // 10 == n.lons[0] % 30.0 // 10 for p in n.malefics))),
    ("9.23", "2 or 6 months", "All seven grahas without bala, in apoklimas",
     lambda n: all(n.house(p) in APOKLIMA and not n.strong(p) for p in range(1, 8))),
]
ANTIDOTES = [
    ("10.2", "Destroys all evils", "Mercury, Jupiter or Venus in a kendra", lambda n: any(n.house(p) in KENDRA for p in (4, 5, 6))),
    ("10.3", "Wards off all evils", "A strong Jupiter in the lagna", lambda n: n.house(5) == 1 and n.strong(5)),
    ("10.4", "Counters all evils", "A strong lagna lord in a kendra", lambda n: n.strong(n.lord(1)) and n.house(n.lord(1)) in KENDRA),
    ("10.5", "Destroys all evils", "Night birth in the bright half with a benefic aspecting the lagna, or day birth in the dark half with a malefic aspecting it",
     lambda n: (not n.is_day and n.waxing and any(n.sees_house(p, 1) for p in n.b7)) or (n.is_day and not n.waxing and any(n.sees_house(p, 1) for p in n.malefics))),
    ("10.6", "A hundred years", "Libra lagna with the Sun in the 12th", lambda n: n.s[0] == 6 and n.house(1) == 12),
    ("10.7", "Good for mother and child", "Mars with or aspected by Jupiter", lambda n: n.touched_by(3, (5,))),
    ("10.8", "Evils disappear soon", "Every malefic between benefics, and a benefic in a kendra or kona",
     lambda n: all(any(n.s[q] == (n.s[p] + 1) % 12 for q in n.b7) and any(n.s[q] == (n.s[p] - 1) % 12 for q in n.b7) for p in n.m7) and any(n.house(p) in KENDRA + KONA for p in n.b7)),
]


def rules(n: Natal, table: Sequence[tuple]) -> List[dict]:
    return [{"verse": v, "gives": g, "condition": c, "present": bool(test(n))} for v, g, c, test in table]
