"""
core_logic/conditional_dasas.py
===============================
Which nakshatra dasa suits a chart (the "Conditional Nakshatra Dasa Methodology" text). Parasara's condition only
makes a dasa applicable: it beats Vimsottari when its controlling planet is strong too, and among the applicable
dasas the strongest controlling planet wins. The strength reads the app's dignity tables, compound
relationships and combustion rule.

The text leaves its exceptions to judgement. Here they are fixed rules:

* "with" a planet means in the same rasi sign, for association and for affliction alike;
* wherever a condition names a house (Rahu from the lagna lord, the 10th lord in the 10th, the lagna lord in the 7th,
  Sun in lagna) the house is counted from the reference point's degree using equal 30° bhava-madhya divisions (the
  reference longitude is the midpoint of the 1st division), not by whole signs — so a planet near the boundary of a
  sign-based house may fall outside by degree (PVR paper Examples 15 & 28);
* a Shadbala below the planet's minimum (percent of the required rupas under 100) is a weakening too; the nodes have none;
* a weakening (sign edge, combust, afflicted) makes the planet weak whatever else it has;
* a 9th or 10th lord beside the planet associates, it does not afflict, even when it is an enemy or also a 6th / 8th lord;
* "extra strong" and a node with other planets are half a step: they rank a planet above its own rung, not past the
  next one, and lift a weak planet just into consideration;
* a node with other planets is never afflicted by them ("any planets").

Points are indexed as in dasa_systems.JChart: 0 Lagna, 1 Sun .. 7 Saturn, 8 Rahu, 9 Ketu.
"""
from typing import Any, Dict, List, Sequence

from . import dasa_systems as J
from . import natal_chart as N
from . import sign_strength as S
from .shadbala import NATURAL_RELATIONS_9, compound_relationships

VIMSOTTARI = "vimsottari_dasa"
SIGN_EDGE_DEGREES = 1.0     # "the very beginning or end of a sign"; the text gives no number
NAMES = J.JChart.POINTS
ENEMY = 4                   # NATURAL_RELATIONS_9's code
RELATION = {1: (2, "great friend's sign"), 2: (1, "friend's sign"), 3: (0, "neutral sign"), 4: (0, "enemy's sign"),
            5: (0, "great enemy's sign")}       # compound code -> (rung, name)

# (dasa, controlling planet, condition)
DASAS = (
    ("shodasottari_dasa", 5, "Lagna in Sun's hora in Sukla paksha or in Moon's hora in Krishna paksha"),
    ("dwadasottari_dasa", 9, "Lagna in Taurus or Libra navamsa"),
    ("ashtottari_dasa", 3, "Rahu in a quadrant or trine from the lagna lord, but not in lagna"),
    ("panchottari_dasa", 6, "Lagna in Cancer dwadasamsa"),
    ("sataabdika_dasa", 1, "Lagna in the same sign in rasi and navamsa"),
    ("chaturaseeti_sama_dasa", 7, "The 10th lord in the 10th"),
    ("dwi_saptati_sama_dasa", 8, "Lagna lord in the 7th or 7th lord in lagna"),
    ("shashti_hayani_dasa", 2, "Sun in lagna"),
    ("shat_trimsa_sama_dasa", 4, "Lagna in Sun's hora by day or in Moon's hora by night"),
)


def _lord(jc: J.JChart, house: int) -> int:
    return S.SIGN_LORDS[(jc.signs[0][0] + house - 1) % 12]


def _house(jc: J.JChart, frm: int, p: int) -> int:
    """0-based house of point ``p`` counted from point ``frm`` (0 the lagna) by degree: equal 30° houses with ``frm`` at the midpoint of the 1st."""
    return int(((jc.lons[p] - jc.lons[frm]) % 360.0 + 15.0) // 30.0) % 12


def _conditions(jc: J.JChart) -> Dict[str, bool]:
    lagna = jc.signs[0][0]
    sun_hora = N.compute_varga_d2(jc.lons[0]) == 4      # Parasara's hora whatever the chart's hora scheme: only it has the Sun's and Moon's halves
    lord = _lord(jc, 1)
    from_lord = _house(jc, lord, 8)
    return {
        "shodasottari_dasa": sun_hora == (J._elongation(jc) < 180.0),
        "dwadasottari_dasa": jc.signs[1][0] in (1, 6),
        "ashtottari_dasa": _house(jc, 0, 8) != 0 and (from_lord % 3 == 0 or from_lord % 4 == 0),
        "panchottari_dasa": jc.signs[11][0] == 3,
        "sataabdika_dasa": jc.signs[1][0] == lagna,
        "chaturaseeti_sama_dasa": _house(jc, 0, _lord(jc, 10)) == 9,
        "dwi_saptati_sama_dasa": _house(jc, 0, lord) == 6 or _house(jc, 0, _lord(jc, 7)) == 0,
        "shashti_hayani_dasa": _house(jc, 0, 1) == 0,
        "shat_trimsa_sama_dasa": sun_hora == jc.day["is_day"],
    }


def _dignity(p: int, sign: int, compound: Sequence[Sequence[int]]):
    """The text's order of strength: (rung 5 .. 1, or 0 when weak, name)."""
    if S.EXALTATION[p] == sign:
        return 5, "exalted"
    if S.DEBILITATION[p] == sign:
        return 0, "debilitated"
    if S.MOOLATRIKONA[p] == sign:
        return 4, "moolatrikona"
    if sign in J.OWN_SIGNS[p]:
        return 3, "own sign"
    return RELATION[compound[p - 1][S.SIGN_LORDS[sign] - 1]]


def _strength(p: int, jc: J.JChart, retrograde: Sequence[bool], by_motion: bool, shadbala: Sequence[float], classical: bool = False) -> Dict[str, Any]:
    sg = jc.signs[0]
    rung, dignity = _dignity(p, sg[p], compound_relationships(sg[1:10]))
    others = [q for q in range(1, 10) if q != p and sg[q] == sg[p]]
    good = {_lord(jc, 9): "9th lord", _lord(jc, 10): "10th lord"}
    bad = {_lord(jc, 6): "6th lord", _lord(jc, 8): "8th lord"}
    weak: List[str] = []
    if min(jc.lons[p] % 30.0, 30.0 - jc.lons[p] % 30.0) < SIGN_EDGE_DEGREES:
        weak.append("at the edge of its sign")
    if N.is_combust(p, jc.lons, retrograde, by_motion, classical):
        weak.append("combust")
    if p < 8 and p < len(shadbala) and shadbala[p] < 100.0:
        weak.append("Shadbala %.0f%% of the minimum" % shadbala[p])
    if p < 8:
        for q in others:
            if q in bad and q not in good:
                weak.append("with %s (%s)" % (NAMES[q], bad[q]))
            elif NATURAL_RELATIONS_9[p - 1][q - 1] == ENEMY and q not in good:
                weak.append("with its enemy %s" % NAMES[q])
    with_lords = ["with %s (%s)" % (NAMES[q], good[q]) for q in others if q in good]
    node_joined = p >= 8 and bool(others)
    boosts = with_lords + (["with %s" % ", ".join(NAMES[q] for q in others)] if node_joined else [])
    score = 0.0 if weak else rung + 0.5 * (bool(with_lords) + node_joined)
    return {"score": score, "dignity": dignity, "notes": weak + boosts}


def best_dasa(jc: J.JChart, retrograde: Sequence[bool] = (), by_motion: bool = True, shadbala: Sequence[float] = (), classical: bool = False) -> Dict[str, Any]:
    """The method's steps on one chart. ``best`` lists the winning dasas, more than one when their controlling planets
    tie (the text has no further rule), or Vimsottari when no applicable dasa has a strong planet; ``rows`` shows all
    nine. ``jc.day`` is needed for the day / night condition, ``retrograde`` by point and ``by_motion`` for combustion,
    ``shadbala`` the percent of the required rupas by point (index 0 unused; empty: Shadbala is not weighed)."""
    met = _conditions(jc)
    rows = [{"key": key, "planet": NAMES[p], "condition": text, "met": met[key], **_strength(p, jc, retrograde, by_motion, shadbala, classical)}
            for key, p, text in DASAS]
    top = max((r["score"] for r in rows if r["met"]), default=0.0)
    return {"best": [r["key"] for r in rows if r["met"] and r["score"] == top] if top > 0 else [VIMSOTTARI], "rows": rows}
