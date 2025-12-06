# Data Directory

The `places.db` file (1.1GB+) and `allCountries.zip` (396MB+) are excluded from this repository due to size limits.

## How to Generate `places.db`

You can generate the database locally using the provided script. It will automatically download the necessary files from GeoNames.

```bash
python3 scripts/build_places_db.py
```

This will:
1.  Download `allCountries.zip` and other reference files to `data/raw/`.
2.  Build `data/places.db` (SQLite).

## Requirements
- Internet connection (for first run).
- Approx 2GB of disk space.
