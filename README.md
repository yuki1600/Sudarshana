# Celestial Intelligence (Sudarshana)

A comprehensive Vedic Astrology calculation engine and visualization platform.

## Features

- **Calculations**: Accurate planetary positions using Swiss Ephemeris.
- **Charts**: 
  - **Sudarshana Chakra**: Unified view of Sun, Moon, and Ascendant charts.
  - **Ashtakavarga**: Benefic point calculations and Longevity analysis.
  - **Divisional Charts (Vargas)**: Support for D1-D60 charts.
- **Mundane Astrology**: Tools for ingress charts and planetary phenomena.
- **Dasa Systems**: Vimshottari Dasa calculation and visualization.

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: HTML5, Vanilla JavaScript, CSS3
- **Database**: SQLite (for geo-data)
- **Astrology Core**: `pyswisseph` integration.

## Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yuki1600/Sudarshana.git
    cd Sudarshana
    ```
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Setup Data**:
    *The location database is too large to host on GitHub, so you must generate it locally.*
    ```bash
    python3 scripts/build_places_db.py
    ```

3.  **Run the application**:
    ```bash
    uvicorn src.app:app --reload
    ```
4.  **Access UI**: Open `http://localhost:8000` in your browser.
