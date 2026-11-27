"""
core_logic/natal_chart/
=======================
Modularized Calculation Engine for Natal Chart, Vargas (D1-D60), Special Lagnas,
Arudha Padas, Chara Karakas, and Upagrahas.

Sources (docs/SOURCES.md sections 2-5): signs, dignities and relationships BPHS 3.49-58 and 4; vargas BPHS 6
and PVR 6.2; special lagnas BPHS 5; arudhas BPHS 29; chara karakas BPHS 32; Mrityu and Pushkara bhagas PD 13.10-11
and JP 1.58; the "malicious divisions" (22nd drekkana, 64th navamsa) PM 8.61 and 9.4.
"""
# The module was split into these parts; every name is re-exported from the part holding its final binding.
from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple
from .signs import (  # noqa: F401
    DEBILITATION,
    EXALTATION,
    MOOLATRIKONA,
    NAKSHATRA_LORDS,
    NAKSHATRA_NAMES,
    OWN_SIGNS,
    RASI_LORDS,
    RASI_NAMES_EN,
    RASI_NAMES_SA,
    deg_to_dms,
    get_graha_dignity,
    get_house_of_sign,
    get_nakshatra_info,
    get_rasi_info,
    norm360,
)
from .vargas import (  # noqa: F401
    compute_all_vargas,
    compute_varga_d1,
    compute_varga_d10,
    compute_varga_d108,
    compute_varga_d11,
    compute_varga_d12,
    compute_varga_d144,
    compute_varga_d16,
    compute_varga_d2,
    compute_varga_d20,
    compute_varga_d24,
    compute_varga_d27,
    compute_varga_d3,
    compute_varga_d30,
    compute_varga_d4,
    compute_varga_d40,
    compute_varga_d45,
    compute_varga_d5,
    compute_varga_d6,
    compute_varga_d60,
    compute_varga_d7,
    compute_varga_d8,
    compute_varga_d81,
    compute_varga_d9,
)
from .arudhas import (  # noqa: F401
    GRAHA_OWNED_SIGNS,
    compute_all_graha_arudhas,
    compute_arudha_pada,
    compute_graha_arudha,
)
from .karakas import (  # noqa: F401
    CLASSICAL_COMBUSTION,
    compute_chara_karakas,
    is_combust,
    chara_karaka_slots,
    is_combust_by_orbs,
    planetary_war,
)
from .lagnas import (  # noqa: F401
    compute_bhava_lagna,
    compute_ghati_lagna,
    compute_hora_lagna,
)
from .bhagas import (  # noqa: F401
    MKS_HOUSES,
    MRITYU_BHAGA_MAANDI,
    MRITYU_BHAGA_PARASARA,
    MRITYU_BHAGA_SARAVALI,
    PUSHKARA_BHAGA_SCHEME1,
    PUSHKARA_BHAGA_SCHEME2,
    UMA_SHAMBHU_SIGN_MAP,
    _MB_ROWS,
    compute_22nd_drekkana,
    compute_64th_navamsha,
    compute_all_malicious_divisions,
    compute_drekkana,
    detect_marana_karaka_sthana,
    evaluate_mrityu_bhaga,
    evaluate_pushkara_bhaga,
    get_mrityu_bhaga_degree,
    get_pushkara_bhaga_degree,
    is_in_pushkaramsha,
    mrityu_bhaga_distance,
    pushkara_position,
)
