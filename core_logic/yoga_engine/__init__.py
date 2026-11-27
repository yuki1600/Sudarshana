"""
core_logic/yoga_engine/
=======================
The yoga engine: the yoga catalogue of the "Other strengths" page and its list mode, and the 91 checks run on one
divisional chart, group by group: Mahapurusha (BPHS 75), solar (BPHS 38), lunar (BPHS 37), Naabhasa (BPHS 35), other
popular yogas (BPHS 36, PD 6), raja yogas (BPHS 34, 39), raja sambandha (BPHS 40), dhana (BPHS 41), daridra (BPHS 42)
and parivraja (BPHS 79).  Each yoga's verses: ``YOGA_SOURCES``; docs/SOURCES.md section 11.

The checks read signs only: the bodies (0 Lagna, 1 Sun .. 9 Ketu) in the chosen varga, a few special points
in it (14 Hora Lagna, 15 Ghati Lagna, 59 Arudha Lagna, 67 the 9th bhava arudha), the navamsa (varga 1) and
for one yoga the D-1, D-9, D-2, D-3, D-12, D-30 signs, the chara karakas, the lagna's degree and the
compound relationships of the varga.  Results are listed in the reference catalogue's order with their givers
(point indices); the names and texts are that catalogue's.

It replaced the textbook ``yogas.py``, deleted on 2026-10-27.
"""
# The module was split into these parts; every name is re-exported from the part holding its final binding.
from typing import Any, Dict, List, Optional, Sequence, Tuple
from .. import house_systems as H
from .. import dasa_systems as JD
from .. import natal_chart as N
from .. import sign_strength as SS
from ..shadbala import NATURAL_RELATIONS_9, compound_relationships
from .catalogue import (  # noqa: F401
    ASCETIC,
    BASIS,
    BASIS_NAMES,
    BENEFICS,
    CATALOGUE,
    CO_LORDS,
    DEBIL,
    DHANA_5_11,
    DHANA_LAGNA,
    EXALT,
    GIVER_CODES,
    GROUPS,
    LORDS,
    MALEFICS,
    MAX_YOGAS,
    MOOLA,
    NAABHASA_GIVERS,
    OCCUPANCY,
    YOGA_SOURCES,
)
from .engine import (  # noqa: F401
    _Yogas,
    _lagna_degree,
    graha_drishti,
    chart_yogas,
    owns,
    rasi_drishti,
)
