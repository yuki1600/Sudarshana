"""python -m server [--port N]: serve the API and the built web/dist on localhost, open the browser."""
import argparse
import os
import threading
import webbrowser

import uvicorn


def main():
    ap = argparse.ArgumentParser(prog="python -m server")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)))
    # 127.0.0.1 (this Mac only) unless HOST says otherwise: a container sets 0.0.0.0, behind its platform's proxy
    ap.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    ap.add_argument("--no-browser", action="store_true", help="don't open a browser (host.sh runs it in the background)")
    a = ap.parse_args()
    if not a.no_browser:
        threading.Timer(1.0, webbrowser.open, [f"http://127.0.0.1:{a.port}"]).start()
    # proxy headers are trusted from FORWARDED_ALLOW_IPS only (uvicorn's default: 127.0.0.1, which is cloudflared); see .env.example
    uvicorn.run("server.app:app", host=a.host, port=a.port, server_header=False)


if __name__ == "__main__":
    main()
