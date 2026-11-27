"""What the books say: each nakshatra (data/lore/nakshatras.json, from Dr. Pai's Cosmic Insights, with nakshatra_readings.json's fuller
introduction and its Lagna, Moon and Sun readings), each graha, rashi and bhava (grahas.json, rashis.json, bhavas.json, from the
classics, with the BPHS slokas in bphs_quotes.json), what each of the four signifies, living (jiva) and non-living (ajiva)
(jiva_ajiva.json, nakshatra_significations.json), the lord of each bhava in each bhava (data/lore/bhava_lords.json, BPHS Ch. 24)
and each graha's transit from the natal Moon (data/lore/gochara.json, Phaladeepika Ch. 26), with every pairing of rashi, nakshatra
and graha with the bhavas, rashis and nakshatras (rashi_bhava.json and the rest; data/lore/README.md maps them). bhava_reading puts
the pairings together for one bhava of a chart. Starlight's lore panel and the Transits Domain table's info pop-up read them."""
import functools
import json
import os

from core_logic import natal_chart as N, shadbala as SB

from .houses import ORDINAL

DIR = os.path.join(os.path.dirname(__file__), "..", "data", "lore")
NAK = 360.0 / 27.0
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORD = ["Ma", "Ve", "Me", "Mo", "Su", "Me", "Ve", "Ma", "Ju", "Sa", "Sa", "Ju"]
AIM = ["Dharma", "Artha", "Kama", "Moksha"]          # a navamsa's purushartha by its sign's element: fire, earth, air, water
EXALT = {"Su": 10.0, "Mo": 33.0, "Ma": 298.0, "Me": 165.0, "Ju": 95.0, "Ve": 357.0, "Sa": 200.0}
NAMES = {"Su": "Sun", "Mo": "Moon", "Ma": "Mars", "Me": "Mercury", "Ju": "Jupiter", "Ve": "Venus", "Sa": "Saturn", "Ra": "Rahu", "Ke": "Ketu"}


@functools.cache
def _load(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as f:
        return json.load(f)


def nakshatra(n: int) -> dict:
    """Nakshatra n (1 Ashwini .. 27 Revati) as the book gives it, with its four padas worked out: each one's navamsa sign and lord,
    purushartha, and whether it is vargottama or a pushkara navamsa (as the Grahas tab marks a graha's)."""
    rec = dict(_load("nakshatras.json")["nakshatras"][n - 1])
    padas = []
    for k in range(4):
        mid = (n - 1) * NAK + (k + 0.5) * NAK / 4
        nav = ((n - 1) * 4 + k) % 12
        padas.append({"pada": k + 1, "sign": SIGNS[nav], "lord": SIGN_LORD[nav], "aim": AIM[nav % 4],
                      "vargottama": nav == int(mid // 30), "pushkara": bool(N.pushkara_position(mid, False)[0])})
    rec["pada_facts"] = padas
    # what it is, in a few sentences, and how it reads as the Lagna's, the Moon's and the Sun's nakshatra (data/lore/nakshatra_readings.json)
    rd = _load("nakshatra_readings.json")
    rec["reading"] = {k: v for k, v in rd["readings"][n - 1].items() if k != "n"} | {"source": rd["source"]}
    # the deepest exaltation and debilitation points that fall in it (Su 10° Aries … Sa 20° Libra), with their pada
    rec["dignities"] = [{"graha": g, "kind": kind, "pada": int((x % NAK) // (NAK / 4)) + 1}
                        for g, lon in EXALT.items() for kind, x in (("exalted", lon), ("debilitated", (lon + 180.0) % 360.0)) if int(x // NAK) + 1 == n]
    if n in (21, 22):
        rec["abhijit"] = _load("nakshatras.json")["abhijit"]
    # its living and non-living significations (nakshatra_significations.json), with the book's body part, yoni and tree, careers and places
    own = _load("nakshatra_significations.json")["nakshatras"][n - 1]
    yoni = rec["yoni"] if "(" in rec["yoni"] else rec["yoni"].rstrip(")")          # "Female Horse)": a bracket left by the book's table
    more = {"body": [rec["body"]], "creatures": [f"{yoni} (its yoni)", f"{rec['tree']['names'].split(',')[0].strip()} (its tree)"],
            "work": rec["careers"]["items"], "places": rec["places"]["items"]}
    rec["significations"] = significations({side: {k: v + more.get(k, []) for k, v in own[side].items()} for side in ("jiva", "ajiva")})
    nb, gn = _table("nakshatra_bhava.json"), _table("graha_nakshatra.json")
    rec["on_bhava"] = nb["readings"][n - 1]["houses"] if nb else []             # this nakshatra on each bhava's cusp, jiva and ajiva
    rec["grahas_in"] = [{"graha": g, "text": gn["readings"][g][n - 1]} for g in GRAHAS] if gn else []
    return rec


# --- grahas, rashis and bhavas: what each one is and signifies (data/lore/grahas.json, rashis.json, bhavas.json), with the BPHS slokas
# that describe it (bphs_quotes.json)

GRAHAS = ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"]
NAK_LORDS = ["Ke", "Ve", "Su", "Mo", "Ma", "Ra", "Ju", "Sa", "Me"]       # Ashwini's lord, Ketu, and on round the Vimshottari order
OWN = {"Su": [5], "Mo": [4], "Ma": [1, 8], "Me": [3, 6], "Ju": [9, 12], "Ve": [2, 7], "Sa": [10, 11], "Ra": [11], "Ke": [8]}   # the nodes as co-lords
# moolatrikona from .. to (BPHS 3.51-54, the nodes' signs 47.34-39), and the nodes' exaltations (47.34-39; the app's default, nodal_parasara)
MOOLA = {"Su": (120.0, 140.0), "Mo": (33.0, 60.0), "Ma": (0.0, 12.0), "Me": (165.0, 170.0), "Ju": (240.0, 250.0), "Ve": (180.0, 195.0),
         "Sa": (300.0, 320.0), "Ra": (60.0, 90.0), "Ke": (240.0, 270.0)}
NODE_EXALT = {"Ra": 2, "Ke": 8}


def significations(sides: dict) -> list:
    """{"jiva": {"people": [...], ...}, "ajiva": {...}} as the pop-ups show them: each side and each part named (jiva_ajiva.json),
    empty parts left out, an item given twice once."""
    out = []
    for g in _load("jiva_ajiva.json")["groups"]:
        parts = []
        for p in g["parts"]:
            items = list(dict.fromkeys(x.strip() for x in sides.get(g["id"], {}).get(p["id"], []) if x and x.strip()))
            if items:
                parts.append({"id": p["id"], "name": p["name"], "items": items})
        out.append({"id": g["id"], "name": g["name"], "gloss": g["gloss"], "parts": parts})
    return out


def _relations(ab: str) -> dict:
    """Its natural friends, neutrals and enemies as the app counts them (the app's table, the nodes too; BPHS 3.55 for the seven)."""
    row = SB.NATURAL_RELATIONS_9[GRAHAS.index(ab)]
    pick = lambda code: [GRAHAS[i] for i, c in enumerate(row) if c == code]  # noqa: E731
    return {"friends": pick(2), "neutral": pick(3), "enemies": pick(4)}


def graha(ab: str) -> dict:
    """Graha ``ab`` (Su .. Ke) as the classics give it, with what it rules (its signs and nakshatras), the bhavas it is a karaka of
    (BPHS 32.34; Phaladeepika 15.17), its friends and enemies, and the BPHS slokas on it."""
    d = _load("grahas.json")
    rec = dict(next(g for g in d["grahas"] if g["id"] == ab))
    rec["significations"] = significations(rec["significations"])
    rec["relations"] = _relations(ab)
    rec["rules"] = {"signs": OWN[ab], "nakshatras": [n for n in range(1, 28) if NAK_LORDS[(n - 1) % 9] == ab]}
    bh = _load("bhavas.json")["bhavas"]
    rec["karaka_of"] = {k: [b["n"] for b in bh if ab in b["karakas"][k]] for k in ("bphs", "phaladeepika")}
    q = _load("bphs_quotes.json")
    rec["classics"], rec["classics_all"] = q["grahas"][ab], q["grahas_all"]
    rec["aspects_note"], rec["source"] = d["aspects_note"], d["source"]
    # its rows of the combination tables: in each bhava (Phaladeepika 8), its aspect on each, in each rashi and each nakshatra
    gb, ga, gr, gn = (_table(f) for f in ("graha_bhava.json", "graha_aspects.json", "graha_rashi.json", "graha_nakshatra.json"))
    rec["in_bhava"], rec["bhava_note"] = (gb["readings"][ab], gb["note"]) if gb else ([], "")
    rec["aspect_on"], rec["aspect_note"] = (ga["readings"][ab], ga["note"]) if ga else ([], "")
    rec["in_rashi"] = gr["readings"][ab] if gr else []
    rec["in_nakshatra"] = gn["readings"][ab] if gn else []
    return rec


def _dignities(sign: int) -> list:
    """The grahas exalted, debilitated, in moolatrikona or in their own sign in rashi ``sign`` (1-12), with the degrees that matter."""
    out = []
    for g, lon in EXALT.items():
        if int(lon // 30) + 1 == sign:
            out.append({"graha": g, "kind": "exalted", "deg": round(lon % 30)})
        if int(((lon + 180.0) % 360.0) // 30) + 1 == sign:
            out.append({"graha": g, "kind": "debilitated", "deg": round(lon % 30)})
    for g, s in NODE_EXALT.items():
        out += [{"graha": g, "kind": "exalted", "deg": None}] if s == sign else []
        out += [{"graha": g, "kind": "debilitated", "deg": None}] if (s + 5) % 12 + 1 == sign else []
    for g, (a, b) in MOOLA.items():
        if int(a // 30) + 1 == sign:
            out.append({"graha": g, "kind": "moolatrikona", "deg": [round(a % 30), round(b - 30 * (sign - 1))]})
    out += [{"graha": g, "kind": "own", "deg": None} for g in GRAHAS if sign in OWN[g]]
    return out


def rashi(n: int) -> dict:
    """Rashi n (1 Aries .. 12 Pisces) as the classics give it, with the nakshatras and padas in it, the grahas that are exalted,
    debilitated, moolatrikona or own there, and its BPHS sloka."""
    d = _load("rashis.json")
    rec = dict(d["rashis"][n - 1])
    rec["significations"] = significations(rec["significations"])
    names = [x["name"] for x in _load("nakshatras.json")["nakshatras"]]
    stars: dict = {}
    for p in range((n - 1) * 9, n * 9):          # nine padas to a rashi
        stars.setdefault(p // 4 + 1, []).append(p % 4 + 1)
    rec["nakshatras"] = [{"n": k, "name": names[k - 1], "padas": v, "lord": NAK_LORDS[(k - 1) % 9]} for k, v in stars.items()]
    rec["dignities"] = _dignities(n)
    rec["lord"] = SIGN_LORD[n - 1]
    q = _load("bphs_quotes.json")
    rec["classics"], rec["classics_all"], rec["source"] = q["rashis"][str(n)], q["rashis_all"], d["source"]
    rb, gr = _table("rashi_bhava.json"), _table("graha_rashi.json")
    rec["on_bhava"] = rb["readings"][n - 1]["houses"] if rb else []             # this rashi on each bhava's cusp, jiva and ajiva
    rec["grahas_in"] = [{"graha": g, **gr["readings"][g][n - 1]} for g in GRAHAS] if gr else []
    return rec


def bhava(n: int) -> dict:
    """Bhava n (1-12) as the classics give it: its names, kinds, karakas, limb, relations and significations, its BPHS slokas
    (Ch. 11 and its own chapter), and BPHS 24 on its lord in each bhava and on each lord in it."""
    d = _load("bhavas.json")
    rec = dict(d["bhavas"][n - 1])
    rec["significations"] = significations(rec["significations"])
    k = rec["karakas"]
    rec["facts"] = [
        {"name": "What it is", "rows": [
            {"k": "Name", "v": f"{rec['name']} ({rec['gloss']})", "src": "BPHS 11", "tile": True},
            {"k": "Also called", "v": ", ".join(rec["names"]), "src": "Phaladeepika 1.10-16"},
            {"k": "Kind", "v": ", ".join(rec["kinds"]), "src": "BPHS 32.35-37", "tile": True},
            {"k": "Purushartha", "v": rec["purushartha"], "src": "", "tile": True}]},
        {"name": "Who and what", "rows": [
            {"k": "Karaka", "v": ", ".join(NAMES[g] for g in k["bphs"]), "src": "BPHS 32.31-34", "tile": True},
            {"k": "Karakas, by Phaladeepika", "v": ", ".join(NAMES[g] for g in k["phaladeepika"]), "src": "Phaladeepika 15.17"},
            {"k": "Limb of Kalapurusha", "v": rec["limb"], "src": "BPHS 4.4", "tile": True},
            {"k": "Relations", "v": ", ".join(rec["relatives"]), "src": "BPHS 11"}]},
    ]
    q = _load("bphs_quotes.json")
    rec["classics"], rec["judge"], rec["karaka_slokas"] = q["bhavas"][str(n)], q["bhavas_judge"], q["bhavas_karakas"]
    lords = _load("bhava_lords.json")["slokas"]
    src = lambda s: f"BPHS 24.{s['sloka']}"  # noqa: E731
    rec["lords"] = {"from": [{"house": s["house"], "text": s["text"], "source": src(s)} for s in lords if s["lord"] == n],
                    "into": [{"lord": s["lord"], "text": s["text"], "source": src(s)} for s in lords if s["house"] == n]}
    rec["source"] = d["source"]
    # the template: every rashi and every nakshatra on this cusp, every graha in it and aspecting it
    rb, nb, gb, ga = (_table(f) for f in ("rashi_bhava.json", "nakshatra_bhava.json", "graha_bhava.json", "graha_aspects.json"))
    rec["on_cusp"] = {"rashis": [r["houses"][n - 1] for r in rb["readings"]] if rb else [],
                      "nakshatras": [r["houses"][n - 1] for r in nb["readings"]] if nb else []}
    rec["grahas_in"] = [{"graha": g, **gb["readings"][g][n - 1]} for g in GRAHAS] if gb else []
    rec["aspects_on"] = [{"graha": g, "text": ga["readings"][g][n - 1]} for g in GRAHAS] if ga else []
    return rec


def _short(v: str) -> str:
    """"Laghu and Kshipra (The Light and Swift)" -> "Laghu and Kshipra"."""
    return v.split(" (")[0].strip()


def transit_info(ab: str, d: int, domain: str, house: int, moon_house: int, rules: list, karaka: bool, lon: float,
                 moon_good: int, vedha_by: list) -> list:
    """The Domain table's info pop-up for one graha: what its transit through the house means, the classical result from the natal
    Moon, each lordship it carries there (BPHS 24), the karaka role, and the nakshatra it is in. Each part: kind, head, text, notes,
    source; the nakshatra's ``n`` opens its own pop-up."""
    g = _load("gochara.json")
    gr, hs = g["grahas"][ab], g["houses"]
    name = NAMES[ab]
    chart = "Lagna" if d == 1 else f"the D{d} lagna"
    out = []
    text = f"{name} {gr['nature']} the {ORDINAL[house - 1]} house ({hs[house - 1]['name']}): {hs[house - 1]['themes']}."
    if d != 1:
        text += f" In the D{d} these are read for {domain.lower()}."
    out.append({"kind": "house", "head": f"Through the {ORDINAL[house - 1]} from {chart}", "text": text,
                "notes": [f"{name} signifies {gr['signifies']}."], "source": ""})
    verdict = "Favourable" if moon_good > 0 else "Unfavourable" if moon_good < 0 else "Neither good nor bad"
    notes = [f"Obstructed (vedha) by {', '.join(vedha_by)}: its good results are held back while that lasts."] if vedha_by else []
    said = gr["from_moon"][moon_house - 1]
    if d != 1 and ab == "Sa" and ": " in said:       # sade sati, kantaka and ashtama Shani are the rasi's: a varga keeps only the result
        said = said.split(": ", 1)[1].capitalize()
    out.append({"kind": "moon", "head": f"{ORDINAL[moon_house - 1]} from the natal Moon{'' if d == 1 else f' in D{d}'}", "tone": "good" if moon_good > 0 and not vedha_by else "bad" if moon_good < 0 else None,
                "verdict": verdict + (", under vedha" if vedha_by else ""), "text": said, "notes": notes, "source": g["source"]})
    lords = {(s["lord"], s["house"]): s for s in _load("bhava_lords.json")["slokas"]}
    for k in rules:
        s = lords[(k, house)]
        out.append({"kind": "lord", "head": f"{ORDINAL[k - 1]} lord in the {ORDINAL[house - 1]}", "text": s["text"],
                    "notes": [f"The classic gives this for a birth chart. While the {ORDINAL[k - 1]} lord transits the {ORDINAL[house - 1]}, the {ORDINAL[k - 1]} house's matters ({hs[k - 1]['themes']}) are carried into the {ORDINAL[house - 1]}'s."],
                    "source": f"BPHS 24.{s['sloka']}"})
    if karaka:
        out.append({"kind": "karaka", "head": f"Karaka of {domain.lower()}", "text": f"{name} is a natural significator of {domain.lower()}: its transit speaks for the domain as a whole, whatever house it is in.", "notes": [], "source": ""})
    n, pada = int(lon // NAK) + 1, int((lon % NAK) // (NAK / 4)) + 1
    rec = _load("nakshatras.json")["nakshatras"][n - 1]
    facts = [f"ruled by {_short(rec['ruler'])}", f"deity {rec['deity']['name']}" if rec["deity"]["name"] else "",
             f"{_short(rec['quality'])} (quality)" if rec["quality"] else "", _short(rec["shakti"]) if rec["shakti"] else ""]
    notes = list(rec["grahas"].get(ab, []))
    if ab == "Mo":
        notes += ["Good for: " + ", ".join(rec["moon_good"]["items"]) + "."] if rec["moon_good"]["items"] else []
        notes += ["Avoid: " + ", ".join(rec["moon_bad"]["items"]) + "."] if rec["moon_bad"]["items"] else []
    out.append({"kind": "nakshatra", "head": f"In {rec['name']}, pada {pada}", "n": n,
                "text": f"{rec['name']}: " + "; ".join(f for f in facts if f) + ".", "notes": notes,
                "source": ""})
    return out


# --- a bhava read for the chart: its rashi, lord, cusp and the cusp's nakshatra, the grahas in it and aspecting it, its strength,
# and what the classics say of each (the tables in data/lore/), put together, with BPHS 11.14-16's tests of whether it prospers

CO_LORD = {8: "Ke", 11: "Ra"}       # Scorpio and Aquarius: the nodes co-own them, as the app counts lordships
AGE_GOOD, AGE_BAD = ("Yuva", "Kumara"), ("Vriddha", "Mrita")       # BPHS 11.14-16: youthful, adolescent (kishora) vs old and dead
DUSTHANA_LORDS = (3, 6, 8, 11, 12)                                 # "the lords of evil and such other bhavas" (11.16)


def _table(name: str):
    """A combination table, or None until it is written (the pop-up leaves its part out)."""
    return _load(name) if os.path.exists(os.path.join(DIR, name)) else None


def _span(start: float, end: float, back: bool) -> list:
    """How much of the bhava, start to end, lies in each sign, in the order it runs through them ("82% Aries, 18% Taurus")."""
    a, total = (end, (start - end) % 360.0) if back else (start, (end - start) % 360.0)
    parts: dict = {}
    x, left = a, total
    while left > 1e-9:
        s = int(x // 30.0) % 12
        step = min(left, 30.0 * (s + 1) - x if 30.0 * (s + 1) - x > 1e-9 else 30.0)
        parts[s] = parts.get(s, 0.0) + step
        x, left = (x + step) % 360.0, left - step
    out = [{"sign": s + 1, "name": SIGNS[s], "percent": round(100.0 * v / total)} for s, v in parts.items() if total]
    if out:                      # the rounding made to add up to 100, on the largest part
        big = max(out, key=lambda p: p["percent"])
        big["percent"] += 100 - sum(p["percent"] for p in out)
    return [p for p in out if p["percent"] > 0]


def the(ab: str, start: bool = False) -> str:
    """A graha's name as a sentence carries it: "the Sun", "the Moon", "Mars"; ``start``: at the start of a sentence."""
    name = ("the " if ab in ("Su", "Mo") else "") + NAMES[ab]
    return name[:1].upper() + name[1:] if start else name


def bhava_reading(b, ch, cfg, s, house: int, ref: int = 0) -> dict:
    """Bhava ``house`` of the chart, counted from the Lagna (``ref`` 0) or from a graha (1 Sun .. 9 Ketu, the bhava chart's reference),
    in the chosen house system. Its facts (cusp, sign, the cusp's nakshatra with its star and KP sub lords, its span by sign, its lord
    and where the lord is, the grahas in it, every graha's aspect on its cusp in virupas, its Bhava Bala as a share of 7 rupas, the
    sarva bindus of its sign, its karakas), BPHS 11.14-16's tests of whether it prospers, and the reading: each part says which table
    it comes from and what to open (``link``)."""
    from core_logic import ephemeris as E, house_systems as H, kp_astrology as K
    from .houses import REFS, _bhavas
    from .insights import graha_insights
    from .strengths import ashtakavarga_of
    from .windows import aspect_table

    bh = [tuple(x % 360.0 for x in t) for t in _bhavas(b, ch, cfg, s, ref)]      # an arc may run past 360°
    back = sum((e - a) % 360.0 for a, _, e in bh) > 361.0
    start, mid, end = bh[house - 1]
    cusp = mid if s.house_cusp_in_middle else start
    sign = int(cusp // 30.0) + 1
    nak, pada = int(cusp // NAK) + 1, int((cusp % NAK) // (NAK / 4)) + 1
    names = [x["name"] for x in _load("nakshatras.json")["nakshatras"]]
    lon = {ab: ch["planet_longitudes"][NAMES[ab]] for ab in GRAHAS}
    bhava_of = {ab: H.house_of(x, bh) + 1 for ab, x in lon.items()}
    ins = {g["name"]: g for g in graha_insights(b, ch, cfg, s, 1)}
    info = lambda ab: ins[NAMES[ab]]  # noqa: E731
    benefic = lambda ab: info(ab)["natural"] == "Benefic"  # noqa: E731
    asp = {r["body"][:2]: r for r in aspect_table(b, ch, cfg, s, 1, ref)["rows"]}
    full = s.aspect_full
    cusp_sign = lambda h: int((bh[h - 1][1] if s.house_cusp_in_middle else bh[h - 1][0]) // 30.0) + 1  # noqa: E731
    lord_of = lambda h: SIGN_LORD[cusp_sign(h) - 1]  # noqa: E731
    lord = lord_of(house)
    kp = K.get_kp_sub_levels(cusp, 2)
    star_lord = NAK_LORDS[(nak - 1) % 9]
    sub_lord = next(ab for ab in GRAHAS if NAMES[ab] == kp["sub_lord"])
    rec = bhava(house)
    ordn, bname = ORDINAL[house - 1], ORDINAL[house - 1] + " bhava"
    frm = "the Lagna" if ref == 0 else "the " + REFS[ref] if REFS[ref] in ("Sun", "Moon") else REFS[ref]

    def where(ab: str) -> dict:
        g = info(ab)
        return {"graha": ab, "bhava": bhava_of[ab], "sign": g["sign_no"] + 1, "sign_name": g["sign"], "dignity": g["dignity"],
                "retro": bool(ch["retrograde"].get(NAMES[ab])) and ab not in ("Ra", "Ke"), "combust": g["combust"]}

    # the reference graha stands in its own 1st bhava: not an occupant of it
    occupants = [ab for ab in GRAHAS if bhava_of[ab] == house and not (ref and house == 1 and GRAHAS.index(ab) + 1 == ref)]
    aspects = sorted(({"graha": ab, "value": asp[ab]["houses"][house - 1], "benefic": asp[ab]["benefic"] if ab not in ("Ra", "Ke") else False}
                      for ab in GRAHAS if asp[ab]["houses"][house - 1]), key=lambda a: -a["value"])
    seen = full * 0.75          # three quarters of a full aspect or more (BPHS 26's 4th, 8th and 7th): what the reading and its tests count
    strong = [a for a in aspects if a["value"] >= seen]
    k = rec["karakas"]
    karakas = list(dict.fromkeys(k["bphs"] + k["phaladeepika"]))
    bala = None
    if ref == 0:
        rupas = E.chart_shadbala(b, ch, cfg)["bhavas"][house - 1]["rupas"]
        bala = {"rupas": rupas, "percent": rupas / 7.0 * 100.0}       # as a share of the 7 rupas a bhava needs
    sav = ashtakavarga_of(ch, s)["sav"][sign - 1]

    # BPHS 11.14-16: what makes a bhava prosper and what destroys it, tested on this chart
    lg = info(lord)
    age, alert = lg["avasthas"]["Baaladi (age)"], lg["avasthas"]["Jaagradadi (alertness)"]
    ben_in = [ab for ab in occupants if benefic(ab)]
    ben_asp = [a["graha"] for a in strong if a["benefic"] and a["graha"] not in occupants]
    lord_in, lord_asp = bhava_of[lord] == house, asp[lord]["houses"][house - 1] >= seen
    mates = [x for x in lg["with"] if x in ins]
    with_bad = [x for x in mates if ins[x]["natural"] == "Malefic"]
    evil = [(x, [h for h in DUSTHANA_LORDS if h != house and lord_of(h) == x[:2]]) for x in mates]
    evil = [(x, hs) for x, hs in evil if hs]
    L = the(lord)
    awake = alert.startswith(("Jaag", "Jag"))
    checks = [
        (bool(ben_in), f"A benefic in it: {', '.join(the(x) for x in ben_in)}", "BPHS 11.14"),
        (bool(ben_asp), f"A benefic aspects it: {', '.join(the(x) for x in ben_asp)}", "BPHS 11.14"),
        (age.startswith(AGE_GOOD) or awake, f"Its lord, {L}, is {age.split(' (')[0]} in age and {alert.split(' (')[0]} in alertness", "BPHS 11.14-15"),
        (bhava_of[lord] == 10 and house != 10, f"Its lord, {L}, is in the 10th", "BPHS 11.15"),
        (lord_in, f"Its lord, {L}, is in it", "BPHS 11.16"),
        (lord_asp and not lord_in, f"Its lord, {L}, aspects it", "BPHS 11.16"),
    ]
    checks = [{"good": True, "text": t, "source": src} for ok, t, src in checks if ok]
    bad = [
        (not lord_in and not lord_asp, f"Its lord, {L}, neither occupies nor aspects it", "BPHS 11.16"),
        (bool(with_bad), f"Its lord, {L}, is joined by a malefic: {', '.join(the(x[:2]) for x in with_bad)}", "BPHS 11.16"),
        (bool(evil), "Its lord, %s, is joined by %s" % (L, "; ".join(f"{the(x[:2])}, lord of the {' and '.join(ORDINAL[h - 1] for h in hs)}" for x, hs in evil)), "BPHS 11.16"),
        (lg["war"] == "Loses", f"Its lord, {L}, lost a graha war", "BPHS 11.16"),
        (age.startswith(AGE_BAD) or alert.startswith("Sush"), f"Its lord, {L}, is {age.split(' (')[0]} in age and {alert.split(' (')[0]} in alertness", "BPHS 11.16"),
        (bhava_of[lord] in (6, 8, 12) and not lord_in, f"Its lord, {L}, is in the {ORDINAL[bhava_of[lord] - 1]}, a dusthana", "BPHS 12.1-2, 23.7"),
    ]
    checks += [{"good": False, "text": t, "source": src} for ok, t, src in bad if ok]
    mal_in = [ab for ab in occupants if not benefic(ab)]
    if mal_in and house in (3, 6, 10, 11):        # the upachayas: malefics in them give drive and gains in time
        checks.append({"good": True, "text": f"A malefic in an upachaya, which gives it drive: {', '.join(the(x) for x in mal_in)}", "source": ""})
    elif mal_in and not ben_in and not ben_asp:
        checks.append({"good": False, "text": f"A malefic in it, and no benefic in it or aspecting it: {', '.join(the(x) for x in mal_in)}", "source": "BPHS 12.3, 23.7"})
    if bhava_of[lord] in (1, 4, 5, 7, 9) and not lord_in:
        checks.append({"good": True, "text": f"Its lord, {L}, is in the {ORDINAL[bhava_of[lord] - 1]}, a kendra or trikona", "source": "BPHS 12.1-2, 23.7"})
    good, badn = sum(c["good"] for c in checks), sum(not c["good"] for c in checks)
    word = "Favourable" if good > badn else "Afflicted" if badn > good else "Mixed"

    # the reading, part by part
    parts = []
    rb, nb, gb, ga, gr = (_table(n) for n in ("rashi_bhava.json", "nakshatra_bhava.json", "graha_bhava.json", "graha_aspects.json", "graha_rashi.json"))
    if rb:
        r = rb["readings"][sign - 1]["houses"][house - 1]
        parts.append({"kind": "rashi", "head": f"{SIGNS[sign - 1]} on the {ordn} cusp", "jiva": r["jiva"], "ajiva": r["ajiva"],
                      "notes": [f"{L[:1].upper() + L[1:]}, lord of {SIGNS[sign - 1]}, rules the {bname}."], "source": "", "link": {"kind": "rashi", "n": sign}})
    if nb:
        r = nb["readings"][nak - 1]["houses"][house - 1]
        sb = bhava_of[star_lord]
        notes = [f"Its star lord, {the(star_lord)}, is in this bhava itself: its results stay with its own matters." if sb == house else
                 f"Its star lord, {the(star_lord)}, is in the {ORDINAL[sb - 1]} bhava: the {ordn}'s results come through the {ORDINAL[sb - 1]}'s matters.",
                 f"KP sub lord of the cusp: {the(sub_lord)}, in the {ORDINAL[bhava_of[sub_lord] - 1]}."]
        parts.append({"kind": "nakshatra", "head": f"The cusp in {names[nak - 1]}, pada {pada}", "jiva": r["jiva"], "ajiva": r["ajiva"],
                      "notes": notes, "source": "", "link": {"kind": "nakshatra", "n": nak}})
    lords = {(x["lord"], x["house"]): x for x in _load("bhava_lords.json")["slokas"]}
    sl = lords[(house, bhava_of[lord])]
    w = where(lord)
    notes = [f"{L[:1].upper() + L[1:]} is in {w['sign_name']} ({w['dignity'].lower()}){', retrograde' if w['retro'] else ''}{', combust' if w['combust'] else ''}."]
    if gr:
        notes.append(gr["readings"][lord][w["sign"] - 1]["text"])
    if sign in CO_LORD:
        notes.append(f"{NAMES[CO_LORD[sign]]} co-owns {SIGNS[sign - 1]} and speaks for the {bname} too.")
    parts.append({"kind": "lord", "head": f"The {ordn} lord, {NAMES[lord]}, in the {ORDINAL[bhava_of[lord] - 1]}", "text": sl["text"], "notes": notes,
                  "source": f"BPHS 24.{sl['sloka']}", "link": {"kind": "graha", "n": lord}})
    for ab in occupants:
        x = gb["readings"][ab][house - 1] if gb else None
        notes = [f"{the(ab, True)} is in {info(ab)['sign']} ({info(ab)['dignity'].lower()})."]
        if ab in karakas:
            notes.append(f"{NAMES[ab]} is a karaka of the {bname}: the classics warn that a karaka in its own bhava can harm what it signifies there (karako bhava nashaya), though Saturn in the 8th gives a long life.")
        parts.append({"kind": "occupant", "head": f"{NAMES[ab]} in the {ordn}", "text": x["text"] if x else "", "notes": notes,
                      "source": x["source"] if x else "", "link": {"kind": "graha", "n": ab}, "tone": "good" if benefic(ab) else "bad"})
    for a in strong:
        if a["graha"] in occupants:
            continue
        x = ga["readings"][a["graha"]][house - 1] if ga else None
        parts.append({"kind": "aspect", "head": f"{NAMES[a['graha']]}'s aspect, {a['value']} of {full} virupas", "text": x or "",
                      "notes": [], "source": "", "link": {"kind": "graha", "n": a["graha"]}, "tone": "good" if a["benefic"] else "bad"})
    for ab in karakas:
        if ab in occupants:
            continue
        w = where(ab)
        parts.append({"kind": "karaka", "head": f"Karaka {NAMES[ab]} in the {ORDINAL[w['bhava'] - 1]}",
                      "text": f"{the(ab, True)}, a natural significator of the {bname}, is in {w['sign_name']} ({w['dignity'].lower()}) in the {ORDINAL[w['bhava'] - 1]} bhava; judge the {ordn}'s matters from it as well as from the bhava and its lord.",
                      "notes": [], "source": "BPHS 32.31-34" if ab in k["bphs"] else "Phaladeepika 15.17", "link": {"kind": "graha", "n": ab}})
    return {"house": house, "ref": ref, "from": frm, "name": rec["name"], "gloss": rec["gloss"], "cusp": cusp, "start": start, "end": end,
            "sign": sign, "sign_name": SIGNS[sign - 1],
            "nakshatra": {"n": nak, "name": names[nak - 1], "pada": pada, "lord": star_lord, "lord_bhava": bhava_of[star_lord],
                          "sub_lord": sub_lord, "sub_bhava": bhava_of[sub_lord]},
            "span": _span(start, end, back), "lord": {**where(lord), "co": CO_LORD.get(sign)},
            "occupants": [where(ab) for ab in occupants], "aspects": aspects, "full": full, "bala": bala, "sav": sav,
            "karakas": [{**where(ab), "in_it": bhava_of[ab] == house} for ab in karakas],
            "checks": checks, "verdict": {"good": good, "bad": badn, "word": word}, "parts": parts,
            "significations": rec["significations"], "about": rec["about"]}
