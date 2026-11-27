# Graph Report - Sudarshana  (2026-11-27)

## Corpus Check
- 276 files · ~423,243 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: .css 12, (none) 5, .example 1)

## Summary
- 5563 nodes · 15051 edges · 177 communities (149 shown, 28 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 436 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cb25c84e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- factors.py
- norm360
- service.py
- Panels.tsx
- useChart
- Longevity.tsx
- rasi.py
- windows.py
- compatibility/__init__.py
- Calculations tab UI
- Natal
- tajika.py
- core_logic/chakras.py
- shadbala/__init__.py
- TopBar.tsx
- time_search.py
- ChartGrid.tsx
- mundane_rodden.py
- pinda_transits
- api.ts
- Client-side calc math
- server/tables.py
- key_info.py
- MatchingKutas.tsx
- core_logic/__init__.py
- Textbook dasha engines
- math
- finance.py
- Ayurdaya tests
- app/__init__.py
- lib.rs
- panchanga.py
- solve_longitude_crossing
- store.ts
- Matching.tsx
- modes.py
- Chakras.tsx
- varga_charts.py
- Remedies.tsx
- Muhurta.tsx
- Lore.tsx
- dasa_systems/__init__.py
- traditions/src/lib.rs
- places.py
- strengths.py
- Ephemeris workflows
- astrocartography.py
- sign_strength.py
- useChart
- avasthas.py
- _Yogas
- Server muhurta
- MatchingCompare.tsx
- _db
- Traditions.tsx
- parse_jhd_string
- Server longevity
- report.py
- mundane_rodden.py
- test_pending_options.py
- Astrocartography.tsx
- traditions.py
- App.tsx
- Conditional dasa tests
- periods
- place
- Auth tests
- muhurtaMath.test.ts
- test_security.py
- mundane_data.py
- Predictions.tsx
- Mundane.tsx
- Server miscellany
- get
- Calendar (timeline) UI
- _chart
- translate.ts
- ayurdaya.py
- oauth_callback
- insights.py
- events.py
- build_places_db.py
- muhurtaMath.ts
- zones.ts
- basics.py
- auth.py
- Finance UI
- ChartPane.tsx
- BirthData
- test_astrocartography.py
- lore.py
- core_logic/jamakkol.py
- kp_astrology.py
- charts.py
- karakas.py
- language.ts
- Festival calendars
- Sudarshana chakra intro
- Panels.tsx
- Ephemeris addition tests
- index_members
- Wheels
- Astrocartography tests
- _arc_span
- Sky
- house_systems.py
- kept.ts
- wheelGeometry.ts
- traditionsMath.ts
- MuhurtaFind.tsx
- CI workflow
- TestOAuth
- server/transits.py
- .sees_house
- chart_routes.py
- Tier 8 audit tests
- names.ts
- _forward_from
- JChart
- marakas
- Tier 6 tests
- build_world_map.py
- Festival tests
- civil_day_panchanga
- chakraTables.ts
- mundaneMath.ts
- place
- TestTier7Engines
- ref_node_assert
- Records
- main.tsx
- amsayu
- .touched_by
- PyResult
- tithi_pravesha
- mundane_finance.py
- longitude_sums.py
- Vimshottari tests
- Hosting script
- chinese_calendar.py
- FindMuhurta
- day
- file_routes.py
- Places
- cls
- BodyLimit
- test_traditions.py
- mundaneMath.test.ts
- special_search
- calc
- yearOf
- TestJplKernel
- deltat.py
- _bisect
- Bala
- rodden.py
- _gzipped
- remedies.py
- match_charts
- Detail
- prasna_lagna
- Package metadata
- retrograde_period
- Sudarsana
- Filters
- Database
- special_point
- dasa_routes.py
- traditions
- refresh.sh
- traditions
- jpl-kernel
- jpl-kernel
- server/chakras.py

## God Nodes (most connected - your core abstractions)
1. `useChart` - 197 edges
2. `norm360()` - 166 edges
3. `useKept()` - 103 edges
4. `Loaded()` - 98 edges
5. `to_jsonable()` - 66 edges
6. `supOrd()` - 66 edges
7. `JChart` - 65 edges
8. `ChartReq` - 61 edges
9. `_raw()` - 61 edges
10. `_key()` - 58 edges

## Surprising Connections (you probably didn't know these)
- `edge()` --calls--> `inside()`  [INFERRED]
  server/strengths.py → core_logic/tests/test_astrocartography.py
- `at()` --calls--> `bhavas_at()`  [INFERRED]
  core_logic/astrocartography.py → server/astrocarto.py
- `aspect_evaluation()` --indirect_call--> `label()`  [INFERRED]
  server/tables.py → core_logic/longitude_sums.py
- `edge()` --indirect_call--> `inside()`  [INFERRED]
  server/transits.py → core_logic/tests/test_astrocartography.py
- `find()` --indirect_call--> `parts()`  [INFERRED]
  server/modes.py → tools/build_world_map.py

## Import Cycles
- 3-file cycle: `web/src/Chakras.tsx -> web/src/Modes.tsx -> web/src/Starlight.tsx -> web/src/Chakras.tsx`
- 3-file cycle: `web/src/Modes.tsx -> web/src/Starlight.tsx -> web/src/StarSettings.tsx -> web/src/Modes.tsx`
- 3-file cycle: `core_logic/__init__.py -> core_logic/ayurdaya.py -> core_logic/yoga_engine/__init__.py -> core_logic/__init__.py`
- 3-file cycle: `core_logic/__init__.py -> core_logic/tithi_pravesha.py -> core_logic/time_search.py -> core_logic/__init__.py`
- 3-file cycle: `core_logic/__init__.py -> core_logic/ayurdaya.py -> core_logic/shadbala/__init__.py -> core_logic/__init__.py`
- 4-file cycle: `web/src/Modes.tsx -> web/src/Starlight.tsx -> web/src/StarSettings.tsx -> web/src/Settings.tsx -> web/src/Modes.tsx`
- 4-file cycle: `web/src/Modes.tsx -> web/src/Starlight.tsx -> web/src/Windows.tsx -> web/src/Settings.tsx -> web/src/Modes.tsx`
- 4-file cycle: `web/src/Modes.tsx -> web/src/Panels.tsx -> web/src/Windows.tsx -> web/src/Settings.tsx -> web/src/Modes.tsx`
- 4-file cycle: `core_logic/__init__.py -> core_logic/compatibility/__init__.py -> core_logic/compatibility/kuja.py -> core_logic/shadbala/engine.py -> core_logic/__init__.py`
- 4-file cycle: `core_logic/__init__.py -> core_logic/ayurdaya.py -> core_logic/shadbala/__init__.py -> core_logic/shadbala/engine.py -> core_logic/__init__.py`
- 4-file cycle: `core_logic/__init__.py -> core_logic/ayurdaya.py -> core_logic/yoga_engine/__init__.py -> core_logic/dasa_systems/__init__.py -> core_logic/__init__.py`
- 4-file cycle: `core_logic/__init__.py -> core_logic/ayurdaya.py -> core_logic/yoga_engine/__init__.py -> core_logic/shadbala/__init__.py -> core_logic/__init__.py`
- 4-file cycle: `core_logic/__init__.py -> core_logic/ayurdaya.py -> core_logic/yoga_engine/__init__.py -> core_logic/yoga_engine/catalogue.py -> core_logic/__init__.py`
- 4-file cycle: `core_logic/__init__.py -> core_logic/ayurdaya.py -> core_logic/yoga_engine/__init__.py -> core_logic/yoga_engine/engine.py -> core_logic/__init__.py`
- 4-file cycle: `core_logic/__init__.py -> core_logic/ayurdaya.py -> core_logic/key_info.py -> core_logic/dasa_systems/__init__.py -> core_logic/__init__.py`
- 5-file cycle: `web/src/Account.tsx -> web/src/Modes.tsx -> web/src/Panels.tsx -> web/src/Windows.tsx -> web/src/Settings.tsx -> web/src/Account.tsx`
- 5-file cycle: `web/src/Account.tsx -> web/src/Modes.tsx -> web/src/Starlight.tsx -> web/src/StarSettings.tsx -> web/src/Settings.tsx -> web/src/Account.tsx`
- 5-file cycle: `web/src/Account.tsx -> web/src/Modes.tsx -> web/src/Starlight.tsx -> web/src/Windows.tsx -> web/src/Settings.tsx -> web/src/Account.tsx`
- 5-file cycle: `web/src/Chakras.tsx -> web/src/Windows.tsx -> web/src/Settings.tsx -> web/src/Modes.tsx -> web/src/Starlight.tsx -> web/src/Chakras.tsx`
- 5-file cycle: `web/src/Modes.tsx -> web/src/Starlight.tsx -> web/src/Panels.tsx -> web/src/Windows.tsx -> web/src/Settings.tsx -> web/src/Modes.tsx`

## Communities (177 total, 28 thin omitted)

### Community 0 - "factors.py"
Cohesion: 0.08
Nodes (43): _apart(), mars(), relation(), _house(), _sign(), _sign_dignity(), ab(), alone() (+35 more)

### Community 1 - "norm360"
Cohesion: 0.04
Nodes (49): compute_aspect_details(), evaluate_planetary_sambandha(), compute_all_graha_arudhas(), compute_arudha_pada(), compute_graha_arudha(), compute_22nd_drekkana(), compute_64th_navamsha(), compute_all_malicious_divisions() (+41 more)

### Community 3 - "service.py"
Cohesion: 0.05
Nodes (89): to_jsonable(), AdjustIn, amsa(), angular_return(), ashtakavarga(), aspect_table(), astrocartography(), bars() (+81 more)

### Community 4 - "Panels.tsx"
Cohesion: 0.04
Nodes (96): DasaPeriod, Table, TransitVisit, YogaBasis, YogaListRow, YogaRow, pageScale(), Meter() (+88 more)

### Community 5 - "useChart"
Cohesion: 0.04
Nodes (125): AheadEvent, Basics, CalendarRow, CorrelationRow, DomainAhead, Jamakkol, JamakkolPoint, LoreNote (+117 more)

### Community 6 - "Longevity.tsx"
Cohesion: 0.07
Nodes (53): Ages, LgBody, LongevityData, LongevityHeadline, LongevitySection, useKept(), ageAt(), ages() (+45 more)

### Community 7 - "rasi.py"
Cohesion: 0.06
Nodes (32): ak_kendradi_rasi_dasa(), chara_knrao_dasa(), chara_parasara_dasa(), chara_rangacharya_dasa(), _co_lord(), _direction(), drig_dasa(), _from_lord_of_stronger() (+24 more)

### Community 8 - "windows.py"
Cohesion: 0.10
Nodes (10): dasa_transit(), locate(), _lord_sign(), matching(), matching_compare(), matching_detail(), matching_matrix(), period_at() (+2 more)

### Community 9 - "compatibility/__init__.py"
Cohesion: 0.04
Nodes (38): compute_all_planetary_friendships(), compute_panchadha_maitri(), compute_rasi_drishti(), compute_tatkalika_relationship(), get_natural_relationship(), compute_ancillary_kootas(), compute_dashakoota(), compare_charts() (+30 more)

### Community 10 - "Calculations tab UI"
Cohesion: 0.08
Nodes (75): ABBR, Angle(), Antardasa(), Aprakasha(), arcGap(), Argala(), Arudha(), at() (+67 more)

### Community 11 - "Natal"
Cohesion: 0.15
Nodes (6): _clean(), death_circumstances(), Natal, placement(), _reductions(), _short_kendra()

### Community 12 - "tajika.py"
Cohesion: 0.06
Nodes (21): compute_all_50_sahams(), compute_single_saham(), resolve_body_coord(), saham_coverage(), saham_longitude(), saham_longitudes(), check_ithasala_ishrafa_yoga(), check_tajika_aspect() (+13 more)

### Community 13 - "core_logic/chakras.py"
Cohesion: 0.07
Nodes (17): compute_chandra_kalanal_chakra(), compute_kalachakra_directional_wheel(), compute_kota_chakra_structure(), compute_kurma_chakra(), compute_lagna_navatara_and_special_nakshatras(), compute_sarvatobhadra_vedhas(), compute_shoola_chakra(), compute_sudarshana_chakra() (+9 more)

### Community 14 - "shadbala/__init__.py"
Cohesion: 0.04
Nodes (34): compute_parasara_drik_virupas(), compute_bhava_bala(), generate_bhava_bala_ascii_graph(), generate_bhava_bala_graph_svg(), compute_ayana_bala(), compute_cheshta_bala(), compute_dig_bala(), compute_drekkana_bala() (+26 more)

### Community 15 - "TopBar.tsx"
Cohesion: 0.08
Nodes (43): ChartFormat, Choice, SettingOption, moveTo(), reconcile(), def, OPTIONAL, starOptional() (+35 more)

### Community 16 - "time_search.py"
Cohesion: 0.14
Nodes (14): _crossing(), event_period(), fortnight(), half_cycle_period(), longitude_event(), lunar_day(), lunar_month(), lunar_year() (+6 more)

### Community 17 - "ChartGrid.tsx"
Cohesion: 0.11
Nodes (53): ChartPanel, bodyKind(), bodySizes, Box, columns(), degOf(), degText(), ems() (+45 more)

### Community 18 - "mundane_rodden.py"
Cohesion: 0.11
Nodes (16): asc_off(), born(), chart(), coord(), event(), facts(), fields(), main() (+8 more)

### Community 19 - "pinda_transits"
Cohesion: 0.23
Nodes (9): _motion(), pinda_transits(), dasa_at(), local(), text(), visit(), _samples(), _visits() (+1 more)

### Community 20 - "api.ts"
Cohesion: 0.03
Nodes (74): AmsaRow, AskResult, Astro, auth, authPost(), AvakahadaReading, BarPanel, BestDasa (+66 more)

### Community 21 - "Client-side calc math"
Cohesion: 0.06
Nodes (51): antardasas(), aprakasha(), arcYears(), arudha(), ascendant(), charaKarakas(), clockHours(), d12Sign() (+43 more)

### Community 22 - "server/tables.py"
Cohesion: 0.07
Nodes (46): _points(), ChartSpec, relationships(), vaiseshikamsa_of(), _varga_signs(), vimsopaka_of(), aspect_evaluation(), avasthas() (+38 more)

### Community 23 - "key_info.py"
Cohesion: 0.07
Nodes (23): anga_graha(), aspect_evaluation_row(), aspected_stars(), brahma_rudra_maheswara(), drekkana_labels(), latta_star(), _lord28(), lords_of_sign() (+15 more)

### Community 24 - "MatchingKutas.tsx"
Cohesion: 0.18
Nodes (16): MatchDetail, ASHTA_ABOUT, bare(), DASHA_ABOUT, GRADE_TONE, kutaHow(), kutaPair(), KutaTables() (+8 more)

### Community 25 - "core_logic/__init__.py"
Cohesion: 0.05
Nodes (30): ashtakavarga_tables(), compute_ashtakavarga_ayurdaya(), compute_bav_and_sav(), compute_bhava_driven_sav(), compute_eight_contributor_sav(), compute_prastara_ashtakavarga(), compute_shodhya_pinda(), compute_shodhya_pinda_sensitive_points() (+22 more)

### Community 26 - "Textbook dasha engines"
Cohesion: 0.09
Nodes (18): chara_sign_years(), compare_vimshottari_seeds(), compute_chara_dasa(), compute_narayana_dasa_timeline(), compute_narayana_dasa_years(), compute_narayana_sign_order(), compute_vimshottari_balance(), compute_vimshottari_tree() (+10 more)

### Community 27 - "math"
Cohesion: 0.07
Nodes (29): is_combust(), _angdist(), _ascension(), _asin(), ayanamsa(), chart(), _day_arc(), _equation_of_time() (+21 more)

### Community 28 - "finance.py"
Cohesion: 0.13
Nodes (20): ccxt_ohlc(), _combustions(), _conjunctions(), _eclipses(), events(), _ingresses(), _iso(), _ms() (+12 more)

### Community 29 - "Ayurdaya tests"
Cohesion: 0.06
Nodes (8): chart(), row(), TestMarakas, TestPlacement, TestReductions, TestRules, TestThreePairs, TestYears

### Community 30 - "app/__init__.py"
Cohesion: 0.05
Nodes (109): ChartReq, _found(), AngularReq, CalendarReq, change_timezone(), CorrelationReq, LifecycleReq, mode_angular_return() (+101 more)

### Community 31 - "lib.rs"
Cohesion: 0.08
Nodes (17): AU_KM, C, frames(), GMB, J2000, KERNEL, M3, MEAN_NODE_DIST (+9 more)

### Community 32 - "panchanga.py"
Cohesion: 0.08
Nodes (17): evaluate_maraka_grahas(), find_laghu_parasari_raja_yogas(), get_houses_owned_by_planet(), compute_bhava_tithis(), compute_durmuhurta_timings(), compute_full_panchanga(), compute_gowri_panchangam(), compute_karana() (+9 more)

### Community 33 - "solve_longitude_crossing"
Cohesion: 0.04
Nodes (37): compute_angular_separation_return(), separation(), compute_bhrigu_pada_progression(), compute_choghadiya_muhurta(), compute_kalachakra_progression(), compute_planetary_return(), compute_prashna_sphutas(), compute_secondary_progression() (+29 more)

### Community 34 - "store.ts"
Cohesion: 0.08
Nodes (42): Birth, CHART_FILES, CloudChart, DasaEvent, Meta, Recast, RoddenChart, SharedChart (+34 more)

### Community 35 - "Matching.tsx"
Cohesion: 0.05
Nodes (88): chartName(), Home, MatchArea, MatchCell, MatchMatrix, MatchPart, MatchTone, BirthDialog() (+80 more)

### Community 36 - "modes.py"
Cohesion: 0.13
Nodes (12): add_months(), _at(), entry_chart(), fit_dasa(), lifecycle(), prasna(), progression(), _sunrise() (+4 more)

### Community 37 - "Chakras.tsx"
Cohesion: 0.06
Nodes (37): ChakraOptions, ABBR27, ABBR28, ASPECT, BASE_POINTS, BENEFICS, BODY_SETS, DATED (+29 more)

### Community 38 - "varga_charts.py"
Cohesion: 0.05
Nodes (54): check_sade_sati(), compute_anga_graha_transits(), compute_latta_afflictions(), compute_murthi_nirnaya(), evaluate_gochara_transit(), _fold(), gochara_row(), gochara_vedha() (+46 more)

### Community 39 - "Remedies.tsx"
Cohesion: 0.07
Nodes (60): RemediesChartFlags, RemedyBphsEntry, RemedyVaishnavaTopic, CHAPTERS, FACTS, Graha(), Level, LEVELS (+52 more)

### Community 40 - "Muhurta.tsx"
Cohesion: 0.10
Nodes (30): FestivalCalendar, Festivals, LunarSystem, MuhurtaDay, Place, calLabel(), calTip(), iso() (+22 more)

### Community 41 - "Lore.tsx"
Cohesion: 0.06
Nodes (73): BhavaLore, BhavaReading, GrahaLore, JivaAjiva, LoreFacts, LoreLink, LoreQuote, LoreSide (+65 more)

### Community 42 - "dasa_systems/__init__.py"
Cohesion: 0.13
Nodes (17): _by_lord(), _conditional(), _cycle(), dasa_seed(), _elongation(), _forward_subs(), group_dasa(), karana_chaturaseeti_dasa() (+9 more)

### Community 43 - "traditions/src/lib.rs"
Cohesion: 0.04
Nodes (4): ALL_ASPECTS, CLASSICAL, HOUSES, month_stem()

### Community 44 - "places.py"
Cohesion: 0.13
Nodes (13): list_countries(), list_states(), search_places(), _connect(), countries(), _db_path(), _elevation_sql(), _place_dict() (+5 more)

### Community 45 - "strengths.py"
Cohesion: 0.19
Nodes (8): bar_group(), bars_of(), cusp_bala_of(), shadbala_of(), strengths(), vargas_used(), yoga_list(), yogas_of()

### Community 46 - "Ephemeris workflows"
Cohesion: 0.11
Nodes (15): angular_return(), ardra_pravesha(), chart_at_jd(), dasa_transit_correlation(), entry_chart(), find_transit(), lagna_sign_change(), lifecycle_moment() (+7 more)

### Community 47 - "astrocartography.py"
Cohesion: 0.09
Nodes (20): armc_curves(), band_areas(), bands(), crossings(), at(), edge(), ecliptic_poles(), _equatorial() (+12 more)

### Community 48 - "sign_strength.py"
Cohesion: 0.06
Nodes (19): _aspect_score(), dasa_sign_lord(), _deg(), direction_override(), graha_arudha(), longitude_bhava_arudhas(), owns_sign(), planets_in_sign() (+11 more)

### Community 49 - "useChart"
Cohesion: 0.10
Nodes (50): themeNow(), AspectTable, currentSettings(), BaseDialog(), HouseDialog(), PickDialog(), StarDialog(), division() (+42 more)

### Community 50 - "avasthas.py"
Cohesion: 0.11
Nodes (10): compute_baalaadi_avastha(), compute_comprehensive_planetary_avasthas(), compute_deeptaadi_avastha(), compute_jagrataadi_avastha(), compute_lajjitadi_avastha(), graha_avasthas(), _jh_owns(), compute_vaiseshikamsa() (+2 more)

### Community 51 - "_Yogas"
Cohesion: 0.15
Nodes (3): owns(), rasi_drishti(), _Yogas

### Community 52 - "Server muhurta"
Cohesion: 0.09
Nodes (20): _at(), chandra_house(), _combust(), day(), events(), find(), intersect(), _iso() (+12 more)

### Community 53 - "MatchingCompare.tsx"
Cohesion: 0.07
Nodes (38): MatchCompare, MatchKuja, MatchSide, natural, AGE, ALERT, AREA_COLS, AreaId (+30 more)

### Community 54 - "_db"
Cohesion: 0.13
Nodes (20): signed_in_only(), check_password(), _client(), _db(), delete_account(), delete_chart(), delete_shared(), DeleteIn (+12 more)

### Community 55 - "Traditions.tsx"
Cohesion: 0.10
Nodes (47): ABBR, BA_ZHAI, bodyLabel(), Box(), Chinese(), ChineseChart(), Count(), deg() (+39 more)

### Community 56 - "parse_jhd_string"
Cohesion: 0.11
Nodes (8): decode_hm(), encode_hm(), parse_jhd_file(), parse_jhd_string(), serialize_to_jhd(), TestHouseSystemsAgainstSwe, TestJhdIo, parse_jhd()

### Community 57 - "Server longevity"
Cohesion: 0.11
Nodes (36): prastara_tables(), _ad_item(), _age(), _amsa_table(), _arc_table(), ashtakavarga_section(), _body(), _chip() (+28 more)

### Community 58 - "report.py"
Cohesion: 0.12
Nodes (18): dasa_list(), Dasa, level(), listing(), options(), _options(), _av(), basic() (+10 more)

### Community 59 - "mundane_rodden.py"
Cohesion: 0.12
Nodes (20): build(), country_table(), fetch(), iso_codes(), main(), moment(), place(), countries() (+12 more)

### Community 60 - "test_pending_options.py"
Cohesion: 0.12
Nodes (12): event_year_definition(), kp_period_date(), AmsaBala, vaiseshikamsa_counts(), bhava_arudhas(), _amsa(), TestAvasthaCompound, TestEventYearDefinition (+4 more)

### Community 61 - "Astrocartography.tsx"
Cohesion: 0.08
Nodes (44): AstroBand, AstroLine, AREAS, Astrocartography(), Bands(), bandSpots(), cityMarks(), COPIES (+36 more)

### Community 62 - "traditions.py"
Cohesion: 0.16
Nodes (21): colors(), available(), chinese(), compute(), _date(), _declination(), _house_of(), iching() (+13 more)

### Community 63 - "App.tsx"
Cohesion: 0.07
Nodes (51): About(), CREDITS, Emblem(), AccountPanel(), BUILT_IN, shrink(), Account, onSettings() (+43 more)

### Community 64 - "Conditional dasa tests"
Cohesion: 0.18
Nodes (7): chart(), result(), row(), sign(), TestConditions, TestSelection, TestStrength

### Community 65 - "periods"
Cohesion: 0.07
Nodes (21): _md(), periods(), _ak_graha_years(), ak_kendradi_graha_dasa(), buddhi_gati_dasa(), _count_to(), _graha_order(), karaka_dasa() (+13 more)

### Community 66 - "place"
Cohesion: 0.12
Nodes (28): ab(), AMSA_TONE(), band(), BhavaSum(), both(), CrossAspects(), dignityTone(), DRISHTI (+20 more)

### Community 67 - "Auth tests"
Cohesion: 0.09
Nodes (3): hash_password(), reset_password(), TestAuth

### Community 68 - "muhurtaMath.test.ts"
Cohesion: 0.13
Nodes (19): DayView(), nowAt(), reduced(), SpanButton(), ViewIcon(), wrap(), goodWindows(), hoursOn() (+11 more)

### Community 69 - "test_security.py"
Cohesion: 0.33
Nodes (3): host_ok(), client(), TestSecurity

### Community 70 - "mundane_data.py"
Cohesion: 0.05
Nodes (24): mundane_summary(), birth_of(), dataset(), dropped(), _eclipses(), _event_factors(), _factors(), _file() (+16 more)

### Community 71 - "Predictions.tsx"
Cohesion: 0.11
Nodes (30): api, deathAt(), useDeath(), Answer, Answers, answerText(), chartKey(), COUNTS (+22 more)

### Community 72 - "Mundane.tsx"
Cohesion: 0.10
Nodes (21): ABOUT, cap(), Card(), COLS, DATE, facts(), fmtYear(), KIND (+13 more)

### Community 73 - "Server miscellany"
Cohesion: 0.12
Nodes (16): _tables(), _aspects(), _clock(), _dp_line(), _entries(), _ephemeris(), laghu_parasari(), monthly_text() (+8 more)

### Community 74 - "get"
Cohesion: 0.13
Nodes (11): healthz(), find_users(), get_chart(), get_facts(), get_shared(), list_charts(), list_shared(), owner_login() (+3 more)

### Community 75 - "Calendar (timeline) UI"
Cohesion: 0.15
Nodes (28): SkyPlace, TimelineYear, TimeSpan, ab(), ABBR, Conjunctions(), date(), dms() (+20 more)

### Community 76 - "_chart"
Cohesion: 0.13
Nodes (10): angular_return(), _body(), _chart(), _eclipse(), _local(), mundane(), nisheka(), pravesha() (+2 more)

### Community 77 - "translate.ts"
Cohesion: 0.08
Nodes (41): GRAMMAR, loaded, PAKSHA, SIGN_ABBR, SIGN_KEYS, wordsFor(), add(), ASPIRATE (+33 more)

### Community 78 - "ayurdaya.py"
Cohesion: 0.13
Nodes (8): ashtakavarga_years(), class_of_years(), _degrees(), maraka_stars(), pair_class(), rules(), saturn_ashtakavarga(), three_pairs()

### Community 79 - "oauth_callback"
Cohesion: 0.14
Nodes (11): _back(), _creds(), _fetch(), _first_name_username(), _give_samples(), _home(), oauth_callback(), oauth_start() (+3 more)

### Community 80 - "insights.py"
Cohesion: 0.19
Nodes (8): _bhavas(), _bodies(), house_type(), houses(), kp(), mars_bhavas(), _dignity(), natal_of()

### Community 81 - "events.py"
Cohesion: 0.11
Nodes (12): _builder_key(), event_dasa(), event_years(), fitted_to_span(), locate_event(), nakshatra_progression_arc(), sub_periods(), sum_of_longitudes() (+4 more)

### Community 82 - "build_places_db.py"
Cohesion: 0.18
Nodes (12): build_fts(), download(), ensure(), iter_dump(), load_admin1(), load_countries(), load_places(), log() (+4 more)

### Community 83 - "muhurtaMath.ts"
Cohesion: 0.14
Nodes (25): AVOID_BAND, bandsOf(), Dial(), GOOD_BAND, Hit, Pick, PLANET, PopInfo (+17 more)

### Community 84 - "zones.ts"
Cohesion: 0.21
Nodes (18): place(), ZoneInput(), ZONE_COUNTRY, browserZone(), countryOf(), guessZone(), HALF_HOURS, offsetOf() (+10 more)

### Community 85 - "basics.py"
Cohesion: 0.08
Nodes (20): adjusted(), amsa_rulers(), basics(), body_group(), core_info(), _dms(), extra_points(), _hms() (+12 more)

### Community 86 - "auth.py"
Cohesion: 0.07
Nodes (31): _account(), AccountIn, AvatarIn, change_password(), ChartIn, _check_names(), _check_room(), _check_terms() (+23 more)

### Community 87 - "Finance UI"
Cohesion: 0.17
Nodes (23): FinanceBar, FinanceEvent, FinanceEventKind, FinanceOhlc, FinanceSuggest, EVENT_KINDS, eventAbbr(), eventActor() (+15 more)

### Community 88 - "ChartPane.tsx"
Cohesion: 0.10
Nodes (29): ChartSpec, SettingGroup, Bitmap, copyBitmap(), CSS_VARS, downloadBlob(), inline(), sharePng() (+21 more)

### Community 89 - "BirthData"
Cohesion: 0.17
Nodes (7): body_longitude(), cusps_by_reference(), ecliptic_rise_set(), semi_diameter(), sign_window(), special_lagna(), varga_window()

### Community 90 - "test_astrocartography.py"
Cohesion: 0.21
Nodes (5): inside(), lon_at(), off(), TestAstrocartography, edge()

### Community 91 - "lore.py"
Cohesion: 0.06
Nodes (24): lore_bhava(), lore_graha(), lore_nakshatra(), lore_rashi(), graha_insights(), bhava(), bhava_reading(), _dignities() (+16 more)

### Community 92 - "core_logic/jamakkol.py"
Cohesion: 0.09
Nodes (9): aarudam(), jama_grahas(), jamam(), kalam_points(), kavippu(), points(), udayam(), veethi() (+1 more)

### Community 93 - "kp_astrology.py"
Cohesion: 0.14
Nodes (9): _build_249_sub_table(), compute_cuspal_sub_lords(), compute_kp_significators(), get_kp_ruling_planets(), get_kp_sub_levels(), get_kp_sub_lords(), resolve_kp_horary_number(), main() (+1 more)

### Community 94 - "charts.py"
Cohesion: 0.08
Nodes (28): argala_signs(), _arudhas(), bodies(), _boxed(), _check(), _duration(), highlight(), marana() (+20 more)

### Community 95 - "karakas.py"
Cohesion: 0.17
Nodes (5): chara_karaka_slots(), compute_chara_karakas(), is_combust_by_orbs(), planetary_war(), stronger_for_sthira()

### Community 96 - "language.ts"
Cohesion: 0.18
Nodes (17): attr(), ATTRS, back, cache, listen(), listeners, observer, ordinals() (+9 more)

### Community 97 - "Festival calendars"
Cohesion: 0.18
Nodes (9): calendars(), criteria(), data(), _month_name(), _sign(), _solar_name(), tithi_text(), view() (+1 more)

### Community 98 - "Sudarshana chakra intro"
Cohesion: 0.19
Nodes (18): around(), circle(), design(), petal(), polar(), Pt, quad(), R (+10 more)

### Community 99 - "Panels.tsx"
Cohesion: 0.04
Nodes (97): AvView, GrahaInsight, nowMoment(), Strengths, AvakahadaView(), formatLon(), keep(), useSaved() (+89 more)

### Community 100 - "Ephemeris addition tests"
Cohesion: 0.09
Nodes (5): to_birth_data(), diff(), TestEphemerisOracle, TestEphemerisAdditions, TestWorkflows

### Community 101 - "index_members"
Cohesion: 0.21
Nodes (7): big_companies(), index_members(), _link(), _text(), unicorn_titles(), wiki_page(), wiki_tables()

### Community 102 - "Wheels"
Cohesion: 0.17
Nodes (13): Chakras, SpecialPoint, boxesOf(), kalaDir(), mix(), pickList(), star27(), starName() (+5 more)

### Community 103 - "Astrocartography tests"
Cohesion: 0.21
Nodes (5): house_with(), lon_at(), post(), TestAstrocartography, wrap()

### Community 104 - "_arc_span"
Cohesion: 0.17
Nodes (6): _arc_span(), arc_years(), _lagna_cut(), lagna_years(), navamsa_years(), spans()

### Community 105 - "Sky"
Cohesion: 0.14
Nodes (6): _calendar(), _days(), _eclipses(), _entry(), _parana(), Sky

### Community 106 - "house_systems.py"
Cohesion: 0.10
Nodes (18): _armc_from_mc(), _asc1(), _asc_from_armc(), bhava_spans(), _check_latitude(), compute_campanus_houses(), compute_dinamana_ratrimana(), compute_equal_houses() (+10 more)

### Community 107 - "kept.ts"
Cohesion: 0.36
Nodes (8): chain, Changes, flush(), leave(), pending, pull(), send(), watch()

### Community 108 - "wheelGeometry.ts"
Cohesion: 0.11
Nodes (24): WheelSlot, CHANDRA, KALA, KOTA_X, KOTA_Y, pack(), Point, Row (+16 more)

### Community 109 - "traditionsMath.ts"
Cohesion: 0.11
Nodes (22): AZTEC_SIGNS, BRANCH_ANIMALS, BRANCH_HANZI, BRANCHES, branchIndex(), FLIGHT, flyStars(), LO_SHU (+14 more)

### Community 110 - "MuhurtaFind.tsx"
Cohesion: 0.14
Nodes (27): Festival, FestivalDate, FestivalDay, FestivalTime, MuhurtaEvent, MuhurtaFind, MuhurtaJudged, Count (+19 more)

### Community 111 - "CI workflow"
Cohesion: 0.13
Nodes (14): jobs, unittest, python, name, name, run, uses, with (+6 more)

### Community 113 - "server/transits.py"
Cohesion: 0.06
Nodes (33): in_gandanta(), _iso(), _ahead(), close_stay(), contacts_in(), cross(), open_stay(), _ashtakavarga() (+25 more)

### Community 115 - "chart_routes.py"
Cohesion: 0.14
Nodes (13): basics(), BhavaReadingReq, chart(), graha_insights(), GrahaInsightsReq, houses(), HousesReq, JhdReq (+5 more)

### Community 117 - "names.ts"
Cohesion: 0.22
Nodes (10): Inspector(), CHART_LABELS, KEYS, labels(), retroMark(), SANSKRIT, SANSKRIT_SIGNS, shown() (+2 more)

### Community 118 - "_forward_from"
Cohesion: 0.22
Nodes (6): sudarsana_chakra_dasa(), chakra_dasa(), _forward_from(), navamsa_dasa(), shoola_dasa(), start()

### Community 119 - "JChart"
Cohesion: 0.11
Nodes (10): best_dasa(), _conditions(), _dignity(), _house(), _lord(), _strength(), JChart, brahma_dasa() (+2 more)

### Community 120 - "marakas"
Cohesion: 0.28
Nodes (3): _lagna_lord_with(), marakas(), sun_relation()

### Community 122 - "build_world_map.py"
Cohesion: 0.39
Nodes (6): area(), load(), main(), parts(), path(), simplify()

### Community 123 - "Festival tests"
Cohesion: 0.27
Nodes (3): dates(), Festivals, items()

### Community 124 - "civil_day_panchanga"
Cohesion: 0.17
Nodes (5): civil_day_panchanga(), part(), _ends(), yogini_mrityu(), place()

### Community 125 - "chakraTables.ts"
Cohesion: 0.20
Nodes (12): GHATAKA, GhatakaDay, ghatakaHits(), MONTHS, SHALAKA, shalakaPartner(), SYLLABLES, TARA_KIND (+4 more)

### Community 126 - "mundaneMath.ts"
Cohesion: 0.11
Nodes (18): Col, Cell, Confidence, DatasetName, DATASETS, Factor, Filter, GRAHAS (+10 more)

### Community 127 - "place"
Cohesion: 0.31
Nodes (18): aberrate(), add(), at(), cross(), deflect(), dot(), from_ecliptic(), moon() (+10 more)

### Community 129 - "ref_node_assert"
Cohesion: 0.32
Nodes (3): plan, nameAnka(), SYLLABLES

### Community 131 - "main.tsx"
Cohesion: 0.36
Nodes (4): client, onKey(), starts(), startSelectKeys()

### Community 134 - "PyResult"
Cohesion: 0.21
Nodes (14): chinese(), extra_bodies(), houses(), iching(), input(), lalkitab(), norm(), num() (+6 more)

### Community 135 - "tithi_pravesha"
Cohesion: 0.33
Nodes (3): tithi_pravesha(), tithi_pravesha_months(), _tithi_return()

### Community 136 - "mundane_finance.py"
Cohesion: 0.05
Nodes (45): TestPointNames, aliases(), build(), founding(), home(), listings(), match(), moment_of_listing() (+37 more)

### Community 137 - "longitude_sums.py"
Cohesion: 0.25
Nodes (3): label(), part_in_division(), rows()

### Community 139 - "Hosting script"
Cohesion: 0.52
Nodes (5): admin(), alive(), halt(), keep(), host.sh script

### Community 140 - "chinese_calendar.py"
Cohesion: 0.19
Nodes (6): _day(), _end(), lunar_date(), new_moon_by(), next_new_moon(), TestChineseCalendar

### Community 143 - "file_routes.py"
Cohesion: 0.03
Nodes (31): export_jhd(), ExportReq, ini_export(), ini_parse(), IniExportReq, IniReq, mundane_patterns(), PatternsReq (+23 more)

### Community 145 - "cls"
Cohesion: 0.23
Nodes (14): Avakahada(), Bodies(), cls(), Kota(), Kurma(), Packed(), Rows(), SaptaShalaka() (+6 more)

### Community 147 - "test_traditions.py"
Cohesion: 0.39
Nodes (3): birth(), part(), TestTraditions

### Community 148 - "mundaneMath.test.ts"
Cohesion: 0.14
Nodes (14): categories(), categoryOf(), chiSquareP(), compare(), FactorRow, NO_FILTER, normalCdf(), bce (+6 more)

### Community 149 - "special_search"
Cohesion: 0.40
Nodes (3): find(), special_search(), _varga_event()

### Community 150 - "calc"
Cohesion: 0.32
Nodes (5): calc(), jpl_kernel(), kernel(), load(), naif()

### Community 151 - "yearOf"
Cohesion: 0.40
Nodes (5): fmtDate(), useRecords(), when(), yearBins(), yearOf()

### Community 152 - "TestJplKernel"
Cohesion: 0.13
Nodes (4): arcsec(), TestJplKernel, TestSwissIsTheDefault, TestSwissOnDE442

### Community 153 - "deltat.py"
Cohesion: 0.22
Nodes (3): deltat_se202(), _tidal(), TestDeltaT

### Community 157 - "rodden.py"
Cohesion: 0.19
Nodes (6): rodden_chart(), chart(), facts(), listing(), _query(), with_death()

### Community 158 - "_gzipped"
Cohesion: 0.32
Nodes (3): _gzipped(), mundane_dataset(), rodden_charts()

### Community 159 - "remedies.py"
Cohesion: 0.15
Nodes (11): calculations_topics(), remedies_topics(), _abhukta_mula(), calculation_topics(), chart_flags(), _jyeshtha_gandanta(), _load(), _moon_gandanta() (+3 more)

### Community 161 - "Detail"
Cohesion: 0.33
Nodes (9): Badge(), Detail(), fmtTime(), shortName(), useAdd(), useOpen(), foundingOf(), titleOf() (+1 more)

### Community 166 - "Sudarsana"
Cohesion: 0.83
Nodes (4): band(), polar(), Sudarsana(), wedge()

### Community 167 - "Filters"
Cohesion: 0.38
Nodes (7): byKind(), Filters(), MultiPick(), applyFilter(), countBy(), indicesOf(), kindOf()

### Community 168 - "Database"
Cohesion: 0.27
Nodes (10): cellText(), colActive(), ColMenu(), Database(), DataTable(), needs(), Overview(), Research() (+2 more)

### Community 171 - "dasa_routes.py"
Cohesion: 0.24
Nodes (10): best_dasa(), dasa(), dasa_transit(), DasaReq, entry_chart(), locate_event(), LocateReq, _on_dasa() (+2 more)

### Community 203 - "server/chakras.py"
Cohesion: 0.11
Nodes (9): eras(), lunar_month(), avakahada(), _base_star(), _bodies(), ghataka_day(), _natal_point(), special_point() (+1 more)

## Knowledge Gaps
- **6 isolated node(s):** `jpl-kernel`, `jpl-kernel`, `traditions`, `traditions`, `core-logic` (+1 more)
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1918 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `norm360()` connect `norm360` to `factors.py`, `rasi.py`, `compatibility/__init__.py`, `tajika.py`, `core_logic/chakras.py`, `shadbala/__init__.py`, `file_routes.py`, `core_logic/__init__.py`, `Textbook dasha engines`, `math`, `panchanga.py`, `solve_longitude_crossing`, `varga_charts.py`, `dasa_systems/__init__.py`, `Ephemeris workflows`, `avasthas.py`, `kp_astrology.py`, `Ephemeris addition tests`, `house_systems.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `norm360()` (e.g. with `compute_aspect_details()` and `compute_parasara_drik_virupas()`) actually correct?**
  _`norm360()` has 78 INFERRED edges - model-reasoned connections that need verification._
- **What connects `jpl-kernel`, `jpl-kernel`, `traditions` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `factors.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0762739370334307 - nodes in this community are weakly interconnected._
- **Why does `useChart` connect `useChart` to `Panels.tsx`, `Longevity.tsx`, `Calculations tab UI`, `TopBar.tsx`, `ChartGrid.tsx`, `api.ts`, `Detail`, `store.ts`, `Matching.tsx`, `Chakras.tsx`, `Remedies.tsx`, `Muhurta.tsx`, `Lore.tsx`, `Database`, `useChart`, `MatchingCompare.tsx`, `Traditions.tsx`, `Astrocartography.tsx`, `App.tsx`, `place`, `Predictions.tsx`, `Mundane.tsx`, `Calendar (timeline) UI`, `Finance UI`, `ChartPane.tsx`, `language.ts`, `Panels.tsx`, `Wheels`, `MuhurtaFind.tsx`, `names.ts`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Should `norm360` be split into smaller, more focused modules?**
  _Cohesion score 0.03745905141717704 - nodes in this community are weakly interconnected._
- **Should `service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05042016806722689 - nodes in this community are weakly interconnected._