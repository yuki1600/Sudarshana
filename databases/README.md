# Databases — Geographic Location & Timezone

This directory builds and stores the **World Places Database** used by the birth-data place typeahead (`server/places.py`). The data comes from [GeoNames](https://www.geonames.org/) and is free under **Creative Commons Attribution 4.0**.

The place search reads only this database; `start.sh` builds it when it is missing.

---

## Places Database (`places.db`)

> **Note:** `places.db` is **not** in git (it is large). Build it locally once:

```bash
python databases/build_places_db.py                 # cities ≥ 15 000 pop (~few MB download)
python databases/build_places_db.py --source cities5000
python databases/build_places_db.py --source allCountries   # full gazetteer, ~1 GB DB
```

### Schema

| Table | Columns | Purpose |
|-------|---------|---------|
| `places` | `geonameid`, `name`, `asciiname`, `alternatenames`, `lat`, `lon`, `country_iso2`, `admin1_code`, `population`, `timezone`, `fclass`, `fcode` | GeoNames populated places |
| `countries` | `iso2`, `name` | ISO 3166-1 country codes |
| `admin1` | `key`, `name` | First-level administrative divisions |
| `places_fts` | FTS5 virtual table | Prefix typeahead |

Each place stores an **IANA timezone** (e.g. `Asia/Kolkata`); the API converts it to standard/DST hour offsets for the birth dialog.

### Requirements

- Internet (first run only, to download the GeoNames dump)
- Python 3 with `sqlite3` (stdlib)

---

## Rodden Library (`rodden.db`)

> **Note:** `rodden.db` (~140 MB) and its source folder `BTS/` are **not** in git. Build it once, then restart the server:

```bash
.venv/bin/python databases/build_rodden_db.py          # reads BTS/rodden_AA and BTS/rodden_A
```

About 54 000 AA- and A-rated charts (duplicate spellings dropped), listed under **Open chart > Rodden** for every account. Each
row keeps the chart as a .vs file and its Predictions facts: gender, parents' deaths, marriage, illness and retirement in the
questions, every dated event under Other events, and the biography, relationships, sources and keywords in Notes. The build
checks each parsed birth against the Ascendant its file states and lists the ones more than 1° off.

`tools/mundane_rodden.py` cross-checks the library's event charts with the Research tab's databases, one way only: Rodden
event charts Research lacks join Research (`data/mundane/rodden_*.json`; those of no kind Research has form its Events
database), and Research records without an exact time take a matching Rodden chart's. The library itself is unchanged. The
findings, including every time and place the two disagree on, are in `data/mundane/RODDEN.md`.

---

## Finance companies (`data/mundane/finance.json`)

`tools/mundane_finance.py` builds the Research tab's Finance database, which is in git like the other Research sets:

```bash
.venv/bin/python -I tools/mundane_finance.py          # fetch what is missing, then build
.venv/bin/python -I tools/mundane_finance.py build    # rebuild from the downloads already cached
```

Its downloads are cached in `databases/raw/finance/` (git-ignored; delete a file to fetch it again). A first run takes about an
hour, because Wikidata's query service allows one query a minute. The database holds every listed company companiesmarketcap.com ranks,
with its listings and first trading days, a Yahoo Finance profile, and its Wikidata founding facts. It also holds CB Insights'
unicorns as startups. `data/mundane/FINANCE.md` records how far Yahoo's first trading days were trusted on each exchange, and every
listing day where the sources disagree.

---

## Utility Scripts

| Script | Purpose |
|--------|---------|
| `build_places_db.py` | Download a GeoNames dump and build `places.db` |
