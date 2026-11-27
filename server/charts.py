"""The chart pane: which chart a panel shows, which bodies it draws, and the questions its menu answers. The signs come from
core_logic.varga_charts; each view's bodies are set by its flags below."""
import re
from typing import Literal

from pydantic import BaseModel, Field

from core_logic import house_systems as H, key_info as K, time_search as JS, varga_charts as V, yoga_engine as Y, shadbala as SB, sign_strength as SS, special_lagnas_upagrahas as U

from . import settings as S
from .basics import PLANET_ABBR, PLANETS, SIGNS, VARGA_NAMES, _points
from .houses import ORDINAL, house_type

ABBR = ["As"] + PLANET_ABBR
BODIES = ["Lagna"] + PLANETS
ARUDHA = ["AL", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "UL"]
OPTIONAL = {"nodes": ["Rahu", "Ketu"], "outer": ["Uranus", "Neptune", "Pluto"], "al": ["AL"], "arudhas": ARUDHA[1:], "hl": ["Hora Lagna"], "gl": ["Ghati Lagna"], "sl": ["Sree Lagna"],
            "bb": ["Bhrigu Bindu"], "pp": ["Pranapada Lagna"], "md": ["Maandi"], "gk": ["Gulika"]}
SHORT = {"Hora Lagna": "HL", "Ghati Lagna": "GL", "Bhava Lagna": "BL", "Vighati Lagna": "VG", "Pranapada Lagna": "PP", "Sree Lagna": "SL", "Indu Lagna": "IL", "Bhrigu Bindu": "BB", "Kunda": "Ku", "Dhooma": "Dh",
         "Vyatipata": "Vy", "Parivesha": "PV", "Indra Chapa": "IC", "Upaketu": "UK", "Kaala": "Kl", "Mrityu": "Mri", "Artha Prahara": "AP", "Yama Ghantaka": "YG", "Maandi": "Md", "Gulika": "Gk",
         "Uranus": "Ur", "Neptune": "Ne", "Pluto": "Pl", "Varnada Lagna": "VL", **{p: a for p, a in zip(PLANETS, PLANET_ABBR)}, **{"V%d" % i: "V%d" % i for i in range(2, 13)}}
UPAGRAHAS = ["Dhooma", "Vyatipata", "Parivesha", "Indra Chapa", "Upaketu", "Kaala", "Mrityu", "Artha Prahara", "Yama Ghantaka", "Maandi", "Gulika"]
DUAL = [("Ma1", 3, 0), ("Me3", 4, 2), ("Ju9", 5, 8), ("Ve2", 6, 1), ("Sa10", 7, 9), ("Ma8", 3, 7), ("Me6", 4, 5), ("Ju12", 5, 11), ("Ve7", 6, 6), ("Sa11", 7, 10)]
VIEWS = ("standard", "with_graha_arudhas", "upagraha", "graha_arudha", "dual_graha_arudha", "chandra_arudha", "surya_arudha", "varnada", "chara_karaka", "special_lagna")
CLASS_NAMES = ["Self", "Great friend", "Friend", "Neutral", "Enemy", "Great enemy"]


class ChartSpec(BaseModel):
    """Which chart a panel shows: a varga in its chosen scheme, the bhava chart based on one, or a research chart."""
    kind: Literal["varga", "bhava", "custom", "sub"] = "varga"
    d: int = Field(1, ge=1)                # the varga; custom: the number of parts
    m: int = 9                             # sub: D-n of D-m
    n: int = 1
    cyclic: bool = False                   # custom
    from_sign: bool = False
    reverse_even: bool = False
    start: int = Field(0, ge=0, le=9)


def _check(spec):
    if spec.kind in ("varga", "bhava") and spec.d not in V.DIVISIONS:
        raise ValueError("no such division: D-%d" % spec.d)
    if spec.kind == "sub" and (spec.m not in V.DIVISIONS or spec.n not in V.DIVISIONS):
        raise ValueError("no such division")
    if spec.kind == "custom" and spec.d > 3600:
        raise ValueError("enter at most 3600 parts")


def needs_houses(s, spec):
    """The bhava chart of D-1 follows the house system of its reference (Sripati, Placidus ..) when it is not one of the equal ones."""
    return spec.kind == "bhava" and spec.d == 1 and house_type(s, s.bhava_ref) >= 3


def sign_of(ch, s, spec):
    """longitude -> sign in the chart ``spec``. ``ch["bhavas"]``: the houses (service.with_houses), for the bhava chart of D-1 in a system other than equal."""
    _check(spec)
    opt = S.varga_options(s)
    if spec.kind == "custom":
        return lambda x: V.custom_varga(x, spec.d, spec.cyclic, spec.from_sign, spec.reverse_even, spec.start)
    if spec.kind == "sub":
        return lambda x: V.sub_varga(x, spec.m, spec.n, opt)
    if spec.kind == "varga":
        return lambda x: V.varga_sign(x, spec.d, opt)
    if needs_houses(s, spec):
        # the other house systems apply in D-1 only: the first house is in the reference's sign
        bh = ch["bhavas"]
        first = int(([ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS])[s.bhava_ref] // 30) if s.bhava_ref else ch["lagna_sign"]
        return lambda x: (first + H.house_of(x, bh)) % 12
    ref = ([ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS])[s.bhava_ref]
    return lambda x: V.bhava_chart_sign(V.varga_longitude(x, spec.d, opt), V.varga_longitude(ref, spec.d, opt), s.bhava_ref >= 8, s.house_cusp_in_middle, s.bhava_nodes_reversed)


# The scheme tag of each division's title, by scheme
TAGS = {2: ["CnL", "Jn", "Pv", "SN", "Md", "KN", "US", "Lm", "Rm", "RmM", "Ni", "NiM"], 3: ["Trd", "Pv", "Sn", "Jn", "US"], 4: ["", "Pv"], 5: ["", "Pv"], 7: ["Trd", "", ""], 8: ["", "Ra"], 9: ["", "K", "KM", "UKM"],
        10: ["Trd", "Pv", "", "", ""], 11: ["", "Ra"], 12: ["Trd", "Rev"], 16: ["Trd", "Rev"], 20: ["Trd", "Rev"], 24: ["Rev", "Trd", "Rev2"], 27: ["Trd", "Rev"], 30: ["", "Pv", "Sh"], 60: ["Trd", "Rev", "RvAr", "Ar"], 81: ["", "K"]}
REF_NAME = ["Asc", "Sun", "Moon", "Mars", "Merc", "Jup", "Ven", "Sat", "Rah", "Ket"]


def _tagged(n, s):
    opt = S.varga_options(s)
    tag = TAGS[n][getattr(opt, "d%d" % n)] if n in TAGS else ""
    return "D-%d (%s)" % (n, tag) if tag else "D-%d" % n


def title_of(spec, s):
    if spec.kind == "custom":
        return "Custom D-%d" % spec.d
    if spec.kind == "sub":
        return "Sub D-%d x D-%d" % (spec.m, spec.n) if spec.n != 1 else "Sub %s" % _tagged(spec.m, s)
    if spec.kind == "bhava":
        return "Bhava/Chalit D-%d (%s)" % (spec.d, REF_NAME[s.bhava_ref])
    return "Rasi" if spec.d == 1 else "%s %s" % (VARGA_NAMES[spec.d], _tagged(spec.d, s))


def _arudhas(ch, s, spec, signs, sign):
    """The 12 house arudhas of this chart."""
    rasi = _nine(ch)
    if not s.arudha_longitude:
        return SS.bhava_arudhas(signs, rasi, s.arudha_exceptions_bhava, s.arudha_nodes)
    nodes_base = s.arudha_base in (8, 9)
    base_of = lambda lons: ch["special_lagnas"]["Bhava_Lagna"] if s.arudha_base == 10 else lons[s.arudha_base]  # noqa: E731
    if s.arudha_div_longs and spec.kind == "varga":
        opt = S.varga_options(s)
        vl = [V.varga_longitude(x, spec.d, opt) for x in rasi]
        vs = [int(x // 30) for x in vl]
        return [int(x // 30) for x in SS.longitude_bhava_arudhas(base_of(vl), lambda g: vl[SS.sign_lord(g, vs, rasi)], s.arudha_exceptions_bhava, nodes_base)]
    rs = [int(x // 30) for x in rasi]
    return [sign(x) for x in SS.longitude_bhava_arudhas(base_of(rasi), lambda g: rasi[SS.sign_lord(g, rs, rasi)], s.arudha_exceptions_bhava, nodes_base)]


def _nine(ch):
    return [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS]


def _outer(ch):
    return ch.get("outer", {})


def placements(ch, s, spec, sign=None):
    """Every body a view can draw: label -> sign (``sign``: another chart's, as ``panel``)."""
    sign = sign or sign_of(ch, s, spec)
    pts = {**_points(ch), **_outer(ch)}
    nine = _nine(ch)
    signs = [sign(x) for x in nine]
    out = {SHORT[n]: sign(x) for n, x in pts.items() if n in SHORT and n not in PLANETS}
    out.update({a: g for a, g in zip(ABBR, signs)})
    vl = U.compute_varnada_lagnas(signs[0] * 30.0, sign(ch["special_lagnas"]["Hora_Lagna"]) * 30.0)     # per-varga, see tables._sign_in
    out.update({"VL" if i == 0 else "V%d" % (i + 1): int(x // 30) for i, x in enumerate(vl)})
    arudhas = _arudhas(ch, s, spec, signs, sign)
    out.update(dict(zip(ARUDHA, arudhas)))
    out["_arudhas"] = arudhas
    out["_graha"] = {PLANET_ABBR[p - 1]: SS.graha_arudha(p, signs, nine, s.arudha_exceptions_graha) for p in range(1, 10)}
    exc = s.arudha_exceptions_graha
    dual = {}
    for label, p, own in DUAL:     # the same rule from one own sign (BPHS 29.6-7, counted from that sign)
        a = (own * 2 + 144 - signs[p]) % 12
        dual[label] = (a + 141) % 12 if exc and (a - signs[p]) % 6 == 0 else a
    out["_dual"] = dual
    return out


def bodies(ch, s, spec, view="standard", optional=None, sign=None):
    """[(label, sign)] of the bodies of a view (by the view's flags)."""
    on = {**{k: True for k in OPTIONAL}, "outer": False, **(optional or {})}
    p = placements(ch, s, spec, sign)
    pick = lambda labels: [(a, p[a]) for a in labels if a in p]  # noqa: E731
    lagna = pick(["As", "HL", "GL"])
    al = pick(["AL"])
    standard = pick(ABBR[:8])
    for key, names in OPTIONAL.items():
        if on.get(key):
            standard += pick([SHORT.get(n, n) for n in names])
    if view in ("standard", "with_graha_arudhas"):
        return standard
    if view == "upagraha":
        return lagna + al + pick([SHORT[n] for n in UPAGRAHAS])
    if view == "graha_arudha":
        return lagna + [(a, g) for a, g in p["_graha"].items()]
    if view == "dual_graha_arudha":
        return lagna + [(a, p["_graha"][a]) for a in ("Su", "Mo", "Ra", "Ke")] + list(p["_dual"].items())
    if view in ("chandra_arudha", "surya_arudha"):
        ref = p["Mo" if view == "chandra_arudha" else "Su"]
        turn = (ref - p["As"]) % 12
        return [(a, g) for a, g in standard if a not in ARUDHA] + [(a, p["_arudhas"][(i + turn) % 12]) for i, a in enumerate(ARUDHA) if on["arudhas"] or i == 0]
    if view == "varnada":
        return lagna + al + pick(ABBR[1:]) + pick(["VL"] + ["V%d" % i for i in range(2, 13)])
    if view == "chara_karaka":
        return lagna + pick(ABBR[1:]) + pick(ARUDHA)
    return lagna + al + pick(["VG", "PP", "SL", "IL", "BB", "VL"])     # special lagna view


def panel(ch, s, spec, view="standard", optional=None, karakas=None, user_points=None, retro_all=False, sign=None):
    """A chart panel. A retrograde planet of the rasi is marked in the rasi only (``retro_all``: in every varga, as its text charts do); the chara karaka view labels Sun .. Rahu by their karaka.
    ``sign``: another chart's longitude -> box, in place of this chart's own (a transit's bhava chart placed in the natal houses)."""
    sign = sign or sign_of(ch, s, spec)
    boxes = {g: [] for g in range(12)}
    for label, g in bodies(ch, s, spec, view, optional, sign):
        if karakas and label in karakas:
            label = karakas[label]
        elif (retro_all or spec.kind == "varga" and spec.d == 1) and label in PLANET_ABBR and ch["retrograde"].get(PLANETS[PLANET_ABBR.index(label)]) and view != "graha_arudha":
            label += "R"
        boxes[g].append(label)
    for label, lon in (user_points or {}).items():
        boxes[sign(lon)].append(label)
    if ch.get("prasna_lagna") is not None:
        boxes[sign(ch["prasna_lagna"])].append("PLag")
    out = {"title": title_of(spec, s), "lagna": sign(ch["lagna_lon"]), "boxes": boxes, "arudha_view": view in ("graha_arudha", "dual_graha_arudha")}
    if ch.get("muntha") is not None:      # a varga takes the Muntha's own sign there (MunthaPreference), not the varga of its longitude
        m = ch["muntha_signs"][V.DIVISIONS.index(spec.d)] if spec.kind == "varga" and spec.d in V.DIVISIONS and ch.get("muntha_signs") else sign(ch["muntha"])
        boxes[m].append("Mu")
        out["muntha"] = m
    if spec.kind in ("varga", "bhava"):     # each graha's sign and degrees in it of this varga (a bhava chart: of the varga it is based on), for the chart that shows them
        opt = S.varga_options(s)
        out["degrees"] = {a: V.varga_longitude(x, spec.d, opt) % 30 for a, x in zip(ABBR, _nine(ch))}
        # the varga longitudes of the nine, the outer planets, maandi and gulika: the transit chart shows them all with their degrees and signs
        more = {SHORT[n]: x for n, x in {**_points(ch), **_outer(ch)}.items() if n in ("Uranus", "Neptune", "Pluto", "Maandi", "Gulika")}
        out["longitudes"] = {a: V.varga_longitude(x, spec.d, opt) for a, x in [*zip(ABBR, _nine(ch)), *more.items()]}
        out["degrees"].update({a: out["longitudes"][a] % 30 for a in ("Ur", "Ne", "Pl") if a in out["longitudes"]})     # drawn with their degrees too, when shown
        if ch.get("muntha") is not None:
            out["degrees"]["Mu"] = V.varga_longitude(ch["muntha"], spec.d, opt) % 30
            if spec.kind == "bhava":    # its longitude too, so a bhava chart names the rasi it moved from, as the grahas'
                out["longitudes"]["Mu"] = V.varga_longitude(ch["muntha"], spec.d, opt)
    # in every chart, for the charts that colour them. Rahu and Ketu too: by their own motion, always with the mean nodes,
    # with the true nodes not while they move forward
    out["retro"] = [a for a, p in zip(PLANET_ABBR, PLANETS) if ch["retrograde"].get(p)]
    return out


# Highlight rasi(s): the signs each option picks

def argala_signs(rasi, ketu_sign, virodha=False):
    """Having argala on ``rasi``: the 2nd, 4th, 11th, 5th from it; from Ketu's own sign they count backward. Virodhargala: the 12th, 10th, 3rd, 9th, the same way."""
    steps = (1, 3, 10, 4) if rasi != ketu_sign else (11, 9, 2, 8)
    if virodha:
        steps = (11, 9, 2, 8) if rasi != ketu_sign else (1, 3, 10, 4)
    return sorted((rasi + k) % 12 for k in steps)


def highlight(ch, s, spec, kind, planet=None, rasi=None):
    sign = sign_of(ch, s, spec)
    signs = [sign(x) for x in _nine(ch)]
    if kind == "argala":
        return argala_signs(rasi, signs[9])
    if kind == "virodhargala":
        return argala_signs(rasi, signs[9], True)
    if kind == "rasi_drishti_of_rasi":
        return [g for g in range(12) if g != rasi and Y.rasi_drishti(rasi, g)]
    if kind == "graha_drishti":
        return [g for g in range(12) if Y.graha_drishti(planet, signs[planet], g)]
    if kind == "rasi_drishti":
        return [g for g in range(12) if g != signs[planet] and Y.rasi_drishti(signs[planet], g)]
    if kind == "owned":
        return [g for g in range(12) if SS.owns_sign(planet, g)]
    table = {"moolatrikona": SS.MOOLATRIKONA, "exalted": SS.EXALTATION, "debilitated": SS.DEBILITATION}[kind]
    return [table[planet]] if table[planet] < 12 else []


def relationships(ch, s, spec, kind, planet):
    """The class (0 self, 1 great friend .. 5 great enemy) of each of Sun .. Ketu to ``planet``, by the five-fold relationship (BPHS 3.55-58)."""
    sign = sign_of(ch, s, spec)
    signs = [sign(ch["planet_longitudes"][p]) for p in PLANETS]
    me = planet - 1
    if kind == "permanent":
        row = SB.NATURAL_RELATIONS_9[me]
    elif kind == "temporary":
        row = [0 if j == me else 2 if (signs[j] - signs[me]) % 12 in (1, 2, 3, 9, 10, 11) else 4 for j in range(9)]
    else:
        row = SB.compound_relationships(signs)[me]
    return {a: row[i] for i, a in enumerate(PLANET_ABBR)}


def _duration(days):
    secs = round(abs(days) * 86400)
    d, h, m, c = secs // 86400, secs % 86400 // 3600, secs % 3600 // 60, secs % 60
    return ("%d days " % d if d else "") + "%d:%02d:%02d" % (h, m, c)


def when_changes(birth, ch, s, cfg, spec, body):
    """"When will lagna / this planet change sign in this chart?": how far the birth time would have to move, in a varga's division."""
    _check(spec)
    parts = spec.d if spec.kind == "varga" else 1
    since, until = JS.varga_window(birth.jd_ut, body, parts, cfg, birth)
    return "%s changes sign in %s chart, if the birthtime is\n%s earlier, or\n%s later." % (BODIES[body], title_of(spec, s), _duration(since), _duration(until))


def marana(ch, s, spec):
    """"Planets in marana karaka sthana" (0x00442xxx's message): by house from the lagna, Ketu has none."""
    sign = sign_of(ch, s, spec)
    signs = [sign(x) for x in _nine(ch)]
    houses = (12, 8, 7, 7, 3, 6, 1, 9)
    lines = ["%s is in the %s from lagna." % (PLANETS[p], ORDINAL[houses[p] - 1]) for p in range(8) if (signs[p + 1] - signs[0]) % 12 + 1 == houses[p]]
    return "\n".join(lines) or "No graha is in marana karaka sthana in %s." % title_of(spec, s)


def pachakadi(ch, s, spec, planet=None, rasi=None):
    sign = sign_of(ch, s, spec)
    signs = [sign(x) for x in _nine(ch)][1:8]
    if planet is not None:
        got = K.pachakadi_signs(planet, signs)
        return "\n".join("%s: %s" % (k, SIGNS[v]) for k, v in got.items())
    got = K.pachakadi_of_rasi(rasi, signs)
    return "\n".join("%s: %s" % (k, ", ".join(PLANETS[p - 1] for p in v) or "-") for k, v in got.items())


def move_lagna(birth, cfg, forward):
    """"Change birthtime to move lagna to the next / previous sign": the moment just past the lagna's sign change."""
    since, until = JS.varga_window(birth.jd_ut, 0, 1, cfg, birth)
    return birth.jd_ut + (until + 1.0 / 1440.0 if forward else -since - 1.0 / 1440.0)


TEXT_ORDER = ABBR + ["HL", "GL", "Md", "Gk", "AL"]              # ChartText prints k = 0..9, 14, 15, 31, 32, 59 only, in this order
TEXT_BODIES = set(TEXT_ORDER)
GRID = {(0, 1): 0, (0, 2): 1, (0, 3): 2, (1, 3): 3, (2, 3): 4, (3, 3): 5, (3, 2): 6, (3, 1): 7, (3, 0): 8, (2, 0): 9, (1, 0): 10, (0, 0): 11}


def _text_bodies(p, g):
    return sorted((a for a in p["boxes"][g] if a.rstrip("R") in TEXT_BODIES), key=lambda a: TEXT_ORDER.index(a.rstrip("R")))


def text_south(p):
    """"Copy chart as text", South Indian: 5 lines a cell, two bodies a line.
    A retrograde graha as the app writes it, "Sa(R)", the two on a line a space apart so two of them fill the cell's 11. The North and
    East copies write "SaR": their slots are three wide, some four apart."""
    def lines(g):
        names = [re.sub(r"^(%s)R$" % "|".join(ABBR), r"\1(R)", x) for x in _text_bodies(p, g)]
        return [" ".join(names[i:i + 2]).ljust(11) for i in range(0, 10, 2)]
    cell = {g: lines(g) for g in range(12)}
    empty = " " * 23
    words = p["title"].split(" D-")
    head, foot = (words[0], "D-" + words[1]) if len(words) > 1 else ("", "")
    centre = lambda t: (" " * ((23 - len(t)) // 2) + t).ljust(23)  # noqa: E731
    out = ["+" + "-" * 47 + "+"]
    for r in range(4):
        for i in range(5):
            if r in (1, 2):
                mid = centre(head) if (r, i) == (1, 4) else centre(foot) if (r, i) == (2, 0) else empty
                out.append("|%s|%s|%s|" % (cell[GRID[(r, 0)]][i], mid, cell[GRID[(r, 3)]][i]))
            else:
                out.append("|" + "|".join(cell[GRID[(r, c)]][i] for c in range(4)) + "|")
        if r < 3:
            title = centre(words[0]) if r == 1 and len(words) == 1 else empty       # a title of one line sits on the middle rule
            out.append("|-----------%s-----------|" % ("|" + title + "|" if r == 1 else "+" + "-" * 23 + "+"))
    out.append("+" + "-" * 47 + "+")
    return "\n".join(out)


# The North and East Indian text charts. Their tables:
# the cell of each house (North) or sign (East) as (row, column), which of the five slot lists it uses, and each list's ten (line, column).
NORTH_DIAMONDS = ("| \\                   /   \\                   / |", "|   \\               /       \\               /   |", "|     \\           /           \\           /     |",
                  "|       \\       /               \\       /       |", "|         \\   /                   \\   /         |", "|           x                       x           |",
                  "|         /   \\                   /   \\         |", "|       /       \\               /       \\       |", "|     /           \\           /           \\     |",
                  "|   /               \\       /               \\   |", "| /                   \\   /                   \\ |")
NORTH_BOX = (" " * 49, "+" + "-" * 47 + "+", *NORTH_DIAMONDS, "|                       x                       |", *NORTH_DIAMONDS, "+" + "-" * 47 + "+")
NORTH_CELLS = ((0, 1), (0, 0), (0, 0), (1, 0), (2, 0), (2, 0), (2, 1), (2, 2), (2, 2), (1, 2), (0, 2), (0, 2))
NORTH_USES = (0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 1)
NORTH_SLOTS = (((5, 11), (3, 11), (7, 11), (5, 5), (5, 17), (4, 11), (6, 11), (2, 11), (4, 6), (4, 16)),
               ((1, 11), (0, 8), (0, 13), (2, 8), (2, 13), (1, 6), (1, 16), (3, 11), (0, 18), (0, 3)),
               ((5, 1), (5, 6), (4, 1), (6, 1), (3, 3), (7, 3), (2, 1), (8, 1), (4, 6), (4, 6)),
               ((9, 11), (10, 8), (10, 13), (8, 8), (8, 13), (9, 6), (9, 16), (7, 11), (10, 18), (10, 3)),
               ((5, 20), (5, 15), (4, 20), (6, 20), (3, 19), (7, 19), (2, 20), (8, 20), (4, 16), (4, 16)))
EAST_FRAME = ("+-----------------------------------------------+", "| \\             |               |             / |", "|   \\           |               |           /   |",
              "|     \\         |               |         /     |", "|       \\       |               |       /       |", "|         \\     |               |     /         |",
              "|           \\   |               |   /           |", "|             \\ |               | /             |", "|---------------+---------------+---------------|",
              *["|               |               |               |"] * 7, "|---------------+---------------+---------------|",
              "|             / |               | \\             |", "|           /   |               |   \\           |", "|         /     |               |     \\         |",
              "|       /       |               |       \\       |", "|     /         |               |         \\     |", "|   /           |               |           \\   |",
              "| /             |               |             \\ |", "+---------------+---------------+---------------+")
EAST_BARE = ("\\               |               |               /", "  \\             |               |             /  ", "    \\           |               |           /    ",
             "      \\         |               |         /      ", "        \\       |               |       /        ", "          \\     |               |     /          ",
             "            \\   |               |   /            ", "              \\ |               | /              ", "----------------+---------------+----------------",
             *["                |               |                "] * 7, "----------------+---------------+----------------",
             "              / |               | \\              ", "            /   |               |   \\            ", "          /     |               |     \\          ",
             "        /       |               |       \\        ", "      /         |               |         \\      ", "    /           |               |           \\    ",
             "  /             |               |             \\  ", "/               |               |               \\")
EAST_CELLS = ((0, 1), (0, 0), (0, 0), (1, 0), (2, 0), (2, 0), (2, 1), (2, 2), (2, 2), (1, 2), (0, 2), (0, 2))
EAST_USES = (0, 1, 2, 0, 3, 4, 0, 2, 1, 0, 4, 3)
EAST_SLOTS = (((1, 3), (1, 10), (2, 3), (2, 10), (3, 3), (3, 10), (4, 3), (4, 10), (5, 3), (5, 10)),
              ((3, 11), (1, 11), (1, 6), (0, 8), (2, 12), (2, 7), (4, 12), (0, 3), (0, 12), (5, 13)),
              ((3, 2), (5, 2), (5, 7), (6, 6), (4, 1), (4, 6), (2, 2), (6, 1), (6, 10), (1, 1)),
              ((3, 2), (1, 2), (1, 7), (0, 6), (2, 1), (2, 6), (4, 2), (0, 1), (0, 10), (5, 1)),
              ((3, 11), (5, 11), (5, 6), (6, 8), (4, 12), (4, 7), (2, 12), (6, 3), (6, 12), (1, 13)))


def _boxed(template, place):
    """The template as a flat buffer of 51 characters a line, with each cell's bodies written over it. ``place``: 0-11 and a slot's (line, column) -> offset."""
    buf = list("\r\n".join(template) + "\r\n")
    for i in range(12):
        for slot, name in place(i):
            buf[slot:slot + 3] = name.ljust(3)
    return buf


def _write(buf, at, text):
    buf[at:at + len(text)] = text


def text_north(p):
    """"Copy chart as text", North Indian: the houses from the lagna, the lagna's sign number in the first, the varga's name (and D-n) on the top line."""
    def place(h):
        row, col = NORTH_CELLS[h]
        return [(51 + col * 12 + row * 306 + (line + 1) * 51 + at, name)
                for (line, at), name in zip(NORTH_SLOTS[NORTH_USES[h]], _text_bodies(p, (p["lagna"] + h) % 12))]
    buf = _boxed(NORTH_BOX, place)
    _write(buf, 0x249, str(p["lagna"] + 1))
    words = p["title"].split(" D-")
    if len(words) > 1:
        _write(buf, 0, words[0])
        _write(buf, 49 - len(words[1]) - 2, "D-" + words[1])
    else:
        _write(buf, (49 - len(words[0])) // 2, words[0])
    return "".join(buf).replace("\r\n", "\n").rstrip("\n")


def text_east(p, frame=False):
    """"Copy chart as text", East Indian: the signs in their fixed places, the varga's name (and D-n) in the middle cell. Style code 3 has no frame, code 4 and the south-north-east copy have one."""
    def place(g):
        row, col = EAST_CELLS[g]
        return [(col * 16 + row * 408 + (line + 1) * 51 + at, name)
                for (line, at), name in zip(EAST_SLOTS[EAST_USES[g]], _text_bodies(p, g))]
    buf = _boxed(EAST_FRAME if frame else EAST_BARE, place)
    words = p["title"].split(" D-")
    _write(buf, (0x23e if len(words) > 1 else 0x271) + (23 - len(words[0])) // 2, words[0])
    if len(words) > 1:
        _write(buf, 0x2a4 + (23 - len(words[1]) - 2) // 2, "D-" + words[1])
    return "".join(buf).replace("\r\n", "\n").rstrip("\n")


def text_chart(p, kind="south"):
    """A chart as text (South, North or East Indian), and the south-north-east copy, which frames its East chart."""
    if kind == "all":
        return "\n\n".join((text_south(p), text_north(p), text_east(p, True)))
    return {"south": text_south, "north": text_north, "east": text_east}[kind](p)
