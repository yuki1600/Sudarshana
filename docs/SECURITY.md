# Security

How the app protects its accounts and the personal data in them, what to set before it runs in the cloud, and what is
still open. Last reviewed 2026-11-19. The settings named here are all in [`.env.example`](../.env.example).

## What there is to protect

- **Accounts:** email, name, username, scrypt password hash, sessions. One of them is the owner's admin account.
- **Personal data:** birth date, time and place of the account holder and of everyone whose chart they save; the
  Predictions tab's life facts (parents, marriage, children, illnesses, events); notes; the profile picture; the web
  app's localStorage kept with the account (open and recent charts, settings, what was on screen: `kept`, `/api/auth/state`).
- **The server:** sign-up is open, so anyone who reaches the site can make an account and run the calculations.

| How it runs | Who can reach it |
|---|---|
| `./start.sh` | This Mac only (127.0.0.1:8000). |
| `./host.sh` | Anyone with the `trycloudflare.com` link: the sign-in page, `/api/sky`, sign-up and sign-in; everything else after signing in. |
| A cloud host ([`Dockerfile`](../Dockerfile)) | The internet, through the platform's proxy. |

## What is in place

| Area | What the app does | Where |
|---|---|---|
| Sign-in gate | Every `/api/*` route needs a session, except `/api/sky` (public sky for the sign-in page) and `/api/auth/*`, whose routes check for themselves. | `server/app/main.py` `signed_in_only` |
| Passwords | scrypt N=2^14, r=8, p=5 (OWASP's minimum), 16-byte salt, constant-time compare; hashes at an older cost are redone at sign-in. 8 to 256 characters. | `server/auth.py` |
| Sessions | 256-bit random token in an HttpOnly, SameSite=Lax cookie, Secure over https. The database keeps only its SHA-256, so a copy of it signs no one in. 30 days; expired rows are purged. Sign out, sign out everywhere, and a password change signs out the other devices. | `server/auth.py` |
| Guessing | 10 wrong passwords per account and per address in 15 minutes, then a pause; 10 sign-ups per address in 15 minutes. | `server/auth.py` `_guard`, `_throttle` |
| Sign in with a provider | Authorization-code flow; `state` bound to an HttpOnly cookie; PKCE (S256) for Google and Microsoft; only an email the provider has verified. An account made at sign-up by typing that email is taken over by the provider-verified owner: its password and every session on it are revoked (account pre-hijacking). | `server/auth.py` `oauth_*` |
| Redirects | After sign-in, only to a query string on `/`, never another site. | `server/auth.py` `_back` |
| CSRF | SameSite=Lax cookies, so another site's forms and scripts don't carry them (`trycloudflare.com` and `*.run.app` are public suffixes: each tunnel or service is its own site); the routes that take a body want JSON, which FastAPI refuses from a plain form; no CORS headers, so no other site can read a response. | |
| XSS | React escapes all text; no `dangerouslySetInnerHTML`, `innerHTML` or `eval` in `web/src`; a profile picture must be a PNG, JPEG or WebP `data:` URL (no SVG); CSP `script-src 'self'`. | `web/src`, `server/auth.py` `set_avatar` |
| Headers | Content-Security-Policy (own scripts, Google Fonts, `data:`/`blob:` pictures, no framing), X-Frame-Options DENY, nosniff, Referrer-Policy same-origin, COOP same-origin-allow-popups, Permissions-Policy, HSTS over https; no `Server` header. | `server/app/main.py` `HEADERS` |
| Host names | Only those in `ALLOWED_HOSTS` (default: this Mac and the quick tunnel; `PUBLIC_URL`'s is added), against DNS rebinding. `/healthz` answers any host. | `server/app/main.py` |
| Input | Request models with ranges and fixed choices; bodies up to 2 MB, chunked ones too; place search up to 100 rows; finance spans capped; each account keeps at most 10 000 saved charts, fact sets and incoming shares, and 10 000 keys or 8 MB of kept browser state. | `server/app/*.py`, `server/auth.py` `_check_room` |
| Data between accounts | Every account query filters by the session's user. A new account's cloud starts with the sample charts alone (`data/sample_charts`, its own copies), never another account's. Kept browser state names the account its page pulled from; the server refuses it for any other (a tab left open on one account after another signed in on that browser), and that tab reloads. Tested: `test_facts_are_per_account`, `test_cloud_charts_are_per_account`, `test_new_account_starts_with_the_sample_charts`, `test_share_chart`, `test_browser_state_is_kept_per_account`. | `server/tests/test_auth.py` |
| SQL | Parameters everywhere; the only names put into SQL text are constants in the code. | |
| Files | Sample charts only by a name from the listing; Research databases by allowlist; static files through Starlette (no `..`); CCXT exchanges only by an id in `ccxt.exchanges`. | `server/app/file_routes.py`, `server/finance.py` |
| Owner's login prefill | Only for Host 127.0.0.1 or localhost with no proxy headers. `.owner-login.json` is git- and docker-ignored, mode 600. | `server/auth.py` `owner_login` |
| Secrets | No keys, tokens or the owner's email anywhere in the repo or its history (checked 2026-11-19). OAuth secrets come from the environment. `server/owner.json` holds only hashes. `databases/accounts.db` is mode 600 and git- and docker-ignored. | `.gitignore`, `.dockerignore` |
| API map | `/docs`, `/redoc` and `/openapi.json` are off: they sat outside the gate. | `server/app/main.py` |
| Dependencies | `pip-audit -r requirements.txt` and `npm audit` in `web/`: no known vulnerabilities on 2026-11-19. | |

The tests are in `server/tests/test_auth.py` and `server/tests/test_security.py`.

## Before the cloud

1. **Decide where the accounts live.** They are one SQLite file, so run one instance with a persistent disk: a small
   VM, or a container platform with a mounted disk and at most one instance. A Cloud Run container's own disk is wiped
   on every restart, and Cloud Storage FUSE is not safe for SQLite. More than one instance needs a server database
   (Cloud SQL, Firestore): a port of `server/auth.py`'s queries, with the sign-in limits, now kept in memory, moved there too.
2. **Set the environment:** `PUBLIC_URL` (https), `ALLOWED_HOSTS` if the site has more than one name,
   `FORWARDED_ALLOW_IPS` to the proxy's range (never `*`, see `.env.example`), `ACCOUNTS_DB` on the persistent disk.
   The Dockerfile sets `HOST=0.0.0.0`.
3. **Keep secrets in the platform's secret store:** `OAUTH_*_SECRET`, and `OWNER_FILE` if `owner.json` leaves the repo.
4. **The admin password.** Its scrypt hash is in `server/owner.json`, so anyone with a copy of the repo can try to
   guess it offline. Keep it long and random, and change it if the repo is ever shared or made public. Settings >
   Account changes the database's copy; for a fresh server, regenerate `owner.json`:
   `.venv/bin/python -c "import getpass; from server.auth import hash_password; print(hash_password(getpass.getpass()))"`
   for `password_hash`, and `python3 -c "import hashlib; print(hashlib.sha256('you@example.com'.lower().encode()).hexdigest())"` for `email_sha256`.
5. **Back up** `ACCOUNTS_DB` with `sqlite3 accounts.db ".backup backup.db"` (not a plain copy of a live file), keep
   the backups encrypted, and try a restore once.
6. **Rate-limit at the edge** (Cloudflare, the load balancer): with open sign-up, anyone can run calculations that
   take seconds each.
7. **Logs.** uvicorn's access log prints query strings, and some carry personal data (`/api/auth/chart?name=`,
   `/api/auth/facts?key=<name>|<birth date>`). Keep the logs private and short-lived, or turn the access log off.
8. **Pin versions for the image.** `requirements.txt` gives minimums only; run `pip-audit` and `npm audit` before
   each release.

## Sign in with Google

1. Google Cloud console > APIs & Services > OAuth consent screen: External, scopes `openid`, `email` and `profile`
   only. These are not sensitive scopes, so Google's verification review does not apply.
2. Credentials > Create OAuth client ID > Web application. Authorized redirect URIs:
   `<PUBLIC_URL>/api/auth/oauth/google/callback`, and to try it on this Mac,
   `http://127.0.0.1:8000/api/auth/oauth/google/callback`. No JavaScript origins: the flow is server-side redirects.
3. Set `OAUTH_GOOGLE_ID` and `OAUTH_GOOGLE_SECRET`: in `.env` on this Mac, in the secret store in the cloud. The Google
   button on the sign-in page then works.
4. The quick tunnel's address changes at every start, so it can't be registered with Google; use a fixed name
   (a named Cloudflare tunnel, or the cloud host's domain).
5. The CSP needs no change for this flow. Google's own JavaScript button (Google Identity Services) would need
   `accounts.google.com` in `script-src`, `frame-src`, `connect-src` and `style-src`.
6. For more than sign-in (Drive, Calendar), ask for those scopes only when the person uses the feature, and keep the
   refresh tokens encrypted at rest. The app stores no provider tokens today.

## Open, and by choice

Most serious first.

- **No email verification and no password reset by email.** An email typed at sign-up is not checked, and the owner
  resets passwords by hand (`python -m server.auth reset <email or username>`). Both need an email provider. Until then,
  a sign-in through a provider with the same verified email takes such an account over, as above.
- **Lock-out.** Anyone who knows an account's email or username can lock it for 15 minutes with 10 wrong passwords.
- **Who has an account can be learnt.** Sign-up says when an email is taken, sign-in answers more slowly for an
  existing account (scrypt runs), and the share box lists usernames and names by prefix to any signed-in account.
- **Shared computers.** Open and recent charts stay in the browser's localStorage after sign-out, until another account
  signs in on that browser: `web/src/kept.ts` wipes them first, and sends none of them to the new account.
- **Sign-in page text.** The page shows `?auth_error=` as it comes, so a link can make it say anything (as text, never HTML).
- **Inline styles.** The CSP allows `'unsafe-inline'` styles, which the boot cover and style attributes need; scripts stay `'self'`.
- **One process.** The sign-in limits are per process and forgotten on restart. Every `/api` request reads SQLite
  synchronously inside the async middleware: fine for one instance, a bottleneck under heavy load.
- **Data at rest.** SQLite is not encrypted; rely on the disk's encryption (the default on the big clouds) and
  private, encrypted backups.
- **Outbound calls.** The Finance tab calls Yahoo Finance and CCXT exchanges, at fixed hosts with timeouts.
- **Providers.** Facebook and LinkedIn get no PKCE, since their documentation doesn't promise it for web apps.
  Microsoft is limited to personal accounts; see the comment in `PROVIDERS` before opening it to work accounts.

## If something goes wrong

- **Sign everyone out:** `sqlite3 databases/accounts.db "DELETE FROM sessions"`.
- **One account:** `python -m server.auth reset <email or username>` sets a new password and signs it out everywhere.
- **A leaked OAuth secret:** rotate it in the provider's console, update the environment, restart.
- **A leaked admin password or `owner.json`:** change the password under Settings > Account, then regenerate `owner.json` (above).
