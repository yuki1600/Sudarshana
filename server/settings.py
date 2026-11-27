"""Preferences > Related to Calculations as one table: each option's key, group, label, choices and default (data/default_settings.ini
unless noted). The API validates against it and the Settings screen is generated from it, so a screen control always
has a request field behind it. Only options an engine reads are listed. One dasa's own values go in ``per_dasa``, by dasa key (server/dasas.py)."""
import dataclasses
from datetime import datetime, timedelta
from typing import Literal

from pydantic import Field, create_model

from core_logic import ephemeris as E, dasa_systems as J, varga_charts as V, sahams_library as SL, shadbala as SB, sign_strength as SS, natal_chart as N

CHART = "Chart"     # options that change the chart itself; the rest change one calculation
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
DIVISION_NAMES = [(i, "Rasi" if n == 1 else "D-%d" % n) for i, n in enumerate(V.DIVISIONS)]
SEEDS = ["Janma tara (Moon)", "Utpanna tara (5th star)", "Kshema tara (4th star)", "Aadhaana tara (8th star)", "Lagna sphuta", "Maandi sphuta", "Gulika sphuta",
         "Trisphuta (sookshma)", "Surya sphuta (Sun)", "Kuja sphuta (Mars)", "Budha sphuta (Mercury)", "Guru sphuta (Jupiter)", "Sukra sphuta (Venus)", "Sani sphuta (Saturn)",
         "Rahu sphuta (Rahu)", "Ketu sphuta (Ketu)", "Bhrigu Bindu", "Indu Lagna", "Pranapada", "User's special point", "User's special lagna"]
AD_METHODS = ["Start from the dasa lord, forward", "Start from the dasa lord, backward", "Start from the next dasa lord, forward", "Start from the next dasa lord, backward",
              "Start from the previous dasa lord, forward", "Start from the previous dasa lord, backward"]
YEARS = {0: "Mean tropical solar year (365.24219 days)", 7: "True tropical solar year (Sun traversing 360 deg tropically)", 6: "Mean sidereal solar year (365.256364 days)",
         3: "True sidereal solar year (Sun traversing 360 deg sidereally)", 1: "Savana year (360 days)", 4: "Year with 360 tithis", 2: "User defined year (n days)"}
RISE = [(0, "the beginning"), (1, "the middle"), (2, "the end")]
_no = (False, True)
OPTIONS = []


def _add(group, key, label, default, choices=None, help=None, **limits):
    OPTIONS.append({"group": group, "key": key, "label": label, "default": default, "help": help, "limits": limits,
                    "choices": [{"value": v, "label": t} for v, t in choices] if choices else None})


def _ch(group, key, label, default, choices, help=None):
    _add(group, key, label, default, list(enumerate(choices)) if choices and not isinstance(choices[0], tuple) else choices, help)


g = "Model and ayanamsa"
_add(g, "siddhanta", "Graha model", 0, [(0, "Drik Siddhanta (as observed by modern planetariums)"), (1, "Sri Surya Siddhanta (generalized Makaranda version)")])
_add(g, "ephemeris", "Ephemeris (Drik Siddhanta)", "swiss", [("swiss", "Swiss Ephemeris"), ("xalen", "XALEN Ephemeris")],
     help="The engine that turns NASA JPL's DE442 (its newest planetary ephemeris, 1550 to 2650; outside it the Swiss Ephemeris' own files) into the grahas' "
          "positions. Both read it, and agree to thousandths of an arc second (the mean node, a formula in each, to a fraction of one). "
          "Houses, ayanamsas, sunrise and eclipses come from the Swiss Ephemeris either way.")
_add(g, "ayanamsa", "Ayanamsa", "PUSHYA_PAKSHA", [(a["key"], a["label"]) for a in E.AYANAMSAS])
_add(g, "ayanamsa_offset_deg", "Add this correction to the ayanamsa (degrees, may be negative)", 0.0, ge=-30, le=30)
_add(g, "custom_star", "Custom ayanamsa: star code", ",alVir", help="Used only with the fixed star based custom ayanamsa. Swiss Ephemeris star code, e.g. ,alVir", max_length=40, pattern=r"^[,\w ]+$")
_add(g, "custom_star_longitude", "Custom ayanamsa: star's sidereal longitude (degrees)", 180.0, ge=0, lt=360)
_add(g, "custom_star_fixed_plane", "Custom ayanamsa: use a fixed solar rotation plane", False)
_add(g, "sidereal_nakshatras_in_tropical", "Use sidereal zodiac for nakshatras and nakshatra dasas when using tropical zodiac (Spica fixed in the middle of Chitra)", False)
_add(g, "swisseph_202", "Use the reference Swiss Ephemeris 2.02 (its Delta-T, ayanamsas and star catalogue)", True,
     help="Off: the current Swiss Ephemeris'. Positions change by fractions of an arc second; dates of old charts can move more.")

g = "Grahas"
_ch(g, "topocentric", "Positions as seen from", False, [(False, "Geocentric positions"), (True, "Topocentric positions")])
_ch(g, "true_positions", "Positions", True, [(True, "True positions"), (False, "Apparent positions")])
_ch(g, "apparent_refraction", "Refraction (apparent positions only)", False, [(False, "Don't use refraction"), (True, "Use refraction")])
_ch(g, "no_aberration", "Annual aberration of light", False, [(False, "Use annual aberration of light"), (True, "Don't use annual aberration of light")])
_ch(g, "no_gravitational_deflection", "Gravitational deflection", False, [(False, "Use gravitational deflection"), (True, "Don't use gravitational deflection")])
_ch(g, "no_nutation", "Nutation", False, [(False, "Use nutation"), (True, "Don't use nutation")])
_add(g, "nodes", "Rahu and Ketu", "true", [("mean", "Mean nodes"), ("true", "True nodes")])     # the owner's choice; the ini's is mean
_ch(g, "nodal_parasara", "Nodal exaltation", True, [(True, "Rahu exalted in Ta, Ketu in Sc (some versions of BPHS)"), (False, "Rahu exalted in Ge/Ta, Ketu in Sg/Le (Pt Sanjay Rath)")])
_ch(g, "chara_karakas", "Chara karaka scheme", 0, ["Eight chara karakas", "Seven chara karakas (no Pitri karaka, Sri K.N. Rao)", "Seven chara karakas (PK merged with MK)", "Mixed 7/8 chara karakas of Parasara"])

# Not in the classics: modern proposals, the most cited is the default (2026-11-19); every sign can be chosen (2026-11-20). Debilitated in the opposite sign; own signs Aq, Pi, Sc.
g = "Outer grahas"
OUTER_HELP = "Not in the classics: modern proposals, the most cited is the default; own signs Uranus Aquarius, Neptune Pisces, Pluto Scorpio by default."
OUTER_EXALTATION = {"Uranus": [7], "Neptune": [4, 3, 10], "Pluto": [0, 4, 5, 11]}
OUTER_OWN = {"Uranus": 10, "Neptune": 11, "Pluto": 7}     # Aquarius, Pisces, Scorpio
for _p, _signs in OUTER_EXALTATION.items():
    _add(g, _p.lower() + "_own", _p + "'s own sign", OUTER_OWN[_p], list(enumerate(SIGNS)) + [(-1, "None")], help=OUTER_HELP)
    _add(g, _p.lower() + "_exalted", _p + " exalted in", _signs[0], [(e, "%s (debilitated in %s)" % (SIGNS[e], SIGNS[(e + 6) % 12])) for e in range(12)] + [(-1, "None")], help=OUTER_HELP)

g = "Sunrise and special lagnas"
_ch(g, "sunrise_definition", "Sunrise is when", 0, ["The center of Sun's disk is truly on the eastern horizon", "The tip of Sun's disk is truly on the eastern horizon",
                                                    "The tip of Sun's disk appears to be on the eastern horizon", "The center of Sun's disk appears to be on the eastern horizon"])
_add(g, "continuous_special_lagnas", "Use the alternative special lagna definition giving continuity", False)

g = "Upagrahas"
_ch(g, "vyatipata_method", "Dhuma-Vyatipata relation", 0, ["Vyatipata = 360 deg - Dhuma", "Vyatipata = Dhuma + 53 deg 20 min"])
_add(g, "gulika_rise", "Gulika rises at", 0, RISE)
_ch(g, "gulika_in_saturn_portion", "... of which portion", True, [(False, "The eighth portion"), (True, "Saturn's portion")])
_add(g, "mandi_rise", "Mandi rises at", 1, RISE)
_ch(g, "mandi_in_saturn_portion", "... of which portion", True, [(False, "The eighth portion"), (True, "Saturn's portion")])
_add(g, "kaala_rise", "Kala, Mrityu etc rise at (of their portions)", 1, RISE)
_ch(g, "upagraha_day_definition", "Day and night, for the upagrahas", 0, ["Start at sunrise and sunset", "Start at 6 am LMT and 6 pm LMT"])

g = "Hora, Kaala and weekday"
_ch(g, "weekday_definition", "New hora and weekday start", 0, ["At sunrise (hora is 1/24th of the sunrise-to-sunrise day)", "At 6 am LMT (hora is exactly 1 hour)"])
_ch(g, "mahakala_definition", "Mahakala hora and day", 1, [(1, "Start at 6 am LMT"), (2, "Start at 6 am LST")])
_ch(g, "kaala_day_night_separate", "Kaala", True, [(False, "Divide day and night together into 16 equal parts"), (True, "Divide day into 8 equal parts and night into 8 equal parts")])

g = "Divisional charts"
_names = {2: "Hora (D-2)", 3: "Drekkana (D-3)", 4: "Chaturthamsa (D-4)", 5: "Panchamsa (D-5)", 7: "Saptamsa (D-7)", 8: "Ashtamsa (D-8)", 9: "Navamsa (D-9)", 10: "Dasamsa (D-10)",
          11: "Rudramsa (D-11)", 12: "Dwadasamsa (D-12)", 16: "Shodasamsa (D-16)", 20: "Vimsamsa (D-20)", 24: "Siddhamsa (D-24)", 27: "Nakshatramsa (D-27)", 30: "Trimsamsa (D-30)",
          60: "Shashtyamsa (D-60)", 81: "Nava-navamsa (D-81)", 108: "Ashtottaramsa (D-108)", 150: "Nadyamsa (D-150)"}
for _n, _label in _names.items():
    _ch(g, "d%d" % _n, _label, getattr(V.DEFAULT, "d%d" % _n), list(V.SCHEMES[_n]))
_ch(g, "d150_names", "Nadyamsa names", 0, ["Names in Deva Keralam (Chandra Kala Nadi)", "Names given by C.G. Rajan"])
_add(g, "equal_d30_longitudes", "Map each 1 degree in rasi to 30 degrees in D-30 (when finding divisional longitudes)", True)
_add(g, "mirror_reversed_longitudes", "Reckon divisional longitudes from the end of the sign when using reverse reckoning of signs", True)

g = "Bhavas"
HOUSE_SYSTEMS = [(0, "Each rasi is a bhava"), (1, "Equal bhavas (cusp at the lagna's degree)"), (2, "Equal bhavas from the middle of the lagna's pada"), (3, "Sripati (Porphyry)"),
                 (4, "Placidus"), (5, "Koch"), (6, "Regiomontanus"), (7, "Campanus"), (8, "Axial rotation"), (9, "Polich/Page"), (10, "Alcabitus")]
_ch(g, "house_type", "Bhava system", 3, HOUSE_SYSTEMS)
_ch(g, "house_type_graha", "Bhava system when the reference is a graha (Sun .. Ketu)", 1, [(1, "Equal bhavas (cusp at the graha's degree)")] + [c for c in HOUSE_SYSTEMS if c[0] != 1])
_ch(g, "house_cusp_in_middle", "The ascendant is", True, [(True, "The middle of the first bhava"), (False, "The start of the first bhava")])

g = "Ashtakavarga"
_ch(g, "av_definition", "Meaning of the references", 1, [(1, "As usual"), (0, "Reversed, as far as references are concerned")])
_add(g, "av_bhava_driven_sav", "Consolidate bhavas from references when finding SAV (instead of signs)", False)
for _k, _label in enumerate(("Moon is benefic in the 9th from Moon", "Moon is malefic in the 9th from Mars", "Moon is benefic in the 2nd from Jupiter", "Moon is malefic in the 12th from Jupiter",
                             "Venus is benefic in the 4th from Mars", "Venus is malefic in the 5th from Mars")):
    _add(g, "av_parasara_%d" % _k, _label, True)

g = "Balas"
_ch(g, "vimsopaka_from_rasi", "Compound relationships in vimsopaka", False, [(False, "From the relevant varga chart"), (True, "From the rasi chart always")])
_ch(g, "avastha_compound", "Relationships in the avasthas", False, [(False, "Permanent"), (True, "Compound")])
_ch(g, "swarudha", "Vaiseshikamsa: what \"swarudha\" means", 0, [(0, "Ignore this special case"), (1, "Arudha lagna of the rasi chart"), (2, "Arudha lagna of each varga"), (3, "Graha arudha of the rasi chart"), (4, "Graha arudha of each varga"),
                                                                 (5, "AL lord of the rasi chart (kendra from him in vargas)"), (6, "AL of rasi, but take kendra lords (not grahas in kendra)"), (7, "AL of each varga, but take kendra lords")],
    help="Choices 2, 4 and 7 follow the rule as the option is worded.")
for _k, _label, _d in (("combustion", "If the graha is combust", True), ("dispositor_combustion", "If the dispositor is combust", False), ("defeat", "If the graha is defeated in a graha war", True),
                       ("dispositor_defeat", "If the dispositor is defeated in a graha war", False), ("neecha", "If the graha is debilitated in the division", True),
                       ("dispositor_neecha", "If the dispositor is debilitated in the division", False), ("dispositor_neecha_rasi", "If the dispositor is debilitated in rasi", False),
                       ("poor_vimsopaka", "If the graha is in satru/adhisatru sthana", True), ("dispositor_poor_vimsopaka", "If the dispositor is in satru/adhisatru sthana", False),
                       ("sayanadi", "If the graha is in a bad sayanadi avastha", True), ("dispositor_sayanadi", "If the dispositor is in a bad sayanadi avastha", False)):
    _add(g, "amsa_" + _k, "Annul the swarudha placement: " + _label.lower(), _d)

_ch(g, "moolatrikona_bphs", "Moolatrikona degrees in Shadbala (saptavargaja)", True, [(True, "BPHS: Mo 3°–30° Ta, Me 15°–20° Vi"), (False, "Narrow: Mo 4°–20° Ta, Me 16°–20° Vi")])
_ch(g, "combustion_classical", "Combustion", True, [(True, "Classical orbs: Mo 12°, Ma 17°, Me 14° (12° retrograde), Ju 11°, Ve 10° (8° retrograde), Sa 15° (Surya Siddhanta)"),
                                                   (False, "Fixed orb: Ma, Me, Ju, Ve, Sa within 6° of the Sun")])
_add(g, "combustion_by_motion", "Fixed-orb combustion only: retrograde Mercury and direct Venus are not combust (Sanjay Rath)", True)

g = "Dasa years"
_ch(g, "year_definition", "Definition of year in dasas", 3, [(k, YEARS[k]) for k in (0, 7, 6, 3, 1, 4, 2)])
_add(g, "year_length", "User defined year (days)", 365.24219, gt=1, le=1000)
_add(g, "special_year_tajaka", "In Tajaka charts, always use the true sidereal solar year", True)
_add(g, "special_year_tp", "In Tithi Pravesha charts, always use the year of 360 tithis", True)
_add(g, "dasa_sesham_mundane", "Use dasa sesham in compressed mundane dasas", True)

g = "Nakshatra dasas"
_ch(g, "dasa_seed", "Seed (start point)", 0, SEEDS, help="The user's special point and lagna count as 0 degrees here, set or not.")
_ch(g, "dasa_shift", "Start from this many stars on", 0, [(i, str(i)) for i in range(9)])
_ch(g, "dasa_ad_method", "Antardasas", 0, AD_METHODS)
_add(g, "dasa_reverse", "Reckon everything antizodiacally (Vimsottari only)", False)
_add(g, "dasa_tribhagi", "Tribhagi variation", False)
_ch(g, "kalachakra_method", "Kalachakra dasa", 5, ["Full cycle fraction, continuous MDs, ADs strictly from dasa cycle (Santhanam)", "First dasa fraction, ADs strictly from MDs (Dr. Raman)",
                                                   "Full cycle fraction, continuous MDs & ADs (version 5.0)", "First dasa fraction, continuous ADs",
                                                   "First dasa fraction, continuous MDs, ADs from MD like MDs from navamsa (Rao & Rath)",
                                                   "Navamsa progression, standard cycles used for ADs instead of MDs (Raghavacharya)", "Full cycle fraction, MDs strictly from cycle, ADs from MD like MDs from navamsa (SM Singh)"])
_ch(g, "kalachakra_rohini_leo", "Kalachakra: Rohini's 4th pada is", True, [(False, "Cancer navamsa"), (True, "Leo navamsa")])

g = "Rasi dasas"
for _k, _label, _d in (("narayana_varga", "Narayana dasa of", 0), ("lagnamsaka_varga", "Lagnamsaka dasa from", 1), ("padanathamsa_varga", "Padanaathaamsa dasa of", 1), ("paryaya_varga", "Paryaaya dasa of", 6)):
    _add(g, _k, _label, _d, DIVISION_NAMES)
_ch(g, "sudasa_ad", "Sudasa antardasas", 4, ["Like in Narayana dasa", "Quadrants from dasa sign (odd/even: forward/backward)", "Regular from dasa sign (odd/even: forward/backward)",
                                             "Quadrants from dasa sign or 7th (odd/even: forward/backward)", "Regular from dasa sign or 7th (odd/even: forward/backward)"])
_ch(g, "shoola_ad", "Shoola dasa antardasas", 1, ["From dasa sign itself", "From the stronger of dasa sign and 7th from it", "From the lord of the stronger of dasa sign and 7th from it"])
_ch(g, "drig_parasara", "Drigdasa", True, [(True, "Taught by Parasara"), (False, "Taught by SJC teachers in 1998-2007")])
_add(g, "chara_exaltation", "Chara dasa: add/subtract one year if the lord is exalted/debilitated", True)

g = "Other dasas"
_add(g, "moola_lagna", "Moola dasa: use lagna as a candidate", True)
_add(g, "moola_moon", "Moola dasa: use Moon as a candidate", True)
_add(g, "moola_sun", "Moola dasa: use Sun as a candidate", True)
_ch(g, "moola_no_correction", "Moola dasa: graha in moolatrikona", False, [(False, "Twelve years"), (True, "Zero years")])
_add(g, "naisargika_no_lord", "Naisargika: mahadasa lord has no antardasa", True)
_add(g, "naisargika_3_10", "Naisargika: grahas in 3rd and 10th from dasa lord have no antardasas", False)
_add(g, "naisargika_others", "Naisargika: grahas in 2nd, 6th, 11th and 12th from dasa lord have no antardasas", False)
_ch(g, "tara_parasara", "Tara dasa", False, [(False, "Pt Sanjay Rath's teaching"), (True, "Parasara's definition")])
_add(g, "tara_direction_from_star", "Tara dasa: use nakshatra (savya/apasavya) to reckon direction, instead of sign (odd/even)", False)
_ch(g, "tara_sesham", "Tara dasa: dasa sesham", 1, ["No dasa sesham", "From Moon, like in Vimsottari dasa", "From Moon, but in reverse for apasavya nakshatras"])
_add(g, "sudarsana_varga", "Sudarsana Chakra dasa of", 0, DIVISION_NAMES)
_ch(g, "sudarsana_ad_lord", "Sudarsana Chakra antardasas", True, [(False, "From dasa sign"), (True, "From the lord of dasa sign")])
_add(g, "buddhi_varga", "Buddhi gati dasa of", 0, DIVISION_NAMES)

g = "Tajaka"
_ch(g, "tajaka_true_year", "Year by", True, [(False, "Mean solar motion"), (True, "Exact solar motion")])
_ch(g, "tajaka_tropical", "Solar year", False, [(False, "Sidereal solar year (mean: 365.256364 days)"), (True, "Tropical solar year (mean: 365.24219 days)")])
_ch(g, "muntha_method", "Muntha", 1, ["Muntha of rasi chart shown in all vargas", "Muntha from each varga chart, with antardasas starting from dasa sign", "Muntha from each varga chart, with antardasas starting from dasa lord"])

g = "Tithi Pravesha"
_add(g, "tp_solar_month", "Use solar (as opposed to soli-lunar) months in Tithi Pravesha", True)

g = "Calendars"
_ch(g, "lunar_month_kind", "Lunar month", 1, ["Suklanta (month starts & ends at Full Moon)", "Amanta (month starts & ends at New Moon)", "Solar (month starts when Sun changes sign)"])
_ch(g, "lunar_tropical", "Lunar months are named from", False, [(False, "Sidereal signs (most popular, star aligned)"), (True, "Tropical signs (Vishnu Purana, season aligned)")])
_add(g, "lunar_year_sign", "Sign that begins the lunar year", 11, list(enumerate(SIGNS)))
_add(g, "solar_year_sign", "Sun's entry into this sign starts a new solar year", 0, list(enumerate(SIGNS)))
_ch(g, "solar_tropical", "Solar year in", False, [(False, "Sidereal signs (most popular, star aligned)"), (True, "Tropical signs (Vishnu Purana, season aligned)")])



def _degrees(key, tables):
    """Settings shows the table of degrees each choice of ``key`` follows under it: ``tables`` maps a choice's value to its rows, (name, a degree
    per sign from Aries)."""
    o = next(o for o in OPTIONS if o["key"] == key)
    for c in o["choices"]:
        c["table"] = [{"name": n, "degrees": [int(d) for d in degs]} for n, degs in tables[c["value"]]]


# Pushkara and Mrityu bhaga on one page, each chosen apart, so any table of one goes with either of the other (docs/SOURCES.md section 4)
g = "Pushkara and Mrityu Bhaga"
_ch(g, "pushkara_patel", "Pushkara Bhaga definition", False, [(False, "Given in Jataka Parijatam"), (True, "Given by Sri CS Patel in \"Nadi & Navamsha Astrology\"")],
    help="One degree in each sign, the same for every graha; a degree of 21 is the 21st degree, 20 to 21. Jataka Parijatam 1.58 is the classical list; "
         "Sri CS Patel's is modern, one degree for each element.")
_degrees("pushkara_patel", {False: [("Every graha", N.PUSHKARA_BHAGA_SCHEME1)], True: [("Every graha", N.PUSHKARA_BHAGA_SCHEME2)]})
# the app's default is the second table, whose Moon row is the one the texts give (PD 13.10; SAR ch. 5 and HS 5.47 but for Virgo); the ini's is the first
_ch(g, "mrityu_second_table", "Mrityu Bhaga table", True, [(True, "Phala Deepika and Brihat Prajapatyam"), (False, "Saravali, Jataka Parijatam and Sarvartha Chintamani")],
    help="A degree for each graha, the lagna and Maandi in each sign. The two tables differ only in the Moon's row: Phala Deepika's is its verse 13.10, "
         "the Moon's list most texts give (Saravali and Hora Sara read 4 for Virgo); the other table's Moon row has no verse found.")
_ch(g, "mrityu_location", "A Mrityu Bhaga of 19 degrees means", 2, ["Starts there, i.e. 19 deg - 20 deg is the region", "Mid-point there, i.e. 18.5 deg - 19.5 deg is the region", "The 19th degree, i.e. 18 deg - 19 deg is the region"],
    help="The texts give a degree, not a span. Counted as the 19th degree, the one in progress from 18 to 19, is the traditional reading.")
_MRITYU = lambda t: [(n, N.MRITYU_BHAGA_MAANDI if n == "Maandi" else t[n]) for n in N._MB_ROWS]  # noqa: E731
_degrees("mrityu_second_table", {False: _MRITYU(N.MRITYU_BHAGA_PARASARA), True: _MRITYU(N.MRITYU_BHAGA_SARAVALI)})

g = "Arudha padas"
_ch(g, "arudha_exceptions_bhava", "Bhava arudhas", True, [(False, "Do not use exceptions in bhava arudha padas"), (True, "Use exceptions in bhava arudha padas")])
_ch(g, "arudha_exceptions_graha", "Graha arudhas", True, [(False, "Do not use exceptions in graha arudha padas"), (True, "Use exceptions in graha arudha padas")])
_add(g, "arudha_nodes", "Use Rahu and Ketu as the lords of Aq and Sc when they are stronger than Saturn and Mars", True)
_add(g, "arudha_longitude", "Find arudha padas of bhavas using exact longitudes", False)
_add(g, "arudha_div_longs", "Use divisional longitudes of grahas for longitude based arudha padas in divisional charts", False)
_ch(g, "arudha_base", "Base for longitude based arudha padas", 0, [(i, n) for i, n in enumerate(("Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Bhava Lagna"))])

g = "Bhava chart and aspect table"
_ch(g, "bhava_ref", "Reference for the bhava/chalit chakra", 2, [(i, n) for i, n in enumerate(("Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"))])
_add(g, "bhava_nodes_reversed", "Bhavas from Rahu and Ketu are reckoned anti-zodiacally", False)     # the ini's default is on; here they count forward like every graha
_ch(g, "aspect_full", "Full aspect value in the aspect table", 100, [(60, "60"), (100, "100")])     # the ini's default is 60; out of 100 reads as a percentage
_ch(g, "aspect_parasara", "Aspects of Mars, Jupiter and Saturn", True, [(True, "As per Parasara's teachings"), (False, "As per Dr Raman's teachings")])

g = "Life cycle"
_add(g, "lifecycle_years", "Life cycle length for casting a new chart (years)", 144.0, gt=0, le=1000)
_add(g, "lifecycle_kind", "Year of the life cycle", "SOLAR", [("SOLAR", "Solar longitude based year (360 deg year)"), ("TITHI", "Year with 360 tithis")])

g = "Longevity"
_ch(g, "longevity_orbs", "Yuti and drishti in the longevity rules", True,
    [(True, "Within the Tajika deeptamsas (Su 15°, Mo 12°, Ma 8°, Me 7°, Ju 9°, Ve 7°, Sa 9°, Ra and Ke 8°): two grahas within the smaller one, a bhava within the graha's of its cusp"),
     (False, "By rasi (BPHS): the same sign, or graha drishti on the sign")])
_ch(g, "longevity_saturn", "Saturn lowers the three pairs' class (43.47)", 0,
    [(0, "Only when he decides as the lagna or 8th lord (he causes the yoga)"), (1, "Whenever he is among the deciding grahas, his own Saturn-Moon pair too"), (2, "Never")])
_add(g, "longevity_jupiter", "Jupiter in the 1st or 7th, touched only by benefics, raises the three pairs' class (43.48)", True)
_ch(g, "longevity_outer_years", "Years for Very short and Extremely long life", False,
    [(False, "None: BPHS gives years only for short, medium and long"), (True, "20 (Yogarishta, 43.53) and 120 (the full span in Kali yuga)")])
_ch(g, "longevity_pairs_figure", "The three pairs' years in the Summary's average", "rectified",
    [("rectified", "Kept inside the class's range (Jaimini)"), ("literal", "The class's years x (1 - degrees / 30), as 43.45 is worded")])


g = "User defined special point"
_add(g, "special_point_on", "Show this special point in charts", False)
_add(g, "special_point_name", "Named", "Special Point", max_length=40)
_add(g, "special_point_symbol", "Denoted by the symbol", "SP", max_length=4)
_add(g, "special_point_offset", "At this many degrees (decimal)", 0.0, ge=0, lt=360)
_ch(g, "special_point_after", "The offset is", True, [(False, "behind"), (True, "ahead of")])
_add(g, "special_point_kind", "From", "planet", [("planet", "A graha"), ("saham", "A sahama"), ("sign", "The beginning of a sign"), ("midpoint", "The mid-point of two grahas")])
_add(g, "special_point_planet", "The graha (or the first of the mid-point)", 0, list(enumerate(("Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"))))
_add(g, "special_point_planet2", "The second graha of the mid-point", 0, list(enumerate(("Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"))))
_add(g, "special_point_saham", "The sahama (its number in the Sahamas list, from 0)", 0, list(enumerate(SL.SAHAMA_NAMES[::-1])))
_add(g, "special_point_sign", "The sign", 0, list(enumerate(SIGNS)))

g = "Graha special lagna"
_add(g, "special_lagna_on", "Show this special lagna in charts (research)", False, help="At the longitude of the chosen graha when it rose, moving this many circles a day since. Jupiter and 9 shows as Ju9.")
_add(g, "special_lagna_planet", "Graha used", 1, [(i, n) for i, n in enumerate(("Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")) if i])
_add(g, "special_lagna_speed", "Speed factor", 5, [(i, str(i)) for i in range(1, 25)])
_add(g, "special_lagna_nodes_reverse", "Go in reverse for Rahu and Ketu", True)


def _type(o):
    if o["choices"]:
        return Literal[tuple(c["value"] for c in o["choices"])]
    return type(o["default"])


# the request's settings: an option left out takes its default
SettingsIn = create_model("SettingsIn", per_dasa=(dict[str, dict], {}), **{o["key"]: (_type(o), Field(o["default"], **o["limits"])) for o in OPTIONS})


def schema():
    """The Settings screen's content: the groups in order, each with its options."""
    groups = {}
    for o in OPTIONS:
        groups.setdefault(o["group"], []).append({k: o[k] for k in ("key", "label", "default", "choices", "help")} | {
            "kind": "choice" if o["choices"] else {bool: "bool", float: "number", str: "text"}[type(o["default"])], **o["limits"]})
    return [{"name": n, "options": v} for n, v in groups.items()]


def config(s) -> E.EphemerisConfig:
    """The options that change the chart itself. Surya Siddhanta keeps the chosen ayanamsa."""
    star = s.custom_star if s.ayanamsa == "CUSTOM_STAR" else None
    return E.EphemerisConfig(
        ayanamsa=s.ayanamsa, ayanamsa_offset_deg=s.ayanamsa_offset_deg, custom_star=star, custom_star_longitude=s.custom_star_longitude,
        custom_star_fixed_plane=s.custom_star_fixed_plane, nodes=s.nodes, topocentric=s.topocentric, true_positions=s.true_positions,
        apparent_refraction=s.apparent_refraction, no_aberration=s.no_aberration, no_gravitational_deflection=s.no_gravitational_deflection,
        no_nutation=s.no_nutation, sunrise_definition=s.sunrise_definition,
        upagraha_rise=(s.kaala_rise,) * 4 + (s.mandi_rise, s.gulika_rise), mandi_in_saturn_portion=s.mandi_in_saturn_portion,
        gulika_in_saturn_portion=s.gulika_in_saturn_portion, upagraha_day_definition=s.upagraha_day_definition, vyatipata_method=s.vyatipata_method,
        continuous_special_lagnas=s.continuous_special_lagnas, swisseph_202=s.swisseph_202, siddhanta=s.siddhanta, ephemeris=s.ephemeris)


def varga_options(s) -> V.VargaOptions:
    picked = {"d%d" % n: getattr(s, "d%d" % n) for n in _names}
    return dataclasses.replace(V.DEFAULT, equal_d30_longitudes=s.equal_d30_longitudes, mirror_reversed_longitudes=s.mirror_reversed_longitudes, **picked)


def apply_process_wide(s) -> None:
    # shortcut: one table for the whole process, as sign_strength.set_nodal_exaltation says; a single-user local app has one setting at a time
    SS.set_nodal_exaltation(s.nodal_parasara)
    SB.set_moolatrikona_bphs(s.moolatrikona_bphs)


def jchart(ch, day, s) -> J.JChart:
    """The chart the dasa builders read, with the chosen varga schemes. The builders' own signs are the default schemes (test_settings checks they agree)."""
    jc = J.JChart(ch, day)
    jc.correction = ch.get("nakshatra_correction", 0.0)
    opt = varga_options(s)
    if opt != V.DEFAULT:
        jc.signs = [[V.varga_sign(x, n, opt) for x in jc.lons] for n in V.DIVISIONS]
    return jc


def ashtakavarga_kw(s) -> dict:
    return {"parasara": tuple(getattr(s, "av_parasara_%d" % k) for k in range(6)), "definition": s.av_definition,
            "bhava_driven_sav": s.av_bhava_driven_sav}


def day_kw(s) -> dict:
    return {"kaala_day_night_separate": s.kaala_day_night_separate, "weekday_definition": s.weekday_definition, "mahakala_definition": s.mahakala_definition}


def amsa_bala(s, ch, lagna_signs, janma_ghatis):
    """The vaiseshikamsa options; the other flags only cancel what swarudha added, so they have no effect at swarudha 0."""
    if not s.swarudha:
        return None
    nine = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    flags = {f.name: getattr(s, "amsa_" + f.name) for f in dataclasses.fields(SB.AmsaBala) if hasattr(s, "amsa_" + f.name)}
    return SB.AmsaBala(swarudha=s.swarudha, past_table=True, rasi_lons=[ch["planet_longitudes"][p] for p in nine], retrograde=[ch["retrograde"][p] for p in nine],
                       lagna_lon=ch["lagna_lon"], lagna_signs=lagna_signs, ghatis_since_sunrise=janma_ghatis, combustion_classical=s.combustion_classical, **flags)


def year_mapper(birth, cfg, s, definition=None):
    """Dasa years -> dates by the year definitions (ephemeris.dasa_year_mapper's docstring). The fixed ones count days from birth."""
    d = s.year_definition if definition is None else definition
    if d == 3:
        return E.dasa_year_mapper(birth, cfg, "SOLAR")
    if d == 4:
        return E.dasa_year_mapper(birth, cfg, "TITHI")
    if d == 7:
        return E.dasa_year_mapper(birth, dataclasses.replace(cfg, ayanamsa="TROPICAL"), "SOLAR")
    days = {0: 365.24219, 1: 360.0, 2: s.year_length, 6: 365.256364}[d]
    born = datetime(birth.year, birth.month, birth.day) + timedelta(hours=birth.hour_local)
    return lambda years: born + timedelta(days=days * years)
