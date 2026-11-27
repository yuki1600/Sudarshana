# Sources of every calculation and setting

Sudarshana's calculations come from public knowledge: the classical texts of Jyotiṣa and modern public
astronomy. This document maps each calculation, and each choice in Settings, to the text that states the rule,
and names the code that carries it out.

Every rule below is given with its classical or public source. Where the classics are silent, the rule is marked as a
modern teacher's or as an app convention, so nothing passes for classical that is not.

## How to read it

Each row has the calculation, the rule in brief, its **source**, and the **code** (module, function or table).
The source column uses these marks:

| Mark | Meaning |
| :--- | :--- |
| *(none)* | The rule is stated in the cited verse(s). Checked against the edition listed under [Editions](#editions-cited). |
| **reading** | The text states the rule, and the code settles a detail the text leaves open; the note says how. |
| **modern** | Not in the classics: a named modern teacher's rule, cited to their publication. |
| **astronomy** | Modern astronomy, cited to the public reference. |
| **convention** | An implementation choice with no textual source, stated as such. |

Citations are *chapter.verse* (e.g. BPHS 27.32–33). Verse numbers differ between translations, so each text is
cited in **one** edition, listed below.

## Editions cited

| Short | Text | Edition used for chapter.verse | Where it can be read |
| :--- | :--- | :--- | :--- |
| **BPHS** | *Bṛhat Parāśara Horā Śāstra*, Parāśara | The 97-chapter English translation (G. C. Sharma's translation, with verses added from R. Santhanam's edition and marked "Addition from Santhanam")). Numbers are that translation's. | Published |
| **SS** | *Sūrya Siddhānta* | Ebenezer Burgess, *Translation of the Sûrya-Siddhânta*, JAOS 6 (1860) | archive.org: `surya-siddhanta-english-translation-ebenezer-burgess` |
| **BJ** | *Bṛhat Jātaka*, Varāhamihira | N. Chidambaram Iyer's translation (1885) | archive.org: `b2488442x` |
| **BS** | *Bṛhat Saṃhitā*, Varāhamihira | M. Ramakrishna Bhat's translation | archive.org: `brihatsamhitaencoded_303_G` |
| **PD** | *Phaladīpikā*, Mantreśvara | V. Subrahmanya Sastri, 2nd ed. (1950) | archive.org: `Phaladeepika2ndEd.1950ByVSubrahmanyaSastri` |
| **SAR** | *Sārāvalī*, Kalyāṇavarmā | R. Santhanam's translation | archive.org: `saravaliofkalyanavarmasanthanamr.astrology_202003_28_Z` |
| **JP** | *Jātaka Pārijāta*, Vaidyanātha | V. Subrahmanya Sastri (1932), 2 vols | archive.org: `JatakaParijataVolIOfIIByVSubrahmanyaSastri`, `…VolIIOfII…` |
| **UK** | *Uttara Kālāmṛta*, Kālidāsa | P. S. Sastri's translation | archive.org: `kupdf.net_uttkalamrita-kalidas-ps-sastri` |
| **JUS** | *Jaimini Upadeśa Sūtras* | B. Suryanarain Rao, *Jaimini Sutras* (1955); adhyāya.pāda.sūtra | archive.org: `Jaiminisutras1955EditionByBSRao` |
| **PM** | *Praśna Mārga* | B. V. Raman's translation, parts 1–2 | archive.org: `PrasnaMargaBVR`, `prasna-marga-part-2-by-bv-raman` |
| **KP** | *Kālaprakāśikā* | N. P. Subramania Iyer (1917; 1982 reprint) | archive.org: `Kalaprakasika1982EditionByN.Iyer` |
| **HS** | *Horā Sāra*, Pṛthuyaśas | R. Santhanam's translation | archive.org: `HoraSaraRSanthanamEng` |
| **LP** | *Laghu Pārāśarī* (*Jātaka Candrikā*) | B. Suryanarain Rao, *Jataka Chandrika* (1900) | archive.org: `jatakachandrikaormoonlighttoastrologysuryanarianraob._202003_329_Q` |
| **DK** | *Deva Keralam* (*Candra Kalā Nāḍi*) | R. Santhanam's translation (1992) | archive.org: `deva-keralam` |
| **TN** | *Tājika Nīlakaṇṭhī*, Nīlakaṇṭha | Cited by tantra and verse as in the Sanskrit–Hindi editions; English summary in B. V. Raman, *Varshaphal* (1941) | archive.org: `VarshaphalOrTheHinduProgressedHoroscope` |
| **MC** | *Muhūrta Cintāmaṇi*, Rāma Daivajña | Cited by prakaraṇa | archive.org: `muhurta-chintamani-of-daivagya-ramacharya-mahidhar-sharma` |
| **SP** | *Śrīpati Paddhati*, Śrīpati | Cited by chapter | archive.org: `sripati-paddhati` |
| **KSK** | K. S. Krishnamurti, *Krishnamurti Padhdhati* (the KP Readers) | Vol. I | archive.org: `in.ernet.dli.2015.128044` |
| **PVR** | P. V. R. Narasimha Rao, *Vedic Astrology: An Integrated Approach* (Sagar, 2000) | By chapter | archive.org: `vedic-astrology-integrated-approach-1` |
| **GBB** | B. V. Raman, *Graha and Bhava Balas* (1942) | By chapter | archive.org: `gzwo_graha-and-bhava-balas-by-b-v-raman-…` |
| **SE** | Swiss Ephemeris documentation, Astrodienst (2.10) | By section | <https://www.astro.com/swisseph/swisseph.htm>, <https://www.astro.com/swisseph/swephprg.htm> |

PVR is a modern book, cited for the rules its author teaches from the Jaimini and Parāśari texts. The rules that
are his or another modern teacher's are marked **modern**.

---

## 1. Astronomy and time

Everything else starts from where the grahas are, which degree is rising, and how long after sunrise the moment
falls. BPHS 3.8–9 asks for the grahas' positions "as per Drikganit", computed to agree with observation, which is
what a modern ephemeris gives.

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Graha longitudes, latitudes, speeds, retrogression | Geocentric ecliptic positions from NASA JPL's DE442 ephemeris (1550–2650: JPL's binary file, built from its ASCII files by JPL's `asc2eph`, read by the Swiss Ephemeris with SEFLG_JPLEPH; outside it the Swiss Ephemeris' DE441 files); retrograde when the sidereal speed is negative | **astronomy**: SE §2.1 (planetary and lunar ephemerides); Park et al., *AJ* 161:105 (2021) for DE440/441; NAIF `de442_tech-comments.txt` for DE442; SE §2.1.3 (JPL files); BPHS 3.8–9 for using observed positions | `ephemeris/positions.py` `planet_positions`, `ephemeris/config.py` `_ephe_flag`, `ephemeris/jpl.py` `asc2eph` |
| Ephemeris (Settings › Model and ayanamsa) | The engine on JPL's DE442: the Swiss Ephemeris, or the XALEN Ephemeris engine reading DE442's SPK kernel: light-time, the Sun's light deflection and annual aberration (SOFA `iauLd`, `iauAb`), IAU 2006 precession with frame bias and IAU 2000B nutation, the true node from the Moon's osculating orbit, the mean node by the IAU polynomial. The Swiss Ephemeris' ΔT either way, and its positions outside DE442's 1550–2650. The two agree to thousandths of an arc second; the mean node to 0.25″ (1550–2200) | **astronomy**: NAIF `de442_tech-comments.txt` (DE442, integrated May 2024: DE440 with Uranus occultations and more Mars and Juno ranging); Park et al., *AJ* 161:105 (2021) for DE440; *Explanatory Supplement to the Astronomical Almanac*, 3rd ed., ch. 7; IAU SOFA; J. Meeus, *Astronomical Algorithms* ch. 47 (mean node); XALEN Ephemeris (Apache-2.0, `native/jpl_kernel/NOTICE-xalen`) | `ephemeris/jpl.py`, `native/jpl_kernel` |
| True / apparent positions, aberration, light deflection, nutation | The Swiss Ephemeris position flags (SEFLG_TRUEPOS, NOABERR, NOGDEFL, NONUT) | **astronomy**: SE §3 (apparent versus true positions); SE Programmer's Manual (`swe_calc` flags) | `ephemeris/config.py` `_calc_flags` |
| Refraction (apparent positions only) | Ecliptic → horizon, true altitude → apparent by `swe_refrac`, back to the ecliptic | **astronomy**: SE Programmer's Manual, `swe_refrac` / `swe_azalt` | `ephemeris/positions.py` `_apparent_ecliptic` |
| Topocentric positions | Positions seen from the birthplace, not the Earth's centre | **astronomy**: SE §4 (geocentric and topocentric positions) | `ephemeris/positions.py` |
| Rahu and Ketu | The Moon's ascending node, mean or true (osculating); Ketu = Rahu + 180° | SS 1.33 gives the node's revolutions (232,238 a yuga, retrograde): the classical node is the mean one. **astronomy**: SE §2.2.1–2.2.2 (mean and true node) | `ephemeris/positions.py` |
| Sidereal longitude | Tropical longitude − ayanamsa | SS 3.9–12 (the circle of asterisms against the equinox); [§1.1](#11-ayanamsas) for each ayanamsa | `ephemeris/positions.py` |
| ΔT (TT − UT) | Swiss Ephemeris' model, with the Moon's tidal acceleration of DE440–DE442 (−25.936″/cy²); optionally the 2.02.01 model: a yearly table 1620–2019 interpolated to fourth differences, Espenak & Meeus (2006) before it, tidal acceleration −25.80″/cy² | **astronomy**: SE §7 (ΔT); Espenak & Meeus, *Five Millennium Canon of Solar Eclipses*, NASA TP-2006-214141; the yearly table is the one in the Swiss Ephemeris 2.02.01 source (`swephlib.c`) | `deltat.py` `deltat_se202`, `ephemeris/config.py` `_delta_t` |
| Julian day, calendar | Gregorian / Julian calendars to Julian days | **astronomy**: SE `swe_julday`, `swe_revjul`; J. Meeus, *Astronomical Algorithms* ch. 7 | `ephemeris/moments.py` |
| Time zone and daylight saving | The IANA time-zone database (historical zones and DST) | **astronomy/civil**: IANA tz database | `ephemeris/points.py` `zone_offset_hours` |
| Atlas-only places' daylight saving | National DST rules (EU: last Sunday of March to last Sunday of October, 01:00 UT; US 1987–2006: first Sunday of April to last Sunday of October, 02:00 local; others by country), kept to read old `.jhd` charts and the bundled atlas as they were cast | **civil**: Directive 2000/84/EC (EU), Uniform Time Act 1966 as amended 1986 (US); the other countries' rules as listed in `dst.py`. **convention**: one rule per country for every year, as older chart files assumed | `dst.py` |
| Local mean time | 4 minutes of time per degree of longitude | SS 1.60–66 (correction for longitude, *deśāntara*) | `ephemeris/points.py` `lmt_offset_hours` |
| Units of time | 60 vighaṭīs (vināḍīs) = 1 ghaṭī (nāḍī); 60 ghaṭīs = 1 day; 1 hour = 2.5 ghaṭīs | SS 1.11–12 | throughout (`house_systems.py`, `ephemeris/day.py`) |
| Eclipses | Next / previous solar and lunar eclipse, globally or seen from a place | SS ch. 4–5 (lunar and solar eclipses). **astronomy**: SE §5.2 (eclipses), `swe_sol_eclipse_when_*`, `swe_lun_eclipse_when*` | `ephemeris/points.py` `next_eclipse` |

### 1.1 Ayanamsas

Every sidereal ayanamsa fixes the zodiac to the stars. The classical anchor is a junction star (*yogatārā*) at a
stated place in its nakshatra. SS ch. 8 lists the junction stars, which Burgess identifies (Citrā = Spica,
Rohiṇī = Aldebaran, Puṣya = δ Cancri, Mūla = λ Scorpii). A nakshatra is 13°20′ (SS 2.64), so "the star in the
middle of its nakshatra" fixes a longitude.

| Ayanamsa | Definition | Source | Code |
| :--- | :--- | :--- | :--- |
| True Lahiri / Chitrapaksha | Spica always at 180° (the middle of Citrā) | Report of the Calendar Reform Committee (Saha & Lahiri, CSIR 1955); SE §2.8.5, mode 27 "True Chitrapaksha" | `ephemeris/config.py` `AYANAMSAS` |
| Traditional Lahiri | The committee's epoch value and precession | SE §2.8.5, mode 1 | same |
| Pushya-paksha (the app's default) | δ Cancri always at 106° (the middle of Puṣya) | **modern**: P. V. R. Narasimha Rao, "Introducing Pushya-paksha Ayanamsha" (2013); SE §2.8.4, mode 29 "True Pushya" ("Siddhantas usually assume the star Pushya at 106°") | same |
| Rohini-paksha | Aldebaran always at 46°40′ (the middle of Rohiṇī) | **modern**: the same definition with Rohiṇī's junction star (SS ch. 8); not among SE's modes | same |
| Chandra Hari | λ Scorpii (Shaula) always at 240° (0° Sagittarius, the start of Mūla) | **modern**: K. Chandra Hari; SE §2.8.7, mode 35 "True Mula" | same |
| Jagannatha | Spica at 180° measured on the solar system's invariable plane | **modern**: SE §2.8.12 ("the solar system rotation plane", SE_SIDBIT_SSY_PLANE) | same, `_plane_shift` |
| Raman | B. V. Raman's ayanamsa | **modern**: SE mode 3 | same |
| Krishnamurti (KP) | K. S. Krishnamurti's ayanamsa | **modern**: SE §2.8.6, mode 5; KSK vol. I | same |
| Usha-Shashi, Yukteshwar, J. N. Bhasin, Fagan-Bradley, DeLuce, Djwhal Khul, Aldebaran 15° Ta, Galactic centre 0° Sg, Hipparchos, Sassanian | As defined by Swiss Ephemeris | **modern / astronomy**: SE §2.8, modes 4, 7, 8, 0, 2, 6, 14, 17, 15, 16 | same |
| Deva-datta | Traditional Lahiri less 0°22′37.0″ | **convention**: kept as the option was defined in older chart software; no published definition was found | same |
| Sri Surya Siddhanta | The SS's libration of the equinox: 600 oscillations a yuga (7,200 years each), amplitude 27° | SS 3.9–10 | `surya_siddhanta.py` `precession`, `ayanamsa` |
| Custom star | A chosen star at a chosen sidereal longitude | **convention** (the user defines it) | `ephemeris/config.py` `_ayanamsa_spec` |
| Tropical (sāyana) | No ayanamsa | — | — |
| Swiss Ephemeris 2.02 option | The same definitions with Swiss Ephemeris 2.02.01's ayanamsa epochs and star catalogue (and its ΔT, row above) | **astronomy**: the `ayanamsa[]` table of the Swiss Ephemeris 2.02.01 source (`sweph.c`) | `ephemeris/config.py` `_SE202_AYANAMSAS` |

### 1.2 The Sūrya Siddhānta model (Settings › Graha model)

The optional planetary model computes the grahas from the SS itself, in the "generalized Makaranda" form (the
SS's mean motions with the *bīja* corrections of the Makaranda tables).

| Part | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Time count | Days since the Kali epoch (midnight at Ujjain, 17–18 February 3102 BCE, JD 588465.5) | SS 1.29–34 and Burgess's note there; SS 1.45–51 (the count of days, *ahargaṇa*) | `surya_siddhanta.py` `KALI_OFFSET` |
| Prime meridian | Ujjain (75.77° E) | SS 1.62 | `surya_siddhanta.py` `UJJAIN` |
| Mean motions | Revolutions in a mahāyuga: Sun 4,320,000; Moon 57,753,336; Mars 2,296,832; Mercury (śīghra) 17,937,060; Jupiter 364,220; Venus (śīghra) 7,022,376; Saturn 146,568; node −232,238 | SS 1.29–34 | `surya_siddhanta.py` `_REVOLUTIONS` |
| Apsides | Revolutions in a kalpa: Sun 387, Moon 488,203,000, Mars 204, Mercury 368, Jupiter 900, Venus 535, Saturn 39 | SS 1.41–44 | `surya_siddhanta.py` `_APOGEE_REVOLUTIONS` |
| Bīja corrections | Corrections to the mean motions, in 10⁻¹⁰ degrees per year since creation | The Makaranda tables (Makaranda, 1478 CE) as applied to the SS; **reading**: the values are those of the "generalized Makaranda" model | `surya_siddhanta.py` `_BIJA` |
| Epicycles | Manda: Sun 14°, Moon 32° (20′ less at the odd quadrants); Mars 75/72, Mercury 30/28, Jupiter 33/32, Venus 12/11, Saturn 49/48. Śīghra: Mars 235/232, Mercury 133/132, Jupiter 70/72, Venus 262/260, Saturn 39/40 | SS 2.34–37 | `surya_siddhanta.py` `_EPI_EVEN`, `_EPI_ODD`, `_moon_manda` |
| True planet | Half śīghra, half manda, full manda, full śīghra equations, on a sine table of radius 3438′ | SS 2.15–22 (sines), 2.39–45 (the equations; 2.43–44 their order) | `surya_siddhanta.py` `_star_planet`, `_sun_manda` |
| Retrogression | The planet is retrograde in a band of śīghra anomaly about the conjunction | SS 2.51–55. **reading**: the band edges are computed from the epicycles; SS 2.52–53's round values (Mars 164°, Mercury 144°, Jupiter 130°, Venus 163°, Saturn 115°) differ by up to 6° | `surya_siddhanta.py` `_RETRO` |
| Equation of time, sunrise, rising signs, lagna | Ascensional difference; oblique ascensions of the signs; the point rising a given time after sunrise | SS 2.60–63 (ascensional difference, day length), 3.42–45 (rising times of the signs), 3.46–49 (the lagna). The equation of time is **astronomy**: Smart's series (J. Meeus, *Astronomical Algorithms*, eq. 28.3) with the SS obliquity of 24° | `surya_siddhanta.py` `true_days`, `sunrise_hours`, `_rising_minutes`, `_horizon_point` |
| Obliquity | 24° | SS 2.28 | `surya_siddhanta.py` `_ascension` |

### 1.3 Sunrise, the day and its lords

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Sunrise and sunset | The Sun's centre or upper limb on the true or apparent horizon (Settings › Sunrise) | SS 2.60–63 computes sunrise for the Sun's centre on the true horizon. **astronomy**: SE Programmer's Manual, `swe_rise_trans` and its flags (disc centre, no refraction) for the other three definitions | `ephemeris/sunrise.py` `sunrise_sunset` |
| Midnight-sun and polar-night days | When the Sun does not cross the horizon, the day runs from lower transit to lower transit (midnight sun) or has no length (polar night) | **convention**: the texts assume the Sun rises and sets | `ephemeris/sunrise.py` `_polar_day_edge` |
| The Vedic day and weekday | The day runs from sunrise to the next sunrise; the weekday changes at sunrise | BPHS 27.13 ("each day from sunrise to sunrise"); SS 1.51–52 for the lords of the day | `ephemeris/sunrise.py` `day_night_span` |
| Weekday from 6 am local mean time (option) | The day starts at 6 am LMT instead of sunrise | **convention**: an alternative to sunrise offered for comparison; LMT by SS 1.60–66 | `ephemeris/day.py` `day_lords` |
| Hora lord | The day is 24 horas; the first is the weekday lord's, each next one the lord of the 6th weekday from the previous (the Chaldean order Sa Ju Ma Su Ve Me Mo) | BPHS 27.13; SS 12.78–79 | `ephemeris/day.py` `day_lords` (`hora_lord = (hora * 5 + weekday) % 7 + 1`) |
| Hora's 5-minute sign | Each hora split into twelve signs, starting from the hora lord's sign | **convention**: an ancillary display; no text found | `ephemeris/day.py` `_HORA_SIGN_DAY`, `_HORA_SIGN_NIGHT` |
| Kāla lord (and Mahākāla) | Day and night each in 8 parts; the lords run in the order Su Ma Ju Me Ve Sa Mo Ra from the weekday lord by day, and from the 5th of that order by night | **reading**: the eight parts of day and night are BPHS 3.66–69's, with Rāhu in the lord-less 8th part. The order is the Tamil *jāma* order (as in Jamakkol, [§14](#14-praveśa-charts-progressions-and-praśna)), the order that puts Rāhu's part on each weekday's Rāhu kāla; the night starts from the 5th of it, as BPHS 3.66–69 starts the night from the lord of the 5th weekday. PM 16.25 lords the eight parts in plain weekday order instead (Su Mo Ma Me Ju Ve Sa Ra), which this app does not use | `ephemeris/day.py` `_KAALA_ORDER`, `_KAALA_START_DAY`, `_KAALA_START_NIGHT` |
| Ishta kala, dinamana, ratrimana | Time from sunrise; day and night lengths in ghaṭīs | SS 1.11–12, 2.60–63 | `house_systems.py` `compute_ishta_kala`, `compute_dinamana_ratrimana` |
| Sandhyās and Brahma muhūrta | Brahma muhūrta: 2 muhūrtas before sunrise; prātaḥ, madhyāhna, sāyaṃ sandhyās | **reading**: a muhūrta is 1/15 of the day (the fifteen day-muhūrtas of the Taittirīya Brāhmaṇa 3.10.1, as the muhūrta texts take them). **convention**: the sandhyā spans as commonly kept; no single verse checked | `house_systems.py` `compute_trikuta_sandhyas` |

### 1.4 Houses (bhavas)

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Lagna and MC | The ecliptic degree rising, and the one culminating | SS 3.46–49 (lagna); **astronomy**: SE `swe_houses` | `ephemeris/houses.py` `house_cusps` |
| Each rasi a bhava (whole sign) | The lagna's sign is the 1st bhava, and so on | BPHS 11.2 (the 1st bhava is "the ascending Rāśi") and the rasi charts of every classic | `ephemeris/houses.py`, `house_systems.py` `compute_whole_sign_houses` |
| Equal bhavas, lagna at the cusp or the middle | 30° bhavas from the lagna's degree | **reading**: BPHS 27.26–29 treats the lagna degree as the bhava's reference point; the "lagna in the middle of the 1st bhava" form is the Sripati / Kerala practice | `house_systems.py` `bhava_spans`, `compute_equal_houses` |
| Equal bhavas from the middle of the lagna's pada | 30° bhavas starting from the start of the lagna's navamsa-pada (9 padas a bhava) | **convention**: an option of the app; no text found | `ephemeris/houses.py` (`EQUAL_PADA`), `house_systems.py` `bhava_spans` |
| Śrīpati (Porphyry) | Each quadrant between lagna and MC trisected; bhava sandhis halfway | SP, Bhāvādhyāya; **astronomy**: SE §6.2.6 (Porphyry) | `house_systems.py` `compute_sripathi_houses` |
| Placidus, Koch, Regiomontanus, Campanus, Axial rotation, Polich/Page, Alcabitus | The Western quadrant systems | **astronomy**: SE §6.2 (house systems), each system's definition there | `ephemeris/houses.py`, `house_systems.py` |
| Bhava of a point | The first bhava whose arc holds the point; bhavas from Rahu and Ketu optionally counted backwards | **reading**: BPHS 31.2–9 counts from the nodes "in a reverse manner" (argala); applying that to bhavas is an option | `house_systems.py` `house_of`, `arc_contains` |

---

## 2. Signs, nakshatras and dignities

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| The twelve rasis | 30° each from 0° Aries; movable, fixed, dual in turn; odd signs male, even female | BPHS 4.3, 4.5 | `natal_chart/signs.py` `get_rasi_info` |
| Sign lords | Ma Ve Me Mo Su Me Ve Ma Ju Sa Sa Ju, Aries to Pisces | BPHS 4.6–24 (each rasi's description names its lord) | `natal_chart/signs.py` `RASI_LORDS` |
| Rāhu and Ketu as co-lords | Rāhu owns Aquarius with Saturn, Ketu Scorpio with Mars | BPHS 47.34–39 ("the own Rāśis of Rahu and Ketu are Kumbh and Vrischik") | `sign_strength.py` `owns_sign`, `yoga_engine/catalogue.py` `CO_LORDS` |
| The 27 nakshatras and their padas | 13°20′ each (800′), four padas of 3°20′ | SS 2.64; BPHS 3.4–7 (names, in the addition from Santhanam) | `natal_chart/signs.py` `get_nakshatra_info` |
| Nakshatra lords | Ke Ve Su Mo Ma Ra Ju Sa Me from Aśvinī, repeating (the Vimśottarī lords) | BPHS 46.12–14 | `natal_chart/signs.py` `NAKSHATRA_LORDS` |
| The 28-star wheel (with Abhijit) | Abhijit inserted between Uttarāṣāḍhā and Śravaṇa, as the last quarter of Uttarāṣāḍhā (276°40′–280°) | The 28-star count is classical (UK, on counting from the Sun's star "include Abhijit"; PM ch. 16). **modern**: Abhijit as "the last quarter of Uttarashadha" is PVR ch. 25 | `utils.py` `nakshatra_to_28`, `key_info.py` `nak28` |
| Exaltation and debilitation | Exalted Su Ar 10°, Mo Ta 3°, Ma Cp 28°, Me Vi 15°, Ju Cn 5°, Ve Pi 27°, Sa Li 20°; debilitated at the same degree of the 7th sign | BPHS 3.49–50 | `natal_chart/signs.py` `EXALTATION`, `DEBILITATION` |
| Rāhu and Ketu's exaltation (Settings › Nodal exaltation) | Rāhu exalted in Taurus, Ketu in Scorpio; or Rāhu in Gemini, Ketu in Sagittarius | BPHS 47.34–39 for Taurus / Scorpio (and moolatrikona Gemini / Sagittarius). **modern**: Gemini / Sagittarius as Pt. Sanjay Rath teaches it | `sign_strength.py` `set_nodal_exaltation` |
| Moolatrikona | Su Le 0–20°, Mo Ta 3–30°, Ma Ar 0–12°, Me Vi 15–20°, Ju Sg 0–10°, Ve Li 0–15°, Sa Aq 0–20° | BPHS 3.51–54 | `natal_chart/signs.py` `MOOLATRIKONA` |
| Moolatrikona, narrow degrees (option) | Mo Ta 4–20°, Me Vi 16–20° | **convention**; no text found | `shadbala/engine.py` `set_moolatrikona_bphs` |
| Dignity of a graha | Moolatrikona and exaltation split the same sign by degree (Mercury's Virgo: exalted 0–15°, moolatrikona 15–20°, own 20–30°) | BPHS 3.51–54 | `natal_chart/signs.py` `get_graha_dignity` |
| Natural relationships | Friends: lords of the 2nd, 4th, 5th, 8th, 9th, 12th from the moolatrikona, and the exaltation lord; the rest enemies; both at once, neutral | BPHS 3.55. The 7 × 7 table is computed from this rule | `aspects_friendships.py` `NAISARGIKA_MATRIX` |
| Rāhu and Ketu's natural relationships | Enemies of Su Mo Ma, friends of Ve Sa, neutral to Me Ju (Ketu as Rāhu) | **convention**: BPHS 3.55 covers the seven grahas only; this table is the one in common software use | same |
| Temporary relationships | Grahas in the 2nd, 3rd, 4th, 10th, 11th, 12th from each other are friends, otherwise enemies | BPHS 3.56 | `aspects_friendships.py` `compute_tatkalika_relationship` |
| Compound (five-fold) relationships | Friend + friend = great friend; friend + enemy = neutral; neutral + friend = friend; neutral + enemy = enemy; enemy + enemy = great enemy | BPHS 3.57–58 | `aspects_friendships.py` `compute_panchadha_maitri`, `shadbala/engine.py` `compound_relationships` |
| Benefics and malefics | Malefics: Su, Sa, Ma, waning Mo, Ra, Ke (Me with malefics); the rest benefics | BPHS 3.11. **reading**: the yoga engine counts the Moon among the benefics and Mercury always benefic, as its yoga definitions say | `yoga_engine/catalogue.py` `BENEFICS`, `MALEFICS` |
| Combustion, classical orbs (default) | Within Mo 12°, Ma 17°, Me 14° (12° when retrograde), Ju 11°, Ve 10° (8° when retrograde), Sa 15° of the Sun | SS 9.6–9 and 10.1. **reading**: the SS gives these as degrees of time (*kālāṃśa*, oblique ascension); they are applied here to ecliptic longitude, the usual simplification | `natal_chart/karakas.py` `CLASSICAL_COMBUSTION`, `is_combust` |
| Combustion, a fixed orb (option) | Ma, Me, Ju, Ve, Sa within 6° of the Sun; optionally retrograde Mercury and direct Venus are not combust | **convention**; the motion exception is attributed to Pt. Sanjay Rath | `natal_chart/karakas.py` `is_combust_by_orbs` |
| Planetary war (graha yuddha) | Two of Ma Me Ju Ve Sa within 1° | SS 7.18–21 (an "encounter" is an interval under a degree). **convention**: the graha further along in longitude is taken as the winner; SS 7.20–21 names the planet to the north, the brighter and larger, as the victor | `natal_chart/karakas.py` `planetary_war`, `shadbala/components.py` `compute_graha_yuddha_bala` |
| Planetary war in Shadbala | The difference of the two Shadbalas is added to the winner and taken from the loser | BPHS 27.20 | `shadbala/components.py` `compute_graha_yuddha_bala` |
| Marana kāraka sthāna | A graha in its "death" house (Su 12, Mo 8, Ma 7, Me 7, Ju 3, Ve 6, Sa 1, Ra 9) | **modern**: Sanjay Rath, *Crux of Vedic Astrology: Timing of Events* (1998), which uses the term ("Jupiter in third and Venus in sixth are marana karaka graha"); the list is the one taught by his school | `natal_chart/bhagas.py` `detect_marana_karaka_sthana` |

---

## 3. Divisional charts (vargas)

BPHS ch. 6 defines the sixteen vargas (6.2–4) and how each maps the parts of a sign. The other divisions are
named in Jaimini and Tājika works and taught in their modern form in PVR ch. 6. Each "Choose …" option in
Settings › Divisional charts is one scheme below; the app's defaults are the first of each list unless noted.

| Division | Scheme (Settings label) | Rule | Source |
| :--- | :--- | :--- | :--- |
| D-1 Rasi | — | The sign itself | BPHS 6.5 |
| D-2 Horā | Traditional Parāśara | Odd sign: 1st half Leo (Sun), 2nd half Cancer (Moon); even sign the reverse | BPHS 6.5–6 |
| | Parāśara with parivṛtti and even-sign reversal (Uma-Shambhu, default) | Horās counted cyclically through the zodiac, degrees counted from the end in even signs | **modern**: P. V. R. Narasimha Rao's "Uma-Shambhu hora" |
| | Parivṛtti-dvaya (bicyclical) | The 24 horās counted cyclically from Aries | **modern**: the *parivṛtti* (cyclical) varga form; BPHS 6.6 counts the 24 horās "from Mesh, repeated twice" |
| | Jagannātha, Kāśīnātha, Samasaptaka, Maṇḍūka, Lābha Maṇḍūka, Raman (and SJC-modified), Niranjan (and SJC-modified) | As the option labels say (1st/7th by day/night; ownership by day/night; rasi and 7th; rasi and 3rd; rasi and 11th; 1st/11th; 3rd/8th and 2nd/7th) | **modern**: named for their proposers (Kāśīnātha for Pt. Kashinath Rath; Raman for B. V. Raman); "SJC" is the Sri Jagannath Centre. No primary text; no publication checked |
| D-3 Drekkāṇa | Traditional Parāśara (default) | The sign, its 5th and 9th | BPHS 6.7–8; PVR 6.2.3 |
| | Parivṛtti-traya | 36 drekkāṇas counted cyclically from Aries | **modern**: the parivṛtti form; BPHS 6.7 counts the 36 "from Mesh, repeating thrice" |
| | Somanātha | Odd signs continue forward from Aries (Ar: Ar Ta Ge; Ge: Cn Le Vi …), even signs backward from Pisces (Ta: Pi Aq Cp; Cn: Sg Sc Li …) | **modern**: as named in the option; no publication checked |
| | Jagannātha | From the movable sign of the sign's element, then its 5th and 9th | **modern**: as named in the option; no publication checked |
| | Parāśara with parivṛtti and even-sign reversal | Uma-Shambhu form for D-3 | **modern** |
| D-4 Caturthāṃśa | Traditional Parāśara (default) | The sign, its 4th, 7th, 10th | BPHS 6.9; PVR 6.2.4 |
| | Parivṛtti | Cyclical | **modern** |
| D-5 Pañcāṃśa | Standard (default) | Odd signs Ar Aq Sg Ge Li, even signs Ta Vi Pi Cp Sc, 6° each | PVR 6.2.5 ("Jaimini and Tājaka writers" name D-5, D-6, D-8, D-11) |
| | Parivṛtti | Cyclical | **modern** |
| D-6 Ṣaṣṭhāṃśa | — | From Aries (odd) or Libra (even), 5° each | PVR 6.2.6 |
| D-7 Saptāṃśa | Traditional Parāśara (default) | From the sign (odd) or its 7th (even) | BPHS 6.10–11; PVR 6.2.7 |
| | Even-sign reversal (two forms) | Even signs counted backwards, starting from the 7th or ending in it | **modern** |
| D-8 Aṣṭāṃśa | Continuous (default) | From Ar, Sg, Le for movable, fixed, dual signs (the same as counting continuously) | PVR 6.2.8 |
| | Dr. Raman's (tattva based) | From Ar, Le, Sg by modality | **modern**: B. V. Raman |
| D-9 Navāṃśa | Parāśara (default) | From the sign itself, its 9th, its 5th for movable, fixed, dual (= Ar, Cp, Li, Cn by element) | BPHS 6.12; PVR 6.2.9 |
| | Kālacakra navāṃśa | The navāṃśas in the savya / apasavya order of the Kālacakra | BPHS 46 (Kālacakra daśā, the savya and apasavya cycles); see [§9](#9-daśās) |
| | Rangacharya's Krishna Mishra navāṃśa (non-uniform), Parāśara with even-sign reversal (uniform Krishna Mishra) | As labelled | **modern**: Iranganti Rangacharya's reading of Krishna Mishra; no primary text checked |
| D-10 Daśāṃśa | Traditional Parāśara (default) | From the sign (odd) or its 9th (even) | BPHS 6.13–14; PVR 6.2.10 |
| | Parivṛtti (Ojha), even-sign reversal (three forms) | As labelled | **modern** |
| D-11 Rudrāṃśa | Rudrāṃśa (regular, Pt. Rath; default) | Count from Aries to the sign; count as many backwards from Aries; the 11 parts run forward from there | **modern**: PVR 6.2.11 (Sanjay Rath's form) |
| | Ekādaśāṃśa (anti-zodiacal, Dr. Raman) | Counted backwards | **modern**: B. V. Raman |
| D-12 Dvādaśāṃśa | Traditional Parāśara (default) | From the sign itself | BPHS 6.15; PVR 6.2.12 |
| | Even-sign reversal | Even signs backwards | **modern** |
| D-16 Ṣoḍaśāṃśa | Traditional Parāśara (default) | From Ar, Le, Sg for movable, fixed, dual | BPHS 6.16; PVR 6.2.13 |
| D-20 Viṃśāṃśa | Traditional Parāśara (default) | From Ar, Sg, Le for movable, fixed, dual | BPHS 6.17–21; PVR 6.2.14 |
| D-24 Siddhāṃśa | Traditional Parāśara (default: odd Le → Cn, even Cn → Ge) | From Leo (odd) or Cancer (even), forward | BPHS 6.22–23 as worded; PVR 6.2.15 |
| | Even-sign reversal; double reversal | Even signs backwards from Cancer; or both from Leo | **modern** |
| D-27 Nakṣatrāṃśa | Traditional Parāśara (default) | From Ar, Cn, Li, Cp by element | BPHS 6.24–26 ("commences from Mesh and other Movable Rāśis"); PVR 6.2.16 |
| D-30 Triṃśāṃśa | Parāśara (default) | Odd signs: Ma 5°, Sa 5°, Ju 8°, Me 7°, Ve 5° (Ar Aq Sg Ge Li); even signs reversed (Ta Vi Pi Cp Sc) | BPHS 6.27–28; PVR 6.2.17 |
| | Parivṛtti; "Ṣaṣṭyāṃśa-like" | Cyclical; one sign a degree from the sign | **modern** |
| D-40 Khavedāṃśa | — | From Aries (odd) or Libra (even) | BPHS 6.29–30; PVR 6.2.18 |
| D-45 Akṣavedāṃśa | — | From Ar, Le, Sg for movable, fixed, dual | BPHS 6.31–32; PVR 6.2.19 |
| D-60 Ṣaṣṭyāṃśa | From the sign (default) | Twice the degrees in the sign, plus one, counted from the sign itself | BPHS 6.33–41 (**reading**: the verse's count is read from the sign itself, as PVR 6.2.20 does) |
| | From Aries; even-sign reversal (from the sign or from Aries) | As labelled | BPHS 6.33–41 read literally (from Aries); the reversals **modern** |
| D-81 Nava-navāṃśa | Parāśara (default); Kālacakra | The navāṃśa of the navāṃśa | **reading**: BPHS 6.12 applied twice; the Kālacakra form as for D-9 |
| D-108 Aṣṭottarāṃśa | From the navāṃśa sign (default); from the sign | The dvādaśāṃśa of the navāṃśa, or 108 parts from the sign | **modern**: the 108 = 9 × 12 division as named in the option; no publication checked |
| D-144 Dvādaśa-dvādaśāṃśa | — | The dvādaśāṃśa of the dvādaśāṃśa | **reading**: BPHS 6.15 applied twice |
| D-150 Nāḍyaṃśa | Equal parts; unequal parts (default) | 150 parts of a sign (12′ each), counted forward in movable, backward in fixed and in their own order in dual signs; or the unequal spans of the text | DK (Santhanam's introduction and Table 1: "In movable signs, the count is in regular order from 1 to 150 … for an immovable sign, the count is reverse") |
| | Names: Deva Keralam; C. G. Rajan | The two lists of nāḍyaṃśa names | DK, Table 1 and Santhanam's note on Rajan's list |
| Custom D-n, D-m of D-n | — | The user's division, cyclical or from the sign, with the chosen start table | **convention** (user-defined) |

| Related calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Deities of the parts (amśa rulers) | Each division's presiding deities (Nārada, Agastya, Durvāsa for D-3; Indra … Ananta for D-10; Kālī … Sumukhī for D-20; the 60 ṣaṣṭyāṃśa names …) | BPHS 6.7–41 | `varga_charts.py` `amsa_ruler` |
| Varga groups (ṣaḍ, sapta, daśa, ṣoḍaśa) and their amśa names | Kiṃśuka … Kuṇḍala; Pārijāta … Śrīdhāma; Bhedaka … Śrī Vallabha | BPHS 6.42–53 | `shadbala/engine.py` `vaiseshikamsa_counts`, `shadbala/vimsopaka.py` |
| Divisional longitude | The varga sign plus the degrees of (longitude × n) within a sign; mirrored in even signs for the reversing schemes | **convention**: a continuous longitude inside the varga sign, common in software; no text | `varga_charts.py` `varga_longitude` |
| D-30 longitudes, "1° in rasi = 30° in D-30" (Settings) | Each degree of the sign spread over a whole sign | **convention** | `varga_charts.py` `d30_unequal_longitude` |
| 22nd drekkāṇa and 64th navāṃśa | The drekkāṇa 21 drekkāṇas on (the 8th sign's first drekkāṇa) and the navāṃśa 63 on, from the lagna and the Moon; their lords | PM 9.4 (lords of the 22nd drekkāṇa among the killers); PM 8.61 (the 64th navāṃśa from the Moon's navāṃśa) | `natal_chart/bhagas.py` `compute_22nd_drekkana`, `compute_64th_navamsha`; `key_info.py` `malicious_divisions` |
| Bhāva (chalit) chart | A graha moves one sign when it lies across the reference point's degree | **convention**: the bhāva-chart of Śrīpati bhāvas (SP) drawn by the reference's degree | `varga_charts.py` `bhava_chart_sign` |

---

## 4. Sensitive degrees (Mṛtyu and Puṣkara bhāgas)

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Mṛtyu bhāga, first table (an option) | A fatal degree for each graha and the lagna in each sign | The texts give lists for the Moon and the lagna, and they differ: PD 13.10–11; SAR ch. 5; HS 5.46–47 (whose notes also quote Jātaka Tattva's). The full table, every graha and the lagna, is the one the Settings option attributes to Sārāvalī, Jātaka Pārijāta and Sarvārtha Cintāmaṇi. **Differs**: its lagna row has Aries 1°, Virgo 2°, Aquarius 24° where PD 13.11 and HS 5.46–47 have 8°, 14°, 21° | `natal_chart/bhagas.py` `MRITYU_BHAGA_PARASARA` |
| Mṛtyu bhāga, second table (default) | The Moon's degrees 26, 12, 13, 25, 24, 11, 26, 14, 13, 25, 5, 12 from Aries | PD 13.10 (also in UK's notes). SAR ch. 5 and HS 5.47 read 4° for Virgo | `natal_chart/bhagas.py` `MRITYU_BHAGA_SARAVALI` |
| Mṛtyu bhāga of Māndi | As tabulated | **convention**: no verse checked | `natal_chart/bhagas.py` `MRITYU_BHAGA_MAANDI` |
| "A Mṛtyu bhāga of 19°" (Settings) | 19°–20°, 18.5°–19.5°, or the 19th degree 18°–19° (default) | **reading**: the texts give a degree, not a span; the three readings are offered | `natal_chart/bhagas.py` `mrityu_bhaga_distance` |
| Puṣkara bhāga (default) | The Moon's auspicious degrees 21, 14, 18, 8, 19, 9, 24, 11, 23, 14, 19, 9 from Aries | JP 1.58 (the same list as the "auspicious degrees" of UK's notes) | `natal_chart/bhagas.py` `PUSHKARA_BHAGA_SCHEME1` |
| Puṣkara bhāga, C. S. Patel's | 21°, 14°, 24°, 7° in fire, earth, air, water signs | **modern**: C. S. Patel, *Navamsa and Nadi Astrology*, as the option names it; not checked | `natal_chart/bhagas.py` `PUSHKARA_BHAGA_SCHEME2` |
| Puṣkara navāṃśas | Fire signs' 7th and 9th navāṃśas, earth 3rd and 5th, air 6th and 8th, water 1st and 3rd | **convention**: the common list; no verse checked | `natal_chart/bhagas.py` `is_in_pushkaramsha` |
| Gaṇḍānta | The last part of the water signs and the first of the fire signs | BPHS 92 (birth in gaṇḍānta) | `server/timeline.py` |

---

## 5. Special lagnas and shadow points

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Bhāva lagna | The Sun's longitude at sunrise, moving on a sign every 5 ghaṭīs (2 hours) after sunrise | BPHS 5.2–3 | `natal_chart/lagnas.py` `compute_bhava_lagna`; `time_search.py` |
| Horā lagna | The same, a sign every 2½ ghaṭīs (1 hour) | BPHS 5.4–5 | `natal_chart/lagnas.py` `compute_hora_lagna` |
| Ghaṭī lagna | The same, a sign every ghaṭī (24 minutes) | BPHS 5.6–8 | `natal_chart/lagnas.py` `compute_ghati_lagna` |
| Vighaṭī lagna | The same, a sign every vighaṭī | **convention**: the pattern of BPHS 5.2–8 carried one unit further; the time unit as in Prāṇapada (BPHS 3.71–74) | `special_lagnas_upagrahas.py` `compute_vighati_lagna` |
| "Alternative special lagna definition giving continuity" (Settings) | The lagnas move on continuously from the Sun's longitude at birth instead of from sunrise | **convention**: an option of the app | `time_search.py` `special_lagna` |
| Varṇada lagna (and of each bhava) | Counted from the lagna and the horā lagna by odd and even signs | BPHS 5.10–24 | `special_lagnas_upagrahas.py` `compute_varnada_lagna`, `compute_varnada_lagnas` |
| Śrī lagna | The lagna moved on by the Moon's part of its nakshatra × 360° | **modern**: PVR 5.7 | `special_lagnas_upagrahas.py` `compute_sree_lagna` |
| Indu lagna | The 9th lords from the lagna and the Moon, their rays (Su 30, Mo 16, Ma 6, Me 8, Ju 10, Ve 12, Sa 1) added, mod 12, counted from the Moon | UK ch. 4 (the rays as listed there) | `special_lagnas_upagrahas.py` `compute_indu_lagna`, `compute_indu_lagna_longitude` |
| Prāṇapada | Vighaṭīs since sunrise ÷ 15 as signs, added to the Sun; +240° if the Sun is in a fixed sign, +120° in a dual one | BPHS 3.71–74 | `special_lagnas_upagrahas.py` `compute_pranapada_lagna` |
| Bhṛgu Bindu | The midpoint of Rāhu and the Moon | **modern**: as named; no classical verse found | `special_lagnas_upagrahas.py` `compute_bhrigu_bindu` |
| Kuṇḍa | The lagna × 81, the navāṃśa of the navāṃśa | PM 5.8 | `special_lagnas_upagrahas.py` `compute_kunda` |
| Yogi and Avayogi points | Sun + Moon + 93°20′ | **modern**: no classical verse found | `miscellany.py` |
| The five shadow points (aprakāśa grahas) | Dhūma = Sun + 133°20′; Vyatīpāta = 360° − Dhūma; Pariveṣa = Vyatīpāta + 180°; Indracāpa = 360° − Pariveṣa; Upaketu = Indracāpa + 16°40′ | BPHS 3.61–64 | `special_lagnas_upagrahas.py` `compute_aprakash_grahas` |
| "Dhuma–Vyatipata relation" (Settings) | 360° − Dhūma (default) or Dhūma + 53°20′ | BPHS 3.61–64 for the default; the other is **convention**, an option of the app | `ephemeris/config.py` `vyatipata_method` |
| Kāla, Mṛtyu, Ardhaprahara, Yamaghaṇṭaka, Gulika (kālavelās) | Day and night each in eight parts, lorded from the weekday lord by day and from the 5th weekday lord by night, the 8th part lordless; Sun's part Kāla, Mars's Mṛtyu, Mercury's Ardhaprahara, Jupiter's Yamaghaṇṭaka, Saturn's Gulika | BPHS 3.66–69 | `special_lagnas_upagrahas.py` `kalavela_part`, `compute_kalavela_time`; `ephemeris/points.py` `kalavela_longitudes` |
| Gulika's longitude, and "Gulika / Mandi / Kala … rise at the beginning, middle or end of their portion" (Settings) | The degree rising at the start of Saturn's part | BPHS 3.70 (the start of the part). PM 5.14–16 (B. V. Raman's notes) puts Gulika at the end of Saturn's part. The middle is **convention**, an option of the app | `special_lagnas_upagrahas.py` `kalavela_offset_fraction` |
| Māndi | The degree rising within Saturn's part of the day or night, at its middle by default (Settings › "Mandi rises at") | PM 5.14–16 gives Māndi its own rising time, so many ghaṭīs after sunrise by weekday (6 on a Friday of 30 ghaṭīs), and its notes say the author takes Gulika and Māndi as one. **convention**: Māndi placed at a point of Saturn's part, an option | `special_lagnas_upagrahas.py` `kalavela_offset_fraction` |
| "Day and night, for the upagrahas" (Settings) | Day and night from sunrise and sunset (default), or from 6 am and 6 pm local mean time | BPHS 3.66–69's notes divide the day "according to altitude", the true day. The LMT halves are **convention** | `special_lagnas_upagrahas.py` |
| User's special point, graha special lagna (Settings) | A point the user defines (an offset from a graha, a midpoint, a saham or a sign); a "special lagna" moving from a graha at a chosen speed | **convention** (user-defined, for research) | `ephemeris/points.py`, `time_search.py` `special_lagna` |

---

## 6. Aspects and argalā

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Graha dṛṣṭi (which houses a graha aspects) | Every graha the 7th fully; Mars also the 4th and 8th, Jupiter the 5th and 9th, Saturn the 3rd and 10th | BPHS 26.2–5 | `aspects_friendships.py` `compute_aspect_details` |
| Sphuṭa dṛṣṭi in virupas | By the arc from the aspecting graha: 0 at 30°, 15 at 60°, 45 at 90°, 30 at 120°, 0 at 150°, 60 at 180°, falling to 0 at 300° | BPHS 26.6–12 | `aspects_friendships.py` `compute_parasara_drik_virupas`; `shadbala/engine.py` `aspect_value` |
| The special aspects' extra virupas (Settings › "Aspects of Mars, Jupiter and Saturn") | Mars +15 at the 4th and 8th, Jupiter +30 at the 5th and 9th, Saturn +45 at the 3rd and 10th | **modern**: GBB §§109–120, B. V. Raman's reading of BPHS 26 | same |
| "Full aspect value in the aspect table" (Settings) | 60 virupas or 1 (a fraction) | **convention**: a display unit | `server/windows.py` |
| Rāśi dṛṣṭi (Jaimini sign aspects) | Movable signs aspect the fixed signs except the adjacent one; fixed signs the movable except the adjacent; dual signs each other | BPHS 8.1–9 (the rāśi dṛṣṭis 8.1–3, the rule 8.4–5, the diagram 8.6–9) | `sign_strength.py` `rasi_drishti`, `aspects_friendships.py` `compute_rasi_drishti` |
| Argalā and virodhārgalā | Grahas in the 2nd, 4th, 11th (and 5th) give argalā, obstructed from the 12th, 10th, 3rd (and 9th); counted backwards from the nodes | BPHS 31.2–9 | `server/charts.py` (Highlight rasis) |
| Sambandha (relationship of two grahas) | Exchange of signs, conjunction, mutual aspect, one aspecting the other | **reading**: the four relationships the Parāśari texts use for yogas (BPHS 34; LP); no single verse checked | `aspects_friendships.py` `evaluate_planetary_sambandha` |
| Planetary Aspect Evaluation table | Each graha's aspect strength on each point, in a chosen varga | BPHS 26.6–12 | `key_info.py` `aspect_evaluation_row` |
| Nakshatra-based aspects | Aspects counted between nakshatras | **modern**: PVR 26.5 | `key_info.py`, `transits.py` |
| Tājika aspects | See [§13](#13-tājika-annual-charts-and-sahams) | | |

---

## 7. Jaimini: kārakas, ārūḍhas and the stronger sign

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Chara kārakas (Settings › "Chara karaka scheme") | The grahas ranked by degrees in their signs, the highest the ātmakāraka; seven (Sun to Saturn) or eight (with Rāhu, his degrees counted from 30°) | BPHS 32.1–8 (seven, or "the 8 Grahas, including Rahu"; Rāhu from 30°), the names 32.13–17 | `natal_chart/karakas.py` `compute_chara_karakas`, `chara_karaka_slots` |
| Kārakāṃśa | The ātmakāraka's navāṃśa sign | BPHS 33 | `natal_chart/karakas.py` |
| Ārūḍha padas of the bhavas (A1–A12) | As far from the bhava's lord as the lord is from the bhava | BPHS 29.1–3 | `natal_chart/arudhas.py` `compute_arudha_pada`, `sign_strength.py` `bhava_arudhas` |
| The exceptions (Settings › "Bhava arudhas") | A pad in the bhava itself moves to its 10th; in the 7th, to the 4th | BPHS 29.4–5. Off: the rule without exceptions, **convention** | same |
| Graha ārūḍhas (Settings › "Graha arudhas") | As far from the graha's own sign as that sign is from the graha; of two own signs, the stronger | BPHS 29.6–7. The exceptions applied to grahas as to bhavas are **reading** | `natal_chart/arudhas.py` `compute_graha_arudha`, `sign_strength.py` `graha_arudha` |
| Upapada | The ārūḍha of the 12th bhava | BPHS 30.1–6 ("calculated for the Bhava, following the natal Lagn") | `natal_chart/arudhas.py` |
| Rāhu and Ketu as lords of Aquarius and Scorpio in ārūḍhas (Settings) | When the node is the stronger co-lord | Co-lordship BPHS 47.34–39; the stronger co-lord **modern**: PVR 15.5.1 | `sign_strength.py` `stronger_co_lord` |
| Ārūḍhas from exact longitudes (Settings, three options) | The pad counted by degrees, not signs, in the rasi or a varga | **convention**: options of the app; no text | `sign_strength.py` `longitude_bhava_arudhas` |
| The stronger of two signs | A cascade of tests: grahas in the sign, aspects of Jupiter, Mercury and the lord, the lord's dignity, the lord's degrees, the modality … | **modern**: PVR 15.5.2, the rules taught from the Jaimini Upadeśa Sūtras | `sign_strength.py` `stronger_sign`, `stronger_by_dignity`, `stronger_own_sign` |
| The stronger co-lord | Mars or Ketu for Scorpio, Saturn or Rāhu for Aquarius | **modern**: PVR 15.5.1 | `sign_strength.py` `stronger_co_lord`, `stronger_co_lord_dasa` |
| Brahmā, Rudra, Maheśvara | The grahas chosen by their rules | BPHS 46.170–173; JUS 2.1 | `key_info.py` `brahma_rudra_maheswara`, `dasa_systems/rasi.py` `brahma_planet` |
| Nārāyaṇa daśā's direction exceptions | Saturn in a sign takes the dasa forward, Ketu backward | **modern**: PVR ch. 18 | `sign_strength.py` `direction_override` |

---

## 8. Pañcāṅga, muhūrta and calendars

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Tithi | (Moon − Sun) in parts of 12° | SS 2.66 | `ephemeris/day.py` `panchanga`, `panchanga.py`, `time_search.py` `lunar_day` |
| Nakshatra | The Moon's longitude in parts of 13°20′ | SS 2.64 | same |
| Yoga | (Sun + Moon) in parts of 13°20′ | SS 2.65 | same, `time_search.py` `sum_event` |
| Karaṇa | Half-tithis: the four fixed (Śakuni, Catuṣpada, Nāga, Kiṃstughna) and the seven movable (Bava …) eight times each | SS 2.67–69 | `ephemeris/day.py` `_karana_index`, `panchanga.py` |
| Vāra (weekday) and its lord | From sunrise, lords in the order of the days | SS 1.51–52; BPHS 27.13 | `ephemeris/day.py` `day_lords` |
| End times of each element | Found by search over time, the next one from 0.1 day after an end | **astronomy**: root finding, see [§12](#12-transits-key-information-and-searches) | `daily_panchanga.py` |
| Lords of the tithi, yoga and karaṇa | Tithi: Sun … Rāhu from each pakṣa's start (Saturn on the 15th, Rāhu on the 30th); yoga: the Vimśottarī lords from Saturn's (Puṣya's) on; karaṇa: the seven movable ones Sun … Saturn, the four fixed by a sign counted from the lagna | **convention**: the lords as the app tabulates them them; no verse checked | `ephemeris/day.py` `_TITHI_LORDS`, `_YOGA_LORDS`; `dasa_systems/nakshatra.py` `TITHI_LORD` |
| Special tithis (36) | The tithi of k × (Moon − Sun), k = 1 … 36 | **convention**: no verse checked | `key_info.py` `special_tithis`, `panchanga.py` `compute_bhava_tithis` |
| Rāhu kāla, Gulika kāla, Yamaghaṇṭa | An eighth of the daytime: Rāhu the 8th, 2nd, 7th, 5th, 6th, 4th, 3rd eighth from Sunday | KP ch. 33 (its table: Sunday 4:30–6, Monday 7:30–9 … with sunrise at 6). UK's notes (Second Kāṇḍa 29): "observed specially in Tamil Nadu, Karnataka, and Kerala. Standard texts have no mention of it" | `panchanga.py` `RAHU_KALAM_PARTS`, `YAMA_GHANTAM_PARTS`, `GULIKA_KALAM_PARTS` |
| Muhūrtas of the day | 15 by day and 15 by night, the day's 1st, 2nd, 4th, 10th, 11th, 12th, 15th inauspicious | PM 2.21 (notes) | `panchanga.py` |
| Durmuhūrtas by weekday | One or two fifteenths of the day for each weekday | **convention**: the app's weekday table; no verse checked (PM 2.21 gives no weekday list). Common lists give Wednesday the 5th and Thursday the 6th and 13th | `panchanga.py` `DURMUHURTA_PARTS` |
| Abhijit muhūrta, Brahma muhūrta | The 8th muhūrta of the day; two muhūrtas before sunrise | **reading**: the fifteen day-muhūrtas as above; see [§1.3](#13-sunrise-the-day-and-its-lords) | `panchanga.py`, `house_systems.py` |
| Tyājya (varjyam, viṣa ghaṭikā) | Starts so many ghaṭīs (of 60 in the nakshatra) into each nakshatra and lasts 4 of them, a fifteenth of it | PM 2.21 (notes and table) and UK's notes list 50 24 30 40 14 11 30 20 32 30 20 18 22 20 14 14 10 14 20 24 20 10 10 18 16 24 30 from Aśvinī. **Differs**: the app's table has Bharaṇī 4, Ārdrā 21, U. Phalgunī 1, Hasta 21, P. Āṣāḍhā 20, U. Bhādrapadā 30 | `panchanga.py` `TYAJYA_GHATIS`, `tyajya_time` |
| Gowri pañcāṅgam | Eighths of the day and night named in the weekday's order | **convention**: the Tamil almanacs' practice; no verse checked | `panchanga.py` `compute_gowri_panchangam` |
| Choghaḍiyā | Eighths of the day and night | **convention**: the North and West Indian almanacs' practice; no verse checked | `miscellany.py` `compute_choghadiya_muhurta`, `server/muhurta.py` |
| Muhūrta search (Muhurta tab, "Find a muhurta") | Pañcāṅga śuddhi by event: allowed tithis, nakshatras, months; kharmās; combust planets; Pañcaka | MC (by prakaraṇa) "and common practice", as `data/muhurta_rules.json` states; editable data, not code | `server/muhurta.py`, `data/muhurta_rules.json` |
| Lunar month (Settings › Calendars) | Amānta or pūrṇimānta; named from the sign the Sun is in at its start (sidereal or tropical); adhika months | SS 14.12–14 (lunar months). **reading**: SS 14.16 names the months by the nakshatra of the full moon; naming them by the sign the Sun is in at the new moon is the almanacs' equivalent rule | `server/calendars.py`, `time_search.py` `lunar_month` |
| Solar month and year (Settings) | The Sun's entry (saṅkrānti) into each sign; the year from the chosen sign | SS 14.3 (solar time, the saṅkrāntis) | `time_search.py` `solar_month` |
| Festivals and observances | A lunar festival takes the tithi covering a stated part of the day (sunrise, aruṇodaya, pūrvāhṇa, madhyāhna, aparāhṇa, pradoṣa, niśītha, moonrise); Ekādaśī by the Smārta or Vaiṣṇava rule | *Dharmasindhu*'s kālas, as `server/festivals.py` names them; editable data (`data/festivals.json`) | `server/festivals.py` |
| Barhaspatya saṃvatsara | The 60-year Jupiter cycle | BS 8 (*Bṛhaspati-cāra*, Jupiter's course); verse not checked | `server/timeline.py` |

---

## 9. Daśās

The years run on the chosen year definition (Settings › Dasa years, [§9.1](#91-the-dasa-year)). BPHS 46.2–11 names
most of these daśās; the verses below define each. Antardaśās: BPHS 51.1–2 for graha daśās (the lord's share in
proportion to its years, starting from the lord), 51.3–4 for rasi daśās; BJ 8.3 for the weighted sub-periods.

### Nakshatra daśās

| Daśā | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Vimśottarī | Lords Su Mo Ma Ra Ju Sa Me Ke Ve from Kṛttikā, 6 10 7 18 16 19 17 7 20 years; balance by the Moon's part of its nakshatra still to run | BPHS 46.12–16 | `dashas.py` `compute_vimshottari_tree`, `dasa_systems/nakshatra.py` `vimsottari_dasa` |
| Aṣṭottarī | 108 years from Ārdrā, groups of 4 and 3 stars: Su 6, Mo 15, Ma 8, Me 17, Sa 10, Ju 19, Ra 12, Ve 21 | BPHS 46.17–22 | `dasa_systems/nakshatra.py` `group_dasa` |
| Ṣoḍaśottarī | 116 years | BPHS 46.23–26 | `dasa_systems/nakshatra.py` `nakshatra_dasa` |
| Dvādaśottarī | 112 years | BPHS 46.27–28 | same |
| Pañcottarī | From Anurādhā; Su Me Sa Ma Ve Mo Ju, 12 … 18 years | BPHS 46.29–30 | same |
| Śatābdikā | From Revatī; Su Mo Ve Me Ju Ma Sa, 5 5 10 10 20 20 30 years | BPHS 46.31–34 | same |
| Caturaśīti-sama | From Svātī; seven lords, 12 years each | BPHS 46.35–36 | same |
| Dvisaptati-sama | 72 years | BPHS 46.37–39 | same |
| Ṣaṣṭihāyanī | 60 years | BPHS 46.40–41 | `dasa_systems/nakshatra.py` `group_dasa` |
| Ṣaṭtriṃśat-sama | From Śravaṇa, eight lords, 36 years | BPHS 46.42–43 | `dasa_systems/nakshatra.py` `nakshatra_dasa` |
| Yoginī | (Janma nakshatra + 3) mod 8; Maṅgalā … Saṅkaṭā of Mo Su Ju Ma Me Sa Ve Ra, 1 … 8 years | BPHS 46.195–199 | `dashas.py` `compute_yogini_dasa`, `dasa_systems/nakshatra.py` |
| Which conditional daśā applies | Each daśā's condition (Rāhu not in lagna but in a kendra or trikoṇa from the lagna lord for Aṣṭottarī; lagna vargottama for Śatābdikā; …) and its controlling planet's strength | BPHS 46.17–43 (the conditions); **modern**: the ranking by the controlling planet's strength is P. V. R. Narasimha Rao's, *Unified Nakshatra Dasa Approach: In Annual & Natal Charts* (2014) | `conditional_dasas.py` `best_dasa` |
| Kālacakra | Savya and apasavya cycles of nakshatra padas, each pada's nine signs with Deha and Jīva; years Su 5, Mo 21, Ma 7, Me 9, Ju 10, Ve 16, Sa 4 | BPHS 46.52–95 (the cycles 54–82, the years 84, the balance 90–93), the gatis 96–100 | `dasa_systems/kalachakra.py` |
| Kālacakra variants (Settings › Kalachakra dasa) | Santhanam; Dr. Raman; "version 5.0"; Rao & Rath; Raghavacharya (default); S. M. Singh | **modern**: the readings the option names (R. Santhanam, B. V. Raman, P. V. R. Narasimha Rao with Sanjay Rath, Raghavacharya, S. M. Singh); PVR ch. 24 teaches the daśā. Not checked against each author | same |
| Kālacakra: Rohiṇī's 4th pada | Cancer or Leo navāṃśa | **reading**: BPHS 46.73–76 lists Rohiṇī's padas; editions differ on its 4th | same |
| Saptarṣi nakshatra | 27 nakshatras backwards from the lagna's, 10 years each | **modern**: Pt. Sanjay Rath ("not mentioned by any rishis") | `dasa_systems/nakshatra.py` `saptarshi_dasa` |
| Seeds (Settings › Nakshatra dasas › Seed) | The Moon, or the 5th, 4th, 8th star from it (utpanna, kṣema, ādhāna), lagna, Māndi, Gulika, the sphuṭas, a graha, Bhṛgu Bindu, Indu lagna, Prāṇapada | BPHS 46.16 (the Moon); PVR 16.4.1–16.4.2 (the kṣema, utpanna, ādhāna stars and the lagna). **modern**: the other seeds as named; no publication checked | `ephemeris/points.py` `vimsottari_seed_longitude`, `dasa_systems/nakshatra.py` `dasa_seed` |
| Antardaśā order (Settings) | From the daśā lord forward (default), or backward, or from the next / previous lord | BPHS 51.2 (from the lord, in the daśā order); the others **modern**, as named; no publication checked | `dasa_systems/nakshatra.py` `nak_ad_position` |
| Tribhāgī | Each mahādaśā a third of its length, the cycle run three times | **modern**: as named; no publication checked | `dasa_systems/nakshatra.py` `_conditional` |
| Tithi Aṣṭottarī, Tithi Yoginī | Aṣṭottarī / Yoginī lords from the janma tithi's lord, balance of the tithi | **modern**: P. V. R. Narasimha Rao's Tithi Praveśa teaching | `dasa_systems/nakshatra.py` |
| Yoga Vimśottarī | Vimśottarī from the lord of the yoga (Sun + Moon) | **modern**: the research of P. V. R. Narasimha Rao | `dasa_systems/nakshatra.py` `yoga_vimsottari_dasa` |
| Karaṇa Caturaśīti-sama | Su … Sa, 12 years each, from the karaṇa's lord | **modern**: P. V. R. Narasimha Rao's Tithi / Karaṇa Praveśa teaching | `dasa_systems/nakshatra.py`, `tithi_pravesha.py` |

### Rasi daśās

| Daśā | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Chara (Parāśara) | Every sign from the lagna, forward or backward by the 9th's pada; years = signs to the lord (12 in its own sign), +1 exalted, −1 debilitated; Scorpio and Aquarius by the stronger lord | BPHS 46.158–167 | `dasa_systems/rasi.py` `chara_parasara_dasa`, `dashas.py` `compute_chara_dasa` |
| Chara (K. N. Rao) | As K. N. Rao teaches it (no exaltation rule) | **modern**: K. N. Rao, *Predicting through Jaimini's Chara Dasha* | `dasa_systems/rasi.py` `chara_knrao_dasa` |
| Chara (Iranganti Rangacharya) | From the lagna by the modality's steps | **modern**: Iranganti Rangacharya's reading of the Jaimini commentaries of Raghava Bhatta and Nṛsiṃha Sūri | `dasa_systems/rasi.py` `chara_rangacharya_dasa` |
| Nārāyaṇa | From the stronger of the lagna and the 7th; order by modality; years to the lord; Saturn forward, Ketu backward | JUS 1.1 (the rasi daśās). **modern**: as PVR ch. 18 teaches it | `dasa_systems/rasi.py` `narayana_dasa`, `dashas.py` |
| Lagnāṃśaka, Padanāthāṃśa | Nārāyaṇa daśā from the D-9 lagna, or from the navāṃśa of the arudha lagna's lord | **modern**: Sanjay Rath's Nārāyaṇa variants, as named | `dasa_systems/rasi.py` |
| Lagna Kendrādi rasi | Kendras, paṇapharas, āpoklimas from the stronger of the lagna and the 7th | BPHS 46.175–177 (Kendrādi); PVR ch. 19 | `dasa_systems/rasi.py` `lagna_kendradi_rasi_dasa` |
| Ātmakāraka Kendrādi rasi; AK Kendrādi graha | The same from the ātmakāraka | **modern**: as named; no publication checked | `dasa_systems/rasi.py`, `dasa_systems/graha.py` |
| Sudaśā | From the strongest kendra of the Śrī lagna, the first period cut to the Śrī lagna's part still to run | **modern**: PVR ch. 20 (Śrī lagna, [§5](#5-special-lagnas-and-shadow-points)) | `dasa_systems/rasi.py` `sudasa` |
| Dṛg daśā | The 9th, 10th, 11th, each followed by the signs it aspects; 7, 8, 9 years by modality | BPHS 46.185–187; JUS 2.4; PVR ch. 21 | `dasa_systems/rasi.py` `drig_dasa` |
| Dṛg daśā, "SJC teachers 1998–2007" (Settings) | The variant taught then | **modern**: the Sri Jagannath Centre's earlier teaching, as named | same |
| Trikoṇa | From the strongest of the lagna and its trines | BPHS 46.183–184; JUS 2.4 | `dasa_systems/rasi.py` `trikona_dasa` |
| Yogārdha | The mean of the Chara and Sthira years | BPHS 46.174; JUS 2.4 | `dasa_systems/rasi.py` `yogardha_dasa` |
| Sthira | From the Brahmā graha's sign; 7, 8, 9 years for movable, fixed, dual | BPHS 46.168–169; JUS 2.3 | `dasa_systems/rasi.py` `sthira_dasa` |
| Brahmā | From Brahmā (the graha chosen by 46.170–173's rules) | BPHS 46.170–173; JUS 2.1 (Brahmā, Rudra, Maheśvara) | `dasa_systems/rasi.py` `brahma_planet`, `brahma_dasa` |
| Śūla | 9 years each from the stronger of the lagna and the 7th | BPHS 46.181–182; JUS 2.2–2.3; PVR ch. 23 | `dasa_systems/rasi.py` `shoola_dasa` |
| Niryāṇa Śūla | From the stronger of the 2nd and 8th; 7, 8, 9 years | JUS 2.2–2.3; PVR ch. 22 | `dasa_systems/rasi.py` `niryaana_shoola_dasa` |
| Navāṃśa | 9 years each | JUS 2.3 | `dasa_systems/rasi.py` `navamsa_dasa` |
| Maṇḍūka | From the lagna or the 7th, the frog's jump | BPHS 46.179–180; the D-11 form **modern** (Sanjay Rath), the K. N. Rao form **modern** | `dasa_systems/rasi.py` `mandooka_d11_dasa`, `mandooka_knrao_dasa` |
| Varṇada | From the stronger of the lagna and the horā lagna; years from the Varṇada lagna | BPHS 5.10–24 | `dasa_systems/rasi.py` `varnada_dasa` |
| Paryāya | From the house of the varga's own number in that varga | **modern**: as named; no publication checked | `dasa_systems/rasi.py` `paryaya_dasa` |
| Chakra | 10 years each, from the lagna lord's sign (day), the lagna (night) or the 2nd (twilight) | BPHS 46.50–51 | `dasa_systems/rasi.py` `chakra_dasa` |
| Sudarśana Cakra | A year for each sign from the lagna, Moon and Sun together | BPHS 74 (Sudarśana cakra); PVR ch. 31 | `dasa_systems/graha.py` `sudarsana_chakra_dasa` |

### Graha and other daśās

| Daśā | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Mūla | The strongest of lagna, Sun and Moon first, then the grahas in kendras, paṇapharas, āpoklimas by strength | BJ 8.1–2 (and the antardaśās 8.3). **modern**: the years (Vimśottarī years less the signs to the moolatrikoṇa) are Sanjay Rath's | `dasa_systems/graha.py` `moola_dasa` |
| Naisargika | Mo 1, Ma 2, Me 9, Ve 20, Ju 18, Su 20, Sa 50, lagna 12; antardaśās weighted ½ conjunct, ⅓ in trines, 1/7 in the 7th, ¼ in the 4th / 8th | BPHS 43.16–17 (Nisargāyu years), 3.48; BJ 8.3 (the weights) | `dasa_systems/graha.py` `naisargika_dasa` |
| Tārā (Parāśara's / Sanjay Rath's, Settings) | The grahas in kendras from the lagna, then paṇapharas, āpoklimas; Vimśottarī years | BPHS 46.207–209 (Parāśara); **modern**: Pt. Sanjay Rath's teaching (default) | `dasa_systems/graha.py` `tara_dasa` |
| Kāla | Day and night in parts around the twilights; Sun's period × 1 … Ketu × 9, then again | BPHS 46.44–49 | `dasa_systems/rasi.py` `kaala_dasa` |
| Kāraka | AK … DK, years = signs from the lagna | BPHS 46.178 | `dasa_systems/graha.py` `karaka_dasa` |
| Buddhi gati | The grahas by house from the 4th | **modern**: as the option names its source (the Agni Purāṇa); not checked | `dasa_systems/graha.py` `buddhi_gati_dasa` |
| Pātyāyinī | Lagna and the grahas by their degrees in the sign; differences scaled to the year | TN (Tājika daśā); PVR ch. 30 | `dasa_systems/rasi.py` `patyayini_dasa` |
| Rasi-bhukta Vimśottarī | Vimśottarī mahādaśās with the 12 signs as antardaśās | **modern**: as named | `dasa_systems/rasi.py` |

### 9.1 The dasa year

| Choice (Settings › Dasa years) | Rule | Source |
| :--- | :--- | :--- |
| True sidereal solar year (default) | The Sun moving 360° sidereally | SS 14.3 (solar time); PVR 16.2 ("most scholars … use solar years") |
| True tropical solar year | The Sun moving 360° tropically | **astronomy** |
| Mean sidereal / mean tropical solar year | 365.256364 / 365.24219 days | **astronomy** |
| Sāvana year | 360 days | SS 14.18–19 (civil time); PVR 16.2 (the author's preference) |
| Year of 360 tithis | The Moon gaining 4320° on the Sun | SS 14.12–13 (lunar time); PVR 16.2 |
| The Moon's 360 stars (definition 5) | The Moon back at its natal longitude 12 times… | PVR 16.2 ("a period in which Moon traverses through 360 constellations") |
| User-defined | n days | **convention** |
| Tājaka and Tithi Praveśa charts | True sidereal solar year; 360 tithis | **convention** (Settings), following the charts' own clocks |
| Daśā seṣam in mundane charts | The first period cut to its balance, or not | **convention** |

---

## 10. Strengths, avasthās, Aṣṭakavarga and longevity

"Which is stronger" always compares each strength with its own minimum: Ṣaḍbala as a share of the required rupas
(BPHS 27.32–36), Bhāva bala as a share of 7 rupas (**convention**: the app's yardstick; Raman's GBB states Bhāva
bala in rupas but gives no minimum).

### 10.1 Ṣaḍbala and Bhāva bala

| Part | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Uccha bala | A third of the graha's distance from its debilitation point, in virupas | BPHS 27.1–1½ | `shadbala/components.py` `compute_uchcha_bala`; `shadbala/engine.py` `shadbala_and_bhava_bala` |
| Saptavargaja bala | 45, 30, 20, 15, 10, 4, 2 virupas for moolatrikona, own, great friend's, friend's, neutral's, enemy's, great enemy's sign, in the seven vargas | BPHS 27.2–4 | `shadbala/components.py` `compute_saptavargaja_bala` |
| "Moolatrikona degrees in Shadbala" (Settings) | BPHS's degrees, or the narrow ones | See [§2](#2-signs-nakshatras-and-dignities) | `shadbala/engine.py` `set_moolatrikona_bphs` |
| Ojayugmarāśyaṃśa bala | Moon and Venus in even signs and navāṃśas, the others in odd ones, 15 virupas each | BPHS 27.4½ | `shadbala/components.py` `compute_ojayugmarasyamsa_bala` |
| Kendrādi bala | 60, 30, 15 virupas in kendras, paṇapharas, āpoklimas | BPHS 27.5 | `shadbala/components.py` |
| Drekkāṇa bala | Male, female, neuter grahas strong in the 1st, 2nd, 3rd drekkāṇa | BPHS 27.6 | `shadbala/components.py` `compute_drekkana_bala` |
| Dig bala | A third of the distance from the point of no strength: the 4th for Sun and Mars, the 7th for Jupiter and Mercury, the 10th for Venus and Moon, the lagna for Saturn | BPHS 27.7–7½ | `shadbala/components.py` `compute_dig_bala` |
| Nathonnata bala | By the distance from midnight (diurnal grahas) or noon (nocturnal); Mercury always full | BPHS 27.8–9 | `shadbala/components.py` `compute_nathonnatha_bala` |
| Pakṣa bala | By the Moon's elongation; benefics in the bright half, malefics in the dark | BPHS 27.10–11 | `shadbala/components.py` |
| Tribhāga bala | Mercury, Sun, Saturn in the thirds of the day; Moon, Venus, Mars in the thirds of the night; Jupiter always | BPHS 27.12 | `shadbala/components.py` `compute_tribhaga_bala` |
| Varṣa, māsa, dina, horā bala | 15, 30, 45, 60 virupas to the lords of the year, month, day and hora | BPHS 27.13 | `shadbala/components.py` `compute_temporal_lords_bala` |
| Naisargika bala | 60 × k / 7 virupas, Saturn 1 to the Sun 7 | BPHS 27.14 | `shadbala/components.py` |
| Ayana bala | By the declination, with the khaṇḍas 45, 33, 12 | BPHS 27.15–17 | `shadbala/components.py` `compute_ayana_bala` |
| Ceṣṭā bala | The Sun's is his ayana bala, the Moon's her pakṣa bala; Mars to Saturn by their ceṣṭā kendra (mean and true longitudes) | BPHS 27.18, 27.21–25 | `shadbala/components.py` `compute_cheshta_bala` |
| Dṛk bala | A quarter of the aspects received, benefic added, malefic taken away | BPHS 27.19 | `shadbala/engine.py` `aspect_value` |
| Yuddha bala | The war's loser gives the difference to the winner | BPHS 27.20 (the war itself SS 7.18–21, see [§2](#2-signs-nakshatras-and-dignities)) | `shadbala/components.py` `compute_graha_yuddha_bala` |
| Required Ṣaḍbala | 390, 360, 300, 420, 390, 330, 300 virupas, Sun to Saturn | BPHS 27.32–33; GBB §122 | `shadbala` `SHADBALA_REQUIREMENTS` |
| Bhāva bala | Bhāva's lord's strength, its dig bala, the aspects on it; Jupiter and Mercury's houses +60, the rules of 27.30–31 | BPHS 27.26–31 | `shadbala/bhava.py` |
| Iṣṭa and Kaṣṭa phala | From the uccha and ceṣṭā raśmis | BPHS 28.2–6 | `shadbala/engine.py` `rashmis_ishta_kashta` |
| Vimśopaka bala | The dignity in the ṣaḍ-, sapta-, daśa- and ṣoḍaśavargas, weighted per varga, of 20 | BPHS 7.17–27 | `shadbala/vimsopaka.py` |
| "Compound relationships in vimsopaka" (Settings) | The rasi chart's relationships in every varga, or each varga's own | **convention**: an option of the app | `shadbala/vimsopaka.py` |
| Vaiśeṣikāṃśa | Own, exaltation or moolatrikona signs counted over the varga groups, the amśas named Pārijāta … | BPHS 6.42–53 | `shadbala/vimsopaka.py` `compute_vaiseshikamsa`, `shadbala/engine.py` `AmsaBala` |
| What "swarudha" means, and the eleven "Annul the swarudha placement" options (Settings) | Which placements count, and combustion, defeat, debilitation or a poor avastha of the graha or its dispositor cancelling them | **convention**: options of the app; no verse checked | `shadbala/engine.py` `_swarudha_good` |

### 10.2 Avasthās

| Avasthā | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Bālādi (age) | Six degrees each, Bāla … Mṛta in odd signs, reversed in even | BPHS 45.3–4 | `avasthas.py` `compute_baalaadi_avastha`, `graha_avasthas` |
| Jāgradādi (alertness) | Awake in own sign or exaltation, dreaming in a friend's or neutral's, asleep in an enemy's or debilitation | BPHS 45.5–6 | same |
| Dīptādi (mood), Parāśara's nine | Dīpta exalted, Svastha own, Pramudita great friend's, Śānta friend's, Dīna neutral's, Vikala with a malefic, Duḥkhita enemy's, Khala great enemy's, Kopa eclipsed by the Sun | BPHS 45.7–10 | `avasthas.py` `graha_avasthas` (`parashara_mood_names`) |
| Dīptādi, the app's eleven | As above, with Khala "by union with the Varga of a malefic" (a malefic's sign), Kopita within 6° of the Sun, and Lajjita and Garvita added | PD 3.18–19 (Khala); BPHS 45.11–18 (Lajjita, Garvita); the 6° orb **convention** | same (`mood_names`) |
| Lajjitādi | Lajjita, Garvita, Kṣudhita, Tṛṣita, Mudita, Kṣobhita | BPHS 45.11–18 | `avasthas.py` |
| Śayanādi (activity) and its sub-state | (nakshatra × graha number × navāṃśa + Moon's nakshatra + ghaṭīs + lagna) mod 12; the sub-state (avasthā² + the name's first syllable's aṅka) mod 12 + the graha's additive (Su 5, Mo 2, Ma 2, Me 3, Ju 5, Ve 3, Sa 3, Ra 4), mod 3 | BPHS 45.30–37 (shown for each of the five aṅka values) | same |
| "Relationships in the avasthas" (Settings) | Natural or compound relationship with the sign's lord | BPHS 3.55 / 3.57–58 | same |

### 10.3 Aṣṭakavarga

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Bindus (Prastāra, BAV, SAV) | From each of the seven grahas and the lagna, the houses that give a bindu | BPHS 66 | `ashtakavarga.py` `compute_prastara_ashtakavarga`, `ashtakavarga_tables` |
| The six cells where the texts differ (Settings › Ashtakavarga, six options) | Moon benefic in the 9th from the Moon, malefic in the 9th from Mars, benefic in the 2nd and malefic in the 12th from Jupiter; Venus benefic in the 4th and malefic in the 5th from Mars | BPHS 66 (all set, the default) against BJ 9 | `ashtakavarga.py` `PARASARA_CELLS` |
| "Meaning of the references", "Consolidate bhavas … when finding SAV", the lagna's row in the SAV (Settings) | Whose row a bindu counts in; SAV by houses; 8 contributors | **convention**: options of the app | `ashtakavarga.py` `compute_bhava_driven_sav`, `compute_eight_contributor_sav` |
| Trikoṇa śodhana | The least of each trine taken from all three | BPHS 67 | `ashtakavarga.py` `trikona_sodhana` |
| Ekādhipatya śodhana | The two signs of one lord reduced by their occupancy | BPHS 68 | `ashtakavarga.py` `ekadhipatya_sodhana`, `_ekadhipatya_pair` |
| Rāśi, graha and śodhya piṇḍas | Sign multipliers 7 10 8 4 10 5 7 8 9 5 11 12 (Aries to Pisces) and the grahas' multipliers | BPHS 69 | `ashtakavarga.py` `compute_shodhya_pinda` |
| Piṇḍa × bindus ÷ 27 (÷ 12): the nakshatra (sign) whose transit by Saturn harms | | BPHS 70.10–11, 70.41–42 | `server/strengths.py` |
| Transits by bindus and kakṣyās | Each sign in 8 kakṣyās of 3°45′, lorded Saturn … Moon, lagna | **modern**: PVR 25.5.2 | `kakshyas.py`, `server/transits.py` |
| Longevity from the Aṣṭakavarga | Each sign's span by its rekhās | BPHS 71.1–4 | `ashtakavarga.py` `compute_ashtakavarga_ayurdaya`, `ayurdaya.py` `ashtakavarga_years` |
| Saturn's Aṣṭakavarga and the years of distress | | BPHS 70.37–42 | `ayurdaya.py` `saturn_ashtakavarga` |
| Aggregate aṣṭakavargas | | BPHS 72 | `ashtakavarga.py` |

### 10.4 Longevity (āyurdāya) and mārakas

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Piṇḍāyu | Full years at deep exaltation, half at deep debilitation, by the rule of three between | BPHS 43.4–8 | `ayurdaya.py` `arc_years` |
| Its reductions | The visible half; a malefic in the lagna | BPHS 43.9–13, 43.22 | `ayurdaya.py` `_reductions`, `_lagna_cut` |
| The lagna's years | | BPHS 43.14–15 | `ayurdaya.py` `lagna_years` |
| Aṃśāyu | A year a navāṃśa from Aries, with the same reductions; trebled or doubled | BPHS 43.18–22 | `ayurdaya.py` `navamsa_years`, `amsayu` |
| Nisargāyu | The natural years | BPHS 43.16–17. **reading**: BPHS gives only the years; the arc is worked as for Piṇḍāyu, as later texts do | `ayurdaya.py` `_arc_span` |
| Which of the three applies | The strongest of lagna, Sun and Moon | BPHS 43.30–32 | `ayurdaya.py` `spans` |
| The three pairs | Lagna–8th lord, Moon–Saturn, lagna–horā lagna, by modality; the class of two or three that agree | BPHS 43.33–50 (Settings: Saturn and Jupiter's corrections, 43.47) | `ayurdaya.py` `three_pairs` |
| Classes of life | Short before 32, medium to 64, long to 100 | BPHS 44.10–14. The compartments within each class (120 to 80 …) are **modern**, from the Jaimini tables | `ayurdaya.py` `class_of_years` |
| Placement and the Sun | The lords of the lagna and 8th in kendras, paṇapharas, āpoklimas; the lagna lord's relation to the Sun | BPHS 43.71–73 | `ayurdaya.py` `placement`, `sun_relation` |
| Mārakas | The 2nd and 7th and their lords, and the others BPHS names | BPHS 44 (44.3, 44.9, 44.22–31), the app's help "Marakas" | `ayurdaya.py` `marakas` |
| Māraka stars | The stars from the birth star whose lords may kill | BPHS 44.15–21 | `ayurdaya.py` `maraka_stars` |
| Manner of death | From the 3rd and 8th | BPHS 44.25–39 | `ayurdaya.py` `death_circumstances` |
| Short life, evils at birth | | BPHS 9 and 10 | `ayurdaya.py` |
| Rudra and Triśūla | The Śūla daśās' readings | **modern**: PVR chs. 22–23, the app's help on the Śūla daśās | `server/longevity.py` |

---

## 11. Yogas

Each yoga's verses are kept beside its check in `yoga_engine/catalogue.py` (`YOGA_SOURCES`, 112 yogas). The groups
and their chapters:

| Group | Source | Code |
| :--- | :--- | :--- |
| Mahāpuruṣa (Haṃsa, Mālavya, Bhadra, Rucaka, Śaśa) | BPHS 75.1–2; PD 6.1–4 | `yoga_engine/engine.py` |
| Solar (Ubhayacarī, Veśi, Vośi; Nipuṇa) | BPHS 38.1–3; PD 6.8–10 | same |
| Lunar (Sunaphā, Anaphā, Durudharā, Kemadruma, Adhi; Gaja-Kesarī) | BPHS 37.5–13, 36.3–4; PD 6.5–7, 6.14–16, 6.42–43 | same |
| Nābhasa (32: Rajju … Gola) | BPHS 35.7–49 | same |
| Other popular yogas (50) | BPHS 36; PD 6 | same |
| Rāja yogas, yoga kāraka | BPHS 34.11–14, 39 | same |
| Rāja sambandha | BPHS 40 | same |
| Dhana | BPHS 41 | same |
| Daridra | BPHS 42 | same |
| Pravrajyā | BPHS 79.2–3 | same |
| Laghu Pārāśarī (functional natures, kendrādhipatya, rāja yogas, mārakas) | LP's chapters on the lords, yogas and longevity; BPHS 34, 39, 44 | `laghu_parasari.py` |

27 of the 112 have no verse checked: Nipuṇa (Budha-Āditya), Candra-Maṅgala, Guru-Maṅgala, Kulavardhana, Go,
Vidyut, Cāpa, Makuṭa, Jaya, Tapasvī, Sādhu, Brahmā (2), Viṣṇu, Śiva, Trilocana, Caṇḍikā, Bhāratī, Aṃśāvatāra,
Devendra, Indra, Ravi, Bhāskara, Gandharva, Mahā Yogada, Yogada (GL), Yogada (HL) and Viparīta Rāja yoga (marked ""
in `YOGA_SOURCES`). Their verses were not found in the editions above, so for these the rule is the catalogue's.

---

## 12. Transits, key information and searches

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Gochara from the natal Moon, and vedha | The good houses for each graha and the houses that obstruct them | PD 26.2–8 (vedha 26.3–5) | `transits.py` `evaluate_gochara_transit`, `gochara_vedha` |
| Mūrti (gold, silver, copper, iron) | By the Moon's house from the natal Moon when the graha entered its sign | **modern**: PVR 26.2 | `transits.py` `compute_murthi_nirnaya`, `server/transits.py` |
| Rāśi gochara vedha | | **modern**: PVR 26.3 | `transits.py` |
| The nine tārās | Janma, Sampat, Vipat, Kṣema, Pratyak, Sādhana, Naidhana, Mitra, Parama-mitra, from the natal star (or the lagna's) | **modern**: PVR 26.4.1 | `key_info.py`, `chakras.py` |
| Special nakshatras | Karma, Sāṅghātika, Sāmudāyika, Vaināśika, Mānasa … on the 28-star wheel | **modern**: PVR 26.4.2 | `key_info.py` `transit_special_nakshatras` |
| Nakshatra aspects | | **modern**: PVR 26.5 | `key_info.py` |
| Lattās (forward and rear kicks) | Sun the 12th star, Mars the 3rd, Jupiter the 6th, Saturn the 8th forward; Venus the 5th, Mercury the 7th, Rāhu the 9th, Moon the 22nd backward | PD 26.42–47 | `transits.py` `LATTA_RULES`, `key_info.py` |
| Aṅga graha (the limb a transit falls on) | Per graha, by the count from the natal star: Sun face 1, head 2–5, chest 6–9 … | PD 26.35–40 (the Sun's 26.35); PVR 26.6 | `key_info.py` `anga_graha` |
| Sapta Śalākā | | PD 26.26–27 | `transits.py` |
| Transits by Aṣṭakavarga and kakṣyā | See [§10.3](#103-aṣṭakavarga) | | |
| Pācakādi relationships | Pācaka, Bodhaka, Kāraka, Vedhaka houses from each graha | **convention**: no verse checked | `key_info.py` `PACHAKADI_HOUSES` |
| 22nd drekkāṇa, 64th navāṃśa | See [§3](#3-divisional-charts-vargas) | PM 8.61, 9.4 | `key_info.py` `malicious_divisions` |
| Transit calendar, longitude correlation, Dasa-Transit correlation | Each transit body's sign and house from natal points; exact aspects within an orb; Jupiter, Saturn and the nodes through the houses from a dasa lord | Gochara PD 26.1–8. The orbs and the correlation views are **convention** | `workflows.py`, `server/transits.py`, `server/windows.py` |
| Searches (a body at a longitude, two bodies at an angle, stations, sign windows, end times) | Stepping and root finding, tolerances to the second | **astronomy**: numerical root finding (regula falsi and bisection, interpolated from one end of the bracket) | `time_search.py`, `mundane.py` `solve_longitude_crossing` |

---

## 13. Tājika: annual charts and sahams

Tājika comes from *Tājika Nīlakaṇṭhī* (TN), cited here through B. V. Raman's English account (*Varshaphal*, 1941;
VAR in the code) and PVR chs. 27–30.

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| The annual chart | The Sun back at its natal sidereal longitude (Settings › Tajaka: the true sidereal or the tropical year, or a mean year) | TN; PVR ch. 27 | `workflows.py`, `server/modes.py` |
| Monthly and finer charts | Each a twelfth of the one above | **modern**: PVR ch. 27 | `tajika.py` `tajaka_period`, `TAJAKA_LEVELS` |
| Munthā | The natal lagna moved on a sign a year (Settings › Muntha: from which point) | TN; VAR art. 45; PVR ch. 27 | `tajika.py` `compute_muntha`, `muntha_position` |
| Tājika aspects and orbs (dīptāṃśas) | Friendly and inimical aspects; each graha's orb | TN; VAR ch. III arts. 12–13 | `tajika.py` `TAJIKA_ASPECTS`, `DEEPTAMSA` |
| Tājika friendship | | TN; VAR ch. III art. 12 | `tajika.py` `TAJAKA_FRIENDS` |
| The 16 Tājika yogas (Ikkavāla, Itthasāla, Īśarāpha …) | | TN; VAR ch. VII arts. 57–63 | `tajika.py` `detect_16_tajika_yogas`, `check_ithasala_ishrafa_yoga` |
| Haddā (terms) | The five lords' terms in each sign | TN; VAR ch. III arts. 36–37 | `tajika.py` `HADDA_ENDS`, `HADDA_LORDS` |
| Harṣa, Pañcavargīya, Dvādaśavargīya balas | | TN; VAR ch. III arts. 29–40 | `tajika.py` `tajaka_balas` |
| The year lord (varṣeśa) | The strongest by pañcavargīya bala of five candidates: the lord of the Sun's sign (by day) or the Moon's (by night), the birth lagna's lord, the year lagna's lord, Munthā's lord, the Tri-rāśi lord | TN; VAR ch. IV arts. 42–47 (the five, art. 43) | `tajika.py` `evaluate_varsheshwara_candidates` |
| Sahams | A − B + C by day, B − A + C at night (some keep the day order); +30° when the lagna is not on the arc from B forward to A | TN (VAR ch. VII art. 64 on); the 36 formulas PVR 28.8 (and the app's help, "Sahamas") | `sahams_library.py` `saham_longitude`, `tajika.py` `compute_sahams` |
| Mudda and Pātyāyinī daśās | See [§9](#9-daśās) | TN; PVR ch. 30 | `dasa_systems/rasi.py` `patyayini_dasa` |

---

## 14. Praveśa charts, progressions and praśna

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Tithi Praveśa (annual, monthly, daily) | The moment Moon − Sun is back at its natal value, with the Sun in the natal solar month (or soli-lunar month, Settings › Tithi Pravesha) | **modern**: P. V. R. Narasimha Rao's teaching (the app's help, "Tithi Pravesha"); the tithi SS 2.66 | `tithi_pravesha.py` `annual_tithi_pravesha`, `next_pravesha` |
| Yoga and Nakshatra Praveśa | The same with Sun + Moon (SS 2.65) or the Moon's star | **modern**: as named | `tithi_pravesha.py` `solve_yoga_pravesha_chart`, `solve_nakshatra_pravesha_chart` |
| Planetary and angular returns | A body, or the angle between two, back at its natal value | **astronomy** | `miscellany.py` `compute_planetary_return`, `compute_angular_separation_return`; `workflows.py` `angular_return` |
| Progressions ("taught by Manu") | A day for a year, a degree for a year, and the varga progressions | Manusmṛti 1.67 (a human year a day and night of the gods), as the app's help gives it; **modern**: PVR's teaching | `miscellany.py` `compute_secondary_progression`, `compute_symbolic_manu_progression`, `progression_sun_arc` |
| Sudarśana cakra and Kālacakra progressions | A sign a year from lagna, Moon and Sun; the Kālacakra's order | BPHS 74; PVR ch. 31; BPHS 46.52–95 | `miscellany.py` `sudarsana_progression_arc`, `compute_kalachakra_progression` |
| "Progressed (Bhrigu)" chart | | **convention**: no text found | `miscellany.py` `compute_bhrigu_pada_progression` |
| The "Laghu Parasari" tab (sums of longitudes) | Sums of 1 to 5 bodies' longitudes in a division, and when they repeat | **convention**: a research aid "like simple progression techniques" (the tab's own words) | `longitude_sums.py` |
| Niṣeka (conception) chart | Days before birth from the arc Saturn–Māndi, the 1st to 9th cusp, and the Moon's degrees when the lagna lord is below the horizon | BPHS 4.25–30. **convention**: the constant 28.5 and reading "signs, degrees" as months of 30 days and days | `workflows.py` `nisheka_moment`, `nisheka_days` |
| Life-cycle charts (Settings › Life cycle) | The chart 144 (or n) years on | **convention** | `workflows.py` `lifecycle_moment` |
| Praśna lagna from a number | 1–108 the middle of the n-th navāṃśa; 1–249 the start of the n-th KP sub; 1–1800 the middle of the n-th nāḍyaṃśa | **convention** of each school; the divisions BPHS 6.12, KSK, DK | `workflows.py` `prasna_lagna` |
| Praśna sphuṭas | Trisphuṭa = lagna + Moon + Gulika; Catuḥsphuṭa = + Sun; Pañcasphuṭa = + Rāhu; Prāṇa = 5 × lagna + Gulika; Deha = 8 × Moon + Gulika; Mṛtyu = 7 × Gulika + Sun | PM 5.17–19 | `miscellany.py` `compute_prashna_sphutas` |
| Kuṇḍa | See [§5](#5-special-lagnas-and-shadow-points) | PM 5.8 | |
| Tāmbūla praśna | The betel leaves' count gives a lord | PM ch. 16 (betel leaves and the Tāmbūla lagna); the code's count rule not checked there | `miscellany.py` `compute_tamboola_prashna` |
| Kārya siddhi | The lords of the lagna and the matter, by house and aspect | **convention**: no verse checked | `miscellany.py` `evaluate_karya_siddhi` |
| Jamakkol praśna (Udayam, Ārūḍam, Kavippu) | Udayam round the zodiac once by day and once by night from the Sun; Ārūḍam a sign every 5 minutes from Aries each hour; Kavippu from the Sun's vīthi | **convention**: the Tamil Jamakkol tradition; no text checked | `jamakkol.py`, `server/jamakkol.py` |

---

## 15. Krishnamurti Paddhati

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Sign, star and sub lords | Each nakshatra divided among the nine lords in proportion to their Vimśottarī years, from the star's own lord | **modern**: KSK vol. I | `kp_astrology.py` `get_kp_sub_lords` |
| Sub-sub and finer levels (to 5) | The same division repeated | **convention** past the sub-sub | `kp_astrology.py` `get_kp_sub_levels` |
| Cusps | Placidus | **modern**: KSK vol. I; **astronomy**: SE §6.2 | `kp_astrology.py`, `ephemeris/houses.py` |
| Significators (four levels), ruling planets | | **modern**: KSK's Readers (not checked page by page) | `kp_astrology.py` |
| The 249 horary numbers | The subs, split where they cross a sign | **modern**: KSK's Readers | `kp_astrology.py` `KP_249_TABLE`, `resolve_kp_horary_number` |
| KP ayanamsa | See [§1.1](#11-ayanamsas) | KSK vol. I | |

---

## 16. Compatibility (matching)

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| The eight kūṭas and their points | Varṇa 1, Vaśya 2, Tārā 3, Yoni 4, Graha maitrī 5, Gaṇa 6, Bhakūṭa 7, Nāḍī 8; 36 in all | MC, Vivāha prakaraṇa (verses not checked) | `compatibility/kutas.py`, `compatibility/matching.py` |
| Each kūṭa's rule | Rāśi (bhakūṭa) | PM 21.4–11 | `compatibility/kutas.py` |
| | Vaśya | PM 21.8, 21.17–18 | same |
| | The rāśi lords (graha maitrī) | PM 21.19–20 | same |
| | Dina (tārā) | PM 21.21–24 | same |
| | Gaṇa | PM 21.27 | same |
| | Varṇa | PM 21.28–29 | same |
| | Yoni | PM 21.30–32, 21.38–42 | same |
| | Nāḍī | PM 21.50 | same |
| Mahendra, Strī-dīrgha, Rajju, Vedha | | PM 21.25, 21.26, 21.43–44, 21.45–46 | `compatibility/ancillary.py` |
| Exceptions (same rāśi, same star; exempt stars) | | **reading**: PM 21.15–16 and the common exemptions; no single verse checked | `compatibility/kutas.py` |
| Kuja doṣa | Mars in the 1st, 2nd, 4th, 7th, 8th, 12th bhava from lagna, Moon and Venus, counted in each one's bhava chakra (the cusps of the Bhava system options; by sign when no cusps are given); cancelled by Mars in own sign, moolatrikona (by degree) or exalted, Jupiter with Mars or aspecting it (5th, 7th, 9th: BPHS 26) within the smaller of their Tajika deeptamsas (Ma 8°, Ju 9°: 8°) of the conjunction or the aspect's exact angle, the aspect's sphuta drishti shown as a percentage, and the sign exceptions (Aries 1st, Scorpio 4th, Capricorn 7th, Leo/Aquarius 8th, Sagittarius 12th) | **convention**: the common rule, the 2nd bhava as in the south; no verse checked. Jupiter's aspects: **BPHS 26**; the orbs **Tajika Neelakanthi** (deeptamsas), applied here by **convention** as in the Longevity rules | `compatibility/kuja.py`, `server/houses.py` `mars_bhavas` |
| Matching comparison checks | lagnas hard 6/8, 2/12; Moon signs hard 6/8, 2/12, 5/9 (Bhakoota); each graha alike in the same bhava; lagna lords unless natural enemies; spouse karakas outside the dusthanas; lords alike in the same kind of bhava (kendra/trikona, dusthana, neither); Bhava Bala against 7 rupas; shadbala against the required rupas | **convention**: this app's checks; the strength yardsticks as in "Which is stronger" above (BPHS 27.32–36 for the required rupas) | `compatibility/compare.py` |
| Matching comparison: the twelve bhavas, and what each says of the marriage | 1st self, 2nd family, 3rd courage, 4th home, 5th children, 6th disputes, 7th spouse, 8th longevity, 9th fortune, 10th career, 11th gains, 12th bed comforts; 2, 4, 5, 7, 8, 12 the marriage bhavas | BPHS 11 (each bhava's significations); the one-word summaries **convention** | `compatibility/compare.py` `_BHAVAS` |
| Matching comparison's colours (good, middling, bad) | A graha or lord in a kendra or trikona good, a dusthana bad; exalted, moolatrikona, own sign or vargottama good, debilitated bad; age young or adolescent good, infant middling, old or dead bad; awake good, dreaming middling, asleep bad; the moods of an exalted, own, great friend's or friend's sign good, the others bad, both middling; Shadbala against its required rupas, Bhava Bala against 7; Vimsopaka strong from 15, weak under 10; a bhava holding only benefics good, only malefics bad; Mars in the 1st, 2nd, 4th, 7th, 8th or 12th bad, a cancelled dosha good; a lord (Lord of, a bhava's Lord) by its functional nature for the lagna, benefic or yogakaraka good, malefic bad, the 8th lord bad (middling beside a trikona) unless it is the lagna lord or the Sun or Moon; a graha in its own or a natural friend's nakshatra good, an enemy's bad, Rahu and Ketu by none | BPHS 45.3–10 (avasthas), 11.14–16 (age as good or bad), 27.32–36 (required rupas), 7.17–27 (Vimsopaka), 34 and LP (functional natures, the 8th lord), 3.55 (natural relationships); **convention**: reading a graha by its nakshatra lord's relationship, the Vimsopaka bands, and Vaiseshikamsa good from Gopura (4 of 10) or Kalpavriksha (7 of 16), bad when none | `web/src/MatchingCompare.tsx` |
| Matching comparison's Grahas and Bhavas tables | Each partner's grahas aspecting the other's grahas (Grahas) and bhava cusps (Bhavas), by the Aspects tab's curves and full value; The five avasthas (Baaladi, Jaagradadi, Deeptadi by Parashara, Sayanadi, Lajjitadi; Lajjitadi proud or delighted good, ashamed, starved, thirsty or agitated bad); each bhava's occupants and the grahas whose full graha drishti falls on its sign (benefics only good, malefics only bad); its sign's SAV bindus with the lagna's own row (8 rows), good from 32, weak under 29 (28 and 25 without it, the lagna adding about 4 a sign); its karaka and the bhava that sits in | BPHS 45 (avasthas; 45.11–18 Lajjitadi), 26 (graha drishti), 66 (SAV), 32.31–34 (bhava karakas); **convention**: the SAV bands and the tones | `web/src/MatchingCompare.tsx` |
| Matching factors: the areas and their rows | Doshas (Kuja: Mars's bhava from Venus, the Moon and the Lagna in one row, then whether it is cancelled and why; Papa samya, its points and where they are; the kuta doshas are the Kutas tab's), Mind (the Moon, each Moon from the other's Lagna), Marriage (Lagna to Lagna, the Lagna lords, the 7th and its lord, Venus, the girl's Jupiter, the D-9 7th lord and Venus in D-9, Darakaraka, Upapada), Family (the 5th, its lord, Jupiter, the D-7 5th lord, Beeja and Kshetra sphuta, the 2nd, 4th and 11th), Health (the Lagna, its lord, the 6th, the 8th), Timing (Vimsottari now, the next mahadasa) | BPHS 11 (each bhava's significations), 32 (the karakas: Venus of the spouse, Jupiter of children and the husband; the Darakaraka), 6 (D-7 for children, D-9 for the spouse), chapters only, verses not checked; the choice of rows **convention** | `compatibility/factors.py` |
| Matching factors: a graha or bhava read good or bad | A graha: its bhava (kendra or trikona good, dusthana bad), dignity (exalted, moolatrikona, own good; debilitated bad) and Shadbala against its need (good from 100%, middling from 85%, weak below); a bhava: its Bhava Bala against 7 rupas on the same bands, benefics only in it good, malefics only bad, and its lord's bhava; averaged, good from 1.5 of 2, middling from 0.75 | BPHS 27.32–36 (required rupas); the 85% band and the averaging **convention** | `compatibility/factors.py` `Side.graha`, `Side.bhava`, `mix` |
| Matching factors: Together | Both good, both weak, one good and one weak "carries it" (middling); an area's verdict the average of its rows, the doshas' the worst of theirs | **convention** | `compatibility/factors.py` `carry`, `match_factors` |
| Lagna to Lagna, Moon from the other's Lagna | The Lagnas 6/8 or 2/12 apart hard; each one's Moon in a kendra or trikona of the other's chart good, a dusthana bad | **convention** | `compatibility/factors.py` |
| Upapada and its 2nd | Malefics in or aspecting (graha drishti) the 2nd from Upapada break the marriage, benefics keep it | BPHS 30 (verses not checked); Upapada itself BPHS 30.1–6 | `compatibility/factors.py` `_marriage` |
| Papa samya | A point for each of Su Ma Sa Ra Ke in the 1st, 2nd, 4th, 7th, 8th or 12th from the Lagna, the Moon and Venus, unweighted; the boy's total at least the girl's good, up to 2 less middling | **modern**: South Indian practice; no classical verse found, and the schools weigh the three points differently | `compatibility/factors.py` `Side.papa` |
| Beeja and Kshetra sphuta | Beeja (man) Su + Ve + Ju, Kshetra (woman) Mo + Ma + Ju; the man's odd sign and odd navamsa, the woman's even and even, children; sign and navamsa of different kinds, with effort; both of the other kind, difficulty | Phaladeepika 12.14 (two translations checked; the last case is stated in one) | `miscellany.py` `fertility_reading` |
| Timing in matching | The running Vimsottari periods by their lords' functional nature for each Lagna; both mahadasas changing within a year of each other avoided | Laghu Parasari for the natures; the dasa sandhi rule **convention** | `compatibility/factors.py` `_timing` |
| Marriage in the dasas | A graha tied to marriage: the 7th lord, a graha in the 7th, Venus, the Darakaraka (the strong ties), the girl's Jupiter, the navamsa's 7th lord, Upapada's lord; an antardasa likely when both lords are tied, one strongly, possible when either is strongly tied | **convention**: the common rules for timing marriage by Vimsottari; no verse checked | `compatibility/factors.py` `marriage_lords`, `marriage_dasas` |
| Horoscope Matching Score | The kūṭas' points tabulated for every pair of the 36 Moon parts; the levels (Excellent from 31 …) | MC for the points; the levels **convention** | `compatibility/pada_points.py` |

---

## 17. Chakras, mundane charts and other views

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Sarvatobhadra cakra | The 9 × 9 grid of 28 stars, vowels, consonants, signs and tithis; vedhas from transits | PD 26.48 (its auspicious and inauspicious vedhas); **modern**: PVR 26.8; the 28 stars PVR ch. 25. The grid's letters as in the Svarodaya tradition, not checked | `chakras.py`, `server/chakras.py` |
| Kota, Kālānala (Sūrya, Candra), Śūla, Tripatākī, Kālacakra (directional) cakras | | The Svarodaya tradition (Narapati's) and the Varṣaphala texts; no verse checked | `chakras.py`, `server/chakras.py` |
| Kūrma cakra | Stars in threes from Kṛttikā: the middle, then east, south-east … north-east | BS 14.1 (the Chakras page). The library table `KURMA_CHAKRA_REGIONS` is grouped differently and the page does not use it | `server/chakras.py`, `chakras.py` |
| Sudarśana cakra | Lagna, Moon and Sun charts as three rings | BPHS 74 | `chakras.py` `compute_sudarshana_chakra` |
| Solar new year, solar months | The Sun's entry into Aries, into each sign | SS 14.3 | `mundane.py` `compute_solar_new_year`, `compute_solar_month_ingress` |
| Lunar new year | Caitra śukla pratipat | SS 14.12–14 | `mundane.py` `compute_lunar_new_year` |
| The year's king and minister | The lords of the weekdays of Caitra śukla pratipat and of Meṣa saṅkrānti | BS 19 (the year of each graha); the weekday rule as the almanacs reckon it, no verse checked | `mundane.py` `compute_year_lords` |
| "Meteorological year" chart | The Sun's entry into Ārdrā (66°40′) | **convention**: almanac practice (Ārdrā praveśa); no verse checked | `server/modes.py` |
| Stations, conjunctions, eclipses | | **astronomy**; eclipses also SS ch. 4–5 | `mundane.py`, `ephemeris/points.py` |
| Astrocartography | Where each sidereal longitude is on the angles | **astronomy** (an original view) | `astrocartography.py`, `server/astrocarto.py` |
| Timeline (saṃvatsara, gaṇḍānta, combustion, conjunctions) | | See [§4](#4-sensitive-degrees-mṛtyu-and-puṣkara-bhāgas), [§8](#8-pañcāṅga-muhūrta-and-calendars) and [§2](#2-signs-nakshatras-and-dignities) | `server/timeline.py` |
| Lore panels ("what the books say") | Texts, not calculations: BPHS 24 (lords in the bhavas), PD 26 (transits from the Moon), Dr. Pai's *Cosmic Insights* (nakshatras) | As each data file names it (`data/lore/README.md`) | `server/lore.py` |
| Remedies | BPHS's remedies; the Śrī Vaiṣṇava ones from the Bhagavad Gītā and Śrīmad Bhāgavatam, each entry with its verse | As each entry names it (`data/remedies_bphs.json`, `data/remedies_vaishnava.json`) | `server/remedies.py` |

---

## 18. Settings index

Every option in Settings (`server/settings.py`, 163 options) and where its source is given.

| Settings group | Options | Section |
| :--- | :--- | :--- |
| Model and ayanamsa | Graha model; ephemeris; Swiss Ephemeris data; ayanamsa and its correction; custom star; Swiss Ephemeris 2.02 | [§1.1](#11-ayanamsas), [§1.2](#12-the-sūrya-siddhānta-model-settings--graha-model). "Use sidereal zodiac for nakshatras … when using tropical zodiac": **convention** |
| Grahas | Topocentric, true or apparent positions, refraction, aberration, deflection, nutation; mean or true nodes | [§1](#1-astronomy-and-time) |
| | Nodal exaltation | [§2](#2-signs-nakshatras-and-dignities) |
| | Chara karaka scheme | [§7](#7-jaimini-kārakas-ārūḍhas-and-the-stronger-sign) |
| Outer grahas | Own and exaltation signs of Uranus, Neptune, Pluto | **convention**: no classical text knows the outer planets |
| Sunrise and special lagnas | Sunrise definition; continuous special lagnas | [§1.3](#13-sunrise-the-day-and-its-lords), [§5](#5-special-lagnas-and-shadow-points) |
| Upagrahas | Dhūma–Vyatīpāta; when Gulika, Māndi, Kāla rise; which portion; day and night | [§5](#5-special-lagnas-and-shadow-points) |
| Hora, Kaala and weekday | When the weekday and hora start; Mahākāla; Kāla day and night | [§1.3](#13-sunrise-the-day-and-its-lords) |
| Divisional charts | Every "Choose …" scheme, D-150 names, divisional longitudes | [§3](#3-divisional-charts-vargas) |
| Bhavas | Bhāva system; for a graha reference; lagna at the cusp or the middle | [§1.4](#14-houses-bhavas) |
| Ashtakavarga | Meaning of the references; SAV by bhavas; the six cells | [§10.3](#103-aṣṭakavarga) |
| Balas | Vimśopaka relationships; avasthā relationships; swarudha and its annulments; moolatrikona degrees; combustion | [§10](#10-strengths-avasthās-aṣṭakavarga-and-longevity), [§2](#2-signs-nakshatras-and-dignities) |
| Dasa years | Year definition; Tājaka and Tithi Praveśa years; daśā śeṣam in mundane charts | [§9.1](#91-the-dasa-year) |
| Nakshatra dasas, Rasi dasas, Other dasas | Seeds, antardaśā order, Tribhāgī, Kālacakra variants, each daśā's options | [§9](#9-daśās) |
| Tajaka | Year by; solar year; Munthā | [§13](#13-tājika-annual-charts-and-sahams) |
| Tithi Pravesha | Solar or soli-lunar months | [§14](#14-praveśa-charts-progressions-and-praśna) |
| Calendars | Lunar month kind and naming; the signs that begin the lunar and solar years | [§8](#8-pañcāṅga-muhūrta-and-calendars) |
| Pushkara and Mrityu Bhaga | The Pushkara table; the Mrityu table; what "a Mṛtyu bhāga of 19°" means | [§4](#4-sensitive-degrees-mṛtyu-and-puṣkara-bhāgas) |
| Arudha padas | Exceptions; nodes as lords; longitude-based ārūḍhas | [§7](#7-jaimini-kārakas-ārūḍhas-and-the-stronger-sign) |
| Bhava chart and aspect table | Reference for the bhāva chart; nodes' bhavas reversed; aspect units; special aspects | [§3](#3-divisional-charts-vargas), [§1.4](#14-houses-bhavas), [§6](#6-aspects-and-argalā) |
| Life cycle | Length and year | [§14](#14-praveśa-charts-progressions-and-praśna) |
| Longevity | Orbs; Saturn and Jupiter in the three pairs; the outer classes' years; the Summary's average | [§10.4](#104-longevity-āyurdāya-and-mārakas). The orbs, the outer years and the average are **convention** |
| User defined special point, Graha special lagna | The point or lagna the user defines | [§5](#5-special-lagnas-and-shadow-points): **convention** |

## 19. The Traditions tab (XALEN Ephemeris)

Astrology outside Jyotish, from the XALEN Ephemeris crates (Apache-2.0, `native/traditions`, `server/traditions.py`). The
positions are the app's own on NASA JPL's DE442 (§1), tropical, under the user's position settings; XALEN's crates do the
techniques. Where a crate names its source it is given; the rest is **convention**: XALEN's implementation as it stands.

| Calculation | Rule | Source | Code |
| :--- | :--- | :--- | :--- |
| Western houses | Fifteen systems (Placidus, Koch, Regiomontanus, Campanus, Porphyry, Equal, Whole sign …) on mean sidereal time; within 0.01° of the Swiss Ephemeris' | **astronomy/convention**: XALEN `xalen-houses` | `native/traditions` `houses` |
| Chiron, Black Moon Lilith | Chiron from XALEN's orbital elements; the mean and osculating lunar apogee | **astronomy**: XALEN `xalen-ephem` (`chiron`, `lilith`) | `extra_bodies` |
| Aspects and patterns | Eleven aspects with orbs; grand trine, T-square, grand cross, yod, kite, stellium, mystic rectangle | **convention**: XALEN `xalen-western` `aspects`, `patterns` | `western` |
| Essential dignities | Domicile, exaltation, detriment, fall, triplicity, the Egyptian terms, the Chaldean faces; a score | Ptolemy, *Tetrabiblos* I.17–21 (the terms per Robbins' translation, as XALEN cites) | `western` |
| Arabic lots | 97 lots, day and night formulas; Fortune and Spirit | **convention**: XALEN `xalen-western` `lots` | `western` |
| Time lords | Annual profection, zodiacal releasing from Spirit and Fortune, firdaria, decennials, sect | Vettius Valens, *Anthology* IV (releasing, profections); **convention**: XALEN `hellenistic` | `western` |
| Midpoints and the 90° dial | Midpoints within 1.5°, planetary pictures | R. Ebertin, *The Combination of Stellar Influences* (as XALEN cites, `cosmobiology`) | `western` |
| Uranian points | The eight trans-Neptunian points of the Hamburg School | A. Witte (Hamburg School), as XALEN cites (`uranian`) | `western` |
| Declinations, antiscia | Parallels and contra-parallels within 1°; reflections over the solstitial axis | **convention**: XALEN `declination`, `antiscia` | `western` |
| Harmonics | The 5th, 7th and 9th harmonic charts | **modern**: J. Addey, *Harmonics in Astrology* (1976) | `western` |
| Progressions, solar arc, returns | A day for a year; every point by the progressed Sun's arc; the solar and lunar returns by the app's own root finder (tropical, DE442) | **convention**; returns: `time_search.longitude_event` | `server/traditions.py` `western` |
| Fixed stars | Bright Star Catalogue stars to magnitude 2.5 within 1° of a body or angle | **astronomy**: XALEN `stars` (Yale Bright Star Catalogue, IAU-CSN names) | `western` |
| Chinese lunar date | Months new moon to new moon, the eleventh holding the winter solstice, a 13-month year's first month without a principal term its leap month, all in China time (UTC+8) | H. Aslaksen, "The Mathematics of the Chinese Calendar" (2010) §§3–4 | `core_logic/chinese_calendar.py` |
| BaZi | The year from Li Chun (the Sun at 315°), the month by the solar terms, its stem by the Five Tigers rule; the day by the sexagenary count from local midnight; the hour's stem from the day's | **convention**: the Chinese calendar; the solar terms by the app's Sun (DE442) | `chinese` |
| Zi Wei Dou Shu | Ming and Shen palaces, the five-element bureau, the fourteen major and the minor stars, Da Xian decades, on the lunar date | **convention**: XALEN `ziwei` | `chinese` |
| Flying Stars, Ba Zhai, Qi Men Dun Jia | The period and annual stars flown through the Lo Shu; the Kua number's eight mansions; the San Yuan Qi Men board (XALEN marks it experimental) | **convention**: XALEN `fengshui`, `qimen` | `chinese` |
| Korean Saju, Nine Star Ki, Mahabote, the Tibetan year | The four pillars in Korean with Daeun; the year and month stars of the Lo Shu; the Burmese day sign and seven-house square; the Rabjung cycle's animal and element | **convention**: XALEN `xalen-world` | `world` |
| Maya and Aztec calendars | The Long Count, Tzolk'in and Haab'; the tonalpohualli's day sign and number | **convention**: XALEN `mayan`, `aztec` | `world` |
| Egyptian decans, Celtic tree | 36 decans with Chaldean-order rulers; the thirteen tree months | **convention**: XALEN `egyptian`; **modern**: R. Graves, *The White Goddess* (1948) for the tree months | `world` |
| Jarbakhtar | The planets' minor years (129 in all) from the almuten, here the planet of the highest essential dignity score | Abū Maʿshar, as XALEN cites (`persian`) | `world` |
| I Ching | The hexagram of the birth's date and hour, its changing line; the relating, nuclear and opposite hexagrams | Shao Yong, *Mei Hua Yi Shu* (as XALEN cites); the texts in J. Legge, *The Yî King*, SBE XVI (1882) | `iching` |
| Numerology | Life path, birthday, expression, soul urge, personality, maturity, personal year; Pythagorean or Chaldean letters | **modern/convention**: XALEN `xalen-numerology` | `numerology` |
| Lal Kitab | The grahas by house from the lagna (Aries the first house); each one's effect, dormancy, the debts (rin), the year's chart (Varshphal) | **convention**: XALEN `xalen-lalkitab` (its remedy texts are not included) | `lalkitab` |
