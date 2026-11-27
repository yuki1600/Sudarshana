"""The Longevity tab: each method of core_logic.ayurdaya as a section {id, name, source, verdict, tables, notes}, its tables in the {columns, rows} of the other views.
Rudra and Trishoola follow the Shoola dasas of Jaimini (JUS 2.2-2.3; PVR ch. 22-23).

Primary reading path (BPHS, Jaimini): Three Pairs → Marakas → Niryana Shoola timing; Pinda/Amsa/Nisarga and the rest corroborate."""
import re

from core_logic import ayurdaya as A, ephemeris as E, house_systems as H, key_info as K, varga_charts as V, natal_chart as N, sign_strength as SS

from . import settings as S
from .basics import PLANETS, SIGNS as SHORT_SIGNS, _tables
from .houses import _bhavas
from .strengths import SEVEN, ashtakavarga_view, vaiseshikamsa_of
from .tables import BODIES, _lon, _table

SIGNS = N.RASI_NAMES_EN
MODES = ("movable", "fixed", "dual")
AB = ["As", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"]      # Starlight's two-letter grahas
# 44.10-14: the ages of each class of life; the two outer classes have no years in SPAN_YEARS, so BEYOND says what stands for them
WINDOWS = {A.VERY_SHORT: (0.0, 32.0), A.SHORT: (0.0, 32.0), A.MEDIUM: (32.0, 64.0), A.LONG: (64.0, 100.0), A.EXTREME: (100.0, 120.0)}
BEYOND = {A.VERY_SHORT: "Up to 20 (Yog Arisht, 43.53)", A.EXTREME: "Above 100 (44.10-14)"}
AGE_ROWS = (A.SHORT, A.MEDIUM, A.LONG)                                  # the help's first, middle and last 4 of a Shoola dasa's 12


def natal_of(b, ch, cfg, s):
    sb = E.chart_shadbala(b, ch, cfg)
    day = E.day_lords(b, cfg, **S.day_kw(s))
    vai = vaiseshikamsa_of(ch, s, day)
    ghatis, day_length = day["janma_ghatis"], day["day_ghatis"]
    points = [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS]
    per = lambda key: [0.0] + [sb["planets"][p][key] for p in SEVEN] + [0.0, 0.0]  # noqa: E731
    bh = _bhavas(b, ch, cfg, s)
    return A.Natal(points, bhavas=[H.house_of(x, bh) + 1 for x in points], hora_lagna=ch["special_lagnas"]["Hora_Lagna"], retro=[False] + [bool(ch["retrograde"].get(p)) for p in PLANETS], bala=per("total"), percent=per("percent"),
                   lagna_bala=sb["bhavas"][0]["total"], natures=sb["natures"], amsa=[0] + [vai[p]["dasa"] for p in PLANETS], is_day=day["is_day"],
                   # 9.14: 3 ghatis either side of the night
                   twilight=day_length + day["night_ghatis"] - ghatis <= 3.0 or day_length <= ghatis <= day_length + 3.0, moon_hora=day["hora_lord"] == 2,
                   by_motion=s.combustion_by_motion, classical=s.combustion_classical, orbs=s.longevity_orbs, cusps=[m for _, m, _ in bh], saturn_rule=s.longevity_saturn, jupiter_rule=s.longevity_jupiter,
                   outer_years=s.longevity_outer_years), sb


def _named(title, columns, rows):
    return {"title": title, **_table(columns, rows)}


def _section(id_, name, source, verdict, tables, notes=(), headline=None, primary=False, data=None):
    """``data``: the same results as values, for the Starlight view; ``tables`` and ``notes`` are the Windows layout's and Copy's."""
    out = {"id": id_, "name": name, "source": source, "verdict": verdict, "tables": tables, "notes": list(notes), "primary": primary, "data": data or {}}
    if headline is not None:
        out["headline"] = headline
    return out


def _y(x):
    return "%.2f" % x


def _nth(h):
    return "%d%s" % (h, {1: "st", 2: "nd", 3: "rd"}.get(h, "th"))


def _names(points):
    return ", ".join(BODIES[p] for p in points) or "-"


def _yes(on):
    return "Yes" if on else "-"


def _span(r):
    """The years of a three-pairs result, or what stands for them in the classes with no table."""
    return "%d" % r["years"] if r["years"] else BEYOND[r["class"]]


def _body(label, p, sign):
    name = label if p is None or label in ("Saturn", "Moon", "Lagna") else "%s %s" % (label, BODIES[p])
    return "%s in %s (%s)" % (name, SIGNS[sign], MODES[sign % 3])


def pairs_section(n, r):
    rows = [["%s and %s" % (a[0], b[0]), _body(*a, sa), _body(*b, sb), c] for (a, b), (sa, sb), c in zip(r["groups"], r["signs"], r["classes"])]
    steps = [["How it is decided", r["decided"]], ["Class before Saturn and Jupiter", r["base"]], ["Contributors", ", ".join(r["contributors"])],
             ["Their average degree in the sign", _y(r["average"])], ["Saturn (43.47)", r["saturn"]], ["Jupiter (43.48)", r["jupiter"]], ["Final class", r["class"]],
             ["Span by class and agreement (43.41-44)", _span(r)]]
    if r["years"]:
        steps += [["Rectified inside the class, Jaimini compartment", "%s (the span runs from %d down to %d across the sign)" % (_y(r["rectified"]), r["years"], r["floor"])],
                  ["Rectified literally, 43.45-46", "%s (full at the start of a sign, nil at its end)" % _y(r["literal"])]]
    verdict = "%s: %s years" % (r["class"], _span(r)) + (", rectified %s" % _y(r["rectified"]) if r["years"] else "")
    body = lambda label, p, sign: {"label": label, "graha": None if p is None or label in ("Saturn", "Moon", "Lagna") else AB[p], "sign": SHORT_SIGNS[sign], "mode": sign % 3}  # noqa: E731
    data = {"pairs": [{"name": "%s and %s" % (a[0], b[0]), "a": body(*a, sa), "b": body(*b, sb), "class": c, "contributes": c == r["base"]}
                      for (a, b), (sa, sb), c in zip(r["groups"], r["signs"], r["classes"])],
            "decided": r["decided"], "votes": r["votes"], "base": r["base"], "saturn": r["saturn"], "jupiter": r["jupiter"], "falls": r["falls"], "rises": r["rises"],
            "class": r["class"], "years": r["years"], "span": _span(r), "floor": r["floor"], "rectified": r["rectified"], "average": r["average"], "contributors": r["contributors"],
            # 43.45-46: each contributor's degrees in its sign (the nodes counted back), whose average rectifies the span
            "degrees": [{"label": label, "graha": None if p is None else AB[p], "deg": A._degrees(n, p)}
                        for g, c in zip(r["groups"], r["classes"]) if c == r["base"] for label, p in g]}
    return _section("pairs", "Three Pairs", "BPHS 43.33-50; Jaimini Upadesa Sutras", verdict,
                    [_named("The three pairs", ["Pair", "First", "Second", "Class"], rows), _named("The result", ["Step", "Result"], steps)],
                    ["Both movable, or fixed and dual: long. Movable and fixed, or both dual: medium. Movable and dual, or both fixed: short.",
                     "The compartments are the usual Jaimini reading and are not in our BPHS text. Taken literally, 43.45-46 can drop a long-life chart below its own class.",
                     "43.47 also records the opposite opinion, that some raise the class when Saturn contributes. This screen lowers it, the verse's first reading, so a short class can fall to very short."],
                    primary=True, data=data)


def _reduced(x):
    return ("%.3f" % x) if x else "-"


def _arc_table(title, n, span):
    rows = [[BODIES[r["point"]], _lon(n.lons[r["point"]]), r["full"], _y(r["gross"]), _reduced(r["visible"]), _yes(r["combust"]), _yes(r["enemy"]), _y(r["lagna_cut"]) if r["lagna_cut"] else "-", _y(r["net"])] for r in span["rows"]]
    rows += [["Lagna", _lon(n.lons[0]), "-", _y(span["lagna"]), "-", "-", "-", "-", _y(span["lagna"])], ["Total", "", "", "", "", "", "", "", _y(span["total"])]]
    return _named("%s (the lagna counted by %s)" % (title, span["lagna_basis"]), ["Body", "Longitude", "Full years", "By arc", "Visible half", "Combust", "Enemy sign", "Malefic in lagna", "Net years"], rows)


def _amsa_table(n, span):
    rows = [[BODIES[r["point"]], _lon(n.lons[r["point"]]), _y(r["gross"]), {3: "x3", 2: "x2", 1: "-"}[r["factor"]], _reduced(r["visible"]), _yes(r["combust"]), _yes(r["enemy"]), _y(r["net"])] for r in span["rows"]]
    rows += [["Lagna", _lon(n.lons[0]), _y(span["lagna"]), "-", "-", "-", "-", _y(span["lagna"])], ["Total", "", "", "", "", "", "", _y(span["total"])]]
    return _named("Amsayu", ["Body", "Longitude", "Navamsa years", "Trebled or doubled", "Visible half", "Combust", "Enemy sign", "Net years"], rows)


SPAN_NAMES = {"amsa": "Amsayu", "pinda": "Pindayu", "nisarga": "Nisargayu"}
JUDGES = {"amsa": "Lagna (Bhava Bala)", "pinda": "Sun (Shadbala)", "nisarga": "Moon (Shadbala)"}


def spans_section(n, sp):
    verdict = "%s: %s years, %s" % (" and ".join(SPAN_NAMES[k] for k in sp["chosen"]), _y(sp["years"]), A.class_of_years(sp["years"]))
    choice = [[JUDGES[k], "%.2f" % (sp["strength"][k] / 60.0), "%.0f%%" % sp["percent"][k], SPAN_NAMES[k], _y(sp[k]["total"]), A.class_of_years(sp[k]["total"]), _yes(k in sp["chosen"])] for k in ("amsa", "pinda", "nisarga")]
    def rows(span):
        return [{"graha": AB[r["point"]], "lon": _lon(n.lons[r["point"]]), "full": r.get("full"), "gross": r["gross"], "factor": r.get("factor", 1), "visible": r["visible"],
                 "combust": r["combust"], "enemy": r["enemy"], "lagnaCut": r.get("lagna_cut", 0.0), "net": r["net"]} for r in span["rows"]]
    data = {"judges": [{"id": k, "judge": ("Lagna", "Su", "Mo")[i], "rupas": sp["strength"][k] / 60.0, "percent": sp["percent"][k], "span": SPAN_NAMES[k], "years": sp[k]["total"],
                        "class": A.class_of_years(sp[k]["total"]), "chosen": k in sp["chosen"]} for i, k in enumerate(("amsa", "pinda", "nisarga"))],
            "years": sp["years"], "class": A.class_of_years(sp["years"]),
            "spans": {k: {"rows": rows(sp[k]), "lagna": sp[k]["lagna"], "lagnaLon": _lon(n.lons[0]), "basis": sp[k].get("lagna_basis", "navamsas"), "total": sp[k]["total"]}
                      for k in ("pinda", "amsa", "nisarga")}}
    return _section("spans", "Pinda Amsa Nisarga", "BPHS 43.4-22, 43.30-32", verdict,
                    [_named("Which span applies (43.30-32)", ["Bala of", "Rupas", "Of its minimum", "Span it picks", "Years", "Class (44.10-14)", "Chosen"], choice),
                     _arc_table("Pindayu", n, sp["pinda"]), _amsa_table(n, sp["amsa"]), _arc_table("Nisargayu", n, sp["nisarga"])],
                    ["Visible half: the share a graha in the 7th to 12th loses; only the strongest in a bhava loses it. Combust and enemy sign together only halve (43.22).",
                     "Strongest against its minimum: the Lagna's Bhava Bala over 7 rupas, the Sun's and Moon's Shadbala over their required rupas.",
                     "BPHS gives Nisargayu only its fixed years, so it is worked here by the arc and reductions of Pindayu, as later texts do."], data=data)


def life_and_death(n, sb):
    """The help: for good longevity the 3rd and 8th bhavas and their lords strong, the 2nd and 7th and theirs weak. Bhava Bala in rupas,
    the lords' Shadbala as a share of the required (the nodes have none, so they are left out)."""
    rupas = lambda hs: sum(sb["bhavas"][h - 1]["rupas"] for h in hs)  # noqa: E731
    lords = lambda hs: [n.percent[p] for p in {n.lord(h) for h in hs} if 1 <= p <= 7]  # noqa: E731
    mean = lambda xs: sum(xs) / len(xs) if xs else None  # noqa: E731
    life, death, life_lords, death_lords = rupas((3, 8)), rupas((2, 7)), mean(lords((3, 8))), mean(lords((2, 7)))
    votes = [life > death] + ([life_lords > death_lords] if life_lords is not None and death_lords is not None else [])
    outcome = "Supports long life" if all(votes) else "Shortens life" if not any(votes) else "Mixed"
    return {"life": life, "death": death, "lifeLords": life_lords, "deathLords": death_lords, "outcome": outcome}


def eighth_section(n, sb, av):
    pl, sr, ld = A.placement(n), A.sun_relation(n), life_and_death(n, sb)
    strength = lambda p: "%.0f%%" % n.percent[p] if 1 <= p <= 7 else "-"  # noqa: E731
    in_bhava = lambda h: [p for p in range(1, 10) if n.bhava(p) == h]  # noqa: E731
    placed = [["Lagna lord", BODIES[pl["lagna_lord"]], strength(pl["lagna_lord"]), SIGNS[n.s[pl["lagna_lord"]]], _nth(n.bhava(pl["lagna_lord"]))],
              ["8th lord", BODIES[pl["eighth_lord"]], strength(pl["eighth_lord"]), SIGNS[n.s[pl["eighth_lord"]]], _nth(n.bhava(pl["eighth_lord"]))]]
    relation = [["Lagna lord %s towards the Sun" % BODIES[sr["lord"]], sr["relation"], sr["class"] or "No reading: the Sun is the lord"]]
    houses, rows = [], []
    for h, role in ((8, "Longevity"), (3, "Vitality"), (2, "Death: the stronger maraka bhava"), (7, "Death")):
        lord, sign = n.lord(h), n.house_sign(h)
        aspects = [p for p in range(1, 10) if n.aspects(p, sign) and n.house(p) != h]
        rows.append({"house": h, "life": h in (3, 8), "sign": SHORT_SIGNS[sign], "lord": AB[lord], "lordIn": n.bhava(lord), "lordBala": n.percent[lord] if 1 <= lord <= 7 else None,
                     "rupas": sb["bhavas"][h - 1]["rupas"], "occupants": [AB[p] for p in in_bhava(h)], "aspects": [AB[p] for p in aspects], "sav": av["sav"][sign]})
        houses.append([_nth(h), role, SIGNS[sign], BODIES[lord], _nth(n.bhava(lord)), strength(lord), "%.2f" % sb["bhavas"][h - 1]["rupas"], _names(in_bhava(h)),
                       _names(aspects), av["sav"][sign]])
    lords_text = " (lords %.0f%% against %.0f%%)" % (ld["lifeLords"], ld["deathLords"]) if ld["lifeLords"] is not None and ld["deathLords"] is not None else ""
    verdict = "The stronger lord, %s, is in the %s bhava, a %s: %s. Bhavas of life %.2f rupas against bhavas of death %.2f%s: %s." % (
        BODIES[pl["stronger"]], _nth(pl["house"]), pl["kind"].lower(), pl["class"], ld["life"], ld["death"], lords_text, ld["outcome"].lower())
    bala = lambda p: n.percent[p] if 1 <= p <= 7 else None  # noqa: E731
    data = {"placement": {"lagnaLord": AB[pl["lagna_lord"]], "eighthLord": AB[pl["eighth_lord"]], "lagnaBala": bala(pl["lagna_lord"]), "eighthBala": bala(pl["eighth_lord"]),
                          "lagnaIn": n.bhava(pl["lagna_lord"]), "eighthIn": n.bhava(pl["eighth_lord"]),
                          "stronger": AB[pl["stronger"]], "house": pl["house"], "kind": pl["kind"], "class": pl["class"]},
            "sun": {"lord": AB[sr["lord"]], "relation": sr["relation"], "class": sr["class"]}, "houses": rows, **ld}
    return _section("eighth", "8th Bhava", "BPHS 43.71-73, 44.2-5", verdict,
                    [_named("The lagna lord against the 8th lord (43.71-72)", ["Lord", "Graha", "Bala", "Sign", "Bhava"], placed),
                     _named("The lagna lord against the Sun (43.72-73)", ["Lord", "Relation", "Gives"], relation),
                     _named("Bhavas of life and death", ["Bhava", "Stands for", "Sign", "Lord", "Lord in", "Lord's bala", "Bhava Bala", "Occupants", "Aspected by", "SAV"], houses)],
                    ["In a kendra, panaphara or apoklima bhava the stronger lord gives long, medium or short life; bhavas are of the chosen house system.",
                     "For good longevity the 3rd and 8th and their lords should be strong, the 2nd and 7th and their lords weak (help)."], data=data)


def _date(d):
    return d.date().isoformat()


def _age(p):
    return "%.1f to %.1f" % (max(p["t"], 0.0), p["t"] + p["years"])


def _trines(sign):
    return [(sign + k) % 12 for k in (0, 4, 8)]


def _occupied_or_aspected(n, sign, group):
    return any(SS.rasi_drishti(n.s[p], sign) for p in group)


def _period_table(title, periods, marks, windows=True, wanted=None, first=False):
    """The dasa's periods with what marks each; a period of the life class's ages that carries a mark and no protection is a candidate
    (``first``: only the first such period, Varnada's limit). Also the periods as values, for the Starlight view."""
    rows, found, details, items = [], [], [], []
    for i, p in enumerate(periods):
        m = marks(p["lord"])
        window = AGE_ROWS[min(i // 4, 2)]
        guard = m.pop("guard", False)
        mark_names = list(m)
        candidate = bool(m) and not guard and (not windows or window == wanted) and not (first and found)
        if candidate:
            found.append("%s (age %s)" % (SIGNS[p["lord"]], _age(p)))
            details.append({"sign": SIGNS[p["lord"]], "sign_i": p["lord"], "age": _age(p), "from": _date(p["start"]),
                            "to": _date(p["end"]), "marks": mark_names, "period": p, "index": i})
        rows.append([SIGNS[p["lord"]], _date(p["start"]), _date(p["end"]), _age(p)] + ([window.split()[0]] if windows else []) + [", ".join(mark_names + ["Protected"] * guard) or "-", _yes(candidate)])
        items.append({"sign": SHORT_SIGNS[p["lord"]], "from": _date(p["start"]), "to": _date(p["end"]), "age": [max(p["t"], 0.0), p["t"] + p["years"]],
                      "inWindow": windows and window == wanted, "marks": mark_names, "guarded": guard, "candidate": candidate,
                      "ads": [_ad_item(ad) for ad in p.get("antardasas", []) if ad["years"] > 0]})
    return _named(title, ["Rasi", "From", "To", "Age"] + (["Class of these ages"] if windows else []) + ["Marks", "Candidate"], rows), found, details, items


def _ad_item(ad, from_dasa=None, aspects=False, preferred=False):
    return {"sign": SHORT_SIGNS[ad["lord"]], "from": _date(ad["start"]), "to": _date(ad["end"]), "age": [max(ad["t"], 0.0), ad["t"] + ad["years"]],
            "fromDasa": from_dasa, "aspects": aspects, "preferred": preferred}


def _niryana_antardasas(n, md, opt):
    """Niryana Shoola timing (PVR ch. 22): AD of 6/7/8/12 from MD, or AD of a rasi that aspects the navamsa of the 8th-lord-from-MD; intersection preferred."""
    md_sign = md["lord"]
    eighth_sign = (md_sign + 7) % 12
    eighth_lord = SS.sign_lord(eighth_sign, n.s, list(n.lons))
    d9_sign = V.varga_sign(n.lons[eighth_lord], 9, opt)
    rows, preferred, items = [], [], []
    for ad in md.get("antardasas", []):
        ad_sign = ad["lord"]
        from_md = (ad_sign - md_sign) % 12 + 1 in (6, 7, 8, 12)
        aspects = SS.rasi_drishti(ad_sign, d9_sign)
        if not (from_md or aspects):
            items.append(_ad_item(ad))
            continue
        reasons = []
        if from_md:
            reasons.append("%s from dasa" % _nth((ad_sign - md_sign) % 12 + 1))
        if aspects:
            reasons.append("Aspects D-9 of 8th lord from dasa (%s in %s)" % (BODIES[eighth_lord], SIGNS[d9_sign]))
        hit = from_md and aspects
        row = [SIGNS[md_sign], SIGNS[ad_sign], _date(ad["start"]), _date(ad["end"]), _age(ad), ", ".join(reasons), _yes(hit)]
        rows.append(row)
        items.append(_ad_item(ad, (ad_sign - md_sign) % 12 + 1 if from_md else None, aspects, hit))
        if hit:
            preferred.append("%s / %s (age %s)" % (SIGNS[md_sign], SIGNS[ad_sign], _age(ad)))
    return rows, preferred, items


def rudra_section(n, jc, s, r, why, dasa):
    brahma, rudra, mahes = K.brahma_rudra_maheswara(jc)
    second, eighth = n.lord(2), n.lord(8)
    aprani = second if rudra == eighth else eighth
    tri = _trines(n.s[rudra])
    arudha = SS.bhava_arudhas(n.s, list(n.lons), s.arudha_exceptions_bhava, s.arudha_nodes)[0]
    al_trines = _trines(arudha)
    ak = jc.atmakaraka()
    guards = [p for p in dict.fromkeys((ak, 5)) if p != rudra]       # the help: AK or Jupiter protects a rasi, unless it is Rudra
    wanted = {A.VERY_SHORT: A.SHORT, A.EXTREME: A.LONG}.get(r["class"], r["class"])
    primary = [n.lord(2), n.lord(7)]
    hitters = list(dict.fromkeys(n.malefics + list(why)))
    opt = S.varga_options(s)

    def niryana(sign):
        m = {"guard": _occupied_or_aspected(n, sign, guards)}
        if sign in tri:
            m["Trishoola"] = True
        if sign in (n.house_sign(2), n.house_sign(7)):
            m["Maraka rasi"] = True
        if any(n.s[p] == sign for p in primary):
            m["Holds a maraka lord"] = True
        if any(n.s[p] == sign for p in why):
            m["Holds a maraka graha"] = True
        if n.house(rudra) == 12 and n.s[rudra] == sign:
            m["Rudra in the 12th"] = True
        return m

    def shoola(sign):
        m = {"guard": _occupied_or_aspected(n, sign, guards)}
        if sign in tri:
            m["Trishoola"] = True
        if sign in al_trines:
            m["AL or its trine"] = True
        for k, name in ((2, "3rd from AL"), (7, "8th from AL")):
            if sign == (arudha + k) % 12 and _occupied_or_aspected(n, sign, hitters):
                m["%s with a malefic or maraka on it" % name] = True
        return m

    def varnada(sign):
        return {"Kona of the Varnada, a malefic on it": True} if sign in _trines(jc.varnada_sign) and _occupied_or_aspected(n, sign, n.malefics) else {}

    ns_periods = dasa("niryana_shoola_dasa")[2]
    ns, ns_found, ns_details, ns_items = _period_table("Niryana Shoola dasa: the motion of prana", ns_periods, niryana, wanted=wanted)
    sh, sh_found, _, sh_items = _period_table("Shoola dasa: the motion of Shiva", dasa("shoola_dasa")[2], shoola, wanted=wanted)
    vd, _, _, vd_items = _period_table("Varnada dasa (5.16-20)", [p for p in dasa("varnada_dasa")[2] if p["years"] > 0 and p["t"] < 120.0], varnada, windows=False, first=True)

    ad_rows, preferred_ads, niryana_headline = [], [], []
    for d in ns_details:
        rows, pref, ns_items[d["index"]]["ads"] = _niryana_antardasas(n, d["period"], opt)
        ad_rows += rows
        preferred_ads += pref
        niryana_headline.append({"sign": d["sign"], "age": d["age"], "from": d["from"], "to": d["to"], "marks": d["marks"],
                                 "preferredAds": pref})
    ad_table = _named("Niryana Shoola antardasas of the candidate mahadasas (help)",
                      ["Maha", "Antar", "From", "To", "Age", "Why", "Preferred"], ad_rows)

    who = [["Prani Rudra", BODIES[rudra], SIGNS[n.s[rudra]], _nth(n.house(rudra)), "The stronger of the lords of the 2nd and 8th"],
           ["Aprani Rudra", BODIES[aprani], SIGNS[n.s[aprani]], _nth(n.house(aprani)), "The weaker of them"],
           ["Maheshwara", BODIES[mahes], SIGNS[n.s[mahes]], _nth(n.house(mahes)), "From the 8th from the atmakaraka: the Key Info rule"],
           ["Brahma", BODIES[brahma], SIGNS[n.s[brahma]], _nth(n.house(brahma)), "Starts the Brahma and Sthira dasas"],
           ["Atmakaraka", BODIES[ak], SIGNS[n.s[ak]], _nth(n.house(ak)), "Protects a rasi it occupies or aspects"],
           ["Arudha Lagna", "-", SIGNS[arudha], _nth((arudha - n.s[0]) % 12 + 1), "Its trines and 3rd and 8th matter in Shoola dasa"]]
    moon_on = [SIGNS[x] for x in (1, 7) if SS.rasi_drishti(n.s[2], x)]
    tris = [[SIGNS[x], _nth((x - n.s[rudra]) % 12 + 1), _names([p for p in range(1, 10) if n.s[p] == x])] for x in tri]
    ad_note = ("; preferred antardasas: %s" % "; ".join(preferred_ads)) if preferred_ads else ""
    verdict = "Rudra is %s in %s. Trishoola rasis: %s. For %s, Niryana Shoola points to %s%s." % (
        BODIES[rudra], SIGNS[n.s[rudra]], ", ".join(SIGNS[x] for x in tri), r["class"], "; ".join(ns_found) or "none of its periods", ad_note)
    place = lambda name, p: {"name": name, "graha": AB[p], "sign": SHORT_SIGNS[n.s[p]], "house": n.house(p)}  # noqa: E731
    data = {"who": [place("Rudra", rudra), place("Aprani Rudra", aprani), place("Maheshwara", mahes), place("AK", ak),
                    {"name": "AL", "graha": None, "sign": SHORT_SIGNS[arudha], "house": (arudha - n.s[0]) % 12 + 1}],
            "trishoola": [SHORT_SIGNS[x] for x in tri], "class": r["class"], "rudraYoga": [SHORT_SIGNS[x] for x in (1, 7) if SS.rasi_drishti(n.s[2], x)],
            "dasas": [{"id": "niryana", "name": "Niryana Shoola", "periods": ns_items}, {"id": "shoola", "name": "Shoola", "periods": sh_items},
                      {"id": "varnada", "name": "Varnada", "periods": vd_items}]}
    tables = [_named("Rudra and the other deities", ["Name", "Graha", "Sign", "Bhava", "How it is found"], who),
              _named("Trishoola rasis: the trines from Rudra", ["Rasi", "From Rudra", "Occupants"], tris), ns, ad_table, sh, vd]
    return _section("rudra", "Rudra Trishoola", "JUS 2.2-2.3; PVR ch. 23; BPHS 5.16-20", verdict, tables,
                    ["Niryana Shoola is the primary death timer: praana hitting Trishoola or a maraka rasi. Prefer antardasas that are the 6th, 7th, 8th or 12th from the dasa rasi, or that aspect the navamsa of the 8th lord from the dasa; a rasi common to both is strongest.",
                     "Shoola dasa is secondary: Shiva's force hitting AL trines or the 3rd/8th from AL.",
                     "A rasi occupied or aspected by the atmakaraka or Jupiter usually does not kill, unless that graha is Rudra. Rudra yoga (Moon's rasi aspect on Taurus or Scorpio): %s." % (", ".join(moon_on) or "absent"),
                     "The last 4 periods of a dasa stand for long life, the middle 4 for medium and the first 4 for short."],
                    primary=True, data=data), ns_found, niryana_headline, preferred_ads


def _chip(reason):
    """A maraka's reason as a short label and its verse: "Malefic with the 2nd lord (44.3)" → ("with 2nd lord", "44.3")."""
    text, verse = reason[:-1].rsplit(" (", 1)
    text = re.sub(r"Lord of the (\w+)", r"\1 lord", text)
    for a, b in (("Malefic in the ", "in "), ("Malefic with the ", "with "), ("Malefic aspecting the ", "aspects "), ("Benefic with the ", "with "), ("Node in the ", "in "),
                 ("Node with", "with"), ("Exclusive malefic", "owns only bad houses"), ("Saturn related to a maraka", "tied to a maraka"), ("Rahu for Scorpio or Capricorn lagna", "Sc or Cp lagna")):
        text = text.replace(a, b)
    return {"label": text, "verse": verse}


def maraka_section(n, jc, r, why, dasa):
    mds = dasa("vimsottari_dasa")[2]
    lo, hi = WINDOWS[r["class"]]
    rows, periods = [], []
    prime_set = {p for p in why if A.prime(why[p])}
    for md in mds:
        if md["lord"] in why:
            for ad in md.get("antardasas", []):
                if ad["lord"] in why and ad["t"] + ad["years"] > lo and ad["t"] < hi:
                    rows.append(["%s / %s" % (BODIES[md["lord"]], BODIES[ad["lord"]]), _date(ad["start"]), _date(ad["end"]), _age(ad)])
                    periods.append({"md": AB[md["lord"]], "ad": AB[ad["lord"]], "from": _date(ad["start"]), "to": _date(ad["end"]),
                                    "age": [max(ad["t"], 0.0), ad["t"] + ad["years"]], "prime": md["lord"] in prime_set and ad["lord"] in prime_set})
    planets = [[BODIES[p], "; ".join(why[p])] for p in sorted(why)]
    prime = prime_set
    stars = _tables()[0]["nakshatras"]
    moon = n.lons[2] + jc.correction
    star_rows = [[x["name"], x["count"], stars[x["star"]], x["lord"], x["for"]] for x in A.maraka_stars(moon)]
    malicious = K.malicious_divisions(n.lons[0], n.lons[2])
    cancer = [["Lords of the 2nd and 12th from Cancer", "Sun, Mercury", "Death with a malefic Moon, disease with a benefic one: the Moon is %s here" % ("benefic" if n.benefic(2) else "malefic")]]
    death = A.death_circumstances(n)
    death_rows = [["Manner"] + [m] for m in death["manners"]] + [
        ["Place (3rd's mode)", death["place"]], ["Place quality (3rd)", death["shrine_3rd"]],
        ["Shrine reading (8th)", death["shrine_8th"]], ["Consciousness", death["consciousness"]]]
    verdict = "Marakas: %s. In the ages of %s (%d to %d) %d Vimsottari periods have marakas for both lords." % (_names(sorted(why)), r["class"], lo, hi, len(rows))
    wanted = {A.VERY_SHORT: A.SHORT, A.EXTREME: A.LONG}.get(r["class"], r["class"])
    data = {"grahas": [{"graha": AB[p], "prime": p in prime, "reasons": [_chip(x) for x in why[p]]} for p in sorted(why, key=lambda p: (p not in prime, p))],
            "class": r["class"], "window": [lo, hi], "periods": sorted(periods, key=lambda x: not x["prime"]),
            "stars": [{"name": x["name"], "count": x["count"], "nakshatra": stars[x["star"]], "lord": AB[PLANETS.index(x["lord"]) + 1], "current": x["for"] == wanted}
                      for x in A.maraka_stars(moon)],
            "readings": [["Manner", "; ".join(death["manners"])], ["Place", death["place"]], ["Place quality", death["shrine_3rd"]], ["Shrine", death["shrine_8th"]],
                         ["Consciousness", death["consciousness"]], ["2nd and 12th from Cn", "Su, Me: %s" % ("disease, the Moon being benefic" if n.benefic(2) else "death, the Moon being malefic")]],
            # the Parasara rows of K.malicious_divisions: from the lagna, then from the Moon
            "divisions": [["64th navamsa", malicious[0][1]], ["22nd drekkana", malicious[1][1]], ["64th navamsa from Mo", malicious[5][1]], ["22nd drekkana from Mo", malicious[6][1]]]}
    return _section("marakas", "Marakas", "BPHS 44", verdict,
                    [_named("Maraka grahas", ["Graha", "Why"], planets),
                     _named("Manner and place of death (44.25-39)", ["Topic", "Reading"], death_rows),
                     _named("Stars from the birth star (44.15-21)", ["Star", "Count", "Nakshatra", "Lord", "Class of life"], star_rows),
                     _named("Other lords (44.15-21)", ["Rule", "Graha", "Effect"], cancer),
                     _named("The 22nd drekkana and 64th navamsa", ["Division", "Lord"], malicious),
                     _named("Vimsottari periods with marakas for both lords, in the ages of the life class", ["Period", "From", "To", "Age"], rows)],
                    ["The 2nd is the stronger maraka bhava. In a chart with many marakas they cause disease and trouble, not only death (44.15-21).",
                     "Rahu and Ketu become marakas in the 1st, 7th, 8th or 12th, with or 7th from a maraka lord, or for Scorpio/Capricorn lagna (44.22-24).",
                     "Manner and place readings are classical significations for study, not medical or forensic claims."],
                    primary=True, data=data)


def ashtakavarga_section(n, av):
    total = A.ashtakavarga_years(av["bav"])
    rows = [[name] + list(row) + [_y(y)] for name, row, y in zip(["Lagna"] + SEVEN, av["bav"], total["rows"])]
    sat = A.saturn_ashtakavarga(av["bav"][7], av["pindas"][7][0], n.s[0], n.s[7])
    stars = _tables()[0]["nakshatras"]
    distress = [["Rekhas from the lagna to Saturn", sat["lagna_to_saturn"]], ["Rekhas from Saturn to the lagna", sat["saturn_to_lagna"]], ["Their total, with an Arishta dasa running", sat["total"]]]
    pinda = [["Yoga pinda of Saturn", av["pindas"][7][0]], ["Rekhas in the 8th from Saturn", sat["rekhas"]], ["Their product", sat["product"]],
             ["Saturn's transit of these nakshatras", ", ".join(stars[x] for x in sat["stars"]) or "-"], ["Saturn's transit of these rasis", ", ".join(SIGNS[x] for x in sat["signs"]) or "-"]]
    verdict = "%s years, %s" % (_y(total["years"]), A.class_of_years(total["years"]))
    data = {"rows": [{"name": AB[i], "rekhas": list(row), "years": y} for i, (row, y) in enumerate(zip(av["bav"], total["rows"]))], "years": total["years"],
            "class": A.class_of_years(total["years"]), "distress": [sat["lagna_to_saturn"], sat["saturn_to_lagna"], sat["total"]],
            "saturn": {"pinda": av["pindas"][7][0], "rekhas": sat["rekhas"], "product": sat["product"], "stars": [stars[x] for x in sat["stars"]], "signs": [SHORT_SIGNS[x] for x in sat["signs"]]}}
    return _section("ashtakavarga", "Ashtakavarga", "BPHS 71.1-4, 70.37-42", verdict,
                    [_named("Rekhas in each ashtakavarga, and their years (71.1-4)", ["Ashtakavarga"] + SHORT_SIGNS + ["Years"], rows + [["Half of the sum", *[""] * 12, _y(total["years"])]]),
                     _named("Ages of distress (70.37-40)", ["Count", "Age"], distress), _named("Saturn's transits (70.41-42)", ["Step", "Result"], pinda)],
                    ["0 rekhas give 2 days, 1 gives 1.5, 2 gives 1, 3 gives half a day, 4 gives 7.5 days; 5 give 2 years, 6 give 4, 7 give 6, 8 give 8. A year here has 360 days."], data=data), total


def _rule_rows(found):
    return [[x["verse"], x["condition"], x["gives"], _yes(x["present"])] for x in sorted(found, key=lambda x: not x["present"])]


def yogas_section(n):
    long_, short, arishta, antidote = [A.rules(n, t) for t in (A.LONG_LIFE, A.SHORT_LIFE, A.BALARISHTA, A.ANTIDOTES)]
    count = lambda rows: sum(x["present"] for x in rows)  # noqa: E731
    columns = ["Verse", "Condition", "Gives", "Present"]
    verdict = "Present: %d long-life yogas, %d short-life yogas, %d Balarishtas, %d antidotes." % (count(long_), count(short), count(arishta), count(antidote))
    data = {"groups": [{"id": i, "name": name, "rules": rows} for i, name, rows in
                       (("long", "Long life", long_), ("short", "Short and medium life", short), ("arishta", "Balarishta", arishta), ("antidotes", "Antidotes", antidote))]}
    return _section("yogas", "Yogas and Arishta", "BPHS 43.55-78, 9.3-23, 10.2-8", verdict,
                    [_named("Yogas of long life (43.55-70)", columns, _rule_rows(long_)), _named("Yogas of short and medium life (43.74-78)", columns, _rule_rows(short)),
                     _named("Balarishta: evils at birth (9.3-23)", columns, _rule_rows(arishta)), _named("Antidotes (10.2-8)", columns, _rule_rows(antidote))],
                    ["Evils at birth run up to the 24th year, so no definite span should be fixed before it (9.2). Aspects are graha drishti%s. Strong means Shadbala at or above the rupas required." % ("; yuti and drishti within the smaller of the two deeptamsas, drishti on a bhava within the graha's deeptamsa of its cusp (Settings: Longevity)" if n.orbs else ""),
                     "All the malefics means the Sun, Mars, Saturn and a malefic Moon or Mercury; the nodes cannot both sit in such bhavas."], data=data), (count(long_), count(short), count(arishta), count(antidote))


def sections(b, ch, cfg, s, dasa):
    """``dasa(key)``: what service._dasa_any gives for a natal dasa of this chart.

    Section order follows the primary reading path: Summary, Three Pairs, Marakas, Rudra/Niryana,
    then corroborating spans, 8th house, Ashtakavarga, yogas.
    """
    n, sb = natal_of(b, ch, cfg, s)
    jc = dasa("vimsottari_dasa")[0]
    r = A.three_pairs(n)
    sp = A.spans(n)
    why = A.marakas(n)
    pl, sr = A.placement(n), A.sun_relation(n)
    av = ashtakavarga_view(ch, s)
    av_sec, av_total = ashtakavarga_section(n, av)
    rudra_sec, candidates, niryana_detail, preferred_ads = rudra_section(n, jc, s, r, why, dasa)
    yoga_sec, (long_n, short_n, arishta_n, antidote_n) = yogas_section(n)
    ld = life_and_death(n, sb)
    life, death = ld["life"], ld["death"]

    # Primary rows first, then corroboration
    primary_rows = [
        ["Three pairs: Lagna lord + 8th lord, Saturn + Moon, Lagna + Hora Lagna", "BPHS 43.33-50", r["class"],
         _span(r) + (" (rectified %s)" % _y(r["rectified"]) if r["years"] else ""), "primary"],
        ["Marakas: %s" % _names(sorted(why)), "BPHS 44", "%d killers" % len(why), "-", "primary"],
        ["Niryana Shoola: Trishoola or maraka rasi in the ages of the class", "PVR ch. 22",
         "; ".join(candidates) or "None",
         ("; ".join(preferred_ads[:3]) + ("…" if len(preferred_ads) > 3 else "")) or "-", "primary"],
    ]
    secondary_rows = [
        ["The span chosen by the strongest of Lagna, Sun and Moon against their minimums: %s" % " and ".join(SPAN_NAMES[k] for k in sp["chosen"]),
         "BPHS 43.30-32", A.class_of_years(sp["years"]), _y(sp["years"]), "secondary"],
    ]
    secondary_rows += [[SPAN_NAMES[k], src, A.class_of_years(sp[k]["total"]), _y(sp[k]["total"]), "secondary"]
                       for k, src in (("pinda", "BPHS 43.4-15"), ("amsa", "BPHS 43.18-22"), ("nisarga", "BPHS 43.16-17"))]
    secondary_rows += [
        ["The stronger of the lagna and 8th lords, %s in the %s" % (BODIES[pl["stronger"]], _nth(pl["house"])),
         "BPHS 43.71-72", pl["class"], "-", "secondary"],
        ["The lagna lord %s and the Sun: %s" % (BODIES[sr["lord"]], sr["relation"].lower()),
         "BPHS 43.72-73", sr["class"] or "-", "-", "secondary"],
        ["Bhavas of life (3+8) vs death (2+7)", "BPHS 44.2-5; help",
         "%s: life %.2f / death %.2f rupas" % (ld["outcome"], life, death), "-", "secondary"],
        ["Ashtakavarga rekhas", "BPHS 71.1-4", A.class_of_years(av_total["years"]), _y(av_total["years"]), "secondary"],
        ["Yogas of long life", "BPHS 43.55-70", "%d present" % long_n, "-", "secondary"],
        ["Yogas of short and medium life", "BPHS 43.74-78", "%d present" % short_n, "-", "secondary"],
        ["Balarishta, with its antidotes", "BPHS 9, 10", "%d present; antidotes present: %d" % (arishta_n, antidote_n), "-", "secondary"],
    ]
    # (name, class, years or None, the sub tab that works it); the three spans are one method, the chosen one's years
    methods = [
        ("Three pairs", r["class"], r[s.longevity_pairs_figure], "pairs"),
        ("Pindayu", A.class_of_years(sp["pinda"]["total"]), sp["pinda"]["total"], "spans"),
        ("Amsayu", A.class_of_years(sp["amsa"]["total"]), sp["amsa"]["total"], "spans"),
        ("Nisargayu", A.class_of_years(sp["nisarga"]["total"]), sp["nisarga"]["total"], "spans"),
        ("Ashtakavarga", A.class_of_years(av_total["years"]), av_total["years"], "ashtakavarga"),
        ("Lagna/8th lord", pl["class"], None, "eighth"),        # the rules that give only a class come last
    ]
    if sr["class"]:
        methods.append(("Lagna lord vs Sun", sr["class"], None, "eighth"))
    class_methods = [(name, c) for name, c, _, tab in methods if tab != "spans"]
    class_methods.insert(1, ("Chosen span", A.class_of_years(sp["years"])))
    agree = [name for name, c in class_methods if c == r["class"]]

    headline = {
        "class": r["class"],
        "pairYears": r["years"],
        "pairSpan": _span(r),
        "rectified": r["rectified"],
        "marakas": [{"planet": BODIES[p], "why": why[p]} for p in sorted(why)],
        "niryana": niryana_detail,
        "preferredAds": preferred_ads,
        "span": {
            "chosen": [SPAN_NAMES[k] for k in sp["chosen"]],
            "years": sp["years"],
            "class": A.class_of_years(sp["years"]),
            "judges": [{"judge": JUDGES[k], "rupas": round(sp["strength"][k] / 60.0, 2), "percent": round(sp["percent"][k], 1),
                        "span": SPAN_NAMES[k], "years": sp[k]["total"], "chosen": k in sp["chosen"]}
                       for k in ("amsa", "pinda", "nisarga")],
        },
        "lifeDeath": {"life": life, "death": death},
        "corroboration": {"agree": agree, "total": len(class_methods), "methods": [{"name": a, "class": b} for a, b in class_methods]},
        "yogas": {"long": long_n, "short": short_n, "balarishta": arishta_n, "antidotes": antidote_n},
        "methods": [{"name": name, "class": c, "years": y, "tab": tab, "agrees": c == r["class"],
                     "chosen": name in [SPAN_NAMES[k] for k in sp["chosen"]]} for name, c, y, tab in methods],
        "primeMarakas": [AB[p] for p in sorted(why) if A.prime(why[p])],
    }
    verdict = "%s · %s years from the pairs%s. Marakas: %s. Niryana: %s." % (
        r["class"], _span(r),
        (" (rectified %s)" % _y(r["rectified"])) if r["years"] else "",
        _names(sorted(why)) or "none",
        "; ".join(candidates) or "no candidate in class window")
    summary = _section(
        "summary", "Summary", "BPHS primary path + corroboration", verdict,
        [_named("Primary methods", ["Method", "Source", "Result", "Years", "Weight"], primary_rows),
         _named("Corroborating methods", ["Method", "Source", "Result", "Years", "Weight"], secondary_rows)],
        ["Read class from the three pairs, killers from the marakas, and timing from Niryana Shoola (help). "
         "Pinda/Amsa/Nisarga and the other rows corroborate; the texts need not agree.",
         "Short life is before 32, medium to 64, long to 100, and beyond that supreme (44.10-14). "
         "Longevity cannot be fixed before age 20 (44.10-14)."],
        headline=headline, primary=True)
    marakas_sec = maraka_section(n, jc, r, why, dasa)
    headline["periods"] = [p for p in marakas_sec["data"]["periods"] if p["prime"]]
    return [summary, pairs_section(n, r), marakas_sec, rudra_sec,
            spans_section(n, sp), eighth_section(n, sb, av), av_sec, yoga_sec]
