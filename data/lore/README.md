# The lore database

What the classics say of the 9 grahas, 12 rashis, 12 bhavas and 27 nakshatras, and of every pairing of them, as JSON. The server
(`server/lore.py`) serves it to Starlight's lore panel (`web/src/Lore.tsx`), and `lore.bhava_reading` puts the pairings together
for one bhava of one chart. Nothing in it depends on the app: any program can read a chart's placements and look each one up.

## Jiva and Ajiva

Every graha, rashi, bhava and nakshatra lists what it signifies in one scheme (`jiva_ajiva.json`):

| Side | Parts |
|---|---|
| **Jiva**, the living | `people` (relations and the people it stands for), `body` (limbs, dhatus, ailments: health), `mind` (temperament, faculties), `creatures` (animals, birds, plants) |
| **Ajiva**, the non-living | `work` (occupations), `wealth` (money, gains, debts), `property` (land, buildings, vehicles), `things` (metals, gems, cloth, food, colours), `places` (and directions), `pursuits` (learning, rites, travel, honour, disputes, events) |

A record holds `significations: {jiva: {people: [...], ...}, ajiva: {work: [...], ...}}`, lists of short phrases. A question of health,
a child or a spouse is read on the Jiva side; one of a job, a house, a vehicle or money on the Ajiva side. The classics' own
three-way division (dhatu, mula, jiva: BPHS 3.47 for the grahas, Phaladeepika 1.9 for the signs) is kept beside it.

## The records

| File | Records | What each holds |
|---|---|---|
| `grahas.json` | 9, by `id` (`Su` … `Ke`) | `about`; `facts` (groups of `{k, v, src, tile}`: what it governs, cabinet, gender, caste, guna, element, form, dhatu, deity, direction, taste, trees, cloth, season, grain, gem, metal, strength, dignities, aspects, dasa years); `significations`; `reading` (`strong`, `weak`, `atmakaraka`) |
| `rashis.json` | 12, by `n` (1 Aries … 12 Pisces) | `sanskrit`, `symbol`, `about`; `facts` (lord, element, modality, gender, nature, class, guna, dosha, varna, Kalapurusha limb, build, colour, feet, direction, dwelling, strength, rising); `significations`; `strengths`, `shadows`; `reading` as the Lagna, the Moon's sign and the Sun's sign |
| `bhavas.json` | 12, by `n` | `name`, `gloss`, other `names`, `about`, `kinds` (kendra, trikona, upachaya …), `purushartha`, `karakas` (`bphs`, `phaladeepika`), Kalapurusha `limb`, `relatives`, `significations`, `reading` (`strong`, `weak`) |
| `nakshatras.json`, `nakshatra_readings.json` | 27 | the nakshatras as Dr. Pai's *Cosmic Insights* gives them, and their introduction and readings as the Lagna's, Moon's and Sun's star |
| `nakshatra_significations.json` | 27 | Jiva and Ajiva lists from Brihat Samhita 15's rulerships; the server adds each star's limb, yoni, tree, careers and places |
| `bphs_quotes.json` | | the BPHS slokas the pop-ups quote, in the app's words: each graha's description and its dasa (3.23-30, 47), each rashi's description (4.6-24), each bhava's indications and its whole chapter (11, 12-23). Made from the BPHS translation; do not edit by hand |

## The combinations

| File | Entries | Shape | Reads as | Basis |
|---|---|---|---|---|
| `rashi_bhava.json` | 12 × 12 | `readings[sign-1].houses[house-1] = {jiva, ajiva}` | that rashi on that bhava's cusp | Sudarshana's synthesis of the sign's nature and the bhava's matters |
| `nakshatra_bhava.json` | 27 × 12 | `readings[n-1].houses[house-1] = {jiva, ajiva}` | that nakshatra on that bhava's cusp | synthesis: the star's deity, shakti and temperament on the bhava |
| `bhava_lords.json` | 12 × 12 | `slokas[] = {lord, house, sloka, text}` | the lord of one bhava placed in another | BPHS 24 (`extract_bhava_lords.py`) |
| `graha_bhava.json` | 9 × 12 | `readings[graha][house-1] = {text, source}` | a graha in a bhava | Phaladeepika 8, sloka by sloka |
| `graha_aspects.json` | 9 × 12 | `readings[graha][house-1] = text` | a graha's aspect on a bhava | synthesis of the graha's drishti and the bhava |
| `graha_rashi.json` | 9 × 12 | `readings[graha][sign-1] = {text, source}` | a graha in a rashi | Brihat Jataka 17 (the Moon), 18 (the others); the nodes from BPHS 47 |
| `graha_nakshatra.json` | 9 × 27 | `readings[graha][n-1] = text` | a graha in a nakshatra | synthesis, with the deepest exaltation and debilitation points where the nakshatra pop-up places them |
| `gochara.json` | 9 × 12 | | a graha's transit from the natal Moon | Phaladeepika 26 |

## Reading a bhava from them

Writing out every rashi × nakshatra × lord × graha for every bhava would be tens of thousands of near-duplicates, so the tables stay
pairwise and a bhava is put together for the chart in hand (`lore.bhava_reading`, `POST /api/lore/bhava_reading`):

1. The cusp (the bhava's middle, or its start when the reference starts the bhava) in the chosen house system, its sign and how much
   of the bhava lies in each sign; the sign gives `rashi_bhava[sign][house]`.
2. The cusp's nakshatra and pada give `nakshatra_bhava[n][house]`; its lord (the star lord) and its KP sub lord, and the bhavas they
   sit in, say through which matters the bhava delivers.
3. The sign's lord and the bhava it sits in give `bhava_lords[(house, lord's bhava)]`, and its sign `graha_rashi[lord][sign]`.
4. Each graha in the bhava gives `graha_bhava[graha][house]`; each graha aspecting the cusp with three quarters of a full aspect or
   more gives `graha_aspects[graha][house]`.
5. The bhava's karakas (`bhavas.json`) are found and named; a karaka in its own bhava is flagged (karako bhava nashaya).
6. BPHS 11.14-16 decides whether the bhava prospers: benefics in it or aspecting it, its lord's age and alertness avasthas, its lord
   in the 10th or in it or aspecting it count for it; its lord neither in nor aspecting it, joined by a malefic or by the lord of the
   3rd, 6th, 8th, 11th or 12th, beaten in a graha war, old, dead or asleep in avastha, or in a dusthana count against it.
   Bhava Bala is given as a share of the 7 rupas a bhava needs.

## Sources and words

- The facts and the slokas name their classic: BPHS (G. C. Sharma's translation), Phaladeepika (V. Subrahmanya
  Sastri, 1950), Brihat Jataka (N. Chidambaram Iyer, 1885), Brihat Samhita (N. Chidambaram Iyer, 1884). A sloka number is given
  only where it was read in the text; otherwise the chapter.
- The syntheses are Sudarshana's own words, built from those natures, and carry no source of their own.
- No modern book is named as a source (`server/tests/test_lore.py` checks it).
- Grahas are written by their abbreviations in keys (`Su Mo Ma Me Ju Ve Sa Ra Ke`); signs, bhavas and nakshatras by number from 1.

`server/tests/test_lore.py` holds every file to its full size and the bhava reading to the screens that show the same facts.
