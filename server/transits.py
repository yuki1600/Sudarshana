"""The Transits > Basic Transit Results list: the transit chart against the natal one, mode by mode."""
import re
from datetime import datetime, timedelta

from core_logic import ashtakavarga as AV, ephemeris as E, house_systems as H, kakshyas as KK, key_info as K, time_search as S, varga_charts as V, yoga_engine as Y, natal_chart as N, sign_strength as SS, transits as TR

from . import settings as SET
from .basics import PLANET_ABBR, PLANETS, _tables
from .houses import ORDINAL, _bhavas

BODIES = ["Lagna"] + PLANETS
NAK = 360.0 / 27.0
MURTHI_CLASS = (0, 1, 2, 3, 1, 0, 2, 3, 1, 2, 0, 3)         # by house from the natal Moon
TARA_MEANING = ("Birth", "Wealth", "Danger", "Well-being", "Obstacles", "Achievement", "Death", "Friend", "Good friend")
_ab = lambda i: PLANET_ABBR[i - 1]  # noqa: E731
_lons = lambda ch: [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS]  # noqa: E731


def _murthis(jd, signs, moon_sign, cfg, last=None, d1=None):
    """The murthi of each planet: the Moon's sign at its last entry into its sign, from the natal Moon. Not the Moon's.
    ``last``: (signs, D-1 signs, murthis) of a row a day or less before, whose murthi a graha keeps while its sign and its D-1 sign
    (``d1``, this row's) are both the same: its last entry cannot have moved (the search is ~30 ms a graha)."""
    names = _tables()[0]["murthis"]
    out = {}
    for p in range(1, 9):
        if p != 2:
            if last and last[0][p] == signs[p] and last[1][p] == d1[p]:
                out[p] = last[2][p]
                continue
            entry = max(S.longitude_event(jd, p, a, backward=True, cfg=cfg) for a in (signs[p] * 30.0, signs[p] * 30.0 + 29.9998))
            out[p] = names[MURTHI_CLASS[(int(S.body_longitude(2, cfg)(entry) // 30) - moon_sign) % 12]]
    out[9] = out[8]                                         # Ketu copies Rahu
    return out


REFERENCES = ["Moon", "Lagna", "Arudha lagna"]


def _reference(natal_ch, reference, s):
    """The natal point the house and star counts run from."""
    nl = _lons(natal_ch)
    if reference == 2:
        signs = [int(x // 30) for x in nl]
        return SS.bhava_arudhas(signs, nl, s.arudha_exceptions_bhava, s.arudha_nodes)[0] * 30.0
    return nl[2 if reference == 0 else 0]


def _standard(tb, nl, tl, cfg, ref=None):
    t = _tables()[0]
    ref = nl[2] if ref is None else ref
    moon_sign, moon_nak = int(ref // 30), int(ref / NAK)
    signs = [int(x // 30) for x in tl]
    murthi = _murthis(tb.jd_ut, signs, moon_sign, cfg)
    under = {p: [] for p in range(1, 10)}
    causing = {p: [] for p in range(1, 10)}
    for p in range(1, 10):
        house = (signs[p] - moon_sign) % 12
        if TR.gochara_vedha(signs, p, house):
            sign = (signs[p] + TR.GOCHARA_VEDHA[p][house] - house + 143) % 12
            for q in range(1, 10):
                if signs[q] == sign:
                    under[p].append(BODIES[q])
                    causing[q].append(BODIES[p])
    rows = []
    for p in range(1, 10):
        house = (signs[p] - moon_sign) % 12
        tara = (int(tl[p] / NAK) - moon_nak) % 9
        rows.append([BODIES[p], "%s (%s)" % (t["taras"][tara].strip(), TARA_MEANING[tara]), murthi.get(p, "-"),
                     ORDINAL[house] + (" (Good)" if TR.GOCHARA_GOOD[p][house] > 0 else ""),
                     ", ".join(under[p]) or "-", ", ".join(causing[p]) or "-"])
    return rows


def _houses(nl, tl):
    refs = (int(nl[2] // 30), int(nl[0] // 30), N.compute_varga_d9(nl[2]), N.compute_varga_d9(nl[0]))
    return [[BODIES[p]] + [ORDINAL[(int(tl[p] // 30) - r) % 12] for r in refs] for p in range(1, 10)]


def _ashtakavarga(nl, tl, s, natal_varga=1, transit_varga=1):
    ab = ["As"] + [_ab(i) for i in range(1, 8)]
    opt = SET.varga_options(s)
    nl, tl = [V.varga_longitude(x, natal_varga, opt) for x in nl], [V.varga_longitude(x, transit_varga, opt) for x in tl]
    table = [[[int(c) for c in r] for r in owner] for owner in AV.BINDUS]
    for o, c, h, v in AV.PARASARA_CELLS:
        table[o][c][h] = v
    signs = [int(x // 30) for x in nl[:8]]
    av = AV.ashtakavarga_tables(signs, **SET.ashtakavarga_kw(s))
    rows = []
    for p in range(8):
        s = int(tl[p] // 30)
        lord = TR.KAKSHYA_LORDS[int((tl[p] % 30.0) / 3.75)]
        who = [ab[c] for c in range(8) if table[p][c][(s - signs[c]) % 12]]
        rows.append([BODIES[p], str(av["bav"][p][s]), str(sum(av["bav"][q][s] for q in range(1, 8))), BODIES[lord],
                     str(int(ab[lord] in who)), ", ".join(who)])
    return rows


def _kakshyas(tl):
    """Each body's kakshya: the eighth of its sign (3°45' each) it is in, and that kakshya's lord."""
    dms = lambda d: "%d°%02d'" % (int(d), round(d % 1 * 60))  # noqa: E731
    return [[BODIES[p], k["sign_name"], ORDINAL[k["kakshya_index"]], "%s-%s" % (dms(k["kakshya_start_deg"]), dms(k["kakshya_end_deg"])), k["kakshya_lord"]]
            for p, k in enumerate(KK.get_kakshya_info(x) for x in tl[:10])]


# where the special nakshatra lists' rules come from, under each list: modern teaching, not a classical text (looked up 2026-11-22)
SPECIAL_NAKS_NOTE = ("Special nakshatras, counted from the natal %s's star on the 28-star wheel with Abhijit: Janma 1st, Jaati 4th, Naidhana 7th, "
                     "Karma 10th, Desa 12th, Sanghatika 16th, Samudayika 18th, Aadhaana 19th, Vainasika 22nd, Maanasa 25th, Abhisheka 28th. "
                     "These are the 28-star counts taught in Sanjay Rath's school (Sri Jagannath Centre), which the app follows; classical lists differ "
                     "(Jataka Parijata, as quoted, counts 27 stars and puts Vainasika 23rd, Jaati 25th and Desa 26th).")
NAK_ASPECTS_NOTE = ("Planetary aspects on nakshatras, counted from the graha's own star (its 1st) on the 28-star wheel: Su and Mo 14th, 15th; "
                    "Ma 1st, 3rd, 7th, 8th, 15th; Me and Ve 1st, 15th; Ju 10th, 15th, 19th; Sa 3rd, 5th, 15th, 19th; Ra and Ke none. "
                    "From Sanjay Rath's Crux of Vedic Astrology (p. 11), which names no classical "
                    "source, and they are not the Sarvatobhadra's vedhas. ")


def views(natal_ch, tb, transit_ch, cfg, s, reference=0, natal_varga=1, transit_varga=1):
    nl, tl = _lons(natal_ch), _lons(transit_ch)
    ref = _reference(natal_ch, reference, s)
    transit = dict(enumerate(tl[1:10]))
    names = BODIES[1:]
    aspects = lambda ref: [[n, occ, ", ".join(hits)] for n, (occ, hits) in zip(names, K.transit_special_aspects(transit, ref))]  # noqa: E731
    return [
        {"key": "standard", "name": "Standard", "note": "Reference: %s of natal D-1" % REFERENCES[reference], "rows": _standard(tb, nl, tl, cfg, ref),
         "columns": ["Graha", "Tara", "Murthi", "Bhava", "Under vedha from", "Causing vedha to"]},
        {"key": "houses", "name": "Bhavas from lagna & Moon", "rows": _houses(nl, tl),
         "columns": ["Graha", "From Moon", "From Lagna", "From Navamsa Moon", "From Navamsa Lagna"]},
        {"key": "ashtakavarga", "name": "Ashtakavarga related", "note": "Natal varga: D-%d, Transit varga: D-%d" % (natal_varga, transit_varga), "rows": _ashtakavarga(nl, tl, s, natal_varga, transit_varga),
         "columns": ["Graha", "AV Score", "SAV Score", "Kakshya", "Good?", "Good bhava from references"]},
        {"key": "kakshya", "name": "Kakshyas", "columns": ["Graha", "Sign", "Kakshya", "Span", "Kakshya lord"], "rows": _kakshyas(tl)},
        {"key": "special_naks", "name": "Special nakshatras (Moon)", "columns": ["Graha", "Special nakshatra occupied"], "note": SPECIAL_NAKS_NOTE % "Moon",
         "rows": [[n, s] for n, s in zip(names, K.transit_special_nakshatras(transit, nl[2]))]},
        {"key": "special_naks_lagna", "name": "Special nakshatras (lagna)", "columns": ["Graha", "Special nakshatra occupied"], "note": SPECIAL_NAKS_NOTE % "lagna",
         "rows": [[n, s] for n, s in zip(names, K.transit_special_nakshatras(transit, nl[0]))]},
        {"key": "special_nak_aspects", "name": "Aspects on special nakshatras (Moon)", "rows": aspects(nl[2]),
         "columns": ["Graha", "Occupied special nakshatra", "Special nakshatras aspected"], "note": NAK_ASPECTS_NOTE + SPECIAL_NAKS_NOTE % "Moon"},
        {"key": "special_nak_aspects_lagna", "name": "Aspects on special nakshatras (lagna)", "rows": aspects(nl[0]),
         "columns": ["Graha", "Occupied special nakshatra", "Special nakshatras aspected"], "note": NAK_ASPECTS_NOTE + SPECIAL_NAKS_NOTE % "lagna"},
        {"key": "latta", "name": "Latta", "columns": ["Graha", "Latta on", "Anything special about it"],
         "rows": [[n, a, b] for n, (a, b) in zip(names, K.transit_latta(transit, nl[2], nl[0]))]},
        {"key": "anga_graha", "name": "Anga graha",
         "columns": ["Graha", "Limb (Moon)", "Result (from Moon)", "Limb (lagna)", "Result (from lagna)", "Limb (Sun)", "Result (from Sun)"],
         "rows": [[n, *m, *l, *s] for n, m, l, s in zip(names, K.anga_graha(transit, nl[2]), K.anga_graha(transit, nl[0]),
                                                        K.anga_graha(transit, nl[1]))]},
    ]


CORRELATION_TAGS = {7, 10, 12, 16, 20, 24, 60}      # these print the scheme tag "(Trd)"; the default of each
ARUDHAS = ["AL", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "UL"]


def _correlation_points(ch):
    s = ch["special_lagnas"]
    p = {"Lagna": ch["lagna_lon"], **{n: ch["planet_longitudes"][n] for n in PLANETS}, "Bhava Lagna": s["Bhava_Lagna"],
         "Hora Lagna": s["Hora_Lagna"], "Ghati Lagna": s["Ghati_Lagna"]}
    p.update({a: 0.0 for a in ARUDHAS})     # the transit chart has no arudhas yet when this runs (docs/TODO.md)
    return p


def correlation(natal_ch, transit_ch, tb, cfg, threshold):
    """Longitude Correlation, the Parasara rule: natal points in the vargas aspected by each transit planet above ``threshold`` %.
    The varga rows read the transit chart's points; docs/TODO.md section 4."""
    points = _correlation_points(natal_ch)
    source = _correlation_points(transit_ch)
    found = TR.longitude_correlation(transit_ch["planet_longitudes"], points, source, threshold)
    speed = E.planet_positions(tb.jd_ut, cfg)
    rows = []
    for planet in TR.CORRELATION_ORDER:
        for (name, d), pct in found[planet].items():
            lon = points[name] if d == 1 else V.varga_longitude(source[name], d)
            rows.append({"planet": planet, "lon": transit_ch["planet_longitudes"][planet], "speed": speed[planet]["speed"],
                         "point": "%s in D-%d%s" % (name, d, " (Trd)" if d in CORRELATION_TAGS else ""), "percent": pct, "natal_lon": lon})
    return rows


def correlation_by_orb(natal_ch, transit_ch, tb, cfg, rule, orb, division=1):
    """Longitude Correlation's other rules: 1 conjunction, full, 3/4 and 1/2 aspects within ``orb``; 2 perfect quadrants; 3 perfect trines and the 7th. D-``division``'s transit points against every natal point in that chart."""
    points = _correlation_points(natal_ch)
    speed = E.planet_positions(tb.jd_ut, cfg)
    rows = []
    for planet in TR.CORRELATION_ORDER:
        i = PLANETS.index(planet) + 1
        lon = V.varga_longitude(transit_ch["planet_longitudes"][planet], division)
        for name, x in points.items():
            if name in ARUDHAS:     # the arudhas are signs, not longitudes: nothing to take an orb from
                continue
            nx = V.varga_longitude(x, division)
            hit = TR.transit_aspect_hit(nx, lon, i, rule, orb)
            if hit is not None:
                rows.append({"planet": planet, "lon": lon, "speed": speed[planet]["speed"], "point": "%s in D-%d" % (name, division), "percent": hit, "natal_lon": nx})
    return rows


def calendar(natal_ch, tb, cfg, s, step, count, items, natal_varga=1, transit_varga=1, offset=0):
    """The Transit Calendar: every ``step`` days from ``tb``, the chosen items of each planet, from the chosen vargas of the natal
    and transit charts. ``offset``: rows to skip first (Starlight's Day by day loads a page at a time)."""
    opt = SET.varga_options(s)
    nl = [V.varga_longitude(x, natal_varga, opt) for x in _lons(natal_ch)]
    natal_signs = [int(x // 30) for x in nl[:8]]
    av = AV.ashtakavarga_tables(natal_signs, **SET.ashtakavarga_kw(s))
    moon_nak, moon_sign = int(nl[2] / NAK), natal_signs[2]
    start = datetime(tb.year, tb.month, tb.day) + timedelta(hours=tb.hour_local)
    taras = _tables()[0]["taras"]
    rows, last = [], None
    for k in range(offset, offset + count):
        jd = tb.jd_ut + k * step
        pos = E.planet_positions(jd, cfg)
        lons = [nl[0]] + [V.varga_longitude(pos[p]["lon"], transit_varga, opt) for p in PLANETS]
        signs = [int(x // 30) for x in lons]
        d1 = [0] + [int(pos[p]["lon"] // 30) for p in PLANETS]
        naks = [int(x / NAK) for x in lons]
        murthi = _murthis(jd, signs, moon_sign, cfg, last, d1) if "murthi" in items else {}
        last = (signs, d1, murthi) if step <= 1 else None
        cells = {}
        for p in range(1, 10):
            g = TR.gochara_row(signs, lons, naks, natal_signs, moon_nak, p)
            cell = {"sign": _sign_text(signs[p])}
            if "moon" in items:
                cell["moon"] = _house(g["house_moon"], g["good_moon"], g["vedha_moon"])
            if "lagna" in items:
                cell["lagna"] = _house(g["house_lagna"], g["good_lagna"], g["vedha_lagna"])
            if "tara" in items:
                cell["tara"] = taras[g["tara"]].strip() + (" (good)" if g["tara_good"] else "")
            if "murthi" in items:
                cell["murthi"] = murthi.get(p, "-").split(" - ")[0]
            if "av" in items and p < 8:
                cell["av"] = "%d/%d" % (av["bav"][p][signs[p]], sum(av["bav"][q][signs[p]] for q in range(1, 8)))
            if "kakshya" in items:
                cell["kakshya"] = BODIES[g["kakshya_lord"]]
            cells[BODIES[p]] = cell
        rows.append({"when": start + timedelta(days=k * step), "cells": cells})
    return rows


def _house(h, good, vedha):
    return ORDINAL[h] + (" (vedha)" if vedha else " (good)" if good else "")


def _sign_text(s):
    return "Ar Ta Ge Cn Le Vi Li Sc Sg Cp Aq Pi".split()[s]


DUSTHANA, GOOD_HOUSES, GOOD_PLACES = {6, 8, 12}, {1, 4, 5, 9, 10}, {1, 4, 5, 7, 9, 10}
SADE_SATI = {12: "Sade Sati begins", 1: "Sade Sati, its peak", 2: "Sade Sati ends", 8: "Ashtama Shani", 4: "Kantaka Shani"}
CONTACT_ORB = 3.0
TONES = ["bad", "mixed", "good"]   # the box lists red flags first, then mixed, then supports


def _owners(sign):
    """A sign's lords, as everywhere in the app (SS.owns_sign): its natural lord, and Rahu for Aquarius, Ketu for Scorpio."""
    return [p for p in range(1, 10) if SS.owns_sign(p, sign % 12)]


def flags(natal_ch, transit_ch, s, hs):
    """D-1's red flags and supports against the natal chart: by bhava from the natal lagna and Moon (``hs``, D-1's _Houses), a bhava's
    lords those of the sign on its cusp (_owners); by sign where a graha is on the lagna's or the Moon's sign."""
    from .timeline import in_gandanta
    nl, tl = _lons(natal_ch), _lons(transit_ch)
    lag, moon = int(nl[0] // 30), int(nl[2] // 30)
    sign = lambda p: int(tl[p] // 30)  # noqa: E731
    house = lambda p: hs.asc(tl[p])  # noqa: E731
    from_moon = lambda p: hs.moon(tl[p])  # noqa: E731
    opt = SET.varga_options(s)
    out = []
    add = lambda tone, p, role, at: out.append({"tone": tone, "graha": _ab(p), "role": role, "at": at})  # noqa: E731
    place = lambda h: ORDINAL[h - 1]  # noqa: E731
    lords = {}      # (graha, house it transits): the natal houses it rules and each one's tone, so a graha ruling two is one line
    for h in range(1, 13):
        for p in _owners(hs.sign(h)):
            at = house(p)
            tone = "bad" if (h in DUSTHANA and at == 1) or (h == 1 and at in DUSTHANA) else "good" if h in GOOD_HOUSES and at in GOOD_PLACES else None
            if tone:
                lords.setdefault((p, at), []).append((place(h), tone))
    for (p, at), ruled in lords.items():
        tones = {t for _, t in ruled}
        add(tones.pop() if len(tones) == 1 else "mixed", p, "%s lord" % " & ".join(h for h, _ in ruled), place(at))
    # 22nd drekkana from the lagna and 64th navamsa from the Moon: both 210° on
    for d, ref, what in ((3, nl[0], "22nd drekkana lord"), (9, nl[2], "64th navamsa lord")):
        for p in _owners(int(V.varga_longitude((ref + 210.0) % 360, d, opt) // 30)):
            for where, r in (("1st", lag), ("Mo's sign", moon)):
                if sign(p) == r:
                    add("bad", p, what, where)
    first = _owners(hs.sign(1))
    for p in first:
        if in_gandanta(tl[p]):
            add("bad", p, "1st lord", "Gandanta")
    if 2 not in first and in_gandanta(tl[2]):
        add("bad", 2, "", "Gandanta")
    hsa = from_moon(7)
    if hsa in SADE_SATI:
        add("bad", 7, SADE_SATI[hsa], "%s from Mo" % ORDINAL[hsa - 1])
    hj = from_moon(5)
    if hj in (2, 5, 7, 9, 11):
        add("good", 5, "", "%s from Mo" % ORDINAL[hj - 1])
    if house(5) in (1, 5, 9) and ("good", 5, house(5)) not in lords:
        add("good", 5, "", place(house(5)))
    for p in (8, 9):
        for where, r in (("1st", lag), ("Mo's sign", moon)):
            if sign(p) == r:
                add("bad", p, "", where)
    # a slow graha within a few degrees of the natal lagna or Moon
    for p in (3, 5, 7, 8, 9):
        for what, x, at in (("Lagna", nl[0], place(house(p))), ("Mo", nl[2], "Mo's sign" if sign(p) == moon else place(house(p)))):
            gap = abs((tl[p] - x + 180) % 360 - 180)
            if gap <= CONTACT_ORB:
                add("good" if p == 5 else "bad", p, "%d° from %s" % (max(1, round(gap)), what), at)
    # one line per graha and place it transits: its roles joined, and a good part beside a bad one makes it mixed
    merged = {}
    for f in out:
        m = merged.setdefault((f["graha"], f["at"]), dict(f, role=[]))
        m["tone"] = m["tone"] if m["tone"] == f["tone"] else "mixed"
        m["role"] += [f["role"]] if f["role"] else []
    return sorted((dict(m, role=", ".join(m["role"])) for m in merged.values()), key=lambda f: TONES.index(f["tone"]))


# Starlight's Transits by domain of life: each varga is read for its key houses (from the natal varga lagna) and karakas
DOMAINS = {1: ("Self", (1,), ()), 2: ("Wealth", (2, 11), (5,)), 3: ("Siblings", (3,), (3,)), 4: ("Home & property", (4,), (3, 2)),
           5: ("Fame & authority", (1, 5, 9), (1, 5)), 6: ("Health & disease", (1, 6), (7, 3)), 7: ("Children", (5,), (5,)),
           8: ("Sudden events", (1, 8), (7,)), 9: ("Spouse & dharma", (7, 9), (6, 5)), 10: ("Career", (10,), (1, 7, 4)),
           11: ("Gains", (11,), (5,)), 12: ("Parents", (4, 9), (1, 2)), 16: ("Vehicles & comforts", (4,), (6,)),
           20: ("Spiritual life", (5, 9, 12), (5, 9)), 24: ("Learning", (4, 5), (4, 5)), 27: ("Strength & stamina", (1,), (3,)),
           30: ("Misfortunes", (6, 8, 12), (7,)), 40: ("Mother's line", (4,), (2,)), 45: ("Father's line & character", (9,), (1,)),
           60: ("Past karma", (1,), ()), 81: ("Hidden destiny", (1, 9), (5,)), 108: ("Life's fruit", (1, 9, 12), (5,)),
           144: ("Inherited karma", (4, 9), (1, 2))}
BENEFICS, UPACHAYA = {2, 4, 5, 6}, {3, 6, 10, 11}
STEP = (0, 0.25, 0.02, 0.5, 0.25, 1.0, 0.25, 1.0, 2.0, 2.0)     # days between samples, by graha
MINUTE = 1.0 / 1440.0
HOUSE_LORDS = re.compile(r"^\d+(st|nd|rd|th)( & \d+(st|nd|rd|th))* lord$")


def _in_key(p, h):
    """A graha in a key house: benefics help, and malefics too in an upachaya."""
    return "good" if p in BENEFICS or h in UPACHAYA else "bad"


def _tone(tones):
    return "mixed" if "mixed" in tones or {"good", "bad"} <= tones else next(iter(tones), None)


class _Houses:
    """D-d's houses from the natal chart (``natal``: service._raw's tb, cfg, chart, settings), each function on a D-1 longitude. In D-1 the
    natal bhavas: from the lagna in the Bhava system set (Sripati unless changed), from the Moon in the system for a graha (equal bhavas,
    the Moon in the middle of the 1st, unless changed). In a varga its signs, from the varga lagna and the varga Moon. ``sign(k)``: the
    sign on house k's cusp, whose lords are the house's (as the bhava yogas count them). ``systems``: the two systems' names."""

    def __init__(self, natal, s, d):
        tb, cfg, ch, _ = natal
        self.opt = SET.varga_options(s)
        self.vl = lambda lon: V.varga_longitude(lon, d, self.opt)
        self.lag = int(self.vl(ch["lagna_lon"]) // 30)
        self.moon_sign = int(self.vl(ch["planet_longitudes"]["Moon"]) // 30)
        self.bl = self.bm = None
        names = dict(SET.HOUSE_SYSTEMS)
        self.systems = [names[0], names[0]]
        if d == 1:
            self.bl, self.bm = _bhavas(tb, ch, cfg, s, 0), _bhavas(tb, ch, cfg, s, 2)
            self.cusps = [int((b[1] if s.house_cusp_in_middle else b[0]) % 360.0 // 30) for b in self.bl]
            self.systems = [names[s.house_type], "Equal bhavas" if s.house_type_graha == 1 else names[s.house_type_graha]]

    def asc(self, lon):
        return H.house_of(lon, self.bl) + 1 if self.bl else (int(self.vl(lon) // 30) - self.lag) % 12 + 1

    def moon(self, lon):
        return H.house_of(lon, self.bm) + 1 if self.bm else (int(self.vl(lon) // 30) - self.moon_sign) % 12 + 1

    def sign(self, k):
        return self.cusps[k - 1] if self.bl else (self.lag + k - 1) % 12


def _nature(p):
    return "good" if p in BENEFICS else "bad"


def domain_rows(natal, transit_ch, s, d):
    """Every graha, Sun to Ketu, read for D-d's domain now: the house it transits from the natal varga lagna and from the natal varga
    Moon (_Houses: D-1's bhavas, a varga's signs), every house it rules there, whether it is a karaka, and its contacts: aspecting a key house, or on, opposite or aspecting a
    natal graha in D-d, by sign (on its own natal place: a return). ``key``: in a key house. Only what ties it to the domain (a key
    house, ruling one or the varga lagna, a karaka, a contact with a karaka or key-house lord, D-1: and the natal Moon) colours the
    row; D-1 adds TR.flags. Each contact carries its ``target``: the degree in its sign at which it is exact."""
    _, keys, karakas = DOMAINS[d]
    natal_ch = natal[2]
    hs = _Houses(natal, s, d)
    tl = _lons(transit_ch)
    nv = [hs.vl(x) for x in _lons(natal_ch)]
    cusp = nv[0] % 30.0
    key_lords = [q for k in keys for q in _owners(hs.sign(k))]
    tied = set(karakas) | set(key_lords) | ({2} if d == 1 else set())
    rows = {}
    rules = lambda p: [k for k in range(1, 13) if p in _owners(hs.sign(k))]   # noqa: E731 -- every house it rules, Ra and Ke co-lords of Aq and Sc
    lordship = lambda p: ["%s lord" % " & ".join(ORDINAL[k - 1] for k in rules(p))] if rules(p) else []  # noqa: E731
    for p in range(1, 10):
        h = hs.asc(tl[p])
        ts = int(hs.vl(tl[p]) // 30)        # its sign: aspects and contacts are by sign, the houses by bhava
        ruled = [k for k in rules(p) if k == 1 or k in keys]                   # the ones that tie it to this domain
        roles = lordship(p) + (["karaka"] if p in karakas else [])
        tones = {_in_key(p, h)} if h in keys else set()
        if ruled or p in karakas:       # only its ties to this domain colour the row; its other lordships are just named
            tones |= {"bad"} if h in DUSTHANA else {"good"} if h in GOOD_PLACES else set()
        contacts = [{"kind": "aspect", "what": ORDINAL[k - 1], "natal": False, "domain": True, "target": cusp, "tone": _nature(p)}
                    for k in keys if k != h and Y.graha_drishti(p, ts, hs.sign(k))]
        for q in range(1, 10):
            ns = int(nv[q] // 30)
            kind = "on" if ts == ns else "opposite" if (ts - ns) % 12 == 6 else "aspect" if Y.graha_drishti(p, ts, ns) else None
            if kind and not (q == p and kind != "on") and not ({p, q} == {8, 9} and kind == "opposite"):   # Ra is always opposite Ke
                contacts.append({"kind": kind, "what": "natal " + _ab(q) + (" (return)" if q == p else ""), "natal": True, "domain": q in tied,
                                 "target": nv[q] % 30.0, "tone": _nature(p)})
        contacts.sort(key=lambda c: (c["natal"], ("on", "opposite", "aspect").index(c["kind"])))
        tones |= {c["tone"] for c in contacts if c["domain"]}
        rows[p] = {"graha": _ab(p), "p": p, "house": ORDINAL[h - 1], "key": h in keys, "role": roles, "rules": rules(p), "karaka": p in karakas,
                   "flags": [], "moon_house": hs.moon(tl[p]), "tone": tones, "contacts": contacts}
    if d == 1:
        for f in flags(natal_ch, transit_ch, s, hs):
            p = PLANET_ABBR.index(f["graha"]) + 1
            r = rows[p]
            for part in (f["role"].split(", ") if f["role"] else []) + ([f["at"]] if f["at"] != r["house"] else []):
                if part not in r["role"] and not HOUSE_LORDS.match(part):    # the row already names every house it rules
                    r["role"].append(part)
                    r["flags"].append(part)
            r["tone"].add(f["tone"])
    return [dict(rows[p], role=", ".join(rows[p]["role"]), tone=_tone(rows[p]["tone"])) for p in range(1, 10)]


MEANINGS = {1: "Body, health, temperament and the course of life as a whole.", 2: "Money earned and kept, family resources, what sustains you.",
            3: "Brothers and sisters, courage, initiative and your own efforts.", 4: "Home, land and property, and settled happiness.",
            7: "Children and grandchildren, and what you bring into being.", 9: "Marriage and the partner, dharma, and the inner strength of every graha.",
            10: "Work, status, achievement and public standing.", 12: "Father and mother, ancestry and what you inherit.",
            16: "Vehicles, comforts and luxuries, and the ease they bring.", 20: "Worship, spiritual practice and devotion.",
            24: "Education, knowledge and learning.", 27: "Physical and inner strength, stamina, and where you are weak.",
            30: "Misfortune, illness, enemies and hidden troubles.", 40: "The mother's line: the blessings and troubles that come through it.",
            45: "The father's line, character and conduct.", 5: "Fame, power and authority, and the merit that earns them.",
            6: "Illness and recovery, enemies, debts and daily struggle.", 8: "Longevity, sudden events, accidents and the unexpected.",
            11: "What comes to you: gains, rewards and the fruit of effort.", 60: "Past karma: the whole of life at its finest grain.",
            81: "The navamsa's navamsa: the subtle pattern of fortune behind the D9.", 108: "Past merit ripening: life's final fruit and release.",
            144: "The D12's finest grain: what is inherited through father and mother."}


def domains(natal, transit_ch, s):
    """The domain buttons: each domain, what it covers and is read from, and the grahas in its key houses and aspecting them (for the hover label). shortcut: the Moon shows on D-1 only, standing in for the table's 2-day stay (16 stays cost ~1.5 s)."""
    out = []
    for d, (name, keys, karakas) in DOMAINS.items():
        rows = [r for r in domain_rows(natal, transit_ch, s, d) if r["p"] != 2 or d == 1]
        pick = lambda r, tone: {"graha": r["graha"], "tone": tone}  # noqa: E731
        out.append({"d": d, "name": name, "meaning": MEANINGS[d], "houses": [ORDINAL[k - 1] for k in keys], "karakas": [_ab(p) for p in karakas],
                    "occupants": [pick(r, _in_key(r["p"], ORDINAL.index(r["house"]) + 1)) for r in rows if r["key"]],
                    "aspecting": [pick(r, _nature(r["p"])) for r in rows if not r["key"] and any(c["kind"] == "aspect" and not c["natal"] for c in r["contacts"])]})
    return out


def _bisect(a, b, same):
    """The last moment from a (where ``same``) towards b (where not), to a minute."""
    while abs(b - a) > MINUTE:
        m = 0.5 * (a + b)
        a, b = (m, b) if same(m) else (a, m)
    return a


def _stay(jd, p, where, pos, targets):
    """Graha p's stay at jd where it is (``where``: jd -> its D-n sign, or its bhava): entry, exit, and for each target the moments
    ``pos`` (jd -> a degree growing through the stay: its degree in the sign, or past the bhava's start) crosses it. Sampled, so D-30's
    unequal parts, the reversing schemes and unequal bhavas come out right.
    shortcut: a retrograde wiggle (in and out of a sign, or over a target) shorter than one STEP is missed; sample finer if one shows."""
    step = STEP[p]
    here = where(jd)
    inside = lambda t: where(t) == here  # noqa: E731

    def edge(k):
        t = jd
        while inside(t + k * step):
            t += k * step
        return _bisect(t, t + k * step, inside)
    entry, exit_ = edge(-1), edge(1)
    n = max(2, int((exit_ - entry) / step))
    ts = [entry + (exit_ - entry) * i / n for i in range(n + 1)]
    xs = [pos(t) for t in ts]
    hits = lambda x: [_bisect(ts[i], ts[i + 1], lambda t, below=xs[i] < x: (pos(t) < x) == below)  # noqa: E731
                      for i in range(n) if (xs[i] < x) != (xs[i + 1] < x)]
    return entry, exit_, {x: hits(x) for x in set(targets)}


def domain_timeline(natal, transit_ch, tb, cfg, s, d):
    """The bottom table: each graha's row of ``domain_rows`` with its stay in its house (entry, exit, the house it moves to then, when it
    is on its house's cusp: in D-1 its bhava and the bhava's middle, in a varga its sign and the varga lagna's degree), each contact's
    exact moments in its stay in its sign (contacts are by sign), whether it is retrograde now, its nakshatra and pada,
    the classical verdict from the natal Moon (the gochara table, with vedha) and the info pop-up's texts (lore.transit_info).
    What comes after is ``domain_ahead``'s."""
    from . import lore
    from .timeline import _iso
    name, keys, _ = DOMAINS[d]
    hs = _Houses(natal, s, d)
    cusp = hs.vl(natal[2]["lagna_lon"]) % 30.0      # a varga's bhava madhya: the varga lagna's degree in every house
    jd, tz = tb.jd_ut, tb.tz_east_hours
    tl = _lons(transit_ch)
    mpos = [0] + [hs.moon(x) - 1 for x in tl[1:]]       # the transit grahas' houses from the natal Moon, for vedha (by house, as by sign)
    moments = lambda ts: [{"when": _iso(t, tz), "past": t < jd} for t in ts]  # noqa: E731
    rows = []
    for r in domain_rows(natal, transit_ch, s, d):
        p = r.pop("p")
        f = S.body_longitude(p, cfg)
        contacts = r.pop("contacts")
        vl = lambda t, f=f: hs.vl(f(t))  # noqa: E731
        entry, exit_, hits = _stay(jd, p, lambda t: int(vl(t) // 30), lambda t: vl(t) % 30.0, [cusp] + [c["target"] for c in contacts])
        hn = ORDINAL.index(r["house"]) + 1
        cusps = hits[cusp]
        if hs.bl:       # D-1: the stay in its bhava, and when it is on the bhava's middle
            start, mid, _ = hs.bl[hn - 1]
            entry, exit_, at = _stay(jd, p, lambda t, f=f: hs.asc(f(t)), lambda t, f=f: (f(t) - start) % 360.0, [(mid - start) % 360.0])
            cusps = at[(mid - start) % 360.0]
        mh = r["moon_house"]
        good = TR.GOCHARA_GOOD[p][mh - 1]
        vedha_by = []
        if TR.gochara_vedha(mpos, p, mh - 1):
            at_h = (mpos[p] + TR.GOCHARA_VEDHA[p][mh - 1] - (mh - 1) + 143) % 12
            vedha_by = [_ab(q) for q in range(1, 10) if mpos[q] == at_h]
        rows.append(dict(r, entry=_iso(entry, tz), exit=_iso(exit_, tz), next=ORDINAL[hs.asc(f(exit_ + 2 * MINUTE)) - 1],
                         retro=(f(jd + 0.01) - f(jd) + 180.0) % 360.0 - 180.0 < 0,     # the nodes too, by their motion (the true ones go forward at times)
                         nakshatra={"n": int(tl[p] // NAK) + 1, "pada": int((tl[p] % NAK) // (NAK / 4)) + 1},
                         moon={"house": ORDINAL[mh - 1], "good": good, "vedha": vedha_by},
                         info=lore.transit_info(r["graha"], d, name, hn, mh, r["rules"], r["karaka"], tl[p], good, vedha_by),
                         cusps=moments(cusps),
                         contacts=[dict({k: v for k, v in c.items() if k != "target"}, exact=moments(hits[c["target"]])) for c in contacts]))
    return {"d": d, "name": name, "houses": [ORDINAL[k - 1] for k in keys], "lagna": _sign_text(hs.lag), "systems": hs.systems, "now": _iso(jd, tz), "rows": rows}


AHEAD_YEARS = (1, 2, 5, 10)
AHEAD_CAP = 24                          # events per graha: the fast ones fill it in months, the slow ones reach years
AHEAD_GRAHAS = (1, 3, 4, 5, 6, 7, 8, 9)  # not the Moon: a sign every 2¼ days is the day-by-day calendar's
SPEED = (0, 1.02, 15.4, 0.8, 2.2, 0.25, 1.26, 0.13, 0.22, 0.22)    # about the fastest each graha moves, degrees a day
FAST = {1, 4, 6}                        # Su, Me, Ve meet every natal graha within a year: only their contacts tied to the domain are listed


def _ahead(p, f, hs, jd, end, d, nv, keys, tied, tz):
    """Graha p's coming events from jd to end, in time order, at most AHEAD_CAP: its stays after the present one in a house from the natal
    lagna and from the Moon (``hs``, _Houses: D-1's bhavas, a varga's signs; a new stay when either changes. D-1: every one; a varga's
    change too often to list them all, so those in a key house, the 1st, or aspecting a key house), each retrograde spell (D-1 motion,
    the nodes' excepted) and each moment it is exact on or opposite a natal graha, or aspecting one tied to the domain (in a varga, and for
    FAST grahas, only those), by sign, in the signs after the present one. Returns (events, the moment the list reaches).
    shortcut: a stay's aspects on the key houses are from its sign as it begins (a bhava can reach into the next sign)."""
    from .timeline import _iso
    step = min(STEP[p], 30.0 / d / SPEED[p] / 3.0)       # three samples at least in the shortest stay
    iso = lambda t: _iso(t, tz)  # noqa: E731
    back_at = lambda t: ((f(t + 0.001) - f(t) + 180.0) % 360.0 - 180.0) < 0  # noqa: E731
    vl = hs.vl
    events, stay, spell, contacts = [], None, None, []
    sign_of = lambda t: int(vl(f(t)) // 30)  # noqa: E731
    house_of = lambda lon: (hs.asc(lon), hs.moon(lon))  # noqa: E731
    t, lon = jd, f(jd)
    x, sign, back = vl(lon), int(vl(lon) // 30), p < 8 and back_at(jd)
    where = house_of(lon)
    if back:
        spell = {"kind": "retro", "from": None, "at": jd}
    full = lambda: len(events) >= AHEAD_CAP  # noqa: E731

    def contacts_in(ts):
        out = []
        for q in range(1, 10):
            ns = int(nv[q] // 30)
            kind = "on" if ts == ns else "opposite" if (ts - ns) % 12 == 6 else "aspect" if Y.graha_drishti(p, ts, ns) else None
            if not kind or (q == p and kind != "on") or ({p, q} == {8, 9} and kind == "opposite"):
                continue
            if (kind == "aspect" or d != 1 or p in FAST) and q not in tied:
                continue
            out.append({"kind": kind, "what": "natal " + _ab(q) + (" (return)" if q == p else ""), "domain": q in tied, "target": nv[q] % 30.0, "tone": _nature(p)})
        return out

    def open_stay(t0, h, mh, ts):
        aspects = [ORDINAL[k - 1] for k in keys if k != h and Y.graha_drishti(p, ts, hs.sign(k))]
        good = TR.GOCHARA_GOOD[p][mh - 1]
        note = SADE_SATI.get(mh, "") if d == 1 and p == 7 else ""
        tones = ({_in_key(p, h)} if h in keys else set()) | ({_nature(p)} if aspects else set()) | ({"good"} if good > 0 else {"bad"} if good < 0 else set())
        tones |= {"bad"} if note else set()
        shown = d == 1 or h in keys or h == 1 or bool(aspects)
        return {"kind": "stay", "from": iso(t0), "at": t0, "house": ORDINAL[h - 1], "key": h in keys, "moon": ORDINAL[mh - 1], "good": good,
                "aspects": aspects, "note": note, "tone": _tone(tones), "shown": shown}

    def close_stay(t1):
        if stay and stay.pop("shown"):
            events.append(dict(stay, to=iso(t1)))

    def cross(ta, xa, tb_, xb):
        """The present sign's contacts exact between two moments in it."""
        a, b = xa % 30.0, xb % 30.0
        for c in contacts:
            if (a < c["target"]) != (b < c["target"]):
                when = _bisect(ta, tb_, lambda u, below=a < c["target"], c=c: (vl(f(u)) % 30.0 < c["target"]) == below)
                if when < end and not full():
                    events.append({"kind": c["kind"], "what": c["what"], "domain": c["domain"], "tone": c["tone"], "at": when, "when": iso(when)})

    # past the end (or the cap), only what is open is followed to its close: the last stay and spell keep their real end
    while t < end + 1100.0 and not ((t >= end or full()) and stay is None and spell is None):
        t1 = t + step
        lon1 = f(t1)
        x1 = vl(lon1)
        s1 = int(x1 // 30)
        if p < 8:
            b1 = ((lon1 - lon + 180.0) % 360.0 - 180.0) < 0
            if b1 != back:      # the samples' motion turned: the station lies within a step either side of t
                when = _bisect(max(jd, t - step), t1, lambda u, was=back: back_at(u) == was)
                if b1 and when < end and not full():
                    spell = {"kind": "retro", "from": iso(when), "at": when}
                elif not b1 and spell:
                    events.append(dict(spell, to=iso(when)))
                    spell = None
                back = b1
        if s1 != sign:
            when = _bisect(t, t1, lambda u, was=sign: sign_of(u) == was) + MINUTE
            sign = sign_of(when)
            contacts = contacts_in(sign) if when < end else []
            cross(when, vl(f(when)), t1, x1)
        else:
            cross(t, x, t1, x1)
        w1 = house_of(lon1)
        if w1 != where:
            when = _bisect(t, t1, lambda u, was=where: house_of(f(u)) == was) + MINUTE
            close_stay(when)
            stay = None
            where = house_of(f(when))
            if when < end and not full():
                stay = open_stay(when, *where, sign_of(when))
        t, lon, x = t1, lon1, x1
    if stay and stay.pop("shown"):      # still in it at the search's reach
        events.append(dict(stay, to=None))
    if spell:
        events.append(dict(spell, to=None))
    events.sort(key=lambda e: e["at"])
    reach = events[AHEAD_CAP - 1]["at"] if len(events) >= AHEAD_CAP else end
    return [{k: v for k, v in e.items() if k != "at"} for e in events[:AHEAD_CAP]], _iso(reach, tz)


def domain_ahead(natal, tb, cfg, s, d, years=2):
    """The Transit Calendar's "Coming up": graha by graha, Sun to Ketu without the Moon, what the next ``years`` bring in D-d's domain
    (``_ahead``): each stay with the house it is in from the natal lagna (D-1: its bhava; a varga: counted from the varga lagna's sign),
    aspects among the key houses, and the house from the natal Moon with its classical verdict (the gochara table, without vedha: who
    obstructs changes through a stay); Saturn's Sade Sati and the like in D-1; the retrograde spells; the exact contacts with natal
    grahas. ``reach``: how far each graha's list gets."""
    from .timeline import _iso
    name, keys, karakas = DOMAINS[d]
    hs = _Houses(natal, s, d)
    nv = [hs.vl(x) for x in _lons(natal[2])]
    tied = set(karakas) | {q for k in keys for q in _owners(hs.sign(k))} | ({2} if d == 1 else set())
    jd, tz = tb.jd_ut, tb.tz_east_hours
    end = jd + 365.25 * years
    out = []
    for p in AHEAD_GRAHAS:
        events, reach = _ahead(p, S.body_longitude(p, cfg), hs, jd, end, d, nv, keys, tied, tz)
        out.append({"graha": _ab(p), "events": events, "reach": reach})
    return {"d": d, "name": name, "years": years, "now": _iso(jd, tz), "grahas": out}
