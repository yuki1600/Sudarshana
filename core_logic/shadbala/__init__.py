"""
core_logic/shadbala/
====================
Modularized Calculation Engine for Shadbala (Six-Fold Planetary Strengths),
Bhava Bala, and Ishta/Kashta Phala.

Sources (docs/SOURCES.md section 10): Shadbala and Bhava Bala BPHS 27; Ishta and Kashta BPHS 28.2-6; Vimsopaka
BPHS 7.17-27; Vaiseshikamsa BPHS 6.42-53; the required strength B. V. Raman, Graha and Bhava Balas section 122
(BPHS 27.32-33 in SHADBALA_REQUIREMENTS).
"""
# The module was split into these parts; every name is re-exported from the part holding its final binding.
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Any
from .. import sign_strength as _SS
from ..utils import norm360
from ..natal_chart import RASI_LORDS, EXALTATION, DEBILITATION, OWN_SIGNS, compute_all_vargas, get_graha_dignity, is_combust
from ..aspects_friendships import get_natural_relationship, compute_tatkalika_relationship, compute_parasara_drik_virupas
from .common import (  # noqa: F401
    DEEP_DEBILITATION_DEGS,
    DIG_BALA_ZERO_OFFSETS,
    NAISARGIKA_BALA,
    PLANETS,
    SHADBALA_REQUIREMENTS,
    SIGN_RULERS,
)
from .components import (  # noqa: F401
    NATURAL_BENEFICS,
    compute_ayana_bala,
    compute_cheshta_bala,
    compute_dig_bala,
    compute_drekkana_bala,
    compute_drik_bala,
    compute_full_shadbala,
    compute_graha_yuddha_bala,
    compute_ishta_kashta_parasara,
    compute_kendradi_bala,
    compute_nathonnatha_bala,
    compute_ojayugmarasyamsa_bala,
    compute_paksha_bala,
    compute_saptavargaja_bala,
    compute_temporal_lords_bala,
    compute_tribhaga_bala,
    compute_uchcha_bala,
)
from .bhava import (  # noqa: F401
    SIGN_OPTIMAL_BHAVA,
    compute_bhava_bala,
    generate_bhava_bala_ascii_graph,
    generate_bhava_bala_graph_svg,
)
from .vimsopaka import (  # noqa: F401
    DIGNITY_POINTS,
    VAISESHIKAMSA_DASA_NAMES,
    VAISESHIKAMSA_SHAD_NAMES,
    VAISESHIKAMSA_SHODASA_NAMES,
    VIMSOPAKA_SCHEMES,
    compute_vaiseshikamsa,
    compute_vimsopaka_bala,
)
from .engine import (  # noqa: F401
    AmsaBala,
    NATURAL_RELATIONS_9,
    VARGA_ORDER,
    _BAD_SAYANADI,
    _AYANA_SIGN,
    _CHESHTA,
    _DEBILITATION_POINT,
    _DIG_OFFSET,
    _KRANTI_CUM,
    _KRANTI_DIFF,
    _MT_RANGE,
    _NAISARGIKA,
    _NATURAL,
    _SEVEN_PLANETS,
    _REQUIRED_RUPAS,
    _SAPTAVARGAJA,
    _SIGN_LORD_INDEX,
    _SPECIAL_ASPECTS,
    _LORD_POINT,
    _MOOLATRIKONA_9,
    _MT_BPHS,
    _NINE,
    _VAISESHIKAMSA_GROUPS,
    _VIMSOPAKA_GROUPS,
    _VIMSOPAKA_POINTS,
    _amsa_context,
    _defeated,
    _fold180,
    _jh_days_since_1900,
    _swarudha_good,
    aspect_value,
    compound_relationships,
    rashmis_ishta_kashta,
    shadbala_and_bhava_bala,
    vaiseshikamsa_counts,
    vimsopaka_balas,
    set_moolatrikona_bphs,
)
