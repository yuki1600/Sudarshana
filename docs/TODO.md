# What is left to do

The single list of open work for Sudarshana (as of 2026-11-27).

## 1. Decisions for the owner

- [x] **UI platform.** A local web UI on a Python API, which reuses `core_logic` directly. If it is hosted
      for other users, the AGPL requires offering them the source.
- [ ] **Before the cloud** ([SECURITY.md](SECURITY.md)): where the accounts live (one SQLite file, so one instance on a
      persistent disk, or a port of `server/auth.py` to a server database), and an email provider for verifying sign-up
      emails and resetting passwords.

## 2. The application

`server/` and `web/` have every tab, the menu bar, the context menus and the windows off the tree. What is thinner than it could be:

- [ ] **Left out on purpose:** auto-update and a licence dialog. Print Setup is the browser's. Email chart opens the mail program with the `.jhd` text in the body, since a `mailto:` link cannot attach a file. Exit is the browser tab.
- [ ] **Printing:** the pages are laid out by this app, and the browser prints.
- [ ] **Chart languages:** the lagna and nine planets, in Unicode, written by hand; the small labels stay Latin.
- [ ] **Colours:** all 125 can be chosen and saved, but 39 of them reach something on the page, by their names; the app does not draw the other items separately.
- [ ] **Panchanga DP format:** R1 .. L12 are taken as the rising signs and their end times.
- [ ] **Preferences `.ini`:** import, export and viewing cover the options the Settings screen has. Keys with a value per dasa are read from the first dasa and written to all; the per-dasa Options stay in the app. Colours, window sizes and `[BodiesToShow]` are not carried across.
- [ ] **Save window sizes** keeps the width of the chart pane only.
- [ ] **Dasa view:** it opens on the period running today, down to the pratyantardasa, with the open levels nested in one table; Copy takes what is open. Durations are in the dasa's own years, 12 months to a year and 30 days to a month, so they can differ by a few days from the calendar gap between From and To; event charts, and anything under a day, read the dates.

## 3. Calculations still open

None.

## 4. Checked only by unit tests or by eye

These are unit tested, but not checked against an independent source:

- [ ] **Stationary Transit Mode**, **Swearing-in Chart Mode**, the **Transit Calendar** beyond its first row.
- [ ] The Aspect Table's numbers; Vimsottari seed comparison; Locate an event; Shift dasa dates; Sum of longitudes; the Tajaka Sunrise chart; Tithi Pravesha's Month, Daily number and "before"; progressions in a varga, or with another dasa or seed; Special Search in a varga (`modes._varga_event`); the orb rules of Longitude Correlation; the Transit view's other natal references and vargas; Key Info in a varga, and the aspect evaluation's options; the avasthas in a varga; Yogas in a varga; the Ashtakavarga view's other vargas and lagnas, and the stars and signs from the pindas; Laghu Parasari in a varga; the bar graph sets; the wheels' other bodies, other bases, and the Sarvatobhadra's highlights and special points; the planetary special lagna and user's special point on charts; the Panchanga's DP format, ephemeris and movements; Copy chart as text in North and East.
- [ ] **Typed strengths in the rasi dasas' Options:** applied where the engine reads the strength tables (`sign_strength.typed_strengths`); they hold for the one dasa. Paka and Sama are the engine's options 1 and 2.
- [ ] **Swarudha choices 2, 4 and 7:** offered by the rule the option states.
- [ ] **Sum of longitudes up to a dasa level and Pachakadi:** unit tested only.
- [ ] **Deeper dasa levels under non-default year definitions:** they go through the same mapper as the mahadasas.
- [ ] **Muhurta tab:** `server/muhurta.py` and `server/calendars.py` follow Drikpanchang's lists. Checked only against
      Drikpanchang's New Delhi page for one day (Abhijit to the minute; Rahu Kalam about 2 minutes early, since Drik rises on the upper limb). Open:
      Do Ghati, Amrit Kalam, Panchaka Rahita, Dwipushkar/Tripushkar, Pancha Pakshi and Jain Pachchakkhan are not built; the Sarvartha/Amrit Siddhi
      tables are from memory of the common lists; Kshaya months are not detected; the last tithi/nakshatra of a day shows "past next sunrise" for its end.
      "Find a muhurta" judges by `data/muhurta_rules.json` (textbook Panchang Shuddhi lists, to be checked against Drikpanchang's
      Vivah, Griha Pravesh, Vehicle and Property pages); Chaturmas is approximated by whole Amanta months; Vivah takes one chart, not both partners.
      Festivals (`server/festivals.py`, `data/festivals.json`): New Delhi 2023-2026 checked by hand against Drikpanchang, ~40 festivals and all Ekadasis, Pradoshams and Sankashtis of 2025 agree;
      `server/tests/test_festivals.py` pins 2025. Known gaps: Holika Dahan and Raksha Bandhan do not shift for Bhadra (2023's Holika comes a day early);
      Drik's Smarta Ekadasi sometimes takes the Dashami-touched first day (Prabodhini 2025: Drik 1 Nov, here 2 Nov, Drik's Gauna day); Drik's Janmashtami 2025 is 16 Aug, the Nishitha rule here gives 15 Aug;
      a star twice in a solar month takes the second (one Sri Vaishnava source); Kshaya months are not detected; the zone is the one of the date shown, for the whole year.
      `panchanga.compute_muhurta_timings` marks Abhijit inapplicable on `weekday_idx == 2` (Tuesday, with 0 = Sunday) though its comment says Wednesday.
- [ ] **Textbook code never verified:** `laghu_parasari`, the Prasna Marga sphutas in `miscellany`, `tajika.detect_16_tajika_yogas`.
- [ ] **Wheels:** Kota Swami is taken as the lord of the natal Moon's sign. The labels of the wheels' other bodies (`Pr`, `Dh` ..) are this app's.
- [ ] **Derived charts:** the dasas of Tithi Pravesha charts other than the annual one take the next chart as their span and the
  Pravesha year definition. The drill-down in event charts is checked only for staying inside its parent. Solar eclipses and the
  non-default Mundane choices are checked for running and their names.

**Behaviours worth deciding on:**

- **Longitude Correlation:** the rows for vargas other than D-1 use the *transit* chart's points, though the tab says natal.
  `transits.longitude_correlation` does either, through `varga_points`.
- **Polar sunrise:** where the Sun does not cross the horizon, `ephemeris.sunrise_sunset` uses a defined day instead; this is the app's own rule.
- **Longevity:** `core_logic/ayurdaya.py` is checked against the verses of BPHS (Ch. 9, 10, 43, 44, 70, 71).
  Readings the text leaves open: one agreeing pair of long life is 96 years, though one edition prints 91 (the series and the Jaimini tables have 96). The rectified span shows the Jaimini compartment and the literal 43.45-46, because the literal rule can leave a chart below its own class; the compartments are not in our text. Nisargayu takes Pindayu's arc and reductions, because BPHS gives only its fixed years. The Lagna's strength is Bhava Bala, "strong" is Shadbala at or above the rupas required, and Saturn lowering the class is the first of the two opinions in 43.47.
  Left out: the parents' evils (9.24-45), other beings' spans (43.23-29), and the `pinda x 7 / 27` routine in `ashtakavarga.py`, whose source could not be traced.
- **Astrocartography:** checked against the app's own relocated charts.
  Lines are zodiacal (the relocated Lagna or MC equals the graha's longitude), not true horizon crossings, so they differ slightly from Western maps, by about 1 degree of longitude for the Moon.
  Bhava zones use a fixed system whatever the House system option: natal Sripati from the Lagna, equal houses for a graha. Their dashed lines are the bhavas' borders; with the Lagna in the middle of the first house each cusp has its own line (shown when zoomed in), and with the Lagna at its start the borders are the cusps.
  Country borders follow Natural Earth's default view, with disputed lines dashed, not any one country's official map; `FCLASS_IN` and its like in `ne_10m_admin_0_boundary_lines_land` hold the other views. Bands and rising and setting lines run on past the polar circles to where each point only grazes the horizon; every Lagna circle passes through the two places with an ecliptic pole overhead, and beyond those a band holds the Lagna of the opposite one, as the ascendant flips.
  Surya Siddhanta, topocentric, refracted and adjusted charts have no map, because their positions change with the place or are not a moment.
- **Dasa start points 19 and 20** (the user's lagna and point) start from 0 degrees, even with the ini flag on.
- **Monthly planetary movements:** each 4/10 and 5/9 is found from both bodies, so those lines print twice, and the Moon's sign and nakshatra entries are left out. A planet that crosses a boundary forward, back and forward again inside the span is not listed every time (`server/miscellany.py`).

## 5. Housekeeping

- [ ] **`.jhd` line 18** is written from the birth dialog's gender combo (Unknown, Male, Female). Layouts beyond the 18 samples, and whether legacy layouts need writing, are unknown.
- [ ] **Engineering:** caching for calendars and searches, input validation in the engines, a schema for the `build_chart`
      result, the `test_tier*` file names.
