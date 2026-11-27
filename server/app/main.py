"""main: part of app (split from one module; see __init__.py)."""
import os
import urllib.parse
import swisseph as swe
from core_logic.ephemeris import EphemerisUnavailable
from fastapi import FastAPI, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from .. import auth

# No /docs, /redoc or /openapi.json: they sit outside /api, so they would hand anyone who finds the site a map of every route
app = FastAPI(title="Sudarshana", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(GZipMiddleware, minimum_size=2048)   # the mundane databases run to megabytes of JSON
app.include_router(auth.router)

# The names this site answers to, from the Host header; "*.x" takes any subdomain of x, "*" any name. Others get a 400,
# so a page whose own name has been pointed at 127.0.0.1 (DNS rebinding) can't reach the server. PUBLIC_URL's is always in.
ALLOWED_HOSTS = [h.strip().lower() for h in os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost,*.trycloudflare.com").split(",") if h.strip()]
if urllib.parse.urlsplit(auth.PUBLIC_URL).hostname:
    ALLOWED_HOSTS.append(urllib.parse.urlsplit(auth.PUBLIC_URL).hostname)
MAX_BODY = 2 * 2 ** 20   # bytes; the largest request the app sends is a few hundred KB (themes, a chart, an avatar)
# The page loads its own scripts only, Google Fonts' styles and fonts, and pictures from itself or data:/blob: URLs; no one
# may frame it. Sign in with Google needs nothing more (its flow is redirects); Google's JavaScript button would.
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; "
       "base-uri 'self'; form-action 'self'; frame-ancestors 'none'")
HEADERS = {"Content-Security-Policy": CSP, "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
           "Referrer-Policy": "same-origin", "Cross-Origin-Opener-Policy": "same-origin-allow-popups",
           "Permissions-Policy": "camera=(), microphone=(), payment=(), usb=(), geolocation=(self)"}


def host_ok(name: str) -> bool:
    return any(h == "*" or name == h or (h.startswith("*.") and name.endswith(h[1:])) for h in ALLOWED_HOSTS)


class BodyLimit:
    """A 413 once a request's body passes MAX_BODY, counted as it arrives: a chunked body has no Content-Length to check first."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        seen = 0

        async def counted():
            nonlocal seen
            m = await receive()
            seen += len(m.get("body", b""))
            if seen > MAX_BODY:   # raised inside the route's read of the body, so FastAPI answers it like any HTTPException
                raise HTTPException(413, "That request is too large.")
            return m
        await self.app(scope, counted, send)


# added before signed_in_only, so it sits inside it: raised out there, in its task group, the 413 would come back a 400
app.add_middleware(BodyLimit)


@app.middleware("http")
async def signed_in_only(request, call_next):
    # every request: a host this site answers to; every /api route but /api/auth/* (which check for themselves) and the
    # public /api/sky: a session; the static pages stay public (the sign-in page is one of them); every response: HEADERS
    p = request.url.path
    if p != "/healthz" and not host_ok((request.url.hostname or "").lower()):
        r = PlainTextResponse("Unknown host.", status_code=400)
    elif auth.REQUIRED and p.startswith("/api/") and not p.startswith(("/api/auth/", "/api/sky")) and not auth.user_of(request):
        r = JSONResponse(status_code=401, content={"detail": "Not signed in."})
    else:
        r = await call_next(request)
    r.headers.update(HEADERS)
    if auth.https(request):
        r.headers["Strict-Transport-Security"] = "max-age=31536000"
    return r


@app.get("/healthz", include_in_schema=False)
def healthz():
    """For a load balancer or uptime check: no session, any Host, nothing about the app."""
    return {"ok": True}


@app.exception_handler(swe.Error)
def swiss_ephemeris_error(request, e):
    # e.g. a custom star code the catalogue does not have: say so instead of a bare 500
    return JSONResponse(status_code=422, content={"detail": "Swiss Ephemeris: %s" % e})


@app.exception_handler(EphemerisUnavailable)
def ephemeris_unavailable(request, e):
    # Settings > Ephemeris "XALEN" on a host without its native module or the JPL kernel (core_logic/ephemeris/jpl.py)
    return JSONResponse(status_code=503, content={"detail": str(e)})
