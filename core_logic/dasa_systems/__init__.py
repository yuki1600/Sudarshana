"""
core_logic/dasa_systems/
=======================
The 49 dasa builders (sources of each: docs/SOURCES.md section 9; BPHS 46 defines most of them), with the
date engine ``chart.periods``:

* a builder fills the lords, their years, a balance and two flags;
* with the balance flag the first period starts ``(1 - balance) * years[0]`` before birth, otherwise at birth;
* antardasas are either equal (``n`` parts) or proportional to the lords' years;
* years become dates through the dasa year definition (default: true sidereal solar year,
  ``ephemeris.dasa_year_mapper``).

Lords are point indices (1 Sun .. 9 Ketu), signs (0 Aries .. 11 Pisces) or nakshatras (0 Ashwini .. 26),
as the ``kind`` of each dasa says.
"""
# The module was split into these parts; every name is re-exported from the part holding its final binding.
import copy
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple
from .. import natal_chart as N
from .. import sign_strength as S
from ..utils import norm360
from .chart import (  # noqa: F401
    JChart,
    NAK,
    NAK28_START,
    PLANET_ABBR,
    SIGN_ABBR,
    VARGAS,
    VARGA_NUMBER,
    _md,
    periods,
)
from .nakshatra import (  # noqa: F401
    DASA_SEEDS,
    GROUP_DASAS,
    PAST_TABLE_STARTS,
    NAKSHATRA_DASAS,
    SEED_SHIFT,
    TITHI_LORD,
    VIMSOTTARI,
    YOGA_LORD,
    _by_lord,
    _conditional,
    _cycle,
    _elongation,
    _forward_subs,
    _progressed_lord,
    _seed,
    dasa_seed,
    group_dasa,
    karana_chaturaseeti_dasa,
    nak_ad_position,
    nakshatra_dasa,
    saptarshi_dasa,
    tithi_ashtottari_dasa,
    tithi_yogini_dasa,
    vimsottari_dasa,
    yoga_vimsottari_dasa,
)
from .rasi import (  # noqa: F401
    AD_STEPS,
    KENDRA_ORDER,
    NARAYANA_STEPS,
    NAVAMSA_EVEN,
    PARYAYA_STEPS,
    RANGACHARYA_STEPS,
    _co_lord,
    _direction,
    _forward_from,
    _from_lord_of_stronger,
    _kaala_unit,
    _kendradi,
    _lord,
    _narayana_like,
    _narayana_order,
    _narayana_years,
    _narayana_years_alt,
    _steps_sub,
    ak_kendradi_rasi_dasa,
    brahma_dasa,
    brahma_planet,
    chakra_dasa,
    chara_knrao_dasa,
    chara_parasara_dasa,
    chara_rangacharya_dasa,
    drig_dasa,
    kaala_dasa,
    lagna_kendradi_rasi_dasa,
    lagnamsaka_dasa,
    mandooka_d11_dasa,
    mandooka_knrao_dasa,
    narayana_dasa,
    navamsa_dasa,
    niryaana_shoola_dasa,
    padanaathaamsa_dasa,
    paryaya_dasa,
    patyayini_dasa,
    rasi_bhukta_vimsottari_dasa,
    shoola_dasa,
    sthira_dasa,
    sudasa,
    trikona_dasa,
    varnada_dasa,
    yogardha_dasa,
)
from .graha import (  # noqa: F401
    KARAKA_ABBR,
    MOOLATRIKONA_DASA,
    NAISARGIKA,
    OWN_SIGNS,
    VIM_YEARS,
    _ak_graha_years,
    _count_to,
    _graha_order,
    _moola_years,
    ak_kendradi_graha_dasa,
    buddhi_gati_dasa,
    karaka_dasa,
    karakas,
    moola_dasa,
    naisargika_dasa,
    sudarsana_chakra_dasa,
    tara_dasa,
)
from .kalachakra import (  # noqa: F401
    KALACHAKRA_SIGNS,
    KALACHAKRA_YEARS,
    PADA,
    _KC_A,
    _KC_B,
    _KC_C,
    _KC_D,
    _kc_table_row,
    _kc_wrap,
    kalachakra_dasa,
    kalachakra_pada,
    kalachakra_row,
    kalachakra_rule,
    sudarsana_rule,
)
from .events import (  # noqa: F401
    EVENT_CYCLE,
    EVENT_YEARS,
    TAJAKA_MUNTHA,
    TAJAKA_NATAL,
    TAJAKA_POINT,
    _builder_key,
    event_dasa,
    event_year_definition,
    event_years,
    fitted_to_span,
    locate_event,
    nakshatra_progression_arc,
    sub_periods,
    sum_of_longitudes,
    tajaka_dasa,
    without_sesham,
    years_in_span,
)
