"""factors: the matching's areas of life, one row per factor, each partner's value and how the two go together.

Each partner's side is a dict of what the server works out for that chart:
    lons {graha: longitude}, lagna_lon, sb (chart_shadbala, or None), d9 / d7 {graha or "Lagna": sign},
    ul (Upapada's sign), dk (Darakaraka), kuja (evaluate_kuja_dosha), periods (every Vimsottari mahadasa:
    (lord, start, end, [(antardasa lord, start, end)])) and now.
Every cell is {"text", "tone", "hint"}: tone "good", "mid", "bad" or None (only informs). A graha's or a bhava's cell also
carries its parts, for the table to draw: "g" (graha), "h" (bhava), "s" (its sign's name), "dig" (dignity), "vg" (vargottama), "pct" (strength as a
share of its minimum), "holds" (occupants), "lord" ({"g", "h"}). A cell read in several parts (Kuja from each reference)
carries "parts" [{"text", "tone"}], a dot each. Every row carries its rule.
Sources in docs/SOURCES.md section 16 ("Matching factors")."""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..utils import norm360
from ..natal_chart import RASI_LORDS, get_graha_dignity
from ..aspects_friendships import get_natural_relationship
from ..laghu_parasari import evaluate_functional_nature_for_lagna
from ..miscellany import fertility_reading
from .tables import _ordinal
from .compare import _SIGN_NAMES, _apart, _house, _sign, _sign_dignity

G, M, B = "good", "mid", "bad"
_SCORE = {G: 2, M: 1, B: 0}
_SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
_MALEFICS = ("Sun", "Mars", "Saturn", "Rahu", "Ketu")
_DRISHTI = {"Sun": (7,), "Moon": (7,), "Mercury": (7,), "Venus": (7,), "Mars": (4, 7, 8), "Jupiter": (5, 7, 9), "Saturn": (3, 7, 10)}   # BPHS 26
_KUJA_HOUSES = (1, 2, 4, 7, 8, 12)
_BHAVA_NEED = 7.0


def ab(p: str) -> str:
    return p[:2]


def cell(text: str, tone: Optional[str] = None, hint: str = "", **parts: Any) -> Dict[str, Any]:
    return {"text": text, "tone": tone, "hint": hint, **parts}


def mix(*tones: Optional[str]) -> Optional[str]:
    """The tones' average: good from 1.5 (of 2), middling from 0.75, else bad; None when none has a tone."""
    v = [_SCORE[t] for t in tones if t]
    if not v:
        return None
    m = sum(v) / len(v)
    return G if m >= 1.5 else M if m >= 0.75 else B


def place_tone(h: int) -> Optional[str]:
    return B if h in (6, 8, 12) else G if h in (1, 4, 5, 7, 9, 10) else None


def dignity_tone(d: str) -> Optional[str]:
    return B if d == "Debilitated" else G if d in ("Exalted", "Moolatrikona", "Own Sign") else None


def strength_tone(pct: Optional[int]) -> Optional[str]:
    """A strength as a share of its minimum: good from 100%, middling from 85% (convention), weak below."""
    return None if pct is None else G if pct >= 100 else M if pct >= 85 else B


def occupants_tone(holds: List[str]) -> Optional[str]:
    if not holds:
        return None
    bad = [p for p in holds if p in _MALEFICS]
    return B if len(bad) == len(holds) else M if bad else G


def carry(a: Optional[str], b: Optional[str]) -> Dict[str, Any]:
    """Together, for a factor each chart has: both good, both weak, or one making up for the other (convention)."""
    if a is None and b is None:
        return cell("")
    sa, sb = _SCORE.get(a, 1), _SCORE.get(b, 1)
    if sa == sb == 2:
        return cell("both good", G)
    if sa == sb == 0:
        return cell("both weak", B)
    if {sa, sb} == {0, 2}:
        return cell(f"{'girl' if sa == 2 else 'boy'} carries it", M, "Strong in one chart, weak in the other: the stronger makes up for it")
    if sa + sb == 3:
        return cell("good", G)
    if sa == sb == 1:
        return cell("middling", M)
    return cell(f"{'girl' if sa == 0 else 'boy'} weak", B)


def alone(t: Optional[str]) -> Dict[str, Any]:
    """Together, for a factor read in one chart only."""
    return cell({G: "good", M: "middling", B: "weak"}.get(t, ""), t)


class Side:
    """One partner's chart, read for the rows."""

    def __init__(self, x: Dict[str, Any], who: str):
        self.who = who
        self.lons = x["lons"]
        self.lag = x["lagna_lon"]
        self.ls = _sign(self.lag)
        self.sb = x.get("sb")
        self.d9, self.d7 = x["d9"], x["d7"]
        self.ul, self.dk, self.kuja = x["ul"], x["dk"], x["kuja"]
        self.periods, self.now = x.get("periods") or [], x.get("now") or datetime.now()
        self.fn = evaluate_functional_nature_for_lagna(self.ls)
        from ..shadbala import _REQUIRED_RUPAS
        self.need = dict(zip(_SEVEN, _REQUIRED_RUPAS))

    def sign(self, p: str) -> int:
        return self.ls if p == "Lagna" else _sign(self.lons[p])

    def house(self, p: str) -> int:
        return _house(self.sign(p), self.ls)

    def lord(self, h: int) -> str:
        return RASI_LORDS[(self.ls + h - 1) % 12]

    def holds(self, h: int) -> List[str]:
        return [p for p in self.lons if self.house(p) == h]

    def pct(self, p: str) -> Optional[int]:
        """Shadbala as a share of the rupas the graha needs (BPHS 27.32-36)."""
        if not self.sb or p not in self.need:
            return None
        return round(self.sb["planets"][p]["rupas"] / self.need[p] * 100)

    def bhava_pct(self, h: int) -> Optional[int]:
        return round(self.sb["bhavas"][h - 1]["rupas"] / _BHAVA_NEED * 100) if self.sb else None

    def dignity(self, p: str) -> str:
        d = get_graha_dignity(p, self.lons[p])
        return "" if d in ("General Sign", "Neutral") else d

    def graha(self, p: str, label: str = "") -> Dict[str, Any]:
        """A graha's bhava, dignity and strength: "Ve 6th, own sign · 84%"."""
        h, d, pc = self.house(p), self.dignity(p), self.pct(p)
        text = f"{label or ab(p)} {_ordinal(h)}" + (f", {d.lower()}" if dignity_tone(d) else "") + (f" · {pc}%" if pc is not None else "")
        tone = mix(place_tone(h), dignity_tone(d), strength_tone(pc))
        rupas = f", Shadbala {self.sb['planets'][p]['rupas']:.2f} of the {self.need[p]:g} rupas it needs ({pc}%)" if pc is not None else ""
        return cell(text, tone, f"{p} in the {_ordinal(h)} bhava, in {_SIGN_NAMES[self.sign(p)]}" + rupas,
                    g=label or ab(p), h=h, s=_SIGN_NAMES[self.sign(p)], dig=d if dignity_tone(d) else "", pct=pc)

    def bhava(self, h: int, lord: bool = True) -> Dict[str, Any]:
        """A bhava's strength, who is in it, and where its lord sits: "86% · Sa · lord Ju 9th"."""
        pc, holds, lo = self.bhava_pct(h), self.holds(h), self.lord(h)
        lh = self.house(lo)
        parts = ([f"{pc}%"] if pc is not None else []) + ([" ".join(map(ab, holds))] if holds else []) + ([f"lord {ab(lo)} {_ordinal(lh)}"] if lord else [])
        tone = mix(strength_tone(pc), occupants_tone(holds), place_tone(lh) if lord else None)
        hint = f"{_ordinal(h)} bhava in {_SIGN_NAMES[(self.ls + h - 1) % 12]}" + (f": Bhava Bala {self.sb['bhavas'][h - 1]['rupas']:.2f} of the 7 rupas it needs ({pc}%)" if pc is not None else "") + \
            (f"; holds {', '.join(holds)}" if holds else "; empty") + (f"; its lord {lo} in the {_ordinal(lh)}" if lord else "")
        return cell(" · ".join(parts), tone, hint, pct=pc, s=_SIGN_NAMES[(self.ls + h - 1) % 12], holds=[ab(p) for p in holds], **({"lord": {"g": ab(lo), "h": lh}} if lord else {}))

    def nature(self, p: str) -> Optional[str]:
        """A dasa lord by its functional nature for the lagna (Laghu Parasari): benefic or yogakaraka good, malefic bad."""
        c = self.fn.get(p, {}).get("classification", "")
        return G if c in ("Functional Benefic", "Yogakaraka") else B if c == "Functional Malefic" else M

    def papa(self):
        """Papa samya: each of Su Ma Sa Ra Ke in the 1st, 2nd, 4th, 7th, 8th or 12th from Venus, the Moon and the Lagna, a point.
        (the points, [(reference, its abbreviation, ["Sa 2nd", ...])] for all three, an empty list where it has none)."""
        refs = (("Venus", "Ve", self.sign("Venus")), ("Moon", "Mo", self.sign("Moon")), ("Lagna", "As", self.ls))
        by = [(n, a, [f"{ab(q)} {_ordinal(_house(self.sign(q), r))}" for q in _MALEFICS if q in self.lons and _house(self.sign(q), r) in _KUJA_HOUSES])
              for n, a, r in refs]
        return sum(len(h) for _, _, h in by), by


def row(key: str, factor: str, girl: Dict[str, Any], boy: Dict[str, Any], together: Optional[Dict[str, Any]] = None, rule: str = "",
        about: str = "") -> Dict[str, Any]:
    """A factor's row. "together" is the pair's tone (what the area's verdict averages); "pair" marks one read from the two charts
    at once (a kuta dosha, the Lagnas 6/8, the lords' friendship), worth showing, rather than the two values' tones carried over.
    "about" is what the factor tells of, shown under its name ("the body" under "1st bhava")."""
    return {"key": key, "factor": factor, "about": about, "girl": girl, "boy": boy, "together": together or carry(girl["tone"], boy["tone"]),
            "pair": together is not None and bool(girl["text"] and boy["text"]), "rule": rule}


def _doshas(g: Side, b: Side, match: Dict[str, Any]) -> List[Dict[str, Any]]:
    def kuja_from(s: Side):
        """Mars's bhava counted from Venus, the Moon and the Lagna in one line; red when any is the 1st, 2nd, 4th, 7th, 8th or 12th."""
        hs = s.kuja.get("houses") or {}
        refs = [(r, a, hs[r]) for r, a in (("Venus", "Ve"), ("Moon", "Mo"), ("Lagna", "As")) if hs.get(r)]
        if not refs:
            return cell("")
        basis = "by the bhava cusps" if s.kuja.get("basis") == "bhava" else "by sign"
        hit = [f"the {_ordinal(h)} from {r}" for r, _, h in refs if h in _KUJA_HOUSES]
        return cell(" · ".join(f"{a} – {_ordinal(h)}" for _, a, h in refs), B if hit else G,
                    f"Mars {basis}: " + (f"in {' and '.join(hit)}" if hit else "in none of the 1st, 2nd, 4th, 7th, 8th or 12th"),
                    parts=[{"text": f"{a} – {_ordinal(h)}", "tone": B if h in _KUJA_HOUSES else G} for _, a, h in refs])

    def kuja_cancelled(s: Side):
        """yes and why, each reason led by its graha (Ma in Moola, Ma exalted, Ma in Aries in the 1st, Ju conjunct 4°, Ju aspect 75%), or no."""
        k = s.kuja
        if not k.get("has_kuja_dosha"):
            return cell("no dosha", G, "Mars in none of the 1st, 2nd, 4th, 7th, 8th or 12th from the Lagna, the Moon or Venus")
        if k.get("is_cancelled"):
            why = [{"text": "Ma exalted" if c["dig"] == "Exalted" else "Ma in", "tone": None, "dig": c["dig"]} if c["kind"] == "dignity"
                   else {"text": f"Ju conjunct {c['deg']}°", "tone": None} if c["kind"] == "yuti"
                   else {"text": f"Ju aspect {c['pct']}%", "tone": None} if c["kind"] == "drishti"
                   else {"text": c["text"].replace("Mars in ", "Ma in "), "tone": None} for c in k.get("cancel", [])]
            return cell("yes", G, "Cancelled: " + "; ".join(k.get("cancellations", [])), parts=[{"text": "yes", "tone": G}, *why])
        return cell("no", B, "Kuja dosha, not cancelled")
    ga, ba = (s.kuja.get("has_kuja_dosha") and not s.kuja.get("is_cancelled") for s in (g, b))
    kt = cell("balanced", G, "Both have it: one cancels the other") if ga and ba else cell("none", G) if not (ga or ba) \
        else cell(f"only the {'girl' if ga else 'boy'}", B, "One has an active dosha and the other has none")

    gp, gl = g.papa()
    bp, bl = b.papa()

    def papa(n: int, by):
        """the total, then each reference's points as Kuja's references are written ("9 · Ve – 3 · Mo – 3 · As – 3"), a dot each,
        red where it has any, green where none; every reference shown so the boxes run even; which malefics and where on hover"""
        where = "; ".join(f"from {r}: {', '.join(h)}" for r, _, h in by if h) or "No malefic in those bhavas from any of the three"
        return cell(str(n), None, where, parts=[{"text": str(n), "tone": None}, *({"text": f"{a} – {len(h)}", "tone": B if h else G} for _, a, h in by)])
    d = gp - bp
    papa_t = cell("boy's at least the girl's", G) if d <= 0 else cell(f"girl's {d} more", M if d <= 2 else B, "The boy's malefic points should be at least the girl's")
    return [
        dict(row("kuja_ref", "Kuja – wrt ref", kuja_from(g), kuja_from(b), cell(""),     # shown, not judged: the Cancelled row carries the verdict
                 "Mars's bhava from Venus, the Moon and the Lagna: the 1st, 2nd, 4th, 7th, 8th or 12th from any gives Kuja dosha",
                 about="Mars from Ve, Mo, As"), pair=False),
        row("kuja", "Kuja · cancelled", kuja_cancelled(g), kuja_cancelled(b), kt,
            "Mars in its own sign or exalted, Jupiter with it or aspecting it, or Mars in certain signs in those bhavas cancels it; both having it balances",
            about="undone, and by what"),
        row("papa", "Papa samya", papa(gp, gl), papa(bp, bl), papa_t,
            "A point for each of Su Ma Sa Ra Ke in the 1st, 2nd, 4th, 7th, 8th or 12th from Venus, the Moon and the Lagna; the boy's total should be at least the girl's",
            about="malefics from Ve, Mo, As"),
    ]


def _mind(g: Side, b: Side) -> List[Dict[str, Any]]:
    def moon(s: Side):
        c = s.graha("Moon")
        return {**c, "text": f"{_SIGN_NAMES[s.sign('Moon')]}, " + c["text"].split(" ", 1)[1]}

    def other(s: Side, o: Side):
        h = _house(s.sign("Moon"), o.ls)
        return cell(f"{_ordinal(h)} from the {'boy' if s.who == 'girl' else 'girl'}'s Lagna", place_tone(h), f"The {s.who}'s Moon falls in the {_ordinal(h)} bhava of the other's chart")
    return [
        row("moon", "Moon", moon(g), moon(b), about="the mind", rule="The Moon, karaka of the mind: its sign, bhava, dignity and Shadbala"),
        row("moon_other", "Moon from the other's Lagna", other(g, b), other(b, g), about="how each mind sits with the other",
            rule="Each one's Moon counted from the other's Lagna: a kendra or trikona good, the 6th, 8th or 12th bad"),
    ]


def _marriage(g: Side, b: Side) -> List[Dict[str, Any]]:
    pair = _apart(g.ls, b.ls)
    lt = cell(pair, B if pair in ("6/8", "2/12") else G)
    gl, bl = g.lord(1), b.lord(1)
    rel = {get_natural_relationship(gl, bl), get_natural_relationship(bl, gl)} if gl != bl else {"Same"}
    llt = cell("same lord", G) if gl == bl else cell("enemies", B) if "Enemy" in rel else cell("friends", G) if rel == {"Friend"} else cell("neutral", M)

    def d9_lord(s: Side, h: int):
        l9 = s.d9["Lagna"]
        lo = RASI_LORDS[(l9 + h - 1) % 12]
        hh, dg = _house(s.d9[lo], l9), _sign_dignity(lo, s.d9[lo])
        return cell(f"{ab(lo)} {_ordinal(hh)}" + (f", {dg.lower()}" if dg else ""), mix(place_tone(hh), dignity_tone(dg)), f"The navamsa's {_ordinal(h)} lord, {lo}, in its {_ordinal(hh)}",
                    g=ab(lo), h=hh, s=_SIGN_NAMES[s.d9[lo]], dig=dg)

    def d9_of(s: Side, p: str):
        l9 = s.d9["Lagna"]
        hh, dg = _house(s.d9[p], l9), _sign_dignity(p, s.d9[p])
        vg = s.d9[p] == s.sign(p)
        return cell(f"{_ordinal(hh)}" + (f", {dg.lower()}" if dg else "") + (", vargottama" if vg else ""), mix(place_tone(hh), dignity_tone(dg), G if vg else None),
                    f"{p} in the navamsa's {_ordinal(hh)}" + (", vargottama: the same sign as in the rasi chart" if vg else ""), g=ab(p), h=hh, s=_SIGN_NAMES[s.d9[p]], dig=dg, vg=vg)

    def ul(s: Side):
        h = _house(s.ul, s.ls)
        second = (s.ul + 1) % 12
        inn = [p for p in s.lons if s.sign(p) == second]
        seen = [p for p in _DRISHTI if p in s.lons and _house(second, s.sign(p)) in _DRISHTI[p] and p not in inn]
        mal = [p for p in inn + seen if p in _MALEFICS]
        ben = [p for p in inn + seen if p not in _MALEFICS]
        tone = B if mal and not ben else M if mal else G if ben else None
        bits = ([" ".join(map(ab, inn))] if inn else []) + ([f"asp {' '.join(map(ab, seen))}"] if seen else [])
        return cell(f"{_SIGN_NAMES[s.ul]} ({_ordinal(h)}) · 2nd: " + (", ".join(bits) or "clean"), tone,
                    "Upapada, the arudha of the 12th; the 2nd from it with malefics in or aspecting it threatens the marriage's continuance, with benefics it holds")
    def lagna(s: Side, lo: str):
        return cell(f"{_SIGN_NAMES[s.ls]} · lord {ab(lo)}", None, f"Lagna {_SIGN_NAMES[s.ls]}, its lord {lo}")
    return [
        row("lagnas", "Lagna to Lagna", lagna(g, gl), lagna(b, bl), lt, about="how the two lagnas sit", rule="The two Lagnas 6/8 or 2/12 from each other are hard"),
        row("lagna_lords", "Lagna lords", g.graha(gl), b.graha(bl), llt, about="the two selves", rule="Each Lagna lord's place and strength; together, how the two lords regard each other"),
        row("seventh", "7th bhava", g.bhava(7, lord=False), b.bhava(7, lord=False), about="the spouse", rule="The spouse: the 7th's Bhava Bala (of 7 rupas) and who is in it"),
        row("seventh_lord", "7th lord", g.graha(g.lord(7)), b.graha(b.lord(7)), about="the spouse", rule="The 7th lord's bhava, dignity and Shadbala"),
        row("venus", "Venus", g.graha("Venus"), b.graha("Venus"), about="karaka of marriage", rule="Venus, the karaka of marriage: its bhava, dignity and Shadbala"),
        dict(row("jupiter", "Jupiter", g.graha("Jupiter"), b.graha("Jupiter"), alone(g.graha("Jupiter")["tone"]),     # read in her chart alone
                 about="karaka of the husband", rule="Jupiter, the karaka of the husband, read in the girl's chart (the boy's karaka of the wife is Venus); his Jupiter beside it, not counted in the verdict"), pair=False),
        row("d9_seventh", "D-9 7th lord", d9_lord(g, 7), d9_lord(b, 7), about="the spouse in the navamsa", rule="The navamsa's 7th lord in its bhava and dignity"),
        row("d9_venus", "Venus in D-9", d9_of(g, "Venus"), d9_of(b, "Venus"), about="marriage in the navamsa", rule="Venus's bhava and dignity in the navamsa; vargottama good"),
        row("dk", "Darakaraka", g.graha(g.dk), b.graha(b.dk), about="karaka of the spouse", rule="The Darakaraka (the chara karaka of the spouse): its bhava, dignity and Shadbala"),
        row("upapada", "Upapada", ul(g), ul(b), about="the marriage's continuance", rule="Upapada and the 2nd from it: malefics there break, benefics keep"),
    ]


def _family(g: Side, b: Side) -> List[Dict[str, Any]]:
    def d7(s: Side):
        l7 = s.d7["Lagna"]
        lo = RASI_LORDS[(l7 + 4) % 12]
        hh, dg = _house(s.d7[lo], l7), _sign_dignity(lo, s.d7[lo])
        return cell(f"{ab(lo)} {_ordinal(hh)}" + (f", {dg.lower()}" if dg else ""), mix(place_tone(hh), dignity_tone(dg)), f"The saptamsa's 5th lord, {lo}, in its {_ordinal(hh)}",
                    g=ab(lo), h=hh, s=_SIGN_NAMES[s.d7[lo]], dig=dg)

    def sphuta(s: Side):
        male = s.who == "boy"
        lon = norm360(s.lons["Sun"] + s.lons["Venus"] + s.lons["Jupiter"]) if male else norm360(s.lons["Moon"] + s.lons["Mars"] + s.lons["Jupiter"])
        r = fertility_reading(lon, male)
        nav = int(lon // (10.0 / 3.0)) % 12
        odd = lambda i: "odd" if i % 2 == 0 else "even"  # noqa: E731
        return cell(f"{'Beeja' if male else 'Kshetra'} {odd(_sign(lon))}, {odd(nav)}", r,
                    f"{'Su + Ve + Ju' if male else 'Mo + Ma + Ju'} = {_SIGN_NAMES[_sign(lon)]}, navamsa {_SIGN_NAMES[nav]}: " +
                    {G: "children", M: "children with effort", B: "difficulty"}[r])
    return [
        row("fifth", "5th bhava", g.bhava(5), b.bhava(5), about="children", rule="Children: the 5th's Bhava Bala, who is in it, and where its lord sits"),
        row("fifth_lord", "5th lord", g.graha(g.lord(5)), b.graha(b.lord(5)), about="children", rule="The 5th lord's bhava, dignity and Shadbala"),
        row("putra", "Jupiter", g.graha("Jupiter"), b.graha("Jupiter"), about="karaka of children", rule="Jupiter, the karaka of children"),
        row("d7", "D-7 5th lord", d7(g), d7(b), about="children in the saptamsa", rule="The saptamsa (the varga of children): its 5th lord's bhava and dignity"),
        row("sphuta", "Beeja · Kshetra", sphuta(g), sphuta(b), about="fertility",
            rule="The boy's Beeja sphuta (Su + Ve + Ju) in an odd sign and navamsa, the girl's Kshetra sphuta (Mo + Ma + Ju) in an even sign and navamsa: children; mixed, with effort"),
        row("fourth", "4th bhava", g.bhava(4), b.bhava(4), about="home and comforts", rule="Home and comforts: the 4th's Bhava Bala, occupants and lord"),
        row("second", "2nd bhava", g.bhava(2), b.bhava(2), about="family and wealth", rule="Family and wealth: the 2nd's Bhava Bala, occupants and lord"),
        row("eleventh", "11th bhava", g.bhava(11), b.bhava(11), about="gains", rule="Gains: the 11th's Bhava Bala, occupants and lord"),
    ]


def _health(g: Side, b: Side) -> List[Dict[str, Any]]:
    return [
        row("lagna", "1st bhava", g.bhava(1, lord=False), b.bhava(1, lord=False), about="the body", rule="The body: the 1st's Bhava Bala and who is in it"),
        row("lagna_lord", "Lagna lord", g.graha(g.lord(1)), b.graha(b.lord(1)), about="vitality", rule="The Lagna lord's bhava, dignity and Shadbala"),
        row("eighth", "8th bhava", g.bhava(8), b.bhava(8), about="longevity", rule="Longevity (and in the girl's chart the mangalya, the marriage's life): the 8th's Bhava Bala, occupants and lord"),
        row("sixth", "6th bhava", g.bhava(6), b.bhava(6), about="illness and disputes", rule="Illness and disputes: the 6th's Bhava Bala, occupants and lord"),
    ]


def _when(d: datetime) -> str:
    return d.strftime("%b %Y")


def _timing(g: Side, b: Side) -> List[Dict[str, Any]]:
    """The running Vimsottari periods and the next mahadasa; empty when a chart's 120 years are over."""
    def running(s: Side):
        mds = [m for m in s.periods if m[2] > s.now]
        if not mds:
            return None, None
        ad = next(a for a in mds[0][3] if a[2] > s.now)
        return (mds[0][0], ad), mds[1] if len(mds) > 1 else None
    (gn, gx), (bn, bx) = running(g), running(b)
    if not (gn and bn):
        return []

    def now(s: Side, md_ad):
        md, ad = md_ad[0], md_ad[1][0]
        return cell(f"{ab(md)}–{ab(ad)} to {_when(md_ad[1][2])}", mix(s.nature(md), s.nature(ad)),
                    f"{md} mahadasa, {ad} antardasa; by their functional nature for the Lagna")

    def next_md(s: Side, m):
        return cell(f"{ab(m[0])} from {_when(m[1])}", s.nature(m[0]), f"{m[0]} mahadasa next, from {_when(m[1])}") if m else cell("")
    if gx and bx and abs((gx[1] - bx[1]).days) <= 365:
        sandhi = cell(f"both change around {_when(min(gx[1], bx[1]))}", B, "Both mahadasas change within a year of each other (dasa sandhi in both)")
    else:
        sandhi = cell("apart", G, "The two mahadasas change more than a year apart")
    return [
        row("dasa_now", "Dasa now", now(g, gn), now(b, bn), about="the running periods", rule="The running Vimsottari periods, by the functional nature of their lords for each Lagna"),
        row("dasa_next", "Next mahadasa", next_md(g, gx), next_md(b, bx), sandhi, about="when the periods change", rule="The next mahadasa; both changing within a year of each other is avoided"),
    ]


# the lords whose periods bring marriage, the first four the strongest (convention: docs/SOURCES.md "Marriage in the dasas")
_STRONG = ("7th lord", "in the 7th", "Venus", "Darakaraka")


def marriage_lords(s: Side) -> Dict[str, List[str]]:
    """Each graha's ties to marriage: the 7th lord, a graha in the 7th, Venus (the karaka of marriage), the Darakaraka,
    the girl's Jupiter (the husband's karaka), the navamsa's 7th lord and Upapada's lord."""
    tags: Dict[str, List[str]] = {}
    add = lambda p, t: tags.setdefault(p, []).append(t)  # noqa: E731
    add(s.lord(7), "7th lord")
    for p in s.holds(7):
        add(p, "in the 7th")
    add("Venus", "Venus")
    add(s.dk, "Darakaraka")
    if s.who == "girl":
        add("Jupiter", "husband's karaka")
    add(RASI_LORDS[(s.d9["Lagna"] + 6) % 12], "D-9 7th lord")
    add(RASI_LORDS[s.ul], "Upapada lord")
    return tags


def marriage_dasas(x: Dict[str, Any], who: str) -> Dict[str, Any]:
    """Every Vimsottari mahadasa and antardasa, each with its lord's ties to marriage. An antardasa is "likely" when both its lord
    and the mahadasa's are tied, one of them strongly (7th lord, in the 7th, Venus, Darakaraka); "possible" when either is tied strongly."""
    s = Side(x, who)
    tags = marriage_lords(s)
    strong = lambda p: any(t in _STRONG for t in tags.get(p, []))  # noqa: E731
    out = []
    for md, start, end, ads in s.periods:
        rows = []
        for ad, a0, a1 in ads:
            both = md in tags and ad in tags and (strong(md) or strong(ad))
            rows.append({"lord": ad, "start": a0, "end": a1, "tags": tags.get(ad, []),
                         "level": "likely" if both else "possible" if strong(md) or strong(ad) else None})
        out.append({"lord": md, "start": start, "end": end, "tags": tags.get(md, []), "ads": rows, "now": start <= s.now < end})
    return {"tags": tags, "periods": out}


AREAS = [("doshas", "Doshas"), ("mind", "Mind"), ("marriage", "Marriage"), ("family", "Family"), ("health", "Health"), ("timing", "Timing")]


def match_factors(girl: Dict[str, Any], boy: Dict[str, Any], match: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The areas, each with its rows and a tone: for the doshas the worst of them, for the rest their average. An area with
    no rows is left out (Timing, when a chart's Vimsottari periods have run out)."""
    g, b = Side(girl, "girl"), Side(boy, "boy")
    rows = {"doshas": _doshas(g, b, match), "mind": _mind(g, b), "marriage": _marriage(g, b), "family": _family(g, b),
            "health": _health(g, b), "timing": _timing(g, b)}
    out = []
    for key, name in AREAS:
        if not rows[key]:
            continue
        tones = [r["together"]["tone"] for r in rows[key]]
        tone = (B if B in tones else M if M in tones else G) if key == "doshas" else mix(*tones)
        out.append({"id": key, "name": name, "tone": tone, "rows": rows[key]})
    return out
