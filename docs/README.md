# Documentation Index

The living documents of Sudarshana. The code map is in the [README](../README.md) and in
[`graphify-out/GRAPH_REPORT.md`](../graphify-out/GRAPH_REPORT.md).

| Document | Content |
|----------|---------|
| [SOURCES.md](SOURCES.md) | The classical or public source of every calculation and setting, by chapter and verse, and the code that carries it out |
| [TODO.md](TODO.md) | Everything left to do |
| [DESIGN.md](DESIGN.md) | How each kind of thing is drawn across the tabs (tones, references, strengths, values in words, tables), kept up to date with every look the user settles |
| [SECURITY.md](SECURITY.md) | What protects the accounts and their data, the checklist before the cloud, setting up Sign in with Google, and what is still open |

## Data formats

| Format | Where |
|--------|-------|
| `.vs` chart files (JSON: birth data, name, state and notes) | `server/app/file_routes.py`, `web/src/OpenChart.tsx` |
| `.jhd` chart files (lines of text) | `core_logic/jhd_io.py` |
| Preferences `.ini` | `server/ini.py`, defaults in `data/default_settings.ini` |
| Places (GeoNames) | `databases/README.md`, `server/places.py` |
| Ephemeris files | `ephemeris/README.md` |
