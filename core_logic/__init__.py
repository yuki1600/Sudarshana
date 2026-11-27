"""
core_logic
==========
Core Astrological and Astronomical Calculation Engines for Sudarshana Revamped.
The classical source of every calculation and setting: docs/SOURCES.md.

Subsystems:
- house_systems: Coordinate transformations, house cusps, sunrise/sunset, sandhyas.
- natal_chart: Planetary degrees, dignities, D1-D60 vargas, karakas, special lagnas, arudhas,
               Mrityu Bhagas, Pushkara Bhagas, Pushkaramshas, 22nd Drekkana (5 variants), 64th Navamsha.
- aspects_friendships: Parasara Graha Drishti, Aspect Virupas & percentages, Jaimini Rasi Drishti,
                       Naisargika, Tatkalika, and Panchadha Maitri compound relationships, Sambandha.
- mundane: Solar New Year (Mesha Sankranti), Lunar New Year (Chaitra Shukla Pratipat),
           Solar Months (12 Sankrantis), Fortnight (Paksha) charts, Conjunctions & Oppositions,
           Stationary & Retrograde motion events.
- dashas: Vimshottari, Kalachakra, Narayana, Yogini dasa progression engines.
- ashtakavarga: Prastara, Bhinna, Samudaya, Trikona/Ekadhipatya reductions, Shodhya Pinda.
- shadbala: Six-fold planetary strength (Sthana, Dig, Kala, Cheshta, Naisargika, Drik),
            Rashmis (Ray Strengths), Parasara Ishta/Kashta Phala, Bhava Bala, Vimsopaka Bala.
- tajika: Varshaphal, solar return ingress, Muntha, 16 Tajika Yogas, Sahams, Harsha Bala, Panchavargiya Bala.
- transits: Gochara transits, Vedha obstructions, Sade Sati, Kota Chakra.
- panchanga: Five Limbs (Tithi, Vaara, Nakshatra, Yoga, Karana), Rahu Kalam, Yama Ghantam, Abhijit Muhurta.
- laghu_parasari: Functional Benefics/Malefics/Yogakarakas for 12 Lagnas, Kendra-Trikona Raja Yogas, Marakas.

Submodules that need pyswisseph (import them explicitly):
- ephemeris: Swiss Ephemeris positions, houses, sunrise, special lagnas/upagrahas, eclipses, build_chart.
- workflows: transit/sign-change/lagna-change searches, transit calendar, Tajaka and Tithi Pravesha
             moments, Ardra pravesha, angular returns, entry charts, matching from charts.
"""

from .house_systems import (
    compute_equal_houses,
    compute_whole_sign_houses,
    compute_sripathi_houses,
    compute_placidus_houses,
    compute_koch_houses,
    compute_campanus_houses,
    compute_regiomontanus_houses,
    compute_house_cusps,
    compute_dinamana_ratrimana,
    compute_ishta_kala,
    compute_trikuta_sandhyas,
    AYANAMSA_MODES,
    HOUSE_SYSTEMS
)

from .natal_chart import (
    get_rasi_info,
    get_nakshatra_info,
    get_graha_dignity,
    compute_all_vargas,
    compute_arudha_pada,
    compute_chara_karakas,
    compute_hora_lagna,
    compute_ghati_lagna,
    compute_bhava_lagna,
    get_mrityu_bhaga_degree,
    evaluate_mrityu_bhaga,
    get_pushkara_bhaga_degree,
    is_in_pushkaramsha,
    evaluate_pushkara_bhaga,
    compute_drekkana,
    compute_22nd_drekkana,
    compute_64th_navamsha,
    compute_all_malicious_divisions,
    compute_graha_arudha,
    compute_all_graha_arudhas,
    compute_varga_d5,
    compute_varga_d6,
    compute_varga_d8,
    compute_varga_d11,
    compute_varga_d40,
    compute_varga_d45,
    compute_varga_d108,
    compute_varga_d144,
    GRAHA_OWNED_SIGNS,
    MRITYU_BHAGA_PARASARA,
    MRITYU_BHAGA_SARAVALI,
    PUSHKARA_BHAGA_SCHEME1,
    PUSHKARA_BHAGA_SCHEME2,
    RASI_NAMES_EN,
    RASI_NAMES_SA,
    RASI_LORDS
)


from .aspects_friendships import (
    get_natural_relationship,
    compute_tatkalika_relationship,
    compute_panchadha_maitri,
    compute_all_planetary_friendships,
    compute_parasara_drik_virupas,
    compute_aspect_details,
    compute_rasi_drishti,
    evaluate_planetary_sambandha,
    NAISARGIKA_MATRIX
)

from .mundane import (
    solve_longitude_crossing,
    compute_solar_new_year,
    compute_lunar_new_year,
    compute_solar_month_ingress,
    compute_fortnight_ingress,
    find_planetary_aspect_event,
    find_planetary_station_event,
    compute_year_lords
)

from .dashas import (
    chara_sign_years,
    compute_vimshottari_balance,
    compute_vimshottari_tree,
    get_active_vimshottari_subperiod,
    locate_dasa_period,
    shift_dasa_timeline,
    compare_vimshottari_seeds,
    compute_yogini_dasa,
    compute_narayana_sign_order,
    compute_narayana_dasa_years,
    compute_narayana_dasa_timeline,
    compute_chara_dasa,
    YEAR_STANDARDS,
    DASA_START_SEEDS
)


from .ashtakavarga import (
    compute_prastara_ashtakavarga,
    compute_bav_and_sav,
    trikona_sodhana,
    ekadhipatya_sodhana,
    compute_shodhya_pinda,
    compute_ashtakavarga_ayurdaya,
    compute_shodhya_pinda_sensitive_points,
    run_full_ashtakavarga_pipeline
)

from .shadbala import (
    compute_uchcha_bala,
    compute_kendradi_bala,
    compute_dig_bala,
    compute_nathonnatha_bala,
    compute_paksha_bala,
    compute_ojayugmarasyamsa_bala,
    compute_drekkana_bala,
    compute_saptavargaja_bala,
    compute_tribhaga_bala,
    compute_temporal_lords_bala,
    compute_ayana_bala,
    compute_graha_yuddha_bala,
    compute_cheshta_bala,
    compute_drik_bala,
    compute_full_shadbala,
    compute_ishta_kashta_parasara,
    compute_bhava_bala,
    generate_bhava_bala_ascii_graph,
    generate_bhava_bala_graph_svg,
    compute_vimsopaka_bala,
    compute_vaiseshikamsa,
    VIMSOPAKA_SCHEMES
)

from .utils import (
    norm360,
    deg_to_dms,
    get_house_of_sign,
    angular_distance
)

from .tajika import (
    compute_muntha,
    check_ithasala_ishrafa_yoga,
    check_tajika_aspect,
    detect_16_tajika_yogas,
    evaluate_all_tajika_yogas,
    compute_sahams,
    evaluate_varsheshwara_candidates
)

from .transits import (
    evaluate_gochara_transit,
    compute_murthi_nirnaya,
    check_sade_sati,
    compute_kota_chakra_placement
)

from .special_lagnas_upagrahas import (
    compute_sree_lagna,
    compute_indu_lagna,
    compute_bhrigu_bindu,
    compute_kunda,
    compute_pranapada_lagna,
    compute_vighati_lagna,
    compute_varnada_lagna,
    compute_aprakash_grahas,
    compute_kalavela_time,
    kalavela_part,
    kalavela_offset_fraction,
    KALAVELA_LORDS,
    KALAVELA_DEFAULT_POINT,
    compute_all_special_lagnas_and_upagrahas
)

from .avasthas import (
    compute_baalaadi_avastha,
    compute_jagrataadi_avastha,
    compute_deeptaadi_avastha,
    compute_lajjitadi_avastha,
    compute_comprehensive_planetary_avasthas
)

from .kakshyas import (
    get_kakshya_info,
    evaluate_kakshya_transit,
    evaluate_all_transit_kakshyas,
    KAKSHYA_LORDS
)

from .sahams_library import (
    saham_coverage,
    SAHAMA_NAMES,
    compute_single_saham,
    compute_all_50_sahams,
    SAHAM_DEFINITIONS
)

from .tithi_pravesha import (
    get_tithi_info,
    solve_tithi_pravesha_chart
)

from .chakras import (
    compute_sarvatobhadra_vedhas,
    generate_sarvatobhadra_grid_data,
    render_sarvatobhadra_ascii_grid,
    compute_kota_chakra_structure,
    compute_sudarshana_chakra,
    compute_kalachakra_directional_wheel,
    compute_surya_kalanal_chakra,
    compute_chandra_kalanal_chakra,
    compute_kurma_chakra,
    compute_tripataki_chakra,
    compute_shoola_chakra,
    KURMA_CHAKRA_REGIONS,
    SBC_28_NAKSHATRAS
)


from . import dasa_systems, sign_strength

from .jhd_io import (
    parse_jhd_file,
    parse_jhd_string,
    serialize_to_jhd,
    to_birth_data
)

from .ephemeris import (
    BirthData,
    EphemerisConfig,
    EphemerisUnavailable,
    AYANAMSAS,
    HOUSE_SYSTEM_CODES,
    ayanamsa_value,
    julian_day_ut,
    planet_positions,
    house_cusps,
    sunrise_sunset,
    build_chart
)

from .panchanga import (
    compute_tithi,
    compute_vaara,
    compute_nakshatra,
    compute_yoga,
    compute_karana,
    compute_durmuhurta_timings,
    compute_gowri_panchangam,
    compute_muhurta_timings,
    compute_full_panchanga
)

from .laghu_parasari import (
    evaluate_functional_nature_for_lagna,
    find_laghu_parasari_raja_yogas,
    evaluate_maraka_grahas
)

from .miscellany import (
    compute_planetary_return,
    compute_angular_separation_return,
    compute_secondary_progression,
    compute_symbolic_manu_progression,
    compute_sudarshana_progression,
    compute_prashna_sphutas,
    evaluate_karya_siddhi,
    compute_tamboola_prashna,
    compute_choghadiya_muhurta
)

from .compatibility import (
    compute_varna_kuta,
    compute_vashya_kuta,
    compute_tara_kuta,
    compute_yoni_kuta,
    compute_graha_maitri_kuta,
    compute_gana_kuta,
    compute_bhakoota_kuta,
    compute_nadi_kuta,
    compute_ancillary_kootas,
    evaluate_kuja_dosha,
    evaluate_horoscope_matching,
    VARNA_NAMES,
    VASHYA_NAMES,
    YONI_NAMES,
    GANA_NAMES,
    NADI_NAMES,
    RAJJU_NAMES
)

from .kp_astrology import (
    get_kp_sub_lords,
    get_kp_sub_levels,
    compute_cuspal_sub_lords,
    compute_kp_significators,
    get_kp_ruling_planets,
    resolve_kp_horary_number,
    KP_249_TABLE
)

from .ayurdaya import (
    Natal,
    arc_years,
    navamsa_years,
    spans,
    three_pairs,
    placement,
    sun_relation,
    marakas,
    maraka_stars,
    ashtakavarga_years,
    PINDA_YEARS,
    NISARGA_YEARS,
    DEEP_EXALTATION
)

# ---------------------------------------------------------------------------
# Tier-9 Forensic Audit Additions — new functions discovered in this pass
# ---------------------------------------------------------------------------

from .miscellany import (
    compute_bhrigu_pada_progression,
    compute_kalachakra_progression,
)

from .tithi_pravesha import (
    solve_yoga_pravesha_chart,
    solve_nakshatra_pravesha_chart,
    compute_karana_chaturaseeti_dasa,
    KARANA_LORDS,
)

from .natal_chart import (
    detect_marana_karaka_sthana,
    MKS_HOUSES,
)

from .transits import (
    compute_latta_afflictions,
    compute_anga_graha_transits,
    LATTA_RULES,
    ANGA_REGIONS,
)

from .panchanga import (
    compute_bhava_tithis,
    BHAVA_TITHI_NAMES,
)

from .chakras import (
    compute_lagna_navatara_and_special_nakshatras,
    NAVATARA_NAMES,
)

from .ashtakavarga import (
    compute_eight_contributor_sav,
    compute_bhava_driven_sav,
)

__version__ = "4.1.0"




