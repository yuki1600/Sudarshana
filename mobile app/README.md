# Sudarshana Mobile

The plan for an iOS and Android app with every feature of the web app.

| File | What it holds |
|---|---|
| [MOBILE_PLAN.md](MOBILE_PLAN.md) | The full plan: platform choice, architecture, what the server needs first, navigation, desktop-to-touch translations, components, state, native features, security, look, accessibility, performance, testing, the four phases and open questions |
| [FEATURE_MAP.md](FEATURE_MAP.md) | Every web feature (17 tabs, their sub tabs, dialogs and menus), where it goes on the phone, how it's operated by touch, and its priority |
| [wireframes.html](wireframes.html) | Twelve phone screens with real sample data (the India 1947 chart, today's panchanga for New Delhi). Open the file in a browser, or the published page: https://claude.ai/artifact/DcNKSFDmdD17QJUbWBYZTr |

## The decisions in brief

- **One codebase.** The phone layout is a third arrangement of the Starlight theme in `web/src`, used below 600 px, and
  packaged with **Capacitor** for the App Store and Play Store. A React Native rewrite would redo about 14,000 lines
  of screens that already work.
- **The server stays the engine.** The phone calls the same `/api` with the user's settings, so the server tests keep
  covering it. Phase 0 is a hosted server with bearer tokens, CORS for the app and sign-in that returns to the app.
- **Five bottom tabs:** Chart, Dasas, Transits, Today, More. The other eleven tabs are in More, and any of them can be
  pinned to the bar.
- **The web's rules carry over.** Sub tab rows never move, nothing disappears on restart, the colours stay solid
  (purple for what you act on, gold for where you are), grahas read Su Mo Ma, and there are no hover hints.
- **The phone adds** sharing files, "Now, here" charts from location, reminders for muhurtas and dasa changes, open-in-app
  shared links, and later a home-screen widget.
