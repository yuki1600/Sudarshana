# Swiss Ephemeris Data Files

This directory contains **102 high-precision binary ephemeris data files** (used outside 1550–2650, where `jpl/` has NASA JPL's DE442; built from JPL DE441, downloaded from
`aloistr/swisseph` on 2026-10-27; the Astrodienst rebuild of 2026) from the [Swiss Ephemeris](https://www.astro.com/swisseph/) by Astrodienst AG. These files provide the astronomical foundation for all planetary position calculations.

---

## File Inventory

| Series | Count | Pattern | Content |
|--------|-------|---------|---------|
| **Planetary** | 51 | `sepl_*.se1`, `seplm*.se1` | Sun, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Lunar Nodes |
| **Lunar** | 51 | `semo_*.se1`, `semom*.se1` | High-precision Moon positions |

**Total Size:** ~94 MB


## Temporal Coverage

Each file covers a **600-year window**. The complete set spans:

| Range | Era | Files |
|-------|-----|-------|
| -9600 BCE to -9000 BCE | Deep antiquity | `seplm96.se1` / `semom96.se1` |
| 1800 CE to 2400 CE | **Modern era** | `sepl_18.se1` / `semo_18.se1` |
| 16800 CE to 17191 CE | Far future | `sepl_168.se1` / `semo_168.se1` |

## Minimum Modern Set

If disk space is critical, only **2 files** are needed for modern charts (1800–2400 CE):

| File | Size | Content |
|------|------|---------|
| `sepl_18.se1` | 484 KB | Modern planetary positions |
| `semo_18.se1` | 1.3 MB | Modern lunar positions |

**Total:** ~1.8 MB for full Swiss Ephemeris precision in the modern era.

## Moshier Fallback

The `pyswisseph` Python library includes a built-in **Moshier analytical ephemeris** (`FLG_MOSEPH`) that requires **zero external files**. It provides ~0.1 arcsecond accuracy between 3000 BCE and 3000 CE — sufficient for most practical purposes.

## Usage

Point the Swiss Ephemeris to this directory:

```python
import swisseph as swe
swe.set_ephe_path('/path/to/ephemeris/data')
```

## File Naming Convention

- `sepl_NN.se1` — Planetary data starting at year NN×100 CE
- `semo_NN.se1` — Lunar data starting at year NN×100 CE
- `seplmNN.se1` — Planetary data starting at year NN×100 BCE
- `semomNN.se1` — Lunar data starting at year NN×100 BCE


## Fixed-star catalogue

`sefstars.txt` (Swiss Ephemeris fixed-star catalogue, from the official `aloistr/swisseph` repository) is required by `swe_fixstar` for the Aldebaran/Shaula/galactic-centre based ayanamsas (Rohini-paksha, etc.). Spica and delta Cancri are built into pyswisseph. `core_logic/ephemeris/` points Swiss Ephemeris at this directory (override with `SUDARSHANA_EPHE_PATH`).

## NASA JPL DE442 (`jpl/`, git-ignored)

DE442 is NASA JPL's newest planetary and lunar ephemeris, 1550–2650 (integrated May 2024, published February 2025:
DE440 refitted with Uranus occultations and four more years of Mars-orbiter and Juno ranging). Both of the app's
ephemerides read it there, and the .se1 files above answer only outside its span :

| File | Size | For | From |
|------|------|-----|------|
| `de442.eph` | 102 MB | the Swiss Ephemeris (SEFLG_JPLEPH, `core_logic/ephemeris/config.py` `_ephe_flag`) | JPL's ASCII files (`ssd.jpl.nasa.gov/ftp/eph/planets/ascii/de442/`, 330 MB), converted by `jpl.py` `asc2eph`, JPL's asc2eph.f in Python (it gives JPL's own DE440 binary byte for byte from the DE440 ASCII) |
| `de442.bsp` | 114 MB | Settings › Ephemeris "XALEN" (`native/jpl_kernel`) | NAIF's SPK kernel |

`./start.sh` fetches both (`core_logic.ephemeris.fetch_jpl_files()`) and checks their SHA-256. JPL publishes DE442
in its binary form only as ASCII; Astrodienst's .se1 files are still DE441. Override the paths with
`SUDARSHANA_JPL_PATH` (the folder of `de442.eph`) and `SUDARSHANA_JPL_KERNEL` (the kernel).
