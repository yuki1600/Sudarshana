# One container: the API and the built UI on $PORT. Accounts live in /var/lib/sudarshana: mount a persistent disk there,
# and run one instance (SQLite, and the sign-in limits are kept in memory; see docs/SECURITY.md).
# databases/places.db and rodden.db are git-ignored builds (README): build where they exist, or the place typeahead and
# the Rodden library come up empty. .dockerignore keeps out what must never ship (accounts, .env, the owner's login).
#   docker build -t sudarshana .
#   docker run -p 8000:8000 --env-file .env -v sudarshana:/var/lib/sudarshana sudarshana
FROM node:22-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# The XALEN Ephemeris engine's native modules (native/jpl_kernel, native/traditions; Rust) as wheels for the app's Python, and NASA JPL's DE442
# for both ephemerides (the kernel, and the binary file the Swiss Ephemeris reads, built from JPL's ASCII; SHA-256 checked)
FROM python:3.11-slim AS jpl
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl gcc libc6-dev && rm -rf /var/lib/apt/lists/*
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal
ENV PATH=/root/.cargo/bin:$PATH
COPY native /native
RUN pip wheel --no-cache-dir /native/jpl_kernel /native/traditions -w /wheels
COPY core_logic /app/core_logic
RUN cd /app && python -c "from core_logic.ephemeris import fetch_jpl_files; fetch_jpl_files()"

# 3.11: pyswisseph's wheels stop there, and the server's tests pass on it
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
COPY --from=jpl /wheels /wheels
RUN pip install --no-cache-dir -r requirements.txt /wheels/*.whl
COPY core_logic core_logic
COPY server server
COPY data data
COPY ephemeris ephemeris
COPY --from=jpl /app/ephemeris/jpl ephemeris/jpl
COPY databases databases
COPY --from=web /web/dist web/dist
# places.db is built in WAL mode, which a server that can't write beside the file can't open: give the databases a plain journal
RUN python -c "import glob, sqlite3; [sqlite3.connect(f).execute('PRAGMA journal_mode=DELETE') for f in glob.glob('databases/*.db')]"
# the code and data stay root's, read-only to the server; it writes only the accounts database
RUN useradd --system --no-create-home app && mkdir -p /var/lib/sudarshana && chown app /var/lib/sudarshana
USER app
ENV HOST=0.0.0.0 PORT=8000 ACCOUNTS_DB=/var/lib/sudarshana/accounts.db PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "-m", "server", "--no-browser"]
