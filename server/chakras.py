"""The Chakras wheels: which nakshatra (or sign) sits in each slot of a wheel, and the bodies on it. Each view puts a star
in slot (star - base + 28) % 28; web/src/wheelGeometry.ts holds where each slot goes. core_logic.chakras is the textbook
description of the same wheels."""
from core_logic import ephemeris as E, key_info as K, varga_charts as V, panchanga as P, sahams_library as SL, transits as TR
from core_logic.compatibility import tables as CT
from core_logic.mundane import MEAN_DAILY_SPEEDS

from . import settings as S
from .basics import PLANET_ABBR, PLANETS, SIGNS
from .calendars import LUNAR_MONTHS

# Kota Pala: the planet (1 Sun .. 8 Rahu), by the natal Moon's nakshatra and pada
KOTA_PALA = [[6, 6, 6, 2], [2, 2, 2, 2], [1, 1, 1, 1], [1, 2, 2, 2], [2, 2, 3, 3], [3, 3, 3, 6], [3, 3, 8, 8], [8, 8, 8, 4], [4, 4, 4, 4],
             [7, 7, 7, 7], [7, 4, 4, 4], [4, 4, 7, 7], [7, 8, 4, 4], [7, 7, 2, 2], [2, 2, 2, 5], [5, 5, 5, 5], [5, 5, 5, 5], [5, 2, 2, 2],
             [2, 2, 7, 7], [7, 5, 7, 4], [7, 7, 6, 6], [3, 3, 3, 3], [3, 3, 3, 3], [3, 8, 8, 8], [8, 8, 5, 5], [5, 5, 6, 6], [5, 5, 6, 6]]
SIGN_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
# The chakra menu's sets of bodies, as (label, key in the chart's tables)
SPHUTAS = [("Pr", "prana_sphuta"), ("De", "deha_sphuta"), ("Mr", "mrityu_sphuta"), ("TS", "sookshma_trisphuta"), ("Ti", "tithi_sphuta"), ("Yg", "yoga_sphuta"), ("RT", "rahu_tithi_sphuta"), ("Ks", "kshetra_sphuta"),
           ("Bj", "beeja_sphuta"), ("Tr", "trisphuta"), ("Ch", "chatusphuta"), ("Pn", "panchasphuta")]
UPAGRAHAS = [("Dh", "Dhuma"), ("Vy", "Vyatipata"), ("PV", "Parivesha"), ("IC", "Indra Chapa"), ("UK", "Upaketu"), ("Kl", "Kaala"), ("Mri", "Mrityu"), ("AP", "Artha_Prahara"), ("YG", "Yama_Ghantaka"), ("Md", "Mandi"), ("Gk", "Gulika")]
LAGNAS = [("BL", "Bhava_Lagna"), ("HL", "Hora_Lagna"), ("GL", "Ghati_Lagna"), ("VG", "Vighati_Lagna"), ("PP", "Pranapada"), ("SL", "Sree_Lagna"), ("IL", "Indu_Lagna"), ("BB", "Bhrigu_Bindu"), ("Ku", "Kunda")]
BASE_POINTS = ["Lagna"] + PLANETS + ["Uranus", "Neptune", "Pluto"]
TAJAKA_KINDS = (1, 2)    # dasa_systems' chart kinds: Tajaka and Tithi Pravesha


def _bodies(ch, b, cfg, s, shown, d):
    """(label, longitude) of the chosen sets, in D-``d``; the lagna and planets are always a chart's ``planets`` set."""
    opt = S.varga_options(s)
    at = lambda x: V.varga_longitude(x, d, opt)  # noqa: E731
    out = []
    if "planets" in shown:
        out += [("As", at(ch["lagna_lon"]))] + [(a, at(ch["planet_longitudes"][p])) for p, a in zip(PLANETS, PLANET_ABBR)]
    if "trisphuta" in shown:
        out += [(a, at(ch["sphutas"][k])) for a, k in SPHUTAS]
    if "upagrahas" in shown:
        out += [(a, at(ch["upagrahas"][k])) for a, k in UPAGRAHAS]
    if "lagnas" in shown:
        out += [(a, at(ch["special_lagnas"][k])) for a, k in LAGNAS]
    if "sahams" in shown:
        lons = [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS[:7]]
        out += [(n[:3], at(x)) for n, x in zip(SL.SAHAMA_NAMES[::-1], SL.saham_longitudes(lons, E.day_lords(b, cfg)["is_day"]))]
    return out


def _base_star(natal_ch, ch, o, s, default):
    """The star the wheel turns from: the fully customized one, a point in a varga, or the wheel's default."""
    if o.get("base_star") is not None:
        return o["base_star"]
    if o.get("base_point") is not None:
        p = o["base_point"]
        if p == 0:
            lon = natal_ch["lagna_lon"]
        elif BASE_POINTS[p] in natal_ch["planet_longitudes"]:
            lon = natal_ch["planet_longitudes"][BASE_POINTS[p]]
        elif BASE_POINTS[p] in natal_ch.get("outer", {}):
            lon = natal_ch["outer"][BASE_POINTS[p]]
        else:       # the Surya Siddhanta has no outer planets: the wheel's default
            return default
        return K.nak28(V.varga_longitude(lon, o.get("base_division", 1), S.varga_options(s)))
    return default


KURMA_DIRS = ["Madhya", "East", "SE", "South", "SW", "West", "NW", "North", "NE"]   # Brihat Samhita 14: three stars each from Krittika, the centre first
WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def wheels(natal_ch, ch, b, cfg, s, options=None, natal_b=None):
    """The wheels of chart ``ch``; the rotating ones turn from the natal Sun's star (the default of each view's base point) or, in Tajaka and Tithi Pravesha charts, the chart's lagna's; Kota
    from the natal Moon's (its "Natal Moonstar is taken as the base"). ``options``: {show: the sets of the chakra menu, planet_varga, base_point and base_division, base_star, chart_kind}."""
    o = options or {}
    shown = o.get("show") or ["planets"]
    d = o.get("planet_varga", 1)
    day = E.day_lords(b, cfg, **S.day_kw(s))
    yogini, mrityu = TR.yogini_mrityu(day["janma_ghatis"], day["weekday"])
    bodies = _bodies(ch, b, cfg, s, shown, d)
    on_star = [[] for _ in range(28)]
    on_sign = [[] for _ in range(12)]
    on_star27 = [[] for _ in range(27)]
    on_pada = [[] for _ in range(108)]
    for label, lon in bodies:
        on_pada[int(lon % 360 // (K.NAK / 4))].append(label)
        on_star[K.nak28(lon)].append(label)
        on_sign[int(lon // 30)].append(label)
        on_star27[int(lon % 360 // K.NAK)].append(label)
    if "yogini" in shown:
        on_star[yogini].append("Yo")
        on_star[mrityu].append("Mr")
    natal_sun, natal_moon = natal_ch["planet_longitudes"]["Sun"], natal_ch["planet_longitudes"]["Moon"]

    def turned(base, lagna=True):
        return [{"star": K.NAKSHATRAS_28[(i + base) % 28],
                 "bodies": [x for x in on_star[(i + base) % 28] if lagna or x != "As"]} for i in range(28)]
    sun = _base_star(natal_ch, ch, o, s, K.nak28(ch["lagna_lon"]) if o.get("chart_kind") in TAJAKA_KINDS else K.nak28(natal_sun))
    moon27 = int(natal_moon * 0.075)
    rings = [("Lagna", ch["lagna_lon"]), ("Moon", ch["planet_longitudes"]["Moon"]), ("Sun", ch["planet_longitudes"]["Sun"])]
    lagna_sign = int(ch["lagna_lon"] // 30)
    from_moon, from_lagna = K.special_taras(natal_moon), K.special_taras(natal_ch["lagna_lon"])
    # who kicks and who aspects each star, for the Sarvatobhadra's highlights: Sun .. Rahu (Ketu has none of these)
    eight = {i: (ch["planet_longitudes"][p]) for i, p in enumerate(PLANETS[:8])}
    latta = {k: [] for k in K.NAKSHATRAS_28}
    aspect = {k: [] for k in K.NAKSHATRAS_28}
    for i, (kicked, _, asp) in enumerate(K.nakshatra_aspects(eight)):
        latta[kicked].append(PLANET_ABBR[i])
        for star in asp:
            aspect[star].append(PLANET_ABBR[i])
    moon_group = (int(natal_moon // K.NAK) - 2) % 27 // 3
    nb = natal_b or b
    tithi = K.special_tithis(natal_moon, natal_sun)[0]
    refs = {"moon_star": K.NAKSHATRAS_28[K.nak28(natal_moon)], "lagna_sign": SIGNS[int(natal_ch["lagna_lon"] // 30)],
            "tithi_group": TITHI_GROUPS[(tithi["paksha_index"] - 1) % 5], "weekday": WEEKDAYS[E.day_lords(nb, cfg, **S.day_kw(s))["weekday"] % 7]}
    pos = E.planet_positions(b.jd_ut, cfg, b)

    def motion(p):
        """How a graha moves, which picks its main vedha in the Sarvatobhadra: retrograde the right, fast the left, at its usual pace the
        front. The Sun and Moon are always fast, as the Sarvatobhadra's texts take them; Rahu and Ketu retrograde while they move backwards
        (always, with the mean nodes), else at their usual pace."""
        if p in ("Rahu", "Ketu"):
            return "retro" if pos[p]["speed"] < 0 else "normal"
        if p in ("Sun", "Moon"):
            return "fast"
        v = pos[p]["speed"]
        return "retro" if v < 0 else "fast" if v > MEAN_DAILY_SPEEDS[p] else "normal"
    return {
        "motion": {a: motion(p) for a, p in zip(PLANET_ABBR, PLANETS)},
        "kalachakra": turned(sun, lagna=False),
        "surya_kalanala": turned(sun),
        "chandra_kalanala": turned(sun),
        "shoola": turned(sun),
        "kota": {"slots": turned(_base_star(natal_ch, ch, o, s, K.nak28(natal_moon)), lagna=False), "swami": SIGN_LORD[int(natal_moon // 30)],
                 "pala": PLANETS[KOTA_PALA[moon27][int(natal_moon * 0.3) % 4] - 1]},
        "sarvatobhadra": {"stars": {K.NAKSHATRAS_28[i]: on_star[i] for i in range(28)},
                          "special": [[m[0], m[2], l[2]] for m, l in zip(from_moon, from_lagna)], "latta": latta, "aspect": aspect, "refs": refs},
        "kurma": {"regions": [{"dir": KURMA_DIRS[g], "stars": [K.NAKSHATRAS_27[(2 + 3 * g + j) % 27] for j in range(3)],
                               "bodies": [x for j in range(3) for x in on_star27[(2 + 3 * g + j) % 27]]} for g in range(9)], "janma": moon_group},
        "retro": [a for a, p in zip(PLANET_ABBR, PLANETS) if ch["retrograde"].get(p)],
        # each ring starts its sign at the sector just above 3 o'clock and runs clockwise through the reverse zodiac
        "sudarsana": [{"from": name, "sectors": [{"sign": SIGNS[(int(lon // 30) + 2 - k) % 12], "bodies": on_sign[(int(lon // 30) + 2 - k) % 12]}
                                                 for k in range(12)]} for name, lon in rings],
        # "every": each pada's reading as if the Moon were in its middle, for a pada picked on Home's Avakahada
        "avakahada": {"padas": on_pada, "native": avakahada(natal_moon), "every": [avakahada((i + 0.5) * K.NAK / 4) for i in range(108)]},
        "ghataka": {"moon_sign": int(natal_moon // 30), "day": ghataka_day(b, ch, cfg, day["weekday"])},
        # clockwise from top centre, the lagna's sign first
        "tripataki": [{"sign": SIGNS[(lagna_sign - k) % 12], "bodies": on_sign[(lagna_sign - k) % 12]} for k in range(12)],
    }


TATVAS = ["Agni (fire)", "Prithvi (earth)", "Vayu (air)", "Jala (water)"]


def avakahada(moon):
    """The Avakahada chakra's reading of the natal Moon: its pada (0..107) and what the star and sign make of the native."""
    nak, rasi = int(moon % 360 // K.NAK), int(moon // 30)
    lord = SIGN_LORD[rasi] + {10: " and Rahu", 7: " and Ketu"}.get(rasi, "")     # the nodes co-lord Aquarius and Scorpio
    return {"pada": int(moon % 360 // (K.NAK / 4)), "rasi_lord": lord, "nak_lord": K.TARA_LORDS[nak % 9],
            "varna": CT.VARNA_NAMES[CT.VARNA_BY_RASI[rasi]], "vashya": CT.VASHYA_NAMES[CT.vashya_class(rasi, moon)],
            "yoni": CT.YONI_NAMES[CT.NAKSHATRA_YONI[nak]], "gana": CT.GANA_NAMES[CT.NAKSHATRA_GANA[nak]], "nadi": CT.NADI_NAMES[CT.NAKSHATRA_NADI[nak]],
            "tatva": TATVAS[rasi % 4]}


def ghataka_day(b, ch, cfg, weekday):
    """What the Ghataka chakra checks of a moment: its weekday (0 Sunday), tithi (0..29), the Moon's star (0..26) and sign, and the Amanta month (0 Chaitra)."""
    pc = E.panchanga(b, ch, cfg)
    k = pc["tithi"]
    month = (pc["lunar_month"] + 1) % 12      # the panchanga counts from Vaishakha
    return {"weekday": weekday % 7, "tithi": k, "tithi_name": P.TITHI_NAMES[k] if k in (14, 29) else "%s %s" % ("Shukla" if k < 15 else "Krishna", P.TITHI_NAMES[k]),
            "nakshatra": pc["nakshatra"], "moon_sign": int(ch["planet_longitudes"]["Moon"] // 30), "month": month, "month_name": LUNAR_MONTHS[month]}


HOUSE_POINTS = ["Lagna", "Arudha lagna", "Upapada lagna", "Hora lagna", "Ghati lagna", "Bhava lagna", "Varnada lagna"] + PLANETS
TITHI_GROUPS = ["Nanda", "Bhadra", "Jaya", "Rikta", "Poorna"]


def _natal_point(ch, s, name, d):
    from core_logic import sign_strength as SS
    opt = S.varga_options(s)
    nine = [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS]
    signs = [V.varga_sign(x, d, opt) for x in nine]
    if name in PLANETS:
        return V.varga_longitude(ch["planet_longitudes"][name], d, opt)
    if name == "Lagna":
        return V.varga_longitude(ch["lagna_lon"], d, opt)
    if name in ("Arudha lagna", "Upapada lagna"):
        a = SS.bhava_arudhas(signs, nine, s.arudha_exceptions_bhava, s.arudha_nodes)
        return a[0 if name == "Arudha lagna" else 11] * 30.0
    if name == "Varnada lagna":
        return V.varga_longitude(ch["varnada_lagnas"][0], d, opt)
    return V.varga_longitude(ch["special_lagnas"][name.split()[0].capitalize() + "_Lagna"], d, opt)


def special_point(ch, s, kind, value, d=1, point="Moon", star=None):
    """What a Sarvatobhadra special point highlights: {stars, signs, tithi}. ``star``: count from this star ("from here") instead of the natal Moon."""
    opt = S.varga_options(s)
    moon = V.varga_longitude(ch["planet_longitudes"]["Moon"], d, opt)
    seed = moon if star is None else (K.NAKSHATRAS_27.index(star) + 0.5) * K.NAK if star in K.NAKSHATRAS_27 else moon
    if kind == "tara":
        return {"stars": list(K.nava_taras(seed)[value][3:6])}
    if kind == "special_nakshatra":
        return {"stars": [K.special_taras(seed)[value][2]]}
    if kind == "tithi":
        row = K.special_tithis(moon, V.varga_longitude(ch["planet_longitudes"]["Sun"], d, opt))[value]
        return {"tithi": TITHI_GROUPS[(row["paksha_index"] - 1) % 5], "text": "%s: %s" % (row["special"], row["name"])}
    if kind == "house":
        return {"signs": [SIGNS[(int(_natal_point(ch, s, point, d) // 30) + value) % 12]]}
    return {"stars": [K.NAKSHATRAS_28[K.nak28(_natal_point(ch, s, point, d))]]}
