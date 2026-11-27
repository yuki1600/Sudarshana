# Sudarshana — notes for Claude

A Vedic astrology workstation: `core_logic/` (Python calculation engines), `server/` (FastAPI over core_logic),
`web/` (React + Vite, zustand store). README.md has the full map; docs/TODO.md says what is left.

## Layout and finding code

- `data/` is runtime data the server reads; new app data goes there. Name code after what it does, never after another
  program; where a common term is needed, use Sudarshana.
- Big modules are packages split by subsystem (`core_logic/{ephemeris,natal_chart,dasa_systems,shadbala,compatibility,yoga_engine}/`,
  `server/app/`): add code to the part it belongs with; `__init__.py` re-exports every name. `server/app/` parts register
  routes on the one `app` in import order, `static.py` (the web/dist mount) last.
- **Look code up in the knowledge graph before grepping or reading files**: `graphify query "<question>"`,
  `graphify explain "<symbol>"`, `graphify path "<A>" "<B>"`, or `graphify-out/GRAPH_REPORT.md` for the map. After
  structural changes, `graphify update .` (code only, no LLM, about a minute). `.graphifyignore` keeps it to code.

## Running and checking

- `./start.sh` sets up, rebuilds `web/dist` if `web/src` changed, and (re)starts the server on port 8000. Use `.venv/bin/python` (homebrew python has no uvicorn).
- The server serves `web/dist`, so after a web change run `npm run build` in `web/` or the change isn't live. After a Python change, restart the server.
- **Don't verify UI changes yourself.** No screenshots, no headless Chrome, no opening browser tabs. Make the change, rebuild/restart so it's live, say what changed, and the user checks it after each change.
- **After every change that's live (a web build, a server restart, a rebuilt database), run `./refresh.sh`**: it waits for
  the server, then reloads the user's Chrome tabs on the app (127.0.0.1:8000 and the trycloudflare link). It only reloads, never opens a tab.
- The app is http://127.0.0.1:8000, not localhost: the user's charts live in that origin's localStorage.
- The server sends a strict CSP (`HEADERS` in `server/app/main.py`): a new external script, image, font or fetch needs its
  origin added there, or the browser blocks it. New `/api` routes are behind the sign-in gate unless under `/api/auth/`
  (which must check for themselves). `docs/SECURITY.md` lists every control and the checklist before the cloud.
- Tests: `npm test` and `npm run typecheck` in `web/`; `python -m unittest discover -s core_logic/tests -t .` and `-s server/tests`; the two can run at once. Run the slow suites only for the area you touched.
- All suites are green (2026-11-27), so a failure is new. A change to a default, a label or a format can break a
  test: run the server suite in the same change and fix the test with it. Left red, they hid other failures for days.
- After moving code between modules: `ruff check --isolated --select F821,F811,F822,F823 core_logic server` (ruff is
  installed system-wide, not in `.venv`) finds names left behind in paths no test runs; `server/tests/test_imports.py`
  resolves every import, the ones inside functions too.

## Calculations

- The app's defaults are the user's own choices (ayanamsa Pushya Paksha, date format, house type…). The tests run on fixed
  settings pinned in `server/tests/__init__.py`: when a test fails, check settings first (a uniform ~1° offset means an
  ayanamsa mismatch), and pin there, never change the app default back.
- Swiss Ephemeris state (Delta-T, `set_topo`, `set_sid_mode`) is process-wide on macOS and the server answers requests on
  many threads: code that sets it runs inside `with _SWE_LOCK:` (`core_logic/ephemeris/config.py`), as `planet_positions` does.
- Root finders: interpolate from one end of the bracket (`lo + (hi - lo) * r`), never as a weighted average of Julian days.
  At a JD of ~2.4e6 a rounding of 1e-11 is seconds; that kept `time_search._crossing` up to 1 s late until 2026-11-19.
- Every calculation and setting has its source in `docs/SOURCES.md` (classical text by chapter.verse, or marked modern,
  astronomy or convention): a new one gets its row there. Code comments cite verses.
- Small numeric differences (arc seconds, seconds of a dasa date) are accepted; report in one line, don't chase. Real errors still get fixed.
- Recompute with the user's settings, not the server's defaults, or results won't match what they see.
- "Which is stronger" always compares strength against each one's minimum: Shadbala as % of its required rupas,
  Bhava Bala as % of 7 rupas. Never raw virupas.

## UI rules (the user has asked for each of these, some more than once)

- **`docs/DESIGN.md` is how each kind of thing is drawn** (tones as dots, references as `Ve – 1st`, strengths as a ring or a
  house, values in words). Read it before UI work and match it without being asked; when the user settles a new look or
  corrects one, update it in the same change.

- Two layout themes: Windows (four charts and the Key Info windows; leave as is) and Starlight (all redesign work goes here, behind `display.layout === "starlight"`).
- Solid colours only: black, white, the intro's gold, purple. No gradients, no cream. Purple = what you act on; where you are is `--here` (purple in Sudarshana Starlight, gold in the Windows layout and Praajna). Show colour options visually before asking the user to pick.
- No visible scrollbars anywhere; things still scroll.
- Sub tab rows never move: a fixed tab row over a separate scrolling area, not `position: sticky`.
- A tab's header is just its sub tabs, no heading repeating the tab or sub tab name.
- In Starlight, the last box of a tab stretches to end level with the charts.
- Nothing disappears on refresh: a reload reopens exactly what was on screen (page, tab, sub tab, open pop-up/dialog, results, form inputs). Persist all of it (`useKept`/`useSaved` in `web/src/hooks.ts`, the chart store).
- Graha abbreviations are capital + small: Su Mo Ma Me Ju Ve Sa Ra Ke. Where colour already names an event, the label skips the event name.
- Settings > Language (11 languages): `web/src/language.ts` translates the page's text as it is drawn (text values and a few
  attributes only, never the DOM's structure), from the rows of `languageWords.ts`; `translate.ts` reads them. The data and
  React stay English. A new label translates once its words have a row (a Sanskrit term needs only its Hindi); a label
  with any English word the rows lack stays English whole. People's and places' names go in `translate="no"`. A component
  that measures its text (OneRowTabs) calls `tr()` itself; the charts' labels are `names.ts` CHART_LABELS.
- Calendar tab is the row-per-graha strip only; don't pitch other chart forms for it.
- Login: no card around the form, real NASA/Webb imagery. The chakra intro plays only before sign-in; signing in is a short fade.
- The owner's login is prefilled on the sign-in form only at 127.0.0.1 (`/api/auth/owner-login` reads git-ignored `.owner-login.json`), never through the tunnel. The admin account is `server/owner.json`: hashes only, never put the real email or password in the repo.

## Working style

- Branches on GitHub (yuki1600/Sudarshana): `main`, `dev`, and `archive` (the earlier Sudarshana, kept as it was).
  Commit and push straight to `main`; no other branches unless asked.
- Don't raise licensing.
- Keep changes small and in the codebase's existing patterns; reuse what's in `web/src/ui.tsx`, `hooks.ts`, `format.ts` before adding new helpers.
