---
name: start
description: Start Sudarshana and open it in Chrome — "start local" runs it on this Mac only (http://127.0.0.1:8000), "start cloud" shares it through a Cloudflare quick tunnel and opens the public link; also "stop cloud" and "cloud status". Use whenever the user says start local, start cloud, run the app, host it, share it, stop cloud, or /start.
---

# Start Sudarshana

Run every command from the repo root. The argument (or the user's words) picks the mode: **local**, **cloud**, **stop cloud** or **status**. No mode given: ask "local or cloud?" in one line.

On http://127.0.0.1:8000 the sign-in form comes prefilled with the owner's login (from the git-ignored `.owner-login.json`), so the user just clicks Sign in. Through the tunnel link the form is empty: the server never sends it there.

## start local

1. Build the UI (fast): `(cd web && npm run build >/dev/null)`
2. If something already serves port 8000 (`lsof -tiTCP:8000 -sTCP:LISTEN`), keep it. That includes the cloud server: local and cloud are the same server, so the local URL works while hosting. Restart it only if `server/` Python changed this session: `kill <pid>`; if `.host/server.pid` is alive, host.sh's loop brings it back by itself in ~2 s, so don't start another.
3. Otherwise start it in the background so it outlives this session:
   `mkdir -p .host && nohup .venv/bin/python -m server --port 8000 --no-browser > .host/local.log 2>&1 & disown`
4. Wait until it answers (Bash with run_in_background): `until curl -sf -o /dev/null http://127.0.0.1:8000/; do sleep 0.5; done`
5. Open it: `open -a "Google Chrome" http://127.0.0.1:8000/` (always 127.0.0.1, never localhost: the user's charts live in that origin's storage).
6. Reply with the URL in one line.

## start cloud

1. `./host.sh start` (timeout 180000). It builds the UI, replaces any local server on 8000, starts the server and a `cloudflared` quick tunnel in background loops (they restart themselves if they crash), and runs `caffeinate`. macOS shows a password dialog to keep the Mac awake with the lid closed: tell the user to expect it before running. If they cancel, hosting still runs, but closing the lid will sleep the Mac.
2. Take the `https://….trycloudflare.com` link from its output (or `./host.sh status`). If it printed none, check `.host/tunnel.log` and report what it says.
3. Open it: `open -a "Google Chrome" <link>`
4. Reply with the link and one reminder: it changes whenever the tunnel restarts, so check status before sharing it.

## stop cloud

`./host.sh stop`. macOS shows a password dialog to let the Mac sleep again. The server stops too; say "start local" to bring the local one back.

## status

`./host.sh status`, then relay it in one line.
