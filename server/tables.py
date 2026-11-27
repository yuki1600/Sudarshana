"""The list views that are one table each: the Key Info modes and the Strengths lists, as
{columns, rows}. One builder per list."""
from core_logic import avasthas as AV, ephemeris as E, key_info as K, varga_charts as V, natal_chart as N, sahams_library as SL, shadbala as SB, sign_strength as SS, special_lagnas_upagrahas as U, tajika as T

from . import settings as S
from .basics import KARAKA_SLOTS, POINT_ORDER, PLANETS, SIGNS, _points, _tables
from .chakras import SIGN_LORD
from .charts import CLASS_NAMES, ChartSpec, relationships
from .houses import ORDINAL, _bhavas
from .strengths import SEVEN, _varga_signs, vaiseshikamsa_of

BODIES = ["Lagna"] + PLANETS
HOUSE_ROWS = PLANETS + ["Maandi", "Lagna"] + ["%s bhava" % ORDINAL[i] for i in range(1, 12)]
CHECK = lambda on: "Yes" if on else "-"  # noqa: E731


def _lon(x):
    """The longitude text, rounded to 0.01 arc second."""
    h = round((x % 360.0) * 360000) % 129600000
    return "%d %s %02d' %05.2f\"" % (h // 360000 % 30, SIGNS[h // 10800000], h % 360000 // 6000, h % 6000 / 100.0)


def _lons(ch):
    return [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS]


def _table(columns, rows):
    return {"columns": columns, "rows": [[str(c) for c in r] for r in rows]}


def latitudes(b, ch, cfg, s):
    pos = E.planet_positions(b.jd_ut, cfg, b)
    # the list ends at Rahu
    return _table(["Graha", "Longitude", "Lon Speed", "Latitude", "Lat Speed", "Distance", "Dist Speed"],
                  [[p, "%.3f deg" % pos[p]["lon"], "%.3f deg/day" % pos[p]["speed"], "%.3f deg" % pos[p]["lat"], "%.3f deg/day" % pos[p]["lat_speed"], "%.4f AU" % pos[p]["dist"], "%.6f AU/day" % pos[p]["dist_speed"]] for p in PLANETS[:8]])


LONGITUDE_DIVISIONS = (1, 9, 10, 2, 3, 4, 7, 12, 16, 20, 24, 27, 30, 40, 45, 60, 5, 6, 8, 11, 81, 108, 144)


def varga_longitudes(b, ch, cfg, s):
    opt = S.varga_options(s)

    def text(x):
        h = x % 360.0
        return "%d%s%02d" % (int(h % 30), SIGNS[int(h // 30)], round((h % 1.0) * 60))    # the minutes are rounded alone: 3Cn60
    pts = _points(ch)


    def lon_in(n, d):
        if n == "Varnada Lagna" or (n[0] == "V" and n[1:].isdigit()):       # the varga's own sign (see _sign_in), with the degrees of the rasi Varnada in that varga
            return _sign_in(ch, pts, n, d, opt) * 30.0 + V.varga_longitude(pts[n], d, opt) % 30.0
        return V.varga_longitude(pts[n], d, opt)
    return _table(["Body"] + ["D-%d" % d for d in LONGITUDE_DIVISIONS], [[n] + [text(lon_in(n, d)) for d in LONGITUDE_DIVISIONS] for n in POINT_ORDER])


def _sign_in(ch, pts, name, d, opt):
    """A body's sign in division ``d``. Each varga has its own Varnada Lagnas, from its own lagna and hora lagna ."""
    if name == "Varnada Lagna" or (name[0] == "V" and name[1:].isdigit()):
        house = 0 if name == "Varnada Lagna" else int(name[1:]) - 1
        return int(U.compute_varnada_lagnas(V.varga_sign(ch["lagna_lon"], d, opt) * 30.0, V.varga_sign(ch["special_lagnas"]["Hora_Lagna"], d, opt) * 30.0)[house] // 30)
    return V.varga_sign(pts[name], d, opt)


def rasis(b, ch, cfg, s):
    opt = S.varga_options(s)
    pts = _points(ch)
    return _table(["Body"] + ["D-%d" % d for d in V.DIVISIONS], [[n] + [SIGNS[_sign_in(ch, pts, n, d, opt)] for d in V.DIVISIONS] for n in POINT_ORDER])


def _nava(lon):
    return _table(["Tara", "Meaning", "Lord", "Nakshatra 1", "Nakshatra 2", "Nakshatra 3"], K.nava_taras(lon))


def _special(lon):
    return _table(["Special tara", "Meaning", "Nakshatra", "Lord"], K.special_taras(lon))


def nakshatra_aspects(b, ch, cfg, s):
    rows = K.nakshatra_aspects(dict(enumerate(_lons(ch)[1:9])))
    return _table(["Graha", "Latta on", "Occupied Star", "Aspected Stars"], [[PLANETS[i], latta, star, " ".join(asp)] for i, (latta, star, asp) in enumerate(rows)])


# The transit view's murthi, anga graha and kakshya lists, for the birth (server/transits.py): each graha at birth as if it were the transit
def murthis(b, ch, cfg, s):
    """Each graha's murthi at birth: the Moon's sign, from the natal Moon, when the graha last entered its sign (PVR 26.2). The Moon has none."""
    from .transits import _murthis
    lons = _lons(ch)
    m = _murthis(b.jd_ut, [int(x // 30) for x in lons], int(lons[2] // 30), cfg)
    return _table(["Graha", "Murthi"], [[PLANETS[p - 1], m.get(p, "-")] for p in range(1, 10)])


def anga_grahas(b, ch, cfg, s):
    """The limb each graha's star falls on, counted from the natal Moon's, lagna's and Sun's stars (PD 26.35-40)."""
    lons = _lons(ch)
    natal = dict(enumerate(lons[1:10]))
    return _table(["Graha", "Limb (Moon)", "Result (from Moon)", "Limb (lagna)", "Result (from lagna)", "Limb (Sun)", "Result (from Sun)"],
                  [[n, *m, *l, *u] for n, m, l, u in zip(PLANETS, K.anga_graha(natal, lons[2]), K.anga_graha(natal, lons[0]), K.anga_graha(natal, lons[1]))])


def kakshyas(b, ch, cfg, s):
    """Each body's kakshya at birth: the eighth of its sign (3°45') and its lord (PVR 25.5.2)."""
    from .transits import _kakshyas
    return _table(["Graha", "Sign", "Kakshya", "Span", "Kakshya lord"], _kakshyas(_lons(ch)))


def yogi(b, ch, cfg, s):
    lons = _lons(ch)
    y = (lons[1] + lons[2] + 93.0 + 1.0 / 3.0) % 360.0
    a = (y + 186.0 + 2.0 / 3.0) % 360.0
    return _table(["Title", "Graha in this chart", "Longitude"], [["Yogi", K.TARA_LORDS[int(y // K.NAK) % 9], _lon(y)], ["Sahayogi", SIGN_LORD[int(y // 30)], "-"],
                                                                   ["Avayogi", K.TARA_LORDS[int(a // K.NAK) % 9], _lon(a)]])


def _house_points(b, ch, cfg, s):
    """The bodies and cusps of the Pushkara and Mrityu Bhaga lists: (label, table row of the engine, longitude)."""
    pts = _points(ch)
    cusps = [x[1 if s.house_cusp_in_middle else 0] for x in _bhavas(b, ch, cfg, s)]
    return [(n, "Lagna", cusps[ORDINAL.index(n.split()[0])]) if n.endswith("bhava") else (n, n, pts[n]) for n in HOUSE_ROWS]


def pushkaras(b, ch, cfg, s):
    rows = []
    for name, _, lon in _house_points(b, ch, cfg, s):
        amsa, bhaga, d = N.pushkara_position(lon, s.pushkara_patel)
        rows.append([name, CHECK(amsa), CHECK(bhaga), "%.4f deg" % d])
    return _table(["Body", "In Pushkaramsa?", "In Pushkara Bhaga?", "From Pushkara Bhaga Center"], rows)


def mrityu_bhaga(b, ch, cfg, s):
    rows = []
    for name, row, lon in _house_points(b, ch, cfg, s):
        d, within = N.mrityu_bhaga_distance(row, lon, s.mrityu_second_table, s.mrityu_location)
        rows.append([name, "%.4f deg" % d, CHECK(within)])
    return _table(["Body", "From Mrityu Bhaga Center", "Within the Trimsamsa (degree)"], rows)


def drekkanas(b, ch, cfg, s):
    pts = _points(ch)
    return _table(["Body", "Drekkana occupied"], [[n, K.drekkana_labels(ch["lagna_lon"] + 30.0 * (HOUSE_ROWS.index(n) - 10) if n.endswith("bhava") else pts[n])] for n in HOUSE_ROWS])


def special_tithis(b, ch, cfg, s):
    rows = K.special_tithis(ch["planet_longitudes"]["Moon"], ch["planet_longitudes"]["Sun"])
    return _table(["Special Tithi", "Seed", "Name", "% left", "Lord", "Deity", "Index", "Index in paksha"],
                  [[r["special"], r["seed"], r["name"], "%d%%" % int(r["left"] * 100), r["lord"], r["deity"], ORDINAL_TEXT(r["tithi"]), "%s in %s half" % (ORDINAL_TEXT(r["paksha_index"]), r["paksha"])] for r in rows])


def ORDINAL_TEXT(n):
    return "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}.get(n if n < 20 else n % 10, "th"))     # 22nd, 1st


def karakas(b, ch, cfg, s):
    lons = _lons(ch)
    slots = N.chara_karaka_slots(lons, [int(x // 30) for x in lons], s.chara_karakas)
    return _table(["Chara karaka", "Graha", "Meaning of portfolio"], [[k, BODIES[i], m] for k, m, i in zip(KARAKA_SLOTS, _tables()[0]["karaka_meanings"], slots) if i])


def combustion(b, ch, cfg, s):
    lons = _lons(ch)
    retro = [False] + [bool(ch["retrograde"].get(p)) for p in PLANETS]
    return _table(["Graha", "Combust?"], [[BODIES[p], CHECK(N.is_combust(p, lons, retro, s.combustion_by_motion, s.combustion_classical))] for p in range(2 if s.combustion_classical else 3, 8)])


def graha_yuddha(b, ch, cfg, s):
    war = N.planetary_war(_lons(ch))
    return _table(["Graha", "Wins?", "Loses?"], [[BODIES[p], CHECK(war[p][0]), CHECK(war[p][1])] for p in range(1, 10)])


def brahma_rudra(b, ch, cfg, s):
    return _table(["Special Deity", "Graha in this chart"], [[n, BODIES[p]] for n, p in zip(("Brahma", "Rudra", "Maheswara"), K.brahma_rudra_maheswara(S.jchart(ch, None, s)))])


def malicious(b, ch, cfg, s):
    return _table(["Malicious Division", "Lord"], K.malicious_divisions(ch["lagna_lon"], ch["planet_longitudes"]["Moon"]))


def sahams(b, ch, cfg, s):
    t = _tables()[0]
    lons = SL.saham_longitudes(_lons(ch)[:8], E.day_lords(b, cfg)["is_day"])
    return _table(["Sahama name", "Position", "Nakshatra", "Meaning of sahama"], [["%s Sahama" % n, _lon(x), t["nakshatra_abbr"][int(x * 0.075)], m] for n, x, m in zip(SL.SAHAMA_NAMES[::-1], lons, t["sahama_meanings"])])


def aspect_evaluation(b, ch, cfg, s, natal_ch=None, aspecting_varga=1, aspected_varga=1, aspecting_natal=False, aspected_natal=False):
    """Planetary Aspect Evaluation and its options: the chart and the varga of the aspecting planets and of the aspected positions."""
    opt = S.varga_options(s)
    source = lambda natal, d: [V.varga_longitude(x, d, opt) for x in _lons(natal_ch if natal and natal_ch else ch)]  # noqa: E731
    from_planets = source(aspecting_natal, aspecting_varga)
    lons = source(aspected_natal, aspected_varga)
    planets = {i: from_planets[i] for i in range(1, 10)}
    rows = []
    same = aspecting_varga == aspected_varga and (aspecting_natal == aspected_natal or not natal_ch)     # the aspecting and aspected grahas are the same chart's
    row = lambda label, target, skip=0: [label, _lon(target)] + ["%.2f%%" % v if v and p != skip else "-" for p, v in enumerate(K.aspect_evaluation_row(target, planets), 1)]  # noqa: E731
    for k, name in enumerate(BODIES):     # Rahu and Ketu don't count on each other: none from Ketu on Rahu's own row, nor from Rahu on Ketu's
        rows += [row(name if h == 0 else "%s from %s" % (ORDINAL[h], name), lons[k] + (-30.0 if k >= 8 else 30.0) * h, 17 - k if same and h == 0 and k >= 8 else 0) for h in range(12)]     # the nodes count backward
    pts = _points(natal_ch if aspected_natal and natal_ch else ch)
    rows += [row(n, V.varga_longitude(pts[n], aspected_varga, opt)) for n in POINT_ORDER[10:]]
    return _table(["Aspected Body", "Longitude (in D-%d)" % aspected_varga] + PLANETS, rows)


# Strengths

def _avasthas(b, ch, cfg, s, varga=1):
    opt = S.varga_options(s)
    points = [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS]
    retro = [False] + [bool(ch["retrograde"].get(p)) for p in PLANETS]
    # as ayurdaya.Natal.combust: Mars .. Saturn by the fixed-orb rule, the Moon within 12 degrees
    combust = [min((points[2] - points[1]) % 360.0, (points[1] - points[2]) % 360.0) <= 12.0 if p == 2 else N.is_combust(p, points, retro, s.combustion_by_motion, s.combustion_classical) for p in range(1, 10)]
    return AV.graha_avasthas(points[1:], ch["lagna_lon"], E.day_lords(b, cfg, **S.day_kw(s))["janma_ghatis"], compound=s.avastha_compound,
                             varga_signs=None if varga == 1 else [V.varga_sign(ch["planet_longitudes"][p], varga, opt) for p in PLANETS], combust=combust)


def avasthas(b, ch, cfg, s, varga=1):
    av = _avasthas(b, ch, cfg, s, varga)
    return _table(["Graha", "Age", "Alertness (D-%d)" % varga, "Mood (D-%d)" % varga], [[p, av[p]["age_name"], av[p]["alertness_name"], av[p]["mood_names"]] for p in PLANETS])


def sign_dignity(p, lon, sign):
    """Exalted, debilitated, moolatrikona or own sign, or "": by BPHS degrees in the rasi (as the aspect table marks them),
    by the sign alone for the nodes and in a varga (``lon`` None)."""
    if p <= 7 and lon is not None:
        d = N.get_graha_dignity(PLANETS[p - 1], lon)
        return d if d in ("Exalted", "Debilitated", "Moolatrikona", "Own Sign") else ""
    return ("Exalted" if SS.EXALTATION[p] == sign else "Debilitated" if SS.DEBILITATION[p] == sign else
            "Moolatrikona" if lon is None and SS.MOOLATRIKONA[p] == sign else "Own Sign" if SS.owns_sign(p, sign) else "")


def avasthas_parashara(b, ch, cfg, s, varga=1):
    """Starlight's avasthas by Parashara (BPHS 45): age, alertness and mood with the reasons for each, and the dignity of the
    sign, in the varga (alertness and mood) and the rasi (the rest)."""
    av = _avasthas(b, ch, cfg, s, varga)
    opt = S.varga_options(s)
    lon = lambda p: ch["planet_longitudes"][p]  # noqa: E731
    rasi = lambda i, p: sign_dignity(i, lon(p), int(lon(p) // 30) % 12)  # noqa: E731
    vrg = lambda i, p: rasi(i, p) if varga == 1 else sign_dignity(i, None, V.varga_sign(lon(p), varga, opt))  # noqa: E731
    return _table(["Graha", "Age", "Alertness (D-%d)" % varga, "Mood (D-%d)" % varga, "Dignity (D-1)", "Dignity (D-%d)" % varga, "Why age", "Why alertness", "Why mood"],
                  [[p, av[p]["age_name"], av[p]["parashara_alertness_name"], av[p]["parashara_mood_names"], rasi(i, p), vrg(i, p),
                    av[p]["age_why"], av[p]["parashara_alertness_why"], "; ".join(av[p]["parashara_mood_why"])] for i, p in enumerate(PLANETS, 1)])


def sayanadi(b, ch, cfg, s):
    av = _avasthas(b, ch, cfg, s)
    return _table(["Graha", "Activity"] + ["Intensity %d" % i for i in range(1, 6)], [[p, av[p]["activity_name"], *av[p]["intensity_names"]] for p in PLANETS])


def vaiseshikamsa(b, ch, cfg, s):
    t = _tables()[0]
    vai = vaiseshikamsa_of(ch, s, E.day_lords(b, cfg, **S.day_kw(s)))
    name = lambda n, table: t[table][n - 2].strip() if n >= 2 else ""  # noqa: E731
    return _table(["Vaiseshikamsas", "Dasa Varga (10)", "Shodasa Varga (16)", "Sapta Varga (7)", "Shad Varga (6)"],
                  [[p, name(vai[p]["dasa"], "vaiseshikamsa_dasa"), name(vai[p]["shodasa"], "vaiseshikamsa_shodasa"), name(vai[p]["sapta"], "vaiseshikamsa_sapta"), name(vai[p]["shad"], "vaiseshikamsa_shad")] for p in PLANETS])


def _tajaka_balas(b, ch, cfg, s):
    jc = S.jchart(ch, None, s)
    sb = E.chart_shadbala(b, ch, cfg)
    return T.tajaka_balas(jc.signs, jc.lons, [sb["planets"][p]["uchcha"] for p in SEVEN], E.day_lords(b, cfg)["is_day"])


def pancha(b, ch, cfg, s):
    tb = _tajaka_balas(b, ch, cfg, s)
    return _table(["Graha", "Pancha-vargeeya", "Classification"], [[p, "%.2f" % tb[p]["pancha_vargeeya"], tb[p]["pancha_class"]] for p in SEVEN])


def dwadasa(b, ch, cfg, s):
    tb = _tajaka_balas(b, ch, cfg, s)
    return _table(["Graha", "Dwadasa-vargeeya"], [[p, "%d (out of 12)" % tb[p]["dwadasa_vargeeya"]] for p in SEVEN])


def harsha(b, ch, cfg, s):
    tb = _tajaka_balas(b, ch, cfg, s)
    return _table(["Graha", "Harsha Bala", "Bala"], [[p, tb[p]["harsha"], tb[p]["harsha_class"]] for p in SEVEN])


def rashmis(b, ch, cfg, s):
    ra = SB.rashmis_ishta_kashta(E.chart_shadbala(b, ch, cfg)["planets"])
    keys = ["uchcha_rashmi", "cheshta_rashmi", "subha", "asubha", "ishta", "kashta"]
    return _table(["Graha", "Uchcha Rashmi", "Cheshta Rashmi", "Subha Rashmi", "Asubha Rashmi", "Ishta (Parasara)", "Kashta (Parasara)"], [[p] + ["%.2f" % ra[p][k] for k in keys] for p in SEVEN])


def _shadbala(columns, keys):
    def view(b, ch, cfg, s):
        planets = E.chart_shadbala(b, ch, cfg)["planets"]
        return _table(["Graha"] + columns, [[p] + ["%.2f" % planets[p][k] for k in keys] for p in SEVEN])
    return view


def _friends(kind):
    """The natural, temporary or compound relationship of each of Sun .. Ketu (rows) with each other one (columns), in the rasi chart."""
    def view(b, ch, cfg, s):
        rows = [relationships(ch, s, ChartSpec(), kind, p) for p in range(1, 10)]
        return _table(["Graha"] + list(rows[0]), [[p] + [CLASS_NAMES[c] for c in r.values()] for p, r in zip(PLANETS, rows)])
    return view


KEY_INFO = [("latitudes", "Latitudes, speeds etc", latitudes), ("aspects", "Graha Aspect Evaluation", aspect_evaluation), ("varga_longitudes", "All Divisional Longitudes", varga_longitudes),
            ("rasis", "Rasis occupied in all vargas", rasis), ("nava_moon", "Nava Taras (from Moon)", lambda b, ch, cfg, s: _nava(ch["planet_longitudes"]["Moon"])),
            ("nava_lagna", "Nava Taras (from lagna)", lambda b, ch, cfg, s: _nava(ch["lagna_lon"])), ("special_moon", "Special Taras (from Moon)", lambda b, ch, cfg, s: _special(ch["planet_longitudes"]["Moon"])),
            ("special_lagna", "Special Taras (from lagna)", lambda b, ch, cfg, s: _special(ch["lagna_lon"])), ("nak_aspects", "Nakshatra Aspects & Latta", nakshatra_aspects), ("yogi", "Yogi, Sahayogi, Avayogi", yogi),
            ("pushkaras", "Pushkaramsas and Pushkara Bhagas", pushkaras), ("tithis", "Special Tithis", special_tithis), ("karakas", "Chara Karakas", karakas), ("combustion", "Combustion", combustion),
            ("yuddha", "Graha Yuddha", graha_yuddha), ("brahma", "Brahma, Rudra, Maheswara", brahma_rudra), ("mrityu", "Distances from Mrityu Bhaga", mrityu_bhaga), ("drekkanas", "Graha drekkanas", drekkanas),
            ("malicious", "Lords of the 64th navamsa and 22nd drekkana", malicious), ("sahams", "Sahamas", sahams),
            ("friends_natural", "Friendships: natural", _friends("permanent")), ("friends_temporal", "Friendships: temporary", _friends("temporary")),
            ("friends_compound", "Friendships: compound", _friends("compound"))]
STRENGTH_LISTS = [("sthana", "Shadbala: Sthana", _shadbala(["Sthana Bala", "Uchcha", "Saptavargaja", "Oja Yugma", "Kendra", "Drekkana"], ["sthana", "uchcha", "saptavargaja", "oja_yugma", "kendra", "drekkana"])),
                  ("kaala", "Shadbala: Kaala", _shadbala(["Kaala Bala", "Natonnata", "Paksha", "Tribhaga", "Abda", "Maasa", "Vaara", "Hora", "Ayana", "Yuddha"],
                                                         ["kala", "natonnata", "paksha", "tribhaga", "abda", "masa", "vara", "hora", "ayana", "yuddha"])),
                  ("dig", "Shadbala: Dig", _shadbala(["DigBala"], ["dig"])), ("cheshta", "Shadbala: Cheshta", _shadbala(["Cheshta Bala"], ["cheshta"])),
                  ("drig", "Shadbala: Drik", _shadbala(["DrikBala"], ["drig"])), ("naisargika", "Shadbala: Naisargika", _shadbala(["Naisargika Bala"], ["naisargika"])),
                  ("rashmis", "Ishta-Kashta and Rashmis", rashmis), ("vaiseshikamsa", "Vaiseshikamsas", vaiseshikamsa), ("avasthas", "Basic Avasthas", avasthas), ("sayanadi", "Sayanadi Avasthas", sayanadi),
                  ("pancha", "Pancha-vargeeya Bala", pancha), ("dwadasa", "Dwadasa-vargeeya Bala", dwadasa), ("harsha", "Harsha Bala", harsha)]
VIEWS = {key: fn for key, _, fn in KEY_INFO + STRENGTH_LISTS} | {"avasthas_parashara": avasthas_parashara,     # Starlight's, in no list
                                                                  "murthis": murthis, "anga_grahas": anga_grahas, "kakshyas": kakshyas}
VARGA_VIEWS = {"avasthas", "avasthas_parashara"}      # these take the chart's varga


def listing():
    return {"key_info": [{"key": k, "name": n} for k, n, _ in KEY_INFO], "strengths": [{"key": k, "name": n} for k, n, _ in STRENGTH_LISTS]}
