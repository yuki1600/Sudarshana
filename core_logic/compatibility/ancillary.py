"""ancillary: part of compatibility (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Dict, Any
from ..natal_chart import RASI_NAMES_EN, RASI_LORDS
from ..aspects_friendships import get_natural_relationship
from .tables import GANA_NAMES, NAKSHATRA_GANA, NAKSHATRA_RAJJU, NAKSHATRA_YONI, RAJJU_NAMES, VEDHA_PAIRS, YONI_NAMES, YONI_POINTS, _ordinal
from .kutas import compute_bhakoota_kuta

# ---------------------------------------------------------------------------
# 3. Ancillary Kootas (Mahendra, Stree Deergha, Rajju, Vedha)
# ---------------------------------------------------------------------------

def compute_ancillary_kootas(bride_nak: int, groom_nak: int) -> Dict[str, Any]:
    """
    Computes ancillary non-point Kootas:
    - Mahendra Kuta (progeny, longevity, divine blessing)
    - Stree Deergha (groom star distance > 9 nakshatras)
    - Rajju Kuta (5 ropes; affliction if same rope)
    - Vedha Kuta (piercing stars causing friction)
    """
    b_nak = bride_nak % 27
    g_nak = groom_nak % 27
    
    dist = ((g_nak - b_nak) % 27) + 1
    mahendra = dist in [4, 7, 10, 13, 16, 19, 22, 25]
    stree_deergha = dist > 9
    
    b_r = NAKSHATRA_RAJJU[b_nak]
    g_r = NAKSHATRA_RAJJU[g_nak]
    rajju_compatible = (b_r != g_r)
    rajju_dosha_zone = RAJJU_NAMES[b_r] if b_r == g_r else None
    
    vedha_afflicted = (b_nak, g_nak) in VEDHA_PAIRS
    
    return {
        "mahendra_kuta": {
            "is_present": mahendra,
            "status": "Auspicious for Progeny & Wealth" if mahendra else "Neutral"
        },
        "stree_deergha": {
            "is_present": stree_deergha,
            "distance_nakshatras": dist,
            "status": "Favorable (> 9 nakshatras)" if stree_deergha else "Short Distance"
        },
        "rajju_kuta": {
            "is_compatible": rajju_compatible,
            "bride_rajju": RAJJU_NAMES[b_r],
            "groom_rajju": RAJJU_NAMES[g_r],
            "status": "Safe (Different Rajjus)" if rajju_compatible else f"Rajju Dosha on {rajju_dosha_zone}"
        },
        "vedha_kuta": {
            "is_afflicted": vedha_afflicted,
            "status": "Severe Vedha Obstruction" if vedha_afflicted else "No Vedha Obstruction"
        }
    }

# Dasa Kuta (South India's ten poruthams), each Uttama 1, Madhyama ½ or Adhama 0, of 10, counting from the girl's star or sign to the boy's
VASYA_SIGNS = {0: (4, 7), 1: (3, 6), 2: (5,), 3: (7, 8), 4: (6,), 5: (11, 2), 6: (9, 5), 7: (3,), 8: (11,), 9: (0, 10), 10: (0,), 11: (9,)}
DASHA_LEVELS = ((6.5, "Excellent"), (4.5, "Good"), (3.0, "Average"), (0.0, "Low"))


def compute_dashakoota(bride_nak: int, groom_nak: int, bride_rasi: int, groom_rasi: int) -> Dict[str, Any]:
    b, g, br, gr = bride_nak % 27, groom_nak % 27, bride_rasi % 12, groom_rasi % 12
    n = (g - b) % 27 + 1                      # the boy's star counted from the girl's
    out = []

    def add(name, grade, why, girl="", boy=""):
        """``girl`` / ``boy``: each one's own value, where the porutham compares two (their ganas, yonis …), for the table's columns."""
        out.append({"kuta": name, "grade": grade, "points": {"Uttama": 1.0, "Madhyama": 0.5, "Adhama": 0.0}[grade], "status": why, "girl": girl, "boy": boy})
    r = n % 9
    add("Dina", "Madhyama" if n == 1 else "Uttama" if r in (0, 2, 4, 6, 8) else "Adhama",
        "Same star" if n == 1 else f"{_ordinal(n)} star from the girl's ({'good' if r in (0, 2, 4, 6, 8) else 'janma, vipat, pratyak or naidhana tara'})")
    bg, gg = NAKSHATRA_GANA[b], NAKSHATRA_GANA[g]
    add("Gana", "Uttama" if bg == gg or (bg, gg) == (0, 1) else "Madhyama" if (bg, gg) == (1, 0) else "Adhama", f"Girl {GANA_NAMES[bg]}, boy {GANA_NAMES[gg]}", GANA_NAMES[bg], GANA_NAMES[gg])
    add("Mahendra", "Uttama" if n in (4, 7, 10, 13, 16, 19, 22, 25) else "Adhama", "Same star" if n == 1 else f"{_ordinal(n)} star from the girl's")
    add("Stree Deergha", "Uttama" if n > 13 else "Madhyama" if n >= 7 else "Adhama", ("Same star" if n == 1 else f"{_ordinal(n)} star from the girl's") + " (beyond 13th good, 7th to 13th middling)")
    y = YONI_POINTS[NAKSHATRA_YONI[b]][NAKSHATRA_YONI[g]]
    add("Yoni", "Uttama" if y >= 3 else "Madhyama" if y == 2 else "Adhama", f"{YONI_NAMES[NAKSHATRA_YONI[b]]} / {YONI_NAMES[NAKSHATRA_YONI[g]]}", YONI_NAMES[NAKSHATRA_YONI[b]], YONI_NAMES[NAKSHATRA_YONI[g]])
    bk = compute_bhakoota_kuta(br, gr)
    add("Rasi", "Uttama" if not bk["has_dosha"] else "Madhyama" if bk["is_cancelled"] else "Adhama", f"{bk['placement']} from each other" + (" (lords friendly)" if bk["is_cancelled"] else ""))
    bl, gl = RASI_LORDS[br], RASI_LORDS[gr]
    rel = {get_natural_relationship(bl, gl), get_natural_relationship(gl, bl)} if bl != gl else {"Friend"}
    add("Rasyadhipati", "Adhama" if "Enemy" in rel else "Uttama" if rel == {"Friend"} else "Madhyama", f"{bl} / {gl}" + (": the same lord" if bl == gl else ": " + " / ".join(sorted(rel)).lower()), bl, gl)
    vasya = gr in VASYA_SIGNS[br] or br in VASYA_SIGNS[gr]
    add("Vasya", "Uttama" if vasya else "Adhama", f"{RASI_NAMES_EN[br]} / {RASI_NAMES_EN[gr]}" + (" attract each other" if vasya else ""), RASI_NAMES_EN[br], RASI_NAMES_EN[gr])
    rb, rg = NAKSHATRA_RAJJU[b], NAKSHATRA_RAJJU[g]
    add("Rajju", "Adhama" if rb == rg else "Uttama", f"Both {RAJJU_NAMES[rb]}: rajju dosha" if rb == rg else f"{RAJJU_NAMES[rb]} / {RAJJU_NAMES[rg]}", RAJJU_NAMES[rb], RAJJU_NAMES[rg])
    vedha = (b, g) in VEDHA_PAIRS
    add("Vedha", "Adhama" if vedha else "Uttama", "The stars pierce each other" if vedha else "No vedha")
    score = sum(k["points"] for k in out)
    return {"score": score, "max_score": 10.0, "level": next(name for least, name in DASHA_LEVELS if score >= least), "kutas": out,
            "rajju_dosha": rb == rg, "vedha_dosha": vedha}
