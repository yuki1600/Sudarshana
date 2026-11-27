#!/usr/bin/env bash
# Share the app on the internet through a free Cloudflare quick tunnel (a random https://….trycloudflare.com link),
# running in the background until you stop it: closing the terminal, the editor or the lid doesn't stop it.
#   ./host.sh start    build the UI, start the server and the tunnel, keep the Mac awake (asks for your password once)
#   ./host.sh stop     stop all of it and let the Mac sleep again (asks for your password once)
#   ./host.sh status   whether it is running, and the link to share
# A crashed server or tunnel starts again by itself after 2 s. The link changes whenever the tunnel restarts,
# including after every start: check `./host.sh status` before sharing it.
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] && { set -a; . ./.env; set +a; }   # sign-in keys and other settings (.env.example), git-ignored
PORT="${PORT:-8000}"
RUN=.host   # pid files and logs
mkdir -p "$RUN"

alive() { [ -f "$RUN/$1.pid" ] && kill -0 "$(cat "$RUN/$1.pid")" 2>/dev/null; }
link() { grep -Eo 'https://[a-z0-9-]+\.trycloudflare\.com' "$RUN/tunnel.log" 2>/dev/null | tail -1 || true; }

# run "$@" in the background for good: again 2 s after it stops, until stop kills the loop; nohup so a closed terminal doesn't end it
keep() {
  local name=$1; shift
  nohup bash -c 'while true; do "$@"; sleep 2; done' keep "$@" >>"$RUN/$name.log" 2>&1 &
  echo $! >"$RUN/$name.pid"
  disown
}

# macOS's own password dialog: works from a terminal and from Claude alike, where sudo has no way to ask
admin() { osascript -e "do shell script \"$1\" with administrator privileges" >/dev/null 2>&1 || echo "Not allowed, so $2" >&2; }

halt() {   # the loop first, so it can't start its child again, then the child
  alive "$1" || return 0
  local loop kids
  loop=$(cat "$RUN/$1.pid"); kids=$(pgrep -P "$loop" || true)
  kill "$loop" 2>/dev/null || true
  [ -z "$kids" ] || kill $kids 2>/dev/null || true
  rm -f "$RUN/$1.pid"
}

case "${1:-status}" in
start)
  if alive server; then echo "Already running: $(link)"; exit 0; fi
  [ -x .venv/bin/python ] || { echo "No .venv yet: run ./start.sh once first." >&2; exit 1; }
  (cd web && npm run build >/dev/null)
  OLD=$(lsof -tiTCP:"$PORT" -sTCP:LISTEN || true)   # the app started by start.sh: this one replaces it
  if [ -n "$OLD" ]; then
    ps -p "$OLD" -o command= | grep -qE -- "-m (server|uvicorn server)" || { echo "port $PORT is used by another program" >&2; exit 1; }
    kill $OLD; sleep 1
  fi
  echo "Keeping the Mac awake with the lid closed (macOS asks for your password)."
  admin "pmset -a disablesleep 1" "closing the lid will still put the Mac, and the site, to sleep."
  : >"$RUN/tunnel.log"
  keep server .venv/bin/python -m server --port "$PORT" --no-browser
  keep tunnel cloudflared tunnel --no-autoupdate --url "http://127.0.0.1:$PORT"
  # -i: no idle sleep, -s: no system sleep on power; ends by itself when the server loop does
  nohup caffeinate -is -w "$(cat "$RUN/server.pid")" >/dev/null 2>&1 & disown
  for _ in $(seq 30); do [ -n "$(link)" ] && break; sleep 1; done
  echo "Running. Share this link: $(link)"
  echo "Also on this Mac: http://127.0.0.1:$PORT   Stop with: ./host.sh stop"
  ;;
stop)
  halt tunnel; halt server
  echo "Letting the Mac sleep again (macOS asks for your password)."
  admin "pmset -a disablesleep 0" "sleep stays off: run  sudo pmset -a disablesleep 0  yourself."
  echo "Stopped. ./start.sh runs the app on this Mac only again."
  ;;
status)
  if alive server; then
    echo "Running. Link: $(link)"
    alive tunnel || echo "The tunnel is down; it should come back within seconds (log: $RUN/tunnel.log)."
  else
    echo "Not running. Start with: ./host.sh start"
  fi
  pmset -g | grep -q "SleepDisabled.*1" && echo "Sleep is off (lid closed stays awake)." || true
  ;;
*) echo "usage: ./host.sh start|stop|status" >&2; exit 2 ;;
esac
