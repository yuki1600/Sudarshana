"""Graha insights: what Starlight's Planets tab shows when a graha's row is opened. Each fact comes from the view that already lists it
(Key Info, Strengths, Longevity); this only gathers them per graha."""
import dataclasses
import re

from core_logic import avasthas as AV, ayurdaya as A, house_systems as H, key_info as K, varga_charts as V, laghu_parasari as LP, natal_chart as N, shadbala as SB, sign_strength as SS

from . import settings as S
from .basics import PLANETS
from .charts import CLASS_NAMES
from .houses import _bhavas
from .longevity import natal_of
from .strengths import vimsopaka_of
from .tables import _avasthas, sign_dignity
from .windows import aspect_table

MKS = {**N.MKS_HOUSES, "Ketu": 4}       # Ketu in the 4th is the usual reading; the table stops at Rahu


def _dignity(p, lon, sign, rel):
    """Exalted, debilitated, moolatrikona or own (tables.sign_dignity); otherwise its relation to the sign's lord."""
    d = sign_dignity(p, lon, sign)
    if d:
        return d
    return "Neutral sign" if CLASS_NAMES[rel] == "Neutral" else "%s's sign" % CLASS_NAMES[rel]


def graha_insights(b, ch, cfg, s, d=1):
    """In D-``d`` the facts read from signs (sign, house, dignity, relation, yutis, drishtis, lordships, functional nature) are that varga's;
    the ones read from the longitude itself (combustion, war, mrityu and pushkara bhaga, shadbala, avasthas) stay the rasi's."""
    rasi, sb = natal_of(b, ch, cfg, s)
    opt = S.varga_options(s)
    n = rasi if d == 1 else dataclasses.replace(rasi, lons=[V.varga_longitude(x, d, opt) for x in rasi.lons])
    lons, sg, L = n.lons, n.s, n.s[0]
    av = _avasthas(b, ch, cfg, s)
    comp = SB.compound_relationships(sg[1:10])
    nature = LP.evaluate_functional_nature_for_lagna(L)
    marakas = A.marakas(n)
    war = N.planetary_war(rasi.lons)
    vim = {r["name"]: r for r in vimsopaka_of(ch, s)}
    # the 64th navamsa and the Parasara 22nd drekkana only, from the Lagna and the Moon, as the Overview's lords box shows
    malicious = [(label.replace("Pararsara", "Parasara"), lords) for label, lords in K.malicious_divisions(rasi.lons[0], rasi.lons[2])
                 if re.match(r"The (64th navamsa|22nd Para?r?sara drekkana)", label)]
    bh = _bhavas(b, ch, cfg, s)        # the chosen house system's bhavas, from the lagna
    asp = aspect_table(b, ch, cfg, s, d, 0)["rows"]      # the Aspects tab's virupas in this varga, houses from the lagna: row p's aspect on each graha and house
    BALAS = ("sthana", "kala", "dig", "cheshta", "naisargika", "drig", "ishta", "kashta")
    seven = [sb["planets"][q] for q in PLANETS[:7]]
    rank = lambda q, k: 1 + sum(o[k] > q[k] for o in seven)  # noqa: E731     # 1st: the highest of the seven
    out = []
    for p in range(1, 10):
        name, lon, sign = PLANETS[p - 1], lons[p], sg[p]
        house, lord = n.house(p), SS.SIGN_LORDS[sign]
        bhava = H.house_of(lon, bh) + 1 if d == 1 else house     # a varga has no bhava chart of its own: its house from its lagna
        dig = _dignity(p, lon, sign, comp[p - 1][lord - 1])
        others = [q for q in range(1, 10) if q != p and {p, q} != {8, 9}]     # Rahu and Ketu, always 7th from each other, don't count on each other
        withs = [PLANETS[q - 1] for q in others if sg[q] == sign]
        aspects = [PLANETS[q - 1] for q in others if sg[q] != sign and n.aspects(q, sign)]
        if p <= 7:
            f = nature[name]
            func = {"label": f["classification"], "why": re.sub(r"\[([\d, ]*)\]", r"\1", f["rationale"])}     # the engine prints its house lists as Python lists
        else:
            func = {"label": "Results of its dispositor", "why": "A node owns no bhava of its own in Laghu Parasari: it gives the results of %s, its sign's lord, and of the grahas with it." % PLANETS[lord - 1]}
        a = av[name]
        laj = AV.compute_lajjitadi_avastha(name, sign, house, withs, aspects, dig)
        amsa, bhaga, _ = N.pushkara_position(rasi.lons[p], s.pushkara_patel)
        wins, loses = war[p]
        x = {"name": name, "sign": N.RASI_NAMES_EN[sign], "sign_no": sign, "house": house, "dignity": dig,
             "owns": [(sg2 - L) % 12 + 1 for sg2 in range(12) if SS.owns_sign(p, sg2)],
             "with": withs, "aspected_by": aspects,
             "aspects_on": sorted(({"from": PLANETS[q - 1], "value": asp[q - 1]["cells"][p - 1], "benefic": q in n.b7} for q in others if asp[q - 1]["cells"][p - 1]), key=lambda a: -a["value"]),
             "aspects_houses": asp[p - 1]["houses"], "aspect_full": s.aspect_full,
             "natural": "Benefic" if p in n.b7 else "Malefic",
             "functional": func,
             "vimsopaka": vim[name]["shodasa"],
             "avasthas": {"Baaladi (age)": a["age_name"], "Jaagradadi (alertness)": a["parashara_alertness_name"], "Deeptaadi (mood)": a["parashara_mood_names"] or "-",
                          "Sayanadi (activity)": a["activity_name"], "Lajjitadi": ", ".join(laj["all_qualifying_states"]) or laj["primary_lajjitadi_avastha"]},
             "maraka": marakas.get(p, []),
             "bhava": bhava, "mks": MKS.get(name) == bhava, "mks_house": MKS.get(name),     # by the bhava it occupies, not its sign from the lagna
             "combust": rasi.combust(p), "relation": "Self" if SS.owns_sign(p, sign) else CLASS_NAMES[comp[p - 1][lord - 1]],     # Rahu and Ketu co-own Aquarius and Scorpio "vargottama": V.varga_sign(lon, 9, opt) == sign,
             "war": "Wins" if wins else "Loses" if loses else None,
             "mrityu": N.mrityu_bhaga_distance(name, rasi.lons[p], s.mrityu_second_table, s.mrityu_location)[1],
             "pushkara_amsa": amsa, "pushkara_bhaga": bhaga,
             "drekkana": K.drekkana_labels(rasi.lons[p]),
             "malicious": [label for label, lords in malicious if name in lords]}
        if p <= 7:
            q = sb["planets"][name]
            x["shadbala"] = {"rupas": q["rupas"], "required": SB._REQUIRED_RUPAS[p - 1], "percent": q["percent"],
                             "parts": [{"key": k, "value": q[k], "rank": rank(q, k)} for k in BALAS]}
        out.append(x)
    return out
