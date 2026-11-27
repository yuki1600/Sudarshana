# `core_logic` — Jyotish calculation engines

Sudarshana's Python calculation engines, from the classical texts and public astronomy. The source of every rule is in
[`docs/SOURCES.md`](../docs/SOURCES.md); what is still open is in [`docs/TODO.md`](../docs/TODO.md).

## Modules

The six largest are packages split by subsystem: `ephemeris`, `natal_chart`, `dasa_systems`, `shadbala`, `compatibility`,
`yoga_engine`. Each package's `__init__.py` re-exports every name, so `from core_logic.shadbala import X` works as it
always did; add new code to the part it belongs with.

| Module | Contents |
| :--- | :--- |
| `ephemeris` | Swiss Ephemeris: positions, 22 ayanamsas, houses, sunrise/sunset, special lagnas, upagrahas (kalavelas), eclipses, time zones, `build_chart` *(needs pyswisseph)* |
| `workflows` | Transit / sign-change / lagna-change searches, transit calendar, Tajaka and Tithi Pravesha moments, Ardra pravesha, angular returns, entry charts, matching from charts *(needs pyswisseph)* |
| `jhd_io` | `.jhd` reader/writer (6 layouts) |
| `house_systems` | Closed-form house systems, dinamana/ratrimana, sandhyas |
| `natal_chart` | Rasi/nakshatra info, dignities, D1–D150 vargas, karakas, arudhas, Hora/Ghati/Bhava lagna, Mrityu/Pushkara bhaga |
| `special_lagnas_upagrahas` | Sree, Indu, Pranapada, Vighati, Varnada lagnas, Bhrigu Bindu, Kunda, Dhuma…Upaketu, kalavela rules |
| `aspects_friendships` | Graha drishti virupas, Jaimini rasi drishti, Naisargika/Tatkalika/Panchadha relationships, sambandha |
| `dashas` | Vimshottari tree (pass `to_date=dasa_year_mapper(birth)` for the chosen year) |
| `dasa_systems` | The 49 dasa builders |
| `varga_charts` | Divisional charts: all 57 schemes, custom D-n, D-m×n, bhava charts, D-150, amsa rulers |
| `time_search`, `daily_panchanga`, `longitude_sums`, `surya_siddhanta` | The search family, Panchanga tab, Laghu Parasari view, Sri Surya Siddhanta model |
| `sign_strength`, `deltat` | Jaimini strength rules; Δ-T of Swiss Ephemeris 2.02 |
| `ashtakavarga`, `kakshyas` | Prastara/BAV/SAV, sodhanas, Shodhya Pinda, kakshya transit scoring |
| `shadbala` | Six-fold strength, Ishta/Kashta, Bhava bala, Vimsopaka |
| `avasthas`, `yoga_engine`, `laghu_parasari` | Avasthas, yoga engine, functional nature |
| `tajika`, `sahams_library` | Varshaphal, Muntha, Tajaka balas, the textbook 16 Tajika yogas; the sahamas |
| `tithi_pravesha`, `mundane` | Lunar returns, ingress/new-year/station root solvers |
| `transits`, `chakras`, `panchanga`, `compatibility`, `kp_astrology`, `ayurdaya`, `miscellany` | Gochara/vedha, chakras, panchanga & muhurta, Ashta Kuta, KP, longevity, progressions & sphutas |
| `utils` | `norm360` and friends |

## Usage

```python
from datetime import datetime, timedelta
import core_logic as cl
from core_logic import ephemeris as E, workflows as W

birth = cl.to_birth_data(cl.parse_jhd_file("data/sample_charts/Swami Vivekananda.jhd"))
chart = E.build_chart(birth)                      # positions, houses, sunrise, special lagnas, upagrahas
born = datetime(birth.year, birth.month, birth.day) + timedelta(hours=birth.hour_local)

tree = cl.compute_vimshottari_tree(chart["planet_longitudes"]["Moon"], born, subperiod_depth=3)
print(tree[0]["lord"], tree[0]["balance_years"])
print(cl.locate_dasa_period(tree, datetime(1893, 9, 11)))          # dasa running at an event

seed_lon, seed_type = E.vimsottari_seed_longitude(chart, "GULIKA")  # other dialog-137 seeds
solar = cl.compute_vimshottari_tree(chart["planet_longitudes"]["Moon"], born,
                                    to_date=E.dasa_year_mapper(birth, kind="SOLAR"))

sahams = cl.compute_all_50_sahams(chart["planet_longitudes"], chart["lagna_lon"], is_night=chart["is_night"])
av = cl.run_full_ashtakavarga_pipeline({k: v for k, v in chart["planet_signs"].items()
                                        if k in E.CLASSICAL_PLANETS}, chart["lagna_sign"])
print(W.next_sign_change("Saturn", chart["jd_ut"]), W.lagna_sign_change(birth))
```

`python -m core_logic chart.jhd` runs a short pipeline from the command line.
Tests: `python -m unittest discover -s core_logic/tests -t .` (ephemeris tests skip without pyswisseph).
