"""kuja: part of compatibility (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Dict, Any, Optional
from ..utils import norm360
from ..natal_chart import get_graha_dignity
from ..shadbala.engine import aspect_value
from ..tajika import DEEPTAMSA

# ---------------------------------------------------------------------------
# 4. Kuja Dosha (Manglik Dosha) Evaluation Engine
# ---------------------------------------------------------------------------

# Mars in these bhavas from the lagna, the Moon or Venus (the common rule, with the 2nd as in the south; docs/SOURCES.md)
KUJA_HOUSES = (1, 2, 4, 7, 8, 12)
KUJA_REFS = ("Venus", "Moon", "Lagna")      # strongest first
# Jupiter touches Mars only within the smaller of their Tajika deeptamsas (Ma 8°, Ju 9°), as the Longevity rules' orbs
KUJA_ORB = min(DEEPTAMSA["Mars"], DEEPTAMSA["Jupiter"])


def evaluate_kuja_dosha(
    planet_longitudes: Dict[str, float],
    lagna_lon: float,
    mars_bhavas: Optional[Dict[str, int]] = None,
    aspect_parasara: bool = True,
) -> Dict[str, Any]:
    """
    Evaluates Kuja Dosha (Manglik Dosha) for a native:
    Mars placed in bhavas 1, 2, 4, 7, 8, 12 counted from, strongest first:
    1. Venus (Shukra Manglik)
    2. Moon (Chandra Manglik)
    3. Lagna

    ``mars_bhavas``: Mars's bhava (1-12) from "Lagna", "Moon" and "Venus" in the chart's own bhava system (the
    bhava chakra, by the cusps); without it, the signs are counted (whole-sign houses).

    Classical Cancellations:
    - Mars in Aries in 1st bhava
    - Mars in Scorpio in 4th bhava
    - Mars in Capricorn in 7th bhava
    - Mars in Leo / Aquarius in 8th bhava
    - Mars in Sagittarius in 12th bhava
    - Mars in own sign, moolatrikona or exalted (by its degree)
    - Jupiter with Mars or looking at it (Jupiter's full aspects on the 5th, 7th and 9th, BPHS 26), within ``KUJA_ORB``
      of the conjunction or the aspect's exact angle, across a sign's edge too; the aspect's sphuta drishti as a
      percentage (``aspect_parasara``: Parasara's curves for Jupiter, else Raman's)

    ``cancel``: each cancellation as {"kind": "dignity" | "sign" | "yuti" | "drishti", "text", and "dig" (the dignity),
    "deg" (the yuti's or the aspect's distance from exact) or "aspect" (5, 7 or 9) and "pct"}; ``cancellations`` its texts.
    """
    if "Mars" not in planet_longitudes:
        return {"has_kuja_dosha": False, "reason": "Mars longitude not provided"}

    mars_sign = int(norm360(planet_longitudes["Mars"]) // 30.0)

    def by_sign(ref_lon: float) -> int:
        return ((mars_sign - int(norm360(ref_lon) // 30.0)) % 12) + 1

    if mars_bhavas:
        houses = {r: int(mars_bhavas[r]) for r in KUJA_REFS}
    else:
        houses = {"Lagna": by_sign(lagna_lon), "Moon": by_sign(planet_longitudes.get("Moon", lagna_lon)),
                  "Venus": by_sign(planet_longitudes.get("Venus", lagna_lon))}
    h_from_lagna = houses["Lagna"]

    afflictions = [f"{r} (Bhava {houses[r]})" for r in KUJA_REFS if houses[r] in KUJA_HOUSES]
    has_dosha = len(afflictions) > 0
    cancel = []

    dig = get_graha_dignity("Mars", planet_longitudes["Mars"])
    if dig in ("Own Sign", "Moolatrikona", "Exalted"):
        cancel.append({"kind": "dignity", "dig": dig, "text": f"Mars {'exalted' if dig == 'Exalted' else dig.lower()}"})

    rule = {(1, 0): "Aries in the 1st", (4, 7): "Scorpio in the 4th", (7, 9): "Capricorn in the 7th", (8, 4): "Leo in the 8th",
            (8, 10): "Aquarius in the 8th", (12, 8): "Sagittarius in the 12th"}.get((h_from_lagna, mars_sign))
    if rule:
        cancel.append({"kind": "sign", "text": f"Mars in {rule}"})

    if "Jupiter" in planet_longitudes:
        d = norm360(planet_longitudes["Mars"] - planet_longitudes["Jupiter"])      # Mars this far ahead of Jupiter
        off = lambda a: abs((d - a + 180.0) % 360.0 - 180.0)  # noqa: E731
        if off(0.0) <= KUJA_ORB:
            cancel.append({"kind": "yuti", "deg": round(off(0.0), 1), "text": f"Jupiter with Mars, {off(0.0):.1f}° apart"})
        for n, a in ((5, 120.0), (7, 180.0), (9, 240.0)):
            if off(a) <= KUJA_ORB:
                pct = round(aspect_value(d, 5, aspect_parasara))
                cancel.append({"kind": "drishti", "aspect": n, "pct": pct, "deg": round(off(a), 1),
                               "text": f"Jupiter's {n}th aspect on Mars, {pct}% ({off(a):.1f}° from exact)"})
    cancellations = [c["text"] for c in cancel]

    is_cancelled = len(cancellations) > 0

    return {
        "has_kuja_dosha": has_dosha,
        "is_cancelled": is_cancelled,
        "houses": houses,
        "basis": "bhava" if mars_bhavas else "sign",
        "affliction_sources": afflictions,
        "cancellations": cancellations,
        "cancel": cancel,
        "intensity": "None" if not has_dosha else ("Neutralized" if is_cancelled else ("High" if len(afflictions) >= 2 else "Moderate")),
        "status": "No Kuja Dosha" if not has_dosha else ("Kuja Dosha Cancelled" if is_cancelled else f"Active Kuja Dosha from {', '.join(afflictions)}")
    }
