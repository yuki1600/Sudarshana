"""
core_logic/compatibility/
=========================
Horoscope Matching & Marriage Compatibility Engine.
Sources (docs/SOURCES.md section 16): the eight kutas and their points (1 .. 8, of 36) MC, Vivaha prakarana;
the kutas one by one PM 21 (rasi 4-11, vasya 8 and 17-18, the rasi lords 19-20, dina 21-24, mahendra 25,
stree deergha 26, gana 27, varna 28-29, yoni 30-42, rajju 43-44, vedha 45-46, nadi 50); Kuja dosha as commonly
kept, no verse checked.

Features:
1. Ashta Kuta (8-Factor Compatibility, Total 36 Gunas):
   - Varna Kuta (1 point): Spiritual hierarchy and spiritual compatibility
   - Vashya Kuta (2 points): Mutual magnetic attraction and control
   - Tara Kuta / Dina Kuta (3 points): Destiny, health, and mutual longevity
   - Yoni Kuta (4 points): Physical, biological, and intimate compatibility (14 yonis)
   - Graha Maitri Kuta (5 points): Psychological harmony and friendship of Moon sign lords
   - Gana Kuta (6 points): Temperament and behavior (Deva, Manushya, Rakshasa)
   - Bhakoota Kuta (7 points): Emotional bonding, progeny, and family welfare (2/12, 6/8, 9/5 doshas)
   - Nadi Kuta (8 points): Genetic and physiological compatibility (Adi, Madhya, Antya)
2. Ancillary Kootas:
   - Mahendra Kuta: Lineage and prosperity
   - Stree Deergha: Distance from bride to groom
   - Rajju Kuta: 5 bodily cords (Shiro, Kantha, Nabhi, Kati, Pada)
   - Vedha Kuta: Mutual piercing / affliction nakshatra pairs
3. Kuja Dosha (Manglik Dosha) Engine:
   - Evaluated from Lagna, Moon, and Venus in houses 1, 2, 4, 7, 8, 12
   - Complete classical cancellations (exaltation, own sign, Jupiter aspect, sign exemptions)

"""
# The module was split into these parts; every name is re-exported from the part holding its final binding.
from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Any
from ..utils import norm360
from ..natal_chart import NAKSHATRA_NAMES, RASI_NAMES_EN, RASI_LORDS, EXALTATION, DEBILITATION, get_graha_dignity
from ..aspects_friendships import get_natural_relationship, compute_tatkalika_relationship, compute_panchadha_maitri
from .tables import (  # noqa: F401
    GANA_NAMES,
    MAITRI_LORDS,
    MAITRI_POINTS,
    NADI_NAMES,
    NAKSHATRA_GANA,
    NAKSHATRA_NADI,
    NAKSHATRA_RAJJU,
    NAKSHATRA_YONI,
    RAJJU_NAMES,
    SWORN_YONI_ENEMIES,
    VARNA_BY_RASI,
    VARNA_NAMES,
    VASHYA_BY_RASI,
    VASHYA_MATRIX,
    VASHYA_NAMES,
    VEDHA_PAIRS,
    YONI_NAMES,
    YONI_POINTS,
    _ordinal,
    vashya_class,
)
from .kutas import (  # noqa: F401
    compute_bhakoota_kuta,
    compute_gana_kuta,
    compute_graha_maitri_kuta,
    compute_nadi_kuta,
    compute_tara_kuta,
    compute_varna_kuta,
    compute_vashya_kuta,
    compute_yoni_kuta,
)
from .ancillary import (  # noqa: F401
    DASHA_LEVELS,
    VASYA_SIGNS,
    compute_ancillary_kootas,
    compute_dashakoota,
)
from .kuja import (  # noqa: F401
    evaluate_kuja_dosha,
)
from .matching import (  # noqa: F401
    evaluate_horoscope_matching,
)
from .pada_points import (  # noqa: F401
    PADA_MATCH_PART,
    PADA_MATCH_POINTS,
    pada_match_level,
    pada_match_points,
    match_from_padas,
    match_matrix,
    match_parts,
    moon_longitude_of,
)
from .compare import (  # noqa: F401
    _BHAVAS,
    _BODIES,
    _MALEFICS,
    _MARRIAGE_HOUSES,
    _SEVEN,
    _SIGN_NAMES,
    _apart,
    _house,
    _place_class,
    _sign,
    _sign_dignity,
    _who,
    compare_charts,
)
from .factors import (  # noqa: F401
    marriage_dasas,
    marriage_lords,
    match_factors,
)
