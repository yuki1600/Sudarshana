# Jyotisha Engine Architecture

Sudarshana organizes every calculation as a **modular component** under one of five **functional categories**. Each category maps to a role in the computational model (your schema: identity → strength → state → timing → relational).

## Category tree

```
src/jyotisha/
├── base/                    # Shared: constants, dates, utils, ephemeris
├── identity/                # What grahas/signs represent
│   ├── vargas.py
│   └── astrocartography.py
├── strength/                # How strongly grahas deliver
│   └── panchbala.py         # planned
├── state/                   # How effectively grahas deliver
│   └── avastha.py           # planned
├── timing/                  # When effects manifest
│   ├── ashtakavarga.py
│   ├── transits.py
│   ├── mundane.py
│   └── dasha/
│       ├── vimshottari.py
│       └── systems.py
├── relational/              # How grahas modulate each other
│   ├── match/               # Das Kuta
│   └── yogas.py             # planned
├── pipeline/
│   └── chart.py             # Orchestrator: full birth chart
└── registry.py              # Component catalog & metadata
```

## Five categories (functional roles)

| Category | Jyotisha elements | Model role | Package |
|----------|-------------------|------------|---------|
| **Identity / Nature** | Graha positions, rashi, nakshatra, vargas, panchanga, lagnas | Semantic embedding | `jyotisha.identity` + positions in `pipeline.chart` |
| **Strength / Intensity** | Shadbala, bhava bala, dignity tables | Amplitude scalar on node | `jyotisha.strength` (+ `pipeline.chart` until extracted) |
| **State / Readiness** | Avastha (jagrat/swapna/sushupti; bala/yuva/vriddha/mrita) | Modulation on strength | `jyotisha.state` |
| **Timing / Activation** | Dasha, AD/PD, transits, ashtakavarga, mundane | Temporal gate scalar | `jyotisha.timing` |
| **Relational / Effect** | Aspects, arudha, kutas, yogas, conjunctions | Edge weights | `jyotisha.relational` + aspects in `pipeline.chart` |

## Component registry

Every module is listed in `src/jyotisha/registry.py` with:

- `id` — stable name (e.g. `timing.ashtakavarga`)
- `category` — one of the five enums
- `module` — Python import path
- `encodes` / `model_role` — semantic meaning
- `status` — `implemented` | `partial` | `planned`

```python
from src.jyotisha.registry import COMPONENTS, by_category, Category

for c in by_category(Category.TIMING):
    print(c.id, c.status, c.entrypoint)
```

## Pipeline vs components

- **Standalone components** live in their category package (e.g. `timing/transits.py`).
- **`pipeline/chart.py`** still orchestrates the full natal chart (positions, shadbala, dashas, aspects). Large blocks are marked for **extraction** into category packages without changing API output.
- **API layer** (`src/app.py`) continues to import via `src.ci_core` — thin **compatibility shims** re-export from `jyotisha`.

## Backward compatibility

| Old path | New canonical path |
|----------|----------------------|
| `src/ci_core/*` | `src/jyotisha/...` (shim re-exports) |
| `src/dasa_systems.py` | `src/jyotisha/timing/dasha/systems.py` |
| `src/ci_match/*` | `src/jyotisha/relational/match/` |

Prefer new imports in new code:

```python
from src.jyotisha.pipeline import compute_chart_with_tzname
from src.jyotisha.timing import compute_ashtakavarga
from src.jyotisha.relational.match import calculate_match
```

## Roadmap (extraction order)

1. **Strength** — move shadbala / bhava bala / ishta-kashta out of `pipeline/chart.py` → `strength/`
2. **Identity** — move panchanga & special lagnas → `identity/`
3. **Relational** — move aspect grid & arudha → `relational/`
4. **State** — implement `state/avastha.py`
5. **Relational** — implement classical `relational/yogas.py`
