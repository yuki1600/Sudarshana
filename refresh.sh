#!/usr/bin/env bash
# Reload every Chrome tab showing the app (http://127.0.0.1:8000 or the trycloudflare link) once the server answers,
# so a change is on screen without pressing reload. Run after `npm run build` or a server restart. Opens nothing:
# Chrome not running, or no app tab, does nothing.
# A restart has a gap of ~2.5 s with nothing on the port, and the old server still answers for a moment after it is
# told to stop: so it waits for answers in a row, then for the tunnel link, and reloads again any tab that came up as
# an error page (Cloudflare's "502: Bad gateway", Chrome's "can't be reached"): the app's own pages are titled Sudarshana.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8000}"

ok=0
for _ in $(seq 1 120); do      # up to ~60 s: three answers in a row, half a second apart
  if curl -sf -o /dev/null --max-time 2 "http://127.0.0.1:$PORT/"; then ok=$((ok + 1)); [ $ok -ge 3 ] && break; else ok=0; fi
  sleep 0.5
done
[ $ok -ge 3 ] || echo "The server is not answering on port $PORT; reloading anyway." >&2

LINK=$(grep -Eo 'https://[a-z0-9-]+\.trycloudflare\.com' .host/tunnel.log 2>/dev/null | tail -1 || true)
if [ -n "$LINK" ] && [ -f .host/tunnel.pid ] && kill -0 "$(cat .host/tunnel.pid)" 2>/dev/null; then
  for _ in $(seq 1 20); do [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 4 "$LINK/" || true)" = 200 ] && break; sleep 1; done
fi

# which: "all" reloads every app tab, "failed" only those that finished loading as an error page; prints how many
chrome() {
  osascript - "$1" "$PORT" <<'EOF'
on run {which, port}
  if application "Google Chrome" is not running then return "none"
  tell application "Google Chrome"
    set n to 0
    repeat with w in windows
      repeat with t in tabs of w
        set u to URL of t
        if u starts with ("http://127.0.0.1:" & port) or u contains ".trycloudflare.com" then
          if which is "all" or ((not (loading of t)) and (title of t does not contain "Sudarshana")) then
            reload t
            set n to n + 1
          end if
        end if
      end repeat
    end repeat
    return n as text
  end tell
end run
EOF
}

n=$(chrome all)
[ "$n" = none ] && { echo "Chrome is not running"; exit 0; }
again=0
for _ in 1 2 3 4 5; do      # an error page: reload it again, a few seconds apart
  sleep 3
  m=$(chrome failed)
  [ "$m" = 0 ] && break
  again=$((again + m))
done
echo "reloaded $n tab(s)$([ $again -gt 0 ] && echo ", $again again after an error page" || true)"
