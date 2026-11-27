# Feature map: every web feature on the phone

Each row is something the web app does today (`web/src/`, Starlight layout), where it lives in the mobile app, and how it
is operated by touch. Priority is the release it ships in (see the roadmap in [MOBILE_PLAN.md](MOBILE_PLAN.md#14-roadmap)):

- **P0**: first release; the app is not useful without it.
- **P1**: second release; full-depth astrology.
- **P2**: third release; research, maps and data tools.

Where to find a feature: **Tab** = one of the five bottom tabs; **More** = the More grid; **Sheet** = a bottom sheet
opened from the screen named.

## Global: charts, settings, account

| Web feature (file) | Mobile placement | Touch pattern | P |
|---|---|---|---|
| Open chart: local list, cloud charts, shared with me, sample charts, Rodden AA/A library (`OpenChart.tsx`) | Chart switcher: tap the chart name in the header | Sheet with segments Mine · Cloud · Shared · Samples · Rodden; search field; swipe a row left to delete or share | P0 |
| New chart, edit birth data (`BirthDialog.tsx`) | Full-screen form from the switcher ("New chart") or the chart's ⋯ menu | Date and time wheels, place search that fills latitude, longitude, zone and altitude, "Now, here" button using location | P0 |
| Time zone and DST by date (`Zone.tsx`, `/api/zone`) | Inside the birth form | Recomputed when the date changes; shown as a chip "IST +5:30" that opens the zone list | P0 |
| Calculation options (`Settings.tsx`, `StarSettings.tsx`, `/api/settings/schema`) | More › Settings | Grouped list generated from the schema, with search; each option opens a picker; "Reset to defaults" at the end | P0 |
| Account: profile, avatar, saved themes, password, sign out everywhere (`Account.tsx`) | More › Account | Plain list screens | P0 |
| Sign in, sign up, provider sign-in (`Login.tsx`) | First screen | Full-bleed sky image, no card; provider sign-in through the system browser | P0 |
| Save and export `.vs` / `.jhd`, import `.jhd` and `.ini` (`App.tsx`, `/api/jhd/*`, `/api/ini/*`) | Chart ⋯ menu and Settings › Import | Share sheet for export; document picker for import | P1 |
| Copy basic / complete calculations (`Windows.tsx`, `/api/report`) | Chart ⋯ menu › Share report | Share sheet with text, or a PDF file | P1 |
| Print pages (`Print.tsx`) | Chart ⋯ menu › Share as PDF | PDF rendered on device from the same pages, sent to the share sheet (AirPrint and Android print are in it) | P1 |
| Email chart | Chart ⋯ menu › Share chart | Share sheet with the `.jhd` attached (the web can only paste it into a mailto body) | P1 |
| Moment controls: step the time ±, transit and prasna modes (`Modes.tsx`, `/api/step`, `/api/modes/*`) | Clock chip in the chart header | Sheet with a time stepper (s, min, h, day, month, year) and the mode list | P1 |
| Windows off the tree: aspect table, dasa-transit correlation, sum of longitudes, entry chart, locate event (`Windows.tsx`) | Opened from the screen they belong to | Full-screen modal with a back button; several can stack | P2 |
| About, Terms (`About.tsx`, `Terms.tsx`) | More › Help, More › About | Searchable reading list | P2 |

## The seventeen tabs

| Web tab and its sub tabs | Mobile placement | Touch pattern | P |
|---|---|---|---|
| **Home**: Overview, Grahas, Bhavas, Aspects, Yogas, KP, Amsas, Speeds, Options (`Starlight.tsx`); Key Info, Bhavas, Amsa rulers, KP (`Views.tsx`) | **Tab: Chart** | Fixed chip row of sub tabs; the chart card on top in South, North, East or wheel style; tap a varga chip to change D-1…D-60; long-press a graha for its action sheet | P0 |
| **Dasas**: every dasa system, nested periods to the pratyantar, per-dasa options, Quick Info, shift dates, locate an event (`Dasas.tsx`) | **Tab: Dasas** | System picker chip; nested list that opens on the running period with "now" in gold; tap a row to open its sub-periods; options in a sheet | P0 |
| **Transits**: Transits, Tajaka, Tithi Pravesha, Transit Calendar, Special Search, Longitude Correlation, Angular Return, Progressions, Prasna (Horary), Laghu Parasari (`Transits.tsx`) | **Tab: Transits** | Chip row; Transits as cards per graha; Calendar is the row-per-graha strip, panned sideways through time; searches as forms that list results | P0 (Transits, Calendar), P1 (the rest) |
| **Tajaka** (`Tajaka.tsx`) | Transits › Tajaka chip | Year stepper; annual chart, muntha, sahams, Tajaka yogas and dasas as sections | P1 |
| **Tithi Pravesha** | Transits › Tithi Pravesha chip | Year stepper; the chart and its dasas | P1 |
| **Muhurta**: Panchanga, Muhurta finder, festivals by regional calendar, the day dial (`Muhurta.tsx`, `MuhurtaFind.tsx`, `MuhurtaDial.tsx`) | **Tab: Today** | Day pager (swipe for the next day); panchanga list; day strip of good and bad windows; "Find a muhurta" form; festival list | P0 |
| **Strengths**: Shadbala & Bhava bala, Ashtakavarga (with Nakshatras & rasis), Vimsopaka, Vaiseshikamsa, Yogas, Avasthas (Age, Alertness, Mood, Activity, Lajjitadi), Other balas, Bar graphs (`Strengths.tsx`) | More › Strengths | Chip row; tables become one card per graha; bar graphs at full width; ashtakavarga grid pinch-zoomable | P1 |
| **Timeline**: Timeline, Tables (`Timeline.tsx`) | More › Timeline | Vertical timeline of signs, retrogression, gandanta, combustion and conjunctions, newest first; Tables as cards | P1 |
| **Predictions**: life facts questions and dated events (`Predictions.tsx`) | More › Predictions | One question per card; add-an-event form (kept across restarts) | P1 |
| **Longevity** (`Longevity.tsx`) | More › Longevity | Sections with the methods' results | P2 |
| **Chakras**: Many Vargas, Mixed 2-Vargas, Kalachakra, Sarvatobhadra, Kota, Kurma, Surya Kalanala, Chandra Kalanala, Sudarsana, Shoola, Tripataki (`Chakras.tsx`, `Wheels.tsx`) | More › Chakras | Chip row; each chakra on a pinch-and-pan canvas; Many Vargas as a pager, one varga per page | P1 |
| **Matching**: Overview, Comparison, areas, Shortlist; partners, kutas, ranking (`Matching*.tsx`) | More › Matching | Two partner cards; score ring; kuta list; Key Points filter (all / same / different); shortlist | P1 |
| **Mundane**: chart finders by group (`Modes.tsx`) | More › Mundane | Group chips; list of events; tap opens the event chart | P2 |
| **Astrocartography**: world map, lines, city points, place search, relocated chart inspector (`Astrocartography.tsx`) | More › Astrocartography | Full-screen map with pinch and pan; long-press a point to relocate; inspector as a sheet | P2 |
| **Research**: Overview, Disasters, Elections, Nations, Sports, Events, Finance; filters, counts, chi-square (`Mundane.tsx`) | More › Research | Dataset chips; filters in a sheet; results as cards; open a record's chart | P2 |
| **Finance**: symbol search, price chart with planetary overlays (`Finance.tsx`) | More › Finance | Chart turns to landscape; drag to select a span | P2 |
| **Remedies**: Navagraha, Birth moment; chapters, verses (`Remedies*.tsx`) | More › Remedies | Reading layout with Devanagari verses; chapter pickers kept across restarts | P1 |

The Calculations tab is hidden on the web (`TopBar.tsx`) and stays hidden on the phone.

## What the phone adds

These have no web counterpart. Each one uses a phone capability the browser version lacks.

| Feature | Why | P |
|---|---|---|
| "Now, here" chart | One tap casts a prasna or a chart for this moment at this place (location permission) | P1 |
| Reminders | Local notifications for a chosen muhurta window, the start of a new antardasa, or a slow graha changing sign | P1 |
| Home-screen widget | Today's tithi, nakshatra and Rahu Kalam, and the running dasa | P2 |
| Open shared links in the app | A chart someone shares opens in the app instead of the browser | P1 |
| Face ID / fingerprint unlock | Birth data is personal; optional lock on open | P2 |
