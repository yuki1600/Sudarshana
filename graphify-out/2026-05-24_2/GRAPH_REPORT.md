# Graph Report - .  (2026-05-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 623 nodes · 1415 edges · 52 communities (35 shown, 17 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 108 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ba616cda`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]

## God Nodes (most connected - your core abstractions)
1. `norm360()` - 73 edges
2. `lon_to_sign_idx()` - 63 edges
3. `compute_chart()` - 55 edges
4. `get_all_vargas()` - 25 edges
5. `get_ayanamsa_code()` - 24 edges
6. `calculate_match()` - 22 edges
7. `compute_shadbala()` - 22 edges
8. `navamsa_for()` - 21 edges
9. `HistoricalDate` - 19 edges
10. `jd_to_datetime()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `BPHS Contents` --references--> `Brihat Parashara Hora Shastra (BPHS)`  [EXTRACTED]
  docs/BPHS.md → BPHS[1].pdf
- `Sudarshana UI` --implements--> `Celestial Intelligence (Sudarshana)`  [INFERRED]
  ui/index.html → README.md
- `lunar_new_year()` --calls--> `find_lunar_new_year()`  [INFERRED]
  src/app.py → src/jyotisha/timing/mundane.py
- `lunar_new_year()` --calls--> `compute_ashtakavarga()`  [INFERRED]
  src/app.py → src/jyotisha/timing/ashtakavarga.py
- `lunar_month()` --calls--> `get_ayanamsa_code()`  [INFERRED]
  src/app.py → src/jyotisha/base/constants.py

## Communities (52 total, 17 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (62): lon_to_sign_idx(), norm360(), rashi_name(), compute_lagna_for_location(), compute_lagna_grid(), compute_rashi_lines(), _find_longitude_for_ascendant(), Split line into segments when longitude jumps > threshold degrees. (+54 more)

### Community 1 - "Community 1"
Cohesion: 0.12
Nodes (36): check_ashtakoota_bhakoot(), check_ashtakoota_gana(), check_ashtakoota_tara(), check_ashtakoota_yoni(), check_graha_maitri(), check_varna(), get_nadi_type(), calculate_match() (+28 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (22): get_ayanamsa_list(), HistoricalDate, local_and_utc(), Subtract timedelta from HistoricalDate or calculate difference between dates, Represents a date that might be outside Python's datetime range (1-9999).     Mi, Add timedelta to HistoricalDate, Less than or equal comparison, Build timezone-aware local and UTC datetimes.     If tzname_override is provided (+14 more)

### Community 3 - "Community 3"
Cohesion: 0.13
Nodes (30): Strength / Intensity — how strongly grahas deliver., abda_bala(), ayana_bala(), cheshta_bala(), chesta_rasmi_val(), compute_ishta_kashta(), compute_shadbala(), dig_bala() (+22 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (26): build_dirga_dasa(), build_karak_dasa(), build_kendradi_dasa(), build_manduk_dasa(), build_shula_dasa(), build_sthir_dasa(), build_trikon_dasa(), build_yogardha_dasa() (+18 more)

### Community 5 - "Community 5"
Cohesion: 0.21
Nodes (25): _are_conjunct(), _chandra_yogas(), _daridra_yogas(), detect_yogas(), _dhana_yogas(), _house_of(), _is_exalted(), _is_in_kendra() (+17 more)

### Community 6 - "Community 6"
Cohesion: 0.18
Nodes (26): get_ayanamsa_code(), Get Swiss Ephemeris code for ayanamsa name, jd_to_datetime(), Convert Julian Day (UT) to timezone-aware datetime (or HistoricalDate), ensure_year_in_range(), format_datetime_for_js(), full_moon(), lunar_new_year() (+18 more)

### Community 7 - "Community 7"
Cohesion: 0.17
Nodes (20): benchmark_pair(), count_tokens(), main(), print_table(), count_bullets(), extract_code_blocks(), extract_headings(), extract_inline_codes() (+12 more)

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (22): Enum, Sudarshana Jyotisha engine — modular calculations by functional category.  Categ, by_category(), Category, Component, get_component(), Catalog of Jyotisha calculation components by functional category.  Categories m, One modular Jyotisha calculation unit. (+14 more)

### Community 9 - "Community 9"
Cohesion: 0.16
Nodes (20): main(), print_usage(), build_compress_prompt(), build_fix_prompt(), call_claude(), compress_file(), is_sensitive_path(), Heuristic denylist for files that must never be shipped to a third-party API. (+12 more)

### Community 10 - "Community 10"
Cohesion: 0.23
Nodes (19): Find when a specific tithi begins, Timing / Activation — when effects manifest., find_full_moon(), find_lunar_month_start(), find_lunar_new_year(), find_nakshatra_pravesha(), find_new_moon(), find_solar_return() (+11 more)

### Community 11 - "Community 11"
Cohesion: 0.11
Nodes (8): Deprecated location — use src.jyotisha.timing.ashtakavarga., Deprecated location — use src.jyotisha.identity.astrocartography., Deprecated location — use src.jyotisha.pipeline.chart., Deprecated location — use src.jyotisha.timing.dasha.vimshottari., Deprecated location — use src.jyotisha.timing.mundane., Deprecated location — use src.jyotisha.base.utils., Deprecated location — use src.jyotisha.identity.vargas., Deprecated location — use src.jyotisha.timing.dasha.systems.

### Community 12 - "Community 12"
Cohesion: 0.13
Nodes (18): BaseModel, api_get_generic_sub_period(), Country, get_db(), lagna_grid(), lagna_location(), list_countries(), match_charts() (+10 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (17): build_dwisaptati_sama(), build_shodshottari(), Build Shodshottari Dasa (116-year cycle).     Count from Pushya to birth nakshat, Build Dwisaptati-sama Dasa (72-year cycle, 8 planets, each 9 years).     Count f, compute_elements_gunas(), Compute elemental and guna profile for the chart.      Returns:         {, compute_chara_karakas(), compute_karakamsha() (+9 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (15): fmt_dt(), build_ashtottari(), build_chakra(), build_chaturashiti_sama(), build_dwadashottari(), build_shastihayani(), build_shatabdik(), Build Dwadashottari Dasa (112-year cycle).     Count from birth nakshatra to Rev (+7 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (16): datetime_to_jd(), Convert datetime (or HistoricalDate) to Julian Day (UT), conjunction(), lunar_month(), planet_sign_change(), planet_stationary(), Find when a planet becomes stationary (before retrograde or direct), Find conjunction of two planets (+8 more)

### Community 16 - "Community 16"
Cohesion: 0.36
Nodes (13): build_fts(), connect_db(), create_schema(), dl(), ensure_files(), finalize_db(), is_valid_place(), iter_allCountries_zip() (+5 more)

### Community 17 - "Community 17"
Cohesion: 0.41
Nodes (13): Caveman Stats Guide, computedHash, skillPath, source, sourceType, skills, cavecrew, caveman (+5 more)

### Community 18 - "Community 18"
Cohesion: 0.23
Nodes (11): Dasha systems — temporal activation., get_vimshottari_antardasha(), get_vimshottari_pratyantardasha(), get_yogini_antardasha(), get_yogini_pratyantardasha(), api_get_antardasha(), api_get_pratyantardasha(), api_get_yogini_antardasha() (+3 more)

### Community 19 - "Community 19"
Cohesion: 0.15
Nodes (13): init_ephe(), find_new_moon_in_sign(), find_planetary_conjunction(), find_solar_ingress(), Find the exact datetime of Sun-Moon conjunction (New Moon) in a specific sign., Find the exact datetime when Sun enters a specific sign (0° of that sign)., Find the exact datetime when two planets form a conjunction or opposition., Refine conjunction time using bisection method. (+5 more)

### Community 20 - "Community 20"
Cohesion: 0.17
Nodes (12): Identity / Nature, Jyotisha Engine Architecture, Relational / Effect, State / Readiness, Strength / Intensity, Timing / Activation, BPHS Contents, Brihat Parashara Hora Shastra (BPHS) (+4 more)

### Community 21 - "Community 21"
Cohesion: 0.33
Nodes (8): aspect_strength_pct(), Piecewise-linear aspect strength in percentage based on anchor angles., sign_dms_str(), aspect_score(), compute_aspect_grid(), pct_to_color(), Aspect grid and aspect score calculations., compute_bhava_bala()

### Community 22 - "Community 22"
Cohesion: 0.28
Nodes (8): compute_chart_with_tzname(), chart(), mundane_chart(), Compute mundane chart event datetime and return full chart.          This endpoi, calculate_ashtakavarga_longevity(), compute_ashtakavarga(), Calculate longevity based on Ashtakavarga rekhas.     Mapping:     0 rekhas = 2, Compute Bhinnashtakavarga (individual planet contributions) and Sarvashtakavarga

### Community 23 - "Community 23"
Cohesion: 0.36
Nodes (6): compute_avastha(), in_moolatrikona(), Avastha (planetary state / readiness). Implements five classical avastha systems, Computes Baladi, Jagratadi, Deeptaadi, Lajjitadi, and Shayanadi Avasthas     for, relation_to_lord(), State / Readiness — how effectively grahas deliver.

### Community 24 - "Community 24"
Cohesion: 0.47
Nodes (5): compute_marak_grahas(), _house_of(), _lord_of_house(), Marak Grahas — Death-Inflicting Planets (BPHS Ch. 44).  Primary Maraks : lords o, Identify Marak Grahas for the chart.      Returns:         list of dicts: planet

### Community 25 - "Community 25"
Cohesion: 0.60
Nodes (5): Cavecrew Builder, Cavecrew Investigator, Cavecrew Decision Guide, Cavecrew Reviewer, Cavecrew Skill Matrix

### Community 27 - "Community 27"
Cohesion: 0.40
Nodes (5): C2PA Claim v2, Google C2PA Media Services 1P ICA G3, Google C2PA Root CA G3, Google Generative AI, ui/logo-light.png

### Community 28 - "Community 28"
Cohesion: 0.40
Nodes (5): C2PA Metadata (logo-dark), Google Generative AI, ui/logo-dark.png, ui/logo-invert.png, ui/logo.png

### Community 29 - "Community 29"
Cohesion: 0.80
Nodes (4): download_file(), get_ssl_context(), log(), main()

### Community 30 - "Community 30"
Cohesion: 0.50
Nodes (4): build_kalachakra_dasa(), get_kalachakra_sequences(), Returns a dictionary mapping (Nakshatra_Idx, Pada) -> [List of Rashi Indices]., Kalachakra Dasa implementation.     Calculation:     1. Find Moon's Nakshatra an

### Community 31 - "Community 31"
Cohesion: 0.50
Nodes (4): calculate_generic_sub_periods(), get_dasa_config(), Returns configuration (Order List, Years Dict, Total Years) for a given Dasa sys, Calculate sub-periods (Antardasha/Pratyantardasha) for a given parent period.

### Community 32 - "Community 32"
Cohesion: 0.50
Nodes (4): opposition(), Find opposition of two planets, find_opposition(), Find when two planets are in opposition (180 degrees apart).

### Community 33 - "Community 33"
Cohesion: 0.67
Nodes (3): build_panch_swar_dasa(), get_name_swara_index(), Determine the Swara index (0-4) from the name.     A=0, I=1, U=2, E=3, O=4.

## Knowledge Gaps
- **28 isolated node(s):** `version`, `@opencode-ai/plugin`, `plugin`, `ui/logo-invert.png`, `Google Generative AI` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `compute_chart()` connect `Community 14` to `Community 0`, `Community 33`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 8`, `Community 42`, `Community 43`, `Community 13`, `Community 19`, `Community 21`, `Community 22`, `Community 23`, `Community 24`, `Community 30`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Why does `norm360()` connect `Community 0` to `Community 32`, `Community 2`, `Community 3`, `Community 6`, `Community 10`, `Community 13`, `Community 14`, `Community 15`, `Community 19`, `Community 21`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `lon_to_sign_idx()` connect `Community 0` to `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 10`, `Community 13`, `Community 14`, `Community 15`, `Community 21`, `Community 24`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `norm360()` (e.g. with `nakshatra_pravesha()` and `yoga_pravesha()`) actually correct?**
  _`norm360()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `get_ayanamsa_code()` (e.g. with `lunar_new_year()` and `lunar_month()`) actually correct?**
  _`get_ayanamsa_code()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `version`, `@opencode-ai/plugin`, `plugin` to the rest of the system?**
  _188 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06873706004140787 - nodes in this community are weakly interconnected._