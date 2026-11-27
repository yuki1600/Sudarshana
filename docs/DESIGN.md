# Design patterns

How a kind of thing is drawn, so the same thing looks the same in every tab. The user has settled each of these; read this
before UI work, reuse the pattern that fits, and when the user settles a new look (or changes one), add or edit its line here
in the same change. CLAUDE.md "UI rules" has the app-wide rules (colours, scrollbars, tab rows, persistence); this file is
the parts they are built from.

## Verdicts and tones

- A judged value has a tone: `good` / `mid` / `bad`, drawn green / amber / red (`--strong`, `--middling`, `--weak`). A value that
  only informs has none: no dot, no colour.
- The tone is a **dot before the value** (`.mc-box.good::before`…), not a coloured background or a word. A bad value's text is
  tinted toward red as well.
- A table row whose body meets a good or bad condition (Pushkara / Mrityu bhaga) is tinted whole, green or red, with the tone's
  dot before its name, in place of a Yes / No column; the condition is the row's hover.
- An area's or a section's verdict in a word beside its name: Good / Mixed / Weak (Dosha for a dosha area), `toneWord`.

## A value read from several references

- Each reference as `Ve – 1st`: its abbreviation, an en dash with spaces, the value. Its own dot before it, red where the
  reference gives the dosha (or any point), green where not. Side by side in one box (`parts` on the server, `.mc-parts`).
- **Every reference is shown, even at none**, so both partners' boxes have the same parts and line up.
- A total comes first, plain, then the references: Papa samya `9 · Ve – 3 · Mo – 3 · As – 3`.
- Which grahas and bhavas make up each count goes in the hover, not the box.
- Used by: Kuja – wrt ref (Mars's bhava from Ve, Mo, As), Papa samya (malefics from Ve, Mo, As).
- Reasons (why a dosha is cancelled) each lead with their graha, side by side after the verdict: `yes · Ma in Moola ·
  Ju aspect 75%`; a dignity as `Ma in` + the `Dignity` mark (Moola, Own), `Ma exalted ↑`.

## Strengths

- Always a % of the minimum (Shadbala of its required rupas, Bhava Bala of 7 rupas), never raw rupas or virupas; the rupas
  ("4.62 of the 5.5 rupas it needs") on hover.
- Tone by the %: good from 100, middling from 85, weak below (`pctTone`).
- **A graha's strength is a ring, a bhava's is a house**, so the two never read alike: the ring closes at 100% with a darker
  second lap past it; the house fills to its eaves at 100% and into the roof past it, darker. `Strength kind="graha" | "bhava"`
  (MatchingFactors.tsx). No progress bars for strengths.
- Where a column head does not already name it, the measure is written under the %: "Shadbala", "Bhava Bala".
- Other scores show their scale: Vimsopaka `12.3/20`, Vaiseshikamsa `7/16`, Ashta Kuta `24/36`.

## Values in words

- Name what a value is about: `Venus in Taurus` over `2nd bhava`; a bhava as `Taurus · holds Ma Ve` (or `· empty`) over
  `lord Ju in 9th`. Never a bare chip of grahas or a bare sign.
- Signs in full in sentences and factor boxes (Taurus; the chart's own names with Sanskrit or another language); the chart
  abbreviations (Ta) only in charts and tight grid cells.
- Grahas: full name for the subject of a box (Venus), abbreviations for lists in it (Ma Ve, lord Ju). Abbreviations are
  capital + small: Su Mo Ma Me Ju Ve Sa Ra Ke.
- Dignity as `Dignity` (ui.tsx), the same everywhere: ↑ exalted, ↓ debilitated, "Moola" outlined, "Own" on `--here`, "Vg".
- Ordinals level with their number ("2nd", `supOrd`), not raised.

## Tables and boxes

- A factor row: its name, under it in muted small text what it tells of (`1st bhava` / `the body`), its rule on the ⓘ.
  **Every** factor row has that line, the doshas too (`Papa samya` / `malefics from Ve, Mo, As`).
- Girl's column before the boy's, each headed with their age (`WhoAge`).
- **A running dasa goes darker to lighter down its levels**: the running mahadasa solid `--here`, its antardasa about half,
  its pratyantardasa a light wash, paler below (Matching's dasas, `.md-d*`; the Dasas tab's tree in Starlight). The period running
  now keeps its level's shade and is marked by its NOW pill, not by a solid row.
- Every value in a box of one height, bold, one size; inside a box only a measure's caption (Shadbala) is small and muted.
- In the Grahas and Bhavas tabs each group of tables sits in its own box, its name small and uppercase above (`Section`).
- One chart against several (Matching Starred, `Shortlist`): two boxes, Ranking (Ashtakuta, Dashakuta, Kuja, the gravest kuta
  doshas) then Domain, which fills the rest of the half, a row per partner in the same rank order in both so a column reads
  straight down. Scores as small band cards (`.ms-score`, the Overview's colours); each
  kuta's points with its dot. No "best in" counts and no bold leader; the pair shown in the charts is the row in `--here`.
  Every column left-aligned, so its head, each row's dot and each score card's band stack in one vertical line. Domain's
  tabs sit on its rule: All (each domain's verdict: Ashtakuta's and Dashakuta's level, then each area's), Ashtakuta (the 8
  kutas), Dashakuta (the 10 poruthams), then one per area (Doshas … Timing: a column per factor, how the two read on it, its
  verdict last; the partner's value, the fixed chart's and why on hover).
- A page's sub tabs in Starlight sit over its box, not inside it: one size and rule on every page (Home, Dasas, Matching's right
  half, `.match-top` as `.star-tabbar`), the box starting below them. No action buttons in the row beyond a way to another view or its options (Tara matrix, Mundane's calendar
  options), each drawn as Tara matrix: small padding, the tabs' size, centred a little above the rule. A starred list's tab is `★ Starred 3`.
- What a column or a value means goes on hover (`data-tip` for an instant tip), not in extra text in the cell.
- A setting whose choices are tables of degrees (Pushkara, Mrityu bhaga, on one page) shows the chosen one's table under it, a column per
  sign (Ar … Pi), the rows that differ in the other choice in `--here` (`choices[].table` in the schema, `ChoiceTable`).
- Dropdowns in Starlight open as an in-page list (`appearance: base-select`), a panel box with no scrollbar, the chosen
  option in `--here`, the arrow a small thin muted chevron (not a solid triangle); a letter key goes to the next option starting with it and cycles (`selectKeys.ts`), never past it.

## Bands

- SAV with the lagna's row: good from 32, weak under 29.
- Ashta Kuta: Excellent 30–36, Good 24–29, Average 18–23, Low under 18 (`RANK_BANDS`).
