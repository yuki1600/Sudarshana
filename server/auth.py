"""Accounts: email + password sign-up and sign-in, a session cookie, and the gate that keeps /api/* behind it.
Stdlib only: sqlite3 for storage, scrypt for passwords, urllib for the OAuth calls. password_hash is NULL for an account
made through Google, Facebook, LinkedIn or Microsoft."""
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from . import rodden

REQUIRED = True   # server/tests/__init__.py turns this off so the calculation tests need no account
DB = os.environ.get("ACCOUNTS_DB") or os.path.join(os.path.dirname(__file__), "..", "databases", "accounts.db")
# The site's public address behind a proxy (https://…): the OAuth redirect, and Secure cookies even when the proxy
# hands requests on as plain http. Unset: taken from each request, as on this Mac and through the tunnel.
PUBLIC_URL = os.environ.get("PUBLIC_URL", "").rstrip("/")
COOKIE = "sid"
MAX_AGE = 30 * 24 * 3600
# scrypt cost, OWASP's minimum at 16 MiB a hash; stored with each hash, so older ones still check, and are redone at sign-in
N, R, P = 2 ** 14, 8, 5
TERMS_VERSION = 20261127   # the date of web/src/Terms.tsx's text; raise both together (sign-up records which one was ticked)
TRIES, WINDOW = 10, 15 * 60   # wrong passwords allowed per account and per address before a pause
SIGNUPS = 10                  # new accounts per address in WINDOW
MOST = 10_000                 # rows an account may keep in charts, facts or shared: no one account can fill the disk
# The owner's (admin's) account: its username, a sha256 of its email and a scrypt hash of its password, never the real ones.
# A server with no admin yet (a fresh accounts.db) makes the account from it; the email is learnt at its first sign-in by email.
# OWNER_FILE: another path for it, e.g. a secret the cloud host mounts as a file.
try:
    with open(os.environ.get("OWNER_FILE") or os.path.join(os.path.dirname(__file__), "owner.json")) as _f:
        OWNER = json.load(_f)
except (OSError, ValueError):
    OWNER = None
# The owner's login in plain text, for the sign-in form on this Mac only; git-ignored, so it never leaves this machine
OWNER_LOGIN = os.path.join(os.path.dirname(__file__), "..", ".owner-login.json")
# The sample charts: what a new account's cloud starts with, under Open chart's "Sample charts" (nothing of another account's)
SAMPLES = os.path.join(os.path.dirname(__file__), "..", "data", "sample_charts")
SAMPLE_CATEGORY = "Sample charts"
_SAMPLE_NAME = {"Author of this software": "PVR Narasimha Rao"}   # the file's name for the chart; the list shows the person's name

router = APIRouter(prefix="/api/auth")


@contextmanager
def _db():
    """A connection that commits on success and is always closed."""
    new = not os.path.exists(DB)
    c = sqlite3.connect(DB)
    if new:
        os.chmod(DB, 0o600)   # accounts and their charts: for this server's user alone
    c.row_factory = sqlite3.Row
    c.executescript("""
      CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE COLLATE NOCASE,
        name TEXT NOT NULL, password_hash TEXT, created INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
        created INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS facts (user_id INTEGER NOT NULL REFERENCES users(id), chart_key TEXT NOT NULL,
        data TEXT NOT NULL, updated INTEGER NOT NULL, PRIMARY KEY (user_id, chart_key));
      CREATE TABLE IF NOT EXISTS charts (user_id INTEGER NOT NULL REFERENCES users(id), name TEXT NOT NULL,
        content TEXT NOT NULL, updated INTEGER NOT NULL, PRIMARY KEY (user_id, name));
      CREATE TABLE IF NOT EXISTS shared (id INTEGER PRIMARY KEY, to_id INTEGER NOT NULL REFERENCES users(id),
        from_id INTEGER NOT NULL REFERENCES users(id), name TEXT NOT NULL, content TEXT NOT NULL, updated INTEGER NOT NULL,
        UNIQUE (to_id, from_id, name));
      CREATE TABLE IF NOT EXISTS kept (user_id INTEGER NOT NULL REFERENCES users(id), key TEXT NOT NULL,
        value TEXT NOT NULL, PRIMARY KEY (user_id, key));
    """)
    cols = [r["name"] for r in c.execute("PRAGMA table_info(users)")]
    if "username" not in cols:   # added after the first accounts; NULL for them
        c.executescript("ALTER TABLE users ADD COLUMN username TEXT COLLATE NOCASE; CREATE UNIQUE INDEX users_username ON users (username);")
    if "home" not in cols:       # the default place for new charts, as JSON; NULL until one is chosen
        c.execute("ALTER TABLE users ADD COLUMN home TEXT")
    if "terms" not in cols:      # TERMS_VERSION when the account agreed, and when; NULL until it has
        c.executescript("ALTER TABLE users ADD COLUMN terms INTEGER; ALTER TABLE users ADD COLUMN terms_at INTEGER;")
    if "avatar" not in cols:     # the profile picture as a data: URL, and the saved themes as JSON; NULL until set
        c.executescript("ALTER TABLE users ADD COLUMN avatar TEXT; ALTER TABLE users ADD COLUMN themes TEXT;")
    if "admin" not in cols:      # 1 for the owner's account, NULL for everyone else
        c.execute("ALTER TABLE users ADD COLUMN admin INTEGER")
    if "email_verified" not in cols:   # 1 once a sign-in provider has vouched for the email; NULL for one only typed in
        c.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER")
    if c.execute("PRAGMA user_version").fetchone()[0] < 1:   # sessions held the cookies' tokens: keep only their SHA-256
        c.execute("BEGIN IMMEDIATE")   # one thread migrates; another waits here, then finds it done
        if c.execute("PRAGMA user_version").fetchone()[0] < 1:
            for (t,) in c.execute("SELECT token FROM sessions").fetchall():
                c.execute("UPDATE sessions SET token = ? WHERE token = ?", (_digest(t), t))
            c.execute("PRAGMA user_version = 1")
        c.execute("COMMIT")
    if OWNER and not c.execute("SELECT 1 FROM users WHERE admin = 1").fetchone():
        # "owner" for the email until the first sign-in by email: no real address lacks an "@", so it can't collide
        c.execute("INSERT OR IGNORE INTO users (email, username, name, password_hash, created, terms, terms_at, admin) "
                  "VALUES ('owner', ?, ?, ?, ?, ?, ?, 1)", (OWNER["username"], OWNER["name"], OWNER["password_hash"],
                                                          int(time.time()), TERMS_VERSION, int(time.time())))
    try:
        with c:
            yield c
    finally:
        c.close()


def hash_password(pw: str) -> str:
    salt = secrets.token_bytes(16)
    h = hashlib.scrypt(pw.encode(), salt=salt, n=N, r=R, p=P)
    return f"scrypt${N}${R}${P}${salt.hex()}${h.hex()}"


def check_password(pw: str, stored: str | None) -> bool:
    if not stored:
        return False
    _, n, r, p, salt, h = stored.split("$")
    got = hashlib.scrypt(pw.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p))
    return hmac.compare_digest(got, bytes.fromhex(h))


def _digest(token: str) -> str:
    """What sessions keeps of a cookie's token, so a copy of the database signs no one in."""
    return hashlib.sha256(token.encode()).hexdigest()


def https(request: Request) -> bool:
    """Whether the browser reached the site over https (its cookies are then Secure, and HSTS is sent)."""
    return request.url.scheme == "https" or PUBLIC_URL.startswith("https://")


def user_of(request: Request):
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    with _db() as c:
        return c.execute("SELECT u.id, u.name, u.email, u.username, u.home, u.terms, u.avatar, u.themes, u.admin, u.password_hash IS NOT NULL AS has_pw "
                         "FROM sessions s JOIN users u ON u.id = s.user_id "
                         "WHERE s.token = ? AND s.created > ?", (_digest(token), int(time.time()) - MAX_AGE)).fetchone()


def _theme_now(t: dict) -> dict:
    """A theme saved under an earlier name of the Windows layout or of the swisseph_202 option takes today's."""
    settings, display = dict(t.get("settings") or {}), dict(t.get("display") or {})
    for k in [k for k in settings if k.endswith("_se202")]:
        settings.setdefault("swisseph_202", settings.pop(k))
    if display.get("layout") not in (None, "windows", "starlight"):
        display["layout"] = "windows"
    return {**t, "settings": settings, "display": display}


def _account(u) -> dict:
    """What the browser learns about the signed-in account."""
    return {"name": u["name"], "email": u["email"], "username": u["username"] or "", "home": json.loads(u["home"]) if u["home"] else None,
            "hasPassword": bool(u["has_pw"]), "termsAccepted": u["terms"] == TERMS_VERSION,
            "admin": bool(u["admin"]),   # the owner's: only it may pick the Windows layout and the Praajna colours, for now
            "avatar": u["avatar"], "themes": [_theme_now(t) for t in json.loads(u["themes"])] if u["themes"] else []}


# shortcut: in memory, so a restart forgets them and each server process counts its own; move to the database or the
# host's rate limiting before running more than one instance
_fails: dict[str, list[float]] = {}


def _guard(keys: list[str], ok) -> None:
    """Refuse once any key has TRIES wrong passwords in the last WINDOW; otherwise count this try when ``ok`` is false."""
    now = time.time()
    if len(_fails) > 10_000:   # someone trying many names: forget the keys with nothing recent
        for k, ts in list(_fails.items()):
            if not ts or ts[-1] <= now - WINDOW:
                _fails.pop(k, None)
    for k in keys:
        _fails[k] = [t for t in _fails.get(k, []) if t > now - WINDOW]
        if len(_fails[k]) >= TRIES:
            raise HTTPException(429, "Too many wrong passwords. Wait 15 minutes and try again.")
    if not ok():
        for k in keys:
            _fails[k].append(now)
        raise HTTPException(401, "That password isn't right.")


def _throttle(key: str, most: int) -> None:
    """Count this try under key, and refuse it when it is more than ``most`` in the last WINDOW."""
    now = time.time()
    _fails[key] = hits = [t for t in _fails.get(key, []) if t > now - WINDOW] + [now]
    if len(hits) > most:
        raise HTTPException(429, "Too many tries from here. Wait 15 minutes and try again.")


def _client(request: Request) -> str:
    # uvicorn takes it from X-Forwarded-For when the proxy's address is in FORWARDED_ALLOW_IPS (cloudflared's 127.0.0.1 is)
    return "ip:" + (request.client.host if request.client else "")


def _check_names(name: str, username: str):
    if not name:
        raise HTTPException(422, "Enter your name.")
    if len(name) > 100:
        raise HTTPException(422, "Use a name of at most 100 characters.")
    if username and not re.fullmatch(r"[A-Za-z0-9_.-]{2,32}", username):   # no "@", so it never reads as an email
        raise HTTPException(422, "Use 2 to 32 letters, digits, dots, dashes or underscores for a username.")


def _first_name_username(c, name: str) -> str | None:
    """The first name as a username (only its letters, digits, dots, dashes and underscores), with 2, 3... after it
    when taken; None when too little of it is left, as for a name in another script."""
    base = re.sub(r"[^A-Za-z0-9_.-]", "", (name.split() or [""])[0])[:29]
    if len(base) < 2:
        return None
    for n in ["", *range(2, 1000)]:
        if not c.execute("SELECT 1 FROM users WHERE username = ?", (f"{base}{n}",)).fetchone():
            return f"{base}{n}"
    return None


def _start_session(request: Request, response: Response, user_id: int):
    token, now = secrets.token_urlsafe(32), int(time.time())
    with _db() as c:
        c.execute("DELETE FROM sessions WHERE created <= ?", (now - MAX_AGE,))   # expired ones, anyone's
        c.execute("INSERT INTO sessions VALUES (?, ?, ?)", (_digest(token), user_id, now))
    response.set_cookie(COOKIE, token, max_age=MAX_AGE, httponly=True, samesite="lax", secure=https(request))


def _check_room(c, table: str, owner: str, uid: int, **key) -> None:
    """Refuse a new row once an account holds MOST in this table; overwriting a row under the same key is no new row."""
    if c.execute(f"SELECT count(*) FROM {table} WHERE {owner} = ?", (uid,)).fetchone()[0] < MOST:
        return
    same = " AND ".join(f"{k} = ?" for k in key)
    if not c.execute(f"SELECT 1 FROM {table} WHERE {owner} = ? AND {same}", (uid, *key.values())).fetchone():
        raise HTTPException(422, "That is as many as one account can keep. Delete some first.")


class SignUp(BaseModel):
    name: str
    email: str = Field(max_length=254)
    password: str = Field(max_length=256)
    username: str = ""   # optional
    terms: int = 0       # the TERMS_VERSION the person ticked the box for


class SignIn(BaseModel):
    email: str   # or the username
    password: str = Field(max_length=256)


_samples: tuple[str, list[tuple[str, str]]] | None = None   # (the folder, its charts): read once


def sample_charts() -> list[tuple[str, str]]:
    """The sample charts as (name, .vs file), as export_jhd writes one, each under SAMPLE_CATEGORY; a file it can't read is left out."""
    global _samples
    if _samples is None or _samples[0] != SAMPLES:
        from datetime import datetime, timezone
        from core_logic import jhd_io
        from .jsonenc import to_jsonable
        out, at = [], datetime.now(timezone.utc).isoformat(timespec="seconds")
        for f in sorted(os.listdir(SAMPLES)) if os.path.isdir(SAMPLES) else []:
            if not f.endswith(".jhd"):
                continue
            try:
                with open(os.path.join(SAMPLES, f), encoding="utf-8", errors="ignore") as fh:
                    p = jhd_io.parse_jhd_string(fh.read())
                name = _SAMPLE_NAME.get(f[:-4], f[:-4])
                vs = {"format": "sudarshana-chart", "version": 1, "app": "Sudarshana", "saved_utc": at, "name": name,
                      "birth": to_jsonable(jhd_io.to_birth_data(p)),
                      "meta": {"city": p.get("city") or "", "state": p.get("state") or "", "country": p.get("country") or "", "dst": bool(p.get("dst")),
                               "tz_standard_east": p["tz_standard_east"], "tz_dst_east": p["tz_dst_east"], "gender": p.get("field18") or 0},
                      "notes": "", "category": SAMPLE_CATEGORY}
            except (OSError, ValueError, KeyError, IndexError):
                continue
            out.append((name, json.dumps(vs, indent=2, ensure_ascii=False) + "\n"))
        _samples = (SAMPLES, out)
    return _samples[1]


def _give_samples(c, uid: int) -> None:
    """A new account's first cloud charts: the sample charts, its own to keep, rename or delete."""
    now = int(time.time())
    c.executemany("INSERT OR IGNORE INTO charts (user_id, name, content, updated) VALUES (?, ?, ?, ?)", [(uid, n, v, now) for n, v in sample_charts()])


def _check_terms(version: int):
    if not version:
        raise HTTPException(422, "Agree to the Terms of Service to go on.")
    if version != TERMS_VERSION:
        raise HTTPException(409, "The Terms of Service have changed. Reload the page to read them.")


@router.post("/signup")
def signup(body: SignUp, request: Request, response: Response):
    _throttle("signup:" + _client(request), SIGNUPS)
    name, email, username = body.name.strip(), body.email.strip(), body.username.strip()
    _check_names(name, username)
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(422, "Enter an email address like name@example.com.")
    if len(body.password) < 8:
        raise HTTPException(422, "Use a password of at least 8 characters.")
    _check_terms(body.terms)
    now = int(time.time())
    try:
        with _db() as c:
            username = username or _first_name_username(c, name) or ""   # left blank: the first name
            uid = c.execute("INSERT INTO users (email, username, name, password_hash, created, terms, terms_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (email, username or None, name, hash_password(body.password), now, TERMS_VERSION, now)).lastrowid
            _give_samples(c, uid)
    except sqlite3.IntegrityError as e:
        raise HTTPException(409, "That username is taken." if "username" in str(e) else "An account with this email already exists.")
    _start_session(request, response, uid)
    return {"name": name, "email": email, "username": username, "home": None, "hasPassword": True, "termsAccepted": True, "admin": False, "avatar": None, "themes": []}


@router.post("/login")
def login(body: SignIn, request: Request, response: Response):
    who = body.email.strip()
    owner = bool(OWNER) and hmac.compare_digest(hashlib.sha256(who.lower().encode()).hexdigest(), OWNER["email_sha256"])
    with _db() as c:
        u = c.execute("SELECT id, name, email, username, home, terms, avatar, themes, admin, password_hash, password_hash IS NOT NULL AS has_pw "
                      "FROM users WHERE " + ("admin = 1" if owner else "email = :id OR username = :id"), {"id": who}).fetchone()
    try:
        _guard(["id:" + who.lower(), _client(request)], lambda: u is not None and check_password(body.password, u["password_hash"]))
    except HTTPException as e:
        if e.status_code == 401:
            raise HTTPException(401, "That email and password don't match an account.")
        raise
    if owner and u["email"].lower() != who.lower():   # a fresh server's admin learns its real email here
        with _db() as c:
            c.execute("UPDATE users SET email = ? WHERE id = ?", (who, u["id"]))
        u = {**dict(u), "email": who}
    if not u["password_hash"].startswith(f"scrypt${N}${R}${P}$"):   # hashed at an older cost: redo it while the password is at hand
        with _db() as c:
            c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(body.password), u["id"]))
    _start_session(request, response, u["id"])
    return _account(u)


@router.get("/owner-login")
def owner_login(request: Request):
    """The owner's login for the sign-in form, only when the page is opened on this machine itself: never through the
    Cloudflare tunnel (which adds CF-Connecting-IP) or any other proxy. Null when not, or when there is no such file."""
    if request.url.hostname not in ("127.0.0.1", "localhost") or "cf-connecting-ip" in request.headers or "x-forwarded-for" in request.headers:
        return None
    try:
        with open(OWNER_LOGIN) as f:
            d = json.load(f)
        return {"email": str(d["email"]), "password": str(d["password"])}
    except (OSError, ValueError, KeyError, TypeError):
        return None


@router.post("/logout")
def logout(request: Request, response: Response):
    with _db() as c:
        c.execute("DELETE FROM sessions WHERE token = ?", (_digest(request.cookies.get(COOKIE, "")),))
    response.delete_cookie(COOKIE)
    return {}


@router.get("/me")
def me(request: Request):
    u = user_of(request)   # null when signed out: a 200, so the browser logs no error for the everyday case
    return _account(u) if u else None


class Home(BaseModel):
    """The default place for new charts, as the web app keeps it: coordinates, zone, height, and the place's names."""
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    tz: float = Field(ge=-14, le=14)
    alt: float = 0
    meta: dict = {}


class HomeIn(BaseModel):
    home: Home | None   # null: none chosen; new charts ask the browser where it is


@router.put("/home")
def set_home(body: HomeIn, request: Request):
    u = user_of(request)   # /api/auth/* is outside the gate, so this one checks for itself
    if not u:
        raise HTTPException(401, "Sign in first.")
    blob = body.home.model_dump_json() if body.home else None
    if blob and len(blob) > 4000:
        raise HTTPException(422, "That place has too much attached to it.")
    with _db() as c:
        c.execute("UPDATE users SET home = ? WHERE id = ?", (blob, u["id"]))
    return {"home": body.home}


class AvatarIn(BaseModel):
    avatar: str | None = Field(None, max_length=200_000)   # the browser shrinks the picture to 128 px first; null: none


@router.put("/avatar")
def set_avatar(body: AvatarIn, request: Request):
    u = _signed_in(request)
    if body.avatar and not re.fullmatch(r"data:image/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+", body.avatar):
        raise HTTPException(422, "Use a PNG, JPEG or WebP picture.")
    with _db() as c:
        c.execute("UPDATE users SET avatar = ? WHERE id = ?", (body.avatar, u["id"]))
    return me(request)


class ThemeIn(BaseModel):
    """A theme the user made: their settings, chart style and display, under a name (web/src/Account.tsx)."""
    name: str = Field(min_length=1, max_length=60)
    settings: dict = {}
    chartStyle: str = "south"
    display: dict = {}


class ThemesIn(BaseModel):
    themes: list[ThemeIn] = Field(max_length=50)


@router.put("/themes")
def set_themes(body: ThemesIn, request: Request):
    u = _signed_in(request)
    blob = json.dumps([t.model_dump() for t in body.themes])
    if len(blob) > 500_000:
        raise HTTPException(422, "Too much to keep in themes.")
    with _db() as c:
        c.execute("UPDATE users SET themes = ? WHERE id = ?", (blob, u["id"]))
    return me(request)


def _signed_in(request: Request):
    u = user_of(request)   # /api/auth/* is outside the gate, so these check for themselves
    if not u:
        raise HTTPException(401, "Sign in first.")
    return u


class AccountIn(BaseModel):
    name: str
    username: str = ""


@router.put("/account")
def update_account(body: AccountIn, request: Request):
    u = _signed_in(request)
    name, username = body.name.strip(), body.username.strip()
    _check_names(name, username)
    try:
        with _db() as c:
            c.execute("UPDATE users SET name = ?, username = ? WHERE id = ?", (name, username or None, u["id"]))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "That username is taken.")
    return me(request)


class PasswordIn(BaseModel):
    current: str = Field("", max_length=256)   # empty for an account made through a social sign-in, which has none yet
    new: str = Field(max_length=256)


def _own_password(request: Request, u, password: str):
    """Ask for the account's password again before a change that matters; an account without one has nothing to ask."""
    with _db() as c:
        stored = c.execute("SELECT password_hash FROM users WHERE id = ?", (u["id"],)).fetchone()["password_hash"]
    if stored:
        _guard(["user:%d" % u["id"], _client(request)], lambda: check_password(password, stored))


@router.put("/password")
def change_password(body: PasswordIn, request: Request):
    """A new password; every other signed-in device is signed out, this one stays."""
    u = _signed_in(request)
    if len(body.new) < 8:
        raise HTTPException(422, "Use a new password of at least 8 characters.")
    _own_password(request, u, body.current)
    with _db() as c:
        c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(body.new), u["id"]))
        c.execute("DELETE FROM sessions WHERE user_id = ? AND token != ?", (u["id"], _digest(request.cookies.get(COOKIE, ""))))
    return me(request)


@router.post("/logout-all")
def logout_all(request: Request, response: Response):
    u = _signed_in(request)
    with _db() as c:
        c.execute("DELETE FROM sessions WHERE user_id = ?", (u["id"],))
    response.delete_cookie(COOKIE)
    return {}


class DeleteIn(BaseModel):
    password: str = Field("", max_length=256)


@router.delete("/account")
def delete_account(body: DeleteIn, request: Request, response: Response):
    """The account and everything kept with it: saved charts, life facts, sessions. Not undoable."""
    u = _signed_in(request)
    _own_password(request, u, body.password)
    with _db() as c:
        for table in ("facts", "charts", "kept", "sessions"):
            c.execute(f"DELETE FROM {table} WHERE user_id = ?", (u["id"],))
        c.execute("DELETE FROM shared WHERE to_id = ? OR from_id = ?", (u["id"], u["id"]))
        c.execute("DELETE FROM users WHERE id = ?", (u["id"],))
    response.delete_cookie(COOKIE)
    return {}


def reset_password(who: str, password: str) -> bool:
    """For the owner, when someone has forgotten theirs and writes in: ``python -m server.auth reset <email or username>``.
    Signs that account out everywhere. False when no account matches."""
    if len(password) < 8:
        raise ValueError("Use a password of at least 8 characters.")
    with _db() as c:
        u = c.execute("SELECT id FROM users WHERE email = :id OR username = :id", {"id": who.strip()}).fetchone()
        if not u:
            return False
        c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(password), u["id"]))
        c.execute("DELETE FROM sessions WHERE user_id = ?", (u["id"],))
    return True


class FactsIn(BaseModel):
    key: str = Field(min_length=1, max_length=300)   # the chart's name and birth date (web/src/lifeFacts.ts chartKey)
    data: dict


@router.get("/facts")
def get_facts(key: str, request: Request):
    """The life facts the Predictions tab collected for one chart of this account; before any, a Rodden library chart's
    own (from its biography and events), else null."""
    u = _signed_in(request)
    with _db() as c:
        row = c.execute("SELECT data FROM facts WHERE user_id = ? AND chart_key = ?", (u["id"], key)).fetchone()
    return {"data": json.loads(row["data"]) if row else rodden.facts(key)}


@router.put("/facts")
def set_facts(body: FactsIn, request: Request):
    u = _signed_in(request)
    blob = json.dumps(body.data)
    if len(blob) > 65536:
        raise HTTPException(422, "Too much to keep for one chart.")
    with _db() as c:
        _check_room(c, "facts", "user_id", u["id"], chart_key=body.key)
        c.execute("INSERT INTO facts (user_id, chart_key, data, updated) VALUES (?, ?, ?, ?) "
                  "ON CONFLICT (user_id, chart_key) DO UPDATE SET data = excluded.data, updated = excluded.updated",
                  (u["id"], body.key, blob, int(time.time())))
    return {"data": body.data}



class ChartIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=200_000)   # a .vs file's text


def _summary(content: str) -> dict:
    """What the Open chart list shows of a saved .vs file: the birth moment and place; empty for one it can't read."""
    try:
        d = json.loads(content)
        b, m = d.get("birth") or {}, d.get("meta") or {}
        return {"year": b["year"], "month": b["month"], "day": b["day"], "hour": b.get("hour_local"), "tz": b.get("tz_east_hours"),
                "place": m.get("city") or b.get("place") or "", "state": m.get("state") or "", "country": m.get("country") or "",
                "notes": bool((d.get("notes") or "").strip()),
                # the rest of what the file keeps, so the app can tell an open chart edited since it was saved
                "lat": b.get("latitude"), "lon": b.get("longitude_east"), "city": m.get("city") or "", "dst": bool(m.get("dst")),
                "gender": m.get("gender") or 0, "noteText": (d.get("notes") or "").strip(), "category": str(d.get("category") or "")}
    except (ValueError, KeyError, TypeError, AttributeError):
        return {}


@router.get("/charts")
def list_charts(request: Request):
    """The charts this account saved in the cloud, newest first, each with its birth moment and place."""
    u = _signed_in(request)
    with _db() as c:
        rows = c.execute("SELECT name, updated, content FROM charts WHERE user_id = ? ORDER BY updated DESC", (u["id"],)).fetchall()
    return [{"name": r["name"], "updated": r["updated"], **_summary(r["content"])} for r in rows]


@router.get("/chart")
def get_chart(name: str, request: Request):
    u = _signed_in(request)
    with _db() as c:
        row = c.execute("SELECT content FROM charts WHERE user_id = ? AND name = ?", (u["id"], name)).fetchone()
    if not row:
        raise HTTPException(404, "No chart of that name in the cloud.")
    return {"name": name, "content": row["content"]}


def _keep_category(old: str | None, new: str) -> str:
    """A chart saved again from the app has no category in its file: it keeps the one it was saved under."""
    try:
        was, d = json.loads(old or "{}").get("category"), json.loads(new)
    except (ValueError, AttributeError):
        return new
    if not was or not isinstance(d, dict) or "category" in d:
        return new
    return json.dumps({**d, "category": was}, indent=2, ensure_ascii=False) + "\n"


@router.put("/chart")
def put_chart(body: ChartIn, request: Request):
    """Save a chart under its name; the same name again overwrites it, keeping its category."""
    u = _signed_in(request)
    with _db() as c:
        _check_room(c, "charts", "user_id", u["id"], name=body.name)
        old = c.execute("SELECT content FROM charts WHERE user_id = ? AND name = ?", (u["id"], body.name)).fetchone()
        content = _keep_category(old["content"] if old else None, body.content)
        c.execute("INSERT INTO charts (user_id, name, content, updated) VALUES (?, ?, ?, ?) "
                  "ON CONFLICT (user_id, name) DO UPDATE SET content = excluded.content, updated = excluded.updated",
                  (u["id"], body.name, content, int(time.time())))
    return {"name": body.name}


class RenameIn(BaseModel):
    old: str = Field(min_length=1, max_length=200)
    new: str = Field(min_length=1, max_length=200)


@router.post("/chart/rename")
def rename_chart(body: RenameIn, request: Request):
    """Give a saved chart another name; refused when that name is taken, so nothing is overwritten."""
    u = _signed_in(request)
    with _db() as c:
        row = c.execute("SELECT content FROM charts WHERE user_id = ? AND name = ?", (u["id"], body.old)).fetchone()
        if not row:
            raise HTTPException(404, "No chart of that name in the cloud.")
        if body.new != body.old and c.execute("SELECT 1 FROM charts WHERE user_id = ? AND name = ?", (u["id"], body.new)).fetchone():
            raise HTTPException(409, "A chart called \"%s\" is already saved." % body.new)
        content = row["content"]
        try:   # the name inside the .vs file follows, so a download carries the new one
            d = json.loads(content)
            d["name"] = body.new
            content = json.dumps(d, indent=2)
        except (ValueError, TypeError):
            pass
        c.execute("UPDATE charts SET name = ?, content = ?, updated = ? WHERE user_id = ? AND name = ?",
                  (body.new, content, int(time.time()), u["id"], body.old))
    return {"name": body.new}


@router.delete("/chart")
def delete_chart(name: str, request: Request):
    u = _signed_in(request)
    with _db() as c:
        c.execute("DELETE FROM charts WHERE user_id = ? AND name = ?", (u["id"], name))
    return {"name": name}

# ---- What the web app used to keep only in the browser's localStorage (open charts, recents, settings, what is on
# screen), kept per account on this server's disk too, so a new browser or Mac opens where the last one left off.

KEPT_MOST = 8 * 2 ** 20   # bytes of it an account may keep; this Mac's own is ~0.1 MB


@router.get("/state")
def get_state(request: Request):
    u = user_of(request)   # null when signed out, like /me: the web app asks before it knows
    if not u:
        return None
    with _db() as c:
        rows = c.execute("SELECT key, value FROM kept WHERE user_id = ?", (u["id"],)).fetchall()
    return {"user": u["id"], "data": {r["key"]: r["value"] for r in rows}}


class StateIn(BaseModel):
    changes: dict[str, str | None]   # null removes the key
    user: int | None = None          # the account the page pulled its state from: another tab may since have signed in as another


@router.put("/state")
def put_state(body: StateIn, request: Request):
    u = _signed_in(request)
    if body.user is not None and body.user != u["id"]:   # a page still showing another account's charts: none of it into this one
        raise HTTPException(409, "This page belongs to another account. Reload it.")
    if any(not k or len(k) > 200 for k in body.changes):
        raise HTTPException(422, "A key is empty or too long.")
    with _db() as c:
        for k, v in body.changes.items():
            if v is None:
                c.execute("DELETE FROM kept WHERE user_id = ? AND key = ?", (u["id"], k))
            else:
                c.execute("INSERT INTO kept (user_id, key, value) VALUES (?, ?, ?) "
                          "ON CONFLICT (user_id, key) DO UPDATE SET value = excluded.value", (u["id"], k, v))
        size = c.execute("SELECT coalesce(sum(length(key) + length(value)), 0) FROM kept WHERE user_id = ?", (u["id"],)).fetchone()[0]
        if size > KEPT_MOST or c.execute("SELECT count(*) FROM kept WHERE user_id = ?", (u["id"],)).fetchone()[0] > MOST:
            raise HTTPException(422, "That is more than one account can keep.")   # raised inside the transaction: rolled back
    return {}

# ---- Sharing: a copy of a saved chart goes to another account, found by its username; it shows in their Open chart > Shared.

@router.get("/users")
def find_users(q: str, request: Request):
    """Accounts whose username starts with q (two letters at least), for the share box: username and name only."""
    u = _signed_in(request)
    q = q.strip().lstrip("@")
    if len(q) < 2:
        return []
    like = re.sub(r"([\\%_])", r"\\\1", q) + "%"
    with _db() as c:
        rows = c.execute("SELECT username, name FROM users WHERE username LIKE ? ESCAPE '\\' AND id != ? ORDER BY username LIMIT 8",
                         (like, u["id"])).fetchall()
    return [{"username": r["username"], "name": r["name"]} for r in rows]


class ShareIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    to: str = Field(min_length=1, max_length=100)


@router.post("/chart/share")
def share_chart(body: ShareIn, request: Request):
    """Send a copy of this account's saved chart to the account with that username; sending it again replaces their copy."""
    u = _signed_in(request)
    with _db() as c:
        row = c.execute("SELECT content FROM charts WHERE user_id = ? AND name = ?", (u["id"], body.name)).fetchone()
        if not row:
            raise HTTPException(404, "No chart of that name in the cloud.")
        to = c.execute("SELECT id, username FROM users WHERE username = ?", (body.to.strip().lstrip("@"),)).fetchone()
        if not to:
            raise HTTPException(404, "No user with that ID.")
        if to["id"] == u["id"]:
            raise HTTPException(400, "That is your own account.")
        _check_room(c, "shared", "to_id", to["id"], from_id=u["id"], name=body.name)   # no one can flood another's list
        c.execute("INSERT INTO shared (to_id, from_id, name, content, updated) VALUES (?, ?, ?, ?, ?) "
                  "ON CONFLICT (to_id, from_id, name) DO UPDATE SET content = excluded.content, updated = excluded.updated",
                  (to["id"], u["id"], body.name, row["content"], int(time.time())))
    return {"name": body.name, "to": to["username"]}


@router.get("/shared")
def list_shared(request: Request):
    """Charts other accounts shared with this one, newest first, each with who sent it."""
    u = _signed_in(request)
    with _db() as c:
        rows = c.execute("SELECT s.id, s.name, s.updated, s.content, f.username, f.name AS from_name FROM shared s "
                         "JOIN users f ON f.id = s.from_id WHERE s.to_id = ? ORDER BY s.updated DESC", (u["id"],)).fetchall()
    return [{"id": r["id"], "name": r["name"], "updated": r["updated"], "from": r["username"] or r["from_name"], **_summary(r["content"])} for r in rows]


@router.get("/shared/{sid}")
def get_shared(sid: int, request: Request):
    u = _signed_in(request)
    with _db() as c:
        row = c.execute("SELECT name, content FROM shared WHERE id = ? AND to_id = ?", (sid, u["id"])).fetchone()
    if not row:
        raise HTTPException(404, "No such shared chart.")
    return {"name": row["name"], "content": row["content"]}


@router.delete("/shared/{sid}")
def delete_shared(sid: int, request: Request):
    """Take a shared chart off this account's list; the sender's own copy stays."""
    u = _signed_in(request)
    with _db() as c:
        c.execute("DELETE FROM shared WHERE id = ? AND to_id = ?", (sid, u["id"]))
    return {}


# ---- Sign in with Google / Facebook / LinkedIn / Microsoft: the OAuth 2 authorization-code flow.
# Each provider is switched on by OAUTH_<NAME>_ID and OAUTH_<NAME>_SECRET in the environment (an app registered on the
# provider's developer console, its redirect URI set to <site>/api/auth/oauth/<name>/callback). A provider's sign-in
# lands on the account with the same email, or makes one, but only for an email the provider says it has verified:
# otherwise anyone could claim someone else's address there and walk into their account here.
PROVIDERS = {
    # pkce: the provider takes a PKCE challenge from a web server app (RFC 7636), so a stolen code is useless without the verifier
    "google": dict(label="Google", scope="openid email profile", pkce=True,
                   authorize="https://accounts.google.com/o/oauth2/v2/auth", token="https://oauth2.googleapis.com/token",
                   userinfo="https://openidconnect.googleapis.com/v1/userinfo"),
    "facebook": dict(label="Facebook", scope="email public_profile",
                     authorize="https://www.facebook.com/v19.0/dialog/oauth", token="https://graph.facebook.com/v19.0/oauth/access_token",
                     userinfo="https://graph.facebook.com/v19.0/me?fields=name,email"),
    "linkedin": dict(label="LinkedIn", scope="openid profile email",
                     authorize="https://www.linkedin.com/oauth/v2/authorization", token="https://www.linkedin.com/oauth/v2/accessToken",
                     userinfo="https://api.linkedin.com/v2/userinfo"),
    # shortcut: "consumers" takes personal accounts only (Outlook, Hotmail, Live, Xbox), whose email Microsoft has verified;
    # a work or school tenant can set any email unverified, so before opening it to them, check the xms_edov claim
    "microsoft": dict(label="Microsoft", scope="openid email profile", pkce=True,
                      authorize="https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize",
                      token="https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
                      userinfo="https://graph.microsoft.com/oidc/userinfo"),
}
OAUTH_COOKIE = "oauth"


def _creds(name: str):
    k = name.upper()
    cid, secret = os.environ.get(f"OAUTH_{k}_ID"), os.environ.get(f"OAUTH_{k}_SECRET")
    return (cid, secret) if cid and secret else None


def _redirect_uri(request: Request, name: str) -> str:
    # behind a proxy the request may look like plain http, but the provider must get the public URL it has on file
    return f"{(PUBLIC_URL or str(request.base_url)).rstrip('/')}/api/auth/oauth/{name}/callback"


def _back(q: str) -> str:
    """The sign-in page's own query string (so ?garden survives the trip); only ever a query on "/", never another site."""
    return q if q.startswith("?") and "\n" not in q and "\r" not in q else ""


def _home(back: str, error: str | None = None) -> RedirectResponse:
    if error:
        back = (back + "&" if back else "?") + urllib.parse.urlencode({"auth_error": error})
    return RedirectResponse("/" + back, status_code=303)


def _fetch(url: str, data: dict | None = None, token: str | None = None):
    """JSON from a provider: a form POST with data, else a GET; with token, as that user."""
    req = urllib.request.Request(url, urllib.parse.urlencode(data).encode() if data else None,
                                 {"Accept": "application/json", "User-Agent": "Sudarshana"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def _verified_email(name: str, info: dict) -> str | None:
    if name in ("google", "linkedin"):   # OpenID Connect: the provider says outright
        return info.get("email") if info.get("email_verified") in (True, "true") else None
    if name in ("facebook", "microsoft"):   # both hand over only an email the person has confirmed (Microsoft: personal accounts)
        return info.get("email")
    return None


@router.get("/oauth/{name}")
def oauth_start(name: str, request: Request, back: str = ""):
    p, back = PROVIDERS.get(name), _back(back)
    if not p:
        raise HTTPException(404, "No such sign-in provider.")
    creds = _creds(name)
    if not creds:
        return _home(back, f"Sign in with {p['label']} isn't set up on this server yet.")
    state, verifier = secrets.token_urlsafe(24), secrets.token_urlsafe(48)
    q = {"client_id": creds[0], "redirect_uri": _redirect_uri(request, name), "response_type": "code", "scope": p["scope"], "state": state}
    if p.get("pkce"):
        q.update(code_challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode(),
                 code_challenge_method="S256")
    r = RedirectResponse(p["authorize"] + "?" + urllib.parse.urlencode(q), status_code=303)
    # the state comes back on the callback and must match this cookie, so no other site can complete a sign-in for you
    r.set_cookie(OAUTH_COOKIE, f"{state} {verifier} {back}", max_age=600, httponly=True, samesite="lax", secure=https(request))
    return r


@router.get("/oauth/{name}/callback")
def oauth_callback(name: str, request: Request, code: str = "", state: str = "", error: str = ""):
    p, creds = PROVIDERS.get(name), _creds(name)
    if not p or not creds:
        raise HTTPException(404, "No such sign-in provider.")
    saved, _, rest = request.cookies.get(OAUTH_COOKIE, "").partition(" ")
    verifier, _, back = rest.partition(" ")
    back = _back(back)
    if error:   # the person said no on the provider's page
        return _home(back, f"Sign in with {p['label']} was cancelled.")
    if not saved or not state or not hmac.compare_digest(saved, state) or not code:
        return _home(back, "That sign-in link has expired. Try again.")
    form = {"client_id": creds[0], "client_secret": creds[1], "code": code, "grant_type": "authorization_code",
            "redirect_uri": _redirect_uri(request, name)}
    if p.get("pkce"):
        form["code_verifier"] = verifier
    try:
        token = _fetch(p["token"], form)["access_token"]
        info = _fetch(p["userinfo"], token=token)
        email = _verified_email(name, info)
    except (urllib.error.URLError, OSError, KeyError, ValueError):
        return _home(back, f"Couldn't finish signing in with {p['label']}. Try again.")
    if not email:
        return _home(back, f"Your {p['label']} account has no verified email address, so it can't sign you in here.")
    with _db() as c:
        u = c.execute("SELECT id, email_verified, admin FROM users WHERE email = ?", (email,)).fetchone()
        if not u:
            full = info.get("name") or info.get("login") or email.split("@")[0]
            uid = c.execute("INSERT INTO users (email, username, name, created, email_verified) VALUES (?, ?, ?, ?, 1)",
                            (email, _first_name_username(c, full), full, int(time.time()))).lastrowid
            _give_samples(c, uid)
        else:
            uid = u["id"]
            if not u["email_verified"] and not u["admin"]:
                # Made at sign-up by typing this email in, which proves nothing: it may be someone else's, waiting for its owner
                # to arrive this way (account pre-hijacking). The provider has just shown the email is this person's, so the
                # password set then, and every device signed in with it, go; they can set a new one under Settings > Account.
                c.execute("UPDATE users SET password_hash = NULL, email_verified = 1 WHERE id = ?", (uid,))
                c.execute("DELETE FROM sessions WHERE user_id = ?", (uid,))
    r = _home(back)
    r.delete_cookie(OAUTH_COOKIE)
    _start_session(request, r, uid)
    return r


if __name__ == "__main__":
    import getpass
    import sys
    if len(sys.argv) != 3 or sys.argv[1] != "reset":
        sys.exit("usage: python -m server.auth reset <email or username>")
    pw = getpass.getpass("New password: ")
    if pw != getpass.getpass("Again: "):
        sys.exit("The two don't match; nothing changed.")
    try:
        found = reset_password(sys.argv[2], pw)
    except ValueError as e:
        sys.exit(str(e))
    if not found:
        sys.exit("No account with that email or username.")
    print("Done. Tell them the new password; they can change it under Settings > Account.")
