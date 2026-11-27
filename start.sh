#!/usr/bin/env bash
# One-command start: set up whatever is missing, rebuild the UI if web/src changed, (re)start the server.
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] && { set -a; . ./.env; set +a; }   # sign-in keys and other settings (.env.example), git-ignored
PORT="${PORT:-8000}"

[ -d .venv ] || python3 -m venv .venv
PY=.venv/bin/python
$PY -c "import fastapi, uvicorn, swisseph, ccxt, httpx" 2>/dev/null || $PY -m pip install -q -r requirements.txt

# The XALEN Ephemeris engine's native modules (Rust): native/jpl_kernel (Settings > Ephemeris "XALEN") and native/traditions
# (the Traditions tab), each rebuilt when its source changes. Without Rust the Swiss Ephemeris still works; the two then say
# what is missing
export PATH="$HOME/.cargo/bin:$PATH"
for crate in jpl_kernel traditions; do
  if command -v cargo >/dev/null; then
    if ! $PY -c "import $crate" 2>/dev/null || [ ! -f .venv/.$crate ] \
       || [ -n "$(find native/$crate/src native/$crate/Cargo.toml -newer .venv/.$crate -print -quit)" ]; then
      $PY -m pip install -q ./native/$crate && touch .venv/.$crate
    fi
  elif ! $PY -c "import $crate" 2>/dev/null; then
    echo "native/$crate needs Rust to build (https://rustup.rs); the Swiss Ephemeris works without it." >&2
  fi
done
# NASA JPL's DE442 for both ephemerides (ephemeris/jpl/): the kernel XALEN reads and the binary file the Swiss Ephemeris
# reads, which JPL publishes as ASCII (330 MB, converted once). Until they are there the Swiss Ephemeris uses its .se1 files
$PY -c "from core_logic.ephemeris import fetch_jpl_files; fetch_jpl_files()" || echo "Could not fetch NASA JPL's DE442 files to ephemeris/jpl/." >&2
# The place search's GeoNames database (databases/README.md): built once, a few MB to download
[ -f databases/places.db ] || $PY databases/build_places_db.py || echo "Could not build databases/places.db: the place search is empty until it is built." >&2

[ -d web/node_modules ] || (cd web && npm install)
# shortcut: staleness = any web/src file newer than dist/index.html, fine for a local app
if [ ! -f web/dist/index.html ] || [ -n "$(find web/src web/index.html -newer web/dist/index.html -print -quit)" ]; then
  (cd web && npm run build)
fi

# replace a previous instance of this app so it serves the current code
OLD=$(lsof -tiTCP:"$PORT" -sTCP:LISTEN || true)
if [ -f .host/server.pid ] && kill -0 "$(cat .host/server.pid)" 2>/dev/null; then
  # hosted (host.sh): its loop starts the server again with the new code. Wait for the old one to go and the new one to
  # answer, so whatever runs next (refresh.sh) doesn't meet the old server on its way out or the gap after it
  if [ -n "$OLD" ]; then
    kill $OLD
    for _ in $(seq 1 50); do kill -0 $OLD 2>/dev/null || break; sleep 0.2; done
  fi
  for _ in $(seq 1 150); do
    NEW=$(lsof -tiTCP:"$PORT" -sTCP:LISTEN || true)
    [ -n "$NEW" ] && [ "$NEW" != "$OLD" ] && curl -sf -o /dev/null --max-time 2 "http://127.0.0.1:$PORT/" && { echo "Hosted: the server is back with the new code."; exit 0; }
    sleep 0.2
  done
  echo "Hosted: the server has not come back after 30 s; see .host/server.log" >&2; exit 1
fi
if [ -n "$OLD" ]; then
  ps -p "$OLD" -o command= | grep -qE -- "-m (server|uvicorn server)" || { echo "port $PORT is used by another program" >&2; exit 1; }
  kill $OLD; sleep 1
fi

exec $PY -m server --port "$PORT"   # opens the browser itself
