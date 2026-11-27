"""Remedies: serve curated JSON and compute birth-condition flags for BPHS Ch. 85–96."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from . import service

ROOT = os.path.join(os.path.dirname(__file__), "..", "data")

# ephemeris.panchanga tithi is 0..29 (0 = Śukla Pratipadā, 14 = Pūrṇimā, 29 = Amāvāsyā)
_AMAVASYA = 29
_KRISHNA_CHATURDASHI = 28  # Kṛṣṇa Caturdaśī
# Yoga indices 0..26; Vyātīpāta is traditionally the 17th yoga (0-based 16)
_VYATIPATA = 16
# Karaṇa: the compact index; Vishti/Bhadra is the inauspicious repeating karaṇa.
# ephemeris maps elong/6 into _karana_index — treat "Bhadra" via name when available.


def _load(name: str) -> Any:
    path = os.path.join(ROOT, name)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def topics() -> Dict[str, Any]:
    return {
        "vaishnava": _load("remedies_vaishnava.json"),
        "bphs": _load("remedies_bphs.json"),
    }


def calculation_topics() -> Dict[str, Any]:
    return _load("calculations_topics.json")


def _moon_gandanta(lon: float) -> bool:
    """Water–fire junctions: last/first pādas of Revatī–Aśvinī, Āśleṣā–Maghā, Jyeṣṭhā–Mūla."""
    # Same rule as ayurdaya.Natal.gandanta: Moon in star quarter on either side of water-fire junction
    return not (10.0 / 3.0 <= lon % 120.0 < 120.0 - 10.0 / 3.0)


def _abhukta_mula(moon_lon: float) -> bool:
    """Last 6 ghaṭīs of Jyeṣṭhā + first 8 of Mūla ≈ last 1.333° of Jyeṣṭhā and first 1.777° of Mūla.
    Jyeṣṭhā = nakṣatra 17 (0-based), Mūla = 18; each nakṣatra = 13°20′."""
    nak = moon_lon * 0.075  # / 13.333...
    # Jyeṣṭhā spans 226°40′–240°; Mūla 240°–253°20′
    # Abhukta: last 6/60 of Jyeṣṭhā (1.333°) and first 8/60 of Mūla (1.777°)
    if 240.0 - (13.3333333333 * 6.0 / 60.0) <= moon_lon < 240.0:
        return True
    if 240.0 <= moon_lon < 240.0 + (13.3333333333 * 8.0 / 60.0):
        return True
    return False


def _jyeshtha_gandanta(moon_lon: float) -> bool:
    """Jyeṣṭhā–Mūla nakṣatra gandānta: last 2 ghaṭīs Jyeṣṭhā + first 2 Mūla."""
    span = 13.3333333333
    if 240.0 - (span * 2.0 / 60.0) <= moon_lon < 240.0 + (span * 2.0 / 60.0):
        return True
    return False


def _sankranti(sun_lon: float, orb_deg: float = 0.5) -> bool:
    """Sun within orb of a sign boundary."""
    rem = sun_lon % 30.0
    return rem <= orb_deg or rem >= 30.0 - orb_deg


def _near_eclipse(jd_ut: float, cfg, orb_days: float = 0.75) -> bool:
    try:
        from core_logic import ephemeris as E
        for kind in ("solar", "lunar"):
            try:
                info = E.next_eclipse(jd_ut - orb_days, kind=kind, cfg=cfg)
                peak = info.get("max_jd")
                if peak is not None and abs(float(peak) - jd_ut) <= orb_days:
                    return True
            except Exception:
                continue
    except Exception:
        pass
    return False


def chart_flags(birth: service.BirthIn, settings: Optional[service.SettingsIn]) -> Dict[str, Any]:
    b, cfg, ch, _ = service._raw(*service._key(birth, settings))
    from core_logic import ephemeris as E

    p = E.panchanga(b, ch, cfg)
    sun = ch["planet_longitudes"]["Sun"]
    moon = ch["planet_longitudes"]["Moon"]
    tithi = int(p["tithi"])
    yoga = int(p["yoga"])
    karana = int(p["karana"])  # 6 = Vishti (Bhadra)

    flags = {
        "amavasya": tithi == _AMAVASYA,
        "krishna_chaturdashi": tithi == _KRISHNA_CHATURDASHI,
        "bhadra_yoga": karana == 6 or yoga == _VYATIPATA,  # Bhadra karaṇa or Vyātīpāta (Ch. 88)
        "vyatipata": yoga == _VYATIPATA,
        "sankranti": _sankranti(sun),
        "gandanta": _moon_gandanta(moon),
        "abhukta_mula": _abhukta_mula(moon),
        "jyeshtha_gandanta": _jyeshtha_gandanta(moon),
        "eclipse": _near_eclipse(b.jd_ut, cfg),
        # Not detectable from birth alone without family data:
        "family_nakshatra": False,
        "daughter_after_three_sons": False,
        "unusual_delivery": False,
        "inauspicious_list": True,  # overview chapter always listed when any flag, else for browsing
    }

    bphs = _load("remedies_bphs.json")
    applicable: List[str] = []
    for e in bphs.get("conditional", []):
        cond = e.get("condition")
        if cond == "inauspicious_list":
            if any(flags[k] for k in flags if k not in ("inauspicious_list", "family_nakshatra", "daughter_after_three_sons", "unusual_delivery")):
                applicable.append(e["id"])
            continue
        if cond and flags.get(cond):
            applicable.append(e["id"])

    return {"flags": flags, "applicable": applicable, "panchanga": {
        "tithi": tithi, "yoga": yoga, "nakshatra": int(p["nakshatra"]),
        "karana": int(p["karana"]),
    }}
