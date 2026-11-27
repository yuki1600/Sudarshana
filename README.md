<div align="center">

<img src="docs/assets/sudarshana-chakra.svg" width="140" alt="The Sudarshana Chakra, turning">

# Sudarshana

**सुदर्शन · divine light on the sky you were born under**

*A complete Vedic astrology workstation in the browser: Parashari, Jaimini, Tajaka, KP and Muhurta,<br>
computed with the Swiss Ephemeris and drawn as clearly as the classics deserve.*

</div>

---

## What it does

Enter a birth with a place typeahead of the whole world, open a `.jhd` / `.vs` file, or pick from a library of Rodden AA
and A birth records. Every page then computes from that chart with your own settings: ayanamsa, house system, chart style, date format.

| Page | What you get |
| :--- | :--- |
| **Home** | Four charts side by side (South, North or East Indian, in any varga), with Key Info, Bhavas, Amsa rulers, KP, Aspects, Yogas, Speeds, Avakahada and the nava taras. The Starlight inspector puts a card on every graha and bhava, with **Lore**: what BPHS, Phaladeepika, Brihat Jataka and Brihat Samhita say about it in this chart |
| **Dasas** | 49 dasa systems (nakshatra, rasi, graha, Kalachakra, event and Tajaka dasas), opening on the period running today, down to the pratyantardasa, each with its own options |
| **Balas** | Shadbala and Bhava Bala (as % of what each one needs), Ashtakavarga with its sodhanas, Vimsopaka, Vaiseshikamsa, the full yoga catalogue, avasthas, other balas, bar graphs |
| **Transits** | Gochara over the natal chart, plus Tajaka, Tithi Pravesha, Jamakkol, a transit calendar, special searches, longitude correlation, angular returns, progressions, Prasna and Laghu Parasari, with a time stepper from seconds to years |
| **Calendar** | A year of the sky as one strip per graha: signs, retrogressions, gandanta, combustion, conjunctions and eclipses |
| **Predictions** | What is known of the native, picked from chips and kept with the chart |
| **Tajaka · Tithi Pravesha** | Annual and lunar-return charts with Muntha, sahamas, Tajaka balas and their own dasas |
| **Muhurta** | The day's Panchanga on a dial, a muhurta finder, and festival calendars: Purnimanta, Amanta (Telugu, Kannada, Marathi, Gujarati) and Sauramana (Tamil, Sri Vaishnava, Malayalam, Bengali), with Ekadasi parana and Pitru Paksha |
| **Longevity** | The three pairs, marakas, Niryana Shoola timing, then Pinda, Amsa and Nisarga ayus, the 8th house, Ashtakavarga and yogas |
| **Chakras** | Divisional charts, mixed 2-vargas, Kalachakra, Sarvatobhadra, Tara, Sapta Shalaka, Ghataka, Kota, Kurma, Surya and Chandra Kalanala, Sudarshana |
| **Matching** | Ashta Kuta and the ancillary kootas, Kuja dosha, a 36 × 36 nakshatra matrix, two charts side by side, ranking partners |
| **Mundane** | Charts of the year, the month, eclipses and other turning points, found from the chart's moment and place |
| **Research** | Searchable databases of nations, elections, sports, events, markets and disasters (earthquakes, tsunamis, volcanoes), each record a chart |
| **Astrocartography** | A world map of the chart's moment: lagna bands, and each graha on the Lagna, 7th, MC and IC by place |
| **Finance** | Stock, index and crypto prices with graha ingresses, retrogressions and combustion marked on the chart |
| **Remedies** | Upayas for each graha from BPHS and the Vaishnava texts, read by chapter and verse |

**Two layouts.** *Starlight*: four charts, an inspector and tabs, in black, white, gold and purple. *Windows*: four
charts and the Key Info windows. A *Praajna Jyotisha* palette (saffron, gold and maroon) is there too.

**Accounts.** Sign in with a password or with Google, Facebook, LinkedIn or Microsoft; charts, notes and settings travel with the
account. A reload brings back exactly what was on screen.

**Eleven languages.** Settings > Language puts the app in English, Hindi, Gujarati, Marathi, Odia, Bengali, Assamese, Kannada,
Tamil, Telugu or Punjabi: the charts' grahas and signs, the tabs, the tables and the labels change; long explanations stay in English.

---

## How it is built

```
            ephemeris/  (Swiss Ephemeris, DE441)          data/  (tables, festivals, lore, remedies)   
                       │                                     │
                       ▼                                     ▼
                ┌──────────────────────────────────────────────────┐
                │  core_logic/   Python calculation engines         │
                └──────────────────────────────────────────────────┘
                                        │
                                        ▼
                ┌──────────────────────────────────────────────────┐
                │  server/       FastAPI: charts, dasas, transits,  │
                │                accounts, places, the built UI     │
                └──────────────────────────────────────────────────┘
                                        │  /api
                                        ▼
                ┌──────────────────────────────────────────────────┐
                │  web/          React 19 + Vite + Zustand          │
                └──────────────────────────────────────────────────┘
```

### Repository map

```
├── core_logic/            the calculation engines; the big subsystems are packages
│   ├── ephemeris/          Swiss Ephemeris: config and 22 ayanamsas, positions, houses, sunrise, day lords, build_chart;
│   │                       jpl.py the XALEN choice of Settings > Ephemeris (NASA JPL's DE442 kernel)
│   ├── natal_chart/        signs and dignities, D1–D150 vargas, arudhas, karakas, special lagnas, sensitive degrees
│   ├── dasa_systems/       the 49 dasas: nakshatra, rasi, graha, Kalachakra, event and Tajaka
│   ├── shadbala/           Shadbala, Bhava Bala, Vimsopaka
│   ├── compatibility/      kutas, ancillary kootas, Kuja dosha, matching score, chart comparison
│   ├── yoga_engine/        the yoga catalogue and its engine
│   ├── *.py                panchanga, tajika, kp_astrology, chakras, transits, ayurdaya, astrocartography,
│   │                       jamakkol, mundane, workflows (searches, returns, entry charts) …
│   └── tests/              unit tests
│
├── server/                FastAPI over core_logic
│   ├── app/                the app and its routes (chart, modes, views, transits, dasas, files); web/dist mounted last
│   ├── *.py                the services behind them: auth, places, festivals, muhurta, lore, remedies, finance, rodden …
│   └── tests/              the API's tests
│
├── web/                   React + Vite UI
│   ├── src/                one component per page (Dasas.tsx, Transits.tsx, Muhurta.tsx …), store.ts, api.ts,
│   │                       hooks.ts, ui.tsx; chakra.ts draws the Sudarshana Chakra of the intro and sign-in
│   └── src/styles/         base, starlight, praajna and per-page stylesheets
│
├── data/                  what the server reads at runtime: string tables, festivals and muhurta rules, remedies,
│                          lore (grahas, rashis, bhavas, nakshatras and every pairing), mundane records,
│                          the default settings, sample charts
├── ephemeris/             Swiss Ephemeris files: data/ (DE441, 102 .se1 files, −9600 to +16800, and sefstars.txt);
│                          jpl/: NASA JPL's DE442 (1550–2650), de442.eph for the Swiss Ephemeris and de442.bsp for
│                          XALEN, fetched by start.sh, git-ignored
├── native/jpl_kernel/     Rust (PyO3): the DE442 kernel read and reduced with the XALEN Ephemeris crates
├── native/traditions/     Rust (PyO3): the Traditions tab's Western, Chinese and world traditions from the XALEN crates
├── databases/             builders for places.db (GeoNames) and rodden.db; accounts.db lives here, git-ignored
├── BTS/                   Rodden AA and A birth records, the source of rodden.db
├── tools/                 generators for app data (world map, mundane records)
├── docs/                  SOURCES, TODO, DESIGN, SECURITY, and this README's assets
├── mobile app/            the plan and wireframes for a mobile version
└── graphify-out/          a knowledge graph of the code (GRAPH_REPORT.md)
```

---

## Getting started

Needs Python 3.10+ and Node 22+. (On Windows use Python 3.10 or 3.11, the last versions with `pyswisseph` wheels.)

```bash
./start.sh                      # sets up .venv and web/node_modules, builds the UI if it changed, serves on :8000
```

Then open **http://127.0.0.1:8000**. By hand, it is:

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python databases/build_places_db.py    # once (start.sh does it): world cities for the place typeahead
.venv/bin/python databases/build_rodden_db.py    # once: the Rodden library in Open chart
(cd web && npm install && npm run build)
.venv/bin/python -m server
```

`npm run dev` in `web/` serves the UI with hot reload and passes `/api` to the server.

Both ephemerides read NASA JPL's DE442 from `ephemeris/jpl/` (git-ignored): the Swiss Ephemeris its binary file, built
from JPL's ASCII files, and the XALEN Ephemeris engine (Settings › Ephemeris) its SPK kernel. `./start.sh` fetches both
(`core_logic.ephemeris.fetch_jpl_files()` by hand) and builds XALEN's native module `native/jpl_kernel`, which needs
Rust ([rustup.rs](https://rustup.rs)); by hand, `.venv/bin/pip install ./native/jpl_kernel`.

**Sharing it.** `./host.sh start` puts the app on a free Cloudflare quick tunnel (`./host.sh status` gives the link,
`./host.sh stop` ends it). For a cloud host, the `Dockerfile` builds one container; settings go in `.env` (see
`.env.example`), and [docs/SECURITY.md](docs/SECURITY.md) is the checklist first.

### From Python

The engines work on their own:

```bash
.venv/bin/python -m core_logic "data/sample_charts/Swami Vivekananda.jhd"   # positions, KP lords, Vimshottari, Ashtakavarga
```

```python
import core_logic as cl

birth = cl.to_birth_data(cl.parse_jhd_file("data/sample_charts/India.jhd"))
chart = cl.build_chart(birth, cl.EphemerisConfig(ayanamsa="TRUE_LAHIRI"), house_system="PLACIDUS")
chart["planet_longitudes"], chart["lagna_sign"], chart["sunrise_hours"]
```

[core_logic/README.md](core_logic/README.md) lists every module.

### Tests

```bash
cd web && npm test && npm run typecheck                     # UI unit tests and types
.venv/bin/python -m unittest discover -s core_logic/tests -t .     # engines
.venv/bin/python -m unittest discover -s server/tests -t .         # API
```

[docs/SOURCES.md](docs/SOURCES.md) gives the classical or public source of every calculation and setting.

---

## Built on

- [**Swiss Ephemeris**](https://www.astro.com/swisseph/) by Astrodienst AG, through `pyswisseph`, on NASA JPL's DE442: every graha position
- [**XALEN Ephemeris**](https://github.com/vedika-io/xalen-ephemeris) by XALEN Technology (Apache-2.0) and NASA JPL's
  [**DE442**](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/): the other choice of Settings › Ephemeris, and the
  Traditions tab's Western, Chinese and world traditions, I Ching, numerology and Lal Kitab
- [**GeoNames**](https://www.geonames.org/): places, coordinates and time zones (CC BY 4.0)
- [**IANA Time Zones**](https://www.iana.org/time-zones): historical zone and daylight-saving rules
- [**Natural Earth**](https://www.naturalearthdata.com/): the world map
- [**NOAA NCEI**](https://www.ncei.noaa.gov/): earthquake, tsunami and volcano records
- [**Rodden ratings**](https://www.astro.com/astro-databank/): the birth-data library in Open chart
- [**FastAPI**](https://fastapi.tiangolo.com/), [**React**](https://react.dev/), [**Vite**](https://vite.dev/), [**Zustand**](https://zustand.docs.pmnd.rs/), [**Tabler Icons**](https://tabler.io/icons)
- The classics: *Brihat Parasara Hora Sastra*, *Jaimini Upadesa Sutras*, *Phaladeepika*, *Brihat Jataka*, *Brihat Samhita*, *Tajika Neelakanthi*; the nakshatras from Dr. Arjun Pai's *Cosmic Insights*

## Acknowledgements

With gratitude to **P.V.R. Narasimha Rao**, creator of the original
[Jagannatha Hora](https://www.vedicastrologer.org/jh/) desktop application, whose software and teaching have been the
inspiration behind Sudarshana.

<div align="center"><sub>Vision and creation: <a href="https://www.linkedin.com/in/yuktesh-b-aa4a801a5/">Yuktesh B</a></sub></div>
